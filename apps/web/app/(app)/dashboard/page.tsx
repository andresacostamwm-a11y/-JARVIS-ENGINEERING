"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: () => api<{ status: string; ai_available: boolean; version: string }>("/api/v1/health"),
  });
  const assets = useQuery({queryKey:["assets"],queryFn:()=>api<unknown[]>("/api/v1/assets")});
  const projects = useQuery({queryKey:["projects"],queryFn:()=>api<unknown[]>("/api/v1/projects")});
  return (<div><h1 className="text-2xl font-bold">Dashboard</h1><p className="mt-1 text-sm text-[var(--muted)]">Vista general del MVP. Datos marcados DEMO son de semilla.</p><div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[{label:"API",value:health.data?.status||"…"},{label:"IA (Grok)",value:health.data?.ai_available?"Disponible":"Degradado"},{label:"Activos",value:assets.data?.length??"…"},{label:"Proyectos",value:projects.data?.length??"…"}].map((c)=><div key={c.label} className="jarvis-panel rounded-xl border p-4"><div className="text-xs text-[var(--muted)]">{c.label}</div><div className="mt-1 text-xl font-semibold">{c.value}</div></div>)}</div><div className="mt-8 grid gap-3 sm:grid-cols-3"><Link href="/assets" className="jarvis-panel rounded-xl border p-4 hover:border-jarvis-400">Ver activos DEMO</Link><Link href="/calculations" className="jarvis-panel rounded-xl border p-4 hover:border-jarvis-400">Ejecutar cálculos verificados</Link><Link href="/drawings" className="jarvis-panel rounded-xl border p-4 hover:border-jarvis-400">Editor de diagramas (React Flow)</Link></div></div>);
}
