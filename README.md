# DocuMind AI — Enterprise-Grade Document Intelligence SaaS

DocuMind AI is a production-ready, highly optimized Document Intelligence SaaS platform designed for conversational RAG, semantic retrieval, multi-document reasoning, and automated compliance verification. Built with a Turborepo monorepo configuration, it features an asynchronous Python/FastAPI backend, a modern Next.js 15 App Router frontend, and an advanced 2-stage semantic retrieval pipeline.

---

## 🏛 System Architecture & Data Flow

### Core Architecture Map

```mermaid
graph TD
    %% Client Tier
    subgraph Client ["Client Tier (Next.js 15 & @documind/ui)"]
        UI[Minimalist Alabaster UI]
        State[Zustand Client State]
        Query[TanStack Server Cache]
        SDK[Typesafe @documind/sdk]
    end

    %% API Gateway & Security Tier
    subgraph Gateway ["API Service Gateway (FastAPI)"]
        Router[API Routers]
        Limiter[Sliding-Window Rate Limiter]
        Auth[OAuth Guard & JWT Verification]
    end

    %% Business Logic Tier
    subgraph Logic ["Business & Pipeline Services"]
        WS_Sec[Workspace Security Service]
        Audit[Audit Logger]
        RAG[RAG Retrieval Pipeline]
        TestLab[Automated Test Suite Lab]
    end

    %% Storage & AI Engine Tier
    subgraph Data ["Data & AI Core"]
        DB[(Neon PostgreSQL / Async SQLAlchemy)]
        Chroma[(Chroma DB Vector Store)]
        Rerank[BAAI/bge-reranker-large]
        LLM[LLM Orchestration: OpenAI / Gemini]
    end

    %% Interactions
    UI --> State
    UI --> Query
    State & Query --> SDK
    SDK -- HTTP / SSE Streaming --> Router
    Router --> Limiter
    Limiter --> Auth
    Auth --> WS_Sec
    WS_Sec --> Audit
    Audit --> DB
    Router --> RAG
    RAG --> Chroma
    RAG --> Rerank
    RAG --> LLM
    Router --> TestLab
    TestLab --> RAG
    TestLab --> DB
```

### 2-Stage Semantic Retrieval Pipeline (RAG)

```mermaid
sequenceDiagram
    autonumber
    actor User as Client UI
    participant RAG as Retrieval Service
    participant VS as ChromaDB Vector Store
    participant CE as Cross-Encoder Reranker
    participant LLM as LLM Provider (OpenAI/Gemini)

    User->>RAG: Ask Question (Query)
    Note over RAG: Pipeline Stage 1: Vector Space Retrieval
    RAG->>VS: Query Embeddings (Retrieve Top 30 Candidate Chunks)
    VS-->>RAG: Returns Top 30 Chunks + Metadata

    Note over RAG: Pipeline Stage 2: Deep Semantic Re-Scoring
    RAG->>CE: Submit Query & 30 Chunks
    Note over CE: Run BAAI/bge-reranker-large Inference<br/>(Local fallback: Hybrid Cosine + Token Overlap)
    CE-->>RAG: Returns Re-Ranked Chunks with Semantic Scores

    Note over RAG: Slice top 5 highest-quality contexts
    RAG->>LLM: Construct System Prompts + Top 5 Chunks
    LLM-->>User: Stream SSE Tokens (Answers with precise source attributions)
```

---

## 🛠 Features Breakdown

### 1. 🔒 Workspace Security & Multi-Tenancy (RBAC)

- **Organizations**: Support for multi-tenant organizations where users can create or join multiple organizational boundaries.
- **Role-Based Access Control (RBAC)**: Fine-grained user levels:
  - `admin`: Complete workspace lifecycle capabilities (rename, delete, manage members).
  - `member`: Standard workspace and document management permissions.
  - `viewer`: Read-only actions (cannot modify workspaces, ingest documents, or delete assets).
- **Audit Trails**: Live compliance ledger recording all key lifecycle actions (workspace creation, deletion, rename, document uploads) with timestamp, actor, description, and IP mapping.
- **Sliding-Window Rate Limiter**:
  - `Standard Route Limit` (100 req/min): Metadata and UI configuration requests.
  - `Heavy Route Limit` (10 req/min): Prompt generations, vector searches, and document chunking.

### 2. ⚡ 2-Stage Cross-Encoder Reranking

- Combines **dense retrieval** (ChromaDB top-30 vector query) with **dense deep learning reranking** via HuggingFace's `BAAI/bge-reranker-large` (pruned down to the Top-5 most relevant chunks).
- **Local Fallback Mode**: If the HuggingFace API is unavailable or unconfigured, the system automatically uses a hybrid score combining Jaccard token overlap intersection and local embedding cosine similarity:
  $$\text{Score} = 0.3 \times \text{TokenOverlap} + 0.7 \times \text{EmbeddingCosineSimilarity}$$

### 3. 🧪 Q&A Test Lab Suite

- A permanent validation lab built into the workspace to evaluate RAG models.
- **Test Packs**:
  - `Easy`: Direct factual retrieval.
  - `Medium`: Context retrieval with minor paraphrasing.
  - `Hard`: Contradictions, requirements analysis, and structural references.
  - `Nightmare`: Cross-document context isolation and adversarial prompts.
- Includes one-click test execution, live trust score evaluation, and retrieval latency metrics.

---

## 📂 Repository Topology

```
DocuMind AI/
├── apps/
│   ├── web/                    # Next.js 15 Frontend Web App
│   └── api/                    # Asynchronous FastAPI Backend
├── packages/
│   ├── config/                 # Monorepo TypeScript & ESLint configurations
│   ├── ui/                     # Shared Minimalist Alabaster UI Design System
│   ├── types/                  # Shared TypeScript types matching Pydantic schemas
│   ├── prompts/                # Shared Prompt engineering templates
│   └── sdk/                    # Fully typed API Client SDK
├── docker/                     # Environment Dockerfiles
├── docker-compose.yml          # Container configuration orchestrator
└── pnpm-workspace.yaml         # PNPM Monorepo workspaces definition
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js**: `v22+`
- **pnpm**: `v10+`
- **Python**: `v3.13+`
- **Git**

### Local Environment Configuration

Clone the repository and set up environment files in their respective folders:

```bash
git clone https://github.com/shiteshkhaw/DocuMindAI.git
cd DocuMindAI
pnpm install
```

#### 1. Frontend Environment ([apps/web/.env.local](file:///c:/Users/khaws/Desktop/Interns/DocuMind%20AI/apps/web/.env.local))

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=201955150232-uj4ads188ei0iimp7eqkoqt0cgnpj7dc.apps.googleusercontent.com
```

#### 2. Backend Environment ([apps/api/.env](file:///c:/Users/khaws/Desktop/Interns/DocuMind%20AI/apps/api/.env))

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:password@your-neon-host/neondb
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
MAX_FILE_SIZE_MB=10
EMBEDDING_PROVIDER=openai
VECTOR_STORE_PROVIDER=chroma
CHROMA_PERSIST_DIRECTORY=./chroma_db
JWT_SECRET=YOUR_SUPER_SECURE_JWT_SECRET_KEY
GOOGLE_CLIENT_ID=201955150232-uj4ads188ei0iimp7eqkoqt0cgnpj7dc.apps.googleusercontent.com
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
HF_API_KEY=your_huggingface_inference_key_here
```

### Starting the Dev Ecosystem

1. **Set Up Python Virtual Environment**

   ```bash
   cd apps/api
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Boot the Monorepo**
   Return to the root directory and start Next.js and FastAPI concurrently via Turborepo:
   ```bash
   cd ../..
   pnpm dev
   ```

   - Next.js Frontend: `http://localhost:3000`
   - FastAPI Swagger Docs: `http://localhost:8000/docs`

---

## 🔒 Google Cloud Console OAuth Configuration

To support **Google Sign-In** with the client-side Google SDK flow, configure your credentials on the [Google Cloud Console](https://console.cloud.google.com):

1. **Authorized JavaScript Origins**
   Add the exact schema and origin of the frontend application. Google OAuth blocks any authentication request originating from an unregistered domain:
   - **Development**: `http://localhost:3000` and `http://127.0.0.1:3000`
   - **Production**: `https://documind-ai.vercel.app` (replace with your Vercel deployment URL)

2. **Authorized Redirect URIs**
   The application uses `@react-oauth/google` with a popup flow (`ux_mode: 'popup'`). This means the authentication code/access token is returned instantly to the existing page context via postMessage rather than triggering a redirect.
   - **No redirect URI is required to be configured for the popup flow**.
   - If you choose to switch to a redirect ux_mode, add:
     - **Development**: `http://localhost:3000/auth/login`
     - **Production**: `https://documind-ai.vercel.app/auth/login`

---

## ☁️ Vercel & Production Deployment

### 1. Frontend Web Application (Vercel)

1. Link your GitHub repository `https://github.com/shiteshkhaw/DocuMindAI.git` to **Vercel**.
2. Set the following Build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web` (Vercel will build this folder and automatically compile packages inside `/packages/` because they are defined as local workspace references in `package.json` and resolved via `pnpm` workspaces).
   - **Build Command**: `pnpm build` (or leave default)
3. Set your production environment variables:
   - `NEXT_PUBLIC_API_URL`: `https://your-api-backend-url.com`
   - `NEXT_PUBLIC_APP_URL`: `https://documind-ai.vercel.app`
   - `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: `201955150232-uj4ads188ei0iimp7eqkoqt0cgnpj7dc.apps.googleusercontent.com`

### 2. Backend API Deployment (Render / Railway / VPS)

Because FastAPI requires a persistent Python environment, deployment is recommended on platforms like Render, Railway, or standard VPS instances.

1. Connect the repository and set the root directory to `apps/api`.
2. Choose **Python** as the runtime.
3. Configure the environment variables in your PaaS hosting portal (ensure `CORS_ORIGINS` includes your Vercel production domain).
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
