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

// --- Runs (M1: live multi-agent handoff) ---

export type StepType = "plan" | "handoff" | "tool" | "llm" | "result";
export type StepStatus = "started" | "completed" | "failed";

export interface StepEvent {
  run_id: string;
  seq: number;
  agent: string;
  type: StepType;
  status: StepStatus;
  title: string;
  detail: Record<string, unknown>;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  latency_ms: number;
  ts: number;
}

export interface RunSnapshot {
  run_id: string;
  goal: string;
  status: "queued" | "running" | "success" | "failed";
  result: string;
  error: string | null;
  steps: number;
}

export function startRun(goal: string, mock = true): Promise<{ run_id: string; status: string }> {
  return post("/v1/runs", { goal, mock });
}

export function runEventsUrl(runId: string): string {
  return `${API_URL}/v1/runs/${runId}/events`;
}
