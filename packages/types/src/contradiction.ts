import { Citation } from "./chat.js";

export interface ConflictingStatement {
  text: string;
  page: number;
  documentId: string;
}

export interface ContradictionInsight {
  id: string;
  type: "timeline" | "statement" | "numerical" | "logical" | "requirement" | "entity";
  severity: "low" | "medium" | "high" | "critical";
  confidence: number;
  summary: string;
  explanation: string;
  conflictingStatements: ConflictingStatement[];
  citations: Citation[];
}
