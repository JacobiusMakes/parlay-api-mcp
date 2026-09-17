# parlay-api-mcp compatibility package

**Use [`parlayapi-mcp`](https://pypi.org/project/parlayapi-mcp/) for new
installations.** It is the canonical ParlayAPI MCP package:

```sh
uvx parlayapi-mcp
# Or:
pip install parlayapi-mcp
```

This official compatibility package supports existing directory listings and
client configurations that use the GitHub repository name, `parlay-api-mcp`,
as the install name. It depends on exactly `parlayapi-mcp==0.3.7` and provides
the `parlay-api-mcp` command through the canonical package's existing entry
point. It contains no server implementation.

Existing `uvx parlay-api-mcp` and `pip install parlay-api-mcp` instructions
therefore resolve to that canonical release. For future releases, use the
canonical package name. Configuration, tools, account requirements, and
[API terms](https://parlay-api.com/terms) are unchanged; see the
[canonical README](https://github.com/JacobiusMakes/parlay-api-mcp#readme).

To build this compatibility distribution separately from the repository root:

```sh
python -m build compat/parlay-api-mcp --outdir dist/compat
```
