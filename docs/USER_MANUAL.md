# DocuMind AI: User Manual & Analyst Guide

DocuMind AI is an enterprise document intelligence platform designed to analyze, audit, and interact with complex document vaults. This manual provides a comprehensive, step-by-step guide for end users, compliance analysts, risk officers, and product managers to effectively navigate and leverage the platform.

---

## 🧭 Introduction

DocuMind AI is built to eliminate the risk of manual document audits. It ingests large volumes of technical specifications, legal contracts, or standard operating procedures, and automatically scans them for errors, inconsistencies, and compliance risks.

At its core, the platform acts as an intelligent assistant, enabling you to query your documents conversationally while receiving absolute citations, and reviewing structured risk indices such as the **Trust Score** and **Contradiction Logs**.

---

## 📂 Core Concepts

To use DocuMind AI effectively, it is essential to understand the core structural elements of the system:

### 1. Workspaces

Workspaces are isolated containers used to group related documents and chat sessions.

- **Strict Separation:** Documents uploaded to Workspace A cannot be accessed, read, or queried from Workspace B.
- **Collaboration:** Workspaces can be created under personal accounts or shared within an **Organization** where members have specific roles (Admin, Member, Viewer).

### 2. Documents

Documents are standard files (PDF, DOCX) uploaded by users. Once uploaded, they undergo an ingestion process: text extraction, cleaning, chunking, and vector embedding generation.

### 3. RAG Sessions (Chat)

RAG (Retrieval-Augmented Generation) Sessions are interactive chat conversations linked to one or more documents. When you ask a question, the AI retrieves the most relevant paragraphs from your selected documents to construct a factual, context-grounded response.

### 4. Trust Score

The Trust Score is an explainable quality index (0.0 to 100.0) computed for each document. It evaluates six distinct quality dimensions and applies deductions based on detected issues:

- **Contradiction Health (35%):** Penalizes logical or semantic conflicts.
- **Reference Integrity (20%):** Penalizes broken internal document cross-references.
- **Requirement Traceability (15%):** Penalizes orphaned or undefined requirement codes.
- **Entity Consistency (15%):** Penalizes conflicting attributes assigned to the same entity.
- **Ambiguity Analysis (10%):** Penalizes vague or speculative phrasing.
- **Document Completeness (5%):** Penalizes placeholders like "TODO" or "TBD".

### 5. Contradictions

Contradictions are conflicting claims found within the same document or across documents. They are divided into two categories:

- **Deterministic Contradictions:** Rule-based conflicts (e.g., matching opposing dates for the same deadline, or conflicting budget values).
- **Semantic Contradictions:** Multi-paragraph logical conflicts verified by AI embeddings (e.g., claiming a system "must support SSO" in one section, and "cannot support SSO" in another).

### 6. Entities & Relationships

Entities are concrete nouns (Organizations, People, Dates, Money, Products, Sections, Requirements) extracted from text. DocuMind AI maps these entities and visualizes their cross-references in an interactive relationship graph.

---

## 🚀 Step-by-Step Walkthrough

Follow this step-by-step workflow to configure your workspace, ingest documents, and execute compliance audits.

### 1. Creating an Account

1. Open the DocuMind AI portal in your browser (e.g., `http://localhost:3000`).
2. Click **Sign Up** on the authentication page.
3. Fill in your Name, Email Address, and password.
4. Alternatively, click **Sign up with Google** for secure OAuth2-based authentication.
5. Click **Create Account**.

`[SCREENSHOT_HERE: Signup interface showing email registration and Google OAuth options]`

### 2. Logging In

1. Navigate to the login screen.
2. Enter your registered email address and password.
3. Click **Login** to obtain your security token and enter the dashboard.

`[SCREENSHOT_HERE: Login portal with secure credential fields]`

### 3. Managing Organizations & Workspaces

Upon logging in, a default personal workspace is automatically loaded. To create a dedicated project workspace:

1. Click the **Workspaces Menu** in the sidebar.
2. Under the Workspaces tab, click **New Workspace**.
3. Enter a descriptive Name (e.g., "Project Alabaster Specs") and Description.
4. Select whether to assign this workspace to a shared **Organization** or keep it personal.
5. Click **Create Workspace**.

`[SCREENSHOT_HERE: Workspace creation modal within the settings dashboard]`

### 4. Uploading Documents

1. Navigate to the **Document Intelligence** tab.
2. Click the **Upload File** dropzone.
3. Drag and drop your target PDFs or DOCX files, or browse your local system.
4. The system will write the file, assign a unique hash checksum, and place it in the ingestion queue.
5. Monitor the progress bar (0% to 100%) as the system parses the text and builds embeddings.

`[SCREENSHOT_HERE: Ingestion dashboard showing active document queues, file sizes, and status percentages]`

### 5. Reviewing the Trust Score Dashboard

Once a document is processed, navigate to the **Trust Score** tab to review its quality index:

1. View the large percentage indicator (e.g., `54.4%`) representing the overall document health.
2. Inspect the **6-Dimension Radar Breakdown** mapping specific category scores.
3. Review the **Deductions Log**: every point deduction lists the page number, severity level, specific evidence text, and the unique finding ID.

`[SCREENSHOT_HERE: Trust Score report highlighting deductions, component scores, and evidence tags]`

### 6. Navigating Contradictions

Click the **Contradiction Intelligence** tab to review conflicting claims:

1. The dashboard groups conflicts into **Logical**, **Numerical**, **Temporal**, and **Polarity** tabs.
2. Expand any card to review **Statement A** (with page number) alongside **Statement B** (with page number).
3. Read the AI-generated explanation detailing _why_ these claims conflict and the corresponding severity.

`[SCREENSHOT_HERE: Contradiction log displaying statement comparisons, page highlights, and severity indicators]`

### 7. Reviewing Entities & Visual Graph

1. Navigate to **Entity Intelligence**.
2. Review the filtered lists of entities (e.g., click **Money** to see all budget references, or **Requirement ID** to list all requirements).
3. Interact with the **SVG Network Graph**: hover over any node (entity) to highlight its connected relationships (e.g., which requirements are tied to which organization).

`[SCREENSHOT_HERE: Interactive Entity Graph showing network linkages, node circles, and labels]`

### 8. Using the Workspace Chat (RAG)

1. Navigate to the **Workspace Chat** tab.
2. In the sidebar or chat header, ensure the correct documents are checked/selected.
3. Select your model (e.g., `DocuMind-V3` or `DeepSeek-R1`).
4. Type your query (e.g., "What is the start date and total budget of the project?") and hit Enter.
5. As the AI streams its answer, hover over any **Citation Card** to inspect the source paragraph.

`[SCREENSHOT_HERE: Streaming chat page with document selector, model dropdown, and inline citation numbers]`

### 9. Using the Retrieval Inspector

To audit how the AI gathered context for your query:

1. In the chat interface, click the **Retrieval Inspector** button on the assistant's response.
2. View the **Expanded Query** to see how the system modified your search concepts.
3. Review the retrieved text chunks, sorted by their **Hybrid Score** (combining dense vector cosine similarity and keyword overlap).
4. Review page numbers and exact chunk indexes.

`[SCREENSHOT_HERE: Retrieval Inspector panel with hybrid similarity gauges and query expansion logs]`

### 10. Reviewing Copilot Compliance Recommendations

1. Click the **Review Copilot** tab.
2. Review the **Reviewer Checklist** showing items that require human review.
3. Scan the **Compliance Concerns** and **Risk Items** flagged by the model.
4. Check off items in your dashboard as you complete manual compliance verification tasks.

`[SCREENSHOT_HERE: Review Copilot checklists with interactive checkboxes and risk ratings]`

### 11. Tracing Requirements & References

1. Navigate to the **Requirements Traceability** tab to inspect the status matrix:
   - **COMPLIANT:** Requirement is defined and referenced correctly.
   - **MISSING:** Requirement is referenced in text but has no formal definition section.
   - **ORPHANED:** Requirement is formally defined but never referenced in operational clauses.
2. Navigate to **Reference Validation** to inspect internal cross-links:
   - Review broken reference items (e.g., "See Section 4" when Section 4 does not exist in the document).

`[SCREENSHOT_HERE: Requirements compliance matrix and broken reference ledger]`

---

## 🛠️ Troubleshooting & FAQ

### Ingestion is stuck at "Queued" or "Processing"

- **Check Server Logs:** Ensure the FastAPI backend is running and the background task executor is active.
- **ChromaDB Access:** Ensure ChromaDB credentials in `.env` are correct. If ChromaDB is unreachable, the ingestion task will fail.
- **Large Files:** Ingestion of documents exceeding 100 pages can take up to 2 minutes as multiple LLM API calls are made for entity extraction.

### Trust Score is unusually low

- A low score indicates that the system detected severe contradictions, broken internal references, or incomplete sections (placeholders like "TODO"). Check the deductions log for specific page numbers and evidence.

### Chat answers claim "No Document Context Available"

- Make sure you have selected at least one document in the chat sidebar before typing your query.
- Verify that the document has completed ingestion (status is "completed").

---

## 🎯 Best Practices for Analysts

1. **Upload Clean PDFs:** Documents with high-quality digital text yield much cleaner chunking and extraction results than low-quality scanned documents.
2. **Review Deterministic Conflicts First:** Deterministic contradictions (numerical and polarity) have zero hallucination risk. Resolve these conflicts first before reviewing semantic conflicts.
3. **Audit the Retrieval Inspector:** If the chat response seems incomplete, open the Retrieval Inspector to verify if the relevant sections were fetched and scored correctly.
4. **Use Requirements IDs:** Format requirements consistently (e.g., `REQ-101`, `REQ-102`) to ensure the parser correctly maps the traceability matrix.
