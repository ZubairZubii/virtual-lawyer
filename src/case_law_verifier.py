"""
Enhanced Case Law Verification Layer
Long-term solution: Better citation removal with NLP-based cleaning
"""
import re
from typing import Dict, List, Optional, Set
import json
import os

class CaseLawVerifier:
    """Enhanced case law verifier with better citation removal"""
    
    def __init__(self, rag_corpus_path: str = "./data/processed/shc_cases_rag.json"):
        """Initialize with RAG corpus"""
        self.rag_corpus_path = rag_corpus_path
        self.valid_citation_patterns = [
            r'\d{4}\s+SCMR\s+\d+',  # 2020 SCMR 316
            r'PLD\s+\d{4}\s+SC\s+\d+',  # PLD 2009 SC 45
            r'\d{4}\s+YLR\s+\d+',  # 2020 YLR 123
            r'PLD\s+\d{4}\s+\w+\s+\d+',  # PLD 2009 Lahore 123
        ]
        self.invalid_patterns = [
            r'Cr\.J\.A\s+\d+/\d+',  # SHC case number, not citation
            r'Cr\.Rev\s+\d+/\d+',
            r'Case\s+\d+/\d+',
        ]
        self.known_cases = self._load_known_cases()
    
    def _load_known_cases(self) -> Set[str]:
        """Load known case citations from RAG corpus"""
        known_cases = set()
        
        # Load from SHC cases
        if os.path.exists(self.rag_corpus_path):
            try:
                with open(self.rag_corpus_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for doc in data:
                        # Extract case numbers
                        case_no = doc.get('case_no', '')
                        if case_no:
                            known_cases.add(case_no.lower())
                        
                        # Extract citations from text
                        text = doc.get('text', '')
                        citations = self._extract_citations(text)
                        known_cases.update(c.lower() for c in citations)
            except Exception as e:
                print(f"Warning: Could not load case law corpus: {e}")
        
        # Add standard known cases
        standard_cases = [
            '2020 SCMR 316',
            '2019 SCMR 1362',
            'PLD 2009 SC 45',
            '2017 SCMR 2022',
            'PLD 2016 SC 49',
        ]
        known_cases.update(c.lower() for c in standard_cases)
        
        return known_cases
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract case citations from text"""
        citations = []
        
        for pattern in self.valid_citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return citations
    
    def verify_citation(self, citation: str) -> Dict:
        """
        Verify if a citation is valid and exists in corpus
        
        Returns:
            Dict with 'valid', 'exists', 'format_valid', 'message'
        """
        citation_lower = citation.lower().strip()
        
        # Check format
        format_valid = any(re.match(pattern, citation, re.IGNORECASE) for pattern in self.valid_citation_patterns)
        format_invalid = any(re.search(pattern, citation, re.IGNORECASE) for pattern in self.invalid_patterns)
        
        if format_invalid:
            return {
                'valid': False,
                'exists': False,
                'format_valid': False,
                'message': f'Citation "{citation}" uses non-standard format (SHC case number, not legal citation)',
                'should_remove': True
            }
        
        if not format_valid and len(citation) > 10:
            # Might be a citation but format unclear
            return {
                'valid': False,
                'exists': False,
                'format_valid': False,
                'message': f'Citation "{citation}" format unclear. Use standard format: SCMR, PLD, or YLR.',
                'should_remove': True
            }
        
        # Check if exists in known cases
        exists = citation_lower in self.known_cases or any(
            citation_lower in known_case or known_case in citation_lower
            for known_case in self.known_cases
        )
        
        if not exists:
            return {
                'valid': False,
                'exists': False,
                'format_valid': format_valid,
                'message': f'Citation "{citation}" not found in RAG corpus. May be hallucinated.',
                'should_remove': True
            }
        
        return {
            'valid': True,
            'exists': True,
            'format_valid': True,
            'message': f'Citation "{citation}" verified',
            'should_remove': False
        }
    
    def verify_answer(self, answer: str, references: List[Dict] = None) -> Dict:
        """
        Verify all citations in an answer
        
        Returns:
            Dict with 'valid', 'invalid_citations', 'warnings'
        """
        # Extract all citations
        all_citations = []
        for pattern in self.valid_citation_patterns + self.invalid_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            all_citations.extend(matches)
        
        invalid_citations = []
        warnings = []
        
        for citation in all_citations:
            verification = self.verify_citation(citation)
            if not verification['valid']:
                invalid_citations.append({
                    'citation': citation,
                    'reason': verification['message'],
                    'should_remove': verification.get('should_remove', False)
                })
            elif not verification['exists']:
                warnings.append({
                    'citation': citation,
                    'message': verification['message']
                })
        
        # Check citations against references
        if references:
            ref_cases = [ref.get('case_no', '') for ref in references if ref.get('type') == 'Case Law']
            for citation in all_citations:
                if not any(
                    citation.lower() in ref_case.lower() or ref_case.lower() in citation.lower()
                    for ref_case in ref_cases
                ):
                    if citation not in [ic['citation'] for ic in invalid_citations]:
                        warnings.append({
                            'citation': citation,
                            'message': f'Citation "{citation}" not found in RAG references'
                        })
        
        return {
            'valid': len(invalid_citations) == 0,
            'invalid_citations': invalid_citations,
            'warnings': warnings,
            'total_citations': len(all_citations),
            'valid_citations': len(all_citations) - len(invalid_citations)
        }
    
    def _find_citation_context(self, text: str, citation: str) -> List[tuple]:
        """
        Find all occurrences of citation with their context
        
        Returns:
            List of (start_pos, end_pos, context_sentence)
        """
        occurrences = []
        citation_escaped = re.escape(citation)
        
        # Find all matches
        for match in re.finditer(citation_escaped, text, re.IGNORECASE):
            start = match.start()
            end = match.end()
            
            # Find sentence boundaries
            sentence_start = max(0, text.rfind('.', 0, start) + 1)
            sentence_end = text.find('.', end)
            if sentence_end == -1:
                sentence_end = len(text)
            
            context = text[sentence_start:sentence_end].strip()
            occurrences.append((start, end, context))
        
        return occurrences
    
    def clean_answer(self, answer: str, references: List[Dict] = None) -> str:
        """
        Enhanced citation removal with better NLP-based cleaning
        
        Returns:
            Cleaned answer with invalid citations removed intelligently
        """
        verification = self.verify_answer(answer, references)
        
        cleaned_answer = answer
        
        # Remove invalid citations with better context handling
        for invalid in verification['invalid_citations']:
            if invalid['should_remove']:
                citation = invalid['citation']
                
                # Find all occurrences with context
                occurrences = self._find_citation_context(cleaned_answer, citation)
                
                # Remove each occurrence intelligently
                for start, end, context in reversed(occurrences):  # Reverse to maintain positions
                    # Check if context is just the citation (standalone)
                    context_clean = context.strip()
                    citation_in_context = citation.lower() in context_clean.lower()
                    
                    if citation_in_context:
                        # If context is mostly just the citation, remove the whole sentence
                        words_in_context = len(context_clean.split())
                        citation_words = len(citation.split())
                        
                        if words_in_context <= citation_words + 3:  # Context is mostly citation
                            # Remove entire sentence
                            sentence_start = max(0, cleaned_answer.rfind('.', 0, start) + 1)
                            sentence_end = cleaned_answer.find('.', end)
                            if sentence_end == -1:
                                sentence_end = len(cleaned_answer)
                            
                            # Remove sentence
                            cleaned_answer = cleaned_answer[:sentence_start].strip() + \
                                          cleaned_answer[sentence_end:].strip()
                        else:
                            # Remove just the citation and surrounding words
                            # Try to remove citation with minimal context
                            pattern = r'\s*[\(\[,]?\s*' + re.escape(citation) + r'\s*[\)\],]?\s*'
                            cleaned_answer = re.sub(pattern, ' ', cleaned_answer, flags=re.IGNORECASE)
                    else:
                        # Simple removal
                        pattern = r'\s*' + re.escape(citation) + r'\s*'
                        cleaned_answer = re.sub(pattern, ' ', cleaned_answer, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        cleaned_answer = re.sub(r'\s+', ' ', cleaned_answer)  # Multiple spaces
        cleaned_answer = re.sub(r'\s+\.', '.', cleaned_answer)  # Space before period
        cleaned_answer = re.sub(r'\.\s*\.+', '.', cleaned_answer)  # Multiple periods
        cleaned_answer = re.sub(r',\s*,+', ',', cleaned_answer)  # Multiple commas
        cleaned_answer = re.sub(r'\s*\(\s*\)', '', cleaned_answer)  # Empty parentheses
        
        # Fix sentence boundaries
        cleaned_answer = re.sub(r'\.\s+\.', '.', cleaned_answer)
        cleaned_answer = re.sub(r'\.\s*,\s*', ', ', cleaned_answer)
        
        return cleaned_answer.strip()
