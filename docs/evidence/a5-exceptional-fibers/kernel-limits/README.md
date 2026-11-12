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
component of W8 has no rational arc here, so no real arc is exhibited on it; the section on the fiber-to-Grassmannian
map below fits the image of each fiber on several hundred arcs.

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
parametrization is k / (1 + k^2) = i omega with omega = (e^2 - 1) / (4 e); with e = (1 + i kappa) / (1 - i kappa),
i omega = -kappa / (1 + kappa^2), so k = -kappa and the VB point k0 = -9 is e0 = (1 + 9i) / (1 - 9i), and the degree-3 component V(P1) needs w of order 2 against order 1 for rho and sigma
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

## The map from a fiber to the Grassmannian is quadratic on five families (A5-296)

`fiber_plucker_map.py` samples arcs with distinct leading parameters on one family, takes from `plucker_limits.py`
the fiber point y (the normalized leading vector of G) and the Plucker vector Pl of the limiting 8-plane of each arc,
and tests whether Pl is a vector of forms of one degree delta in y: scalars c_s and one matrix T with
c_s Pl_s = v_delta(y_s) T, v_delta the monomials of degree delta. With N the left kernel of the sample matrix of
v_delta, the scalars solve N diag(Pl[:, j]) c = 0 over every Plucker coordinate j. The arc parameters come from a
SHA-256 of the arc index, which avoids the line that parameters affine in the index lie on; the ranks of v_1, v_2
and v_3 on the sample are the evidence of genericity. Each run fits 320 arcs per case, tests 40 further arcs against
the fitted T, and repeats the scalar system with each Plucker vector paired to the next arc's fiber point (the
mutation arm, which a real fit must fail). The record keeps a SHA-256 of the normalized T, the count of distinct
fiber points and a verdict, and the script exits nonzero without a validated quadratic fit. Prediction stated before
the run: delta = 2, since the Plucker ranks of the earlier sections equal the Hilbert function of the fiber in
degree 2. Each family runs on its N- header and, with `--plus`, on its N+ header (X+ -> N- and X- -> N+, X- -> N-
and X+ -> N+, Iso, W8 and E8-bar -> N- and N+), at F_32009 and F_32029: 20 records.

| family (records on the N- and N+ headers) | linear span of y | rank of v_2(y) = Plucker rank = rank of T | least delta | solution space | held-out arcs proportional | mutation arm |
|---|---|---|---|---|---|---|
| opposite-sign X ([32009](fiber-plucker-map-x-p32009.json), [32029](fiber-plucker-map-x-p32029.json); N+: [32009](fiber-plucker-map-x-plus-p32009.json), [32029](fiber-plucker-map-x-plus-p32029.json)) | 3 | 6 | 2 | 1 | 40 of 40 | no solution |
| same-sign X ([32009](fiber-plucker-map-x-same-p32009.json), [32029](fiber-plucker-map-x-same-p32029.json); N+: [32009](fiber-plucker-map-x-same-plus-p32009.json), [32029](fiber-plucker-map-x-same-plus-p32029.json)) | 12 | 45 | 2 | 1 | 40 of 40 | no solution |
| Iso ([32009](fiber-plucker-map-iso-p32009.json), [32029](fiber-plucker-map-iso-p32029.json); N+: [32009](fiber-plucker-map-iso-plus-p32009.json), [32029](fiber-plucker-map-iso-plus-p32029.json)) | 17 | 85 | 2 | 1 | 40 of 40 | no solution |
| W8, degree-30 component ([32009](fiber-plucker-map-w8-p32009.json), [32029](fiber-plucker-map-w8-p32029.json); N+: [32009](fiber-plucker-map-w8-plus-p32009.json), [32029](fiber-plucker-map-w8-plus-p32029.json)) | 20 | 120 | 2 | 1 | 40 of 40 | no solution |
| W8, degree-20 component (same records) | 15 | 84 | 2 | 1 | 40 of 40 | no solution |
| W8, both components (same records) | 24 | 156 | 2 | 1 | 80 of 80 | no solution |
| E8-bar, arcs of kind `p2` ([32009](fiber-plucker-map-e8-p32009.json), [32029](fiber-plucker-map-e8-p32029.json); N+: [32009](fiber-plucker-map-e8-plus-p32009.json), [32029](fiber-plucker-map-e8-plus-p32029.json)) | 7 | 22 | 2 | 1 | 40 of 40 | no solution |
| E8-bar, arcs of kind `p1` (same records) | 12 | 53 | 2 | 1 | 40 of 40 | no solution |
| E8-bar, both kinds (same records) | 16 | 69 | 2 | 1 | 80 of 80 | no solution |

All 20 records carry the verdict `degree_2_fit_validated`, and each row reads the same on both headers and both
primes. No linear fit exists (delta = 1 has no solution), the quadratic fit is unique up to one scalar, every c_s is
nonzero and T is injective on the degree-2 piece of the sampled fiber ring, so on each sampled family the kernel
plane is the image of the fiber point under the second Veronese map followed by a linear injection into Plucker
space. On W8 and on E8-bar one matrix T serves both kinds of arc. Scope: a fit on samples with held-out validation at
two primes. The Iso sample spans all 17 coordinates and its 85 equals the degree-2 Hilbert function of the fiber. The
same-sign X arcs span 12 of the 15 coordinates and 45 of the 51 quadrics of k[y]/K2, the Hilbert function of the
reduced fiber, whose prime contains y1, y5 and y6 ([arcs-x-same](../arcs-x-same/README.md), A5-297), so that row
covers the whole reduced fiber. The E8-bar arcs span 16 of the 21 coordinates and 69 of the 83 quadrics of the fiber
of E8-bar -> N+- (A5-026); 16 and 69 are the Hilbert function of its reduced fiber in degrees 1 and 2
([e8-radical](../structure/e8-radical/README.md)), so that row covers the whole reduced fiber as well. Runs took
1 to 27 minutes each on the 32-thread laptop with a peak of 1.6 GB.

### Certification boundary of the quadratic fits

The retained records certify sampled interpolation, not a morphism on a fiber scheme and not an attaching map. In
particular, each record retains only `t_sha256`; it does not retain the coefficients of `T`, the pivot-monomial basis
used for its rows, or a characteristic-zero lift. The following obligations are therefore the admission boundary for
using these fits in the attachment program. A later certificate must keep its field, header slug, input digests and
the following coordinate orders with the coefficient matrix itself:

- fiber coordinates in the order of the selected header's `G` list;
- quadratic monomials in the lexicographic order emitted by
  `combinations_with_replacement(range(len(G)), 2)`, together with the selected pivot columns;
- the boundary-kernel basis as the reduced row-echelon basis returned by `base_kernel`;
- Plucker coordinates as `vb_limit_span.plucker` emits them: the maximal minors of the annihilator of the plane in
  the coordinates of that basis, over the column subsets of size (basis length minus plane dimension) in the
  lexicographic order of `itertools.combinations`.

| Obligation | What the retained records establish | Certificate still required |
|---|---|---|
| Coefficient matrix and conventions | A normalized SHA-256 of the fitted modular matrix and its rank | Every normalized coefficient of `T`, the four coordinate orders above, the header and input digests |
| Construction from the kernel map | Exact arcwise limits are computed from `L_x(s)` | Derive the coordinate functions from the Pfaffian/kernel construction, independently of interpolation |
| Coordinate-ring identity | The equation holds on 320 fitted and 40 held-out arcs per arc family (640 and 80 in a pooled case) | Reduce every kernel and Plucker equation modulo the full defining ideal of each intended fiber component, with exact remainders or cofactor witnesses |
| Projective base locus | The fitted image is nonzero at every sampled point and `T` has the sampled degree-two rank | Determine the common-zero locus of all projective coordinate forms on the full fiber support |
| Component intersections | One fitted matrix serves both sampled W8 families and both sampled E8-bar families | Verify that the componentwise morphisms agree scheme-theoretically on their complete intersections |
| Characteristic zero | Some source arc families and their planes lift from `Q` to both retained primes | Construct the map over `Q(i)` and prove that both modular matrices are its compatible reductions |
| Physical-limit transfer | Rational arcs exhibit physical limits at their sampled points | Prove the general projection lemma, identify the source stratum and graph closure, and apply real curve selection so every admitted holomorphic limit is a physical limit |
| Coverage | The samples cover the stated arc families; same-sign X covers its known reduced support in degree two | Determine every limiting plane over every boundary modulus, including the unsampled E8-bar coordinates and all blocked Rees fibers |
| Boundary-orbit variation and equivariance | Each fit sits at one boundary point of its header | Compute the limit set at moved points over every compact boundary modulus and classify it under the stabilizer `K_p` of the boundary point (requirement A3 and deliverable 1 of the [attachment program](../../../design/a5-kernel-attachments-program.md)) |
| Attaching maps | No retained fit supplies link or sphere-bundle data | Construct the link-to-limit-set map and the union of partner spheres inside the boundary sphere |
| Specialization compatibility | No retained fit compares a composite specialization with a direct one | Compare every 8-to-12-to-16 composite with the corresponding direct 8-to-16 specialization in the same coordinates |

The first bounded next step is retention, not another interpolation run: revise the producer so a replay writes the
candidate coefficients and coordinate metadata above. The identity check then works component by component over a
split prime before any `Q(i)` lift. A failed identity, a projective basepoint or disagreement on a component
intersection rejects the candidate matrix even when all held-out arcs remain proportional. The run times and peak
memory quoted above (1 to 27 minutes and 1.6 GB on the 32-thread laptop) are reported in this README and held by no
record, and they apply only to interpolation; there is no measured runtime or memory bound for the all-point
coordinate-ring checks.

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
    (cd docs/evidence/a5-exceptional-fibers/kernel-limits && "$PYTHON" fiber_plucker_map.py iso --prime 32009 \
        --fit 320 --held-out 40 --out fiber-plucker-map-iso-p32009.json)

## Retaining a fitted coordinate map

The default record of `fiber_plucker_map.py` holds ranks, validation counts and the digest `t_sha256`, which do
not determine the fitted map. `--retain-map` adds `cases[...].map` to the record of one family:

    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py iso --fit 240 --held-out 40 \
        --retain-map --out fiber-plucker-map-iso-p32009-with-map.json

`map` holds the prime, the degree delta, the selected monomial indices of degree delta (in the order of
`itertools.combinations_with_replacement`), the Plucker coordinate count and the fitted matrix, scaled so that its
first nonzero entry in row-major order is 1, the normalization `t_sha256` hashes. The matrices are large, so the
retained records carry the digest alone. The map is a fit over one finite field: symbolic Plucker identities, a
base-locus analysis and agreement with the kernel-limit construction are the checks that would certify it.
