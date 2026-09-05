# Right Triangles & the Pythagorean Theorem: The 3 Mistakes That Cause Most Errors

This is a second free sample lesson — same format as the factoring lesson,
different subject (Geometry instead of Algebra), so you can judge teaching
quality across more than one topic before trusting a stranger with your
kid's grades. If you're a student, try the practice problems at the end
*before* checking the answers.

For any right triangle with legs `a` and `b` and hypotenuse `c`:
`a² + b² = c²`. Almost every error at the high school level comes from one
of three places. Let's go through each one with a worked example.

---

## Mistake 1: Mislabeling which side is the hypotenuse

**The hypotenuse is always the side opposite the right angle, and it's
always the longest side.** The most common setup error is plugging a given
side into the `c` slot just because it's listed last in the problem, without
checking whether it's actually opposite the right angle.

**Example:** A right triangle has legs of length 6 and 8. Find the
hypotenuse.

```
c² = 6² + 8² = 36 + 64 = 100
c = √100 = 10
```

**Check by working backwards:** `10² = 100`, and `6² + 8² = 36 + 64 = 100`.
✓ Matches.

The error shows up on messier problems: given a right triangle with one leg
9 and hypotenuse 15, a student who isn't sure which number is `c` might
plug both 9 and 15 in as legs and solve for a "hypotenuse" bigger than 15 —
which should be a red flag, since the hypotenuse can never be shorter than
either leg, and here it would be a sign the wrong side got labeled `c`.

---

## Mistake 2: Adding when you should subtract (solving for a leg, not the hypotenuse)

The formula `a² + b² = c²` only adds two squares directly when you're
solving *for the hypotenuse*. If you're solving for a **leg** instead, you
need to isolate it first — which means **subtracting**, not adding.

**Example:** A right triangle has one leg of length 9 and a hypotenuse of
15. Find the other leg.

Wrong approach (adding instead of subtracting):
```
9² + 15² = 81 + 225 = 306 → √306 ≈ 17.5   ✗ (too big — bigger than the hypotenuse itself, impossible)
```

Right approach — isolate the missing leg first:
```
a² = c² − b²
a² = 15² − 9² = 225 − 81 = 144
a = √144 = 12
```

**Check by expanding:** `9² + 12² = 81 + 144 = 225`, and `15² = 225`. ✓
Matches.

**The rule of thumb:**
- Solving for the **hypotenuse** → **add** the two legs' squares.
- Solving for a **leg** → **subtract** the known leg's square from the
  hypotenuse's square, then take the square root of what's left.

A missing leg can never come out larger than the hypotenuse — if your
answer does, that's a sign you added when you should have subtracted.

---

## Mistake 3: Using the theorem on a triangle that isn't actually a right triangle

`a² + b² = c²` only holds for **right** triangles. Two related errors live
here:

**3a — Assuming a triangle is right-angled just because a problem gives
three side lengths.** Not every triangle with three known sides has a right
angle. You can check with the **converse of the Pythagorean theorem**: if
the sum of the squares of the two shorter sides equals the square of the
longest side, it's a right triangle; if not, it isn't.

**Example:** Is a triangle with sides 5, 6, and 8 a right triangle?

```
5² + 6² = 25 + 36 = 61
8² = 64
61 ≠ 64  →  not a right triangle
```

Since the two don't match, this triangle has no right angle at all — the
Pythagorean theorem simply doesn't apply to it, and trying to force
`a² + b² = c²` onto it (or "solve" for a missing angle with it) is a
category error, not a computation one.

**3b — Missing common Pythagorean triples, which cost time on triangles
that don't need a calculator at all.** A few whole-number combinations
recur constantly in textbook problems: `3-4-5`, `5-12-13`, `8-15-17`,
`7-24-25` — and any whole-number multiple of them (like `6-8-10`, which is
just `3-4-5` doubled, or `9-12-15`, which is `3-4-5` tripled). Recognizing
one of these on sight turns a square-root problem into instant recall.

**Example:** A right triangle has legs 9 and 12. Recognize `9 = 3×3` and
`12 = 3×4` — this is a `3-4-5` triple scaled by 3, so the hypotenuse is
`3×5 = 15` without needing to compute `9² + 12²` at all.

**Check:** `9² + 12² = 81 + 144 = 225`, and `15² = 225`. ✓ Confirms the
shortcut matches the long way.

---

## Practice (check yourself before reading the answers)

1. Legs 5 and 12. Find the hypotenuse.
2. One leg is 7, hypotenuse is 25. Find the other leg.
3. Legs 9 and 12. Find the hypotenuse. (Look for a shortcut before you compute.)
4. A triangle has sides 5, 6, and 8. Is it a right triangle?
5. Hypotenuse 17, one leg 8. Find the other leg.

### Answers

1. `5² + 12² = 25 + 144 = 169`, `√169 = 13`. Hypotenuse is **13**.
   (This is the `5-12-13` triple.)
   Check: `5² + 12² = 169 = 13²` ✓

2. Solving for a leg — subtract, don't add: `25² − 7² = 625 − 49 = 576`,
   `√576 = 24`. Other leg is **24**.
   (This is the `7-24-25` triple.)
   Check: `7² + 24² = 49 + 576 = 625 = 25²` ✓

3. Shortcut: `9 = 3×3`, `12 = 3×4` → `3-4-5` triple scaled by 3 →
   hypotenuse `= 3×5 = 15`.
   Check the long way: `9² + 12² = 81 + 144 = 225 = 15²` ✓

4. `5² + 6² = 61`, but `8² = 64`. `61 ≠ 64`, so **no**, this is not a right
   triangle — the converse test fails, and the Pythagorean theorem doesn't
   apply here at all. If you spent time trying to "solve" this one, that's
   normal — recognizing *when the theorem doesn't apply* is itself the
   skill this lesson is teaching.

5. Solving for a leg — subtract: `17² − 8² = 289 − 64 = 225`, `√225 = 15`.
   Other leg is **15**.
   (This is the `8-15-17` triple.)
   Check: `8² + 15² = 64 + 225 = 289 = 17²` ✓

---

*This is a second real lesson from a tutoring session, not a teaser — same
depth and correctness bar as the factoring lesson, on a different subject
(Geometry instead of Algebra), so the teaching quality can be judged across
more than one topic before booking a real session. A live session still
adapts to wherever the actual gap is, whether that's here, upstream in
basic arithmetic with squares and square roots, or somewhere else entirely.*
