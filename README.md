# parlay-api-mcp

MCP server for [ParlayAPI](https://parlay-api.com): live sports betting odds across 21+ sportsbooks, DFS apps, exchanges, and prediction markets, exposed as tools any MCP-aware AI agent (Claude, Cursor, Continue, Devin, Codex) can call directly during a conversation.

## What you get

10 tools your agent can call:

| Tool | Purpose |
| --- | --- |
| `list_sports` | Enumerate every sport_key supported |
| `get_odds` | Live moneyline / spread / total across all books |
| `get_player_props` | Player props with optional filter by player or market |
| `find_arbitrage` | Pre-computed cross-book arb opportunities |
| `find_positive_ev` | Pre-computed +EV bets vs no-vig consensus |
| `compare_books` | Side-by-side line comparison across all books |
| `get_prediction_market_prices` | Kalshi + Polymarket prices in standard odds format |
| `get_historical_odds` | Pull historical odds for backtesting (1.15M+ rows back to 2005) |
| `get_archive_coverage` | Public archive coverage stats (no API key required) |
| `get_account_usage` | Your free-tier or paid-tier remaining credits |

## Install

```bash
pip install parlay-api-mcp
```

Or from source:

```bash
git clone https://github.com/parlay-api/parlay-api-mcp.git
cd parlay-api-mcp
pip install -e .
```

## Configure

Get a free API key at https://parlay-api.com/signup (1,000 requests/month, no credit card).

### Claude Code

Add to `~/.config/claude/mcp_settings.json` (Linux/macOS) or `%APPDATA%\claude\mcp_settings.json` (Windows):

```json
{
  "mcpServers": {
    "parlay-api": {
      "command": "parlay-api-mcp",
      "env": { "PARLAY_API_KEY": "your_key_here" }
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "parlay-api": {
      "command": "parlay-api-mcp",
      "env": { "PARLAY_API_KEY": "your_key_here" }
    }
  }
}
```

### Continue (VS Code / JetBrains)

Add to your `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "parlay-api",
      "command": "parlay-api-mcp",
      "env": { "PARLAY_API_KEY": "your_key_here" }
    }
  ]
}
```

### Anthropic Workbench / Claude Desktop

Add via the standard MCP configuration UI or `claude_desktop_config.json`.

## Run manually for testing

```bash
PARLAY_API_KEY=your_key parlay-api-mcp
```

It runs over stdio and waits for an MCP client to connect.

## Try it

Once configured, ask your AI agent things like:

- "What are the current MLB moneyline odds at DraftKings vs FanDuel?"
- "Find me arbitrage opportunities in the NBA right now."
- "What's Aaron Judge's home run prop line at every book?"
- "Pull NBA closing lines from January 2024 and compute a line-shopping backtest."
- "Are there any Kalshi vs sportsbook arbitrage plays in baseball today?"

## Configuration

Environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PARLAY_API_KEY` | (required) | Your ParlayAPI key |
| `PARLAY_API_URL` | `https://parlay-api.com` | Override for self-hosted / staging |

## Pricing

ParlayAPI tiers (full info at https://parlay-api.com/pricing):

- **Free** — 1,000 requests/month, 5 sports, REST only
- **Starter** — $19/mo, 100K requests, all sports
- **Pro** — $99/mo, 1M requests, WebSocket, all DFS apps, all prediction markets
- **Business** — $499/mo, 10M requests
- **Enterprise** — $2,499/mo, 100M requests, SLA

Each MCP tool call counts as one API request against your tier.

## License

MIT. See LICENSE.

## Links

- ParlayAPI: https://parlay-api.com
- Documentation: https://parlay-api.com/docs
- LLM-readable spec: https://parlay-api.com/llms.txt
- Capability manifest: https://parlay-api.com/agents.json
- Comparison vs alternatives: https://parlay-api.com/vs-toa
- Historical archive: https://parlay-api.com/historical-coverage
