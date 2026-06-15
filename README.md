<div align="center">
  <img src="https://img.shields.io/badge/DocuMind--AI-Enterprise--Grade--Document--Intelligence-6366f1?style=for-the-badge&logo=openai&logoColor=white" alt="DocuMind AI" />

  <h2>Architected for Perfection. Built for Production.</h2>

  <p>
    An enterprise-grade, full-stack AI document intelligence SaaS. Featuring a highly concurrent 2-stage Cross-Encoder Reranking RAG pipeline, multi-tenant RBAC workspaces, sliding-window rate limiters, and complete workspace audit trails.
  </p>

  <p>
    <a href="https://docu-mind-ai-web.vercel.app/"><img src="https://img.shields.io/badge/Live%20Application-Vercel-000000?style=flat-square&logo=vercel" alt="Live App" /></a>
    <a href="https://documind-api-qzei.onrender.com/docs"><img src="https://img.shields.io/badge/Backend%20API-Render-46E3B7?style=flat-square&logo=render" alt="Backend API" /></a>
    <img src="https://img.shields.io/badge/Next.js-15.5-black?style=flat-square&logo=next.js" alt="Next.js" />
    <img src="https://img.shields.io/badge/FastAPI-Async-009688?style=flat-square&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/PostgreSQL-Neon-3178C6?style=flat-square&logo=postgresql" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/TypeScript-Strict-3178C6?style=flat-square&logo=typescript" alt="TypeScript" />
    <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python" alt="Python" />
  </p>
</div>

<br />

<div align="center">
  <img src="apps/web/public/logo.png" alt="DocuMind AI Interactive Demonstration" width="100%" style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);" />
  <p><i>Demonstrating the optimized Alabaster Design System and intelligent multi-tenant AI RAG workflow.</i></p>
</div>

<br />

---

DocuMind AI is not merely an application; it is an exercise in **engineering excellence**. It represents the culmination of distributed systems architecture, advanced information retrieval pipelines, and strict security practices. Whether evaluated through the lens of a user seeking frictionless AI collaboration or a Senior Staff Engineer parsing its infrastructural decisions, DocuMind AI stands as a testament to what modern, decoupled web architecture can achieve.

## 🧭 The Product Vision (User's Perspective)

DocuMind AI fundamentally redefines how organizations interact with structural information. It transforms raw PDF documents into highly accessible, context-aware intelligence networks, backed by strict security boundaries.

### The Ultimate Enterprise Workspace
- **For the Compliance Auditor:** Instantly scan workspaces for factual contradictions, requirements compliance, and reference integrity. The testing engine verifies cross-document assertions, warning users of logical conflicts.
- **For the Enterprise Team:** DocuMind AI introduces the **Multi-Tenant Organization**. Users manage isolated organization entities, invite members with fine-grained roles (Admin, Member, Viewer), and review live audit records of all workspace operations.
- **Precision RAG Engine**: Communicate with multiple documents simultaneously. Ask complex questions and receive streaming answers complete with exact paragraph citations and trust scores, ensuring zero-hallucination outputs.

---

## 💻 The Architecture of Perfection (Engineer's Perspective)

From the very first line of code, DocuMind AI was designed to scale. It rejects monolithic limitations by decoupling presentation state from highly concurrent, asynchronous data pipelines.

### 🌟 Key Engineering Triumphs

1. **The Decoupled Monorepo Architecture:** Next.js 15 leverages edge compiler optimizations for client rendering, while an asynchronous FastAPI backend handles data ingestion, vector operations, and LLM processing. This protects the frontend from server execution timeouts during heavy document chunking or indexing processes.
2. **2-Stage Cross-Encoder Reranking:** Resolves the high-noise limit of vector databases. ChromaDB retrieves the top 30 candidate chunks, which are then passed to a deep-learning Cross-Encoder (`BAAI/bge-reranker-large`). The re-scored top 5 chunks form the LLM context. If external inference fails, a hybrid cos-similarity and Jaccard token overlap validator takes over:
   $$\text{Score} = 0.3 \times \text{TokenOverlap} + 0.7 \times \text{EmbeddingCosineSimilarity}$$
3. **Workspace Isolation & RBAC:** Enforces strict multi-tenancy. Organization members are bound to roles (`admin`, `member`, `viewer`), and authorization checks guard every API endpoint. Read-only viewers are restricted from mutating workspace state or uploading files.
4. **Sliding-Window Rate Limiting:** Built-in rate limiting isolates noisy tenants. Requests are tracked using an optimized in-memory window blocker, separating standard operations (100 req/min) from expensive LLM and vector indexing operations (10 req/min).

---

## 🏛️ System Topology

```mermaid
graph TB
    subgraph "Presentation Tier"
        UI[Next.js 15.5 Client<br/>Alabaster Design System]
        State[Zustand Local State]
        Query[TanStack Server Cache]
    end

    subgraph "API Gateway & Security Tier"
        SDK[Typesafe Client SDK]
        Router[FastAPI Routing Layer]
        Limiter[Sliding-Window Rate Limiter]
        Auth[JWT Guard & Google OAuth]
    end

    subgraph "Business Services Tier"
        OrgService[Organization & RBAC Service]
        AuditLogger[Compliance Audit Engine]
        RAG[2-Stage RAG Pipeline]
        Lab[Q&A Testing Suite]
    end

    subgraph "Persistence & AI Execution"
        DB[(Neon PostgreSQL asyncpg)]
        Chroma[(Chroma DB Vector Store)]
        CE[BAAI/bge-reranker-large]
        LLM[LLM Gateway: OpenAI/Gemini]
    end

    %% Flow connections
    UI --> State
    UI --> Query
    State & Query --> SDK
    SDK -- "HTTP / SSE Streaming" --> Router
    Router --> Limiter
    Limiter --> Auth
    Auth --> OrgService
    OrgService --> AuditLogger
    AuditLogger --> DB
    Router --> RAG
    RAG --> Chroma
    RAG --> CE
    RAG --> LLM
    Router --> Lab
    Lab --> DB
```

---

## 🧠 The 2-Stage Cross-Encoder Reranking Pipeline

To guarantee the highest possible quality for context generation, DocuMind AI implements a hybrid retrieval framework:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client Browser
    participant API as FastAPI RAG Service
    participant VS as Chroma DB
    participant HF as Cross-Encoder (HF)
    participant LLM as LLM Engine

    Client->>API: Submit Query
    Note over API: Stage 1: Vector Search (Dense Retrieval)
    API->>VS: Query Embeddings (Retrieve Top 30 Chunks)
    VS-->>API: 30 Candidates + Metadata
    Note over API: Stage 2: Deep Semantic Reranking
    API->>HF: Submit Query & 30 Chunks
    Note over HF: Score via BAAI/bge-reranker-large
    HF-->>API: Reranked List + Confidence Scores
    Note over API: Select Top 5 Chunks<br/>(Fallback: Hybrid Cosine + Jaccard overlap)
    API->>LLM: Construct System Prompts + Top 5 Chunks
    LLM-->>Client: Stream SSE Tokens + Source Citations
```

---

## 🔒 Enterprise Workspace Security & Auditing

DocuMind AI provides deep security auditing and role-based validation built directly into the core relational schema.

*   **RBAC Enforcement**: Routes are guarded via Dependency Injection. Admin privileges are required to edit organization structures or delete workspaces, members manage content, and viewers can only read RAG outputs.
*   **Audit Compliance Ledger**: Every mutating operation (document ingestion, member role alteration, workspace modifications) writes an entry to an immutable, append-only database table, recording timestamps, user IDs, event labels, and client IP mappings.
*   **Sliding-Window Protection**: Dynamic rate limits guard compute resources. If a user exceeds standard (100 req/min) or query-heavy (10 req/min) limits, the API immediately throws an `HTTP 429` error, which is caught by the client to trigger a floating warning banner.

---

## 🧪 Q&A Test Lab Suite

To measure information retrieval accuracy under different document contexts, the system integrates a permanent testing framework divided into distinct validation scopes:

*   **Easy Pack**: Evaluates direct factual retrieval with standard query-response matching.
*   **Medium Pack**: Tests semantic search resilience against paraphrasing and vocabulary shifts.
*   **Hard Pack**: Validates requirement extraction, reference chains, and conflicting document claims.
*   **Nightmare Pack**: Forces RAG pipeline validation against adversarial inputs, cross-document isolation, and multi-hop logical deductions.

---

## 📊 Relational Mastery: PostgreSQL Schema

The database is designed with third-normal-form (3NF) relational hygiene, utilizing SQLAlchemy’s asynchronous ORM drivers to execute parallel database calls.

*   **Identity & Session Core**: `users`, `sessions`
*   **Multi-Tenancy Entities**: `organizations`, `organization_members`, `workspaces`
*   **Document Intelligence Nodes**: `documents`, `document_chunks`
*   **Compliance & Logs**: `audit_logs`, `testing_logs`

---

<p align="center">
  Crafted with relentless attention to detail by <strong>Shitesh</strong>. <br/>
  <a href="https://docu-mind-ai-web.vercel.app/">Experience the Live Application</a>
</p>
