#!/usr/bin/env python3
"""Does the cash-flow verdict (BAD/MARGINAL/GOOD) match the total-return picture at exit?

analyze.py's verdict() labels a deal by year-1 cash flow alone. monte_carlo.py's own
docstring already flags the gap: "No appreciation or resale is modeled -- this measures
cash-flow survivability during the hold, not total return." Selling a property also has
a real cost this tool has never modeled: a realtor commission (typically 5-6%) plus
closing costs on the sale, on top of paying off whatever loan balance remains.

This adds remaining_loan_balance() and exit_proceeds() to analyze.py and uses them here
to answer the question buy-and-hold investors actually care about: after N years, sell
the property, pay off the loan, pay the realtor, and compare (cumulative cash flow
during the hold) + (net sale proceeds) against (total cash invested). Does the deal
analyze.py calls "bad" on cash flow alone turn out fine once appreciation is counted --
or does the deal it calls "good" turn out to depend on appreciation just to break even,
once selling costs are counted?

This is a simplified, deterministic total-return model: it holds rent and expenses flat
(no growth/inflation -- see monte_carlo.py for that) and applies a single compounding
appreciation rate to the purchase price. It is meant to isolate the effect of exit
costs and appreciation, not to combine with monte_carlo.py's variance model.

Usage:
    python3 total_return_test.py --csv sample_deals.csv
    python3 total_return_test.py --csv sample_deals.csv --years 10 --appreciation 0,2,4
"""
import argparse

from analyze import analyze_deal, exit_proceeds, load_csv

DEFAULT_APPRECIATION_PCTS = [0.0, 2.0, 4.0]
DEFAULT_SELLING_COST_PCT = 6.0


def total_return(deal, years_held, appreciation_pct, selling_cost_pct):
    result = analyze_deal(deal)
    cumulative_cash_flow = result["annual_cash_flow"] * years_held
    exit_result = exit_proceeds(deal, result, years_held, appreciation_pct, selling_cost_pct)
    total_profit = (
        cumulative_cash_flow + exit_result["net_sale_proceeds"] - result["total_cash_invested"]
    )
    total_return_pct = (
        (total_profit / result["total_cash_invested"] * 100)
        if result["total_cash_invested"] else 0.0
    )
    return {
        "cash_flow_verdict_positive": result["monthly_cash_flow"] >= 0,
        "cumulative_cash_flow": cumulative_cash_flow,
        "total_cash_invested": result["total_cash_invested"],
        "total_profit": total_profit,
        "total_return_pct": total_return_pct,
        **exit_result,
    }


def print_result(deal, years_held, selling_cost_pct, appreciation_pcts):
    cf_verdict = "positive" if analyze_deal(deal)["monthly_cash_flow"] >= 0 else "negative"
    print(f"=== {deal['name']} -- {years_held}yr hold, {selling_cost_pct:.0f}% selling cost "
          f"(year-1 cash flow: {cf_verdict}) ===")
    for appreciation_pct in appreciation_pcts:
        r = total_return(deal, years_held, appreciation_pct, selling_cost_pct)
        print(f"  {appreciation_pct:.1f}%/yr appreciation:  "
              f"total return {r['total_return_pct']:+.1f}%  "
              f"(cash flow during hold ${r['cumulative_cash_flow']:,.0f}, "
              f"net sale proceeds ${r['net_sale_proceeds']:,.0f}, "
              f"invested ${r['total_cash_invested']:,.0f})")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, help="Path to a CSV of deals (same format as analyze.py).")
    p.add_argument("--years", type=int, default=7, help="Hold length in years before selling (default 7)")
    p.add_argument("--appreciation", type=str, default=",".join(str(a) for a in DEFAULT_APPRECIATION_PCTS),
                    help="comma-separated annual appreciation %% scenarios")
    p.add_argument("--selling-cost-pct", type=float, default=DEFAULT_SELLING_COST_PCT,
                    help="realtor commission + closing costs on sale, %% of sale price (default 6)")
    args = p.parse_args()

    appreciation_pcts = [float(a) for a in args.appreciation.split(",")]
    deals = load_csv(args.csv)

    print("Total-return test: cumulative cash flow + net sale proceeds vs. cash invested")
    print(f"({args.years}yr hold, {args.selling_cost_pct:.0f}% selling cost, rent/expenses held "
          f"flat -- no growth/inflation, see monte_carlo.py for that)\n")

    for deal in deals:
        print_result(deal, args.years, args.selling_cost_pct, appreciation_pcts)


if __name__ == "__main__":
    main()
