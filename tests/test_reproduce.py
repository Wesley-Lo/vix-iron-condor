"""Check the frozen backtest numbers in STRATEGY.md against the exported trade file. Run: python -m pytest tests -q (or python tests/test_reproduce.py)."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CUT = pd.Timestamp("2025-12-04")


def load():
    t = pd.read_csv(ROOT / "data" / "backtest" / "backtest_trades.csv", parse_dates=["date"])
    return t[t.traded.astype(str).str.lower() == "true"]


def test_held_out_count_and_mean():
    h = load(); h = h[h.date >= CUT]
    assert len(h) == 148
    assert round(h.pnl_ws.mean(), 1) == 30.0


def test_fees_are_four_dollars():
    t = pd.read_csv(ROOT / "data" / "backtest" / "backtest_trades.csv")
    d = (t.gross_pnl_usd - t.pnl_ws).dropna().round(2).unique()
    assert list(d) == [4.0]


if __name__ == "__main__":
    test_held_out_count_and_mean(); test_fees_are_four_dollars(); print("ok")
