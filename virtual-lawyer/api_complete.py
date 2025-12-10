"""
Complete Legal AI API
Includes: Risk Analysis, Case Prediction, Advanced Analysis, and Chatbot
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from bson import ObjectId
import uvicorn
import sys
from pathlib import Path
import shutil
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# MongoDB imports
from database.models import UserModel, LawyerModel, CaseModel, LawyerClientModel, AdminSettingsModel
from database.connection import init_database, check_connection
import bcrypt

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

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Utility: sanitize Mongo docs (remove _id and convert ObjectId to str)
def sanitize_docs(docs: List[Dict]):
    sanitized = []
    for d in docs:
        if not isinstance(d, dict):
            continue
        doc = dict(d)
        doc.pop("_id", None)
        for k, v in list(doc.items()):
            if isinstance(v, ObjectId):
                doc[k] = str(v)
        sanitized.append(doc)
    return sanitized

# Utility: sanitize Mongo docs (remove _id and convert ObjectId to str)
def sanitize_docs(docs: List[Dict]):
    sanitized = []
    for d in docs:
        if not isinstance(d, dict):
            continue
        doc = dict(d)
        doc.pop("_id", None)
        for k, v in list(doc.items()):
            if isinstance(v, ObjectId):
                doc[k] = str(v)
        sanitized.append(doc)
    return sanitized

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
    # IDs should come from auth token in a real app; keeping optional for now
    userId: Optional[str] = None
    lawyerId: Optional[str] = None
    userEmail: Optional[str] = None
    lawyerEmail: Optional[str] = None

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
            "validator": validator is not None,
            "mongodb": await check_connection()
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
async def get_citizen_dashboard(user_id: Optional[str] = None):
    """
    Get dashboard data for citizen users (MongoDB only)
    """
    try:
        filter_dict = {"userId": {"$exists": True}}
        if user_id:
            filter_dict["userId"] = user_id

        cases = sanitize_docs(await CaseModel.find_all(filter_dict))
        active_cases = len([c for c in cases if c.get("status") == "Active"])
        pending_hearings = len([c for c in cases if c.get("next_hearing")])
        next_hearing_case = next((c for c in cases if c.get("next_hearing")), None)

        dashboard_data = {
            "stats": {
                "active_cases": active_cases,
                "pending_hearings": pending_hearings,
                "documents": 0,
                "top_lawyers": 0
            },
            "recent_cases": cases,
            "recommendations": [],
            "next_hearing": next_hearing_case,
            "trends": {
                "cases_this_month": 0,
                "documents_this_month": 0,
                "next_hearing_date": next_hearing_case.get("next_hearing") if next_hearing_case else None,
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
    Get dashboard data for lawyer users (MongoDB only)
    """
    try:
        filter_dict = {"lawyerId": {"$exists": True}}
        if lawyer_id:
            filter_dict["lawyerId"] = lawyer_id

        cases = sanitize_docs(await CaseModel.find_all(filter_dict))
        active_cases = len([c for c in cases if c.get("status") == "Active"])
        hearings = [c for c in cases if c.get("next_hearing")]
        urgent_cases = [c for c in cases if c.get("priority") == "High"]

        dashboard_data = {
            "metrics": {
                "active_cases": active_cases,
                "win_rate": 0,
                "pending_hearings": len(hearings),
                "total_clients": 0
            },
            "urgent_cases": urgent_cases,
            "performance": {
                "cases_won": 0,
                "cases_total": len(cases),
                "avg_resolution_months": 0,
                "client_rating": 0
            },
            "trends": {
                "cases_this_month": 0,
                "win_rate_trend": "N/A",
                "next_hearing_date": urgent_cases[0].get("next_hearing") if urgent_cases else None,
                "active_clients": 0
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

# ============================================================
# NOTE: Hardcoded data has been migrated to MongoDB
# The following data is kept for reference only
# All endpoints now use MongoDB via database.models
# ============================================================

# DEPRECATED: In-memory storage (migrated to MongoDB)
# CITIZEN_CASES_STORAGE: List[Dict] = []
# LAWYER_CASES_STORAGE: List[Dict] = []

# DEPRECATED: In-memory storage (migrated to MongoDB)
# USERS_STORAGE: List[Dict] = [
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
# ]

# DEPRECATED: In-memory storage (migrated to MongoDB)
# LAWYERS_STORAGE: List[Dict] = [
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
        "phone": "+91-9876543201"
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
        "phone": "+91-9876543202"
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
        "phone": "+91-9876543203"
    },
# ]

# DEPRECATED: In-memory storage (migrated to MongoDB)
# LAWYER_CLIENTS_STORAGE: List[Dict] = [
    {
        "lawyerId": "1",
        "clientId": "1",
        "clientName": "Rajesh Kumar",
        "clientEmail": "rajesh.kumar@email.com",
        "clientPhone": "+91-9876543210",
        "caseType": "Bail Application",
        "status": "Active",
        "activeCases": 1,
        "totalCases": 2
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
        "totalCases": 1
    },
# ]

# DEPRECATED: In-memory storage (migrated to MongoDB)
# ADMIN_SETTINGS: Dict = {
#     "platform_name": "Lawmate",
#     "support_email": "support@justiceai.com",
#     "max_file_upload_size_mb": 50,
#     "email_notifications": True,
#     "ai_monitoring": True,
#     "auto_backup": True,
#     "maintenance_mode": False,
# }

@app.get("/api/cases/citizen")
async def get_citizen_cases(status: Optional[str] = None, user_id: Optional[str] = None, user_email: Optional[str] = None):
    """
    Get all cases for a citizen user
    Can filter by status: active, hearing_scheduled, closed, all
    """
    try:
        # Get cases from MongoDB (filter by userId if available, otherwise get all citizen cases)
        # Note: In a real app, you'd pass userId from auth token
        or_filters = []
        if user_id:
            or_filters.append({"userId": user_id})
        if user_email:
            or_filters.append({"userEmail": user_email.lower()})
        if or_filters:
            filter_dict = {"$or": or_filters}
        else:
            filter_dict = {"userId": {"$exists": True}}

        all_cases = sanitize_docs(await CaseModel.find_all(filter_dict))
        
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
async def get_lawyer_cases(status: Optional[str] = None, lawyer_id: Optional[str] = None, lawyer_email: Optional[str] = None):
    """
    Get all cases for a lawyer user
    Can filter by status: active, urgent, closed, all
    """
    try:
        # Get cases from MongoDB (filter by lawyerId if provided)
        or_filters = []
        if lawyer_id:
            or_filters.append({"lawyerId": lawyer_id})
        if lawyer_email:
            or_filters.append({"lawyerEmail": lawyer_email.lower()})
        if or_filters:
            filter_dict = {"$or": or_filters}
        else:
            filter_dict = {"lawyerId": {"$exists": True}}

        all_cases = sanitize_docs(await CaseModel.find_all(filter_dict))
        
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
        case_details = await CaseModel.find_by_id(case_id)
        if not case_details:
            raise HTTPException(status_code=404, detail="Case not found")
        case_details.pop("_id", None)
        for k, v in list(case_details.items()):
            if isinstance(v, ObjectId):
                case_details[k] = str(v)
        return case_details
    except Exception as e:
        import traceback
        print(f"Error getting case details: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting case details: {str(e)}")

@app.post("/api/cases")
async def create_case(
    request: CreateCaseRequest,
    user_type: str = "citizen",
    user_id: Optional[str] = None,
    lawyer_id: Optional[str] = None,
    user_email: Optional[str] = None,
    lawyer_email: Optional[str] = None
):
    """
    Create a new case
    user_type: "citizen" or "lawyer"
    """
    try:
        from datetime import datetime
        import uuid
        
        # allow query params if body missing, also allow lookup by email
        req_user_id = request.userId or user_id
        req_lawyer_id = request.lawyerId or lawyer_id

        req_user_email = (request.userEmail or user_email or "").lower() if (request.userEmail or user_email) else None
        req_lawyer_email = (request.lawyerEmail or lawyer_email or "").lower() if (request.lawyerEmail or lawyer_email) else None

        # If missing IDs, try to resolve by email
        if user_type == "citizen" and not req_user_id and req_user_email:
            user_doc = await UserModel.find_by_email(req_user_email)
            if user_doc:
                req_user_id = user_doc.get("id")
        if user_type == "lawyer" and not req_lawyer_id and req_lawyer_email:
            lawyer_doc = await LawyerModel.find_by_email(req_lawyer_email)
            if lawyer_doc:
                req_lawyer_id = lawyer_doc.get("id")

        # Require an owner id (but allow fallback to email; as last resort, generate a temp id)
        if user_type == "citizen" and not req_user_id:
            if req_user_email:
                req_user_id = f"email-{req_user_email}"
            else:
                req_user_id = f"anon-{uuid.uuid4()}"
        if user_type == "lawyer" and not req_lawyer_id:
            if req_lawyer_email:
                req_lawyer_id = f"email-{req_lawyer_email}"
            else:
                req_lawyer_id = f"anon-{uuid.uuid4()}"

        # Generate unique case ID
        async def generate_case_id():
            if user_type == "lawyer":
                return f"C-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:6]}"
            if request.fir_number:
                return request.fir_number
            return f"FIR/{datetime.now().strftime('%Y')}/{str(uuid.uuid4())[:6]}"

        case_id = await generate_case_id()
        # Ensure uniqueness
        while await CaseModel.find_by_id(case_id):
            case_id = await generate_case_id()
        
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
            new_case["userId"] = req_user_id
            if req_user_email:
                new_case["userEmail"] = req_user_email
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
            new_case["lawyerId"] = req_lawyer_id
            if req_lawyer_email:
                new_case["lawyerEmail"] = req_lawyer_email
        
        # Store the case in MongoDB
        await CaseModel.create(new_case)
        print(f"✅ Case created and stored in MongoDB: {case_id} ({user_type})")
        
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
        total_citizen_cases = await CaseModel.count({"userId": {"$exists": True}})
        total_lawyer_cases = await CaseModel.count({"lawyerId": {"$exists": True}})
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
        settings = await AdminSettingsModel.get_settings()
        if not settings:
            # Initialize default settings if not exists
            settings = await AdminSettingsModel.initialize_default_settings()
        # Remove MongoDB _id from response
        settings.pop("_id", None)
        return settings
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
        # Prepare update data (only non-None fields)
        update_data = {}
        if request.platform_name is not None:
            update_data["platform_name"] = request.platform_name
        if request.support_email is not None:
            update_data["support_email"] = request.support_email
        if request.max_file_upload_size_mb is not None:
            update_data["max_file_upload_size_mb"] = request.max_file_upload_size_mb
        if request.email_notifications is not None:
            update_data["email_notifications"] = request.email_notifications
        if request.ai_monitoring is not None:
            update_data["ai_monitoring"] = request.ai_monitoring
        if request.auto_backup is not None:
            update_data["auto_backup"] = request.auto_backup
        if request.maintenance_mode is not None:
            update_data["maintenance_mode"] = request.maintenance_mode
        
        # Update in MongoDB
        updated_settings = await AdminSettingsModel.update_settings(update_data)
        updated_settings.pop("_id", None)
        updated_settings.pop("password", None)  # Remove password if exists
        
        print(f"✅ Admin settings updated in MongoDB")
        
        return {
            "success": True,
            "settings": updated_settings,
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
        total_cases = await CaseModel.count({"lawyerId": {"$exists": True}})
        
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
    specialization: Optional[str] = None
    specializations: Optional[List[str]] = None
    location: Optional[str] = None
    yearsExp: Optional[int] = None

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login endpoint - validates credentials and returns user info"""
    try:
        # Admin login (demo mode - no password check)
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
        
        # Lawyer login with password verification
        elif request.userType == "lawyer":
            lawyer = await LawyerModel.find_by_email(request.email.lower())
            if lawyer:
                # Verify password
                if bcrypt.checkpw(request.password.encode('utf-8'), lawyer["password"].encode('utf-8')):
                    return {
                        "success": True,
                        "user": {
                            "id": lawyer["id"],
                            "name": lawyer["name"],
                            "email": lawyer["email"],
                            "role": "Lawyer",
                            "userType": "lawyer",
                            "verificationStatus": lawyer.get("verificationStatus", "Pending")
                        },
                        "message": "Login successful"
                    }
                else:
                    raise HTTPException(status_code=401, detail="Invalid email or password")
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Citizen login with password verification
        elif request.userType == "citizen":
            user = await UserModel.find_by_email(request.email.lower())
            if user:
                # Verify password
                if bcrypt.checkpw(request.password.encode('utf-8'), user["password"].encode('utf-8')):
                    return {
                        "success": True,
                        "user": {
                            "id": user["id"],
                            "name": user["name"],
                            "email": user["email"],
                            "role": "Citizen",
                            "userType": "citizen",
                            "status": user.get("status", "Active")
                        },
                        "message": "Login successful"
                    }
                else:
                    raise HTTPException(status_code=401, detail="Invalid email or password")
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password")
        else:
            raise HTTPException(status_code=400, detail="Invalid user type")
            
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
        
        # Check if email already exists in MongoDB
        existing_user = await UserModel.find_by_email(request.email.lower())
        existing_lawyer = await LawyerModel.find_by_email(request.email.lower())
        
        if existing_user or existing_lawyer:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), salt).decode('utf-8')
        
        if request.userType == "lawyer":
            new_lawyer = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email.lower(),
                "password": hashed_password,
                "specialization": request.specialization or "General Practice",
                "verificationStatus": "Pending",
                "casesSolved": 0,
                "casesHandled": 0,
                "winRate": 0,
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "location": request.location or "Not specified",
                "rating": 0.0,
                "reviews": 0,
                "specializations": request.specializations or [],
                "yearsExp": request.yearsExp or 0,
                "cases": 0,
                "phone": ""
            }
            await LawyerModel.create(new_lawyer)
            print(f"✅ New lawyer registered: {request.email}")
            return {
                "success": True,
                "user": {
                    "id": new_lawyer["id"],
                    "name": new_lawyer["name"],
                    "email": new_lawyer["email"],
                    "role": "Lawyer",
                    "userType": "lawyer",
                "verificationStatus": "Pending",
                "specialization": new_lawyer["specialization"],
                "location": new_lawyer["location"],
                "yearsExp": new_lawyer["yearsExp"],
                "winRate": new_lawyer["winRate"],
                "casesHandled": new_lawyer["casesHandled"]
                },
                "message": "Account created successfully. Verification pending."
            }
        else:  # citizen
            new_user = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email.lower(),
                "password": hashed_password,
                "role": "Citizen",
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active",
                "casesInvolved": 0,
                "phone": None
            }
            await UserModel.create(new_user)
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
        # Get all users and lawyers from MongoDB
        users_list = await UserModel.find_all()
        lawyers_list = await LawyerModel.find_all()
        
        # Format users
        users = []
        for user in users_list:
            users.append({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": "Citizen",
                "joinDate": user.get("joinDate", ""),
                "status": user.get("status", "Active"),
                "casesInvolved": user.get("casesInvolved", 0)
            })
        
        # Format lawyers
        for lawyer in lawyers_list:
            users.append({
                "id": lawyer["id"],
                "name": lawyer["name"],
                "email": lawyer["email"],
                "role": "Lawyer",
                "joinDate": lawyer.get("joinDate", ""),
                "status": lawyer.get("verificationStatus", "Pending"),
                "casesInvolved": lawyer.get("cases", 0)
            })
        
        # Filter by search if provided
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
        
        # Check if email already exists
        existing_user = await UserModel.find_by_email(request.email.lower())
        existing_lawyer = await LawyerModel.find_by_email(request.email.lower())
        if existing_user or existing_lawyer:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), salt).decode('utf-8')
        
        if request.role == "Lawyer":
            new_lawyer = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email.lower(),
                "password": hashed_password,
                "specialization": "General Practice",
                "verificationStatus": "Pending",
                "casesSolved": 0,
                "winRate": 0,
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "location": "Not specified",
                "rating": 0.0,
                "reviews": 0,
                "specializations": [],
                "yearsExp": 0,
                "cases": 0,
                "phone": ""
            }
            await LawyerModel.create(new_lawyer)
            # Remove password from response
            new_lawyer.pop("password", None)
            return {"success": True, "user": new_lawyer, "message": "Lawyer created successfully"}
        else:
            new_user = {
                "id": str(uuid.uuid4())[:8],
                "name": request.name,
                "email": request.email.lower(),
                "password": hashed_password,
                "role": "Citizen",
                "joinDate": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active",
                "casesInvolved": 0,
                "phone": None
            }
            await UserModel.create(new_user)
            # Remove password from response
            new_user.pop("password", None)
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
        # Hash password if provided
        if "password" in updates:
            salt = bcrypt.gensalt()
            updates["password"] = bcrypt.hashpw(updates["password"].encode('utf-8'), salt).decode('utf-8')
        
        # Try to update user
        user = await UserModel.update(user_id, updates)
        if user:
            user.pop("password", None)  # Remove password from response
            user.pop("_id", None)
            return {"success": True, "user": user, "message": "User updated successfully"}
        
        # Try to update lawyer
        lawyer = await LawyerModel.update(user_id, updates)
        if lawyer:
            lawyer.pop("password", None)  # Remove password from response
            lawyer.pop("_id", None)
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
        # Try to delete user
        deleted = await UserModel.delete(user_id)
        if deleted:
            return {"success": True, "message": "User deleted successfully"}
        
        # Try to delete lawyer
        deleted = await LawyerModel.delete(user_id)
        if deleted:
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
        lawyers = await LawyerModel.find_all()
        # Remove passwords from response
        for lawyer in lawyers:
            lawyer.pop("password", None)
            lawyer.pop("_id", None)
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

@app.post("/api/admin/lawyers")
async def create_lawyer(request: CreateLawyerRequest):
    """Create a new lawyer (admin only)"""
    try:
        from datetime import datetime
        import uuid
        existing = await LawyerModel.find_by_email(request.email.lower())
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), salt).decode('utf-8')
        
        new_lawyer = {
            "id": str(uuid.uuid4())[:8],
            "name": request.name,
            "email": request.email.lower(),
            "password": hashed_password,
            "specialization": request.specialization or "General Practice",
            "verificationStatus": "Pending",
            "casesSolved": 0,
            "winRate": 0,
            "joinDate": datetime.now().strftime("%Y-%m-%d"),
            "location": "Not specified",
            "rating": 0.0,
            "reviews": 0,
            "specializations": [],
            "yearsExp": 0,
            "cases": 0,
            "phone": ""
        }
        await LawyerModel.create(new_lawyer)
        new_lawyer.pop("password", None)  # Remove password from response
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
        lawyer = await LawyerModel.update(lawyer_id, {"verificationStatus": status})
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        lawyer.pop("password", None)  # Remove password from response
        lawyer.pop("_id", None)
        return {"success": True, "lawyer": lawyer, "message": f"Lawyer {status.lower()} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error verifying lawyer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error verifying lawyer: {str(e)}")

@app.delete("/api/admin/lawyers/{lawyer_id}")
async def delete_lawyer(lawyer_id: str):
    """Delete a lawyer"""
    try:
        deleted = await LawyerModel.delete(lawyer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        return {"success": True, "message": "Lawyer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error deleting lawyer: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting lawyer: {str(e)}")

# ============================================================
# LAWYER CLIENTS ENDPOINTS
# ============================================================

@app.get("/api/lawyer/clients")
async def get_lawyer_clients(lawyer_id: Optional[str] = None):
    """Get clients for a lawyer"""
    try:
        if lawyer_id:
            clients = await LawyerClientModel.find_by_lawyer_id(lawyer_id)
        else:
            clients = await LawyerClientModel.find_all()
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
                    "totalCases": client["totalCases"]
                }
        return {"clients": list(unique_clients.values()), "total": len(unique_clients)}
    except Exception as e:
        import traceback
        print(f"Error getting lawyer clients: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting clients: {str(e)}")

# ============================================================
# CITIZEN FIND LAWYERS ENDPOINTS
# ============================================================

@app.get("/api/lawyers")
async def get_lawyers_for_citizens(search: Optional[str] = None, specialization: Optional[str] = None):
    """Get list of verified lawyers for citizens to browse"""
    try:
        all_lawyers = await LawyerModel.find_all()
        lawyers = []
        for l in all_lawyers:
            l.pop("password", None)  # Remove password
            l.pop("_id", None)
            lawyers.append(l)
        
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
                "phone": lawyer.get("phone", "")
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
        lawyer = await LawyerModel.find_by_id(lawyer_id)
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
            "verificationStatus": lawyer.get("verificationStatus", "Pending")
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error getting lawyer profile: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting lawyer profile: {str(e)}")

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

