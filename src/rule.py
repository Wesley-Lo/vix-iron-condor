"""The frozen strategy rule (see STRATEGY.md). Do not change these values during the forward test."""
import math
import numpy as np
import pandas as pd

ROOT = "SPXW"
ENTRY_TIME = "15:00"          # ET
VIX_MAX = 18.0                # trade only if the PRIOR trading day's VIX close is < 18
M_EM = 1.0                    # short strikes at F +/- 1.0 x expected move
WING = 10                     # index points beyond each short strike
STRIKE_STEP = 5
STRIKE_WINDOW = 250           # quote symbols within +/-250 points of the prior SPX close
FEE_PER_CONDOR = 4.00         # Wealthsimple US$1/contract x 4 legs (IBKR ~US$5.60)
MULT = 100


def osi(exp, cp, k):
    return f"{ROOT:<6}{exp:%y%m%d}{cp}{int(k) * 1000:08d}"


def tick(px):
    return 0.05 if px < 3 else 0.10


def should_trade(vix_prev_close):
    return vix_prev_close is not None and not math.isnan(vix_prev_close) and vix_prev_close < VIX_MAX


def build(quotes: pd.DataFrame, exp):
    """quotes: index = OSI symbol, columns bid, ask (two-sided, not crossed, <=2 min old at 15:00).
    Returns a dict describing the condor, or {'skip_reason': ...}."""
    q = quotes[(quotes.bid > 0) & (quotes.ask >= quotes.bid)]
    ks = sorted({int(s[-8:]) // 1000 for s in q.index})
    pairs = [k for k in ks if osi(exp, "C", k) in q.index and osi(exp, "P", k) in q.index]
    if not pairs:
        return {"skip_reason": "no_quotes"}
    mid = lambda s: (q.loc[s, "bid"] + q.loc[s, "ask"]) / 2
    K = min(pairs, key=lambda k: abs(mid(osi(exp, "C", k)) - mid(osi(exp, "P", k))))
    C, P = mid(osi(exp, "C", K)), mid(osi(exp, "P", K))
    F, EM = K + C - P, C + P
    calls = sorted(k for k in ks if osi(exp, "C", k) in q.index)
    puts = sorted((k for k in ks if osi(exp, "P", k) in q.index), reverse=True)
    sc = next((k for k in calls if k >= F + M_EM * EM), None)
    sp = next((k for k in puts if k <= F - M_EM * EM), None)
    if sc is None or sp is None:
        return {"skip_reason": "leg_missing", "forward_1500": F, "expected_move_1500": EM}
    legs = {"short_call": osi(exp, "C", sc), "long_call": osi(exp, "C", sc + WING),
            "short_put": osi(exp, "P", sp), "long_put": osi(exp, "P", sp - WING)}
    if any(v not in q.index for v in legs.values()):
        return {"skip_reason": "leg_missing", "forward_1500": F, "expected_move_1500": EM}
    b = {k: q.loc[v, "bid"] for k, v in legs.items()}; a = {k: q.loc[v, "ask"] for k, v in legs.items()}
    credit = b["short_call"] + b["short_put"] - a["long_call"] - a["long_put"]
    credit_s = (b["short_call"] - tick(b["short_call"]) + b["short_put"] - tick(b["short_put"])
                - a["long_call"] - tick(a["long_call"]) - a["long_put"] - tick(a["long_put"]))
    if credit <= 0:
        return {"skip_reason": "no_credit", "forward_1500": F, "expected_move_1500": EM}
    return {"skip_reason": None, "forward_1500": F, "expected_move_1500": EM, "parity_strike": K,
            "short_call": sc, "long_call": sc + WING, "short_put": sp, "long_put": sp - WING,
            **{f"bid_{k}": b[k] for k in b}, **{f"ask_{k}": a[k] for k in a},
            "credit_usd": round(credit * MULT, 2), "credit_stress_usd": round(credit_s * MULT, 2)}


def settle(short_call, short_put, spx_close, credit_usd, credit_stress_usd=None, fee=FEE_PER_CONDOR):
    """Cash settlement at the official SPX close. Returns (gross, net, net_stress)."""
    pay = max(0.0, min(spx_close - short_call, WING)) + max(0.0, min(short_put - spx_close, WING))
    gross = credit_usd - pay * MULT
    stress = None if credit_stress_usd is None or (isinstance(credit_stress_usd, float) and np.isnan(credit_stress_usd)) \
        else credit_stress_usd - pay * MULT - fee
    return round(gross, 2), round(gross - fee, 2), None if stress is None else round(stress, 2)
