# Final adversarial review: A_5 roadmap item 6, open tasks, and compute placement

[measured] I reviewed the two-commit range `d970b76f3..84276830f`, every artifact named by `brief-final.md`, the
canonical item-6 plan, the ledger rows cited by the scope document, the full engine-v13 diff against v12, and the live
outputs allowed by the brief. `git log --oneline d970b76f3..HEAD` returned `e97d7f285` and `84276830f`; live outputs
remain provisional unless a retained record binds them.

## Verdict and findings ranked by consequence

### 1. FATAL: the document that claims to list every open task omits the work that item 6 must deliver

[proved] The scope document says item 6 admits attaching maps on every admitted incidence, lists compatibility and
attaching maps among its four deliverables, and then claims to list every open task
(`docs/design/a5-open-tasks-and-compute-scope.md:3-17`). Its open-task section contains neither a compatibility task nor
an attaching-map task (`docs/design/a5-open-tasks-and-compute-scope.md:56-103`). The canonical JSON plan still marks
the 8-to-12 limit sets, both families into nullity 16, compatibility, and attaching maps `todo`
(`docs/state/plans/a5-kernel-attachments.json:28-58`). The claim that the listed tasks leave no gap is false.

[proved] The omitted surface is large rather than clerical. The working program requires two-sided semialgebraic
certificates for 15 incidences from nullity 8 to 12, eight from 12 to 16, and ten from 8 to 16; compatibility of direct
and composed limits; and link-to-limit-set and sphere-union attaching maps
(`docs/design/a5-kernel-attachments-program.md:33-48,73-82,154-165`). The program also calls its ledger of questions not
previously asked a standing deliverable (`docs/design/a5-kernel-attachments-program.md:84-98`), yet the scope document
does not count or place that work.

[proved] Roadmap item 7 consumes the actual attaching maps, assembles them as a homotopy colimit, and requires
chain-level compatibility with the sphere-bundle data; homology agreement alone is insufficient
(`docs/design/dimension32-global-topology-program.md:79-88`). Item 8 consumes item 7 at `n=5` and compares incidence
posets, attaching maps, and classes at `n=4` and `n=5` (`docs/design/dimension32-global-topology-program.md:90-96`).
Every item-6 output required by those consumers remains open, so the current compute campaign cannot admit item 6.

### 2. SERIOUS: the launchers can return success after failed children, and the degree-7 launcher exceeds its own host budget

[computed] The probe `sh -c '(exit 1)& wait'; echo $?` returned `0`; an `xargs -P` wrapper that wrote a child status and
then ended normally also returned `0`. Consequently bare `wait` in `run-cells-v13.sh` and three probe launchers loses
the failed child status (`docs/evidence/a5-exceptional-fibers/vb-d7/run-cells-v13.sh:14-31`,
`docs/evidence/a5-exceptional-fibers/vb-export-levers/run-probes.sh:7-19`,
`docs/evidence/a5-exceptional-fibers/vb-export-levers/run-laptop.sh:8-17`, and
`docs/evidence/a5-exceptional-fibers/vb-export-levers/ladder/run-ladder.sh:8-12`). Each child status is recorded, but the
top-level command still advertises success. `run-lifts.sh` correctly accumulates and returns failure
(`docs/evidence/a5-char0-transfer/cofactors/run-lifts.sh:7-16`). `sh -n` and `shellcheck -S error` passed all five
scripts; this defect is semantic.

[proved] `run-cells-v13.sh` says four 12 GiB cells fit the 52.5 GB laptop budget, then launches every argument without
enforcing a count (`docs/evidence/a5-exceptional-fibers/vb-d7/run-cells-v13.sh:2-5,14-30`). The prescribed invocation
launched five cells, whose declared maxima total 60 GiB, above the laptop budget
(`docs/design/a5-open-tasks-and-compute-scope.md:42-45`). The engine's preflight bounds one process only
(`docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v13.py:1048-1068`); it cannot enforce aggregate host
memory. The degree-5 cell has since exited, leaving four live cells, but a lucky completion does not repair the launcher.

### 3. SERIOUS: the W8 order-16 estimate quotes one substage as if it were the whole check

[measured] The scope document uses 114 seconds at order 13 to size W8 check 3
(`docs/design/a5-open-tasks-and-compute-scope.md:60-65`). The retained JSON reports 114.3 seconds for the Q(i) basis
substage, while `/usr/bin/time` reports 21:46.36 wall and 365288 KiB peak for the complete driver
(`docs/evidence/a5-char0-transfer/truncation-w8-nm-n13.json:1-12` and
`docs/evidence/a5-char0-transfer/logs/truncation-w8-nm-n13.time:1-10`). Ledger A5-277 correctly says 22 minutes
(`docs/evidence/a5-exceptional-fibers/ledger.tsv:276`). The order-16 process remained live when checked, so it supplies
no result or completion rate. Scheduling from 114 seconds understates the measured end-to-end cost by 11.4 times.

### 4. SERIOUS: engine v13 has a sound export change but no automated regression gate

[proved] The v12-to-v13 code diff changes the export producer from `std` to `slimgb`; v13 still fixes `dp`, enables
`redSB`, checks a recomputed quotient basis, binds published files by digest, checks every table basis, and aggregates
all worker failures before raising (`docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v13.py:350-365,630-720`).
No test or CI file references `fiber_rank_v13.py` or `run-cells-v13.sh` (`rg 'fiber_rank_v13|run-cells-v13' tests ci
.github` returned no match). Pinned ruff 0.17.4 and mypy 2.4.1 both returned success.

[measured] The permitted laptop validation returned order 15 quotient dimension 6105, rank 255, block ranks
75/50/65/65, total 414.1 seconds, wall 416.17 seconds, and peak 352232 KiB. Those values match the retained degree-5
prediction (`docs/design/a5-vb-degree7-and-w8-char0-plan.md:14-24`). Four order-21/order-22 cells remain live and their
zero-byte `.json.part` files establish no degree-7 result.

## `slimgb` from first principles

[proved] A reduced Groebner basis over a field is unique after the global monomial order is fixed: each leading
monomial is a minimal generator of the initial ideal, and each monic tail is the unique normal-form representative
modulo the other leading monomials. Engine v13 fixes `dp` and requests `redSB`, so replacing the algorithm can preserve
the canonical reduced basis (`fiber_rank_v13.py:350-365`). Singular 4.4.1 help for `slimgb` states that the basering
order must be global, the algorithm keeps polynomials short with small coefficients, `redSB` returns a reduced basis,
and `prot` reports progress (`Singular -q --no-rc -c 'help slimgb;' < /dev/null`).

[hypothesis] In `J+m^N`, the monomial ideal contributes a large degree-`N` frontier while inhomogeneous generators of
`J` repeatedly expose lower tails under reduction (`docs/design/a5-vb-degree7-and-w8-char0-plan.md:46-49`).
Brickenstein's slim-basis algorithm selects pairs by polynomial and weighted length and balances reductions by length;
that mechanism suppresses intermediate support and coefficient growth on this frontier. The explanation fits the VB
measurements but is workload-specific: `slimgb` was 4.4 times slower than `std` on X-minus membership
(`docs/runbooks/compute-flags.md:271`).

| Lever | Evidence and consequence |
|---|---|
| `prot` | [proved] Singular help says it prints progress and pair/reduction diagnostics; it changes observability, not the mathematical result. |
| `redTail` / `redSB` | [proved] Help says `redTail` may improve or worsen time and memory and does not guarantee a reduced result; `redSB` does. |
| weighted length / `weightM` | [proved] The slim algorithm uses its length heuristics; Singular help says `weightM` computes weights for weighted ecart and sugar. A weighted ordering still requires the exact torus and positive-weight homogeneity test of task 115 (`a5-vb-degree7-and-w8-char0-plan.md:85-86`). |
| `degBound` | [proved] Singular help applies it to `std` and `slimgb`; `slimgb` interprets it as total degree with unit weights. A prior `J+m^N` test saved 8 percent with an identical basis (`docs/runbooks/compute-flags.md:280`). |
| `groebner` | [proved] `help groebner` lists direct `std`/`slimgb` and conversion `hilb`/`fglm`, reports its choice under `prot`, and recommends calibration on a simplified hard example. |
| `modStd` | [proved] `/usr/share/singular/LIB/modstd.lib:34-51` limits it to rational coefficients and says an inhomogeneous global result is only high probability unless separately certified; it does not replace exact Q(i) checks. |
| `parallel.lib` | [proved] `/usr/share/singular/LIB/parallel.lib:169-181` dispatches a list of independent jobs. It does not parallelize one `std` or `slimgb`; the repository reaches the same conclusion (`docs/runbooks/compute-flags.md:149-182`). |
| variable order | [proved] The global `dp` order includes the declared variable order, so a permutation can change pair growth and cost. A promoted permutation must map exported tables back to canonical variables (`a5-vb-degree7-and-w8-char0-plan.md:79-83`). |

[measured] One-at-a-time laptop runs under a 900-second deadline produced the following provisional measurements. All
completed rows returned status 0 and 3627 standard monomials at order 13; fixed-order rows returned the same reduced
basis bytes, while reversed variables returned its own reduced basis. Concurrent session jobs make absolute wall times
load-sensitive.

| Order and method | Wall | Peak RSS | Relative result |
|---|---:|---:|---|
| [measured] N=13 `slimgb` baseline | 54.83 s | 224892 KiB | reference |
| [measured] N=13 `std` baseline | 200.61 s | 45796 KiB | 3.66 times slower |
| [measured] N=13 `slimgb`, no `redTail` | 55.88 s | 224624 KiB | 1.9 percent slower |
| [measured] N=13 `slimgb`, `degBound=13` | 48.26 s | 224532 KiB | 12.0 percent faster |
| [measured] N=13 default `groebner` | 173.02 s | 46032 KiB | 3.16 times slower |
| [measured] N=13 `std` with `option(length)` | 279.08 s | 46128 KiB | 39.1 percent slower than `std` |
| [measured] N=13 `slimgb`, reversed variables | 99.13 s | 343592 KiB | 1.81 times slower; 1236 basis elements / 3627 monomials |
| [measured] N=14 `slimgb` / `std` | 150.76 / 534.67 s | 283728 / 64180 KiB | same sizes: 1514 / 4746 |
| [measured] N=15 `slimgb` / `std` | 339.18 / 1313.06 s | 351620 / 87228 KiB | same sizes: 1797 / 6105; `std` 3.87 times slower |
| [measured] N=15 `slimgb`, `degBound=15` | 225.65 s | 352632 KiB | 33.5 percent faster; basis and kbase byte-identical |

## Tool suitability by computation class

[measured] The inventory command found Singular 4.4.1, msolve 0.11.0, FLINT 3.6.0, python-flint 0.9.0, M4RI,
M4RIE, FFLAS-FFPACK 2.5.0, LinBox 1.7.1, Macaulay2 1.26.06, Giac 2.1.0, CuPy 14.2.0, and torch 2.15.0; CoCoA and
openF4 were absent (`pacman -Q ...`, `M2 --version`, `command -v ...`, and Python imports).

| Class | Verdict grounded in a rate |
|---|---|
| Truncated standard basis | [measured] Singular `slimgb` with `degBound=N` is the current VB winner: 48.26 versus 54.83 seconds at N=13 and 225.65 versus 339.18 seconds at N=15, with identical reduced bases. msolve is refuted for this shape: at N=7..9 it took 5-6 times longer and grew to 6.24 GB, then its N=11 run hit 20 GiB (`compute-flags.md:281`). |
| Rank closure | [measured] FLINT remains the CPU oracle; exact GPU RREF matches FLINT and takes 2.1 versus 19.9 seconds on a 2000-by-15037 rank-1800 matrix (`engine-v12/gpu-rref-probe/README.md:3-16`). The GPU belongs where closure dominates, not in VB's export-bound cells (`docs/design/gpu-exact-modular-linear-algebra.md:211-242`). |
| Membership | [measured] Singular `std` with `redSB` remains the calibrated producer: X-minus degree 3 took 415.8 seconds, while `slimgb` took 1836.9 seconds with identical normal forms (`compute-flags.md:271`). FLINT/GPU may accelerate the resulting exact rank, not construct the standard basis. |
| Check 2 | [proved] Canonical RREF and reconstruction fit FLINT, FFLAS-FFPACK, LinBox, or the exact GPU PLUQ; the final Q(i) identities remain mandatory (`a5-vb-degree7-and-w8-char0-plan.md:137-152`). `pacman -Qi m4ri m4rie` identifies them as F_2 and F_(2^e) libraries, so they do not represent primes 32009/32029 or Q(i). |
| Saturation | [measured] Singular's homogenized variable saturation is the only calibrated route: 272 seconds versus 3022 seconds for `sat_with_exp` on the Iso slice (`compute-flags.md:285`). Full pivot saturation reached 9.4 GB at 12 hours and 72 GB at 10 hours (`compute-flags.md:270`), so solver substitution without a transverse formulation merely changes how the run stalls. |
| Q(i) checks | [proved] Singular global-order exact arithmetic is the retained producer. `modStd` is a Q-only probabilistic shortcut on inhomogeneous global input; M4RI/M4RIE and modular GPU kernels cannot certify Q(i). Macaulay2, Giac, CoCoA, and openF4 remain candidates only after byte- or leading-ideal comparison; the program records a Giac 30-minute timeout and an msolve memory failure (`a5-kernel-attachments-program.md:328-331`). |

[proved] FFLAS-FFPACK/LinBox, FLINT, CuPy, and torch therefore falsify the blanket claim that Singular is the best tool
for every class. They do not falsify Singular for the sparse Groebner, saturation, and Q(i) producer classes.

## Placement of every listed open task

[proved] Host budgets are laptop 52.5 GB plus 13.4 GiB GPU, build host 38.6 GiB plus 10.1 GiB GPU, `lab-a1` 9.5
GiB, five independent 30 GB Kaggle CPU sessions, two independent Kaggle GPU sessions, Azure FX4 84 GB, GCP up to 12
vCPU, and AWS 2 vCPU/6.6 GiB job RAM (`a5-open-tasks-and-compute-scope.md:40-54`).

| Task | Cores, RAM, GPU, placement, estimate, tandem |
|---|---|
| 118/119 VB lever ladder | [measured] One core and below 0.36 GiB per measured N=13..15 cell, no GPU; laptop. N=13..15 `slimgb` took 55, 151, 339 s. Run only after the four degree-7 cells, or use one Kaggle CPU session per independent variant. |
| 120 VB degree 7 | [hypothesis] One core per Singular export, four Python workers, at most 12 GiB, no useful GPU; four laptop cells are live. Dividing the retained `std` extrapolations by the observed 1.7-1.9 pilot factor gives N=21 about 2.3-5.0 h and N=22 about 3.3-14.6 h (`a5-vb-degree7-and-w8-char0-plan.md:41-44,71-75`). Do not add a fifth laptop cell. |
| 122 W8 check 3 | [measured] One core, 0.36 GiB at N=13, no GPU; build host, live at N=16 under 12 GiB/3 h. The only defensible complete-driver rate is 21.8 min at N=13, so completion by 3 h is a hypothesis. It runs beside laptop and `lab-a1`. |
| 103 retained-provider claims | [proved] No new compute is authorized or needed; one core and below 1 GiB for record reconciliation in its own worktree. The brief contains no measured review rate, so an elapsed estimate would be invented (`a5-open-tasks-and-compute-scope.md:65`). |
| 123 truncated linear-algebra export | [hypothesis] Start one 4-core, 12 GiB CPU pilot on build host after W8; 900-second deadline against the measured 420-second N=15 Singular baseline (`a5-vb-degree7-and-w8-char0-plan.md:87-90`). Move the exact rank to a Kaggle GPU only if the exported sparse matrix dominates. |
| 124 and task 37 jet arcs | [measured] One core, at most 8 GiB, no GPU; `lab-a1`, then build host. Chart-t7 normalization took 451 s, so two initial loci get a 20-minute serial envelope (`a5-open-tasks-and-compute-scope.md:72,85-86`). They run beside laptop/build-host heavy jobs. |
| 125 for task 110 sparse membership | [hypothesis] Up to 8 cores, 12 GiB, no GPU for basis production; laptop after degree 7 or one Kaggle CPU session. Degree 2 took 12678 s, so 91 degree-5 forms need a solver-sizing pilot with a 3.5-hour ceiling, not a linear extrapolation (`a5-open-tasks-and-compute-scope.md:73`). |
| 115 exact torus/weighted order | [hypothesis] One core, below 8 GiB, no GPU; build host after W8. Give the exact torus a 15-minute pilot, then N=15 about 7-10 minutes per ordering and N=18 only for a winner (`a5-vb-degree7-and-w8-char0-plan.md:33-44,85-86`). |
| 56 Iso point-blowup plane | [measured] One core, below 1 GiB, no GPU; `lab-a1`. An analogous W8 plane took 45-52 s and 26 MiB, so two primes receive 3 minutes plus setup (`a5-open-tasks-and-compute-scope.md:75`). |
| variable-order screen | [hypothesis] One core and below 2 GiB per permutation, no GPU; use five Kaggle CPU sessions after the fixed N=13 screen, one permutation each. At the 420-second retained N=15 rate, ten permutations finish in about 14 minutes over two waves (`a5-open-tasks-and-compute-scope.md:76`). |
| 121/75 check-2 sizing | [hypothesis] One 8-core, 12 GiB process on laptop or one Kaggle CPU session; GPU RREF only after the 277 MB cofactor corpus determines matrix dimensions. Allow 15 minutes for sizing; the subsequent solve has no evidence-based estimate (`a5-open-tasks-and-compute-scope.md:80-83`; `a5-vb-degree7-and-w8-char0-plan.md:124-147`). |
| 42 W8 characteristic zero | [proved] No independent process exists: it waits for N=16 check 3 and canonical check 2. The all-degree promotion additionally waits for the flatness, affine-cone, cycle, and A5-066-transfer arguments (`a5-vb-degree7-and-w8-char0-plan.md:154-180`). |
| 113 W8 degree-6 engine test | [measured] The v11 route needs 129-223 GiB and 18-27 h, so every listed CPU host is refuted (`a5-open-tasks-and-compute-scope.md:88-92`). After streamed-by-degree tables and compact storage, place closure on laptop RTX 4090 or two Kaggle T4s; GPU timing remains unmeasured for this matrix. |
| 106 gororoba-open follow-up | [proved] This separate repository needs Rocq lemmas, an exact-rank test, and a mutation arm (`a5-open-tasks-and-compute-scope.md:94-97`). The current repository supplies no timing or memory record, so placement beyond a light AWS 2-vCPU replay is unearned. |

[proved] The table still cannot place compatibility, attaching maps, or the standing-question ledger because the scope
document created no tasks for them. The canonical plan, not more hardware, must supply their atomic work and acceptance
criteria first.

## Soonest truthful schedule

[hypothesis] The shortest evidence-bound critical path is: (1) leave the four laptop degree-7 cells and build-host W8
order-16 check undisturbed; (2) run tasks 124 then 56 serially on `lab-a1`; (3) use five Kaggle CPU sessions for fixed
variable-order candidates, the sparse-export pilot, and check-2 sizing, while two Kaggle GPU sessions calibrate exact
RREF/PLUQ on exported check-2 matrices; (4) after W8, use the build host for task 115 and exact Q(i) identity blocks; (5)
use the laptop GPU for task 113 only after the streaming engine exists. This exploits all seven independent Kaggle
sessions without pretending they share memory (`a5-open-tasks-and-compute-scope.md:47-54`).

[hypothesis] Azure's 84 GB FX4 is the paid option for a memory-heavy saturation or a degree-7 cell that exceeds 12 h;
its credit lapses 2026-11-23 and measured Singular speed is 1.6 times slower than the laptop. GCP's 12-vCPU/300 USD
trial fits three independent one-core or four-core screens, not one faster `slimgb`. AWS's 2-vCPU/8 GiB free-plan host
fits certificate replays and Rocq, not task 113 or the 16.5 GB lift (`a5-open-tasks-and-compute-scope.md:49-51`). Paid
cloud requires an owner-approved written case; these are placements, not launches.

## Foundations and real blockers

| Task or claim | Missing foundation; blocker verdict |
|---|---|
| Item-6 admission | [proved] Missing theorem/computation: all four canonical deliverables and the standing-question ledger. This is the governing blocker (`a5-kernel-attachments-program.md:73-98`). |
| 118/119 and 120 | [measured] Missing measurement: retained N=18 equivalence and completed degree-7 cells. The engine mechanism is present; a theorem is not the blocker. |
| 122/75/42 | [proved] Check 3 lacks the N=16 measurement; check 2 lacks matrix sizing, a canonical solve, reconstruction bounds, and exact Q(i) identities. The all-degree claim lacks the flatness/affine-cone/cycle/A5-066 chain (`a5-vb-degree7-and-w8-char0-plan.md:124-180`). These are real blockers, but the scope document improperly merges running check 3 with blocked check 2 under task 122. |
| 37 | [proved] The `blocked` label is false as an execution statement: task 124 is ready and its second independent falsifier, degree-7 rank, is running (`a5-open-tasks-and-compute-scope.md:71-76,85-86`). The scientific claim remains undecided. |
| 123/125 | [proved] Missing measurement and algorithm calibration, respectively; neither is blocked on new mathematics (`a5-vb-degree7-and-w8-char0-plan.md:87-90`; `a5-open-tasks-and-compute-scope.md:71-74`). |
| 115 | [proved] Missing exact torus and positive-weight homogeneity argument precede the timing measurement (`a5-vb-degree7-and-w8-char0-plan.md:85-86`). This is a real foundation dependency. |
| 56 | [proved] No listed blocker remains; the measured W8 pilot supplies a bounded next probe (`a5-open-tasks-and-compute-scope.md:75`). |
| 113 | [proved] Streaming `L` by degree, compact storage, and GPU echelon are genuine engine changes; the existing RAM lower bound excludes every current CPU substrate (`a5-open-tasks-and-compute-scope.md:88-92`). |
| 103/106 | [proved] These are separate repository/document changes, not blockers on the item-6 computation graph (`a5-open-tasks-and-compute-scope.md:65,94-97`). |

## Ledger and record reconciliation

| Rows | Reconciliation |
|---|---|
| A5-010, A5-061, A5-062, A5-066 | [proved] Their `proved` status is finite-field structure at the two split primes; none proves a Q(i) transfer (`ledger.tsv:11,62-66`). |
| A5-138 through A5-149 | [proved] The modular Hilbert values match their retained lower/upper bounds. A5-143 and A5-149 inherit degree 6 from A5-066; a direct degree-6 rank remains only an engine test (`ledger.tsv:137-149`). |
| A5-247 | [proved] It establishes good reduction of `J` and `G`, explicitly only transfer check 1 (`ledger.tsv:246`). |
| A5-248 | [proved] `stalled` is correct; it records the three-hour Q(i) failure, the 1565-second/16.5 GB modular lift, and noncanonical cofactors (`ledger.tsv:247`). |
| A5-249 | [proved] `survives` through X-minus degrees 1-5 is correct; order 22/degree 6 remains untested (`ledger.tsv:248`). |
| A5-258 | [proved] `open` is correct; weighted export is untested (`ledger.tsv:257`). |
| A5-260 and A5-269 | [proved] `survives` is correct through measured degrees 4-6; degree 7 remains a preregistered test (`ledger.tsv:259,268`). |
| A5-277 | [proved] The row correctly says W8 orders 16 and 19 were not run when retained; the scope's “running” text is live state, not a result (`ledger.tsv:276`). |
| A5-279 | [proved] `stalled` remains correct for engine v11; live v13 cells have not produced degree-7 JSON (`ledger.tsv:278`). |

## Steelman

[proved] The revised plan repaired the first review's invalid one-root Gaussian bound, noncanonical cofactor-support
criterion, omitted W8 order-16 dependency, and `run-lifts.sh` failure handling
(`docs/archive/reviews/a5-vb7-w8-char0/README.md:9-18`). It preregisters four independently falsifiable degree-7
predictions, keeps exact global orderings, separates per-degree transfer from all-degree geometry, and versions the
changed export producer. Engine v13's completed degree-5 validation supports the narrow claim that `slimgb` preserved
the known rank on one cell. The plan is a useful compute campaign; it is not a complete item-6 roadmap.

## Owner decisions

1. [hypothesis] **Repair the item-6 task graph.** Option A: add atomic tasks for all 33 incidence certificates,
   compatibility, attaching maps, and the standing-question ledger before treating the scope as canonical; estimate:
   planning plus bounded first probes, 1-2 engineering days, with the full mathematics unestimated. Option B: rename
   the document as a compute-campaign subset and make no completeness claim; estimate: under 1 hour. Recommendation:
   choose A because items 7 and 8 consume the omitted outputs.
2. [hypothesis] **Repair all four failure-propagation paths and cap the degree-7 launcher.** Option A: collect each PID,
   wait for each, return aggregate failure, and reject arguments whose declared memory exceeds 52.5 GB; estimate: 2-4
   hours including deterministic failing-child tests. Option B: require manual inspection of `.status` files; estimate:
   no code time but an unreliable automation boundary. Recommendation: choose A before another launch.
3. [hypothesis] **Adopt `slimgb` plus a bounded degree test only after retained validation.** Option A: retain N=18 basis,
   kbase, table, generator, rank, version, and resource equivalence; estimate: the running lever campaign's measured
   hours. Option B: promote the N=13/N=15 pilot directly; estimate: immediate, with unbounded regression risk.
   Recommendation: choose A; test `degBound` at N=18 because its byte-identical N=13 and N=15 pilots saved 12.0 and
   33.5 percent.
4. [hypothesis] **Treat W8 check 3 as a complete-driver job.** Option A: let the live N=16 process reach its 3-hour
   deadline and record total wall, peak, result, and per-stage times; estimate: at most the current deadline. Option B:
   extrapolate from the 114-second substage; estimate: falsely optimistic by 11.4 times at N=13. Recommendation: A.
5. [hypothesis] **Use free concurrency before paid credit.** Option A: the `lab-a1`/five-Kaggle-CPU/two-Kaggle-GPU
   schedule above; estimate: first calibrated probes within one 12-hour Kaggle window. Option B: approve Azure before
   its 2026-11-23 lapse for a named >30 GB or >12 h case; GCP for independent CPU batches; AWS only for light replays.
   Recommendation: A now, then Azure only for a measured case that fails the free limits.
6. [proved] **Keep roadmap item 6 open.** Option A: admit it from the present VB/W8 computations; the admission criterion
   fails because attaching maps and compatibility remain todo. Option B: keep it open until the canonical plan's four
   deliverables have replayed evidence and chain-level consumers. Recommendation: B
   (`dimension32-global-topology-program.md:79-96`; `a5-kernel-attachments.json:28-58`).
