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

## Robustness check: does this hold up across more than one path?

Every finding above came from a single synthetic price path — a real risk,
since one seed's random walk could just be unlucky for these strategies.
`robustness_test.py` closes that gap: it runs both strategies against
buy-and-hold on 30 independent synthetic paths (seeds 0-29, same
geometric-random-walk generator used across this repo) and reports how
often each strategy actually wins, not just what one run showed.

```
python3 robustness_test.py --paths 30
python3 robustness_test.py --paths 30 --annual-drift 0.0
```

With a realistic +8%/yr drift (roughly long-run equity market average) and
25% annual volatility, 504 trading days (~2 years) per path:

| Strategy | Beat buy-and-hold | Avg excess return | Median excess | Best / worst |
|---|---|---|---|---|
| SMA(20)/SMA(50) crossover | 6/30 (20%) | -15.86 pts | -16.98 pts | +74.53 / -71.71 pts |
| RSI(14) mean-reversion | 13/30 (43%) | -23.01 pts | -8.09 pts | +49.09 / -172.81 pts |

Both strategies lose to buy-and-hold on *most* paths, not just the one
originally reported — the single-path findings above weren't a fluke of bad
luck. SMA crossover wins on only 1 in 5 paths and loses by a lot on average.
RSI wins closer to half the time (its median loss is smaller than SMA's),
but its *average* is worse, dragged down by a small number of catastrophic
paths (worst case -172.81 pts) — a classic mean-reversion failure mode: it
looks fine most of the time, then gets run over on the paths where the
"oversold" signal fires right before the price keeps falling anyway.

In a flat market (0% drift, same volatility), both strategies still lose to
buy-and-hold on average (-4.90 and -10.33 pts respectively) but with win
rates closer to a coin flip (40% and 47%) — makes sense, since buy-and-hold
has less of a moving target to beat when it isn't going anywhere.

**This is still all synthetic data.** It answers "is the single-path result
representative of this specific random-walk model," not "would this work on
real markets" — real prices have autocorrelation, regime changes, and fat
tails that a gaussian random walk doesn't reproduce. But it does rule out
the easy objection that the original finding was just one unlucky draw.

## To actually use this for real decisions

1. Run it locally (normal internet) with real historical data — either pip-install `yfinance` and dump a CSV, or export one from Yahoo Finance / Stooq.
2. Try it on strategies and assets you actually understand, over multiple time windows — one backtest window proves nothing.
3. Account for transaction costs and taxes, which this prototype ignores.
4. If you ever want it to touch real money, that means wiring up a real brokerage API (e.g. Alpaca) with your own account and keys — a separate, deliberate step, not something to automate quietly.
