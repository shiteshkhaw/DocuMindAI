<div align="center">

# DocuMind AI

**Enterprise-grade AI Document Intelligence SaaS Platform**

[![CI](https://github.com/your-org/documind-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/documind-ai/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![pnpm](https://img.shields.io/badge/pnpm-10.28-F69220?logo=pnpm&logoColor=white)](https://pnpm.io)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## Overview

DocuMind AI is a production-grade, multi-tenant document intelligence platform that transforms unstructured documents into structured, queryable knowledge. It combines a **12-stage AI analysis pipeline** with a **conversational RAG engine**, enabling engineers, legal teams, compliance officers, and enterprise customers to interrogate documents with the precision of a senior analyst.

### Why DocuMind AI?

- **Automatically extracts** facts, entities, key-value pairs, and requirements from uploaded documents (PDF, DOCX, Markdown)
- **Detects contradictions** using a two-layer engine: a deterministic regex scanner (zero hallucination) + an LLM semantic layer for nuanced logical inconsistencies
- **Computes a Trust Score** across six measurable dimensions
- **Enables conversational Q&A** with full source citation, backed by a 2-stage retrieve-and-rerank RAG pipeline
- **Streams insights in real time** over Server-Sent Events

### Business Value

| Capability                     | Impact                                            |
| ------------------------------ | ------------------------------------------------- |
| AI Contradiction Detection     | Reduces manual review time by up to 80%           |
| Trust Score                    | Single quantified quality signal for stakeholders |
| Conversational RAG             | Instant document interrogation without full read  |
| Multi-tenant Workspaces & Orgs | Enterprise team collaboration with RBAC           |
| Audit Trail                    | SOC 2-aligned action logging                      |
| Streaming Responses            | Real-time UX without polling                      |

---

## Features

### Document Intelligence Pipeline

- **12-stage sequential analysis**: Entity extraction -> Fact extraction -> Entity consistency -> Deterministic contradiction detection -> Semantic conflict discovery -> Ambiguity detection -> Reference integrity -> Requirement traceability -> Trust score -> Executive summary -> Review copilot
- **Hybrid contradiction engine**: Regex polarity detection (zero hallucination) merged with LLM semantic conflict discovery, deduplicated by summary fingerprint
- **Trust Score V2**: Weighted formula across 6 dimensions with per-dimension deduction explanations
- **Executive Summary & Review Copilot**: AI-generated structured summaries and reviewer checklists

### Retrieval-Augmented Generation (RAG)

- **2-stage pipeline**: Dense ChromaDB vector search (top-30 candidates) -> Cross-encoder reranking (top-5 chunks)
- **Semantic chunking**: TiktokenTokenizer with cl100k_base encoding, 500-token chunks, 50-token overlap
- **Fallback scoring**: Hybrid `0.7 * CosineSimilarity + 0.3 * TokenOverlap` when reranker unavailable
- **Source citations**: Every RAG response includes chunk-level source attributions

### Streaming Chat

- **SSE streaming**: Real-time token streaming with `X-Accel-Buffering: no` headers
- **Multi-document sessions**: Chat sessions span multiple documents within a workspace
- **Streaming contradiction analysis**: SSE endpoint streams findings as they are discovered

### Multi-Tenant Architecture

- **Organizations -> Workspaces -> Documents** hierarchy
- **RBAC**: Three roles (`admin`, `member`, `viewer`) enforced at every mutating route
- **Personal workspace**: Auto-created on signup for immediate use
- **Audit trail**: Immutable log of all mutating actions

### Authentication & Security

- **Stateful JWT**: HS256 tokens (24h expiry) with session-based revocation — tokens are invalid after logout
- **Google OAuth**: Access-token-based login with auto-provisioning and account linking
- **bcrypt password hashing** via passlib
- **Insecure secret detection**: Runtime warning when JWT_SECRET is a known-insecure default
- **Rate limiting**: Redis sliding-window limiter (5 tiers) with in-memory fallback

### Infrastructure & Performance

- **Async throughout**: FastAPI + SQLAlchemy 2.0 asyncpg — no blocking I/O
- **Redis caching**: Analysis results cached (1h TTL); cache-then-DB eliminates redundant AI calls
- **Dramatiq workers**: Background ingestion via Redis queue (3 retries, exponential backoff)
- **Connection pooling**: SQLAlchemy pool (size=10, overflow=20, pre_ping=True)
- **Conditional commits**: Sessions only commit if dirty — saves unnecessary round-trips
- **Analysis locks**: In-memory asyncio.Lock dict (bounded to 500 keys) prevents duplicate analysis runs

---

## Tech Stack

### Backend

| Technology          | Version  | Purpose                       |
| ------------------- | -------- | ----------------------------- |
| Python              | 3.13     | Runtime                       |
| FastAPI             | >= 0.115 | Async API framework           |
| Uvicorn             | >= 0.30  | ASGI server                   |
| SQLAlchemy          | >= 2.0   | Async ORM                     |
| asyncpg             | >= 0.29  | PostgreSQL async driver       |
| Pydantic v2         | >= 2.8   | Schema validation & settings  |
| python-jose         | >= 3.3   | JWT encoding/decoding         |
| passlib[bcrypt]     | >= 1.7   | Password hashing              |
| google-auth         | >= 2.29  | Google OAuth token validation |
| ChromaDB            | >= 0.5   | Vector store                  |
| tiktoken            | >= 0.7   | Token counting & chunking     |
| numpy               | >= 1.24  | Vector arithmetic             |
| httpx               | >= 0.27  | Async HTTP client             |
| tenacity            | >= 8.3   | Retry logic                   |
| dramatiq[redis]     | >= 1.16  | Background task queue         |
| redis[hiredis]      | >= 5.0   | Rate limiter & cache backend  |
| sentry-sdk[fastapi] | >= 2.0   | Error monitoring              |
| resend              | >= 2.0   | Transactional email           |
| pypdf               | >= 4.0   | PDF parsing                   |
| python-docx         | >= 1.1   | DOCX parsing                  |
| markdown            | >= 3.6   | Markdown parsing              |

### Frontend

| Technology           | Version | Purpose                 |
| -------------------- | ------- | ----------------------- |
| Next.js              | ^15.2   | React SSR framework     |
| React                | ^19.0   | UI library              |
| TypeScript           | ^5.7    | Type safety             |
| TailwindCSS          | ^3.4    | Utility CSS             |
| Framer Motion        | ^11.18  | Animations              |
| Zustand              | ^5.0    | Client state management |
| TanStack React Query | ^5.66   | Server state & caching  |
| @react-oauth/google  | ^0.13   | Google OAuth client     |
| @sentry/nextjs       | ^10.62  | Frontend error tracking |
| lucide-react         | ^0.475  | Icon library            |

### Infrastructure & Tooling

| Technology        | Version | Purpose                            |
| ----------------- | ------- | ---------------------------------- |
| pnpm              | 10.28   | Package manager                    |
| Turborepo         | ^2.4    | Monorepo build orchestration       |
| PostgreSQL (Neon) | --      | Primary relational database        |
| ChromaDB          | >= 0.5  | Vector/embedding store             |
| Upstash Redis     | --      | Rate limiting, caching, task queue |
| Supabase Storage  | --      | Document binary storage            |
| Sentry            | --      | Full-stack observability           |
| Resend            | --      | Email delivery                     |
| Docker            | --      | Containerization                   |
| GitHub Actions    | --      | CI/CD                              |
| Vercel            | --      | Frontend deployment                |
| Render            | --      | Backend deployment                 |
| Husky             | ^9.1    | Git hooks                          |
| Prettier          | ^3.5    | Code formatting                    |
| Ruff              | --      | Python linting & formatting        |

### LLM Providers (Configurable)

| Provider         | Config Variable  |
| ---------------- | ---------------- |
| OpenAI           | `OPENAI_API_KEY` |
| Groq             | `GROQ_API_KEY`   |
| Google Gemini    | `GEMINI_API_KEY` |
| HuggingFace      | `HF_API_KEY`     |
| Mock (local dev) | No key required  |

---

## Repository Structure

```
documind-ai/
|-- apps/
|   |-- api/                          # FastAPI backend
|   |   |-- chunking/                 # Semantic boundary chunker (TiktokenTokenizer)
|   |   |-- citations/                # Citation attribution utilities
|   |   |-- cleaners/                 # Text cleaning pipeline
|   |   |-- config.py                 # Pydantic Settings -- all environment vars
|   |   |-- context/                  # Context compression for RAG
|   |   |-- core/                     # Redis manager, Sentry initializer
|   |   |-- db/                       # SQLAlchemy engine, session factory, Base
|   |   |-- embeddings/               # Embedding provider abstraction
|   |   |-- llm/                      # LLM client abstraction layer
|   |   |-- local_storage/            # Local file storage fallback
|   |   |-- main.py                   # FastAPI app: lifespan, CORS, router mounting
|   |   |-- models/                   # SQLAlchemy ORM models
|   |   |   |-- analysis.py           # DocumentAnalysisModel
|   |   |   |-- audit.py              # AuditLogModel
|   |   |   |-- auth.py               # UserModel, SessionModel
|   |   |   |-- chat.py               # ChatSessionModel, MessageModel
|   |   |   |-- document.py           # DocumentModel
|   |   |   |-- organization.py       # OrganizationModel, OrganizationMemberModel
|   |   |   `-- workspace.py          # WorkspaceModel
|   |   |-- observability/            # Rate limiter, structured logger
|   |   |-- orchestration/            # Ingestion orchestrator, RAG engine
|   |   |-- parsers/                  # PDF, DOCX, Markdown parsers + resolver
|   |   |-- repositories/             # Data access objects (CRUD)
|   |   |-- requirements.txt          # Python dependencies
|   |   |-- retrieval/                # Retrieval + reranking logic
|   |   |-- routers/                  # FastAPI route handlers
|   |   |   |-- auth.py               # /auth/signup|login|google|logout|me
|   |   |   |-- chat.py               # /chat/sessions|messages|stream
|   |   |   |-- contradiction.py      # /documents/:id/contradictions[/stream]
|   |   |   |-- document.py           # /documents CRUD + analysis sub-routes
|   |   |   |-- health.py             # /health
|   |   |   |-- organization.py       # /organizations CRUD + members
|   |   |   |-- search.py             # /search
|   |   |   |-- testing.py            # /testing -- dataset generation & validation
|   |   |   `-- workspace.py          # /workspaces CRUD + audit
|   |   |-- schemas/                  # Pydantic request/response schemas
|   |   |-- services/                 # Business logic services
|   |   |   |-- ambiguity.py          # Ambiguity detection
|   |   |   |-- analysis.py           # 12-phase document analysis coordinator
|   |   |   |-- auth.py               # JWT, bcrypt, Google OAuth
|   |   |   |-- cache/                # Redis cache abstraction
|   |   |   |-- chat.py               # Chat session & message management
|   |   |   |-- contradiction_v2.py   # Contradiction analysis service
|   |   |   |-- copilot.py            # Review copilot generator
|   |   |   |-- dependencies.py       # FastAPI DI: embedding & vector store providers
|   |   |   |-- deterministic_contradiction.py  # Regex-based conflict detector
|   |   |   |-- document.py           # Document upload & management
|   |   |   |-- email/                # Email template service
|   |   |   |-- entity.py             # Entity graph extraction service
|   |   |   |-- entity_consistency.py # Cross-entity attribute conflict detection
|   |   |   |-- executive_summary.py  # AI executive summary generator
|   |   |   |-- fact_extraction.py    # Fact (subject-predicate-value) extractor
|   |   |   |-- organization.py       # Organization & membership management
|   |   |   |-- reference.py          # Reference integrity verifier
|   |   |   |-- requirements.py       # Requirement traceability matrix
|   |   |   |-- semantic_conflict.py  # LLM-based semantic conflict discovery
|   |   |   |-- trust_score.py        # Trust Score V2 computation
|   |   |   `-- workspace.py          # Workspace management
|   |   |-- storage/                  # Storage provider abstraction (Supabase / Local)
|   |   |-- tests/                    # pytest test suite (18 test files)
|   |   |-- vectorstore/              # ChromaDB vector store abstraction
|   |   `-- workers/                  # Dramatiq workers
|   |       |-- broker.py             # Redis / StubBroker initialization
|   |       |-- document_ingestion.py # Ingestion actor (max 3 retries, exponential backoff)
|   |       `-- email.py              # Email notification actor
|   |
|   `-- web/                          # Next.js 15 frontend
|       |-- src/
|       |   |-- app/                  # App Router pages & layouts
|       |   |   |-- (app)/dashboard/  # Main dashboard page
|       |   |   |-- auth/             # Login / signup pages
|       |   |   `-- providers.tsx     # React Query + Google OAuth provider wrapper
|       |   |-- components/           # Reusable UI components
|       |   |   |-- dashboard/        # Dashboard-specific components
|       |   |   `-- landing/          # Landing page components
|       |   `-- store/                # Zustand state stores
|       |       |-- useAuthStore.ts   # Auth tokens, user profile
|       |       |-- useChatStore.ts   # Chat sessions, messages, citations
|       |       `-- useWorkspaceStore.ts  # Active workspace selection
|       |-- next.config.ts            # Next.js + Sentry config
|       |-- sentry.server.config.ts   # Sentry server-side setup
|       `-- sentry.edge.config.ts     # Sentry edge runtime setup
|
|-- packages/
|   |-- config/                       # Shared ESLint / Prettier configs
|   |-- prompts/                      # Shared LLM prompt templates
|   |-- sdk/                          # DocuMindSDK -- typed fetch client (TypeScript)
|   |   `-- src/client.ts             # Full SDK: auth, docs, analysis, chat, orgs, streaming
|   |-- types/                        # Shared TypeScript type definitions
|   `-- ui/                           # Shared React UI component library
|
|-- docker/
|   |-- Dockerfile.api                # Python 3.13 multi-stage API image
|   |-- Dockerfile.web                # Node 22 multi-stage Next.js image
|   `-- Dockerfile.worker             # Python 3.13 Dramatiq worker image
|
|-- docs/
|   |-- ARCHITECTURE.md               # Deep technical architecture reference
|   |-- ENGINEERING_HIGHLIGHTS.md     # Key engineering decisions
|   `-- USER_MANUAL.md                # End-user documentation
|
|-- .github/
|   `-- workflows/
|       |-- ci.yml                    # CI: lint, typecheck, build, test, deploy
|       `-- docker.yml                # Docker: build & push to registry
|
|-- docker-compose.yml                # Local full-stack development compose
|-- docker-compose.prod.yml           # Production-ready compose with health checks
|-- package.json                      # Root monorepo scripts
|-- pnpm-workspace.yaml               # pnpm workspace definition
|-- turbo.json                        # Turborepo task pipeline
|-- .env.example                      # All environment variables documented
`-- ARCHITECTURE_CONTEXT.md           # Engineering principles & conventions
```

---

## Architecture Overview

DocuMind AI follows a **layered, service-oriented architecture** with strict clean architecture enforcement:
no business logic in routers, no ORM leakage into API responses.

### Internal Backend Layers

```
Router Layer     -> Route validation, auth dependency, HTTP response shaping
    |
Service Layer    -> Business logic, orchestration, AI pipeline coordination
    |
Repository Layer -> SQL query construction, ORM operations, data access
    |
Model Layer      -> SQLAlchemy declarative ORM models
    |
Database         -> PostgreSQL (asyncpg) + ChromaDB (vector store)
```

---

## System Architecture Diagram

```mermaid
flowchart TD
    User["Browser / Client App"]
    SDK["@documind/sdk TypeScript Client"]
    NextJS["Next.js 15 App - Vercel"]
    API["FastAPI Backend - Render"]
    Auth["Auth Service - JWT + Google OAuth"]
    DocService["Document Service - Upload + Manage"]
    AnalysisCoord["Analysis Coordinator - 12-Phase AI"]
    RAG["RAG Orchestrator - 2-Stage Retrieve + Rerank"]
    CE["Contradiction Engine - Deterministic + Semantic"]
    Postgres["PostgreSQL - Neon DB"]
    Chroma["ChromaDB - Vector Store"]
    Redis["Upstash Redis - Cache + Rate Limit + Queue"]
    Worker["Dramatiq Worker - Ingestion + Email"]
    Supabase["Supabase Storage - File Binaries"]
    Sentry["Sentry - Observability"]
    Resend["Resend - Email"]
    LLM["LLM Providers - OpenAI / Groq / Gemini"]

    User --> SDK --> NextJS --> API
    API --> Auth --> Postgres
    API --> DocService --> Postgres & Supabase & Redis & Worker
    API --> AnalysisCoord --> Chroma & Postgres & Redis & LLM
    API --> RAG --> Chroma & LLM
    API --> CE --> Chroma & LLM
    Worker --> Supabase & Chroma & Postgres & Resend
    API & NextJS --> Sentry
```

---

## Request Flow Diagram

```mermaid
sequenceDiagram
    participant B as Browser
    participant API as FastAPI
    participant Auth as AuthService
    participant DB as PostgreSQL
    participant Cache as Redis
    participant Worker as Dramatiq Worker
    participant Storage as Supabase

    Note over B,Storage: Document Upload Flow
    B->>API: POST /documents/upload (multipart + Bearer)
    API->>Auth: Validate JWT + session lookup
    Auth->>DB: SELECT sessions WHERE access_token = ?
    DB-->>Auth: Session record
    Auth-->>API: UserModel
    API->>Storage: Upload binary file
    Storage-->>API: storage_key
    API->>DB: INSERT document (status=queued)
    API->>Worker: ingest_document.send() via Redis
    API-->>B: DocumentResponse (status=queued)

    Note over Worker,Cache: Background Ingestion
    Worker->>Storage: Download file bytes
    Worker->>Worker: Parse -> Clean -> Chunk -> Embed -> Upsert
    Worker->>DB: UPDATE status=COMPLETED
    Worker->>DB: INSERT document_analyses
    Worker->>Cache: SET analysis key TTL=3600s

    Note over B,Cache: Analysis Fetch
    B->>API: GET /documents/:id/analysis
    API->>Cache: GET analysis:document:{doc_id}
    alt Cache HIT
        Cache-->>API: Cached JSON
    else Cache MISS
        API->>DB: SELECT document_analyses
        API->>Cache: SET (TTL 1h)
    end
    API-->>B: DocumentAnalysisResponse
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant Auth as AuthService
    participant Google as Google OAuth
    participant DB as PostgreSQL

    Note over C,DB: Email/Password Signup
    C->>API: POST /auth/signup {name, email, password}
    API->>Auth: signup(user_in)
    Auth->>DB: Check duplicate email
    Auth->>DB: INSERT users (bcrypt hash)
    Auth->>DB: INSERT workspaces (Personal Workspace)
    Auth->>Auth: create_access_token (HS256, 24h)
    Auth->>DB: INSERT sessions
    API-->>C: UserResponse + access_token + refresh_token

    Note over C,DB: Google OAuth Login
    C->>API: POST /auth/google {token}
    API->>Auth: google_login(token)
    Auth->>Google: GET /oauth2/v3/userinfo
    Google-->>Auth: email, sub, name
    Auth->>DB: Find or create user + INSERT sessions
    API-->>C: TokenResponse

    Note over C,DB: Token Revocation on Logout
    C->>API: POST /auth/logout (Bearer token)
    Auth->>DB: DELETE sessions WHERE access_token = ?
    API-->>C: success: true
```

---

## Document Ingestion State Machine

```mermaid
stateDiagram-v2
    [*] --> QUEUED : upload_document()
    QUEUED --> UPLOADING : Worker picks up task
    UPLOADING --> PARSING : File downloaded from Supabase
    PARSING --> CLEANING : DocumentParserResolver
    CLEANING --> CHUNKING : ContentCleanerPipeline
    CHUNKING --> EMBEDDING : SemanticBoundaryChunker
    EMBEDDING --> INDEXING : embed_documents()
    INDEXING --> COMPLETED : vector_store.upsert()
    COMPLETED --> ANALYZING : Pre-compute 12-phase analysis
    ANALYZING --> COMPLETED : Analysis persisted
    UPLOADING --> FAILED : Exception
    PARSING --> FAILED : Exception
    CHUNKING --> FAILED : Exception
    EMBEDDING --> FAILED : Exception
    INDEXING --> FAILED : Exception
    COMPLETED --> [*]
    FAILED --> [*]
```

---

## AI Analysis Pipeline

```mermaid
flowchart TD
    Start["Document Chunks from ChromaDB"]
    P1["Phase 1 - EntityGraphService\nExtract entities, KV pairs, document summary"]
    P2a["Phase 2a - FactExtractionService\nSubject-predicate-value facts"]
    P2b["Phase 2b - EntityConsistencyService\nAttribute conflict detection"]
    P2c1["Phase 2c-i - DeterministicContradictionDetector\nRegex polarity + numerical conflicts"]
    P2c2["Phase 2c-ii - SemanticConflictDiscovery\nCosine similarity + LLM verification"]
    Merge["Merge and deduplicate by summary fingerprint"]
    P2d["Phase 2d - AmbiguityDetectionService\nVague terms, undefined references"]
    P2e["Phase 2e - ReferenceIntegrityService\nBroken internal references"]
    P2f["Phase 2f - RequirementTraceabilityService\nMissing, orphaned requirements"]
    P2g["Phase 2g - TrustScoreV2Service\nWeighted 6-dimension score"]
    P2h["Phase 2h - ExecutiveSummaryService\nAI-generated summary"]
    P2i["Phase 2i - ReviewCopilotService\nReviewer checklist and risk items"]
    Persist["Persist to PostgreSQL + Redis Cache TTL=1h"]

    Start --> P1 --> P2a
    P2a --> P2b & P2c1 & P2c2
    P2c1 & P2c2 --> Merge
    P2b & Merge --> P2d --> P2e --> P2f --> P2g --> P2h --> P2i --> Persist
```

---

## Trust Score Formula

Trust Score V2 is computed across six weighted dimensions:

| Component                      | Weight | Description                                | Deductions Per Incident                       |
| ------------------------------ | ------ | ------------------------------------------ | --------------------------------------------- |
| C -- Contradiction Health      | 35%    | Conflict severity                          | Critical: -20, High: -12, Medium: -6, Low: -2 |
| Ri -- Reference Integrity      | 20%    | Broken internal cross-references           | -8 per broken ref                             |
| Rt -- Requirement Traceability | 15%    | Missing or orphaned requirements           | Missing: -12, Orphaned: -4                    |
| E -- Entity Consistency        | 15%    | Attribute conflicts across entity mentions | -15 per conflict                              |
| A -- Ambiguity Analysis        | 10%    | Vague, undefined, or ambiguous terms       | High: -8, Med: -4, Low: -1.5                  |
| Dc -- Document Completeness    | 5%     | TODO/TBD placeholder markers               | -8 per placeholder                            |

`Trust Score = 0.35*C + 0.20*Ri + 0.15*Rt + 0.15*E + 0.10*A + 0.05*Dc`

---

## Database Schema

```mermaid
erDiagram
    users {
        string id PK
        string email UK
        string name
        string password_hash
        string auth_provider
        string google_id UK
        datetime created_at
        datetime last_login_at
    }
    sessions {
        string id PK
        string user_id FK
        string access_token UK
        string refresh_token UK
        datetime expires_at
        datetime created_at
    }
    organizations {
        string id PK
        string name
        datetime created_at
    }
    organization_members {
        string id PK
        string organization_id FK
        string user_id FK
        string role
    }
    workspaces {
        string id PK
        string user_id FK
        string organization_id FK
        string name
        string description
        datetime created_at
    }
    documents {
        string id PK
        string name
        string storage_url
        string status
        json metadata_json
        string user_id
        string workspace_id FK
        int progress_percentage
        string failure_reason
        datetime created_at
    }
    document_analyses {
        string id PK
        string document_id FK
        json entities_json
        json facts_json
        json semantic_conflicts_json
        json ambiguities_json
        json references_json
        json requirements_json
        json trust_score_json
        json executive_summary_json
        json review_json
        datetime analyzed_at
    }
    chat_sessions {
        string id PK
        string title
        json document_ids
        string user_id FK
        string workspace_id FK
        datetime created_at
    }
    messages {
        string id PK
        string session_id FK
        string role
        string content
        json citations_json
        datetime created_at
    }
    audit_logs {
        string id PK
        string user_id FK
        string workspace_id
        string organization_id
        string action
        string details
        string ip_address
        datetime timestamp
    }

    users ||--o{ sessions : "has"
    users ||--o{ workspaces : "owns"
    users ||--o{ organization_members : "belongs to"
    organizations ||--o{ organization_members : "has"
    organizations ||--o{ workspaces : "contains"
    workspaces ||--o{ documents : "contains"
    documents ||--o| document_analyses : "has"
    users ||--o{ chat_sessions : "creates"
    workspaces ||--o{ chat_sessions : "scopes"
    chat_sessions ||--o{ messages : "contains"
    users ||--o{ audit_logs : "generates"
```

---

## Environment Variables

### Frontend (root `.env`)

| Variable                       | Required | Description             | Default                 |
| ------------------------------ | -------- | ----------------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL`          | Yes      | Backend API base URL    | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_URL`          | Yes      | Frontend base URL       | `http://localhost:3000` |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Optional | Google OAuth client ID  | --                      |
| `NEXT_PUBLIC_SENTRY_DSN`       | Optional | Sentry DSN for frontend | --                      |

### Backend (`apps/api/.env`)

| Variable                    | Required    | Description                               | Default                         | Security |
| --------------------------- | ----------- | ----------------------------------------- | ------------------------------- | -------- |
| `DATABASE_URL`              | Yes         | PostgreSQL asyncpg connection string      | --                              | Secret   |
| `JWT_SECRET`                | Yes         | HS256 signing secret (min 32 chars)       | `super-secret-key-for-dev`      | Secret   |
| `GOOGLE_CLIENT_ID`          | Optional    | Google OAuth client ID                    | --                              |          |
| `CORS_ORIGINS`              | Yes         | JSON array of allowed origins             | `["http://localhost:3000"]`     |          |
| `MAX_FILE_SIZE_MB`          | No          | Max upload file size                      | `10`                            |          |
| `EMBEDDING_PROVIDER`        | Yes         | `openai`, `gemini`, `huggingface`, `mock` | `mock`                          |          |
| `VECTOR_STORE_PROVIDER`     | Yes         | `chroma`                                  | `chroma`                        |          |
| `OPENAI_API_KEY`            | Optional    | OpenAI API key                            | --                              | Secret   |
| `GEMINI_API_KEY`            | Optional    | Google Gemini API key                     | --                              | Secret   |
| `HF_API_KEY`                | Optional    | HuggingFace API key                       | --                              | Secret   |
| `GROQ_API_KEY`              | Optional    | Groq API key                              | --                              | Secret   |
| `CHROMA_SERVER_HOST`        | No          | ChromaDB remote host (blank=local)        | --                              |          |
| `CHROMA_PERSIST_DIRECTORY`  | No          | Local ChromaDB path                       | --                              |          |
| `CHROMA_API_KEY`            | No          | ChromaDB Cloud API key                    | --                              | Secret   |
| `CHROMA_TENANT`             | No          | ChromaDB tenant                           | `default`                       |          |
| `CHROMA_DATABASE`           | No          | ChromaDB database                         | `default_database`              |          |
| `UPSTASH_REDIS_URL`         | Recommended | Redis URL for rate limiting + caching     | --                              | Secret   |
| `SUPABASE_URL`              | Recommended | Supabase project URL                      | --                              |          |
| `SUPABASE_ANON_KEY`         | Recommended | Supabase anonymous key                    | --                              | Secret   |
| `SUPABASE_SERVICE_ROLE_KEY` | Recommended | Supabase service role key                 | --                              | Secret   |
| `SUPABASE_STORAGE_BUCKET`   | No          | Storage bucket name                       | `documind-vault`                |          |
| `SENTRY_DSN`                | No          | Sentry DSN for backend                    | --                              |          |
| `SENTRY_ENVIRONMENT`        | No          | Sentry environment tag                    | `development`                   |          |
| `SENTRY_TRACES_SAMPLE_RATE` | No          | Traces sample rate                        | `0.1`                           |          |
| `RESEND_API_KEY`            | No          | Resend API key for email                  | --                              | Secret   |
| `EMAIL_FROM`                | No          | Sender email address                      | `noreply@documind.ai`           |          |
| `DRAMATIQ_BROKER_URL`       | No          | Redis URL for workers                     | Falls back to UPSTASH_REDIS_URL | Secret   |

> **Security:** `JWT_SECRET` must be 32+ characters. The app warns at startup if an insecure default is detected.

---

## Installation

### Prerequisites

| Tool    | Version | Install                          |
| ------- | ------- | -------------------------------- |
| Node.js | >= 22   | [nodejs.org](https://nodejs.org) |
| pnpm    | 10.28   | `npm install -g pnpm@10.28.0`    |
| Python  | 3.13    | [python.org](https://python.org) |
| Docker  | Latest  | [docker.com](https://docker.com) |

### 1. Clone

```bash
git clone https://github.com/your-org/documind-ai.git
cd documind-ai
```

### 2. Install Node.js dependencies

```bash
pnpm install
```

### 3. Install Python dependencies

```bash
cd apps/api
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cd ../..
```

### 4. Configure environment

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env with your credentials
```

Minimum for local dev (no external services needed):

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/documind
JWT_SECRET=your-32-char-or-longer-secret-key-here
EMBEDDING_PROVIDER=mock
VECTOR_STORE_PROVIDER=chroma
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

---

## Running Locally

### Option A -- Docker Compose (Recommended)

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Option B -- Manual

**Terminal 1 -- API:**

```bash
cd apps/api && source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 -- Worker:**

```bash
cd apps/api && source venv/bin/activate
dramatiq workers
```

**Terminal 3 -- Frontend:**

```bash
pnpm dev
```

---

## Production Deployment

### Vercel (Frontend)

1. Import repo to Vercel, set Root Directory to `apps/web`
2. Add env vars: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID`, `NEXT_PUBLIC_SENTRY_DSN`
3. Deploy -- Vercel auto-deploys on push to `main`

### Render (Backend + Worker)

1. Create Web Service using `docker/Dockerfile.api`
2. Create Background Worker using `docker/Dockerfile.worker`
3. Set all backend environment variables in Render settings
4. Add `RENDER_DEPLOY_HOOK_URL` to GitHub Actions secrets for automated CD

### Automated CD

The `ci.yml` workflow auto-deploys on merge to `main` after all checks pass.

Required GitHub Secrets:

- `RENDER_DEPLOY_HOOK_URL` -- Render deploy hook URL
- `VERCEL_DEPLOY_HOOK_URL` -- Vercel deploy hook URL

---

## Scripts

### Root Monorepo

| Script   | Command            | Description                    |
| -------- | ------------------ | ------------------------------ |
| `dev`    | `turbo dev`        | Start all apps in dev mode     |
| `build`  | `turbo build`      | Build all packages and apps    |
| `lint`   | `turbo lint`       | Lint all packages and apps     |
| `format` | `prettier --write` | Format all TS/JS/JSON/MD files |

### Frontend

| Script  | Command      | Description             |
| ------- | ------------ | ----------------------- |
| `dev`   | `next dev`   | Dev server on port 3000 |
| `build` | `next build` | Production build        |
| `start` | `next start` | Start production server |
| `lint`  | `next lint`  | ESLint check            |

### Backend

```bash
uvicorn main:app --reload    # Dev server
dramatiq workers              # Task workers
python -m pytest              # Tests
ruff check .                  # Lint
ruff format .                 # Format
```

---

## API Documentation

Interactive docs: `http://localhost:8000/docs` (Swagger) | `http://localhost:8000/redoc` (ReDoc)

All protected endpoints require: `Authorization: Bearer <access_token>`

### Rate Limits

| Tier       | Limit    | Window | Endpoints                           |
| ---------- | -------- | ------ | ----------------------------------- |
| `standard` | 100 req  | 1 min  | Workspaces, sessions, orgs          |
| `heavy`    | 10 req   | 1 min  | Chat messages, contradiction stream |
| `upload`   | 50 req   | 24h    | Document uploads                    |
| `chat`     | 1000 req | 24h    | Chat operations                     |
| `analysis` | 20 req   | 1h     | Analysis operations                 |

### Auth (`/api/v1/auth`)

| Method | Path      | Auth | Description                           |
| ------ | --------- | ---- | ------------------------------------- |
| POST   | `/signup` | No   | Register user. Returns user + tokens. |
| POST   | `/login`  | No   | Email/password login. Returns tokens. |
| POST   | `/google` | No   | Google OAuth login. Returns tokens.   |
| POST   | `/logout` | Yes  | Revoke session token.                 |
| GET    | `/me`     | Yes  | Get current user profile.             |

### Documents (`/api/v1/documents`)

| Method | Path                         | Auth | Description                              |
| ------ | ---------------------------- | ---- | ---------------------------------------- |
| GET    | `/`                          | Yes  | List documents. Filter: `?workspace_id=` |
| GET    | `/:id`                       | Yes  | Get single document + status.            |
| POST   | `/upload`                    | Yes  | Upload document (multipart/form-data).   |
| DELETE | `/:id`                       | Yes  | Delete document and all associated data. |
| GET    | `/:id/analysis`              | Yes  | Full 12-phase analysis result.           |
| GET    | `/:id/facts`                 | Yes  | Extracted factual assertions.            |
| GET    | `/:id/entity-conflicts`      | Yes  | Entity attribute conflicts.              |
| GET    | `/:id/ambiguities`           | Yes  | Detected ambiguities.                    |
| GET    | `/:id/references`            | Yes  | Reference integrity findings.            |
| GET    | `/:id/requirements`          | Yes  | Requirement traceability matrix.         |
| GET    | `/:id/trust-score`           | Yes  | Trust score with breakdown.              |
| GET    | `/:id/executive-summary`     | Yes  | AI executive summary.                    |
| GET    | `/:id/review`                | Yes  | Review copilot checklist.                |
| GET    | `/:id/contradictions`        | Yes  | Contradiction findings (static).         |
| GET    | `/:id/contradictions/stream` | Yes  | Stream contradictions via SSE.           |

### Chat (`/api/v1/chat`)

| Method | Path               | Rate     | Description                     |
| ------ | ------------------ | -------- | ------------------------------- |
| GET    | `/sessions`        | standard | List user chat sessions.        |
| POST   | `/sessions`        | standard | Create new session.             |
| GET    | `/sessions/:id`    | standard | Get session with messages.      |
| POST   | `/messages`        | heavy    | Send message, get RAG response. |
| POST   | `/messages/stream` | heavy    | Stream response via SSE.        |

### Search (`/api/v1/search`)

| Method | Path | Description                       |
| ------ | ---- | --------------------------------- |
| POST   | `/`  | Semantic search across documents. |

### Workspaces (`/api/v1/workspaces`)

| Method | Path         | Description                           |
| ------ | ------------ | ------------------------------------- |
| GET    | `/`          | List workspaces.                      |
| POST   | `/`          | Create workspace.                     |
| PATCH  | `/:id`       | Rename workspace (admin/member only). |
| DELETE | `/:id`       | Delete workspace (admin only).        |
| GET    | `/:id/audit` | Workspace audit logs.                 |

### Organizations (`/api/v1/organizations`)

| Method | Path                        | Description                     |
| ------ | --------------------------- | ------------------------------- |
| GET    | `/`                         | List organizations.             |
| POST   | `/`                         | Create organization.            |
| DELETE | `/:id`                      | Delete (admin only).            |
| GET    | `/:id/members`              | List members.                   |
| POST   | `/:id/members`              | Add member by user_id or email. |
| DELETE | `/:id/members/:userId`      | Remove member.                  |
| PATCH  | `/:id/members/:userId/role` | Update member role.             |

### Health

| Method | Path      | Description                                      |
| ------ | --------- | ------------------------------------------------ |
| GET    | `/health` | System health (Postgres, Redis, ChromaDB, LLMs). |
| GET    | `/`       | Root endpoint with service info.                 |

---

## Security

### Authentication Model

- **Stateful JWT**: Tokens stored in `sessions` table. Logout deletes the session row -- tokens invalid immediately.
- **Algorithm**: HS256, 24h access token, 7-day refresh token
- **Guard**: Runtime startup warning if JWT_SECRET is weak or < 32 chars

### RBAC Authorization

| Action                  | Admin | Member | Viewer |
| ----------------------- | ----- | ------ | ------ |
| View documents / chat   | Yes   | Yes    | Yes    |
| Upload documents        | Yes   | Yes    | No     |
| Delete documents        | Yes   | Yes    | No     |
| Create/rename workspace | Yes   | Yes    | No     |
| Delete workspace        | Yes   | No     | No     |
| View audit logs         | Yes   | Yes    | No     |
| Add/remove org members  | Yes   | No     | No     |
| Update member roles     | Yes   | No     | No     |
| Delete organization     | Yes   | No     | No     |

### Best Practices

1. Never commit `.env` files
2. Rotate `JWT_SECRET` periodically -- invalidates all existing sessions
3. `SUPABASE_SERVICE_ROLE_KEY` is server-side only
4. Restrict `CORS_ORIGINS` to exact production domain
5. Use Redis for distributed rate limiting across API replicas

---

## Error Handling

| HTTP Code | Meaning               | Common Cause                                      |
| --------- | --------------------- | ------------------------------------------------- |
| 400       | Bad Request           | Duplicate email, missing fields                   |
| 401       | Unauthorized          | Invalid/expired token, session revoked            |
| 403       | Forbidden             | Insufficient RBAC role                            |
| 404       | Not Found             | Document not owned by user                        |
| 429       | Too Many Requests     | Rate limit exceeded -- check `Retry-After` header |
| 444       | User Not Found        | Email-based invite with unknown email             |
| 500       | Internal Server Error | Unhandled exception (captured by Sentry)          |

Streaming endpoints emit `{"type": "error", "message": "..."}` JSON events before closing.

---

## Logging

Named structured loggers per module:

```python
logger = logging.getLogger("documind.services.analysis")
logger.info(f"[Analysis] Phase 1 complete {elapsed:.1f}ms | entities={len(entities)}")
```

Log namespaces: `documind.startup`, `documind.services.analysis`, `documind.workers.document_ingestion`,
`documind.workers.broker`, `documind.observability.rate_limiter`, `documind.services.auth`

---

## Testing

```bash
cd apps/api
python -m pytest             # All tests
python -m pytest -v          # Verbose
python -m pytest -k "rag"    # Filter by name
```

### Test Coverage (18 test files)

| File                           | Area                           |
| ------------------------------ | ------------------------------ |
| test_auth.py                   | Signup, login, JWT validation  |
| test_chunking.py               | SemanticBoundaryChunker        |
| test_cleaners.py               | ContentCleanerPipeline         |
| test_contradiction_pipeline.py | Contradiction detection        |
| test_document_intelligence.py  | 12-phase analysis              |
| test_email.py                  | Email notification service     |
| test_embeddings.py             | Embedding provider abstraction |
| test_orchestration.py          | Ingestion orchestrator         |
| test_parsers.py                | PDF, DOCX, Markdown parsers    |
| test_rag.py                    | RAG pipeline and reranking     |
| test_storage.py                | Storage provider               |
| test_caching.py                | Redis cache service            |
| test_vectorstore.py            | ChromaDB vector store          |
| test_workers.py                | Dramatiq worker actors         |
| test_workspace.py              | Workspace management           |
| test_testing.py                | Testing Lab endpoints          |

Test environment (conftest.py) auto-configures:

- `sqlite+aiosqlite:///:memory:` (no Postgres needed)
- ChromaDB ephemeral in-memory mode
- `LocalStorageProvider` (no Supabase needed)
- `StubBroker` (no Redis needed)
- Fresh DB per test, rolled back on teardown

---

## Performance

### Caching Strategy

| Layer                 | Implementation    | TTL           |
| --------------------- | ----------------- | ------------- |
| Analysis results      | Redis ZSET        | 1 hour        |
| Rate limit counters   | Redis ZSET        | Window-scoped |
| ChromaDB vector index | ChromaDB internal | Persistent    |

### Concurrency Controls

- **Analysis deduplication**: `asyncio.Lock` per document (max 500 entries) -- prevents duplicate AI runs
- **Async SQLAlchemy**: Non-blocking, pool size=10, overflow=20
- **Conditional commits**: Only commits if session is dirty
- **Background workers**: Ingestion + email in Dramatiq actors -- API never blocks

### Ingestion Timing (from source logs)

```
[Ingestion] Parse:  ~1200ms per 42-page PDF
[Ingestion] Clean:  ~85ms
[Ingestion] Chunk:  ~310ms (127 chunks, avg 419 tokens)
[Ingestion] Embed:  ~2800ms (1536-dim vectors)
[Ingestion] Upsert: ~560ms
```

---

## CI/CD Pipeline

```mermaid
flowchart LR
    Push["git push to main or PR"]
    FE["Frontend CI\nLint + Typecheck + Build"]
    BE["Backend CI\nRuff + pytest"]
    Deploy["Deploy\nmain branch only"]
    Render["Backend to Render"]
    Vercel["Frontend to Vercel"]

    Push --> FE & BE
    FE & BE --> Deploy
    Deploy --> Render & Vercel
```

### Workflow: `.github/workflows/ci.yml`

**lint-and-build-fe** (all PRs + pushes):

- Setup Node 22 + pnpm 10.28 + pnpm cache
- `pnpm install --frozen-lockfile`
- `pnpm lint` + `pnpm build`

**test-and-verify-be** (all PRs + pushes):

- Setup Python 3.13 + pip cache
- `pip install -r requirements.txt ruff mypy pytest pytest-asyncio`
- `ruff check apps/api` + `ruff format --check apps/api`
- `pytest` with `DATABASE_URL=sqlite+aiosqlite:///:memory:`

**deploy** (push to `main` only, after both CI jobs pass):

- `curl $RENDER_DEPLOY_HOOK_URL` -- backend redeploy
- `curl -X POST $VERCEL_DEPLOY_HOOK_URL` -- frontend redeploy

### Workflow: `.github/workflows/docker.yml`

Triggers on push to `main` or version tags:

- Builds `api`, `web`, and `worker` Docker images
- Pushes to GitHub Container Registry (ghcr.io)

---

## Code Style & Patterns

### Backend

| Pattern              | Implementation                                                         |
| -------------------- | ---------------------------------------------------------------------- |
| Repository Pattern   | `repositories/` -- all DB queries isolated                             |
| Service Layer        | `services/` -- business logic, no HTTP context                         |
| Dependency Injection | FastAPI `Depends()` for DB, auth, vector store, embeddings             |
| Settings Object      | Pydantic `BaseSettings` with env file + field validators               |
| Strategy Pattern     | Embedding providers, storage providers, broker -- swappable via config |
| Lifespan Pattern     | FastAPI `@asynccontextmanager` for startup/shutdown                    |

### Frontend

| Pattern           | Implementation                                                       |
| ----------------- | -------------------------------------------------------------------- |
| Server Components | Default; `use client` only when browser APIs needed                  |
| Global State      | Zustand stores (`useAuthStore`, `useWorkspaceStore`, `useChatStore`) |
| Server State      | TanStack React Query with invalidation                               |
| Type-Safe API     | `@documind/sdk` -- typed `DocuMindSDK` class                         |
| Shared Types      | `@documind/types` package shared between SDK and web                 |

---

## Third-Party Integrations

| Service           | Purpose                                       | Config                   |
| ----------------- | --------------------------------------------- | ------------------------ |
| Neon (PostgreSQL) | Primary relational database                   | `DATABASE_URL`           |
| ChromaDB          | Vector store for embeddings                   | `CHROMA_*`               |
| Upstash Redis     | Rate limiting, analysis cache, Dramatiq queue | `UPSTASH_REDIS_URL`      |
| Supabase Storage  | Binary file storage                           | `SUPABASE_*`             |
| OpenAI            | Embeddings + LLM                              | `OPENAI_API_KEY`         |
| Groq              | Fast LLM inference                            | `GROQ_API_KEY`           |
| Google Gemini     | Embeddings + LLM                              | `GEMINI_API_KEY`         |
| HuggingFace       | Open-source embedding models                  | `HF_API_KEY`             |
| Google OAuth      | Social login                                  | `GOOGLE_CLIENT_ID`       |
| Sentry            | Full-stack error tracking                     | `SENTRY_DSN`             |
| Resend            | Transactional email                           | `RESEND_API_KEY`         |
| Vercel            | Frontend hosting                              | `VERCEL_DEPLOY_HOOK_URL` |
| Render            | Backend + worker Docker hosting               | `RENDER_DEPLOY_HOOK_URL` |

---

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response includes: `postgres` (connected/disconnected), `redis` (connected/not_configured), `redis_version`,
`chroma` (connected/disconnected), `chroma_backend` (local/remote), `chroma_collection_count`,
`embedding_provider` (name + key status), `llm_providers` (list with active/missing status).

### Sentry

Both API and Next.js are instrumented with Sentry:

- Backend: `sentry-sdk[fastapi]` with trace and profile sampling
- Frontend: `@sentry/nextjs` with `/monitoring` tunnel route (bypasses ad-blockers)
- Request errors: `onRequestError = Sentry.captureRequestError`

---

## Scaling Considerations

**Stateless API**: Sessions in Postgres, not server memory. Run any number of replicas behind a load balancer.

**Rate Limiting**: Redis ZSETs enforce limits across all replicas. Falls back to per-process in-memory limiting if Redis is unavailable.

**Worker Scaling**: Add more worker containers to scale ingestion throughput. No coordination required.

**Vector Store**: Set `CHROMA_SERVER_HOST` to point all instances at a shared ChromaDB server.

---

## Troubleshooting

### JWT_SECRET warning on startup

Generate a strong secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Set the output as `JWT_SECRET` in `apps/api/.env`.

### ChromaDB returns 0 results after upload

Check `GET /api/v1/documents/:id` -- inspect `status`, `error`, `failure_reason` fields. Status must be `COMPLETED`.

### Redis not connecting

Without Redis: system runs in degraded mode (in-memory rate limiting, no analysis caching). Set `UPSTASH_REDIS_URL` to enable.

### Document upload returns 403

User is a `viewer` in the workspace's organization. An `admin` must change the role via `PATCH /api/v1/organizations/:id/members/:userId/role`.

### Analysis returns empty results

Document not yet ingested. Wait for `status=COMPLETED`. Check worker container logs for ingestion errors.

---

## FAQ

**Q: Can I run without any LLM API keys?**
Set `EMBEDDING_PROVIDER=mock`. System boots and processes documents. Analysis quality is reduced (mock embeddings).

**Q: What document formats are supported?**
PDF, DOCX, and Markdown. Scanned/image-only PDFs are not supported (no OCR).

**Q: How is multi-tenancy enforced?**
Every resource carries `user_id` + `workspace_id` foreign keys. Every endpoint validates ownership. Cross-tenant access requires explicit organization membership.

**Q: Can I use my own ChromaDB instance?**
Yes. Set `CHROMA_SERVER_HOST` + `CHROMA_SERVER_PORT` for self-hosted, or `CHROMA_API_KEY` + `CHROMA_TENANT` for ChromaDB Cloud.

**Q: How does contradiction detection avoid hallucination?**
Layer 1 uses deterministic regex (zero hallucination). Layer 2 sends only pre-filtered fact pairs to LLM for confirmation. Results are merged and deduplicated.

**Q: How does SSE streaming work?**
Both chat and contradiction endpoints push JSON-encoded events via SSE. `X-Accel-Buffering: no` disables nginx buffering.

---

## Roadmap

### Implemented

- [x] 12-phase document analysis pipeline
- [x] Trust Score V2 with 6-dimension formula
- [x] Streaming contradiction detection (SSE)
- [x] Multi-tenant organizations + workspaces + RBAC
- [x] JWT + Google OAuth authentication
- [x] RAG conversational Q&A with citations
- [x] Redis sliding-window rate limiting
- [x] Dramatiq background workers with retry
- [x] Supabase file storage
- [x] Sentry full-stack observability
- [x] Resend email notifications
- [x] Testing Lab (dataset generation + validation suite)
- [x] Audit trail logging
- [x] Docker multi-stage builds
- [x] GitHub Actions CI/CD

### Future [Inferred]

- [ ] OCR for scanned PDFs
- [ ] Cross-document contradiction analysis
- [ ] Webhook support for analysis completion
- [ ] Export reports (PDF, JSON)
- [ ] Custom LLM model per workspace

---

## Contributing

```bash
git clone https://github.com/your-org/documind-ai.git
cd documind-ai
pnpm install
cd apps/api && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Code Standards

- TypeScript: Prettier + ESLint
- Python: Ruff linter + formatter
- Git hooks: Husky + lint-staged

### PR Guidelines

1. Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `test/`
2. No business logic in routers
3. No ORM models in API responses (use Pydantic schemas)
4. All Python functions must have type annotations
5. TypeScript: no `any`

Before submitting:

```bash
pnpm lint && pnpm build
cd apps/api && ruff check . && ruff format --check . && python -m pytest
```

---

## License

MIT License -- see [LICENSE](LICENSE) for details.

---

## Credits

- [FastAPI](https://fastapi.tiangolo.com) -- Async Python API framework
- [Next.js](https://nextjs.org) -- React production framework
- [ChromaDB](https://www.trychroma.com) -- Open-source vector database
- [Dramatiq](https://dramatiq.io) -- Background task processing
- [Neon](https://neon.tech) -- Serverless PostgreSQL
- [Supabase](https://supabase.com) -- Open-source Firebase alternative
- [Upstash](https://upstash.com) -- Serverless Redis
- [Sentry](https://sentry.io) -- Error and performance monitoring
- [Resend](https://resend.com) -- Email for developers
- [Turborepo](https://turbo.build) -- Monorepo build system

---

_DocuMind AI -- Turn documents into intelligence._

---

<div align="center">

**Architected & Built by [Shitesh K Khaw](https://github.com/shiteshkhaw)**

</div>
