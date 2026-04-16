import { api } from "../api";

export type CaseDetails = {
  sections: string[];
  evidence?: string;
  witnesses?: number;
  previous_cases?: number;
  bail_status?: string;
  evidence_strength?: string;
  case_description?: string;
  client_in_custody?: boolean;
  lawyer_experience?: number;
  procedural_violations?: boolean;
  flight_risk?: boolean;
};

export type RiskAnalysisResponse = {
  overall_risk: number;
  risk_level: string;
  confidence: number;
  factors: Array<{ factor: string; impact: number; description: string }>;
  recommendations: string[];
  risk_breakdown: {
    critical: boolean;
    high: boolean;
    medium: boolean;
    low: boolean;
  };
};

export type CasePredictionResponse = {
  predictions: {
    conviction_probability: number;
    acquittal_probability: number;
    bail_probability: number;
    sentence_prediction: string;
    timeline_prediction: string;
  };
  risk_assessment: {
    overall_risk: number;
    risk_level: string;
    confidence: number;
  };
  recommendations: string[];
  suggested_actions: string[];
  plea_deal_probability?: number;
  plea_deal_recommendation?: string;
};

export type AdvancedAnalysisResponse = {
  comprehensive_analysis: {
    risk_analysis: RiskAnalysisResponse;
    outcome_prediction: CasePredictionResponse["predictions"];
    legal_strategy: {
      recommended_approach: string;
      key_arguments: string[];
      potential_defenses: string[];
    };
    evidence_analysis: {
      strength: string;
      weaknesses: string[];
      opportunities: string[];
    };
    defense_recommendations: string[];
    prosecution_strength: {
      overall: string;
      key_strengths: string[];
    };
    overall_assessment: {
      summary: string;
      immediate_action: string;
      long_term_strategy: string;
    };
  };
  summary: {
    overall_risk: number;
    risk_level: string;
    conviction_probability: number;
    bail_probability: number;
    immediate_action: string;
  };
};

export type ComprehensiveResponse = {
  comprehensive_results: {
    chat_response?: {
      answer: string;
      references: unknown[];
      response_time: number;
    };
    risk_analysis: RiskAnalysisResponse;
    prediction: CasePredictionResponse["predictions"];
    advanced_analysis: AdvancedAnalysisResponse["comprehensive_analysis"];
  };
  summary: {
    overall_risk: number;
    risk_level: string;
    conviction_probability: number;
    bail_probability: number;
    immediate_action: string;
  };
};

export type CaseTextAnalysisResponse = {
  case_analysis: {
    sections_involved: string[];
    risk_score: number;
    risk_category: string;
  };
  risk_assessment: RiskAnalysisResponse;
  predictions: {
    conviction_probability: number;
    bail_probability: number;
  };
  recommendations: string[];
};

export type BailPredictionResponse = {
  bail_prediction: {
    likelihood: number;
    probability: string;
    factors: string[];
    recommendation: string;
  };
  sections: string[];
  factors: {
    mitigating_factors: string[];
    aggravating_factors: string[];
  };
};

// Risk Analysis
export async function analyzeRisk(caseDetails: CaseDetails): Promise<RiskAnalysisResponse> {
  return api.post<RiskAnalysisResponse>("/api/risk-analysis", {
    case_details: caseDetails,
  });
}

// Case Prediction
export async function predictCase(caseDetails: CaseDetails): Promise<CasePredictionResponse> {
  return api.post<CasePredictionResponse>("/api/case-prediction", {
    case_details: caseDetails,
  });
}

// Advanced Analysis
export async function advancedAnalysis(
  caseDetails: CaseDetails
): Promise<AdvancedAnalysisResponse> {
  return api.post<AdvancedAnalysisResponse>("/api/advanced-analysis", {
    case_details: caseDetails,
  });
}

// Comprehensive Analysis (All-in-One)
export async function comprehensiveAnalysis(
  caseDetails: CaseDetails
): Promise<ComprehensiveResponse> {
  return api.post<ComprehensiveResponse>("/api/comprehensive", {
    case_details: caseDetails,
  });
}

// Text-Based Case Analysis
export async function analyzeCaseFromText(
  caseDescription: string,
  sectionNumbers?: string[]
): Promise<CaseTextAnalysisResponse> {
  return api.post<CaseTextAnalysisResponse>("/api/case-analysis-text", {
    case_description: caseDescription,
    section_numbers: sectionNumbers || [],
  });
}

// Bail Prediction
export async function predictBail(
  sections: string[],
  mitigatingFactors: string[] = [],
  aggravatingFactors: string[] = []
): Promise<BailPredictionResponse> {
  return api.post<BailPredictionResponse>("/api/bail-prediction", {
    sections,
    mitigating_factors: mitigatingFactors,
    aggravating_factors: aggravatingFactors,
  });
}



