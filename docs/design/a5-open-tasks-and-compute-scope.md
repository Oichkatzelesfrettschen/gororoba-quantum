# A_5 roadmap item 6: open tasks, blockers and compute placement

Roadmap item 6 of `dimension32-global-topology` ([program](dimension32-global-topology-program.md#attachments-roadmap-item-6))
admits attaching maps on every admitted incidence, not a frontier matrix. Its working program is
[a5-kernel-attachments-program.md](a5-kernel-attachments-program.md), which names four deliverables:
1. the 8 -> 12 limit sets;
2. 12 -> 16 and 8 -> 16;
3. compatibility;
4. attaching maps.

The exceptional-fiber computations (ledger `docs/evidence/a5-exceptional-fibers/ledger.tsv`) supply the supports and
limit sets these deliverables need. Item 7, the finite global model of Z_5 with its homology and cup products,
consumes the attaching maps. Item 8, the recurrence across the doubling ladder, compares n = 4 with n = 5.

This document lists the open tasks of the session tracker with their next computation, what blocks it, where each runs
and its cost estimate from a measured record. The exceptional-fiber tasks below supply supports and Hilbert functions;
they do not by themselves admit item 6, whose four plan steps (`docs/state/plans/a5-kernel-attachments.json`) stay
open in the section "Item-6 deliverables". [a5-vb-degree7-and-w8-char0-plan.md](a5-vb-degree7-and-w8-char0-plan.md)
holds the detail for E8-bar -> VB degree 7 and W8 in characteristic 0.

## Where the campaign stands (2026-11-10)

The truncated-rank ladder computes h_d = HF(F(I), d) one degree at a time: degree d closes at truncation order
N = 3d + 1 on E8-bar -> VB (A5-260) and at N = 4, 8, 11, 15, 18, 22 for d = 1 to 6 on X- (A5-249). The highest
closed order is N = 22 (VB degree 7, A5-286 and A5-287; X- degree 6). Every certified value equals HF(k[y]/K2, d),
the value K2 predicted before the run.

| fiber pair | certified h_d (both primes) | all-degree statement | what closes it |
|---|---|---|---|
| X+ -> N-, X- -> N+ | C(d + 2, 2) | proved over Q(i): F(I) = Q(i)[y1, y2, y3] (A5-270) | closed |
| W8 -> N+- | d = 1 to 5; h_6 = 8,624 proved | proved mod p: F(I) = k[y]/K2, V(K2) = C20 cup C30 (A5-066) | characteristic 0 (task 122) |
| Iso -> N+- | d = 1 to 6 | proved mod p: an explicit arc family is dense in V(K2), so F(I) = k[y]/K2 (A5-067, A5-007) | characteristic 0 |
| E8-bar -> VB | d = 1 to 7 | proved mod p: arcs are dense in both components of V(K2), so F(I) = k[y]/K2 (A5-005, A5-015, A5-016) | characteristic 0 |
| X+ -> N+, X- -> N- | every degree | proved: the slice ideal is a monomial ideal M at all four modular cells (both incidences, both primes) and over Q(i), so F(I) is the positive part of P[M T] / q P[M T]; its defining ideal is the 69 quadrics K2 at the three modular cells with a retained K2 (X- -> N- at 32009 and 32029, X+ -> N+ at 32029) and in the Q(i) presentation, and X+ -> N+ at 32009 retains I = M without a K2 comparison (A5-304, A5-305, A5-306, A5-314); K2 is saturated and nonreduced along one embedded plane (A5-303); F(I) is not Cohen-Macaulay (A5-245 refuted) | closed at the three checked cells; the K2 comparison of X+ -> N+ at 32009 is not retained |
| E8-bar -> N+- | d = 1 to 6 | open: K2 is saturated and nonreduced on an embedded quadric threefold (A5-312, A5-313); h_6 = 1,666 on N- and on N+ at both primes and L_d = (K2)_d through degree 6 (A5-335, arc-jet ranks on each header; K2 inside L for N+ at 32009 by the sign isomorphism); the slice ideal is an ideal of S = P + P b, so F(I) is the positive part of S[I T] / (m_R S) S[I T] (A5-309) | the elimination of that presentation (task 110), or membership of degree-6 forms (task 125) |

Three findings bound the ladder's value. Every all-degree statement above came from geometry (arcs, component
containment, blowup planes), never from a rung. The export cost grows about 1.36 times per order on VB with
`slimgb` (12,150 s at N = 21, 16,500 s at N = 22 on the laptop), so N = 31, degree 10, extrapolates to about three
days per prime for a value K2 already predicts. E8-bar -> N+- degree 6 is the one cell whose value is unknown.
The ladder therefore stops at its present rungs except for that cell, and task 113 (W8 degree 6 at N = 19, a value
A5-066 already proves, 129 to 223 GiB) is withdrawn (owner decision of 2026-11-10, ledger row A5-291).

Three gaps separate the fiber record from item 6:
- field: every fiber statement except A5-270 holds at p = 32009 and p = 32029. Check 1 of the characteristic-0
  transfer covers all ten pairs (A5-247). A5-249 and A5-277 certify ambient good reduction for X- and W8 but do not
  compare rank_Q(i) W_N with rank_F_p W_N, so they supply no characteristic-zero lower bound by themselves. Direct
  check-2 results exist for X- (A5-248), Iso -> N- (A5-294) and E8-bar -> VB at 32029 (A5-315); the remaining rows
  need exact relations and either the W_N rank equality or a direct characteristic-zero lower bound;
- kernels: F(I) describes limits of the generator vector G, and item 6 needs limits of ker L_a in a Grassmannian.
  The exact limit along sampled arcs is computed on every family, the VB arcs through k = -9 included (A5-272 to
  A5-276, A5-292, A5-295): dimension 8, inside the base kernel. The limit is one plane per fiber point on the families whose
  fiber coordinates y are computed; on E8-bar -> VB the dependence on the fiber point is untested, since y is not
  computed there (A5-276). The image of a whole fiber in the Grassmannian is not computed;
- reality: item 6 admits limits along real arcs with two-sided certificates. Real arcs now exist on the opposite-sign
  and same-sign X incidences, on Iso and on the degree-30 component of W8 (rational arcs); the degree-20 component of
  W8 and both E8-bar families have arcs over the prime fields only, and no incidence has the excluded side (A5-250).

The order of work that follows: the E8-bar -> N+- degree-6 membership (tasks 110 and 125), the same-sign X relations
beyond degree 6, the real certificates (tasks 126 and 127), then check 2 on W8. None of these needs more than the laptop's 52 GB, so no paid-cloud case is open.

## Run policy

The owner's ruling of 2026-11-09 approves well-scoped long runs and any Kaggle session that finishes under 12 hours;
Kaggle's 12-hour session limit is the one hard cap. A run is well scoped when it states:
- its falsifier;
- its host;
- a runtime estimate from a measured rate;
- its memory against the host budget.

It launches with a deadline equal to the estimate plus margin and a watcher that pulls results and cleans up on exit.
Paid cloud time (Azure, AWS, GCP credit) and QPU jobs keep their written-case rule. A real choice between alternatives
goes to the owner as a question with the estimates.

On 2026-11-09 the session generalized a limit the owner had given for one run into a 3-hour cap on every run. That
policy never existed, and it stopped three runs that had no other defect:
- check 2 on X- (A5-248);
- the ambient good-reduction check at X- N = 22 (A5-249), which cannot replace the missing W_N rank comparison;
- VB degree 7 (A5-279).

Heavy computation stays off the build host, the owner's interactive workstation, unless the owner authorizes that run:
Kaggle first, then the Windows compute laptop.

## Hardware (sources: `docs/runbooks/classical-compute-pool.md`, gororoba-infrastructure `hosts/README.md`, `clouds/`)

| substrate | CPU, RAM, GPU | job budget | limit and cost |
|---|---|---|---|
| Windows workstation laptop (`ALIENWARE`, WSL) | 32 threads, 54 GiB visible, RTX 4090 Laptop 16 GiB | 52.5 GB RAM + 13.4 GiB GPU | free; Singular 4.4.1 from passagemath, engines v11 to v13 |
| build host | 12 threads, 47 GiB visible, RTX 4070 Ti 12 GiB | 38.6 GiB + 10.1 GiB | free; heavy runs stay off it while Windows is in use |
| OCI `lab-a1` | A1.Flex, 2 OCPU aarch64, 12 GB | 9.5 GiB | free |
| Kaggle CPU session | 4 cores, 30 GB | 0.82 x RAM | 12 h; 5 batch sessions at once; free |
| Kaggle GPU session | 4 cores, 29 GB, 2 x T4 15 GiB or P100 | 0.84 x GPU + 0.82 x RAM | 12 h; 2 at once; 30 GPU-hours a week |
| Azure (pay-as-you-go) | `Standard_FX4ms_v2`, 4 vCPU, 84 GB, for jobs above the laptop's RAM; 8-vCPU D-series for CPU batches; 10 vCPUs per region (14 in westus3); no GPU quota | 0.82 x RAM | sign-up credit lapses 2026-11-23, hourly billing after; sizes, prices and the selection rule in gororoba-infrastructure `clouds/azure/README.md`; Singular 1.63 times slower than the laptop on one std (`forecasts/std13-bench/` under the A5 evidence) |
| GCP trial | 12 vCPU across all regions, no GPU, no Spot | 0.82 x RAM | 300 USD credit to 2027-01-30; e.g. one n2-highmem-8 (8 vCPU, 64 GB) |
| AWS free plan | 2 vCPU, 8 GiB largest eligible type (`m7i-flex.large`; `aws-avx512` host) | 6.6 GiB | 199.77 USD credit to 2027-04-24 |

The Kaggle CPU and GPU pools are independent, so up to five CPU sessions and two GPU sessions run at once, seven in
all.

## Open tasks by blocker

### Running now

| task | computation | host | state | falsifier |
|---|---|---|---|---|
| 120 | engine v13 (`slimgb` export) on VB, degree 7 at N = 21 and 22, both primes | Windows workstation laptop | done: r_21 = 609, r_22 = 624 at both primes (A5-286, A5-287) | passed |
| 120 (cross-check) | the same `slimgb` exports at N = 21 and 22, plus six variable rotations at N = 15 | Kaggle CPU, kernels `a5-vb-d7-slimgb-p32009` and `-p32029` | pushed before the runner exited 1 on failure: read `summary.json` (rc and RESULT lines) | a reduced basis whose sha256 differs from the laptop export |
| 75, 121 | X- check 2 over Q(i), the direct `quadric_lift.py` | Kaggle CPU, kernel `a5-char0-xm-quadrics` | stopped on the build host at 2:11; the direct computation never finished in 3 h before | a Q(i) relation space whose dimension or reduction differs from K2 mod p |
| 42 (X- degree 6) | X- ambient good reduction at N = 22, `truncation_check.py` | Kaggle CPU, kernel `a5-char0-xm-truncation-n22` | stopped on the build host at 2:11; even a pass does not prove the lower bound | a denominator divisible by p, or a basis differing from the header's |

Done since the scope was first written:
- 118 and 119: the `slimgb` ladder at N = 1 to 20 (A5-280), with a local `ds` ordering refuted (A5-285).
- 122 (ambient part only): W8 J + m^16 reduces well (A5-277); rank_Q(i) W_N = rank_F_p W_N remains untested.
- 56: the Iso planes sweep V(K2) at both primes (A5-284, pending review in task 133).
- 103: the wide-coset and Tuna claims, reviewed.

### Item-6 deliverables (plan `a5-kernel-attachments`)

| task | plan step | state | depends on |
|---|---|---|---|
| 126 | incidence census, real versus complex, all 33 incidences | doing | |
| 127 | limit sets 8 -> 12, 15 incidences, closed Gauss-graph fibers in Gr(4,6) with two-sided real certificates | todo | 126 |
| 128 | limit sets 12 -> 16 (8) and 8 -> 16 (10), from a two-approach path-dependence test | todo | 126; the exceptional-fiber supports of task 5 |
| 129 | compatibility of composed and direct limits | todo | 127, 128 |
| 130 | attaching maps with homotopy data | todo | 129 |
| 131 | ledger of questions not yet asked (program section 5) | standing | |

Roadmap item 7 assembles the attaching maps of task 130 as a homotopy colimit over the incidence poset. Item 8 compares
that model at n = 4 and n = 5. Neither can start on Hilbert functions alone, so item 6 stays open until tasks 126 to
130 hold replayed evidence.

### Ready, no blocker

| task | computation | host | estimate |
|---|---|---|---|
| 123 | linear-algebra export of k[t]/(J + m^N) at N = 15 | Kaggle CPU | unmeasured; compare against 420 s |
| 124 (for 37) | done: arcs through the point k = -9 of the contracted line of the slice parametrization are dense in the degree-3 component (`arcs-vb`, A5-016 proved at both primes) | | |
| 125 (for 110) | membership of the 91 degree-5 forms of E8-bar, by a sparse solver | laptop | unmeasured; the degree-2 receipt took 12,678 s |
| 115 | exact torus over Q in the Klein centralizer, then a weighted dp order | Kaggle CPU or the laptop | symbolic; the weighted std then runs at N = 15 and 18 |
| 133 | done by a second route: the arc family of `structure/arcs-iso-w8/blowup-arcs` decides A5-007 and A5-067 at both primes without the fiber-cone deduction | | |
| 132 | withdrawn: the fez qubit-90 channel admits every mapped marginal (second review of the wide-coset write-up); an independent calibration of qubit 90 replaces it | none | |
| 134 | byte-reproducible serializer for the Tuna-17 one-CZ null analysis, as a versioned successor | code change | regeneration drifts by at most 1.78e-14 today |
| variable-order screen | fixed dp permutations at N = 15 | Kaggle CPU sessions, one permutation each | about 420 s per permutation; reversed variables measured 1.81 times slower at N = 13 |
| `degBound` lever | `slimgb` with `degBound = N` at N = 18 | laptop, after the degree-7 cells | byte-identical basis and 12 percent faster at N = 13, 33.5 percent at N = 15 (Codex final review) |

### Blocked on a measurement

- 121, 75: if the direct Kaggle run does not finish, the canonical degree-bounded system for check 2 on X-, sized
  first from the maximum cofactor degree of the 32029 lift (277 MB of cofactor text).
- 122: W8 check 2 waits on the X- route. The per-degree lower bounds also wait on exact W_N rank comparisons or
  independent direct lower bounds. The all-degree statement waits on the flatness of K2 over Z[i]_(p), the
  affine-cone bridge and a transfer of A5-066.
- 42: its ambient-good-reduction computation is independent, but a characteristic-zero degree-6 conclusion also
  waits on the W_N rank equality and the degree-2 upper bound.
- 37: decided in favor by the dominant arc family onto V(P1) of `arcs-vb` (A5-016).

### Blocked on an engine change

- 113, W8 degree 6 at N = 19, an engine test (A5-066 already proves h_6 = 8,624): withdrawn on 2026-11-10 by the
  owner's decision (ledger row A5-291). Under v11 it needs 129 to 223 GiB and 18 to 27 h, beyond every substrate
  above, and its only output would be a check of the rank engine and the closing law. A later engine test would
  first need the multiplication matrix L streamed by degree, uint16 storage and engine v12's GPU echelon.

### Separate changes

- 106: gororoba-open follow-up (Rocq lemmas, an exact-rank test, a mutation arm).

## Questions for the owner

- The Azure credit (lapses 2026-11-23): no recommended route needs more than 52 GB. Its candidate use is an FX4 (84 GB)
  for a characteristic-0 check that hits Kaggle's 12-hour limit.
- The GCP credit (12 vCPU across regions, to 2027-01-30): independent CPU batches.
