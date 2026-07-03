"""Agent tools.

Phase 1 ships a single deterministic mock tool so the vertical slice runs
offline with no MCP server, network, or API keys. The signature mirrors what
a real MCP tool call returns, so swapping in a live MCP web-search server
(Phase 2) is a drop-in replacement behind the same `ToolResult` shape.
"""

from agentfleet_worker.tools.mock_search import (
    ToolResult,
    ToolResultItem,
    mock_web_search,
)

__all__ = ["ToolResult", "ToolResultItem", "mock_web_search"]
