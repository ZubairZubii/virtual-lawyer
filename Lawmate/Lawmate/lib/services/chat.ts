import { api } from "../api";

export type ChatResponse = {
  answer: string;
  question?: string;
  references?: string[];
  sources_count?: number;
  response_time?: number;
  context_used?: boolean;
  retrieved_sources?: number;
};

export async function sendChat(question: string, use_formatter: boolean = false): Promise<ChatResponse> {
  try {
    const response = await api.post<{
      answer: string;
      question?: string;
      references?: any[];
      sources_count?: number;
      response_time?: number;
      stage1_time?: number;
      stage2_time?: number;
      stage3_time?: number;
      formatted?: boolean;
      context_used?: boolean;
      retrieved_sources?: number;
    }>("/api/chat", { 
      question,
      use_formatter
    });
    
    // Map backend response to frontend format
    return {
      answer: response.answer || "",
      context_used: (response.sources_count || 0) > 0 || response.context_used || false,
      retrieved_sources: response.sources_count || response.retrieved_sources || 0,
      references: response.references || [],
      response_time: response.response_time || 0,
      question: response.question || question
    };
  } catch (error: any) {
    console.error("Chat API Error:", error);
    throw new Error(error.message || "Failed to get response from AI assistant");
  }
}

