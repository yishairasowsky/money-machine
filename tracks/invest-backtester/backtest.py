#!/usr/bin/env python3
"""SMA-crossover / RSI mean-reversion backtester vs. buy-and-hold, stdlib only.

Usage:
    python3 backtest.py [csv_path] --strategy sma [--short N] [--long N]
    python3 backtest.py [csv_path] --strategy rsi [--rsi-period N]
        [--rsi-oversold N] [--rsi-overbought N]

--strategy defaults to sma, so existing behavior/output is unchanged unless
you opt in to --strategy rsi.

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


def rsi(values, period=14):
    """Wilder's RSI, computed from scratch (stdlib only, no numpy/pandas).

    out[i] is None until index `period` (0-based), matching the style of
    sma() which pads None for the first `window - 1` entries.
    """
    out = [None] * len(values)
    if len(values) <= period:
        return out

    def rsi_from_avgs(avg_gain, avg_loss):
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    gains = losses = 0.0
    for i in range(1, period + 1):
        change = values[i] - values[i - 1]
        gains += max(change, 0.0)
        losses += max(-change, 0.0)
    avg_gain = gains / period
    avg_loss = losses / period
    out[period] = rsi_from_avgs(avg_gain, avg_loss)

    for i in range(period + 1, len(values)):
        change = values[i] - values[i - 1]
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        # Wilder's smoothing: exponential moving average of gains/losses.
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        out[i] = rsi_from_avgs(avg_gain, avg_loss)

    return out


def _run_long_only(dates, prices, should_enter, should_exit):
    """Shared long-only, all-in/all-out trade simulation.

    should_enter(i) / should_exit(i) are callbacks that decide, at bar i,
    whether to open/close the position (or None to mean "no signal yet").
    Returns the same metrics dict shape used by both strategies.
    """
    in_position = False
    cash = 1.0
    shares = 0.0
    equity_curve = []
    trades = 0

    for i in range(len(prices)):
        equity = cash + shares * prices[i]
        equity_curve.append(equity)

        if not in_position and should_enter(i):
            shares = cash / prices[i]
            cash = 0.0
            in_position = True
            trades += 1
        elif in_position and should_exit(i):
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


def backtest_sma_crossover(rows, short_window=20, long_window=50):
    dates = [r[0] for r in rows]
    prices = [r[1] for r in rows]
    short = sma(prices, short_window)
    long_ = sma(prices, long_window)

    def should_enter(i):
        return short[i] is not None and long_[i] is not None and short[i] > long_[i]

    def should_exit(i):
        return short[i] is not None and long_[i] is not None and short[i] < long_[i]

    return _run_long_only(dates, prices, should_enter, should_exit)


def backtest_rsi_meanreversion(rows, period=14, oversold=30, overbought=70):
    """Buy when RSI drops below `oversold` (oversold bounce), sell when it
    rises above `overbought` (overbought pullback) — classic mean-reversion,
    as opposed to the trend-following SMA crossover above."""
    dates = [r[0] for r in rows]
    prices = [r[1] for r in rows]
    rsi_vals = rsi(prices, period)

    def should_enter(i):
        return rsi_vals[i] is not None and rsi_vals[i] < oversold

    def should_exit(i):
        return rsi_vals[i] is not None and rsi_vals[i] > overbought

    return _run_long_only(dates, prices, should_enter, should_exit)


def main():
    args = sys.argv[1:]
    csv_path = "sample_data/DEMO.csv"
    strategy = "sma"
    short_window, long_window = 20, 50
    rsi_period, rsi_oversold, rsi_overbought = 14, 30, 70
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--short":
            short_window = int(args[i + 1]); i += 2
        elif args[i] == "--long":
            long_window = int(args[i + 1]); i += 2
        elif args[i] == "--strategy":
            strategy = args[i + 1]; i += 2
        elif args[i] == "--rsi-period":
            rsi_period = int(args[i + 1]); i += 2
        elif args[i] == "--rsi-oversold":
            rsi_oversold = float(args[i + 1]); i += 2
        elif args[i] == "--rsi-overbought":
            rsi_overbought = float(args[i + 1]); i += 2
        else:
            positional.append(args[i]); i += 1
    if positional:
        csv_path = positional[0]

    if strategy not in ("sma", "rsi"):
        print(f"Unknown --strategy {strategy!r}; expected 'sma' or 'rsi'.")
        sys.exit(1)

    min_rows = long_window if strategy == "sma" else rsi_period
    rows = load_csv(csv_path)
    if len(rows) <= min_rows:
        print(f"Need more than {min_rows} rows of data; got {len(rows)}.")
        sys.exit(1)

    if strategy == "sma":
        result = backtest_sma_crossover(rows, short_window, long_window)
        strategy_label = f"SMA({short_window}) / SMA({long_window}) crossover"
    else:
        result = backtest_rsi_meanreversion(rows, rsi_period, rsi_oversold, rsi_overbought)
        strategy_label = (
            f"RSI({rsi_period}) mean-reversion "
            f"(buy < {rsi_oversold}, sell > {rsi_overbought})"
        )

    print(f"Data:            {csv_path}  ({result['start']} to {result['end']}, {len(rows)} bars)")
    print(f"Strategy:        {strategy_label}")
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
