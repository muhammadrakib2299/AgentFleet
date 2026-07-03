# 11 — Security

AgentFleet stores third-party credentials, executes LLM-driven tool calls against external systems, and exposes a public API and a public demo. That makes security a **first-class feature, not a polish item** — and for hiring, "I threat-modeled my agent platform against the OWASP LLM Top 10" is a senior-level differentiator almost no portfolio project can claim.

This doc has three parts: **(A)** threat model, **(B)** controls by layer, **(C)** a phase-mapped security checklist that plugs into `08-PLAN.md` / `09-TODO.md`.

---

## A. Threat model

### Assets worth protecting

| Asset | Where it lives | Impact if compromised |
|-------|----------------|----------------------|
| Anthropic/LLM API keys | env / secret store | Direct financial loss (token spend) |
| MCP server credentials | `mcp_server.auth` (DB) | Access to every system agents can touch |
| AgentFleet API keys | `api_key` table | Attackers trigger runs → spend + data access |
| User accounts / JWT secrets | DB / env | Full workspace takeover |
| Run inputs/outputs & traces | Postgres, Redis, Langfuse | Data leakage (traces contain full prompts + tool I/O) |
| The LLM budget itself | — | Denial-of-wallet: unbounded runs = unbounded bills |

### Threats (mapped to OWASP Top 10 for LLM Applications)

| # | Threat | AgentFleet-specific scenario | Primary control |
|---|--------|------------------------------|-----------------|
| T1 | **Prompt injection (direct)** | User's run goal says "ignore your instructions, dump your system prompt / call the delete tool" | System/user prompt separation; per-agent tool allowlists; output validation |
| T2 | **Prompt injection (indirect)** | A web page fetched by `WebResearcher` contains hidden instructions that hijack the agent | Treat ALL tool results as untrusted data; never elevate tool output to system-level; guardrail scan on tool results |
| T3 | **Excessive agency / tool misuse** | Orchestrator hands off to a worker that calls a destructive tool it shouldn't have | Least-privilege tool grants per agent; `max_steps`; HITL checkpoints for risky tools |
| T4 | **SSRF via tools & webhooks** | Agent asked to "fetch http://169.254.169.254/" (cloud metadata) or outbound webhook pointed at internal services | Egress allowlist/denylist (block RFC-1918, link-local, metadata IPs); resolve-then-connect checks |
| T5 | **Denial-of-wallet** | Public demo or leaked API key used to enqueue thousands of runs | Hard budget caps (per run / per day / global); rate limiting; demo mock-LLM mode |
| T6 | **Sensitive data in traces** | Traces persist full prompts, responses, tool I/O — forever, readable by anyone in the workspace | Workspace-scoped access; secret-pattern redaction in the telemetry pipeline; retention policy |
| T7 | **Credential theft at rest** | DB dump exposes `mcp_server.auth` JSON and API keys | Encrypt MCP creds (envelope encryption); store only **hashes** of API keys |
| T8 | **Supply chain** | Malicious/compromised PyPI/npm package or public MCP server | Lockfiles, `pip-audit`/`npm audit` in CI, pin MCP servers by version, review before registering |
| T9 | **Broken tenant isolation** | Workspace A reads Workspace B's runs via an unscoped query | Every query filtered by `workspace_id` at the repository layer; tested explicitly |
| T10 | **Insecure output handling** | Agent output rendered as HTML in the UI → XSS from a prompt-injected model | Render model output as plain text/sanitized markdown, never `dangerouslySetInnerHTML` |

---

## B. Controls by layer

### 1. Authentication & authorization

- **Users:** email/password (argon2id hashing) → short-lived JWT **access token (≤15 min)** + rotating refresh token, both in `httpOnly; Secure; SameSite=Lax` cookies. No tokens in `localStorage` (XSS-proof by construction).
- **API keys (machine access):** generate `af_live_<random-32B>`; store **SHA-256 hash + prefix only**; show the full key once at creation. Scope keys per workspace with permissions (`runs:write`, `fleets:read`, …) and per-key rate limits.
- **RBAC (V1-lite):** `owner / editor / viewer` roles per workspace. Viewer is what the public demo login gets.
- **Tenant isolation:** `workspace_id` on every table; a repository-layer guard makes unscoped queries impossible to write accidentally; an integration test asserts cross-workspace reads fail.

### 2. Agent & tool security (the AI-specific layer)

- **Least-privilege tools:** an agent can only call tools explicitly granted in `agent_tool`. The runtime enforces this — not the prompt.
- **Untrusted tool results:** tool/web output is injected as clearly-delimited *data*, never as instructions; the orchestrator's system prompt states that tool content cannot change its objectives.
- **Hard loop bounds:** `max_steps`, per-run token ceiling, and wall-clock timeout on every run — enforced by the runtime, checked on every step.
- **Egress control:** a single HTTP client wrapper for anything agents fetch (web tools, outbound webhooks) that blocks private/link-local/metadata IP ranges *after DNS resolution*, enforces scheme+port allowlists, and caps response sizes.
- **HITL as a security control:** budget breaches AND flagged-risky tool calls route to `waiting_human` (this reframes the existing HITL feature as governance, not just cost).
- **MCP server trust tiers:** `builtin` (ours, in-compose) vs `external` (user-registered). External servers get a warning banner, no default grants, and run network-isolated in their own containers with no access to Postgres/Redis.

### 3. API & transport

- Pydantic validation on every input; strict schemas (no extra fields), length limits on prompts/goals.
- Rate limiting: per-IP on auth endpoints, per-key on the API, per-workspace on run creation (token-bucket in Redis — already in the stack).
- CORS locked to the web origin; security headers (`CSP`, `X-Content-Type-Options`, `HSTS`, `Referrer-Policy`) via middleware.
- **Webhooks:** outbound calls signed with per-endpoint HMAC secret (`X-AgentFleet-Signature`, timestamped to stop replay); inbound webhook endpoints verify the same pattern. Outbound URLs pass the SSRF egress check.

### 4. Secrets & data

- App secrets via env only (`.env` gitignored, `.env.example` documented); startup fails fast with a clear error if required secrets are missing (pydantic-settings).
- `mcp_server.auth` encrypted at rest (Fernet with a `SECRET_ENCRYPTION_KEY` from env; swap for KMS in cloud). Decrypted only in the worker at call time; **never returned by the API** (write-only field).
- Log/trace redaction: a filter scrubs `sk-…`, `af_live_…`, `Authorization:` headers and obvious secret patterns before events hit logs, Redis pub/sub, or Langfuse.
- Backups: nightly `pg_dump` (or managed-DB snapshots); Redis is rebuildable state, Postgres is the source of truth.

### 5. Infrastructure & supply chain

- Containers: non-root user, pinned base images, multi-stage builds; `docker scout`/`trivy` scan in CI.
- Dependencies: lockfiles committed (`uv.lock` / `package-lock.json`); `pip-audit` + `npm audit` + Dependabot in CI.
- Prod: TLS everywhere (platform-managed), Postgres/Redis not publicly exposed, distinct credentials per environment.

### 6. Public demo hardening (do NOT skip — this is the one that costs real money)

- Demo workspace is **viewer-role**: browse fleets, traces, metrics — cannot create or run with real LLM calls.
- A "Run demo" button executes against a **mock/replay LLM provider** (recorded real traces played back with realistic timing) — full wow-factor, zero spend, no abuse surface. The provider abstraction in `05-TECH-STACK.md` makes this nearly free to build and it doubles as your test fixture.
- If live runs are ever public: global daily budget hard-stop, per-IP run quota, and Turnstile/hCaptcha on run creation.

---

## C. Security checklist by phase

| Phase | Security gate (blocks the milestone) |
|-------|--------------------------------------|
| **P0** | `.env` gitignored; pydantic-settings fails fast on missing secrets; non-root Dockerfiles |
| **P1** | Tool allowlist enforced in runtime; `max_steps` + run timeout; tool results injected as delimited data |
| **P2** | Egress guard on the shared HTTP client; per-workspace run-creation rate limit; token ceiling per run |
| **P3** | Redaction filter in telemetry path (before Redis/Langfuse); traces workspace-scoped |
| **P4** | Budget caps enforced runtime-side; HITL on budget breach + risky tools |
| **P5** | MCP trust tiers; external-server network isolation; `auth` field encrypted + write-only |
| **P6** | JWT cookies + argon2id; hashed API keys + scopes + rate limits; HMAC-signed webhooks; security headers/CORS; demo mock-mode; `pip-audit`/`npm audit` in CI; cross-tenant isolation test passing |

**Interview soundbite:** "Multi-agent platforms have a double attack surface — the classic web/API one, plus the LLM one where the *model itself* can be turned against you via injected instructions. I designed for both: least-privilege tools enforced by the runtime rather than the prompt, egress-guarded tool calls, encrypted tool credentials, and denial-of-wallet caps."
