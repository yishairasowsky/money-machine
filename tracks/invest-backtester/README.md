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

## Window sensitivity: was 20/50 ever a fair pick?

`robustness_test.py` fixed the SMA windows at the 20/50 default and varied
the seed. `window_sensitivity.py` asks the question that leaves open: was
20/50 ever a fair test, or would a different fast/slow window pair have
actually beaten buy-and-hold? It sweeps five classic pairs (10/30, 20/50,
10/50, 20/100, 50/200) across 30 seeds each, in three market regimes:

```
python3 window_sensitivity.py --paths 30
```

| Windows | Uptrend win rate | Uptrend avg excess | Downtrend win rate | Downtrend avg excess |
|---|---|---|---|---|
| 10/30 | 13% | -27.97 pts | 63% | +9.35 pts |
| 20/50 (default) | 17% | -24.69 pts | 67% | +8.56 pts |
| 10/50 | 20% | -24.40 pts | 70% | +10.74 pts |
| 20/100 | 17% | -28.94 pts | 63% | +11.90 pts |
| 50/200 | 23% | -34.30 pts | 63% | +10.88 pts |

**Honest finding: no window pair changes the story.** Every pair loses to
buy-and-hold on the large majority of uptrend paths (13-23% win rate, all
strongly negative average) and every pair beats it on the majority of
downtrend paths (63-70% win rate, all positive average) — the differences
between window pairs are noise-sized (a few points) next to the gap between
regimes (30-40+ points). The 20/50 default wasn't an unlucky pick that made
SMA crossover look bad; every classic fast/slow combination tested has the
same shape, because the mechanism that hurts it in an uptrend (lag: the
crossover confirms a move only after it's underway, so entries are late and
exits give back gains) doesn't go away with a different window length. This
closes a real gap `robustness_test.py` left open — varying the seed proved
the result wasn't bad luck; varying the window proves it wasn't a bad
parameter choice either.

## RSI threshold sensitivity: was 30/70 ever a fair pick?

`window_sensitivity.py` answered this for SMA crossover's one real decision
(the fast/slow window pair). RSI mean-reversion has its own equivalent real
decision: how oversold/overbought counts as a signal. `robustness_test.py`
fixed RSI at the 14/30/70 default and varied the seed; `rsi_sensitivity.py`
instead sweeps five classic oversold/overbought threshold pairs (looser
20/80 to stricter 40/60) across 30 seeds each in three regimes:

```
python3 rsi_sensitivity.py --paths 30
```

| Thresholds | Uptrend win rate | Uptrend avg excess | Downtrend win rate | Downtrend avg excess |
|---|---|---|---|---|
| 20/80 | 23% | -52.77 pts | 70% | +9.86 pts |
| 25/75 | 27% | -49.97 pts | 77% | +10.86 pts |
| 30/70 (default) | 20% | -44.34 pts | 70% | +6.72 pts |
| 35/65 | 30% | -36.83 pts | 63% | +4.44 pts |
| 40/60 | 33% | -38.81 pts | 73% | +6.71 pts |

**Honest finding: no threshold pair changes the story, and the pattern is
the same shape as SMA's.** Every pair loses to buy-and-hold on the large
majority of uptrend paths (20-33% win rate, all strongly negative average)
and beats it on the majority of downtrend paths (63-77% win rate, all
positive average) — the spread between threshold pairs is noise-sized next
to the 60-90+ point gap between regimes. Looser thresholds (40/60) trade far
more often (11.1 average trades vs. 0.2-0.9 for the strictest pairs) without
turning the uptrend loss into a win — more signals isn't the fix, since
mean-reversion entries keep firing into a trend that doesn't revert. The
30/70 default wasn't an unlucky choice that made RSI look worse than it is;
between `robustness_test.py` (rules out unlucky seed) and this (rules out
bad threshold choice), both of Track A's strategies now rest on the same
two-part evidence base.

## Combining the signals: does a trend filter fix RSI's tail risk?

Every test above treats SMA crossover and RSI mean-reversion as
*alternatives* — never together. RSI's own documented failure mode (the
threshold sweep above, and the README's first finding) is an oversold
signal firing right before price keeps falling anyway. `backtest.py` now
also exposes `--strategy combined` (`backtest_trend_filtered_rsi`): only
take an RSI oversold entry while the SMA crossover says the trend is up,
and exit on RSI overbought *or* the trend flipping down, whichever comes
first — a natural, real combination a trader might actually use.
`combined_signal_test.py` runs all three (SMA alone, RSI alone, combined)
on the same seeded paths across the same three regimes:

```
python3 combined_signal_test.py --paths 30
```

| Scenario | Strategy | Win rate | Avg excess | Worst | Avg trades |
|---|---|---|---|---|---|
| Uptrend | SMA alone | 16.7% | -24.69p | -81.50p | 10.3 |
| Uptrend | RSI alone | 20.0% | -44.34p | -215.33p | 2.6 |
| Uptrend | Combined | 20.0% | -52.31p | -232.55p | 0.7 |
| Flat | SMA alone | 40.0% | -4.90p | -73.83p | 10.9 |
| Flat | RSI alone | 46.7% | -10.33p | -136.17p | 3.2 |
| Flat | Combined | 43.3% | -12.93p | -146.50p | 1.1 |
| Downtrend | SMA alone | 66.7% | +8.56p | -46.57p | 10.4 |
| Downtrend | RSI alone | 70.0% | +6.72p | -73.37p | 3.3 |
| Downtrend | Combined | 70.0% | +16.48p | -82.69p | 1.4 |

**Honest finding: combining the signals does not fix RSI's tail risk — it
makes the uptrend and flat-market results *worse*, and the downtrend
improvement it does deliver comes from a mechanism that has nothing to do
with fixing bad entries.** Requiring the SMA uptrend filter *and* an RSI
oversold reading at the same bar is a much stronger condition than either
alone, so the combined strategy trades far less (0.7-1.4 average trades vs.
2.6-3.3 for RSI alone) — checked directly: it takes **zero trades on 18-20
of 30 paths in every regime tested**, versus only 1-2/30 for RSI alone.
Sitting entirely in cash for the whole path is a bad outcome in an uptrend
(it forgoes nearly all of buy-and-hold's gain, which is exactly why the
combined strategy's uptrend average excess is worse than RSI alone despite
an identical win rate) and a good one in a downtrend (it forgoes the
losses), which is also why the downtrend average *improves* — not because
the trend filter screened out bad RSI entries, but because the same filter
mostly prevented the strategy from entering the market at all. This is the
same lesson the wheel's idle-cash mechanism taught in options-income-sim
(9/9, 9/11) from a different track: a filter that looks like it's adding
discipline can really just be forcing more time in cash, which helps or
hurts depending entirely on which way the market that period happened to
go — not evidence the filter fixed anything about *how* RSI enters trades.

## Transaction costs: does a realistic per-trade cost change the ranking?

Every result above uses frictionless trades — this README's own "To
actually use this for real decisions" section has flagged that as unmodeled
since day one. `backtest.py` now accepts `cost_pct`, a round-trip-agnostic
friction cost (commission + slippage) deducted from the traded value on
every entry *and* every exit. `transaction_cost_test.py` sweeps a small,
realistic cost range (0% to 0.5% per trade) across all three strategies —
worth doing now specifically because the three strategies trade at very
different frequencies (SMA ~10 trades/path, RSI ~2.6-3.3, combined
~0.7-1.4), so a flat per-trade cost should not hit them equally:

```
python3 transaction_cost_test.py --paths 30
```

| Cost/trade | Scenario | Strategy | Win rate | Avg excess |
|---|---|---|---|---|
| 0.0% | Downtrend | SMA | 66.7% | +8.56p |
| 0.5% | Downtrend | SMA | 50.0% | +4.09p |
| 0.0% | Downtrend | RSI | 70.0% | +6.72p |
| 0.5% | Downtrend | RSI | 70.0% | +5.09p |
| 0.0% | Downtrend | Combined | 70.0% | +16.48p |
| 0.5% | Downtrend | Combined | 70.0% | +15.78p |

**Honest finding: SMA crossover's best result in this whole track — its
downtrend defensive edge — is also the most fragile to realistic trading
costs, for the simple reason that it's the strategy that trades the most.**
At a 0.5%-per-trade cost (a plausible retail commission-plus-slippage
figure, not an extreme one), SMA's downtrend win rate falls from 66.7% to
50.0% (a coin flip) and its average excess return is cut by more than half
(+8.56 to +4.09 pts) — while RSI's downtrend average only erodes 24% (+6.72
to +5.09) and the combined strategy's barely moves at all (+16.48 to
+15.78, -4%), because they simply trade far less often for the cost to bite
on. The uptrend losses for all three strategies barely move with cost —
they were already large enough that a few tenths of a percent per trade is
noise by comparison — so the real headline is specifically about SMA's
*good* result, not its bad one: the strategy whose frictionless numbers
looked most solid is the one whose edge shrinks fastest once a real broker
is involved, precisely because "trades more often" was never separated
from "trades better" until this sweep isolated it.

## To actually use this for real decisions

1. Run it locally (normal internet) with real historical data — either pip-install `yfinance` and dump a CSV, or export one from Yahoo Finance / Stooq.
2. Try it on strategies and assets you actually understand, over multiple time windows — one backtest window proves nothing.
3. Account for taxes, which this prototype still ignores (transaction costs now have a first-pass model via `--cost-pct`, see above, but taxes on realized gains do not).
4. If you ever want it to touch real money, that means wiring up a real brokerage API (e.g. Alpaca) with your own account and keys — a separate, deliberate step, not something to automate quietly.
