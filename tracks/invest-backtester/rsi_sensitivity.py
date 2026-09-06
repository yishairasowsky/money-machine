#!/usr/bin/env python3
"""Does the RSI mean-reversion verdict depend on which thresholds you picked?

window_sensitivity.py asked this question for SMA crossover's one real
decision (the fast/slow window pair). RSI mean-reversion has its own
equivalent real decision: how oversold/overbought counts as a signal.
robustness_test.py fixed RSI at the 14/30/70 default and varied the seed --
that answers "is the 14/30/70 result representative of many paths," not
"was 30/70 ever a fair pick." This sweeps several classic oversold/
overbought threshold pairs (looser vs. stricter) across many seeds and
three market regimes to see whether *any* threshold pair reliably beats
buy-and-hold, or whether RSI's losses hold regardless of where you draw
the oversold/overbought lines.

Usage:
    python3 rsi_sensitivity.py
    python3 rsi_sensitivity.py --paths 30 --thresholds 20:80,25:75,30:70,35:65,40:60
"""
import argparse
import statistics

from backtest import backtest_rsi_meanreversion
from robustness_test import generate_price_path, make_rows

SCENARIOS = {
    "uptrend": 0.15,
    "flat": 0.0,
    "downtrend": -0.15,
}


def run_trial(oversold, overbought, seed, days, annual_drift, annual_vol, period):
    prices = generate_price_path(seed, 100.0, days, annual_drift, annual_vol)
    rows = make_rows(prices)
    result = backtest_rsi_meanreversion(rows, period, oversold, overbought)
    return result["strategy_return_pct"] - result["buy_hold_return_pct"], result["trades"]


def summarize(oversold, overbought, scenario_name, excess_list, trades_list):
    wins = sum(1 for e in excess_list if e > 0)
    n = len(excess_list)
    return {
        "thresholds": f"{oversold}/{overbought}",
        "scenario": scenario_name,
        "win_rate": 100 * wins / n,
        "avg_excess_pts": statistics.mean(excess_list),
        "worst_excess_pts": min(excess_list),
        "avg_trades": statistics.mean(trades_list),
    }


def print_table(rows, scenario_name):
    print(f"--- Scenario: {scenario_name} ---")
    print(f"{'Thresh':>8}  {'Win rate':>9}  {'Avg excess':>11}  {'Worst excess':>13}  {'Avg trades':>10}")
    for r in rows:
        print(f"{r['thresholds']:>8}  {r['win_rate']:8.1f}%  "
              f"{r['avg_excess_pts']:+10.2f}p  {r['worst_excess_pts']:+12.2f}p  "
              f"{r['avg_trades']:10.1f}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent seeds per threshold pair (default 30)")
    p.add_argument("--thresholds", type=str, default="20:80,25:75,30:70,35:65,40:60",
                    help="comma-separated oversold:overbought threshold pairs to sweep")
    p.add_argument("--rsi-period", type=int, default=14)
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--scenarios", type=str, default="uptrend,flat,downtrend",
                    help="comma-separated scenario names from SCENARIOS")
    args = p.parse_args()

    threshold_pairs = []
    for pair in args.thresholds.split(","):
        oversold_s, overbought_s = pair.split(":")
        threshold_pairs.append((float(oversold_s), float(overbought_s)))
    scenario_names = args.scenarios.split(",")

    print("RSI mean-reversion oversold/overbought threshold sensitivity")
    print(f"{args.paths} seeds per point, RSI({args.rsi_period}), {args.days} trading days, annual_vol={args.annual_vol:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        rows = []
        for oversold, overbought in threshold_pairs:
            excess_list = []
            trades_list = []
            for seed in range(args.paths):
                excess, trades = run_trial(
                    oversold, overbought, seed, args.days, annual_drift, args.annual_vol, args.rsi_period
                )
                excess_list.append(excess)
                trades_list.append(trades)
            rows.append(summarize(oversold, overbought, scenario_name, excess_list, trades_list))
        print_table(rows, scenario_name)


if __name__ == "__main__":
    main()
