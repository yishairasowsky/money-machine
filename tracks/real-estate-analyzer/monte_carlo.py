#!/usr/bin/env python3
"""Multi-year Monte Carlo projection for a rental deal, stdlib only.

analyze.py's --sensitivity flag already asks "how fragile is this deal to a
different purchase price or interest rate quote" — a snapshot at year 1.
This script asks a different question: assuming the deal you locked in is
exactly as analyzed, how much does ordinary year-to-year variance (rent
growth, expense inflation, and the occasional surprise repair that a
maintenance-percent-of-rent rule of thumb doesn't cover) erode a "good" or
"marginal" label over a multi-year hold? It never looks up a real listing,
real market data, or touches real money — every random draw is clearly a
model assumption, not a forecast.

Usage:
    python3 monte_carlo.py --csv sample_deals.csv
    python3 monte_carlo.py --csv sample_deals.csv --years 10 --trials 2000

Model (all stdlib random, seeded for reproducibility unless --seed changes):
  - Rent grows each year by a random rate ~ Normal(mean=3%, stdev=2%).
  - Property tax, insurance, and HOA (the fixed-dollar operating costs)
    inflate each year by a random rate ~ Normal(mean=3%, stdev=1.5%).
  - Maintenance and management stay the same % of rent (they scale with
    rent by construction in analyze.py's model).
  - Each year, an independent 12% chance of one "surprise repair" costing
    1-3 months of that year's rent (uniform) — the real-world risk the
    README already flags: maintenance-as-%-of-rent is a rule of thumb, not
    an itemized bid, and this is what it misses.
  - The mortgage payment is fixed (this assumes, realistically, a
    fixed-rate loan — an ARM would need a different model entirely).
  - No appreciation or resale is modeled — this measures cash-flow
    survivability during the hold, not total return.
"""
import argparse
import csv
import random
import statistics
import sys

from analyze import analyze_deal, REQUIRED_CSV_FIELDS, load_csv

RENT_GROWTH_MEAN = 0.03
RENT_GROWTH_STDEV = 0.02
EXPENSE_INFLATION_MEAN = 0.03
EXPENSE_INFLATION_STDEV = 0.015
SURPRISE_REPAIR_PROB_PER_YEAR = 0.12
SURPRISE_REPAIR_MONTHS_RANGE = (1.0, 3.0)


def simulate_one_trial(deal, years, rng):
    """Runs one random multi-year path for `deal`. Returns
    (had_negative_year, cumulative_cash_flow, worst_year_cash_flow)."""
    rent = deal["monthly_rent"]
    tax = deal["property_tax_annual"]
    insurance = deal["insurance_annual"]
    hoa = deal["monthly_hoa"]

    base = analyze_deal(deal)
    mortgage_pmt = base["mortgage_payment"]

    had_negative_year = False
    cumulative_cash_flow = 0.0
    worst_year_cash_flow = float("inf")

    for _ in range(years):
        rent *= max(1 + rng.gauss(RENT_GROWTH_MEAN, RENT_GROWTH_STDEV), 0.0)
        infl = max(1 + rng.gauss(EXPENSE_INFLATION_MEAN, EXPENSE_INFLATION_STDEV), 0.0)
        tax *= infl
        insurance *= infl
        hoa *= infl

        variant = dict(deal)
        variant["monthly_rent"] = rent
        variant["property_tax_annual"] = tax
        variant["insurance_annual"] = insurance
        variant["monthly_hoa"] = hoa
        year_result = analyze_deal(variant)
        year_cash_flow = year_result["annual_cash_flow"]

        if rng.random() < SURPRISE_REPAIR_PROB_PER_YEAR:
            months = rng.uniform(*SURPRISE_REPAIR_MONTHS_RANGE)
            year_cash_flow -= months * rent

        if year_cash_flow < 0:
            had_negative_year = True
        worst_year_cash_flow = min(worst_year_cash_flow, year_cash_flow)
        cumulative_cash_flow += year_cash_flow

    return had_negative_year, cumulative_cash_flow, worst_year_cash_flow


def run_monte_carlo(deal, years, trials, seed):
    rng = random.Random(seed)
    negative_year_count = 0
    cumulative_totals = []
    worst_years = []

    for _ in range(trials):
        had_negative, cumulative, worst = simulate_one_trial(deal, years, rng)
        if had_negative:
            negative_year_count += 1
        cumulative_totals.append(cumulative)
        worst_years.append(worst)

    return {
        "trials": trials,
        "years": years,
        "pct_trials_with_a_negative_year": 100 * negative_year_count / trials,
        "median_cumulative_cash_flow": statistics.median(cumulative_totals),
        "p10_cumulative_cash_flow": sorted(cumulative_totals)[int(trials * 0.10)],
        "p90_cumulative_cash_flow": sorted(cumulative_totals)[int(trials * 0.90)],
        "median_worst_year": statistics.median(worst_years),
    }


def print_result(deal, result):
    print(f"--- Monte Carlo: {deal['name']} "
          f"({result['years']}yr hold, {result['trials']} trials) ---")
    print(f"  Trials with >=1 negative-cash-flow year: "
          f"{result['pct_trials_with_a_negative_year']:.1f}%")
    print(f"  Median cumulative cash flow over {result['years']}yr: "
          f"${result['median_cumulative_cash_flow']:,.0f}")
    print(f"  10th/90th percentile cumulative cash flow:  "
          f"${result['p10_cumulative_cash_flow']:,.0f} / "
          f"${result['p90_cumulative_cash_flow']:,.0f}")
    print(f"  Median worst single year in the hold:  "
          f"${result['median_worst_year']:,.0f}")
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, help="Path to a CSV of deals (same format as analyze.py).")
    p.add_argument("--years", type=int, default=10, help="Hold length in years (default 10)")
    p.add_argument("--trials", type=int, default=2000, help="Number of random trials per deal (default 2000)")
    p.add_argument("--seed", type=int, default=7, help="RNG seed (default 7)")
    args = p.parse_args()

    deals = load_csv(args.csv)
    if args.trials < 10:
        print("Need at least 10 trials for the percentile math to make sense.", file=sys.stderr)
        sys.exit(1)

    for deal in deals:
        result = run_monte_carlo(deal, args.years, args.trials, args.seed)
        print_result(deal, result)


if __name__ == "__main__":
    main()
