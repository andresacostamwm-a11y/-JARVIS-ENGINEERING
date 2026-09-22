"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";
import { getToken } from "@/lib/api";
import { JarvisPanel } from "@/components/JarvisPanel";
import clsx from "clsx";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/assets", label: "Activos" },
  { href: "/projects", label: "Proyectos / CAPEX" },
  { href: "/documents", label: "Documentos" },
  { href: "/calculations", label: "Cálculos" },
  { href: "/drawings", label: "Diagramas" },
  { href: "/audit", label: "Auditoría" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, fetchMe, logout } = useAuthStore();
  const { theme, toggle } = useThemeStore();

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    fetchMe();
  }, [fetchMe, router]);

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="jarvis-panel flex w-56 shrink-0 flex-col border-r">
        <div className="border-b border-[var(--border)] px-4 py-4">
          <div className="text-sm font-bold tracking-wide text-jarvis-400">JARVIS</div>
          <div className="text-xs text-[var(--muted)]">Engineering MVP</div>
        </div>
        <nav className="flex-1 space-y-0.5 p-2">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "block rounded-lg px-3 py-2 text-sm",
                pathname.startsWith(item.href)
                  ? "bg-jarvis-600/20 text-jarvis-400"
                  : "text-[var(--muted)] hover:bg-white/5 hover:text-[var(--fg)]"
              )}
            >
              {item.label}
            </Link>
          ))}
          <div className="mt-4 rounded-lg border border-dashed border-[var(--border)] px-3 py-2 text-xs text-[var(--muted)]">
            BIM / IFC — COMING SOON
          </div>
        </nav>
        <div className="border-t border-[var(--border)] p-3 text-xs">
          <div className="truncate font-medium">{user?.full_name || "…"}</div>
          <div className="text-[var(--muted)]">{user?.role}</div>
          {user?.is_demo && (
            <span className="mt-1 inline-block rounded bg-amber-500/20 px-1.5 py-0.5 text-amber-400">
              DEMO
            </span>
          )}
          <div className="mt-2 flex gap-2">
            <button
              onClick={toggle}
              className="rounded border border-[var(--border)] px-2 py-1 hover:bg-white/5"
            >
              {theme === "dark" ? "☀ Claro" : "🌙 Oscuro"}
            </button>
            <button
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="rounded border border-[var(--border)] px-2 py-1 hover:bg-white/5"
            >
              Salir
            </button>
          </div>
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-auto p-6">{children}</div>
      </main>

      <JarvisPanel />
    </div>
  );
}
