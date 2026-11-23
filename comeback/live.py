"""Live check: alert when a team that trailed big has pulled close or taken the lead.

Usage: python -m comeback.live
Sends a push notification through ntfy.sh when NTFY_TOPIC is set.
"""

import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import espn
from .detect import live_comeback, parse_game
from .leagues import LEAGUES

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "alerts" / "state.json"
LOG = ROOT / "alerts" / "log.csv"
KEEP_SECONDS = 3 * 24 * 3600


def describe(margin, unit):
    if margin > 0:
        return f"now leads by {margin}"
    if margin == 0:
        return "has tied it"
    return f"is within {-margin} {unit}"


def notify(title, message):
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data=message.encode(),
        headers={"Title": title, "Tags": "rotating_light"},
    )
    urllib.request.urlopen(req, timeout=20)


def main():
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    now = time.time()
    state = {k: v for k, v in state.items() if now - v < KEEP_SECONDS}
    new_alerts = []

    for league in LEAGUES:
        try:
            events = espn.scoreboard(league)
        except Exception as exc:
            print(f"{league.key}: {exc}", file=sys.stderr)
            continue
        for event in events:
            status = event["competitions"][0]["status"]
            if status["type"].get("state") != "in":
                continue
            try:
                game = parse_game(espn.summary(league, event["id"]))
            except Exception as exc:
                print(f"{league.key} {event['id']}: {exc}", file=sys.stderr)
                continue
            result = live_comeback(game, league)
            if not result:
                continue
            team, deficit, margin = result
            key = f"{league.key}:{game.event_id}:{team.id}"
            if key in state:
                continue
            other = game.away if team is game.home else game.home
            title = f"Comeback alert: {team.name}"
            message = (f"{league.name}: {team.name} trailed {other.name} by {deficit} {league.unit} "
                       f"and {describe(margin, league.unit)}. {status['type'].get('shortDetail', '')}")
            print(message)
            try:
                notify(title, message)
            except Exception as exc:
                print(f"notify failed: {exc}", file=sys.stderr)
            state[key] = now
            new_alerts.append([datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               league.key, game.event_id, team.name, other.name, deficit, margin])

    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
    if new_alerts:
        write_header = not LOG.exists()
        with LOG.open("a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["time_utc", "league", "event_id", "team", "opponent", "deficit", "margin"])
            writer.writerows(new_alerts)
    print(f"{len(new_alerts)} new alert(s)")


if __name__ == "__main__":
    main()
