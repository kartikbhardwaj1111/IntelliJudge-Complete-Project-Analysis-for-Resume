/**
 * IntelliJudge — Auth Store (Zustand)
 *
 * Single source of truth for authentication state.
 * Persists the JWT token and user object to localStorage so the session
 * survives page refreshes without a round-trip to /api/auth/me.
 *
 * Usage:
 *   const { user, token, login, logout, isAuthenticated } = useAuthStore();
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { api, tokenStore } from "@/lib/api";
import type { AuthResponse, User } from "@/types";

// Sync token to a cookie so Next.js middleware can read it (middleware
// runs on the edge and cannot access localStorage).
function setCookie(token: string) {
  if (typeof document === "undefined") return;
  const maxAge = 60 * 60 * 24; // 24 hours — matches JWT_EXPIRY_HOURS
  document.cookie = `ij_token=${token}; path=/; max-age=${maxAge}; SameSite=Lax`;
}
function clearCookie() {
  if (typeof document === "undefined") return;
  document.cookie = "ij_token=; path=/; max-age=0";
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;

  // Actions
  login(email: string, password: string): Promise<void>;
  register(email: string, username: string, password: string): Promise<void>;
  logout(): void;
  refreshUser(): Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      async login(email, password) {
        const data = await api.post<AuthResponse>("/auth/login", {
          email,
          password,
        });
        tokenStore.set(data.token);
        setCookie(data.token);
        set({ user: data.user, token: data.token, isAuthenticated: true });
      },

      async register(email, username, password) {
        const data = await api.post<AuthResponse>("/auth/register", {
          email,
          username,
          password,
        });
        tokenStore.set(data.token);
        setCookie(data.token);
        set({ user: data.user, token: data.token, isAuthenticated: true });
      },

      logout() {
        tokenStore.clear();
        clearCookie();
        set({ user: null, token: null, isAuthenticated: false });
      },

      async refreshUser() {
        // Re-fetch the current user profile — call on app boot to validate
        // that the stored token is still valid.
        if (!get().token) return;
        try {
          const user = await api.get<User>("/auth/me");
          set({ user, isAuthenticated: true });
        } catch {
          // Token expired or revoked — clear state
          tokenStore.clear();
          set({ user: null, token: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: "ij-auth",
      // Only persist token + user — isAuthenticated is derived on rehydration
      partialize: (state) => ({ user: state.user, token: state.token }),
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          state.isAuthenticated = true;
          tokenStore.set(state.token);
          setCookie(state.token);
        }
      },
    }
  )
);
