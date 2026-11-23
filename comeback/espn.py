"""Thin client for ESPN's public scoreboard and game summary feeds."""

import json
import time
import urllib.request

BASE = "https://site.api.espn.com/apis/site/v2/sports"


def _get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "comeback-app"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def scoreboard(league, date=None):
    """Games for a league on a date (YYYYMMDD). No date means today's slate."""
    url = f"{BASE}/{league.path}/scoreboard?"
    if date:
        url += f"dates={date}"
    return _get(url + league.scoreboard_params).get("events", [])


def summary(league, event_id):
    return _get(f"{BASE}/{league.path}/summary?event={event_id}")
