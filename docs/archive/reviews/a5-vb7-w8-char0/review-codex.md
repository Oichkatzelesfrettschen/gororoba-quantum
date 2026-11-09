# Adversarial review: VB degree 7 and W8 characteristic-zero transfer

Artifact: `git diff d970b76f3...HEAD`, the cited records, the named ledger rows, the transfer proposition, and engine v11.
Field: computational commutative algebra, specialization, exact replay identity, and bounded-compute planning.
Evidence visibility: committed records support retained claims; ignored and untracked live outputs support only provisional observations.

## Verdict

The plan is not safe to execute as written. Two proposed certificates are mathematically invalid, the W8 degree-5
decision omits a required check, and both launchers can print success after a failed or stalled Singular process. The
finite-degree transfer proposition itself is sound. The owner should run a retained order-18 lever comparison before
authorizing an order-21 cell.

## Findings ranked by consequence

### 1. Critical: the Gaussian multi-modular identity criterion is false

The plan applies the integer rule `M > 2B` after evaluating `i` at one root modulo each split prime
(`docs/design/a5-vb-degree7-and-w8-char0-plan.md:120-124`). A congruence at `i -> r` gives divisibility by the Gaussian
prime `(p, i-r)`, not by the rational integer `p` in both coefficient components. The product ideal has norm `M`, so
a nonzero element can have complex absolute value about `sqrt(M)`.

A one-prime counterexample already fires. The Gaussian integer `128 + 125i` has norm
`128^2 + 125^2 = 32009`, and the command
`(128 + 125*10754) % 32009` returned `0`. Its absolute value is `sqrt(32009) < 179`, while
`32009 > 2*179`. The coefficient is nonzero despite satisfying the plan's test. Claim 4 is refuted.

The repair must either check both conjugate roots at every rational prime, making `p` divide both integer components,
or prove a Gaussian norm bound and require a modulus product above the square of the coefficient bound. The current
alternate endpoint supplies no certificate.

### 2. Critical: equal cofactor support cannot certify a characteristic-zero lift

Singular computes `matrix T=lift(Q,Rel)` without a canonical solution rule
(`docs/evidence/a5-char0-transfer/cofactors/lift-cofactors.sing.in:11-16`). The plan treats equal nonzero positions at
two primes as evidence that both matrices reduce from one computation over `Q(i)`
(`docs/design/a5-vb-degree7-and-w8-char0-plan.md:114-119`). Equal positions supply neither compatible coefficients nor
a reconstruction bound, and a nonzero numerator can vanish at one good prime, so differing positions do not disprove
a common characteristic-zero solution. Ledger row A5-248 already states that the cofactors are noncanonical
(`docs/evidence/a5-exceptional-fibers/ledger.tsv:247`). Claim 5 and the proposed canonicality decision are refuted.

The sound endpoint is a canonical degree-bounded linear system with a fixed pivot convention, rational reconstruction,
and an exact identity over `Q(i)`. Support comparison can remain a diagnostic only.

### 3. High: W8 degree 5 still needs transfer check 3

The plan's status table says W8 check 3 survives only at closing orders 4, 7, 10, and 13 and leaves order 16 pending
(`docs/design/a5-vb-degree7-and-w8-char0-plan.md:99-103`). Ledger A5-277 confirms that order 16 has not run
(`docs/evidence/a5-exceptional-fibers/ledger.tsv:276`). The owner decision nevertheless says degrees 1 through 5 need
check 2 only (`docs/design/a5-vb-degree7-and-w8-char0-plan.md:141-145`). Degrees 1 through 4 need only check 2; degree 5
needs checks 2 and 3. Radicality remains separate from every per-degree transfer.

### 4. High: both launchers can announce completion without a valid result

`run-lifts.sh` converts every nonzero `systemd-run` status to success with `|| true` and then prints `lifts done`
(`docs/evidence/a5-char0-transfer/cofactors/run-lifts.sh:6-10`). `run-probes.sh` backgrounds four independent CPU jobs,
uses an unqualified `wait`, and prints `probes done` without recording every child status
(`docs/evidence/a5-exceptional-fibers/vb-export-levers/run-probes.sh:6-13`). Both commands leave Singular stdin open.
Singular 4.4.1 can wait until timeout when stdin remains open (`docs/runbooks/compute-flags.md:29-33`). The probe loop
also bypasses the required `parallel.py` mapping (`AGENTS.md:47-50`). A timeout, memory kill, or algebra failure can
therefore acquire an apparent successful terminal message. `sh -n` and `shellcheck -S error` pass because the defects
are semantic.

### 5. Medium: the measured standard-basis share is 94.528 to 98.648 percent, not 99 percent

The command that divided `export.computed_seconds["s.txt"]` by `seconds.total` for every retained JSON under
`vb-d6-laptop/` returned 94.750, 94.528, 96.066, 96.995, 97.798, 98.648, 98.523, 98.372, and 98.107 percent. The
standard basis dominates every retained cell, but the blanket measured claim at
`docs/design/a5-vb-degree7-and-w8-char0-plan.md:26-43` overstates the evidence. Claim 1 is refuted as written.

### 6. Medium: the plan promotes live scratch measurements into committed prose

The order-15 lever values at `docs/design/a5-vb-degree7-and-w8-char0-plan.md:57-65` come from ignored logs and
untracked `.time` and `.kbase` files. `git status --short` during the audit listed those files and the cofactor timing
outputs as untracked. The committed branch contains neither a bound receipt nor a digest ledger for those values.
The observed values can size a next test, but the plan must label them provisional until retention binds inputs,
versions, output hashes, statuses, and resource conditions.

### 7. Medium: the all-degree W8 argument omits the affine-cone bridge

The proposed monic, constant-leading-ideal Groebner basis would make each graded piece free over the localized
`Z[i]` base. `Proj` would then be flat, proper, and finitely presented. Because the finite residue field is perfect,
radicality of its finite-type fiber gives geometric reducedness. The standard EGA IV_3 openness results cited as
12.1.6 and 12.2.4 can then carry geometric reducedness and Cohen-Macaulayness from the closed fiber to the generic
point of the local base, provided the cited theorem numbers and hypotheses are checked against a source copy.

Reduced `Proj` alone does not state that the homogeneous affine cone is reduced. The missing argument is that the
positive-dimensional standard graded generic quotient is Cohen-Macaulay, hence has no finite-length
`H^0_m`; any nilradical supported only at the irrelevant ideal would lie in that module and must vanish. The plan must
write that bridge before replacing a direct radicality test. The degree 20/30 dichotomy also needs an explicit
specialization-of-effective-cycles argument: reduced special components occur with multiplicity one, so a generic
component can specialize to degree 20, degree 30, or their union of degree 50, and distinct generic components cannot
reuse a special component. Status: hypothesis with a plausible proof route, not a proved transfer.

### 8. Medium: the W8 cost basis is internally inconsistent

The plan scales from an unexplained 5,619-second W8 value and an 18-second X pilot
(`docs/design/a5-vb-degree7-and-w8-char0-plan.md:109-115,143-145`). The retained receipts instead record product and
standard-basis stages of 6,559.564 seconds at 32009 and 9,860.33 seconds at 32029, with membership stages of 325.071
and 575.423 seconds (`working/distribute/out/a5-w8-receipt-p1/w8_p1/d2/receipt-d2.json:28-48` and
`working/distribute/out/a5-p2-w8/w8_p2/d2/receipt-d2.json:28-48`). They also record 53,584 columns and about 2.637
million nonzeros in lines 7-10 of those receipts. Even the plan's favorable
`1565*(5619/18)` scale is 135.706 hours per prime, so it does not size a three-hour W8 lift.

## Claims under review

| Claim | Verdict | Evidence |
|---|---|---|
| 1. `std` is 99 percent of a VB cell | Refuted, measured | Retained range is 94.528 to 98.648 percent; `std` still dominates. |
| 2. Order 21 tests three of four degree-7 predictions | Supported, argued | Order 21 can refute `r_21=609`, closure exactly at 22 by reaching 624 early, and the 7/8/0/0 split; only `r_22=624` requires order 22 (`a5-vb-degree7-and-w8-char0-plan.md:17-24`). It cannot certify closure at 22 by itself. |
| 3. Per-degree transfer needs checks 2 and 3, while radicality is all-degree | Proved as dependency; plan application false | The proposition uses rank specialization only and expressly separates radicality (`docs/notes/topics/a5-char0-and-kernel-limits.md:56-67`). Order 16 check 3 is missing. |
| 4. Product above `2B` proves a Gaussian identity | Refuted | `128+125i` supplies a concrete counterexample at 32009 and the chosen root. |
| 5. Equal supports prove a common `Q(i)` cofactor computation | Refuted | `lift` is noncanonical and support carries no coefficient compatibility or bound. |

## Audit dimensions

1. **Finite-degree mathematics.** Check 2 is an upper bound because the generic relation-multiple matrix has rank at
   least its special-fiber rank. Check 3 is a lower bound because a nonzero modular minor remains nonzero generically.
   The bounds meet when the modular rank equals the modular Hilbert value
   (`docs/notes/topics/a5-char0-and-kernel-limits.md:56-64`). Radicality does not enter.
2. **All-degree W8.** Flatness, finite presentation, properness, geometric reducedness, Cohen-Macaulayness, affine-cone
   radicality, and effective-cycle specialization require the chain stated in finding 7. The plan has not completed
   that chain or transferred the A5-066 containment argument (`a5-vb-degree7-and-w8-char0-plan.md:126-139`).
3. **Costs.** Means from retained standard-basis times are 423.6, 676.4, 2,591.3, 7,204.6, and 10,556.55 seconds at
   orders 15, 16, 18, 19, and 20. Step ratios are 1.597, 1.957 per step, 2.780, and 1.465. Min/max bracketing gives
   order 21 at 15,468 to 29,350 seconds and order 22 at 22,665 to 81,603 seconds. A 10,000-second target requires a
   2.27 to 8.16 times speedup at order 18. Status: computed extrapolation, not measurement.
4. **Falsifiers and mutation arms.** The four degree-7 predictions, bad-reduction checks, corrupted-coefficient arms,
   engine file hashes, and rank-equivalence checks can fire. The Gaussian `2B` arm and equal-support decision cannot
   establish their claims. Order 21 can falsify three predictions but can confirm neither order-22 closure nor the
   target value. Launcher terminal messages are not verdicts until child statuses propagate.
5. **Engine identity.** Engine v11 keys an export by prime, variable order, order `N`, and `J` and `G` digests
   (`fiber_rank_v11.py:527-534`) and binds each export file by SHA-256 (`fiber_rank_v11.py:618-652,747-754`). A changed
   Singular producer belongs in a successor engine. Equal `kbase` bytes permit reuse of the standard-monomial basis;
   they do not prove byte equality of every multiplication table or generator normal form.
6. **Repository canon.** The proposed `dp` and `groebner` tests retain global orderings as required by
   `docs/runbooks/computer-algebra.md:8-18`. Independent loops require `parallel.py`; new random samples require named
   QRNG draw indices (`AGENTS.md:47-50,67-77`); every unapproved run stays within three hours. This audit drew no random
   value and launched no long computation.
7. **Ledger consistency.** A5-010, A5-061, A5-062, and A5-066 prove finite-field structure only. A5-138 through A5-149
   match the modular evidence; A5-143 and A5-149 use A5-066 while direct degree-6 ranks remain engine tests. A5-247
   covers only check 1. A5-248 correctly says cofactors are noncanonical. A5-249 covers X degrees 1 through 5. A5-258
   remains open. A5-260 and A5-269 survive measured degrees only. A5-277 omits orders 16 and 19. A5-278 is a mechanism
   hypothesis. A5-279 correctly remains stalled. The statuses are internally consistent; the plan's unretained lever
   prose and omitted W8 order-16 check are the inconsistent summaries.
8. **Probe and lift scripts.** The Singular templates form `Q = std(J) + m*P` and call `lift(Q,Rel)`, matching the
   intended modular cofactor computation (`lift-cofactors.sing.in:1-17`). The launchers fail reliable status, stdin,
   and parallelism requirements as finding 4 records. The cofactor support comparison does not decide canonicality.

## Owner decisions

### Run a lever before an order-21 cell

Run one retained order-18 comparison against the baseline, including basis, table, generator, rank, resource, and
producer digests. Order 21 exceeds the three-hour cap at the low estimate and cannot certify order-22 closure. The live
order-15 `slimgb` observation reports 301.0 seconds against a loaded baseline of 562.2 seconds, a provisional 1.87
times speedup close enough to justify the bounded order-18 test. Change the decision only if the retained order-18
winner is slower than 2.27 times baseline, exceeds the cap, changes the quotient/ranks, or fails byte/equivalence
checks. In that case, request approval for one order-21 cell at 32009 to falsify the three order-21 predictions.

### Add deterministic variable-order autotuning with `groebner`

Keep `dp`, enumerate a small fixed set of variable permutations at order 15, and call `groebner` from Singular's
`standard.lib`. `Singular -q --no-rc -c 'help groebner;' < /dev/null` says that `groebner` heuristically chooses among
direct and conversion methods and recommends testing methods on a simplified hard example. Promote the fastest
permutation to one order-18 test. A successor engine must record the variable order and map the exported basis and
tables back to the canonical variables. Falsifier: every retained order-18 candidate is below 2.27 times speedup or
changes the quotient/ranks. Expected pilot cost is the retained 420 to 427 seconds per order-15 baseline cell, with
the loaded live baseline of 562 seconds as the conservative bound. The deterministic enumeration uses no seed.

### Use canonical linear systems for W8 check 2

Reuse each retained W8 receipt's five `sq.txt.part*` standard-basis fragments, relation file, and two normal-form
fragments. Build a fixed degree-bounded coefficient matrix, compute a canonical RREF at each prime, reconstruct its
coefficients over `Q(i)`, and verify every reconstructed relation exactly over `Q(i)` through `parallel.py`. The
receipts already paid the 6,559.564- and 9,860.33-second standard-basis stages; rerunning a noncanonical whole-matrix
`lift` discards that advantage. If modular identity verification remains, use both conjugate roots or a proved
Gaussian norm bound. Acceptance is 144 exact identities whose reductions span the retained K2 at both primes.

## Open-task attack and bounded schedule

| Task | Present-foundation action or precise blocker | Falsifier and evidence-bound cost |
|---|---|---|
| 5, A5 exceptional fibers | The blanket thesis is false: tasks 37, 42, 56, 75, 115, and the VB lever have bounded next computations. | The per-task falsifiers below decide each increment. |
| 37, VB degree-3 component | On OCI A1, solve deterministic order-2 jet-parameter arcs over the `t1=0` plane in the `t3`, `t5`, and `t7` charts, then test P1 generators on leading vectors. | A dominant generic-rank-3 family supports P1; a sampled failure is inconclusive. The retained chart-5 normalization took 359 seconds and `normal(...,"isPrim")` on chart `t7` took 451 seconds (`docs/notes/topics/a5-exceptional-fiber-findings.md:456-475,526`). |
| 42, characteristic zero | Complete W8 order-16 check 3 on the build host, then apply the canonical check-2 route degree by degree. | A denominator or changed leading ideal refutes check 3; a reconstructed relation or span failure refutes check 2. Order 13 took 22 minutes (`ledger.tsv:276`), so order 16 receives the three-hour cap rather than an assumed completion. |
| 56, Iso support | On OCI A1, run one Iso point-blowup local-plane pilot modeled on the W8 C30 certificate. | Rank below cone dimension at every sampled point, or a base locus missing V(K2), refutes the route. One analogous W8 plane took 45 to 52 seconds and 26 MiB (`a5-exceptional-fiber-findings.md:445-448,527`). |
| 75, W8/X check 2 | Replace support comparison with the canonical bounded RREF and exact identity route. Start with X, then reuse retained W8 standard bases. | Any failed exact identity, incompatible reduction, or wrong relation-space dimension refutes transfer. X lift measured 1,565 seconds at 16.5 GB (`ledger.tsv:247`); naive W8 lift scaling is 135.706 hours, so direct W8 `lift` lacks a bounded case. |
| 103, merged IBM-wide and Tuna six-CZ claims | This task is a separate claim-interpretation change, not a Singular foundation problem. Reconcile the retained acquisition records and write only claims supported by their existing analyses. | A claimed statistic absent from the retained records blocks the claim. The brief supplies no replay timing, so this review does not invent an expected compute cost. |
| 106, gororoba-open | In the other repository, prove the right-nullity and zero-lower-half companions, run exact ranks at Cayley-Dickson orders 4 and 5, and add the mutation arm (`a5-exceptional-fiber-findings.md:489-492`). | A rank not divisible by four or a mutation that leaves the observable unchanged refutes the proposed result. The current repository contains no timing record; the missing artifacts are the named Rocq lemmas, exact-rank test, and mutation proof. |
| 110, E8-bar membership | The thesis holds for the current algorithm. Develop a sparse bounded membership/cofactor solver for the 91 degree-5 and 140 degree-6 forms before another receipt attempt. | The solver fails exact membership controls or still invokes `std(J+mP_d)`. Degree 2 already took 12,678 seconds and degree 3 did not finish (`a5-exceptional-fiber-findings.md:528`). |
| 113, W8 degree-6 rank | The scientific value is already proved by A5-066. Treat order 19 only as an engine test after streamed-by-degree `L`, in-place block updates, compact/free-column storage, and GPU completion. | A direct rank above 8,624 exposes an engine/receipt defect; a lower truncated rank does not refute `h_6`. Engine v11 needs 129 to 223 GiB and 18 to 27 hours (`a5-exceptional-fiber-findings.md:449-453,531-533`). |
| 115, exact torus | Solve the three-dimensional abelian Klein centralizer over `Q`, test positive weights for homogeneity, then run the winning weighted global-ordering basis at order 15 and 18 on the build host. | Absence of positive weights, lost quotient/ranks, or order-18 speedup below 2.27 refutes the lever. The first performance stage inherits the 420-562 second order-15 baselines (`a5-exceptional-fiber-findings.md:498-509`). |
| VB degree 7 | Run the retained order-18 lever comparison first; run one order-21 cell only after the stated failure condition and owner approval. | Order-21 values other than 609 or 7/8/0/0, or early 624, fire three independent falsifiers. Cost is 15,468 to 29,350 seconds extrapolated. |
| W8 characteristic zero | Run order-16 check 3 and the canonical check-2 pilot on separate resources. Reserve the all-degree statement for the flatness/openness and A5-066-transfer proofs. | Bad reduction, failed exact relations, or a broken affine-cone argument blocks promotion. Receipt costs are 6,559.564 and 9,860.33 seconds for the already-retained modular bases. |

The VB lever can run on the Windows workstation laptop while W8 order-16 check 3 runs alone on the build host and
task 37 runs on OCI A1. The Iso pilot can follow task 37 on OCI A1. The exact-torus solve can run beside laptop work
only when the build host has no other active Singular computation. Provider and paid-cloud sessions remain subject to
their separate written approvals.

## New conjectures suggested by the records

1. **Variable-order sensitivity drives a material part of the VB standard-basis wall.** Falsifier: every fixed `dp`
   permutation at order 15 matches baseline within noise or loses at order 18. Cheapest test: deterministic order-15
   permutation screen followed by one retained order-18 winner.
2. **The live `slimgb` advantage persists at the decision size.** Falsifier: retained order-18 speedup below 2.27 or
   any unequal quotient/rank artifact. Cheapest test: one prime at order 18.
3. **W8's generic characteristic-zero projective fiber has either one degree-50 component or degree-20 and degree-30
   components.** Falsifier: a p-integral leading ideal fails, the generic fiber is nonreduced, or an exact generic
   decomposition has another degree partition. Cheapest test: finish canonical check 2, prove the graded flat family,
   then factor one generic linear section rather than run a global radical computation.
4. **Canonical W8 relation systems remain sparse enough to avoid a fresh 6,559- to 9,860-second standard basis.**
   Falsifier: the fixed RREF matrix exceeds the three-hour or 6 GiB review bound, or reconstructed identities fail.
   Cheapest test: one relation block against the retained `sq` and normal-form fragments.

## Steelman

The plan correctly isolates the VB standard basis as the dominant stage, preregisters independently falsifiable
degree-7 predictions, preserves global orderings, separates per-degree rank transfer from all-degree geometry, and
requires a successor engine for a changed producer. Those choices turn several formerly day-scale questions into
bounded tests. The invalid Gaussian bound, noncanonical support test, missing order-16 check, unreliable launchers,
and unretained timing claims must be repaired before the plan can govern execution or support characteristic-zero
claims.
