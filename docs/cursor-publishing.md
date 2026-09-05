# ParlayAPI for Cursor

This repository includes a Cursor plugin manifest in `.cursor-plugin/plugin.json`.
It loads `cursor-mcp.json` and the published `parlayapi-mcp` 0.3.5 package.
Install [uv](https://docs.astral.sh/uv/getting-started/installation/) on the machine
that runs the MCP server. The existing `.plugin/` metadata serves a separate
community format; use this repository's Cursor manifest for the official portal.

## Configuration

The plugin declares an optional `PARLAYAPI_KEY` variable, defaulting to empty.
Public discovery is available with that default. For authenticated access,
configure your own ParlayAPI key through Cursor's plugin variable settings.
Team administrators manage these values under Dashboard > Plugins > Configure.
Do not commit the key or put it in an install URL. Each account's allowance
applies to its requests; inspect current pricing through `parlayapi_get_pricing`.

First inspect the tool list. A later request can inspect source coverage with
`parlayapi_book_coverage` before choosing a sport or market. Account creation,
login email, checkout-link creation and preference changes are separate actions;
approve them only when you want them. No tools are automatically approved by
this package. Software installation does not grant API data redistribution rights.

For a client without plugin variables, use the manual Cursor configuration in
the main README and place your own key only in your private local configuration.

## Publisher handoff

Submit `https://github.com/JacobiusMakes/parlay-api-mcp` through the
[official Cursor publishing portal](https://cursor.com/marketplace/publish).
The manifest, icon, MCP configuration, README and
[privacy policy](https://parlay-api.com/privacy) are public.

This is a prepared package, not an approved Cursor marketplace listing.
Schema and protocol checks do not certify a native Cursor installation; complete
that client verification before claiming it in a submission.

Reference: [Cursor plugin manifest, variables and submission requirements](https://prod.cursor.com/docs/reference/plugins).
