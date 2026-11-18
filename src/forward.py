"""Forward-test runner for the frozen SPXW VIX-filtered condor (see STRATEGY.md).

Usage (from the repo root):
  python src/forward.py update   # decide + record every complete trading day not yet logged
  python src/forward.py report   # summary of forward trades only

Set DATABENTO_API_KEY in your environment. Never commit it. Budget cap: FWD_DATABENTO_BUDGET_USD (default 5).
"""
import csv, datetime as dt, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import rule, data_sources as ds, stats

REPO = Path(__file__).resolve().parents[1]
TRADES = REPO / "forward" / "trades.csv"
FREEZE_START = dt.date(2026, 11, 18)          # first decision day after the pre-registration
FIELDS = ["date", "traded", "skip_reason", "vix_prev", "spx_prev_close", "forward_1500", "expected_move_1500", "parity_strike",
          "short_call", "long_call", "short_put", "long_put", "credit_usd", "credit_stress_usd", "spx_close",
          "gross_pnl_usd", "pnl_ws", "pnl_stress_ws", "pnl_ibkr"]


def logged():
    if not TRADES.exists():
        return set()
    return {r["date"] for r in csv.DictReader(TRADES.open())}


def append(row):
    TRADES.parent.mkdir(parents=True, exist_ok=True)
    new = not TRADES.exists()
    with TRADES.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


def trading_days(until):
    s = ds.yahoo_close("^GSPC", FREEZE_START - dt.timedelta(days=5), until)
    return [d for d in s.index if d >= FREEZE_START and d <= until]


def update():
    today = dt.datetime.now(ds.NY).date()
    # Only complete days: the close must exist and the day must be at least 1 day old (vendor data lag).
    until = today - dt.timedelta(days=1)
    done = logged()
    for d in trading_days(until):
        if f"{d:%Y-%m-%d}" in done:
            continue
        _, vix_prev = ds.prior_close("^VIX", d)
        pd_, spx_prev = ds.prior_close("^GSPC", d)
        base = dict(date=f"{d:%Y-%m-%d}", vix_prev=vix_prev, spx_prev_close=spx_prev)
        if not rule.should_trade(vix_prev):
            append({**base, "traded": False, "skip_reason": "vix_filter"}); print(d, "skip: VIX", vix_prev); continue
        k0 = int(round(spx_prev / rule.STRIKE_STEP) * rule.STRIKE_STEP)
        syms = sorted(rule.osi(d, cp, k) for k in range(k0 - rule.STRIKE_WINDOW, k0 + rule.STRIKE_WINDOW + 1, rule.STRIKE_STEP) for cp in "CP")
        quotes = ds.spxw_quotes_1500(d, syms)
        c = rule.build(quotes, d) if len(quotes) else {"skip_reason": "no_quotes"}
        if c["skip_reason"]:
            append({**base, "traded": False, "skip_reason": c["skip_reason"], "forward_1500": c.get("forward_1500"),
                    "expected_move_1500": c.get("expected_move_1500")}); print(d, "skip:", c["skip_reason"]); continue
        spx_close = ds.close_on("^GSPC", d)
        if spx_close != spx_close:          # NaN: settlement close not published yet
            print(d, "close not available yet; rerun later"); break
        gross, net, net_s = rule.settle(c["short_call"], c["short_put"], spx_close, c["credit_usd"], c["credit_stress_usd"])
        ibkr = round(gross - 5.60, 2)
        append({**base, "traded": True, "skip_reason": "", "forward_1500": round(c["forward_1500"], 3),
                "expected_move_1500": round(c["expected_move_1500"], 3), "parity_strike": c["parity_strike"],
                "short_call": c["short_call"], "long_call": c["long_call"], "short_put": c["short_put"], "long_put": c["long_put"],
                "credit_usd": c["credit_usd"], "credit_stress_usd": c["credit_stress_usd"], "spx_close": spx_close,
                "gross_pnl_usd": gross, "pnl_ws": net, "pnl_stress_ws": net_s, "pnl_ibkr": ibkr})
        print(d, "TRADE", c["short_put"], c["short_call"], "credit", c["credit_usd"], "net", net)


def report():
    if not TRADES.exists():
        sys.exit("no forward trades yet")
    t = pd.read_csv(TRADES, parse_dates=["date"])
    f = t[t.traded.astype(str).str.lower() == "true"].copy(); f["date"] = f.date.dt.date
    s = stats.summary(f)
    print(f"days logged: {len(t)}  traded: {len(f)}  skipped (VIX >= 18): {int((t.skip_reason == 'vix_filter').sum())}")
    for k, v in s.items():
        print(f"{k:14s} {v:.2f}" if isinstance(v, float) else f"{k:14s} {v}")
    need = 100
    print(f"\nprogress: {len(f)}/{need} traded days for the pass test")
    if len(f) >= need:
        verdict = "PASS" if s["ci2_5"] > 0 and s.get("stress_mean", 0) > 0 else "FAIL"
        print("forward verdict:", verdict)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    {"update": update, "report": report}[cmd]()
