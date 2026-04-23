"""
Complete Legal AI API
Includes: Risk Analysis, Case Prediction, Advanced Analysis, and Chatbot
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import sys
import os
from pathlib import Path
import shutil
import re
import requests
from difflib import SequenceMatcher

# Ensure UTF-8 console output so emojis in logs don't crash the server on Windows.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from two_stage_pipeline import TwoStagePipeline

try:
    from pipeline_trace import configure_pipeline_logging

    configure_pipeline_logging()
except Exception:
    pass
try:
    from three_stage_pipeline import ThreeStagePipeline
    THREE_STAGE_AVAILABLE = True
except ImportError:
    THREE_STAGE_AVAILABLE = False
    ThreeStagePipeline = None
from legal_risk_analyzer import LegalRiskAnalyzer, RiskAssessment
from case_predictor import CasePredictor
from advanced_case_analyzer import AdvancedCaseAnalyzer

# Document Analysis and Generation
try:
    from document_analyzer import DocumentAnalyzer
    from document_generator import DocumentGenerator
    DOCUMENT_FEATURES_AVAILABLE = True
except ImportError:
    DOCUMENT_FEATURES_AVAILABLE = False
    DocumentAnalyzer = None
    DocumentGenerator = None

# Import analytics if available
try:
    from analytics_engine import AdvancedAnalytics
    analytics_available = True
except ImportError:
    analytics_available = False
    AdvancedAnalytics = None

# Import legal accuracy validator
try:
    from legal_accuracy_validator import LegalAccuracyValidator
    validator_available = True
except ImportError:
    validator_available = False
    LegalAccuracyValidator = None

# Import safety and verification components
try:
    from safety_guard import SafetyGuard
    from domain_classifier import LegalDomainClassifier
    from question_normalizer import QuestionNormalizer
    from case_law_verifier import CaseLawVerifier
    safety_components_available = True
except ImportError:
    safety_components_available = False
    SafetyGuard = None
    LegalDomainClassifier = None
    QuestionNormalizer = None
    CaseLawVerifier = None

# Initialize FastAPI
app = FastAPI(
    title="Pakistan Criminal Law AI API",
    description="Complete API for legal analysis, risk assessment, case prediction, and chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from db.bootstrap import init_app_database

init_app_database()
import db.repository as db_repo

# Initialize components
print("Initializing API components...")
validator = None  # Initialize at module level
safety_guard = None
domain_classifier = None
question_normalizer = None
case_law_verifier = None

try:
    # Prefer fast two-stage mode by default; opt into three-stage via env flag.
    enable_three_stage = os.getenv("ENABLE_THREE_STAGE_PIPELINE", "false").lower() == "true"

    # Try three-stage pipeline only when explicitly enabled.
    if THREE_STAGE_AVAILABLE and enable_three_stage:
        try:
            pipeline = ThreeStagePipeline(
                peft_model_path="./models/fine-tuned/golden_model/final_golden_model",
                formatter_type="groq",
                formatter_api_key=None  # Will use from config
            )
            print("✅ Using Three-Stage Pipeline (Local Model + RAG + Groq)")
        except Exception as e:
            print(f"⚠️  Three-stage pipeline failed, using two-stage: {e}")
            pipeline = TwoStagePipeline(
                peft_model_path="./models/fine-tuned/golden_model/final_golden_model",
                formatter_type="groq",
                formatter_api_key=None  # Will use from config
            )
            print("✅ Using Two-Stage Pipeline (Local Model + RAG)")
    else:
        pipeline = TwoStagePipeline(
            peft_model_path="./models/fine-tuned/golden_model/final_golden_model",
            formatter_type="groq",
            formatter_api_key=None  # Will use from config
        )
        mode_label = "forced fast mode (default)" if not enable_three_stage else "fallback mode"
        print(f"✅ Using Two-Stage Pipeline (Local Model + RAG) [{mode_label}]")
    risk_analyzer = LegalRiskAnalyzer()
    case_predictor = CasePredictor()
    advanced_analyzer = AdvancedCaseAnalyzer()
    
    # Initialize document features if available
    document_analyzer = None
    document_generator = None
    if DOCUMENT_FEATURES_AVAILABLE:
        try:
            document_analyzer = DocumentAnalyzer()
            document_generator = DocumentGenerator()
            print("✅ Document analysis and generation initialized!")
        except Exception as e:
            print(f"⚠️  Document features not available: {e}")
            document_analyzer = None
            document_generator = None
    else:
        print("⚠️  Document features not available (modules not found)")
    
    # Initialize validator if available
    if validator_available:
        validator = LegalAccuracyValidator()
        print("Legal accuracy validator initialized!")
    else:
        validator = None
        print("Warning: Legal accuracy validator not available")
    
    # Initialize safety components
    if safety_components_available:
        safety_guard = SafetyGuard()
        domain_classifier = LegalDomainClassifier()
        question_normalizer = QuestionNormalizer()
        case_law_verifier = CaseLawVerifier()
        print("Safety components initialized!")
    else:
        print("Warning: Safety components not available")
    
    print("All components initialized successfully!")
except Exception as e:
    print(f"Warning: Some components failed to initialize: {e}")
    pipeline = None
    risk_analyzer = LegalRiskAnalyzer()
    case_predictor = CasePredictor()
    advanced_analyzer = AdvancedCaseAnalyzer()
    validator = None
    safety_guard = None
    domain_classifier = None
    question_normalizer = None
    case_law_verifier = None

# Request/Response Models
class QuestionRequest(BaseModel):
    question: str
    # Groq formatter is on by default for best final answer quality.
    use_formatter: bool = True


def _is_low_quality_answer(answer: str) -> bool:
    """
    Heuristic guardrail for raw/broken outputs.
    Triggers a formatter retry when the answer looks instruction-like,
    truncated, or unrelated to user-facing legal guidance.
    """
    if not answer:
        return True

    text = answer.strip()
    lower = text.lower()
    word_count = len(re.findall(r"\w+", text))

    bad_phrases = [
        "you should not do anything until you have read the legal context",
        "followed it directly",
        "follow it directly",
        "office of the",
        "legal context and followed it",
        "understand the legal context and follow it directly",
        "you should not take any actions until you have read",
    ]
    if any(p in lower for p in bad_phrases):
        return True

    if "LEGAL CONTEXT" in text or "ANSWER FORMAT" in text:
        return True

    # Very short/truncated responses are usually low-quality for legal guidance.
    if word_count < 40:
        return True

    # Detect likely truncation.
    if re.search(r"(of the|under the|with the)\s*$", lower):
        return True

    return False


def _is_false_fir_urgent_question(question: str) -> bool:
    q = question.lower()
    has_fir = "fir" in q or "first information report" in q
    has_false = "false" in q or "wrong" in q or "fake" in q
    has_urgent_window = "first 24" in q or "24 hours" in q or "immediately" in q
    return has_fir and has_false and has_urgent_window


def _build_false_fir_urgent_answer() -> str:
    return (
        "In the first 24 hours after a false FIR, act quickly and in writing.\n\n"
        "1) Contact a criminal lawyer immediately and share FIR number, police station, and exact allegations.\n"
        "2) Apply for protective/pre-arrest bail (if arrest risk exists) through your lawyer as early as possible.\n"
        "3) Collect and preserve exculpatory proof right away (location evidence, CCTV, call records, witnesses, documents).\n"
        "4) Submit a written representation to senior police officials explaining falsity and requesting fair inquiry.\n"
        "5) Do not ignore police notices; appear through counsel and avoid any informal admissions.\n"
        "6) Keep copies of every complaint/application with date and receiving stamp.\n\n"
        "Legal basis: FIR registration is under Section 154 CrPC, and case handling differs for non-cognizable matters under Section 155 CrPC. "
        "For arrest/remand and bail strategy, your lawyer should move immediately under applicable CrPC provisions."
    )


def _is_structured_answer_complete(structured: Dict) -> bool:
    if not isinstance(structured, dict):
        return False
    issue = (structured.get("issue") or "").strip()
    conclusion = (structured.get("conclusion") or "").strip()
    law = structured.get("law") or []
    application = structured.get("application") or []
    return bool(issue and conclusion and isinstance(law, list) and len(law) > 0 and isinstance(application, list) and len(application) > 0)


def _fallback_structured_answer(question: str, answer: str, references: List[Dict]) -> Dict:
    law_items = []
    for ref in references[:4]:
        if not isinstance(ref, dict):
            continue
        label = ref.get("title") or ref.get("case_no") or ref.get("section") or ref.get("type")
        if label:
            law_items.append(str(label))
    if not law_items:
        law_items = ["Grounded Pakistan criminal law references were limited for this query."]

    first_sentences = re.split(r"(?<=[.!?])\s+", (answer or "").strip())
    first_sentences = [s.strip() for s in first_sentences if s.strip()]
    app = first_sentences[:2] if first_sentences else ["No stable application point extracted from model output."]
    conclusion = first_sentences[-1] if first_sentences else "Please verify key facts with a qualified lawyer before action."

    return {
        "issue": question.strip(),
        "law": law_items[:4],
        "application": app,
        "analysis": [],
        "conclusion": conclusion,
    }


def _extract_answer_sections(answer: str) -> List[str]:
    """Extract section mentions like 'Section 154 CrPC' from answer text."""
    if not answer:
        return []
    matches = re.findall(r"section\s+(\d+[a-z]?)\s*(ppc|crpc)", answer, re.IGNORECASE)
    return [f"{num.lower()}_{code.lower()}" for num, code in matches]


def _extract_reference_sections(references: List[Dict]) -> List[str]:
    """Extract section mentions available in grounded references."""
    extracted = []
    for ref in references:
        if not isinstance(ref, dict):
            continue
        rtype = str(ref.get("type", "")).lower()
        title = str(ref.get("title", "")).lower()
        section = str(ref.get("section", "")).lower()
        if rtype == "ppc" and section:
            extracted.append(f"{section}_ppc")
        # Capture CrPC/PPC sections from title text when available
        for num, code in re.findall(r"section\s+(\d+[a-z]?)\s*(ppc|crpc)", title, re.IGNORECASE):
            extracted.append(f"{num.lower()}_{code.lower()}")
    return extracted


def _is_legally_grounded_answer(answer: str, references: List[Dict]) -> bool:
    """
    Reject answers that introduce new section numbers not present in references.
    This prevents hallucination amplification through formatting/reasoning.
    """
    ans_sections = set(_extract_answer_sections(answer))
    if not ans_sections:
        return True
    ref_sections = set(_extract_reference_sections(references))
    if not ref_sections:
        return True
    return ans_sections.issubset(ref_sections)

class CaseDetailsRequest(BaseModel):
    sections: List[str]
    evidence: Optional[str] = ""
    witnesses: Optional[int] = 0
    previous_cases: Optional[int] = 0
    bail_status: Optional[str] = "unknown"
    evidence_strength: Optional[str] = "medium"
    case_description: Optional[str] = ""  # For text-based analysis
    client_in_custody: Optional[bool] = False
    lawyer_experience: Optional[int] = 0
    procedural_violations: Optional[bool] = False
    flight_risk: Optional[bool] = False

class RiskAnalysisRequest(BaseModel):
    case_details: CaseDetailsRequest

class PredictionRequest(BaseModel):
    case_details: CaseDetailsRequest

class AnalysisRequest(BaseModel):
    case_details: CaseDetailsRequest

class CaseTextRequest(BaseModel):
    """Request for text-based case analysis (from old API)"""
    case_description: str
    section_numbers: Optional[List[str]] = None

class CreateCaseRequest(BaseModel):
    """Request to create a new case"""
    case_type: str
    court: str
    judge: Optional[str] = None
    sections: Optional[List[str]] = None
    police_station: Optional[str] = None
    fir_number: Optional[str] = None
    client_name: Optional[str] = None  # For lawyer cases
    description: Optional[str] = None
    filing_date: Optional[str] = None
    next_hearing: Optional[str] = None
    priority: Optional[str] = None  # For lawyer cases: High, Medium, Low
    owner_citizen_id: Optional[str] = None
    owner_lawyer_id: Optional[str] = None

class LawyerRecommendationRequest(BaseModel):
    """Citizen-provided case intake for lawyer recommendations"""
    case_type: Optional[str] = ""
    case_description: str
    charges_or_sections: Optional[str] = ""
    city: Optional[str] = ""
    urgency: Optional[str] = "medium"  # low, medium, high
    preferred_experience_years: Optional[int] = 0
    budget_range: Optional[str] = "medium"  # low, medium, high
    preferred_language: Optional[str] = ""
    hearing_court: Optional[str] = ""


class CitizenQuickCaseRequest(BaseModel):
    """Simple citizen input for fast, non-technical case analysis"""
    case_description: str
    urgency: Optional[str] = "medium"  # low, medium, high
    city: Optional[str] = ""
    hearing_court: Optional[str] = ""
    custody_status: Optional[str] = "unknown"  # in_custody, not_in_custody, unknown
    case_stage: Optional[str] = ""
    incident_date: Optional[str] = ""
    incident_location: Optional[str] = ""
    fir_status: Optional[str] = ""
    police_station: Optional[str] = ""
    witness_status: Optional[str] = ""
    witness_count: Optional[int] = 0
    evidence_summary: Optional[str] = ""
    available_documents: Optional[str] = ""
    key_question: Optional[str] = ""
    desired_outcome: Optional[str] = ""
    child_involved: Optional[bool] = False


class LawyerQuickCaseRequest(BaseModel):
    """Advocate-facing quick triage: same JSON output as citizen flow, richer optional intake."""
    case_description: str
    urgency: Optional[str] = "medium"
    city: Optional[str] = ""
    hearing_court: Optional[str] = ""
    custody_status: Optional[str] = "unknown"
    known_ppc_sections: Optional[str] = ""
    case_stage: Optional[str] = ""
    procedural_notes: Optional[str] = ""
    incident_date: Optional[str] = ""
    incident_location: Optional[str] = ""
    fir_status: Optional[str] = ""
    police_station: Optional[str] = ""
    witness_status: Optional[str] = ""
    witness_count: Optional[int] = 0
    evidence_summary: Optional[str] = ""
    available_documents: Optional[str] = ""
    key_question: Optional[str] = ""
    desired_outcome: Optional[str] = ""
    child_involved: Optional[bool] = False
    opposing_party_version: Optional[str] = ""
    evidence_gaps: Optional[str] = ""
    relief_sought: Optional[str] = ""
    client_goal: Optional[str] = ""


class OnboardingDocumentItem(BaseModel):
    doc_id: str
    file_name: str


class CaseOnboardingExtractRequest(BaseModel):
    case_description: str
    city: Optional[str] = ""
    case_type: Optional[str] = ""
    urgency: Optional[str] = "medium"
    custody_status: Optional[str] = "unknown"
    uploaded_documents: Optional[List[OnboardingDocumentItem]] = []


class CreateLawyerClientRequest(BaseModel):
    lawyerId: str
    clientName: str
    clientEmail: str
    clientPhone: str
    city: Optional[str] = ""
    notes: Optional[str] = ""
    status: Optional[str] = "Active"
    riskLevel: Optional[str] = "Medium"
    priority: Optional[str] = "Medium"


class CreateLawyerClientCaseRequest(BaseModel):
    lawyerId: str
    clientId: str
    caseType: str
    status: Optional[str] = "Active"
    firNumber: Optional[str] = ""
    court: Optional[str] = ""
    policeStation: Optional[str] = ""
    caseStage: Optional[str] = "Initial Review"
    riskLevel: Optional[str] = "Medium"
    priority: Optional[str] = "Medium"
    nextHearing: Optional[str] = ""
    outstandingAmount: Optional[float] = 0
    notes: Optional[str] = ""

# Health Check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "online",
        "service": "Pakistan Criminal Law AI API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "risk_analysis": "/api/risk-analysis",
            "case_prediction": "/api/case-prediction",
            "advanced_analysis": "/api/advanced-analysis",
            "comprehensive": "/api/comprehensive",
            "case_analysis_text": "/api/case-analysis-text",
            "bail_prediction": "/api/bail-prediction",
            "analytics": "/api/analytics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "pipeline": pipeline is not None,
            "risk_analyzer": risk_analyzer is not None,
            "case_predictor": case_predictor is not None,
            "advanced_analyzer": advanced_analyzer is not None,
            "validator": validator is not None
        }
    }

# Chatbot Endpoint
@app.post("/api/chat")
async def chat(request: QuestionRequest):
    """
    Chat with the legal AI chatbot
    
    Ask any question about Pakistan criminal law
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Chatbot pipeline not available")
    
    try:
        original_question = request.question
        
        # Step 1: Normalize question
        normalized_question = original_question
        if question_normalizer:
            try:
                normalization = question_normalizer.normalize(original_question)
                normalized_question = normalization['normalized']
            except Exception as e:
                print(f"Warning: Question normalization error: {e}")
        
        # Step 2: Safety check
        if safety_guard:
            try:
                safety_check = safety_guard.check_question(normalized_question)
                if safety_check.get('should_refuse', False):
                    return {
                        "question": original_question,
                        "answer": safety_check.get('suggested_response', "I cannot answer this question."),
                        "references": [],
                        "sources_count": 0,
                        "response_time": 0,
                        "stage1_time": 0,
                        "stage2_time": 0,
                        "formatted": False,
                        "safety_check": {
                            "refused": True,
                            "reason": safety_check.get('reason', 'unknown'),
                            "safe": safety_check.get('safe', False)
                        }
                    }
            except Exception as e:
                print(f"Warning: Safety check error: {e}")
        
        # Step 3: Domain classification and greeting detection
        is_greeting = False
        if domain_classifier:
            try:
                classification = domain_classifier.classify(normalized_question)
                if not classification.get('in_scope', True):
                    refusal_msg = domain_classifier.get_refusal_message(normalized_question)
                    return {
                        "question": original_question,
                        "answer": refusal_msg or "I can only answer questions about Pakistani criminal law.",
                        "references": [],
                        "sources_count": 0,
                        "response_time": 0,
                        "stage1_time": 0,
                        "stage2_time": 0,
                        "formatted": False,
                        "domain_check": {
                            "in_scope": False,
                            "domain": classification.get('domain', 'unknown'),
                            "reason": classification.get('reason', 'unknown')
                        }
                    }
                
                # Check if it's a greeting (STRICT - only exact matches or very short phrases)
                question_lower = normalized_question.lower().strip()
                question_words = question_lower.split()
                
                # Exact greeting phrases (must match exactly or be very short)
                exact_greetings = [
                    'hi', 'hello', 'hey', 'hey there', 'hi there',
                    'good morning', 'good afternoon', 'good evening', 'good night',
                    'thanks', 'thank you', 'thankyou',
                    'who are you', 'introduce yourself', 'how are you'
                ]
                
                # Check for exact greeting matches
                is_exact_greeting = question_lower in exact_greetings or any(
                    question_lower.startswith(greeting + ' ') or question_lower == greeting 
                    for greeting in exact_greetings
                )
                
                # Check for very short questions (1-2 words) that are likely greetings
                is_short_greeting = len(question_words) <= 2 and any(
                    word in ['hi', 'hello', 'hey', 'thanks', 'thank'] for word in question_words
                )
                
                # Check for specific help/intro questions (must be exact or start with these)
                help_questions = ['what can you do', 'what do you do', 'how can you help']
                is_help_question = any(
                    question_lower == hq or question_lower.startswith(hq + ' ') 
                    for hq in help_questions
                )
                
                # Only treat as greeting if it's clearly a greeting, not a legal question
                is_greeting = (is_exact_greeting or is_short_greeting or is_help_question) and len(question_words) <= 5
                
            except Exception as e:
                print(f"Warning: Domain classification error: {e}")
        
        # Step 3.5: Handle greetings with friendly response (skip RAG)
        if is_greeting:
            welcome_message = """I'm here to help with criminal law matters! I can assist you with:

1) FIR (First Information Report) - Filing and procedures
2) Bail - Types, conditions, and application process
3) Appeals - Criminal appeals and procedures
4) Remand - Custody and bail remand procedures
5) Constitutional Rights - Fundamental rights in criminal cases
6) Court Procedures - Criminal trial procedures
7) Sections of Law - IPC, CrPC, and other relevant laws

Please ask me about any specific legal concern you have. I can also help with document generation and case analysis."""
            
            return {
                "question": original_question,
                "answer": welcome_message,
                "references": [],
                "sources_count": 0,
                "response_time": 0.1,
                "stage1_time": 0,
                "stage2_time": 0,
                "formatted": False,
                "is_greeting": True
            }
        
        # Step 4: Generate answer
        result = pipeline.generate_answer(
            normalized_question,
            use_formatter=request.use_formatter
        )
        
        # Hard fallback for urgent false-FIR guidance where model quality is currently unstable.
        if _is_false_fir_urgent_question(normalized_question):
            result["answer"] = _build_false_fir_urgent_answer()
            result["references"] = [
                {"type": "CrPC", "title": "CrPC Section 154 - First Information Report (FIR)"},
                {"type": "CrPC", "title": "CrPC Section 155 - Non-Cognizable Cases"},
            ]
            result["sources_count"] = 2

        # If fast mode produced a low-quality/raw response, retry once with formatter.
        if (not request.use_formatter) and _is_low_quality_answer(result.get("answer", "")):
            try:
                retry_result = pipeline.generate_answer(
                    normalized_question,
                    use_formatter=True
                )
                if retry_result.get("answer"):
                    result = retry_result
                    # If retry is still weak for urgent false-FIR query, force safe structured answer.
                    if _is_false_fir_urgent_question(normalized_question) and _is_low_quality_answer(result.get("answer", "")):
                        result["answer"] = _build_false_fir_urgent_answer()
                        result["references"] = [
                            {"type": "CrPC", "title": "CrPC Section 154 - First Information Report (FIR)"},
                            {"type": "CrPC", "title": "CrPC Section 155 - Non-Cognizable Cases"},
                        ]
                        result["sources_count"] = 2
            except Exception as e:
                print(f"Warning: formatter retry failed: {e}")

        # Step 5: Verify case citations
        cleaned_answer = result['answer']
        citation_warnings = []
        if case_law_verifier:
            try:
                citation_check = case_law_verifier.verify_answer(
                    result['answer'],
                    result.get('references', [])
                )
                if not citation_check['valid']:
                    # Clean invalid citations
                    cleaned_answer = case_law_verifier.clean_answer(
                        result['answer'],
                        result.get('references', [])
                    )
                    citation_warnings = citation_check.get('invalid_citations', [])
            except Exception as e:
                print(f"Warning: Citation verification error: {e}")
        
        # Step 6: Validate answer
        validation = None
        validation_warnings = []
        if validator:
            try:
                validation = validator.validate_answer(
                    answer=cleaned_answer,
                    question=normalized_question,
                    references=result.get('references', [])
                )
                validation_warnings = validation.get('warnings', [])
            except Exception as e:
                print(f"Warning: Validation error: {e}")
        
        # Ensure cleaned_answer is used (fix for citation removal)
        final_answer = cleaned_answer if cleaned_answer else result.get('answer', '')
        structured_answer = result.get("structured_answer")
        
        # Keep grounded references for internal validation/guardrails.
        filtered_references = []
        for ref in result.get('references', []):
            if not isinstance(ref, dict):
                continue
            ref_type = ref.get("type")
            if ref_type == "PPC" and ref.get("section"):
                filtered_references.append(ref)
            elif ref_type == "CrPC" and ref.get("title"):
                filtered_references.append(ref)
            elif ref_type == "Constitution" and ref.get("title"):
                filtered_references.append(ref)
            elif ref_type == "Case Law" and ref.get("case_no"):
                filtered_references.append(ref)
            elif ref.get("title"):
                filtered_references.append(ref)

        # Deduplicate references while preserving order.
        dedup_refs = []
        seen_refs = set()
        for ref in filtered_references:
            key = (
                str(ref.get("type", "")),
                str(ref.get("title", "")),
                str(ref.get("case_no", "")),
                str(ref.get("section", "")),
            )
            if key in seen_refs:
                continue
            seen_refs.add(key)
            dedup_refs.append(ref)
        filtered_references = dedup_refs

        # Frontend-facing sources: prefer Groq-generated display references.
        frontend_references = []
        if isinstance(result.get("display_references"), list):
            frontend_references = [str(x).strip() for x in result.get("display_references", []) if str(x).strip()]
        if not frontend_references:
            # fallback to readable legal references if Groq display source generation fails
            for ref in filtered_references[:5]:
                if isinstance(ref, dict):
                    title = ref.get("title") or ref.get("case_no") or ref.get("section") or ref.get("type")
                    if title:
                        frontend_references.append(str(title))

        # Source visibility fallback: keep at least one readable source item when available.
        if not filtered_references and isinstance(result.get("references"), list):
            for ref in result.get("references", [])[:3]:
                if isinstance(ref, dict):
                    title = ref.get("title") or ref.get("case_no") or ref.get("type")
                    if title:
                        filtered_references.append({
                            "type": ref.get("type", "Reference"),
                            "title": str(title),
                        })

        # Deterministic completeness check for structured output.
        if not _is_structured_answer_complete(structured_answer):
            structured_answer = _fallback_structured_answer(
                question=original_question,
                answer=final_answer,
                references=filtered_references,
            )

        # Legal grounding lock: if answer introduces sections not in references,
        # fall back to stage1 extractive draft (grounded by construction).
        if not _is_legally_grounded_answer(final_answer, filtered_references):
            extractive_fallback = result.get("initial_answer", "")
            if extractive_fallback:
                final_answer = extractive_fallback
            structured_answer = _fallback_structured_answer(
                question=original_question,
                answer=final_answer,
                references=filtered_references,
            )
            citation_warnings.append({
                "type": "grounding_lock_fallback",
                "message": "Generated answer introduced ungrounded section references; reverted to grounded extractive answer."
            })

        try:
            from pipeline_trace import scrub_statute_numbers_from_chat_answer

            final_answer = scrub_statute_numbers_from_chat_answer(final_answer or "")
        except Exception:
            pass

        response = {
            "question": original_question,
            "answer": final_answer,  # Use cleaned answer
            "references": frontend_references,
            "sources_count": len(frontend_references),
            "response_time": round(result.get('response_time', 0), 2),
            "stage1_time": round(result.get('stage1_time', 0), 2),
            "stage1_5_time": round(result.get('stage1_5_time', 0), 2),
            "stage2_time": round(result.get('stage2_time', 0), 2),
            "stage3_time": round(result.get('stage3_time', 0), 2) if 'stage3_time' in result else 0,
            "formatted": result.get('formatted', False),
            "reasoned": result.get("reasoned", False),
            "intent": result.get("intent", "general"),
            "confidence": result.get("confidence", "medium"),
            "structured_answer": structured_answer,
            "model_sources": {
                "reasoner_mode": result.get("reasoner_mode", "none"),
                "reasoner_model": result.get("reasoner_model_used", ""),
                "formatter_mode": result.get("formatter_mode", "none"),
                "formatter_model": result.get("formatter_model_used", ""),
            },
        }
        
        # Add validation if available
        if validation:
            response["validation"] = {
                "valid": validation['valid'],
                "score": validation['score'],
                "warnings": validation_warnings if validation['score'] < 90 else []
            }
        
        if citation_warnings:
            response['citation_warnings'] = citation_warnings
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

# Risk Analysis Endpoint
@app.post("/api/risk-analysis")
async def risk_analysis(request: RiskAnalysisRequest):
    """
    Advanced Risk Analysis
    
    Analyzes legal case and provides comprehensive risk assessment
    """
    try:
        case_dict = request.case_details.dict()
        assessment = risk_analyzer.analyze_case(case_dict)
        
        return {
            "overall_risk": assessment.overall_risk,
            "risk_level": assessment.risk_level,
            "confidence": assessment.confidence,
            "factors": assessment.factors,
            "recommendations": assessment.recommendations,
            "risk_breakdown": {
                "critical": assessment.overall_risk >= 80,
                "high": 60 <= assessment.overall_risk < 80,
                "medium": 40 <= assessment.overall_risk < 60,
                "low": assessment.overall_risk < 40
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in risk analysis: {str(e)}")

# Case Prediction Endpoint
@app.post("/api/case-prediction")
async def case_prediction(request: PredictionRequest):
    """
    Case Outcome Prediction
    
    Predicts case outcome, bail probability, and sentencing
    """
    try:
        case_dict = request.case_details.dict()
        prediction = case_predictor.predict_outcome(case_dict)
        
        return {
            "predictions": {
                "conviction_probability": prediction['conviction_probability'],
                "acquittal_probability": prediction['acquittal_probability'],
                "bail_probability": prediction['bail_probability'],
                "sentence_prediction": prediction['sentence_prediction'],
                "timeline_prediction": prediction['timeline_prediction']
            },
            "risk_assessment": {
                "overall_risk": prediction['overall_risk'],
                "risk_level": prediction['risk_level'],
                "confidence": prediction['confidence']
            },
            "recommendations": prediction['recommendations'],
            "suggested_actions": prediction.get('suggested_actions', []),
            "plea_deal_probability": prediction.get('plea_deal_probability', 0),
            "plea_deal_recommendation": prediction.get('plea_deal_recommendation', '')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in case prediction: {str(e)}")

# Advanced Analysis Endpoint
@app.post("/api/advanced-analysis")
async def advanced_analysis(request: AnalysisRequest):
    """
    Comprehensive Advanced Case Analysis
    
    Complete analysis with risk, prediction, strategy, evidence, and defense
    """
    try:
        case_dict = request.case_details.dict()
        analysis = advanced_analyzer.comprehensive_analysis(case_dict)
        
        return {
            "comprehensive_analysis": analysis,
            "summary": {
                "overall_risk": analysis['risk_analysis']['overall_risk'],
                "risk_level": analysis['risk_analysis']['risk_level'],
                "conviction_probability": analysis['outcome_prediction']['conviction_probability'],
                "bail_probability": analysis['outcome_prediction']['bail_probability'],
                "immediate_action": analysis['overall_assessment']['immediate_action']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in advanced analysis: {str(e)}")

# Comprehensive Endpoint (All-in-One)
@app.post("/api/comprehensive")
async def comprehensive(request: AnalysisRequest):
    """
    Complete Comprehensive Analysis
    
    Returns everything: Chat response, Risk Analysis, Prediction, and Advanced Analysis
    """
    try:
        case_dict = request.case_details.dict()
        
        # Build question from case details
        sections_str = ", ".join(case_dict.get('sections', []))
        question = f"What are the legal implications of {sections_str}? What is the risk and possible outcomes?"
        
        results = {}
        
        # Chat response
        if pipeline:
            try:
                chat_result = pipeline.generate_answer(question, use_formatter=True)
                results['chat_response'] = {
                    "answer": chat_result['answer'],
                    "references": chat_result.get('references', []),
                    "response_time": round(chat_result.get('response_time', 0), 2)
                }
            except:
                results['chat_response'] = {"error": "Chatbot unavailable"}
        
        # Risk Analysis
        risk_assessment = risk_analyzer.analyze_case(case_dict)
        results['risk_analysis'] = {
            "overall_risk": risk_assessment.overall_risk,
            "risk_level": risk_assessment.risk_level,
            "factors": risk_assessment.factors,
            "recommendations": risk_assessment.recommendations
        }
        
        # Prediction
        prediction = case_predictor.predict_outcome(case_dict)
        results['prediction'] = {
            "conviction_probability": prediction['conviction_probability'],
            "bail_probability": prediction['bail_probability'],
            "sentence_prediction": prediction['sentence_prediction'],
            "timeline_prediction": prediction['timeline_prediction']
        }
        
        # Advanced Analysis
        advanced = advanced_analyzer.comprehensive_analysis(case_dict)
        results['advanced_analysis'] = {
            "legal_strategy": advanced['legal_strategy'],
            "evidence_analysis": advanced['evidence_analysis'],
            "defense_recommendations": advanced['defense_recommendations'],
            "prosecution_strength": advanced['prosecution_strength'],
            "overall_assessment": advanced['overall_assessment']
        }
        
        return {
            "comprehensive_results": results,
            "summary": {
                "overall_risk": risk_assessment.overall_risk,
                "risk_level": risk_assessment.risk_level,
                "conviction_probability": prediction['conviction_probability'],
                "bail_probability": prediction['bail_probability'],
                "immediate_action": advanced['overall_assessment']['immediate_action']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comprehensive analysis: {str(e)}")

# Text-Based Case Analysis (from old API)
@app.post("/api/case-analysis-text")
async def case_analysis_text(request: CaseTextRequest):
    """
    Analyze case from text description (compatible with old API)
    
    Accepts case description text and extracts sections automatically
    """
    try:
        # Use text-based analysis
        assessment = risk_analyzer.analyze_case_from_text(
            request.case_description,
            request.section_numbers
        )
        
        # Get predictions
        case_dict = {
            'sections': request.section_numbers or [],
            'evidence': 'medium',
            'witnesses': 0
        }
        prediction = case_predictor.predict_outcome(case_dict)
        
        return {
            "case_analysis": {
                "sections_involved": request.section_numbers or [],
                "risk_score": assessment.overall_risk,
                "risk_category": assessment.risk_level
            },
            "risk_assessment": {
                "overall_risk": assessment.overall_risk,
                "risk_level": assessment.risk_level,
                "factors": assessment.factors,
                "confidence": assessment.confidence
            },
            "predictions": {
                "conviction_probability": prediction['conviction_probability'],
                "bail_probability": prediction['bail_probability']
            },
            "recommendations": assessment.recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in text analysis: {str(e)}")


def _extract_sections_from_text(text: str) -> List[str]:
    """Extract likely section numbers from free text."""
    if not text:
        return []
    matches = re.findall(r"\b\d{2,4}[A-Za-z]?\b", text)
    sections: List[str] = []
    for item in matches:
        normalized = item.strip().upper()
        if normalized not in sections:
            sections.append(normalized)
    return sections[:8]


def _normalize_risk_score_0_100(raw) -> int:
    """
    Groq often returns risk as a 0–1 float (e.g. 0.08 → wrongly shown as 8%),
    or a 1–10 scale. Normalize to integer 0–100 (severity / legal exposure for triage).
    """
    if raw is None:
        return 50
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return 50
    if 0 < val <= 1:
        return int(max(1, min(100, round(val * 100))))
    if 1 < val <= 10 and val == int(val):
        return int(max(1, min(100, round(val * 10))))
    return int(max(0, min(100, round(val))))


def _heuristic_risk_floor_core(
    case_description: str,
    custody_status: Optional[str],
    urgency: Optional[str],
    supplementary_text: str = "",
) -> int:
    """Minimum plausible severity from narrative + optional advocate context (Pakistan criminal triage)."""
    combined = f"{case_description or ''} {supplementary_text or ''}"
    text = combined.lower()
    sections = _extract_sections_from_text(combined)
    sec_join = " ".join(sections).lower()

    floor = 22
    violent = [
        "murder", "kill", "killed", "killing", "death", "dead", "die", "dies",
        "qatal", "qatil", "302", "307", "324", "kidnap", "abduct", "rape",
        "dacoity", "392", "terror", "blast", "bomb", "acid", "narcotics", "drugs",
    ]
    if any(k in text for k in violent) or any(s in sec_join for s in ["302", "307", "324", "392"]):
        floor = 78
    elif any(
        k in text
        for k in [
            "theft", "steal", "stole", "stolen", "robbery", "snatch", "snatching",
            "chor", "chori", "pickpocket", "379", "380", "356",
        ]
    ) or any(s in sec_join for s in ["379", "380", "356", "457"]):
        floor = 44
    elif any(
        k in text for k in ["fraud", "420", "cyber", "online", "cheat", "cheating", "forgery", "468", "471"]
    ) or any(s in sec_join for s in ["420", "468", "471"]):
        floor = 52
    elif any(k in text for k in ["assault", "beat", "beating", "hurt", "323", "354", "harass"]):
        floor = 48
    if (custody_status or "").lower() == "in_custody":
        floor = min(95, floor + 8)
    if (urgency or "medium").lower() == "high":
        floor = min(95, floor + 5)
    return floor


def _heuristic_risk_floor(request: CitizenQuickCaseRequest) -> int:
    """Citizen quick-analysis risk floor (unchanged behaviour: narrative only)."""
    return _heuristic_risk_floor_core(
        request.case_description or "",
        request.custody_status,
        request.urgency,
        "",
    )


def _risk_level_from_score(score: int) -> str:
    if score >= 75:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def _fallback_quick_case_analysis(
    request: CitizenQuickCaseRequest,
    *,
    supplementary_text: str = "",
    audience: str = "citizen",
) -> Dict:
    """Fast no-model fallback for quick triage (citizen or advocate audience)."""
    combined = f"{request.case_description or ''} {supplementary_text or ''}".strip()
    text = combined.lower()
    sections = _extract_sections_from_text(combined)

    risk_score = 45
    if any(k in text for k in ["murder", "302", "kidnap", "terror", "narcotics", "rape"]):
        risk_score = 82
    elif any(k in text for k in ["fraud", "420", "cyber", "harassment", "cheating"]):
        risk_score = 67
    elif any(k in text for k in ["bail", "custody", "arrest"]):
        risk_score = 58

    if (request.urgency or "medium").lower() == "high":
        risk_score = min(95, risk_score + 5)
    if (request.custody_status or "unknown").lower() == "in_custody":
        risk_score = min(95, risk_score + 6)

    floor = _heuristic_risk_floor_core(
        request.case_description or "",
        request.custody_status,
        request.urgency,
        supplementary_text,
    )
    risk_score = int(max(0, min(100, max(risk_score, floor))))
    risk_level = _risk_level_from_score(risk_score)

    if audience == "lawyer":
        recommendations = [
            "Cross-check FIR narrative with witness statements and recovery memos for material contradictions.",
            "Map statutory ingredients to facts; note gaps the prosecution must prove beyond reasonable doubt.",
            "Calendar limitation, remand, and bail-application deadlines; preserve proof of service on opposing counsel.",
        ]
        if (request.custody_status or "").lower() == "in_custody":
            recommendations.insert(0, "Prioritize bail grounds (352 Cr.P.C., case law, medical/family hardship) and custody conditions.")
        if "cyber" in text:
            recommendations.append("Chain-of-custody for digital exhibits: hash values, seizure memos, FIA/cybercrime lab reports.")
        next_steps = [
            "Prepare a one-page issues matrix (charges, elements, key exhibits, adverse witnesses).",
            "Request complete investigation file where procedure allows; flag illegal search or arrest if applicable.",
            "Align client instructions with written brief before hearings.",
        ]
        summary = "Advocate triage from your case memo and optional sections—verify against the complete record."
    else:
        recommendations = [
            "Keep FIR copy, arrest memo, and all police documents in one folder.",
            "Write a clear timeline of events with dates, locations, and witness names.",
            "Consult a criminal lawyer before giving detailed statements.",
        ]
        if (request.custody_status or "").lower() == "in_custody":
            recommendations.insert(0, "Discuss urgent bail preparation and hearing strategy immediately.")
        if "cyber" in text:
            recommendations.append("Preserve digital evidence (screenshots, logs, messages, transaction IDs).")
        next_steps = [
            "Share all available documents with your lawyer.",
            "Track next hearing date and required court documents.",
            "Do not delete chats/files that may be evidence.",
        ]
        summary = "Initial legal triage generated from your plain-language case description."

    return {
        "summary": summary,
        "extracted_sections": sections,
        "likely_case_type": "Criminal Matter",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendations": recommendations[:6],
        "next_steps": next_steps,
        "disclaimer": "This is AI-supported guidance, not a substitute for formal legal advice.",
        "missing_information": _build_missing_information(request),
        "confidence_note": _build_confidence_note(request),
    }


def _build_missing_information(request: CitizenQuickCaseRequest) -> List[str]:
    missing: List[str] = []
    if not (request.incident_date or "").strip():
        missing.append("Incident date/time")
    if not (request.incident_location or "").strip():
        missing.append("Exact incident location")
    if not (request.fir_status or "").strip():
        missing.append("FIR status (registered / refused / unknown)")
    if not (request.evidence_summary or "").strip():
        missing.append("Evidence summary (CCTV, medical report, screenshots, call data)")
    if not (request.witness_status or "").strip():
        missing.append("Witness status (available / none / unknown)")
    if not (request.available_documents or "").strip():
        missing.append("Available documents (FIR copy, medico-legal, notices, orders)")
    if not (request.key_question or "").strip():
        missing.append("Main legal question")
    return missing[:6]


def _build_confidence_note(request: CitizenQuickCaseRequest) -> str:
    score = 0
    if len((request.case_description or "").strip()) >= 120:
        score += 1
    if (request.incident_date or "").strip():
        score += 1
    if (request.incident_location or "").strip():
        score += 1
    if (request.fir_status or "").strip():
        score += 1
    if (request.evidence_summary or "").strip():
        score += 1
    if (request.witness_status or "").strip():
        score += 1
    if score >= 5:
        return "High confidence: analysis includes strong factual context."
    if score >= 3:
        return "Medium confidence: useful analysis, but adding missing facts can improve precision."
    return "Low confidence: please add timeline, FIR status, evidence, and witness details for better accuracy."


@app.post("/api/citizen/case-quick-analysis")
async def citizen_case_quick_analysis(request: CitizenQuickCaseRequest):
    """
    Citizen-first quick case analysis:
    - Plain-language input
    - Groq extraction + triage when available
    - No heavy local model / RAG / embedding path
    """
    try:
        description = (request.case_description or "").strip()
        if len(description) < 20:
            raise HTTPException(status_code=400, detail="Please provide at least 20 characters describing your case.")

        groq_key = ""
        try:
            from config import GROQ_API_KEY
            groq_key = GROQ_API_KEY or ""
        except Exception:
            groq_key = ""

        if not groq_key:
            return _fallback_quick_case_analysis(request)

        prompt = f"""You are a Pakistan criminal-law intake assistant.
Analyze this citizen case in simple practical language.

Citizen input:
- Description: {request.case_description}
- Urgency: {request.urgency or "medium"}
- City: {request.city or "not provided"}
- Hearing court: {request.hearing_court or "not provided"}
- Custody status: {request.custody_status or "unknown"}
- Case stage: {request.case_stage or "not provided"}
- Incident date/time: {request.incident_date or "not provided"}
- Incident location: {request.incident_location or "not provided"}
- FIR status: {request.fir_status or "not provided"}
- Police station: {request.police_station or "not provided"}
- Witness status/count: {(request.witness_status or "not provided")} / {request.witness_count or 0}
- Evidence summary: {request.evidence_summary or "not provided"}
- Available documents: {request.available_documents or "not provided"}
- Main legal question: {request.key_question or "not provided"}
- Desired outcome: {request.desired_outcome or "not provided"}
- Child involved: {"yes" if request.child_involved else "no"}

Return STRICT JSON in this schema:
{{
  "summary": "short plain-language summary",
  "extracted_sections": ["302","420"],
  "likely_case_type": "string",
  "risk_score": 0,
  "risk_level": "Low|Medium|High",
  "recommendations": ["3-6 action bullets"],
  "next_steps": ["3-5 immediate steps"],
  "disclaimer": "short legal disclaimer",
  "missing_information": ["3-6 missing details if needed"],
  "confidence_note": "High|Medium|Low confidence with one-line reason"
}}

CRITICAL for risk_score:
- risk_score MUST be an INTEGER from 0 to 100 (NOT a decimal, NOT a probability).
- It measures overall legal seriousness / exposure for triage (higher = more serious).
- Examples: petty dispute ~25; theft ~45–55; fraud/cyber ~55–70; violent crime/murder ~85–95.
- Do NOT output values like 0.08 (that is forbidden). Use whole numbers only.

Rules:
- Keep output non-technical and citizen-friendly.
- Stay within Pakistan criminal law framing only.
- Use missing_information to list critical facts still needed.
- If sections are unknown, use [].
- Return JSON only. No markdown.
"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You generate valid JSON for legal-intake triage."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 700
            },
            timeout=25
        )

        if response.status_code != 200:
            return _fallback_quick_case_analysis(request)

        payload = response.json()
        content = payload["choices"][0]["message"]["content"].strip()

        import json
        try:
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            parsed = json.loads(cleaned)
        except Exception:
            return _fallback_quick_case_analysis(request)

        normalized = _normalize_risk_score_0_100(parsed.get("risk_score"))
        floor = _heuristic_risk_floor(request)
        parsed["risk_score"] = int(max(0, min(100, max(normalized, floor))))

        if parsed.get("risk_level") not in {"Low", "Medium", "High"}:
            parsed["risk_level"] = _risk_level_from_score(parsed["risk_score"])
        else:
            # Align label with numeric score if model disagrees
            expected = _risk_level_from_score(parsed["risk_score"])
            if parsed["risk_level"] == "Low" and parsed["risk_score"] >= 60:
                parsed["risk_level"] = expected
            elif parsed["risk_level"] == "High" and parsed["risk_score"] < 45:
                parsed["risk_level"] = expected

        if not isinstance(parsed.get("extracted_sections"), list):
            parsed["extracted_sections"] = _extract_sections_from_text(request.case_description)
        parsed.setdefault("disclaimer", "This is AI-supported guidance, not a substitute for formal legal advice.")
        if not isinstance(parsed.get("missing_information"), list):
            parsed["missing_information"] = _build_missing_information(request)
        parsed.setdefault("confidence_note", _build_confidence_note(request))
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in citizen quick case analysis: {e}")
        print(traceback.format_exc())
        return _fallback_quick_case_analysis(request)


def _lawyer_quick_supplementary(req: LawyerQuickCaseRequest) -> str:
    return " ".join(
        p
        for p in [
            req.known_ppc_sections or "",
            req.case_stage or "",
            req.procedural_notes or "",
            req.evidence_summary or "",
            req.evidence_gaps or "",
            req.available_documents or "",
            req.relief_sought or "",
            req.client_goal or "",
            req.key_question or "",
            req.opposing_party_version or "",
        ]
        if (p or "").strip()
    )


def _merge_quick_extracted_sections(*text_blobs: str) -> List[str]:
    """Union section-like tokens from multiple free-text fields (dedup, cap length)."""
    seen: List[str] = []
    for blob in text_blobs:
        if not blob:
            continue
        for item in _extract_sections_from_text(blob):
            u = str(item).strip().upper()
            if u and u not in seen:
                seen.append(u)
            if len(seen) >= 12:
                return seen
    return seen


@app.post("/api/lawyer/case-quick-analysis")
async def lawyer_case_quick_analysis(request: LawyerQuickCaseRequest):
    """
    Advocate quick triage: same JSON schema as /api/citizen/case-quick-analysis,
    with optional PPC/stage/notes for sharper strategy-oriented output.
    """
    try:
        description = (request.case_description or "").strip()
        if len(description) < 20:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least 20 characters describing the matter.",
            )

        supplementary = _lawyer_quick_supplementary(request)
        base = CitizenQuickCaseRequest(
            case_description=request.case_description,
            urgency=request.urgency,
            city=request.city,
            hearing_court=request.hearing_court,
            custody_status=request.custody_status,
            case_stage=request.case_stage,
            incident_date=request.incident_date,
            incident_location=request.incident_location,
            fir_status=request.fir_status,
            police_station=request.police_station,
            witness_status=request.witness_status,
            witness_count=request.witness_count,
            evidence_summary=request.evidence_summary,
            available_documents=request.available_documents,
            key_question=request.key_question,
            desired_outcome=request.desired_outcome,
            child_involved=request.child_involved,
        )

        groq_key = ""
        try:
            from config import GROQ_API_KEY
            groq_key = GROQ_API_KEY or ""
        except Exception:
            groq_key = ""

        if not groq_key:
            parsed_fb = _fallback_quick_case_analysis(
                base, supplementary_text=supplementary, audience="lawyer"
            )
            parsed_fb["extracted_sections"] = _merge_quick_extracted_sections(
                request.case_description,
                request.known_ppc_sections or "",
                supplementary,
            )
            return parsed_fb

        prompt = f"""You are a senior Pakistan criminal-law advocate advising another lawyer on a live file.
Use precise but concise professional language (court-ready thinking, not lay explanations).

Matter summary:
- Facts / memo: {request.case_description}
- Known PPC sections (if stated): {request.known_ppc_sections or "not specified"}
- Procedural stage: {request.case_stage or "not specified"}
- Advocate notes (procedure / evidence / risk): {request.procedural_notes or "none"}
- Incident date/time: {request.incident_date or "not provided"}
- Incident location: {request.incident_location or "not provided"}
- FIR status: {request.fir_status or "not provided"}
- Police station: {request.police_station or "not provided"}
- Witness status/count: {(request.witness_status or "not provided")} / {request.witness_count or 0}
- Evidence summary: {request.evidence_summary or "not provided"}
- Evidence gaps: {request.evidence_gaps or "not provided"}
- Available documents: {request.available_documents or "not provided"}
- Opposing version: {request.opposing_party_version or "not provided"}
- Relief sought: {request.relief_sought or "not provided"}
- Client goal: {request.client_goal or "not provided"}
- Main legal question: {request.key_question or "not provided"}
- Child involved: {"yes" if request.child_involved else "no"}
- Urgency: {request.urgency or "medium"}
- City: {request.city or "not provided"}
- Hearing court: {request.hearing_court or "not provided"}
- Client custody status: {request.custody_status or "unknown"}

Return STRICT JSON in this schema:
{{
  "summary": "short professional summary of issues and exposure",
  "extracted_sections": ["302","420"],
  "likely_case_type": "string",
  "risk_score": 0,
  "risk_level": "Low|Medium|High",
  "recommendations": ["3-6 tactical bullets for counsel"],
  "next_steps": ["3-5 immediate litigation / file tasks"],
  "disclaimer": "short legal disclaimer",
  "missing_information": ["3-6 missing details if needed"],
  "confidence_note": "High|Medium|Low confidence with one-line reason"
}}

CRITICAL for risk_score:
- risk_score MUST be an INTEGER from 0 to 100 (NOT a decimal, NOT a probability).
- It measures overall seriousness / litigation exposure for triage (higher = more serious).
- Calibrate using both narrative and any stated PPC sections.
- Do NOT output values like 0.08. Use whole numbers only.

Rules:
- Recommendations should reflect advocate work (applications, record, cross-examination angles, disclosure)—not generic client advice.
- Keep analysis tied to Pakistan criminal law procedural practice.
- Use missing_information to request file facts that are absent.
- If sections are unknown, use [] or best inference from text.
- Return JSON only. No markdown.
"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "You generate valid JSON for Pakistan criminal-law advocate triage.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 800,
            },
            timeout=25,
        )

        if response.status_code != 200:
            parsed_fb = _fallback_quick_case_analysis(
                base, supplementary_text=supplementary, audience="lawyer"
            )
            parsed_fb["extracted_sections"] = _merge_quick_extracted_sections(
                request.case_description,
                request.known_ppc_sections or "",
                supplementary,
            )
            return parsed_fb

        payload = response.json()
        content = payload["choices"][0]["message"]["content"].strip()

        import json

        try:
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            parsed = json.loads(cleaned)
        except Exception:
            parsed_fb = _fallback_quick_case_analysis(
                base, supplementary_text=supplementary, audience="lawyer"
            )
            parsed_fb["extracted_sections"] = _merge_quick_extracted_sections(
                request.case_description,
                request.known_ppc_sections or "",
                supplementary,
            )
            return parsed_fb

        normalized = _normalize_risk_score_0_100(parsed.get("risk_score"))
        floor = _heuristic_risk_floor_core(
            request.case_description or "",
            request.custody_status,
            request.urgency,
            supplementary,
        )
        parsed["risk_score"] = int(max(0, min(100, max(normalized, floor))))

        if parsed.get("risk_level") not in {"Low", "Medium", "High"}:
            parsed["risk_level"] = _risk_level_from_score(parsed["risk_score"])
        else:
            expected = _risk_level_from_score(parsed["risk_score"])
            if parsed["risk_level"] == "Low" and parsed["risk_score"] >= 60:
                parsed["risk_level"] = expected
            elif parsed["risk_level"] == "High" and parsed["risk_score"] < 45:
                parsed["risk_level"] = expected

        model_sections = parsed.get("extracted_sections")
        if not isinstance(model_sections, list):
            model_sections = []
        parsed["extracted_sections"] = _merge_quick_extracted_sections(
            request.known_ppc_sections or "",
            request.case_description,
            " ".join(str(s) for s in model_sections),
        )
        if not isinstance(parsed.get("missing_information"), list):
            parsed["missing_information"] = _build_missing_information(base)
        parsed.setdefault("confidence_note", _build_confidence_note(base))
        parsed.setdefault(
            "disclaimer",
            "This is AI-supported guidance, not a substitute for formal legal advice.",
        )
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        import traceback

        print(f"Error in lawyer quick case analysis: {e}")
        print(traceback.format_exc())
        supplementary = _lawyer_quick_supplementary(request)
        base = CitizenQuickCaseRequest(
            case_description=request.case_description,
            urgency=request.urgency,
            city=request.city,
            hearing_court=request.hearing_court,
            custody_status=request.custody_status,
            case_stage=request.case_stage,
            incident_date=request.incident_date,
            incident_location=request.incident_location,
            fir_status=request.fir_status,
            police_station=request.police_station,
            witness_status=request.witness_status,
            witness_count=request.witness_count,
            evidence_summary=request.evidence_summary,
            available_documents=request.available_documents,
            key_question=request.key_question,
            desired_outcome=request.desired_outcome,
            child_involved=request.child_involved,
        )
        parsed_fb = _fallback_quick_case_analysis(
            base, supplementary_text=supplementary, audience="lawyer"
        )
        parsed_fb["extracted_sections"] = _merge_quick_extracted_sections(
            request.case_description,
            request.known_ppc_sections or "",
            supplementary,
        )
        return parsed_fb


@app.post("/api/case-onboarding/extract")
async def case_onboarding_extract(request: CaseOnboardingExtractRequest):
    """
    Dynamic onboarding extractor:
    - Uses Groq to structure intake facts
    - Returns profile + suggested analysis modes/parameters
    - Works even with partial information and uploaded doc metadata
    """
    description = (request.case_description or "").strip()
    if len(description) < 20:
        raise HTTPException(status_code=400, detail="Please provide at least 20 characters in case description.")

    docs = request.uploaded_documents or []
    doc_lines = "\n".join([f"- {d.file_name} ({d.doc_id})" for d in docs[:10]]) or "- none"

    try:
        groq_key = ""
        try:
            from config import GROQ_API_KEY
            groq_key = GROQ_API_KEY or ""
        except Exception:
            groq_key = ""

        if not groq_key:
            return {
                "extracted_case_profile": {
                    "case_type_guess": request.case_type or "Criminal Matter",
                    "stage_guess": "Initial intake",
                    "core_facts": [description[:240]],
                    "parties": [],
                    "timeline_points": [],
                    "evidence_found": [d.file_name for d in docs[:5]],
                    "missing_critical_information": [
                        "Exact timeline of events",
                        "FIR status and police action",
                        "Witness and evidence details",
                    ],
                },
                "suggested_analysis_modes": ["risk", "remedy", "strategy"],
                "suggested_parameters": ["urgency", "case_stage", "custody_status", "evidence_strength"],
                "one_paragraph_summary": "Initial onboarding summary generated without external model; add more details and run analysis.",
            }

        prompt = f"""You are a Pakistan criminal-law case onboarding analyst.
Convert user intake into structured profile for downstream analysis/prediction.

Input:
- Case type selected: {request.case_type or "not specified"}
- City: {request.city or "not specified"}
- Urgency: {request.urgency or "medium"}
- Custody status: {request.custody_status or "unknown"}
- User narrative: {description}
- Uploaded documents:
{doc_lines}

Return STRICT JSON:
{{
  "extracted_case_profile": {{
    "case_type_guess": "string",
    "stage_guess": "string",
    "core_facts": ["..."],
    "parties": ["..."],
    "timeline_points": ["..."],
    "evidence_found": ["..."],
    "missing_critical_information": ["..."]
  }},
  "suggested_analysis_modes": ["risk","remedy","strategy","bail","evidence-gap","timeline-check"],
  "suggested_parameters": ["key-value style labels to ask user"],
  "one_paragraph_summary": "single concise paragraph"
}}

Rules:
- Pakistan criminal law context only.
- Do not invent section numbers/case law when missing.
- Prefer practical factual extraction over legal jargon.
- Return JSON only.
"""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You generate valid JSON for legal case onboarding extraction."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 900,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Onboarding extraction provider error.")

        payload = response.json()
        content = payload["choices"][0]["message"]["content"].strip()
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        import json
        parsed = json.loads(cleaned)

        profile = parsed.get("extracted_case_profile") or {}
        profile.setdefault("case_type_guess", request.case_type or "Criminal Matter")
        profile.setdefault("stage_guess", "Initial intake")
        profile.setdefault("core_facts", [description[:240]])
        profile.setdefault("parties", [])
        profile.setdefault("timeline_points", [])
        profile.setdefault("evidence_found", [d.file_name for d in docs[:5]])
        profile.setdefault("missing_critical_information", [])
        parsed["extracted_case_profile"] = profile
        if not isinstance(parsed.get("suggested_analysis_modes"), list):
            parsed["suggested_analysis_modes"] = ["risk", "remedy", "strategy"]
        if not isinstance(parsed.get("suggested_parameters"), list):
            parsed["suggested_parameters"] = ["urgency", "case_stage", "custody_status"]
        parsed.setdefault("one_paragraph_summary", "Case onboarding summary prepared.")
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in onboarding extraction: {str(e)}")


# Bail Prediction Endpoint (standalone)
class BailFactorsRequest(BaseModel):
    """Request for bail prediction with factors"""
    sections: List[str]
    mitigating_factors: Optional[List[str]] = []
    aggravating_factors: Optional[List[str]] = []

@app.post("/api/bail-prediction")
async def bail_prediction(request: BailFactorsRequest):
    """
    Standalone bail prediction with factors (from old API)
    
    Accepts sections and mitigating/aggravating factors
    """
    try:
        factors = {
            'mitigating_factors': request.mitigating_factors or [],
            'aggravating_factors': request.aggravating_factors or []
        }
        
        # Predict bail
        bail_pred = risk_analyzer.predict_bail_likelihood(request.sections, factors)
        
        return {
            "bail_prediction": bail_pred,
            "sections": request.sections,
            "factors": factors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in bail prediction: {str(e)}")

# Analytics Endpoint (if available)
if analytics_available:
    analytics = AdvancedAnalytics()
    
    @app.get("/api/analytics")
    async def get_analytics(days: int = 30):
        """Get analytics and statistics"""
        try:
            stats = analytics.get_comprehensive_stats(days)
            return stats
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in analytics: {str(e)}")

# ============================================================
# DOCUMENT ANALYSIS ENDPOINTS
# ============================================================

class DocumentQuestionRequest(BaseModel):
    doc_id: str
    question: str

class DocumentGenerationRequest(BaseModel):
    template_id: str
    data: Dict
    generate_ai_sections: bool = True

class AnalyzeAndGenerateRequest(BaseModel):
    doc_id: str
    template_id: str
    additional_data: Optional[Dict] = None

@app.post("/api/document/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process document for analysis
    Accepts PDF or DOCX files
    """
    if not document_analyzer:
        raise HTTPException(status_code=503, detail="Document analysis not available")
    
    try:
        # Save uploaded file temporarily
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        result = document_analyzer.upload_document(
            file_path=str(file_path),
            file_name=file.filename
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.post("/api/document/question")
async def ask_document_question(request: DocumentQuestionRequest):
    """
    Ask question about uploaded document
    """
    if not document_analyzer:
        raise HTTPException(status_code=503, detail="Document analysis not available")
    
    try:
        # Get relevant chunks
        search_result = document_analyzer.answer_question(
            doc_id=request.doc_id,
            question=request.question
        )
        
        # Generate answer using pipeline
        if pipeline:
            # Combine document context with main RAG
            context = search_result['context']
            
            # Generate answer
            result = pipeline.generate_answer(
                request.question,
                use_formatter=True
            )
            
            # Enhance with document context
            enhanced_answer = f"{result['answer']}\n\n[Based on uploaded document context]"
            
            return {
                "question": request.question,
                "answer": enhanced_answer,
                "doc_id": request.doc_id,
                "relevant_chunks": search_result['relevant_chunks'][:3],  # Top 3
                "confidence": search_result['confidence'],
                "references": result.get('references', [])
            }
        else:
            return {
                "question": request.question,
                "answer": "AI pipeline not available",
                "doc_id": request.doc_id,
                "relevant_chunks": search_result['relevant_chunks'][:3],
                "confidence": search_result['confidence']
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/api/document/{doc_id}/extract")
async def extract_document_facts(doc_id: str):
    """
    Extract structured facts from document
    """
    if not document_analyzer:
        raise HTTPException(status_code=503, detail="Document analysis not available")
    
    try:
        facts = document_analyzer.extract_facts(doc_id)
        summary = document_analyzer.get_document_summary(doc_id)
        
        return {
            "doc_id": doc_id,
            "facts": facts,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting facts: {str(e)}")

@app.get("/api/document/{doc_id}/summary")
async def get_document_summary_endpoint(doc_id: str):
    """
    Get summary of document
    """
    if not document_analyzer:
        raise HTTPException(status_code=503, detail="Document analysis not available")
    
    try:
        summary = document_analyzer.get_document_summary(doc_id)
        return {
            "doc_id": doc_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")

# ============================================================
# DOCUMENT GENERATION ENDPOINTS
# ============================================================

@app.get("/api/document/templates")
async def list_templates(category: Optional[str] = None):
    """
    List available document templates
    """
    if not document_generator:
        raise HTTPException(status_code=503, detail="Document generation not available")
    
    try:
        templates = document_generator.list_templates(category=category)
        return {
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing templates: {str(e)}")

@app.get("/api/document/templates/{template_id:path}")
async def get_template_details(template_id: str):
    """
    Get detailed information about a specific template including placeholder descriptions
    Note: template_id can contain slashes (e.g., "general/Affidavits")
    """
    if not document_generator:
        raise HTTPException(status_code=503, detail="Document generation not available")
    
    try:
        # URL decode the template_id
        import urllib.parse
        template_id = urllib.parse.unquote(template_id)
        
        if not template_id or template_id.strip() == "":
            raise HTTPException(status_code=400, detail="Template ID cannot be empty")
        
        templates = document_generator.list_templates()
        template = next((t for t in templates if t.get('id') == template_id or t.get('template_id') == template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        
        # Get placeholders and guide from template
        placeholders = template.get('placeholders', [])
        placeholder_map = template.get('placeholder_map', {})
        template_guide = template.get('placeholder_guide', {})
        
        # Generate placeholder descriptions
        # First, use template guide if available
        placeholder_descriptions = {}
        for placeholder_key in placeholders:
            # Check if we have a guide entry for this placeholder
            if placeholder_key in template_guide:
                guide_info = template_guide[placeholder_key]
                placeholder_descriptions[placeholder_key] = {
                    "description": guide_info.get('description', 'Enter value for this field'),
                    "type": "text",
                    "required": False,
                    "original_name": guide_info.get('original_name', placeholder_key)
                }
            else:
                # Generate description based on placeholder name
                placeholder_lower = placeholder_key.lower()
                description = "Enter value for this field"
                field_type = "text"
                
                # Common placeholder patterns and their descriptions
                if 'name' in placeholder_lower:
                    if 'accused' in placeholder_lower or 'applicant' in placeholder_lower:
                        description = "Full name of the accused/applicant"
                    elif 'complainant' in placeholder_lower:
                        description = "Full name of the complainant"
                    elif 'petitioner' in placeholder_lower:
                        description = "Full name of the petitioner"
                    elif 'respondent' in placeholder_lower:
                        description = "Full name of the respondent"
                    else:
                        description = "Full name"
                elif 'fir' in placeholder_lower or 'f.i.r' in placeholder_lower:
                    description = "FIR number (e.g., FIR No. 123/2024)"
                    field_type = "text"
                elif 'section' in placeholder_lower or 'sections' in placeholder_lower:
                    description = "PPC/CrPC section numbers (e.g., '302', '302, 34', or ['302', '34'])"
                    field_type = "text"
                elif 'police_station' in placeholder_lower or 'ps' in placeholder_lower:
                    description = "Name of the police station"
                elif 'date' in placeholder_lower:
                    if 'filing' in placeholder_lower or 'filed' in placeholder_lower:
                        description = "Date when the case was filed (format: DD/MM/YYYY)"
                    elif 'incident' in placeholder_lower:
                        description = "Date of the incident (format: DD/MM/YYYY)"
                    else:
                        description = "Date (format: DD/MM/YYYY)"
                    field_type = "date"
                elif 'court' in placeholder_lower:
                    description = "Name of the court (e.g., 'Sessions Court Karachi')"
                elif 'judge' in placeholder_lower:
                    description = "Name of the presiding judge"
                elif 'address' in placeholder_lower:
                    description = "Complete address"
                    field_type = "textarea"
                elif 'cnic' in placeholder_lower or 'nic' in placeholder_lower:
                    description = "CNIC number (format: XXXXX-XXXXXXX-X)"
                    field_type = "text"
                elif 'phone' in placeholder_lower or 'contact' in placeholder_lower:
                    description = "Phone/contact number"
                    field_type = "tel"
                elif 'email' in placeholder_lower:
                    description = "Email address"
                    field_type = "email"
                elif 'case_brief' in placeholder_lower or 'brief' in placeholder_lower:
                    description = "Brief description of the case (can be auto-generated by AI if left empty)"
                    field_type = "textarea"
                elif 'bail_arguments' in placeholder_lower or 'arguments' in placeholder_lower:
                    description = "Legal arguments for bail (can be auto-generated by AI if left empty)"
                    field_type = "textarea"
                elif 'grounds' in placeholder_lower:
                    description = "Grounds for the application (can be auto-generated by AI if left empty)"
                    field_type = "textarea"
                elif 'prayer' in placeholder_lower:
                    description = "Prayer/relief sought (can be auto-generated by AI if left empty)"
                    field_type = "textarea"
                elif 'case_laws' in placeholder_lower or 'precedents' in placeholder_lower:
                    description = "Relevant case laws and precedents (can be auto-generated by AI if left empty)"
                    field_type = "textarea"
                elif 'facts' in placeholder_lower:
                    description = "Facts of the case"
                    field_type = "textarea"
                elif 'evidence' in placeholder_lower:
                    description = "Description of evidence"
                    field_type = "textarea"
                elif 'witness' in placeholder_lower:
                    description = "Names/details of witnesses"
                    field_type = "textarea"
                elif 'punishment' in placeholder_lower:
                    description = "Punishment prescribed under the section"
                elif 'bailable' in placeholder_lower:
                    description = "Whether the offence is bailable or non-bailable"
                elif 'cognizable' in placeholder_lower:
                    description = "Whether the offence is cognizable or non-cognizable"
                
                # Store the description for this placeholder
                placeholder_descriptions[placeholder_key] = {
                    "description": description,
                    "type": field_type,
                    "required": placeholder_key in ['accused_name', 'fir_number', 'sections', 'police_station'],
                    "original_name": placeholder_map.get(placeholder_key, placeholder_key)
                }
        
        # If no placeholders found, provide default structure
        if not placeholders:
            placeholders = [
                "accused_name", "fir_number", "sections", "police_station", 
                "court", "date", "address", "cnic", "phone", "email"
            ]
            placeholder_descriptions = {
                "accused_name": {"description": "Full name of the accused/applicant", "type": "text", "required": True},
                "fir_number": {"description": "FIR number (e.g., FIR No. 123/2024)", "type": "text", "required": True},
                "sections": {"description": "PPC/CrPC section numbers (e.g., '302', '302, 34')", "type": "text", "required": True},
                "police_station": {"description": "Name of the police station", "type": "text", "required": False},
                "court": {"description": "Name of the court (e.g., 'Sessions Court Karachi')", "type": "text", "required": False},
                "date": {"description": "Date (format: DD/MM/YYYY)", "type": "date", "required": False},
                "address": {"description": "Complete address", "type": "textarea", "required": False},
                "cnic": {"description": "CNIC number (format: XXXXX-XXXXXXX-X)", "type": "text", "required": False},
                "phone": {"description": "Phone/contact number", "type": "tel", "required": False},
                "email": {"description": "Email address", "type": "email", "required": False}
            }
        
        # Create example JSON structure using placeholder keys (not original names)
        example_data = {}
        for placeholder_key in placeholders:
            original_name = placeholder_map.get(placeholder_key, placeholder_key)
            placeholder_lower = placeholder_key.lower()
            
            if 'name' in placeholder_lower or 'party' in placeholder_lower:
                example_data[placeholder_key] = "John Doe"
            elif 'fir' in placeholder_lower:
                example_data[placeholder_key] = "FIR No. 123/2024"
            elif 'section' in placeholder_lower or 'offence' in placeholder_lower:
                example_data[placeholder_key] = "302, 34"
            elif 'police_station' in placeholder_lower:
                example_data[placeholder_key] = "Clifton Police Station"
            elif 'date' in placeholder_lower or 'dated' in placeholder_lower:
                example_data[placeholder_key] = "01/01/2024"
            elif 'court' in placeholder_lower:
                example_data[placeholder_key] = "Sessions Court Karachi"
            elif 'address' in placeholder_lower or 'office' in placeholder_lower:
                example_data[placeholder_key] = "123 Main Street, Karachi"
            elif 'cnic' in placeholder_lower or 'nic' in placeholder_lower:
                example_data[placeholder_key] = "12345-1234567-1"
            elif 'phone' in placeholder_lower or 'contact' in placeholder_lower:
                example_data[placeholder_key] = "0300-1234567"
            elif 'email' in placeholder_lower:
                example_data[placeholder_key] = "example@email.com"
            elif 'reference' in placeholder_lower or 'ref' in placeholder_lower:
                example_data[placeholder_key] = "REF-2024-001"
            elif 'case' in placeholder_lower and 'number' in placeholder_lower:
                example_data[placeholder_key] = "123/2024"
            elif 'year' in placeholder_lower:
                example_data[placeholder_key] = "2024"
            elif 'amount' in placeholder_lower or 'bail' in placeholder_lower:
                example_data[placeholder_key] = "50000"
            elif 'enrollment' in placeholder_lower or 'bar' in placeholder_lower:
                example_data[placeholder_key] = "12345/2020"
            else:
                example_data[placeholder_key] = f"[Enter {original_name}]"
        
        template_id_value = template.get('id') or template.get('template_id') or template_id
        
        return {
            "template_id": template_id_value,
            "name": template.get('name'),
            "category": template.get('category'),
            "placeholders": placeholders,
            "placeholder_descriptions": placeholder_descriptions,
            "placeholder_map": placeholder_map,  # Maps key -> original name
            "example_data": example_data,
            "total_placeholders": len(placeholders)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting template details: {str(e)}")

@app.post("/api/document/generate")
async def generate_document(request: DocumentGenerationRequest):
    """
    Generate document from template
    """
    if not document_generator:
        raise HTTPException(status_code=503, detail="Document generation not available")
    
    try:
        # Validate data
        validation = document_generator.validate_data(
            request.template_id,
            request.data
        )
        
        if not validation['valid']:
            return {
                "status": "validation_failed",
                "validation": validation
            }
        
        # Generate document
        result = document_generator.fill_template(
            template_id=request.template_id,
            data=request.data,
            generate_ai_sections=request.generate_ai_sections
        )
        
        # Log document generation status
        print(f"\n📄 Document Generation Result:")
        print(f"   DOCX: {result.get('output_path', 'N/A')}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")

@app.get("/api/document/download/{filename:path}")
async def download_document(filename: str, format: Optional[str] = None):
    """
    Download generated document in DOCX or PDF format
    """
    from fastapi.responses import FileResponse
    import os
    from urllib.parse import unquote
    
    # Decode URL and extract just the filename (handle both / and \ path separators)
    decoded = unquote(filename)
    # Remove any path components - only keep the actual filename
    filename_clean = os.path.basename(decoded.replace('\\', '/'))
    
    print(f"📥 Download request: original='{filename}', decoded='{decoded}', clean='{filename_clean}'")
    
    # Determine file type from format parameter or filename extension
    if format and format.lower() == "pdf":
        # If filename already ends with .pdf, use it directly
        if filename_clean.lower().endswith('.pdf'):
            pdf_filename = filename_clean
        else:
            # Try PDF version by replacing .docx with .pdf
            pdf_filename = filename_clean.replace('.docx', '.pdf').replace('.DOCX', '.pdf')
        
        doc_path = Path("./data/generated_documents") / pdf_filename
        
        print(f"📄 Looking for PDF: {doc_path} (exists: {doc_path.exists()})")
        
        if doc_path.exists():
            return FileResponse(
                path=str(doc_path),
                filename=pdf_filename,
                media_type="application/pdf"
            )
        else:
            # List available files for debugging
            doc_dir = Path("./data/generated_documents")
            available_files = [f.name for f in doc_dir.glob("*.pdf")] if doc_dir.exists() else []
            raise HTTPException(
                status_code=404, 
                detail=f"PDF version not found: {pdf_filename}. Available PDFs: {available_files[:5]}. Please generate the document first or check if PDF conversion is available."
            )
    
    # Default to DOCX
    doc_path = Path("./data/generated_documents") / filename_clean
    
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_path}")
    
    return FileResponse(
        path=str(doc_path),
        filename=filename_clean,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ============================================================
# DASHBOARD ENDPOINTS
# ============================================================

@app.get("/api/dashboard/citizen")
async def get_citizen_dashboard(citizen_id: Optional[str] = None):
    """
    Get dashboard data for citizen users
    Returns statistics, cases, recommendations, and next hearing info
    """
    try:
        from datetime import datetime

        all_citizen_cases = db_repo.list_stored_cases("citizen")
        if citizen_id:
            all_citizen_cases = [c for c in all_citizen_cases if c.get("owner_citizen_id") == citizen_id]

        active_cases = [c for c in all_citizen_cases if c.get("status") == "Active"]
        pending_hearings = [c for c in all_citizen_cases if c.get("next_hearing")]
        sorted_cases = sorted(
            all_citizen_cases,
            key=lambda c: c.get("filing_date") or "",
            reverse=True,
        )
        recent_cases = []
        for c in sorted_cases[:5]:
            recent_cases.append(
                {
                    "id": c.get("id", ""),
                    "status": c.get("status", "Active"),
                    "type": c.get("case_type", "Case"),
                    "progress": c.get("progress", 0),
                    "date": c.get("filing_date", ""),
                    "court": c.get("court", ""),
                    "judge": c.get("judge", ""),
                    "next_action": "Prepare for hearing" if c.get("next_hearing") else "Update case details",
                }
            )

        next_hearing_case = sorted(
            [c for c in all_citizen_cases if c.get("next_hearing")],
            key=lambda c: c.get("next_hearing") or "",
        )
        next_hearing = None
        if next_hearing_case:
            nh = next_hearing_case[0]
            next_hearing = {
                "case_id": nh.get("id", ""),
                "date": nh.get("next_hearing", ""),
                "time": "10:00 AM",
                "court": nh.get("court", ""),
                "judge": nh.get("judge", ""),
            }

        dashboard_data = {
            "stats": {
                "active_cases": len(active_cases),
                "pending_hearings": len(pending_hearings),
                "documents": int(sum(int(c.get("documents_count", 0) or 0) for c in all_citizen_cases)),
                "top_lawyers": db_repo.count_lawyers_with_verification("Verified"),
            },
            "recent_cases": recent_cases,
            "recommendations": [
                {
                    "title": "Keep case data updated",
                    "description": "Use the case form to keep hearing dates and sections current.",
                    "action": "Review Now",
                    "type": "warning",
                },
                {
                    "title": "Find verified lawyers",
                    "description": "Browse verified lawyers with strong criminal-law experience.",
                    "action": "View Cases",
                    "type": "success",
                },
                {
                    "title": "Legal Update",
                    "description": "Track your dashboard regularly for status and hearing updates.",
                    "action": "Read Update",
                    "type": "info",
                },
            ],
            "next_hearing": next_hearing,
            "trends": {
                "cases_this_month": len(
                    [c for c in all_citizen_cases if str(c.get("filing_date", "")).startswith(datetime.now().strftime("%Y-%m"))]
                ),
                "documents_this_month": int(sum(int(c.get("documents_count", 0) or 0) for c in all_citizen_cases)),
                "next_hearing_date": next_hearing["date"] if next_hearing else "",
            },
        }
        
        return dashboard_data
    except Exception as e:
        import traceback
        print(f"Error getting citizen dashboard: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")

@app.get("/api/dashboard/lawyer")
async def get_lawyer_dashboard(lawyer_id: Optional[str] = None):
    """
    Get dashboard data for lawyer users
    Returns metrics, urgent cases, performance data, and client information
    """
    try:
        from datetime import datetime

        all_lawyer_cases = db_repo.list_stored_cases("lawyer")
        if lawyer_id:
            all_lawyer_cases = [c for c in all_lawyer_cases if c.get("owner_lawyer_id") == lawyer_id]

        active_cases = [c for c in all_lawyer_cases if c.get("status") == "Active"]
        urgent_cases_rows = [c for c in all_lawyer_cases if c.get("priority", "Medium") == "High"]
        urgent_cases_rows = sorted(urgent_cases_rows, key=lambda c: c.get("deadline") or "", reverse=False)[:5]
        urgent_cases = [
            {
                "id": c.get("id", ""),
                "priority": c.get("priority", "Medium"),
                "client_name": c.get("client_name", "Client"),
                "deadline": c.get("deadline") or c.get("next_hearing") or "",
                "hours_billed": c.get("hours_billed", 0),
                "progress": c.get("progress", 0),
            }
            for c in urgent_cases_rows
        ]

        total_clients = db_repo.unique_client_count_for_lawyer(lawyer_id) if lawyer_id else len(
            {
                row.get("clientId")
                for row in db_repo.list_lawyer_client_payloads()
                if row.get("clientId")
            }
        )

        dashboard_data = {
            "metrics": {
                "active_cases": len(active_cases),
                "win_rate": 0,
                "pending_hearings": len([c for c in all_lawyer_cases if c.get("next_hearing")]),
                "total_clients": total_clients,
            },
            "urgent_cases": urgent_cases,
            "performance": {
                "cases_won": 0,
                "cases_total": len(all_lawyer_cases),
                "avg_resolution_months": 0,
                "client_rating": 0,
            },
            "trends": {
                "cases_this_month": len(
                    [c for c in all_lawyer_cases if str(c.get("filing_date", "")).startswith(datetime.now().strftime("%Y-%m"))]
                ),
                "win_rate_trend": "N/A",
                "next_hearing_date": min(
                    [c.get("next_hearing", "") for c in all_lawyer_cases if c.get("next_hearing")] or [""]
                ),
                "active_clients": total_clients,
            },
        }
        
        return dashboard_data
    except Exception as e:
        import traceback
        print(f"Error getting lawyer dashboard: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")

# ============================================================
# CASES ENDPOINTS
# ============================================================

# Users, lawyers, cases, lawyer-clients, and admin settings persist in SQLite (data/lawmate.db).

LAWYER_IMAGES_DIR = Path("data/lawyer_images")
LAWYER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/api/cases/citizen")
async def get_citizen_cases(status: Optional[str] = None, citizen_id: Optional[str] = None):
    """
    Get all cases for a citizen user
    Can filter by status: active, hearing_scheduled, closed, all
    """
    try:
        all_cases = db_repo.list_stored_cases("citizen")
        if citizen_id:
            all_cases = [c for c in all_cases if c.get("owner_citizen_id") == citizen_id]
        all_cases = sorted(all_cases, key=lambda c: c.get("filing_date") or "", reverse=True)
        
        # Filter by status if provided
        if status and status.lower() != "all":
            status_map = {
                "active": "Active",
                "hearing_scheduled": "Hearing Scheduled",
                "closed": "Closed"
            }
            filtered_status = status_map.get(status.lower(), status)
            all_cases = [c for c in all_cases if c["status"] == filtered_status]
        
        return {
            "cases": all_cases,
            "total": len(all_cases),
            "status_filter": status
        }
    except Exception as e:
        import traceback
        print(f"Error getting citizen cases: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting cases: {str(e)}")

@app.get("/api/cases/lawyer")
async def get_lawyer_cases(status: Optional[str] = None, lawyer_id: Optional[str] = None):
    """
    Get all cases for a lawyer user
    Can filter by status: active, urgent, closed, all
    """
    try:
        all_cases = db_repo.list_stored_cases("lawyer")
        if lawyer_id:
            all_cases = [c for c in all_cases if c.get("owner_lawyer_id") == lawyer_id]
        all_cases = sorted(all_cases, key=lambda c: c.get("filing_date") or "", reverse=True)
        
        # Filter by status if provided
        if status and status.lower() != "all":
            if status.lower() == "urgent":
                all_cases = [c for c in all_cases if c.get("priority") == "High"]
            else:
                status_map = {
                    "active": "Active",
                    "hearing_scheduled": "Hearing Scheduled",
                    "closed": "Closed"
                }
                filtered_status = status_map.get(status.lower(), status)
                all_cases = [c for c in all_cases if c["status"] == filtered_status]
        
        return {
            "cases": all_cases,
            "total": len(all_cases),
            "status_filter": status
        }
    except Exception as e:
        import traceback
        print(f"Error getting lawyer cases: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting cases: {str(e)}")

@app.get("/api/cases/{case_id}")
async def get_case_details(case_id: str):
    """
    Get detailed information about a specific case
    """
    try:
        case_details = db_repo.find_stored_case_by_id(case_id)
        if not case_details:
            raise HTTPException(status_code=404, detail="Case not found")
        return case_details
    except Exception as e:
        import traceback
        print(f"Error getting case details: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting case details: {str(e)}")

@app.post("/api/cases")
async def create_case(request: CreateCaseRequest, user_type: str = "citizen"):
    """
    Create a new case
    user_type: "citizen" or "lawyer"
    """
    try:
        from datetime import datetime
        import uuid
        
        # Generate case ID
        if user_type == "lawyer":
            case_id = f"C-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:3]}"
        else:
            # For citizens, use FIR number if provided, otherwise generate
            if request.fir_number:
                case_id = request.fir_number
            else:
                case_id = f"FIR/{datetime.now().strftime('%Y')}/{str(uuid.uuid4())[:6]}"
        
        # Create case object
        new_case = {
            "id": case_id,
            "case_type": request.case_type,
            "status": "Active",
            "court": request.court,
            "judge": request.judge or "Not assigned",
            "filing_date": request.filing_date or datetime.now().strftime("%Y-%m-%d"),
            "next_hearing": request.next_hearing,
            "documents_count": 0,
            "progress": 0
        }
        
        # Add citizen-specific fields
        if user_type == "citizen":
            new_case["assigned_lawyer"] = None
            new_case["owner_citizen_id"] = request.owner_citizen_id or None
            if request.sections:
                new_case["sections"] = request.sections
            if request.police_station:
                new_case["police_station"] = request.police_station
            if request.fir_number:
                new_case["fir_number"] = request.fir_number
        
        # Add lawyer-specific fields
        if user_type == "lawyer":
            new_case["owner_lawyer_id"] = request.owner_lawyer_id or None
            new_case["client_name"] = request.client_name or "Client"
            new_case["priority"] = request.priority or "Medium"
            new_case["deadline"] = request.next_hearing or None
            new_case["hours_billed"] = 0
        
        if user_type == "lawyer":
            db_repo.append_stored_case("lawyer", new_case)
            print(f"✅ Case created and stored: {case_id} (lawyer) - Total stored: {db_repo.count_stored_cases('lawyer')}")
        else:
            db_repo.append_stored_case("citizen", new_case)
            print(f"✅ Case created and stored: {case_id} (citizen) - Total stored: {db_repo.count_stored_cases('citizen')}")
        
        return {
            "success": True,
            "case": new_case,
            "message": f"Case {case_id} created successfully"
        }
    except Exception as e:
        import traceback
        print(f"Error creating case: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating case: {str(e)}")

@app.post("/api/document/suggest")
async def suggest_document_type(facts: Dict):
    """
    Suggest document types based on facts
    """
    if not document_generator:
        raise HTTPException(status_code=503, detail="Document generation not available")
    
    try:
        suggestions = document_generator.suggest_document_type(facts)
        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error suggesting documents: {str(e)}")

# ============================================================
# COMBINED WORKFLOW: ANALYZE + GENERATE
# ============================================================

@app.post("/api/document/analyze-and-generate")
async def analyze_and_generate(request: AnalyzeAndGenerateRequest):
    """
    Complete workflow: Analyze document → Extract facts → Generate document
    """
    if not document_analyzer or not document_generator:
        raise HTTPException(status_code=503, detail="Document features not available")
    
    try:
        # Step 1: Extract facts from document
        facts = document_analyzer.extract_facts(request.doc_id)
        
        # Step 2: Merge with additional data
        data = {**facts, **(request.additional_data or {})}
        
        # Step 3: Validate
        validation = document_generator.validate_data(request.template_id, data)
        
        # Step 4: Generate document
        result = document_generator.fill_template(
            template_id=request.template_id,
            data=data,
            generate_ai_sections=True
        )
        
        return {
            "status": "success",
            "extracted_facts": facts,
            "generation_result": result,
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in analyze-and-generate: {str(e)}")

# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@app.get("/api/admin/dashboard")
async def get_admin_dashboard():
    """
    Get dashboard data for admin users
    Returns system metrics, recent activity, and system status
    """
    try:
        # Calculate metrics from stored data
        total_citizen_cases = db_repo.count_stored_cases("citizen")
        total_lawyer_cases = db_repo.count_stored_cases("lawyer")
        total_cases = total_citizen_cases + total_lawyer_cases
        
        total_citizens = db_repo.count_citizens()
        total_lawyers = db_repo.count_lawyers()
        total_users = total_citizens + total_lawyers
        verified_lawyers = db_repo.count_lawyers_with_verification("Verified")
        pending_lawyer_reviews = max(total_lawyers - verified_lawyers, 0)
        all_citizens = db_repo.list_all_citizens_public()
        all_lawyers = db_repo.list_all_lawyers_public()
        latest_citizens = sorted(all_citizens, key=lambda u: u.get("joinDate", ""), reverse=True)[:3]
        latest_lawyers = sorted(all_lawyers, key=lambda u: u.get("joinDate", ""), reverse=True)[:3]

        recent_activity = []
        for c in latest_citizens:
            recent_activity.append(
                {
                    "action": "New citizen registration",
                    "user": c.get("name", "Citizen"),
                    "time": c.get("joinDate", ""),
                    "type": "info",
                    "detail": f"Registered with email {c.get('email', '')}",
                }
            )
        for l in latest_lawyers:
            recent_activity.append(
                {
                    "action": "Lawyer profile updated",
                    "user": l.get("name", "Lawyer"),
                    "time": l.get("joinDate", ""),
                    "type": "success" if l.get("verificationStatus") == "Verified" else "warning",
                    "detail": f"Verification status: {l.get('verificationStatus', 'Pending')}",
                }
            )
        recent_activity = sorted(recent_activity, key=lambda x: x.get("time", ""), reverse=True)[:8]

        dashboard_data = {
            "metrics": {
                "total_users": total_users,
                "verified_lawyers": verified_lawyers,
                "active_cases": total_cases,
                "pending_reviews": pending_lawyer_reviews,
            },
            "recent_activity": recent_activity,
            "system_status": [
                {
                    "service": "API Server",
                    "status": "Operational",
                    "uptime": "Online"
                },
                {
                    "service": "Database",
                    "status": "Operational",
                    "uptime": "Online"
                },
                {
                    "service": "AI Service",
                    "status": "Operational",
                    "uptime": "Online"
                },
                {
                    "service": "Storage",
                    "status": "Operational",
                    "uptime": "Online"
                }
            ]
        }
        
        return dashboard_data
    except Exception as e:
        import traceback
        print(f"Error getting admin dashboard: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting admin dashboard: {str(e)}")

@app.get("/api/admin/settings")
async def get_admin_settings():
    """
    Get admin settings
    """
    try:
        return db_repo.get_admin_settings()
    except Exception as e:
        import traceback
        print(f"Error getting admin settings: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting admin settings: {str(e)}")

class UpdateSettingsRequest(BaseModel):
    platform_name: Optional[str] = None
    support_email: Optional[str] = None
    max_file_upload_size_mb: Optional[int] = None
    email_notifications: Optional[bool] = None
    ai_monitoring: Optional[bool] = None
    auto_backup: Optional[bool] = None
    maintenance_mode: Optional[bool] = None

@app.post("/api/admin/settings")
async def update_admin_settings(request: UpdateSettingsRequest):
    """
    Update admin settings
    """
    try:
        patch = {}
        if request.platform_name is not None:
            patch["platform_name"] = request.platform_name
        if request.support_email is not None:
            patch["support_email"] = request.support_email
        if request.max_file_upload_size_mb is not None:
            patch["max_file_upload_size_mb"] = request.max_file_upload_size_mb
        if request.email_notifications is not None:
            patch["email_notifications"] = request.email_notifications
        if request.ai_monitoring is not None:
            patch["ai_monitoring"] = request.ai_monitoring
        if request.auto_backup is not None:
            patch["auto_backup"] = request.auto_backup
        if request.maintenance_mode is not None:
            patch["maintenance_mode"] = request.maintenance_mode

        merged = db_repo.update_admin_settings_partial(patch)
        print(f"✅ Admin settings updated: {merged}")

        return {
            "success": True,
            "settings": merged,
            "message": "Settings updated successfully"
        }
    except Exception as e:
        import traceback
        print(f"Error updating admin settings: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating admin settings: {str(e)}")

@app.get("/api/analytics/lawyer")
async def get_lawyer_analytics(lawyer_id: Optional[str] = None):
    """
    Get analytics data for lawyer users
    Returns case performance metrics, outcomes, and success rates
    """
    try:
        from datetime import datetime

        all_cases = db_repo.list_stored_cases("lawyer")
        if lawyer_id:
            all_cases = [c for c in all_cases if c.get("owner_lawyer_id") == lawyer_id]

        def _status_bucket(status: str) -> str:
            s = (status or "").lower()
            if s in {"won", "success", "completed"}:
                return "won"
            if s in {"lost", "dismissed", "rejected"}:
                return "lost"
            return "pending"

        month_order = {}
        for c in all_cases:
            key = str(c.get("filing_date") or "")[:7]
            if key:
                month_order[key] = {"won": 0, "lost": 0, "pending": 0}
        for c in all_cases:
            key = str(c.get("filing_date") or "")[:7]
            if key not in month_order:
                continue
            bucket = _status_bucket(str(c.get("status", "")))
            month_order[key][bucket] += 1

        recent_months = sorted(month_order.keys())[-6:]
        case_outcomes = []
        for m in recent_months:
            case_outcomes.append(
                {
                    "month": datetime.strptime(m + "-01", "%Y-%m-%d").strftime("%b") if len(m) == 7 else m,
                    "won": month_order[m]["won"],
                    "lost": month_order[m]["lost"],
                    "pending": month_order[m]["pending"],
                }
            )

        case_type_map: Dict[str, Dict[str, float]] = {}
        for c in all_cases:
            ct = c.get("case_type") or "Other"
            if ct not in case_type_map:
                case_type_map[ct] = {"count": 0, "won": 0}
            case_type_map[ct]["count"] += 1
            if _status_bucket(str(c.get("status", ""))) == "won":
                case_type_map[ct]["won"] += 1

        case_type_performance = []
        for ct, vals in case_type_map.items():
            count = int(vals["count"])
            won = int(vals["won"])
            win_rate = round((won / count) * 100, 2) if count else 0
            case_type_performance.append({"type": ct, "count": count, "winRate": win_rate})
        case_type_performance = sorted(case_type_performance, key=lambda x: x["count"], reverse=True)[:8]

        total_cases = len(all_cases)
        cases_won = sum(1 for c in all_cases if _status_bucket(str(c.get("status", ""))) == "won")
        cases_lost = sum(1 for c in all_cases if _status_bucket(str(c.get("status", ""))) == "lost")
        cases_pending = max(total_cases - cases_won - cases_lost, 0)
        success_rate = round((cases_won / total_cases) * 100, 2) if total_cases else 0

        analytics_data = {
            "case_outcomes": case_outcomes,
            "case_type_performance": case_type_performance,
            "summary_metrics": {
                "avg_resolution_time_months": 0,
                "client_satisfaction": 0,
                "case_success_rate": success_rate,
                "total_cases": total_cases,
                "cases_won": cases_won,
                "cases_lost": cases_lost,
                "cases_pending": cases_pending,
            },
            "trends": {
                "resolution_time_change": 0,
                "satisfaction_change": 0,
                "success_rate_change": 0,
            }
        }
        
        return analytics_data
    except Exception as e:
        import traceback
        print(f"Error getting lawyer analytics: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting lawyer analytics: {str(e)}")

# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

class LoginRequest(BaseModel):
    email: str
    password: str
    userType: str  # "citizen", "lawyer", or "admin"

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    userType: str  # "citizen" or "lawyer"

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login endpoint - validates credentials and returns user info"""
    try:
        if request.userType == "admin":
            admin_user = db_repo.verify_admin_login(request.email.strip(), request.password)
            if not admin_user:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            return {"success": True, "user": admin_user, "message": "Login successful"}

        if request.userType == "lawyer":
            lawyer = db_repo.verify_lawyer_login(request.email.strip(), request.password)
            if not lawyer:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            return {
                "success": True,
                "user": {
                    "id": lawyer["id"],
                    "name": lawyer["name"],
                    "email": lawyer["email"],
                    "role": "Lawyer",
                    "userType": "lawyer",
                    "verificationStatus": lawyer["verificationStatus"],
                },
                "message": "Login successful",
            }

        if request.userType == "citizen":
            user = db_repo.verify_citizen_login(request.email.strip(), request.password)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": "Citizen",
                    "userType": "citizen",
                    "status": user["status"],
                },
                "message": "Login successful",
            }

        raise HTTPException(status_code=400, detail="Unsupported userType")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in login: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    """Signup endpoint - creates new user or lawyer account"""
    try:
        from datetime import datetime
        import uuid
        
        if db_repo.email_exists_as_citizen_or_lawyer(request.email.strip()):
            raise HTTPException(status_code=400, detail="Email already registered")

        if request.userType == "lawyer":
            new_lawyer = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name.strip(),
                "email": request.email.strip(),
                "specialization": "General Practice",
                "verificationStatus": "Pending",
                "casesSolved": 0,
                "winRate": 0,
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "location": "Not specified",
                "rating": 0,
                "reviews": 0,
                "specializations": [],
                "yearsExp": 0,
                "cases": 0,
                "phone": "",
                "bio": "",
                "profileImage": "",
            }
            try:
                created = db_repo.create_lawyer_record(new_lawyer, request.password)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            print(f"✅ New lawyer registered: {request.email}")
            return {
                "success": True,
                "user": {
                    "id": created["id"],
                    "name": created["name"],
                    "email": created["email"],
                    "role": "Lawyer",
                    "userType": "lawyer",
                    "verificationStatus": created["verificationStatus"],
                },
                "message": "Account created successfully. Verification pending.",
            }

        try:
            new_user = db_repo.create_citizen_record(
                name=request.name.strip(),
                email=request.email.strip(),
                password_plain=request.password,
                join_date=datetime.now().strftime("%Y-%m-%d"),
                status="Active",
                cases_involved=0,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        print(f"✅ New user registered: {request.email}")
        return {
            "success": True,
            "user": {
                "id": new_user["id"],
                "name": new_user["name"],
                "email": new_user["email"],
                "role": "Citizen",
                "userType": "citizen",
                "status": new_user["status"],
            },
            "message": "Account created successfully",
        }
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in signup: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")

# ============================================================
# ADMIN USER MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/admin/users")
async def get_admin_users(search: Optional[str] = None):
    """Get all users for admin management"""
    try:
        users = list(db_repo.list_all_citizens_public())
        for lawyer in db_repo.list_all_lawyers_public():
            users.append({
                "id": lawyer["id"],
                "name": lawyer["name"],
                "email": lawyer["email"],
                "role": "Lawyer",
                "joinDate": lawyer["joinDate"],
                "status": lawyer["verificationStatus"],
                "casesInvolved": lawyer.get("cases", 0),
            })
        if search:
            search_lower = search.lower()
            users = [u for u in users if search_lower in u["name"].lower() or search_lower in u["email"].lower()]
        return {"users": users, "total": len(users)}
    except Exception as e:
        import traceback
        print(f"Error getting admin users: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")

class CreateUserRequest(BaseModel):
    name: str
    email: str
    role: str
    password: str

@app.post("/api/admin/users")
async def create_user(request: CreateUserRequest):
    """Create a new user (admin only)"""
    try:
        from datetime import datetime
        import uuid
        if db_repo.email_exists_as_citizen_or_lawyer(request.email.strip()):
            raise HTTPException(status_code=400, detail="Email already exists")
        if request.role == "Lawyer":
            new_lawyer = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name.strip(),
                "email": request.email.strip(),
                "specialization": "General Practice",
                "verificationStatus": "Pending",
                "casesSolved": 0,
                "winRate": 0,
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "location": "Not specified",
                "rating": 0,
                "reviews": 0,
                "specializations": [],
                "yearsExp": 0,
                "cases": 0,
                "phone": "",
                "bio": "",
                "profileImage": "",
            }
            try:
                created = db_repo.create_lawyer_record(new_lawyer, request.password)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            return {"success": True, "user": created, "message": "Lawyer created successfully"}
        try:
            new_user = db_repo.create_citizen_record(
                name=request.name.strip(),
                email=request.email.strip(),
                password_plain=request.password,
                join_date=datetime.now().strftime("%Y-%m-%d"),
                status="Active",
                cases_involved=0,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return {"success": True, "user": new_user, "message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error creating user: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.put("/api/admin/users/{user_id}")
async def update_user(user_id: str, updates: Dict):
    """Update user information"""
    try:
        updated = db_repo.update_citizen_by_id(user_id, updates)
        if updated:
            return {"success": True, "user": updated, "message": "User updated successfully"}
        try:
            lawyer_updated = db_repo.update_lawyer_by_id(user_id, updates)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if lawyer_updated:
            return {"success": True, "user": lawyer_updated, "message": "Lawyer updated successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error updating user: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        if db_repo.delete_citizen_by_id(user_id):
            return {"success": True, "message": "User deleted successfully"}
        if db_repo.delete_lawyer_by_id(user_id):
            return {"success": True, "message": "Lawyer deleted successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error deleting user: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

# ============================================================
# ADMIN LAWYER MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/admin/lawyers")
async def get_admin_lawyers():
    """Get all lawyers for admin management"""
    try:
        lawyers = db_repo.list_all_lawyers_public()
        return {"lawyers": lawyers, "total": len(lawyers)}
    except Exception as e:
        import traceback
        print(f"Error getting admin lawyers: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting lawyers: {str(e)}")

class CreateLawyerRequest(BaseModel):
    name: str
    email: str
    specialization: Optional[str] = "General Practice"
    password: str
    location: Optional[str] = "Not specified"
    phone: Optional[str] = ""
    yearsExp: Optional[int] = 0
    bio: Optional[str] = ""
    specializations: Optional[List[str]] = []
    profileImage: Optional[str] = ""

class UpdateLawyerRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    yearsExp: Optional[int] = None
    bio: Optional[str] = None
    specializations: Optional[List[str]] = None
    casesSolved: Optional[int] = None
    winRate: Optional[float] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    verificationStatus: Optional[str] = None

@app.post("/api/admin/lawyers")
async def create_lawyer(request: CreateLawyerRequest):
    """Create a new lawyer (admin only)"""
    try:
        from datetime import datetime
        import uuid
        if db_repo.email_exists_as_citizen_or_lawyer(request.email.strip()):
            raise HTTPException(status_code=400, detail="Email already exists")
        new_lawyer = {
            "id": str(uuid.uuid4())[:8],
            "name": request.name.strip(),
            "email": request.email.strip(),
            "specialization": request.specialization,
            "verificationStatus": "Pending",
            "casesSolved": 0,
            "winRate": 0,
            "joinDate": datetime.now().strftime("%Y-%m-%d"),
            "location": request.location or "Not specified",
            "rating": 0,
            "reviews": 0,
            "specializations": request.specializations or ([] if not request.specialization else [request.specialization]),
            "yearsExp": request.yearsExp or 0,
            "cases": 0,
            "phone": request.phone or "",
            "bio": request.bio or "",
            "profileImage": request.profileImage or "",
        }
        try:
            created = db_repo.create_lawyer_record(new_lawyer, request.password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return {"success": True, "lawyer": created, "message": "Lawyer created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error creating lawyer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating lawyer: {str(e)}")

@app.put("/api/admin/lawyers/{lawyer_id}/verify")
async def verify_lawyer(lawyer_id: str, status: str = "Verified"):
    """Verify or reject a lawyer"""
    try:
        updated = db_repo.set_lawyer_verification_status(lawyer_id, status)
        if not updated:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        return {"success": True, "lawyer": updated, "message": f"Lawyer {status.lower()} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error verifying lawyer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error verifying lawyer: {str(e)}")

@app.put("/api/admin/lawyers/{lawyer_id}")
async def update_lawyer(lawyer_id: str, request: UpdateLawyerRequest):
    """Update lawyer profile fields"""
    try:
        update_data = request.dict(exclude_unset=True)
        try:
            lawyer = db_repo.update_lawyer_by_id(lawyer_id, update_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")

        return {"success": True, "lawyer": lawyer, "message": "Lawyer updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error updating lawyer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating lawyer: {str(e)}")

@app.delete("/api/admin/lawyers/{lawyer_id}")
async def delete_lawyer(lawyer_id: str):
    """Delete a lawyer"""
    try:
        if not db_repo.delete_lawyer_by_id(lawyer_id):
            raise HTTPException(status_code=404, detail="Lawyer not found")
        return {"success": True, "message": "Lawyer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error deleting lawyer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting lawyer: {str(e)}")

@app.post("/api/admin/lawyers/{lawyer_id}/image")
async def upload_lawyer_image(lawyer_id: str, image: UploadFile = File(...)):
    """Upload and store profile image for a lawyer"""
    try:
        if not db_repo.lawyer_exists(lawyer_id):
            raise HTTPException(status_code=404, detail="Lawyer not found")

        content_type = (image.content_type or "").lower()
        if content_type not in {"image/jpeg", "image/jpg", "image/png", "image/webp"}:
            raise HTTPException(status_code=400, detail="Only JPG, PNG, or WEBP images are allowed")

        ext = Path(image.filename or "image.jpg").suffix.lower() or ".jpg"
        file_name = f"{lawyer_id}{ext}"
        save_path = LAWYER_IMAGES_DIR / file_name
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_url = f"/api/lawyers/{lawyer_id}/image"
        db_repo.update_lawyer_profile_image(lawyer_id, image_url)
        return {"success": True, "imageUrl": image_url}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error uploading lawyer image: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

# ============================================================
# LAWYER CLIENTS ENDPOINTS
# ============================================================

@app.get("/api/lawyer/clients")
async def get_lawyer_clients(lawyer_id: Optional[str] = None):
    """Get clients for a lawyer"""
    try:
        clients = db_repo.list_lawyer_client_payloads(lawyer_id)
        unique_clients = {}
        for client in clients:
            client_id = client["clientId"]
            if client_id not in unique_clients:
                unique_clients[client_id] = {
                    "id": client_id,
                    "name": client["clientName"],
                    "email": client["clientEmail"],
                    "phone": client["clientPhone"],
                    "caseType": client["caseType"],
                    "status": client["status"],
                    "activeCases": client["activeCases"],
                    "totalCases": client["totalCases"],
                    "caseId": client.get("caseId", ""),
                    "firNumber": client.get("firNumber", ""),
                    "court": client.get("court", ""),
                    "policeStation": client.get("policeStation", ""),
                    "caseStage": client.get("caseStage", "Initial Review"),
                    "riskLevel": client.get("riskLevel", "Medium"),
                    "priority": client.get("priority", "Medium"),
                    "nextHearing": client.get("nextHearing", ""),
                    "lastContactDate": client.get("lastContactDate", ""),
                    "assignedDate": client.get("assignedDate", ""),
                    "outstandingAmount": client.get("outstandingAmount", 0),
                    "notes": client.get("notes", ""),
                    "city": client.get("city", "")
                }
        return {"clients": list(unique_clients.values()), "total": len(unique_clients)}
    except Exception as e:
        import traceback
        print(f"Error getting lawyer clients: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting clients: {str(e)}")


@app.post("/api/lawyer/clients")
async def create_lawyer_client(request: CreateLawyerClientRequest):
    """Create a new client record for a lawyer"""
    try:
        if not request.clientName.strip() or not request.clientEmail.strip() or not request.clientPhone.strip():
            raise HTTPException(status_code=400, detail="clientName, clientEmail and clientPhone are required")

        if not db_repo.lawyer_exists(request.lawyerId):
            raise HTTPException(status_code=404, detail="Lawyer not found")

        import uuid
        from datetime import datetime

        client_id = f"cli-{str(uuid.uuid4())[:8]}"
        db_repo.append_lawyer_client_row({
            "lawyerId": request.lawyerId,
            "clientId": client_id,
            "clientName": request.clientName.strip(),
            "clientEmail": request.clientEmail.strip(),
            "clientPhone": request.clientPhone.strip(),
            "caseType": "",
            "status": request.status or "Active",
            "activeCases": 0,
            "totalCases": 0,
            "caseId": "",
            "firNumber": "",
            "court": "",
            "policeStation": "",
            "caseStage": "Initial Review",
            "riskLevel": request.riskLevel or "Medium",
            "priority": request.priority or "Medium",
            "nextHearing": "",
            "lastContactDate": datetime.now().strftime("%Y-%m-%d"),
            "assignedDate": datetime.now().strftime("%Y-%m-%d"),
            "outstandingAmount": 0,
            "notes": request.notes or "",
            "city": request.city or "",
        })

        return {"success": True, "message": "Client created successfully", "clientId": client_id}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error creating lawyer client: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating client: {str(e)}")


@app.get("/api/lawyer/clients/{client_id}/cases")
async def get_lawyer_client_cases(client_id: str, lawyer_id: Optional[str] = None):
    """Get all case records for a specific lawyer client"""
    try:
        entries = [c for c in db_repo.list_lawyer_client_payloads() if c.get("clientId") == client_id]
        if lawyer_id:
            entries = [c for c in entries if c.get("lawyerId") == lawyer_id]

        cases = [{k: v for k, v in c.items() if k != "_row_id"} for c in entries if c.get("caseId")]
        return {
            "clientId": client_id,
            "cases": [
                {
                    "caseId": c.get("caseId"),
                    "caseType": c.get("caseType", ""),
                    "status": c.get("status", "Active"),
                    "firNumber": c.get("firNumber", ""),
                    "court": c.get("court", ""),
                    "policeStation": c.get("policeStation", ""),
                    "caseStage": c.get("caseStage", "Initial Review"),
                    "riskLevel": c.get("riskLevel", "Medium"),
                    "priority": c.get("priority", "Medium"),
                    "nextHearing": c.get("nextHearing", ""),
                    "outstandingAmount": c.get("outstandingAmount", 0),
                    "notes": c.get("notes", ""),
                    "assignedDate": c.get("assignedDate", ""),
                    "lastContactDate": c.get("lastContactDate", ""),
                }
                for c in cases
            ],
            "total": len(cases)
        }
    except Exception as e:
        import traceback
        print(f"Error getting client cases: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting client cases: {str(e)}")


@app.post("/api/lawyer/clients/{client_id}/cases")
async def create_lawyer_client_case(client_id: str, request: CreateLawyerClientCaseRequest):
    """Create a new case for an existing lawyer client"""
    try:
        if request.clientId != client_id:
            raise HTTPException(status_code=400, detail="Path client_id and payload clientId do not match")
        if not request.caseType.strip():
            raise HTTPException(status_code=400, detail="caseType is required")

        client_entries = db_repo.get_entries_for_lawyer_client(request.lawyerId, client_id)
        if not client_entries:
            raise HTTPException(status_code=404, detail="Client not found for this lawyer")

        import uuid
        from datetime import datetime

        new_case_id = f"LC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:6].upper()}"
        base = {k: v for k, v in client_entries[0].items() if k != "_row_id"}
        new_outstanding = float(request.outstandingAmount or 0)

        db_repo.append_lawyer_client_row({
            "lawyerId": request.lawyerId,
            "clientId": client_id,
            "clientName": base.get("clientName", ""),
            "clientEmail": base.get("clientEmail", ""),
            "clientPhone": base.get("clientPhone", ""),
            "caseType": request.caseType.strip(),
            "status": request.status or "Active",
            "activeCases": 1 if (request.status or "Active") != "Closed" else 0,
            "totalCases": 1,
            "caseId": new_case_id,
            "firNumber": request.firNumber or "",
            "court": request.court or "",
            "policeStation": request.policeStation or "",
            "caseStage": request.caseStage or "Initial Review",
            "riskLevel": request.riskLevel or "Medium",
            "priority": request.priority or "Medium",
            "nextHearing": request.nextHearing or "",
            "lastContactDate": datetime.now().strftime("%Y-%m-%d"),
            "assignedDate": datetime.now().strftime("%Y-%m-%d"),
            "outstandingAmount": new_outstanding,
            "notes": request.notes or "",
            "city": base.get("city", "")
        })

        all_entries = db_repo.get_entries_for_lawyer_client(request.lawyerId, client_id)
        total_cases = len([c for c in all_entries if c.get("caseId")])
        active_cases = len([c for c in all_entries if c.get("caseId") and c.get("status", "Active") != "Closed"])
        total_outstanding = float(sum(float(c.get("outstandingAmount", 0) or 0) for c in all_entries if c.get("caseId")))

        latest_case = next((c for c in reversed(all_entries) if c.get("caseId")), None)
        for entry in all_entries:
            row_id = entry.get("_row_id")
            if row_id is None:
                continue
            plain = {k: v for k, v in entry.items() if k != "_row_id"}
            plain["totalCases"] = total_cases
            plain["activeCases"] = active_cases
            plain["outstandingAmount"] = total_outstanding
            if latest_case:
                lc = {k: v for k, v in latest_case.items() if k != "_row_id"}
                plain["caseType"] = lc.get("caseType", plain.get("caseType", ""))
                plain["status"] = lc.get("status", plain.get("status", "Active"))
                plain["caseId"] = lc.get("caseId", plain.get("caseId", ""))
                plain["firNumber"] = lc.get("firNumber", plain.get("firNumber", ""))
                plain["court"] = lc.get("court", plain.get("court", ""))
                plain["policeStation"] = lc.get("policeStation", plain.get("policeStation", ""))
                plain["caseStage"] = lc.get("caseStage", plain.get("caseStage", "Initial Review"))
                plain["riskLevel"] = lc.get("riskLevel", plain.get("riskLevel", "Medium"))
                plain["priority"] = lc.get("priority", plain.get("priority", "Medium"))
                plain["nextHearing"] = lc.get("nextHearing", plain.get("nextHearing", ""))
                if lc.get("notes"):
                    plain["notes"] = lc.get("notes")
            plain["lastContactDate"] = datetime.now().strftime("%Y-%m-%d")
            db_repo.save_lawyer_client_entry(row_id, plain)

        return {"success": True, "message": "Client case created successfully", "caseId": new_case_id}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error creating client case: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating client case: {str(e)}")

# ============================================================
# CITIZEN FIND LAWYERS ENDPOINTS
# ============================================================

def _extract_case_tags(case_type: Optional[str], case_description: str, charges_or_sections: str = "") -> List[str]:
    """Extract criminal-law specific tags from citizen input"""
    text = f"{case_type} {case_description} {charges_or_sections}".lower()
    keyword_map = {
        "bail": ["bail", "pre-arrest", "post-arrest", "anticipatory", "custody", "remand"],
        "fir": ["fir", "22a", "22b", "registration", "police", "false case"],
        "appeal": ["appeal", "revision", "sentence", "conviction", "acquittal"],
        "evidence": ["evidence", "witness", "cross examination", "forensic", "contradiction"],
        "cyber": ["cyber", "online fraud", "harassment", "digital", "electronic"],
        "constitutional": ["article 199", "constitutional", "fundamental rights", "writ"],
        "white_collar": ["fraud", "embezzlement", "corruption", "financial crime"],
        "violent_offense": ["murder", "302", "assault", "hurt", "kidnapping", "homicide"],
        "narcotics": ["narcotics", "drugs", "cns", "control of narcotic substances"],
    }
    found_tags = []
    for tag, words in keyword_map.items():
        if any(w in text for w in words):
            found_tags.append(tag)
    return found_tags

def _normalize_text(value: str) -> str:
    return "".join(ch for ch in (value or "").lower().strip() if ch.isalnum() or ch.isspace())

def _city_match(city_a: str, city_b: str) -> bool:
    """Fuzzy city match (handles typos like Islambad vs Islamabad)."""
    a = _normalize_text(city_a)
    b = _normalize_text(city_b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio >= 0.82

def _recommendation_scores(lawyer: Dict, req: LawyerRecommendationRequest, case_tags: List[str]) -> Dict:
    """Weighted scoring model for lawyer matching"""
    score = 0.0
    reasons: List[str] = []

    # 1) Domain/specialization fit (max 45)
    spec_text = _normalize_text(f"{lawyer.get('specialization', '')} {' '.join(lawyer.get('specializations', []))}")
    tag_hits = sum(1 for tag in case_tags if tag.replace("_", " ") in spec_text or tag in spec_text)
    case_type_norm = _normalize_text(req.case_type or "")
    case_type_hit = case_type_norm in spec_text if case_type_norm else False
    spec_score = min(45.0, (tag_hits * 10.0) + (12.0 if case_type_hit else 0.0))
    # Strong bonus for the frequent real-world "cyber crime bail" scenario.
    if "cyber" in case_tags and "bail" in case_tags and "cyber" in spec_text and "bail" in spec_text:
        spec_score = min(45.0, spec_score + 8.0)
    if spec_score > 0:
        score += spec_score
        reasons.append(f"Practice area fit score: {round(spec_score, 1)}/45")

    # 2) Location fit (max 25)
    city = (req.city or "").lower().strip()
    lawyer_location = (lawyer.get("location") or "").lower()
    if city:
        if _city_match(city, lawyer_location):
            score += 25.0
            reasons.append("Location strongly matched with citizen city preference")
        else:
            score += 4.0
            reasons.append("Different city, but still available for consultation")
    else:
        score += 10.0

    # 3) Experience fit (max 10)
    years_exp = float(lawyer.get("yearsExp", 0) or 0)
    exp_score = min(8.0, (years_exp / 15.0) * 8.0)
    preferred_exp = float(req.preferred_experience_years or 0)
    if preferred_exp > 0 and years_exp >= preferred_exp:
        exp_score += 2.0
        reasons.append("Meets preferred experience threshold")
    score += exp_score

    # 4) Performance fit (max 10)
    win_rate = float(lawyer.get("winRate", 0) or 0)
    rating = float(lawyer.get("rating", 0) or 0)
    perf_score = min(10.0, (win_rate / 100.0) * 6.0 + (rating / 5.0) * 4.0)
    score += perf_score
    reasons.append(f"Strong performance indicators (Win rate {int(win_rate)}%, Rating {rating}/5)")

    # 5) Urgency and workload fit (max 5)
    urgency = (req.urgency or "medium").lower()
    current_cases = float(lawyer.get("cases", 0) or 0)
    workload_bonus = 5.0 if current_cases <= 20 else 3.5 if current_cases <= 40 else 2.0
    if urgency == "high":
        score += workload_bonus
        reasons.append("Workload-adjusted for urgent matter handling")
    else:
        score += max(2.5, workload_bonus - 0.5)

    # 6) Budget compatibility estimate (max 5)
    budget_range = (req.budget_range or "medium").lower()
    estimated_fee_band = "high" if years_exp >= 12 else "medium" if years_exp >= 6 else "low"
    if budget_range == estimated_fee_band:
        score += 5.0
        reasons.append("Estimated fee band aligned with budget preference")
    elif budget_range == "medium" and estimated_fee_band in {"low", "high"}:
        score += 3.0
    else:
        score += 1.5

    # 7) Critical-fit bonus (max 10): prioritize "right specialist in right city"
    has_primary_legal_fit = spec_score >= 24.0  # substantial legal domain match
    location_is_match = _city_match(city, lawyer_location) if city else False
    if has_primary_legal_fit and location_is_match:
        score += 10.0
        reasons.append("Critical-fit bonus: strong legal fit + same city")

    return {
        "score": round(min(score, 100.0), 2),
        "reasons": reasons,
        "estimated_fee_band": estimated_fee_band,
    }

@app.post("/api/lawyers/recommendations")
@app.post("/api/recommendations/lawyers")
async def recommend_lawyers_for_case(request: LawyerRecommendationRequest):
    """Recommend best-fit criminal lawyers for a citizen case intake"""
    try:
        verified_lawyers = [l for l in db_repo.list_all_lawyers_public() if l.get("verificationStatus") == "Verified"]
        if not verified_lawyers:
            return {"recommendations": [], "total": 0, "message": "No verified lawyers currently available"}

        case_tags = _extract_case_tags(request.case_type, request.case_description, request.charges_or_sections or "")
        ranked = []
        for lawyer in verified_lawyers:
            scoring = _recommendation_scores(lawyer, request, case_tags)
            ranked.append({
                "id": lawyer["id"],
                "name": lawyer["name"],
                "location": lawyer.get("location", "Not specified"),
                "expertise": lawyer.get("specialization", "General Practice"),
                "specializations": lawyer.get("specializations", []),
                "yearsExp": lawyer.get("yearsExp", 0),
                "winRate": lawyer.get("winRate", 0),
                "rating": lawyer.get("rating", 0),
                "reviews": lawyer.get("reviews", 0),
                "cases": lawyer.get("cases", 0),
                "email": lawyer.get("email", ""),
                "phone": lawyer.get("phone", ""),
                "bio": lawyer.get("bio", ""),
                "profileImage": lawyer.get("profileImage", ""),
                "matchScore": scoring["score"],
                "whyRecommended": scoring["reasons"][:4],
                "estimatedFeeBand": scoring["estimated_fee_band"],
            })

        ranked = sorted(ranked, key=lambda x: x["matchScore"], reverse=True)
        top = ranked[:5]

        return {
            "recommendations": top,
            "total": len(top),
            "caseTags": case_tags,
            "selectionCriteria": {
                "specialization_fit_weight": 45,
                "location_weight": 25,
                "experience_weight": 10,
                "performance_weight": 10,
                "urgency_workload_weight": 5,
                "budget_alignment_weight": 5,
                "critical_fit_bonus_weight": 10,
            },
        }
    except Exception as e:
        import traceback
        print(f"Error recommending lawyers: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/api/lawyers")
async def get_lawyers_for_citizens(
    search: Optional[str] = None,
    specialization: Optional[str] = None,
    verified_only: bool = False,
):
    """Get lawyer directory data for citizens to browse"""
    try:
        lawyers = db_repo.list_all_lawyers_public()
        if verified_only:
            lawyers = [l for l in lawyers if l["verificationStatus"] == "Verified"]
        if search:
            search_lower = search.lower()
            lawyers = [l for l in lawyers if search_lower in l["name"].lower() or search_lower in l.get("specialization", "").lower()]
        if specialization and specialization != "all":
            lawyers = [l for l in lawyers if specialization.lower() in l.get("specialization", "").lower() or any(spec.lower() == specialization.lower() for spec in l.get("specializations", []))]
        formatted_lawyers = []
        for lawyer in lawyers:
            formatted_lawyers.append({
                "id": lawyer["id"],
                "name": lawyer["name"],
                "expertise": lawyer.get("specialization", "General Practice"),
                "location": lawyer.get("location", "Not specified"),
                "winRate": lawyer.get("winRate", 0),
                "cases": lawyer.get("cases", 0),
                "rating": lawyer.get("rating", 0),
                "reviews": lawyer.get("reviews", 0),
                "specialization": lawyer.get("specializations", []),
                "yearsExp": lawyer.get("yearsExp", 0),
                "email": lawyer["email"],
                "phone": lawyer.get("phone", ""),
                "bio": lawyer.get("bio", ""),
                "profileImage": lawyer.get("profileImage", "")
            })
        return {"lawyers": formatted_lawyers, "total": len(formatted_lawyers)}
    except Exception as e:
        import traceback
        print(f"Error getting lawyers: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting lawyers: {str(e)}")

@app.get("/api/lawyers/{lawyer_id}")
async def get_lawyer_profile(lawyer_id: str):
    """Get detailed lawyer profile"""
    try:
        lawyer = db_repo.get_lawyer_public_by_id(lawyer_id)
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        return {
            "id": lawyer["id"],
            "name": lawyer["name"],
            "email": lawyer["email"],
            "specialization": lawyer.get("specialization", "General Practice"),
            "location": lawyer.get("location", "Not specified"),
            "winRate": lawyer.get("winRate", 0),
            "cases": lawyer.get("cases", 0),
            "rating": lawyer.get("rating", 0),
            "reviews": lawyer.get("reviews", 0),
            "specializations": lawyer.get("specializations", []),
            "yearsExp": lawyer.get("yearsExp", 0),
            "phone": lawyer.get("phone", ""),
            "verificationStatus": lawyer.get("verificationStatus", "Pending"),
            "bio": lawyer.get("bio", ""),
            "profileImage": lawyer.get("profileImage", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error getting lawyer profile: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting lawyer profile: {str(e)}")

@app.get("/api/lawyers/{lawyer_id}/image")
async def get_lawyer_image(lawyer_id: str):
    """Serve stored lawyer profile image"""
    try:
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            image_path = LAWYER_IMAGES_DIR / f"{lawyer_id}{ext}"
            if image_path.exists():
                return FileResponse(str(image_path))
        raise HTTPException(status_code=404, detail="Lawyer image not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading image: {str(e)}")

# Run server
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PAKISTAN CRIMINAL LAW AI API - COMPLETE SYSTEM")
    print("=" * 70)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("\nEndpoints:")
    print("  POST /api/chat - Chat with legal AI")
    print("  POST /api/risk-analysis - Risk analysis")
    print("  POST /api/case-prediction - Case prediction")
    print("  POST /api/advanced-analysis - Advanced analysis")
    print("  POST /api/comprehensive - All-in-one analysis")
    print("  POST /api/case-analysis-text - Text-based case analysis")
    print("  POST /api/bail-prediction - Standalone bail prediction")
    if analytics_available:
        print("  GET  /api/analytics - Analytics and statistics")
    print("\n  📊 Dashboard & Cases:")
    print("  GET  /api/dashboard/citizen - Citizen dashboard data")
    print("  GET  /api/dashboard/lawyer - Lawyer dashboard data")
    print("  GET  /api/cases/citizen - Citizen cases list")
    print("  GET  /api/cases/lawyer - Lawyer cases list")
    print("  GET  /api/cases/{case_id} - Get case details")
    print("  POST /api/cases - Create new case")
    print("\n  🔧 Admin Features:")
    print("  GET  /api/admin/dashboard - Admin dashboard data")
    print("  GET  /api/admin/settings - Get admin settings")
    print("  POST /api/admin/settings - Update admin settings")
    if analytics_available:
        print("  GET  /api/analytics - Platform analytics (admin)")
        print("  GET  /api/analytics/lawyer - Lawyer case analytics")
    if DOCUMENT_FEATURES_AVAILABLE and document_analyzer and document_generator:
        print("\n  📄 Document Features:")
        print("  POST /api/document/upload - Upload document for analysis")
        print("  POST /api/document/question - Ask question about document")
        print("  GET  /api/document/{doc_id}/extract - Extract facts from document")
        print("  GET  /api/document/{doc_id}/summary - Get document summary")
        print("  GET  /api/document/templates - List available templates")
        print("  POST /api/document/generate - Generate document from template")
        print("  POST /api/document/suggest - Suggest document type")
        print("  POST /api/document/analyze-and-generate - Complete workflow")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

