# Ascella mesh-persistence case: what failed the two-block mirror test

Written case for one `sim:ascella` gate job and one `qpu:ascella` job of 84 single-photon iterations, the successor of
the [two-coset-block case](ascella-pathion-coset-block-pairs-case.md). Builder
[`scripts/ascella_pathion_mesh_persistence.py`](../../scripts/ascella_pathion_mesh_persistence.py), reading
[`scripts/ascella_pathion_mesh_persistence_analysis.py`](../../scripts/ascella_pathion_mesh_persistence_analysis.py),
test `tests/scripts/test_ascella_pathion_mesh_persistence.py`. Nothing has been submitted.

## The question

The two-block job (`db6355f7`, run `2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00`) read 9
of 46 mirrored block readings more than 0.07 apart against an allowance of 4, so its instrument was not admitted
(ledger A5-189, refuted). Its `sim:ascella` gate run reads 0 of 46, maximum 0.0066
([mirror_test_sim.txt](../evidence/pathion-kernel-map/conjectures/mirror_test_sim.txt)), so the failure enters on the
chip, not in the analysis or the compilation. Ledger A5-191 holds the surviving hypothesis: the failure follows the
per-slot anchor calibration (B/A 1.082 from the anchor pair against 0.992 from the other meshes; 1 of 46 fail without
the division), with a static phase error of about 0.02 rad per shifter as the residual.

The retained record supports two readings of that hypothesis, and this job separates them:

| Reading | What it says | Evidence for | Evidence against |
|---|---|---|---|
| per-mesh fixed error | every served mesh (seed with its circuit parameters) carries its own fixed departure from its programmed law; the slot efficiencies come from one anchor mesh per slot, so the anchor pair's own errors set B/A | the signed-coherence program on this chip: a seed serves the byte-identical mesh nine hours and twelve days later, its error persists at the counting ceiling (r 0.885 at ceiling 0.880; r 0.958 at 0.956), and a per-seed table removes about 90 percent of the per-mesh variance ([signed-coherence design](ascella-signed-coherence-conformance.md), seed-repeat, long-horizon and prospective-correction cases) | none on the pathion meshes yet |
| static per-shifter map | one offset or gain per physical shifter acts on every mesh | fitted on one slot orientation it predicts the other at r +0.54 to +0.88 ([c1_static.txt](../evidence/pathion-kernel-map/conjectures/c1_static.txt), [c1_heldout.txt](../evidence/pathion-kernel-map/conjectures/c1_heldout.txt)), beats shuffled links ([c1_static_null.txt](../evidence/pathion-kernel-map/conjectures/c1_static_null.txt)), and reproduces about half the anchor excess in-sample ([c1_anchor_map.txt](../evidence/pathion-kernel-map/conjectures/c1_anchor_map.txt): B/A 1.033 to 1.053) | on unseen meshes the signed-coherence offsets carried r 0.157 and 0.319 (share 2.5 and 10.5 percent, new-seed score) |

A true slot efficiency of 1.08 and drift between configurations are the two other candidates; the mode fit of the
original job already argues against the first (0.992), and the signed-coherence program found no predecessor effect
(rho 0.06).

## Design

84 iterations at 131,072 samples, `max_shots` 131,072, order fixed in the builder:

- replay (52): every setting of the original job, sent verbatim (its compilation seed and circuit parameters byte for
  byte), in the original palindromic order split around the fresh block. The builder rebuilds each from cd_core and
  requires the identical seed, orientation and role and the target operator and laws within 1e-12; the template
  decomposition is degenerate (equal columns from phases that differ by pi/2), so the rebuilt parameters are not the
  request.
- fresh anchors (14): the anchor design (A16 block 4 at level 1 beside A16 block 5 in its kernel) at 7 new seeds, each
  in both slot orientations, so each seed gives its own B/A.
- fresh failing settings (16): the eight settings that carry the nine failing readings (a-h-NN, b-i-NN, c-d-TD,
  c-d-TN, c-d-TT, e-b-TT, g-h-TT, i-f-TC), each at one new seed in both orientations.
- fresh dark (2): the dark design at one new seed in both orientations.

Seeds: [`draw-2026-11-07T162910Z.json`](../evidence/anu_qrng/draw-2026-11-07T162910Z.json), 18 uint16 values in index
order: 0 to 6 fresh anchor seeds, 7 to 14 one seed per failing setting, 15 the dark seed, 16 the permutation
generator, 17 the seed-block relabeling generator of the frozen maps. Every value is nonzero, distinct and
unused by the original job. The replay keeps the original job's seeds as identifiers of the meshes it reproduces
(AGENTS.md, Seeds).

## Preregistered decisions

The thresholds live in the builder's `PREREGISTERED` and in `cases.json` (`preregistered`); the reading script holds
them as code, and its tests run it on synthetic runs built from the retained record. The readings are not exclusive:
each decision names what it excludes, a mixture of carriers is allowed, and every decision can read "not read" (a
partial run, or a non-finite or constant correlation input) or "unresolved".

| Decision | Statistic | Reading rule | What it excludes |
|---|---|---|---|
| mesh gate (sim run) | the run's `cases.json` against the frozen `sim-00` bytes; 84 results with echoed seeds and parameters; the 52 replay original names, each once; largest entry modulus of each replay served unitary minus the original job's | every check holds and every gap is at most 1e-6, or the QPU job is not sent | a QPU job on meshes other than the original ones |
| admission | replayed anchors and darks: raw anchor level, dark share, sentinel share | the predecessor's 0.90 floor, 0.05 ceiling, 0.05 share | an instrument outside the predecessor's admission |
| persistence | Pearson r of the 46 calibrated replay mirror differences with the original ones | at or above 0.9919 (`persistence_plan.json`): fixed per mesh; below it with relabeling p < 0.01: partly fixed; otherwise not reproduced. The raw-level r is reported beside it | at or above: a redraw of the per-mesh errors between the jobs |
| within-job control | the same r on the replay's early and late halves; the early and late replayed anchors | anchors more than 0.03 apart read drift within the job | drift within the job, the only drift this case reads |
| anchor replay | replayed B/A | within 0.02 of 1.082: anchor error unchanged; otherwise moved | a change of the anchor pair's error |
| fresh anchors | the seven per-seed B/A | median within 0.03 of 0.992 with standard deviation above 0.012: anchor ratio follows the mesh; every seed within 0.03 of 1.082: slot efficiency; otherwise unresolved | follows the mesh: a slot efficiency of 1.08; slot efficiency: the per-mesh anchor reading |
| fresh failing | aligned mean A = mean over the nine failing items of sign(original raw d) x fresh raw d; carried fraction A / 0.0376 with its 99 percent interval | A at or above 0.0196: follows the design; A below 0.0181: follows the mesh; between: unresolved | follows the design: a purely per-mesh failure; follows the mesh: a design-tied failure at the original size |
| frozen map | the gain and offset maps of `c1_static.npz` (frozen in commit cc8d8107c) on each fresh iteration's returned circuit (BS.Rx checked); Pearson r of predicted against observed raw departures, centered within kind | p from 20,000 relabelings of whole compilation-seed blocks (both orientations and slots of a seed together), one-sided below 0.005 per map: map carries, with share r^2 / ceiling (ceiling from each row's multinomial variance) | does not carry: a static map carrying the per-mesh error at the size the test resolves |
| correction | the original job's per-iteration calibrated departures applied as a per-mesh table to the replay | at most 4 of 46 mirror differences above 0.07 | a per-mesh table failing to correct a fixed error |

Raw levels carry no calibration, so the fresh-failing and frozen-map decisions compare meshes without the anchor
pair; dividing both sides by the replayed anchors would put the shared B/A gain into both and bias the fresh
comparison toward "follows the design".

Error rates and cutoffs (`persistence_plan.json`, from [`draw-2026-11-07T165920Z.json`](../evidence/anu_qrng/draw-2026-11-07T165920Z.json)
value 0 for the resampling and value 1 for the classification; the audit test rebuilds it):

- Persistence: 2,000 pairs of jobs resampled from the original job's per-iteration click laws at 131,072 samples,
  each calibrated with its own anchor and dark rows, give r with first percentile 0.9919 and median 0.9963. The cutoff
  is that first percentile, so a fixed per-mesh error reads "fixed per mesh" in 99 percent of jobs; a redraw gives r
  near 0 against 46 pairs.
- Fresh anchors: under the per-mesh reading (median 0.992, sd 0.025) the rule reads "follows the mesh" in 95.5 percent
  and "unresolved" in 4.5 percent; under the slot reading (1.082, sd 0.0039) it reads "slot efficiency" in 100 percent.
  The bands are engineering thresholds, and these rates are their calibration.
- Fresh failing: the aligned-mean standard error is 0.0084 for nine items (per-mesh raw spread 0.0251 of the original
  46 raw differences). A design-tied failure at the original size reads "follows the design" in 98.4 percent and
  "follows the mesh" in 1.0 percent; a per-mesh failure reads "follows the mesh" in 98.5 percent and "follows the
  design" in 1.0 percent.

Predictions under each reading:

| Reading | Persistence r | Replay B/A | Fresh B/A | Fresh failing A | Frozen map |
|---|---|---|---|---|---|
| per-mesh fixed | at least 0.9919 | 1.082 +- 0.02 | median 0.992, sd about 0.025 | below 0.0181 | weak (prior art r 0.16 to 0.32) |
| static per-shifter map | high | 1.082 | spread set by the map | partial carried fraction | carries at p < 0.005 |
| slot efficiency | high | 1.082 | every seed near 1.082, sd about 0.004 | at or above 0.0196 | not decisive |
| redraw or drift between jobs | below 0.9919 | may move | | | |

Outcome onto ledger A5-191: the row is rewritten to the carriers the decisions leave standing. Persistence fixed per
mesh, a fresh anchor ratio following the mesh and a failure following the mesh with no carrying map give "per-mesh
fixed errors, the anchor pair's among them"; a carrying map adds the per-shifter clause with its share; a design-tied
carried fraction adds a block or slot term of that size; "not reproduced" leaves redraw and drift between the jobs
unresolved unless the within-job control reads drift. The pathion block cases then take their slot efficiencies from
many anchor seeds or a per-mesh table, sized by the fresh anchors of this job.

## Review and the changes it made

A Codex review (gpt-daybreak-blue at high effort, `docs/local/reviews/codex-ascella-report.md`, untracked) read the
first version and ranked eight findings; each is fixed in the builder, the reading script or this document:

| Finding | Change |
|---|---|
| the nine-item correlation had about 25 percent power at r 0.6 and read non-rejection as "follows the mesh" | replaced by the aligned mean with both error rates near 1 percent and an "unresolved" band |
| the mesh gate could pass an incomplete or duplicated replay set | the gate binds the frozen `sim-00` bytes, the result count, the echoed requests and the 52 names once each; tests cover a changed, missing and duplicated replay and a foreign manifest |
| the outcome map treated the readings as exclusive and read drift from low persistence | the decisions name what each excludes, mixtures are allowed, and drift is read only from the within-job control |
| the frozen-map p counted 64 correlated readings as independent | relabelings move whole compilation-seed blocks; the ceiling uses each row's multinomial variance |
| the persistence cutoff was a homoscedastic plug-in | the fixed-mesh resampling of the full calibrated statistic sets it at 0.9919 |
| non-finite or constant inputs became mechanism labels | every correlation returns "not read" on such input; a test covers it |
| the frozen-map topology check omitted the beam-splitter convention | every served beam splitter must be BS.Rx |
| the specification test missed the 15 s budget on a cold cache | the unmarked test runs two settings; the full check stays the `--spec-check` command |

## Published imperfections, simulated

`--spec-check` runs Perceval 1.3.1's `NoiseModel` with the processor record read 2026-11-07 (g2 2 percent,
indistinguishability 0.8898) through threshold detectors on the anchor and every failing setting in both orientations,
post-selected on one click as the analysis is: the largest level shift is 0.0026. Dark counts (68 to 340 per second
per mode at a 13.33 MHz clock, against a 5.46 percent transmittance) bound a level shift by 0.0030. Both sit an order
below the 0.07 to 0.11 failures, so the published imperfections are not the mechanism; transmittance scales every mode
alike and drops out of a ratio.

## Why a simulation cannot answer it

The question is which property of the served meshes fails the mirror test. Local SLOS returns the ideal law for every
seed, Perceval's `SimulatedComputer` uses `compilation_seed` for random phase noise rather than the remote
compilation, and `sim:ascella` read the original request at 0 of 46. Whether the original anchor and sign meshes still
carry their errors, and what errors seven new anchor meshes and eight new failing meshes carry, are measurements of the
chip.

## Live state and cost

`qd_platform` read `qpu:ascella` available at 15:45 UTC on 2026-11-07, token occupancy 0 of 1. `scripts/qd_platform.py
plan` at 17:14 and 17:16 UTC: `sim:ascella` credit ceiling 1.0, body sha256 `cc6e1c1ced0a79f0c81a19fdb3d8739fe4dccb5e89a8a5d3e7532c8ea754d6f0`;
`qpu:ascella` credit ceiling 1.131072 (1 + 1e-6 x 131,072), body sha256
`47e146cfb15515846bfcd6553e351f90b1e51277afff8970320a4484bc539224`, Explorer `running`, processor `available`;
11,010,048 estimated shots each. Expected seconds: 84 x 3.2 = 268.8 against the 270 s packing margin of the 300 s cut
(the original job ran 52 iterations in 161 s, 3.10 s each). The binding plan at submission replaces the plan quoted
here.

## What made the earlier Ascella runs succeed, and what failed

- The four-term block case (`f3a11b5f`) passed every preregistered rule with one block per photon: one mesh per block
  reading, no division by a slot anchor, and a `sim:ascella` gate first.
- The two-block case folded two blocks onto one photon and calibrated each slot with one anchor mesh. The fold saved
  reconfigurations but put one mesh's fixed error into every reading of its slot, which this case tests directly.
- The signed-coherence program established the tools this case reuses: a seed serves the same mesh across days and
  software updates, a per-seed table corrects it, and a static element map transfers little to unseen meshes. Queue
  position: job-09 queued behind another user's job, so a running Explorer row means waiting, not refusal.

## Execution (not run)

On the owner's approval, with `PYTHON` set and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` exported, and
`C=results/quandela/cases/ascella_pathion_mesh_persistence`:

```sh
"$PYTHON" scripts/qd_platform.py submit --platform sim:ascella --max-credits 1.14 --expected-seconds 90 \
  --per-job-credits 1 --admit-status running --approval "<the owner's approval, quoted>" "$C/sim-00"
"$PYTHON" scripts/qd_platform.py collect RUN_DIR_OF_SIM
"$PYTHON" scripts/ascella_pathion_mesh_persistence_analysis.py --mesh-gate RUN_DIR_OF_SIM   # exit 1 stops here
"$PYTHON" scripts/qd_platform.py plan --platform qpu:ascella --max-credits 1.14 --expected-seconds 268.8 \
  --per-job-credits 1 --admit-status running "$C/job-00"
"$PYTHON" scripts/qd_platform.py submit --platform qpu:ascella --max-credits 1.14 --expected-seconds 268.8 \
  --per-job-credits 1 --admit-status running --approval "<the owner's approval, quoted>" "$C/job-00"
"$PYTHON" scripts/qd_platform.py collect RUN_DIR_OF_QPU
"$PYTHON" scripts/ascella_pathion_mesh_persistence_analysis.py --analyze RUN_DIR_OF_QPU \
  --out results/quandela/ascella_pathion_mesh_persistence_analysis.json
```

The runtime seed rows (`ci/seed_provenance.py --add-runtime`) land in the change that retains the runs.

## Not run

- Both jobs: they wait for the owner's approval of this case after the local review.
- A noise model of the per-mesh error itself: no published model exists, and the retained per-mesh residuals of the
  original job are what the replay measures.
- Static non-unitary per-path loss: per-component loss is not retained.
