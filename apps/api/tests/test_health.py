async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agentfleet-api"}


async def test_playground_rejects_empty_prompt(client):
    response = await client.post("/v1/playground/messages", json={"prompt": ""})
    assert response.status_code == 422


async def test_playground_rejects_oversized_prompt(client):
    response = await client.post("/v1/playground/messages", json={"prompt": "x" * 9000})
    assert response.status_code == 422
