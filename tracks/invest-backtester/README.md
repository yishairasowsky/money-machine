# Track A — Investing backtester

A stdlib-only Python tool that backtests two strategies — SMA crossover and RSI mean-reversion — against buy-and-hold on historical price data. It only evaluates strategies on paper — it never places a trade or touches real money.

## Run it

```
python3 backtest.py sample_data/DEMO.csv
python3 backtest.py sample_data/DEMO.csv --short 10 --long 30

python3 backtest.py sample_data/DEMO.csv --strategy rsi
python3 backtest.py sample_data/DEMO.csv --strategy rsi --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70
```

`--strategy` selects `sma` (default, unchanged from before) or `rsi`. SMA's flags (`--short`/`--long`) and output format are untouched by this addition.

`sample_data/DEMO.csv` is **synthetic** (a seeded random walk), not real market data — this sandbox's outbound network is locked to an allowlist and a direct fetch to a market-data site (stooq.com) came back 403 from the proxy, so it can't pull real prices from here. On the demo data, the default 20/50 SMA crossover *underperforms* buy-and-hold, which is a genuinely common result for this kind of simple strategy and not a bug.

## RSI mean-reversion

Buys when RSI(14) drops below 30 (oversold) and sells when it rises above 70 (overbought) — the opposite bet from SMA crossover: instead of following a trend, it bets that extremes revert to the mean. RSI is computed from scratch with Wilder's smoothing, stdlib only, matching the hand-rolled `sma()` already in this file.

## First finding

Simple SMA crossovers are a reasonable teaching example but have a large body of evidence against them reliably beating buy-and-hold after costs — this prototype reproduces that here on synthetic data. Don't read "beat buy-and-hold" on any one run as a signal to trade on.

On the same demo data with default parameters (RSI 14, 30/70), the mean-reversion strategy fares even worse in a specific way: DEMO.csv's RSI(14) never drops below 30 (it bottoms around 32.6), so the oversold entry condition never fires — 0 trades, 0% return, versus buy-and-hold's 51.6%. That's not a bug either; it just means this particular synthetic random walk never got "oversold enough" by this threshold, so all of buy-and-hold's gain was left on the table by sitting in cash. Both strategies underperforming buy-and-hold on the same window — for different reasons (bad timing vs. no signal at all) — is consistent with the same broader point: simple technical-indicator strategies are not a free lunch, and neither result should be read as evidence for or against either approach in general. As before, one backtest window on synthetic data proves nothing either way.

## To actually use this for real decisions

1. Run it locally (normal internet) with real historical data — either pip-install `yfinance` and dump a CSV, or export one from Yahoo Finance / Stooq.
2. Try it on strategies and assets you actually understand, over multiple time windows — one backtest window proves nothing.
3. Account for transaction costs and taxes, which this prototype ignores.
4. If you ever want it to touch real money, that means wiring up a real brokerage API (e.g. Alpaca) with your own account and keys — a separate, deliberate step, not something to automate quietly.
