# Forward test: week of 2026-11-16

**Result: no trades entered. 0 executed, 3 skipped.**

| Date | Prior-day VIX close | SPX prior close | Decision | Reason |
|---|---|---|---|---|
| Mon 2026-11-16 | n/a | n/a | not in test | Before the forward-test start (rule frozen 2026-11-18) |
| Tue 2026-11-17 | n/a | n/a | not in test | Before the forward-test start (rule frozen 2026-11-18) |
| Wed 2026-11-18 | 25.46 | 7340.53 | skip | VIX filter: 25.46 ≥ 18 |
| Thu 2026-11-19 | 24.56 | 7323.63 | skip | VIX filter: 24.56 ≥ 18 |
| Fri 2026-11-20 | 28.44 | 7175.83 | skip | VIX filter: 28.44 ≥ 18 |

## Why no trades were entered

The frozen rule (see `STRATEGY.md`) only sells the 15:00 ET SPXW iron condor when the **prior trading day's VIX close is below 18**.
VIX stayed well above that all week, between 24.56 and 28.44, peaking at 28.44 going into Friday as SPX fell about 165 points from Wednesday's reference close.
So every forward day this week was skipped by the filter. No strikes were picked and no SPXW quotes were bought (Databento spend: US$0).

The filter is doing its job here. In the backtest, the high-VIX days were where the unfiltered condor took its largest losses,
and avoiding them is what cut the max drawdown from about −US$10,600 to −US$2,800.

Mon 11/16 and Tue 11/17 are not part of the forward test because they fall before the 2026-11-18 freeze date.

## Running totals (forward test only)

| | Value |
|---|---|
| Days logged | 3 |
| Traded | 0 |
| Skipped (VIX ≥ 18) | 3 |
| Forward P&L | US$0 |
| Progress to pass test | 0 / 100 traded days |

## Files
- `trades.csv`: this week's rows from `forward/trades.csv` (traded and skipped days).
