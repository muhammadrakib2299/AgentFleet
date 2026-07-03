# packages/prompts

Versioned system prompts and eval rubrics, treated as code.

- One markdown file per prompt, named `<agent-role>.<version>.md`
  (e.g. `orchestrator.v1.md`, `judge-market-brief.v1.md`).
- Prompts are loaded by the worker runtime at fleet-compile time (Phase 1+).
- Changing a prompt = new version file + eval regression run (Phase 4).
