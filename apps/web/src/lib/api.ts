/** Typed API client. Replaced by OpenAPI-generated types
 * (packages/shared-types) once the surface stabilizes in Phase 1. */

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface CompletionResult {
  text: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  stop_reason: string | null;
}

export interface PlaygroundRequest {
  prompt: string;
  system?: string;
  role?: "orchestrator" | "worker" | "judge";
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export function createPlaygroundMessage(
  body: PlaygroundRequest,
): Promise<CompletionResult> {
  return post<CompletionResult>("/v1/playground/messages", body);
}
