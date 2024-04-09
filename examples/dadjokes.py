#!/usr/bin/env python3

"""Dad Jokes from Fatherhood.gov (https://fatherhood.gov/for-dads/dad-jokes)"""

import argparse
import logging
import random
import time
from typing import List
from typing import NamedTuple
from typing import Set

import httpx

import vesta


class Joke(NamedTuple):
    opener: str
    response: str


def fetch_jokes(limit) -> List[Joke]:
    jokes: Set[Joke] = set()

    next_url = "https://fatherhood.gov/jsonapi/node/dad_jokes"
    while next_url and len(jokes) < limit:
        logging.info("Fetching %s", next_url)
        resp = httpx.get(next_url)
        resp.raise_for_status()
        payload = resp.json()

        data = payload.get("data", [])
        if not data:
            break

        jokes.update(
            Joke(
                opener=joke["attributes"]["field_joke_opener"],
                response=joke["attributes"]["field_joke_response"],
            )
            for joke in data
        )
        next_url = payload.get("links", {}).get("next", {}).get("href")

    if len(jokes) < 2:
        raise RuntimeError("Failed to load enough jokes (%d)", len(jokes))

    return list(jokes)[:limit]


def main(args: argparse.Namespace):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
    )

    client = vesta.SubscriptionClient(args.key, args.secret)

    jokes = fetch_jokes(args.count)
    logging.info("Loaded %d jokes", len(jokes))

    joke = random.choice(jokes)
    last = None

    while True:
        while joke == last:
            joke = random.choice(jokes)

        try:
            chars = vesta.encode_text(
                f"{joke.opener}\n\n{joke.response}",
                valign="middle",
            )
        except ValueError:
            # Skip jokes that result in too many characters when encoded.
            continue

        logging.info("%s", joke)
        if args.pprint:
            vesta.pprint(chars)

        try:
            client.send_message(args.sub, chars)
        except httpx.HTTPStatusError as e:
            logging.error(e)
            time.sleep(60)
            continue

        last = joke
        time.sleep(args.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--key", required=True, help="API key")
    parser.add_argument("--secret", required=True, help="API secret")
    parser.add_argument("--sub", required=True, help="subscription ID")
    parser.add_argument("--pprint", action="store_true", help="print the board")
    parser.add_argument(
        "--count", type=int, default=100, help="number of jokes to fetch"
    )
    parser.add_argument(
        "--interval", type=int, default=10 * 60, help="update interval in seconds"
    )

    args = parser.parse_args()
    main(args)
