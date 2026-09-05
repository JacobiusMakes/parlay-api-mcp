# LobeHub publisher handoff

This repository contains a prepared owner declaration for LobeHub, `lhm.plugin.json`. It is not proof of a published listing or a completed LobeHub client installation.

## Prepared configuration

- Repository: https://github.com/JacobiusMakes/parlay-api-mcp
- Proposed stable identifier: `jacobiusmakes-parlay-api-mcp`. Confirm any existing listing before publishing; do not create another identifier to work around a conflict.
- Display name: ParlayAPI Sports Odds. Server/package version: `0.3.5`.
- Local stdio package: `parlayapi-mcp==0.3.5`, launched with `uvx`.
- No key is needed to start the server or inspect its tools. Public discovery tools are available without a key. Authenticated data uses each user's own ParlayAPI key in their private client's `PARLAYAPI_KEY` environment configuration.
- Scope: personal and internal research. The code's MIT license does not grant API data redistribution rights. See the [API terms](https://parlay-api.com/terms) and [privacy policy](https://parlay-api.com/privacy).

The server includes account signup, login-email, checkout-link and saved-book-preference actions. Invoke these only at the user's request. None was invoked during preparation.

Copyable keyless local-client configuration:

```json
{
  "mcpServers": {
    "parlayapi": {
      "command": "uvx",
      "args": ["parlayapi-mcp==0.3.5"]
    }
  }
}
```

LobeHub's current owner-manifest fields do not include a stdio command, arguments, environment configuration or deployment-options array. Unknown extra fields are stripped. Consequently, the local launch command belongs in installation instructions; adding an invented `mcp` or `deploymentOptions` field would not configure the listing. Verify the generated installation option after publication.

`cloudEndpoint` is deliberately omitted from this local integration. This does not claim LobeHub hosted execution or OAuth support. For an existing listing, omitting this field preserves an earlier remote endpoint; inspect that listing before an update and resolve any incorrect deployment option separately.

## Local validation completed

Checked September 5, 2026 with Node 22.22.0 and the official `@lobehub/market-cli@0.0.41`.

The official `plugin init --stdio` generator connected to the actual repository server and discovered **22 tools, one resource and zero prompts**. The temporary launcher removed API-key variables and disabled provider HTTP clients; inspection invoked no tools. Because the CLI reads `package.json` fallback metadata but this is a Python project, a temporary package metadata file was supplied outside the repository. It mirrored the existing package name, version, description and repository URL.

The reviewed declaration preserves every captured tool name, input/output schema and resource. Its concise tool descriptions come from the existing MCPB manifest. Metadata was adjusted for the display name, personal/internal scope and exposed account actions. No runtime or dependencies changed.

The CLI's own `readPluginManifest` function was evaluated offline against this file, without entering authentication or publication code. The CLI only checks a JSON object and nonempty identifier/name/version at that step; it has no standalone full-manifest validation command. Additional checks covered the documented field allowlist, URL fields, identifier pattern, nonempty first-publication description, and the official MCP SDK tool/resource schemas. These checks do not establish server-side acceptance, crawler behavior or native-client installation.

## When the owner can authorize the marketplace

Use Node.js 22 or newer. The following are maintainer commands, not a script that runs automatically. Keep credentials in the CLI's own storage; never read, copy or commit its credential files.

First inspect status:

```sh
npx -y @lobehub/market-cli@0.0.41 auth status --output json
npx -y @lobehub/market-cli@0.0.41 github status
```

No credentials may produce exit code 1. If authorization is missing, the owner completes each browser flow once, on the machine where the CLI runs:

```sh
npx -y @lobehub/market-cli@0.0.41 login
npx -y @lobehub/market-cli@0.0.41 github connect
```

The connected GitHub account must own or have push access to the canonical repository. M2M registration cannot grant publication permission. No login, registration or GitHub authorization was initiated during this preparation.

Then inspect owned listings and check the public marketplace for this exact repository:

```sh
npx -y @lobehub/market-cli@0.0.41 plugin list --output json
```

If there is no existing listing, publish the reviewed declaration from this checkout:

```sh
lobehub_repo_dir="$(git rev-parse --show-toplevel)"
npx -y @lobehub/market-cli@0.0.41 plugin publish \
  https://github.com/JacobiusMakes/parlay-api-mcp \
  --dir "$lobehub_repo_dir" --output json
```

For an existing listing, reconcile its actual identifier and repository first. Claim it only if needed, then use `plugin update --dir "$lobehub_repo_dir"`. Updating version `0.3.5` merges supplied fields into that version; do not invent a new package version just for a metadata correction.

After publication, confirm the owned listing and public page. Check the identifier, repository, version, capability counts and installation command. Repository enrichment is asynchronous; a successful command alone is not proof of a working public install. Stop on an incorrect package, generated remote endpoint or authentication configuration instead of repeatedly resubmitting.

## Primary references

- [Official publisher guide and manifest reference](https://market.lobehub.com/s/publish-mcp), reached from https://lobehub.com/publish-mcp/skill.md. The guide declares last synchronization August 5, 2026; it was read September 5.
- [Pinned publisher CLI](https://www.npmjs.com/package/@lobehub/market-cli/v/0.0.41), checked against its published executable for local inspection, parsing and command order.
- [Official MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk), used for the standard tool and resource schema checks.
