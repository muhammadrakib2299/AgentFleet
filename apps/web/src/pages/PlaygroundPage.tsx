import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Loader2, Send } from "lucide-react";
import { createPlaygroundMessage } from "../lib/api";

/** M0 milestone screen: one button, one real Claude call, response + cost. */
export function PlaygroundPage() {
  const [prompt, setPrompt] = useState(
    "In two sentences: why do multi-agent systems beat a single agent on complex research tasks?",
  );

  const mutation = useMutation({ mutationFn: createPlaygroundMessage });

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Playground</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Single-agent test call — proves API → Claude → UI end to end.
        </p>
      </header>

      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (prompt.trim()) mutation.mutate({ prompt, role: "orchestrator" });
        }}
      >
        <label htmlFor="prompt" className="block text-sm font-medium">
          Prompt
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          maxLength={8000}
          className="w-full rounded-lg border border-border bg-surface-raised p-3 font-mono text-sm outline-none focus:border-accent"
        />
        <button
          type="submit"
          disabled={mutation.isPending || !prompt.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending ? (
            <Loader2 className="size-4 animate-spin" aria-hidden />
          ) : (
            <Send className="size-4" aria-hidden />
          )}
          {mutation.isPending ? "Running…" : "Run"}
        </button>
      </form>

      <div aria-live="polite">
        {mutation.isError && (
          <div
            role="alert"
            className="rounded-lg border border-failed/40 bg-failed/10 p-4 text-sm text-failed"
          >
            {(mutation.error as Error).message}
          </div>
        )}

        {mutation.isSuccess && (
          <div className="space-y-3">
            <div className="rounded-lg border border-border bg-surface-raised p-4 text-sm leading-relaxed whitespace-pre-wrap">
              {mutation.data.text}
            </div>
            <dl className="flex flex-wrap gap-x-6 gap-y-1 font-mono text-xs text-ink-muted">
              <div>
                <dt className="inline">model </dt>
                <dd className="inline text-ink">{mutation.data.model}</dd>
              </div>
              <div>
                <dt className="inline">tokens </dt>
                <dd className="inline text-ink">
                  {mutation.data.input_tokens} in / {mutation.data.output_tokens} out
                </dd>
              </div>
              <div>
                <dt className="inline">latency </dt>
                <dd className="inline text-ink">{mutation.data.latency_ms} ms</dd>
              </div>
              <div>
                <dt className="inline">cost </dt>
                <dd className="inline text-success">
                  ${mutation.data.cost_usd.toFixed(4)}
                </dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </div>
  );
}
