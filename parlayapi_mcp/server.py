"""ParlayAPI MCP server.

Run as: parlayapi-mcp
Or:     python -m parlayapi_mcp

Configures Claude Desktop / Cursor / any MCP client to call ParlayAPI's
endpoints natively. The signup tool requires no API key (it creates one
for the user). Data tools require a key, set via the PARLAYAPI_KEY env
var or the PARLAY_API_KEY alias in your MCP client config.

Example Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json):

    {
      "mcpServers": {
        "parlayapi": {
          "command": "uvx",
          "args": ["parlayapi-mcp"],
          "env": {"PARLAYAPI_KEY": "your_key_here"}
        }
      }
    }

Or after `pip install parlayapi-mcp`:

    {
      "mcpServers": {
        "parlayapi": {
          "command": "parlayapi-mcp",
          "env": {"PARLAYAPI_KEY": "your_key_here"}
        }
      }
    }
"""
from __future__ import annotations

import os
import sys
from typing import Any

import httpx

try:  # mcp SDK >= 2.0 renamed FastMCP to MCPServer and moved it
    from mcp.server.mcpserver import MCPServer as _ServerClass
except ImportError:  # mcp SDK 1.x
    from mcp.server.fastmcp import FastMCP as _ServerClass

try:
    from . import __version__ as _VERSION
except Exception:  # running as a loose script, not the installed package
    _VERSION = "0.3.0"


BASE_URL = os.environ.get("PARLAYAPI_BASE_URL", "https://parlay-api.com").rstrip("/")
API_KEY = (
    os.environ.get("PARLAYAPI_KEY")
    or os.environ.get("PARLAY_API_KEY")
    or ""
).strip()


mcp = _ServerClass("parlayapi")


def _client(needs_key: bool = True) -> httpx.Client:
    headers = {"User-Agent": f"parlayapi-mcp/{_VERSION}"}
    if needs_key:
        if not API_KEY:
            raise RuntimeError(
                "PARLAYAPI_KEY environment variable is not set. "
                "PARLAY_API_KEY is also accepted. "
                "Either set it in your MCP server config, or call "
                "parlayapi_signup() to create a free-tier key."
            )
        headers["X-API-KEY"] = API_KEY
    return httpx.Client(base_url=BASE_URL, headers=headers, timeout=20.0)


# ── Signup / billing ──────────────────────────────────────────────────


@mcp.tool()
def parlayapi_signup(
    email: str,
    intended_use: str = "",
    agent_id: str = "mcp-client",
) -> dict[str, Any]:
    """Create a free-tier ParlayAPI account for the given email.

    Returns the API key, a magic-login URL the user can click to access
    their dashboard, and a Stripe upgrade URL. Idempotent: if the email
    already has an account, returns exists=true with the login URL only
    (the existing API key is intentionally NOT exposed for security).

    Use this when a user wants to start building with ParlayAPI and
    does not have a key yet. After signup, ask the user to add the
    returned api_key to their MCP server config under PARLAYAPI_KEY,
    then restart the MCP client to pick it up.

    Args:
        email: User's email address.
        intended_use: Optional one-line description of what they're
            building. Used for analytics.
        agent_id: Identifier for the agent making the call. Defaults
            to "mcp-client".
    """
    with _client(needs_key=False) as c:
        r = c.post(
            "/v1/agent/signup",
            json={"email": email, "intended_use": intended_use, "agent_id": agent_id},
        )
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_checkout_link(email: str, tier: str = "pro") -> dict[str, Any]:
    """Generate a Stripe Checkout URL the user can click to upgrade.

    Tiers: starter ($5), pro ($20), business ($40), enterprise ($100),
    scale ($200). All are monthly subscriptions.
    """
    with _client(needs_key=False) as c:
        r = c.post("/v1/agent/checkout-link", json={"email": email, "tier": tier})
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_magic_link(email: str) -> dict[str, Any]:
    """Email a magic-login link for an existing ParlayAPI account.

    Always returns ok=true regardless of whether the email exists, to
    prevent account enumeration. The user receives the link by email.
    """
    with _client(needs_key=False) as c:
        r = c.post("/v1/agent/magic-link", json={"email": email})
        r.raise_for_status()
        return r.json()


# ── Sports / odds data ────────────────────────────────────────────────


@mcp.tool()
def parlayapi_get_pricing() -> dict[str, Any]:
    """Return the current public pricing table.

    No API key required. Use this when an agent needs to explain which
    tier unlocks a workflow before sending a checkout link.
    """
    with _client(needs_key=False) as c:
        r = c.get("/v1/pricing")
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_live_sports() -> list[dict[str, Any]]:
    """List currently active live sports on the retail /live surface.

    No API key required. Returns sport keys plus live event and book
    counts so agents can discover what is active right now.
    """
    with _client(needs_key=False) as c:
        r = c.get("/live/api/sports")
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_live_search(q: str, limit: int = 25) -> dict[str, Any]:
    """Search live teams, players, and sport keys.

    No API key required. Useful when the user asks for a team, player,
    or league by natural-language name and the agent needs the exact
    sport_key to call next.
    """
    safe_limit = max(1, min(int(limit), 100))
    with _client(needs_key=False) as c:
        r = c.get("/live/api/search", params={"q": q, "limit": safe_limit})
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_live_command_center(
    sport_key: str = "",
    limit: int = 12,
) -> dict[str, Any]:
    """Return the public best-line command center payload.

    No API key required. Shows current games, participating books, and
    best available real prices on the /live dashboard preview. This is
    a discovery and demo surface, not a substitute for the paid odds
    endpoints.
    """
    params: dict[str, Any] = {"limit": max(1, min(int(limit), 50))}
    if sport_key:
        params["sport"] = sport_key
    with _client(needs_key=False) as c:
        r = c.get("/live/api/command_center", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_source_quality(minutes: int = 10, limit: int = 40) -> dict[str, Any]:
    """Return public per-source freshness and quality metadata.

    No API key required. Use this to prove that rows are flowing from
    each source before choosing books for a customer workflow.
    """
    params = {
        "minutes": max(1, min(int(minutes), 1440)),
        "limit": max(1, min(int(limit), 200)),
    }
    with _client(needs_key=False) as c:
        r = c.get("/v1/meta/source-quality", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_book_coverage(
    window_minutes: int = 15,
    include_warn: bool = True,
) -> dict[str, Any]:
    """Return public per-book coverage gates.

    No API key required. This is the proof surface for whether each
    source survives freshness, normalization, database, REST-shape, and
    stream-shape checks.
    """
    params = {
        "window_minutes": max(5, min(int(window_minutes), 1440)),
        "include_warn": "true" if include_warn else "false",
    }
    with _client(needs_key=False) as c:
        r = c.get("/v1/meta/book-coverage", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_list_sports(active_only: bool = True) -> list[dict[str, Any]]:
    """List available sport keys. Use these in subsequent calls.

    Examples: baseball_mlb, basketball_nba, americanfootball_nfl,
    icehockey_nhl, soccer_epl, mma_ufc, esports_lol, table_tennis_*.
    """
    with _client() as c:
        params = {"all": "true"} if not active_only else {}
        r = c.get("/v1/sports", params=params)
        r.raise_for_status()
        return {"sports": r.json()}


@mcp.tool()
def parlayapi_get_odds(
    sport_key: str,
    markets: str = "h2h",
    regions: str = "us",
    bookmakers: str = "",
    odds_format: str = "decimal",
) -> dict[str, Any]:
    """Get game-level odds for a sport from all configured bookmakers.

    Args:
        sport_key: e.g. "baseball_mlb", "soccer_epl"
        markets: Comma-separated. h2h, spreads, totals.
        regions: us, us2, uk, eu, fr, au, ca, mx, latam, br, asia. Comma-separated for multiple.
        bookmakers: Comma-separated bookmaker keys (optional).
            Examples: pinnacle, draftkings, fanduel, bovada, caesars.
        odds_format: decimal | american
    """
    with _client() as c:
        params = {
            "markets": markets,
            "regions": regions,
            "oddsFormat": odds_format,
        }
        if bookmakers:
            params["bookmakers"] = bookmakers
        r = c.get(f"/v1/sports/{sport_key}/odds", params=params)
        r.raise_for_status()
        return {"events": r.json()}


@mcp.tool()
def parlayapi_get_props(
    sport_key: str,
    markets: str = "",
    bookmakers: str = "",
    player: str = "",
    include_futures: bool = False,
) -> dict[str, Any]:
    """Get player prop odds for a sport.

    Args:
        sport_key: e.g. "baseball_mlb", "basketball_nba"
        markets: Comma-separated prop market keys (optional).
            Examples: player_points, player_rebounds, player_strikeouts,
            player_passing_yards, player_total_bases.
        bookmakers: Comma-separated. Examples: prizepicks, underdog,
            sleeper, draftkings, fanduel.
        player: Filter to props mentioning this player name.
        include_futures: Include season-long futures (default False).
    """
    with _client() as c:
        params: dict[str, Any] = {}
        if markets:
            params["markets"] = markets
        if bookmakers:
            params["bookmakers"] = bookmakers
        if player:
            params["player"] = player
        if include_futures:
            params["include_futures"] = "true"
        r = c.get(f"/v1/sports/{sport_key}/odds/props", params=params)
        r.raise_for_status()
        return {"props": r.json()}


@mcp.tool()
def parlayapi_best_line(
    sport_key: str,
    market: str = "h2h",
    bookmakers: str = "",
) -> dict[str, Any]:
    """Find the best (highest) price for each outcome across bookmakers.

    Useful for line-shopping bots. Returns one row per game / market /
    side with the bookmaker offering the best price.

    Args:
        sport_key: e.g. "baseball_mlb"
        market: h2h | spreads | totals
        bookmakers: Restrict the search to these books (optional).
    """
    with _client() as c:
        params = {"markets": market, "regions": "us", "oddsFormat": "decimal"}
        if bookmakers:
            params["bookmakers"] = bookmakers
        r = c.get(f"/v1/sports/{sport_key}/odds", params=params)
        r.raise_for_status()
        events = r.json()

    # Compute best per (event_id, outcome_name)
    best: list[dict[str, Any]] = []
    for ev in events:
        market_best: dict[str, dict[str, Any]] = {}
        for bk in ev.get("bookmakers", []):
            for m in bk.get("markets", []):
                if m.get("key") != market:
                    continue
                for outcome in m.get("outcomes", []):
                    name = outcome.get("name", "")
                    price = outcome.get("price")
                    if price is None:
                        continue
                    cur = market_best.get(name)
                    if cur is None or price > cur["price"]:
                        market_best[name] = {
                            "name": name,
                            "price": price,
                            "point": outcome.get("point"),
                            "bookmaker": bk.get("key"),
                            "last_update": bk.get("last_update"),
                        }
        if market_best:
            best.append({
                "event_id": ev.get("id"),
                "home_team": ev.get("home_team"),
                "away_team": ev.get("away_team"),
                "commence_time": ev.get("commence_time"),
                "best_per_outcome": list(market_best.values()),
            })
    return {"events": best}


@mcp.tool()
def parlayapi_verdict(
    sport: str,
    side: str,
    market: str = "h2h",
    home: str = "",
    away: str = "",
    team: str = "",
    player: str = "",
    line: float | None = None,
    book: str = "",
    price: str = "",
    region: str = "",
    books: str = "",
    bankroll: float | None = None,
    kelly: float = 0.5,
) -> dict[str, Any]:
    """Should I bet this? One-call verdict for a specific bet.

    Returns the no-vig fair price for the exact bet, the best available price
    and which book has it, how the user's price (if given) grades as EV, a
    line-shopping nudge, and a plain-English call: BET / LEAN / FAIR / PASS
    (or NO_DATA). Use this when a user asks whether a specific bet is worth
    making, or whether they're getting a good number, instead of stitching
    /ev + /consensus + /best-line yourself.

    The best-price / shop recommendation is scoped to books the user can bet
    at (default US, so a US bettor is never told to use a euro book). Set it
    once with parlayapi_set_bettable_books and it is remembered per key, or
    pass region / books here per call.

    Args:
        sport: sport_key, e.g. "baseball_mlb".
        side: the team you'd bet (h2h / spreads), or "over" / "under" (totals / props).
        market: h2h | spreads | totals | a player-prop key (player_hits, player_points, ...).
        home, away: the two teams, to identify the game. Or pass `team` with one name.
        team: one team name to find the game (alternative to home + away).
        player: player name (required for player-prop markets).
        line: the number for spreads, totals, or props.
        book: the book you'd bet at (grades that book's current price).
        price: the price you're offered (American like -110, or decimal like 1.91).
            Overrides `book`, use it to grade a specific number in hand.
        region: where you can bet: us (default) | eu | uk | au | ca.
        books: exact CSV of books you can bet at (overrides region; use for
            state-level geo-blocks, e.g. "draftkings,fanduel,novig").
        bankroll: the user's bankroll; when the bet is +EV, returns a suggested
            Kelly stake amount ("bet it, ~$X").
        kelly: Kelly fraction (default 0.5 = half-Kelly, the bankroll-safe standard).

    The response also carries an `edge_alert` when a book shows a price far
    better than the market (a possible soft error worth grabbing, or a stale
    line to verify) that the normal best-price guard would otherwise hide.
    """
    params: dict[str, Any] = {"sport": sport, "market": market, "side": side}
    for k, v in (("home", home), ("away", away), ("team", team),
                 ("player", player), ("book", book), ("price", price),
                 ("region", region), ("books", books)):
        if v:
            params[k] = v
    if line is not None:
        params["line"] = line
    if bankroll is not None:
        params["bankroll"] = bankroll
        params["kelly"] = kelly
    with _client() as c:
        r = c.get("/v1/verdict", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_set_bettable_books(region: str = "", books: str = "") -> dict[str, Any]:
    """Remember which books the user can bet at, so parlayapi_verdict scopes its
    best-price and shop recommendations to them automatically (no need to pass
    region/books every call).

    Call this once when a user tells you where they bet ("I'm in the US on
    DraftKings and FanDuel"). Pass region OR an exact books list.

    Args:
        region: us | eu | uk | au | ca.
        books: exact CSV of book keys, e.g. "draftkings,fanduel,novig". Overrides region.
    """
    params: dict[str, Any] = {}
    if region:
        params["region"] = region
    if books:
        params["books"] = books
    with _client() as c:
        r = c.post("/v1/verdict/prefs", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_parlay_verdict(
    legs: list[dict],
    region: str = "",
    books: str = "",
    stake: float | None = None,
    book: str = "",
    bankroll: float | None = None,
    kelly: float = 0.5,
) -> dict[str, Any]:
    """Grade a multi-leg parlay: should you bet it, and at which book?

    Give 2 to 12 legs (each shaped like a parlayapi_verdict bet) and get the
    combined no-vig fair price, the single best BOOK to place the whole slip at
    (a real parlay is one slip, not best-of-each), the parlay's EV, the weakest
    leg, same-game correlation warnings, and (with stake) the payout. Best-price
    is scoped to books the user can bet at (set once via
    parlayapi_set_bettable_books, or pass region/books here).

    Args:
        legs: list of leg objects, e.g.
            [{"sport": "baseball_mlb", "home": "Detroit Tigers",
              "away": "Kansas City Royals", "market": "h2h", "side": "Detroit Tigers"},
             {"sport": "baseball_mlb", "team": "Detroit Tigers",
              "market": "totals", "side": "over", "line": 8.5}]
            Each leg: sport, market (h2h/spreads/totals or a player-prop key),
            side (team, or over/under), home+away or team, player (for props), line.
        region: us (default) | eu | uk | au | ca.
        books: exact CSV of books you can bet at (overrides region).
        stake: optional stake amount, to compute the payout if it hits.
        book: optional, also report the parlay price at this specific book.
    """
    body: dict[str, Any] = {"legs": legs}
    if region:
        body["region"] = region
    if books:
        body["books"] = books
    if stake is not None:
        body["stake"] = stake
    if book:
        body["book"] = book
    if bankroll is not None:
        body["bankroll"] = bankroll
        body["kelly"] = kelly
    with _client() as c:
        r = c.post("/v1/parlay/verdict", json=body)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_best_bets(
    sport_key: str,
    region: str = "",
    books: str = "",
    limit: int = 20,
    min_edge: float = 2.0,
) -> dict[str, Any]:
    """What should I bet right now? Ranked +EV plays for a sport.

    The discovery counterpart to parlayapi_verdict: scans the whole board,
    grades every candidate with the same no-vig engine, keeps only bets that
    are +EV at a book the user can bet at, and ranks them by edge. Also returns
    edge_alerts (books showing a price far off the market). Player props only,
    priced by several books, prediction markets and game moneylines excluded
    (for a game line, use parlayapi_verdict). Scoped to the user's books.

    Args:
        sport_key: e.g. "baseball_mlb".
        region: us (default) | eu | uk | au | ca.
        books: exact CSV of books you can bet at (overrides region).
        limit: max plays to return (default 20).
        min_edge: minimum edge %% vs the no-vig fair line (default 2.0).
    """
    params: dict[str, Any] = {"limit": limit, "min_edge": min_edge}
    if region:
        params["region"] = region
    if books:
        params["books"] = books
    with _client() as c:
        r = c.get(f"/v1/sports/{sport_key}/best-bets", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def parlayapi_account_info() -> dict[str, Any]:
    """Get info about the API key currently in use: tier, credits
    remaining, billing period.
    """
    with _client() as c:
        r = c.get("/v1/account")
        r.raise_for_status()
        return r.json()


# ── Value-hunting tools (the reason sharp bettors + agents use us) ─────


@mcp.tool()
def parlayapi_find_arbitrage(
    sport_key: str,
    min_profit: float = 0.0,
    exclude_exchanges: bool = False,
    markets: str = "",
) -> dict[str, Any]:
    """Find guaranteed-profit arbitrage opportunities across bookmakers.

    Scans every event and returns bets where the combined implied
    probability across the books is under 100%, so betting each side locks
    in profit regardless of outcome. Soccer and other 3-way (home/draw/away)
    markets are fully supported, including arbs anchored on the draw.

    Args:
        sport_key: e.g. "baseball_mlb", "soccer_epl".
        min_profit: Minimum profit % to include (e.g. 1.5 for 1.5%). Default 0.
        exclude_exchanges: Drop arbs anchored on an exchange (novig/prophetx),
            whose asks can be no-volume. Default False.
        markets: Comma-separated market_keys to limit the scan (optional),
            e.g. "h2h,spreads,totals".
    """
    with _client() as c:
        params: dict[str, Any] = {"minProfit": min_profit}
        if exclude_exchanges:
            params["exclude_exchanges"] = "true"
        if markets:
            params["markets"] = markets
        r = c.get(f"/v1/sports/{sport_key}/arbitrage", params=params)
        r.raise_for_status()
        return {"arbitrage": r.json()}


@mcp.tool()
def parlayapi_find_ev(
    sport_key: str,
    sharp_book: str = "pinnacle",
    min_edge: float = 2.0,
    markets: str = "",
) -> dict[str, Any]:
    """Find positive-EV bets vs a sharp book's no-vig fair line.

    Compares every soft book's price against the no-vig fair probability
    derived from a sharp book (default Pinnacle); rows where a soft book
    offers better odds than the sharp fair price are +EV. Three-way soccer
    markets use a dedicated no-vig pass over home/draw/away, so +EV on the
    draw surfaces too.

    Args:
        sport_key: e.g. "baseball_mlb", "soccer_epl".
        sharp_book: Sharp baseline book. Default "pinnacle".
        min_edge: Minimum edge % to include (e.g. 3 for 3%). Default 2.
        markets: Comma-separated market_keys (optional).
    """
    with _client() as c:
        params: dict[str, Any] = {"sharpBook": sharp_book, "minEdge": min_edge}
        if markets:
            params["markets"] = markets
        r = c.get(f"/v1/sports/{sport_key}/ev", params=params)
        r.raise_for_status()
        return {"ev": r.json()}


@mcp.tool()
def parlayapi_consensus(
    sport_key: str,
    markets: str = "",
) -> dict[str, Any]:
    """Get consensus (average) odds across all bookmakers per market.

    Returns average, best, and worst price per (event, market, player,
    line), a sharp baseline for line-shopping. Soccer and other 3-way
    markets return separate home, draw, and away consensus rows.

    Args:
        sport_key: e.g. "baseball_mlb", "soccer_epl".
        markets: Comma-separated market_keys (optional), e.g. "moneyline,totals".
    """
    with _client() as c:
        params: dict[str, Any] = {}
        if markets:
            params["markets"] = markets
        r = c.get(f"/v1/sports/{sport_key}/consensus", params=params)
        r.raise_for_status()
        return {"consensus": r.json()}


@mcp.tool()
def parlayapi_find_middles(
    sport_key: str,
    min_gap: float = 1.0,
    markets: str = "",
    include_props: bool = True,
) -> dict[str, Any]:
    """Find cross-book middle opportunities.

    A middle takes the Over at a low line on one book and the Under at a
    higher line on another, so a window of whole numbers cashes BOTH bets
    (e.g. Over 7.5 at one book, Under 9.5 at another means 8 or 9 wins both).
    Scans game totals, spreads, AND player-total props (points, rebounds,
    strikeouts, ...). Each result carries the window, the numbers that hit,
    and per-$100 economics: profit_if_hit and net_if_above/below_window.

    Args:
        sport_key: e.g. "baseball_mlb", "basketball_nba".
        min_gap: Minimum window width in points/runs/goals. Default 1.0.
        markets: Comma-separated market_keys to limit the scan (optional),
            e.g. "totals" or "player_points".
        include_props: Include player-total props alongside game lines. Default True.
    """
    with _client() as c:
        params: dict[str, Any] = {
            "min_gap": min_gap,
            "include_props": "true" if include_props else "false",
        }
        if markets:
            params["markets"] = markets
        r = c.get(f"/v1/sports/{sport_key}/middles", params=params)
        r.raise_for_status()
        return {"middles": r.json()}


# ── Resources (read-only, large, cached) ──────────────────────────────


@mcp.resource("parlayapi://docs/quickstart")
def docs_quickstart() -> str:
    """Quickstart code samples for ParlayAPI in Python and JS."""
    return """# ParlayAPI quickstart

## Python
```python
import requests
r = requests.get(
    "https://parlay-api.com/v1/sports/baseball_mlb/odds",
    params={"markets": "h2h", "regions": "us"},
    headers={"X-API-KEY": "YOUR_KEY"},
)
print(r.json())
```

## JS / Node
```js
const r = await fetch(
  "https://parlay-api.com/v1/sports/baseball_mlb/odds?markets=h2h&regions=us",
  { headers: { "X-API-KEY": "YOUR_KEY" } }
);
const events = await r.json();
console.log(events);
```
"""


# ── Entry point ───────────────────────────────────────────────────────


def main():
    """Console-script entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
