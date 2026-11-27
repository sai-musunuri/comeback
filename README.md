# Comeback

Comeback finds the games worth watching: the ones where a team climbs out of a big hole. It watches the NFL, NBA, MLB, NHL, MLS, college football, and men's college basketball, sends a push alert while a comeback is happening, and keeps a daily record of every completed one.

## How it works

- **Live alerts** (`comeback/live.py`): every 15 minutes during game hours, a GitHub Action checks every game in progress. When a team that trailed by a league's comeback threshold pulls within striking distance, it sends a push notification through [ntfy](https://ntfy.sh) and logs it to `alerts/log.csv`.
- **Daily recap** (`comeback/recap.py`): each morning it checks every final from the day before, measures the largest deficit the winner erased using play-by-play scoring, and writes `recaps/YYYY-MM-DD.md` and `data/comebacks.csv`.
- **Data**: ESPN's public scoreboard and game summary feeds. Python standard library only.

| League | Comeback threshold | Live alert when within |
|---|---|---|
| NFL | 14 points | 3 points |
| NBA | 18 points | 3 points |
| MLB | 4 runs | 1 run |
| NHL | 3 goals | tied |
| MLS | 2 goals | tied |
| College Football | 17 points | 3 points |
| Men's College Basketball | 15 points | 3 points |

## Recent comebacks

<!-- recent:start -->
Latest recap: [2026-11-26](recaps/2026-11-26.md)

| Date | League | Winner | Deficit erased | Final |
|---|---|---|---|---|
| 2026-11-26 | NFL | Philadelphia Eagles | 21 points | PHI 39, DAL 38 |
| 2026-11-25 | Men's College Basketball | St. Bonaventure Bonnies | 16 points | SBU 71, BEL 68 |
| 2026-11-24 | Men's College Basketball | Colorado Buffaloes | 20 points | COLO 70, STAN 65 |
| 2026-11-24 | Men's College Basketball | Ole Miss Rebels | 18 points | MISS 73, BYU 63 |
| 2026-11-23 | Men's College Basketball | BYU Cougars | 15 points | BYU 83, WASH 77 |
| 2026-11-22 | Men's College Basketball | Troy Trojans | 18 points | TROY 78, NICH 77 |
| 2026-11-22 | Men's College Basketball | Southern Miss Golden Eagles | 22 points | USM 99, VAL 89 |
| 2026-11-22 | NHL | St. Louis Blues | 3 goals | STL 5, EDM 4 |
| 2026-11-21 | College Football | Oklahoma State Cowboys | 17 points | OKST 30, ASU 27 |
| 2026-11-21 | College Football | Jacksonville State Gamecocks | 17 points | JXST 25, MOST 20 |
| 2026-11-21 | Men's College Basketball | Eastern Michigan Eagles | 17 points | EMU 70, DEN 68 |
| 2026-11-21 | Men's College Basketball | Oral Roberts Golden Eagles | 17 points | ORU 78, AMCC 74 |
| 2026-11-21 | Men's College Basketball | Valparaiso Beacons | 19 points | VAL 77, TROY 72 |
| 2026-11-20 | NBA | Oklahoma City Thunder | 18 points | OKC 126, NO 120 |
| 2026-11-19 | Men's College Basketball | VCU Rams | 18 points | VCU 83, SCU 77 |
<!-- recent:end -->

## Run locally

```
python -m comeback.recap 2026-11-21   # recap a specific date
python -m comeback.live               # check live games (set NTFY_TOPIC to get push alerts)
python -m unittest                    # tests
```

## Get alerts on your phone

Install the ntfy app, subscribe to the topic stored in the repo's `NTFY_TOPIC` secret, and alerts arrive as push notifications.
