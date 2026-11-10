# Exact limits of ker L_a along the arcs of the fiber track

The fiber cone F(I) records limits of the Pfaffian kernel coordinates G. This directory computes the limit of the
kernel of left multiplication itself, from the 32 x 32 matrix L_a of `gororoba_quantum/cd_core.py`, along exact arcs
(ledger rows A5-272 to A5-276, one row per arc family).

## Opposite-sign X incidences (A5-272)

`plucker_limits.py` takes the arcs x(s) = Phi(w, rho, sig, s1) of [arcs-x](../arcs-x/README.md) with
w = W s + W2 s^2, rho = R s + R2 s^2, sig = S s + S2 s^2, s1 = K s + K2 s^2, completes them by the producer's
eliminated slice variables (t3 = -t1 t9 + t9^2 + t1 - 3 t9 and t8 = 0, read from `elimpart` at each field), maps the
slice point to the operand through z_k = i^popcount(k) split_k, z_k = x_k + i x_(16+k), and eliminates L_x(s) over
k[[s]] with pivots of least valuation. The columns left without a pivot are a saturated kernel basis, and their
constant terms span the limiting plane.

[x-opposite-result.json](x-opposite-result.json) holds 36 arcs (9 directions (W, R, S), 4 choices of the remaining
coefficients) and 9 mutated arcs per incidence and field, for X+ -> N- and X- -> N+ over F_32009, F_32029 and Q:

| quantity | value on all six cases |
|---|---|
| nullity of L at the base point | 16 |
| pivots along the arc | 24, valuations summing to 8, so the kernel has dimension 8 |
| limiting plane | dimension 8, inside the 16-dimensional kernel of the base point |
| arcs sharing a direction (W : R : S) | one plane, whatever K, W2, R2, S2 and K2 are |
| 9 directions | 9 distinct planes |
| the header's J on the arc (both primes) | 0 through order 11 |
| each plane over Q reduced modulo 32009 and 32029 | equals the plane computed modulo that prime |
| mutated arc (sign of t9 reversed, the other incidence's sheet) | more than 24 pivots: the arc leaves the nullity-8 locus |

The direction (W : R : S) is the point of the fiber P^2 (the limit of G is (a1 W^2, a2 W (R + S), a3 W (R - S)),
[arcs-x](../arcs-x/README.md)), so on these samples the limiting kernel is a function of the fiber point and the
map from the sampled fiber points to the Grassmannian of 8-planes in the base kernel is injective. An arc with
rational coefficients is a real arc, so each of the 9 planes over Q is a limit that a real arc realizes.

Scope: the statement is a sample of 9 fiber points, all with W nonzero; it does not describe the line W = 0 of the
fiber, the same-sign X incidences (which have no arc certificate, A5-022) or the image of the whole fiber in the
Grassmannian. The mutated arc ends with 7 columns without a pivot at truncation order 12, which shows that its
kernel is smaller than 8 and does not measure its nullity.

Replay from the repository root (Singular 4.4.1, python-flint 0.9.0, sympy 1.14.0, Python 3.14.7; about four
minutes on 12 threads):

    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py
