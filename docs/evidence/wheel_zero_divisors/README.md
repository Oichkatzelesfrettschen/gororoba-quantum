# What the wheel of fractions detects in Cayley-Dickson zero divisors

`result.json` is the output of `scripts/wheel_zero_divisors.py --out`. The
script uses exact rational arithmetic and spreads independent elements and
pairs over `parallel.ordered_map`. Every random draw happens first, in seeded
order (seed 20041029), so pooled and serial runs write the same bytes.

The record tests Carlstrom's wheel of fractions against the zero divisors of
the Cayley-Dickson algebras:

- `gororoba_quantum/wheel_algebra.py` is the wheel over Q.
- `gororoba_quantum/gaussian_wheel.py` is the wheel over Q(i).
- `gororoba_quantum/cd_core.py` is the specification. `cd_core.cd_sign`
  builds every product and every left and right multiplication matrix.
- `cross_check_cd_core` checks that arithmetic against
  `cd_core.cd_multiply` and `cd_core.left_mult_matrix`. It uses 24 seeded
  small-integer vector pairs, six in each of dimensions 4, 8, 16 and 32,
  where float arithmetic is exact.

Gates:

| gate | command |
| --- | --- |
| core-494 | `"$PYTHON" scripts/wheel_zero_divisors.py --check docs/evidence/wheel_zero_divisors/result.json`, normal and `-O` |
| core-497 | `"$PYTHON" scripts/wheel_zero_divisors.py --self-test`, normal and `-O` |
| core-498 | `"$PYTHON" gaussian_wheel.py --self-test` from `gororoba_quantum/`, normal and `-O` |

`--check` recomputes every field and compares the rendered JSON byte for
byte. The one exception is `pyadic_cross_check`. `--out` writes it when
pyadic imports, and CI does not pin pyadic. In that cross-check, pyadic 0.3.0
`GaussianRational` recomputed the norm N(a) and the two-sided inverse of all
61 Q(i) rows, and all 61 agree.

## Elements

| family | dimension | elements | source |
| --- | --- | --- | --- |
| corpus | 16 | 84 | every element e_i + t e_j of `cd_core.sedenion_zero_divisor_corpus()` (336 signed pairs) |
| two-term | 16 | 156 | every other e_i +- e_j, 0 <= i < j <= 15, including e0 +- e_j and cd_core's counterexamples e0 + e9, e1 + e9 |
| random | 16 | 32 | seeded rational coefficients +-n/d, n and d in 1..9 |
| frame | 16 | 16 + 16 | a = q (u, v) with (u, v) a Cayley-frame orthonormal pure octonion pair (`moreno_stiefel_nullity.cayley_frame`) and q a seeded positive rational; b a seeded rational combination of the four exact kernel vectors of L_a |
| composition | 4, 8 | 96 | every imaginary e_i +- e_j and 24 seeded rationals per dimension |
| dimension 32 | 32 | 16 | the first four elements of each mod-p nullity stratum of the 930 imaginary e_i +- e_j, in index order |
| Q(i) | 4, 8, 16 | 61 | fixtures e0 + i e1, e0 - i e1, e0, 0 (and e1 + e10 at 16); 8 isotropic c (u + i v) per dimension, with (u, v) a Cayley-frame pair and c a seeded Gaussian rational; 8 anisotropic per dimension with seeded Gaussian-rational coefficients |

Two rank measurements accompany every wheel verdict:

- the exact rank of L_a over Q;
- the rank modulo P = 2^61 - 1 of L_a with each row scaled to integers.

The modular rank is a lower bound on the rational rank.

## Predictions and verdicts

Each prediction and its falsifier were stated before the run.

### W1: a sedenion zero divisor is invertible; cancellation fails. PASS

**Prediction.** Every nonzero real a has the two-sided inverse
conj(a) / |a|^2. If ab = 0 with b != 0, the associator gives

(a^-1, a, b) = (a^-1 a) b - a^-1 (a b) = b - 0 = b,

so cancellation fails. The sedenion product is noncommutative and
nonassociative, so the wheel's commutative-monoid axioms cannot describe it.

**Falsifier.** Any of the following:

- a corpus product that is not exactly zero;
- an inverse that is not two-sided;
- a zero-product pair whose associator differs from b.

**Measured.**

- All 336 corpus pairs give an exact zero product through `cd_core.cd_multiply`
  and through the exact `cd_sign` product.
- All 336 also give ba = 0.
- All 16 Cayley-frame pairs give ab = ba = 0 exactly.
- On all 352 pairs, a has a two-sided inverse, a^-1 (ab) = 0 != b, and the
  associator (a^-1, a, b) equals b.

Basis counts from `cd_core`:

| dimension | ordered noncommuting pairs of imaginary units | nonassociating ordered triples |
| --- | --- | --- |
| 4 | 6 | 0 of 64 |
| 8 | 42 | 168 of 512 |
| 16 | 210 | 1848 of 4096 |

The 1848 of 4096 is the count in docs/notes/algebra_circuit_rules.md's 25/256 witness expectation.

### W2: the Gram detector is exact for left zero divisors. PASS

**Prediction.** G = L_a^T L_a is positive semidefinite, and it is positive
definite exactly when L_a is nonsingular.

- If G is positive definite, every leading principal minor is positive
  (Sylvester's criterion), so every natural-order pivot is finite and
  nonzero. `wheel_algebra.solve(G, L_a^T e_0)` then returns the unique
  solution of a x = 1, which is a^-1.
- If L_a is singular, some pivot is zero. The involution turns it into
  infinity. In a PSD matrix the sub-column under a zero pivot is also zero,
  so the elimination factor is 0 * infinity = bottom. Bottom then reaches
  every later row and every back-substituted component.
- For D = 4 and 8, G = |a|^2 I.

**Falsifier.** Any of the following:

- a wheel verdict that disagrees with rank;
- a finite result different from `fraction_solve` or from conj(a) / |a|^2;
- a singular element with a finite component;
- a composition-algebra Gram matrix other than |a|^2 I.

**Measured agreement.** Wheel verdict against rank over Q and rank modulo P:

| set | rows | wheel bottom, both ranks singular | wheel finite, both ranks full | all three agree |
| --- | --- | --- | --- | --- |
| composition, D = 4 and 8 | 96 | 0 | 96 | 96 |
| sedenion corpus | 84 | 84 | 0 | 84 |
| sedenion two-term outside the corpus | 156 | 0 | 156 | 156 |
| sedenion random rational | 32 | 0 | 32 | 32 |
| sedenion Cayley-frame a and b | 32 | 32 | 0 | 32 |
| dimension 32 sample | 16 | 12 | 4 | 16 |

**Finite results.** All 288 finite results equal both `fraction_solve` and
conj(a) / |a|^2.

**Singular results.**

- Each of the 128 singular elements gives bottom in every component.
- `fraction_solve` raises ZeroDivisionError on all 128.
- The first zero pivot of G falls at index 9 to 20, always before the last
  index.

**Gram identity.**

- G = |a|^2 I on all 96 composition elements.
- G = |a|^2 I also holds on all 156 two-term sedenion non-zero-divisors,
  where G = 2I.
- It fails on the random and zero-divisor sedenions.
- This is the eigenvalue split {0, 2, 4} of the research-state claim
  `singular-sector-split`.

**Left versus right.** The detector reads L_a, so it detects left zero
divisors. On all 304 sedenion elements, rank R_a = rank L_a, and every
zero-product pair above has ba = 0 as well.

**Pair-level control.** The 336 bright controls (e_i + t e_j)(e_k - s e_l)
were read by `cd_core.cd_multiply` and by the exact product:

- All 336 products are nonzero.
- Both factors of every bright pair are corpus elements, with singular L and
  a bottom wheel verdict.
- A zero product is therefore a property of the pair, read by multiplying. A
  singular L_a is a property of one element.

**Negative control.** The control solves L_a x = e_0 directly, with no Gram
matrix, on the 156 invertible two-term sedenions:

- A pure element has a zero diagonal, so the first pivot is zero.
- All 126 invertible pure two-term sedenions read bottom, a false
  "singular".
- The 30 elements e0 +- e_j, where a_0 != 0, read finite.
- The detector is the Gram matrix ordered by Sylvester's criterion. The
  wheel alone detects nothing.

### W3: the wheel verdict carries no nullity and no consistency. PASS

**Prediction.** The wheel verdict is binary. Bottom swamps every component,
so it gives the same output for every nonzero nullity. It also gives the
same output with an inconsistent right-hand side.

**Falsifier.** Either of the following:

- a singular stratum whose verdict differs from the others;
- a kernel-vector right-hand side that yields anything but all bottom.

**Measured.** Nullity against wheel verdict:

| algebra | nullity | elements | wheel verdict |
| --- | --- | --- | --- |
| sedenions | 0 | 188 | finite |
| sedenions | 4 | 116 | bottom (16 of 16) |
| dimension 32 sample | 0 | 4 | finite |
| dimension 32 sample | 4 | 4 | bottom (32 of 32) |
| dimension 32 sample | 8 | 4 | bottom (32 of 32) |
| dimension 32 sample | 12 | 4 | bottom (32 of 32) |

**Dimension 32 census.** The 930 imaginary e_i +- e_j have these nullities
modulo P:

| nullity | elements |
| --- | --- |
| 0 | 342 |
| 4 | 168 |
| 8 | 168 |
| 12 | 252 |

On the 16 sampled elements, the exact rank over Q equals the modular rank.

**Inconsistent right-hand side.** For each of the 128 singular elements, the
solve used an exact kernel vector k of L_a. That vector is orthogonal to
range(G) = range(L_a^T), so G x = k has no solution. The result is all
bottom on all 128, the same output as for the consistent system.

The signal is lost because the first zero pivot comes before the last index
on all 128 elements (indices 9 to 20). The resulting bottom factor reaches
the last row before back substitution. A zero pivot only at the last index
can still separate the two cases. wheel_algebra's self-test fixture
[[1, 1], [1, 1]] shows this: it reads infinity for an inconsistent
right-hand side and bottom for a consistent one.

Nullity, kernels and consistency come only from rank.

### W4: the wheel over Q(i) flags isotropy exactly. PASS

**Setup.** Over Q(i):

- conj is Cayley-Dickson conjugation. It negates the imaginary units and
  leaves the Q(i) coefficients alone.
- N(a) = sum a_k^2 is the complex-bilinear norm, with a conj(a) = N(a) e_0.
- Complex conjugation enters only in the scalar division of Q(i) and in the
  Hermitian Gram L_a^H L_a.

**Prediction.**

- If N(a) != 0, the totalized inverse conj(a) * /N(a) is finite and is a
  two-sided inverse.
- If N(a) = 0, the inverse is infinity on each nonzero coefficient of
  conj(a) and bottom on each zero coefficient. Then a conj(a) = conj(a) a = 0
  is a zero product with a nonzero factor.
- In D = 4 and 8, isotropy coincides with a singular L_a. In D = 16,
  isotropy is sufficient but not necessary.

**Falsifier.** Any of the following:

- an inverse pattern that differs from the prediction;
- an anisotropic inverse that is not two-sided;
- an isotropic element with a nonsingular L_a;
- an anisotropic singular element in D = 4 or 8.

**Measured.**

| D | elements | nonzero isotropic | anisotropic | inverse pattern as predicted | anisotropic inverse two-sided | isotropic: a conj(a) = conj(a) a = 0 and L_a singular | anisotropic with L_a singular | Hermitian Gram verdict agrees with rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 20 | 10 | 9 | 20 | 9 | 10 | 0 | 20 |
| 8 | 20 | 10 | 9 | 20 | 9 | 10 | 0 | 20 |
| 16 | 21 | 10 | 10 | 21 | 10 | 10 | 1 (e1 + e10) | 21 |

**Fixtures.**

- e0 + i e1 and e0 - i e1 give an inverse of 2 infinities and D - 2
  bottoms.
- 0 gives D bottoms.
- e0 gives D finite components.

**Ranks.** The exact rank over Q(i) equals half the rank modulo P of the
realified matrix on all 61 rows.

### W5: scope. Statement, no measurement

What the wheel adds:

- Exact arithmetic that is total and raises no exceptions. In a
  "divide, then check" pipeline, a singular step becomes a bottom or
  infinity that propagates through every later operation. Without the wheel,
  the same step raises an exception or needs a guard at every division.
- Inside elimination, the code has no branch on zero. The test moves into
  each element's canonical form: `Wheel.__init__` and
  `GaussianWheel.__init__` test the denominator.
- A semantic home for the isotropic cone of the complexified norm. There,
  1/N(a) is a real division by zero, and the resulting pattern of infinity
  and bottom marks the support of conj(a).

What it leaves to exact rank and cd_core:

- the size of a kernel (nullity 4, 8 or 12);
- kernel vectors;
- whether a singular system is consistent;
- left versus right annihilators;
- the box-kite and assessor geometry of which pairs multiply to zero.

## What the wheel gives for zero divisors

A real Cayley-Dickson zero divisor is an invertible element. Its inverse
conj(a) / |a|^2 has a positive rational denominator, so the wheel's 1/0
never arises in the algebra's own division. What breaks is cancellation,
through the associator (a^-1, a, b) = b.

The wheel acts on the linear algebra of left multiplication. Elimination in
natural order on the Gram matrix L_a^T L_a stays finite exactly when a is not
a left zero divisor. It then returns a^-1, and it returns bottom in every
component otherwise. This makes it an exact binary detector, and it agreed
with exact and modular rank on all 304 sedenion elements, 96 composition
elements and 16 dimension-32 elements. The detector is the Gram matrix with
Sylvester's ordering. The same elimination applied to L_a itself calls 126
invertible elements singular.

Bottom carries one bit. Nullity 4, 8 and 12 and an inconsistent right-hand
side all read the same, so the strata and kernels of the zero-divisor
geometry stay with exact rank and cd_core.

Over Q(i), the norm is isotropic, and there the wheel does what it was built
for. conj(a) * /N(a) is a two-sided inverse off the cone. On the cone it is a
pattern of infinity and bottom, and the element is a zero divisor through
a conj(a) = 0. Up to dimension 8, that cone is exactly the set of zero
divisors. In the sedenions, the real zero divisors lie off the cone.
