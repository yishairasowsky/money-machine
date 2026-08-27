# Factoring Quadratics: The 3 Mistakes That Cause Most Errors

This is a free sample of the kind of teaching an actual tutoring session looks
like — not a marketing summary. If you're a student, try the practice
problems at the end *before* checking the answers.

We're factoring trinomials of the form `ax² + bx + c` into two binomials,
like `x² + 7x + 12 = (x + 3)(x + 4)`. Almost every factoring mistake at the
high school level comes from one of three places. Let's go through each one
with a worked example.

---

## Mistake 1: Skipping the GCF check

**Always look for a Greatest Common Factor across all three terms first.**
Skipping this step doesn't just make the numbers uglier — it can leave you
with an answer that *looks* factored but isn't fully factored, which many
teachers mark wrong.

**Example:** Factor `2x² + 20x + 42`.

Wrong approach (jumping straight to guessing binomials):
You'd need two numbers that multiply to `2 × 42 = 84` and add to `20`. That's
`6` and `14`. Splitting the middle term:

```
2x² + 6x + 14x + 42
= 2x(x + 3) + 14(x + 3)
= (2x + 14)(x + 3)
```

This is *correct* as far as it goes, but `(2x + 14)` still has a common
factor of 2 hiding inside it — the expression isn't fully factored yet.

Right approach — pull the GCF out first:

```
2x² + 20x + 42
= 2(x² + 10x + 21)
```

Now factor the simpler trinomial inside: two numbers that multiply to `21`
and add to `10` → `3` and `7`.

```
= 2(x + 3)(x + 7)
```

**Check by expanding:** `(x + 3)(x + 7) = x² + 7x + 3x + 21 = x² + 10x + 21`,
times 2 gives `2x² + 20x + 42`. ✓ Matches the original.

Same final answer either way once you finish reducing — but checking for a
GCF first gets you there with smaller numbers and less chance of stopping
one step too early.

---

## Mistake 2: Sign errors when picking the factor pair

When factoring `x² + bx + c`, you need two numbers that **multiply to `c`**
and **add to `b`**. The most common student error is finding a pair that
multiplies correctly but getting the *signs* wrong, so the sum comes out
wrong (or backwards).

**Example:** Factor `x² − 2x − 15`.

You need two numbers with product `−15` and sum `−2`. Since the product is
negative, the two numbers must have **opposite signs** — that's the first
thing to lock in before guessing.

Common wrong guess: `5` and `3` → sum `8` or `−8`, but never `−2`. Both
numbers being positive (or the pair `−5` and `−3`) can't work here because
their product would be positive, not negative.

Correct pair: `−5` and `3` → product `(−5)(3) = −15` ✓, sum `−5 + 3 = −2` ✓.

```
x² − 2x − 15 = (x − 5)(x + 3)
```

**Check by expanding:** `(x − 5)(x + 3) = x² + 3x − 5x − 15 = x² − 2x − 15`. ✓

**The rule of thumb:**
- If `c` is **positive**, both numbers have the **same sign** as `b`.
- If `c` is **negative**, the numbers have **opposite signs**, and the
  larger-magnitude one takes the sign of `b`.

---

## Mistake 3: Forcing a pattern that doesn't fit (or missing one that does)

Two related errors live here:

**3a — Missing a special pattern.** `x² − 9` is a **difference of squares**
(`a² − b² = (a − b)(a + b)`), not a trinomial, since the middle term is
missing (`b = 0`). It factors as:

```
x² − 9 = (x − 3)(x + 3)
```

A common mistake is writing `(x − 3)(x − 3)` out of habit from
same-sign trinomials. Check by expanding: `(x − 3)(x + 3) = x² + 3x − 3x − 9
= x² − 9`. ✓ Note `(x − 3)² = x² − 6x + 9`, a completely different
expression — that's the mix-up to watch for.

Similarly, `x² + 6x + 9` is a **perfect square trinomial**
(`a² + 2ab + b² = (a + b)²`):

```
x² + 6x + 9 = (x + 3)²
```

Check: `(x + 3)(x + 3) = x² + 3x + 3x + 9 = x² + 6x + 9`. ✓

**3b — Forcing a "factorization" on a trinomial that doesn't factor over
the integers.** Not every trinomial breaks into nice integer binomials, and
guessing-and-checking forever on one that doesn't is a common time sink.

Quick test: for `ax² + bx + c`, compute the discriminant `b² − 4ac`. If
it's a **perfect square**, integer factoring works. If it isn't (and
especially if it's negative), don't force it.

**Example:** `x² + 5x + 5`. Discriminant: `5² − 4(1)(5) = 25 − 20 = 5`. Since
5 isn't a perfect square, this trinomial does **not** factor into binomials
with integer coefficients — it needs the quadratic formula, and that's a
correct, complete answer to give ("this doesn't factor nicely"), not a sign
that you're doing something wrong.

---

## Practice (check yourself before reading the answers)

1. `x² + 7x + 12`
2. `x² − 5x + 6`
3. `3x² + 12x − 36`
4. `4x² − 25`
5. `x² + 5x + 5` (trick question — see if you can tell why)

### Answers

1. Two numbers multiplying to `12`, adding to `7` → `3` and `4`.
   `x² + 7x + 12 = (x + 3)(x + 4)`.
   Check: `x² + 4x + 3x + 12 = x² + 7x + 12` ✓

2. Two numbers multiplying to `6`, adding to `−5` → `−2` and `−3`.
   `x² − 5x + 6 = (x − 2)(x − 3)`.
   Check: `x² − 3x − 2x + 6 = x² − 5x + 6` ✓

3. GCF first: `3x² + 12x − 36 = 3(x² + 4x − 12)`. Numbers multiplying to
   `−12`, adding to `4` → `6` and `−2`.
   `= 3(x + 6)(x − 2)`.
   Check: `(x + 6)(x − 2) = x² − 2x + 6x − 12 = x² + 4x − 12`, times 3 gives
   `3x² + 12x − 36` ✓

4. Difference of squares: `4x² − 25 = (2x)² − 5² = (2x − 5)(2x + 5)`.
   Check: `4x² + 10x − 10x − 25 = 4x² − 25` ✓

5. Discriminant `= 25 − 20 = 5`, not a perfect square — this one doesn't
   factor over the integers. If you spent ten minutes guessing pairs for
   this one, that's normal, and recognizing *when to stop guessing and use
   the discriminant check* is itself the skill this lesson is teaching.

---

*This is one real lesson from a tutoring session, not a teaser. A live
session adapts to wherever the actual gap is — sign errors, GCF habits,
special patterns, or something upstream of factoring entirely, like
distributing or combining like terms.*
