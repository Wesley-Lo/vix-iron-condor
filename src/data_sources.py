"""Market data: VIX / SPX closes (Yahoo Finance) and SPXW 15:00 quotes (Databento, cost-checked)."""
import csv, datetime as dt, os
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / "data" / "raw"            # git-ignored: raw vendor data is NOT redistributed
COST_LOG = REPO / "forward" / "databento_cost_log.csv"
BUDGET_USD = float(os.environ.get("FWD_DATABENTO_BUDGET_USD", "5.00"))
NY = ZoneInfo("America/New_York")


def _load_dotenv():
    """Read KEY=VALUE lines from REPO/.env into os.environ (never overrides real environment variables)."""
    f = REPO / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


def yahoo_close(ticker, start, end):
    import yfinance as yf
    x = yf.download(ticker, start=str(start), end=str(end + dt.timedelta(days=1)), progress=False, auto_adjust=False)["Close"]
    x = x.iloc[:, 0] if isinstance(x, pd.DataFrame) else x
    x.index = x.index.date
    return x.dropna()


def prior_close(ticker, d):
    s = yahoo_close(ticker, d - dt.timedelta(days=10), d - dt.timedelta(days=1))
    s = s[s.index < d]
    return (s.index[-1], float(s.iloc[-1])) if len(s) else (None, float("nan"))


def close_on(ticker, d):
    s = yahoo_close(ticker, d, d)
    return float(s.loc[d]) if d in s.index else float("nan")


def utc_iso(d, hhmm):
    h, m = map(int, hhmm.split(":"))
    return dt.datetime(d.year, d.month, d.day, h, m, tzinfo=NY).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def spent():
    if not COST_LOG.exists():
        return 0.0
    return sum(float(r["cost_usd"]) for r in csv.DictReader(COST_LOG.open()) if r["action"] == "download")


def spxw_quotes_1500(d, symbols):
    """OPRA.PILLAR cbbo-1m 14:55-15:01 for `symbols`; state at 15:00 = last record <= 15:00, <= 2 min old."""
    import databento as db
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        raise SystemExit("set DATABENTO_API_KEY in your environment (never commit it)")
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"spxw_{d:%Y%m%d}_1455_1501.dbn.zst"
    kw = dict(dataset="OPRA.PILLAR", schema="cbbo-1m", symbols=symbols, stype_in="raw_symbol", start=utc_iso(d, "14:55"), end=utc_iso(d, "15:01"))
    if not f.exists():
        c = db.Historical(key)
        cost = float(c.metadata.get_cost(**kw))
        action = "download" if spent() + cost <= BUDGET_USD else "REFUSED_budget"
        new = not COST_LOG.exists()
        with COST_LOG.open("a", newline="") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["utc_time", "trade_date", "cost_usd", "action"])
            w.writerow([dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), d, f"{cost:.4f}", action])
        if action != "download":
            raise SystemExit(f"Databento request ${cost:.2f} would exceed the forward-test budget ${BUDGET_USD:.2f}")
        c.timeseries.get_range(**kw, path=str(f))
    o = db.DBNStore.from_file(f).to_df().reset_index()
    if o.empty:
        return pd.DataFrame(columns=["bid", "ask"])
    o = o[["ts_recv", "symbol", "bid_px_00", "ask_px_00"]]; o.columns = ["ts", "symbol", "bid", "ask"]
    T = pd.Timestamp(utc_iso(d, "15:00"), tz="UTC")
    o = o[(o.ts <= T) & (o.ts >= T - pd.Timedelta("2min"))].sort_values("ts").groupby("symbol").tail(1)
    return o.set_index("symbol")[["bid", "ask"]]
