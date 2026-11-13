# Good reduction of the fiber-track germ ideals (characteristic-0 transfer, check 1)

[`reduction_check.py`](reduction_check.py) tests, for each of the ten fiber-track pairs, the conjecture that the
presolved germ ideal J and the Nakayama generators G have good reduction at the two split primes the rank
certificates use: 32009 with i = 10754 and 32029 with i = 9115. It runs the producer that writes the rank engine's
headers (`../a5-kernel-attachments/nullity16_rees_fibers.py`, phase one, the path `fiber_inputs.py` specializes) once
over Q(i) (`ring (0,I)`, `minpoly=I2+1`) and once over each F_p, takes the monic reduced standard basis of J
(`option(redSB)`, `option(redTail)`, dp) and G reduced modulo J, reduces the Q(i) coefficients at the prime (i -> r),
and compares. It also computes the same basis and reduction of G from the retained header each rank certificate binds
(`../a5-exceptional-fibers/working/build/inputs/p<prime>-r<root>/<slug>.sing`) and requires an identical result
(`retained_header_equal` in each record).

Why it matters: [a5-char0-and-kernel-limits.md](../../notes/topics/a5-char0-and-kernel-limits.md) states the corrected
checks under which an h_d certified modulo p holds over Q(i). This is check 1; it makes J over Z[i] localized at p
specialize to the header's J, which check 2 (the degree-2 relations q(G) in J + m I^2 over Q(i)) and the common
integral model of check 3 build on. It does not compare the ranks of the subspace W_N used by check 3.

Falsifier: a coefficient whose denominator is divisible by p, a presolve that eliminates different variables, or an
F_p basis of J (or list of G) that differs from the reduction of the Q(i) one. Mutation: adding 1 to one coefficient
of the Q(i) basis must break the equality; it does on every row.

| Pair | Basis of J over Q(i) (elements, terms) | Largest denominator | G | 32009 | 32029 | Q(i) run |
|---|---|---|---|---|---|---|
| X- -> N- | 12, 78 | 1 | 15 | equal | equal | 4.5 s |
| X+ -> N+ | 12, 78 | 1 | 15 | equal | equal | 4.6 s |
| X+ -> N- | 12, 93 | 1 | 3 | equal | equal | 5.1 s |
| X- -> N+ | 12, 93 | 1 | 3 | equal | equal | 3.9 s |
| Iso -> N- | 1, 5 | 1 | 17 | equal | equal | 2.0 s |
| Iso -> N+ | 1, 5 | 1 | 17 | equal | equal | 2.2 s |
| W8 -> N- | 1, 9 | 1 | 24 | equal | equal | 17.8 s |
| W8 -> N+ | 1, 9 | 1 | 24 | equal | equal | 16.6 s |
| E8-bar -> N- | 16, 148 | 1 | 21 | equal | equal | 59.5 s |
| E8-bar -> N+ | 16, 148 | 1 | 21 | equal | equal | 59.3 s |

Every basis has integer coefficients with no imaginary part, so J is defined over Q. The comparison certifies good
reduction at the two primes tested only: another prime can still change the producer's decomposition or presolve.
The G lists match as reduced forms, and every retained header gives the same basis and G. Verdict: the conjecture survives
on all ten pairs at both primes (ledger A5-247). Records: `reduction-<slug>.json`; logs and `/usr/bin/time -v`
measurements in [`logs/`](logs/) (the longest pair, E8-bar -> N+, 2 min 33 s wall for the three fields and the two headers, and 165 MiB peak
for the controller). Host: the build host, one pair at a time, each Singular call in the producer's 16 GiB cgroup
scope.

Run from the repository root: `"$PYTHON" docs/evidence/a5-char0-transfer/reduction_check.py --slug xm-nm` (slugs as
in `fiber_inputs.SPECS`).

Not covered here: E8-bar -> VB (its header comes from the Nakayama route, `fiber_inputs` slug `e8-vb`) and the radicality and decomposition steps of the W8 all-degree proof over Q(i).

## Check 2, the good-reduction part of check 3, and the opposite-sign X fibers over Q(i)

- [`truncation_check.py`](truncation_check.py) (the ambient good-reduction part of check 3): the monic reduced standard basis of J + m^N over Q(i), m the
  ideal of the seven slice variables (the producer's ring still carries the presolve-eliminated t3 and t8), against the
  same basis from the retained header at both primes. X- -> N- survives at N = 4, 8, 11, 15 and 18, the closing orders of
  degrees 1 to 5 (N = 22, degree 6, stopped at the 3-hour cap without a result): 91, 366, 775, 1,696 and 2,743 elements, integer coefficients, equal at both primes, a corrupted coefficient
  detected (`truncation-xm-nm-n<N>.json`; ledger A5-249). A first revision took m from the producer ring and read
  refuted on a basis of 2,566 elements against 366; its records were overwritten by the fixed run.
  W8 -> N- survives at N = 4, 7, 10, 13 and 16 (d = 1 to 5): 183, 1,257, 5,009, 14,761 and 35,858 elements
  (ledger A5-277). These are good-reduction results only. If P_d is the degree-d product matrix and W_N is the image
  of m I^d in the truncation, the computed rank is rank [W_N; P_d] - rank W_N. Ambient good reduction does not
  compare this difference across characteristics. The corrected lower-bound criterion additionally requires a
  common integral ambient model, compatible matrix reduction in the retained coordinate order, and
  rank_Q(i) W_N = rank_F_p W_N. Neither A5-249 nor A5-277 computes that equality, so neither supplies a
  characteristic-zero lower bound by itself.
- [`quadric_lift.py`](quadric_lift.py) (check 2): the degree-2 relations {q : q(G) in J + m I^2} over Q(i) by the
  computation of the modular degree-2 receipts (`working/distribute/out/*/d2/d2-products.sing`), compared with the
  retained K2 at both primes (ledger A5-248). The run finished on a 4-core Kaggle CPU kernel in 30,481 s at 1.98 GiB peak
  ([`quadrics-xm-nm.json`](quadrics-xm-nm.json)): dimension 69, largest denominator 2, echelon form equal to K2 at
  both primes, mutation detected, so check 2 survives for X- -> N-. The build-host attempt stopped at the 3-hour cap without finishing (3:00:02, 1.26 GiB peak,
  `logs/quadrics-xm-nm.time`); the exact standard basis grows with the Gaussian coefficients of G. The upper bound needs only that the lifted
  quadrics are relations over Q(i) and reduce to K2, so the next route checks cofactor identities reconstructed from
  modular `lift` runs instead of a Q(i) standard basis, after it is timed against the cap. A first run took m from the nine-variable producer ring;
  that contracts to the same relation space but added 240 generators, and it was restarted on the slice variables.
- [`span_check.py`](span_check.py): over Q(i), every one of the 126 Pfaffian kernel coordinates reduces to 0 modulo
  J + m * FullF + (G), so G generates the kernel-coordinate ideal at the origin (Nakayama) and the fiber cone of (G)
  is the one the attaching data needs; dropping a generator leaves nonzero remainders (`span-<slug>.json`).
- [`x_opposite_qi.py`](x_opposite_qi.py): the arc certificate of X+ -> N- and X- -> N+ (`../a5-exceptional-fibers/arcs-x/`)
  replayed exactly over Q(i) in Singular: J smooth of dimension 4 at the origin, Phi on V(J) and a formal isomorphism,
  I = w (G'') with (G'') a smooth curve germ, so F(I) = Q(i)[y1, y2, y3] in every degree
  ([`x-opposite-qi.json`](x-opposite-qi.json); ledger A5-270). The first revision computed the gcd in sympy over
  Q(i) and stopped at its 20-minute limit; Singular takes 4 s per incidence.

## Check 2 for Iso -> N- and W8 -> N- (written case, 2026-11-10)

`quadric_lift.py --slug iso-nm` and `--slug w8-nm` compute the Q(i) degree-2 relation space of Iso (153 products of
17 generators, 6 slice variables) and of W8 (300 products of 24 generators, 7 slice variables) and compare its
reduction with the retained K2 at both primes, as the run of X- -> N- did (A5-248; 30,481 s and 1.98 GiB on a 4-core
Kaggle CPU kernel for 120 products). A simulation cannot answer it: the question is the exact standard basis over
Q(i). Falsifier: a relation space whose dimension differs from 68 (Iso) or 144 (W8), a denominator divisible by a
prime, or a reduced echelon form that differs from K2. Host: one Kaggle CPU kernel each (`a5-char0-iso-quadrics`,
`a5-char0-w8-quadrics`), free, inside the 12-hour session limit with the driver's timeout at 41,000 s. Runtime is
unmeasured for these fibers; the product count predicts that Iso is near the X- time and that W8 exceeds the session,
in which case its record is a `blocked_timeout` and the run moves to a host without the limit. The Iso relation file
uses the run's generators, ten of which are the negatives of the header's (`NEGATED`).

Result for Iso -> N- (ledger A5-294): the kernel `a5-char0-iso-quadrics` finished in 1,507 s at 0.39 GiB peak on 4
cores ([`quadrics-iso-nm.json`](quadrics-iso-nm.json)). The Q(i) relation space has dimension 68, so h_2 = 85, with
integer coefficients and a nonzero imaginary part; its reduced row echelon form reduces to the retained K2 at
(32009, i = 10754) and (32029, i = 9115), and the mutation arm is detected. The runtime prediction from the product
count was wrong by a factor of 20: the X- run took 30,481 s for 120 products and Iso took 1,507 s for 153.

Result for W8 -> N- on Kaggle: no record. The kernel `a5-char0-w8-quadrics` was pushed with
`kaggle kernels push --timeout 41000`, the driver's own 41,000 s limit counted from its start 370 s into the session,
and the runner held the driver's output in memory until the driver returned. The Kaggle limit therefore fired first
and cancelled the session with the setup-stage `summary.json` as its only output: the W8 computation exceeds 40,600 s
on a 4-core Kaggle CPU kernel, and its position at the stop is unknown. `kaggle/runner.py` now orders the three
limits (driver, outer `timeout`, the 41,400 s push limit), streams the driver's and Singular's output into
`/kaggle/working` as it is produced and rewrites `summary.json` every minute, and `quadric_lift.py` prints a STAGE
line per step; `a5-char0-e8-quadrics` was cancelled 2.5 hours in and pushed again with that runner. The W8 check
continues on the workstation, which has no session limit.

`truncation_check.py` counts its `--timeout` over its three Singular calls together: it fixes one deadline at the
start, passes each call the seconds left, and reports a call with none left as `blocked_timeout` without starting it.
The runner's rewritten `--timeout` therefore bounds the driver, where per-call allowances (39,500 s and 600 s under a
39,700 s limit) could sum past the outer `timeout`. The kernel `a5-char0-xm-truncation-n22` pins
`7e22f6d5b7813407ca14e17ddb03114176ddfa59`, which holds the shared deadline. The retained output that ledger row
A5-290 records used the per-call form.

### Where the direct Q(i) computation stops, and the modular engine (2026-11-11)

The STAGE lines locate the cost. On E8-bar -> N- the re-pushed kernel `a5-char0-e8-quadrics` (version 2, the runner
with ordered limits) kept its logs ([summary](kaggle/a5-char0-e8-quadrics/output/summary.json),
[Singular log](kaggle/a5-char0-e8-quadrics/output/singular.log)): the standard basis of J took 70 s, the 231
products were done at 823 s, and Singular exited with status 137 (a SIGKILL) 27,718 s into the standard basis of
the relation ideal J + m * products (2,095 generators). The retained files name no sender and hold no memory
reading; hypothesis: the session's memory limit. On the workstation the same check and the W8 check each stopped in
the same step under a 16 GB cap on their Singular scope; the systemd journal of that host reported an out-of-memory
kill of each scope, and no file of this directory retains those lines. The direct standard basis over Q(i) did not
finish for W8 or E8-bar on a 16 to 30 GB host; no verdict on either relation space follows.

`quadric_lift.py --cores N` replaces the two standard bases by `nfmodStd` (Singular `nfmodstd.lib`): standard bases
modulo primes on N processes, Chinese remaindering and rational reconstruction, then the library's final test
(`final_Test` in the installed `nfmodstd.lib`), which in characteristic 0 reduces every input generator to zero by
the result G and checks that G is a standard basis of the ideal it generates. That test proves input ⊆ <G>; it does
not prove <G> ⊆ input. For a homogeneous input the two tests and one prime at which G reduces to the standard basis
of the reduced input give equality by comparison of Hilbert functions; the relation ideals here are inhomogeneous in
the global ordering `dp`, where `modstd.lib` states its result holds "with high probability". A modular record of
this directory is therefore a standard basis of an ideal that contains the relation ideal, and equal to it up to
that probability: a relation space read from it contains the true one, so its dimension is an upper bound on the
number of degree-2 relations until the reverse inclusion is certified. On Iso -> N- with 8 processes it
gives the record of the direct run ([`quadrics-iso-nm-modular.json`](quadrics-iso-nm-modular.json): dimension 68,
both reductions equal, mutation detected) with stages at 3 s (J), 573 s (relation ideal), 578 s (normal forms) and
2,174 s (syzygies of the coefficient matrix,
[log](quadrics-iso-nm-modular.singular.log)). The syzygy step, a nullspace over Q(i) that Singular computes as a
module standard basis, takes 73 percent of that run and is the next step to move to exact linear algebra.

A modular reconstruction becomes an exact certificate only after the missing reverse membership is verified. One
sufficient record checks both ideal inclusions for the entire reconstructed standard basis. Another retains, for
enough independent reconstructed quadrics q, exact cofactor identities
q(G) = sum_j a_j J_j + sum_(ell,u,v) b_(ell,u,v) x_ell G_u G_v over Q(i). The record must keep the q coefficients,
coordinate and generator order, field and root convention, header and input hashes, and the membership witnesses.
Agreement after reduction at the retained primes and `final_Test` alone does not replace these identities for the
global inhomogeneous inputs used here.

The direct and the modular Iso -> N- records hold the same Q(i) relation space. The modular ideal contains the
relation ideal (the final test), so its relation space contains the one of the direct run; both have dimension 68,
so they are equal. The two records retain neither the Q(i) rows nor a digest, and the equal reductions at the two
primes alone would not show it: two echelon forms that differ by a multiple of 32009 * 32029 in one entry reduce
alike at both. A record written from now on carries `qi_echelon_sha256`, the digest of its reduced row echelon form
over Q(i).

On the workstation (54 GB) the modular engine ran out of memory on the 2,095-generator relation ideal of E8-bar and
the 2,101-generator one of W8, since each `nfmodStd` process holds the input and its own standard basis: E8-bar with
12 processes at a 22 GB cap after 14 minutes, W8 with 12 processes at a 44 GB cap within a minute of the start of
the relation ideal, and E8-bar with 4 processes at a 46 GB cap after 26 minutes (out-of-memory kills in the systemd
journal of that host, 2026-11-11; the journal lines are not retained here). Neither check has a verdict.

## Arc families over Q(i) (ledger A5-293)

[arcs_qi.py](arcs_qi.py) replays the arc families of the Iso, W8 and same-sign X slices
([blowup-arcs](../a5-exceptional-fibers/structure/arcs-iso-w8/blowup-arcs/README.md),
[arcs-x-same](../a5-exceptional-fibers/arcs-x-same/README.md)) on the J and G of the Q(i) producer. The arcs have
rational coefficients, and over Q(i) they keep J = 0, the order of G (4, 4, 5) and the rank of the limit map (5 on
Iso -> N+-, 6 on W8 -> N+-, 4 on X- -> N- and X+ -> N+) at the parameter points of the modular certificates
([arcs-qi.json](arcs-qi.json)). The fiber cones therefore have at least those dimensions in characteristic 0. The
record alone does not show that the limits fill V(K2) over Q(i); the Q(i) quadrics of every pair came later
(A5-421), and with them Iso closes by primality (A5-429) and W8 by the section below (A5-431); E8-bar -> VB is outside the Q(i) producer and is not replayed.

## One arc family in each component of the W8 quadric locus over Q(i) (ledger A5-431)

[`w8_component_arcs_qi.py`](w8_component_arcs_qi.py) substitutes two arc families into the J and G of the Q(i)
producer at the N- and the N+ basepoint and adds, to the order and rank of the section above, the dimension of the
linear span of the limits ([w8-component-arcs-qi.json](w8-component-arcs-qi.json)).

| Family | J on the arc | Order of G | Rank of [dF, F] | Span of the limits | Component |
|---|---|---|---|---|---|
| linear, five parameters, coefficients in Q(i) ([cert-w8-P](../a5-exceptional-fibers/structure/arcs-iso-w8/README.md)) | zero identically | 2 | 6, 6 | 15 | degree 20 |
| power series of the section above | zero through the truncation order | 4 | 6, 6 | 20 | degree 30 |

The quadric ideal K of W8 over Q(i) is the intersection of two primes of dimension 6, one containing 9 linear forms
and one containing 4 ([weight-slice record](../a5-kernel-attachments/README.md), A5-421 and A5-430). A family of
rank 6 has a 6-dimensional irreducible set of limits inside V(K), so its closure is a component, and the span
tells which: 15 dimensions cannot hold the degree-30 component, and 20 dimensions exceed the span of the
degree-20 one. The relation ideal L therefore lies in both primes, and L = K at both basepoints. The linear family
with the sign of its last slice coordinate reversed is the control: one generator of J is nonzero on it. A linear
case takes 25 s; a series case takes 1,540 s and 1.8 GB.

Check the record with `"$PYTHON" docs/evidence/a5-char0-transfer/w8_component_arcs_qi.py --check`; without the
flag the producer regenerates it.

[`w8_component_arc_matrices_qi.py`](w8_component_arc_matrices_qi.py) runs the same script and writes the eight
rank matrices themselves ([w8-component-arc-matrices-qi.json](w8-component-arc-matrices-qi.json)): two basepoints,
two families, two parameter points, each 24 rows by 6 columns (the five partial derivatives of F, then F), every
entry a pair of rationals for its real and imaginary part. Its check needs no Singular: it recomputes each rank
by exact elimination over Q(i) (6 for the full matrix, 5 for the derivative columns alone) and compares order,
rank and the count of nonzero limit coordinates with the record above. The matrices are the input of the rank
certificates planned in Rocq. Regeneration takes 26 minutes, the check 1 second.

## The same-sign X fiber cone over Q(i): I = M and L is 69 quadrics

[`monomial_certificate_qi.py`](monomial_certificate_qi.py) repeats over Q(i) the exact certificate of
[monomial-ladder](../a5-exceptional-fibers/monomial-ladder/README.md) with the G of the Q(i) producer. In one
Singular run per incidence (5 s, 0.1 GB) the producer's J vanishes on the parametrization, every term of
(1 + w)^8 G_j lies in the monomial ideal M = w^2 (a, rho, sig) + w (rho, sig) (a, rho, sig)^2, and the classes of the
15 generators in M / q M (dimension 15, q = (w^2, a, rho, sig) P) have rank 15. Nakayama's lemma gives I = M over
Q(i), so F(I) = Q(i) + sum_(d >= 1) M^d / q M^d, and elimination gives its defining ideal L:

| Pair | L over Q(i) | dimension, multiplicity | saturated | y1, y5, y6 | reduction at (p, i -> r) |
|---|---|---|---|---|---|
| X- -> N- | 69 quadrics, no higher generator | 4, 12 | yes | outside L, squares inside L | equals the retained K2 at 32009 and 32029 |
| X+ -> N+ | 69 quadrics, no higher generator | 4, 12 | yes | outside L, squares inside L | equals the retained K2 at 32029 |

The Hilbert series numerator is 1, 11, -3, 4, -1 over (1 - t)^4, that of k[y]/K2 modulo p, so every h_d of the
same-sign X incidences holds in characteristic 0, and the projective fiber V_+(L) is nonreduced over Q(i): L is
saturated and y1, y5, y6 are nilpotent. Falsifier: an element of the completed local ring of the slice outside
R = Q(i)[[t]] + (a, rho, sig) P, the one identification the certificate takes from the parametrization. The record is
`monomial-certificate-qi.json`; it holds the 69 generators of L as `l_polynomials`, and its verdict is `certified`
only when the generator count and degrees, the dimension, the multiplicity, the Hilbert numerator, the saturation
and the three nilpotents all take the values above (`invariant_failures` lists each one that differs).

## The slice rings over Q(i): kernel of the parametrization (A5-314)

[`slice_rings_qi.py`](slice_rings_qi.py) eliminates the parameters from the graph of each slice parametrization over
Q(i) and compares the kernel with the J of the Q(i) producer (together with the variables its presolve removed, which
J does not involve and which vanish on the slice):

| Pair | kernel: generators, dimension, multiplicity | equals J | run |
|---|---|---|---|
| X- -> N- | 14, 4, 6 | yes | 3.6 s |
| X+ -> N+ | 14, 4, 6 | yes | 3.5 s |
| E8-bar -> N- | 16, 5, 12 | yes | 59 s |
| E8-bar -> N+ | 16, 5, 12 | yes | 60 s |

So the coordinate ring of each slice is the image ring of its parametrization in characteristic 0 as well, the
input of the certificates of `../a5-exceptional-fibers/monomial-ladder`. Records: `slice-rings-qi-kernel-*.json`.
The same script holds a standard-basis form of the E8-bar closure check over Q(i) (I = I S); its two `nfmodStd`
cases ended at their 40,000 s timeout without a result, and the certificate below takes their place.

## The E8-bar slice ideal is an ideal of S over Q(i)

[`e8_closure_certificate.py`](e8_closure_certificate.py) proves over Q(i) the statement that A5-309 records at the
split primes: the slice ideal I of the E8-bar fiber is an ideal of S = P + P b, I = I S. In the polynomial model of S
(qw, qr, qs, qz, qa, qb, qu modulo qu (1 + qw) = 1 and qb^2 = EA (EA - qw (qw + 2)) qu^2) let It_k be the image of the
k-th generator of the Q(i) producer and n = (qa, qz, qr, qs, qb, qw^2) S. For each of the 42 targets t = qw It_j and
t = (qu - 1) It_j the cofactor file holds Gaussian rationals alpha_k, beta_k and polynomials D_xk with

    t = sum_k (alpha_k + beta_k (qu - 1)) It_k + sum_(x, k) D_xk x It_k    in S,

and one Singular run in characteristic 0 (minpoly I^2 + 1, ordering dp) reduces each of the 42 differences to zero
modulo the relations of S. The same run shows n = m_R S (every coordinate image reduces to zero modulo n, every
generator of n to zero modulo the coordinate images), S / n = Q(i) + Q(i) qw (colength 2) and J = 0 on the
parametrization. Since qu - 1 = -qw modulo n, the 42 identities are linear relations in I S / n I S whose qw-parts
have exact rank 21 over Q(i); so every qw It_j lies in sum_k Q(i) It_k + n I S, and with S = R + R qw and
n I S = m_R (I S), Nakayama's lemma over R gives I S = I.

Linear algebra found the cofactors, not a standard basis: 13,830 monomial multiples qb^b m^e qr^i qs^j qz^k qa^l x It_k
(m = 1 + qw, weight at most 10, m-exponent in [-7, 9]), the 42 class columns It_k and (qu - 1) It_k and the 42
targets form a 23,903 x 13,914 matrix whose reduced row echelon form gives one solution per prime, the reduction of
the Q(i) solution. Both roots of -1 at each split prime give real and imaginary parts, and rational reconstruction stabilizes over the primes listed in the table. Smaller
boxes leave a measured gap: weight 9 with the m-range [-7, 9] or [-8, 10] gives qw-relation rank 20 over Q(i), and
weight 10 with [-6, 8] gives rank 16 modulo 32009. `--check` first compares the sha256 of `e8_closure_certificate.py`,
`slice_rings_qi.py` and `reduction_check.py` with the record, so an edit of any of the three makes it fail until
`--write` regenerates the records with the resource flags below; it then reruns the exact
identities from the cofactor file and two mutations: one cofactor coefficient plus 1 breaks 1 of the 42 identities,
one coefficient of G_1 doubled breaks 42.

`--check` sends producer, exact-check and mutation scripts and diagnostics to a unique ignored workspace under
`docs/local/e8-closure-certificate/checks/`; retained generation diagnostics keep their bytes. Rational
reconstruction uses the integer square root of half the modulus, so an exact boundary coefficient remains
admissible when the modulus exceeds binary64 integer precision.

The modular stage defaults to two process workers with a twelve-GiB declared resident-memory budget. Each worker
reserves five GiB, based on the retained 4.073-GiB process peak plus margin, and the controller reserves one GiB.
`--workers 4 --memory-budget-gib 24` admits four workers when the host's reviewed case provides that capacity;
a declared budget below the required twenty-one GiB fails before a producer starts. The budget admits concurrency
and imposes no operating-system memory or swap limit. Native arithmetic threads stay one. The record's
`execution` fields retain requested and effective workers, the budget, native-thread environment and runtime versions.

| Pair | primes (root of -1) | coefficients, largest numerator / denominator digits | modular search and full-run cost | exact check | mutations fail |
|---|---|---|---|---|---|
| E8-bar -> N- | 32009 (10754), 32029 (9115), 32749 (15645), 32717 (11332), 32713 (974), 32693 (8590) | 39,168; 11 / 8 | 12 solves of 194.9-201.8 s, 655.3 s total wall, 4.10 GiB peak per worker | 14.2 s | 1 of 42, 42 of 42 |
| E8-bar -> N+ | the same six primes and roots | 39,168; 11 / 8 | 12 solves of 193.3-199.6 s, 653.4 s total wall, 4.09 GiB peak per worker | 14.5 s | 1 of 42, 42 of 42 |

The table records a full regeneration with four process workers, a twenty-four-GiB planning budget and one native
arithmetic thread per worker. Both compressed cofactor files reproduce their retained bytes.
[`e8-closure-check-validation.json`](e8-closure-check-validation.json) binds the generated records to the completed
exact replay and mutations and records identical selected-sign generation-diagnostic hashes before and after each
`--check`. [`e8_closure_validation.py`](e8_closure_validation.py) checks the certificate, cofactor, source and
diagnostic bindings. The on-demand `core-a5-e8-closure-certificate-qi` gate pins the complete receipt bytes and runs
that reader; `GOROROBA_SINGULAR_REQUIRED=1` also enables the corrected two-sign exact replay. Elapsed-time floats
record execution telemetry. Polynomial identities, ideal inclusions and the exact relation rank decide the verdict.

Records: `e8-closure-certificate-SLUG.json` (primes, box, counts, digests of the producer script, the Q(i) J and G,
this producer, `slice_rings_qi.py`, `reduction_check.py` and the cofactor file, stage times, verdict),
`cofactors/e8-closure-SLUG.json.xz`, and the Singular logs `logs/e8-closure-*`. Not covered: the premises that S is
finite over R and that S = R + R qw (A5-306 and A5-309 argue them; the certificate checks only S / n = Q(i) + Q(i) qw),
the fiber cone and its defining ideal L over Q(i), the Rees ideal in every degree, and E8-bar -> VB.


## The lower-bound step of the transfer is refuted as a criterion (ledger A5-316)

[transfer_counterexample.py](transfer_counterexample.py) replays the exact counterexample of an outside review
(2026-11-11) to the claim that good reduction of the ambient truncation k[t]/(J + m^N) turns a truncated rank computed
modulo p into a lower bound for h_d in characteristic 0. With J = 0 and I = (x^7, y^7, x^4 y^2 (c + x)),
c = 32009 * 32029, the degree-2 relation space is 0 over Q and modulo both primes, and the truncated rank of degree 3
at order 22 is 10 modulo each prime and 9 over Q ([transfer-counterexample.json](transfer-counterexample.json)): the
image W of m I^3 has rank 23 over Q and 0 modulo p, and a difference of ranks is not semicontinuous. The repaired
criterion and the rows it leaves standing are in
[a5-char0-and-kernel-limits.md](../../notes/topics/a5-char0-and-kernel-limits.md); `truncation_check.py` (A5-249)
remains a good-reduction computation and no longer stands for a lower bound.

## The E8-bar fiber cones over Q(i): the arc-jet ranks are lower bounds (ledger A5-346)

Over Q(i) the fiber cone F(I) of E8-bar -> N- and of E8-bar -> N+ satisfies h_d >= 21, 83, 225, 495, 952, 1666 and
2718 for d = 1 to 7, the values that the arc-jet ranks prove modulo 32009 and 32029
([arc-jets](../a5-exceptional-fibers/arc-jets/README.md), A5-335 and A5-339). [arc_jets_qi.py](arc_jets_qi.py)
lifts the modular computation arc by arc instead of transferring a truncated rank, which is the step A5-316 refutes.

The arcs of `jet_rank.py` are Phi(w, rho, sigma, e, zeta) with parameters that are polynomials in s with integer
coefficients, and Phi divides only by 2, 1 + w, (1 + w)^2 + 1 and e, whose constant terms are prime to p. The same
integers and formulas define an arc over Q(i) with coefficients in the localization of Z[i] at P = (p, i - r), and
reduction modulo P carries it to the modular arc. Reduction can raise a valuation, and then the functionals over
Q(i) differ from the modular ones; the counterexample of A5-316 has that shape (a coefficient divisible by both
primes). The record excludes it exactly:

1. J(Phi) = 0 over Q(i) as an identity in the five parameters: Singular substitutes Phi into the 16 generators of J
   of the Q(i) producer (the one whose good reduction A5-247 checks) and reduces modulo the three inverse relations;
   0 of 16 remain. The mutated map t9 + w leaves 15 of 16 nonzero. Every arc therefore lies on V(J) over Q(i) and
   its functionals vanish on L_d.
2. For each of the 3,000 arcs of each target (every arc of every retained record), exact arithmetic over Q(i) to
   order v + e: every coefficient is P-integral and reduces to the modular one, e = min val t_i equals its modular
   value, every coefficient of every G_j(t(s)) below s^v is exactly zero, and the coefficients of s^v to
   s^(v + e - 1) reduce to the modular ones. The valuations are (v, e) = (4, 2) on 2,000 arcs and (10, 2) on
   1,000, as in the modular records. The argument uses e and v alone. One coordinate does lose valuation: on arc
   2996 of both headers at 32009 the coefficient of s^3 in t2 is nonzero over Q(i) and divisible by P, so t2 has
   valuation 3 over Q(i) and 4 modulo p; e = 2 and v stand, each record lists the arc under
   `coordinate_valuation_drops`, and the bound is unchanged. A drop of e or v would void the arc's functionals,
   and the record's verdict fails on one.
3. The matrix of functionals over Q(i) then has P-integral entries and reduces entry by entry to the modular
   matrix, so its rank over Q(i) is at least the modular rank.

| Fiber | Record | Primes | Arcs checked per prime | Lower bounds over Q(i) |
|---|---|---|---|---|
| E8-bar -> N- | [arc-jets-qi-e8-nm.json](arc-jets-qi-e8-nm.json) | 32009, 32029 | 3,000 | h_1..h_7 >= 21, 83, 225, 495, 952, 1666, 2718 |
| E8-bar -> N+ | [arc-jets-qi-e8-np.json](arc-jets-qi-e8-np.json) | 32009, 32029 | 3,000 | the same |

One prime suffices for each bound; the second is a replicate on other arc coefficients. The bound h_2 >= 83 says
that the degree-2 relations of the cone over Q(i) span at most 231 - 83 = 148 dimensions, the number of quadrics of
K2 modulo p. Equality h_d = HF(k[y]/K2, d) over Q(i) needs the converse, 148 quadrics in L over Q(i) that reduce to
K2, which no record holds for E8-bar -> N+-; the lower bounds stand without it. Falsifier: an arc of a retained
record whose exact e or v differs from the modular one, or a generator of J over Q(i) that Phi leaves nonzero.

`arc_jets_qi.py --slug SLUG --write` produces a record and `--check` replays it (gate `core-a5-e8-arc-jets-qi`); one
header takes 16 to 23 minutes of wall time and 4,000 to 5,600 CPU seconds on five workers with 170 MB of peak resident
memory, measured on the build host with Singular 4.4.1.

## Both components of the E8-bar quadric scheme lie in the fiber over Q(i) (ledger A5-425)

Conditional on the quadric ideal over Q(i) of A5-421 and on the slice premise of A5-423, the reduced exceptional
fiber of E8-bar -> N- and of E8-bar -> N+, over the complex numbers, is the union of the two components of the
quadric scheme after the complex-linear change of the 21 generators that the premise supplies: a fourfold of degree
11 and a threefold of degree 4. The relation ideal L lives on the header slice and the minimal primes on the weight
slice; the change of generators between them is not shown to be defined over Q(i), so the statement is one about
complex points and transported components, and the computations below are over Q(i). [e8_fiber_components_qi.py](e8_fiber_components_qi.py)
substitutes the two arc families of the modular certificate ([arcs](../a5-exceptional-fibers/arcs/README.md)) into
the generators G of the Q(i) producer, with the family parameters W, R, S, Z, E as ring variables, and reads the limit
vector F, the first nonzero coefficient vector of G(x(s)); the record is
[e8-fiber-components-qi.json](e8-fiber-components-qi.json).

| Family | Arc | Order of G | Rank of [dF, F] at two points | Linear span of the limits |
|---|---|---:|---|---:|
| first-order | w = W s, rho = R s, sigma = S s, e = E, zeta = Z s | 2 | 4, 4 | 7 |
| order-5 | w = W s^2, rho = (R + S) s / 2, sigma = (R - S) s / 2, e = -1 + E s^2, zeta = Z s | 5 | 5, 5 | 12 |
| order-5 recentered at e = 2 (control) | the same with e = 2 + E s^2 | 3 | 2, 2 | 2 |

The numbers are the same on both targets. The two spans together have dimension 16. Phi satisfies the 16 generators
of J over Q(i) identically and the mutated Phi leaves 15 nonzero (the identity of A5-346, rerun here). Each limit
vector reduced at (32009, i = 10754) and at (32029, i = 9115) equals, polynomial by polynomial in all 21
coordinates, the limit of the retained modular family log of the same target. The spans 7 and 12 equal 21 minus
the 14 and 9 linear forms of the two minimal primes of the quadric ideal over Q(i) (A5-421).

**Inferred.** A relation f of degree d of the fiber cone has f(G) in J + m I^d in the local ring at the origin,
so on an arc of V(J) through the
origin with G of order nu the series f(G(x(s))) has order above d nu and f(F) = 0: every limit vector lies in V(L),
L the relation ideal. The premise of A5-423 supplies an isomorphism, over the complex numbers, of the slice germs
at the basepoint that carries the Pfaffian ideal of one slice onto that of the other; it induces a complex-linear
change A of the 21 generators under which the degree-2 relations on the header slice become the 148 quadrics K of
A5-421. Nothing shows that A is defined over Q(i), so the deduction runs over the complex numbers. There
V(L) lies in the image under A of V(K) = V(P1) union V(P2), where P1 (dimension 5, degree 11) and P2 (dimension 4,
degree 4) are prime over Q(i) and each is a union of conjugate geometric components of one dimension and degree.
A nondegenerate irreducible variety has degree at least its codimension plus one. The closure Y1 of the order-5
limits is geometrically irreducible of dimension at least 5, so it is a geometric component of the image of V(P1);
it spans 12 dimensions, so its degree is at least 12 - 5 + 1 = 8, more than half of 11, and V(P1) has a single
geometric component: Y1 is the whole image of V(P1). The closure Y2 of the first-order limits is geometrically
irreducible of dimension at least 4 and holds a point outside the linear span of Y1, because the joint span 16
exceeds 12; so it is a geometric component of the image of V(P2), of degree at least 7 - 4 + 1 = 4 = deg P2, and
equals that image. Hence V(L) = Y1 union Y2, both geometrically irreducible and defined over Q(i): a fourfold of
degree 11 and a threefold of degree 4 in projective terms. The
[attachments record](../a5-kernel-attachments/README.md#the-ten-blocked-fibers-into-nullity-16-are-the-fiber-cones-of-the-exceptional-fiber-record)
identifies the set of limits of the kernel with the complex points of this fiber, under its own premises (A5-411,
A5-415 and A5-417, which rest on a closure theorem whose text is uninspected). Under those premises and the two
above, that set for E8-bar no longer waits on the relation ideal in degrees 8 and above (A5-009); those degrees
decide the scheme structure alone, including whether the five coordinates that are nilpotent on the quadric scheme stay
nilpotent on the fiber.

Not covered: the scheme structure of the fiber, and the premise that joins the two slices. That premise is the
local-product argument of the
[attachments record](../a5-kernel-attachments/README.md#g_2-and-scaling-act-on-the-holomorphic-kernel-and-the-boost-does-not)
with the invariance `pf4(W) = det(B)^2 pf4(S)`; no map between the 21 generators of the two slices is retained, and
this record does not recompute it. The control family is a genuine family of arcs of V(J): its order 3 and rank 2
show that the order and rank of the certified family belong to the center e = -1. A family whose order, rank or span differs, a reduced limit that differs from
its modular log, a first-order limit inside the span of the order-5 limits, a control that keeps order 5 and rank
5, or a quadric ideal over Q(i) with other minimal primes falsifies the record.

`e8_fiber_components_qi.py --write` produces the record and `--check` replays it (gate
`core-a5-e8-fiber-components-qi`). One replay takes 7 minutes 8 seconds of wall time and 722 CPU seconds on two workers.
The Python parent ran under a 12 GiB memory scope and peaked at 0.17 GiB; each Singular process runs in its own
scope of the shared runner (`_run_singular` of `nullity16_rees_fibers.py`, 16 GiB each), two at a time, so the
parent scope does not bound the solvers and the admitted total is 12 + 2 x 16 GiB. Measured on the build host with Singular 4.4.1, Python 3.14.9 and python-flint 0.9.0.

## The plane where the two components of the reduced E8-bar quadric scheme meet

`scripts/a5_e8_plane_certificate.py HEADER PRIME_ID --repo . --run --record FILE` writes a Singular script (global
ordering `dp`) that adds the five nilpotent coordinates y4, y6, y7, y12, y14 to the retained degree-2 relations of an
E8-bar fiber, takes the two minimal primes, and tests their sum T against the ideal H of its linear forms: both
inclusions T in H and H in T, 18 independent linear generators, dimension 3 and multiplicity 1 for both. The script
embeds the relation text, so its sha256 binds the bytes Singular reads. The records in [`e8-plane/`](e8-plane/) hold
the verdict, the sha256 of the relation file and of the script, the Singular version and Singular's output, for the
three relation files this tree holds (Singular 4.4.1; 5 to 6 s of CPU and 27 MB each):

| Fiber | Prime | Record | Verdict |
|---|---|---|---|
| E8-bar -> N- | 32009 | [e8-nm-p32009.json](e8-plane/e8-nm-p32009.json) | the two components meet in a linear P^2 |
| E8-bar -> N- | 32029 | [e8-nm-p32029.json](e8-plane/e8-nm-p32029.json) | the same |
| E8-bar -> N+ | 32029 | [e8-np-p32029.json](e8-plane/e8-np-p32029.json) | the same |

E8-bar -> N- passes at both primes and E8-bar -> N+ at 32029; E8-bar -> N+ at 32009 is not run, because its relation
file (`e8np_p1`) is not retained. Each verdict holds modulo its prime; no characteristic-0 form is computed.

## Check 2 for E8-bar -> N- (written case, 2026-11-10)

`quadric_lift.py --slug e8-nm` computes the Q(i) degree-2 relation space of E8-bar -> N- (231 products of 21
generators, 9 slice variables, a J of 16 generators) and compares its reduction with the retained K2 (148 quadrics,
h_2 = 83) at both primes. A simulation cannot answer it: the question is the exact standard basis over Q(i).
Falsifier: a relation space whose dimension differs from 148, a denominator divisible by a prime, or a reduced echelon
form that differs from K2; a difference that a sign convention of the run's generators explains is read from the
record before any verdict. Host: one Kaggle CPU kernel (`a5-char0-e8-quadrics`), free, inside the 12-hour session
limit with the driver's timeout at 41,000 s. Runtime is unmeasured: the Q(i) producer alone takes 64 s on the build
host, X- -> N- with a J of 12 generators and 120 products took 30,481 s, so this run may exceed the session, in which
case its record is a `blocked_timeout` and the question moves to the certificate route of
`../a5-exceptional-fibers/monomial-ladder`. E8-bar -> VB runs through the same driver
(`--slug e8-vb`, 55 products of 10 generators, 8 slice variables, a J of 17 generators): its row and Schur data come
from `nakayama_rees_fibers` (`fiber_inputs._nakayama_inputs`), which `reduction_check._script` now uses for that
slice; the Q(i) producer takes 97 s and 1.3 GiB on the build host. It is compared with the retained K2 at 32029
only, the prime whose relation file sits with the other fibers' files; it runs on the owned workstation, which has
no session limit.

Result for E8-bar -> VB (ledger A5-315): `quadric_lift.py --slug e8-vb` finished on the workstation in 650 s at
1.24 GiB peak ([`quadrics-e8-vb.json`](quadrics-e8-vb.json)). The Q(i) relation space has dimension 21, so
h_2 = 34, with largest denominator 25 and a nonzero imaginary part; no denominator is divisible by 32029, its
reduced row echelon form reduces to the retained K2 at (32029, i = 9115), and the mutation arm is detected. The
comparison at 32009 is not run: that relation file is retained outside the directory the driver reads.
