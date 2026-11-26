"""Check one sport on ParlayAPI's public board through the installed MCP server."""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


TOOL = "parlayapi_live_sports"


def board_rows(response):
    if response.get("isError"):
        raise ValueError("The public board tool returned an error. Try again later.")

    structured = response.get("structuredContent")
    if structured is not None:
        rows = structured.get("result") if isinstance(structured, dict) else None
    else:
        # Older MCP clients expose the list as JSON text blocks.
        blocks = response.get("content")
        if not isinstance(blocks, list) or not blocks:
            raise ValueError("The tool returned no readable board data.")
        values = []
        for block in blocks:
            if not isinstance(block, dict) or block.get("type") != "text" or not isinstance(block.get("text"), str):
                raise ValueError("The tool returned an unexpected content type.")
            values.append(json.loads(block["text"]))
        rows = values[0] if len(values) == 1 and isinstance(values[0], list) else values

    if not isinstance(rows, list) or any(
        not isinstance(row, dict) or not isinstance(row.get("key"), str) for row in rows
    ):
        raise ValueError("The public board response has an unexpected shape.")
    return rows


def board_observation(rows, sport_key):
    matches = [row for row in rows if row["key"] == sport_key]
    if not matches:
        return {"status": "not_listed", "event_count": None}
    if len(matches) > 1:
        raise ValueError("The board returned multiple rows for this sport key.")
    count = matches[0].get("event_count")
    if type(count) is not int or count < 0:
        return {"status": "count_unknown", "event_count": None}
    return {"status": "listed", "event_count": count}


async def check(sport_key):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-I", "-m", "parlayapi_mcp"],
        env={
            "PARLAYAPI_BASE_URL": "https://parlay-api.com",
            "PARLAYAPI_KEY": "",
            "PARLAY_API_KEY": "",
        },
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            result = await client.call_tool(TOOL, {})
            received_at = datetime.now(timezone.utc).isoformat()
    rows = board_rows(result.model_dump(mode="json", by_alias=True))
    return {
        "sport_key": sport_key,
        **board_observation(rows, sport_key),
        "source_tool": TOOL,
        "received_at_utc": received_at,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sport_key", help="Exact sport key, for example basketball_nba")
    args = parser.parse_args()
    try:
        print(json.dumps(asyncio.run(check(args.sport_key)), indent=2))
    except ValueError as error:
        parser.exit(1, f"{error}\n")
