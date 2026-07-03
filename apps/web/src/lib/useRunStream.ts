import { useEffect, useRef, useState } from "react";
import { runEventsUrl, type RunSnapshot, type StepEvent } from "./api";

interface RunStream {
  events: StepEvent[];
  snapshot: RunSnapshot | null;
  streaming: boolean;
}

/** Subscribe to a run's SSE stream and collect steps as they arrive.
 * Dedupes on `seq` because streamed delivery is at-least-once. */
export function useRunStream(runId: string | null): RunStream {
  const [events, setEvents] = useState<StepEvent[]>([]);
  const [snapshot, setSnapshot] = useState<RunSnapshot | null>(null);
  const [streaming, setStreaming] = useState(false);
  const seen = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (!runId) return;
    setEvents([]);
    setSnapshot(null);
    seen.current = new Set();
    setStreaming(true);

    const source = new EventSource(runEventsUrl(runId));

    source.addEventListener("step", (e) => {
      const step = JSON.parse((e as MessageEvent).data) as StepEvent;
      if (seen.current.has(step.seq)) return;
      seen.current.add(step.seq);
      setEvents((prev) => [...prev, step]);
    });

    source.addEventListener("done", (e) => {
      setSnapshot(JSON.parse((e as MessageEvent).data) as RunSnapshot);
      setStreaming(false);
      source.close();
    });

    source.onerror = () => {
      setStreaming(false);
      source.close();
    };

    return () => source.close();
  }, [runId]);

  return { events, snapshot, streaming };
}
