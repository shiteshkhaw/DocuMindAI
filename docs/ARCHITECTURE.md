# DocuMind AI: Technical Architecture Design Document

This document outlines the technical design, architectural patterns, database schemas, and data pipelines of DocuMind AI. It serves as an internal guide for senior staff engineers, security officers, and systems architects.

---

## 🎯 System Goals & Non-Goals

### Goals

- **Strict Multi-Tenant Isolation:** Enforce user, workspace, and organization isolation boundaries. Prevent cross-workspace data leakage at the API and database levels.
- **Low Latency & High Concurrency:** Maximize database throughput and ensure the presentation layer remains responsive under high document ingestion loads.
- **Auditability & Traceability:** Maintain an immutable ledger of all mutating workspace operations. Provide explainable confidence and trust score metrics.
- **State Decoupling:** Keep the frontend stateless, relying on reactive store configurations and type-safe client SDK contracts.

### Non-Goals

- **Real-time Document Co-authoring:** The system is an analytics and retrieval engine, not a real-time collaborative document editor (like Google Docs).
- **Multi-Format Media Processing:** The ingestion pipeline focuses strictly on textual document formats (PDF, DOCX) and does not support video or audio parsing.

---

## 🏛️ Architectural Decisions & Tradeoffs

1. **Monorepo Architecture (pnpm Workspaces):**
   - _Decision:_ Decoupled web application, CLI configs, shared TypeScript types, and SDK packages into a single repository managed via `pnpm`.
   - _Tradeoff:_ Requires a unified dependency build graph, but significantly simplifies contract-sharing and type safety.
2. **Asynchronous FastAPI Execution Model:**
   - _Decision:_ Used FastAPI's asynchronous ASGI framework combined with SQLAlchemy 2.0 (`asyncpg`) to handle I/O-bound operations.
   - _Tradeoff:_ Asynchronous programming in Python requires careful management of task loops and context boundaries to avoid blocking the event loop.
3. **2-Stage Retrieve-and-Rerank Pipeline:**
   - _Decision:_ Dense vector search is performed in ChromaDB to retrieve 30 candidates, which are then reranked using a Cross-Encoder model down to the top 5 chunks.
   - _Tradeoff:_ Adds ~100-300ms to the retrieval process, but drastically reduces RAG noise and eliminates LLM context hallucinations.

---

## 💻 Backend Architecture

The backend is structured around modular, layered services and repository patterns.

```
apps/api/
├── db/                        # Database connectivity & Session creation
├── models/                    # Declarative SQLAlchemy ORM models
├── repositories/              # CRUD operations and SQL construction
├── services/                  # Document analysis, auditing, and business logic
├── orchestration/             # Document ingestion and RAG coordinators
├── routers/                   # API gateway routes
└── main.py                    # Application lifespans & Middleware registry
```

### Async Database Session Flow

Every incoming request initiates an asynchronous SQLAlchemy session in `get_db()`.

- **Pooling:** Connection parameters (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`) prevent neon connection saturation during high-throughput parallel queries.
- **Conditional Commits:** To eliminate network round-trip overhead on read-only requests, the session commit is executed conditionally:
  ```python
  if session.new or session.dirty or session.deleted:
      await session.commit()
  ```

---

## 💻 Frontend Architecture

The frontend is built on Next.js 15 App Router and uses a decoupled state model:

```
apps/web/src/
├── app/                       # App Router layouts, CSS, and main page dashboard
└── store/                     # Zustand stores for reactive client state
    ├── useAuthStore.ts        # Client credentials, tokens, and active user profile
    ├── useWorkspaceStore.ts   # Active workspace selection and shared metadata
    └── useChatStore.ts        # Message history, citations, and retrieval diagnostics
```

### Reactive State Sync

All data fetches utilize **TanStack React Query** to cache server state. Local UI interactions (collapsible panels, tab routing, query inputs) are handled by **Zustand** stores, keeping the rendering tree clean and lightweight.

---

## 🧠 AI Pipeline & Contradiction Engine Design

DocuMind's analysis coordinator coordinates 12 distinct extraction and verification stages:

### Step 1: Segmentation & Chunking

- Documents are cleaned of control characters.
- Segmented into sliding-window text blocks using a `TiktokenTokenizer` set to `cl100k_base` (average size: 419 tokens per chunk).

### Step 2: Entity Graph & Fact Extraction

- **EntityGraphService:** Extracts key entities (Person, Org, Location, Date, Money, Product, Requirement ID, Section Ref) using structured schemas.
- **FactExtractionService:** Processes text chunks in batches to construct factual assertions in subject-predicate-value format.

### Step 3: Multi-Layer Contradiction Engine

The contradiction engine executes in two distinct validation layers:

- **Layer 1: DeterministicContradictionDetector:** High-speed regex checks scan the text for concrete polarity conflicts (e.g., `system shall encrypt` vs `system shall not encrypt`) and numerical/date conflicts.Detections are 100% accurate, carrying zero hallucination risk.
- **Layer 2: SemanticConflictDiscovery:** Computes cosine similarity between all pairwise facts. Pairs with a similarity score in the "contradiction zone" (between 0.20 and 0.85) are flagged and sent to the LLM to verify and generate an explanation.

### Step 4: Trust Score V2 Computation

The Trust Score evaluates the quality of a document across 6 dimensions:
$$\text{Trust Score} = 0.35 \times C + 0.20 \times R_i + 0.15 \times R_t + 0.15 \times E + 0.10 \times A + 0.05 \times D_c$$
Where:

- $C$: Contradiction Health (deductions per conflict based on severity: Critical = 20, High = 12, Medium = 6, Low = 2).
- $R_i$: Reference Integrity (broken internal references deduct 8 points).
- $R_t$: Requirement Traceability (missing requirements deduct 12 points, orphaned deduct 4).
- $E$: Entity Consistency (attribute conflicts deduct 15 points).
- $A$: Ambiguity Analysis (vague terms deduct 8, 4, or 1.5 points).
- $D_c$: Document Completeness (TODO/TBD placeholders deduct 8 points).

---

## 🔒 Security & Multi-Tenancy Design

- **Route-Level Authorization:** FastAPI dependency injection enforces JWT token verification (`get_current_user`) for all non-public endpoints.
- **Workspace Isolation:** Every document and chat session contains a foreign key relation to a `workspace_id`. Queries must explicitly match the selected workspace and assert user access to prevent cross-tenant data leaks.
- **Organization Membership & RBAC:** Users are assigned roles within an organization (`admin`, `member`, `viewer`). RBAC verification prevents Viewers from executing mutations, uploading documents, or deleting workspaces.
- **Compliance Audit Trail:** Mutating actions are logged in the `audit_logs` table, capturing:
  - `user_id` and `workspace_id` / `organization_id`
  - `action` type and descriptive `details` string
  - Client `ip_address` and `timestamp`

---

## 📉 Concurrency, Performance & Failure Modes

### Concurrency Management

- To prevent database race conditions during concurrent document analyses, the coordinator uses an in-memory lock dictionary (`_analysis_locks = {}`) bounded to 500 active locks.
- Sequential API requests from a single client are handled by a **sliding-window rate limiter** to prevent resource exhaustion.

### Failure Modes & Resiliency

- **Embedding/Reranker Timeout:** If the external Cross-Encoder API fails, the retrieval service falls back to a local hybrid formula:
  $$\text{Score} = 0.7 \times \text{CosineSimilarity} + 0.3 \times \text{TokenOverlap}$$
- **API Rate Limits:** If standard API limit thresholds (100 req/min) or query limits (10 req/min) are breached, the server throws an `HTTP 429` error, which is handled gracefully by the client to trigger floating warning banners.
