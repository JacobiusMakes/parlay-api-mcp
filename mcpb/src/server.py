"""MCPB entry point for parlayapi-mcp.

Thin wrapper: the real server ships on PyPI as parlayapi-mcp (pinned in
this bundle's pyproject.toml). The host app runs this file with uv,
which installs the pinned dependency on first launch, and the server
speaks MCP over stdio.
"""

from parlayapi_mcp.server import main

if __name__ == "__main__":
    main()
