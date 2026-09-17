# parlay-api-mcp compatibility package

**UNPUBLISHED — PyPI name-similarity review pending.** PyPI rejected this
distribution name as too similar to an existing project. The compatibility
package is not available from PyPI; use the working canonical commands below.

**Use [`parlayapi-mcp`](https://pypi.org/project/parlayapi-mcp/) for new
installations.** It is the canonical ParlayAPI MCP package:

```sh
uvx parlayapi-mcp
# Or:
pip install parlayapi-mcp
```

This official compatibility package is prepared to support existing directory listings and
client configurations that use the GitHub repository name, `parlay-api-mcp`,
as the install name. It depends on exactly `parlayapi-mcp==0.3.7` and provides
the `parlay-api-mcp` command through the canonical package's existing entry
point. It contains no server implementation.

If PyPI approves the name and the package is published, existing
`uvx parlay-api-mcp` and `pip install parlay-api-mcp` instructions would resolve
to that canonical release. For future releases, use the
canonical package name. Configuration, tools, account requirements, and
[API terms](https://parlay-api.com/terms) are unchanged; see the
[canonical README](https://github.com/JacobiusMakes/parlay-api-mcp#readme).

To build this compatibility distribution separately from the repository root:

```sh
python -m build compat/parlay-api-mcp --outdir dist/compat
```
