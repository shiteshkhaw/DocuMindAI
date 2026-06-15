import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@documind/types';
import { DocuMindSDK } from '@documind/sdk';

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const sdk = new DocuMindSDK({ baseUrl: apiBaseUrl });

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: true,
      setAuth: (user, token) => {
        sdk.setToken(token);
        set({ user, token });
      },
      logout: () => {
        sdk.setToken("");
        set({ user: null, token: null });
      },
      initialize: async () => {
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
      }
    }),
    {
      name: 'documind-auth',
    }
  )
);
