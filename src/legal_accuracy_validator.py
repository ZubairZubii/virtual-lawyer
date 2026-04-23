"""
Legal Accuracy Validator
Validates answers against known legal principles to prevent incorrect information
"""
import re
from typing import Dict, List, Tuple, Optional

class LegalAccuracyValidator:
    """Validates legal answers for accuracy and prevents hallucination"""
    
    def __init__(self):
        """Initialize validator with legal principles database"""
        
        # Core legal principles (expandable database)
        self.legal_principles = {
            'evidence_priority': {
                'rule': 'Ocular evidence has primacy over medical evidence',
                'correct': [
                    'ocular evidence prevails',
                    'eyewitness testimony has priority',
                    'medical evidence is corroborative',
                    'ocular evidence is primary',
                    'medical evidence cannot override ocular'
                ],
                'incorrect': [
                    'medical evidence has precedence',
                    'medical evidence overrides ocular',
                    'medical evidence is primary',
                    'medical evidence takes priority'
                ],
                'exception': 'unless medical evidence makes prosecution impossible'
            },
            'case_citation_format': {
                'valid_formats': [
                    r'\d{4}\s+SCMR\s+\d+',  # 2020 SCMR 316
                    r'PLD\s+\d{4}\s+SC\s+\d+',  # PLD 2009 SC 45
                    r'\d{4}\s+YLR\s+\d+',  # 2020 YLR 123
                    r'PLD\s+\d{4}\s+\w+\s+\d+',  # PLD 2009 Lahore 123
                ],
                'invalid_patterns': [
                    r'Cr\.J\.A\s+\d+/\d+',  # Cr.J.A 430/2020 (SHC format, not standard citation)
                    r'Case\s+\d+/\d+',  # Generic case numbers
                ]
            },
            'section_format': {
                'valid': r'Section\s+\d+[A-Z]?\s+PPC|Section\s+\d+[A-Z]?\s+CrPC',
                'invalid': r'Section\s+\d+\s+PPC/CrPC'  # Mixed format
            }
        }
        
        # Known case citations (expandable)
        self.known_cases = {
            'evidence_priority': [
                '2020 SCMR 316',
                '2019 SCMR 1362',
                'PLD 2009 SC 45',
                '2017 SCMR 2022'
            ]
        }
    
    def validate_answer(self, answer: str, question: str, references: List[Dict] = None) -> Dict:
        """
        Validate answer for legal accuracy
        
        Returns:
            Dict with validation results
        """
        issues = []
        warnings = []
        score = 100
        
        # Check 1: Evidence priority rule
        if self._is_evidence_priority_question(question):
            priority_check = self._check_evidence_priority(answer)
            penalty = priority_check.get('score_penalty', 0)
            if penalty > 0:
                issues.append({
                    'type': 'legal_principle_error',
                    'severity': 'critical' if penalty >= 50 else 'moderate',
                    'message': priority_check['message'],
                    'correction': priority_check.get('correction', '')
                })
                score -= penalty
        
        # Check 2: Case citation format
        citation_check = self._check_case_citations(answer, references)
        if citation_check['issues']:
            issues.extend(citation_check['issues'])
            score -= len(citation_check['issues']) * 10
        
        # Check 3: Section format
        section_check = self._check_section_format(answer)
        if section_check['issues']:
            warnings.extend(section_check['issues'])
            score -= len(section_check['issues']) * 5
        
        # Check 4: Hallucination detection
        hallucination_check = self._detect_hallucination(answer, references)
        if hallucination_check['detected']:
            issues.append({
                'type': 'hallucination',
                'severity': 'high',
                'message': hallucination_check['message'],
                'details': hallucination_check['details']
            })
            score -= 30
        
        # Check 5: Contradiction detection
        contradiction_check = self._check_contradictions(answer)
        if contradiction_check['found']:
            warnings.append({
                'type': 'contradiction',
                'message': contradiction_check['message']
            })
            score -= 10
        
        return {
            'valid': len([i for i in issues if i['severity'] == 'critical']) == 0,
            'score': max(0, score),
            'issues': issues,
            'warnings': warnings,
            'recommendations': self._generate_recommendations(issues, warnings)
        }
    
    def _is_evidence_priority_question(self, question: str) -> bool:
        """Check if question is about evidence priority"""
        keywords = ['eyewitness', 'medical evidence', 'priority', 'precedence', 'contradict', 'conflict']
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in keywords)
    
    def _check_evidence_priority(self, answer: str) -> Dict:
        """Enhanced check for evidence priority - requires BOTH primacy AND corroborative"""
        answer_lower = answer.lower()
        
        # Check for incorrect statements
        for incorrect_phrase in self.legal_principles['evidence_priority']['incorrect']:
            if incorrect_phrase in answer_lower:
                return {
                    'correct': False,
                    'message': f'Answer incorrectly states: "{incorrect_phrase}". Ocular evidence has primacy, not medical evidence.',
                    'correction': 'Ocular (eyewitness) evidence has primacy over medical evidence. Medical evidence is only corroborative and cannot override reliable ocular testimony unless it makes the prosecution story impossible.',
                    'score_penalty': 50
                }
        
        # Check for correct statements - need BOTH primacy AND corroborative
        has_primacy = any(phrase in answer_lower for phrase in [
            'ocular evidence prevails',
            'eyewitness testimony has priority',
            'ocular evidence is primary',
            'ocular evidence has primacy',
            'ocular evidence takes priority'
        ])
        
        has_corroborative = any(phrase in answer_lower for phrase in [
            'medical evidence is corroborative',
            'medical evidence is only corroborative',
            'medical evidence cannot override',
            'medical evidence is confirmatory',
            'medical evidence supports'
        ])
        
        # Both required for full credit
        if has_primacy and has_corroborative:
            return {
                'correct': True,
                'message': 'Evidence priority correctly stated (both primacy and corroborative nature mentioned)',
                'score_penalty': 0
            }
        elif has_primacy:
            return {
                'correct': True,  # Partially correct
                'message': 'Evidence priority partially correct - mentions primacy but missing explicit "corroborative" statement',
                'score_penalty': 20  # Partial penalty
            }
        elif has_corroborative:
            return {
                'correct': False,
                'message': 'Answer mentions medical evidence is corroborative but does not clearly state ocular primacy',
                'correction': 'Should state: Ocular evidence has primacy over medical evidence. Medical evidence is corroborative.',
                'score_penalty': 30
            }
        else:
            return {
                'correct': False,
                'message': 'Answer does not clearly state the correct evidence priority rule',
                'correction': 'Should state: Ocular evidence has primacy over medical evidence, unless medical evidence makes prosecution impossible. Medical evidence is corroborative.',
                'score_penalty': 50
            }
    
    def _check_case_citations(self, answer: str, references: List[Dict] = None) -> Dict:
        """Check case citation format and validity"""
        issues = []
        
        # Extract all case citations
        citations = re.findall(r'[A-Z][a-z]*\s+\d{4}[^.]*|\d{4}\s+[A-Z]+\s+\d+', answer)
        
        # Check format
        for citation in citations:
            # Check if matches valid format
            is_valid = any(re.match(pattern, citation) for pattern in self.legal_principles['case_citation_format']['valid_formats'])
            
            # Check if matches invalid pattern
            is_invalid = any(re.search(pattern, citation) for pattern in self.legal_principles['case_citation_format']['invalid_patterns'])
            
            if is_invalid:
                issues.append({
                    'type': 'invalid_citation_format',
                    'citation': citation,
                    'message': f'Citation "{citation}" uses non-standard format. Use SCMR, PLD, or YLR format.'
                })
            elif not is_valid and len(citation) > 10:  # Likely a citation
                issues.append({
                    'type': 'suspicious_citation',
                    'citation': citation,
                    'message': f'Citation "{citation}" may be hallucinated. Verify against known cases.'
                })
        
        # Check if citations match references
        if references:
            ref_cases = [ref.get('case_no', '') for ref in references if ref.get('type') == 'Case Law']
            for citation in citations:
                if not any(citation in ref_case or ref_case in citation for ref_case in ref_cases):
                    issues.append({
                        'type': 'citation_not_in_references',
                        'citation': citation,
                        'message': f'Citation "{citation}" not found in RAG references. May be hallucinated.'
                    })
        
        return {'issues': issues}
    
    def _check_section_format(self, answer: str) -> Dict:
        """Check PPC/CrPC section format"""
        issues = []
        
        # Find mixed format (Section X PPC/CrPC)
        mixed_format = re.search(r'Section\s+\d+[A-Z]?\s+PPC/CrPC', answer, re.IGNORECASE)
        if mixed_format:
            issues.append({
                'type': 'mixed_section_format',
                'text': mixed_format.group(),
                'message': 'Mixed PPC/CrPC format. Use either "Section X PPC" or "Section X CrPC" separately.'
            })

        # Find section mentions without legal code suffix (possible ambiguity)
        bare_sections = re.findall(r'Section\s+\d+[A-Z]?\b(?!\s*(PPC|CrPC))', answer, re.IGNORECASE)
        if bare_sections:
            issues.append({
                'type': 'ambiguous_section_reference',
                'text': ', '.join(sorted(set(bare_sections))),
                'message': 'Section references should include code suffix (PPC or CrPC) for clarity.'
            })
        
        return {'issues': issues}
    
    def _detect_hallucination(self, answer: str, references: List[Dict] = None) -> Dict:
        """Detect potential hallucination"""
        detected = False
        details = []
        
        # Check for case citations not in references
        if references:
            ref_cases = [ref.get('case_no', '') for ref in references if ref.get('type') == 'Case Law']
            citations = re.findall(r'[A-Z][a-z]*\s+\d{4}[^.]*|\d{4}\s+[A-Z]+\s+\d+', answer)
            
            for citation in citations:
                if not any(citation in ref_case or ref_case in citation for ref_case in ref_cases):
                    detected = True
                    details.append(f'Citation "{citation}" not found in retrieved references')
        
        # Check for specific patterns that suggest hallucination
        suspicious_patterns = [
            r'Case\s+\d+/\d+/\d+',  # Generic case numbers
            r'Cr\.J\.A\s+\d+/\d+',  # SHC format without proper citation
        ]
        
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, answer)
            if matches:
                detected = True
                details.extend([f'Suspicious pattern found: {match}' for match in matches])
        
        return {
            'detected': detected,
            'message': 'Potential hallucination detected' if detected else 'No hallucination detected',
            'details': details
        }
    
    def _check_contradictions(self, answer: str) -> Dict:
        """Check for internal contradictions"""
        answer_lower = answer.lower()
        
        # Check for contradictory statements about evidence
        has_ocular_priority = any(phrase in answer_lower for phrase in ['ocular', 'eyewitness', 'witness testimony'])
        has_medical_priority = any(phrase in answer_lower for phrase in ['medical evidence has precedence', 'medical evidence overrides'])
        
        if has_ocular_priority and has_medical_priority:
            return {
                'found': True,
                'message': 'Answer contains contradictory statements about evidence priority'
            }
        
        return {'found': False}
    
    def _generate_recommendations(self, issues: List[Dict], warnings: List[Dict]) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []
        
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        if critical_issues:
            recommendations.append('CRITICAL: Answer contains incorrect legal principles. Review and correct before returning to user.')
        
        hallucination_issues = [i for i in issues if i.get('type') == 'hallucination']
        if hallucination_issues:
            recommendations.append('Remove or verify all case citations. Only cite cases from retrieved references.')
        
        citation_issues = [i for i in issues if 'citation' in i.get('type', '')]
        if citation_issues:
            recommendations.append('Use standard citation format: SCMR, PLD, or YLR. Verify all citations against known cases.')
        
        if not recommendations:
            recommendations.append('Answer appears legally accurate. Minor improvements may be needed.')
        
        return recommendations

# Example usage
if __name__ == "__main__":
    validator = LegalAccuracyValidator()
    
    # Test with the problematic answer
    test_answer = """The rule of priority gives precedence to medical evidence over eyewitness testimony..."""
    test_question = "If all eyewitnesses support the prosecution but medical evidence contradicts the time of death, what is the rule of priority in Pakistani law?"
    
    result = validator.validate_answer(test_answer, test_question)
    print("Validation Result:")
    print(f"Valid: {result['valid']}")
    print(f"Score: {result['score']}/100")
    print(f"Issues: {len(result['issues'])}")
    print(f"Warnings: {len(result['warnings'])}")
    print("\nIssues:")
    for issue in result['issues']:
        print(f"  - {issue['message']}")
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")


