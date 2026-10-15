# Moreno's Stiefel elements: exact nullity in A_5 and A_6

`nullity.json` is written by `scripts/moreno_stiefel_nullity.py --out` and
re-derived by `--check` (gate core-267). A Stiefel element of A_(n+1) is
v = (a, b) with a and b pure in A_n, a orthogonal to b and |a| = |b|
(math/0512517, Section 5), stored in cd_core's doubling convention.

| Algebra | Elements | Nullity | Certificate |
|---|---:|---:|---|
| A_5 | 24 Cayley-transform rational + 8 disjoint-support integer | 4 each | rank 28 mod 2^61 - 1 and 4 exact rational kernel vectors |
| A_6 | 24 Cayley-transform rational + 8 disjoint-support integer | 0 each | full rank of D L_v mod 2^61 - 1 |
| A_6 controls | Moreno Proposition 4.3, (e1 + e2, e3 + e4) and (e1 + e2, (e1 + e2) ee0) | 28 each | rank 36 mod P and 28 exact kernel vectors |

`a6_integer_witness` is the seed-0 disjoint-support element: an integer
vector of length 64 that is a Stiefel element of A_6 and not a zero divisor,
the negative answer to the open question at A_6. Each A_5 and A_6 entry
records its seed, the sha256 of its skew-symmetric matrix and of the exact
pair, the squared norm and the size of the cleared denominator. The script
checks its L_v construction against `cd_core.cd_multiply` before measuring.
