# MCP registry submissions for parlayapi-mcp

After publishing to PyPI, submit to these registries to increase
discoverability. All submissions are simple PRs / form fills.

## 1. modelcontextprotocol.io / mcp-servers list

The official curated list of MCP servers lives at
https://github.com/modelcontextprotocol/servers. To add parlayapi-mcp:

1. Fork the repo.
2. Add an entry to `README.md` under "Community" (alphabetical):

```markdown
- **[ParlayAPI](https://github.com/JacobiusMakes/ParlayAPI/tree/main/mcp-server)** - Sports betting odds, player props, and prediction-market data from 32 bookmakers. Free-tier signup tool means agents can provision an account and start using it in one call.
```

3. Open PR. They review within a day or two.

## 2. Smithery

Smithery (https://smithery.ai) is a discovery + install hub. Submit at
https://smithery.ai/server/new with this metadata:

```yaml
name: parlayapi
displayName: ParlayAPI
description: Sports odds, live dashboard previews, source-quality proof, and frictionless agent signup
repository: https://github.com/JacobiusMakes/ParlayAPI
homepage: https://parlay-api.com/mcp
license: MIT
keywords: [sports, betting, odds, agent, signup, claude, gpt, mcp]
runtime: python
install:
  - command: uvx
    args: [parlayapi-mcp]
config:
  env:
    PARLAYAPI_KEY:
      type: string
      description: ParlayAPI API key. Public preview and signup tools work without it.
      required: false
tools:
  - parlayapi_signup
  - parlayapi_checkout_link
  - parlayapi_magic_link
  - parlayapi_get_pricing
  - parlayapi_live_sports
  - parlayapi_live_search
  - parlayapi_live_command_center
  - parlayapi_source_quality
  - parlayapi_book_coverage
  - parlayapi_list_sports
  - parlayapi_get_odds
  - parlayapi_get_props
  - parlayapi_best_line
  - parlayapi_account_info
```

## 3. mcp.so

Open submission at https://mcp.so/submit. Include the server.json:

```json
{
  "name": "parlayapi-mcp",
  "description": "Sports odds, player props, live dashboard previews, source-quality proof, prediction-market data, and frictionless agent signup. Free tier exists.",
  "repository": "https://github.com/JacobiusMakes/ParlayAPI",
  "homepage": "https://parlay-api.com/mcp",
  "package_name": "parlayapi-mcp",
  "package_registry": "pypi",
  "tools": [
    {"name": "parlayapi_signup", "description": "Create a free-tier account, return API key + magic-link claim URL"},
    {"name": "parlayapi_live_command_center", "description": "Public best-line preview from the /live dashboard"},
    {"name": "parlayapi_source_quality", "description": "Public source freshness and quality metadata"},
    {"name": "parlayapi_book_coverage", "description": "Public per-book coverage proof"},
    {"name": "parlayapi_get_odds", "description": "h2h, spreads, totals across 32 bookmakers"},
    {"name": "parlayapi_get_props", "description": "Player prop odds (DK, FanDuel, BetMGM, PrizePicks, Underdog, etc.)"},
    {"name": "parlayapi_best_line", "description": "Best price per outcome across all bookmakers"}
  ],
  "categories": ["data", "sports", "betting", "agent"],
  "license": "MIT"
}
```

## 4. PulseMCP

Submit at https://pulsemcp.com/submit. Form-based, paste GitHub repo
URL and the MCP server section of the README is auto-extracted.

## 5. Awesome MCP Servers

There's an "awesome" list at
https://github.com/punkpeye/awesome-mcp-servers. Same pattern as
modelcontextprotocol/servers - PR adding an entry under the appropriate
category (Data / APIs / similar).

## Order of submissions

1. **modelcontextprotocol/servers** (highest signal, official-adjacent)
2. **Smithery** (highest install volume)
3. **mcp.so** (good SEO)
4. **PulseMCP** (newer but growing)
5. **Awesome MCP Servers**

Each takes ~10 min. Total: under an hour. Do AFTER publishing to PyPI
so the install command actually works for users who find the listing.

## 6. OpenClaw

OpenClaw has first-class MCP save/list/show commands. There is no
separate registry submission step in the docs right now, so treat this
as a community-distribution channel:

1. Publish a short post with the keyless install command:

```bash
openclaw mcp set parlayapi '{"command":"uvx","args":["parlayapi-mcp"]}'
```

2. Show an immediate no-key prompt:

```text
Use ParlayAPI to show me which live sports are active, then pull the
current best-line preview and source-quality report.
```

3. Then show the upgrade path:

```bash
openclaw mcp set parlayapi '{"command":"uvx","args":["parlayapi-mcp"],"env":{"PARLAYAPI_KEY":"YOUR_KEY"}}'
```

Positioning: "agent-native sports odds infrastructure that proves live
coverage before asking for a key."
