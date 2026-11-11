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

Why it matters: [a5-char0-and-kernel-limits.md](../../notes/topics/a5-char0-and-kernel-limits.md) states three checks
under which every h_d certified modulo p holds over Q(i). This is check 1; it makes J over Z[i] localized at p
specialize to the header's J, which checks 2 (the degree-2 relations q(G) in J + m I^2 over Q(i)) and 3 (good reduction of J + m^N) build on.

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

## Checks 2 and 3, and the opposite-sign X fibers over Q(i)

- [`truncation_check.py`](truncation_check.py) (check 3): the monic reduced standard basis of J + m^N over Q(i), m the
  ideal of the seven slice variables (the producer's ring still carries the presolve-eliminated t3 and t8), against the
  same basis from the retained header at both primes. X- -> N- survives at N = 4, 8, 11, 15 and 18, the closing orders of
  degrees 1 to 5 (N = 22, degree 6, stopped at the 3-hour cap without a result): 91, 366, 775, 1,696 and 2,743 elements, integer coefficients, equal at both primes, a corrupted coefficient
  detected (`truncation-xm-nm-n<N>.json`; ledger A5-249). A first revision took m from the producer ring and read
  refuted on a basis of 2,566 elements against 366; its records were overwritten by the fixed run.
  W8 -> N- survives at N = 4, 7, 10 and 13 (d = 1 to 4): 183, 1,257, 5,009 and 14,761 elements (ledger A5-277).
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

## Arc families over Q(i) (ledger A5-293)

[arcs_qi.py](arcs_qi.py) replays the arc families of the Iso, W8 and same-sign X slices
([blowup-arcs](../a5-exceptional-fibers/structure/arcs-iso-w8/blowup-arcs/README.md),
[arcs-x-same](../a5-exceptional-fibers/arcs-x-same/README.md)) on the J and G of the Q(i) producer. The arcs have
rational coefficients, and over Q(i) they keep J = 0, the order of G (4, 4, 5) and the rank of the limit map (5 on
Iso -> N+-, 6 on W8 -> N+-, 4 on X- -> N- and X+ -> N+) at the parameter points of the modular certificates
([arcs-qi.json](arcs-qi.json)). The fiber cones therefore have at least those dimensions in characteristic 0. The
record does not show that the limits fill V(K2) over Q(i), because the Q(i) quadrics exist for X- -> N- only
(A5-248); E8-bar -> VB is outside the Q(i) producer and is not replayed.

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

