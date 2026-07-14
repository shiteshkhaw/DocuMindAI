export const DOCUMENT_QA_SYSTEM = `You are a helpful, expert document intelligence AI assistant.
Your goal is to answer the user's questions about the uploaded documents by analyzing the provided text segments.

Rules:
1. Base your answers ONLY on the provided document contexts.
2. If the answer cannot be found in the context, state clearly that you do not have enough information in the documents. Do not make up answers.
3. Keep answers concise, factual, and extremely professional.
4. When writing your response, cite specific snippets/documents if possible.

You will be given the contexts in the following format:
[Document Name (Page X)]
"Snippet text..."`;

export interface ContextChunk {
  documentName: string;
  pageNumber: number;
  snippet: string;
}

export const getDocumentQAUserPrompt = (
  query: string,
  contexts: ContextChunk[],
  chatHistory: { role: "user" | "assistant"; content: string }[],
): string => {
  const formattedContext = contexts
    .map((ctx) => `[${ctx.documentName} (Page ${ctx.pageNumber})]\n"${ctx.snippet}"`)
    .join("\n\n");

  const formattedHistory = chatHistory
    .map((msg) => `${msg.role === "user" ? "User" : "Assistant"}: ${msg.content}`)
    .join("\n");

  return `Contexts:
${formattedContext}

---

Chat History:
${formattedHistory}

---

User Question: ${query}

Answer:`;
};
