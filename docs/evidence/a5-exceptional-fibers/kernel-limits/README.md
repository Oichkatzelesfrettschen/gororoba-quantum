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
| arcs sharing a direction (W : R : S), which share the limit y of G | one plane, whatever K, W2, R2, S2 and K2 are |
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

## E8-bar -> N- and E8-bar -> N+ (A5-275)

The same script takes the two certified arc families of [arcs](../arcs/README.md): the first-order family (limit of
G at order 2, dense in the degree-4 component V(P2)) and the order-5 family at the conic point e = -1 (dense in
V(P1)). Their t8 coordinate carries the square root of -1, so the arcs run over F_32009 and F_32029 only. Each of 6
parameter points per family is run 4 times, with further coefficients added one and two orders above every leading
term. [e8-result.json](e8-result.json), truncation order 48:

| quantity | value on all four cases (two incidences, two primes) |
|---|---|
| nullity of L at the base point | 16 |
| pivots along the arc | 24 on all 48 arcs; valuation sums at most 20 |
| limiting plane | dimension 8, inside the kernel of the base point |
| order of G on the arc | 2 on the first-order family, 5 on the order-5 family |
| arcs sharing the projective limit y of G | 12 groups of 4 arcs, one plane per group |
| 12 limits y | 12 distinct planes |
| the header's J on the arc | 0 through order 47 |
| mutated arc (sign s9 of t9 reversed) | 30 or 32 pivots |

On both components of the reduced fiber the limiting kernel is therefore a function of the fiber point on these
samples, including under perturbations that change the arc and keep y. Scope: 6 fiber points per component; no arc
over Q or Q(i), so no statement about real arcs.

## Arcs of E8-bar through a point of VB (A5-016, A5-276)

`vb_limit_span.py` uses the same parametrization Phi of the E8-bar slice at N-. Phi meets the orbit VB on the curve
w = rho = sigma = 0, zeta nonzero (orbit read by `hardware-orbits/hardware_orbits.py`; with rho or sigma nonzero the
point lies in B9), and e drops out of Phi there. An arc with w, rho and sigma of leading orders 1 to 3, zeta = 1 + ...
and e = e0 + ... therefore runs in the closure of E8-bar through one VB point with free coefficients at three
orders, and e0 is a parameter the base point does not see. Each limiting 8-plane is written in a basis of the
12-dimensional kernel of the VB point and sent to its 495 Plucker coordinates.
[vb-limit-span-result.json](vb-limit-span-result.json), 24 arcs for each of 27 leading-order patterns and 6 values
of e0, truncation order 24, the same at both primes:

| quantity | value |
|---|---|
| nullity at the base point, kernel dimension along the arc | 12 and 8 on 156 of 162 patterns |
| the pattern with w, rho and sigma all of leading order 3 | 23 pivots at truncation order 24, no limit taken |
| span of the Plucker vectors of one pattern | 6 on leading orders (1, 1, 1) and (2, 2, 2); 3 on 54 patterns; 1 on 90 |
| cumulative span as e0 runs through 2, -1, 1, 3, 5, 7 | 6, 12, 18, 21, 22, 22 |
| span of all 3,744 limits | 22 |

Reading: a plane of limits has Plucker span 6 = HF(P^2, 2), so on this sample the Plucker vector is quadratic in
the fiber coordinates y. The two components of V(K2) of E8-bar -> VB have HF(2) = 22 (the degree-4 threefold in a
P^6) and 18 (the degree-3 threefold in a P^5), and their union has 34 (A5-020, `k2-hilbert.jsonl`). The sample
saturates at 22: every pattern, at leading orders up to 3 in three parameters, lands in the degree-4 component, and
no arc of this family reaches the degree-3 component. The quadratic reading is an inference from the ranks 6 and
22; the fiber coordinates y of the VB header are not computed at this base point, so the identification of the
rank-22 span with the degree-4 component is not checked against the header's G.

## Iso, both components of W8, and the same-sign X incidences (A5-273, A5-274, A5-292)

`plucker_limits.py` takes four more families. Three have rational coefficients, so they run over F_32009, F_32029
and Q and each plane over Q is a limit that a real arc realizes: the blowup arcs of
[blowup-arcs](../structure/arcs-iso-w8/blowup-arcs/README.md) on Iso -> N- and Iso -> N+ (`iso`, dense in V(K2)) and
on the degree-30 component of W8 -> N- and W8 -> N+ (`w8-c30`), and the weighted arcs of
[arcs-x-same](../arcs-x-same/README.md) on X- -> N- and X+ -> N+ (`x-same`). The linear family of
[arcs-iso-w8](../structure/arcs-iso-w8/README.md) on the degree-20 component of W8 (`w8-c20`) carries the square root
of -1 and runs over the two prime fields. The header of W8 -> N+ is that of W8 -> N- at -t9, and the Iso headers
share J, so one arc formula serves both signs. A variant adds coefficients above the jet that fixes the limit of G.

| quantity | `iso` | `w8-c30` | `w8-c20` | `x-same` |
|---|---|---|---|---|
| record | [iso-result.json](iso-result.json) | [w8-c30-result.json](w8-c30-result.json) | [w8-c20-result.json](w8-c20-result.json) | [x-same-result.json](x-same-result.json) |
| cases (incidences x fields) | 6 | 6 | 4 | 6 |
| parameter points, arcs per case | 9, 36 | 6, 24 | 6, 24 | 9, 36 |
| truncation order | 32 | 32 | 32 | 40 |
| nullity at the base point | 16 | 16 | 16 | 16 |
| pivots along the arc, largest valuation sum | 24, 16 | 24, 16 | 24, 8 | 24, 20 |
| limiting plane | dimension 8, inside the base kernel | the same | the same | the same |
| order of G on the arc (prime fields) | 4 | 4 | 2 | 5 |
| the header's J on the arc (prime fields) | 0 to the truncation order | the same | the same | the same |
| arcs sharing the limit y of G | one plane per group | one plane per group | one plane per group | one plane per group |
| distinct planes | 9 of 9 points | 6 of 6 | 6 of 6 | 9 of 9 |
| each plane over Q reduced modulo both primes | equals the modular plane | equals the modular plane | no rational arc | equals the modular plane |
| columns without a pivot on the mutated arc | 4 | 4 | 0 | 5 |

On every family the kernel limit is therefore 8-dimensional, lies in the kernel of the base point and is a function
of the fiber point on the sample. The mutated arcs (the quadric term reversed on Iso and W8, t9 reversed on X) leave
the slice and keep fewer than 8 columns without a pivot. Scope: 6 or 9 fiber points per family; the degree-20
component of W8 has no rational arc here, so no real arc is exhibited on it; the image of a whole fiber in the
Grassmannian is not computed.

## Arcs through a VB point on which e tends to 0 or infinity (A5-016)

`vb_pole_arcs.py` extends the sample above to arcs with e = E s^k (1 + ...), k = 1 or 2, and w of order above k, on
which Phi stays finite because nu and omega enter only multiplied by m^2 - 1; e -> 1/e reverses omega, so the arcs
with e -> infinity are the same arcs with omega reversed. [vb-pole-arcs-result.json](vb-pole-arcs-result.json), 72
pole patterns of 24 arcs at each prime, truncation order 24: every arc has J = 0 to order 22, base nullity 12 and an
8-dimensional limit, and the Plucker span of the finite-e patterns with leading orders 1 and 2 (rank 22) does not
grow when the pole patterns join it. These arcs also stay in the span of the degree-4 component. The degree-3
component is reached elsewhere: [arcs-vb](../arcs-vb/README.md) finds it over one point of the contracted line of
the VB slice's own parametrization, with the limit of the header's G computed directly, so A5-016 is decided there
and the Plucker-span reading of this section is not needed for it.

## Arcs through the VB point that carries the degree-3 component (A5-295)

`vb_special_arcs.py` samples the point the two sections above leave out. The conic coordinate of the VB slice's
parametrization is k / (1 + k^2) = i omega, so k0 corresponds to e0 = (1 + i k0) / (1 - i k0) up to the sign
convention of the two headers, and the degree-3 component V(P1) needs w of order 2 against order 1 for rho and sigma
([arcs-vb](../arcs-vb/README.md)). The prediction was fixed before the run: if the Plucker vector of the limiting
plane is quadratic in the fiber coordinates, its span has rank HF(k[y]/P2, 2) = 22 over the degree-4 component, 18
over the degree-3 component and 34 over the fiber (A5-020: 22 + 18 - 6, the two components meet in a plane).
[vb-special-arcs-result.json](vb-special-arcs-result.json), truncation order 24, 96 arcs per pattern, five patterns
of leading orders at each of e0(-9), e0(8) and e0(9), both primes:

| patterns | arcs with an 8-dimensional limit in the base kernel | span rank of the group | rank of all vectors so far |
|---|---|---|---|
| finite-e family of `vb_pole_arcs.py` | 288 of 288 | 22 | 22 |
| mirror point e0(-9), five patterns | 480 of 480 | at most 6 per pattern | 22 |
| neighbor e0(8), five patterns | 480 of 480 | at most 6 per pattern | 22 |
| special point e0(9), five patterns | 480 of 480 | 18 | 34 |

The pattern with leading orders (2, 1, 1) at e0(9) alone raises the rank from 22 to 34 and has pivot valuation sum 16
against 12 at the mirror and the neighbor. The three predicted ranks hold at both primes, so the limits along the
special family lie outside the span of every other sampled family, and the whole sample spans exactly what a
quadratic dependence on the fiber point allows. The special point is e0(9) in this header and k0 = -9 in the VB
slice's header: the mirror is the control that fixes the sign. Scope: the arcs of one pattern have coefficients on
a line (`vb_limit_span.coefficient` is affine in the arc index), which bounds a single pattern's span from below
only; the record computes no fiber coordinate y, so it does not show that the plane is a function of y.

## Replay

From the repository root (Singular 4.4.1, python-flint 0.9.0, sympy 1.14.0; the retained records ran under Python
3.13 on the 32-thread workstation laptop, about five minutes per family):

    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py x
    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py e8
    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py iso
    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py w8-c30
    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py w8-c20
    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py x-same
    (cd docs/evidence/a5-exceptional-fibers/kernel-limits && "$PYTHON" vb_limit_span.py)
    (cd docs/evidence/a5-exceptional-fibers/kernel-limits && "$PYTHON" vb_pole_arcs.py)
    (cd docs/evidence/a5-exceptional-fibers/kernel-limits && "$PYTHON" vb_special_arcs.py)
