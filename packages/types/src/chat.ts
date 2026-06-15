export type MessageRole = "user" | "assistant" | "system";

export interface Citation {
  documentId: string;
  documentName: string;
  pageNumber: number;
  snippet: string;
  score?: number;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  citations?: Citation[];
  createdAt: string;
}

export interface ChatSession {
  id: string;
  title: string;
  documentIds: string[];
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateMessageRequest {
  sessionId: string;
  content: string;
  documentIds: string[];
  stream?: boolean;
  model?: string;
}

export interface CreateSessionRequest {
  title?: string;
  documentIds: string[];
}
