# SPXW VIX-filtered 0DTE condor: forward test

Sells a 15:00 ET SPXW iron condor (10-point wings, strikes at ±1 expected move) on days when the prior day's VIX close is below 18.

**This is a forward test, not a proven strategy.** The backtest failed its statistical gate. See `STRATEGY.md`.

## Layout
- `STRATEGY.md`: the frozen rule, backtest numbers, pass criteria, limitations.
- `src/rule.py`: rule implementation (strike selection, credit, settlement).
- `src/forward.py`: `update` logs each new trading day; `report` summarises forward trades.
- `src/data_sources.py`: Yahoo (VIX, SPX closes) and Databento (SPXW quotes, cost-capped).
- `data/backtest/backtest_trades.csv`: the 596 backtest days (pre-freeze).
- `forward/trades.csv`: forward log, one row per trading day from 2026-11-18.
- `forward/databento_cost_log.csv`: every Databento request and its cost.
- `docs/`: pre-registration and the research reports this rule came from.
- `tests/test_reproduce.py`: checks the STRATEGY.md numbers against the backtest file.

## Running
```
pip install -r requirements.txt
set DATABENTO_API_KEY=...        (Windows; never commit it)
python src/forward.py update
python src/forward.py report
python -m pytest tests -q
```

## Rules for this repo
- Do not change `src/rule.py` parameters during the forward test. Any change starts a new test.
- Commit each `update` run so the log history is public and auditable.
