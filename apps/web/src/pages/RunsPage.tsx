import { useState } from "react";
import {
  ArrowLeftRight,
  CheckCircle2,
  Compass,
  Loader2,
  PenLine,
  Play,
  Wrench,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { startRun, type StepEvent, type StepType } from "../lib/api";
import { useRunStream } from "../lib/useRunStream";

const STEP_ICON: Record<StepType, LucideIcon> = {
  plan: Compass,
  handoff: ArrowLeftRight,
  tool: Wrench,
  llm: PenLine,
  result: CheckCircle2,
};

/** M1 milestone screen: submit a goal, watch the orchestrator hand off to a
 * worker (tool + LLM) and synthesize — every step streamed live over SSE. */
export function RunsPage() {
  const [goal, setGoal] = useState(
    "Give me a market brief on multi-agent AI orchestration platforms in 2026.",
  );
  const [runId, setRunId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const { events, snapshot, streaming } = useRunStream(runId);
  const totalCost = events.reduce((sum, e) => sum + e.cost_usd, 0);

  async function run() {
    setStarting(true);
    try {
      const { run_id } = await startRun(goal, true);
      setRunId(run_id);
    } finally {
      setStarting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Runs</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Submit a goal and watch the fleet work — orchestrator plans, hands off to
          the researcher, then synthesizes. Steps stream live over SSE.
        </p>
      </header>

      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (goal.trim()) run();
        }}
      >
        <label htmlFor="goal" className="block text-sm font-medium">
          Goal
        </label>
        <textarea
          id="goal"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          rows={3}
          maxLength={2000}
          className="w-full rounded-lg border border-border bg-surface-raised p-3 text-sm outline-none focus:border-accent"
        />
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={starting || streaming || !goal.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {starting || streaming ? (
              <Loader2 className="size-4 animate-spin" aria-hidden />
            ) : (
              <Play className="size-4" aria-hidden />
            )}
            {streaming ? "Running…" : "Run fleet"}
          </button>
          <span className="rounded bg-surface-hover px-2 py-1 text-[11px] uppercase tracking-wide text-ink-muted">
            mock provider · zero spend
          </span>
        </div>
      </form>

      {runId && (
        <section aria-live="polite" className="space-y-4">
          <div className="flex items-center justify-between text-xs font-mono text-ink-muted">
            <span>run {runId}</span>
            <span>
              {events.length} steps · ${totalCost.toFixed(6)}
            </span>
          </div>

          <ol className="space-y-2">
            {events.map((step) => (
              <StepRow key={step.seq} step={step} />
            ))}
            {streaming && (
              <li className="flex items-center gap-2 px-3 py-2 text-sm text-ink-muted">
                <Loader2 className="size-4 animate-spin" aria-hidden />
                waiting for next step…
              </li>
            )}
          </ol>

          {snapshot?.status === "success" && (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold">Final brief</h2>
              <div className="rounded-lg border border-border bg-surface-raised p-4 text-sm leading-relaxed whitespace-pre-wrap">
                {snapshot.result}
              </div>
            </div>
          )}
          {snapshot?.status === "failed" && (
            <div
              role="alert"
              className="rounded-lg border border-failed/40 bg-failed/10 p-4 text-sm text-failed"
            >
              {snapshot.error ?? "Run failed."}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function StepRow({ step }: { step: StepEvent }) {
  const Icon = STEP_ICON[step.type];
  const isOrchestrator = step.agent === "orchestrator";
  return (
    <li className="flex gap-3 rounded-lg border border-border bg-surface-raised p-3">
      <div
        className={`mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full ${
          isOrchestrator ? "bg-accent/15 text-accent" : "bg-success/15 text-success"
        }`}
      >
        <Icon className="size-4" aria-hidden />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-sm font-medium">{step.title}</span>
          {step.cost_usd > 0 && (
            <span className="shrink-0 font-mono text-[11px] text-success">
              ${step.cost_usd.toFixed(6)}
            </span>
          )}
        </div>
        <div className="text-[11px] uppercase tracking-wide text-ink-muted">
          {step.agent}
        </div>
        <StepDetail step={step} />
      </div>
    </li>
  );
}

function StepDetail({ step }: { step: StepEvent }) {
  const d = step.detail;
  let text = "";
  if (step.type === "handoff") {
    text = `→ ${d.to_agent}: ${d.task}`;
  } else if (step.type === "tool") {
    const results = (d.results as unknown[]) ?? [];
    text = `${d.tool}("${d.query}") → ${results.length} results`;
  } else if (step.type === "plan") {
    text = String(d.subtask ?? "");
  } else if (step.type === "llm") {
    text = String(d.findings ?? "");
  } else if (step.type === "result") {
    text = String(d.result ?? "");
  }
  if (!text) return null;
  return <p className="mt-1 text-sm text-ink-muted">{text}</p>;
}
