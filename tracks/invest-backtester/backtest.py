#!/usr/bin/env python3
"""SMA-crossover backtester vs. buy-and-hold, stdlib only.

Usage:
    python3 backtest.py [csv_path] [--short N] [--long N]

CSV must have columns: date,close (see sample_data/DEMO.csv). This ships
with synthetic demo data because this sandbox's network is locked down to
an allowlist (a direct fetch to stooq.com returned 403 from the proxy) —
it cannot pull real market data. To backtest for real, run this locally
where you have normal internet, and pass a CSV of real historical prices
(export from Yahoo Finance / Stooq, or dump one from `yfinance`).

This tool only evaluates a strategy on paper. It never places a trade.
"""
import csv
import sys
import statistics


def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"], float(r["close"])))
    rows.sort(key=lambda x: x[0])
    return rows


def sma(values, window):
    out = [None] * len(values)
    for i in range(window - 1, len(values)):
        out[i] = sum(values[i - window + 1 : i + 1]) / window
    return out


def backtest_sma_crossover(rows, short_window=20, long_window=50):
    dates = [r[0] for r in rows]
    prices = [r[1] for r in rows]
    short = sma(prices, short_window)
    long_ = sma(prices, long_window)

    in_position = False
    cash = 1.0
    shares = 0.0
    equity_curve = []
    trades = 0

    for i in range(len(prices)):
        equity = cash + shares * prices[i]
        equity_curve.append(equity)

        if short[i] is None or long_[i] is None:
            continue

        if not in_position and short[i] > long_[i]:
            shares = cash / prices[i]
            cash = 0.0
            in_position = True
            trades += 1
        elif in_position and short[i] < long_[i]:
            cash = shares * prices[i]
            shares = 0.0
            in_position = False
            trades += 1

    final_equity = cash + shares * prices[-1]
    strategy_return = final_equity - 1.0
    buy_hold_return = prices[-1] / prices[0] - 1.0

    daily_returns = [
        equity_curve[i] / equity_curve[i - 1] - 1
        for i in range(1, len(equity_curve))
        if equity_curve[i - 1] > 0
    ]
    sharpe = None
    if len(daily_returns) > 1 and statistics.pstdev(daily_returns) > 0:
        sharpe = (statistics.mean(daily_returns) / statistics.pstdev(daily_returns)) * (252 ** 0.5)

    return {
        "start": dates[0],
        "end": dates[-1],
        "trades": trades,
        "strategy_return_pct": round(strategy_return * 100, 2),
        "buy_hold_return_pct": round(buy_hold_return * 100, 2),
        "sharpe_annualized": round(sharpe, 2) if sharpe is not None else None,
    }


def main():
    args = sys.argv[1:]
    csv_path = "sample_data/DEMO.csv"
    short_window, long_window = 20, 50
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--short":
            short_window = int(args[i + 1]); i += 2
        elif args[i] == "--long":
            long_window = int(args[i + 1]); i += 2
        else:
            positional.append(args[i]); i += 1
    if positional:
        csv_path = positional[0]

    rows = load_csv(csv_path)
    if len(rows) <= long_window:
        print(f"Need more than {long_window} rows of data; got {len(rows)}.")
        sys.exit(1)

    result = backtest_sma_crossover(rows, short_window, long_window)
    print(f"Data:            {csv_path}  ({result['start']} to {result['end']}, {len(rows)} bars)")
    print(f"Strategy:        SMA({short_window}) / SMA({long_window}) crossover")
    print(f"Trades taken:    {result['trades']}")
    print(f"Strategy return: {result['strategy_return_pct']}%")
    print(f"Buy & hold:      {result['buy_hold_return_pct']}%")
    print(f"Sharpe (ann.):   {result['sharpe_annualized']}")
    if result["strategy_return_pct"] <= result["buy_hold_return_pct"]:
        print("\nVerdict: strategy did NOT beat buy-and-hold on this data/window.")
    else:
        print("\nVerdict: strategy beat buy-and-hold on this data/window (not proof it will keep doing so).")


if __name__ == "__main__":
    main()
