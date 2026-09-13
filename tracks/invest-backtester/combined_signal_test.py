#!/usr/bin/env python3
"""Does combining SMA and RSI beat treating them as two separate strategies?

Every test in this track so far — the original single-path runs,
robustness_test.py, window_sensitivity.py, rsi_sensitivity.py — evaluates
SMA crossover and RSI mean-reversion as *alternatives*, never together.
RSI's own documented failure mode (rsi_sensitivity.py, README) is that an
oversold signal can fire right before price keeps falling anyway — a
classic mean-reversion trap. backtest_trend_filtered_rsi() (backtest.py)
tests a natural combination: only take an RSI oversold entry while the SMA
crossover says the trend is up, and exit on RSI overbought OR the trend
flipping down, whichever comes first. This runs that combined strategy
against plain SMA, plain RSI, and buy-and-hold on the same seeded paths
used everywhere else in this track, across the same three regimes.

Usage:
    python3 combined_signal_test.py --paths 30
"""
import argparse
import statistics

from backtest import (
    backtest_sma_crossover,
    backtest_rsi_meanreversion,
    backtest_trend_filtered_rsi,
)
from robustness_test import generate_price_path, make_rows

SCENARIOS = {
    "uptrend": 0.15,
    "flat": 0.0,
    "downtrend": -0.15,
}

STRATEGIES = {
    "SMA(20/50) alone": lambda rows: backtest_sma_crossover(rows),
    "RSI(14, 30/70) alone": lambda rows: backtest_rsi_meanreversion(rows),
    "SMA-filtered RSI (combined)": lambda rows: backtest_trend_filtered_rsi(rows),
}


def run_trial(seed, days, annual_drift, annual_vol):
    prices = generate_price_path(seed, 100.0, days, annual_drift, annual_vol)
    rows = make_rows(prices)
    return {name: fn(rows) for name, fn in STRATEGIES.items()}


def summarize(name, results):
    excess = [r["strategy_return_pct"] - r["buy_hold_return_pct"] for r in results]
    trades = [r["trades"] for r in results]
    wins = sum(1 for e in excess if e > 0)
    n = len(excess)
    return {
        "name": name,
        "win_rate": 100 * wins / n,
        "avg_excess": statistics.mean(excess),
        "worst_excess": min(excess),
        "avg_trades": statistics.mean(trades),
    }


def print_table(rows, scenario_name):
    print(f"--- Scenario: {scenario_name} ---")
    print(f"{'Strategy':>30}  {'Win rate':>9}  {'Avg excess':>11}  {'Worst':>9}  {'Avg trades':>10}")
    for r in rows:
        print(f"{r['name']:>30}  {r['win_rate']:8.1f}%  "
              f"{r['avg_excess']:+10.2f}p  {r['worst_excess']:+8.2f}p  {r['avg_trades']:10.1f}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent seeds per scenario (default 30)")
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--scenarios", type=str, default="uptrend,flat,downtrend")
    args = p.parse_args()

    scenario_names = args.scenarios.split(",")

    print("SMA vs. RSI vs. SMA-filtered-RSI (combined signal)")
    print(f"{args.paths} seeds per scenario, {args.days} trading days, annual_vol={args.annual_vol:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        all_results = [run_trial(seed, args.days, annual_drift, args.annual_vol)
                       for seed in range(args.paths)]
        rows = []
        for name in STRATEGIES:
            results = [r[name] for r in all_results]
            rows.append(summarize(name, results))
        print_table(rows, scenario_name)


if __name__ == "__main__":
    main()
