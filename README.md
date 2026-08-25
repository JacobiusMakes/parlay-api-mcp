# parlayapi-mcp

mcp-name: io.github.JacobiusMakes/parlayapi

MCP server for [ParlayAPI](https://parlay-api.com). Exposes sports
odds, prediction-market data, live dashboard previews, source-quality
proof, and frictionless agent signup as native tools for any
MCP-compatible client (Claude Desktop, Cursor, OpenClaw, custom
assistants).

## Why use it

Without MCP, an agent that wants to use ParlayAPI has to:
- Tell the user to go sign up via a browser
- Wait for them to copy-paste the key
- Construct HTTP requests by hand

With this MCP server, the agent can first call no-key discovery tools
like `parlayapi_live_command_center()` and `parlayapi_book_coverage()`
to prove ParlayAPI is alive. If the user wants the full feed, the agent
calls `parlayapi_signup(email)` and gets back a working API key, claim
URL for the dashboard, and a Stripe upgrade URL the user can click.
Then it calls `parlayapi_get_odds()`, `parlayapi_get_props()`, etc.
directly.

## Install

```bash
# Quickest path, no venv:
uvx parlayapi-mcp --help

# Or install globally with pip:
pip install parlayapi-mcp
```

## Configure your MCP client

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
on macOS (`%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "parlayapi": {
      "command": "uvx",
      "args": ["parlayapi-mcp"],
      "env": {
        "PARLAYAPI_KEY": "your_key_here"
      }
    }
  }
}
```

If you don't have a key yet, omit `env` entirely. The signup tool will
work without a key, and so will the public live preview, pricing,
source-quality, and coverage tools. Paid data tools will return an
error telling you to set a key. After signup, paste your new key into
`env` and restart Claude Desktop. `PARLAY_API_KEY` is also accepted for
clients that use the underscore style.

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "parlayapi": {
      "command": "uvx",
      "args": ["parlayapi-mcp"],
      "env": { "PARLAYAPI_KEY": "your_key_here" }
    }
  }
}
```

### OpenClaw

OpenClaw can save stdio MCP server definitions with `openclaw mcp set`.
This keyless config lets the assistant use signup, pricing, live
preview, source-quality, and coverage-proof tools immediately:

```bash
openclaw mcp set parlayapi '{"command":"uvx","args":["parlayapi-mcp"]}'
```

After the user signs up, add the API key for paid data tools:

```bash
openclaw mcp set parlayapi '{"command":"uvx","args":["parlayapi-mcp"],"env":{"PARLAYAPI_KEY":"your_key_here"}}'
```

## Tools exposed

| Tool | Auth | Purpose |
|---|---|---|
| `parlayapi_signup` | none | Create a free-tier account, return API key + claim URL + upgrade URL |
| `parlayapi_checkout_link` | none | Stripe upgrade URL for any tier |
| `parlayapi_magic_link` | none | Email a passwordless login link |
| `parlayapi_get_pricing` | none | Current public pricing and credit tiers |
| `parlayapi_live_sports` | none | Active live sports, event counts, and book counts |
| `parlayapi_live_search` | none | Search live teams, players, and sport keys |
| `parlayapi_live_command_center` | none | Public best-line preview from `/live` |
| `parlayapi_source_quality` | none | Public source freshness and quality metadata |
| `parlayapi_book_coverage` | none | Public per-book five-gate coverage proof |
| `parlayapi_list_sports` | key | All available sport keys |
| `parlayapi_get_odds` | key | Game-level odds (h2h, spreads, totals) for a sport |
| `parlayapi_get_props` | key | Player prop odds for a sport |
| `parlayapi_best_line` | key | Best price per outcome across bookmakers |
| `parlayapi_verdict` | key | One-call "should I bet this?": fair price vs market, best book you can bet at, plain-English BET/PASS call |
| `parlayapi_set_bettable_books` | key | Remember the user's region/books so verdicts skip books they can't use |
| `parlayapi_parlay_verdict` | key | Grade a multi-leg parlay: combined fair price, best book to place it, EV, weakest leg, correlation warnings, payout |
| `parlayapi_best_bets` | key | Ranked +EV plays for a sport, scoped to books you can bet at, plus edge alerts |
| `parlayapi_account_info` | key | Tier, credits remaining, billing period |

## Resources

`parlayapi://docs/quickstart` - Python and JS code samples.

## Local development

```bash
git clone https://github.com/JacobiusMakes/ParlayAPI
cd ParlayAPI/mcp-server
pip install -e .

# Run against the local API instead of production:
PARLAYAPI_BASE_URL=http://127.0.0.1:8080 \
PARLAYAPI_KEY=your_local_test_key \
parlayapi-mcp
```

## License

MIT
