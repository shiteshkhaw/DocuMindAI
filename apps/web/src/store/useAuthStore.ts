import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "@documind/types";
import { DocuMindSDK } from "@documind/sdk";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const sdk = new DocuMindSDK({ baseUrl: apiBaseUrl });

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  isInitialized: boolean;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: true,
      isInitialized: false,
      setAuth: (user, token) => {
        sdk.setToken(token);
        set({ user, token, isInitialized: true, isLoading: false });
      },
      logout: () => {
        sdk.setToken("");
        set({ user: null, token: null, isInitialized: true, isLoading: false });

        if (typeof window !== "undefined") {
          try {
            const { useChatStore } = require("./useChatStore");
            useChatStore.getState &&
              useChatStore.setState({
                documents: [],
                selectedDocumentIds: [],
                activeSession: null,
                sessions: [],
                isStreaming: false,
              });
          } catch (err) {
            console.error("Error resetting chat store", err);
          }
          try {
            const { useWorkspaceStore } = require("./useWorkspaceStore");
            useWorkspaceStore.getState &&
              useWorkspaceStore.setState({
                workspaces: [],
                activeWorkspaceId: null,
                isLoading: false,
              });
          } catch (err) {
            console.error("Error resetting workspace store", err);
          }
        }
      },
      initialize: async () => {
        if (get().isInitialized) return;
        set({ isInitialized: true });
        const { token } = get();
        if (token) {
          sdk.setToken(token);
          try {
            const user = await sdk.getMe();
            set({ user, isLoading: false });
          } catch (error) {
            console.error("Failed to re-authenticate", error);
            set({ user: null, token: null, isLoading: false });
          }
        } else {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: "documind-auth",
    },
  ),
);
