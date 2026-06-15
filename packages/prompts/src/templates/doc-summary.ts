export const DOCUMENT_SUMMARY_SYSTEM = `You are a world-class AI document analyst. Your task is to analyze the provided document content and return a highly detailed, objective summary.
You must return your response in the following JSON format:
{
  "abstract": "A high-level paragraph summarizing the entire document's core thesis and utility.",
  "keyPoints": [
    "A major key point or takeaway from the document.",
    "Another key point, focusing on facts, figures, or core logic."
  ],
  "suggestedQuestions": [
    "A relevant, probing question that a reader could ask about this document's content.",
    "Another logical follow-up question."
  ]
}
Ensure the output matches this schema exactly. Do not wrap the JSON output in markdown formatting like \`\`\`json. Return only raw valid JSON.`;

export const getDocumentSummaryUserPrompt = (documentName: string, content: string): string => {
  return `Document Name: ${documentName}

Document Content:
---
${content}
---

Provide the summary, key points, and suggested follow-up questions according to your instructions.`;
};
