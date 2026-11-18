# Strategy: SPXW 15:00 iron condor, filtered by prior-day VIX

**Status: forward test only.** The backtest did NOT pass its statistical gate. The VIX filter was added after
looking at the backtest results, so the backtest cannot prove the strategy. Only out-of-sample forward results can.

## Frozen rule (do not change during the forward test)

| Parameter | Value |
|---|---|
| Instrument | SPXW 0DTE index options (cash-settled, no share assignment) |
| Entry time | 15:00 ET |
| VIX filter | Trade only if the **prior trading day's** VIX close is **< 18**. Otherwise skip the day. |
| Strikes | Parity strike K = argmin \|call mid − put mid\|. F = K + C − P. EM = C + P (at K). |
| Short call | Lowest listed strike ≥ F + 1.0 × EM |
| Short put | Highest listed strike ≤ F − 1.0 × EM |
| Wings | 10 index points beyond each short strike |
| Fills (backtest) | Sell shorts at bid, buy longs at ask |
| Quote freshness | Last quote at or before 15:00, at most 2 minutes old, two-sided, not crossed |
| Exit | Hold to the 16:00 cash settlement at the official SPX close |
| Fees | US$4.00 per condor (Wealthsimple, 4 legs × US$1.00) |
| Size | 1 condor per trading day |

Pre-registration hashes: `logs/prereg_hashes.log` in the research repo (`PREREG_STUDY2_VIX.md`, 2026-11-18).

## Backtest results (2024-07-02 to 2026-11-13, 596 trading days)

Source: `data/backtest/backtest_trades.csv` (all trades, with a `traded` column for the VIX filter).

| | Unfiltered | VIX < 18 (this rule) |
|---|---|---|
| Trades, held-out (from 2025-12-04) | 236 | 148 |
| Mean per condor, held-out | +US$20.3 | +US$30.0 |
| 95% day-bootstrap CI, held-out | [−18.0, +55.9] | [−13.2, +70.2] |
| Stress mean (1 tick worse per leg) | −US$0.3 | +US$9.5 |
| Walk-forward mean (threshold re-picked daily from past data) | n/a | +US$21.4 |
| Max drawdown, full 2 years | −US$10,622 | −US$2,832 |

**Gate result: FAIL.** The lower CI bound is below zero (−13.2). The VIX threshold 18 was chosen on the early period,
but the held-out period was known to be calm, so the held-out result is likely flattered.

## What would count as proof

Forward test, same rule, no changes, on trades that were not in the backtest:
- at least 100 traded days (the rule trades about 60% of days, so roughly 5 months of trading days);
- 95% day-bootstrap CI lower bound **> 0** on forward trades only;
- stress-test mean **> 0** on forward trades only.

If it fails, say so and stop. Do not re-tune the VIX threshold or wings on forward results.

## Known limitations
- **Fills are simulated** from recorded bid/ask, not real orders. Real combo fills can differ.
- **Historical data lag:** quotes are pulled after the close, not live at 15:00. The decision is still made from the
  prior VIX close, so the process is not look-ahead, but it is not a live execution test.
- **Tail risk:** worst backtest day was about −US$909. Max loss per condor is about US$860 before fees.
- **Multiple testing:** this rule is one of about 20 ideas tested on the same period. Forward results are the only clean evidence.
