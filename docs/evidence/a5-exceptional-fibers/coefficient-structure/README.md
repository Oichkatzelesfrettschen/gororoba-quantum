# Arithmetic structure of the retained fiber-cone numbers

`fiber_coefficients.py` checks three families of identities on numbers the record already holds. It runs no
computer-algebra system and proves no geometric statement; each identity either restates retained results in one
formula or sharpens a hypothesis. Ledger rows A5-595 and A5-596.

## Reduced Hilbert numerators (A5-595)

The first Hilbert numerators of the weight-slice record
([weight-slice-fiber-relations-result.json](../../a5-kernel-attachments/weight-slice-fiber-relations-result.json))
divide exactly by (1 - t)^c with c the codimension (generators minus affine dimension), over Q(i) at both basepoints
and modulo 32009:

| Fiber | Generators, codimension | Reduced numerator | Sum (multiplicity) | h_2 = C(g + 1, 2) - relations |
|---|---|---|---|---|
| Iso | 17, 12 | 1 + 12 t + 10 t^2 | 23 | 153 - 68 = 85 |
| W8 | 24, 18 | 1 + 18 t + 27 t^2 + 4 t^3 | 50 | 300 - 144 = 156 |
| E8-bar -> N+- | 21, 16 | 1 + 16 t - 12 t^2 + 10 t^3 - 5 t^4 + t^5 | 11 | 231 - 148 = 83 |

The nonnegative numerators of Iso and W8 agree with their Cohen-Macaulay rings (A5-566, A5-567); the negative
coefficients of E8-bar agree with a ring that is not Cohen-Macaulay (A5-568).

The E8-bar numerator is the sum of the numerators, over (1 - t)^5, of the pieces that separate ledger rows describe:

    (1 + 7 t + 3 t^2)  +  (1 - t)(1 + 3 t)  -  (1 - t)^2  +  (1 - t)((1 + t) - (1 - t)^4)

- 1 + 7 t + 3 t^2: the prime of dimension 5 and degree 11 (A5-503);
- (1 - t)(1 + 3 t): the prime of dimension 4 and degree 4, the cone over the scroll S(1,1,2) (A5-502);
- (1 - t)^2: their sum, a linear space of dimension 3 (A5-501);
- (1 - t)((1 + t) - (1 - t)^4): the nilradical module R / K, with the Hilbert function of the irrelevant ideal of a
  quadric of affine dimension 4 (A5-454).

The first three terms are the Hilbert series of S / R for R = P1 n P2 by the exact sequence
0 -> S / (P1 n P2) -> S / P1 + S / P2 -> S / (P1 + P2) -> 0, and the fourth is R / K, so the identity is the Hilbert
series of 0 -> R / K -> S / K -> S / R -> 0. It ties five rows computed separately to the one numerator.

## Character split of the last jump (A5-596)

Rows A5-244 and A5-269 record closed forms for the split of the last jump of the truncated-rank ladder by the four
character blocks: (2d + 1)^2 split as block 0, block 1 and two equal blocks on Iso, W8 -> N- and X-, and 2d + 1 split
over blocks 0 and 1 on E8-bar -> VB. Row A5-278 proposes that the final layer has the dimensions of sections of
O(2d) on P^1 and of O(2d, 2d) on P^1 x P^1 "up to a degree-dependent twist" of the characters.

The script shows that both closed forms are the characters of one model with no twist. Let the four characters be
chi_0 (trivial), chi_1, chi_2 and chi_3 = chi_1 chi_2, and

    R1 = k[a, b, c] / (b c),  a of character chi_0, b and c of character chi_1,
    R2 = k[z, x, y] / (x y),  z of character chi_0, x of character chi_2, y of character chi_3,

the coordinate rings of two nodal conics. Then for d = 1 to 12 (enumeration of monomials):

- the degree-d part of R1 has the character of the E8-bar -> VB split of A5-269;
- the tensor product of the degree-d parts of R1 and R2, the degree-d part of the Segre product of the two conics,
  has the character of the split of A5-244.

The nine measured splits that the two rows cite agree with the model (X- at d = 2, 3, 4, 6; Iso at d = 6;
E8-bar -> VB at d = 4, 5, 6, 7). A smooth conic k[u^2, u v, v^2] with u and v of characters chi_0 and chi_1 gives
(d + 1, d, 0, 0) in every degree and misses the measured split at odd d, so the character data single out the nodal
form. The earlier search of A5-271 ranged over tensor products of polynomial rings and found no model.

This is a character identity. Whether the final layer carries the multiplication of these rings is the falsifier of
A5-278 and A5-596 and is not tested here: it needs the final-layer quotient of an existing degree, which the rank
engines do not retain.

## Replay

    "$PYTHON" docs/evidence/a5-exceptional-fibers/coefficient-structure/fiber_coefficients.py OUT.json

The script uses the standard library only and exits 1 when an identity fails. `fiber-coefficients.json` is its
record and `fiber-coefficients.log` its output (Python 3.14.4).
