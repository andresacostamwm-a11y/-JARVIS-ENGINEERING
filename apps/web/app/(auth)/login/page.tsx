"use client";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuthStore } from "@/stores/auth";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(4),
});

type Form = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { email: "demo@jarvis.local", password: "demo1234" },
  });

  const onSubmit = async (data: Form) => {
    setError(null);
    try {
      await login(data.email, data.password);
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de autenticación");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="jarvis-panel w-full max-w-md rounded-2xl border p-8 shadow-xl"
      >
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight">JARVIS Engineering</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            MVP profesional — inicia sesión (datos DEMO precargados)
          </p>
        </div>
        <label className="mb-2 block text-sm">Correo</label>
        <input
          className="mb-4 w-full rounded-lg border border-[var(--border)] bg-transparent px-3 py-2"
          {...register("email")}
        />
        <label className="mb-2 block text-sm">Contraseña</label>
        <input
          type="password"
          className="mb-4 w-full rounded-lg border border-[var(--border)] bg-transparent px-3 py-2"
          {...register("password")}
        />
        {error && <p className="mb-3 text-sm text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-jarvis-600 px-4 py-2.5 font-medium text-white hover:bg-jarvis-500 disabled:opacity-60"
        >
          {isSubmitting ? "Entrando…" : "Entrar"}
        </button>
        <p className="mt-4 text-xs text-[var(--muted)]">
          Demo: <code>demo@jarvis.local</code> / <code>demo1234</code>
        </p>
      </form>
    </div>
  );
}
