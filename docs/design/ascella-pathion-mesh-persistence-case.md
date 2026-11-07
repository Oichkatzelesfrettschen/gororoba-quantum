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
generator, 17 the bootstrap generator (reserved; the frozen decisions draw none). Every value is nonzero, distinct and
unused by the original job. The replay keeps the original job's seeds as identifiers of the meshes it reproduces
(AGENTS.md, Seeds).

## Preregistered decisions

The thresholds live in the builder's `PREREGISTERED` and in `cases.json` (`preregistered`); the reading script holds
them as code and its test runs it on synthetic runs built from the retained record.

| Decision | Statistic | Reading rule |
|---|---|---|
| mesh gate (sim run) | largest entry modulus of each replay iteration's served unitary minus the original job's under the same setting | every one at most 1e-6, or the QPU job is not sent |
| admission | replayed anchors and darks: raw anchor level, dark share, sentinel share | the predecessor's 0.90 floor, 0.05 ceiling, 0.05 share |
| persistence | Pearson r of the 46 calibrated replay mirror differences with the original ones, p from 20,000 relabelings | fixed per mesh at p < 0.01 with r at least 0.989 (the one-sided 99 percent Fisher bound of the counting ceiling 0.995); partly fixed at p < 0.01 below it; not reproduced otherwise. The raw-level r is reported beside it |
| anchor replay | replayed B/A | within 0.02 of 1.082: anchor error fixed per mesh; otherwise moved |
| fresh anchors | the seven per-seed B/A | median within 0.03 of 0.992 and standard deviation above 0.012: anchor ratio follows the mesh; every one within 0.03 of 1.082: slot efficiency; otherwise unresolved |
| fresh failing | Pearson r of the nine fresh raw mirror differences with the original raw ones, relabeling p | r at least 0.6 at p < 0.01: failure follows the block and slot; otherwise failure follows the mesh |
| frozen map | the gain and offset maps of `c1_static.npz` (keys `x_`, `a_`, `c_` with `_gain_all` and `_offset_all`, frozen in commit cc8d8107c before this case) applied to each fresh iteration's returned circuit; Pearson r of predicted against observed raw level departures, centered within kind | map carries at one-sided p < 0.005 (t on n - 1 - kinds degrees of freedom; Bonferroni over the two maps), with its share r^2 / ceiling; otherwise does not carry |
| correction | the original job's per-iteration calibrated departures applied as a per-mesh table to the replay | at most 4 of 46 mirror differences above 0.07; rms before and after reported |

Raw levels carry no calibration, so the fresh-failing and frozen-map decisions compare meshes without the anchor
pair; dividing both sides by the replayed anchors would put the shared B/A gain into both and bias the fresh
comparison toward "follows the block".

Predictions under each reading (`--plan`; counting standard error of a level 0.0018 at L = 0.25 to 0.0028 at L = 1):

| Reading | Persistence r | Replay B/A | Fresh B/A | Fresh failing r | Frozen map |
|---|---|---|---|---|---|
| per-mesh fixed | at least 0.989 | 1.082 +- 0.02 | median 0.992, sd about 0.025 | near 0 | weak (prior art r 0.16 to 0.32) |
| static per-shifter map | high | 1.082 | spread set by the map | partial | carries at p < 0.005 |
| slot efficiency | high | 1.082 | every seed near 1.082, sd about 0.004 | at least 0.6 | not decisive |
| drift | below 0.989 | moved | | | |

Outcome onto ledger A5-191: fixed per mesh, anchor fixed, fresh ratio following the mesh, failure following the mesh
and no carrying map rewrite the row to "per-mesh fixed errors, the anchor pair's among them"; a carrying map keeps the
per-shifter clause with its measured share; "not reproduced" refutes the static reading in favor of drift. The
pathion block cases then take their slot efficiencies from many anchor seeds (or a per-mesh table), which the fresh
anchors of this job size.

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
plan` at 16:38 UTC: `sim:ascella` credit ceiling 1.0, body sha256 `ffb09ba6b44b4eb86c742dc409453e92d7defe1a17a6f62c3f921a6f00717dfe`;
`qpu:ascella` credit ceiling 1.131072 (1 + 1e-6 x 131,072), body sha256
`445683dc52c010ff352102634ee2202f27468101b6ea698ab4f5076c615a3efe`, Explorer `running`, processor `available`;
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
