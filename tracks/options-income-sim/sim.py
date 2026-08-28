#!/usr/bin/env python3
"""Covered-call ("simplified wheel") paper simulator, stdlib only.

Simulates selling a covered call against 100 shares you already hold, once
per period (default: every 21 trading days, roughly a monthly expiration).
Compares the simulated total return of that strategy against plain
buy-and-hold over the same synthetic price path.

This tool only simulates on paper. It never places a real options trade,
and it never touches a real brokerage account.

Price data: a seeded random walk (geometric, daily drift + gaussian noise),
generated the same way tracks/invest-backtester does its demo data — this
sandbox's network is locked to a proxy allowlist, so there is no real
options-chain or historical-price data available here. The seed and every
market assumption (drift, volatility) are CLI flags, printed in the report,
and documented below.

Options pricing: there is no real options-pricing library available here
(no pip installs; no live options chain). Premiums are estimated with a
simple, clearly-labeled HEURISTIC, not a real pricing model:

    1. At-the-money base value uses the Brenner-Subrahmanyam approximation,
       a well-known back-of-envelope formula:
           C_atm ~= 0.4 * S * IV * sqrt(T)
    2. That base is discounted for how far out-of-the-money the strike is,
       expressed in "standard deviations of expected move over the period"
       (z), using a Gaussian-shaped falloff: multiply by exp(-0.5 * z^2).

This is NOT Black-Scholes and does not model interest rates, dividends,
skew, a real bid/ask spread, or early exercise. It exists to produce a
directionally sane, deterministic premium for a paper simulation — see the
README for the full list of simplifications.

Usage:
    python3 sim.py
    python3 sim.py --seed 7 --days 504 --otm-pct 0.05 --iv 0.25
    python3 sim.py --scenario uptrend --annual-drift 0.20
"""
import argparse
import math
import random


TRADING_DAYS_PER_YEAR = 252


def generate_price_path(seed, start_price, days, annual_drift, annual_vol):
    """Seeded geometric random walk: price[i+1] = price[i] * (1 + mu + sigma*Z)."""
    rng = random.Random(seed)
    daily_drift = annual_drift / TRADING_DAYS_PER_YEAR
    daily_vol = annual_vol / (TRADING_DAYS_PER_YEAR ** 0.5)
    prices = [start_price]
    for _ in range(days):
        z = rng.gauss(0.0, 1.0)
        next_price = prices[-1] * (1 + daily_drift + daily_vol * z)
        prices.append(max(next_price, 0.01))  # floor so price can't go negative
    return prices


def estimate_call_premium(spot, strike, iv, period_days):
    """HEURISTIC premium per share for a call at `strike`, `period_days` out.

    Not a real options pricing model. See module docstring / README for the
    formula and its limitations.
    """
    T = period_days / TRADING_DAYS_PER_YEAR
    sigma_period = iv * (T ** 0.5)  # expected stdev of return over the period
    if sigma_period <= 0:
        return 0.0
    otm_pct = (strike - spot) / spot
    z = otm_pct / sigma_period  # how many period-sigmas OTM the strike is
    atm_premium_frac = 0.4 * sigma_period
    decay = math.exp(-0.5 * z * z)
    premium_frac = max(atm_premium_frac * decay, 0.0)
    return premium_frac * spot


def estimate_put_premium(spot, strike, iv, period_days):
    """HEURISTIC premium per share for a cash-secured put at `strike`.

    Mirrors estimate_call_premium: same Brenner-Subrahmanyam ATM base and
    Gaussian OTM-distance decay, just measured below spot instead of above.
    Same non-model, see module docstring / README.
    """
    T = period_days / TRADING_DAYS_PER_YEAR
    sigma_period = iv * (T ** 0.5)
    if sigma_period <= 0:
        return 0.0
    otm_pct = (spot - strike) / spot  # positive when strike is below spot
    z = otm_pct / sigma_period
    atm_premium_frac = 0.4 * sigma_period
    decay = math.exp(-0.5 * z * z)
    premium_frac = max(atm_premium_frac * decay, 0.0)
    return premium_frac * spot


def simulate_covered_calls(prices, otm_pct, iv, period_days, contract_size=100):
    """Sell one covered call per period against `contract_size` shares.

    State mirrors tracks/invest-backtester's cash/shares split so the two
    tracks read the same way. Premium collected each period sits as cash
    (it is real income, not automatically reinvested). If assigned, the
    shares are sold at the strike and the proceeds are immediately used to
    buy back shares at the next price so the strategy can keep running —
    this is the "simplified wheel" assumption; see README.
    """
    shares = float(contract_size)
    cash = 0.0
    total_premium = 0.0
    assignments = 0
    periods = 0

    i = 0
    n = len(prices) - 1
    while i + period_days <= n:
        start_price = prices[i]
        end_price = prices[i + period_days]
        strike = start_price * (1 + otm_pct)

        premium_per_share = estimate_call_premium(start_price, strike, iv, period_days)
        premium_total = premium_per_share * shares
        cash += premium_total
        total_premium += premium_total
        periods += 1

        if end_price > strike:
            # Assigned: shares called away at the strike. Upside above the
            # strike for this period is given up.
            assignments += 1
            cash += shares * strike
            shares = 0.0
            # Reinvest to keep ~100 shares working so the wheel continues.
            shares = cash / end_price
            cash = 0.0
        # else: keep the shares, keep the premium already collected as cash.

        i += period_days

    final_price = prices[i]  # last price used as a period boundary
    final_equity = cash + shares * final_price
    return {
        "final_price": final_price,
        "final_equity": final_equity,
        "shares_end": shares,
        "cash_end": cash,
        "total_premium": total_premium,
        "periods": periods,
        "assignments": assignments,
    }


def simulate_wheel(prices, otm_pct, iv, period_days, contract_size=100):
    """The full "wheel": alternate cash-secured puts (while holding cash) and
    covered calls (while holding shares), instead of only ever holding
    shares like simulate_covered_calls does.

    Starts in the 'put' phase with cash equal to the starting share value.
    Put phase: sell a put otm_pct below spot each period; collect the
    premium; if the price finishes below the strike, get assigned (buy
    `contract_size` shares at the strike) and switch to the 'call' phase.
    Call phase: sell a call otm_pct above spot each period (same as
    simulate_covered_calls); if the price finishes above the strike, shares
    are called away and the strategy switches back to the 'put' phase.

    Simplification carried over from simulate_covered_calls: cash sitting
    idle in the put phase earns no interest (no risk-free rate is modeled),
    matching this track's "no interest rate" limitation documented in the
    README.
    """
    cash = float(contract_size) * prices[0]
    shares = 0.0
    phase = "put"
    total_premium = 0.0
    put_assignments = 0
    call_assignments = 0
    periods = 0

    i = 0
    n = len(prices) - 1
    while i + period_days <= n:
        start_price = prices[i]
        end_price = prices[i + period_days]
        periods += 1

        if phase == "put":
            strike = start_price * (1 - otm_pct)
            premium_per_share = estimate_put_premium(start_price, strike, iv, period_days)
            cash += premium_per_share * contract_size
            total_premium += premium_per_share * contract_size
            if end_price < strike:
                # Assigned: buy contract_size shares at the strike.
                put_assignments += 1
                cash -= strike * contract_size
                shares = float(contract_size)
                phase = "call"
            # else: keep the cash and the premium, stay in the put phase.
        else:  # phase == "call"
            strike = start_price * (1 + otm_pct)
            premium_per_share = estimate_call_premium(start_price, strike, iv, period_days)
            cash += premium_per_share * shares
            total_premium += premium_per_share * shares
            if end_price > strike:
                # Assigned: shares called away at the strike.
                call_assignments += 1
                cash += shares * strike
                shares = 0.0
                phase = "put"
            # else: keep the shares and the premium, stay in the call phase.

        i += period_days

    final_price = prices[i]
    final_equity = cash + shares * final_price
    return {
        "final_price": final_price,
        "final_equity": final_equity,
        "shares_end": shares,
        "cash_end": cash,
        "total_premium": total_premium,
        "periods": periods,
        "assignments": put_assignments + call_assignments,
        "put_assignments": put_assignments,
        "call_assignments": call_assignments,
        "ended_in_phase": phase,
    }


SCENARIOS = {
    # name: annual_drift
    "uptrend": 0.20,
    "flat": 0.0,
    "downtrend": -0.15,
}


STRATEGY_LABELS = {
    "covered-call": "Covered calls",
    "wheel": "Full wheel",
}


def run_and_report(name, seed, start_price, days, annual_drift, annual_vol,
                    otm_pct, iv, period_days, contract_size=100, strategy="covered-call"):
    prices = generate_price_path(seed, start_price, days, annual_drift, annual_vol)
    if strategy == "wheel":
        result = simulate_wheel(prices, otm_pct, iv, period_days, contract_size)
    else:
        result = simulate_covered_calls(prices, otm_pct, iv, period_days, contract_size)

    initial_equity = contract_size * prices[0]
    strategy_return_pct = (result["final_equity"] / initial_equity - 1) * 100
    buy_hold_final = contract_size * result["final_price"]
    buy_hold_return_pct = (buy_hold_final / initial_equity - 1) * 100
    premium_income_pct = (result["total_premium"] / initial_equity) * 100
    label = STRATEGY_LABELS[strategy]

    print(f"--- Scenario: {name} (seed={seed}, annual_drift={annual_drift:+.0%}, "
          f"annual_vol={annual_vol:.0%}) ---")
    print(f"Strategy:          {label}")
    print(f"Price path:        {prices[0]:.2f} -> {result['final_price']:.2f} "
          f"over {days} trading days")
    print(f"Periods simulated: {result['periods']} "
          f"(period_days={period_days}, otm_pct={otm_pct:.0%}, iv={iv:.0%})")
    if strategy == "wheel":
        print(f"Assignments:       {result['assignments']} / {result['periods']} periods "
              f"({result['put_assignments']} put, {result['call_assignments']} call; "
              f"ended in '{result['ended_in_phase']}' phase)")
    else:
        print(f"Assignments:       {result['assignments']} / {result['periods']} periods")
    print(f"Premium collected: {result['total_premium']:.2f} "
          f"({premium_income_pct:.2f}% of starting equity)")
    print(f"{label + ':':<19}{strategy_return_pct:+.2f}%")
    print(f"Buy & hold:        {buy_hold_return_pct:+.2f}%")
    diff = strategy_return_pct - buy_hold_return_pct
    if diff >= 0:
        print(f"Verdict:           {label.lower()} beat buy-and-hold by {diff:.2f} pts "
              "on this path.")
    else:
        print(f"Verdict:           {label.lower()} UNDERPERFORMED buy-and-hold by "
              f"{-diff:.2f} pts on this path.")
    print()
    return {
        "name": name,
        "strategy_return_pct": strategy_return_pct,
        "buy_hold_return_pct": buy_hold_return_pct,
        "premium_income_pct": premium_income_pct,
        "assignments": result["assignments"],
        "periods": result["periods"],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=7, help="RNG seed (default: 7)")
    p.add_argument("--start-price", type=float, default=100.0)
    p.add_argument("--days", type=int, default=504, help="trading days to simulate (default: 504, ~2yr)")
    p.add_argument("--annual-vol", type=float, default=0.25, help="annualized realized volatility used to generate the price path (default: 0.25)")
    p.add_argument("--iv", type=float, default=0.20, help="assumed implied volatility fed into the premium heuristic (default: 0.20)")
    p.add_argument("--otm-pct", type=float, default=0.08, help="how far out-of-the-money the sold call's strike is, as a fraction of spot (default: 0.08 = 8%%)")
    p.add_argument("--period-days", type=int, default=21, help="trading days per option cycle (default: 21, ~1 month)")
    p.add_argument("--annual-drift", type=float, default=None, help="override annual drift for a single custom run instead of the three built-in scenarios")
    p.add_argument("--scenario", choices=list(SCENARIOS.keys()), default=None,
                    help="run only this one scenario instead of all three")
    p.add_argument("--strategy", choices=list(STRATEGY_LABELS.keys()), default="covered-call",
                    help="'covered-call' (default, unchanged from before) sells calls against "
                         "shares held from the start; 'wheel' starts in cash selling puts and "
                         "alternates puts/calls as it gets assigned")
    args = p.parse_args()

    label = STRATEGY_LABELS[args.strategy]
    print(f"{label} paper simulator")
    print("Synthetic data only. No real trade is ever placed.\n")

    if args.annual_drift is not None:
        scenarios = {"custom": args.annual_drift}
    elif args.scenario is not None:
        scenarios = {args.scenario: SCENARIOS[args.scenario]}
    else:
        scenarios = SCENARIOS

    summaries = []
    for name, drift in scenarios.items():
        summaries.append(run_and_report(
            name, args.seed, args.start_price, args.days, drift, args.annual_vol,
            args.otm_pct, args.iv, args.period_days, strategy=args.strategy,
        ))

    if len(summaries) > 1:
        print(f"=== Summary across scenarios (same seed / vol / strike / IV, drift varied; "
              f"strategy={args.strategy}) ===")
        for s in summaries:
            beat = "beats" if s["strategy_return_pct"] >= s["buy_hold_return_pct"] else "trails"
            print(f"  {s['name']:<10} {label.lower()} {s['strategy_return_pct']:+7.2f}%  "
                  f"buy&hold {s['buy_hold_return_pct']:+7.2f}%  "
                  f"({beat} buy&hold; premium income {s['premium_income_pct']:.2f}% of equity; "
                  f"{s['assignments']}/{s['periods']} periods assigned)")
        if args.strategy == "covered-call":
            print("\nHonest read: covered calls collect steady premium income every period "
                  "regardless of direction, but assignment caps the upside whenever the "
                  "price finishes above the strike. That trade-off should show up above as "
                  "underperformance in a strong uptrend and a smaller gap (or an edge) in a "
                  "flat or falling market. This is not guaranteed on every random seed — "
                  "it's the expected shape of the trade-off, not a law.")
        else:
            print("\nHonest read: the wheel collects premium in both phases (puts while "
                  "waiting in cash, calls while holding shares), but idle cash in the put "
                  "phase earns no modeled interest and is fully out of the market during "
                  "that time — so in a strong uptrend it can trail buy-and-hold by more "
                  "than covered-calls-only does, not less, if it spends time sitting in "
                  "cash while the price runs. Compare directly against --strategy "
                  "covered-call on the same scenario to see the difference.")


if __name__ == "__main__":
    main()
