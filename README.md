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

## Install in Claude Desktop (one click)

Download
[parlayapi-mcp-0.3.5.mcpb](https://github.com/JacobiusMakes/parlay-api-mcp/releases/download/v0.3.5/parlayapi-mcp-0.3.5.mcpb)
and open it (double-click, or drag it onto Claude Desktop). Claude
Desktop unpacks the bundle and runs the server with its managed uv
runtime, so no terminal or Python setup is needed.

The API key field in the install dialog is optional. Leave it blank to
start keyless: signup, pricing, live previews, source quality, and
coverage tools work immediately, and the `parlayapi_signup` tool can
create a free key (1,000 credits/mo, no card) without leaving the chat.
Add the key later any time under Settings, Extensions, ParlayAPI.

The bundle source lives in [`mcpb/`](mcpb/). Rebuild it with
`npx @anthropic-ai/mcpb pack mcpb/`.

## Install (manual, any MCP client)

```bash
# Start the stdio server (normally launched by your MCP client):
uvx parlayapi-mcp

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

## Run locally with Docker

Build the stdio container from this repository:

```bash
docker build -t parlayapi-mcp:local .
docker run --rm -i --read-only --cap-drop=ALL --security-opt=no-new-privileges parlayapi-mcp:local
```

The process waits for MCP messages on stdin. It does not open a web server or
make an API call just by starting. Connect it through an MCP client; do not use
`-t`, which would allocate a terminal instead of the MCP stdio transport.

For account tools, configure your own `PARLAYAPI_KEY` in your MCP client's
secret configuration and pass that environment variable into the container:

```bash
docker run --rm -i --read-only --cap-drop=ALL --security-opt=no-new-privileges -e PARLAYAPI_KEY parlayapi-mcp:local
```

No key is baked into the image. Each user should configure their own key and
keep account responses within their own client. This container is not a shared
community feed. The MIT software license grants no data distribution rights;
[applicable Terms](https://parlay-api.com/terms) and any written agreement govern
API data use. These container defaults do not amend existing agreements.

Public discovery tools need no key. Account tools use your allowance; check
[current plans and limits](https://parlay-api.com/pricing). The existing tool set
also includes account creation, checkout-link creation, login-link email and
saved-book preferences. Approve those actions explicitly in your MCP client.
Listing tools itself creates no account, sends no email and starts no checkout.

For private security reports, email support@parlay-api.com. Do not put API keys
or account responses in public issues.

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
| `parlayapi_find_arbitrage` | key | Cross-book arbitrage candidates, 3-way (home/draw/away) markets included |
| `parlayapi_find_ev` | key | Positive-EV bets vs a sharp book's no-vig fair line |
| `parlayapi_consensus` | key | Consensus (average) odds across all bookmakers per market |
| `parlayapi_find_middles` | key | Cross-book middle opportunities |

## Resources

`parlayapi://docs/quickstart` - Python and JS code samples.

## Local development

```bash
git clone https://github.com/JacobiusMakes/parlay-api-mcp
cd parlay-api-mcp
pip install -e .

# Run against the local API instead of production:
PARLAYAPI_BASE_URL=http://127.0.0.1:8080 \
PARLAYAPI_KEY=your_local_test_key \
parlayapi-mcp
```

## Privacy Policy

This extension connects to ParlayAPI. See the [ParlayAPI Privacy Policy](https://parlay-api.com/privacy).

## License

MIT

---

Part of the [ParlayAPI](https://parlay-api.com) ecosystem: a real-time sports odds API with a free tier of 1,000 credits per month, no card required. Explore all the tools at [github.com/JacobiusMakes](https://github.com/JacobiusMakes).
