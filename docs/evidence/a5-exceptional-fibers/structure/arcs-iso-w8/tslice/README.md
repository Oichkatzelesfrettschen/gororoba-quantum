# t-space slice ladder: the analytic spread of the Iso -> N- ideal from linear slices of the graph of G

The fiber cone F(I) = k[y]/L of I = (G_1, ..., G_17) on the Iso -> N- slice V(J) (the quadric
t2^2 + t4^2 - t5^2 - t6^2 + t7^2 = 0 in the six variables t2..t7) equals k[y]/K2 in every degree exactly when the
analytic spread l(I) is 5. The chart saturations in [../chart-runs/](../README.md#the-deciding-test-one-blowup-chart)
work in the 23 variables (t, z) and did not finish. This ladder works in the six t-variables: it asks whether the
origin lies on the closure of the part of V(J) where l_1(G) = ... = l_k(G) = 0 for k generic linear forms, and reads
dim E0 >= k from the answer. Everything holds over F_32009 (controls and Iso) and F_32029 (Iso preregistration);
the claims are statements over the algebraic closure of those fields and say nothing about characteristic 0.

## The criterion and its reduction

1. K2 is the ideal of the quadratic relations among the G generators (`../../../k2_hilbert.py` docstring), so K2 lies
   in L. K2 is geometrically prime of dimension 5 and degree 23 (A5-058 to A5-060). A proper quotient of the domain
   k[y]/K2 has dimension below 5, so F(I) = k[y]/K2 holds exactly when dim F(I) = 5, that is, when l(I) = 5; the
   multiplicity half of A5-011 then holds as well.
2. l(I) = dim E0 + 1 for E0 = Proj F(I) (reduced), the fiber over the origin of Bl = Bl_I V(J). V(J) is an
   irreducible hypersurface, so Bl is irreducible of dimension 5 and the exceptional divisor E has dimension 4.
3. Let Lambda_k be a generic linear space of codimension k in P^16 and Q_k = (J, l_1(G), ..., l_k(G)). Every
   component of Bl cut by Lambda_k has dimension at least 5 - k, and E cut by Lambda_k has dimension 4 - k, so no
   component lies inside E. Properness of Bl gives: E0 meets Lambda_k exactly when the origin lies on the closure of
   V(Q_k) minus V(I). For generic Lambda_k that happens exactly when dim E0 >= k.
4. Saturation by t2 computes that closure near the origin when V(I) lies inside {t2 = 0} there. For Iso -> N- the
   germ of V(J + G) at the origin is the linear 3-space L0 inside {t2 = 0} (A5-068), and the other components of
   V(J + G) miss the origin. The branches that t2 would remove wrongly are those of V(Q_k) minus V(I) lying inside
   {t2 = 0}. V(J) cut by t2 = 0 is the 4-fold t4^2 - t5^2 - t6^2 + t7^2 = 0, and the preimage of a generic
   codimension-k space under a map from a 4-fold has dimension at most 4 - k, so for k >= 4 the wrongly removed
   set is finite and carries no branch through the origin. At k = 3 it can be a curve, so an "off" reading at k = 3
   would not decide; an "on" reading does.
5. "On" is read as every generator of Q_k : t2^infinity vanishing at the origin (`size(reduce(S, std(maxideal(1)))) == 0`).

Genericity enters each direction, and every record below carries it. A reading "on" implies dim E0 >= k only when
Lambda_k is generic for a possible lower-dimensional E0; a reading "off" implies dim E0 < k only when Lambda_k is
generic for the 4-dimensional E. One QRNG form set is one point of the parameter space, so each reading holds for that
set and is evidence for the generic statement; a second form set and a second prime are the checks. The t2
saturation needs the support condition of item 4.

## Method and files

`tslice_gen.py` (run from the repository root with `$PYTHON`) writes `forms.json` and one Singular script per case
under `sing/`. The scripts read the header of the case (`../../working/build/inputs/`, sha256 in the first script
line), build the forms l_i(G) from the coefficients of `forms.json`, and write each RESULT line to
`logs/CASE.result` as it exists: the dimension and degree of Q_k : t2^infinity, whether its generators vanish at the
origin, and seconds. Global ordering `dp` throughout. `run.sh CASE [CAP_GIB [LIMIT_S]]` runs one script under
`prlimit --as`, `timeout` and `/usr/bin/time -v` and keeps `CASE.log`, `.err`, `.time` (elapsed seconds and peak
resident set; empty when `timeout` ends the run) and `.rss` (resident set every 30 s). It rewrites the repository
prefix to nothing and the home directory to `~` in `.log`, `.time` and `.err`, so the retained logs name
repository-relative paths only.

Forms. Iso l1..l5 take 17 draw values each, and the X forms take 3 each, from
`docs/evidence/anu_qrng/draw-2026-11-06T113431Z.json`: the uint16 values below the prime in index order, zero-based.
`forms.json` lists [index, value] per coefficient. Iso l1..l4 equal the l1..l4 of
`../chart-runs/fx4-w8p2/chart-ckpt.sing` and of `../chart-iso-p32009-slice-coefficients.json` (the generator raises if
they differ); l5 continues the same draw (indices 151 to 187). The draw holds no value in [32009, 32029) below index
188, so the p = 32029 lists are the same indices and values. The X forms use indices 188 to 209 and serve both
incidences. The cross-check function a0 of the Iso runs is the l0 of the chart scripts
(`../chart-iso-pP-coefficients.json`, draw 2026-11-05T235924Z, indices 2 to 27); the X a0 is `x-l0`. No Python seed
literal is involved, so `ci/seed_provenance.py` needs no allocation row.

Saturations. `t2` runs `sat_with_exp(Q, t2)` of `elim.lib` (iterated quotients). `t2h` computes the same ideal: it
homogenizes the `dp` standard basis of Q with a variable h, takes a `dp` standard basis in the ring (other variables, h,
t2) whose last variable is t2, divides each element by the highest power of t2 that it contains (the Bayer-Stillman
rule for a degree-reverse-lexicographic order with t2 last) and sets h = 1. The two give the same dimension, degree
and reading on every case that both finished (the six pairs of the table). `a0` runs `sat_with_exp(Q, a0)`; a0 lies in
I, so this removes V(I) everywhere and is the chart-style cross-check. `G` saturates by the whole ideal I; it ran once,
on the smallest control (X+ -> N-, k = 2), and ended at its 300 s limit with no line past the start, so the
single-function saturations carry the readings.

## Controls

Host: the build host (WSL2 capsule, AMD Ryzen 5 5600X3D, 10 CPUs visible, 47 GiB), passagemath-singular 10.8.13
(Singular 4.4.1, built 12 October 2026), one thread per process, p = 32009. "On" means the origin lies on the closure.
Peak is the maximum resident set of `/usr/bin/time -v` in MiB; times are wall seconds.

| Case | Expected | Reading | Dimension, degree of Q_k : s^infinity | Time | Peak |
|---|---|---|---|---:|---:|
| X+ -> N-, k = 2: `t2` / `t2h` / `a0` | on | on, on, on | 3, 18 / 3, 18 / 2, 58 | 9.5 / 1.9 / 187 s | 32 / 27 / 42 |
| X+ -> N-, k = 3: `t2` / `t2h` / `a0` | off | off, off, off | 3, 18 / 3, 18 / unit ideal | 6.7 / 0.8 / 0.4 s | 23 / 21 / 18 |
| X- -> N+, k = 2: `t2` / `t2h` / `a0` | on | on, on, on | 3, 18 / 3, 18 / 2, 58 | 9.7 / 1.9 / 177 s | 32 / 28 / 42 |
| X- -> N+, k = 3: `t2` / `t2h` / `a0` | off | off, off, off | 3, 18 / 3, 18 / unit ideal | 8.4 / 0.8 / 0.3 s | 23 / 21 / 18 |
| Iso, k = 5: `t2h` / `t2` / `a0` | off | off, off, off | 4, 6 / 4, 6 / 0, 720 | 272 / 3,022 / 814 s | 377 / 382 / 330 |
| Iso, k = 3: `t2h` / `t2` | on | on, on | 4, 6 / 4, 6 | 16 / 37 s | 81 / 74 |

That is 17 readings (12 on X, 3 on Iso at k = 5, 2 on Iso at k = 3), and every one read as predicted. The Iso k = 3
a0 saturation ran 786 s without a line past its start and was stopped; the brief asks for a0 on the cheap controls
only (`logs/iso-p32009-k3-sata0.result` records the stop).

Reading the table.

- The X controls (l(I) = 3, E0 = P^2, certified by `../../arcs-x/`) are forced by linear algebra: with three
  generators any two independent forms meet P^2 and three cut it empty, and Q_3 is exactly (J, G). They test the
  implementation and the support condition of item 4, and leave the genericity half of the criterion untested. At
  k = 3 the a0 saturation is the unit ideal at once, and the t2 saturation leaves a dimension-3, degree-18 closure that
  misses the origin: near the origin V(I) lies inside {t2 = 0} on both incidences. A5-068 names Iso and W8 only, so
  this support condition is measured here for X.
- Iso k = 5 reads "off" three ways, and the expectation is a theorem (E0 lies in V(K2), of dimension 4, so a generic
  Lambda_5 misses it), so this control tests the saturations and the t2 support. The a0 saturation leaves 720 points
  (dimension 0) and none is the origin. The t2 saturations leave a dimension-4, degree-6 closure (it contains the
  closure of V(J, G) minus V(t2), the junk over the base locus, plus the slice points) and the origin is not on it.
- Iso k = 3 reads "on". `sing/iso-p32009-k3-junkcheck.sing` computes JK, the closure of V(J, G) minus V(t2); JK does not
  depend on k. JK has dimension 4 and degree 6 and the origin is not on it (`logs/iso-p32009-k3-junkcheck.result`:
  "origin on the junk 0"). V(S) for S = Q_3 : t2^infinity is the union of V(JK) and the closure of the points with
  G != 0 and t2 != 0 that satisfy l_1(G) = l_2(G) = l_3(G) = 0, so the origin, which lies on V(S) and off V(JK), lies on
  the closure of those points. That is the slice proper, and dim E0 >= 3 agrees with the arcs of A5-067 (rank 4). The
  stage of the script that saturates S by JK to display the slice proper (dimension, degree) had no result at the
  1,800 s limit and is not part of the required controls.
- The costs did not grow with the number of forms: k = 3 took 16 s and k = 5 took 272 s (`t2h`), against the brief's
  expectation that k = 3 costs most, so no stop time or growth curve applies. Hypothesis: Q_5 cuts the junk down to the
  720 isolated slice points and the final standard basis is the cost. The `.rss` files hold the sampled resident
  sets; none exceeds 0.45 GiB.
- `t2h` runs 5 to 11 times faster than `t2` on the cases measured (X: 5 to 10 times; Iso k = 5: 11 times; Iso k = 3:
  2 times), so it is the primary saturation of the preregistered rows and `t2` its twin.

## Preregistered decision: Iso k = 4 at p = 32009 and p = 32029 (not run)

Question. Does the origin lie on the closure of {t in V(J) minus V(I) : l_1(G(t)) = ... = l_4(G(t)) = 0}? The
reading decides dim E0 >= 4, that is l(I) = 5.

Precondition, measured. The origin must lie off JK, the closure of V(J, G) minus V(t2), which does not depend on k. It
does at p = 32009 (the k = 3 junk check) and at p = 32029 (`sing/iso-p32029-junk.sing`, `logs/iso-p32029-junk.result`:
JK of dimension 4 and degree 6, "origin on the junk 0", 0.03 s), so the t2 saturation reads the slice at both primes.

Commands, from the repository root, one decisive run per prime beside its twin:

    sh docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/run.sh iso-p32009-k4-satt2h 20 7200
    sh docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/run.sh iso-p32029-k4-satt2h 20 7200
    sh docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/run.sh iso-p32009-k4-satt2 20 7200
    sh docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/run.sh iso-p32029-k4-satt2 20 7200

The scripts exist in `sing/` (`iso-pP-k4-satt2h.sing`, `iso-pP-k4-satt2.sing`); the forms are l1..l4 of `forms.json`
(indices 2 to 148 of the draw; the same indices at both primes), each with the sha256 of its header in the first
script line, `dp`, the `t2` saturation of item 4 (valid at k >= 4 by the dimension count there). The cap is 20 GiB of
address space and the limit 7,200 s. The `t2h` run decides; the `t2` run confirms.

Forecast. The bracketing controls ran on the same host: k = 3 in 16 s at 81 MiB and k = 5 in 272 s at 377 MiB (`t2h`);
the `t2` twin took 37 s at k = 3 and 3,022 s at k = 5. Q_4 is one-dimensional, between the two. Forecast: `t2h` finishes
between 15 s and 10 min at under 1 GB, `t2` between 37 s and 1 h; rating: 80 percent that `t2h` finishes within 10 min,
raised by a monotone time and memory trend in the `prot` trace and lowered by any pair-set growth past the k = 5 trace
(4,000 pairs). The a0 cross-check costs 814 s at k = 5 and is not preregistered at k = 4.

| Reading at a prime | Meaning | Ledger action |
|---|---|---|
| on | for this form set, E0 meets Lambda_4: dim E0 >= 4, l(I) = 5, F(I) = k[y]/K2 in every degree at that prime (A5-067 survives as an F_p statement; A5-007 holds in every degree there). | A5-067 and A5-007 move to survives with the genericity caveats; both primes on closes the question at the two primes. |
| off | for this form set, E0 misses Lambda_4: dim E0 <= 3 for generic Lambda_4, l(I) <= 4, so F(I) is a proper quotient of k[y]/K2 and A5-007 fails in some degree of at least 6 at that prime. | A5-007 refuted at that prime for generic forms; the reading is first repeated with a second form set from a fresh ANU draw (registered in `docs/evidence/qrng_seeds/allocations.json` before use), because an "off" reading is also what a special Lambda_4 gives. |
| split between the primes | the forms are special at one prime, or l(I) depends on the prime. | A5-026 (agreement of the primes) is tested by a repeat with a second form set at both primes. |
| `t2` and `t2h` disagree | an implementation defect. | Stop; compare the saturated ideals by mutual reduction. |
| a limit or cap ends the run | no reading. | Record the stage and the `prot` trace; no ledger status moves. |

## Reuse for W8 and for E8-bar -> VB

The criterion carries over with the generator count, the slice variety and the support of V(I) replaced: W8 -> N-
(24 generators, l(I) = 6 certified through the component C20, A5-068 for the t2 support) and E8-bar -> VB (10 generators,
l(I) = 4 certified, A5-015). The dimension ladder reads dim E0 only. W8 asks whether the C30 component of V(K2)
(dimension 5, degree 30) lies in E0 beside C20 (dimension 5, degree 20), and E8-bar -> VB asks whether the degree-3 threefold lies in E0 beside the degree-4
one: both components have the same dimension, so a slice of codimension l - 1 meets E0 whether or not the second
component belongs to it, and codimension l misses it either way. The k = l - 1 reading for W8 (k = 5) and for
E8-bar -> VB (k = 3) is therefore a consistency control of the method and decides neither component question. A
component-resolving variant would count the points of E0 cut by Lambda_{l-1} (20 against 50 for W8, 4 against 7 for
E8-bar -> VB) by keeping the G-coordinates, which is the sliced chart that stalled, or by counting the branches of
the closure at the origin; hypothesis: the branch count equals the point count when each point is a transversal
limit, untested and not proved.

## Limits and falsifiers

- A control reading the other way would break the method; none did (17 readings, three saturations).
- A reading "on" at k = 4 from a special form set (the origin on a closure although dim E0 <= 3) or "off" from a special set
  (dim E0 = 4 missed) is possible; a repeat with a fresh draw and the second prime bound it.
- The t2 support condition holds by the dimension count at k >= 4; the origin is off JK at both primes
  (the junk checks above), which A5-068 predicts.
- The reduction concerns the fiber over the origin of Bl_I V(J) at the primes 32009 and 32029.
