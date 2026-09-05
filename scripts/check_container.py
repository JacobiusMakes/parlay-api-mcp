"""Discover container tools with no credentials or network access."""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def check():
    parameters = StdioServerParameters(
        command="docker",
        args=[
            "run", "--rm", "-i", "--name", "parlayapi-mcp-check",
            "--network=none", "--read-only", "--cap-drop=ALL",
            "--security-opt=no-new-privileges", "--memory=256m", "--cpus=1",
            "parlayapi-mcp:check",
        ],
        env={"PATH": "/usr/local/bin:/usr/bin:/bin"},
    )
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            resources = await session.list_resources()
            names = {tool.name for tool in tools.tools}
            assert len(names) == len(tools.tools) == 22
            assert {"parlayapi_get_odds", "parlayapi_get_pricing", "parlayapi_book_coverage"} <= names
            assert any(str(resource.uri) == "parlayapi://docs/quickstart" for resource in resources.resources)
            print("Container passed initialize, 22 tools and quickstart resource discovery.")
            print("Network disabled. No key supplied. Zero tools called.")


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(check(), timeout=30))
