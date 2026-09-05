# Track — High school math tutoring (demand smoke test)

A landing page + a real sample lesson for a 1-on-1 high school math tutoring
service (Algebra I/II, Geometry, Pre-Calc), angled at "get unstuck before
the test, not after" — proactive tutoring rather than crisis tutoring after
a bad grade. This is a **smoke test**, not a running business: the goal is
to see whether real families will hand over an email (and, from the sample
lesson, judge the teaching quality) before committing to actually taking
clients.

`index.html` is a self-contained page — open it directly in a browser to
preview it. It's built the same way as the Calendarize page in
`tracks/micro-saas-landing`: real email capture via `mailto:` (no
third-party form service or new account needed) and a live visitor counter
using Claude's `artifact` capability, both verified in Node before this was
written up.

**It is not published as a live Claude Artifact.** I tried, twice, and both
attempts were blocked by Claude Code's own safety classifier — most likely
because this is a public page soliciting contact information in the
context of a service aimed at tutoring minors, which is a reasonable thing
for that classifier to be cautious about. I'm not attempting to work around
it. If you want this one live too, the options are: publish it yourself
from claude.ai (you may have latitude I don't here), strip anything that
reads as directly soliciting minors' contact info and try again, or just
host `index.html` as a static file (Netlify/Vercel/GitHub Pages) instead of
as a Claude Artifact — the page works the same way either way, it just
loses the live shared counter (`claude.use('artifact')` resolves `null`
outside a Claude-served view, and the page already handles that gracefully
by only sending the `mailto:`).

`sample-lesson.md` is the actual value-proof artifact: a real, correct
diagnostic mini-lesson on factoring quadratics, good enough that a student
could genuinely learn from it, not just ad copy. `sample-lesson-2-right-triangles.md`
is a second one, on a different subject (Geometry — the Pythagorean
theorem — instead of Algebra), added so a prospective family can judge
teaching quality across more than one topic rather than trusting a single
example; every worked computation in it was checked in Python before
publishing (`python3 -c "import math; ..."` reproducing each step) to
confirm no arithmetic slipped through.

## Read this before treating it like the other tracks: it's economically different

Every other track in this repo (content engine, micro-SaaS landing,
investing backtester, real-estate analyzer) is trying to validate something
that can eventually run with your time only loosely coupled to the output —
content compounds, software scales to N users for near-zero marginal cost,
analysis tools run themselves. **Tutoring is not that.** It's a straight
service business:

- **You are trading hours for money, full stop.** One tutor, one student,
  one hour = one hour of income. There's no "publish once, sell forever"
  effect and no software leverage in the base model.
- **It doesn't scale without changing the model.** To grow revenue you
  either work more hours (caps out fast — there are only so many
  after-school and weekend hours, and burnout is real) or raise your rate
  (limited by the local market), or you change the *shape* of the
  business — turn the diagnostic method into a small-group class, a
  written course, a cohort program, or hire and manage other tutors. Any
  of those turns this into a different, more scalable business, but that's
  a distinct next step, not something this track builds or tests.
- **It usually pays more per hour, sooner, than the passive/content
  tracks.** A passive-income idea might take months to earn its first
  dollar, if ever. A tutoring hour is realistically billable almost
  immediately once you have one client — that's a genuine advantage this
  track has over the others, it's just not the same *kind* of income.

In short: this track tests "will people pay for this specific service,"
which is a fair and useful question, but a "yes" answer here proves
something narrower than a "yes" on a content or product track — it proves
you can sell your own hours, not that you've built something that runs
without you.

## What this actually tests

1. Will a real parent/student give an email for a free diagnostic call, off
   a landing page, for this specific angle ("before the test, not after")?
2. Does the sample lesson read as genuinely useful to someone evaluating
   whether to trust a stranger with their kid's grades — i.e., is the
   *proof of quality* actually convincing on its own?

It does **not** test: whether you can actually convert a fit call into a
paying client, whether you can sustain a teaching quality bar across many
different students and topics, or whether the pricing anchor below survives
contact with your actual local market.

## About the pricing numbers

The $45–$65/hr single-session range and the $170–$240 four-session package
in `index.html` are a **planning estimate**, not researched market data:
they're a rough, believable midpoint for independent (non-agency) high
school math tutoring rates in a typical US metro area as of 2026, based on
general knowledge of how platforms like Wyzant and Varsity Tutors price
this subject/level, not a live quote or a cited study. Real rates vary a
lot by region (major metro vs. smaller town), the tutor's credentials
(current teacher vs. college student vs. subject-matter specialist), and
whether it's test-prep-adjacent (which tends to command a premium). Treat
these numbers as a starting anchor to test, not a fact — check 3–5 local
listings (Wyzant, Varsity Tutors, or a local Facebook tutoring group) for
this subject/level before quoting a real family.

## To actually run this test

1. **Host it** — email capture is already wired (see above); it just needs
   a URL. Netlify/Vercel/GitHub Pages all serve a static page like this for
   free, or publish it as a Claude Artifact yourself if you want to try
   past the classifier block described above.
2. **Distribute it to the actual target audience**, not a general
   audience — this only means something if it reaches parents of high
   schoolers:
   - Local Facebook parent groups (town/neighborhood or your specific high
     school's).
   - Nextdoor, posted in your neighborhood.
   - School parent listservs or PTA newsletters, if you can get permission
     to post.
   - As an alternative/complementary distribution channel, list yourself
     directly on **Wyzant** or **Varsity Tutors** — they bring their own
     demand (at the cost of a commission), which is a useful comparison
     point against cold outreach with your own landing page.
4. **Decision rule** — same logic as the micro-SaaS track: put it in front
   of enough of the right people (dozens, not thousands — this is a local,
   narrow market, not an internet-scale one) and see what fraction give
   their email or book the free call. A near-zero response after a real
   attempt at the right audience is a signal to rethink the angle or the
   channel before doing more outreach the same way.

## Before taking any real client: legal/safety considerations

Tutoring minors is not a "just start" business the way a SaaS landing page
is — do real local research before you take a paying client, not after:

- **Background checks** — many school-affiliated listservs, tutoring
  platforms, and even some parents will expect or require one before
  allowing you near their kids. Look into what's standard/required in your
  specific area and, if working through a school, ask the school directly.
- **Liability/insurance** — consider whether you need any kind of tutoring
  liability coverage, especially if you tutor in person at your home or a
  student's home.
- **Local business/tax rules** — even informal tutoring income is usually
  taxable, and some localities require a business license for paid
  in-home services. This varies enough by state/locality that it's worth a
  specific local check, not a general assumption either way.

None of this is required to run the *smoke test* (a landing page and a
sample lesson collect no money and involve no minors directly), but it's
required before turning a "yes" signal into an actual client relationship.
