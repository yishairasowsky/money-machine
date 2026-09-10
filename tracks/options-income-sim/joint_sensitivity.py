#!/usr/bin/env python3
"""Do covered calls' two escape hatches (OTM% and cycle length) stack, or fight?

`otm_sensitivity.py` swept strike distance holding period_days at the 21-day
default. `cycle_sensitivity.py` swept period_days holding otm_pct at the
8% default. Both found an independent escape hatch for covered calls in an
uptrend (wider OTM, or a shorter cycle) -- but neither ever varied the other
lever at the same time, so it's still an open question whether combining
them compounds the benefit, or whether they're actually the same mechanism
wearing two names (cycle_sensitivity's own README section already flags that
its escape works by shrinking the *effective* moneyness of a fixed OTM%, the
same lever otm_sensitivity turns directly) -- in which case stacking them
might not add much, or could even overshoot into near-zero premium territory
from both directions at once.

This sweeps a small OTM% x period_days grid (not the full 5x5 -- 3x3 is
enough to see whether the surface is additive, saturating, or non-monotonic)
for covered calls in the uptrend scenario, the regime where both individual
levers showed an effect.

Usage:
    python3 joint_sensitivity.py
    python3 joint_sensitivity.py --paths 30 --strategy wheel
"""
import argparse
import statistics

from sim import generate_price_path, simulate_covered_calls, simulate_wheel, SCENARIOS

SIMULATORS = {
    "covered-call": simulate_covered_calls,
    "wheel": simulate_wheel,
}


def run_trial(seed, otm_pct, period_days, start_price, days, annual_drift,
              annual_vol, iv, strategy):
    prices = generate_price_path(seed, start_price, days, annual_drift, annual_vol)
    simulate = SIMULATORS[strategy]
    result = simulate(prices, otm_pct, iv, period_days)
    initial_equity = 100 * prices[0]
    strategy_pct = (result["final_equity"] / initial_equity - 1) * 100
    buy_hold_pct = (100 * result["final_price"] / initial_equity - 1) * 100
    premium_pct = (result["total_premium"] / initial_equity) * 100
    return strategy_pct - buy_hold_pct, premium_pct


def summarize(excess_list, premium_list):
    wins = sum(1 for e in excess_list if e >= 0)
    n = len(excess_list)
    return {
        "win_rate": 100 * wins / n,
        "avg_excess_pts": statistics.mean(excess_list),
        "avg_premium_pct": statistics.mean(premium_list),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent seeds per grid cell (default 30)")
    p.add_argument("--otm-pcts", type=str, default="0.02,0.08,0.20",
                    help="comma-separated OTM%% values to sweep (default: the low/default/high points already tested individually)")
    p.add_argument("--periods", type=str, default="5,21,63",
                    help="comma-separated period_days values to sweep (default: weekly/monthly/quarterly)")
    p.add_argument("--start-price", type=float, default=100.0)
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--iv", type=float, default=0.20)
    p.add_argument("--scenario", type=str, default="uptrend",
                    help="scenario name from sim.py's SCENARIOS (default: uptrend, where both individual levers showed an effect)")
    p.add_argument("--strategy", choices=list(SIMULATORS.keys()), default="covered-call")
    args = p.parse_args()

    otm_pcts = [float(x) for x in args.otm_pcts.split(",")]
    period_lengths = [int(x) for x in args.periods.split(",")]
    annual_drift = SCENARIOS[args.scenario]

    label = "Covered-call" if args.strategy == "covered-call" else "Wheel"
    print(f"{label} joint OTM% x cycle-length sensitivity -- scenario: {args.scenario}")
    print(f"{args.paths} seeds per cell, {args.days} trading days, "
          f"annual_vol={args.annual_vol:.0%}, iv={args.iv:.0%}\n")

    grid = {}
    for otm_pct in otm_pcts:
        for period_days in period_lengths:
            excess_list = []
            premium_list = []
            for seed in range(args.paths):
                excess, premium = run_trial(
                    seed, otm_pct, period_days, args.start_price, args.days,
                    annual_drift, args.annual_vol, args.iv, args.strategy,
                )
                excess_list.append(excess)
                premium_list.append(premium)
            grid[(otm_pct, period_days)] = summarize(excess_list, premium_list)

    for metric, fmt in [("win_rate", "{:.0f}%"), ("avg_excess_pts", "{:+.2f}p"), ("avg_premium_pct", "{:.2f}%")]:
        print(f"--- {metric} ---")
        corner = "OTM% / cycle"
        header = f"{corner:>14}" + "".join(f"{str(pd) + 'd':>10}" for pd in period_lengths)
        print(header)
        for otm_pct in otm_pcts:
            row = f"{otm_pct:>13.0%} "
            for period_days in period_lengths:
                row += f"{fmt.format(grid[(otm_pct, period_days)][metric]):>10}"
            print(row)
        print()


if __name__ == "__main__":
    main()
