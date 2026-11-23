import unittest

from comeback.detect import final_comeback, live_comeback, max_deficit, parse_game
from comeback.leagues import BY_KEY


def summary(home_score, away_score, plays=None, home_wins=True, **extra):
    return {
        "header": {"id": "1", "competitions": [{"competitors": [
            {"homeAway": "home", "score": str(home_score), "winner": home_wins,
             "team": {"id": "10", "abbreviation": "HOM", "displayName": "Home Team"}},
            {"homeAway": "away", "score": str(away_score), "winner": not home_wins,
             "team": {"id": "20", "abbreviation": "AWY", "displayName": "Away Team"}},
        ]}]},
        "plays": plays or [],
        **extra,
    }


def plays(*scores):
    return [{"homeScore": h, "awayScore": a} for h, a in scores]


class DetectTests(unittest.TestCase):
    def test_max_deficit_each_side(self):
        timeline = [(0, 0), (0, 20), (25, 22)]
        self.assertEqual(max_deficit(timeline, "home"), 20)
        self.assertEqual(max_deficit(timeline, "away"), 3)

    def test_final_comeback_meets_threshold(self):
        game = parse_game(summary(110, 105, plays((0, 10), (80, 100), (110, 105))))
        team, deficit = final_comeback(game, BY_KEY["nba"])
        self.assertEqual(team.abbr, "HOM")
        self.assertEqual(deficit, 20)

    def test_small_deficit_is_not_a_comeback(self):
        game = parse_game(summary(100, 98, plays((0, 5), (100, 98))))
        self.assertIsNone(final_comeback(game, BY_KEY["nba"]))

    def test_scoring_plays_used_for_football(self):
        s = summary(24, 21, scoringPlays=plays((0, 7), (0, 21), (24, 21)))
        team, deficit = final_comeback(parse_game(s), BY_KEY["nfl"])
        self.assertEqual((team.abbr, deficit), ("HOM", 21))

    def test_soccer_goals_from_key_events(self):
        goal = lambda team_id: {"scoringPlay": True, "team": {"id": team_id}}
        s = summary(3, 2, keyEvents=[goal("20"), goal("20"), goal("10"), goal("10"), goal("10")])
        team, deficit = final_comeback(parse_game(s), BY_KEY["mls"])
        self.assertEqual((team.abbr, deficit), ("HOM", 2))

    def test_linescores_fallback(self):
        s = summary(5, 4)
        comps = s["header"]["competitions"][0]["competitors"]
        comps[0]["linescores"] = [{"value": 0}, {"value": 1}, {"value": 4}]
        comps[1]["linescores"] = [{"value": 3}, {"value": 1}, {"value": 0}]
        team, deficit = final_comeback(parse_game(s), BY_KEY["nhl"])
        self.assertEqual((team.abbr, deficit), ("HOM", 3))

    def test_live_alert_when_within_margin(self):
        game = parse_game(summary(60, 62, plays((0, 20), (60, 62)), home_wins=False))
        team, deficit, margin = live_comeback(game, BY_KEY["nba"])
        self.assertEqual((team.abbr, deficit, margin), ("HOM", 20, -2))

    def test_no_live_alert_when_still_far_behind(self):
        game = parse_game(summary(50, 62, plays((0, 20), (50, 62)), home_wins=False))
        self.assertIsNone(live_comeback(game, BY_KEY["nba"]))


if __name__ == "__main__":
    unittest.main()
