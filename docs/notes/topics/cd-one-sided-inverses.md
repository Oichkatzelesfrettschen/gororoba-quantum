# One-sided inverses in Cayley-Dickson algebras

Every real Cayley-Dickson algebra A_n, in the `cd_core` convention, has
ker L_a = ker R_a for every element a, where L_a x = a x and R_a x = x a.
Hence a b = 1 forces b a = 1, and the right inverses of a zero divisor a form
the affine space conj(a)/<a, a> + ker L_a, every point of which is a
two-sided inverse. The sedenion e_1 + e_10 therefore has a four-parameter
family of two-sided inverses, and a two-blade zero divisor of dimension 32 a
family of dimension 4, 8 or 12. The mechanism is the purity of annihilators:
nonassociativity never breaks it, so the finite-dimensional nonassociative
analog of Kaplansky's direct-finiteness question (a b = 1 implies b a = 1 in
a group algebra K[G]) is a theorem here rather than a conjecture.
[scripts/cd_one_sided_inverses.py](../../../scripts/cd_one_sided_inverses.py)
checks the kernel equality and the inverse law exactly on every element of
three families at dimensions 16 and 32; the retained record and its gate are
described in the [evidence README](../../evidence/cd-one-sided-inverses/README.md).
Tags: [E] exact finite computation; [T] written proof argument, not
machine-checked; [I] interpretation.

## Conventions

- A_n is the Cayley-Dickson algebra of dimension D = 2^n with the doubling
  (a, b)(c, d) = (a c - conj(d) b, d a + b conj(c)) and
  conj(a, b) = (conj(a), -b) of
  [algebra_circuit_rules.md](../algebra_circuit_rules.md), so basis units
  multiply as e_i e_j = sigma(i, j) e_(i XOR j) with sigma = `cd_core.cd_sign`.
- The trace form is <x, y> = sum_i x_i y_i, and N(x) = <x, x>. An element
  is pure when its coordinate on e_0 is zero; x = Re(x) + Im(x) splits every
  element into its real part and its pure part.
- ker L_a is the left annihilator {z : a z = 0} and ker R_a the right
  annihilator {z : z a = 0}.

## Results

| Statement | Status |
| --- | --- |
| conj is an involutive anti-automorphism, conj(x y) = conj(y) conj(x), and an isometry of the trace form | [T] Lemma 1 |
| L1: x conj(x) = conj(x) x = N(x) 1 | [T] Lemma 2; [E] basis pairs through D = 128 |
| L2: <x y, z> = <y, conj(x) z> and <x y, z> = <x, z conj(y)> | [T] Lemma 3; [E] basis triples through D = 128 |
| An element with a nonzero annihilator is pure, and every annihilated element is pure | [T] Lemma 4 |
| ker L_a = ker R_a for every a in every A_n | [T] Theorem; [E] every signed two-blade (210 at D = 16, 930 at D = 32), every three-unit sum with indices below 16 (455 each), and the doubly pure grids (3626 at D = 16, 450 at D = 32) |
| a b = 1 implies b a = 1, and {b : a b = 1} = conj(a)/N(a) + ker L_a | [T] Corollary; [E] a b = b a = 1 for every kernel basis vector of every zero divisor above |
| Annihilator dimensions: 4 for all 84 sedenion two-blade zero divisors and all 1848 doubly pure grid zero divisors at D = 16; 4, 8, 12 in the counts 168, 168, 252 at D = 32 | [E] the record; the 32-dimensional split agrees with [two_blade_blocks.json](../../evidence/box_kite_census/two_blade_blocks.json) |

## Proofs

Write x = (a, b) for an element of A_(n+1) with a, b in A_n. The trace form
of A_(n+1) is <(a, b), (c, d)> = <a, c> + <b, d>, and N(a, b) = N(a) + N(b).
Each lemma holds at n = 0, where A_0 = R with conj the identity, and the
induction step assumes the lemma at level n.

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
and 0 = <a z, z> = r N(z) forces r = 0. Now a is pure, and with
z = s + q, s real and q pure, a z = s a + a q = 0. Lemma 3 and Lemma 2 give
<a q, a> = <q, conj(a) a> = N(a) <q, 1> = 0, so <s a, a> = s N(a) = 0 and
s = 0. The right-sided case follows by applying conj (Lemma 1) to z a = 0.

**Theorem.** ker L_a = ker R_a for every a in A_n. If a is real the two
kernels are zero. Otherwise take z with a z = 0. Lemma 4 makes a and z pure,
so conj(a) = -a and conj(z) = -z, and Lemma 1 gives
0 = conj(a z) = conj(z) conj(a) = z a. Hence ker L_a is contained in
ker R_a, and the mirror argument gives the reverse inclusion.

**Corollary.** If a b = 1 then b a = 1, and the solutions of a b = 1 are
exactly conj(a)/N(a) + ker L_a. Lemma 2 gives a b' = 1 for
b' = conj(a)/N(a), so a (b - b') = 0, b - b' lies in ker L_a = ker R_a, and
b a = b' a + (b - b') a = 1. Conversely every b in b' + ker L_a satisfies
a b = 1.

[I] Associativity is never used: the proof needs the trace-form identities
of Lemmas 1 to 3, which the doubling preserves at every level, and the
dimension count that an associative argument would use is replaced by the
purity of annihilators. In an associative finite-dimensional algebra the
inverse is unique; here a zero divisor's inverses form an affine space of
the annihilator's dimension, which is the content the record checks when it
multiplies conj(a)/N(a) + z against a from both sides for every kernel basis
vector z.

## Relation to direct finiteness

Kaplansky's direct-finiteness question asks whether a b = 1 implies b a = 1
in every group algebra K[G]; the openai/math manuscript collection
(https://github.com/openai/math, commit 7ef5c0cc, families 196 and 197)
claims counterexamples in untwisted group algebras of torsion-free groups.
The Cayley-Dickson algebras are twisted group algebras R^sigma[Z_2^n] of the
torsion group Z_2^n with the cocycle sigma = `cd_sign`
([Albuquerque-Majid convention](../../evidence/albuquerque-majid-convention/README.md)).
The untwisted R[Z_2^n] has the zero divisors (1 - g)(1 + g) at every n;
the cocycle removes all of them for n <= 3 and leaves, from n = 4 on, the
zero divisors the sedenion census describes. The theorem above says the
twisted algebras keep direct finiteness at every n even where they lose the
absence of zero divisors, so the two properties separate along this axis.

## Not established

- No Rocq source proves the kernel equality; the all-dimension statement
  rests on the written induction above. A formal statement would take
  Lemmas 1 to 3 against the tower product of
  [CdTowerBasisSign.v](../../../proofs/CdTowerBasisSign.v).
- The record enumerates fixed families; the general element of dimension
  32 or higher is covered by the written argument alone.
- The falsifier is one element a with ker L_a different from ker R_a, or one
  pair with a b = 1 and b a different from 1, in any dimension; the script
  raises on the first such element at `--write` time.
