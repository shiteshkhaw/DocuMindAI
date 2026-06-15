import { create } from "zustand";
import { Document, Message, ChatSession } from "@documind/types";

interface ChatState {
  documents: Document[];
  selectedDocumentIds: string[];
  activeSession: ChatSession | null;
  sessions: ChatSession[];
  isStreaming: boolean;
  setDocuments: (docs: Document[] | ((prev: Document[]) => Document[])) => void;
  toggleDocumentSelection: (id: string) => void;
  setSelectedDocumentIds: (ids: string[]) => void;
  setActiveSession: (session: ChatSession | null) => void;
  setSessions: (sessions: ChatSession[]) => void;
  setIsStreaming: (streaming: boolean) => void;
  addMessageToActiveSession: (msg: Message) => void;
  updateLastMessageContent: (content: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  documents: [],
  selectedDocumentIds: [],
  activeSession: null,
  sessions: [],
  isStreaming: false,
  setDocuments: (docs) =>
    set((state) => ({
      documents: typeof docs === "function" ? docs(state.documents) : docs,
    })),
  toggleDocumentSelection: (id) =>
    set((state) => {
      const isSelected = state.selectedDocumentIds.includes(id);
      return {
        selectedDocumentIds: isSelected
          ? state.selectedDocumentIds.filter((docId) => docId !== id)
          : [...state.selectedDocumentIds, id],
      };
    }),
  setSelectedDocumentIds: (selectedDocumentIds) => set({ selectedDocumentIds }),
  setActiveSession: (activeSession) => set({ activeSession }),
  setSessions: (sessions) => set({ sessions }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  addMessageToActiveSession: (msg) =>
    set((state) => {
      if (!state.activeSession) return {};
      return {
        activeSession: {
          ...state.activeSession,
          messages: [...state.activeSession.messages, msg],
        },
      };
    }),
  updateLastMessageContent: (content) =>
    set((state) => {
      if (!state.activeSession || state.activeSession.messages.length === 0) return {};
      const messages = [...state.activeSession.messages];
      const lastMsg = messages[messages.length - 1];
      if (lastMsg) {
        messages[messages.length - 1] = {
          ...lastMsg,
          content: lastMsg.content + content,
        };
      }
      return {
        activeSession: {
          ...state.activeSession,
          messages,
        },
      };
    }),
}));
