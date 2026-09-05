# money-machine

An experiment in finding a legitimate, semi-automatable income stream — not a "get rich quick" scheme. Nothing in here trades real money, posts to real social accounts, or charges real customers on its own. It builds and tests prototypes; a human (you) decides which one is worth pursuing for real and connects the accounts/credentials that step needs.

## Why it's structured this way

Anything that claims to make money "automatically and effortlessly" with no capital, no audience, and no risk is a scam pattern, not a strategy. The honest version of "passive income" is: build something once (a tool, an audience, a strategy, a system), that keeps paying off with decreasing marginal effort — but it still takes real work and often real capital up front, and it can lose money. This repo runs several small, independent experiments in parallel so we can see which one is worth doubling down on, instead of betting everything on one guess.

## Tracks

| Track | What it is | Status | To go live |
|---|---|---|---|
| [`tracks/invest-backtester`](tracks/invest-backtester) | Backtests simple trading strategies against historical price data | Prototype (sample data) | Point it at real market data + your own brokerage before risking money |
| [`tracks/options-income-sim`](tracks/options-income-sim) | Paper-simulates a covered-call ("the wheel", simplified) income strategy against buy-and-hold | Prototype (synthetic data + premium heuristic) | Options-approved brokerage account + real capital (100 shares/contract) before risking money |
| [`tracks/content-engine`](tracks/content-engine) | Repeatable process + real drafts for a content niche (audience → affiliate/ad revenue over time) | Prototype (10 real drafts, fact-checked) | Your social/blog accounts to actually publish |
| [`tracks/micro-saas-landing`](tracks/micro-saas-landing) | Landing page to smoke-test demand for a product idea before building it | **Live: [claude.ai/code/artifact/bd3a805a…](https://claude.ai/code/artifact/bd3a805a-3176-406f-8f4d-8c979fdb5eb5)** — real email capture (mailto, no new account) + a live shared signup counter | Share the page publicly, then put it in front of real people (a subreddit, a niche group) — that step needs your accounts |
| [`tracks/real-estate-analyzer`](tracks/real-estate-analyzer) | Screens rental property deals on paper (cash flow, cap rate, cash-on-cash return) | Prototype (sample deals) | Real listings, real financing quotes, and real inspection/legal/tax diligence before buying anything |
| [`tracks/tutoring-smoke-test`](tracks/tutoring-smoke-test) | Landing page + 2 real sample lessons (Algebra, Geometry) to smoke-test demand for high-school math tutoring | Prototype, same live-capable build as Calendarize, but **publishing it as a Claude Artifact was blocked by Claude Code's safety classifier** (likely: soliciting contact info for a service aimed at minors) — see its README | A host (Netlify/Vercel/GitHub Pages, or your own attempt at publishing it), somewhere to post it, and a look at local liability/background-check norms before taking minors as clients |

Note: unlike the other tracks, tutoring is a service business — it trades your hours for money and doesn't get more passive with scale the way the others can, unless it's later turned into a group or course format.

See `SCORING.md` for a side-by-side comparison of all tracks, and `PROGRESS.md` for the running log — it's updated as each track evolves.

## What this repo will never do on its own

- Place real trades or move real money
- Post to your real social media accounts
- Charge real customers
- Guarantee any income at all

Those all require you to plug in real accounts/API keys at a step you choose.
