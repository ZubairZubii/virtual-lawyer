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
from pathlib import Path
import shutil
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

# Initialize components
print("Initializing API components...")
validator = None  # Initialize at module level
safety_guard = None
domain_classifier = None
question_normalizer = None
case_law_verifier = None

try:
    # Try three-stage pipeline first (better quality)
    if THREE_STAGE_AVAILABLE:
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
        print("✅ Using Two-Stage Pipeline (Local Model + RAG)")
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
    use_formatter: bool = True

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
        if validator:
            try:
                validation = validator.validate_answer(
                    answer=cleaned_answer,
                    question=normalized_question,
                    references=result.get('references', [])
                )
            except Exception as e:
                print(f"Warning: Validation error: {e}")
        
        # Ensure cleaned_answer is used (fix for citation removal)
        final_answer = cleaned_answer if cleaned_answer else result.get('answer', '')
        
        response = {
            "question": original_question,
            "answer": final_answer,  # Use cleaned answer
            "references": result.get('references', []),
            "sources_count": result.get('sources_count', 0),
            "response_time": round(result.get('response_time', 0), 2),
            "stage1_time": round(result.get('stage1_time', 0), 2),
            "stage2_time": round(result.get('stage2_time', 0), 2),
            "stage3_time": round(result.get('stage3_time', 0), 2) if 'stage3_time' in result else 0,
            "formatted": result.get('formatted', False)
        }
        
        # Add validation if available
        if validation:
            response["validation"] = {
                "valid": validation['valid'],
                "score": validation['score'],
                "warnings": validation['warnings'] if validation['score'] < 80 else []
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
async def get_citizen_dashboard():
    """
    Get dashboard data for citizen users
    Returns statistics, cases, recommendations, and next hearing info
    """
    try:
        # For now, return default/mock data
        # Later, this will fetch from database
        from datetime import datetime, timedelta
        
        # Enhanced mock data with realistic values
        dashboard_data = {
            "stats": {
                "active_cases": 3,
                "pending_hearings": 2,
                "documents": 15,
                "top_lawyers": 12
            },
            "recent_cases": [
                {
                    "id": "FIR/2024/150",
                    "status": "Active",
                    "type": "Bail Application",
                    "progress": 65,
                    "date": "Dec 10, 2024",
                    "court": "District Court, Mumbai",
                    "judge": "Hon. Justice Sharma",
                    "next_action": "Submit documents"
                },
                {
                    "id": "FIR/2024/151",
                    "status": "Hearing Scheduled",
                    "type": "Evidence Review",
                    "progress": 40,
                    "date": "Dec 18, 2024",
                    "court": "High Court, Mumbai",
                    "judge": "Hon. Justice Patel",
                    "next_action": "Prepare hearing"
                },
                {
                    "id": "FIR/2024/152",
                    "status": "Active",
                    "type": "Appeal",
                    "progress": 25,
                    "date": "Dec 5, 2024",
                    "court": "Sessions Court, Delhi",
                    "judge": "Hon. Justice Reddy",
                    "next_action": "File response"
                }
            ],
            "recommendations": [
                {
                    "title": "Document Review Required",
                    "description": "3 documents need review before Dec 18 hearing",
                    "action": "Review Now",
                    "type": "warning"
                },
                {
                    "title": "Similar Cases Found",
                    "description": "5 cases with 78% win rate similar to yours",
                    "action": "View Cases",
                    "type": "success"
                },
                {
                    "title": "Legal Update",
                    "description": "2 new amendments filed related to your case",
                    "action": "Read Update",
                    "type": "info"
                }
            ],
            "next_hearing": {
                "case_id": "FIR/2024/151",
                "date": "Dec 18, 2024",
                "time": "10:00 AM",
                "court": "High Court, Mumbai, Room 304",
                "judge": "Hon. Justice Patel"
            },
            "trends": {
                "cases_this_month": 2,
                "documents_this_month": 5,
                "next_hearing_date": "Dec 18, 2024"
            }
        }
        
        return dashboard_data
    except Exception as e:
        import traceback
        print(f"Error getting citizen dashboard: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")

@app.get("/api/dashboard/lawyer")
async def get_lawyer_dashboard():
    """
    Get dashboard data for lawyer users
    Returns metrics, urgent cases, performance data, and client information
    """
    try:
        # For now, return default/mock data
        # Later, this will fetch from database
        from datetime import datetime, timedelta
        
        # Enhanced mock data with realistic values
        dashboard_data = {
            "metrics": {
                "active_cases": 15,
                "win_rate": 82,
                "pending_hearings": 6,
                "total_clients": 35
            },
            "urgent_cases": [
                {
                    "id": "C-2024-156",
                    "priority": "High",
                    "client_name": "John Doe",
                    "deadline": "Dec 15, 2024",
                    "hours_billed": 24,
                    "progress": 75
                },
                {
                    "id": "C-2024-157",
                    "priority": "Medium",
                    "client_name": "Jane Smith",
                    "deadline": "Dec 20, 2024",
                    "hours_billed": 18,
                    "progress": 60
                },
                {
                    "id": "C-2024-158",
                    "priority": "High",
                    "client_name": "Raj Kumar",
                    "deadline": "Dec 12, 2024",
                    "hours_billed": 32,
                    "progress": 85
                },
                {
                    "id": "C-2024-159",
                    "priority": "Medium",
                    "client_name": "Priya Singh",
                    "deadline": "Dec 22, 2024",
                    "hours_billed": 15,
                    "progress": 45
                }
            ],
            "performance": {
                "cases_won": 24,
                "cases_total": 29,
                "avg_resolution_months": 3.8,
                "client_rating": 4.9
            },
            "trends": {
                "cases_this_month": 3,
                "win_rate_trend": "Above average",
                "next_hearing_date": "Dec 12, 2024",
                "active_clients": 8
            }
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

# In-memory storage for created cases (in production, use a database)
CITIZEN_CASES_STORAGE: List[Dict] = []
LAWYER_CASES_STORAGE: List[Dict] = []

# In-memory storage for users and lawyers
USERS_STORAGE: List[Dict] = [
    {
        "id": "1",
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@email.com",
        "role": "Citizen",
        "joinDate": "2024-09-15",
        "status": "Active",
        "casesInvolved": 2,
        "password": "demo123"  # In production, use hashed passwords
    },
    {
        "id": "2",
        "name": "Priya Patel",
        "email": "priya.patel@email.com",
        "role": "Citizen",
        "joinDate": "2024-11-10",
        "status": "Pending",
        "casesInvolved": 0,
        "password": "demo123"
    },
]

LAWYERS_STORAGE: List[Dict] = [
    {
        "id": "1",
        "name": "Adv. Sharma",
        "email": "sharma.law@email.com",
        "specialization": "Criminal Law",
        "verificationStatus": "Verified",
        "casesSolved": 45,
        "winRate": 87,
        "joinDate": "2024-08-20",
        "location": "Delhi",
        "rating": 4.8,
        "reviews": 32,
        "specializations": ["Bail", "Appeals", "Evidence"],
        "yearsExp": 12,
        "cases": 45,
        "password": "demo123",
        "phone": "+91-9876543201",
        "bio": "Criminal defense specialist with strong trial and bail experience.",
        "profileImage": ""
    },
    {
        "id": "2",
        "name": "Adv. Kumar",
        "email": "kumar.law@email.com",
        "specialization": "Bail & Remand",
        "verificationStatus": "Verified",
        "casesSolved": 32,
        "winRate": 82,
        "joinDate": "2024-09-15",
        "location": "Mumbai",
        "rating": 4.9,
        "reviews": 28,
        "specializations": ["Constitutional", "Appeals", "FIR Defense"],
        "yearsExp": 15,
        "cases": 38,
        "password": "demo123",
        "phone": "+91-9876543202",
        "bio": "Focuses on remand, constitutional challenges, and appellate strategy.",
        "profileImage": ""
    },
    {
        "id": "3",
        "name": "Adv. Singh",
        "email": "singh.law@email.com",
        "specialization": "Appeals",
        "verificationStatus": "Pending",
        "casesSolved": 0,
        "winRate": 0,
        "joinDate": "2024-11-01",
        "location": "Bangalore",
        "rating": 0,
        "reviews": 0,
        "specializations": ["Appeals"],
        "yearsExp": 5,
        "cases": 0,
        "password": "demo123",
        "phone": "+91-9876543203",
        "bio": "Early-career advocate handling criminal appeals and legal research.",
        "profileImage": ""
    },
]

LAWYER_IMAGES_DIR = Path("data/lawyer_images")
LAWYER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# In-memory storage for lawyer-client relationships
LAWYER_CLIENTS_STORAGE: List[Dict] = [
    {
        "lawyerId": "1",
        "clientId": "1",
        "clientName": "Rajesh Kumar",
        "clientEmail": "rajesh.kumar@email.com",
        "clientPhone": "+91-9876543210",
        "caseType": "Bail Application",
        "status": "Active",
        "activeCases": 1,
        "totalCases": 2,
        "caseId": "FIR/2024/150",
        "firNumber": "FIR-150/2024",
        "court": "High Court, Delhi",
        "policeStation": "Model Town PS",
        "caseStage": "Bail Hearing",
        "riskLevel": "Medium",
        "priority": "High",
        "nextHearing": "2026-05-02",
        "lastContactDate": "2026-04-12",
        "assignedDate": "2026-01-18",
        "outstandingAmount": 35000,
        "notes": "Client cooperative. Need certified FIR copy before next hearing.",
        "city": "Delhi"
    },
    {
        "lawyerId": "1",
        "clientId": "2",
        "clientName": "Priya Sharma",
        "clientEmail": "priya.sharma@email.com",
        "clientPhone": "+91-9876543211",
        "caseType": "Appeal",
        "status": "Active",
        "activeCases": 1,
        "totalCases": 1,
        "caseId": "APL/2025/044",
        "firNumber": "FIR-044/2025",
        "court": "Sessions Court, Delhi",
        "policeStation": "Civil Lines PS",
        "caseStage": "Appeal Drafting",
        "riskLevel": "Low",
        "priority": "Medium",
        "nextHearing": "2026-04-29",
        "lastContactDate": "2026-04-14",
        "assignedDate": "2026-02-05",
        "outstandingAmount": 12000,
        "notes": "Appeal draft shared. Awaiting client approval.",
        "city": "Delhi"
    },
]

# In-memory storage for admin settings
ADMIN_SETTINGS: Dict = {
    "platform_name": "Lawmate",
    "support_email": "support@justiceai.com",
    "max_file_upload_size_mb": 50,
    "email_notifications": True,
    "ai_monitoring": True,
    "auto_backup": True,
    "maintenance_mode": False,
}

@app.get("/api/cases/citizen")
async def get_citizen_cases(status: Optional[str] = None):
    """
    Get all cases for a citizen user
    Can filter by status: active, hearing_scheduled, closed, all
    """
    try:
        # Start with mock data
        all_cases = [
            {
                "id": "FIR/2024/150",
                "case_type": "Bail Application",
                "status": "Active",
                "next_hearing": "2024-12-18",
                "documents_count": 8,
                "assigned_lawyer": "Adv. Sharma",
                "judge": "Hon'ble Justice Reddy",
                "court": "High Court, Delhi",
                "filing_date": "2024-11-15",
                "progress": 65
            },
            {
                "id": "FIR/2024/151",
                "case_type": "Appeal",
                "status": "Hearing Scheduled",
                "next_hearing": "2024-12-22",
                "documents_count": 12,
                "assigned_lawyer": None,
                "judge": "Hon'ble Justice Nair",
                "court": "District Court, Delhi",
                "filing_date": "2024-10-20",
                "progress": 40
            },
            {
                "id": "FIR/2024/152",
                "case_type": "Bail Application",
                "status": "Active",
                "next_hearing": "2024-12-20",
                "documents_count": 5,
                "assigned_lawyer": "Adv. Patel",
                "judge": "Hon'ble Justice Kumar",
                "court": "Sessions Court, Mumbai",
                "filing_date": "2024-11-25",
                "progress": 30
            },
            {
                "id": "FIR/2024/153",
                "case_type": "Revision Petition",
                "status": "Active",
                "next_hearing": "2025-01-05",
                "documents_count": 15,
                "assigned_lawyer": "Adv. Sharma",
                "judge": "Hon'ble Justice Singh",
                "court": "High Court, Mumbai",
                "filing_date": "2024-09-10",
                "progress": 55
            }
        ]
        
        # Add stored cases (created via POST /api/cases) - newest first
        all_cases = CITIZEN_CASES_STORAGE + all_cases
        
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
async def get_lawyer_cases(status: Optional[str] = None):
    """
    Get all cases for a lawyer user
    Can filter by status: active, urgent, closed, all
    """
    try:
        # Start with mock data
        all_cases = [
            {
                "id": "C-2024-156",
                "case_type": "Bail Application",
                "status": "Active",
                "priority": "High",
                "client_name": "John Doe",
                "deadline": "2024-12-15",
                "hours_billed": 24,
                "progress": 75,
                "next_hearing": "2024-12-15",
                "court": "High Court, Delhi",
                "judge": "Hon'ble Justice Reddy"
            },
            {
                "id": "C-2024-157",
                "case_type": "Appeal",
                "status": "Active",
                "priority": "Medium",
                "client_name": "Jane Smith",
                "deadline": "2024-12-20",
                "hours_billed": 18,
                "progress": 60,
                "next_hearing": "2024-12-22",
                "court": "District Court, Delhi",
                "judge": "Hon'ble Justice Nair"
            },
            {
                "id": "C-2024-158",
                "case_type": "Revision Petition",
                "status": "Active",
                "priority": "High",
                "client_name": "Raj Kumar",
                "deadline": "2024-12-12",
                "hours_billed": 32,
                "progress": 85,
                "next_hearing": "2024-12-12",
                "court": "Sessions Court, Mumbai",
                "judge": "Hon'ble Justice Kumar"
            },
            {
                "id": "C-2024-159",
                "case_type": "Bail Application",
                "status": "Active",
                "priority": "Medium",
                "client_name": "Priya Singh",
                "deadline": "2024-12-22",
                "hours_billed": 15,
                "progress": 45,
                "next_hearing": "2024-12-25",
                "court": "High Court, Mumbai",
                "judge": "Hon'ble Justice Singh"
            },
            {
                "id": "C-2024-160",
                "case_type": "Criminal Appeal",
                "status": "Hearing Scheduled",
                "priority": "Low",
                "client_name": "Amit Verma",
                "deadline": "2025-01-10",
                "hours_billed": 28,
                "progress": 50,
                "next_hearing": "2025-01-08",
                "court": "Supreme Court, Delhi",
                "judge": "Hon'ble Justice Mehta"
            }
        ]
        
        # Add stored cases (created via POST /api/cases) - newest first
        all_cases = LAWYER_CASES_STORAGE + all_cases
        
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
        # Mock data - replace with database query later
        case_details = {
            "id": case_id,
            "case_type": "Bail Application",
            "status": "Active",
            "filing_date": "2024-11-15",
            "next_hearing": "2024-12-18",
            "court": "High Court, Delhi",
            "judge": "Hon'ble Justice Reddy",
            "sections": ["302", "34"],
            "police_station": "Central Police Station",
            "fir_number": case_id,
            "client_name": "John Doe",
            "assigned_lawyer": "Adv. Sharma",
            "documents_count": 8,
            "progress": 65,
            "description": "Bail application under Section 302 and 34 of PPC",
            "timeline": [
                {"date": "2024-11-15", "event": "Case filed"},
                {"date": "2024-11-20", "event": "First hearing"},
                {"date": "2024-12-05", "event": "Evidence submitted"},
                {"date": "2024-12-18", "event": "Next hearing scheduled"}
            ]
        }
        
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
            if request.sections:
                new_case["sections"] = request.sections
            if request.police_station:
                new_case["police_station"] = request.police_station
            if request.fir_number:
                new_case["fir_number"] = request.fir_number
        
        # Add lawyer-specific fields
        if user_type == "lawyer":
            new_case["client_name"] = request.client_name or "Client"
            new_case["priority"] = request.priority or "Medium"
            new_case["deadline"] = request.next_hearing or None
            new_case["hours_billed"] = 0
        
        # Store the case in memory (in production, save to database)
        if user_type == "lawyer":
            LAWYER_CASES_STORAGE.append(new_case)
            print(f"✅ Case created and stored: {case_id} (lawyer) - Total cases: {len(LAWYER_CASES_STORAGE)}")
        else:
            CITIZEN_CASES_STORAGE.append(new_case)
            print(f"✅ Case created and stored: {case_id} (citizen) - Total cases: {len(CITIZEN_CASES_STORAGE)}")
        
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
        total_citizen_cases = len(CITIZEN_CASES_STORAGE)
        total_lawyer_cases = len(LAWYER_CASES_STORAGE)
        total_cases = total_citizen_cases + total_lawyer_cases
        
        # Mock data for now (in production, calculate from database)
        dashboard_data = {
            "metrics": {
                "total_users": 2340,
                "verified_lawyers": 456,
                "active_cases": 1203 + total_cases,  # Include stored cases
                "pending_reviews": 23
            },
            "recent_activity": [
                {
                    "action": "New user registration",
                    "user": "Priya Patel",
                    "time": "2 min ago",
                    "type": "info",
                    "detail": "Registered as citizen"
                },
                {
                    "action": "Lawyer profile verified",
                    "user": "Adv. Kumar",
                    "time": "15 min ago",
                    "type": "success",
                    "detail": "All documents verified"
                },
                {
                    "action": "AI response flagged",
                    "user": "System",
                    "time": "1 hour ago",
                    "type": "warning",
                    "detail": "Manual review required"
                },
                {
                    "action": "Case moderation completed",
                    "user": "Admin",
                    "time": "2 hours ago",
                    "type": "success",
                    "detail": "Approved for listing"
                }
            ],
            "system_status": [
                {
                    "service": "API Server",
                    "status": "Operational",
                    "uptime": "99.95%"
                },
                {
                    "service": "Database",
                    "status": "Operational",
                    "uptime": "99.99%"
                },
                {
                    "service": "AI Service",
                    "status": "Operational",
                    "uptime": "99.87%"
                },
                {
                    "service": "Storage",
                    "status": "Operational",
                    "uptime": "100%"
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
        return ADMIN_SETTINGS
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
        # Update only provided fields
        if request.platform_name is not None:
            ADMIN_SETTINGS["platform_name"] = request.platform_name
        if request.support_email is not None:
            ADMIN_SETTINGS["support_email"] = request.support_email
        if request.max_file_upload_size_mb is not None:
            ADMIN_SETTINGS["max_file_upload_size_mb"] = request.max_file_upload_size_mb
        if request.email_notifications is not None:
            ADMIN_SETTINGS["email_notifications"] = request.email_notifications
        if request.ai_monitoring is not None:
            ADMIN_SETTINGS["ai_monitoring"] = request.ai_monitoring
        if request.auto_backup is not None:
            ADMIN_SETTINGS["auto_backup"] = request.auto_backup
        if request.maintenance_mode is not None:
            ADMIN_SETTINGS["maintenance_mode"] = request.maintenance_mode
        
        print(f"✅ Admin settings updated: {ADMIN_SETTINGS}")
        
        return {
            "success": True,
            "settings": ADMIN_SETTINGS,
            "message": "Settings updated successfully"
        }
    except Exception as e:
        import traceback
        print(f"Error updating admin settings: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error updating admin settings: {str(e)}")

@app.get("/api/analytics/lawyer")
async def get_lawyer_analytics():
    """
    Get analytics data for lawyer users
    Returns case performance metrics, outcomes, and success rates
    """
    try:
        # Calculate from stored cases and mock data
        # In production, this would query the database
        total_cases = len(LAWYER_CASES_STORAGE)
        
        # Mock data for now (in production, calculate from actual case data)
        analytics_data = {
            "case_outcomes": [
                { "month": "Jan", "won": 4, "lost": 1, "pending": 2 },
                { "month": "Feb", "won": 3, "lost": 0, "pending": 3 },
                { "month": "Mar", "won": 5, "lost": 1, "pending": 2 },
                { "month": "Apr", "won": 4, "lost": 1, "pending": 3 },
                { "month": "May", "won": 6, "lost": 0, "pending": 2 },
                { "month": "Jun", "won": 5, "lost": 2, "pending": 1 },
            ],
            "case_type_performance": [
                { "type": "Bail", "count": 15, "winRate": 87 },
                { "type": "Appeal", "count": 12, "winRate": 75 },
                { "type": "Remand", "count": 8, "winRate": 62 },
                { "type": "Evidence", "count": 10, "winRate": 80 },
            ],
            "summary_metrics": {
                "avg_resolution_time_months": 4.2,
                "client_satisfaction": 4.8,
                "case_success_rate": 78,
                "total_cases": 45 + total_cases,  # Include stored cases
                "cases_won": 24,
                "cases_lost": 5,
                "cases_pending": 16
            },
            "trends": {
                "resolution_time_change": -0.3,  # months
                "satisfaction_change": 0.2,  # points
                "success_rate_change": 5  # percentage
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
        # Demo mode: accept any credentials
        if request.userType == "admin":
            return {
                "success": True,
                "user": {
                    "id": "admin-1",
                    "name": "Admin User",
                    "email": request.email,
                    "role": "Admin",
                    "userType": "admin"
                },
                "message": "Login successful"
            }
        elif request.userType == "lawyer":
            lawyer = next((l for l in LAWYERS_STORAGE if l["email"] == request.email), None)
            if lawyer:
                return {
                    "success": True,
                    "user": {
                        "id": lawyer["id"],
                        "name": lawyer["name"],
                        "email": lawyer["email"],
                        "role": "Lawyer",
                        "userType": "lawyer",
                        "verificationStatus": lawyer["verificationStatus"]
                    },
                    "message": "Login successful"
                }
        elif request.userType == "citizen":
            user = next((u for u in USERS_STORAGE if u["email"] == request.email), None)
            if user:
                return {
                    "success": True,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                        "role": "Citizen",
                        "userType": "citizen",
                        "status": user["status"]
                    },
                    "message": "Login successful"
                }
        
        # Demo mode: create temporary user if not found
        return {
            "success": True,
            "user": {
                "id": f"temp-{request.userType}-{len(USERS_STORAGE) + 1}",
                "name": request.email.split("@")[0],
                "email": request.email,
                "role": request.userType.capitalize(),
                "userType": request.userType
            },
            "message": "Login successful (demo mode)"
        }
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
        
        # Check if email already exists
        existing_user = next((u for u in USERS_STORAGE if u["email"] == request.email), None)
        existing_lawyer = next((l for l in LAWYERS_STORAGE if l["email"] == request.email), None)
        
        if existing_user or existing_lawyer:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if request.userType == "lawyer":
            new_lawyer = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email,
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
                "password": request.password,
                "phone": ""
            }
            LAWYERS_STORAGE.append(new_lawyer)
            print(f"✅ New lawyer registered: {request.email}")
            return {
                "success": True,
                "user": {
                    "id": new_lawyer["id"],
                    "name": new_lawyer["name"],
                    "email": new_lawyer["email"],
                    "role": "Lawyer",
                    "userType": "lawyer",
                    "verificationStatus": "Pending"
                },
                "message": "Account created successfully. Verification pending."
            }
        else:  # citizen
            new_user = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email,
                "role": "Citizen",
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active",
                "casesInvolved": 0,
                "password": request.password
            }
            USERS_STORAGE.append(new_user)
            print(f"✅ New user registered: {request.email}")
            return {
                "success": True,
                "user": {
                    "id": new_user["id"],
                    "name": new_user["name"],
                    "email": new_user["email"],
                    "role": "Citizen",
                    "userType": "citizen",
                    "status": "Active"
                },
                "message": "Account created successfully"
            }
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
        users = USERS_STORAGE.copy()
        for lawyer in LAWYERS_STORAGE:
            users.append({
                "id": lawyer["id"],
                "name": lawyer["name"],
                "email": lawyer["email"],
                "role": "Lawyer",
                "joinDate": lawyer["joinDate"],
                "status": lawyer["verificationStatus"],
                "casesInvolved": lawyer.get("cases", 0)
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
        existing = next((u for u in USERS_STORAGE if u["email"] == request.email), None)
        existing_lawyer = next((l for l in LAWYERS_STORAGE if l["email"] == request.email), None)
        if existing or existing_lawyer:
            raise HTTPException(status_code=400, detail="Email already exists")
        if request.role == "Lawyer":
            new_lawyer = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email,
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
                "password": request.password,
                "phone": ""
            }
            LAWYERS_STORAGE.append(new_lawyer)
            return {"success": True, "user": new_lawyer, "message": "Lawyer created successfully"}
        else:
            new_user = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email,
                "role": "Citizen",
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active",
                "casesInvolved": 0,
                "password": request.password
            }
            USERS_STORAGE.append(new_user)
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
        user = next((u for u in USERS_STORAGE if u["id"] == user_id), None)
        if user:
            user.update(updates)
            return {"success": True, "user": user, "message": "User updated successfully"}
        lawyer = next((l for l in LAWYERS_STORAGE if l["id"] == user_id), None)
        if lawyer:
            lawyer.update(updates)
            return {"success": True, "user": lawyer, "message": "Lawyer updated successfully"}
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
        user_index = next((i for i, u in enumerate(USERS_STORAGE) if u["id"] == user_id), None)
        if user_index is not None:
            USERS_STORAGE.pop(user_index)
            return {"success": True, "message": "User deleted successfully"}
        lawyer_index = next((i for i, l in enumerate(LAWYERS_STORAGE) if l["id"] == user_id), None)
        if lawyer_index is not None:
            LAWYERS_STORAGE.pop(lawyer_index)
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
        return {"lawyers": LAWYERS_STORAGE, "total": len(LAWYERS_STORAGE)}
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
        existing = next((l for l in LAWYERS_STORAGE if l["email"] == request.email), None)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        new_lawyer = {
            "id": str(uuid.uuid4())[:8],
            "name": request.name,
            "email": request.email,
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
            "password": request.password,
            "phone": request.phone or "",
            "bio": request.bio or "",
            "profileImage": request.profileImage or ""
        }
        LAWYERS_STORAGE.append(new_lawyer)
        return {"success": True, "lawyer": new_lawyer, "message": "Lawyer created successfully"}
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
        lawyer = next((l for l in LAWYERS_STORAGE if l["id"] == lawyer_id), None)
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        lawyer["verificationStatus"] = status
        return {"success": True, "lawyer": lawyer, "message": f"Lawyer {status.lower()} successfully"}
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
        lawyer = next((l for l in LAWYERS_STORAGE if l["id"] == lawyer_id), None)
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")

        update_data = request.dict(exclude_unset=True)

        # Email uniqueness check when email is changed
        if "email" in update_data and update_data["email"] != lawyer.get("email"):
            duplicate = next((l for l in LAWYERS_STORAGE if l["email"] == update_data["email"] and l["id"] != lawyer_id), None)
            if duplicate:
                raise HTTPException(status_code=400, detail="Email already exists")

        for key, value in update_data.items():
            if value is not None:
                lawyer[key] = value

        # Keep derived fields aligned for existing UI compatibility
        if "casesSolved" in update_data:
            lawyer["cases"] = lawyer.get("casesSolved", lawyer.get("cases", 0))

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
        lawyer_index = next((i for i, l in enumerate(LAWYERS_STORAGE) if l["id"] == lawyer_id), None)
        if lawyer_index is None:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        LAWYERS_STORAGE.pop(lawyer_index)
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
        lawyer = next((l for l in LAWYERS_STORAGE if l["id"] == lawyer_id), None)
        if not lawyer:
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
        lawyer["profileImage"] = image_url
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
        if lawyer_id:
            clients = [c for c in LAWYER_CLIENTS_STORAGE if c["lawyerId"] == lawyer_id]
        else:
            clients = LAWYER_CLIENTS_STORAGE
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

        if not any(l.get("id") == request.lawyerId for l in LAWYERS_STORAGE):
            raise HTTPException(status_code=404, detail="Lawyer not found")

        import uuid
        from datetime import datetime

        client_id = f"cli-{str(uuid.uuid4())[:8]}"
        LAWYER_CLIENTS_STORAGE.append({
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
        entries = [c for c in LAWYER_CLIENTS_STORAGE if c.get("clientId") == client_id]
        if lawyer_id:
            entries = [c for c in entries if c.get("lawyerId") == lawyer_id]

        cases = [c for c in entries if c.get("caseId")]
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

        client_entries = [
            c for c in LAWYER_CLIENTS_STORAGE
            if c.get("lawyerId") == request.lawyerId and c.get("clientId") == client_id
        ]
        if not client_entries:
            raise HTTPException(status_code=404, detail="Client not found for this lawyer")

        import uuid
        from datetime import datetime

        new_case_id = f"LC-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:6].upper()}"
        base = client_entries[0]
        new_outstanding = float(request.outstandingAmount or 0)

        LAWYER_CLIENTS_STORAGE.append({
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

        # Refresh aggregate counters and summary snapshot on all entries for this client.
        all_entries = [
            c for c in LAWYER_CLIENTS_STORAGE
            if c.get("lawyerId") == request.lawyerId and c.get("clientId") == client_id
        ]
        total_cases = len([c for c in all_entries if c.get("caseId")])
        active_cases = len([c for c in all_entries if c.get("caseId") and c.get("status", "Active") != "Closed"])
        total_outstanding = float(sum(float(c.get("outstandingAmount", 0) or 0) for c in all_entries if c.get("caseId")))

        latest_case = next((c for c in reversed(all_entries) if c.get("caseId")), None)
        for entry in all_entries:
            entry["totalCases"] = total_cases
            entry["activeCases"] = active_cases
            entry["outstandingAmount"] = total_outstanding
            if latest_case:
                entry["caseType"] = latest_case.get("caseType", entry.get("caseType", ""))
                entry["status"] = latest_case.get("status", entry.get("status", "Active"))
                entry["caseId"] = latest_case.get("caseId", entry.get("caseId", ""))
                entry["firNumber"] = latest_case.get("firNumber", entry.get("firNumber", ""))
                entry["court"] = latest_case.get("court", entry.get("court", ""))
                entry["policeStation"] = latest_case.get("policeStation", entry.get("policeStation", ""))
                entry["caseStage"] = latest_case.get("caseStage", entry.get("caseStage", "Initial Review"))
                entry["riskLevel"] = latest_case.get("riskLevel", entry.get("riskLevel", "Medium"))
                entry["priority"] = latest_case.get("priority", entry.get("priority", "Medium"))
                entry["nextHearing"] = latest_case.get("nextHearing", entry.get("nextHearing", ""))
                if latest_case.get("notes"):
                    entry["notes"] = latest_case.get("notes")
            entry["lastContactDate"] = datetime.now().strftime("%Y-%m-%d")

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
        verified_lawyers = [l for l in LAWYERS_STORAGE if l.get("verificationStatus") == "Verified"]
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
async def get_lawyers_for_citizens(search: Optional[str] = None, specialization: Optional[str] = None):
    """Get list of verified lawyers for citizens to browse"""
    try:
        lawyers = [l for l in LAWYERS_STORAGE if l["verificationStatus"] == "Verified"]
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
        lawyer = next((l for l in LAWYERS_STORAGE if l["id"] == lawyer_id), None)
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

