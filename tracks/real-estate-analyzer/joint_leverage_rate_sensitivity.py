#!/usr/bin/env python3
"""Does leverage (down-payment %) and rate risk interact, stdlib only?

`leverage_sensitivity.py` sweeps down_payment_pct through the 10-year Monte
Carlo, holding interest_rate_pct fixed at each deal's own quoted rate.
`analyze.py --sensitivity` sweeps purchase price and interest rate through a
Year-1 snapshot, holding down_payment_pct fixed at the deal's own value.
Neither ever varies both of a buyer's real, simultaneous uncertainties at
once: how much of your own cash to put down, and what rate you actually lock
in. This sweeps both together through the same 10-year survivability model,
the same "joint grid" idea used for options-income-sim's OTM%/cycle-length
levers -- to see whether a lower down payment is equally risky at every rate,
or whether low-down-payment and a higher-than-quoted rate compound into a
worse combination than either 1-D sweep would suggest.

Usage:
    python3 joint_leverage_rate_sensitivity.py --csv sample_deals.csv
    python3 joint_leverage_rate_sensitivity.py --csv sample_deals.csv --down-pcts 10,20,30 --rate-deltas -1.5,0,1.5 --trials 1000
"""
import argparse

from analyze import analyze_deal, load_csv
from monte_carlo import run_monte_carlo

DEFAULT_DOWN_PCTS = [10, 20, 30]
DEFAULT_RATE_DELTAS = [-1.5, 0, 1.5]


def run_cell(deal, down_pct, rate_delta, years, trials, seed):
    variant = dict(deal)
    variant["down_payment_pct"] = down_pct
    variant["interest_rate_pct"] = max(deal["interest_rate_pct"] + rate_delta, 0.0)
    year1 = analyze_deal(variant)
    mc = run_monte_carlo(variant, years, trials, seed)
    return {
        "cash_on_cash_pct": year1["cash_on_cash_pct"],
        "monthly_cash_flow_year1": year1["monthly_cash_flow"],
        "pct_trials_with_a_negative_year": mc["pct_trials_with_a_negative_year"],
        "median_cumulative_cash_flow": mc["median_cumulative_cash_flow"],
    }


def print_grid(deal_name, down_pcts, rate_labels, grid, metric_key, fmt, title):
    print(f"--- {deal_name}: {title} ---")
    row_label_width = 10
    col_width = max(12, max(len(h) for h in rate_labels) + 2)
    header = " " * row_label_width + "".join(h.rjust(col_width) for h in rate_labels)
    print(header)
    for down_pct, row in zip(down_pcts, grid):
        row_label = f"{down_pct:.0f}% down".ljust(row_label_width)
        cells = "".join(fmt(cell[metric_key]).rjust(col_width) for cell in row)
        print(row_label + cells)
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, help="Path to a CSV of deals (same format as analyze.py).")
    p.add_argument("--down-pcts", type=str, default=",".join(str(x) for x in DEFAULT_DOWN_PCTS),
                    help="comma-separated down-payment percentages to sweep")
    p.add_argument("--rate-deltas", type=str, default=",".join(str(x) for x in DEFAULT_RATE_DELTAS),
                    help="comma-separated rate offsets in percentage points from each deal's own quoted rate")
    p.add_argument("--years", type=int, default=10)
    p.add_argument("--trials", type=int, default=1000, help="Monte Carlo trials per grid cell (default 1000)")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    down_pcts = [float(x) for x in args.down_pcts.split(",")]
    rate_deltas = [float(x) for x in args.rate_deltas.split(",")]
    deals = load_csv(args.csv)

    print("Joint down-payment x interest-rate sensitivity -- 10-year survivability")
    print(f"{args.trials} Monte Carlo trials per cell\n")

    for deal in deals:
        rate_labels = [f"{deal['interest_rate_pct'] + d:.2f}%" + (" (base)" if d == 0 else "")
                        for d in rate_deltas]
        grid = []
        for down_pct in down_pcts:
            row = [run_cell(deal, down_pct, delta, args.years, args.trials, args.seed)
                   for delta in rate_deltas]
            grid.append(row)

        print_grid(deal["name"], down_pcts, rate_labels, grid,
                    "pct_trials_with_a_negative_year",
                    lambda v: f"{v:.1f}%", "% of trials with a negative-cash-flow year")
        print_grid(deal["name"], down_pcts, rate_labels, grid,
                    "median_cumulative_cash_flow",
                    lambda v: f"${v:,.0f}", f"median cumulative {args.years}yr cash flow")


if __name__ == "__main__":
    main()
