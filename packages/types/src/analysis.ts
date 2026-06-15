export interface EntityMention {
  page: number;
  snippet: string;
}

export interface Entity {
  id: string;
  type: string; // e.g., "PERSON", "ORGANIZATION", "MONEY", "DATE", "TECHNOLOGY"
  text: string;
  confidence: number;
  mentions: EntityMention[];
  frequency: number;
  related_entities: string[];
  boundingBox?: [number, number, number, number]; // [xMin, yMin, xMax, yMax]
}

export interface EntityConflict {
  entity_type: string;
  values: string[];
  pages: number[];
  description: string;
}

export interface KeyValuePair {
  id: string;
  key: string;
  value: string;
  confidence: number;
}

export interface DocumentSummary {
  abstract: string;
  keyPoints: string[];
  suggestedQuestions: string[];
}

export interface DocumentAnalysis {
  documentId: string;
  summary: DocumentSummary;
  entities: Entity[];
  keyValuePairs: KeyValuePair[];
  entityConflicts: EntityConflict[];
  analyzedAt: string;
}

// ── Phase 2: Document Intelligence Types ───────────────────────────────────

export interface TrustScoreBreakdown {
  contradictions: number;
  references: number;
  requirements: number;
  entities: number;
  ambiguities: number;
  completeness: number;
}

export interface TrustScoreDeduction {
  dimension?: string;
  component?: string;
  raw_score?: number;
  weight?: number;
  weighted_deduction?: number;
  points?: number;
  reason?: string;
  evidence?: string;
  page?: number;
  finding_id?: string;
}

export interface TrustScore {
  score?: number;
  confidence?: number;
  breakdown?: TrustScoreBreakdown;
  deductions?: TrustScoreDeduction[];
  evidence?: string;
}

export interface ExecutiveSummary {
  executive_summary: string;
  key_findings: string[];
  critical_risks: string[];
  major_contradictions: string[];
  important_entities: string[];
  requirements_overview: string;
  trust_assessment: string;
  recommended_actions: string[];
}

export interface ReviewChecklistItem {
  id: string;
  category: string;
  item: string;
  status: "pass" | "fail" | "warning" | "info";
  detail: string;
  evidence?: string;
}

export interface ReviewCopilot {
  reviewer_checklist: ReviewChecklistItem[];
  open_questions: string[];
  compliance_concerns: string[];
  risk_items: string[];
  verification_tasks: string[];
}

export interface AmbiguityFinding {
  id: string;
  chunk_index: number;
  page: number;
  type: string;
  severity: "high" | "medium" | "low";
  snippet: string;
  matched_pattern: string;
  suggestion: string;
}

export interface ReferenceItem {
  id: string;
  raw: string;
  status: "resolved" | "unresolved" | "external";
  ref_type: string;
  page: number;
  detail: string;
}

export interface RequirementItem {
  id: string;
  req_id: string;
  status: "DEFINED" | "REFERENCED" | "ORPHANED" | "MISSING";
  description: string;
  defined_page?: number;
  referenced_pages: number[];
  chunk_indices: number[];
}

export interface SearchQuery {
  query: string;
  documentIds?: string[]; // Filter search to specific docs
  limit?: number;
  minScore?: number;
}

export interface SearchResult {
  documentId: string;
  pageNumber: number;
  text: string;
  score: number;
  highlightCoordinates?: [number, number, number, number][];
}

export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  service: string;
  postgres: string;
  chroma: string;
  chroma_backend: string;
  chroma_collection_count: number;
  embedding_provider: string;
  llm_providers: string[];
}

export interface RetrievalChunkDiagnostic {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page: number;
  hybrid_score: number;
  semantic_score: number;
  keyword_score: number;
  preview: string;
}

export interface RetrievalDiagnostics {
  original_query: string;
  expanded_query: string | null;
  chunks: RetrievalChunkDiagnostic[];
  retrieval_count: number;
}
