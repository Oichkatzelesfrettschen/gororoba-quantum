# Arc certificates for the exceptional fibers of E8-bar -> N- and E8-bar -> N+

Two families of exact formal arcs through the origin of the slice V(J) reach both components of V(K2) for the
fibers E8-bar -> N- and E8-bar -> N+ at p = 32009 and p = 32029, and every limit vector satisfies K2. This package
holds one implementation of the certificate, parameterized by target, and the records of its replay at the four
targets. Every statement holds over the fields F_32009 and F_32029 and says nothing about characteristic 0. The
[evidence README](../README.md) places the package among the other records, and the
[findings note](../../../notes/topics/a5-exceptional-fiber-findings.md) states the hypotheses these records test.

## Claim

Notation. The slice V(J) of the closure of a nullity-8 orbit is cut out by 16 polynomials J in t1..t9 and carries 21
functions G (the header `ideal G`), whose ideal I defines the blow-up center. The fiber cone is
F(I) = k[y]/L = sum over d of I^d / m I^d, with y1..y21 standing for G1..G21 and m the maximal ideal of the origin;
h_d is its Hilbert function. K2 is the ideal of the 148 quadrics that the degree-2 relation computation produces,
and k is the algebraic closure of F_p.

At each of the four targets:

- **Decomposition.** sqrt(K2) = P1 intersect P2 for two minimal primes over F_p: P1 of projective dimension 4, degree
  11 and 34 minimal generators, and P2, the rational normal scroll S(1,1,2), of projective dimension 3, degree 4 and
  20 minimal generators.
- **Dense arc families.** The limit vectors F(u) of a first-order family (order 2 of G(x(s))) are dense in V(P2), and
  those of an order-5 family near the conic point e = -1 are dense in V(P1).
- **Lower bound.** A relation f in L of degree d satisfies f(G) in m I^d, which forces f(F) = 0 at every limit vector
  F of an arc through the origin. Density in both components therefore gives L inside P1 intersect P2 = sqrt(K2), a
  graded surjection F(I) -> k[y]/sqrt(K2), and h_d >= HF(k[y]/sqrt(K2), d). At d = 5 the bound reads h_5 >= 861 for
  E8-bar -> N- and E8-bar -> N+ at both primes. The inclusion L inside sqrt(K2) uses the arcs alone.
- **Reduced fiber.** With the opposite inclusion K2 inside L, the reduced exceptional fiber over the base point is
  Proj(k[y]/sqrt(K2)), the union of the projective varieties of P1 and P2. The degree-2 membership receipts of the
  working record carry K2 inside L: `witnesses.jsonl` holds a `k2-span` row for E8-bar -> N- at both primes and for
  E8-bar -> N+ at 32029, and a `sign-isomorphism` row (flip t8, t9; mutual K2 remainders 0, 0) that transports the
  E8-bar -> N- receipt to E8-bar -> N+ at 32009, where no receipt of its own exists.

| d | HF(k[y]/sqrt(K2), d) | HF(k[y]/K2, d) | certified or bounded h_d |
|---:|---:|---:|---|
| 1 | 16 | 21 | h_1 = 21 (`degree-one/`) |
| 2 | 69 | 83 | h_2 = 83 |
| 3 | 195 | 225 | h_3 = 225 |
| 4 | 440 | 495 | h_4 = 495 |
| 5 | 861 | 952 | h_5 = 952: N- by r_18 = 952 (`../n18-laptop/`, A5-183, A5-220), N+ by the t8/t9 sign isomorphism (A5-082, A5-088) |
| 6 | 1526 | 1666 | N-: h_6 = 1666 by the jet functionals of [../arc-jets/](../arc-jets/README.md) (A5-335); N+ not run |

The columns come from `k2_primes.log` of each target (`kbase` of the standard bases of K2 and of P1 intersect P2,
equal at all four targets) and `k2-hilbert.jsonl`, which `run_target.py` compares with the K2 column. The upper
bound 952 holds where K2 lies in L (the reduced-fiber statement above). The truncated rank r_N at N = 15 and N = 16 is 742 with blocks 168,
148, 213, 213 ([n16-laptop](../n16-laptop/)); the arc bound exceeds it by 119, so the plateau of r_N across
N = 15 and 16 does not mark h_5.

## Method

**Parametrization of V(J).** Phi maps the parameters (m, rho, sigma, e, zeta) rationally onto V(J), with w = m - 1:

    t4 = (m rho + sigma)/2,  t5 = (m rho - sigma)/2,  t6 = (m sigma + rho)/2,  t7 = (rho - m sigma)/2,
    t9 = -s9 (m-1)^2/(2m),  t3 = zeta,
    nu = (e+1)^2/(4e),  omega = (e^2-1)/(4e),
    t8 = -i (m^2-1) omega / m,  t2 = (2 (m^2-1) nu + (m^2-1) zeta)/(m^2+1),
    t1 = ((1-m^2) t2 + (m^2+1) t3 + (m-1)^2)/(2m),

with i the square root of -1 modulo p (10754 at 32009, 9115 at 32029) and s9 = +1 on the E8-bar -> N- slice and
s9 = -1 on E8-bar -> N+. The target record `arc_targets.py` fixes prime, root, s9, header and K2 file.
`verify_phi.log` shows all 16 generators of J vanishing on Phi identically in F_p(m, rho, sigma, e, zeta), and the
corrupted maps t9 + 1 and -t9 leaving a residue in 12 of 16 generators. `phi_rank.json` gives rank 5 for the
9 x 5 Jacobian of Phi at (w, rho, sigma, e, zeta) = (2, 5, 7, 3, 11) by exact dual-number arithmetic, and
`j_decomp.log` shows one minimal prime of J of dimension 5 and degree 12 inside the maximal ideal of the origin. Phi is
therefore dominant onto V(J), and its polynomial arcs lie on V(J) exactly.

**Limit vectors.** For an arc x(s) with x(0) = 0 the first nonzero coefficient vector F of (G_1(x(s)), ..., G_21(x(s)))
at order nu is the limit. Every t_i has valuation at least 1, so the jet of G_j of degree n fixes the coefficients
through s^n exactly. `gen_family.py` writes one Singular script per family, computes F symbolically in the five
parameters u in a global monomial ordering (`dp`), and counts the generators of P2, P1 and K2 that do not vanish on F
identically. The two certified families are

    P2:  x(s) = Phi(w = W s, rho = R s, sigma = S s, e = E, zeta = Z s),                       nu = 2
    P1:  x(s) = Phi(w = W s^2, rho = (R+S)s/2, sigma = (R-S)s/2, e = -1 + E1 s^2, zeta = Z s),  nu = 5

and their symbolic limits are the logs under `families/`. The conic point e = -1 is where nu and omega both vanish; the
families with generic e or e near 1 land in V(P2) only (see the scans below).

**Component P2.** The 14 linear forms of P2 leave the P^6 on y3, y10, y11, y16, y18, y20, y21 and six quadrics. The
parametrization y3 = s^2, y20 = s t, y21 = -i t^2, y11 = l t, y18 = l s, y10 = i mu t, y16 = mu s, y17 = -i y18,
y15 = i y16, y5 = -y16, y1 = -i y20 (all other y_j = 0) has an image ideal equal to P2 (`scroll_check.log`, affine cone
dimension 4, degree 4), so V(P2) is the cone over the smooth scroll S(1,1,2) and is geometrically irreducible.
The first-order family has Jacobian rank 4 at five parameter points (`numeric_P2.json`). A rank at a point is at most
the generic rank, which is at most the dimension of the image closure, so the image has dimension at least 4, the
affine dimension of V(P2); the image lies in the irreducible V(P2), hence is dense.

**Component P1.** The order-5 family has Jacobian rank 5 at five parameter points (`numeric_P1.json`), so the image
has dimension at least 5 = the affine dimension of V(P1). The image is the closure of a map from A^5 defined over F_p,
hence an F_p-defined irreducible subvariety Y of V(P1) of full dimension. P1 is prime over F_p, so Galois acts
transitively on the geometric components of V(P1); Y is a Galois-stable component and therefore equals V(P1). No
explicit parametrization of V(P1) exists in the package; the density of this family rests on the rank and the Galois
argument.

**Independent numeric replay.** `certify.py` rebuilds each arc with exact truncated Laurent series over F_p
(`laurent.py`, python-flint), a code path separate from Singular, on the 270 grid points W in {1,3,7}, R in {2,5,13},
S in {1,6,19}, Z in {4,11}, E (E1 for P1) in {2,3,5,10,23}. Each point checks that the arc is regular with x(0) = 0,
that G(x(s)) has order nu, that the numeric limit equals the symbolic vector, that it satisfies every generator of the
target prime and of K2 and violates some generator of the other prime. The first six arcs also check all 16 generators
of J. No point fails (`numeric_P2.json`, `numeric_P1.json`).

**Controls.** `mutation_controls.json` corrupts the order-5 arc three ways: t9 + s^3 leaves a residue in 12 of 16
generators of J; adding 1 to the lowest-degree coefficient of G_11 moves nu to 4 and the limit out of V(P1); replacing
e = -1 by e = 2 gives nu = 3 and a limit in V(P2) outside V(P1). At E8-bar -> N+ targets, `cross_control.json` tests
the 270 limits of both families against the E8-bar -> N- ideals at the same prime: the order-5 limits satisfy none of
P1, P2, K2 of E8-bar -> N-, and the first-order limits satisfy the E8-bar -> N- P2 and K2 (the two P2 are the same
ideal, `compare_nm.log`) but not P1. The membership test separates the two slices.

**Twist correspondence.** The symbolic limit vectors of the two families of E8-bar -> N+ equal those of E8-bar -> N-
at the same prime, coordinate by coordinate, up to a sign and a substitution of the parameters, so the arcs of the two
targets correspond one to one (`twist_compare.json`, `twist_compare.log` of `e8np-p32009` and `e8np-p32029`, identical
at both primes; A5-326). In the first-order family (limits E^2 F, polynomials in W, R, S, Z, E) 11 coordinates are
nonzero, the same 11 on both targets, and N+_j(E) = eps_j E^(d_j) N-_j(1/E) holds on all 11 with d_j = 4 and
eps_j = -1 for j = 1, 5, 15, 16, 17, 18, 20 and +1 for j = 3, 10, 11, 21 (no failing coordinate). In the order-5
family (W, R, S, Z, E1) 16 coordinates are nonzero on both targets, and N+_j = eps_j N-_j holds on all 16 under a
common sign change of (W, R, S, Z, E1); eight of the 32 sign vectors qualify, all with E1 -> -E1. The generator
comparison `j_twist.log` applies t9 -> -t9 alone to the slice: 7 of the 16 generators of J of N+ equal the image of
the N- generator and 9 equal its negative, and none of the 21 generators of G equals its image or the negative of it,
so t9 -> -t9 alone is not the isomorphism; the pair flip t8 -> -t8, t9 -> -t9 is (A5-049). The check is confirmatory:
the sign isomorphism of [structure](../structure/README.md) (`doubling_automorphism.py`, A5-049) transports one target
onto the other. The input logs are byte-identical to `families/` of the four targets; the producers
`../working/arcs-p2/e8np-p32009/twist_compare.py` (`twist_compare.py NM_DIR OUT.json` from the N+ target directory)
and `check_j_twist.py` beside it are retained as run, byte-identical for the two primes. They import the earlier `symfam.py` and `arclib.py` of the
campaign, whose interfaces the consolidated modules of this directory replaced (`load_fj(logtext)` against
`load_fj(logtext, p)`), and a per-target `config.py`; with those modules and the `families/` logs as `fam/`, both
producers reproduced the retained files byte for byte. The [retention audit](../../../archive/reviews/untracked-records-audit-2026-11-11/README.md)
lists the twist records as result-missing (section 3A, item 6).

## Records per target

| Target | Fiber | Prime, root of -1 | s9 | Header | K2 relation file |
|---|---|---|---:|---|---|
| `e8nm-p32009` | E8-bar -> N- | 32009, 10754 | +1 | `build/inputs/p32009-r10754/e8-nm.sing` | `distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel` |
| `e8nm-p32029` | E8-bar -> N- | 32029, 9115 | +1 | `build/inputs/p32029-r9115/e8-nm.sing` | `distribute/out/a5-e8-d2/e8nm_p2/d2/relations-upto-d2.rel` |
| `e8np-p32009` | E8-bar -> N+ | 32009, 10754 | -1 | `build/inputs/p32009-r10754/e8-np.sing` | `runs/e8_a2/e8_k2.rel` |
| `e8np-p32029` | E8-bar -> N+ | 32029, 9115 | -1 | `build/inputs/p32029-r9115/e8-np.sing` | `distribute/out/a5-e8-d2/e8np_p2/d2/relations-upto-d2.rel` |

Paths sit under `working/` of the evidence directory and are read in place. `arc_targets.k2_ideal` raises unless the
sha256 of the relation file equals `relations_sha256` of the matching `k2-hilbert.jsonl` row, and
`arc_targets.check_generator_order` raises unless the generator list of the relation run (`gens.txt`, or the
`input.sing` of `runs/e8_a2`) equals the header's G list element by element, which fixes y_j = G_j.

Each target directory holds:

| File | Content |
|---|---|
| `P1.txt`, `P2.txt` | minimal generators of the two primes, identified by (projective dimension, degree) = (4, 11) and (3, 4) |
| `k2_primes.sing`, `k2_primes.log` | radical and minimal primes of K2, `radical == P1 cap P2`, Hilbert functions of k[y]/K2 and k[y]/sqrt(K2) for d = 1 to 6 |
| `scroll_check.sing`, `scroll_check.log` | image ideal of the scroll parametrization equals P2 |
| `verify_phi.sing`, `verify_phi.log`; `phi_rank.json`; `j_decomp.sing`, `j_decomp.log` | J(Phi) = 0, rank of dPhi, minimal primes of J |
| `families/` | Singular script and log of the two certified families |
| `numeric_P2.json`, `numeric_P1.json` | the independent numeric certificates |
| `mutation_controls.json` | the three corruptions |
| `survey.json`, `line_check.json` | the 540 arcs at other base points and the line check |
| `compare_nm.sing`, `compare_nm.log`, `cross_control.json`, `twist_compare.json`, `twist_compare.log`, `j_twist.log` | E8-bar -> N+ targets only |
| `result.json`, `result_P1.json` | the certificate of P2 and of P1 |
| `campaign_summary.json` | every count, including the scan tallies |

Per-family scripts and logs of the scans (4,656 files and 46 MB per target) stay in the scratch directory of the
replay; `campaign_summary.json` keeps their tallies.

## Counts at every target

The four targets give the same counts:

- `verify_phi.log`: 16 of 16 generators of J vanish on Phi; `phi_rank.json`: rank 5; `j_decomp.log`: one minimal prime
  of J, dimension 5, degree 12.
- `k2_primes.log`: K2 has 172 standard-basis elements, dimension 5 (projective dimension 4) and degree 11; sqrt(K2) has
  dimension 5 and degree 11 and equals P1 intersect P2; P1 has projective dimension 4, degree 11, 9 linear generators
  and 34 minimal generators; P2 has projective dimension 3, degree 4, 14 linear generators
  and 20 minimal generators.
- P2 family, order nu = 2, 11 nonzero coordinates (y1, y3, y5, y10, y11, y15, y16, y17, y18, y20, y21): symbolic
  vanishing leaves 0 of 20 generators of P2, 24 of 34 generators of P1 and 0 of 148 generators of K2 nonvanishing;
  Jacobian rank 4 at five points; 270 of 270 grid points regular, 0 failures.
- P1 family, order nu = 5, 16 nonzero coordinates (y1, y2, y3, y5, y8, y9, y10, y11, y13, y15, y16, y17, y18, y19,
  y20, y21): 0 of 34 generators of P1, 15 of 20 generators of P2 and 0 of 148 generators of K2 nonvanishing; Jacobian
  rank 5 at five points; 270 of 270 grid points regular, 0 failures.
- The coordinates y2, y8, y9, y13 and y19 of the order-5 limit vanish on V(P2), so that family leaves V(P2).

Input and output digests (sha256; the output digests are truncated to 16 hexadecimal digits):

| Target | Header | K2 relation file | `P1.txt`, `P2.txt` |
|---|---|---|---|
| `e8nm-p32009` | `7d3521d0e8026e6ff9b17f1a3af618adcd133ff2835ff68f9d445c3db42414de` | `e047f996ad609a40ca9d65a64cb7f28755cbaeea3013a9ada7ff71e76e708de6` | `abca3c9b91b2c9f3`, `31f15063fc456844` |
| `e8nm-p32029` | `48bdcbe0fa17d04cd4899c0a1e056706b9c9c368ccece97ebeb94686ad3c1cca` | `bfd7470cfa57467ea510e8b89a34bcefed60ebb86dbf423c22cef945d2ed831b` | `3c9cc98dbc10e88a`, `d5b6545db4bff6dd` |
| `e8np-p32009` | `ab6dd0ef6281b0d02e84d744ace39f56a8cf95695186324e4d76fb387c628af6` | `bbe9bb734af739d735ca4ca4938b85fce9ed87c07b7373ec5353c47335be0652` | `224b96f2999ea775`, `31f15063fc456844` |
| `e8np-p32029` | `966c836537e2ef8e313cbbb6ae2b9a3ea7ee54de7b106aa3f53c83d555d13cae` | `3c2294f7dee43a1471cec20a7af5c259741b50a02216bbe92074d127dc34694a` | `9219c1dc655f8f05`, `d5b6545db4bff6dd` |

## Scans of monomial families

`scan_families.py` enumerates 1,296 monomial families at the origin (valuations a for w, b and c for the two
rho/sigma coordinates, d for zeta, three conic types) and raises the jet order from 3 to 7 until nu appears. The
tallies are equal at all four targets.

| Scan | Families | Classes |
|---|---:|---|
| e = E0 s^k, rho = R s^b, sigma = S s^c | 324 | 324 in V(P2) only |
| e = E0 s^k, rho, sigma = (R s^b +- S s^c)/2 | 324 | 324 in V(P2) only |
| e = 1 + E1 s^j | 324 | 324 in V(P2) only |
| e = -1 + E1 s^j | 324 | 193 in V(P1) only, 116 in V(P1) and V(P2), 15 without nu <= 7 |

1,281 families are classified and none lies outside V(K2). The Jacobian rank at the test point (3, 5, 7, 11, 2) is at
most 4 for the families in V(P2) only, at most 3 for those in both components, and at most 5 for those in V(P1)
only; the one family of rank 5 is the certified order-5 family, and 15 further families in V(P1) only have rank 4
at that point. The 15 families without nu <= 7 (valuation 3 of w, e = -1) stay unclassified. Generic e and e near 1 reach V(P2) only, so V(P1) needs the conic point.

## Arcs at other base points

`survey.py` classifies 540 arcs with monomial parameters (two coefficient sets) by base point x(0):

| Base point x(0) | Arcs | Limit in V(P2) | Limit outside V(K2) |
|---|---:|---:|---:|
| origin | 64 | 64 | 0 |
| line t1 = t3, other t_i = 0, off the origin | 32 | 32 | 0 |
| t1 = t3, t4 = t6, t5 = t7, t2 = t8 = t9 = 0, (t4, t5) not (0, 0); 12 distinct points | 120 | 0 | 120 |
| base point off V(G): G(x(0)) nonzero, the arc is not exceptional | 216 | | |
| pole in the parameters, excluded | 108 | | |

The 120 limits outside V(K2) start at other points of V(J + G) and concern the fibers over those points, not the
fiber over the origin that K2 describes: K2 holds the degree-2 relations modulo m I^d for the maximal ideal m of the
origin, and a fiber over another point x0 satisfies its relations modulo m_x0 I^d. The decomposition, lower-bound and
reduced-fiber statements concern the origin only, and the 120 limits contradict none of them.

`line_check.json` evaluates J and G at (c, 0, c, 0, ..., 0) for eight values of c (1, 2, 3, 5, 7, 11, 100, -4) and
finds no nonvanishing generator; the control point (3, 0, 2, 0, ...) off the line fails 2 of 16 J generators and 4 of
21 G generators. The eight values prove no polynomial identity. The decomposition of V(J + G) is not part of the
package.

## Replay

    sh docs/evidence/a5-exceptional-fibers/arcs/replay.sh [TARGET...]

The command replays all four targets in order (`e8nm-p32009`, `e8nm-p32029`, `e8np-p32009`, `e8np-p32029`; each
E8-bar -> N+ target compares against the E8-bar -> N- target of its prime) and rewrites every record of this
directory. A replay followed by `git diff --exit-code` over the directory is the determinism check: no timing,
absolute path or random draw enters a retained file, and the scripts take no seed. `replay.sh` runs under
`ulimit -v 8388608` with `GOROROBA_WORKERS` (default 3) Singular processes at once through `parallel.py`, and puts the
scan scratch in `$ARCS_WORK` (default `$TMPDIR/a5-arcs-work`). Singular runs from the repository root with stdin
closed and a 900 s timeout per script.

Measured wall time of the command over all four targets on the build host (12 CPUs, three scan workers, beside the
Singular jobs of other sessions): 8 min 4 s (`time`: real 8m3.753s, user 19m39s), 106 to 136 s per target by the driver
log; a first replay of the same tree took 8 min 33 s. The second replay left `git diff` over this directory empty.

Tools: Singular 4.4.1, python-flint 0.9.0 and Python 3.14.7; `replay.sh` runs `$PYTHON` (default `python3`), which needs python-flint.

Modules: `arc_targets.py` (targets, input digests), `arclib.py` and `laurent.py` (exact series and Phi),
`symfam.py` (symbolic vectors), `gen_family.py`, `scan_families.py`, `certify.py`, `survey.py`, `line_check.py`,
`mutation_controls.py`, `phi_rank.py`, `cross_check.py`, `singular_scripts.py`, `collate.py`, and `run_target.py`
(the driver). The bounded test
[test_a5_arc_certificates.py](../../../../tests/test_a5_arc_certificates.py) runs the P2 certificate on three grid
points, three mutations that must fail, and the retained records.

## Limits

- Everything holds over F_32009 and F_32029. A characteristic-0 statement needs a specialization argument across
  primes that the package does not make.
- The two certified families are dense in the two components by rank and irreducibility. The 15 unclassified
  near-e = -1 families and arcs with several terms per parameter are unexplored and not needed.
- K2 inside L rests on the degree-2 receipts and the sign-isomorphism row cited under the reduced-fiber statement, not on this package.
- The arc bound (861) is superseded at degree 5: r_18 = 952 on N- at both primes (`../n18-laptop/`) reaches the K2
  count, and the sign isomorphism carries it to N+.
- The fibers over the other points of V(J + G) are untested beyond the 120 survey arcs.
