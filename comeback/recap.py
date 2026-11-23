"""Daily recap: find yesterday's completed comebacks and record them.

Usage: python -m comeback.recap [YYYY-MM-DD]
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from . import espn
from .detect import final_comeback, parse_game
from .leagues import BY_KEY, LEAGUES

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "comebacks.csv"
RECAPS = ROOT / "recaps"
README = ROOT / "README.md"
FIELDS = ["date", "league", "event_id", "winner", "loser", "deficit", "unit", "final"]


def find_comebacks(league, date):
    """Return (games_checked, comeback_rows) for one league on one date."""
    events = espn.scoreboard(league, date.replace("-", ""))
    finals = [e for e in events if e["competitions"][0]["status"]["type"].get("completed")]
    rows = []
    for event in finals:
        game = parse_game(espn.summary(league, event["id"]))
        result = final_comeback(game, league)
        if not result:
            continue
        winner, deficit = result
        loser = game.away if winner is game.home else game.home
        rows.append({
            "date": date,
            "league": league.key,
            "event_id": game.event_id,
            "winner": winner.name,
            "loser": loser.name,
            "deficit": deficit,
            "unit": league.unit,
            "final": f"{winner.abbr} {winner.score}, {loser.abbr} {loser.score}",
        })
    return len(finals), rows


def write_recap(date, results):
    lines = [f"# Comebacks for {date}", ""]
    all_rows = [r for _, _, rows in results if rows for r in rows]
    lines.append(f"{len(all_rows)} comeback(s) found." if all_rows else "No comebacks today.")
    lines += ["", "| League | Games checked | Comebacks |", "|---|---|---|"]
    for league, checked, rows in results:
        shown = "feed unavailable" if checked is None else str(checked)
        lines.append(f"| {league.name} | {shown} | {len(rows or [])} |")
    for r in all_rows:
        league = BY_KEY[r["league"]]
        lines += ["", f"**{league.name}:** {r['winner']} came back from {r['deficit']} {r['unit']} down "
                      f"to beat {r['loser']}, {r['final']}."]
    RECAPS.mkdir(exist_ok=True)
    (RECAPS / f"{date}.md").write_text("\n".join(lines) + "\n")


def append_rows(rows):
    DATA.parent.mkdir(exist_ok=True)
    existing = []
    if DATA.exists():
        with DATA.open() as f:
            existing = list(csv.DictReader(f))
    seen = {(r["league"], r["event_id"]) for r in existing}
    merged = existing + [r for r in rows if (r["league"], str(r["event_id"])) not in seen]
    merged.sort(key=lambda r: (r["date"], r["league"], str(r["event_id"])))
    with DATA.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(merged)
    return merged


def update_readme(date, all_rows):
    start, end = "<!-- recent:start -->", "<!-- recent:end -->"
    recent = sorted(all_rows, key=lambda r: r["date"], reverse=True)[:15]
    block = [start, f"Latest recap: [{date}](recaps/{date}.md)", ""]
    if recent:
        block += ["| Date | League | Winner | Deficit erased | Final |", "|---|---|---|---|---|"]
        for r in recent:
            block.append(f"| {r['date']} | {BY_KEY[r['league']].name} | {r['winner']} | "
                         f"{r['deficit']} {r['unit']} | {r['final']} |")
    else:
        block.append("No comebacks recorded yet.")
    block.append(end)
    text = README.read_text()
    head, rest = text.split(start, 1)
    tail = rest.split(end, 1)[1]
    README.write_text(head + "\n".join(block) + tail)


def main(argv):
    if len(argv) > 1:
        date = argv[1]
    else:
        date = (datetime.now(ZoneInfo("America/New_York")) - timedelta(days=1)).strftime("%Y-%m-%d")
    results = []
    for league in LEAGUES:
        try:
            checked, rows = find_comebacks(league, date)
        except Exception as exc:
            print(f"{league.key}: {exc}", file=sys.stderr)
            checked, rows = None, []
        results.append((league, checked, rows))
        print(f"{league.key}: {checked} finals, {len(rows)} comebacks")
    write_recap(date, results)
    merged = append_rows([r for _, _, rows in results for r in rows])
    update_readme(date, merged)


if __name__ == "__main__":
    main(sys.argv)
