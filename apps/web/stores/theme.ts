"use client";
import { create } from "zustand";

type ThemeState = {
  theme: "light" | "dark";
  toggle: () => void;
  set: (t: "light" | "dark") => void;
  hydrate: () => void;
};

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: "dark",
  toggle: () => {
    const next = get().theme === "dark" ? "light" : "dark";
    document.documentElement.classList.toggle("dark", next === "dark");
    localStorage.setItem("jarvis_theme", next);
    set({ theme: next });
  },
  set: (t) => {
    document.documentElement.classList.toggle("dark", t === "dark");
    localStorage.setItem("jarvis_theme", t);
    set({ theme: t });
  },
  hydrate: () => {
    const saved = (localStorage.getItem("jarvis_theme") as "light" | "dark") || "dark";
    document.documentElement.classList.toggle("dark", saved === "dark");
    set({ theme: saved });
  },
}));
