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
- check 3 at X- N = 22 (A5-249);
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
| Azure trial | `Standard_FX4mds_v2`, 4 vCPU, 84 GB; one per region under a 4-vCPU regional cap | 0.82 x RAM | 200 USD credit, expires 2026-11-23; Singular 1.6 times slower than the laptop |
| GCP trial | 12 vCPU across all regions, no GPU, no Spot | 0.82 x RAM | 300 USD credit to 2027-01-30; e.g. one n2-highmem-8 (8 vCPU, 64 GB) |
| AWS free plan | 2 vCPU, 8 GiB largest eligible type (`m7i-flex.large`; `aws-avx512` host) | 6.6 GiB | 199.77 USD credit to 2027-04-24 |

The Kaggle CPU and GPU pools are independent, so up to five CPU sessions and two GPU sessions run at once, seven in
all.

## Open tasks by blocker

### Running now

| task | computation | host | measured basis | falsifier |
|---|---|---|---|---|
| 118, 119 | `slimgb` against `std` for J + m^N, VB at p = 32009, N = 1 to 20 | laptop (`vbladder`, `vblevers`) | N = 13: same s bytes, kbase and tables, 66 s against 112 s; N = 15: 301 s against 562 s | a basis, kbase or table that differs, or a lost speedup at N = 18 to 20 |
| 120 | engine v13 (`slimgb` export) on VB: the degree-5 validation at N = 15 passed (r = 255, blocks 75/50/65/65, 416 s); degree 7 at N = 21 and 22 at both primes | laptop (`vbd7`, deadline 24 h) | `std` at N = 22 extrapolated to 22,300 to 89,300 s ([plan](a5-vb-degree7-and-w8-char0-plan.md#where-the-time-goes-measured)), divided by the measured `slimgb` factor, which depends on host and load (2.9 to 3.9 on the laptop at N = 13 to 18, A5-280): an extrapolation | r_21 not 609, r_21 = 624, split not 7/8/0/0, r_22 below 624, or a degree-5 rank that differs from the record |
| 122 | W8 check 3 at N = 16 over Q(i) | build host | N = 13 took 21:46 wall for the whole driver (114 s of it the Q(i) basis), 0.36 GiB | a denominator divisible by p, or a basis differing from the header's |
| 103 | claims for the IBM 64D/128D wide-coset and Tuna 6-CZ acquisitions, and their implications for the Cayley-Dickson tower | own worktree, branch `claims/ibm-wide-coset-and-tuna-6cz` | | a claim citing a statistic no record holds |

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
| 123 | linear-algebra export of k[t]/(J + m^N) at N = 15 | build host | unmeasured; compare against 420 s |
| 124 (for 37) | jet-parameter arcs at the plane t1 = 0 and the apex of chart t7 | `lab-a1` or build host | chart t7 normalization took 451 s |
| 125 (for 110) | membership of the 91 degree-5 forms of E8-bar, by a sparse solver | laptop | unmeasured; the degree-2 receipt took 12,678 s |
| 115 | exact torus over Q in the Klein centralizer, then a weighted dp order | build host | symbolic; the weighted std then runs at N = 15 and 18 |
| 56 | Iso point-blowup plane pilot modeled on the W8 C30 certificate | `lab-a1` | one W8 plane took 45 to 52 s and 26 MiB |
| variable-order screen | fixed dp permutations at N = 15 | Kaggle CPU sessions, one permutation each | about 420 s per permutation; reversed variables measured 1.81 times slower at N = 13 |
| `degBound` lever | `slimgb` with `degBound = N` at N = 18 | laptop, after the degree-7 cells | byte-identical basis and 12 percent faster at N = 13, 33.5 percent at N = 15 (Codex final review) |

### Blocked on a measurement

- 121, 75: the canonical degree-bounded system for check 2 on X-. It needs a sizing of its unknowns first, from the
  maximum cofactor degree of the 32029 lift (277 MB of cofactor text).
- 122: W8 check 2 waits on 121's route. The all-degree statement waits on the flatness of K2 over Z[i]_(p), the
  affine-cone bridge and a transfer of A5-066.
- 42: waits on 75 and 122.
- 37: decided in favor only by a dominant arc family onto V(P1) (124). It is decided against by a degree >= 7 element
  of L outside I(V(P1)), which the degree-7 rank exposes if r_22 < 624 (120).

### Blocked on an engine change

- 113, W8 degree 6 at N = 19, an engine test (A5-066 already proves h_6 = 8,624). Under v11 it needs 129 to 223 GiB
  and 18 to 27 h, beyond every substrate above. It runs after the multiplication matrix L streams by degree, which
  removes the 103 GiB residency, together with uint16 storage and engine v12's GPU echelon.

### Separate changes

- 106: gororoba-open follow-up (Rocq lemmas, an exact-rank test, a mutation arm).

## Questions for the owner

- Which paid-credit runs to place:
  - the Azure credit, which lapses on 2026-11-23;
  - the GCP credit, with its 12-vCPU cap.
- Whether to duplicate the laptop's degree-7 cells on Kaggle CPU sessions as a cross-host check.
