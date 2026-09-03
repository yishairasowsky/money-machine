#!/usr/bin/env python3
"""How much does the down-payment percentage (leverage) change a deal's
multi-year survivability, stdlib only?

`--sensitivity` (in analyze.py) sweeps purchase price and interest rate --
two things you don't fully control before you've made an offer and locked a
rate. `monte_carlo.py` sweeps time -- ordinary rent/expense variance over a
multi-year hold, at whatever down payment % the deal was analyzed with. This
script sweeps the one input that's neither: down_payment_pct is the actual
decision a real buyer makes (how much of their own cash to put down vs.
borrow), the same way OTM% was the covered-call seller's decision and the
SMA window pair was the trader's decision in this repo's other two tracks.

More down payment -> smaller loan -> smaller mortgage payment -> more cash
flow cushion, but more of the buyer's own cash tied up for the same rental
income (lower cash-on-cash return). Less down payment is the opposite trade.
This runs monte_carlo.py's 10-year survivability simulation at several
down-payment percentages per deal to see how that trade-off actually plays
out, instead of assuming it.

Usage:
    python3 leverage_sensitivity.py --csv sample_deals.csv
    python3 leverage_sensitivity.py --csv sample_deals.csv --down-pcts 10,15,20,25,30,40 --trials 1000
"""
import argparse

from analyze import analyze_deal, load_csv
from monte_carlo import run_monte_carlo

DEFAULT_DOWN_PCTS = [10, 15, 20, 25, 30, 40]


def run_for_down_pct(deal, down_pct, years, trials, seed):
    variant = dict(deal)
    variant["down_payment_pct"] = down_pct
    year1 = analyze_deal(variant)
    mc = run_monte_carlo(variant, years, trials, seed)
    return {
        "down_pct": down_pct,
        "cash_on_cash_pct": year1["cash_on_cash_pct"],
        "monthly_cash_flow_year1": year1["monthly_cash_flow"],
        "pct_trials_with_a_negative_year": mc["pct_trials_with_a_negative_year"],
        "median_cumulative_cash_flow": mc["median_cumulative_cash_flow"],
    }


def print_table(deal_name, rows):
    print(f"--- {deal_name} ---")
    print(f"{'Down %':>7}  {'Cash-on-cash':>13}  {'Yr1 cash flow':>14}  "
          f"{'Neg-year trials':>16}  {'Median 10yr total':>18}")
    for r in rows:
        print(f"{r['down_pct']:6.0f}%  {r['cash_on_cash_pct']:12.2f}%  "
              f"${r['monthly_cash_flow_year1']:12,.0f}  "
              f"{r['pct_trials_with_a_negative_year']:15.1f}%  "
              f"${r['median_cumulative_cash_flow']:16,.0f}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, help="Path to a CSV of deals (same format as analyze.py).")
    p.add_argument("--down-pcts", type=str, default=",".join(str(x) for x in DEFAULT_DOWN_PCTS),
                    help="comma-separated down-payment percentages to sweep")
    p.add_argument("--years", type=int, default=10)
    p.add_argument("--trials", type=int, default=1000, help="Monte Carlo trials per down-payment level (default 1000)")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    down_pcts = [float(x) for x in args.down_pcts.split(",")]
    deals = load_csv(args.csv)

    print("Down-payment (leverage) sensitivity -- 10-year survivability at each level")
    print(f"{args.trials} Monte Carlo trials per point\n")

    for deal in deals:
        rows = [run_for_down_pct(deal, pct, args.years, args.trials, args.seed) for pct in down_pcts]
        print_table(deal["name"], rows)


if __name__ == "__main__":
    main()
