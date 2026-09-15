#!/usr/bin/env python3
"""Does a realistic per-contract commission erase the one corner that works?

joint_sensitivity.py (9/10) found exactly one cell across every sweep in
this track where covered calls beat buy-and-hold *on average*, not just on
a majority of paths: 2%-OTM strikes on a 5-day cycle. That corner works
because a near-ATM strike prices real premium relative to a *weekly*
expected move -- but the same mechanism means it trades ~4x more often
than the 21-day default (100 periods vs ~24 over the same 2-year span).
The README's own limitations list has always flagged "no commissions or
assignment fees" as unmodeled. sim.py now accepts `commission_per_contract`
(a flat per-contract fee deducted every period a contract is sold, see
sim.py's docstring) -- this sweeps it specifically against that one
positive-average cell and the 21-day default, to see whether trading more
often to find an edge just hands the edge to a broker instead.

Usage:
    python3 commission_sensitivity.py --paths 60
"""
import argparse
import statistics

from sim import generate_price_path, simulate_covered_calls, SCENARIOS

DEFAULT_COMMISSIONS = [0.0, 0.65, 2.0, 5.0, 8.0]

CELLS = {
    "corner (2% OTM / 5d cycle)": (0.02, 5),
    "default (8% OTM / 21d cycle)": (0.08, 21),
}


def run_trial(seed, otm_pct, period_days, commission, start_price, days,
              annual_drift, annual_vol, iv):
    prices = generate_price_path(seed, start_price, days, annual_drift, annual_vol)
    result = simulate_covered_calls(prices, otm_pct, iv, period_days, 100, commission)
    initial_equity = 100 * prices[0]
    strategy_pct = (result["final_equity"] / initial_equity - 1) * 100
    buy_hold_pct = (100 * result["final_price"] / initial_equity - 1) * 100
    return strategy_pct - buy_hold_pct, result["periods"]


def summarize(excess_list):
    wins = sum(1 for e in excess_list if e >= 0)
    n = len(excess_list)
    return {
        "win_rate": 100 * wins / n,
        "avg_excess_pts": statistics.mean(excess_list),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=int, default=60, help="independent seeds per point (default 60)")
    p.add_argument("--commissions", type=str, default=",".join(str(c) for c in DEFAULT_COMMISSIONS),
                    help="comma-separated flat per-contract commissions in dollars")
    p.add_argument("--start-price", type=float, default=100.0)
    p.add_argument("--days", type=int, default=504)
    p.add_argument("--annual-vol", type=float, default=0.25)
    p.add_argument("--iv", type=float, default=0.20)
    p.add_argument("--scenarios", type=str, default="uptrend,downtrend",
                    help="comma-separated scenario names from sim.py's SCENARIOS")
    args = p.parse_args()

    commissions = [float(c) for c in args.commissions.split(",")]
    scenario_names = args.scenarios.split(",")

    print("Covered-call commission sensitivity -- corner vs. default cell")
    print(f"{args.paths} seeds per point, {args.days} trading days, "
          f"annual_vol={args.annual_vol:.0%}, iv={args.iv:.0%}\n")

    for scenario_name in scenario_names:
        annual_drift = SCENARIOS[scenario_name]
        print(f"--- Scenario: {scenario_name} ---")
        for cell_name, (otm_pct, period_days) in CELLS.items():
            row = []
            periods = None
            for commission in commissions:
                excess_list = []
                for seed in range(args.paths):
                    excess, periods = run_trial(
                        seed, otm_pct, period_days, commission, args.start_price,
                        args.days, annual_drift, args.annual_vol, args.iv,
                    )
                    excess_list.append(excess)
                row.append(summarize(excess_list))
            print(f"  {cell_name} ({periods} periods/path):")
            header = "    commission " + "".join(f"  ${c:>6.2f}" for c in commissions)
            print(header)
            win_row = "    win rate   " + "".join(f"  {r['win_rate']:>6.0f}%" for r in row)
            excess_row = "    avg excess" + "".join(f" {r['avg_excess_pts']:>+7.2f}p" for r in row)
            print(win_row)
            print(excess_row)
        print()


if __name__ == "__main__":
    main()
