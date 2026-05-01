/** Server-only: base URL for the FastAPI bills API. */
export function backendUrl(): string {
  const raw = process.env.BILLS_API_URL ?? "http://127.0.0.1:8000";
  return raw.replace(/\/$/, "");
}
