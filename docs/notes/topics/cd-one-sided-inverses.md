# One-sided inverses in Cayley-Dickson algebras

Every real Cayley-Dickson algebra A_n, in the `cd_core` convention, has
ker L_a = ker R_a for every element a, where L_a x = a x and R_a x = x a.
Hence a b = 1 forces b a = 1, and the right inverses of a zero divisor a form
the affine space conj(a)/<a, a> + ker L_a, every point of which satisfies
a b = b a = 1. The sedenion e_1 + e_10 has a four-parameter family of such
inverses, and a two-blade zero divisor of dimension 32 a family of dimension
4, 8 or 12. The kernel equality is Corollary 9.3 of Biss, Dugger and Isaksen
([math-0511691.md](../math-0511691.md), proved there through Lemma 9.2 and
the identity x (conj(x) y) = conj(x) (x y)), and the purity of zero divisors
is their Lemmas 9.4 and 9.5 and Moreno's Lemma 4.1
([math-0512517.md](../math-0512517.md)). This note gives a self-contained
proof through the trace-form adjoint identities (Lemma 3 is their Lemma 3.4),
states the direct-finiteness corollary with the affine inverse family, which
neither source states, and binds the statements to an exact replay:
[scripts/cd_one_sided_inverses.py](../../../scripts/cd_one_sided_inverses.py)
checks the identities on every basis tuple through dimension 128 and the
kernel equality with the inverse law on every element of fixed families at
dimensions 16 and 32; the retained record and its gate are described in the
[evidence README](../../evidence/cd-one-sided-inverses/README.md).
Tags: [P] source statement; [E] exact finite computation; [T] written proof
argument, not machine-checked; [R] Rocq-checked theorem; [I] interpretation.

## Conventions

- A_n is the Cayley-Dickson algebra of dimension D = 2^n with the doubling
  (a, b)(c, d) = (a c - conj(d) b, d a + b conj(c)) and
  conj(a, b) = (conj(a), -b) of
  [algebra_circuit_rules.md](../algebra_circuit_rules.md), so basis units
  multiply as e_i e_j = sigma(i, j) e_(i XOR j) with sigma = `cd_core.cd_sign`.
- The trace form is <x, y> = sum_i x_i y_i, and N(x) = <x, x>, which is
  positive for every nonzero x. An element is pure when its coordinate on e_0
  is zero; x = Re(x) + Im(x) splits every element into its real part and its
  pure part.
- ker L_a is the left annihilator {z : a z = 0} and ker R_a the right
  annihilator {z : z a = 0}; both are A_n when a = 0.
- "Inverse" below means an element b with a b = b a = 1. Such a b does not
  invert the map L_a when a is a zero divisor: b (a x) differs from x for x
  in ker L_a.

## Results

| Statement | Status |
| --- | --- |
| conj is an involutive anti-automorphism, conj(x y) = conj(y) conj(x), and an isometry of the trace form | [T] Lemma 1; [R] `conj_conj`, `conj_mul`, `dot_conj` of [CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v) for every level; [E] basis form through D = 128 |
| L1: x conj(x) = conj(x) x = N(x) 1 | [T] Lemma 2; [R] `norm_mul` of [CdAnnihilatorSymmetry.v](../../../proofs/CdAnnihilatorSymmetry.v) for every element of the integer tower at every level, and of [CdAnnihilatorSymmetryReal.v](../../../proofs/CdAnnihilatorSymmetryReal.v) on the real tower of [CdTowerReal.v](../../../proofs/CdTowerReal.v); [E] polarized basis form through D = 128; [R] basis form `sigma_diagonal`, `sigma_anticommute` of [CdTowerBasisSign.v](../../../proofs/CdTowerBasisSign.v) |
| L2: <x y, z> = <y, conj(x) z> and <x y, z> = <x, z conj(y)> | [T] Lemma 3; [P] Lemma 3.4 of math/0511691; [R] `adjoint` of CdAnnihilatorSymmetry.v and of CdAnnihilatorSymmetryReal.v for every element at every level; [E] basis triples through D = 128; [R] basis forms `sigma_left_involution`, `sigma_right_involution` of CdTowerBasisSign.v |
| An element with a nonzero annihilator is pure, and every annihilated element is pure | [T] Lemma 4; [R] `purity_left`, `purity_right` of CdAnnihilatorSymmetry.v, through <a z, z> = N(z) re(a) and <a z, a> = N(a) re(z) (`dot_mul_self_r`, `dot_mul_self_l`), and `purity_left`, `purity_right` of CdAnnihilatorSymmetryReal.v on the real tower through (a + conj(a)) z = 2 re(a) z; [P] Lemmas 9.4, 9.5 of math/0511691 and Lemma 4.1 of math/0512517 |
| ker L_a = ker R_a for every a in every A_n | [T] Theorem; [R] `kernel_equality` of CdAnnihilatorSymmetry.v on the integer tower at every level ([evidence bundle](../../evidence/cd-annihilator-symmetry/README.md)) and of CdAnnihilatorSymmetryReal.v on the real tower, by Lemma 9.2 of math/0511691 ([real evidence bundle](../../evidence/cd-annihilator-symmetry-real/README.md)); [P] Corollary 9.3 of math/0511691; [E] every signed two-blade (210 at D = 16, 930 at D = 32), every three-unit sum (455 at D = 16) and the doubly pure grid (1764 at D = 16) |
| a b = 1 implies b a = 1, and {b : a b = 1} = conj(a)/N(a) + ker L_a | [T] Corollary; [R] `direct_finiteness` and, as N(a) b - conj(a) in ker L_a, `right_inverse_affine` of CdAnnihilatorSymmetry.v; `direct_finiteness` and `right_inverse_form` (b = conj(a)/N(a) + w with a w = 0) of CdAnnihilatorSymmetryReal.v; [E] a b = b a = 1 for every kernel basis vector of every zero divisor above (8904 offsets) |
| Annihilator dimensions: 4 for all 84 sedenion two-blade zero divisors and all 882 doubly pure grid zero divisors; 4, 8, 12 in the counts 168, 168, 252 at D = 32 | [E] the record; the D = 32 split agrees with the two-blade histogram of [annihilator_strata.json](../../../results/hw_estimate/annihilator_strata.json) |

## Proofs

Write x = (a, b) for an element of A_(n+1) with a, b in A_n. The trace form
of A_(n+1) is <(a, b), (c, d)> = <a, c> + <b, d>, and N(a, b) = N(a) + N(b).
Each lemma holds at n = 0, where A_0 = R with conj the identity, and the
induction step assumes the lemma at level n. No step uses associativity,
alternativity or multiplicativity of the norm, which fail from n = 4 on;
every product below is a binary product in its written parentheses.

**Lemma 1 (conjugation).** conj is an involution, an isometry, and
conj(x y) = conj(y) conj(x). The involution and isometry statements read off
the definition. For the anti-automorphism law at level n + 1,
conj((a, b)(c, d)) = (conj(a c - conj(d) b), -(d a + b conj(c))) and
conj(c, d) conj(a, b) = (conj(c), -d)(conj(a), -b)
= (conj(c) conj(a) - conj(b) d, -b conj(c) - d a). The first coordinates
agree because conj(a c) = conj(c) conj(a) and conj(conj(d) b) = conj(b) d at
level n; the second coordinates are equal as written.

**Lemma 2 (norm).** x conj(x) = conj(x) x = N(x) 1. With x = (a, b),
(a, b)(conj(a), -b) = (a conj(a) + conj(b) b, -b a + b a) = (N(a) + N(b), 0)
and (conj(a), -b)(a, b) = (conj(a) a + conj(b) b, b conj(a) - b conj(a))
= (N(a) + N(b), 0), using a conj(a) = conj(a) a = N(a) and conj(b) b = N(b)
at level n.

**Lemma 3 (adjoints).** <x y, z> = <y, conj(x) z> and
<x y, z> = <x, z conj(y)>. The second follows from the first through
Lemma 1: <x y, z> = <conj(y) conj(x), conj(z)> = <conj(x), y conj(z)>
= <x, conj(y conj(z))> = <x, z conj(y)>. For the first at level n + 1, with
x = (a, b), y = (c, d), z = (e, f):

    <x y, z> = <a c - conj(d) b, e> + <d a + b conj(c), f>,
    <y, conj(x) z> = <(c, d), (conj(a) e + conj(f) b, f conj(a) - b conj(e))>
                   = <c, conj(a) e> + <c, conj(f) b> + <d, f conj(a)> - <d, b conj(e)>.

Term by term at level n: <a c, e> = <c, conj(a) e> by the first form;
<d a, f> = <d, f conj(a)> by the second form;
<b conj(c), f> = <b, f c> by the second form and <f c, b> = <c, conj(f) b>
by the first; and <conj(d) b, e> = <b, d e> by the first form with
x = conj(d), while <d e, b> = <d, b conj(e)> by the second form. The four
terms match, with the minus sign of conj(d) b in the first display meeting
the minus sign of b conj(e) in the second.

**Lemma 4 (purity).** If a z = 0 with a, z nonzero then Re(a) = 0 and
Re(z) = 0; the same holds for z a = 0. Write a = r + p with r real and p
pure. Lemma 3 gives <p z, z> = <z, conj(p) z> = -<p z, z>, so <p z, z> = 0,
and 0 = <a z, z> = r N(z) forces r = 0 since N(z) > 0. Now a is pure, and
with z = s + q, s real and q pure, a z = s a + a q = 0. Lemma 3 and Lemma 2
give <a q, a> = <q, conj(a) a> = N(a) <q, 1> = 0, so <s a, a> = s N(a) = 0
and s = 0 since N(a) > 0. The right-sided case follows by applying conj
(Lemma 1) to z a = 0.

**Theorem.** ker L_a = ker R_a for every a in A_n. If a = 0 both kernels are
A_n. If a is a nonzero real scalar both kernels are zero. Otherwise let z lie
in ker L_a; the case z = 0 is immediate, and for z != 0 Lemma 4 makes a and
z pure, so conj(a) = -a and conj(z) = -z, and Lemma 1 gives
0 = conj(a z) = conj(z) conj(a) = z a. Hence ker L_a is contained in
ker R_a, and the mirror argument, with the same split at z = 0, gives the
reverse inclusion.

**Corollary.** If a b = 1 then b a = 1, and the solutions of a b = 1 are
exactly conj(a)/N(a) + ker L_a. Since a b = 1, a is nonzero and N(a) > 0, so
b' = conj(a)/N(a) is defined and Lemma 2 gives a b' = 1. Then a (b - b') = 0,
b - b' lies in ker L_a = ker R_a, and b a = b' a + (b - b') a = 1.
Conversely every b in b' + ker L_a satisfies a b = 1.

[I] In an associative finite-dimensional algebra a zero divisor has no
inverse and an invertible element has exactly one; here every nonzero a has
the inverse conj(a)/N(a), and the zero divisors are exactly the elements
whose inverse is not unique, their inverses forming an affine space of the
annihilator's dimension. The record checks that content when it multiplies
conj(a)/N(a) + z against a from both sides for every kernel basis vector z.

## Relation to direct finiteness

[I] Kaplansky's direct-finiteness question asks whether a b = 1 implies
b a = 1 in every group algebra K[G]; Kaplansky proved it for fields of
characteristic zero, and the openai/math manuscript collection
(https://github.com/openai/math, commit 7ef5c0cc, family 197) claims a
counterexample over a field of characteristic two with a torsion-free group,
beside family 196's claimed zero divisors in a torsion-free group algebra.
The Cayley-Dickson algebras are twisted group algebras R^sigma[Z_2^n] of the
torsion group Z_2^n, n >= 1, with the 2-cochain sigma = `cd_sign`, whose
coboundary is the associator
([Albuquerque-Majid convention](../../evidence/albuquerque-majid-convention/README.md)).
The untwisted R[Z_2^n] is associative and finite-dimensional, so it is
directly finite while carrying the zero divisors (1 - g)(1 + g) for every
g != 0. The twist removes every zero divisor for n <= 3 and, from n = 4 on,
leaves the zero divisors the sedenion census describes; what it adds at
every n is nonassociativity, and the theorem above says direct finiteness
survives that addition, by a mechanism (purity of annihilators) that
associativity never enters.

## Not established

- Two Rocq sources cover the statements, and each rests on a different
  route. [CdAnnihilatorSymmetry.v](../../../proofs/CdAnnihilatorSymmetry.v)
  proves Lemmas 2 to 4, the theorem and the corollary for every element with
  integer coordinates at every level by the argument above, closed under the
  global context
  ([evidence bundle](../../evidence/cd-annihilator-symmetry/README.md)), on
  the tower of
  [CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v),
  which proves Lemma 1 (`conj_mul`, `conj_conj`, `dot_conj`); scaling by a
  common denominator carries its statements to every rational element.
  [CdAnnihilatorSymmetryReal.v](../../../proofs/CdAnnihilatorSymmetryReal.v)
  proves Lemmas 1 to 4, the theorem and the corollary with the affine family
  for every element with real coordinates at every level, the statement this
  note makes, on the real tower of
  [CdTowerReal.v](../../../proofs/CdTowerReal.v), by Lemma 9.2 of
  [math-0511691.md](../math-0511691.md): x y = 0, conj(x) y = 0 and
  x conj(y) = 0 are equivalent because N(conj(x) y) = <y, x (conj(x) y)> and
  x (conj(x) y) = conj(x) (x y), which is bilinearity once
  conj(x) = 2 re(x) - x. Its proof terms depend on the two Stdlib
  real-construction axioms and nothing else
  ([real evidence bundle](../../evidence/cd-annihilator-symmetry-real/README.md)).
  The real tower is Stdlib's R; a tower over an abstract ordered field, which
  would cover both sources at once, has no Rocq source.
- The record enumerates fixed families; the general element of dimension
  32 or higher is covered by the written argument alone.
- The falsifier is one element a with ker L_a different from ker R_a, or one
  pair with a b = 1 and b a different from 1, in any dimension; the script
  raises on the first such element at `--write` time.
