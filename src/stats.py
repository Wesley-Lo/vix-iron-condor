"""Statistics used for both the backtest summary and the forward test."""
import numpy as np
import pandas as pd

NBOOT, SEED = 10_000, 12345


def day_boot_ci(df, col, q=(2.5, 97.5)):
    g = df.groupby("date")[col].agg(["sum", "count"])
    if len(g) < 5:
        return tuple([np.nan] * len(q))
    idx = np.random.default_rng(SEED).integers(0, len(g), (NBOOT, len(g)))
    m = g["sum"].values[idx].sum(1) / g["count"].values[idx].sum(1)
    return tuple(np.percentile(m, q))


def max_drawdown(pnl_by_date: pd.Series):
    c = pnl_by_date.sort_index().cumsum()
    return float((c - c.cummax()).min()) if len(c) else 0.0


def summary(df, col="pnl_ws", stress_col="pnl_stress_ws"):
    if df.empty:
        return dict(n=0)
    lo, hi = day_boot_ci(df, col)
    d = df.groupby("date")[col].sum()
    return dict(n=len(df), mean=df[col].mean(), median=df[col].median(), win_rate=(df[col] > 0).mean(), ci2_5=lo, ci97_5=hi,
                stress_mean=df[stress_col].mean() if stress_col in df else np.nan, total=df[col].sum(), worst=df[col].min(),
                max_drawdown=max_drawdown(d))
