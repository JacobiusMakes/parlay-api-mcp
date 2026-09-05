# Publish ParlayAPI to the official MCP Registry

The published namespace is `io.github.JacobiusMakes/parlayapi`. Its source is
this public repository, and its Python package is `parlayapi-mcp` on PyPI.

`server.official.json` is the canonical registry manifest. Keep
`registry/server.json` identical for consumers that use that path. The root
`server.json` is a separate, descriptive client manifest, not a registry schema.

## Release workflow

1. Update the version in `pyproject.toml` and all three manifests. Keep the
   `mcp-name: io.github.JacobiusMakes/parlayapi` marker in the PyPI README.
2. Publish the Python package to PyPI using the normal package release process.
3. Publish the matching GitHub release, named `v<version>`, from a commit on main.
   The **MCP Registry** workflow validates the package and publishes the manifest.
4. To recover a missed registry publication, run **MCP Registry** from the Actions
   tab on `main`. An identical existing entry is a successful no-op. A conflicting
   entry fails instead of overwriting published metadata.

The workflow uses GitHub OIDC and a checksum-pinned official publisher binary.
No personal token, DNS change or device-code login is required. Pull requests
only validate; publishing runs on GitHub-hosted runners for main/release commits.
Publishing the registry entry does not deploy the API or publish a new PyPI package.

## Verify

```bash
python3 -m pip install 'jsonschema==4.26.0'
python3 scripts/check_registry.py --published
```

This checks the official schema, manifest parity, current PyPI package ownership,
stdio installation, hosted transport and the exact published registry entry.
It does not make account, billing or authenticated odds requests.

Official references:

- [Publishing automation](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/github-actions.mdx)
- [Registry authentication](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/authentication.mdx)
