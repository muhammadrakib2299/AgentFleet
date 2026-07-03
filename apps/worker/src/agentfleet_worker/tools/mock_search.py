"""Deterministic mock web-search tool.

Real MCP web search needs a server, network egress, and (usually) an API key —
none of which belong in a unit test or an offline demo. This returns stable,
plausible results derived from the query so the whole handoff slice is
reproducible. `TOOL_SCHEMA` is the JSON-Schema an agent's tool allowlist keys
on; a live MCP server later advertises the same shape.
"""

import hashlib

from pydantic import BaseModel

TOOL_NAME = "web_search"

TOOL_SCHEMA = {
    "name": TOOL_NAME,
    "description": "Search the web for recent, relevant results on a query.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query."},
        },
        "required": ["query"],
    },
}


class ToolResultItem(BaseModel):
    title: str
    url: str
    snippet: str


class ToolResult(BaseModel):
    tool: str
    query: str
    results: list[ToolResultItem]

    def as_context(self) -> str:
        """Flatten results into a prompt-ready context block."""
        lines = [f"[{i + 1}] {r.title} ({r.url})\n{r.snippet}" for i, r in enumerate(self.results)]
        return "\n\n".join(lines)


def _slug(query: str) -> str:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:8]
    return digest


async def mock_web_search(query: str, *, limit: int = 3) -> ToolResult:
    """Return `limit` deterministic results for `query`.

    Deterministic on the query string so runs are reproducible and tests can
    assert exact output without a live network.
    """
    slug = _slug(query)
    topic = query.strip() or "the topic"
    items = [
        ToolResultItem(
            title=f"{topic.title()} — 2026 overview",
            url=f"https://example.com/{slug}/overview",
            snippet=(
                f"A concise 2026 briefing on {topic}: current state, key players, "
                "and the trends shaping the next 12 months."
            ),
        ),
        ToolResultItem(
            title=f"Market data: {topic.title()}",
            url=f"https://example.com/{slug}/market",
            snippet=(
                f"Figures and growth rates relevant to {topic}, aggregated from "
                "recent industry reports and analyst notes."
            ),
        ),
        ToolResultItem(
            title=f"Expert analysis on {topic.title()}",
            url=f"https://example.com/{slug}/analysis",
            snippet=(
                f"Commentary from practitioners on where {topic} is heading, with "
                "concrete examples and cited caveats."
            ),
        ),
    ]
    return ToolResult(tool=TOOL_NAME, query=query, results=items[:limit])
