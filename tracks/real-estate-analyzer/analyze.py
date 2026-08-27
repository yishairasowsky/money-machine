#!/usr/bin/env python3
"""Rental property deal screener, stdlib only.

Computes standard buy-and-hold rental metrics for a deal: monthly mortgage
payment (amortization formula), monthly cash flow, cap rate, cash-on-cash
return, and a year-1 summary. This tool only analyzes numbers you type in
or put in a CSV — it never looks up a real listing, never talks to a
lender, and never touches real money.

Usage:
    python3 analyze.py --csv sample_deals.csv
    python3 analyze.py --price 300000 --down-pct 20 --rate 7.0 --term 30 \\
        --rent 2400 --tax 3600 --insurance 1400 --maintenance-pct 5 \\
        --vacancy-pct 5 --management-pct 8 --hoa 0 --closing-pct 3

CSV columns (header row required), all numeric except name:
    name,purchase_price,down_payment_pct,interest_rate_pct,loan_term_years,
    monthly_rent,property_tax_annual,insurance_annual,maintenance_pct,
    vacancy_pct,management_pct,monthly_hoa,closing_cost_pct

maintenance_pct, vacancy_pct, management_pct, closing_cost_pct are all
percentages (e.g. 5 means 5%), and maintenance/vacancy/management are
percent-of-rent rules of thumb, not itemized bids — see the README for
why that matters.
"""
import argparse
import csv
import sys

REQUIRED_CSV_FIELDS = [
    "name", "purchase_price", "down_payment_pct", "interest_rate_pct",
    "loan_term_years", "monthly_rent", "property_tax_annual",
    "insurance_annual", "maintenance_pct", "vacancy_pct",
    "management_pct", "monthly_hoa", "closing_cost_pct",
]


def monthly_mortgage_payment(loan_amount, annual_rate_pct, term_years):
    """Standard amortization formula for principal + interest only."""
    n = term_years * 12
    r = (annual_rate_pct / 100) / 12
    if n <= 0:
        return 0.0
    if r == 0:
        return loan_amount / n
    return loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def analyze_deal(deal):
    """deal is a dict of the fields listed in REQUIRED_CSV_FIELDS (numeric
    fields already coerced to float). Returns a dict of computed metrics."""
    price = deal["purchase_price"]
    down_pct = deal["down_payment_pct"]
    rent = deal["monthly_rent"]

    down_payment = price * down_pct / 100
    loan_amount = price - down_payment
    closing_costs = price * deal["closing_cost_pct"] / 100
    total_cash_invested = down_payment + closing_costs

    mortgage_pmt = monthly_mortgage_payment(
        loan_amount, deal["interest_rate_pct"], deal["loan_term_years"]
    )

    # Vacancy reduces the rent actually collected. Maintenance is commonly
    # budgeted as a % of gross scheduled rent (a rule of thumb, not a bid).
    # Management fees are typically charged on rent actually collected.
    effective_rent = rent * (1 - deal["vacancy_pct"] / 100)
    maintenance = rent * deal["maintenance_pct"] / 100
    management = effective_rent * deal["management_pct"] / 100
    property_tax = deal["property_tax_annual"] / 12
    insurance = deal["insurance_annual"] / 12
    hoa = deal["monthly_hoa"]

    operating_expenses = maintenance + management + property_tax + insurance + hoa

    noi_monthly = effective_rent - operating_expenses
    noi_annual = noi_monthly * 12

    monthly_cash_flow = noi_monthly - mortgage_pmt
    annual_cash_flow = monthly_cash_flow * 12

    cap_rate = (noi_annual / price * 100) if price else 0.0
    cash_on_cash = (
        (annual_cash_flow / total_cash_invested * 100)
        if total_cash_invested else 0.0
    )

    return {
        "name": deal["name"],
        "purchase_price": price,
        "down_payment": down_payment,
        "closing_costs": closing_costs,
        "total_cash_invested": total_cash_invested,
        "loan_amount": loan_amount,
        "mortgage_payment": mortgage_pmt,
        "effective_monthly_rent": effective_rent,
        "operating_expenses_monthly": operating_expenses,
        "noi_monthly": noi_monthly,
        "noi_annual": noi_annual,
        "monthly_cash_flow": monthly_cash_flow,
        "annual_cash_flow": annual_cash_flow,
        "cap_rate_pct": cap_rate,
        "cash_on_cash_pct": cash_on_cash,
    }


def verdict(result):
    coc = result["cash_on_cash_pct"]
    cf = result["monthly_cash_flow"]
    if cf < 0:
        return "BAD — negative monthly cash flow, this deal loses money every month as structured."
    if coc < 4:
        return "MARGINAL — cash flow is positive but thin; a single surprise expense could wipe it out."
    return "GOOD — solid positive cash flow and a healthy cash-on-cash return for this level of risk."


def print_result(r):
    print(f"=== {r['name']} ===")
    print(f"  Purchase price:          ${r['purchase_price']:,.0f}")
    print(f"  Down payment:            ${r['down_payment']:,.0f}")
    print(f"  Closing costs:           ${r['closing_costs']:,.0f}")
    print(f"  Total cash invested:     ${r['total_cash_invested']:,.0f}")
    print(f"  Loan amount:             ${r['loan_amount']:,.0f}")
    print(f"  Monthly mortgage (P&I):  ${r['mortgage_payment']:,.2f}")
    print(f"  Effective monthly rent:  ${r['effective_monthly_rent']:,.2f}  (after vacancy)")
    print(f"  Monthly operating exp.:  ${r['operating_expenses_monthly']:,.2f}  (tax+ins+maint+mgmt+hoa)")
    print(f"  Monthly NOI:             ${r['noi_monthly']:,.2f}")
    print(f"  Monthly cash flow:       ${r['monthly_cash_flow']:,.2f}  (after mortgage)")
    print(f"  Year-1 cash flow:        ${r['annual_cash_flow']:,.2f}")
    print(f"  Cap rate:                {r['cap_rate_pct']:.2f}%")
    print(f"  Cash-on-cash return:     {r['cash_on_cash_pct']:.2f}%")
    print(f"  Verdict:                 {verdict(r)}")
    print()



# Steps for --sensitivity: purchase price swept +/-10% in 5% increments,
# interest rate swept +/-1.5 percentage points in 0.75pp increments. These
# are meant to bracket realistic appraisal/negotiation and rate-quote
# uncertainty on a deal you haven't actually locked in yet, not extreme
# stress-test scenarios.
SENSITIVITY_PRICE_PCT_STEPS = [-10, -5, 0, 5, 10]
SENSITIVITY_RATE_PP_STEPS = [-1.5, -0.75, 0, 0.75, 1.5]


def sensitivity_grid(deal, price_pct_steps=None, rate_pp_steps=None):
    """Re-run analyze_deal() across a grid of purchase price x interest rate
    variations around this deal's own numbers. Returns
    (price_list, rate_list, results) where results[i][j] is the
    analyze_deal() output for price_list[i] and rate_list[j]. Every other
    input (rent, taxes, down-payment %, etc.) is held fixed at the deal's
    own values, so this isolates the two inputs that are hardest to know
    exactly before you've actually made an offer and locked a rate."""
    price_pct_steps = price_pct_steps if price_pct_steps is not None else SENSITIVITY_PRICE_PCT_STEPS
    rate_pp_steps = rate_pp_steps if rate_pp_steps is not None else SENSITIVITY_RATE_PP_STEPS

    base_price = deal["purchase_price"]
    base_rate = deal["interest_rate_pct"]

    price_list = [base_price * (1 + pct / 100) for pct in price_pct_steps]
    rate_list = [max(base_rate + pp, 0.0) for pp in rate_pp_steps]

    results = []
    for price in price_list:
        row = []
        for rate in rate_list:
            variant = dict(deal)
            variant["purchase_price"] = price
            variant["interest_rate_pct"] = rate
            row.append(analyze_deal(variant))
        results.append(row)

    return price_list, rate_list, results


def print_sensitivity(deal):
    price_list, rate_list, results = sensitivity_grid(deal)

    col_headers = [f"{rate:.2f}%" for rate in rate_list]
    row_label_width = 15
    col_width = max(10, max(len(h) for h in col_headers) + 2)

    print(f"--- Sensitivity: {deal['name']} ---")
    print(f"(base: price ${deal['purchase_price']:,.0f}, rate {deal['interest_rate_pct']:.2f}% "
          f"-- rows vary price +/-10%, columns vary rate +/-1.5pp)")

    for label, key, fmt in [
        ("Cash-on-cash %", "cash_on_cash_pct", lambda v: f"{v:.2f}%"),
        ("Monthly cash flow", "monthly_cash_flow", lambda v: f"${v:,.0f}"),
    ]:
        print(f"  {label}:")
        header = " " * row_label_width + "".join(h.rjust(col_width) for h in col_headers)
        print("  " + header)
        for price, row in zip(price_list, results):
            row_label = f"${price:,.0f}".ljust(row_label_width)
            cells = "".join(fmt(r[key]).rjust(col_width) for r in row)
            print("  " + row_label + cells)
        print()

    base_row_idx = price_list.index(deal["purchase_price"])
    base_row = results[base_row_idx]
    flips_at_base_price = sorted(
        rate_list[j] for j, r in enumerate(base_row) if r["monthly_cash_flow"] < 0
    )
    any_negative = any(r["monthly_cash_flow"] < 0 for row in results for r in row)

    if flips_at_base_price:
        print(f"  Note: at this deal's base purchase price (${deal['purchase_price']:,.0f}), "
              f"cash flow turns negative once the rate reaches roughly "
              f"{min(flips_at_base_price):.2f}% or higher in this grid.")
    elif any_negative:
        print("  Note: cash flow stays positive at the base purchase price across this "
              "rate range, but turns negative for some price/rate combinations in the grid.")
    else:
        print("  Note: cash flow stays positive across this entire price/rate grid.")
    print()


def load_csv(path):
    deals = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            missing = [k for k in REQUIRED_CSV_FIELDS if k not in row]
            if missing:
                print(f"CSV missing columns: {missing}", file=sys.stderr)
                sys.exit(1)
            deal = {"name": row["name"]}
            for k in REQUIRED_CSV_FIELDS[1:]:
                deal[k] = float(row[k])
            deals.append(deal)
    return deals


def build_arg_parser():
    p = argparse.ArgumentParser(description="Rental property deal screener (paper-only, no real transactions).")
    p.add_argument("--csv", help="Path to a CSV of deals (see REQUIRED_CSV_FIELDS / README).")
    p.add_argument("--name", default="Deal")
    p.add_argument("--price", type=float, help="Purchase price ($)")
    p.add_argument("--down-pct", type=float, help="Down payment (%% of price)")
    p.add_argument("--rate", type=float, help="Mortgage interest rate (annual %%)")
    p.add_argument("--term", type=float, default=30, help="Loan term (years), default 30")
    p.add_argument("--rent", type=float, help="Gross monthly rent ($)")
    p.add_argument("--tax", type=float, default=0.0, help="Annual property tax ($)")
    p.add_argument("--insurance", type=float, default=0.0, help="Annual insurance ($)")
    p.add_argument("--maintenance-pct", type=float, default=5.0, help="Maintenance, %% of gross rent, default 5")
    p.add_argument("--vacancy-pct", type=float, default=5.0, help="Vacancy rate, %% of rent, default 5")
    p.add_argument("--management-pct", type=float, default=0.0, help="Property management, %% of collected rent, default 0 (self-managed)")
    p.add_argument("--hoa", type=float, default=0.0, help="Monthly HOA/condo fee ($), default 0")
    p.add_argument("--closing-pct", type=float, default=3.0, help="Closing costs, %% of price, default 3")
    p.add_argument("--sensitivity", action="store_true",
                    help="Also print a purchase-price x interest-rate sensitivity grid "
                         "(cash-on-cash %% and monthly cash flow) for each deal analyzed.")
    return p


def main():
    args = build_arg_parser().parse_args()

    if args.csv:
        deals = load_csv(args.csv)
    else:
        required = {"price": args.price, "down-pct": args.down_pct, "rate": args.rate, "rent": args.rent}
        missing = [k for k, v in required.items() if v is None]
        if missing:
            print(f"Missing required args: {missing} (or pass --csv instead)", file=sys.stderr)
            sys.exit(1)
        deals = [{
            "name": args.name,
            "purchase_price": args.price,
            "down_payment_pct": args.down_pct,
            "interest_rate_pct": args.rate,
            "loan_term_years": args.term,
            "monthly_rent": args.rent,
            "property_tax_annual": args.tax,
            "insurance_annual": args.insurance,
            "maintenance_pct": args.maintenance_pct,
            "vacancy_pct": args.vacancy_pct,
            "management_pct": args.management_pct,
            "monthly_hoa": args.hoa,
            "closing_cost_pct": args.closing_pct,
        }]

    results = [analyze_deal(d) for d in deals]
    for r in results:
        print_result(r)

    if args.sensitivity:
        for d in deals:
            print_sensitivity(d)

    if len(results) > 1:
        best = max(results, key=lambda r: r["cash_on_cash_pct"])
        worst = min(results, key=lambda r: r["cash_on_cash_pct"])
        print(f"Best cash-on-cash:  {best['name']} ({best['cash_on_cash_pct']:.2f}%)")
        print(f"Worst cash-on-cash: {worst['name']} ({worst['cash_on_cash_pct']:.2f}%)")


if __name__ == "__main__":
    main()
