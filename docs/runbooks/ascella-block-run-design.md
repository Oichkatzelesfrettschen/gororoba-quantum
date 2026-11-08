# Ascella block-run design and reading

This runbook holds what a photonic block case on `qpu:ascella` needs to know before it is built and while its run is
read: what a served mesh is, why the four-term block case passed and the two-coset-block case failed, the reading module
of the mesh-persistence case with the review finding behind each mechanism, the design rules those findings imply, and
the open questions. It is a living document. A result that settles a question appends a revision-log entry and edits the
rule it changes; the numbers below link to the file that carries them, and the sources keep their bytes.

Evidence classes. "Measured" is a number read from a retained file or log. "Computed" comes from a model or a
simulation whose script is in the repository. "Hypothesis" is a reading that no retained result has tested.

Status. The mesh-persistence case ran on 2026-11-07: the `sim:ascella` gate run
(`results/quandela/runs/2026-11-07T181127Z-sim_ascella-ascella_pathion_mesh_persistence-sim-00/`) and the
`qpu:ascella` job `6bc382af` (`results/quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00/`).
The rules below were preregistered in the [case](../design/ascella-pathion-mesh-persistence-case.md) before either run;
the readings are in the [findings](../../results/live/PATHION_KERNEL_MAP_FINDINGS.md) section "Ascella mesh persistence"
and the revision log.

| Part | Content |
|---|---|
| [Served meshes](#what-a-served-mesh-is-on-ascella) | the facts that set the design |
| [Four-term pass, two-block failure](#why-the-four-term-case-passed-and-the-two-block-case-failed) | the retained comparison and the surviving hypothesis |
| [Reading module](#the-reading-module) | one subsection per mechanism of the frozen reading |
| [Design rules](#design-rules-for-the-next-block-case) | what the next case takes from the evidence |
| [Open questions](#open-questions-and-the-decision-each-awaits) | outcomes of the mesh-persistence job and the ledger rewrite each causes |
| [Revision log](#revision-log) | dated entries; append, never rewrite |

## What a served mesh is on Ascella

A served mesh is the circuit the service compiles from a request's compilation seed and circuit parameters and returns
as `computed_circuit` (66 Mach-Zehnder blocks, 132 beam splitters, 126 phase shifters on the pathion cases;
[C1](../evidence/pathion-kernel-map/conjectures/mechanisms.md#c1-ascella-two-block-job-the-mirror-failure-is-not-a-per-mode-efficiency-effect)).
The returned circuit reproduces the programmed label law to 1.9e-4
([c1_mesh.txt](../evidence/pathion-kernel-map/conjectures/c1_mesh.txt)); the light the chip emits departs from it.

| Fact | Number | Class | Source |
|---|---|---|---|
| A seed serves the byte-identical mesh across days and a software update | job-03 returned every setting of job-02's mesh nine hours later; job-08 returned job-03's mesh for all 64 settings twelve days later across a software update; job-09 returned job-02's mesh, and its `sim:ascella` gate stayed within 2.45e-7 | measured | [signed-coherence design](../design/ascella-signed-coherence-conformance.md#seed-repeat-case-job-03), [job-08](../design/ascella-signed-coherence-conformance.md#long-horizon-seed-repeat-case-job-08), [job-09](../design/ascella-signed-coherence-conformance.md#prospective-correction-case-job-09) |
| Each mesh carries a fixed error that persists | per-mesh error correlation r 0.885 at the counting ceiling 0.880 (job-03 against job-02); r 0.925 at 0.936 (job-08 against job-03); r 0.958 at 0.956 (job-09 against job-08) | measured, signed-coherence circuit family | same |
| A per-seed table corrects about 90 percent of the per-mesh variance | standard deviation 0.01085 to 0.00337, ratio 10.37 (98 percent interval 6.16 to 16.21), table fitted twelve days earlier | measured, 56 seeds of one signed-coherence arm | [job-09 outcome](../design/ascella-signed-coherence-conformance.md#prospective-correction-case-job-09) |
| Static element maps carry about 10 percent on unseen meshes | r 0.157 and 0.319 (shares 2.5 and 10.5 percent), replication r 0.240 (6.0 percent); the maps give direction, not amplitude (slopes 0.12 to 0.32) | measured, same family | [new-seed case](../design/ascella-signed-coherence-conformance.md#new-seed-meshes-case-job-04-and-job-05), [replication](../design/ascella-signed-coherence-conformance.md#replication-case-job-06-and-job-07) |
| Published g2, HOM and dark counts move a single-photon level by at most 0.003 | 0.0026 from g2 2 percent and indistinguishability 0.8898 through threshold detectors; 0.0030 from dark counts of 68 to 340 per second per mode | computed (Perceval 1.3.1 `NoiseModel`, processor record of 2026-11-07) | `--spec-check` of [the builder](../../scripts/ascella_pathion_mesh_persistence.py), [case](../design/ascella-pathion-mesh-persistence-case.md#published-imperfections-simulated) |
| The simulator returns the ideal law for every seed | `sim:ascella` of the two-block request reads 0 of 46 failing mirror pairs, maximum 0.0066; job-08's simulator run spread its error statistic at 0.00211 against a counting 0.00203, where the chip spread 0.01175 | measured | [mirror_test_sim.txt](../evidence/pathion-kernel-map/conjectures/mirror_test_sim.txt), [job-08](../design/ascella-signed-coherence-conformance.md#long-horizon-seed-repeat-case-job-08) |
| The pathion meshes' error is static per configuration, about 0.02 to 0.03 rad per shifter | white phase error of 0.033 rad matches the mirror rms 0.0488; a fluctuating error predicts a repeat-pair rms of 0.0189 against 0.0024 observed; identical meshes repeated in one job differ by at most 0.0055 raw | measured and computed | [c1_phase.txt](../evidence/pathion-kernel-map/conjectures/c1_phase.txt), [c1_predecessor.txt](../evidence/pathion-kernel-map/conjectures/c1_predecessor.txt), [c1_observed.txt](../evidence/pathion-kernel-map/conjectures/c1_observed.txt) |

The first four rows were measured on the signed-coherence analyzer circuits, not on the pathion block meshes. That the
pathion meshes behave the same way is a hypothesis; the replay in the mesh-persistence case is its first test.

## Why the four-term case passed and the two-block case failed

| Case | Structure | Outcome |
|---|---|---|
| [four-term blocks](../design/ascella-pathion-four-term-blocks-case.md), job `f3a11b5f`, 88 iterations | one 4 x 4 block per photon; eleven segments with one seed each; the two anchor segments share one seed; the normalization `a'` contracts every reading by the same affine map | 8 of 8 pathion readings, 2 of 2 reference readings and 11 of 11 mutation readings within 0.07; anchor 0.9989, dark 0.0023; the C8 class spread 0.048 under its 0.05 flag (ledger row A5-188) |
| [two coset blocks](../design/ascella-pathion-coset-block-pairs-case.md), job `db6355f7`, 52 iterations | two blocks per photon in two slots; each slot calibrated by the efficiency of one anchor mesh; every setting read in both slot orientations | 9 of 46 mirrored readings more than 0.07 apart against an allowance of 4, maximum 0.1082, rms 0.0488: instrument not admitted (ledger row A5-189) |

The mechanism the retained data leave standing (ledger row A5-191, confidence 0.55) is the anchor calibration. Dividing
each slot by the efficiency of one anchor pair produces the failures:

| Slot efficiencies (A, B) | Failing of 46 | rms | Source |
|---|---|---|---|
| anchor pair, as analyzed (1.0064, 1.0886; B/A 1.082) | 9 | 0.0488 | [c1_anchor.txt](../evidence/pathion-kernel-map/conjectures/c1_anchor.txt) |
| no division (1, 1) | 1 | 0.0250 | same |
| mode fit over all iterations (1.0721, 1.064; B/A 0.992) | 0 | 0.0237 | same |

The rms-minimizing B/A is 0.985, and every analysis without the anchor division leaves 0 or 1 failing pair, below the
allowance. One mesh pair supplies B/A, so its own fixed error acts as a slot gain on every reading of that slot; the
mirror test puts each block in both slots, and a slot gain that differs between the two reads as a difference (the
mechanism is a hypothesis; the replay and the fresh anchors test it). The four-term case read one block per photon, so its anchor
entered as a common scale of 0.9989 and no slot ratio existed. Per-shifter gain maps fitted on the same data reproduce
about half the anchor excess in sample (B/A 1.033 to 1.053,
[c1_anchor_map.txt](../evidence/pathion-kernel-map/conjectures/c1_anchor_map.txt)); the anchors sit in every fit's
training set.

Mechanisms the retained data refute, each with the number that decides it
([C1 table](../evidence/pathion-kernel-map/conjectures/mechanisms.md#c1-ascella-two-block-job-the-mirror-failure-is-not-a-per-mode-efficiency-effect),
ledger rows A5-189, A5-190):

| Mechanism | Decisive number | Source |
|---|---|---|
| analysis or compilation | the `sim:ascella` twin reads 0 of 46, maximum 0.0066 | [mirror_test_sim.txt](../evidence/pathion-kernel-map/conjectures/mirror_test_sim.txt) |
| counting statistics | z = d / se has rms 11.33 | [c1_observed.txt](../evidence/pathion-kernel-map/conjectures/c1_observed.txt) |
| drift between iterations | Spearman of abs(d) with separation -0.050 (p 0.743) | same |
| per-mode efficiency | a nine-parameter model flags 0 of the 9 failing pairs; residual rms 0.0461 against 0.0488 observed (about a tenth of the variance); the earlier attribution read that model's prediction as corrected data and is withdrawn | [mirror_test.txt](../evidence/pathion-kernel-map/conjectures/mirror_test.txt) |
| multiphoton or threshold events | invalid share at most 5.26e-4 against differences of order 0.03 | c1_observed.txt |
| global beam-splitter angle shift | held-out correlation -0.720 and -0.497 | [c1_heldout.txt](../evidence/pathion-kernel-map/conjectures/c1_heldout.txt) |
| sensitivity of the pair to phase error as an independent predictor | partial rank correlation +0.007 given the item's ideal level | [c1_controls.txt](../evidence/pathion-kernel-map/conjectures/c1_controls.txt) |

The static per-shifter map predicts the other orientation at r +0.54 to +0.88 against a shuffled-link maximum of +0.16
([c1_static.txt](../evidence/pathion-kernel-map/conjectures/c1_static.txt),
[c1_static_null.txt](../evidence/pathion-kernel-map/conjectures/c1_static_null.txt)); on unseen signed-coherence meshes
such maps carry about 10 percent. The mesh-persistence case separates the two readings. The ledger falsifier of A5-191
names the outcomes that end it: anchor configurations whose B/A agrees near 1.08, or replayed failing settings that do
not reproduce the difference within 0.005
([ledger](../evidence/a5-exceptional-fibers/ledger.tsv), rows A5-188 to A5-191).

## The reading module

[`ascella_pathion_mesh_persistence.py`](../../scripts/ascella_pathion_mesh_persistence.py) builds the frozen requests
and holds the thresholds (`PREREGISTERED`, copied into `cases.json`);
[`ascella_pathion_mesh_persistence_analysis.py`](../../scripts/ascella_pathion_mesh_persistence_analysis.py) reads a run
through three commands: `--mesh-gate` (the simulator run), `--analyze` (the QPU run, every decision with its numbers)
and `--persistence-plan` (the fixed-mesh simulation that freezes the cutoffs). Its tests
([test_ascella_pathion_mesh_persistence.py](../../tests/scripts/test_ascella_pathion_mesh_persistence.py)) run the
reading on synthetic runs built from the retained record. The case holds the 84-iteration design (52 verbatim replays,
14 fresh-anchor, 16 fresh-failing and 2 fresh-dark iterations) and the decision table
([case](../design/ascella-pathion-mesh-persistence-case.md#design)). Two reviews shaped the module: a Codex adversarial
review of the first version (gpt-daybreak-blue at high effort, eight findings ranked, each fixed) and an Advisor review of
the revised case. Both are local and untracked; their findings appear here by content.

Every decision may read "not read" (a partial run, or a correlation input that is non-finite or constant) or
"unresolved"; the readings are not exclusive, a mixture of carriers is allowed, and each decision names what it excludes.

### Coverage-checked mesh gate

`mesh_gate` compares the `sim:ascella` run with the frozen simulator case and, only when every coverage check holds,
compares each replay's served unitary with the one the original QPU job served under the same name. It requires the
run's `cases.json` to equal the frozen `sim-00` bytes, 84 results, the echoed `compilation_seed` and `circuit_params` of
every result to equal its request, the 52 replay `original_name` values to equal the original job's 52 names once each,
and the largest entry modulus of each unitary difference to stay at or below 1e-6; it exits 1 otherwise and the QPU job
is not sent.

- Defect prevented. The first version skipped non-replay rows and reported a constant 52 for the replay count, so an
  empty replay set, or duplicates that omit an original mesh, produced no miss and passed (Codex review, mesh gate
  finding). The gate now measures the count and the name set.
- Frozen numbers. Tolerance 1e-6 (`mesh_identity_tolerance`); the signed-coherence gates sat at 2.45e-7.
- Tests. A changed mesh, a missing result, a duplicated replay and a foreign manifest each refuse.
- Reuse. A new case binds its own simulator manifest by digest, replaces 84 and 52 by its own counts, and takes the
  reference unitaries from the retained run that it replays, keyed by setting name.

### Binding the QPU run to the frozen request

`analyze` returns "not read: cases.json differs from the frozen job-00 case" for any run whose `cases.json` differs from
`job-00/cases.json` by one byte, before it reads a count.

- Defect prevented. The analysis read whatever manifest the run carried, so a QPU run of another request could score
  against this case's thresholds (Advisor review).
- Reuse. Freeze the request directory, compare bytes, and keep the builder's inputs in `analysis_sources` so a changed
  script or retained file changes the manifest.

### Finite-input guards

`finite_r` returns `None` for fewer than three points, any non-finite value, or a constant vector; every correlation in
the module goes through it, and the decision reads "not read". The frozen-map score, the fresh anchors and the aligned
mean carry the same guard.

- Defect prevented. A `NaN` observed correlation made every comparison false and the relabeling p-value return its
  minimum 1/20001, so a constant detector response became the label "partly fixed", "follows the mesh" or "map does not
  carry" (Codex review, non-finite input finding). A constant response is an identifiability failure.
- Test. `test_constant_or_non_finite_inputs_are_not_read`.
- Reuse. Route every new statistic through `finite_r` or its equivalent before a p-value.

### Fixed-mesh resampled persistence cutoff

The persistence decision is the Pearson r of the 46 calibrated replay mirror differences with the original job's. The
cutoff comes from `persistence_plan`: the original job's per-iteration click laws are each mesh's true law; 2,000 pairs
of jobs are drawn as independent multinomials at 131,072 samples, each calibrated with its own anchor and dark rows, under
three between-job efficiency scenarios.

| Drift scenario | First percentile of r | Median |
|---|---|---|
| none | 0.9914 | 0.9963 |
| measured per-mode ratio of the two retained pathion jobs applied to the replay | 0.9901 | 0.9956 |
| random per-mode ratio of the same spread, sd 0.0197, drawn per replicate | 0.9880 | 0.9954 |

The cutoff is the widest first percentile, 0.988 ([persistence_plan.json](../../results/quandela/cases/ascella_pathion_mesh_persistence/persistence_plan.json),
seeded by value 0 of [the plan draw](../evidence/anu_qrng/draw-2026-11-07T165920Z.json)). A fixed per-mesh error reads
"fixed per mesh" in 99 percent of jobs under that drift; a redraw of the errors gives r near 0 against 46 pairs. An r
below the cutoff with a one-sided relabeling p under 0.01 (20,000 relabelings) reads "partly fixed"; otherwise "not
reproduced". The raw-level r is reported beside it.

- Defect prevented. The first cutoff was a plug-in: a homoscedastic noise variance from one binomial level, subtracted
  from the observed variance and passed through a Fisher transform (cutoff 0.989), presented as a 99 percent bound
  although the statistic uses calibrated differences with shared anchors and heteroskedastic counts (Codex review,
  persistence cutoff finding). The cutoff was also silent on between-job drift (Advisor review).
- The measured drift is an upper bound. The per-mode ratio of the two retained jobs, fitted by the mode-efficiency EM on
  modes 0 to 7 (`MEASURED_MODE_DRIFT`, sd 0.0197), also absorbs each job's own per-mesh errors, so it overstates
  between-job drift. The original job's observed click law serves as truth, so its counting noise enters once, which is
  conservative for the cutoff.
- Reuse. Rebuild the plan with `--persistence-plan` from a new draw, replace the laws with the new original run's, and
  let the audit test confirm the committed record rebuilds. The cutoff constant in the builder is checked against the
  record (`test_the_persistence_cutoff_is_the_frozen_plans`).

### Aligned mean for fresh settings of a failed design

For the eight settings that carry the nine failing readings, each at one fresh seed in both orientations, the statistic
is the aligned mean A = mean over the nine items of sign(original raw d) x fresh raw d, with the original mean |raw d|
0.0376 and the per-mesh raw spread 0.0251 of the 46 original raw differences (standard error 0.0084 for nine items).

| Rule | Reading |
|---|---|
| A at or above 0.0196 | follows the design: excludes a purely per-mesh failure |
| A below 0.0181 | follows the mesh: excludes a design-tied failure at the original size |
| between | unresolved |

Error rates from the normal model (`aligned_power`, recorded in `persistence_plan.json`): a design-tied failure at the
original size reads "follows the design" in 98.4 percent and "follows the mesh" in 1.0 percent; a per-mesh failure reads
"follows the mesh" in 98.5 percent and "follows the design" in 1.0 percent.

- Two-extreme assumption. The labels hold when all of the failure is tied to the design or none of it is. Under a
  mixture the reading is the carried fraction A / 0.0376 with its 99 percent interval, half-width 2.576 x 0.0084 / 0.0376
  = 0.57 for nine items (the written case and the builder docstring round it to 0.58); the labels split the fraction at
  one half (Advisor review, mixture caveat).
- Defect prevented. The first version correlated the nine fresh and original raw differences and read non-rejection as
  "follows the mesh". At nine items that test had about 25 percent power at r 0.6 (a one-sided Pearson test at alpha 0.01
  needs r of about 0.75), so it reported the wrong branch in about 75 percent of runs at its own target effect (Codex
  review, power finding). The aligned mean replaced it with both error rates near 1 percent and an unresolved band.
- Reuse. Compute both error rates from the original effect and the per-mesh spread before the data exist; a failed
  association test reads "unresolved", never a mechanism. A correlation of roughly 24 independent items, not 9, reaches
  80 percent power at r 0.6 under a Fisher reference, so a correlation design needs a frozen permutation-power
  calculation at its own item count.

### Fresh-anchor ratio rule

Each of seven fresh anchor seeds, in both slot orientations beside the fresh dark, gives its own B/A through
`calibrate`. The median within 0.03 of the mode-fit 0.992 with a standard deviation above 0.012 reads "anchor ratio
follows the mesh"; every seed within 0.03 of 1.082 reads "slot efficiency"; otherwise "unresolved". Classification rates
(normal model, [persistence_plan.json](../../results/quandela/cases/ascella_pathion_mesh_persistence/persistence_plan.json)):
under the per-mesh reading (median 0.992, sd 0.025) the rule reads "follows the mesh" in 95.5 percent and "unresolved" in
4.5 percent; under the slot reading (1.082, counting sd 0.0039) it reads "slot efficiency" in 100 percent.

The bands are engineering thresholds, and those rates are their calibration; the 0.992 mode-fit value enters as a
constant, so its own uncertainty is not propagated (Codex review, persistence cutoff finding; Advisor review, open
risk). The replayed B/A is read separately: within 0.02 of 1.082 reads "anchor error unchanged".

### Seed-block permutation for the frozen maps

The gain and offset maps of [`c1_static.npz`](../evidence/pathion-kernel-map/conjectures/c1_static.npz) (frozen in
commit `cc8d8107c`, before the case) predict the raw slot levels of every fresh iteration from its returned circuit. The
score is the Pearson r of predicted against observed departures from the ideal level, centered within kind (fresh anchor,
fresh failing, fresh dark). The p-value comes from 20,000 relabelings that permute whole compilation-seed blocks: 16
fresh seeds, each block holding both orientations and both slots, so four readings move together; one-sided at 0.005
per map (Bonferroni over two maps). "Map carries" reports its share r^2 over the ceiling 1 - (mean per-row multinomial
variance) / (observed variance).

- Defect prevented. The first version appended 64 slot readings and used a Student t reference on 60 degrees of freedom.
  Those readings come from 32 iterations that come from 16 seeds, so the unit of analysis was wrong; at one-sided 0.005
  the critical r is near 0.325 for 60 degrees of freedom, 0.463 for 32 independent configurations and 0.661 for 16 seed
  clusters. The share also used one homoscedastic ceiling (Codex review, frozen-map independence finding).
- Topology guard. Every served circuit must keep the frozen component sequence and every beam splitter must be `BS.Rx`,
  the convention the propagation law assumes; a provider change that keeps the type name but changes the convention
  would otherwise score the wrong unitary (Codex review, beam-splitter convention finding).
- Equal-block requirement. The relabeling needs seed blocks of equal size and raises on unequal sizes.
- Prior art for the expected share: 2.5, 10.5 and 6.0 percent on unseen signed-coherence meshes
  ([new-seed case](../design/ascella-signed-coherence-conformance.md#new-seed-meshes-case-job-04-and-job-05)).
- Gap. No power record exists for this decision at 16 blocks, so "map does not carry" states the resolution of the test,
  unquantified.
- Reuse. Make the shared seed the permutation unit; propagate each row's multinomial variance into the ceiling; check
  convention and topology before applying a map.

### Within-job control

The control reads drift inside the job, the only drift the case reads. It reports the per-iteration persistence r on the
replay's early half and late half, and compares the early replayed anchors (positions 0 and 1) with the late ones (the
last two) against the predecessor's 0.03 drift band (`anchor_drift`). Per-iteration persistence is
(calibrated level - ideal) of each replay iteration and slot against its original twin under `original_name`, each side
calibrated by its own anchors.

- Defect prevented. The first control scored mirror differences on each half, but each half of the palindrome reads a
  design in one orientation only, so the mirror differences were empty (Advisor review); a test requires both halves
  finite. A separate finding barred reading drift from low persistence: a time-varying common gain can preserve
  correlation and a redraw can destroy it, so only a time-ordered control identifies drift (Codex review, overlapping
  outcomes finding).
- Gap. The half-job correlations are reported without a threshold.
- Reuse. Order the job so the early and late slots repeat identical requests, and score twins by name rather than by
  mirror pairs when a half reads one orientation.

### Raw against calibrated levels

A raw level a = 2 x (slot clicks) / (clicks in modes 0 to 8) carries no calibration; the calibrated level l_hat divides
each slot by its anchor efficiency (`calibrate`). Persistence and correction read l_hat with the replayed anchors, the
quantity whose mirror test failed. The fresh-failing and frozen-map decisions read raw levels, so no anchor enters a
comparison of meshes. Dividing both sides by the replayed anchors would put the shared B/A gain into both and bias the
fresh comparison toward "follows the design" ([case](../design/ascella-pathion-mesh-persistence-case.md#preregistered-decisions)).
Admission reads the replay's anchors and darks with the predecessor's limits: anchor at least 0.90, dark at most 0.05,
sentinel share at most 0.05.

### Correction table

The original job's per-iteration calibrated departures from the ideal level, keyed by original name and physical slot,
apply as a per-mesh table to the replay. At most 4 of the 46 mirror differences (floor of 0.10 x 46) may exceed 0.07;
the report carries the failing counts and the rms before and after. Keys use the original name and the physical slot so
the table corrects each orientation of each mesh and never crosses logical items (the Codex review confirmed the keying).
This is the pathion counterpart of the signed-coherence per-seed table (ratio 10.37).

## Design rules for the next block case

1. Calibrate slots from many anchor seeds or from a per-mesh table, never from one anchor mesh. One pair supplied B/A
   1.082 where the other meshes imply 0.992, and removing the division cut the failures from 9 to 1
   ([c1_anchor.txt](../evidence/pathion-kernel-map/conjectures/c1_anchor.txt)). Take the number of anchor seeds from the
   spread the job measured: seven fresh anchor seeds read B/A from 0.84 to 1.05, median 0.951 and sd 0.067, not the
   sd 0.025 the case assumed, so a slot calibration sized for a 0.01 level needs about (0.067 / 0.01)^2 = 45 anchor
   seeds, or a per-mesh table.
2. Read one block per photon where a design allows. The four-term case did and passed every rule; the fold into two
   blocks saved reconfigurations and put one anchor mesh's fixed error into every reading of its slot, which the
   mesh-persistence job confirmed (A5-200, A5-201).
3. Replay verbatim. Send the retained setting's bytes (compilation seed and circuit parameters) under a new name and
   position, and check the rebuild against it: identical seed, orientation and role, the target operator and the laws within
   1e-12. The template decomposition is degenerate (equal columns from phases that differ by pi/2), so rebuilt parameters
   differ from the request; compare operators, not parameters (builder `documents`).
4. Size every fresh-seed set by error rates computed before data, from the original effect and the per-mesh spread:
   anchors 95.5 and 100 percent, aligned mean 98.4 and 98.5 percent, persistence 99 percent. A rule that reads
   non-rejection as a mechanism needs its power computed first (about 25 percent for the nine-item correlation).
5. Gate the QPU job on a `sim:ascella` mesh-identity run of the identical request. The simulator returns the ideal law, so
   it proves the client, the pipeline and the served-mesh identity, and it cannot reproduce the chip's per-mesh error (job-08
   simulator spread 0.00211 against the chip's 0.01175).
6. Budget 3.1 to 3.2 seconds per iteration against the packing margin of 270 seconds (0.9 of the 300-second cut). The
   retained rates are 3.10 s on `db6355f7` (52 iterations in 161 s), 3.04 s on signed-coherence job-04 (80 in 243 s) and
   3.01 s on the four-term job (88 in 265 s). 84 iterations at 3.2 s expect 268.8 s, which leaves 1.2 s inside the margin;
   the 300-second cut is the real safety margin, and a cut loses the late anchors first. The QPU job bills
   1 + 1e-6 x the largest iteration's `max_shots` (1.131072 credits); `check_duration` asserts the fit.
7. Draw every seed from the ANU QRNG and declare every plan draw in the manifest. A fresh seed takes its value from a
   draw in index order, each used once and unused by the replayed job (draw
   [2026-11-07T162910Z](../evidence/anu_qrng/draw-2026-11-07T162910Z.json) fills 18 values: seven anchor seeds, eight
   failing-setting seeds, one dark seed, two analysis generators). A replay keeps the original job's seeds as identifiers
   of the meshes it reproduces. The seeds of a simulation that freezes a cutoff (draw
   [2026-11-07T165920Z](../evidence/anu_qrng/draw-2026-11-07T165920Z.json)) go in the manifest's `plan_seed_source`; the
   seed ledger (`ci/seed_provenance.py --check`) enforces it ([AGENTS.md](../../AGENTS.md#seeds)).
8. Compare meshes on raw levels; reserve calibrated levels for the quantity whose test failed (see "Raw against
   calibrated levels").
9. State what each decision excludes, allow mixtures and keep an "unresolved" band; read non-finite input as "not read".
10. Test the reading on synthetic runs built from the retained record: a replay of the original counts must read r = 1,
    "fixed per mesh" and zero failures after correction. Keep the unmarked test inside the pull-request budget by running
    two settings of the specification check; the full 18-setting simulation stays the `--spec-check` command (a cold cache
    exceeded 15 s).

## Open questions and the decision each awaits

The mesh-persistence job's outcomes rewrite ledger row A5-191 (the anchor-calibration hypothesis, confidence 0.55) as
the case's outcome map specifies ([case](../design/ascella-pathion-mesh-persistence-case.md#preregistered-decisions)):

| Outcome | Rewrite of A5-191 |
|---|---|
| persistence at or above 0.988, fresh anchor ratio follows the mesh, fresh failing follows the mesh, no carrying map | "per-mesh fixed errors, the anchor pair's among them": the per-shifter clause drops and the confidence rises; the block cases take slot efficiencies from many anchor seeds or a per-mesh table |
| a map carries at p under 0.005 | adds the per-shifter clause with its share r^2 / ceiling |
| fresh failing at or above 0.0196, or a carried fraction above one half | adds a block or slot term of that size |
| every fresh anchor near 1.082, or replayed failing settings that do not reproduce the difference within 0.005 | the ledger falsifier fires: the anchor-calibration reading ends |
| persistence below 0.988 with p at or above 0.01 ("not reproduced") | redraw and between-job drift stay unresolved unless the within-job control reads drift |
| any decision "not read" | no verdict on that decision; the run is read as far as its other decisions allow |
| correction leaves more than 4 of 46 above 0.07 | a per-mesh table does not correct the pathion meshes and the signed-coherence correction does not transfer |

The job ran on 2026-11-07 (`6bc382af`): the first two rows apply (fixed per mesh, failure follows the mesh; the frozen
model carries mainly through its per-mode efficiencies; a shifter map beyond them is not established), the fresh-anchor rule reads unresolved with slot efficiency excluded, and A5-191 is decided by A5-200 to
A5-203 (revision log). Further open items:

- The pathion meshes persist like the signed-coherence meshes (replay r 0.9966); whether they persist across days and
  software updates, as job-08 showed for that family, is untested on pathion meshes.
- Where the anchor-ratio distribution centers: the fresh seeds read median 0.951 against the mode-fit 0.992.
- Whether the frozen maps carry on pathion meshes: no power record exists at 16 seed blocks.
- What the half-job correlations of the within-job control mean without a threshold.
- The origin of the per-mesh error: a noise model of it does not exist, per-component loss is not retained, and the
  applied heater voltages that Perceval issue 799 requests are the direct test
  ([signed-coherence design](../design/ascella-signed-coherence-conformance.md#new-seed-meshes-case-job-04-and-job-05)).
- Uncertainty in the mode-fit B/A of 0.992, which the fresh-anchor rule treats as a constant.

## Revision log

Append an entry per result or per revised rule: date, source, what changed. Keep earlier entries as written.

| Date (UTC) | Change |
|---|---|
| 2026-11-07 | First version: the served-mesh facts, the four-term and two-block comparison, the ten mechanisms of the mesh-persistence reading with their review findings, ten design rules and the open questions. No run of the mesh-persistence case exists. |
| 2026-11-07 | Mesh-persistence job `6bc382af` read: fixed per mesh (r 0.9966 against 0.988, same 9 of 46, anchor B/A 1.0876), early-to-late anchor change inside the preregistered 0.03 band (half-job persistence r 0.994 and 0.996, descriptive), failure follows the mesh on fresh seeds (aligned mean -0.0024), fresh anchor B/A 0.84 to 1.05 (median 0.951, sd 0.067; preregistered rule unresolved, slot efficiency excluded), frozen gain model carries (p 0.0016) and the offset model does not (p 0.011), but a post-hoc diagnostic shows the frozen per-mode efficiencies carry it (efficiency-only r 0.484; shifter increments r 0.055 and 0.213), so a static per-shifter map adds little. sim and qpu compile three of 52 requests to different meshes, so a simulator mesh gate compares simulator with simulator. The rule "calibrate slots from many anchor seeds or a per-mesh table" now rests on this job; the center of the anchor-ratio distribution reads near 0.95, so the next case sizes its anchor set against sd 0.067 rather than 0.025. Ledger A5-200 to A5-204; claim hw-ascella-pathion-mesh-persistence. |
| 2026-11-07 | A frozen-map test scores the efficiency-only model and the shifter-map increment over it, since each frozen model carries its own per-mode efficiencies; the mesh-persistence job's "map carries" came mainly from the efficiencies (c1_map_increment.txt: increments p 0.28 gain, 0.041 offset, post hoc), so A5-202 stays open until a preregistered fresh-seed increment test. |
| 2026-11-08 | Status paragraph set to the executed runs; design rule 1 resized on the measured anchor spread (sd 0.067); rule 2 states the confirmed mechanism; the drift statement narrowed to the anchor-change rule (local review of PR #783). |
