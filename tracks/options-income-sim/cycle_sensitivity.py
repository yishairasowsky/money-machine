#!/usr/bin/env python3
"""Does the option-cycle length (period_days) change the covered-call/wheel
verdict, stdlib only?

Every other analysis in this track fixes the option cycle at 21 trading
days (~monthly) and varies the scenario, the seed, or the strike distance.
But period_days is not a fact about the market either -- it is the other
real decision an option seller makes each round, alongside strike distance:
sell weekly, biweekly, monthly, or longer-dated contracts? Shorter cycles
mean more frequent premium collection (and more frequent assignment
decisions); longer cycles mean fewer, larger premiums and longer stretches
locked into one strike. This sweeps period_days across a realistic weekly-
to-quarterly range, at multiple seeds per point, for both strategies, to
see whether the "covered calls/wheel underperform in an uptrend" findings
depend on how often you're rolling contracts.

Usage:
    python3 cycle_sensitivity.py
    python3 cycle_sensitivity.py --paths 30 --periods 5,10,21,42,63 --strategy wheel
"""
import argparse
import statistics

from sim import generate_price_path, simulate_covered_calls, simulate_wheel, SCENARIOS

SIMULATORS = {
    "covered-call": simulate_covered_calls,
    "wheel": simulate_wheel,
}


def run_trial(seed, period_days, start_price, days, annual_drift, annual_vol, otm_pct, iv, strategy):
    prices = generate_price_path(seed, start_price, days, annual_drift, annual_vol)
    simulate = SIMULATORS[strategy]
    result = simulate(prices, otm_pct, iv, period_days)
    initial_equity = 100 * prices[0]
    strategy_pct = (result["final_equity"] / initial_equity - 1) * 100
    buy_hold_pct = (100 * result["final_price"] / initial_equity - 1) * 100
    premium_pct = (result["total_premium"] / initial_equity) * 100
    return strategy_pct - buy_hold_pct, premium_pct, result["periods"]


def summarize(scenario_name, period_days, excess_list, premium_list, periods_list):
    wins = sum(1 for e in excess_list if e >= 0)
    n = len(excess_list)
    return {
        "scenario": scenario_name,
        "period_days": period_days,
        "win_rate": 100 * wins / n,
        "avg_excess_pts": statistics.mean(excess_list),
        "worst_excess_pts": min(excess_list),
        "avg_premium_pct": statistics.mean(premium_list),
        "avg_periods": statistics.mean(periods_list),
    }


def print_table(rows, scenario_name):
    print(f"--- Scenario: {scenario_name} ---")
    print(f"{'Cycle':>7}  {'Win rate':>9}  {'Avg excess':>11}  {'Worst excess':>13}  {'Avg premium':>12}  {'Avg #cycles':>11}")
    for r in rows:
        print(f"{r['period_days']:5d}d  {r['win_rate']:8.1f}%  "
              f"{r['avg_excess_pts']:+10.2f}p  {r['worst_excess_pts']:+12.2f}p  "
              f"{r['avg_premium_pct']:11.2f}%  {r['avg_periods']:11.1f}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=30, help="independent seeds per cycle length (default 30)")
    p.add_argument("--periods", type=str, default="5,10,21,42,63",
                    help="comma-separated option-cycle lengths in trading days to sweep "
                         "(default: ~weekly, ~biweekly, ~monthly, ~6-week, ~quarterly)")
    p.add_argument("--start-price", type=float, default=100.0)
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--iv", type=float, default=0.20)
    p.add_argument("--otm-pct", type=float, default=0.08)
    p.add_argument("--scenarios", type=str, default="uptrend,downtrend",
                    help="comma-separated scenario names from sim.py's SCENARIOS (default: the two extremes where the trade-off is clearest)")
    p.add_argument("--strategy", choices=list(SIMULATORS.keys()), default="covered-call",
                    help="'covered-call' (default) or 'wheel'")
    args = p.parse_args()

    period_lengths = [int(x) for x in args.periods.split(",")]
    scenario_names = args.scenarios.split(",")

    label = "Covered-call" if args.strategy == "covered-call" else "Wheel"
    print(f"{label} option-cycle-length (period_days) sensitivity")
    print(f"{args.paths} seeds per point, {args.days} trading days, "
          f"annual_vol={args.annual_vol:.0%}, iv={args.iv:.0%}, otm_pct={args.otm_pct:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        rows = []
        for period_days in period_lengths:
            excess_list = []
            premium_list = []
            periods_list = []
            for seed in range(args.paths):
                excess, premium, periods = run_trial(
                    seed, period_days, args.start_price, args.days, annual_drift,
                    args.annual_vol, args.otm_pct, args.iv, args.strategy,
                )
                excess_list.append(excess)
                premium_list.append(premium)
                periods_list.append(periods)
            rows.append(summarize(scenario_name, period_days, excess_list, premium_list, periods_list))
        print_table(rows, scenario_name)


if __name__ == "__main__":
    main()
