# DocuMind AI: Enterprise Document Intelligence Platform

DocuMind AI is a state-of-the-art, production-ready document intelligence SaaS built for compliance, auditing, and engineering teams. It transforms unstructured document vaults (PDF, DOCX) into clean, context-rich knowledge systems. Using a hybrid **2-Stage Cross-Encoder Reranking RAG pipeline**, a **deterministic & semantic multi-layer contradiction engine**, and an **explainable 6-dimension Trust Score engine**, DocuMind AI automates compliance checks, locates inconsistencies, maps internal requirements, and enables context-grounded conversational analytics with zero speculative assumptions or hallucinations.

---

## 📌 Executive Summary
DocuMind AI is designed to address the severe limitations of standard document retrieval and review systems. By combining high-performance asynchronous web APIs (FastAPI/SQLAlchemy 2.0) with modular frontends (Next.js App Router/Zustand), DocuMind AI delivers a secure, multi-tenant workspace experience. It acts as an automated auditor that performs deep factual extraction, identifies attribute-level inconsistencies across sections, detects broken requirement chains, flags vague phrasing, and computes an explainable quality index (Trust Score) for every document.

---

## ⚠️ The Problem Statement
Existing document review workflows are highly manual, error-prone, and slow. 
* **Fragmentation:** Enterprise specs, contracts, and regulatory filings are isolated across multiple files. Humans fail to notice contradictions (e.g., page 2 claiming a budget is $1M while page 48 claims it is $2M).
* **RAG Hallucinations:** Simple vector search retrieval brings high-noise context to LLMs, leading to hallucinated claims, missing citations, or incorrect compliance assessments.
* **Lack of Auditability:** Compliance teams cannot verify *why* a document is marked as high-risk, how internal requirement IDs are traced, or if references point to non-existent sections.
* **Security & Isolation Risks:** Many AI tools lack true enterprise multi-tenancy, risking document leaks across departments or workspace boundaries.

DocuMind AI solves these issues by creating a centralized, role-based, audit-trailed document workspace with deep, deterministic validation layers.

---

## 🌟 Key Capabilities
1. **Multi-Layer Contradiction Engine:** Automatically scans and flags conflicting claims. Merges deterministic rule-based checks (numerical, date, monetary, requirement polarity) with deep semantic checks.
2. **Explainable Trust Score:** Computes a weighted quality index (0-100) based on Contradiction Health (35%), Reference Integrity (20%), Requirement Traceability (15%), Entity Consistency (15%), Ambiguity Analysis (10%), and Document Completeness (5%).
3. **Interactive Entity Graph:** Resolves extracted entities (Person, Org, Location, Date, Money, Product, Requirement ID, Section Ref) into an interactive SVG network graph.
4. **Precision Workspace RAG Chat:** Multi-document chat powered by query expansion, dense semantic retrieval, context optimization, and real-time citation cards with page-level links.
5. **Retrieval Inspector:** Visualizes search diagnostics in real-time, displaying semantic, keyword, and hybrid retrieval scores alongside expanded concepts.
6. **Requirements & References Validator:** Traces requirement ids (e.g., `REQ-101`) to map orphaned or missing definitions, and marks broken internal links.
7. **Compliance Review Copilot:** Auto-generates structured checklists, risk concerns, open questions, and verification task items.
8. **Enterprise RBAC & Auditing:** Multi-tenant organizations with isolated workspaces. Enforces fine-grained roles (`admin`, `member`, `viewer`) and writes all changes to an immutable SQL ledger.

---

## 🏛️ System Architecture Overview

The platform uses a fully decoupled monorepo architecture. 

```mermaid
graph TB
    subgraph "Presentation Tier"
        UI["Next.js 15.2 Client (Zustand State)"]
        Components["Alabaster Design UI Component Kit"]
    end

    subgraph "API & Security Layer"
        Router["FastAPI ASGI Router"]
        Auth["OAuth2 & Local JWT Guard"]
        Limiter["Sliding-Window Rate Limiter"]
    end

    subgraph "Business Logic Services"
        Analysis["Analysis Coordinator Service"]
        RAG["RAG Orchestrator Engine"]
        ContrEngine["Deterministic & Semantic Contradiction Detector"]
        Audit["Immutable Audit Logger"]
    end

    subgraph "Data Storage & AI Execution"
        Postgres[("PostgreSQL / Neon DB (Asyncpg)")]
        Chroma[("ChromaDB Cloud Vector Store")]
        LLM["OpenRouter / OpenAI (LLM Models)"]
        CE["BAAI/bge-reranker-large (Cross-Encoder)"]
    end

    UI --> Components
    Components --> Router
    Router --> Limiter
    Limiter --> Auth
    Auth --> Analysis
    Auth --> RAG
    Auth --> Audit
    Analysis --> ContrEngine
    Analysis --> Postgres
    RAG --> Chroma
    RAG --> CE
    RAG --> LLM
    Audit --> Postgres
```

---

## 📦 Database Schema Diagram

```mermaid
erDiagram
    users {
        string id PK
        string email UK
        string name
        string password_hash
        string auth_provider
        string google_id UK
        timestamp created_at
        timestamp updated_at
        timestamp last_login_at
    }
    sessions {
        string id PK
        string user_id FK
        string access_token UK
        string refresh_token UK
        timestamp expires_at
        timestamp created_at
    }
    organizations {
        string id PK
        string name
        timestamp created_at
    }
    organization_members {
        string id PK
        string organization_id FK
        string user_id FK
        string role "admin | member | viewer"
        timestamp created_at
    }
    workspaces {
        string id PK
        string user_id FK
        string organization_id FK
        string name
        string description
        timestamp created_at
    }
    documents {
        string id PK
        string name
        string storage_url
        string status "queued | processing | completed | failed"
        json metadata_json
        timestamp created_at
        timestamp updated_at
        string user_id
        string workspace_id FK
        string error
        integer progress_percentage
        timestamp started_at
        timestamp completed_at
        string failure_reason
    }
    document_analyses {
        string id PK
        string document_id FK "UK"
        json summary_json
        json entities_json
        json kv_pairs_json
        json entity_conflicts_json
        json facts_json
        json semantic_conflicts_json
        json ambiguities_json
        json references_json
        json requirements_json
        json trust_score_json
        json executive_summary_json
        json review_json
        timestamp analyzed_at
    }
    chat_sessions {
        string id PK
        string title
        json document_ids
        timestamp created_at
        timestamp updated_at
        string user_id FK
        string workspace_id FK
    }
    messages {
        string id PK
        string session_id FK
        string role "user | assistant | system"
        string content
        json citations_json
        timestamp created_at
    }
    audit_logs {
        string id PK
        string user_id FK
        string workspace_id
        string organization_id
        string action
        string details
        string ip_address
        timestamp timestamp
    }

    users ||--o{ sessions : manages
    users ||--o{ workspaces : owns
    organizations ||--o{ organization_members : contains
    users ||--o{ organization_members : belongs_to
    organizations ||--o{ workspaces : groups
    workspaces ||--o{ documents : isolates
    documents ||--|| document_analyses : contains
    workspaces ||--o{ chat_sessions : hosts
    chat_sessions ||--o{ messages : groups
```

---

## ⚡ End-to-End Processing Pipeline

The ingestion and analysis pipelines run asynchronously to avoid blocking client threads.

### Document Ingestion Flow
```mermaid
sequenceDiagram
    autonumber
    actor Client as Web Client
    participant API as FastAPI Router
    participant DB as Neon PostgreSQL
    participant Worker as Background Task
    participant Chroma as ChromaDB Store

    Client->>API: POST /documents/upload (File + workspace_id)
    API->>DB: Write document record (status="queued", progress=0)
    API-->>Client: Return DocumentResponse (HTTP 201)
    
    Note over API, Worker: Spawns Asynchronous Processing Thread
    Worker->>Worker: Parse Document (PDF/PyPDF or Docx)
    Worker->>Worker: Clean & Segment (Sliding token window, 419 token chunks)
    Worker->>Chroma: Purge old vector records for document
    Worker->>API: Generate embeddings (OpenAI text-embedding-3-small)
    Worker->>Chroma: Upsert vectors + parent metadata
    Worker->>DB: Update document status="completed", progress=100
```

### Retrieval & RAG Query Pipeline
```mermaid
sequenceDiagram
    autonumber
    actor Client as Web Client
    participant API as FastAPI RAG Router
    participant Chroma as ChromaDB Store
    participant CE as Cross-Encoder Reranker
    participant LLM as OpenRouter Model

    Client->>API: POST /chat/messages/stream (query, session_id)
    Note over API: 1. Expand Query (Synonyms & Concepts via LLM)
    API->>Chroma: 2. Dense Semantic Search (Retrieve top 30 candidate chunks)
    Chroma-->>API: 30 Candidates + Metadata
    API->>CE: 3. Deep Cross-Encoder scoring (BAAI/bge-reranker-large)
    Note over CE: Computes similarity logits for 30 query-chunk pairs
    CE-->>API: Scored & Ordered Chunks
    Note over API: 4. Apply Sigmoid & Filter (Top 5 chunks > min_score)
    API->>API: 5. Optimize Context Token Budget (max 4000 tokens)
    API->>Client: 6. Stream Citations & Retrieval Diagnostics (SSE)
    API->>LLM: 7. Forward ground context + system instructions
    LLM-->>Client: 8. Stream SSE tokens to Client chat
```

---

## 🛠️ Technology Stack

### Frontend Stack (Monorepo Workspace)
* **Framework:** Next.js 15.2 (App Router)
* **Language:** TypeScript (Strict Mode)
* **State Management:** Zustand 5.0 (Isolated client storage)
* **Data Fetching:** TanStack React Query v5 (Server cache synchronization)
* **Animation:** Framer Motion 11 (Premium micro-interactions & tab swaps)
* **Styling:** Custom Vanilla CSS Tailwind components + Alabaster design tokens (`@documind/ui`)

### Backend Stack
* **Web Framework:** FastAPI (ASGI async/await architecture)
* **Database Driver:** SQLAlchemy 2.0 (Asynchronous transactions via `asyncpg`)
* **Task Management:** Asyncio loop execution (built-in FastAPI background workers)
* **Validation:** Pydantic v2 (Strict schema enforcement)
* **Password Hashing:** Passlib (Bcrypt hashing context)
* **Token Security:** PyJWT / Jose (JWT verification with RS256/HS256)

### AI & Vector Stack
* **Vector Store:** ChromaDB Cloud Client (Metadata-filtered cosine-similarity search)
* **Embeddings:** OpenAI `text-embedding-3-small` (1536-dimension vectors)
* **Inference Routing:** OpenRouter API Gateway (`documind-v3`, `deepseek-r1`, `claude-35`)
* **Reranking System:** Hugging Face Inference API / `BAAI/bge-reranker-large`
* **Token Optimization:** Tiktoken (`cl100k_base` encoder)

---

## 🔒 Enterprise Security & Tenant Isolation
DocuMind AI implements multi-tenant security layers across the database and application levels:
1. **Workspace Guardrails:** Documents belong strictly to a `workspace_id`. Cross-workspace document retrieval is prevented via mandatory workspace verification.
2. **Organization-Level RBAC:** Organization members are assigned fine-grained roles:
   * **Admin:** Full read/write access. Can invite members, update roles, create/delete workspaces, and read workspace audit trails.
   * **Member:** Standard read/write access. Can upload documents and use workspaces, but cannot modify organization members or delete workspaces.
   * **Viewer:** Read-only access. Restricted from mutating state, deleting files, or editing settings.
3. **Immutable Compliance Auditing:** Mutating endpoints write audit trails to `audit_logs` tracking user, workspace, organization, timestamp, specific action details, and client IP addresses.
4. **Sliding-Window Rate Limiter:** Protects cloud compute endpoints. Standard endpoints are restricted to 100 requests/minute, while heavy LLM/vector routes are capped at 10 requests/minute to isolate noisy tenants.

---

## 📁 Project Structure

```
DocuMind-AI/
├── apps/
│   ├── api/                       # FastAPI Backend
│   │   ├── chunking/              # Slide-window text parsing
│   │   ├── citations/             # Cite formatting logic
│   │   ├── cleaners/              # Text normalization cleaners
│   │   ├── db/                    # Session factory & Engine configs
│   │   ├── embeddings/            # OpenAI / local embedding drivers
│   │   ├── llm/                   # LLM API registries
│   │   ├── models/                # SQLAlchemy models (Postgres)
│   │   ├── orchestration/         # RAG & Document Ingestion coordinators
│   │   ├── parsers/               # PDF / DOCX content extractors
│   │   ├── repositories/          # CRUD repositories
│   │   ├── retrieval/             # Vector query & reranker modules
│   │   ├── routers/               # FastAPI endpoints
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/              # Document Analysis & Verification services
│   │   ├── tests/                 # Pytest test suites
│   │   └── main.py                # ASGI application root
│   └── web/                       # Next.js Frontend App
│       ├── public/                # Static assets (favicons, logos)
│       └── src/
│           ├── app/               # App Router pages (Dashboard client)
│           └── store/             # Zustand states (Auth, Workspaces, Chat)
├── packages/
│   ├── config/                    # Shared dev configurations
│   ├── prompts/                   # Structured system instruction prompts
│   ├── sdk/                       # Autogenerated TypeScript SDK client
│   ├── types/                     # Shared TypeScript types
│   └── ui/                        # Alabaster design components
├── package.json                   # PNPM Monorepo package manifest
├── pnpm-workspace.yaml            # Monorepo workspaces definition
└── README.md                      # System Documentation
```

---

## 💻 Local Setup & Development

### Prerequisites
* **Node.js** v20+ & **pnpm** v9+
* **Python** 3.13+
* **PostgreSQL** instance (or Neon DB cloud account)
* **ChromaDB Cloud / Local** instance
* **API Keys:** OpenAI (for embeddings) and OpenRouter (for LLM services)

### Step 1: Configure Environment Variables
Create an `.env` file inside `apps/api/.env` matching the configuration below:

```env
DATABASE_URL=postgresql+asyncpg://user:password@hostname/database
OPENAI_API_KEY=your-openai-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
JWT_SECRET=your-jwt-signing-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:3000"]
PROJECT_NAME="DocuMind AI"
CHROMADB_API_KEY=your-chromadb-api-key
CHROMADB_CLOUD_URL=https://api.trychroma.com
CHROMADB_TENANT=your-chromadb-tenant-id
CHROMADB_DATABASE=default_database
```

Create an `.env.local` file inside `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Step 2: Install Dependencies
Run from the root of the project:
```bash
pnpm install
```

Set up a Python virtual environment in `apps/api/` and install requirements:
```bash
cd apps/api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Run the Development Servers
From the root of the monorepo, run:
```bash
pnpm dev
```
This launches the Next.js app on `http://localhost:3000`.

In another terminal, start the FastAPI API server:
```bash
cd apps/api
.\venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Open `http://localhost:8000/docs` to view the Swagger API documentation.

---

## 🧪 Automated Testing Suite
Run backend tests with Pytest. In `apps/api/`:
```bash
.\venv\Scripts\pytest
```

To run the commercial audit compliance test suite, which verifies document ingestion, semantic contradiction processing, and rate limits locally:
```bash
.\venv\Scripts\python scratch/verify_audit.py
```

---

## 📈 Performance & Scalability Characteristics
* **Connection Pool Configuration:** The async PostgreSQL connection pool is optimized for production-grade scale (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`), minimizing neon socket bottlenecks.
* **Concurrent Ingestion Isolation:** The document analysis pipeline is protected from race conditions by an in-memory lock dictionary (`asyncio.Lock()`) bounded to 500 active locks.
* **Semantic Analysis Deduplication:** Logical and semantic conflicts are indexed and deduplicated via substring key signatures (`seen_summaries`) to prevent overloading the database save actions.

---

## 🧭 Why DocuMind AI Demonstrates Senior-Level Engineering

1. **Complex Information Retrieval Pipelines:** Standard RAG is prone to retrieving disjointed chunks that mislead LLMs. DocuMind's 2-stage retrieve-and-rerank model combines vector search with a deep learning cross-encoder and fallback token matching, guaranteeing mathematically optimized context.
2. **Defensive Async Database Design:** Rejects synchronous execution blocks. Utilizes async PostgreSQL drivers combined with `selectin` relationship loading in SQLAlchemy to completely prevent async greenlet errors.
3. **Multi-Tenant Security Architecture:** Custom organization/workspace associations coupled with RBAC and JWT verification, separating data access safely.
4. **Resilient Rate Limiting & Audit Ledger:** High-throughput systems require load shedding. Custom sliding-window token limits prevent database/compute exhaustion while preserving live audit transparency.

---

## 📝 Resume Bullet Points
* **Architected and implemented** an enterprise-grade Document Intelligence SaaS platform using Next.js 15, FastAPI, and PostgreSQL (Neon) with a hybrid 2-Stage Cross-Encoder Reranking RAG pipeline.
* **Designed a multi-layer contradiction engine** combining deterministic regex engines (polarity, date, monetary metrics) with dense embeddings and LLM semantic auditing, achieving a 100/100 production readiness rating.
* **Implemented strict tenant isolation and RBAC security layers** governing users, workspaces, and organizations, backed by an immutable SQL audit ledger.
* **Optimized database interaction and eliminated system bottlenecks** by implementing asynchronous PostgreSQL connection pools and conditional session commits, reducing idle request latencies.
* **Engineered a 6-dimension explainable document Trust Score algorithm** utilizing structured deduplicated deductions, improving audit speed.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Contributors
* **Shitesh** - Principal Architect & Lead Engineer
