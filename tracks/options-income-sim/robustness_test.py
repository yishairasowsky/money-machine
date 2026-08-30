#!/usr/bin/env python3
"""Multi-seed robustness test for covered-calls and the full wheel.

Every finding in this track's README came from a single seed (default 7)
per scenario — explicitly flagged there as "the exact numbers are not
[robust]." This script closes that gap the same way
tracks/invest-backtester/robustness_test.py did for that track: run each
strategy against buy-and-hold on many independent synthetic paths per
scenario (uptrend/flat/downtrend), and report how often it actually wins
and by how much, instead of trusting one draw.

Usage:
    python3 robustness_test.py [--paths N] [--strategy covered-call|wheel|both]

Still entirely on paper, still synthetic data and a heuristic premium model
— see sim.py's module docstring and this track's README for what that does
and doesn't prove.
"""
import argparse
import statistics

from sim import (
    generate_price_path,
    simulate_covered_calls,
    simulate_wheel,
    SCENARIOS,
    STRATEGY_LABELS,
)


def run_trial(strategy, seed, start_price, days, annual_drift, annual_vol,
              otm_pct, iv, period_days, contract_size=100):
    prices = generate_price_path(seed, start_price, days, annual_drift, annual_vol)
    if strategy == "wheel":
        result = simulate_wheel(prices, otm_pct, iv, period_days, contract_size)
    else:
        result = simulate_covered_calls(prices, otm_pct, iv, period_days, contract_size)

    initial_equity = contract_size * prices[0]
    strategy_return_pct = (result["final_equity"] / initial_equity - 1) * 100
    buy_hold_return_pct = (contract_size * result["final_price"] / initial_equity - 1) * 100
    return strategy_return_pct - buy_hold_return_pct


def summarize(strategy, scenario_name, excess_list):
    wins = sum(1 for e in excess_list if e > 0)
    n = len(excess_list)
    label = STRATEGY_LABELS[strategy]
    print(f"{label} / {scenario_name}:")
    print(f"  Beat buy-and-hold: {wins}/{n} paths ({100 * wins / n:.0f}%)")
    print(f"  Avg excess return: {statistics.mean(excess_list):+.2f} pts")
    print(f"  Median excess:     {statistics.median(excess_list):+.2f} pts")
    print(f"  Best / worst:      {max(excess_list):+.2f} / {min(excess_list):+.2f} pts")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent synthetic paths per scenario (default 30)")
    p.add_argument("--start-price", type=float, default=100.0)
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--iv", type=float, default=0.20)
    p.add_argument("--otm-pct", type=float, default=0.08)
    p.add_argument("--period-days", type=int, default=21)
    p.add_argument("--strategy", choices=list(STRATEGY_LABELS.keys()) + ["both"], default="both")
    args = p.parse_args()

    strategies = list(STRATEGY_LABELS.keys()) if args.strategy == "both" else [args.strategy]

    print(f"Running {args.paths} independent synthetic paths per scenario "
          f"(seeds 0..{args.paths - 1})")
    print(f"Assumptions: annual_vol={args.annual_vol:.0%}, iv={args.iv:.0%}, "
          f"otm_pct={args.otm_pct:.0%}, period_days={args.period_days}\n")

    for strategy in strategies:
        for scenario_name, drift in SCENARIOS.items():
            excess_list = [
                run_trial(strategy, seed, args.start_price, args.days, drift,
                           args.annual_vol, args.otm_pct, args.iv, args.period_days)
                for seed in range(args.paths)
            ]
            summarize(strategy, scenario_name, excess_list)


if __name__ == "__main__":
    main()
