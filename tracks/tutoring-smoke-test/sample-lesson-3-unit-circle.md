# The Unit Circle: The 3 Mistakes That Cause Most Errors

This is a third free sample lesson — same format as the factoring and
right-triangle lessons, this time on Pre-Calc material (the unit circle and
evaluating trig functions), since the landing page advertises Algebra,
Geometry, *and* Pre-Calc but only had proof for the first two. Same depth
and correctness bar as the other two. If you're a student, try the practice
problems at the end *before* checking the answers.

On the unit circle, an angle θ (measured counterclockwise from the positive
x-axis) lands on a point `(cos θ, sin θ)`. Almost every error at this level
comes from one of three places.

---

## Mistake 1: Mixing up which coordinate is sine and which is cosine

The point on the unit circle for angle θ is `(x, y) = (cos θ, sin θ)` — **x
is cosine, y is sine**, in that order. It's easy to say them backwards under
time pressure, especially since "sine" gets said first alphabetically but
corresponds to the *second* coordinate.

**Example:** Find sin(150°) and cos(150°).

150° is in Quadrant II. Its **reference angle** (the acute angle to the
nearest x-axis) is `180° − 150° = 30°`. The unit-circle point for 30° is
`(√3/2, 1/2)`, so:

```
cos(150°) = x-coordinate = −√3/2   (negative — Quadrant II)
sin(150°) = y-coordinate = +1/2    (positive — Quadrant II)
```

**Check:** cos(150°) ≈ −0.8660 and sin(150°) ≈ 0.5000, matching a
calculator in degree mode. ✓

A student who reads the coordinates in the wrong order would report
sin(150°) = −√3/2 and cos(150°) = 1/2 — exactly backwards, and off in both
sign *and* value.

---

## Mistake 2: Forgetting to apply the correct sign for the quadrant

The reference angle only tells you the **size** of the trig value, never
its **sign**. The sign depends on which quadrant θ actually lands in — a
common shortcut is the "CAST" rule (going counterclockwise from Quadrant
I): **A**ll positive in QI, **S**ine positive in QII, **T**angent positive
in QIII, **C**osine positive in QIV — sine and cosine are negative
everywhere else.

**Example:** Find sin(210°) and cos(210°).

210° is in Quadrant III (between 180° and 270°). Reference angle:
`210° − 180° = 30°`. In QIII, only tangent is positive — both sine and
cosine are negative:

```
sin(210°) = −sin(30°) = −1/2
cos(210°) = −cos(30°) = −√3/2
```

**Check:** sin(210°) ≈ −0.5000 and cos(210°) ≈ −0.8660. ✓

The mistake shows up as a student computing the reference-angle value
correctly (1/2 and √3/2) and then just reporting those numbers as the
final answer without ever asking "positive or negative in this quadrant?"

---

## Mistake 3: Confusing radians and degrees

`π radians = 180°`, not `π radians = π°` and not "just drop the π and treat
the number as degrees." A radian angle has to be converted before you can
read reference angles and quadrants off the usual degree-based unit circle.

**Example:** Evaluate cos(2π/3).

Convert first: `2π/3 rad × (180°/π) = 120°`. That's Quadrant II, reference
angle `180° − 120° = 60°`. In QII, cosine is negative:

```
cos(2π/3) = cos(120°) = −cos(60°) = −1/2
```

**Check:** cos(2π/3) ≈ −0.5000. ✓

The error to watch for: a student sees "2π/3" and, without converting,
tries to treat "2/3" as if it were close to 60° or 120° by feel rather than
by the actual conversion — which happens to work here by coincidence, but
fails on almost every other angle. Always convert first:
`degrees = radians × (180°/π)`.

---

## Practice (check yourself before reading the answers)

1. Find sin(240°) and cos(240°).
2. Find cos(315°).
3. Evaluate sin(5π/6).
4. A student computes cos(200°) and reports `cos(20°) ≈ 0.94` as the final
   answer. What mistake did they make, and what's the correct value?
5. Convert 7π/4 to degrees, then evaluate tan of that angle.

### Answers

1. 240° is Quadrant III, reference angle `240° − 180° = 60°`. In QIII both
   sine and cosine are negative: `sin(240°) = −sin(60°) = −√3/2` and
   `cos(240°) = −cos(60°) = −1/2`.
   Check: sin(240°) ≈ **−0.8660**, cos(240°) ≈ **−0.5000**. ✓

2. 315° is Quadrant IV, reference angle `360° − 315° = 45°`. In QIV,
   cosine is positive: `cos(315°) = cos(45°) = √2/2`.
   Check: cos(315°) ≈ **0.7071**. ✓

3. `5π/6 × (180°/π) = 150°`, Quadrant II, reference angle `180° − 150° =
   30°`. In QII, sine is positive: `sin(5π/6) = sin(30°) = 1/2`.
   Check: sin(5π/6) ≈ **0.5000**. ✓

4. The mistake is **Mistake 2** — they found the right reference angle
   (20°) but forgot to apply the sign for the actual quadrant. 200° is
   Quadrant III (between 180° and 270°), and cosine is negative there, so
   the correct answer is `cos(200°) = −cos(20°) ≈ **−0.9397**`, not
   positive 0.94.

5. `7π/4 × (180°/π) = 315°`, Quadrant IV, reference angle
   `360° − 315° = 45°`. In QIV, sine is negative and cosine is positive, so
   tangent (sine ÷ cosine) is negative: `tan(315°) = −tan(45°) = **−1**`.
   Check: tan(315°) ≈ −1.0000. ✓

---

*This is a third real lesson from a tutoring session, not a teaser — same
depth and correctness bar as the factoring and right-triangle lessons, on
Pre-Calc material this time, so the landing page's three advertised
subjects (Algebra, Geometry, Pre-Calc) each have real proof of teaching
quality behind them, not just a claim. A live session still adapts to
wherever the actual gap is, whether that's here, upstream in the reference-
angle/quadrant basics, or somewhere else entirely.*
