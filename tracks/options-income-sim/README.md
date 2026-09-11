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

## Strike-distance sensitivity: how much is this the seller's own choice?

`robustness_test.py` varies the random seed at a fixed 8% OTM strike.
`otm_sensitivity.py` asks a different question: OTM% isn't a fact about the
market, it's the one real decision a covered-call seller makes each period
("how far above spot do I sell?"). This sweeps it from 2% to 20% OTM, 25
seeds per point, in the two scenarios where the covered-call trade-off is
sharpest:

```
python3 otm_sensitivity.py
```

| OTM % | Uptrend win rate | Uptrend avg excess | Downtrend win rate | Downtrend avg excess | Avg premium (uptrend) |
|---|---|---|---|---|---|
| 2% | 20% | -27.96 pts | 84% | +10.42 pts | 60.21% of equity |
| 5% | 40% | -7.49 pts | 96% | +15.06 pts | 47.08% |
| 8% (default) | 52% | -3.51 pts | 100% | +10.51 pts | 26.72% |
| 12% | 48% | -2.75 pts | 88% | +3.83 pts | 8.18% |
| 16% | 64% | -0.92 pts | 88% | +0.72 pts | 1.55% |
| 20% | 88% | -0.46 pts | 96% | +0.04 pts | 0.18% |

**Honest finding:** the two things a farther-OTM strike buys and costs move
in opposite directions, and the 8% default is a mid-point, not a
best-of-both-worlds choice. Selling farther out of the money almost erases
the uptrend drag (win rate climbs from 20% at 2% OTM to 88% at 20% OTM, and
average underperformance shrinks from -27.96 to -0.46 pts) — unsurprising,
since a farther strike gets assigned less often and caps less upside. But
the same move **also erases the premium income that is the entire point of
selling calls** (60.21% of equity collected at 2% OTM vs. 0.18% at 20% OTM)
— so a strike chosen wide enough to stop dragging on a rally is, by the same
mechanism, too far out to meaningfully cushion a downtrend (downtrend avg
excess collapses from +15.06 pts at 5% OTM to +0.04 pts at 20% OTM, i.e.
statistically no different from just holding the stock). There is no OTM%
in this sweep that both beats buy-and-hold on average in an uptrend *and*
keeps a real downside cushion — a covered-call seller isn't picking a
strike, they're picking which one of those two things to give up.

## Does the wheel get the same escape hatch from OTM%? No — the opposite one

`otm_sensitivity.py` above only ever swept `simulate_covered_calls`. The
wheel got its seed-robustness check from `robustness_test.py`, but never a
sweep of its own real lever — the same otm_pct decision, just applied to
both legs (the put strike below spot, the call strike above spot once
assigned). Since covered calls' uptrend drag *shrinks* as OTM% widens, the
obvious guess is that the wheel would behave the same way. It doesn't:

```
python3 otm_sensitivity.py --strategy wheel
```

| OTM % | Uptrend win rate | Uptrend avg excess | Downtrend win rate | Downtrend avg excess | Avg premium (uptrend) |
|---|---|---|---|---|---|
| 2% | 23% | -35.88 pts | 80% | +11.20 pts | 69.75% of equity |
| 5% | 37% | -28.29 pts | 87% | +19.29 pts | 50.90% |
| 8% (default) | 23% | -43.98 pts | 83% | +18.58 pts | 28.36% |
| 12% | 20% | -58.02 pts | 77% | +15.21 pts | 8.54% |
| 16% | 17% | -67.69 pts | 73% | +16.22 pts | 1.59% |
| 20% | 17% | -68.51 pts | 70% | +15.84 pts | 0.18% |

**Honest finding: widening OTM% makes the wheel's uptrend result *worse*,
not better — the opposite of covered calls.** For covered calls, a farther
call strike means fewer assignments, so the strategy stays invested in
shares longer and captures more of a rally (that's why its win rate climbed
from 20% to 88% across the same range). For the wheel, a farther-out **put**
strike means fewer *put* assignments too — but that keeps the wheel stuck
longer in its cash-holding put phase, sitting out of the market entirely,
which is exactly the wrong place to be during an uptrend. The two legs pull
in opposite directions for the same reason they pull in the *same* direction
for downtrends (avg excess stays positive, +11 to +19 pts, across the whole
range — a farther put still cushions a fall reasonably well since it rarely
even needs assignment to look fine relative to a falling buy-and-hold). At
5% OTM the wheel does slightly better than the 8% default in both regimes
(best uptrend avg excess in the sweep, -28.29 pts, and best downtrend avg
excess, +19.29 pts) — a real, if modest, argument for a tighter strike than
this track's default, not a wider one. There is no OTM% in this sweep that
fixes the wheel's uptrend problem the way widening did for covered calls,
because the mechanism dragging on it (idle cash, not capped upside) is a
different mechanism entirely.

## Cycle-length sensitivity: the seller's other real lever

Strike distance (OTM%) isn't the only real decision an option seller makes
each round — how often to roll (weekly vs. monthly vs. quarterly
contracts) is the other one, and every analysis above fixed it at 21
trading days (~monthly). `cycle_sensitivity.py` sweeps period_days across a
realistic weekly-to-quarterly range for both strategies, holding OTM% at
the 8% default:

```
python3 cycle_sensitivity.py --strategy covered-call
python3 cycle_sensitivity.py --strategy wheel
```

| Cycle | Covered-call uptrend win rate | Covered-call uptrend avg excess | Wheel uptrend win rate | Wheel uptrend avg excess |
|---|---|---|---|---|
| 5d (~weekly) | 53% | -2.18 pts | 20% | -64.17 pts |
| 10d | 60% | -3.74 pts | 30% | -44.36 pts |
| 21d (default) | 57% | -4.93 pts | 23% | -43.98 pts |
| 42d | 40% | -16.53 pts | 27% | -41.30 pts |
| 63d (~quarterly) | 33% | -26.92 pts | 27% | -44.52 pts |

**Honest finding: cycle length is a real escape hatch for covered calls,
but not for the wheel — and the mechanism why is a genuine surprise.**
Shortening the cycle to weekly nearly halves covered calls' uptrend drag
(win rate 33%→53%, avg excess -26.92→-2.18 pts as cycle length shortens
from quarterly to weekly). The reason isn't fewer assignments — it's that
the premium heuristic collapses at short cycles: an 8%-OTM strike is a
modest, plausible distance relative to a ~monthly expected price move, but
the *same* 8% is enormous relative to a ~weekly expected move, so the
heuristic prices weekly 8%-OTM calls as nearly worthless (2.65% of equity
collected over 100 cycles vs. 27.26% over 24 monthly cycles — see the avg
premium column in the full output). Weekly covered-call selling in this
model is really "sell calls so far out they almost never matter," which
trades away nearly all the premium income but also nearly all the upside
cap — a real trade-off, not a free lunch, and a reminder that OTM% and
cycle length aren't independent levers; the same percentage strike means
something very different at different time horizons.

The wheel doesn't get this escape hatch: its uptrend result stays deeply
negative at every cycle length tested (-41 to -64 pts), actually *worst* at
the shortest cycle rather than best. That's consistent with this track's
earlier finding that the wheel's uptrend drag comes from time spent
sitting in cash during its put phase, not from capped upside the way
covered calls' does — shortening the cycle doesn't reduce time spent in
cash, so it doesn't fix the mechanism actually causing the loss. Two real
levers (OTM%, cycle length) have now each been swept for both strategies,
and both tell the same story: covered calls have more than one dial that
changes the uptrend outcome, the wheel's uptrend problem is structural and
neither dial fixes it.

## Do the two levers stack? A joint sweep finds a corner where covered calls actually win

The OTM% sweep held cycle length at the 21-day default; the cycle-length
sweep held OTM% at the 8% default. Neither ever varied both real levers at
once, and the cycle-length section above already flags the reason that
matters: the same percentage strike means something different at different
horizons, so the two levers interact. `joint_sensitivity.py` sweeps a 3x3
grid (OTM% x period_days) instead of one lever at a time, for covered calls
in the uptrend scenario, the regime where both individual sweeps showed an
effect:

```
python3 joint_sensitivity.py --paths 60
python3 joint_sensitivity.py --scenario downtrend
```

Uptrend, 60 seeds per cell:

| OTM% \ cycle | 5d (~weekly) | 21d (default) | 63d (~quarterly) |
|---|---|---|---|
| 2% | **72% win / +10.28 pts** | 20% win / -28.30 pts | 13% win / -42.81 pts |
| 8% (default) | 57% win / -0.97 pts | 57% win / -2.68 pts | 37% win / -21.21 pts |
| 20% | 100% win / +0.00 pts | 80% win / -1.35 pts | 45% win / -8.63 pts |

**Honest finding: there is exactly one corner of this whole track's parameter
space, across every sweep run so far, where covered calls beat buy-and-hold
*on average* in an uptrend — and it's not the one either 1-D sweep would
have pointed to.** Tight OTM (2%) alone was the single worst setting tested
at the 21-day default (-28.30 pts here, matching `otm_sensitivity.py`'s
finding). Short cycles (5d) alone only got covered calls to roughly break
even (-0.97 to +0.00 pts across the row, matching `cycle_sensitivity.py`).
But combined, 2%-OTM weekly calls collect premium almost every period
(117% of equity over the full 2-year run — a 2%-OTM strike is *not* far
relative to a weekly expected move, so the heuristic prices it close to
ATM) while getting assigned often enough to keep participating in most of
the uptrend rather than sitting capped. The result flips sign: +10.28 pts
average excess, a 72% win rate, confirmed with a larger seed count (30
seeds gave +6.29 pts / 63%, so this isn't a small-sample fluke). The same
corner does even better in a downtrend (+25.51 pts / 97% win, 30 seeds) —
it isn't a regime-specific trick, it's close to dominant across both
scenarios tested. The 20%-OTM/5d cell's apparent 100% win rate is a
different, less interesting story: premium collected there is ~0.00% of
equity, so the strategy has degenerated into holding stock and "winning"
is just rounding noise around buy-and-hold, not real income. The practical
read: this track's own earlier sweeps each varied one lever at a time and
both concluded covered calls "have an escape hatch but still lose on
average" in an uptrend — true within the grid each one checked, but a
region of the *joint* space was never checked, and it's the one place in
this entire track where the strategy's average result turns positive
against buy-and-hold rather than merely less negative.

The same grid on the wheel (`--strategy wheel`) confirms this is a
covered-call-specific escape, not a general one. The 2%-OTM/5-day corner is
still the *least bad* cell in the wheel's uptrend grid (-4.62 pts, 52% win
rate, 60 seeds) — dramatically better than every other cell (-33 to -67
pts) — but it never crosses into positive territory the way covered calls'
does. That gap is exactly what this track's structural explanation
predicts: covered calls' uptrend drag comes from a capped upside, which a
near-ATM strike with near-continuous premium collection can outrun; the
wheel's drag comes from time spent out of the market entirely during its
put phase, which no combination of strike distance and cycle length fixes,
because neither lever changes *how much time* is spent in cash. In a
downtrend the wheel's whole grid is positive regardless of corner (+4 to
+32 pts), consistent with the wheel's already-documented crash-protection
edge.

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
