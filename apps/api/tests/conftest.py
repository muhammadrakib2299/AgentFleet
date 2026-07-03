import os

# Test settings: fail-fast Settings still needs a key present; tests never
# make real LLM calls, so a dummy value is correct here.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")

import pytest
from httpx import ASGITransport, AsyncClient

from agentfleet_api.main import create_app


@pytest.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
