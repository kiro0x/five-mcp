"""FIVE Character Engine — MCP Server

Exposes the FIVE /generate endpoint as an MCP tool so that any
MCP-compatible client (Claude Desktop, Cursor, etc.) can call it directly.

Environment variable required:
    FIVE_API_KEY  –  Your API key (five_sk_xxx)
"""

from __future__ import annotations

import os
from typing import Literal, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# ── Server instance ──────────────────────────────────────────────
mcp = FastMCP(
    "five-character-engine",
    instructions=(
        "FIVE Character Engine – an LLM constraint engine that returns "
        "JSON personality/style constraints for consistent character voices. "
        "Paid API ($1/call). Requires a FIVE_API_KEY environment variable."
    ),
)

FIVE_API_URL = "https://fiveengine.dev/generate"
TIMEOUT = 30.0  # seconds


def _get_api_key() -> str:
    """Read API key from environment; abort clearly if missing."""
    key = os.environ.get("FIVE_API_KEY", "")
    if not key:
        raise RuntimeError(
            "FIVE_API_KEY is not set. "
            "Get your key at https://fiveengine.dev and set it as an "
            "environment variable (e.g. FIVE_API_KEY=five_sk_xxx)."
        )
    return key


ChoiceABCD = Literal["A", "B", "C", "D"]
ScaleValue = Literal[1, 2, 3, 4, 5]


@mcp.tool()
async def generate(
    character_name: str,
    q1: ChoiceABCD,
    q2: ChoiceABCD,
    q3: ChoiceABCD,
    q4: ChoiceABCD,
    s1: Optional[ScaleValue] = None,
    s2: Optional[ScaleValue] = None,
    s3: Optional[ScaleValue] = None,
    s4: Optional[ScaleValue] = None,
    free_text: Optional[str] = None,
) -> dict:
    """Generate character constraints using the FIVE engine.

    This tool calls the FIVE Character Engine API to produce JSON
    constraints that keep an LLM character's voice consistent.

    Each call costs $1 and consumes one credit from your account.

    Args:
        character_name: Name of the character to generate constraints for.
        q1: Personality axis 1 – choose A, B, C, or D.
        q2: Personality axis 2 – choose A, B, C, or D.
        q3: Personality axis 3 – choose A, B, C, or D.
        q4: Personality axis 4 – choose A, B, C, or D.
        s1: Style slider 1 (1-5, default 3). Optional fine-tuning.
        s2: Style slider 2 (1-5, default 3). Optional fine-tuning.
        s3: Style slider 3 (1-5, default 3). Optional fine-tuning.
        s4: Style slider 4 (1-5, default 3). Optional fine-tuning.
        free_text: Optional free-form description to further guide generation.

    Returns:
        A dict with keys: status, remaining (credits left), constraint (the
        generated JSON constraint object).
    """
    api_key = _get_api_key()

    payload: dict = {
        "character_name": character_name,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "q4": q4,
    }
    # Only send optional fields when explicitly provided
    if s1 is not None:
        payload["s1"] = s1
    if s2 is not None:
        payload["s2"] = s2
    if s3 is not None:
        payload["s3"] = s3
    if s4 is not None:
        payload["s4"] = s4
    if free_text is not None:
        payload["free_text"] = free_text

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            FIVE_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code == 401:
        raise RuntimeError(
            "Authentication failed. Check your FIVE_API_KEY."
        )
    if resp.status_code == 402:
        raise RuntimeError(
            "Insufficient credits. Top up at https://fiveengine.dev"
        )
    if resp.status_code == 429:
        raise RuntimeError(
            "Rate limited. Please wait a moment and try again."
        )

    resp.raise_for_status()
    return resp.json()


# ── Entry point ──────────────────────────────────────────────────
def main() -> None:
    """Run the MCP server (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
