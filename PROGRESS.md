# Progress log

## 2026-08-27 — initial build

Set up three parallel experimental tracks (see `README.md` for the full picture):

- **Track A (invest-backtester):** built an SMA-crossover backtester. Confirmed this sandbox can't reach live market data (proxy returned 403 for a stooq.com fetch), so it ships with synthetic demo data. First finding: on the demo data, the 20/50 crossover *underperformed* buy-and-hold — consistent with the well-known evidence that simple crossover strategies rarely beat buy-and-hold after costs. Not yet run on real data.
- **Track B (content-engine):** picked "personal finance for beginners" as the demo niche, wrote 5 real drafts plus a 2-week content calendar and a repeatable topic→draft process. Not yet fact-checked or published anywhere.
- **Track C (micro-saas-landing):** built a static landing page smoke-testing demand for "Calendarize" (a product wrapping Track B's process). Email capture is a placeholder — needs a real form backend (Formspree/Google Form) to actually collect signups.

**Nothing has touched real money or real accounts yet.** Every "next step" above requires a decision or credential only the user can provide.

**Open decision for the user:** which track (if any) is worth the next real step — real market data + a paper-trading brokerage account for A, publishing to a real account for B, or a form backend + traffic source for C?

## 2026-08-27 — added Track D (real-estate-analyzer)

Built a stdlib-only rental property deal screener (`analyze.py`): mortgage amortization, cash flow, cap rate, and cash-on-cash return, driven by CLI flags or a CSV. Ran it on three invented sample deals ($260k–$380k range, same city tier) built to land in three different outcomes, and confirmed the intended contrast: a good deal (11.95% cash-on-cash, +$725/mo), a marginal/break-even one (0.32% cash-on-cash, +$19/mo), and a bad one with negative cash flow (-18.33% cash-on-cash, -$1,045/mo). The bad deal isn't rigged — it fails for the most common real reason deals fail, a purchase price too high relative to achievable rent.

**Still on paper.** This analyzes numbers typed in or put in a CSV; it never looks up a real listing, never talks to a lender, and never touches real money. Going further requires real listings (MLS/Zillow/a realtor), real financing quotes (rates vary by lender and credit), and real inspection/legal/tax diligence this tool doesn't replace.

## 2026-08-27 — added Track E (options-income-sim) and Track F (tutoring-smoke-test)

Built a stdlib-only covered-call ("the wheel", simplified) simulator against a synthetic price path, ran three scenarios (uptrend/flat/downtrend) with identical seed/vol/strike so only market direction varies. It reproduced the textbook trade-off honestly: in a +20%/yr uptrend, covered calls returned +43.37% vs. +48.14% buy-and-hold (underperformed by 4.78 pts — capped upside cost more than the 28.82%-of-equity premium collected); in flat and −15%/yr downtrend markets, the same premium income turned a loss/near-flat market into a small win (beat buy-and-hold by 1.78 and 4.19 pts respectively). Worth noting: the first parameter choice (5% OTM, 25% IV) made premium dominate in *all* scenarios including the uptrend, which didn't match how covered calls actually behave — the numbers above are after correcting to more realistic assumptions (8% OTM, 20% IV). A reminder that a backtest's conclusion can be an artifact of unrealistic inputs, not the strategy.

Also built a demand smoke-test for high-school math tutoring: a landing page plus one real, correctness-checked sample lesson (factoring quadratics — the 3 mistakes that cause most errors) as the actual value-proof, not just marketing copy. Flagged explicitly that this track is economically different from the rest: it's an hours-for-money service, not something that gets more passive with scale unless later turned into a group/course format — though it can pay sooner than the others while a real audience/track record doesn't exist yet.

**Nothing here executed a real options trade or booked a real tutoring client.** Options needs an options-approved brokerage account and real capital (100 shares/contract) most people don't want to risk on a first test; tutoring needs a real form backend and a place to post it, plus a look at local liability/background-check norms before taking on minors.

## 2026-08-27 — Calendarize is live; tutoring page blocked by safety classifier

Rebuilt the Calendarize and Unstuck Math (tutoring) landing pages as self-templating Claude Artifacts: real `mailto:` email capture (no third-party form service, no new account) plus a live signup counter powered by Claude's `artifact` capability, where each submission republishes the page's own state for every viewer. The self-regeneration logic (a page that reconstructs its own complete HTML from its own source, including nested `<script>` tags as embedded string data) had a real bug caught before publishing: an unescaped `</script>` inside that embedded data would have truncated the page's own script tag in any browser. Fixed by escaping to `<\/script>` at the data occurrences, then verified in Node — extracted and ran the logic headlessly, executed the self-templating function three levels deep (state → new state → new state again), and confirmed the output stayed valid HTML with the counter and pluralization correct at every level — before ever publishing.

**Calendarize published successfully:** https://claude.ai/code/artifact/bd3a805a-3176-406f-8f4d-8c979fdb5eb5 — a real, live, working page, not a mockup.

**The tutoring page's publish was blocked twice by Claude Code's own safety classifier**, most likely because it's a public page soliciting contact information for a service aimed at tutoring minors — a reasonable thing for that classifier to be cautious about. No workaround was attempted; the working file and the same live-capable design are in the repo, with the option to host it elsewhere (Netlify/Vercel/GitHub Pages) or have the user attempt the Artifact publish themselves, documented in its README.

**Still true:** neither page has reached a real stranger yet. Getting either one in front of real people (a subreddit, a niche Facebook/Discord group, Nextdoor) requires real social accounts this repo doesn't have and won't create — that step is still the user's.

## 2026-08-27 — business email confirmed working; email business-channel set up

User provided a dedicated business address, Calendarize@proton.me, wired it into both landing pages' `mailto:` links (replacing the personal Gmail), and republished Calendarize live. At the user's request, sent a test email Gmail → Proton to confirm the address actually receives outside mail (not just sends) — confirmed working, user received it in their Proton inbox. That closes out the one real risk flagged when the address was first wired in.

Also set up two automated cycles so the user doesn't need to keep this chat open: an hourly check of a dedicated Gmail thread for replies (treated as real instructions, acted on, confirmed back in-thread — this is how the Proton test request itself was picked up and executed), and a separate once-daily digest email summarizing repo-wide progress. The background loop has also been doing real, unprompted work between check-ins: added a second backtesting strategy (RSI mean-reversion, also lost to buy-and-hold, for a different reason than the first), added sensitivity analysis to the real-estate screener (surfaced that the "marginal" sample deal's positive cash flow isn't robust to a small rate move), and doubled the content-engine's drafted calendar to 10 posts.

## 2026-08-27 — business email wired; two tracks deepened in parallel

Wired the user's dedicated business email (Calendarize@proton.me) into both landing pages' `mailto:` contact, replacing the personal Gmail address; Calendarize republished live at the same URL.

Ran three background extensions in parallel:

- **Invest-backtester**: added a second strategy, RSI(14) mean-reversion, alongside SMA crossover. Genuine finding, not tuned to look good: on the demo data, RSI never fired a single trade (its low, ~32.6, never crossed the 30-oversold threshold) — 0% return vs. buy-and-hold's 51.6%, while SMA crossover (also previously reported) got +40.97% from 2 trades. Both strategies underperform buy-and-hold, for opposite reasons — bad timing vs. no signal at all — which is itself the honest takeaway: simple technical-indicator strategies aren't a free lunch.
- **Real-estate-analyzer**: added a `--sensitivity` flag showing cash-on-cash return and cash flow across a grid of purchase price (±10%) and interest rate (±1.5pp). Verified the base-grid cell reproduces the exact single-point numbers for all 3 sample deals (no computation drift). Real finding: the "marginal" Oakwood Ave deal flips to negative cash flow with just a +0.75pp rate move at the *same* price — ordinary quote-to-quote variation, not a stress test — while the "good" Maple Street deal stays cash-flow-positive across the entire grid. The real difference between "good" and "marginal" here isn't the size of the headline number, it's how much margin for error the deal has.
- **Content-engine**: a second batch of 5 drafts (house affordability, car loan payoff vs. investing, credit score needs, HSAs, index funds vs. individual stocks) filling out the rest of the posting calendar — 10 real drafts now ready across the two batches, none published anywhere yet.

Also set up a faster response loop: an hourly check (separate from the once-daily digest) that reads the business-email thread for new replies from the user and acts on them within the hour, since there's no push/webhook mechanism available for Gmail (confirmed by tool search) — polling is the honest ceiling on responsiveness here, not instant.
