import { api } from "../api";

export type AnalyticsResponse = {
  overview?: {
    total_queries: number;
    rag_usage_rate: number;
    avg_response_time: number;
    total_sources_retrieved: number;
    quality_breakdown: {
      excellent: number;
      good: number;
      fair: number;
      poor: number;
    };
    unique_sessions: number;
  };
  trends?: {
    query_volume: Array<{ date: string; count: number }>;
    quality_trend: Array<{ date: string; avg_quality: number }>;
  };
  popular_topics?: {
    top_sections: Array<{ section: string; count: number }>;
    top_keywords: Array<{ keyword: string; count: number }>;
  };
  performance?: {
    avg_response_time: number;
    median_response_time: number;
    p95_response_time: number;
    min_response_time: number;
    max_response_time: number;
    fast_responses: number;
    slow_responses: number;
  };
  quality_insights?: {
    avg_quality_score: number;
    toxic_responses_count: number;
    toxic_rate: number;
    incomplete_responses: number;
    answers_with_legal_terms: number;
    context_usage_effectiveness: number;
  };
  usage_patterns?: {
    peak_hours: Array<{ hour: string; queries: number }>;
    avg_queries_per_session: number;
    total_sessions: number;
    hourly_distribution: Array<{ hour: number; count: number }>;
  };
  generated_at?: string;
  error?: string;
};

export async function getAnalytics(days: number = 30): Promise<AnalyticsResponse> {
  return api.get<AnalyticsResponse>(`/api/analytics?days=${days}`);
}



