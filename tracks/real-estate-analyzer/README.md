# Track D — Rental property deal analyzer

A stdlib-only Python tool that screens rental property deals on paper: give it a purchase price, financing terms, rent, and expenses, and it computes the monthly mortgage payment, monthly cash flow, cap rate, cash-on-cash return, and a year-1 summary. It only does arithmetic on numbers you give it — it never looks up a real listing, never talks to a lender, and never touches real money.

## Run it

```
python3 analyze.py --csv sample_deals.csv
```

or analyze one deal directly:

```
python3 analyze.py --name "123 Main St" --price 300000 --down-pct 20 \
    --rate 7.0 --rent 2400 --tax 3000 --insurance 1200 \
    --maintenance-pct 5 --vacancy-pct 5 --management-pct 8 --closing-pct 3
```

Run `python3 analyze.py --help` for the full flag list and defaults. CSV columns are documented in the docstring at the top of `analyze.py`.

## How it computes things

- **Mortgage payment**: standard fixed-rate amortization formula on the loan amount (price minus down payment), principal + interest only — no escrow modeling beyond the separate tax/insurance lines.
- **Effective rent**: gross rent reduced by the vacancy rate.
- **Operating expenses**: property tax + insurance + maintenance (% of gross rent, a rule-of-thumb budget, not a bid) + management (% of *collected* rent) + HOA.
- **NOI** (net operating income) = effective rent − operating expenses, *before* the mortgage.
- **Cap rate** = annual NOI / purchase price. Financing-independent — same formula whether you pay cash or leverage it.
- **Cash flow** = NOI − mortgage payment (monthly and annualized).
- **Cash-on-cash return** = annual cash flow / total cash invested (down payment + closing costs). This is the number that actually reflects your leverage and is usually the most useful headline metric.

## Sample deals and what they show

`sample_deals.csv` has three deals in the $260k–$380k range, same city tier, deliberately built to land in three different places:

| Deal | Price | Cash-on-cash | Monthly cash flow | Verdict |
|---|---|---|---|---|
| Maple Street Duplex | $260,000 | 11.95% | +$725 | GOOD |
| Oakwood Ave Single-Family | $320,000 | 0.32% | +$19 | MARGINAL |
| Riverside Condo | $380,000 | -18.33% | -$1,045 | BAD |

All three were run and the numbers above are the actual output of `python3 analyze.py --csv sample_deals.csv` — see the full breakdown by running it yourself.

## Honest finding

The three deals aren't randomly different — the "bad" one isn't bad because of some hidden trick, it's bad for the most common real reason rental deals fail: **the purchase price is too high relative to the rent it can command.** Riverside Condo rents for less than Maple Street Duplex ($2,400 vs. $2,600/mo) on a purchase price nearly 50% higher ($380k vs. $260k) — a poor price-to-rent ratio, plus a higher HOA and management overhead, is enough on its own to flip a deal from strongly cash-flow-positive to solidly negative even with a smaller down payment. That's the single number worth sanity-checking first on any real listing (roughly: does monthly rent land near or above ~0.7–1% of purchase price in this market), before running the rest of the numbers here.

The marginal deal is a reminder that "positive cash flow" by itself is a low bar — $19/month of Year-1 cash flow is not a cushion against one slow month, one repair, or one rate hike at refinance.

## To actually use this for real

This tool tells you whether a deal's *numbers* are internally consistent and how they compare to other deals — it is not underwriting and not investment advice. To go from this to an actual purchase decision, you need, at minimum:

1. **Real listings**, not invented numbers — MLS access via a realtor, Zillow/Redfin, or a wholesaler's deal sheet. Every input here (price, rent, taxes) has to come from a real, current source for a real property.
2. **Real financing quotes.** The interest rate and down-payment requirement this tool takes as an input vary by lender, your credit, the loan type (conventional vs. investment-property loans typically require larger down payments and carry higher rates than owner-occupied), and market conditions at the time you actually apply — get pre-qualified, don't guess.
3. **Real rent numbers**, ideally from comparable active listings and a local property manager's opinion, not a guess — rent is the single input this model is most sensitive to.
4. **A real inspection and real diligence** — this tool has no idea if the roof needs replacing, if there's foundation damage, or what the property is actually worth beyond the number you typed in. A clean spreadsheet does not substitute for a structural inspection.
5. **Legal and tax help** — entity structure (LLC vs. personal), how depreciation and passive-loss rules apply to your specific tax situation, local landlord-tenant law, and closing paperwork all need a real attorney/CPA, not this script.
6. **A margin of safety this tool doesn't enforce for you** — it will happily report a "GOOD" verdict on numbers you got optimistic about (rent too high, vacancy too low, maintenance underestimated). Stress-test any real deal with worse-than-expected numbers before committing money to it.

A positive result from this script is a reason to look closer at a deal, not a reason to make an offer.
