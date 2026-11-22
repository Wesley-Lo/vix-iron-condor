# Weekly forward-test reports

One folder per week (`week_YYYY-MM-DD`, named after the Monday). Each has:
- `README.md`: what the rule did that week and why, plus running totals.
- `trades.csv`: that week's rows (executed and skipped days), copied from `forward/trades.csv`.

`forward/trades.csv` stays the master log written by `python src/forward.py update`.

| Week | Traded | Skipped | Week P&L (WS) | Notes |
|---|---|---|---|---|
| [2026-11-16](week_2026-11-16/) | 0 | 3 | US$0 | VIX 24.6 to 28.4, all days filtered out |
