// Design system tokens and static data for DocuMind AI landing page

export const DESIGN_TOKENS = {
  colors: {
    background: "bg-[#fcfbfa] dark:bg-[#09090b]",
    backgroundMuted: "bg-[#f5f4f0] dark:bg-[#121215]",
    text: "text-neutral-900 dark:text-neutral-100",
    textMuted: "text-neutral-500 dark:text-neutral-400",
    primary: "bg-[#4f46e5] text-white hover:bg-[#4338ca] dark:bg-[#6366f1] dark:hover:bg-[#4f46e5]",
    secondary:
      "bg-white text-neutral-800 border border-neutral-200 hover:bg-neutral-50 hover:border-neutral-300 dark:bg-neutral-900 dark:text-neutral-200 dark:border-neutral-800 dark:hover:bg-neutral-800",
    accent: "text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/30",
    accentBorder: "border-indigo-100 dark:border-indigo-900/50",
    glowGradient: "from-indigo-500/5 to-purple-500/5 dark:from-indigo-500/2 dark:to-purple-500/2",
  },
  typography: {
    heroTitle:
      "text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1]",
    sectionTitle: "text-3xl sm:text-4xl font-bold tracking-tight text-neutral-900 dark:text-white",
    body: "text-base sm:text-lg text-neutral-600 dark:text-neutral-400 leading-relaxed",
    eyebrow: "text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400",
  },
  shadows: {
    sm: "shadow-[0_1px_2px_rgba(0,0,0,0.02)]",
    md: "shadow-[0_4px_12px_rgba(0,0,0,0.03)]",
    lg: "shadow-[0_12px_30px_rgba(0,0,0,0.04)]",
    premium: "shadow-[0_1px_3px_rgba(0,0,0,0.05),0_10px_30px_rgba(0,0,0,0.02)]",
    focus: "focus-visible:ring-2 focus-visible:ring-indigo-500/20 focus-visible:outline-none",
  },
  radius: {
    sm: "rounded-md",
    md: "rounded-lg",
    lg: "rounded-xl",
    xl: "rounded-2xl",
    full: "rounded-full",
  },
  animation: {
    transition: "transition-all duration-300 ease-out-expo",
    timing: {
      fast: 0.15,
      normal: 0.3,
      slow: 0.5,
      cinematic: 0.65,
    },
    spring: {
      type: "spring",
      stiffness: 300,
      damping: 28,
    },
  },
};

export interface NavItem {
  label: string;
  href: string;
}

export const NAVIGATION_ITEMS: NavItem[] = [
  { label: "Features", href: "#features" },
  { label: "Interactive Demo", href: "#demo" },
  { label: "Architecture", href: "#tech" },
  { label: "Security & Trust", href: "#security" },
  { label: "FAQ", href: "#faq" },
];

export interface SocialLogo {
  name: string;
  role: string;
}

export const SOCIAL_PROOF_LOGOS: SocialLogo[] = [
  { name: "Apex Capital", role: "Investment Research" },
  { name: "Vanguard Tech", role: "SaaS Devops" },
  { name: "Nova Legal", role: "Compliance & Auditing" },
  { name: "Helix Bio", role: "Clinical Trials" },
  { name: "Aegis Security", role: "Sovereign Audit" },
];

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  iconName: string;
  tag: string;
  gradient: string;
}

export const FEATURE_ITEMS: FeatureItem[] = [
  {
    id: "rag",
    title: "Double-Attributed RAG Engine",
    description:
      "Run natural language queries over multiple PDFs and docs with millisecond retrieval speed. Every answer includes precise citations linked directly to document coordinates.",
    iconName: "Brain",
    tag: "Intelligence",
    gradient: "from-blue-500/10 to-indigo-500/10 dark:from-blue-500/2 dark:to-indigo-500/2",
  },
  {
    id: "contradictions",
    title: "Cross-Document Collision Checking",
    description:
      "Detect contradictory clauses, misaligned numbers, and timeline discrepancies automatically. Identify risk vectors in parallel contracts or spec files before they deploy.",
    iconName: "ShieldAlert",
    tag: "Safety",
    gradient: "from-amber-500/10 to-orange-500/10 dark:from-amber-500/2 dark:to-orange-500/2",
  },
  {
    id: "entities",
    title: "Visual Entity Mapping",
    description:
      "Generate interactive node-graphs showing how companies, people, locations, and requirements connect across your repository. Surface unseen relations in complex text.",
    iconName: "Network",
    tag: "Visualization",
    gradient: "from-purple-500/10 to-pink-500/10 dark:from-purple-500/2 dark:to-pink-500/2",
  },
];

export interface TechItem {
  title: string;
  description: string;
  iconName: string;
  badge: string;
}

export const TECH_ITEMS: TechItem[] = [
  {
    title: "FastAPI Async Architecture",
    description:
      "Built on high-performance Python ASGI, using asynchronous coroutines to manage file chunking, embedding generation, and LLM orchestration without blocking threads.",
    iconName: "Zap",
    badge: "Backend Core",
  },
  {
    title: "Isolated Vector Shards",
    description:
      "ChromaDB storage sharded per workspace. Direct metadata filter arrays ensure semantic search results never leak between project namespaces.",
    iconName: "Database",
    badge: "Vector Sharding",
  },
  {
    title: "Next.js 15 & TanStack Query",
    description:
      "Sub-second load times using Next.js App Router. State cache hydration is handled seamlessly via TanStack, providing instantaneous client updates on document indexing stages.",
    iconName: "Cpu",
    badge: "Frontend Layer",
  },
];

export interface SecurityCard {
  title: string;
  description: string;
  iconName: string;
}

export const SECURITY_CARDS: SecurityCard[] = [
  {
    title: "Zero Retention Storage",
    description:
      "Uploaded document buffers are shredded from server memory immediately after vector indexing. You retain complete ownership of your raw bytes.",
    iconName: "Lock",
  },
  {
    title: "Enterprise Audit Logging",
    description:
      "Every file ingestion, search vector query, and model config change generates a cryptographically signed audit trail inside your workspace context.",
    iconName: "FileCheck",
  },
  {
    title: "Isolated Workspaces",
    description:
      "Granular member-level roles (Admin, Member, Viewer) isolate organization access scopes. Invite users to specific project vaults with a single command.",
    iconName: "Users",
  },
];

export interface FaqItem {
  question: string;
  answer: string;
}

export const FAQ_ITEMS: FaqItem[] = [
  {
    question: "How does DocuMind AI maintain accuracy and prevent LLM hallucinations?",
    answer:
      "Unlike simple RAG wrappers, DocuMind uses double-attribution indexing. Every generated chunk from the LLM is mathematically cross-referenced with exact coordinates (page number and snippet checksum) in the uploaded source files. If the trust threshold is not met, the system flags the claim as low-confidence.",
  },
  {
    question: "What document types do you support, and how are files structured?",
    answer:
      "We support PDF, DOCX, TXT, and Markdown files. When a file is uploaded, our background worker performs layout-aware parsing, stripping headers/footers, and groups text into semantic chunks based on header hierarchy rather than arbitrary character lengths.",
  },
  {
    question: "Is there a local-only hosting or hybrid deployment option?",
    answer:
      "Yes. Our monorepo is engineered using clean architecture principles, separating the API router layer from the storage services. The backend can be containerized using the provided Docker configurations to run entirely inside your private VPC using local Chroma instances and private LLM endpoints.",
  },
  {
    question: "How are cross-document contradictions identified?",
    answer:
      "Our pipeline executes a pairwise contradiction scan. We cross-compare claims from Document A against statements in Document B by aligning entities and extracting temporal/numerical statements (like dates or headcount limits) and prompt a reasoning LLM to verify if statement A and B can co-exist logically.",
  },
];
