import importlib
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


def load_server():
    return importlib.import_module("five_mcp.server")


def test_get_api_key_requires_environment(monkeypatch):
    server = load_server()
    monkeypatch.delenv("FIVE_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="FIVE_API_KEY is not set"):
        server._get_api_key()


@pytest.mark.asyncio
async def test_generate_omits_unset_optional_fields(monkeypatch):
    server = load_server()
    monkeypatch.setenv("FIVE_API_KEY", "five_sk_test")

    response = SimpleNamespace(
        status_code=200,
        json=lambda: {"status": "ok", "remaining": 1, "constraint": {}},
        raise_for_status=lambda: None,
    )

    async_client = AsyncMock()
    async_client.__aenter__.return_value.post.return_value = response

    with patch.object(server.httpx, "AsyncClient", return_value=async_client):
        result = await server.generate(
            character_name="Luna",
            q1="A",
            q2="B",
            q3="C",
            q4="D",
        )

    assert result["status"] == "ok"
    post_call = async_client.__aenter__.return_value.post
    payload = post_call.call_args.kwargs["json"]
    assert payload == {
        "character_name": "Luna",
        "q1": "A",
        "q2": "B",
        "q3": "C",
        "q4": "D",
    }
    assert post_call.call_args.kwargs["headers"]["Authorization"] == "Bearer five_sk_test"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (401, "Authentication failed"),
        (402, "Insufficient credits"),
        (429, "Rate limited"),
    ],
)
async def test_generate_maps_expected_api_errors(monkeypatch, status_code, message):
    server = load_server()
    monkeypatch.setenv("FIVE_API_KEY", "five_sk_test")

    response = SimpleNamespace(
        status_code=status_code,
        json=lambda: {},
        raise_for_status=lambda: None,
    )

    async_client = AsyncMock()
    async_client.__aenter__.return_value.post.return_value = response

    with patch.object(server.httpx, "AsyncClient", return_value=async_client):
        with pytest.raises(RuntimeError, match=message):
            await server.generate(
                character_name="Luna",
                q1="A",
                q2="B",
                q3="C",
                q4="D",
            )
