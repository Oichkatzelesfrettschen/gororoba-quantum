# Moreno's Stiefel elements: exact nullity in A_5 and A_6

The active [exact-contract record](nullity-exact-contracts.json) succeeds
[nullity.json](nullity.json) after the producer switched its multiplication cross-check
to exact rational arithmetic. Every scientific field retains its predecessor's value;
the producer hash records the changed implementation.

`nullity-exact-contracts.json` is written by `scripts/moreno_stiefel_nullity.py --out` and
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
the negative answer to the open question at A_6. Its determinant residues modulo
2^61 - 1 and 10^9 + 7 are retained and agree with an independent computation;
with the connectedness of V_2(R^31) they give generic invertibility of the
normalized A_6 Stiefel family (`docs/notes/math-0512517.md`). Each A_5 and A_6 entry
records its seed, the sha256 of its skew-symmetric matrix and of the exact
pair, the squared norm and the size of the cleared denominator. The script
checks its L_v construction against `cd_core.cd_multiply_exact` before measuring.

## Pfaffian reduction and identity test

[pfaffian-identity.json](pfaffian-identity.json) is written by
`scripts/stiefel_pfaffian_identity.py --out` and re-derived by `--check`
(gate core-660). For pure a, b in A_4, Moreno's Theorem 2.3 makes
L_(a,b)^2 the real form of A + iS = (L_a + i R_b)(L_a - i R_b), and
N = L_a + i R_b is complex skew-symmetric, so
|det L_(a,b)| = |Pf N|^4: a Stiefel element of A_5 is a zero divisor exactly
when the degree-8 polynomial Pf(L_a + i R_b) vanishes. The script checks
Theorem 2.3 and the skew-symmetry exactly on every e_i and e_i + e_j of the
30 pure coordinates (465 points, which decide an identity of degree 2).

The identity test draws Stiefel points over F_p, for the two largest primes
p = 1 mod 4 below 2^61, through the isotropic parametrization
z = a + i b, z' = a - i b of the complexified Stiefel variety:

| Points | rank N mod p | rank L_(a,b) mod p | Reading |
|---|---:|---:|---|
| 48 A_5 Stiefel points per prime | 14 | 28 | Pf N = 0, nullity 4 |
| 8 A_6 Stiefel points per prime (control) | 32 | 64 | Pf N != 0, as generic invertibility requires |
| 8 non-Stiefel A_5 points per prime (control) | 16 | 32 | full rank |

Clearing the parameters' denominators makes Pf N a polynomial of degree at
most 24 in them, so a Pfaffian whose restriction to the variety is nonzero
modulo p vanishes at one uniformly drawn point with probability at most
26/p, about 1.1e-17 (Schwartz-Zippel). The 96 vanishing A_5 points make a
generic counterexample to Moreno's question improbable at that rate and
prove nothing: the draws are seeded pseudorandom, a modulo-p rank bounds the
rational rank from below only, and the restriction could vanish modulo
these two primes alone. A numerical search over 560 real Stiefel points
finds no kernel vector of N given by a polynomial map of degree 1 or 2 in
(a, b) beyond the multiples of a.a - b.b and a.b, so a proof through an
explicit low-degree kernel vector does not exist at those degrees.
