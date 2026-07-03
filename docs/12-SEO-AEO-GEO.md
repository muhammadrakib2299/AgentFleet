# 12 — SEO / AEO / GEO (Discoverability)

**Reality check first:** the AgentFleet *app* is a dashboard behind a login — search engines will never index it, and it needs zero SEO. Keeping the app a fast Vite SPA is correct. Discoverability lives on three **public surfaces**, each with its own playbook:

1. **GitHub repository** — where recruiters and developers actually find portfolio projects.
2. **Landing + docs site** (`agentfleet.dev`) — a small static site; the SEO/AEO/GEO surface.
3. **Build-log content** — 3–5 posts that earn long-tail search and AI-engine citations.

The goal is not "rank a startup" — it's that when someone searches or asks an AI about *you* or about "multi-agent orchestration example project," AgentFleet shows up looking like a product.

---

## 1. GitHub repo (highest ROI, near-zero effort)

- **Repo description** = keyword-rich one-liner: *"Multi-agent orchestration platform — build, run, trace, and evaluate fleets of AI agents. LangGraph · Claude · MCP · FastAPI · React."*
- **Topics:** `multi-agent-systems`, `ai-agents`, `langgraph`, `mcp`, `agent-orchestration`, `llm-observability`, `fastapi`, `anthropic-claude`.
- **Social preview image** (Settings → Social preview): the dashboard screenshot with the logo — this is what renders when the repo is shared on LinkedIn/X/Slack.
- README top: one GIF of the live trace viewer within the first screenful. GitHub is indexed heavily; the README *is* a landing page.
- Pin the repo on your profile; link it from LinkedIn projects section.

## 2. Landing + docs site — add a tiny `apps/site` in **Astro**

Why Astro and not the React SPA or Next.js: static output (perfect Core Web Vitals with zero effort), islands only where needed, markdown/MDX docs built-in, and it adds "chose the right tool per surface" to the architecture story. It deploys free on Cloudflare Pages/Netlify.

**Pages:** Home (hero + trace-viewer GIF + feature grid), `/docs/*` (quickstart, architecture, API), `/blog/*` (build log), `/demo` (link + video).

### Technical SEO checklist

- Unique `<title>` / meta description per page; canonical URLs; `sitemap.xml` + `robots.txt` (Astro integrations do both).
- Open Graph + Twitter card tags with a real 1200×630 OG image per key page.
- **JSON-LD structured data:** `SoftwareApplication` (home), `FAQPage` (home FAQ section), `TechArticle` (blog posts), `Person` (about — links the project to *you*, which is the actual conversion goal).
- Core Web Vitals: static Astro + self-hosted fonts + compressed images ≈ green by default; verify with Lighthouse in CI once.
- Analytics: Plausible or GA4 + register on **Google Search Console** and Bing Webmaster Tools day one (indexing takes weeks — don't leave it to launch day). You have Ahrefs — set up a project for `agentfleet.dev` to track keywords/backlinks over time.

### Keyword targets (low competition, high intent)

| Intent | Target queries |
|--------|----------------|
| Category | "multi-agent orchestration platform", "AI agent fleet management" |
| How-to (blog) | "LangGraph orchestrator worker example", "agent to agent handoff LangGraph", "Celery async LangGraph", "LLM cost tracking per agent", "MCP tools multi agent" |
| Comparison (blog) | "LangGraph vs CrewAI production", "Langfuse vs LangSmith self-hosted" |

Each blog post = one query, answered in the first paragraph, with real code and a trace screenshot. 3–5 posts beat 20 thin ones.

## 3. AEO (Answer Engine Optimization)

Optimize for being *the extracted answer* (featured snippets, AI Overviews):

- Question-shaped `<h2>`s ("What is agent-to-agent handoff?", "How do you trace a multi-agent run?") followed immediately by a **2–3 sentence direct answer**, then depth.
- A real FAQ section on the home page (marked up as `FAQPage`).
- Definitional first sentence everywhere: "AgentFleet is a multi-agent orchestration platform that…" — same phrasing on GitHub, site, and LinkedIn. Consistent entity naming is how engines learn what a thing *is*.
- Tables and numbered steps (like the docs already use) — the formats engines extract.

## 4. GEO (Generative Engine Optimization — ChatGPT/Claude/Perplexity citations)

- **`llms.txt`** at the site root: a concise markdown map of the project (what it is, architecture summary, links to docs pages). Add `llms-full.txt` with the full docs concatenated.
- **robots.txt allows AI crawlers** (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`) — you *want* to be in training/citation data; this is the opposite of a normal company's dilemma.
- Citable, specific claims with numbers ("AgentFleet traces every LLM/tool/handoff step with per-step cost; a Market Brief run costs ~$0.42") — generative engines cite concrete, quantified statements far more than marketing copy.
- Publish the architecture doc as a public docs page — "how to build a multi-agent platform" is exactly what developers ask AI assistants, and cited docs = your name in the answer.
- Cross-surface consistency: same project name, same one-liner, same author name on GitHub / site / LinkedIn / dev.to cross-posts (canonical → your site).

## 5. What NOT to do

- No keyword stuffing, no AI-generated filler posts, no buying backlinks — one recruiter noticing kills the credibility the whole project exists to build.
- Don't build the site before M1 exists. **Sequence:** GitHub polish (P0, 30 min) → Search Console + domain (P3) → landing + docs + llms.txt (P6) → blog posts (post-launch, one per lesson in `10-LESSONS.md`).

## Measurement

| Metric | Tool | Target (90 days post-launch) |
|--------|------|------------------------------|
| Repo traffic + stars | GitHub Insights | Referrals from site/posts visible |
| Indexed pages, impressions | Search Console | All pages indexed; impressions trending up |
| Keyword positions | Ahrefs | Top-10 for 2–3 long-tail how-to queries |
| AI citations | Ask ChatGPT/Perplexity/Claude "multi-agent orchestration example project" monthly | AgentFleet appears with correct description |
