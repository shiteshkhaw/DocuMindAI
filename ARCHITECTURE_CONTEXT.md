SECTION A — PRODUCT IDENTITY
DocuMind AI is a production-grade AI document intelligence SaaS platform.

Core capabilities:

- conversational RAG
- semantic retrieval
- multi-document reasoning
- AI summaries
- enterprise workspace UX

The platform should feel:

- premium
- intelligent
- infrastructure-grade
- cinematic
- scalable

Avoid:

- beginner patterns
- generic chatbot UX
- monolithic architecture
- inconsistent abstractions

SECTION B — ENGINEERING PRINCIPLES
Engineering Principles:

- Follow SOLID principles
- Follow clean architecture
- Use feature-based modularity
- Prefer composition over inheritance
- Strong typing everywhere
- No duplicated logic
- No large monolithic components
- No business logic inside UI
- No direct DB access inside routers
- Repository + service abstraction required
- All async flows properly typed
- Reusable abstractions preferred
- Production-level naming conventions only

SECTION C — FRONTEND CONVENTIONS
Frontend Standards:

- Next.js 15 App Router
- Server Components by default
- Client components only when needed
- Zustand for client state
- TanStack Query for server state
- shadcn/ui primitives
- TailwindCSS architecture
- Framer Motion for animations

UI Style:

- light-mode first
- minimal enterprise aesthetic
- cinematic motion design
- soft gradients
- clean whitespace hierarchy
- subtle depth
- intelligent transitions
- premium typography
- modern productivity SaaS feel
- infrastructure-grade visual clarity

Design Inspirations:

- Linear
- Notion
- Vercel
- Arc Browser
- Apple
- Raycast

Avoid:

- dark mode dependency
- glassmorphism-heavy UI
- neon/cyberpunk visuals
- cluttered dashboards
- bootstrap aesthetics
- excessive gradients
- generic AI chatbot designs
- inconsistent spacing

SECTION D — BACKEND CONVENTIONS
Backend Standards:

- FastAPI async architecture
- Repository pattern
- Service layer abstraction
- Pydantic v2 schemas
- SQLAlchemy async ORM
- Dependency injection structure
- SSE streaming responses
- Modular routers
- Structured logging
- Environment-based configuration

No business logic inside routers.
No ORM leakage into API responses.

SECTION E — AI SYSTEM STANDARDS
AI Architecture Standards:

- RAG-first architecture
- Prompt abstraction layer
- Configurable LLM providers
- Streaming token responses
- Source attribution required
- Context compression pipelines
- Semantic chunking
- Metadata-aware retrieval
- Vector-search abstraction layer

Avoid:

- tightly coupled LLM calls
- hardcoded prompts
- giant orchestration files

SECTION F — CODE STYLE
Code Quality Standards:

- small reusable functions
- scalable abstractions
- explicit typing
- predictable naming
- readable architecture
- no magic values
- no deeply nested logic
- comments only when necessary
