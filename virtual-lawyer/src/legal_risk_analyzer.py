"""
Advanced Legal Risk Analyzer
Analyzes legal cases and provides risk assessment
Includes all features from old case_risk_predictor.py and risk_predictor.py
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class RiskAssessment:
    """Risk assessment result"""
    overall_risk: float  # 0-100
    risk_level: str  # "Low", "Medium", "High", "Critical"
    factors: List[Dict]
    recommendations: List[str]
    confidence: float  # 0-1

class LegalRiskAnalyzer:
    """Advanced risk analysis for legal cases"""
    
    def __init__(self):
        """Initialize risk analyzer"""
        # Risk factors and their weights
        self.risk_factors = {
            'murder': {'weight': 1.0, 'risk': 90},
            'section_302': {'weight': 1.0, 'risk': 90},
            'non_bailable': {'weight': 0.9, 'risk': 75},
            'cognizable': {'weight': 0.8, 'risk': 70},
            'death_penalty': {'weight': 1.0, 'risk': 95},
            'life_imprisonment': {'weight': 0.9, 'risk': 85},
            'bail': {'weight': -0.5, 'risk': -30},  # Negative = reduces risk
            'weak_evidence': {'weight': -0.3, 'risk': -20},
            'strong_evidence': {'weight': 0.7, 'risk': 60},
            'witness': {'weight': 0.5, 'risk': 40},
            'confession': {'weight': 0.8, 'risk': 70},
            'previous_conviction': {'weight': 0.6, 'risk': 50},
        }
        
        # Section risk mapping
        self.section_risks = {
            '302': {'risk': 90, 'bail': 'non-bailable', 'punishment': 'death/life'},
            '376': {'risk': 85, 'bail': 'non-bailable', 'punishment': 'life'},
            '395': {'risk': 80, 'bail': 'non-bailable', 'punishment': 'life'},
            '392': {'risk': 70, 'bail': 'bailable', 'punishment': '10 years'},
            '420': {'risk': 60, 'bail': 'bailable', 'punishment': '7 years'},
            '379': {'risk': 50, 'bail': 'bailable', 'punishment': '3 years'},
        }
    
    def analyze_case(self, case_details: Dict) -> RiskAssessment:
        """
        Analyze a case and provide risk assessment
        
        Args:
            case_details: Dict with case information
                - sections: List of PPC sections
                - evidence: Description of evidence
                - witnesses: Number of witnesses
                - previous_cases: Previous convictions
                - bail_status: Current bail status
        
        Returns:
            RiskAssessment object
        """
        sections = case_details.get('sections', [])
        evidence = case_details.get('evidence', '').lower()
        witnesses = case_details.get('witnesses', 0)
        previous_cases = case_details.get('previous_cases', 0)
        bail_status = case_details.get('bail_status', 'unknown')
        
        factors = []
        total_risk = 0
        total_weight = 0
        
        # Analyze sections
        for section in sections:
            section_num = re.search(r'\d+', str(section))
            if section_num:
                num = section_num.group()
                if num in self.section_risks:
                    risk_info = self.section_risks[num]
                    risk_score = risk_info['risk']
                    factors.append({
                        'factor': f'Section {num} PPC',
                        'risk': risk_score,
                        'impact': 'High' if risk_score > 80 else 'Medium' if risk_score > 60 else 'Low',
                        'details': f"Non-bailable, {risk_info['punishment']}"
                    })
                    total_risk += risk_score * 1.0
                    total_weight += 1.0
        
        # Analyze evidence
        if 'strong' in evidence or 'direct' in evidence:
            factors.append({
                'factor': 'Strong Evidence',
                'risk': 60,
                'impact': 'High',
                'details': 'Direct or strong evidence present'
            })
            total_risk += 60 * 0.7
            total_weight += 0.7
        elif 'weak' in evidence or 'circumstantial' in evidence:
            factors.append({
                'factor': 'Weak Evidence',
                'risk': -20,
                'impact': 'Low',
                'details': 'Weak or circumstantial evidence'
            })
            total_risk += -20 * 0.3
            total_weight += 0.3
        
        # Analyze witnesses
        if witnesses > 2:
            factors.append({
                'factor': f'Multiple Witnesses ({witnesses})',
                'risk': 40,
                'impact': 'Medium',
                'details': f'{witnesses} witnesses present'
            })
            total_risk += 40 * 0.5
            total_weight += 0.5
        
        # Analyze previous cases
        if previous_cases > 0:
            factors.append({
                'factor': f'Previous Convictions ({previous_cases})',
                'risk': 50,
                'impact': 'High',
                'details': f'{previous_cases} previous conviction(s)'
            })
            total_risk += 50 * 0.6
            total_weight += 0.6
        
        # Analyze bail status
        if bail_status == 'granted':
            factors.append({
                'factor': 'Bail Granted',
                'risk': -30,
                'impact': 'Positive',
                'details': 'Bail has been granted'
            })
            total_risk += -30 * 0.5
            total_weight += 0.5
        elif bail_status == 'rejected':
            factors.append({
                'factor': 'Bail Rejected',
                'risk': 30,
                'impact': 'High',
                'details': 'Bail application rejected'
            })
            total_risk += 30 * 0.5
            total_weight += 0.5
        
        # Calculate overall risk
        if total_weight > 0:
            overall_risk = max(0, min(100, total_risk / total_weight))
        else:
            overall_risk = 50  # Default medium risk
        
        # Determine risk level
        if overall_risk >= 80:
            risk_level = "Critical"
        elif overall_risk >= 60:
            risk_level = "High"
        elif overall_risk >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_risk, factors, sections, bail_status)
        
        # Calculate confidence
        confidence = min(1.0, total_weight / 5.0)  # More factors = higher confidence
        
        return RiskAssessment(
            overall_risk=round(overall_risk, 2),
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            confidence=round(confidence, 2)
        )
    
    def _generate_recommendations(self, risk: float, factors: List[Dict], sections: List, bail_status: str) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk >= 80:
            recommendations.append("CRITICAL: Immediate legal consultation required")
            recommendations.append("Consider hiring experienced criminal defense lawyer")
            recommendations.append("Prepare for potential severe consequences")
            if '302' in str(sections):
                recommendations.append("Section 302 cases require expert defense strategy")
        elif risk >= 60:
            recommendations.append("HIGH RISK: Consult with legal expert immediately")
            recommendations.append("Gather all evidence and documentation")
            recommendations.append("Consider bail application if not yet filed")
        elif risk >= 40:
            recommendations.append("MEDIUM RISK: Legal consultation recommended")
            recommendations.append("Prepare defense strategy")
            recommendations.append("Document all relevant information")
        else:
            recommendations.append("LOW RISK: Standard legal procedures should be sufficient")
            recommendations.append("Maintain proper documentation")
        
        if bail_status == 'rejected' or bail_status == 'unknown':
            recommendations.append("Consider filing bail application with strong grounds")
        
        if any('302' in str(s) for s in sections):
            recommendations.append("Section 302 is non-bailable - bail will be difficult")
            recommendations.append("Focus on proving weak prosecution case or no direct evidence")
        
        return recommendations
    
    def analyze_case_from_text(self, case_description: str, section_numbers: List[str] = None) -> RiskAssessment:
        """
        Analyze case from text description (for compatibility with old API)
        
        Args:
            case_description: Text description of the case
            section_numbers: Optional list of section numbers
        
        Returns:
            RiskAssessment object
        """
        import re
        
        # Extract sections if not provided
        if not section_numbers:
            sections = re.findall(r'\b(\d{2,3}[A-Z]?)\b', case_description)
            # Filter valid PPC sections (100-511)
            section_numbers = []
            for sec in sections:
                sec_num = re.match(r'(\d+)', sec)
                if sec_num and 100 <= int(sec_num.group(1)) <= 511:
                    section_numbers.append(sec)
            section_numbers = list(set(section_numbers))
        
        # Detect evidence strength from text
        case_lower = case_description.lower()
        evidence = "medium"
        if any(word in case_lower for word in ['strong', 'direct', 'clear', 'conclusive']):
            evidence = "strong"
        elif any(word in case_lower for word in ['weak', 'circumstantial', 'insufficient', 'doubt']):
            evidence = "weak"
        
        # Detect witnesses
        witnesses = 0
        witness_match = re.search(r'(\d+)\s*witness', case_lower)
        if witness_match:
            witnesses = int(witness_match.group(1))
        
        # Detect previous cases
        previous_cases = 0
        if 'first offense' in case_lower or 'no prior' in case_lower:
            previous_cases = 0
        elif 'prior' in case_lower or 'previous' in case_lower:
            prev_match = re.search(r'(\d+)\s*(prior|previous)', case_lower)
            if prev_match:
                previous_cases = int(prev_match.group(1))
            else:
                previous_cases = 1
        
        # Detect bail status
        bail_status = "unknown"
        if 'bail granted' in case_lower or 'released on bail' in case_lower:
            bail_status = "granted"
        elif 'bail rejected' in case_lower or 'bail denied' in case_lower:
            bail_status = "rejected"
        
        # Create case_details dict
        case_details = {
            'sections': section_numbers,
            'evidence': evidence,
            'witnesses': witnesses,
            'previous_cases': previous_cases,
            'bail_status': bail_status
        }
        
        return self.analyze_case(case_details)
    
    def predict_bail_likelihood(self, sections: List[str], factors: Dict) -> Dict:
        """
        Predict bail likelihood with factors (from old case_risk_predictor)
        
        Args:
            sections: List of section numbers
            factors: Dict with mitigating_factors and aggravating_factors
        
        Returns:
            Bail prediction dict
        """
        # Calculate base bail probability
        bail_scores = []
        for section in sections:
            section_num = re.search(r'\d+', str(section))
            if section_num:
                num = section_num.group()
                if num in self.section_risks:
                    risk_info = self.section_risks[num]
                    if risk_info['bail'] == 'non-bailable':
                        bail_scores.append(0.15)
                    else:
                        bail_scores.append(0.60)
        
        if not bail_scores:
            avg_bail_prob = 0.5
        else:
            avg_bail_prob = sum(bail_scores) / len(bail_scores)
        
        # Adjust for factors
        mitigating_count = len(factors.get('mitigating_factors', []))
        aggravating_count = len(factors.get('aggravating_factors', []))
        
        adjusted_prob = avg_bail_prob + (mitigating_count * 0.05) - (aggravating_count * 0.1)
        adjusted_prob = max(0, min(1, adjusted_prob))
        
        # Get recommendation
        if adjusted_prob > 0.7:
            recommendation = "Strong grounds for bail. File application with proper sureties."
            likelihood = "HIGH"
        elif adjusted_prob > 0.4:
            recommendation = "Moderate chances. Strengthen case with character witnesses and stable address proof."
            likelihood = "MEDIUM"
        else:
            recommendation = "Bail may be challenging. Focus on building strong defense for trial."
            likelihood = "LOW"
        
        return {
            'bail_probability': round(adjusted_prob * 100, 1),
            'likelihood': likelihood,
            'recommendation': recommendation
        }
    
    def predict_case_outcome(self, case_details: Dict) -> Dict:
        """
        Predict case outcome based on analysis
        
        Returns:
            Dict with predictions
        """
        risk_assessment = self.analyze_case(case_details)
        
        # Predict outcome based on risk
        if risk_assessment.overall_risk >= 80:
            outcome = "Conviction Likely"
            probability = 0.75
        elif risk_assessment.overall_risk >= 60:
            outcome = "Conviction Possible"
            probability = 0.55
        elif risk_assessment.overall_risk >= 40:
            outcome = "Uncertain"
            probability = 0.40
        else:
            outcome = "Acquittal Possible"
            probability = 0.30
        
        # Predict bail
        sections = case_details.get('sections', [])
        bail_prediction = "Unlikely"
        bail_probability = 0.2
        
        if any('302' in str(s) for s in sections):
            bail_prediction = "Very Unlikely"
            bail_probability = 0.1
        elif risk_assessment.overall_risk < 40:
            bail_prediction = "Possible"
            bail_probability = 0.5
        elif risk_assessment.overall_risk < 60:
            bail_prediction = "Unlikely"
            bail_probability = 0.3
        
        return {
            'outcome_prediction': outcome,
            'outcome_probability': round(probability, 2),
            'bail_prediction': bail_prediction,
            'bail_probability': round(bail_probability, 2),
            'risk_assessment': {
                'overall_risk': risk_assessment.overall_risk,
                'risk_level': risk_assessment.risk_level,
                'confidence': risk_assessment.confidence
            },
            'factors': risk_assessment.factors,
            'recommendations': risk_assessment.recommendations
        }

