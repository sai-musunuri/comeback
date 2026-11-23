"""Turn a game summary into a score timeline and measure comebacks."""

from dataclasses import dataclass


@dataclass
class Team:
    id: str
    abbr: str
    name: str
    score: int
    winner: bool


@dataclass
class Game:
    event_id: str
    home: Team
    away: Team
    timeline: list  # [(home_score, away_score), ...] starting at (0, 0)


def _team(c):
    t = c.get("team", {})
    return Team(
        id=str(t.get("id", "")),
        abbr=t.get("abbreviation", ""),
        name=t.get("displayName") or t.get("location", ""),
        score=int(float(c.get("score") or 0)),
        winner=bool(c.get("winner")),
    )


def _scored(plays):
    out = []
    for p in plays:
        h, a = p.get("homeScore"), p.get("awayScore")
        if h is not None and a is not None:
            out.append((int(h), int(a)))
    return out


def _from_goals(key_events, home_id):
    h = a = 0
    out = []
    for e in key_events:
        if not e.get("scoringPlay"):
            continue
        if str(e.get("team", {}).get("id")) == home_id:
            h += 1
        else:
            a += 1
        out.append((h, a))
    return out


def _from_linescores(header_competitors):
    home = next(c for c in header_competitors if c.get("homeAway") == "home")
    away = next(c for c in header_competitors if c.get("homeAway") == "away")
    h = a = 0
    out = []
    for hl, al in zip(home.get("linescores", []), away.get("linescores", [])):
        h += int(float(hl.get("displayValue") or hl.get("value") or 0))
        a += int(float(al.get("displayValue") or al.get("value") or 0))
        out.append((h, a))
    return out


def parse_game(summary):
    comp = summary["header"]["competitions"][0]
    competitors = comp["competitors"]
    home = _team(next(c for c in competitors if c.get("homeAway") == "home"))
    away = _team(next(c for c in competitors if c.get("homeAway") == "away"))

    timeline = _scored(summary.get("plays") or []) or _scored(summary.get("scoringPlays") or [])
    if not timeline and summary.get("keyEvents"):
        timeline = _from_goals(summary["keyEvents"], home.id)
    if not timeline:
        timeline = _from_linescores(competitors)

    return Game(summary["header"]["id"], home, away, [(0, 0)] + timeline)


def max_deficit(timeline, side):
    """Largest deficit the home or away side faced at any point."""
    sign = 1 if side == "home" else -1
    return max(0, max(-sign * (h - a) for h, a in timeline))


def final_comeback(game, league):
    """The winner and the deficit they erased, if it meets the league threshold."""
    for side, team in (("home", game.home), ("away", game.away)):
        if team.winner:
            deficit = max_deficit(game.timeline, side)
            if deficit >= league.threshold:
                return team, deficit
    return None


def live_comeback(game, league):
    """A team that trailed by the threshold and is now within the alert margin."""
    h, a = game.timeline[-1]
    for side, team, margin in (("home", game.home, h - a), ("away", game.away, a - h)):
        deficit = max_deficit(game.timeline, side)
        if deficit >= league.threshold and margin >= -league.alert_margin:
            return team, deficit, margin
    return None
