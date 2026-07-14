import { create } from "zustand";
import { Workspace } from "@documind/types";
import { sdk } from "./useAuthStore";

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspaceId: string | null;
  isLoading: boolean;
  fetchWorkspaces: () => Promise<void>;
  setActiveWorkspace: (id: string) => void;
  createWorkspace: (
    name: string,
    description?: string,
    organizationId?: string,
  ) => Promise<Workspace>;
  deleteWorkspace: (id: string) => Promise<void>;
}

export const useWorkspaceStore = create<WorkspaceState>()((set, get) => ({
  workspaces: [],
  activeWorkspaceId: null,
  isLoading: false,
  fetchWorkspaces: async () => {
    set({ isLoading: true });
    try {
      const workspaces = await sdk.listWorkspaces();
      set({
        workspaces,
        isLoading: false,
        activeWorkspaceId:
          get().activeWorkspaceId || (workspaces.length > 0 ? workspaces[0].id : null),
      });
    } catch (err) {
      console.error("Failed to load workspaces", err);
      set({ isLoading: false });
    }
  },
  setActiveWorkspace: (id: string) => {
    set({ activeWorkspaceId: id });
  },
  createWorkspace: async (name: string, description?: string, organizationId?: string) => {
    const newWs = await sdk.createWorkspace(name, description, organizationId);
    set({ workspaces: [...get().workspaces, newWs], activeWorkspaceId: newWs.id });
    return newWs;
  },
  deleteWorkspace: async (id: string) => {
    await sdk.deleteWorkspace(id);
    const workspaces = get().workspaces.filter((ws) => ws.id !== id);
    const activeWorkspaceId =
      get().activeWorkspaceId === id
        ? workspaces.length > 0
          ? workspaces[0].id
          : null
        : get().activeWorkspaceId;
    set({ workspaces, activeWorkspaceId });
  },
}));
