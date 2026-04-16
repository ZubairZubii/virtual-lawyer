"""
Advanced Case Analyzer
Deep analysis of legal cases with multiple perspectives
"""
from typing import Dict, List
from legal_risk_analyzer import LegalRiskAnalyzer
from case_predictor import CasePredictor

class AdvancedCaseAnalyzer:
    """Advanced case analysis with multiple dimensions"""
    
    def __init__(self):
        """Initialize advanced analyzer"""
        self.risk_analyzer = LegalRiskAnalyzer()
        self.case_predictor = CasePredictor()
    
    def comprehensive_analysis(self, case_details: Dict) -> Dict:
        """
        Comprehensive case analysis
        
        Returns:
            Complete analysis with all dimensions
        """
        # Risk analysis
        risk_assessment = self.risk_analyzer.analyze_case(case_details)
        
        # Outcome prediction
        outcome_prediction = self.case_predictor.predict_outcome(case_details)
        
        # Legal strategy analysis
        strategy = self._analyze_strategy(case_details, risk_assessment)
        
        # Evidence analysis
        evidence_analysis = self._analyze_evidence(case_details)
        
        # Defense recommendations
        defense_recommendations = self._analyze_defense(case_details, risk_assessment)
        
        # Prosecution strength
        prosecution_strength = self._analyze_prosecution(case_details)
        
        return {
            'risk_analysis': {
                'overall_risk': risk_assessment.overall_risk,
                'risk_level': risk_assessment.risk_level,
                'factors': risk_assessment.factors,
                'confidence': risk_assessment.confidence
            },
            'outcome_prediction': outcome_prediction,
            'legal_strategy': strategy,
            'evidence_analysis': evidence_analysis,
            'defense_recommendations': defense_recommendations,
            'prosecution_strength': prosecution_strength,
            'overall_assessment': self._overall_assessment(risk_assessment, outcome_prediction)
        }
    
    def _analyze_strategy(self, case_details: Dict, risk_assessment) -> Dict:
        """Analyze legal strategy"""
        sections = case_details.get('sections', [])
        evidence = case_details.get('evidence', '')
        
        strategies = []
        
        if risk_assessment.overall_risk >= 70:
            strategies.append({
                'strategy': 'Aggressive Defense',
                'priority': 'High',
                'description': 'Focus on challenging evidence and procedural issues'
            })
            strategies.append({
                'strategy': 'Plea Negotiation',
                'priority': 'Medium',
                'description': 'Consider negotiating for reduced charges'
            })
        else:
            strategies.append({
                'strategy': 'Standard Defense',
                'priority': 'Medium',
                'description': 'Follow standard defense procedures'
            })
        
        if any('302' in str(s) for s in sections):
            strategies.append({
                'strategy': 'Expert Legal Team',
                'priority': 'Critical',
                'description': 'Requires experienced criminal defense lawyers'
            })
        
        if 'weak' in evidence.lower():
            strategies.append({
                'strategy': 'Challenge Evidence',
                'priority': 'High',
                'description': 'Focus on weak evidence and lack of direct proof'
            })
        
        return {
            'recommended_strategies': strategies,
            'priority_order': sorted(strategies, key=lambda x: {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}[x['priority']], reverse=True)
        }
    
    def _analyze_evidence(self, case_details: Dict) -> Dict:
        """Analyze evidence strength"""
        evidence = case_details.get('evidence', '').lower()
        witnesses = case_details.get('witnesses', 0)
        
        strength = 'Medium'
        score = 50
        
        if 'strong' in evidence or 'direct' in evidence:
            strength = 'Strong'
            score = 80
        elif 'weak' in evidence or 'circumstantial' in evidence:
            strength = 'Weak'
            score = 30
        
        if witnesses >= 3:
            score += 15
        elif witnesses == 0:
            score -= 20
        
        return {
            'evidence_strength': strength,
            'evidence_score': max(0, min(100, score)),
            'witnesses': witnesses,
            'assessment': 'Strong evidence favors prosecution' if score > 60 else 'Weak evidence favors defense' if score < 40 else 'Balanced evidence'
        }
    
    def _analyze_defense(self, case_details: Dict, risk_assessment) -> Dict:
        """Analyze defense options"""
        recommendations = []
        
        if risk_assessment.overall_risk >= 70:
            recommendations.append({
                'action': 'Hire Expert Lawyer',
                'urgency': 'Immediate',
                'reason': 'High-risk case requires expert defense'
            })
            recommendations.append({
                'action': 'Gather Defense Evidence',
                'urgency': 'High',
                'reason': 'Need to counter prosecution evidence'
            })
        else:
            recommendations.append({
                'action': 'Standard Legal Representation',
                'urgency': 'Medium',
                'reason': 'Standard defense should be sufficient'
            })
        
        recommendations.append({
            'action': 'Document Everything',
            'urgency': 'High',
            'reason': 'Maintain detailed records of all proceedings'
        })
        
        return {
            'recommendations': recommendations,
            'defense_strength': 'Strong' if risk_assessment.overall_risk < 40 else 'Moderate' if risk_assessment.overall_risk < 70 else 'Weak'
        }
    
    def _analyze_prosecution(self, case_details: Dict) -> Dict:
        """Analyze prosecution strength"""
        evidence = case_details.get('evidence', '').lower()
        witnesses = case_details.get('witnesses', 0)
        sections = case_details.get('sections', [])
        
        strength_score = 50
        
        if 'strong' in evidence:
            strength_score += 25
        if witnesses >= 3:
            strength_score += 15
        if any('302' in str(s) for s in sections):
            strength_score += 10  # Serious charge
        
        strength = 'Strong' if strength_score >= 70 else 'Moderate' if strength_score >= 50 else 'Weak'
        
        return {
            'prosecution_strength': strength,
            'strength_score': strength_score,
            'factors': {
                'evidence': 'Strong' if 'strong' in evidence else 'Weak',
                'witnesses': witnesses,
                'charges': 'Serious' if any('302' in str(s) for s in sections) else 'Moderate'
            }
        }
    
    def _overall_assessment(self, risk_assessment, outcome_prediction) -> Dict:
        """Overall case assessment"""
        risk = risk_assessment.overall_risk
        conviction_prob = outcome_prediction['conviction_probability']
        
        if risk >= 80 and conviction_prob >= 0.7:
            assessment = "Critical - High conviction risk"
            action = "Immediate expert legal consultation required"
        elif risk >= 60 and conviction_prob >= 0.5:
            assessment = "High Risk - Conviction possible"
            action = "Consult with experienced lawyer"
        elif risk >= 40:
            assessment = "Moderate Risk - Uncertain outcome"
            action = "Standard legal representation recommended"
        else:
            assessment = "Low Risk - Favorable outcome possible"
            action = "Standard legal procedures should suffice"
        
        return {
            'assessment': assessment,
            'immediate_action': action,
            'overall_risk': risk,
            'conviction_probability': conviction_prob
        }























