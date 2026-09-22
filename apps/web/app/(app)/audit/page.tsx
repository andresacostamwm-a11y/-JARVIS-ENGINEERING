"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

type Ev = {
  id: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  created_at?: string;
  detail?: Record<string, unknown>;
};

export default function AuditPage() {
  const { data, error } = useQuery({
    queryKey: ["audit"],
    queryFn: () => api<Ev[]>("/api/v1/audit/events"),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold">Auditoría</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Eventos de login, CRUD y cálculos. Rol mínimo: AUDITOR (demo engineer puede no alcanzar —
        usa admin@jarvis.local / admin1234 si 403).
      </p>
      {error && <p className="mt-4 text-sm text-amber-400">Nota: {String(error)}</p>}
      <div className="mt-4 overflow-auto rounded-xl border border-[var(--border)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2">Cuando</th>
              <th className="px-3 py-2">Acción</th>
              <th className="px-3 py-2">Recurso</th>
              <th className="px-3 py-2">ID</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((e) => (
              <tr key={e.id} className="border-t border-[var(--border)]">
                <td className="px-3 py-2 text-xs">{e.created_at}</td>
                <td className="px-3 py-2">{e.action}</td>
                <td className="px-3 py-2">{e.resource_type}</td>
                <td className="px-3 py-2 font-mono text-xs">{e.resource_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
