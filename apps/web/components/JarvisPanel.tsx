"use client";
import { useState } from "react";
import { api } from "@/lib/api";

type ChatMsg = { role: "user" | "assistant"; content: string };

export function JarvisPanel() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      role: "assistant",
      content:
        "Hola, soy JARVIS. Puedo buscar activos DEMO, ejecutar cálculos verificados y consultar RAG. Sin XAI_API_KEY el chat degrada con resumen de tools.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [sources, setSources] = useState<unknown[]>([]);
  const [tab, setTab] = useState<"chat" | "sources" | "calcs">("chat");
  const [lastCalcs, setLastCalcs] = useState<unknown[]>([]);

  const send = async () => {
    if (!input.trim() || busy) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setBusy(true);
    try {
      const res = await api<{
        content: string;
        tool_results: unknown[];
        degraded?: boolean;
      }>("/api/v1/chat", {
        method: "POST",
        body: JSON.stringify({
          messages: [...messages, { role: "user", content: userMsg }].map((x) => ({
            role: x.role,
            content: x.content,
          })),
          use_tools: true,
        }),
      });
      setMessages((m) => [...m, { role: "assistant", content: res.content }]);
      if (res.tool_results?.length) {
        setLastCalcs(res.tool_results);
        setSources(res.tool_results);
      }
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: `Error: ${e instanceof Error ? e.message : "falló el chat"}`,
        },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <aside className="jarvis-panel flex w-96 shrink-0 flex-col border-l">
      <div className="flex border-b border-[var(--border)] text-sm">
        {(
          [
            ["chat", "Chat"],
            ["sources", "Fuentes"],
            ["calcs", "Cálculos"],
          ] as const
        ).map(([k, label]) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            className={`flex-1 px-3 py-3 ${
              tab === k ? "border-b-2 border-jarvis-400 text-jarvis-400" : "text-[var(--muted)]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-auto p-3 text-sm">
        {tab === "chat" && (
          <div className="space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`rounded-lg px-3 py-2 ${
                  m.role === "user" ? "bg-jarvis-600/20 ml-6" : "bg-white/5 mr-2"
                }`}
              >
                <div className="mb-1 text-[10px] uppercase text-[var(--muted)]">{m.role}</div>
                <div className="whitespace-pre-wrap">{m.content}</div>
              </div>
            ))}
          </div>
        )}
        {tab === "sources" && (
          <pre className="whitespace-pre-wrap text-xs text-[var(--muted)]">
            {sources.length ? JSON.stringify(sources, null, 2) : "Sin fuentes aún."}
          </pre>
        )}
        {tab === "calcs" && (
          <pre className="whitespace-pre-wrap text-xs text-[var(--muted)]">
            {lastCalcs.length ? JSON.stringify(lastCalcs, null, 2) : "Sin cálculos de tools aún."}
          </pre>
        )}
      </div>
      {tab === "chat" && (
        <div className="border-t border-[var(--border)] p-3">
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-lg border border-[var(--border)] bg-transparent px-3 py-2 text-sm"
              placeholder="Pregunta a JARVIS…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button
              onClick={send}
              disabled={busy}
              className="rounded-lg bg-jarvis-600 px-3 py-2 text-sm text-white disabled:opacity-50"
            >
              Enviar
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}
