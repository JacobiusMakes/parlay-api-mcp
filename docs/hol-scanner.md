# Reproducing the HOL reviewer check

The pending workflow template in `docs/hol-plugin-scanner.yml.pending` pins checkout to v4.2.2 commit 11bd71901bbe5b1630ceea73d27597364c9af683 and HOL action to commit 55616c962cf86368423f7673b2ecdfdbe613d1af (v1.2.515). That action bundles scanner-version.txt selecting plugin-scanner 2.0.1116 and verifies wheel SHA256 40d40308484e49b438c6ef47a7794ab6aac617914447174f80fe4578911cdcb3 plus PyPI provenance. The action exposes no scanner-version input; its immutable commit pins that version transitively.

Use an isolated Python 3.12 environment, outside the source checkout:

```sh
python3.12 -m venv /tmp/parlay-hol-check
/tmp/parlay-hol-check/bin/python -m pip install plugin-scanner==2.0.1116
/tmp/parlay-hol-check/bin/plugin-scanner verify . --format text
/tmp/parlay-hol-check/bin/plugin-scanner scan . --format json
```

The template enables no --online flag, API key, write permissions, SARIF upload, PR comments or registry submission. The pinned scanner installs Cisco skill-scanner transitively; no claim is made that Cisco dependencies are absent.

## Local results and open findings

Pinned verification exits 1: it expects .codex-plugin/plugin.json, which this standalone MCP server does not declare, and skips stdio execution for safety. The initial weighted scan exits 0 but scores 56/100. After adding SECURITY.md and Dependabot configuration, the score is 63/100, still below the 80 threshold. Exit 0 alone is not a passing admission result. Neither scan reports high/critical findings, and optional deep MCP scanning was unavailable. Rule findings:

- PLUGIN_JSON_MISSING / PLUGIN_JSON_INVALID / PLUGIN_JSON_REQUIRED_FIELDS_UNCHECKED: scanner classifies this source as a Codex plugin. Maintainer review should establish the appropriate MCP ecosystem route; adding fictitious package metadata is not a remediation.
- DEPENDENCY_LOCKFILE_MISSING: reproducible dependency locking remains outstanding.
- SECURITY_MD_MISSING / DEPENDABOT_MISSING: addressed by this change; private reporting follows the existing README, and dependency updates are grouped weekly.
- CODEXIGNORE_MISSING: Codex-specific informational finding, pending ecosystem clarification.

The template is intentionally outside `.github/workflows` and does not run in CI until upstream confirms a supported standalone MCP target. No findings are suppressed. No passing badge is claimed. Local verification is not a hosted CI run; no hosted success is claimed. Existing account billing restrictions must be resolved before relying on new hosted runs. No runtime MCP server execution or account-data request was performed in this check.

References: https://github.com/hashgraph-online/awesome-ai-plugins/pull/235#issuecomment-5585054591 and https://github.com/hashgraph-online/awesome-ai-plugins/blob/main/SCANNER_GUIDE.md .

Pinned `scan --help` and `--list-ecosystems` enumerate only auto/codex/claude/gemini/opencode, not standalone MCP. `verify --help` exposes no ecosystem selector. The optional Cisco MCP static check is not an alternative ecosystem classifier. Upstream clarification is required before turning on a misleading Codex gate. The existing library build uses open dependency ranges and no lock workflow; a cosmetic scanner-only lockfile is not added.
