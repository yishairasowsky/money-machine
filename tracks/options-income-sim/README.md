# Track — Options income simulator (covered calls and the full wheel)

A stdlib-only Python paper simulator for two related options-income
strategies. It only simulates on paper — it never places a real options
trade or touches a real brokerage account.

- **`--strategy covered-call`** (default, unchanged since this track's first
  version): sell a covered call against 100 shares you already hold every
  period. If the price finishes above the strike, shares get called away
  (upside capped, then immediately rebought so the strategy keeps running);
  otherwise you keep the shares and the premium and roll again.
- **`--strategy wheel`**: the actual full wheel. Starts in **cash**, selling
  a cash-secured put every period. If the price finishes below the strike,
  you're assigned (buy 100 shares at the strike) and switch to selling
  covered calls; once those shares get called away, you switch back to
  selling puts. It alternates between the two phases for as long as it runs.

## Run it

```
python3 sim.py
python3 sim.py --otm-pct 0.05 --iv 0.30 --annual-drift 0.10
python3 sim.py --scenario uptrend
python3 sim.py --strategy wheel
python3 sim.py --strategy wheel --scenario uptrend
```

With no `--scenario`/`--annual-drift` it runs three scenarios back to
back — `uptrend`, `flat`, `downtrend` — using the **same seed, volatility,
strike distance, and IV** so the only thing that changes between them is
the market's direction. That isolates the one effect this track is
testing: what capping your upside (and, for the wheel, sitting in cash
part of the time) costs or earns you depending on the regime.

## Data and pricing: what's real and what's a heuristic

- **Price path**: synthetic — a seeded geometric random walk (daily drift +
  gaussian noise), generated the same way `tracks/invest-backtester` does
  its demo data. This sandbox's network is locked to a proxy allowlist, so
  there is no real historical-price or options-chain data available here.
  The seed (default `7`) and every market assumption are CLI flags, printed
  in every run's header.
- **Option premium**: there is no real options-pricing library or live
  chain available in this sandbox (no pip installs). Premiums are
  estimated with a simple, clearly-labeled **heuristic**, not a real
  pricing model:
  1. At-the-money base value uses the Brenner–Subrahmanyam approximation
     (a standard back-of-envelope formula): `C_atm ≈ 0.4 * S * IV * sqrt(T)`.
  2. That base is discounted for how far out-of-the-money the strike is,
     in "standard deviations of expected move over the period" (`z`), with
     a Gaussian-shaped falloff: `× exp(-0.5 * z²)`.

  This is **not Black-Scholes** — no interest rate, no dividends, no
  volatility skew, no real bid/ask spread, no time-of-day/early-exercise
  effects. It's a directionally sane, deterministic stand-in so the
  simulation has *something* to sell the call for. See `sim.py`'s
  docstrings for the exact formula.

## What I actually found running it

Default run (`seed=7`, 504 trading days ≈ 2 years, 21-day/~monthly cycles,
8% out-of-the-money strikes, 20% assumed IV, 25% realized annual
volatility for the price path):

| Scenario | Annual drift | Covered calls | Buy & hold | Result |
|---|---|---|---|---|
| Uptrend | +20%/yr | **+43.37%** | +48.14% | Covered calls **underperformed** by 4.78 pts |
| Flat | 0%/yr | **+1.09%** | −0.69% | Covered calls **beat** buy-and-hold by 1.78 pts |
| Downtrend | −15%/yr | **−22.25%** | −26.44% | Covered calls **beat** buy-and-hold by 4.19 pts |

This is the textbook trade-off, and this run reproduces it honestly: in
the strong uptrend, premium income (28.82% of starting equity collected
over 24 cycles) wasn't enough to make up for shares being called away and
missing the rest of the rally — the strategy gave back upside it couldn't
buy back. In the flat and down markets, that same premium income was
enough to turn a loss into a smaller loss, and a near-flat market into a
small win. **Nobody should read the flat/down rows as "covered calls are
free money"** — they won because the market didn't go up much, not because
selling calls has no downside. Run it yourself with `--annual-drift` set
higher (e.g. `0.35`) to see the gap widen further in a strong bull run, or
try different seeds/vol/OTM% — the *direction* of this trade-off is robust
across parameters, the exact numbers are not.

### The full wheel is a different, sharper trade-off — not strictly better

Same default parameters, `--strategy wheel`:

| Scenario | Annual drift | Full wheel | Buy & hold | Result |
|---|---|---|---|---|
| Uptrend | +20%/yr | **+11.43%** | +48.14% | Wheel **underperformed** by 36.72 pts |
| Flat | 0%/yr | **+2.79%** | −0.69% | Wheel **beat** buy-and-hold by 3.48 pts |
| Downtrend | −15%/yr | **−0.66%** | −26.44% | Wheel **beat** buy-and-hold by 25.78 pts |

The wheel's downside protection is dramatically better than covered-calls-only
(−0.66% vs. −22.25% in the same downtrend), but its uptrend cost is *worse*,
not better (underperforms by 36.72 pts vs. covered-calls' 4.78 pts) — the
opposite of "the wheel is just covered calls plus a bonus." The reason is
visible in the run's own phase log: this path spent real time in the **put**
phase (holding cash, not shares) before assignment, so during that stretch
it earned 0% market exposure plus a small premium while buy-and-hold was
fully invested and running. Covered-calls-only, by contrast, holds shares
100% of the time from day one, so it never gives up a rally to sit in cash.
**Neither strategy dominates the other** — the wheel trades uptrend upside
for much better crash protection, which may or may not be the trade you
actually want, and that's a preference question this simulator can surface
but not answer for you.

## Robustness check: does this hold up across more than one seed?

Every number above came from a single seed (7) per scenario — the README
already flagged that as this track's weakest evidence. `robustness_test.py`
closes that gap the same way `tracks/invest-backtester/robustness_test.py`
did for that track: it runs each strategy against buy-and-hold on 30
independent synthetic paths per scenario (seeds 0-29, same default
parameters) instead of one, and reports win rate and average excess return.

```
python3 robustness_test.py --paths 30
python3 robustness_test.py --paths 30 --strategy wheel
```

| Strategy | Scenario | Beat buy-and-hold | Avg excess | Median excess | Best / worst |
|---|---|---|---|---|---|
| Covered calls | Uptrend | 17/30 (57%) | **-4.93 pts** | +3.55 pts | +17.50 / -97.24 pts |
| Covered calls | Flat | 25/30 (83%) | +6.78 pts | +9.87 pts | +21.93 / -41.33 pts |
| Covered calls | Downtrend | 29/30 (97%) | +10.10 pts | +11.45 pts | +21.60 / -20.69 pts |
| Full wheel | Uptrend | 7/30 (23%) | **-43.98 pts** | -38.27 pts | +38.49 / -225.12 pts |
| Full wheel | Flat | 18/30 (60%) | +1.25 pts | +6.39 pts | +47.23 / -116.54 pts |
| Full wheel | Downtrend | 25/30 (83%) | +18.58 pts | +24.66 pts | +58.72 / -57.17 pts |

This confirms the original single-seed findings' *direction* — flat/down
markets favor both income strategies, strong uptrends punish them, and the
wheel's downtrend edge over covered-calls-only holds up (+18.58 vs +10.10
avg pts) — but it also surfaces something the one-seed version couldn't:
**covered calls' uptrend outcome is right-skewed, not just "usually
slightly behind."** It actually beats buy-and-hold on the majority of
paths (57%, median +3.55 pts) — small, steady premium wins on most draws —
but the *average* is negative because a minority of paths are
catastrophic (worst: -97.24 pts), where the underlying ran hard and
capped-upside assignment gave back far more than the premium ever
collected. The wheel shows the same shape, more extreme (worst uptrend
path: -225.12 pts) — its uptrend median loss (-38.27) is already much worse
than covered-calls', and its tail is worse still. **The "expected" outcome
and the "typical" outcome are different things here** — a reminder that
looking only at a strategy's mean return in a backtest can hide a fat left
tail that the median or win-rate wouldn't.

**Still all synthetic data with a heuristic premium model.** This answers
"is the single-seed result representative of this model," not "would this
work with real options pricing on real markets" — real markets have
volatility clustering, skew, and jump risk that a plain gaussian random
walk doesn't reproduce.

## Assumptions and simplifications (read before trusting any number here)

- **Premium is a heuristic, not a market price.** Real option premiums are
  set by supply and demand on an exchange, not a formula, and move with
  the market in ways this can't replicate (volatility skew, term
  structure, event-driven IV spikes, etc.).
- **No bid/ask spread.** Every simulated sale executes at the theoretical
  mid — a real fill will usually be worse.
- **No commissions or assignment/exercise fees.** Real brokers charge for
  both, though many now waive equity assignment fees — check yours.
- **No early assignment risk.** American-style equity options can be
  exercised any time before expiration (e.g. around ex-dividend dates).
  This sim only checks the price at period end, as if every call were
  European-style.
- **No dividends.** Real covered-call writers often give up dividend
  income risk/benefit around assignment; this path has none.
- **No tax treatment.** Premium income, short-term gains from assignment,
  and qualified dividends are all taxed differently in reality; this sim
  reports pre-tax paper numbers only.
- **Reinvestment assumption.** After assignment, the sim immediately buys
  back ~100 shares' worth at the next price so the wheel can keep running
  next period. A real trader might instead sit in cash, sell a cash-secured
  put to try to reacquire lower (the actual second leg of "the wheel"),
  or stop entirely. This sim always re-enters immediately.
- **One size, one clock.** Always exactly one contract (100 shares), and
  the same OTM% and cycle length every period regardless of what the
  market just did — a real trader adjusts strikes to conditions.

## To actually do this for real

1. **You need an options-approved brokerage account.** Selling covered
   calls requires your broker to approve you for at least basic
   options-writing (usually the lowest options tier since it's a
   "covered" — fully collateralized — position).
2. **You need real capital: 100 shares per contract.** At even a modest
   $50 stock that's $5,000 tied up per contract, and it's real money at
   real risk of loss — covered calls do not protect you from the stock
   dropping, they only add a small cushion (the premium) before losses
   start.
3. **Selling options is not free money.** Two real, sometimes large,
   downsides this sim only approximates:
   - **Assignment at a loss** — the stock can drop well below your cost
     basis; you still collected a small premium, but you're still down
     overall, and you no longer own shares that might recover.
   - **Missing a big rally** — if the stock jumps far above your strike,
     you only get paid up to the strike plus premium; you do not
     participate in the rest of the move. In a genuinely strong bull run,
     this can cost far more than the premium ever paid, as shown above.
4. Paper-trade with your actual broker's real option chain (most offer a
   paper/simulated account) before ever doing this with real capital, and
   compare its real quoted premiums against what this heuristic guessed.
