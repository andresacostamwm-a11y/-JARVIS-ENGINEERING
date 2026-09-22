export function apiUrl(path: string, base?: string): string {
  const b = base || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  return `${b.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
}
