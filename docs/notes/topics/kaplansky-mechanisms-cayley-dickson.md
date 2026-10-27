# Kaplansky-type mechanisms in the Cayley-Dickson algebras

Three unrefereed openai/math manuscripts claim counterexamples to Kaplansky-type conjectures: the zero-divisor
conjecture for group algebras of torsion-free groups
([family 196](../papers/openai-2026-torsion-free-zero-divisors.md)), the direct-finiteness conjecture for every
group algebra, with a torsion-free group ([family 197](../papers/openai-2026-torsion-free-not-directly-finite.md)),
and the Kadison-Kaplansky projection conjecture for reduced group C*-algebras of torsion-free groups
([family 285](../papers/openai-2026-kadison-kaplansky-projection.md)), whose projection lies outside the group
ring. The Cayley-Dickson algebras of `cd_core` are twisted group algebras `R^sigma[Z_2^k]` of a torsion group, with
`e_p e_q = sigma(p, q) e_(p xor q)` and `sigma = cd_sign`. No theorem is shared between the two settings; this note
compares mechanisms. Tags: [P] source statement, [E] exact computation in
[kaplansky-cd-mechanisms](../../evidence/kaplansky-cd-mechanisms/README.md) (gate sources-412), [T] written
argument, [I] interpretation.

## Summary

| Property | Group algebras `K[G]`, `G` torsion-free | Cayley-Dickson algebra of dimension `D = 2^k` |
| --- | --- | --- |
| Torsion zero divisors `(1 - g)(1 + g) = 0` | excluded by hypothesis | absent: `e_m^2 = -1` for every `m != 0` [E] |
| No zero divisors | false over `F_2` (family 196) [P] | holds for `D <= 8`; fails at `D = 16` [E] and at every larger `D`, which contains the sedenions as the subalgebra `(a, 0)` [T] |
| Direct finiteness (every group) | false over `F_2` with `G` torsion-free (family 197) [P]; true in characteristic zero | holds at every `D`, from `ker L_a = ker R_a` ([math/0511691](../math-0511691.md) Corollary 9.3) [P] |
| No idempotents besides 0, 1 | group ring of family 285's group satisfies it; the reduced C*-completion does not [P] | holds at every `D`, and no nonzero nilpotents [T], from power-associativity ([math/0405424](../papers/math-0405424.md)) |
| A unit is never a zero divisor; inverses are unique | holds (associativity) | both false from `D = 16`: `e_1 + e_10` is a zero divisor with two distinct two-sided inverses [E] |

## Zero products as fiber cancellation

[T] A product `alpha beta` of two finite sums vanishes exactly when, for every group element `z`, the coefficients
of the terms `p q = z` with `p` in the support of `alpha` and `q` in that of `beta` sum to zero. Family 196 makes
every fiber even in size and works over `F_2` ([P] its equation (1.2) and the degree-sum argument on p. 24). The
sedenions cancel fibers of size two by sign.

[T] Two-blade criterion. Let `i, j, k, l` be distinct nonzero indices and `t, s = +-1`. Then
`(e_i + t e_j)(e_k + s e_l) = sigma(i,k) e_(i xor k) + s sigma(i,l) e_(i xor l) + t sigma(j,k) e_(j xor k) + t s sigma(j,l) e_(j xor l)`.
Since `i != j` and `k != l`, the labels `i xor k` and `j xor k` differ, and so do `i xor k` and `i xor l`; a label
can cancel only against its diagonal partner, so a zero product needs `i xor k = j xor l` and
`i xor l = j xor k`, both equivalent to the skeleton condition `i xor j = k xor l`. On the skeleton the product
vanishes exactly when `t s = -sigma(i,k) sigma(j,l)` and `t s = -sigma(i,l) sigma(j,k)`. These agree exactly when
the cocycle cross-ratio

    chi(i, j; k, l) = sigma(i,k) sigma(j,l) sigma(i,l) sigma(j,k)

equals `+1`, and then `t` is free and `s` is fixed: two signed zero products per skeleton pair (and four over the
two orders of the factors).

[T] Gauge invariance. A re-signing `e_a -> f(a) e_a`, `f(0) = 1`, changes `sigma(p, q)` to
`f(p) f(q) f(p xor q) sigma(p, q)`. In `chi` each of `f(i), f(j), f(k), f(l)` appears twice, and on the skeleton
`i xor k = j xor l` and `i xor l = j xor k`, so the label factors also pair up and `chi` is unchanged.

[E] Counts over ordered pairs of index pairs:

| D | skeleton pairs | `chi = +1` | signed zero products | zero products off the skeleton | index pairs carrying a zero divisor |
| --- | --- | --- | --- | --- | --- |
| 8 | 42 | 0 | 0 | 0 | 0 |
| 16 | 630 | 168 | 336 | 0 | 42 (84 signed elements) |
| 32 | 6510 | 2520 | 5040 | 0 | 294 (588 signed elements) |

`chi` predicts the brute-force sign lift on every skeleton pair, a search over every disjoint pair of pairs finds no
zero product off the skeleton, and `chi` is unchanged under each of the `D - 1` single-index flips, which generate
every re-signing. At `D = 16` the `chi = +1` pairs have `m = i xor j` in 9..15, 24 each.

[I] Prior art. The 42 index pairs are de Marrais's assessors, the seven values of `m` are his box-kites
(`m = 8 xor S` for strut constant `S`), and `chi = +1` on a pair of assessors is his edge law: a non-strut pair has
two vanishing diagonal products, a strut pair none
([box-kite monograph inventory](box-kites/inventory-monographs.md), claims A1-A5; the necessity of matching XOR
labels is a rule of [algebra_circuit_rules.md](../algebra_circuit_rules.md#sedenion-determinant-and-membership)). What
this note adds is the form of the condition: an `F_2` skeleton, the zero-divisor condition of the untwisted
`F_2[Z_2^k]`, times a gauge-invariant `Z_2` obstruction `chi`. Reducing the integral Cayley-Dickson order modulo 2
deletes the sign table and leaves `F_2[Z_2^k]`, commutative and associative, where every skeleton pair is a zero
divisor and `(g_i + g_j)^2 = 0`. Family 196's parity mechanism lives entirely in that skeleton; the Cayley-Dickson
sign is what keeps most of it from lifting to the reals.

## The Fano plane on both sides

- [E] The seven lines `{i, j, fano_completion(i, j)}` of the octonion table are the XOR triples, meet pairwise in one
  point and have three points each, so their incidence Gram matrix is all-ones modulo 2. Family 196 needs exactly
  this odd line-intersection property and takes it from the projective plane over `F_q` with `q = 128` ([P] its
  pp. 3-4); the octonion Fano plane is the `q = 2` member of the same family of planes.
- [E] Family 197 adjoins seven extra labels indexed by the Fano plane and uses the complements of its lines ([P] its
  p. 5). Those complements are the nontrivial cosets `x xor (L cup {0})` of the order-4 subgroups of `Z_2^3`, the
  index sets of `O` minus a quaternion subalgebra `H_L` in the doubling `O = H_L + H_L e_x`. The replay confirms the
  paper's incidence counts (four elements, pairwise intersection two, four per point, two per pair of points).
- [I] Both manuscripts use the Fano plane as an incidence design only; the octonion signs, which decide every
  Cayley-Dickson zero divisor, play no role there.

## Direct finiteness

[T] Every real Cayley-Dickson algebra is directly finite: ker L_a = ker R_a for every a (Corollary 9.3 of
[math/0511691](../math-0511691.md)), so `ab = 1` forces `ba = 1`, and the solutions of `ab = 1` form the affine
space `conj(a)/N(a) + ker L_a`. The proof through the trace-form adjoint identities, its lemma attributions and the
gated exact replay are the content of [cd-one-sided-inverses.md](cd-one-sided-inverses.md), which owns the
statement; this note records only the comparison.
[E] The replay confirms the mechanism on every two-blade zero divisor: all 84 at `D = 16` (nullity 4) and all 588 at
`D = 32` (nullities 4, 8 and 12 on 168, 168 and 252 elements) have kernels of pure elements that right
multiplication by `a` also annihilates.

## Idempotents and nilpotents

[P] Every Cayley-Dickson algebra is flexible and power-associative, and a pure `p` satisfies `p^2 = -|p|^2 e_0`
(Moreno, [math/0405424](../papers/math-0405424.md), p. 2). [T] Hence every `x = r + p` with `p` pure satisfies
`x^2 = 2 r x - N(x)`. If `x^2 = x` with `p != 0`, comparing pure parts gives `r = 1/2`, and the real part gives
`r^2 - N(p) = r`, so `N(p) = -1/4`, impossible; with `p = 0`, `x` is 0 or 1. For nilpotents, `R + R p` is a
subalgebra isomorphic to `C` when `p != 0` (`R` alone when `p = 0`); power-associativity places every power of `x`
in it, and `C` has no nonzero nilpotents, so `x^n = 0` forces `x = 0`. The untwisted `R[Z_2^k]` has the idempotents
`(1 +- g)/2` for every `g != 0`; the sign table turns `g` into a unit with `e_m^2 = -1` [E], and
`((1 + e_m)/2)^2 = e_m / 2`.

## Units that are zero divisors

[E] `a = e_1 + e_10` and `b = e_4 - e_15` satisfy `a b = 0`, and `a` has the two distinct two-sided inverses
`-(e_1 + e_10)/2` and `-(e_1 + e_10)/2 + b`. For the first, `a^(-1) (a b) = 0` while `(a^(-1) a) b = e_4 - e_15`.
[T] In general, by the corollary of [cd-one-sided-inverses.md](cd-one-sided-inverses.md), the two-sided inverses
of a nonzero `a` form the affine space `conj(a)/N(a) + ker L_a`, a single point exactly when `a` is not a zero divisor. In an associative ring a unit
is never a zero divisor and its inverse is unique, the reason family 196 notes that a nontrivial unit is not a zero
divisor ([P] its p. 2); in the sedenions every nonzero element has a two-sided inverse, and the zero divisors are
exactly the elements whose inverse is not unique.

## Qubit reading

The algebra index bit `b` sits on register qubit `b`, little-endian
([algebra_circuit_rules.md](../algebra_circuit_rules.md)).

- [E] Every normalized two-blade zero divisor `(e_i + t e_j)/sqrt(2)` is an eigenstate of the X string `X^m`,
  `m = i xor j`, with eigenvalue `t`. Since `|m| >= 2` for every `chi = +1` pair (weights 2, 3 and 4 on 72, 72 and
  24 of the 168 at `D = 16`), the state is GHZ-type on the support of `m`, and every qubit there has a zero
  single-qubit Bloch vector: 228 support qubits over the 84 elements at `D = 16`, 1772 over the 588 at `D = 32`. At
  `D = 16`, `m` lies in 9..15, so the doubling qubit 3 is always maximally mixed.
- [T] Both factors of a zero product share `m` (the skeleton), so they are entangled on the same qubits and differ
  only by the offset `i` versus `k` and the eigenvalues `t`, `s`.
- [T] In the untwisted algebra, `g_m` acts on the index register as `X^m`, and the torsion zero divisor
  `(1 - g)(1 + g) = 0` and the idempotents `(1 +- g)/2` are the stabilizer projectors `(1 +- X^m)/2`. The twist
  replaces `X^m` by `L_(e_m) = X^m D_m` with `D_m = diag(sigma(m, x))`. [E] `D_m` is affine over `F_2`, a signed
  Pauli string, for all three rows at `D = 4` and for no row at `D = 8, 16, 32`; the degree of the sign row is
  exactly `k - 1` ([CdSignRowAnf.v](../../../proofs/CdSignRowAnf.v)), which makes sedenion left multiplication
  CCZ-type ([algebra-hardware-probe-principles.md](algebra-hardware-probe-principles.md)).
- [E] For two-unit pure `u` at `D = 16`, `L_u^2 = -|u|^2 I` on all 63 invertible pairs and fails on all 42
  zero-divisor pairs. The test does not mark zero divisors in general: the invertible `e_1 + e_2 + e_12`
  (`det L_u = 81`) has a non-scalar `L_u^2`. The spectrum `{0, 1, 2}` of `M_a = L_(conj a) L_a / |a|^2` on a zero
  divisor is a known theorem ([0905.2987.md](../0905.2987.md)).

## Bloch-named families

- [I] openai/math family 040, Bloch's conjecture for surfaces with `p_g = 0`, concerns Spencer Bloch's prediction on
  Chow groups of zero-cycles; it shares only the name with this repository.
- [I] Family 271 and the finite-range Heisenberg manuscript prove Felix Bloch's `T^(3/2)` magnetization law and its
  first lattice correction. Felix Bloch is also the Bloch of the Bloch sphere, but the magnon physics shares no
  mechanism with the algebra circuits; the qubit content above is this repository's link to the Bloch sphere.

## Boundaries

[I] Every counterexample in families 196 and 197 is probabilistic and unlisted, and none of their proofs was checked
here; family 197's torsion-free theorem and family 285 are unformalized at the pinned commit. The exact checks cover
two-blade elements at `D <= 32`; the written arguments cover every element and dimension.
