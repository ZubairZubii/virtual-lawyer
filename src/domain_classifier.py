"""
Enhanced Legal Domain Classifier
Long-term solution: Check out-of-scope FIRST, then criminal law
"""
import re
from typing import Dict, List

class LegalDomainClassifier:
    """Enhanced domain classifier - out-of-scope first, then criminal law"""
    
    def __init__(self):
        """Initialize domain classifier with priority logic"""
        
        # Out-of-scope domains (CHECKED FIRST)
        self.out_of_scope_domains = {
            'family_law': {
                'keywords': ['divorce', 'marriage', 'nikah', 'talaq', 'khula', 'maintenance', 'custody', 'family law'],
                'priority': 10,  # High priority - refuse immediately
                'patterns': [r'divorce.*law', r'marriage.*law', r'family.*law']
            },
            'tax_law': {
                'keywords': ['tax', 'income tax', 'sales tax', 'fbr', 'taxation', 'file.*tax', 'tax return'],
                'priority': 10,
                'patterns': [r'tax.*law', r'income.*tax', r'file.*tax.*return']
            },
            'property_law': {
                'keywords': ['property', 'land', 'real estate', 'ownership', 'transfer', 'sale deed', 'property law'],
                'priority': 9,
                'patterns': [r'property.*law', r'land.*law', r'property.*transfer']
            },
            'commercial_law': {
                'keywords': ['contract', 'commercial', 'business', 'company', 'corporate', 'commercial law'],
                'priority': 8,
                'patterns': [r'contract.*law', r'commercial.*law']
            },
            'constitutional_law': {
                # Do not use bare "writ" — it matches inside "written" (false constitutional hit).
                'keywords': [
                    'constitutional',
                    'fundamental rights',
                    'article 199',
                    'constitutional law',
                    'writ petition',
                    'writ of',
                ],
                'priority': 7,
                'patterns': [
                    r'constitutional.*law',
                    r'\bwrit petition\b',
                    r'\bwrit of\b',
                    r'\bwrits\b',
                    r'\bwrit\b',  # word-boundary: does not match inside "written"
                ],
            },
            'administrative_law': {
                'keywords': ['administrative', 'government', 'bureaucracy', 'administrative law'],
                'priority': 7,
                'patterns': [r'administrative.*law']
            },
            'immigration_law': {
                'keywords': ['immigration', 'visa', 'passport', 'citizenship', 'immigration law'],
                'priority': 9,
                'patterns': [r'immigration.*law', r'visa.*law']
            },
            'labor_law': {
                'keywords': ['labor', 'employment', 'worker', 'employee', 'labor law'],
                'priority': 8,
                'patterns': [r'labor.*law', r'employment.*law']
            },
            'medical_law': {
                'keywords': ['medical law', 'healthcare law', 'medical malpractice'],
                'priority': 7,
                'patterns': [r'medical.*law', r'healthcare.*law']
            },
        }
        
        # Pakistani Criminal Law keywords (CHECKED SECOND)
        self.criminal_law_keywords = {
            'ppc': ['ppc', 'penal code', 'pakistan penal code'],
            'crpc': ['crpc', 'criminal procedure', 'code of criminal procedure'],
            'sections': ['section 302', 'section 497', 'section 154', 'section 300', 'section 34', 'section 109'],
            'crimes': ['murder', 'qatl', 'theft', 'robbery', 'dacoity', 'rape', 'assault', 'bail', 'fir'],
            'procedures': [
                'arrest',
                'remand',
                'investigation',
                'trial',
                'conviction',
                'sentence',
                'appeal',
                'search warrant',
                'warrant',
                'seizure',
                'raid',
                'police',
            ],
            'evidence': ['evidence', 'witness', 'ocular', 'medical evidence', 'confession', 'dying declaration'],
        }
    
    def classify(self, question: str) -> Dict:
        """
        Enhanced classification: Check out-of-scope FIRST, then criminal law
        
        Returns:
            Dict with 'domain', 'in_scope', 'confidence', 'reason'
        """
        question_lower = question.lower()

        # Explicit statute reference — always in scope for this assistant (CrPC/PPC).
        if re.search(r'\bcrpc\b', question_lower) or re.search(r'\bppc\b', question_lower):
            return {
                'domain': 'pakistani_criminal_law',
                'in_scope': True,
                'confidence': 0.95,
                'reason': 'Question references CrPC or PPC by name',
                'should_answer': True,
            }

        # STEP 1: Check out-of-scope FIRST (priority-based)
        out_of_scope_domain = None
        out_of_scope_score = 0
        out_of_scope_priority = 0
        matched_keywords = []
        
        for domain, config in self.out_of_scope_domains.items():
            domain_score = 0
            domain_keywords = []
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in question_lower:
                    domain_score += 1
                    domain_keywords.append(keyword)
            
            # Check patterns
            for pattern in config.get('patterns', []):
                if re.search(pattern, question_lower, re.IGNORECASE):
                    domain_score += 2  # Patterns are stronger indicators
            
            # If this domain matches and has higher priority/score, use it
            if domain_score > 0:
                # Priority-based selection: higher priority wins, or higher score if same priority
                if (config['priority'] > out_of_scope_priority) or \
                   (config['priority'] == out_of_scope_priority and domain_score > out_of_scope_score):
                    out_of_scope_domain = domain
                    out_of_scope_score = domain_score
                    out_of_scope_priority = config['priority']
                    matched_keywords = domain_keywords
        
        # If out-of-scope detected, REFUSE immediately (unless strong criminal law signal)
        if out_of_scope_domain:
            # Check for criminal law keywords (to handle mixed questions)
            criminal_score = 0
            for category, keywords in self.criminal_law_keywords.items():
                for keyword in keywords:
                    if keyword in question_lower:
                        criminal_score += 1
            
            # Only allow if criminal law score is MUCH higher (3x threshold)
            if criminal_score < (out_of_scope_score * 3):
                return {
                    'domain': out_of_scope_domain,
                    'in_scope': False,
                    'confidence': min(0.9, 0.5 + (out_of_scope_score * 0.1)),
                    'reason': f'Question is about {out_of_scope_domain.replace("_", " ")} (keywords: {", ".join(matched_keywords[:3])})',
                    'should_answer': False
                }
        
        # STEP 2: Check for greetings and conversational queries (ALLOW these)
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
                     'thanks', 'thank you', 'help', 'what can you do', 'what do you do',
                     'who are you', 'introduce yourself', 'how are you', 'how can you help']
        # Short tokens must be whole words (e.g. "hi" must not match inside "this").
        greeting_patterns = [r'\bhi\b', r'\bhey\b'] + [re.escape(g) for g in greetings if g not in ('hi', 'hey')]
        is_greeting = any(re.search(p, question_lower) for p in greeting_patterns)
        if is_greeting:
            return {
                'domain': 'pakistani_criminal_law',
                'in_scope': True,
                'confidence': 0.8,
                'reason': 'Greeting or conversational query - allow response',
                'should_answer': True
            }
        
        # STEP 3: Check criminal law (only if not out-of-scope)
        criminal_score = 0
        criminal_matches = []
        
        for category, keywords in self.criminal_law_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    criminal_score += 1
                    criminal_matches.append(keyword)
        
        if criminal_score > 0:
            return {
                'domain': 'pakistani_criminal_law',
                'in_scope': True,
                'confidence': min(1.0, 0.5 + (criminal_score / 5.0)),  # Normalize to 0.5-1.0
                'reason': f'Contains criminal law keywords: {", ".join(criminal_matches[:3])}',
                'should_answer': True
            }
        
        # STEP 4: Check if it's a very short question (likely greeting or follow-up)
        if len(question_lower.split()) <= 3:
            return {
                'domain': 'pakistani_criminal_law',
                'in_scope': True,
                'confidence': 0.6,
                'reason': 'Short question - likely conversational, allow response',
                'should_answer': True
            }
        
        # STEP 5: Unclear - check if it's a general legal question
        legal_keywords = ['law', 'legal', 'court', 'judge', 'lawyer', 'advocate', 'rights', 'case']
        has_legal_keywords = any(kw in question_lower for kw in legal_keywords)
        
        if has_legal_keywords:
            # Allow general legal questions - they might be about criminal law
            return {
                'domain': 'pakistani_criminal_law',
                'in_scope': True,
                'confidence': 0.5,
                'reason': 'General legal question - allow response, may be criminal law related',
                'should_answer': True
            }
        
        # STEP 6: For truly unclear questions, allow them (better to answer than refuse)
        # Only refuse if we're CERTAIN it's out of scope
        return {
            'domain': 'pakistani_criminal_law',
            'in_scope': True,
            'confidence': 0.4,
            'reason': 'Unclear question - allow response to be helpful',
            'should_answer': True
        }
    
    def is_in_scope(self, question: str) -> bool:
        """Quick check if question is in scope"""
        classification = self.classify(question)
        return classification.get('in_scope', False)
    
    def get_refusal_message(self, question: str) -> str:
        """Get appropriate refusal message for out-of-scope questions"""
        classification = self.classify(question)
        domain = classification.get('domain', 'unknown')
        
        if domain == 'pakistani_criminal_law':
            return None  # Should answer
        
        domain_name = domain.replace('_', ' ').title()
        
        return f"I am trained only in Pakistani Criminal Law (PPC, CrPC, and related criminal procedures). Your question appears to be about {domain_name}, which is outside my area of expertise. Please ask questions related to Pakistani criminal law, such as bail, FIR, evidence, trial procedures, or specific PPC/CrPC sections."
