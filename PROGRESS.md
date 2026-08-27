# Progress log

## 2026-08-27 — initial build

Set up three parallel experimental tracks (see `README.md` for the full picture):

- **Track A (invest-backtester):** built an SMA-crossover backtester. Confirmed this sandbox can't reach live market data (proxy returned 403 for a stooq.com fetch), so it ships with synthetic demo data. First finding: on the demo data, the 20/50 crossover *underperformed* buy-and-hold — consistent with the well-known evidence that simple crossover strategies rarely beat buy-and-hold after costs. Not yet run on real data.
- **Track B (content-engine):** picked "personal finance for beginners" as the demo niche, wrote 5 real drafts plus a 2-week content calendar and a repeatable topic→draft process. Not yet fact-checked or published anywhere.
- **Track C (micro-saas-landing):** built a static landing page smoke-testing demand for "Calendarize" (a product wrapping Track B's process). Email capture is a placeholder — needs a real form backend (Formspree/Google Form) to actually collect signups.

**Nothing has touched real money or real accounts yet.** Every "next step" above requires a decision or credential only the user can provide.

**Open decision for the user:** which track (if any) is worth the next real step — real market data + a paper-trading brokerage account for A, publishing to a real account for B, or a form backend + traffic source for C?
