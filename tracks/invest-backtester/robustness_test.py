#!/usr/bin/env python3
"""Multi-seed robustness test for the SMA-crossover and RSI strategies.

Every finding in this track so far (and in README.md/SCORING.md) came from
a *single* synthetic price path — one seed. That's explicitly flagged
elsewhere as low-confidence: "two runs, one synthetic path each." This
script closes that gap without needing real market data: it generates many
independent synthetic paths (same seeded geometric-random-walk generator
used across this repo, see tracks/options-income-sim/sim.py) and runs both
strategies against buy-and-hold on every one, reporting how often each
strategy actually wins rather than trusting one draw.

Usage:
    python3 robustness_test.py [--paths N] [--days N] [--annual-drift X] [--annual-vol X]

Still entirely on paper, still synthetic data — see the module-level caveat
in backtest.py and this track's README for what that does and doesn't prove.
"""
import argparse
import random
import statistics

from backtest import backtest_sma_crossover, backtest_rsi_meanreversion


TRADING_DAYS_PER_YEAR = 252


def generate_price_path(seed, start_price, days, annual_drift, annual_vol):
    """Seeded geometric random walk, same formula as options-income-sim/sim.py."""
    rng = random.Random(seed)
    daily_drift = annual_drift / TRADING_DAYS_PER_YEAR
    daily_vol = annual_vol / (TRADING_DAYS_PER_YEAR ** 0.5)
    prices = [start_price]
    for _ in range(days):
        z = rng.gauss(0.0, 1.0)
        next_price = prices[-1] * (1 + daily_drift + daily_vol * z)
        prices.append(max(next_price, 0.01))
    return prices


def make_rows(prices):
    # Synthetic sequential "dates" — only the ordering matters to backtest.py.
    return [(f"day-{i:04d}", p) for i, p in enumerate(prices)]


def run_trial(seed, days, annual_drift, annual_vol):
    prices = generate_price_path(seed, 100.0, days, annual_drift, annual_vol)
    rows = make_rows(prices)
    sma_result = backtest_sma_crossover(rows)
    rsi_result = backtest_rsi_meanreversion(rows)
    return sma_result, rsi_result


def summarize(label, results):
    excess = [r["strategy_return_pct"] - r["buy_hold_return_pct"] for r in results]
    wins = sum(1 for e in excess if e > 0)
    print(f"\n{label}:")
    print(f"  Beat buy-and-hold: {wins}/{len(results)} paths ({100 * wins / len(results):.0f}%)")
    print(f"  Avg excess return: {statistics.mean(excess):+.2f} pts")
    print(f"  Median excess:     {statistics.median(excess):+.2f} pts")
    print(f"  Best / worst:      {max(excess):+.2f} / {min(excess):+.2f} pts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", type=int, default=30, help="number of independent synthetic paths (default 30)")
    parser.add_argument("--days", type=int, default=504, help="trading days per path (default 504, ~2 years)")
    parser.add_argument("--annual-drift", type=float, default=0.08, help="annual drift, e.g. 0.08 = 8%%/yr (default)")
    parser.add_argument("--annual-vol", type=float, default=0.25, help="annual volatility, e.g. 0.25 = 25%% (default)")
    args = parser.parse_args()

    print(f"Running {args.paths} independent synthetic paths, {args.days} trading days each")
    print(f"Assumptions: annual drift {args.annual_drift:+.0%}, annual vol {args.annual_vol:.0%}")
    print("(seeds 0..N-1, geometric random walk — same generator as options-income-sim)")

    sma_results, rsi_results = [], []
    for seed in range(args.paths):
        sma_result, rsi_result = run_trial(seed, args.days, args.annual_drift, args.annual_vol)
        sma_results.append(sma_result)
        rsi_results.append(rsi_result)

    summarize("SMA(20)/SMA(50) crossover", sma_results)
    summarize("RSI(14) mean-reversion (30/70)", rsi_results)

    rsi_zero_trade = sum(1 for r in rsi_results if r["trades"] == 0)
    print(f"\nRSI paths with 0 trades (never got oversold enough to fire): {rsi_zero_trade}/{len(rsi_results)}")


if __name__ == "__main__":
    main()
