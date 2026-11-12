# Structure of the kernel-map base loci, the sign symmetry, and the same-sign / opposite-sign difference

Three exact checks explain the fibers recorded in [arcs-x/](../arcs-x/README.md), the
[kernel-attachments record](../../a5-kernel-attachments/README.md) and the
[findings note](../../../notes/topics/a5-exceptional-fiber-findings.md). Each script runs from the repository root
with `"$PYTHON"`, uses Singular in global orderings, and writes its scripts and logs beside itself.

## The doubling automorphism carries every Y -> N+ fiber onto a Y' -> N- fiber

`doubling_automorphism.py` checks with `cd_core.cd_multiply_exact` that phi(a, b) = (a, -b) is an algebra
automorphism of A_3, A_4 and A_5 on every basis pair (0 failures of 64, 256 and 1024; `logs/doubling_automorphism.txt`).
On a doubly pure y it conjugates the original coordinates z_k = y_k + i y_(16+k), so in split coordinates it negates
the slots of odd popcount, z'_1, z'_2, z'_4, z'_7, z'_8, z'_11, z'_13, z'_14. `doubling_split_action.py` applies it to
every orbit representative of the [regularity record](../../a5-strata-regularity/README.md): it exchanges X+ and X-,
V^a_+ and V^a_-, N+ and N-, maps W8, E8-bar, Iso, B9, V and VB into themselves, and preserves every nullity
(`logs/doubling_split_action.txt`).

Since L_phi(y) = phi L_y phi^-1, the kernel map commutes with phi, so phi carries the closed Gauss graph of Y and its
fiber over p onto those of phi(Y) over phi(p). G_2 x C^* acts by automorphisms and scalings and is transitive on the
6-dimensional null cone N+- minus 0, so the fiber does not depend on the base point within the orbit. Consequence, in
every characteristic: X+ -> N+ and X- -> N-, X+ -> N- and X- -> N+, and Y -> N+ and Y -> N- for Y in {W8, E8-bar,
Iso, B9, V, VB} have isomorphic fibers. The sign witnesses of [witnesses.jsonl](../witnesses.jsonl) are instances.

## Same-sign versus opposite-sign: which sheet of E8-bar is smooth

`asymmetry.py` (`logs/asymmetry.txt`, `logs/asymmetry.json`, over Q, the regularity record's `germ_job`):

| Ideal | at N- | at N+ |
|---|---|---|
| E8-bar and mu' = 0 | germ (4, 3, 7), sheets (4, 2, 7) and (4, 1, 4), meeting in dimension 3 | same |
| mu' = 0, eta(d) = 0 (the X+ conditions) | smooth (7, 1, 7) | quadric cone of rank 7, (7, 2, 8) |
| mu' = 0, eta(s) = 0 (the X- conditions) | quadric cone of rank 7 | smooth |

On N- the vector d = u' - v' = 2u' is nonzero, so eta(d) has nonzero differential and X+ is the smooth sheet of
E8-bar cut by mu' = 0; on N+ d vanishes and eta(d) lies in the square of the ideal, so X+ is the multiplicity-2 sheet.
The multiplicities add up, 1 + 2 = 3 = mult(E8-bar) along N+- (germ (5, 3, 8)), and the two sheets meet in the
3-dimensional B9 slice. The opposite-sign fibers (P^2) come from the smooth sheet and the same-sign fibers (proper
subvarieties of P^14) from the singular one. The vanishing of eta on the targets does not distinguish them, since
eta(s) = eta(d) = 0 on both N+ and N-.

## The base locus is the B9 slice; the residual is the VB curve or the origin

`base_locus.py FIELD INCIDENCE...` builds the producer's coordinate slice (nine variables, no elimination), the
Schur-coordinate ideal F (whose zero set is the nullity >= 12 locus of the source germ), and the pullbacks of the B9 and
VB closure equations. FIELD p32009 and p32029 use the split primes and roots of -1 of the fiber inputs, and q uses
Q(i). Summaries are in `logs/summary_p32009.txt`, `logs/summary_p32029.txt` and `logs/summary_q.txt`, with one
script and log per row in `sing/` and `logs/`. The three fields agree on every row:

| Incidence | germ dim | base locus V(J + F) near 0 | residual (J + F) : P_B9 |
|---|---|---|---|
| X+ -> N-, X- -> N+ | 4 | one prime, dimension 3, equal to the B9 slice | one prime, dimension 1, equal to the VB slice |
| X+ -> VB, X- -> VB | 3 | one prime, dimension 2, equal to the B9 slice | the origin (m-primary) |
| W8 -> VB | 5 | one prime, dimension 2, equal to the B9 slice | the origin |
| Iso -> VB | 4 | one prime, dimension 2, equal to the B9 slice | the origin |
| B9 -> N-, B9 -> N+ | 3 | the origin (F is m-primary) | not applicable |

Reading: on X+ -> N- the ideal is I = t2 * I' with V(t2) the B9 slice and V(I') the VB curve, so F(I) = F(I') and the
fiber is the exceptional P^2 of the blow-up along a smooth curve germ of codimension 3. On X -> VB the B9 slice is
again a divisor and the residual is m-primary with s = 3 = germ dimension, which forces the full P^2. On B9 -> N+- the
ideal is m-primary with s = 3 = germ dimension, which forces P^2. On W8 -> VB and Iso -> VB the B9 slice has
codimension 3 and 2, the colon is not a factorization, and the full P^4 and P^3 rest on the recorded certificates.

The general criterion is analytic spread (Northcott and Rees 1954, doi 10.1017/s0305004100029194): F(I) is a quotient
of k[y_1..y_s], its Krull dimension l(I) is at most the germ dimension, and F(I) = k[y] exactly when l(I) = s. Every
incidence with s above the germ dimension (V -> N+-, E8-bar -> Va+-, same-sign X, E8-bar -> N+-, E8-bar -> VB,
Iso -> N+-, W8 -> N+-) therefore has a proper fiber, as recorded; smoothness of the source germ is neither needed nor
sufficient.

## Prime decompositions of the quadric schemes, and the components of the E8-bar base locus

[iso-k2/chart-colon/](iso-k2/chart-colon/README.md) proves the Iso -> N- kernel K2 radical at p = 32009 and p = 32029:
K2 : y_i = K2 for every coordinate and a reduced chart y_i = 1 embed k[y]/K2 in a Laurent ring over a reduced ring.
[iso-k2/sections/](iso-k2/sections/README.md) proves it prime and geometrically prime at both primes from QRNG linear
sections cut to 23 points: Cohen-Macaulay by an Artinian reduction of length 23 = degree, one Frobenius orbit of size
23 in a section, and an orbit size prime to 23. [w8-kp/](w8-kp/README.md) proves the W8 -> N- residual K2 : P
geometrically prime of degree 30 at p = 32009 and p = 32029 by the same point sections (orbit partitions 3 + 3 + 24 and 8 + 22 share
no proper subset sum; size-1 orbits exclude conjugate components), so V(K2) = V(P) cup V(K2 : P) with degrees 20 and
30. [e8-base-components/](e8-base-components/provenance.txt) (`e8_base2.py`) pulls the nullity-12 closures back
through E8-bar -> N- at both primes: B9 (dimension 3, degree 1), V (2, 4), VB (1, 1), Va- (1, 1), Va+ absent, F in
each, with V(VB) inside V(B9) and V(V) and V(Va-) inside V(V), so the germ of the base locus at 0 has the two
components B9 and V. Each section or pullback runs in seconds; the whole-ideal radical and `minAssChar` runs they
replace stalled past 40,000 s.

[arcs-iso-w8/](arcs-iso-w8/README.md) certifies by an explicit arc family, symbolically at both primes, that V(P)
lies in the fiber over the origin of W8 -> N-, so the analytic spread of I is 6 and F(I) = k[y]/K2 for W8 hinges on
the multiplicity (50 or 20); it records the arc families searched for the Iso V(K2) and the W8 V(K2 : P) without
reaching them, the base locus L0 that explains the ranks, and the one-chart test that decides the Iso case.

[c30-bounded/](c30-bounded/README.md) decides the W8 multiplicity: at five QRNG points of P(L0), the projectivized
base locus of the point blowup, the fiber cone of the pullback ideal is a linear 3-space in V(K2 : P) outside V(P), the
planes sweep a 5-dimensional set (Jacobian rank 6 with dual numbers), so V(K2 : P) lies in the fiber over the origin
and F(I) = k[y]/K2 for W8 at both primes, with controls and a measured cost of about 50 s per point against the stalled global
slice.

## Sign symmetry of the fiber headers: Smith invariants, signed-permutation sweep, the pair flip

[sign-symmetry/](sign-symmetry/) retains the records behind A5-032 and A5-049 for the three producer specializations
(p, i) = (32009, 10754), (32009, 21255) and (32029, 9115); the [retention audit](../../../archive/reviews/untracked-records-audit-2026-11-11/README.md) lists them as a
provenance gap (section 3B). The exact proof of the pair flip is
`doubling_automorphism.py` above; these records are the computations that found and bounded it.

| File | Content |
|---|---|
| `smith_torus.jsonl` (`smith_torus.py HEADER...`) | the 27 headers (nine at each specialization): the exponent-difference lattice of every displayed J and G polynomial has full rank (6, 7, 8 or 9, the number of variables) and invariant factors 1, ..., 1, 2, 2, so the diagonal torus fixing every polynomial up to a character has order 4 at every header |
| `sweep_p32009.jsonl` (`signed_perm_sweep.py`) | 6,225 lines at p = 32009: 25 per-pair summaries (ordered pairs of headers with the same variable count) and 6,200 signed permutations t_i -> s_i t_pi(i) with span(J_a o sigma) = span(J_b); 68 of them map the G span onto itself, exactly 4 for each of 17 ordered pairs (36 within a header, 32 between the N+ and N- headers of one pair) |
| `sign_search.log` (`sign_search.py HEADER+ HEADER-`) | E8-bar -> N+ against E8-bar -> N- at (32009, 10754): all 2^9 diagonal sign vectors; 8 map J up to sign, and of those the 4 with t9 -> -t9 and t8 fixed leave the combined G span at rank 41 (all 21 generators of G- outside the moved G+), the 4 with t8 -> -t8 and t9 -> -t9 keep it at 21 (none outside); the logs at the other two specializations are identical |
| `npm_map.jsonl`, `map_p32009-r10754.json`, `map_p32009-r21255.json`, `map_p32029-r9115.json` (`npm_map.py`, `k2_transport.py`) | the pair flip t8 -> -t8, t9 -> -t9 as an integer identity on the 16 J and 21 G generators at each specialization (a sign for every index), and the transport of the 148 N- quadrics onto the N+ span (ranks 148, 148, union 148 at 32009 and 32029) |

The sweep prunes permutations by a per-variable profile of J, so an empty result for a multi-generator J is not a
proof of absence and a valid map with J_b = 2 J_a is pruned; it certifies the maps it found. The `tc_*` tangent-cone
probes of the same run carried Singular errors and were withdrawn; they are not retained.

`npm_map.py` wrote the first three lines of `npm_map.jsonl` and `k2_transport.py` the last two. The `map` field of
those two lines names the `map_*.json` file tracked beside the record, and every other field equals the line the run
wrote while reading an untracked copy of the same map (`k2_transport.py` on the retained relation files and the tracked
map reproduces both lines). The `header` fields of `smith_torus.jsonl` hold the run path of the headers, written
`~/Projects/gororoba-workspace/gororoba-quantum/docs/evidence/a5-exceptional-fibers/working/build/inputs/...` by the
scrub of `retain_working.sh`.

Replay from the tracked headers under `../working/build/inputs/`, with `GOROROBA_WORKERS=2`. `smith_torus.py`,
`sign_search.py` and `signed_perm_sweep.py` map their independent items (headers, sign vectors, permutations of one
header pair) through `ordered_map` of `gororoba_quantum/parallel.py` in input order, so each output equals the serial
program's. `smith_torus.py` run on the 27 header paths of the record, from a directory whose `~/Projects/gororoba-workspace/`
subdirectory links to the checkout, reproduced `smith_torus.jsonl` byte for byte (the header paths resolve there);
`sign_search.py` on the E8-bar headers of (32009, 10754) reproduced `sign_search.log` byte for byte; and
`signed_perm_sweep.py` on the nine headers of the run (`e8-nm`, `e8-np`, `e8-vb`, `iso-nm`, `iso-np`, `w8-nm`, `w8-np`,
`xm-nm`, `xp-np` of `p32009-r10754`) reproduced `sweep_p32009.jsonl` byte for byte in 26 s, against 68 s for the serial
program. The programs `smith_torus.py`, `signed_perm_sweep.py` and `tangent_cone.py` are formatted with ruff after the
run (whitespace and quotes only) so the `sources` gate of `ci/gates.json` accepts them.

## Re-audit records: germ fingerprints and the pair flip at three specializations

[reaudit/](reaudit/) retains two records of the Codex re-audit that the findings note cites (`germ-checks.jsonl` for
the table of germ fingerprints). Their producers `germ_checks.py` and `audit.py` are retained as run in
`../working/reviews/codex-reaudit/`.

- `germ-checks.jsonl`: 27 rows, one per header, each with return code 0 and no Singular error.
  Each runs `std(J + m^N)` in `dp` for N = 2 to 7 and prints N, `vdim`, the size of the standard basis and the number of
  generators of G that reduce to zero. The quotient lengths q_2, ..., q_7 are 9, 39, 117, 283, 594, 1127 (E8-bar -> N+-,
  6 headers), 7, 27, 77, 182, 378, 714 (Iso, 6), 8, 35, 112, 294, 672, 1386 (W8, 6), 8, 27, 66, 135, 246, 413 (X-
  and X+, 6) and again 8, 27, 66, 135, 246, 413 (E8-bar -> VB, 3). X and E8-bar -> VB share q_N for N = 2 to 7 while
  their standard bases differ in size (28 against 29 at N = 2).
- `invariants.jsonl`: 42 rows. Each of the 27 headers carries the ranks of J and G, the orders and degrees of the G
  generators and its group of diagonal sign changes; four pair rows per specialization (E8-bar: flips t8, t9; X and W8:
  flip t9; Iso: none) give the ranks of J and G of N+, N- and the union (E8-bar 16, 16, 16 and 21, 21, 21) and the sign
  of each G generator against its partner (every one is +1 or -1); one row per specialization states that the
  receipt's header hashes match.

Replay from the tracked headers: `audit.py` (its `main`) reproduced all 42 rows of `invariants.jsonl` and
`germ_checks.py` all 27 rows of `germ-checks.jsonl` (3.5 s each); the tracked inputs now hold eleven headers per
specialization instead of nine, so a replay prints 46 and 31 rows. Both producers set `ROOT` to the checkout of the run
and read `working/build/inputs/`.

## Tangent cones of X- and E8-bar -> VB

The [retention audit](../../../archive/reviews/untracked-records-audit-2026-11-11/README.md) lists these cones as a result-missing record (section 3A, item 5).
[germ-xvb/](germ-xvb/) holds the tangent cones at the origin of the presolved slice germs of X- -> N- (7 variables, 12
generators of J, header `xm-nm.sing`) and E8-bar -> VB (8 variables, 17 generators, `e8-vb.sing`) at p = 32009. The
program `tangent_cone.py HEADER TAG` writes a Singular script that deforms each generator f to f(u t) / u^ord(f),
saturates by u and sets u = 0, all in the global ordering `dp`; `tc_xm.log` and `tc_vb.log` are its outputs and
`tc.resources` the wall time and peak resident set (0.05 and 0.06 s, 19 MB).

| | X- | E8-bar -> VB |
|---|---|---|
| generators of the cone | nine quadrics | one linear form and nine quadrics |
| Hilbert series numerator | 1, 0, -9, 18, -15, 6, -1 | 1, -1, -9, 27, -33, 21, -7, 1 |
| dimension, multiplicity | 4, 2 | 4, 2 |
| minimal primes | 1 (dimension 4, multiplicity 1, 3 linear generators) | 1 (dimension 4, multiplicity 1, 4 linear generators) |
| singular locus | dimension 4, multiplicity 1 | dimension 4, multiplicity 1 |

The VB numerator equals (1 - t) times the X- numerator, the factor of its one linear form, so the two cones have the
same Hilbert series once that form is eliminated. Each reduced cone is a linear 4-space (a prime of dimension 4 and
multiplicity 1 holding 3 independent linear forms in 7 variables, or 4 in 8), and each cone has multiplicity 2, so both
are double structures on a linear 4-space. The comparison leaves open whether the germs are isomorphic (A5-325): equal
Hilbert series of the cones and equal q_N for N = 2 to 7 (`reaudit/germ-checks.jsonl`) do not give a germ map. The
scripts regenerate byte for byte from the tracked headers with Singular 4.4.1, and a rerun reproduced both logs byte
for byte; the `redefining` lines at the head of each log (139 in both) are Singular's library-load notices.

## Falsifiers

A basis pair failing the automorphism identity, an orbit representative whose phi-image leaves the predicted closure, a
germ tuple different from the table, a base locus with a second prime through 0 or a prime different from the B9
pullback, a residual of a different dimension, or any disagreement between the three fields.
