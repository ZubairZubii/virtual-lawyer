"""
Advanced Case Predictor
Predicts case outcomes, bail probability, and sentencing
"""
from typing import Dict, List
from legal_risk_analyzer import LegalRiskAnalyzer

class CasePredictor:
    """Advanced case prediction system"""
    
    def __init__(self):
        """Initialize case predictor"""
        self.risk_analyzer = LegalRiskAnalyzer()
        
        # Historical data patterns (simulated - in production, use real data)
        self.outcome_patterns = {
            '302': {
                'conviction_rate': 0.65,
                'acquittal_rate': 0.35,
                'avg_sentence': 'Life imprisonment',
                'bail_grant_rate': 0.15
            },
            '376': {
                'conviction_rate': 0.70,
                'acquittal_rate': 0.30,
                'avg_sentence': 'Life imprisonment',
                'bail_grant_rate': 0.20
            },
            '395': {
                'conviction_rate': 0.60,
                'acquittal_rate': 0.40,
                'avg_sentence': '10-15 years',
                'bail_grant_rate': 0.25
            },
        }
    
    def predict_outcome(self, case_details: Dict) -> Dict:
        """
        Predict complete case outcome
        
        Args:
            case_details: Case information
        
        Returns:
            Complete prediction with probabilities
        """
        sections = case_details.get('sections', [])
        evidence_strength = case_details.get('evidence_strength', 'medium')
        witnesses = case_details.get('witnesses', 0)
        
        # Get risk assessment
        risk_assessment = self.risk_analyzer.analyze_case(case_details)
        
        # Predict conviction
        conviction_prob = self._predict_conviction(sections, evidence_strength, witnesses, risk_assessment)
        
        # Predict bail
        bail_prob = self._predict_bail(sections, risk_assessment)
        
        # Predict sentence
        sentence_prediction = self._predict_sentence(sections, risk_assessment)
        
        # Predict timeline
        timeline = self._predict_timeline(sections, case_details)
        
        # Predict plea deal
        plea_deal = self.predict_plea_deal(case_details, risk_assessment)
        
        # Suggest actions
        bail_pred = {'bail_probability': bail_prob * 100}
        actions = self.suggest_actions(case_details, risk_assessment, bail_pred)
        
        return {
            'conviction_probability': conviction_prob,
            'acquittal_probability': round(1 - conviction_prob, 2),
            'bail_probability': bail_prob,
            'plea_deal_probability': plea_deal['plea_deal_probability'],
            'sentence_prediction': sentence_prediction,
            'timeline_prediction': timeline,
            'risk_level': risk_assessment.risk_level,
            'overall_risk': risk_assessment.overall_risk,
            'confidence': risk_assessment.confidence,
            'recommendations': risk_assessment.recommendations,
            'suggested_actions': actions,
            'plea_deal_recommendation': plea_deal['recommendation']
        }
    
    def _predict_conviction(self, sections: List, evidence: str, witnesses: int, risk_assessment) -> float:
        """Predict conviction probability"""
        base_prob = risk_assessment.overall_risk / 100
        
        # Adjust based on evidence
        if evidence == 'strong':
            base_prob += 0.15
        elif evidence == 'weak':
            base_prob -= 0.20
        
        # Adjust based on witnesses
        if witnesses >= 3:
            base_prob += 0.10
        elif witnesses == 0:
            base_prob -= 0.15
        
        # Check section patterns
        for section in sections:
            section_num = str(section).replace('PPC', '').replace('Section', '').strip()
            if section_num in self.outcome_patterns:
                pattern = self.outcome_patterns[section_num]
                base_prob = (base_prob + pattern['conviction_rate']) / 2
        
        return max(0.0, min(1.0, round(base_prob, 2)))
    
    def _predict_bail(self, sections: List, risk_assessment) -> float:
        """Predict bail probability"""
        # Non-bailable sections
        non_bailable = ['302', '376', '395']
        
        has_non_bailable = any(any(nb in str(s) for nb in non_bailable) for s in sections)
        
        if has_non_bailable:
            # Very low probability for non-bailable
            base_prob = 0.15 - (risk_assessment.overall_risk / 100) * 0.10
        else:
            # Bailable sections
            base_prob = 0.60 - (risk_assessment.overall_risk / 100) * 0.30
        
        return max(0.0, min(1.0, round(base_prob, 2)))
    
    def _predict_sentence(self, sections: List, risk_assessment) -> Dict:
        """Predict sentence"""
        sentence_types = []
        
        for section in sections:
            section_num = str(section).replace('PPC', '').replace('Section', '').strip()
            if section_num == '302':
                sentence_types.append({
                    'section': '302',
                    'likely_sentence': 'Death or Life Imprisonment',
                    'probability': 0.85,
                    'min_sentence': 'Life imprisonment',
                    'max_sentence': 'Death'
                })
            elif section_num == '376':
                sentence_types.append({
                    'section': '376',
                    'likely_sentence': 'Life Imprisonment',
                    'probability': 0.80,
                    'min_sentence': '10 years',
                    'max_sentence': 'Life imprisonment'
                })
            elif section_num == '395':
                sentence_types.append({
                    'section': '395',
                    'likely_sentence': '10-15 years',
                    'probability': 0.70,
                    'min_sentence': '7 years',
                    'max_sentence': 'Life imprisonment'
                })
        
        if not sentence_types:
            sentence_types.append({
                'section': 'General',
                'likely_sentence': 'Based on risk assessment',
                'probability': 0.50,
                'min_sentence': 'Varies',
                'max_sentence': 'Varies'
            })
        
        return {
            'predictions': sentence_types,
            'overall_risk': risk_assessment.overall_risk
        }
    
    def _predict_timeline(self, sections: List, case_details: Dict) -> Dict:
        """Predict case timeline"""
        # Estimate based on section complexity
        has_serious = any('302' in str(s) or '376' in str(s) for s in sections)
        
        if has_serious:
            timeline = {
                'investigation': '2-4 months',
                'trial_duration': '1-3 years',
                'appeal_duration': '2-5 years',
                'total_estimated': '3-8 years'
            }
        else:
            timeline = {
                'investigation': '1-2 months',
                'trial_duration': '6 months - 2 years',
                'appeal_duration': '1-3 years',
                'total_estimated': '2-5 years'
            }
        
        return timeline
    
    def predict_plea_deal(self, case_details: Dict, risk_assessment) -> Dict:
        """
        Predict plea deal probability (from old risk_predictor)
        
        Returns:
            Plea deal prediction
        """
        risk = risk_assessment.overall_risk
        
        # Base plea deal probability
        if risk >= 75:
            plea_prob = 0.15
        elif risk >= 50:
            plea_prob = 0.20
        elif risk >= 30:
            plea_prob = 0.15
        else:
            plea_prob = 0.10
        
        # Adjust based on evidence
        evidence = case_details.get('evidence_strength', 'medium')
        if evidence == 'strong':
            plea_prob += 0.10  # Strong evidence encourages plea
        elif evidence == 'weak':
            plea_prob -= 0.05  # Weak evidence reduces plea incentive
        
        plea_prob = max(0.05, min(0.40, plea_prob))
        
        return {
            'plea_deal_probability': round(plea_prob, 2),
            'recommendation': 'Consider plea negotiation' if plea_prob > 0.20 else 'Focus on trial defense'
        }
    
    def suggest_actions(self, case_details: Dict, risk_assessment, bail_prediction) -> List[Dict]:
        """
        Suggest recommended legal actions with priority (from old risk_predictor)
        
        Returns:
            List of action recommendations with priority and timeline
        """
        actions = []
        
        # High priority actions
        if case_details.get('bail_status') == 'unknown' or case_details.get('bail_status') == 'rejected':
            actions.append({
                "priority": "URGENT",
                "action": "File bail petition immediately",
                "reason": "Time-sensitive matter for client's release",
                "timeline": "Within 24-48 hours"
            })
        
        if risk_assessment.overall_risk >= 70:
            actions.append({
                "priority": "URGENT",
                "action": "Engage experienced criminal defense lawyer",
                "reason": "High-risk case requires expert legal strategy",
                "timeline": "Immediately"
            })
        
        # Medium priority
        evidence = case_details.get('evidence', '').lower()
        if 'strong' in evidence or 'direct' in evidence:
            actions.append({
                "priority": "HIGH",
                "action": "Challenge evidence admissibility in court",
                "reason": "Strong prosecution evidence needs legal challenge",
                "timeline": "Before trial proceedings"
            })
        
        witnesses = case_details.get('witnesses', 0)
        if witnesses > 2:
            actions.append({
                "priority": "HIGH",
                "action": "Prepare comprehensive witness cross-examination",
                "reason": f"{witnesses} prosecution witnesses testimony",
                "timeline": "During trial preparation"
            })
        
        # General actions
        actions.append({
            "priority": "MEDIUM",
            "action": "Collect character witnesses and evidence",
            "reason": "Build strong defense narrative",
            "timeline": "Throughout case preparation"
        })
        
        if bail_prediction.get('bail_probability', 0) > 40:
            actions.append({
                "priority": "MEDIUM",
                "action": "Prepare bail application with strong sureties",
                "reason": f"{bail_prediction.get('bail_probability', 0)}% bail approval probability",
                "timeline": "As soon as possible"
            })
        
        return actions

