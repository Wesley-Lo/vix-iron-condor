# VIX filter on the 15:00 SPXW condor (PREREG_STUDY2_VIX.md, post-hoc): FAIL, but the best result so far

- **Signal:** the prior day's VIX close (Yahoo ^VIX), which is known before the 15:00 entry.
- **Trades:** the Study 2 primary (15:00, 10-point wings, US$4 fees).
- **Data cost:** no Databento spend.
- **Pre-registration hash:** in `logs/prereg_hashes.log` (2026-11-18T00:25:19Z).

## Where the condor breaks (full sample, descriptive)

| Prior-day VIX | Trades | Mean per condor | Total | Win rate | Max-loss rate | Avg credit |
|---|---|---|---|---|---|---|
| < 13 | 9 | −US$98 | −883 | 67% | 11% | US$105 |
| 13–15 | 68 | −US$11 | −717 | 79% | 1% | US$110 |
| **15–17** | 204 | **+US$11** | +2,336 | 81% | 6% | US$142 |
| **17–19** | 132 | **+US$31** | +4,062 | 80% | 8% | US$164 |
| 19–21 | 77 | −US$11 | −840 | 74% | 10% | US$167 |
| **21–25** | 58 | **−US$89** | **−5,161** | 67% | **21%** | US$198 |
| 25–30 | 25 | −US$26 | −661 | 68% | 16% | US$212 |
| > 30 | 13 | +US$96 | +1,250 | 85% | 8% | US$238 |

- **The break zone is VIX 21–25.** That is where volatility is "elevated but not panicked". Its 58 trades lost −US$5.2k, which is most of the total loss.
- **Low VIX (below 15) is also weak.** Credits are too small to pay for the occasional breach.
- **VIX above 30 looks positive, but it is only 13 trades.** Those were very rich credits on days after spikes. The sample is too small to rely on.
- **Inverted term structure** (VIX9D > VIX the prior day, 97 trades) averaged +US$34. Normal term structure averaged −US$8. This is the opposite of the usual "stress means danger" story, probably the same rich-premium-after-spike effect. It is descriptive only.

## Pre-registered test

**Threshold selection:**
- The threshold was chosen on the early period only: **trade only if VIX_prev < 18**.
- The early-period mean went from −US$15.4 to +US$4.3, keeping 206 of 350 trades.
- The early threshold curve is noisy. The peak at 18–19 is only about +US$4, and every T ≥ 23 is about −US$13 to −US$20.

| Held-out (from 2025-12-04) | Unfiltered | **VIX_prev < 18** |
|---|---|---|
| Trades | 236 | 148 |
| Mean per condor | +US$20.3 | **+US$30.0** |
| Median per condor | +US$126 | +US$116 |
| 95% CI | [−18.0, +55.9] | **[−13.2, +70.2]** |
| 99% CI (Bonferroni) | [−30.3, +66.2] | [−28.3, +80.6] |
| Stress (1 tick per leg) | −US$0.3 | **+US$9.5** |
| Walk-forward mean (threshold re-picked each day from past data only; T ranged 18–19) | n/a | **+US$21.4** (152 trades) |
| Win rate | 80% | 82% |
| Sharpe, annualized | 1.1 | 1.44 |
| Deflated Sharpe | 0.3 | 0.82 |
| **Max drawdown, full 2 years** | **−US$10,622** | **−US$2,832** |
| Total P&L, full 2 years | −US$614 | +US$5,327 (includes the in-sample period) |

**Criteria:**

| Criterion | Result |
|---|---|
| CI lower bound > 0 | **No** (−13.2) |
| Stress > 0 | Yes |
| Walk-forward > 0 | Yes |
| At least 100 held-out trades | Yes (148) |

**Verdict: FAIL.**

## Interpretation
- **The VIX filter improves almost everything.** It cuts the full-sample drawdown by about 73%, from −US$10.6k to −US$2.8k. It makes the stress test positive. It also works when the threshold is chosen only from past data.
- **But the held-out CI still includes zero.** With about 150 trades and a per-trade SD of about US$300, it would take roughly 400–600 filtered trades to confirm an edge of US$20–30.
- **It is post-hoc.** The filter was suggested by the post-mortem, and the held-out period was already known to be calm.

So this is the **best lead in the project, and still unproven**. The right next step is a forward test of exactly this rule, unchanged: trade the 15:00 SPXW condor, 10-point wings, only when the prior VIX close is below 18.
