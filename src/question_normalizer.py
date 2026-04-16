"""
Question Normalizer
Fixes typos, grammar, and normalizes questions for better processing
"""
import re
from typing import Dict, List

class QuestionNormalizer:
    """Normalizes questions for better processing"""
    
    def __init__(self):
        """Initialize normalizer"""
        
        # Common typos and corrections
        self.typo_corrections = {
            'ppc': 'ppc',
            'crpc': 'crpc',
            'fir': 'fir',
            'bail': 'bail',
            'murder': 'murder',
            'theft': 'theft',
            'section': 'section',
            'evidence': 'evidence',
            'witness': 'witness',
        }
        
        # Common abbreviations
        self.abbreviations = {
            'ppc': 'Pakistan Penal Code',
            'crpc': 'Code of Criminal Procedure',
            'fir': 'First Information Report',
            'sc': 'Supreme Court',
            'hc': 'High Court',
            'shc': 'Sindh High Court',
        }
    
    def normalize(self, question: str) -> Dict:
        """
        Normalize question
        
        Returns:
            Dict with 'normalized', 'original', 'changes', 'confidence'
        """
        original = question
        normalized = question
        
        changes = []
        
        # Fix common typos in legal terms
        for typo, correct in self.typo_corrections.items():
            pattern = r'\b' + re.escape(typo) + r'\b'
            if re.search(pattern, normalized, re.IGNORECASE):
                normalized = re.sub(pattern, correct, normalized, flags=re.IGNORECASE)
                changes.append(f'Fixed typo: {typo} -> {correct}')
        
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = normalized.strip()
        
        # Fix common section number formats
        # "Section 302 PPC" -> "Section 302 PPC"
        normalized = re.sub(r'section\s+(\d+)\s*ppc/crpc', r'Section \1 PPC or CrPC', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'section\s+(\d+)\s*ppc', r'Section \1 PPC', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'section\s+(\d+)\s*crpc', r'Section \1 CrPC', normalized, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if normalized and normalized[0].islower():
            normalized = normalized[0].upper() + normalized[1:]
            changes.append('Capitalized first letter')
        
        # Add question mark if missing
        if normalized and not normalized.endswith(('?', '.', '!')):
            normalized += '?'
            changes.append('Added question mark')
        
        return {
            'normalized': normalized,
            'original': original,
            'changes': changes,
            'confidence': 1.0 if len(changes) == 0 else 0.8
        }
    
    def expand_abbreviations(self, question: str) -> str:
        """Expand common legal abbreviations"""
        expanded = question
        
        for abbrev, full_form in self.abbreviations.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            expanded = re.sub(pattern, f'{full_form} ({abbrev.upper()})', expanded, flags=re.IGNORECASE)
        
        return expanded





















