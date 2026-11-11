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
