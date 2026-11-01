# Belenos per-seed mesh persistence

`scripts/belenos_mesh_persistence.py` builds one `qpu:belenos` job that replays four retained compiled meshes after
the chip's recalibrations. It asks whether a compilation seed is still a hardware setting a day later: whether it
returns the same `computed_circuit`, and whether that mesh's error comes back. No job of this case has been sent; it
waits for the owner's approval of the written case below.

## Question

On `qpu:belenos` the per-seed compiled-mesh error dominates every other error source
([strategy.md](../notes/quandela/strategy.md) section 2): the interleaved mode-swap case measured a per-seed standard
deviation of 0.0515 in a half block's single-click algebra-mode share against binomial errors near 0.007
(claim `qd-belenos-mode-swap-per-seed-mesh-variance`), and the teleportation rehearsal's block contrasts carry a
per-mesh correctness spread of about 0.040 ([design investigation](belenos-best-mesh-design-investigation.md),
finding 2). Within one calibration a seed reproduces its mesh: the teleportation job-02 replay returned all six
meshes 29 minutes later, and every mode-swap primary pair kept one mesh across its two jobs.

The design investigation left one question that decides whether per-seed selection can ever pay: whether a seed's
mesh, and its error, survive a recalibration. If a seed returns a different mesh, or the same mesh with a freshly
drawn error, a best-mesh screen must be repeated after every recalibration and selection buys nothing durable.

## Why a one-photon replay

The mode-swap template puts one photon in each 4-mode slot, so no two photons interfere and the source's HOM and g2
drop out: the share reads the compiled mesh and the detection only. Its mesh signal stands far above its binomial
noise, and a 24-mode iteration of 30,000 samples bills like any other: a job costs 1 credit plus 1e-6 per shot of its
largest iteration's `max_shots` ([credit optimization](../runbooks/quandela-credit-optimization.md)). The
three-photon teleportation replay asks the same question at a binomial error of 0.03 to 0.05 per mesh and 4 to 5
credits per six-iteration job; it is the optional second case below.

## Design

**Group.** Block set 4 is the one set of the mode-swap case whose six blocks are all half blocks (p_algebra 1/2), the
class whose share moves most under a mesh error (2 sqrt(a (1 - a)) per radian); the other sets hold 0 or 4. The rule
"the set with the most half blocks, packed layout" names the group from the block classes alone, before any outcome
of this case. The packed layout of set 4 ran on 2026-10-31 in jobs 09 and 10 (HOM 87.5 %, g2 1.2 %, transmittance
5.42 %) under its primary seed and three replicate seeds.

**Job.** One job of five iterations in the retained relative order: primary, replicate 0, replicate 1, replicate 2,
primary. Each setting is the retained row unchanged (circuit parameters, compilation seed, blocks, operator, source);
only its name and position change, and `--check` holds every other field to the retained row. The seeds are
identifiers of the retained meshes and keep their values: the primary seed is `COMPILATION_SEEDS` index 2k + l of
the mode-swap builder (k 4, l 0) and the replicates are its `REPLICATE_COMPILATION_SEEDS` and `EXTRA_REPLICATE_SEEDS`
values, imported by name. Each iteration takes 30,000 samples with `max_shots` 90,000 and `min_detected_photons` 1,
the mode-swap settings.

**Retained window.** The four meshes of the group, the primary pooled over its two repeats:

| Slot (chip modes) | Primary | Replicate 0 | Replicate 1 | Replicate 2 | Deviation SD | Binomial SE per cell |
|---|---|---|---|---|---|---|
| 0 (0-3) | 0.650 | 0.564 | 0.514 | 0.507 | 0.066 | 0.004-0.006 |
| 1 (4-7) | 0.508 | 0.518 | 0.605 | 0.444 | 0.066 | 0.005-0.007 |
| 2 (8-11) | 0.550 | 0.545 | 0.556 | 0.475 | 0.038 | 0.005-0.007 |
| 3 (12-15) | 0.562 | 0.630 | 0.600 | 0.594 | 0.028 | 0.005-0.007 |
| 4 (16-19) | 0.426 | 0.431 | 0.493 | 0.397 | 0.040 | 0.005-0.007 |
| 5 (20-23) | 0.603 | 0.450 | 0.495 | 0.618 | 0.082 | 0.004-0.007 |

The centered deviations pool to a standard deviation of 0.057 on 18 degrees of freedom, about ten binomial errors per
cell.

## Analysis (`--analyze RUN`)

`analysis.json` is written to the run directory; the frozen `cases.json` must match the run's byte for byte, and all
five iterations must return counts.

- **Identity, the first decision.** Each returned `computed_circuit` is hashed (sha256 of its sorted JSON) and compared
  with the retained digest of the same circuit parameters and seed; both primary repeats must return the primary
  digest. Any mismatch reads **seed does not reproduce its mesh** and withholds everything below. That reading alone
  answers the program's question: a seed that does not survive a recalibration cannot carry a selected mesh.
- **Drift within the new job.** Per block, the two-sample z of the two new primary repeats; D = sum z^2 on 6 degrees
  of freedom. D with p < 0.01 withholds the reading. The retained packed repeats of set 4, which straddled two jobs,
  give D 13.1 (p 0.04).
- **Statistic.** Per block b and mesh j (the pooled primary, then each replicate), e = a - (mean of a over the four
  meshes of b), in the retained window and in the new one. Centering removes every change common to a block's four
  meshes, among them a change of the slot's detection efficiency. T = sum over b and j of e_old e_new.
- **Null.** With no persistence the new mesh labels are exchangeable within each block. The exact one-sided p-value
  is the share of the 24^6 within-block relabelings whose T reaches the observed T, enumerated by splitting the six
  blocks into two halves.
- **Slope.** beta = T / sum e_old^2 regresses the new deviations on the old ones; beta 1 is full persistence and 0 a
  fresh draw. Its one-sided 95 % upper bound uses the residual variance on 24 - 6 - 1 = 17 degrees of freedom.
- **Reading.** **persists** when p < 0.05; **redrawn** when p >= 0.05 and the upper bound on beta is below 0.5,
  half of a mesh's deviation recurring being the least that makes a selected seed worth keeping; **indeterminate**
  otherwise.
- **Secondary, no reading.** The same T and beta on slots 4 and 5 (chip modes 16 to 23, the modes of the teleportation
  layout `(18, 19, 20, 17, 22, 23, 16, 21)`) and with slot 5 excluded, since slot 5 carried the mode-swap case's
  heaviest mesh error (slot homogeneity p 2.5e-8).

## Power

[`results/quandela/belenos-mesh-persistence-power.json`](../../results/quandela/belenos-mesh-persistence-power.json),
from `--power --seed qrng:docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json#2`, runs the analysis's own functions on
2,000 simulated jobs per slope. The new true share of each cell is the retained block mean, plus a slot shift with
standard deviation 0.03 common to the block's meshes, plus beta times the retained deviation, plus sqrt(1 - beta^2)
times a fresh mesh error of standard deviation 0.0515, then a binomial draw at the retained count of the cell.

| Slope beta | persists | redrawn | indeterminate |
|---|---|---|---|
| 0 (fresh mesh error) | 0.047 | 0.730 | 0.223 |
| 0.25 | 0.291 | 0.326 | 0.384 |
| 0.5 | 0.804 | 0.049 | 0.148 |
| 0.75 | 0.9995 | 0 | 0.0005 |
| 1 (full persistence) | 1 | 0 | 0 |

The test holds its size (0.047 at beta 0), a useful persistence (beta 0.5 or more) reads persists in at least 80 % of
jobs and redrawn in under 5 %, and a fresh draw reads redrawn in 73 %. A slope near 0.25, a weak persistence that
would not repay selection, is the region where one job leaves the answer indeterminate.

## Duration and credits

The mode-swap bound gives at most 51.4 s per 30,000-sample iteration, 257 s for five against the 270 s margin of the
300 s cut; the retained packed jobs ran 213 to 245 s. The credit ceiling is 1 + 90,000 x 1e-6 = 1.09.

## What this does not establish

- **Time and recalibration are confounded.** The retained window is 2026-10-31 09:52 to 10:35 UTC; the replay runs a
  day or more later across an unknown number of recalibrations. The result reads as "survives at least one
  recalibration and the elapsed time", with the plan's HOM, g2 and transmittance recorded beside the retained ones.
- **Context.** The retained iterations alternated the packed and swapped layouts; the replay runs the packed layout
  alone. A mesh error that depends on the preceding configuration would read as partial persistence.
- **Transfer.** A persisting one-photon share error on chip modes 0 to 23 makes persistence of the teleportation
  meshes likely but does not show it; the slots 4 and 5 secondary is the closest bridge.

## Written case

- *What it measures.* Whether the four retained compilation seeds of the packed set-4 group return their retained
  `computed_circuit` after the chip's recalibrations, and whether each mesh's deviation from its block's four-mesh
  mean recurs (persistence slope beta, exact within-block relabeling test).
- *Why a simulation cannot answer it.* The deviations are the chip's realized mesh and detection error; an ideal or
  noise-model simulation gives every mesh the target share, and whether the provider's compiler returns the same
  mesh after a recalibration is a property of the service.
- *Backend and budget.* `qpu:belenos`, one job of five iterations of 30,000 samples, `max_shots` 90,000 per
  iteration, `min_detected_photons` 1: 1.09 credits, expected 260 s against the 300 s limit.
- *Procedure.* Copy `results/quandela/cases/belenos_mesh_persistence/job-00/cases.json` and `circuit.json` into a
  fresh run directory under `results/quandela/runs/`, then `scripts/qd_platform.py plan` and `submit` with
  `--platform qpu:belenos --max-credits 1.09 --expected-seconds 260 --per-job-credits 1.0 --admit-status running`,
  `collect`, and `scripts/belenos_mesh_persistence.py --analyze RUN`. The plan records the platform's HOM, g2 and
  transmittance.
- *Stopping rule.* A job that errors, is cut short, or runs longer than 270 s is resubmitted only on the owner's
  further approval. An identity mismatch ends the program question with that reading; a persists or redrawn reading
  ends the case. An indeterminate reading may justify a second job replaying the swapped layout of set 4 (the same
  six half blocks on other slots, 1.09 credits), only on the owner's further approval.

## Optional second case: the teleportation replay

Only if this case reads **persists**, a replay of the twelve job-02 and job-03 teleportation seeds asks whether the
teleportation meshes in particular keep their errors. Grounded in the reviews of the design investigation, it would
run two six-iteration jobs of 1,200 samples (block A's seeds, then block B's after its hashes match), 4.0 to 5.0
credits each at a `max_shots` of 3,000,000 to 4,000,000 per iteration, 8 to 10 credits in all. Its primary
observable would be acceptance per sample within each input (the six A minus B acceptance differences carry
chi-square 65.9 on 6 degrees of freedom, against 20.5 for correctness), with correctness and correct events per sample
beside it, all as within-input contrasts, since input means dominate any correlation of raw per-mesh values. It is
not written as a case here.
