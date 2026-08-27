# Track A — Investing backtester

A stdlib-only Python tool that backtests an SMA-crossover strategy against buy-and-hold on historical price data. It only evaluates strategies on paper — it never places a trade or touches real money.

## Run it

```
python3 backtest.py sample_data/DEMO.csv
python3 backtest.py sample_data/DEMO.csv --short 10 --long 30
```

`sample_data/DEMO.csv` is **synthetic** (a seeded random walk), not real market data — this sandbox's outbound network is locked to an allowlist and a direct fetch to a market-data site (stooq.com) came back 403 from the proxy, so it can't pull real prices from here. On the demo data, the default 20/50 crossover *underperforms* buy-and-hold, which is a genuinely common result for this kind of simple strategy and not a bug.

## First finding

Simple SMA crossovers are a reasonable teaching example but have a large body of evidence against them reliably beating buy-and-hold after costs — this prototype reproduces that here on synthetic data. Don't read "beat buy-and-hold" on any one run as a signal to trade on.

## To actually use this for real decisions

1. Run it locally (normal internet) with real historical data — either pip-install `yfinance` and dump a CSV, or export one from Yahoo Finance / Stooq.
2. Try it on strategies and assets you actually understand, over multiple time windows — one backtest window proves nothing.
3. Account for transaction costs and taxes, which this prototype ignores.
4. If you ever want it to touch real money, that means wiring up a real brokerage API (e.g. Alpaca) with your own account and keys — a separate, deliberate step, not something to automate quietly.
