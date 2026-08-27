# Track C — Micro-SaaS landing page (demand smoke test)

"Calendarize" packages Track B's content-engine process as a product: tell it your niche, get a calendar of dated drafts back. This is a **smoke test**, not a built product — the standard, sane way to validate a paid-product idea is to see if anyone will give you their email for it *before* you spend weeks building it.

`index.html` is a self-contained static page — open it directly in a browser to preview it.

## The form doesn't actually collect emails yet

`action="#"` is a placeholder. To actually collect signups you need one of:
- **Formspring/Formspree/Getform** (free tier, no backend needed) — sign up, drop in the form endpoint they give you.
- **A Google Form** embedded or linked instead.
- **A real backend**, if you want more control — overkill for a smoke test.

Any of those requires *your* account, since it's where the emails would land.

## To actually run the test

1. Wire up email capture (above).
2. Get a domain or use a free host (Netlify/Vercel/GitHub Pages all support a static file like this for free).
3. Put it in front of ~100-500 people in the target audience (a relevant subreddit, a niche Facebook group, your own network) and see what fraction give their email.
4. **Decision rule:** a healthy landing-page conversion rate for a cold audience is often in the low single digits; well under 1% across a few hundred targeted visitors is a signal to rethink the idea before building anything, not a reason to build faster.
