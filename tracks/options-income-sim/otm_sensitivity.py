#!/usr/bin/env python3
"""How much does the strike-distance choice (otm_pct) change the covered-call
verdict, stdlib only?

Every other analysis in this track (the base report, robustness_test.py)
holds otm_pct fixed at a single default (8%) and varies either the scenario
or the random seed. But otm_pct is not an exogenous fact about the market —
it is the one concrete decision a real covered-call seller actually makes
each period ("how far above spot do I sell my strike?"). This script sweeps
that decision across a realistic range, at multiple seeds per point, to see
whether the "covered calls underperform in an uptrend" finding is robust to
that choice or just an artifact of the 8% default.

Usage:
    python3 otm_sensitivity.py
    python3 otm_sensitivity.py --paths 30 --otm-pcts 0.02,0.05,0.08,0.12,0.16,0.20
"""
import argparse
import statistics

from sim import generate_price_path, simulate_covered_calls, SCENARIOS


def run_trial(seed, otm_pct, start_price, days, annual_drift, annual_vol, iv, period_days):
    prices = generate_price_path(seed, start_price, days, annual_drift, annual_vol)
    result = simulate_covered_calls(prices, otm_pct, iv, period_days)
    initial_equity = 100 * prices[0]
    strategy_pct = (result["final_equity"] / initial_equity - 1) * 100
    buy_hold_pct = (100 * result["final_price"] / initial_equity - 1) * 100
    premium_pct = (result["total_premium"] / initial_equity) * 100
    return strategy_pct - buy_hold_pct, premium_pct


def summarize(scenario_name, otm_pct, excess_list, premium_list):
    wins = sum(1 for e in excess_list if e >= 0)
    n = len(excess_list)
    return {
        "scenario": scenario_name,
        "otm_pct": otm_pct,
        "win_rate": 100 * wins / n,
        "avg_excess_pts": statistics.mean(excess_list),
        "worst_excess_pts": min(excess_list),
        "avg_premium_pct": statistics.mean(premium_list),
    }


def print_table(rows, scenario_name):
    print(f"--- Scenario: {scenario_name} ---")
    print(f"{'OTM %':>7}  {'Win rate':>9}  {'Avg excess':>11}  {'Worst excess':>13}  {'Avg premium':>12}")
    for r in rows:
        print(f"{r['otm_pct']*100:6.0f}%  {r['win_rate']:8.1f}%  "
              f"{r['avg_excess_pts']:+10.2f}p  {r['worst_excess_pts']:+12.2f}p  "
              f"{r['avg_premium_pct']:11.2f}%")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=25, help="independent seeds per OTM level (default 25)")
    p.add_argument("--otm-pcts", type=str, default="0.02,0.05,0.08,0.12,0.16,0.20",
                    help="comma-separated OTM fractions to sweep (default covers the 8%% default plus tighter/wider strikes)")
    p.add_argument("--start-price", type=float, default=100.0)
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--iv", type=float, default=0.20)
    p.add_argument("--period-days", type=int, default=21)
    p.add_argument("--scenarios", type=str, default="uptrend,downtrend",
                    help="comma-separated scenario names from sim.py's SCENARIOS (default: the two extremes where the trade-off is clearest)")
    args = p.parse_args()

    otm_pcts = [float(x) for x in args.otm_pcts.split(",")]
    scenario_names = args.scenarios.split(",")

    print("Covered-call strike-distance (OTM %) sensitivity")
    print(f"{args.paths} seeds per point, {args.days} trading days, "
          f"annual_vol={args.annual_vol:.0%}, iv={args.iv:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        rows = []
        for otm_pct in otm_pcts:
            excess_list = []
            premium_list = []
            for seed in range(args.paths):
                excess, premium = run_trial(
                    seed, otm_pct, args.start_price, args.days, annual_drift,
                    args.annual_vol, args.iv, args.period_days,
                )
                excess_list.append(excess)
                premium_list.append(premium)
            rows.append(summarize(scenario_name, otm_pct, excess_list, premium_list))
        print_table(rows, scenario_name)


if __name__ == "__main__":
    main()
