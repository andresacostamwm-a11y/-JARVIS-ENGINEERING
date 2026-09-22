"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

type Asset = {
  id: string;
  tag: string;
  name: string;
  asset_type: string;
  status: string;
  is_demo: boolean;
  specs?: Record<string, unknown>;
};

export default function AssetsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["assets"],
    queryFn: () => api<Asset[]>("/api/v1/assets"),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold">Activos</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">Inventario de equipos — etiquetas DEMO visibles.</p>
      {isLoading && <p className="mt-4 text-sm">Cargando…</p>}
      {error && <p className="mt-4 text-sm text-red-400">{String(error)}</p>}
      <div className="mt-4 overflow-auto rounded-xl border border-[var(--border)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2">Tag</th>
              <th className="px-3 py-2">Nombre</th>
              <th className="px-3 py-2">Tipo</th>
              <th className="px-3 py-2">Estado</th>
              <th className="px-3 py-2">Demo</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((a) => (
              <tr key={a.id} className="border-t border-[var(--border)]">
                <td className="px-3 py-2 font-mono text-jarvis-400">{a.tag}</td>
                <td className="px-3 py-2">{a.name}</td>
                <td className="px-3 py-2">{a.asset_type}</td>
                <td className="px-3 py-2">{a.status}</td>
                <td className="px-3 py-2">{a.is_demo ? "DEMO" : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
