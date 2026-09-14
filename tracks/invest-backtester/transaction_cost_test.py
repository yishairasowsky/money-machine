#!/usr/bin/env python3
"""Does a realistic per-trade cost change which Track A strategy looks best?

Every result in this track so far -- the original runs, robustness_test.py,
window_sensitivity.py, rsi_sensitivity.py, combined_signal_test.py -- uses
frictionless trades, which the README's own "To actually use this for real
decisions" section has flagged as unmodeled since day one ("Account for
transaction costs and taxes, which this prototype ignores"). That gap
matters more than it might look like, because the three strategies now on
record trade at very different frequencies: SMA crossover averages ~10
trades per 2-year path, RSI mean-reversion ~2.6-3.3, and the SMA-filtered
combined strategy (9/13) only ~0.7-1.4 -- a cost-per-trade should hurt them
in exactly that order, and might even flip the ranking between strategies
that looked close on a frictionless basis.

backtest.py now accepts `cost_pct` (a round-trip-agnostic friction cost
deducted from the traded value on every entry AND every exit). This sweeps
a small, realistic range of per-trade costs (0%, 0.05%, 0.1%, 0.25%, 0.5% --
roughly "free" to "a retail CFD/forex-style spread cost") across all three
strategies, the same seeded paths and regimes used everywhere else in this
track.

Usage:
    python3 transaction_cost_test.py --paths 30
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
    "SMA(20/50)": lambda rows, cost: backtest_sma_crossover(rows, cost_pct=cost),
    "RSI(14, 30/70)": lambda rows, cost: backtest_rsi_meanreversion(rows, cost_pct=cost),
    "Combined (SMA-filtered RSI)": lambda rows, cost: backtest_trend_filtered_rsi(rows, cost_pct=cost),
}

DEFAULT_COSTS = [0.0, 0.0005, 0.001, 0.0025, 0.005]


def run_trial(seed, days, annual_drift, annual_vol, cost_pct):
    prices = generate_price_path(seed, 100.0, days, annual_drift, annual_vol)
    rows = make_rows(prices)
    return {name: fn(rows, cost_pct) for name, fn in STRATEGIES.items()}


def summarize(name, results):
    excess = [r["strategy_return_pct"] - r["buy_hold_return_pct"] for r in results]
    trades = [r["trades"] for r in results]
    wins = sum(1 for e in excess if e > 0)
    n = len(excess)
    return {
        "name": name,
        "win_rate": 100 * wins / n,
        "avg_excess": statistics.mean(excess),
        "avg_trades": statistics.mean(trades),
    }


def print_table(scenario_name, cost_pct, rows):
    print(f"--- Scenario: {scenario_name}, cost_pct={cost_pct:.3%} per trade ---")
    print(f"{'Strategy':>30}  {'Win rate':>9}  {'Avg excess':>11}  {'Avg trades':>10}")
    for r in rows:
        print(f"{r['name']:>30}  {r['win_rate']:8.1f}%  "
              f"{r['avg_excess']:+10.2f}p  {r['avg_trades']:10.1f}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent seeds per point (default 30)")
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--costs", type=str, default=",".join(str(c) for c in DEFAULT_COSTS),
                    help="comma-separated per-trade cost fractions, e.g. 0,0.001,0.005")
    p.add_argument("--scenarios", type=str, default="uptrend,flat,downtrend")
    args = p.parse_args()

    costs = [float(c) for c in args.costs.split(",")]
    scenario_names = args.scenarios.split(",")

    print("Transaction-cost sensitivity across all three Track A strategies")
    print(f"{args.paths} seeds per point, {args.days} trading days, annual_vol={args.annual_vol:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        for cost_pct in costs:
            all_results = [run_trial(seed, args.days, annual_drift, args.annual_vol, cost_pct)
                           for seed in range(args.paths)]
            rows = []
            for name in STRATEGIES:
                results = [r[name] for r in all_results]
                rows.append(summarize(name, results))
            print_table(scenario_name, cost_pct, rows)


if __name__ == "__main__":
    main()
