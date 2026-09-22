"use client";
import { create } from "zustand";
import { api, setTokens, clearTokens } from "@/lib/api";

type User = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  org_id: string | null;
  is_demo: boolean;
};

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  login: async (email, password) => {
    const data = await api<{ access_token: string; refresh_token: string }>(
      "/api/v1/auth/login",
      { method: "POST", body: JSON.stringify({ email, password }) }
    );
    setTokens(data.access_token, data.refresh_token);
    const me = await api<User>("/api/v1/auth/me");
    set({ user: me });
  },
  logout: () => {
    clearTokens();
    set({ user: null });
  },
  fetchMe: async () => {
    set({ loading: true });
    try {
      const me = await api<User>("/api/v1/auth/me");
      set({ user: me });
    } catch {
      clearTokens();
      set({ user: null });
    } finally {
      set({ loading: false });
    }
  },
}));
