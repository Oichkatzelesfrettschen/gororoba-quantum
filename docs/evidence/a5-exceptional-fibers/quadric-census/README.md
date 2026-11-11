# Saturation and reducedness of the quadric ideals K2

Each script reads the retained quadrics K2 of one fiber at p = 32009 and asks a question about the projective
scheme V_+(K2), which contains the exceptional fiber E0 = V_+(L) and equals it where L = K2 is proved. A statement
about the affine cone k[y]/K2 passes to V_+(K2) only through the saturation K2 : m^∞, so each fiber gets that
check first. The same-sign X incidences are in [arcs-x-same](../arcs-x-same/README.md) (A5-303).

| Fiber | K2 | dimension, multiplicity | K2 : m = K2 | reducedness of V_+(K2) |
|---|---|---|---|---|
| E8-bar → VB | 21 quadrics in 10 variables | 4, 7 | yes | reduced: K2 equals the intersection of its two minimal primes (degrees 3 and 4); Cohen-Macaulay with a linear resolution (Betti numbers 21, 70, 105, 84, 35, 6) |
| Iso | 68 quadrics in 17 variables | 5, 23 | yes | not computed here |
| E8-bar → N− | 148 quadrics in 21 variables | 5, 11 | yes | not computed here |
| W8 → N− | 144 quadrics in 24 variables | 6, 50 | yes | not computed here |

"Saturated" means the irrelevant ideal is not an associated prime, so k[y]/K2 has no nilpotent or zero divisor
supported at the vertex alone, and nonreducedness of the cone, where it occurs, is nonreducedness of V_+(K2).
The minimal primes of the Iso, E8-bar → N− and W8 → N− ideals are a longer computation and are not in this
directory.

    Singular -q --no-warn < docs/evidence/a5-exceptional-fibers/quadric-census/vb-radical.sing

## Binomial form and linear symmetries (A5-310)

`quadric_structure.py` asks two questions of each K2 at p = 32009 (2 s for all five; record
`quadric-structure-p32009.jsonl`).

Is K2 spanned by monomials and binomials in the header's coordinates y? The reduced row echelon basis of K2 on the
quadratic monomials answers it for these coordinates only. Which linear changes of coordinates could make it so?
A monomial-binomial presentation of a d-dimensional toric variety has a diagonal torus of rank at least d among
its linear symmetries, so the script computes the Lie algebra g of matrices whose derivation preserves K2, its
diagonal part, and the centralizer of one fixed element of g; that centralizer contains a Cartan subalgebra, so its
dimension bounds the rank of every torus of linear symmetries from above.

| Fiber | dim of the cone | supports 1, 2, 3, more | dim g | diagonal torus | torus rank at most |
|---|---|---|---|---|---|
| X− → N− | 4 | 27, 5, 3, 34 | 23 | 1 | 5 |
| E8-bar → VB | 4 | 0, 6, 9, 6 | 15 | 3 | 5 |
| Iso | 5 | 0, 1, 3, 64 | 17 | 1 | 4 |
| E8-bar → N− | 5 | 25, 20, 16, 87 | 34 | 2 | 6 |
| W8 → N− | 6 | 3, 12, 16, 113 | 26 | 2 | 5 |

Readings. No K2 is monomial-binomial in the coordinates y; for X− → N− that is a matter of coordinates, since the
certificate of [monomial-ladder](../monomial-ladder/README.md) presents it by monomials and binomials in the
basis of M / q M. For Iso (4 < 5) and W8 → N− (5 < 6) the bound excludes a torus of full rank among the linear
symmetries of K2, so neither K2 is the ideal of a toric variety in any linear coordinates; a torus of rank 4 on Iso
or 5 on W8 would still make them varieties with a torus action of complexity one, which is untested. For
E8-bar → VB and E8-bar → N− the bound leaves a full-rank torus possible and decides nothing. Trinomial rows
(support 3) occur in every K2 and carry no known structure here. hypothesis: the symmetry algebras come from the
stabilizer of the base point in the automorphism group of the algebra; no record tests that.

