# Study 2 post-mortem: why the 15:00 SPXW condor lost money in the early period

This is descriptive only. It does not change the pre-registered rule or the FAIL verdict. Anything below that looks like a fix was found
*after* seeing the results. It can only be tested in a new pre-registered forward test.

- **Scope:** the primary (enter at 15:00, 10-point wings, no filter, US$4 fees), 586 trades from 2024-07-02 to 2026-11-13.
- **Script:** `src/study2_diagnostics.py`. Per-trade table: `reports/tables/study2_primary_trades_diag.csv`.

## 1. The whole sample is roughly break-even, and the drawdown is large

| | Value |
|---|---|
| Total P&L | **−US$614** over 586 condors (−US$1.05 each) |
| Winners | 455 (78%) totalling **+US$65,261** |
| Losers | 131 (22%) totalling **−US$65,875** |
| Max-loss days | 50 (8.5%) totalling **−US$39,995** |
| **Max drawdown** | **−US$10,622**, from the peak on 2024-10-28 (+US$2,512 cumulative) to the trough on 2026-04-22 (−US$8,110) |
| Length of drawdown | 362 trades, about 18 months |
| Recovered by 2026-11-13? | **No.** The cumulative P&L is −US$614, about US$3,100 short of the peak. |

The study reported a −US$4,475 drawdown because it measured the held-out period only. Over the full two years the drawdown is
**−US$10.6k**, about 12 times the maximum loss on a single condor.

## 2. Why the early period was down: the volatility regime
Results by quarter track how volatile the market was. EM% is the expected move to the close as a percentage of the index.

| Quarter | Mean per trade | EM% | Breach rate | Max-loss rate | Market backdrop |
|---|---|---|---|---|---|
| 2024 Q3 | +21.9 | 0.22% | 21% | 10% | |
| 2024 Q4 | −18.6 | 0.15% | 32% | 5% | election and post-election |
| 2025 Q1 | −16.4 | 0.25% | 33% | 10% | February–March sell-off |
| **2025 Q2** | **−44.7** | **0.30%** | 31% | **15%** | **April 2025 tariff crash** |
| 2025 Q3 | +12.8 | 0.14% | 21% | 3% | calm |
| 2025 Q4 | −29.2 | 0.17% | 32% | 11% | October–November sell-off |
| 2026 Q1 | −26.9 | 0.20% | 33% | 13% | |
| 2026 Q2 | +12.7 | 0.18% | 26% | 8% | |
| **2026 Q3** | **+52.5** | **0.13%** | 20% | 3% | **calm** |
| 2026 Q4 | +42.0 | 0.15% | 23% | 7% | calm |

**By implied-volatility tercile:**

| | Mean per trade | Max-loss rate |
|---|---|---|
| Low IV | +US$4.0 | **1.5%** |
| Mid IV | +US$20.6 | 6.2% |
| High IV | **−US$27.7** | **17.9%** |

**Conclusion:** the held-out period looks good mainly because mid-2026 was calm. The early period contained the turbulent stretches
(Feb–May 2025, Oct–Nov 2025, Q1 2026). This is the classic short-volatility pattern: small steady gains while the market is quiet, given back in
clusters when volatility rises. It reflects the market regime the sample happened to contain, not a stable edge.

## 3. Why individual condors fail (131 losers)

**1. A late move of about 2 expected moves.**
- The median loser moved **1.88× the implied move** between 15:00 and the close.
- SPY's median last-hour move was 0.34% on losing days, against 0.12% on all days.
- The losses are split evenly by side: 69 put-side breaches and 62 call-side.

**2. The fixed 10-point wing becomes a binary bet when volatility is high.**
- In high-IV regimes the 15:00 expected move is 13–20 points, so a 10-point wing sits less than 1 EM beyond the short strike.
- Any breach then tends to run all the way to max loss: 17.9% of high-IV days hit max loss, against 1.5% of low-IV days.
- The $5 strike rounding also gives less cushion: the short strikes sit 2.3 EM apart in high IV versus 2.8 EM in low IV.

**3. It's not trend continuation.**
- Losing breaches went in the direction of the day's 10:00–15:00 trend 49% of the time.
- For all days that figure is 47%, so it's a coin flip.
- A "skip trend days" filter is therefore unlikely to help. The trend-day tercile does lose (−US$24), but that's because trend days are high-IV days.

**4. The options are not mis-priced in the way the condor needs.**
Here is how often the 15:00 → close move exceeded k × EM, compared with a normal distribution where the straddle is priced fairly:

| Move larger than | Actual | Fair (normal) |
|---|---|---|
| 1 EM | 37.2% | 42.5% |
| 1.5 EM | 18.8% | 23.1% |
| 2 EM | 8.9% | 11.0% |
| **3 EM** | **2.2%** | **1.7%** |

- **Moderate moves are slightly overpriced**, which is the condor's small edge.
- **Very large moves are underpriced** (fat tails), and those days are where the max losses come from.
- After the bid-ask spread on four legs and US$4 in fees, the small edge in the middle doesn't cover the tail.

**5. The worst days were ordinary days, not scheduled events.**
- Most of the −US$850 to −US$909 days had no FOMC meeting. They were last-hour sell-offs or rallies (for example 2024-11-20, 2025-11-05, 2026-01-07 and 2026-04-13).
- FOMC days were actually positive (n = 19, +US$82 average). That is too few to mean anything.

## 4. Things that look like patterns but are probably noise
- **Day of week:** Monday averaged −US$35 and Friday +US$43, with about 115 trades each. The standard error per group is about US$29, so with 5 groups compared, a gap this size is expected by chance.
- **Credit:** high-credit days lost money (−US$15) and low-credit days made money (+US$9). This is the same effect as the IV regime, not a separate one.

## 5. What this means
- **The strategy is short volatility.** It earns about US$100–150 on calm days and loses US$500–900 on volatile days. Its long-run average is roughly zero after costs, with an 18-month −US$10.6k drawdown.
- **A low-IV-only rule looks better on paper, but it is post-hoc.** For example, trading only when EM% is in the lower two terciles. It came from looking at these results, and the low-IV tercile alone averages only +US$4 per trade. Any such rule would need its own pre-registration and a forward test on new data before it means anything.
