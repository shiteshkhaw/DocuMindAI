import {
  Document,
  DocumentAnalysis,
  SearchQuery,
  SearchResult,
  ChatSession,
  Message,
  CreateSessionRequest,
  CreateMessageRequest,
  ContradictionInsight,
  HealthStatus,
  TrustScore,
  ExecutiveSummary,
  ReviewCopilot,
  AmbiguityFinding,
  ReferenceItem,
  RequirementItem,
  User,
  TokenResponse,
  Workspace,
} from "@documind/types";

export class DocuMindSDK {
  private baseUrl: string;
  private token?: string;

  constructor(config: { baseUrl: string; token?: string }) {
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.token = config.token;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);
    if (this.token) {
      headers.set("Authorization", `Bearer ${this.token}`);
    }
    if (!(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error [${response.status}]: ${errorText || response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  // Auth
  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await this.request<TokenResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async googleLogin(token: string): Promise<TokenResponse> {
    const res = await this.request<TokenResponse>("/api/v1/auth/google", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async signup(name: string, email: string, password: string): Promise<User> {
    const res = await this.request<User>("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    });
    if (res.access_token) {
      this.setToken(res.access_token);
    }
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/api/v1/auth/me");
  }

  // Workspaces
  async listWorkspaces(): Promise<Workspace[]> {
    return this.request<Workspace[]>("/api/v1/workspaces");
  }

  async createWorkspace(name: string, description?: string, organizationId?: string): Promise<Workspace> {
    return this.request<Workspace>("/api/v1/workspaces", {
      method: "POST",
      body: JSON.stringify({ name, description, organization_id: organizationId }),
    });
  }

  async deleteWorkspace(id: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(`/api/v1/workspaces/${id}`, {
      method: "DELETE",
    });
  }

  // Documents
  async listDocuments(workspaceId?: string): Promise<Document[]> {
    const query = workspaceId ? `?workspace_id=${workspaceId}` : "";
    return this.request<Document[]>(`/api/v1/documents${query}`);
  }

  async getDocument(id: string): Promise<Document> {
    return this.request<Document>(`/api/v1/documents/${id}`);
  }

  async uploadDocument(file: File, workspaceId?: string): Promise<Document> {
    const formData = new FormData();
    formData.append("file", file);
    if (workspaceId) {
      formData.append("workspace_id", workspaceId);
    }
    return this.request<Document>("/api/v1/documents/upload", {
      method: "POST",
      body: formData,
    });
  }

  async deleteDocument(id: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(`/api/v1/documents/${id}`, {
      method: "DELETE",
    });
  }

  // Analysis
  async getAnalysis(documentId: string): Promise<DocumentAnalysis> {
    return this.request<DocumentAnalysis>(`/api/v1/documents/${documentId}/analysis`);
  }

  // Phase 2 — Document Intelligence
  async getTrustScore(documentId: string): Promise<TrustScore> {
    return this.request<TrustScore>(`/api/v1/documents/${documentId}/trust-score`);
  }

  async getExecutiveSummary(documentId: string): Promise<ExecutiveSummary> {
    return this.request<ExecutiveSummary>(`/api/v1/documents/${documentId}/executive-summary`);
  }

  async getReview(documentId: string): Promise<ReviewCopilot> {
    return this.request<ReviewCopilot>(`/api/v1/documents/${documentId}/review`);
  }

  async getAmbiguities(documentId: string): Promise<AmbiguityFinding[]> {
    return this.request<AmbiguityFinding[]>(`/api/v1/documents/${documentId}/ambiguities`);
  }

  async getReferences(documentId: string): Promise<ReferenceItem[]> {
    return this.request<ReferenceItem[]>(`/api/v1/documents/${documentId}/references`);
  }

  async getRequirements(documentId: string): Promise<RequirementItem[]> {
    return this.request<RequirementItem[]>(`/api/v1/documents/${documentId}/requirements`);
  }

  async getContradictions(documentId: string, model?: string): Promise<ContradictionInsight[]> {
    const queryParams = model ? `?model=${model}` : "";
    return this.request<ContradictionInsight[]>(`/api/v1/documents/${documentId}/contradictions${queryParams}`);
  }

  async getHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>("/health");
  }

  // Phase 3.6 Testing Lab
  async generateTestDataset(level: "easy" | "medium" | "hard" | "nightmare", workspaceId?: string): Promise<Document[]> {
    const query = workspaceId ? `?level=${level}&workspace_id=${workspaceId}` : `?level=${level}`;
    return this.request<Document[]>(`/api/v1/testing/generate${query}`, {
      method: "POST"
    });
  }

  async runValidationSuite(): Promise<any> {
    return this.request<any>("/api/v1/testing/run-suite", {
      method: "POST"
    });
  }

  async *streamContradictions(documentId: string, model?: string): AsyncGenerator<any, void, unknown> {
    const queryParams = model ? `?model=${model}` : "";
    const headers: Record<string, string> = {};
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}/api/v1/documents/${documentId}/contradictions/stream${queryParams}`, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => response.statusText);
      throw new Error(`Contradiction streaming failed [${response.status}]: ${errorText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body from streaming endpoint.");

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;

          const dataStr = trimmed.slice(6);
          if (dataStr === "[DONE]") return;

          try {
            const parsed = JSON.parse(dataStr);
            yield parsed;
          } catch (err) {
            // Silently skip malformed JSON
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async search(query: SearchQuery): Promise<SearchResult[]> {
    return this.request<SearchResult[]>("/api/v1/search", {
      method: "POST",
      body: JSON.stringify(query),
    });
  }

  // Chat
  async listSessions(): Promise<ChatSession[]> {
    return this.request<ChatSession[]>("/api/v1/chat/sessions");
  }

  async createSession(req: CreateSessionRequest): Promise<ChatSession> {
    return this.request<ChatSession>("/api/v1/chat/sessions", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async getSession(id: string): Promise<ChatSession> {
    return this.request<ChatSession>(`/api/v1/chat/sessions/${id}`);
  }

  async sendMessage(req: CreateMessageRequest): Promise<Message> {
    return this.request<Message>("/api/v1/chat/messages", {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  // Streaming message generator (SSE)
  // Yields event chunks as they arrive from the real backend SSE stream.
  // Throws on HTTP errors or backend-reported error events.
  async *streamMessage(req: CreateMessageRequest): AsyncGenerator<any, void, unknown> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}/api/v1/chat/messages/stream`, {
      method: "POST",
      headers,
      body: JSON.stringify(req),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => response.statusText);
      throw new Error(`Streaming failed [${response.status}]: ${errorText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body from streaming endpoint.");

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;

          const dataStr = trimmed.slice(6);
          if (dataStr === "[DONE]") return;

          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.type === "error") {
              throw new Error(parsed.content || "Unknown backend error during streaming.");
            }
            yield parsed;
          } catch (err) {
            if (err instanceof SyntaxError) {
              continue;
            }
            throw err;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // Organizations
  async listOrganizations(): Promise<any[]> {
    return this.request<any[]>("/api/v1/organizations");
  }

  async createOrganization(name: string): Promise<any> {
    return this.request<any>("/api/v1/organizations", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  async listOrganizationMembers(orgId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/organizations/${orgId}/members`);
  }

  async addOrganizationMember(orgId: string, userId: string, role: string = "member"): Promise<any> {
    return this.request<any>(`/api/v1/organizations/${orgId}/members`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId, role }),
    });
  }

  async updateOrganizationMemberRole(orgId: string, userId: string, role: string): Promise<any> {
    return this.request<any>(`/api/v1/organizations/${orgId}/members/${userId}/role`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    });
  }

  async getWorkspaceAuditLogs(workspaceId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/workspaces/${workspaceId}/audit`);
  }
}
