# Belenos per-seed mesh persistence

`scripts/belenos_mesh_persistence.py` builds one `qpu:belenos` job that replays four retained compiled meshes after
the chip's recalibrations. It asks whether a compilation seed is still a hardware setting a day later: whether it
returns the mesh of its retained `computed_circuit`, and whether that mesh's error comes back. No job of this case has been sent; it
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

- **Identity, the first decision.** Perceval's deserializer decodes each returned `computed_circuit` to its 24-mode
  unitary, which is compared with the unitary of the retained `computed_circuit` of the same circuit parameters and
  seed; the two are one mesh when their largest entry difference is at most 1e-4. Phases rounded to single
  precision move an entry by 4.5e-7, a difference of 1e-4 moves a share by at most 2e-4 against a binomial error
  near 0.005, and two seeds of one layout differ by at least 1.2 in the retained window, where the repeats of one
  request returned byte-identical circuits. A change of
  the provider's serialization alone therefore keeps the mesh, and `analysis.json` records the sha256 comparison of
  the serialized circuits beside each unitary distance. Both primary repeats must return the primary mesh. Any
  mismatch reads **seed does not reproduce its mesh** and withholds everything below. That reading alone answers
  the program's question: a seed that does not survive a recalibration cannot carry a selected mesh. An iteration
  that returns no `computed_circuit` reads **an iteration returned no computed_circuit** and decides nothing.
- **Drift within the new job.** Per block, the two-sample z of the two new primary repeats; D = sum z^2 on 6 degrees
  of freedom. D with p < 0.01 withholds the reading, and so does an iteration without single-click counts in a
  block. The retained packed repeats of set 4, which straddled two jobs, give D 13.1 (p 0.04).
- **Statistic.** Per block b and mesh j (the pooled primary, then each replicate), e = a - (mean of a over the four
  meshes of b), in the retained window and in the new one. Centering removes every change common to a block's four
  meshes, among them a change of the slot's detection efficiency. T = sum over b and j of e_old e_new.
- **Null.** With no persistence the new mesh labels are exchangeable within each block. The exact one-sided p-value
  is the share of the 24^6 within-block relabelings whose T reaches the observed T, enumerated by splitting the six
  blocks into two halves.
- **Slope.** beta = T / sum e_old^2 regresses the new deviations on the old ones; beta 1 is full persistence and 0 a
  fresh draw. Under a slope b the residuals e_new - b e_old hold the fresh error alone; with that error
  exchangeable within each block and independent between blocks, each block's labels relabel independently,
  whatever the block's error size. q(b) is the share of the 24^6 within-block
  relabelings of those residuals whose cross product with e_old lies at or below the observed one; it never rises
  with b, and the one-sided 95 % upper bound on beta is the largest b with q(b) >= 0.05
  (`mesh_selection.slope_upper_bound`).
- **Reading.** Half of a mesh's deviation recurring (beta 0.5) is the least that makes a selected seed worth
  keeping. q(0.5) < 0.05 places the upper bound on beta below 0.5: the reading is **recurs below the useful
  slope** when p < 0.05 also shows a slope above zero, and **redrawn** when p >= 0.05. With q(0.5) >= 0.05 the
  reading is **persists** when p < 0.05 and the estimate beta is at least 0.5, and **indeterminate** otherwise.
- **Secondary, no reading.** The same T and beta on slots 4 and 5 (chip modes 16 to 23, the modes of the teleportation
  layout `(18, 19, 20, 17, 22, 23, 16, 21)`) and with slot 5 excluded, since slot 5 carried the mode-swap case's
  heaviest mesh error (slot homogeneity p 2.5e-8).

## Power

[`results/quandela/belenos-mesh-persistence-power.json`](../../results/quandela/belenos-mesh-persistence-power.json),
from `--power --seed qrng:docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json#3`, runs the analysis's own functions on
2,000 simulated jobs per slope and fresh-error model. The new true share of each cell is the retained block mean,
plus a slot shift with standard deviation 0.03 common to the block's meshes, plus beta times the retained deviation,
plus sqrt(1 - beta^2) times a fresh mesh error, then a binomial draw at the retained count of the cell. The fresh
error takes four forms: the half-block class size 0.0515 in every block; each block's own retained spread (0.028 to
0.082); and the class size with half, then all, of its variance carried by one term per mesh across the six blocks.

One error size for every block:

| Slope beta | persists | recurs below the useful slope | redrawn | indeterminate |
|---|---|---|---|---|
| 0 (fresh mesh error) | 0.0095 | 0 | 0.6815 | 0.309 |
| 0.25 | 0.116 | 0.003 | 0.2755 | 0.6055 |
| 0.5 | 0.4945 | 0.006 | 0.0425 | 0.457 |
| 0.75 | 0.9645 | 0 | 0 | 0.0355 |
| 1 (full persistence) | 1 | 0 | 0 | 0 |

Each block's retained spread:

| Slope beta | persists | recurs below the useful slope | redrawn | indeterminate |
|---|---|---|---|---|
| 0 (fresh mesh error) | 0.0245 | 0.0005 | 0.54 | 0.435 |
| 0.25 | 0.1555 | 0.0015 | 0.239 | 0.604 |
| 0.5 | 0.445 | 0.003 | 0.0525 | 0.4995 |
| 0.75 | 0.913 | 0 | 0.001 | 0.086 |
| 1 (full persistence) | 1 | 0 | 0 | 0 |

The two decisive error rates over all four models:

| Fresh-error model | persists at beta 0 | redrawn at beta 0.5 |
|---|---|---|
| one error size for every block | 0.0095 | 0.0425 |
| each block's retained spread | 0.0245 | 0.0525 |
| half of the variance shared by a mesh's blocks | 0.0035 | 0.0305 |
| all of the variance shared by a mesh's blocks | 0 | 0.0015 |

A fresh draw reads persists in at most 2.5 % of jobs. Redrawn at the useful slope stays within sampling error of
0.05 (one standard error is 0.005 at 2,000 jobs) when blocks differ in spread, and falls below it when a mesh's
error is shared across blocks, where the test turns conservative. A useful
persistence of beta 0.75 reads persists in 91 to 98 % of jobs and below the useful slope in at most 0.1 %. Beta 0.5,
the threshold itself, reads persists in 45 to 50 % and indeterminate in 46 to 50 %, since the estimate falls on
either side of it. A weak persistence of beta 0.25 reads persists in 8 to 16 % of jobs, so the optional
teleportation replay below opens for it in at most one job in six, and indeterminate in 53 to 61 %. A fresh draw
reads redrawn in 54 to 73 %.

The first version of this case bounded the slope with a Student-t interval on one residual variance pooled over the
six blocks; under the retained block spreads that bound read redrawn at beta 0.5 in 8 % of jobs against a nominal
5 %, and persists carried no slope floor. The review of this case
([reconciliation](../archive/reviews/belenos-mesh-persistence-pr729-reconciliation.md)) records the measurement and
the replacement.

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

- *What it measures.* Whether the four retained compilation seeds of the packed set-4 group return the mesh of
  their retained `computed_circuit` after the chip's recalibrations, and whether each mesh's deviation from its block's four-mesh
  mean recurs (persistence slope beta, exact within-block relabeling test and the upper bound that inverts it).
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
  further approval. An identity mismatch ends the program question with that reading; a persists, recurs below
  the useful slope or redrawn reading ends the case. An indeterminate reading may justify a second job replaying the swapped layout of set 4 (the same
  six half blocks on other slots, 1.09 credits), only on the owner's further approval.

## Scheduled submission

The owner approved this case on 2026-11-06, while `qpu:belenos` read `unreachable` (Explorer availability 0 % on
2026-11-02 to 2026-11-04 and 2026-11-06, 2.19 % on 2026-11-05) and its processor record lacked `specs.architecture`,
so `qd_platform.py plan` refuses it. The schedule
[`belenos-mesh-persistence.json`](../../results/quandela/schedules/belenos-mesh-persistence.json) carries the job
for the workflow of [quandela-scheduled-runs](../runbooks/quandela-scheduled-runs.md), disabled and unpinned until
the chip returns; `qd_schedule.py pin` then plans it read-only, and the merge of `enabled: true` with the pinned body
is the submission act the approval covers. Its plan check, `belenos_mesh_persistence.py --plan-check`, refuses a plan
of another case, platform or ceiling and a record whose photon rate would push five iterations past the 270 s margin:
the measured 50 s iteration already holds 6,000 samples at job-00's photon rate, which a slower record stretches
too, so the check charges the 50 s as setup plus 1 / (clock x efficiency) for each of the 30,000 samples. The
efficiency must reach 30,000 / (clock x 4 s), and the check scales job-00's lowest global efficiency 0.0034 by the
record's Transmittance (%) against job-00's plan-time 4.89 % (hypothesis: the global efficiency follows the record
transmittance). At 4.94 MHz the floor is 2.18 %; the record of 2026-11-06 reads 5.23 %. The matched check runs
`--analyze` on the collected run.

**Deferred while the chip is unreachable.** A read-only recovery watch planned this case against `qpu:belenos`
every 30 minutes from 2026-11-06 18:21 UTC, and every plan through 2026-11-07 04:00 UTC was refused with the chip
`unreachable`; the processor record of 2026-11-07 still lacks `specs.architecture` and its command set, and its
figures (HOM 88.2 %, g2 1.3 %, transmittance 5.23 %) are those of its last calibration. The watch only plans and
reports; it neither pins nor enables the schedule, which stays disabled and unpinned. The per-seed persistence
question meanwhile runs on Ascella, whose
[prospective correction case](ascella-signed-coherence-conformance.md#prospective-correction-case-job-09) scores a
frozen per-seed table on a fresh repeat. The case resumes when `qd_platform.py plan` accepts it: `qd_schedule.py pin`
plans the schedule read-only, the plan check runs on that plan, and the change to `enabled: true` is the submission
the 2026-11-06 approval covers.

## Optional second case: the teleportation replay

Only if this case reads **persists**, a replay of the twelve job-02 and job-03 teleportation seeds asks whether the
teleportation meshes in particular keep their errors. Grounded in the reviews of the design investigation, it would
run two six-iteration jobs of 1,200 samples (block A's seeds, then block B's after its meshes match), 4.0 to 5.0
credits each at a `max_shots` of 3,000,000 to 4,000,000 per iteration, 8 to 10 credits in all. Its primary
observable would be acceptance per sample within each input (the six A minus B acceptance differences carry
chi-square 65.9 on 6 degrees of freedom, against 20.5 for correctness), with correctness and correct events per sample
beside it, all as within-input contrasts, since input means dominate any correlation of raw per-mesh values. It is
not written as a case here.
