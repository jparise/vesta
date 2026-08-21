#!/usr/bin/env python

"""Show live tennis scores on a Vestaboard.

Polls the Live Tennis API (https://livetennisapi.com) for matches that are
currently in play and writes up to two of them to the board, one three-row
block per match:

    CINCINNATI OPEN
    °ALCARAZ      2  4 40
     SINNER       1  3 30

(sets won, games in the current set, current point; ``°`` marks the server.)

An API key is required (free at https://livetennisapi.com/subscribe/free).
The free tier allows 100 requests/day, so the default 15-minute refresh
interval keeps a full day of updates within it. Vestaboards suit that slow
cadence well; this is a score line, not a fast ticker.

Disclosure: this example was contributed by the Live Tennis API team.
"""

import argparse
import json
import os
import time
import unicodedata
import urllib.parse
import urllib.request

import vesta

API_URL = "https://api.livetennisapi.com/api/public/v1/matches"

COLUMNS = 22


def asciify(s: str) -> str:
    """Reduce a string to ASCII by dropping accents (and any other
    characters the board's character set can't represent)."""
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def fetch_live_matches(api_key: str, limit: int = 2) -> list:
    """Fetch up to `limit` live matches from the Live Tennis API."""
    query = urllib.parse.urlencode({"status": "live", "limit": limit})
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"X-API-Key": api_key},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response).get("data", [])


def format_match(match: dict) -> list[str]:
    """Format a match as three board rows: tournament, player 1, player 2."""
    score = match.get("score") or {}
    sets = score.get("sets") or [0, 0]
    games = score.get("games") or [[], []]
    points = score.get("points") or [None, None]
    server = score.get("server")

    rows = [asciify(match.get("tournament", ""))[:COLUMNS]]
    for index in (0, 1):
        player = match["players"]["p1" if index == 0 else "p2"]
        name = asciify(player.get("name") or "?")
        surname = name.split()[-1] if name.split() else "?"
        serving = "°" if server == index + 1 else " "
        current_games = games[index][-1] if games[index] else 0
        point = points[index] or ""
        row = f"{serving}{surname[:12]:<13}{sets[index]}{current_games:>3} {point}"
        rows.append(row[:COLUMNS])
    return rows


def compose_board(matches: list) -> str:
    """Compose up to two matches into a six-row board message."""
    if not matches:
        return "NO LIVE TENNIS\nRIGHT NOW"
    rows: list[str] = []
    for match in matches[:2]:
        rows.extend(format_match(match))
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cloud-key", metavar="KEY", help="Cloud API key")
    group.add_argument("--local-key", metavar="KEY", help="Local API key")
    parser.add_argument(
        "--tennis-key",
        metavar="KEY",
        default=os.environ.get("LIVETENNIS_API_KEY"),
        help="Live Tennis API key (defaults to $LIVETENNIS_API_KEY)",
    )
    parser.add_argument(
        "--interval",
        metavar="SECONDS",
        type=int,
        default=900,
        help="refresh interval; the default (900) fits the free tier's "
        "100 requests/day (default: %(default)s)",
    )

    args = parser.parse_args()
    if not args.tennis_key:
        parser.error("a Live Tennis API key is required (see --tennis-key)")

    client: vesta.CloudClient | vesta.LocalClient
    if args.cloud_key:
        client = vesta.CloudClient(args.cloud_key)
    else:
        client = vesta.LocalClient(args.local_key)

    while True:
        try:
            matches = fetch_live_matches(args.tennis_key)
        except Exception as e:
            print(f"Error fetching live matches: {e}")
        else:
            message = compose_board(matches)
            try:
                chars = vesta.encode_text(message, valign="middle")
                if client.write_message(chars):
                    vesta.pprint(chars)
                else:
                    print("Failed to write message")
            except Exception as e:
                print(f"Error writing message: {e}")

        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
