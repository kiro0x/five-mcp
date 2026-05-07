# five-mcp

MCP server for the [FIVE Character Engine](https://fiveengine.dev) — an LLM constraint engine that generates JSON personality/style constraints for consistent character voices.

## Quick Start

### Install

```bash
pip install five-mcp
```

### Configure

Set your API key as an environment variable:

```bash
export FIVE_API_KEY=five_sk_your_key_here
```

Get your key at [fiveengine.dev](https://fiveengine.dev).

### Use with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "five-character-engine": {
      "command": "five-mcp",
      "env": {
        "FIVE_API_KEY": "five_sk_your_key_here"
      }
    }
  }
}
```

### Use with other MCP clients

Any MCP-compatible client can connect via stdio transport:

```bash
five-mcp
```

## Tool: `generate`

Generates character constraints via the FIVE engine.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `character_name` | string | Yes | Name of the character |
| `q1` – `q4` | A / B / C / D | Yes | Personality axis choices |
| `s1` – `s4` | 1–5 | No | Style sliders (default: 3) |
| `free_text` | string | No | Free-form description |

### Response

```json
{
  "status": "ok",
  "remaining": 42,
  "constraint": { "..." }
}
```

## Pricing

Each `generate` call costs **$1** and consumes one credit. Manage credits at [fiveengine.dev](https://fiveengine.dev).

## Links

- **API & Docs:** [fiveengine.dev](https://fiveengine.dev)
- **GitHub:** [github.com/kiro0x/five-mcp](https://github.com/kiro0x/five-mcp)
- **Engine repo:** [github.com/kiro0x/five-character-engine](https://github.com/kiro0x/five-character-engine)

## License

MIT
