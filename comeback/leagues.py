"""Leagues Comeback watches and what counts as a comeback in each."""

from dataclasses import dataclass


@dataclass(frozen=True)
class League:
    key: str
    name: str
    path: str  # ESPN sport/league path
    unit: str  # points, goals, runs
    threshold: int  # deficit a winner must erase to count as a comeback
    alert_margin: int  # live alert fires when a team that trailed by threshold is within this
    scoreboard_params: str = ""


LEAGUES = [
    League("nfl", "NFL", "football/nfl", "points", 14, 3),
    League("nba", "NBA", "basketball/nba", "points", 18, 3),
    League("mlb", "MLB", "baseball/mlb", "runs", 4, 1),
    League("nhl", "NHL", "hockey/nhl", "goals", 3, 0),
    League("mls", "MLS", "soccer/usa.1", "goals", 2, 0),
    League("ncaaf", "College Football", "football/college-football", "points", 17, 3,
           "&groups=80&limit=300"),
    League("ncaam", "Men's College Basketball", "basketball/mens-college-basketball", "points", 15, 3,
           "&groups=50&limit=500"),
]

BY_KEY = {league.key: league for league in LEAGUES}
