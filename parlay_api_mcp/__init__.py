"""ParlayAPI MCP server.

Exposes ParlayAPI's odds endpoints as MCP tools so Claude / Cursor /
Continue / Devin / Codex can fetch live sports betting odds, player
props, arbitrage opportunities, +EV bets, line movement, and prediction
market prices directly during a conversation.

Install:
    pip install parlay-api-mcp

Run with stdio transport (for Claude Code, Cursor, Continue, Devin):
    PARLAY_API_KEY=your_key python -m parlay_api_mcp

Or via the registered console-script:
    PARLAY_API_KEY=your_key parlay-api-mcp

Configure in Claude Code (~/.config/claude/mcp_settings.json):

    {
      "mcpServers": {
        "parlay-api": {
          "command": "parlay-api-mcp",
          "env": { "PARLAY_API_KEY": "your_key" }
        }
      }
    }

Configure in Cursor (~/.cursor/mcp.json) — same shape.

Get a free API key at https://parlay-api.com/signup. 1,000 requests/month
on the free tier. No credit card required.
"""
from __future__ import annotations

__version__ = "0.1.0"

import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


BASE_URL = os.environ.get("PARLAY_API_URL", "https://parlay-api.com")
API_KEY = os.environ.get("PARLAY_API_KEY", "")

mcp = FastMCP(
    name="parlay-api",
    instructions=(
        "ParlayAPI gives Claude/agents real-time access to sports betting "
        "odds across 21+ sportsbooks (DraftKings, FanDuel, BetMGM, Pinnacle, "
        "Bet365, Bovada, etc), DFS apps (PrizePicks, Underdog, Sleeper, "
        "Pick6), exchanges (Novig, ProphetX), and prediction markets "
        "(Kalshi, Polymarket). 38+ sports including NFL, NBA, MLB, NHL, "
        "soccer leagues, MMA, tennis, golf, esports.\n\n"
        "Use these tools when the user asks about odds, prop bets, "
        "arbitrage, +EV, line shopping, or prediction-market prices. "
        "Free-tier API key gets 1,000 requests/month at "
        "https://parlay-api.com/signup."
    ),
)


def _client() -> httpx.AsyncClient:
    if not API_KEY:
        raise RuntimeError(
            "PARLAY_API_KEY env var is required. Get a free key at "
            "https://parlay-api.com/signup"
        )
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"X-API-Key": API_KEY, "User-Agent": f"parlay-api-mcp/{__version__}"},
        timeout=20.0,
    )


@mcp.tool()
async def list_sports() -> dict[str, Any]:
    """List every sport and league ParlayAPI supports.

    Returns a list of sport_key strings (e.g. baseball_mlb, basketball_nba,
    soccer_epl, mma_ufc) plus human-readable titles.
    """
    async with _client() as c:
        r = await c.get("/v1/sports")
        return {"sports": r.json()}


@mcp.tool()
async def get_odds(
    sport_key: str,
    regions: str = "us",
    markets: str = "h2h",
    bookmakers: str | None = None,
    odds_format: str = "american",
) -> dict[str, Any]:
    """Get live odds for a sport.

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba, americanfootball_nfl,
                   icehockey_nhl, soccer_epl, mma_ufc.
        regions: comma-separated regions (us, us2, uk, eu, au).
        markets: comma-separated markets (h2h, spreads, totals).
        bookmakers: comma-separated book keys (draftkings, fanduel,
                    pinnacle, etc.). Overrides regions if provided.
        odds_format: 'american' or 'decimal'.
    """
    params: dict[str, Any] = {"regions": regions, "markets": markets, "oddsFormat": odds_format}
    if bookmakers:
        params["bookmakers"] = bookmakers
    async with _client() as c:
        r = await c.get(f"/v1/sports/{sport_key}/odds", params=params)
        r.raise_for_status()
        return {"events": r.json()[:20]}  # cap at 20 to keep responses scoped


@mcp.tool()
async def get_player_props(
    sport_key: str,
    market_key: str | None = None,
    player: str | None = None,
    bookmakers: str | None = None,
) -> dict[str, Any]:
    """Get player prop odds.

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba.
        market_key: e.g. batter_home_runs, player_points, player_rebounds.
                    Optional. If omitted, returns all available markets.
        player: filter to a specific player by name (case-insensitive).
        bookmakers: comma-separated bookmaker keys to limit response size.
    """
    params: dict[str, Any] = {}
    if market_key:
        params["markets"] = market_key
    if player:
        params["player"] = player
    if bookmakers:
        params["bookmakers"] = bookmakers
    async with _client() as c:
        r = await c.get(f"/v1/sports/{sport_key}/props", params=params)
        r.raise_for_status()
        return {"props": r.json()[:50]}


@mcp.tool()
async def find_arbitrage(
    sport_key: str,
    min_profit: float = 0.005,
) -> dict[str, Any]:
    """Find pre-computed cross-book arbitrage opportunities.

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba.
        min_profit: minimum profit percentage (e.g. 0.005 = 0.5%).
    """
    async with _client() as c:
        r = await c.get(
            f"/v1/sports/{sport_key}/arbitrage",
            params={"min_profit": min_profit},
        )
        r.raise_for_status()
        return {"arbs": r.json()}


@mcp.tool()
async def find_positive_ev(
    sport_key: str,
    min_edge: float = 0.02,
) -> dict[str, Any]:
    """Find pre-computed +EV bets vs the no-vig market consensus.

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba.
        min_edge: minimum edge percentage over no-vig fair price (e.g. 0.02 = 2%).
    """
    async with _client() as c:
        r = await c.get(
            f"/v1/sports/{sport_key}/ev",
            params={"min_edge": min_edge},
        )
        r.raise_for_status()
        return {"ev_bets": r.json()}


@mcp.tool()
async def compare_books(
    sport_key: str,
) -> dict[str, Any]:
    """Side-by-side line comparison across all sportsbooks for upcoming games.

    Returns each game with every book's price for h2h/spread/total, sorted
    best-to-worst per outcome. The fastest way to identify line-shopping
    value programmatically.

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba.
    """
    async with _client() as c:
        r = await c.get(f"/v1/sports/{sport_key}/compare")
        r.raise_for_status()
        return {"comparison": r.json()[:20]}


@mcp.tool()
async def get_prediction_market_prices(
    sport_key: str,
) -> dict[str, Any]:
    """Get Kalshi and Polymarket prediction-market prices for a sport,
    normalized to American/decimal odds the same shape as sportsbook odds.

    Use to find prediction-market vs sportsbook arb (one of the highest-edge
    plays available right now since Kalshi launched sports event contracts).

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba, americanfootball_nfl.
    """
    async with _client() as c:
        r = await c.get(f"/v1/prediction-markets/{sport_key}")
        r.raise_for_status()
        return {"prediction_markets": r.json()}


@mcp.tool()
async def get_historical_odds(
    sport_key: str,
    start_date: str,
    end_date: str,
    source: str | None = None,
) -> dict[str, Any]:
    """Pull historical odds for backtesting.

    Args:
        sport_key: e.g. baseball_mlb, basketball_nba, soccer_epl.
        start_date: YYYY-MM-DD.
        end_date: YYYY-MM-DD.
        source: optional source filter (pinnacle, draftkings_espn, bet365, etc).
                Use None to get all sources.
    """
    params: dict[str, Any] = {"start": start_date, "end": end_date}
    if source:
        params["source"] = source
    async with _client() as c:
        r = await c.get(f"/v1/historical/sports/{sport_key}/odds", params=params)
        r.raise_for_status()
        return {"historical": r.json()}


@mcp.tool()
async def get_archive_coverage() -> dict[str, Any]:
    """Get historical archive coverage stats: total rows, sports, sources,
    cross-source overlap. Use to verify the archive is rich enough for
    a planned backtest before committing.

    Public, no API key required.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as c:
        r = await c.get("/v1/historical/coverage")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def get_account_usage() -> dict[str, Any]:
    """Get the authenticated account's monthly usage and remaining credits."""
    async with _client() as c:
        r = await c.get("/v1/usage")
        r.raise_for_status()
        return r.json()


def main() -> None:
    """Console entry point. Runs the server over stdio transport."""
    if not API_KEY:
        print(
            "ERROR: PARLAY_API_KEY env var is required.\n"
            "Get a free API key at https://parlay-api.com/signup",
            file=sys.stderr,
        )
        sys.exit(1)
    mcp.run()


if __name__ == "__main__":
    main()
