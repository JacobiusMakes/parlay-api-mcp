# Publishing ParlayAPI to the official MCP registry

**Why this matters for organic growth:** the MCP registry
(`registry.modelcontextprotocol.io`) is where AI-tool users and agents browse for
capabilities. As of 2026-07-25 ParlayAPI is **not listed**, and searching the
registry for "parlay" returns a *different* company (`run.parlay/parlay`, a
prediction-market aggregator). We are invisible in the one directory built for
agent discovery, while a similar name owns the search term.

Everything is prepared. What remains needs an operator credential.

## What is ready

- `mcp-server/registry/server.json` — the manifest in the registry's current
  schema (`2025-12-11`), pointing at the already-published PyPI package
  `parlayapi-mcp` 0.3.0. Validated JSON.
- Signing key — an ed25519 keypair for the `com.parlay-api` namespace already
  exists on the box at `/home/parlay/.mcp_registry_key` (chmod 600, private key
  never printed or copied off the host).
- Public key for DNS verification:

      v=MCPv1; k=ed25519; p=go98ulKv4PEA00vt4vrR1IVX6oMqQ/iax4JH2/iQtKI=

- CLI: `mcp-publisher` 1.8.0 (download from the
  `modelcontextprotocol/registry` releases).

## Path A: branded namespace `com.parlay-api/parlayapi` (recommended)

Reads as vendor-owned, which is worth something in a betting-data category.
Blocked only because the `CLOUDFLARE_API_TOKEN` in `.env` is **expired**
(verified against Cloudflare's token endpoint; nothing else in the codebase uses
it, so its expiry is not breaking anything else).

1. Add a TXT record on `parlay-api.com` with exactly the value above. Either
   paste it in the Cloudflare dashboard, or refresh the API token and re-run
   `scratchpad/cf_txt.py` (that script only ever CREATEs, never edits or deletes
   existing TXT records).
2. Then, on the box:

       mcp-publisher login dns --domain parlay-api.com \
         --private-key "$(cat /home/parlay/.mcp_registry_key)"
       cd mcp-server/registry && mcp-publisher publish

## Path B: GitHub namespace `io.github.JacobiusMakes/parlayapi` (faster)

No DNS needed; uses a GitHub device-code login (about 30 seconds, interactive).

1. Change `name` in `server.json` to `io.github.JacobiusMakes/parlayapi`.
2. `mcp-publisher login github` (visit the URL, enter the code).
3. `cd mcp-server/registry && mcp-publisher publish`

## Verify after publishing

    curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=parlayapi" | head -c 400

The entry should come back with our name, description and the PyPI package.

## Still outstanding on the distribution surface

- **npm SDK unpublished** — blocked on the npm account reset. `~/.npmrc` still
  contains the literal `__PASTE_` placeholder.
- **`/openapi.json` is 200 paths / 294 KB.** Far too large for an agent to
  ingest; anything that tries burns enormous context or gives up. A curated
  agent-facing subset (the ~15 endpoints that matter: odds, props, sports,
  bookmakers, ev, arbitrage, consensus, middles, verdict, best-bets, historical)
  is the obvious next build, linked from `llms.txt`.
