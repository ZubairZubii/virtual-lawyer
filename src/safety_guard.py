"""
Enhanced Safety Guard for Legal AI
Long-term solution: Pattern matching + Semantic intent detection
"""
import re
from typing import Dict, List, Tuple
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using pattern matching only.")

class SafetyGuard:
    """Enhanced safety guard with pattern matching + semantic intent detection"""
    
    def __init__(self):
        """Initialize safety guard with dangerous patterns and semantic model"""
        
        # Dangerous question patterns (expanded)
        self.dangerous_patterns = [
            r'how.*destroy.*evidence',
            r'how.*tamper.*evidence',
            r'how.*avoid.*police',
            r'how.*escape.*arrest',
            r'how.*hide.*crime',
            r'write.*threaten.*message',
            r'write.*blackmail',
            r'how.*kill.*someone',
            r'how.*commit.*murder',
            r'how.*get.*away.*with.*crime',
            r'how.*destroy.*forensic',
            r'how.*remove.*fingerprint',
            r'how.*avoid.*conviction',
            r'help.*commit.*crime',
            r'assist.*illegal',
            # NEW: Expanded patterns for better coverage
            r'how.*avoid.*getting.*caught',
            r'how.*evade.*police',
            r'how.*escape.*punishment',
            r'how.*get.*away.*with.*murder',
            r'how.*avoid.*detection',
            r'how.*conceal.*evidence',
            r'how.*cover.*up.*crime',
        ]
        
        # Dangerous intent examples for semantic matching
        self.dangerous_intent_examples = [
            "How can someone destroy forensic evidence so police cannot trace them?",
            "How to avoid getting caught for murder?",
            "How to escape punishment for a crime?",
            "How to evade law enforcement?",
            "How to conceal evidence of a crime?",
            "How to get away with murder?",
            "How to avoid conviction?",
            "How to destroy evidence?",
            "How to tamper with evidence?",
            "How to escape arrest?",
        ]
        
        # Initialize semantic model if available
        self.semantic_model = None
        self.dangerous_embeddings = None
        if SEMANTIC_AVAILABLE:
            try:
                print("   Loading semantic model for safety guard...")
                self.semantic_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                # Pre-compute embeddings for dangerous intents
                self.dangerous_embeddings = self.semantic_model.encode(
                    self.dangerous_intent_examples,
                    convert_to_tensor=True
                )
                print("   Semantic safety guard initialized!")
            except Exception as e:
                print(f"   Warning: Could not load semantic model: {e}")
                self.semantic_model = None
        
        # Out-of-scope domains (not Pakistani criminal law)
        self.out_of_scope_patterns = [
            r'divorce|marriage|nikah|talaq',
            r'immigration|visa|passport',
            r'tax|income.*tax|sales.*tax',
            r'property.*law|land.*law',
            r'contract.*law|commercial.*law',
            r'family.*law',
            r'constitutional.*law',
            r'administrative.*law',
            r'international.*law',
            r'medical.*law|healthcare.*law',
            r'employment.*law|labor.*law',
            r'corporate.*law|company.*law',
        ]
        
        # Legal domain keywords (Pakistani criminal law)
        self.criminal_law_keywords = [
            'ppc', 'crpc', 'penal code', 'criminal procedure',
            'murder', 'theft', 'robbery', 'bail', 'fir',
            'arrest', 'evidence', 'witness', 'trial',
            'conviction', 'sentence', 'punishment',
            'section 302', 'section 497', 'section 154',
            'qatl', 'dacoity', 'rape', 'assault',
        ]
    
    def _check_semantic_similarity(self, question: str) -> Tuple[bool, float]:
        """
        Check semantic similarity to dangerous intents
        
        Returns:
            (is_dangerous, confidence_score)
        """
        if not self.semantic_model or self.dangerous_embeddings is None:
            return False, 0.0
        
        try:
            # Encode question
            question_embedding = self.semantic_model.encode(question, convert_to_tensor=True)
            
            # Compute similarity to dangerous intents
            similarities = util.cos_sim(question_embedding, self.dangerous_embeddings)[0]
            max_similarity = float(torch.max(similarities))
            
            # Threshold: if similarity > 0.7, consider dangerous
            is_dangerous = max_similarity > 0.7
            
            return is_dangerous, max_similarity
        except Exception as e:
            print(f"Warning: Semantic similarity check error: {e}")
            return False, 0.0
    
    def check_question(self, question: str) -> Dict:
        """
        Enhanced check: Pattern matching + Semantic intent detection
        
        Returns:
            Dict with 'safe', 'in_scope', 'reason', 'suggested_response'
        """
        question_lower = question.lower()
        
        # Check 1: Pattern matching (fast, first pass)
        for pattern in self.dangerous_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return {
                    'safe': False,
                    'in_scope': False,
                    'reason': 'dangerous_question',
                    'suggested_response': "I cannot and will not provide information on how to commit crimes, destroy evidence, or evade law enforcement. I am designed to provide legal information about Pakistani criminal law for educational and informational purposes only. If you have a legitimate legal question, please rephrase it appropriately.",
                    'should_refuse': True,
                    'detection_method': 'pattern'
                }
        
        # Check 2: Semantic intent detection (more robust, catches variations)
        is_dangerous_semantic, similarity_score = self._check_semantic_similarity(question)
        if is_dangerous_semantic:
            return {
                'safe': False,
                'in_scope': False,
                'reason': 'dangerous_question_semantic',
                'suggested_response': "I cannot and will not provide information on how to commit crimes, destroy evidence, or evade law enforcement. I am designed to provide legal information about Pakistani criminal law for educational and informational purposes only. If you have a legitimate legal question, please rephrase it appropriately.",
                'should_refuse': True,
                'detection_method': 'semantic',
                'similarity_score': similarity_score
            }
        
        # Check 3: Out-of-scope domains
        is_criminal_law = any(keyword in question_lower for keyword in self.criminal_law_keywords)
        is_out_of_scope = any(re.search(pattern, question_lower, re.IGNORECASE) for pattern in self.out_of_scope_patterns)
        
        if is_out_of_scope and not is_criminal_law:
            return {
                'safe': True,
                'in_scope': False,
                'reason': 'out_of_scope',
                'suggested_response': "I am trained only in Pakistani Criminal Law (PPC, CrPC, and related criminal procedures). Your question appears to be about a different area of law. Please ask questions related to Pakistani criminal law, such as bail, FIR, evidence, trial procedures, or specific PPC/CrPC sections.",
                'should_refuse': True
            }
        
        # Check 4: Vague or unclear questions
        if len(question.split()) < 3:
            return {
                'safe': True,
                'in_scope': True,
                'reason': 'too_vague',
                'suggested_response': None,
                'should_refuse': False
            }
        
        # Check 5: Questions asking for illegal advice
        illegal_advice_patterns = [
            r'help.*illegal',
            r'assist.*crime',
            r'advice.*commit',
            r'how.*illegal',
        ]
        
        for pattern in illegal_advice_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return {
                    'safe': False,
                    'in_scope': False,
                    'reason': 'illegal_advice_request',
                    'suggested_response': "I cannot provide advice on how to commit illegal acts. I can only provide information about Pakistani criminal law for educational purposes. If you have a legitimate legal question, please rephrase it.",
                    'should_refuse': True
                }
        
        # Question is safe and in scope
        return {
            'safe': True,
            'in_scope': True,
            'reason': 'valid_question',
            'suggested_response': None,
            'should_refuse': False
        }
    
    def should_refuse(self, question: str) -> bool:
        """Quick check if question should be refused"""
        check = self.check_question(question)
        return check.get('should_refuse', False)
    
    def get_refusal_response(self, question: str) -> str:
        """Get appropriate refusal response"""
        check = self.check_question(question)
        return check.get('suggested_response', "I cannot answer this question. Please ask about Pakistani criminal law.")
