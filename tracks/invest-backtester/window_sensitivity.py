#!/usr/bin/env python3
"""Does the SMA-crossover verdict depend on which window pair you picked?

robustness_test.py already fixed the SMA windows at the 20/50 default and
varied the random seed across 30 paths. That answers "is the 20/50 result
representative of many paths" -- it does not answer whether 20/50 was ever
a fair pick in the first place. The window pair is the one real decision an
SMA-crossover trader makes (fast, slow), the same way OTM% was the one real
decision a covered-call seller makes in options-income-sim's
otm_sensitivity.py. This sweeps several classic window pairs across many
seeds and three market regimes to see whether *any* pair reliably beats
buy-and-hold, or whether 20/50 losing was never about picking the "wrong"
window.

Usage:
    python3 window_sensitivity.py
    python3 window_sensitivity.py --paths 30 --windows 10:30,20:50,10:50,20:100,50:200
"""
import argparse
import statistics

from backtest import backtest_sma_crossover
from robustness_test import generate_price_path, make_rows

SCENARIOS = {
    "uptrend": 0.15,
    "flat": 0.0,
    "downtrend": -0.15,
}


def run_trial(short_window, long_window, seed, days, annual_drift, annual_vol):
    prices = generate_price_path(seed, 100.0, days, annual_drift, annual_vol)
    rows = make_rows(prices)
    result = backtest_sma_crossover(rows, short_window, long_window)
    return result["strategy_return_pct"] - result["buy_hold_return_pct"]


def summarize(short_window, long_window, scenario_name, excess_list):
    wins = sum(1 for e in excess_list if e > 0)
    n = len(excess_list)
    return {
        "windows": f"{short_window}/{long_window}",
        "scenario": scenario_name,
        "win_rate": 100 * wins / n,
        "avg_excess_pts": statistics.mean(excess_list),
        "worst_excess_pts": min(excess_list),
    }


def print_table(rows, scenario_name):
    print(f"--- Scenario: {scenario_name} ---")
    print(f"{'Windows':>9}  {'Win rate':>9}  {'Avg excess':>11}  {'Worst excess':>13}")
    for r in rows:
        print(f"{r['windows']:>9}  {r['win_rate']:8.1f}%  "
              f"{r['avg_excess_pts']:+10.2f}p  {r['worst_excess_pts']:+12.2f}p")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent seeds per window pair (default 30)")
    p.add_argument("--windows", type=str, default="10:30,20:50,10:50,20:100,50:200",
                    help="comma-separated short:long window pairs to sweep")
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--scenarios", type=str, default="uptrend,flat,downtrend",
                    help="comma-separated scenario names from SCENARIOS")
    args = p.parse_args()

    window_pairs = []
    for pair in args.windows.split(","):
        short_s, long_s = pair.split(":")
        window_pairs.append((int(short_s), int(long_s)))
    scenario_names = args.scenarios.split(",")

    print("SMA-crossover window-pair sensitivity")
    print(f"{args.paths} seeds per point, {args.days} trading days, annual_vol={args.annual_vol:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        rows = []
        for short_window, long_window in window_pairs:
            excess_list = [
                run_trial(short_window, long_window, seed, args.days, annual_drift, args.annual_vol)
                for seed in range(args.paths)
            ]
            rows.append(summarize(short_window, long_window, scenario_name, excess_list))
        print_table(rows, scenario_name)


if __name__ == "__main__":
    main()
