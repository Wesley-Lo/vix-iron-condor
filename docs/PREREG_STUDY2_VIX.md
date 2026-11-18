# PREREG_STUDY2_VIX: VIX-threshold filter on the Study 2 15:00 SPXW condor (POST-HOC, exploratory)

Written before any VIX data was loaded or merged with the trades.

## Honesty note
This idea came from the Study 2 post-mortem, which showed losses concentrated in high-IV regimes. The held-out period has
already been inspected (it was calm), so a volatility filter is expected to look good there almost by construction.
**Even a PASS here is not evidence of an edge.** It only justifies a forward test on new data.

## Data
- **VIX:** Yahoo Finance ^VIX daily close, plus ^VIX9D daily close for a descriptive term-structure check. Both are free and need no Databento spend.
- **Signal:** the **prior trading day's VIX close**, which is known before the 15:00 entry, so there is no look-ahead.
- **Trades:** the Study 2 PRIMARY trades (15:00, 10-point wings, Wealthsimple US$4 fees). The trade rule is unchanged.

## Filter rule
Trade only if VIX_prev < T.

**Threshold selection (EARLY period only, i.e. dates before 2025-12-04):**
- T ∈ {13, 14, …, 30}.
- Pick the T that maximizes the early-period mean P&L per trade, subject to keeping at least 100 early trades.
- Ties go to the higher T (fewer days skipped).

**Walk-forward variant:**
- For each held-out day, re-select T with the same rule, using all trades **before** that day.
- The minimum is 100 prior trades kept.

## Verdict (held-out, using the T selected on the early period)
**PASS** only if ALL of these hold:
1. The held-out 95% day-bootstrap CI lower bound is > 0 (10,000 resamples, seed 12345).
2. The held-out stress mean is > 0.
3. The walk-forward held-out mean is > 0.
4. There are at least 100 held-out trades kept.

**Also reported:**
- the Bonferroni 99% bound and the Deflated Sharpe Ratio (N trials = 53);
- the max drawdown over the full sample with the filter applied;
- descriptively, P&L by VIX bucket over the full sample, and by VIX9D/VIX above or below 1 (inverted term structure).

Any PASS is labelled "lead for forward test only".
