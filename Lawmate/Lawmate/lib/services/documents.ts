import { api } from "../api";

export type TemplateInfo = {
  id?: string;
  template_id?: string;
  name?: string;
  placeholders?: string[];
  category?: string;
};

export async function listTemplates(category?: string) {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  const res = await api.get<{ templates: TemplateInfo[]; count: number }>(
    `/api/document/templates${query}`
  );
  return res.templates;
}

export async function getTemplateDetails(template_id: string) {
  if (!template_id || template_id.trim() === "") {
    throw new Error("Template ID is required");
  }
  // Encode each part of the template_id separately if it contains slashes
  const encodedId = template_id.split('/').map(part => encodeURIComponent(part)).join('/');
  return api.get<{
    template_id: string;
    name?: string;
    category?: string;
    placeholders: string[];
    placeholder_descriptions: Record<
      string,
      { description: string; type: string; required: boolean }
    >;
    example_data: Record<string, string>;
    total_placeholders: number;
  }>(`/api/document/templates/${encodedId}`);
}

export async function uploadDocument(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  return api.postMultipart<{
    doc_id: string;
    file_name: string;
    chunks_count: number;
    text_length: number;
    status: string;
  }>("/api/document/upload", fd);
}

export async function extractFacts(doc_id: string) {
  return api.get<{ doc_id: string; facts: Record<string, unknown>; summary: string }>(
    `/api/document/${doc_id}/extract`
  );
}

export async function getSummary(doc_id: string) {
  return api.get<{ doc_id: string; summary: string }>(
    `/api/document/${doc_id}/summary`
  );
}

export async function askQuestion(doc_id: string, question: string) {
  return api.post<{
    answer: string;
    context: string;
    chunks_used: number;
    relevant_chunks: unknown[];
    confidence: number;
  }>("/api/document/question", { doc_id, question });
}

export async function generateDocument(
  template_id: string,
  data: Record<string, unknown>,
  generate_ai_sections = false
) {
  return api.post<{
    output_path?: string;
    output_filename?: string;
    pdf_path?: string;
    pdf_filename?: string;
    placeholders_filled?: number;
    total_placeholders?: number;
    template_name?: string;
  }>("/api/document/generate", { template_id, data, generate_ai_sections });
}

export async function analyzeAndGenerate(
  doc_id: string,
  template_id: string,
  additional_data?: Record<string, unknown>
) {
  return api.post<{
    extracted_facts: Record<string, unknown>;
    generation_result: Record<string, unknown>;
  }>("/api/document/analyze-and-generate", {
    doc_id,
    template_id,
    additional_data,
  });
}

export async function suggestDocumentType(facts: Record<string, unknown>) {
  return api.post<{
    suggestions: Array<{
      template_id: string;
      name: string;
      category: string;
      relevance_score: number;
      reason: string;
    }>;
    count: number;
  }>("/api/document/suggest", facts);
}

