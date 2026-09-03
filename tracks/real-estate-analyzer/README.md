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

## Sensitivity analysis

Every metric above is a single-point estimate built on numbers you typed in — but a real listing's price can move in negotiation and a real mortgage rate depends on a lender quote you don't have yet, at the time you actually run this tool. `--sensitivity` shows how fragile a deal's verdict is to being *wrong* about those two inputs by a realistic amount, instead of implying false precision.

For each deal it prints a 5x5 grid — purchase price swept ±10% in 5% steps (rows) against interest rate swept ±1.5 percentage points in 0.75pp steps (columns) — with cash-on-cash return and monthly cash flow at every combination, holding rent/taxes/down-payment %/etc. fixed at the deal's own numbers. It works in both single-deal and `--csv` mode:

```
python3 analyze.py --csv sample_deals.csv --sensitivity
```

**Honest finding from running it on the sample deals:** the "marginal" Oakwood Ave deal (base case: 7.25% rate, +$19/month, 0.32% cash-on-cash) turns cash-flow-negative at the *same* purchase price if the rate it actually closes at is just 0.75 percentage points higher (8.00% instead of 7.25%) — well within normal lender-to-lender quote variation, not a stress scenario. The "good" Maple Street deal, by contrast, stays cash-flow-positive across the entire grid (even at price +10% and rate +1.5pp it's still +$379/month). That's the real value of this feature: it's not that Oakwood's single-point numbers were wrong, it's that a "MARGINAL" verdict built on a $19/month cushion was never a verdict about the deal so much as a verdict about whether you'll get exactly the rate you assumed — and the "GOOD" deal earns that label precisely because it doesn't have that problem.

## Multi-year Monte Carlo: does the label survive an actual hold?

`--sensitivity` answers "is this deal's Year-1 verdict fragile to a wrong price or rate quote." `monte_carlo.py` answers a different question: assuming you locked in exactly the numbers analyzed, how much does *ordinary* year-to-year variance over a multi-year hold — rent growth, expense inflation, and the occasional surprise repair that "maintenance as a % of rent" doesn't cover — erode that verdict?

```
python3 monte_carlo.py --csv sample_deals.csv --years 10 --trials 2000
```

Each of 2,000 independent 10-year paths per deal draws random rent growth (~3%/yr, some variance), random expense inflation (~3%/yr), and gives each year a 12% independent chance of one surprise repair costing 1-3 months' rent — modeling the exact risk the "rule of thumb, not a bid" caveat above already flags, instead of just naming it.

**Honest finding:** over a realistic 10-year hold, the "good" Maple Street deal never has a single negative-cash-flow year across all 2,000 trials (median cumulative cash flow $123k, 10th percentile still $104k) — it earns its label at every horizon, not just Year 1. The "marginal" Oakwood Ave deal looks very different once time is added: it has at least one negative-cash-flow year in **65.6%** of trials, and its median worst single year is *negative* (-$2,094) — a deal whose Year-1 sensitivity grid looked merely thin (a 0.75pp rate move away from trouble) turns out to be more likely than not to see a real down year at some point in a 10-year hold, just from ordinary variance, no bad luck required. The "bad" Riverside Condo has a negative year in 100% of trials, as expected. **The single-point Year-1 verdict and the multi-year survival rate are answering different questions** — a deal can pass the first and still be a bad bet on the second, which is exactly what happened to "marginal" here.

## Leverage sensitivity: how much is this the buyer's own choice?

`--sensitivity` sweeps purchase price and interest rate -- inputs you don't
fully control before an offer and a locked rate. `monte_carlo.py` sweeps
time at whatever down payment the deal was analyzed with. Neither touches
the one input that actually is the buyer's own decision: how much of their
own cash to put down versus borrow. More down payment shrinks the mortgage
payment (more cash-flow cushion) but ties up more cash for the same rental
income (lower cash-on-cash return) -- the same kind of real trade-off as
strike distance in `options-income-sim` or the SMA window pair in
`invest-backtester`. `leverage_sensitivity.py` reruns the 10-year Monte
Carlo survivability check at six down-payment levels (10% to 40%) per deal:

```
python3 leverage_sensitivity.py --csv sample_deals.csv --trials 1000
```

| Deal | Down % | Cash-on-cash | Negative-year trials |
|---|---|---|---|
| Maple St (good) | 10% | 16.77% | 9.3% |
| Maple St (good) | 20% (its own) | 12.86% | 0.3% |
| Maple St (good) | 40% | 10.50% | 0.0% |
| Oakwood (marginal) | 20% (its own) | 0.32% | 66.6% |
| Oakwood (marginal) | 40% | 3.98% | 18.2% |
| Riverside (bad) | 10%-40% (every level tested) | -28.60% to -2.79% | 100% at every level |

**Honest finding: leverage matters a lot for two of the three deals, and not
at all for the third, in a way that's diagnostic.** Even the "good" Maple
Street deal isn't unconditionally safe -- at 10% down (its higher-return,
higher-leverage option) the negative-year rate jumps from near-zero to 9.3%,
purely from taking on a bigger mortgage payment against the same rent. For
the "marginal" Oakwood deal, more down payment helps a lot (66.6% -> 18.2%
negative-year risk from 20% to 40% down) but never gets it comfortable --
even the least-leveraged option tested still fails nearly 1 in 5 ten-year
holds. For the "bad" Riverside Condo, down payment changes nothing at all:
100% of trials have a negative year at every level from 10% to 40%, because
the problem isn't the financing, it's that the rent doesn't cover expenses
at any reasonable leverage -- no down payment size fixes a bad price-to-rent
ratio. That third result is the most useful one: it tells you when *more
money down* is the right lever to pull on a real deal, and when it's wasted
cash on a deal that was never going to work.

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
