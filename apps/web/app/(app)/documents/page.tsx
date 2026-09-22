"use client";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, API_URL, getToken } from "@/lib/api";
import { useState } from "react";

type Doc = {
  id: string;
  title: string;
  filename: string;
  status: string;
  size_bytes: number;
  is_demo: boolean;
};

export default function DocumentsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["documents"],
    queryFn: () => api<Doc[]>("/api/v1/documents"),
  });
  const [uploading, setUploading] = useState(false);
  const [ragQ, setRagQ] = useState("chiller COP");
  const [ragHits, setRagHits] = useState<unknown>(null);

  const onUpload = async (file: File) => {
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("title", file.name);
      const res = await fetch(`${API_URL}/api/v1/documents/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
      await qc.invalidateQueries({ queryKey: ["documents"] });
    } catch (e) {
      alert(String(e));
    } finally {
      setUploading(false);
    }
  };

  const searchRag = async () => {
    const res = await api<{ hits: unknown[] }>("/api/v1/rag/search", {
      method: "POST",
      body: JSON.stringify({ query: ragQ, limit: 5 }),
    });
    setRagHits(res.hits);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold">Documentos & RAG</h1>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Sube texto; worker Celery (o ingest inline) genera chunks. PDF OCR — COMING SOON.
      </p>
      <div className="mt-4">
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-jarvis-600 px-4 py-2 text-sm text-white">
          {uploading ? "Subiendo…" : "Subir documento"}
          <input
            type="file"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
          />
        </label>
      </div>
      <ul className="mt-6 space-y-2">
        {(data || []).map((d) => (
          <li key={d.id} className="jarvis-panel flex items-center justify-between rounded-lg border px-4 py-3 text-sm">
            <div>
              <div className="font-medium">
                {d.title} {d.is_demo && <span className="text-amber-400">DEMO</span>}
              </div>
              <div className="text-[var(--muted)]">
                {d.filename} · {d.status} · {d.size_bytes} B
              </div>
            </div>
          </li>
        ))}
      </ul>
      <div className="mt-8">
        <h2 className="font-semibold">Buscar RAG</h2>
        <div className="mt-2 flex gap-2">
          <input
            className="flex-1 rounded-lg border border-[var(--border)] bg-transparent px-3 py-2 text-sm"
            value={ragQ}
            onChange={(e) => setRagQ(e.target.value)}
          />
          <button onClick={searchRag} className="rounded-lg bg-jarvis-600 px-3 py-2 text-sm text-white">
            Buscar
          </button>
        </div>
        {ragHits && (
          <pre className="mt-3 max-h-64 overflow-auto rounded-lg bg-white/5 p-3 text-xs">
            {JSON.stringify(ragHits, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
