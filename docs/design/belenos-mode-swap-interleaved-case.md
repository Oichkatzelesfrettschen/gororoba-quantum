# Belenos interleaved mode swap

`scripts/belenos_mode_swap_interleaved.py` builds three `qpu:belenos` jobs. They separate the placement of a packed
box-kite block on the chip from drift in time.

## Question

Registry claim `qd-belenos-packed-mode-swap` compares two series that hold the same packed sign blocks in different
4-mode slots: `box_kite_photonic_packed` and `box_kite_photonic_packed_swapped`, which moves every block three of six
slots. The single-click algebra-mode share a of 26 of 32 blocks changed by more than 4.5 two-sample standard errors.
The slot predictor of `scripts/qd_packed_mode_swap_analysis.py` reads r = -0.585, so the residual follows the chip
modes with a reversed sign. The claim's boundary is the gap: the two series ran as separate jobs about an hour apart,
so placement is not separated from drift.

## Design

Each block set k (the six blocks of `box_kite_photonic_packed/job-0k`) runs as four template iterations in the order
packed, swapped, swapped, packed. Both layouts put the six photons on chip modes 0, 4, 8, 12, 16 and 20, so one
template circuit serves every iteration: six independent 4-mode triangular meshes, one per slot, whose parameters
reproduce the retained block-diagonal unitary of the packed or swapped `circuit.json`. `--check` holds every
iteration to that unitary within 1e-9.

The two repeats of one layout carry the same circuit parameters and the same compilation seed, so they request one
compiled mesh. The teleportation job-02 replay of 2026-10-31 showed that the service returns the same
`computed_circuit` for the same parameters and seed, and that per-seed meshes carry fixed errors of their own
([ascella-belenos-entanglement-teleportation.md](ascella-belenos-entanglement-teleportation.md#split-recovered-chip-rehearsal-job-02-and-job-03)).
A repeat pair therefore isolates drift, and the packed-swapped contrast measures placement together with each
layout's mesh.

| Job | Block sets | Iterations | Blocks |
|---|---|---|---|
| job-00 | 0, 1 | 8 | 12 |
| job-01 | 2, 3 | 8 | 12 |
| job-02 | 4 | 4 | 6 |

Set 5 holds two photons, not six, so its input differs and it stays out. The case covers 30 of the 32 blocks.

**Compilation seeds.** One seed per set and layout, in job, set and layout order (packed, swapped): indices 0 to 9
of the ANU QRNG draw [`draw-2026-10-31T043029Z.json`](../evidence/anu_qrng/draw-2026-10-31T043029Z.json),
registered in [`allocations.json`](../evidence/qrng_seeds/allocations.json). Both repeats of a layout take the same
value.

## Analysis (`--analyze RUN`)

- **Binding.** A result iteration binds by its echoed circuit parameters and compilation seed. The two repeats of a
  layout share both, so they bind in returned order. An iteration without counts (the missing, malformed or error
  entry of a cut-short job) binds to nothing and is counted.
- **Observable.** Per block and iteration, a is the share of samples with exactly one click in the block's slot that
  land on an algebra mode, as in `qd_packed_mode_swap_analysis.py`.
- **Drift.** For each block and layout, z is the two-sample z between the two repeats. Pairs whose returned
  `computed_circuit` digests agree enter D = sum z^2, which is tested against chi-square with that many degrees of
  freedom. Drift is detected at p < 0.01. A pair with differing digests stays descriptive.
- **Placement.** For each block, z is taken between the pooled packed and pooled swapped shares; a block moved when
  |z| > 4.5.
- **Slot predictor.** `decide()` of `qd_packed_mode_swap_analysis.py` runs on the pooled shares and returns the
  verdict block, slot, mixed or undetermined.

Reading: moved blocks with no detected drift place the residual on the chip modes and their meshes. Detected drift of
the size of the earlier moves puts the earlier claim's separation in doubt.

## Written case

- *What it measures.* Whether the packed series' block residual follows placement or time, within one job per pair of
  block sets, with mesh-identical repeats as the drift reference.
- *Why a simulation cannot answer it.* The residual is the chip's compiled-mesh and detection error at each slot; an
  ideal or noise-model simulation gives every block its exact share at every slot.
- *Backend and budget.* `qpu:belenos`, three jobs submitted one after the other. Each iteration takes 15,000 samples,
  with a `max_shots` cap of 45,000 per iteration and `min_detected_photons` 1. The credit ceiling is 1.045 per job
  (1 + 45,000 x 1e-06), 3.135 for the case; Quandela bills each job its ceiling. The live plan of 2026-10-31 estimated
  20,000 shots per 20,000-sample iteration, one detection event per sample. The retained packed jobs took 53 to 55 s
  for one iteration of 60,000 samples. With the 6.9 s fixed-cost bound, an iteration of 15,000 samples takes about
  20 s, so eight take about 165 s. Expected seconds are 240 for job-00 and job-01 and 120 for job-02, all under the
  300 s limit.
- *Procedure.* Copy `cases.json` and `circuit.json` of the job into a fresh run directory under
  `results/quandela/runs/`, then run `scripts/qd_platform.py plan` and `submit` with `--platform qpu:belenos
  --max-credits 1.045 --expected-seconds 240 --per-job-credits 1.0 --admit-status running` (expected seconds 120 for
  job-02), `collect`, and `scripts/belenos_mode_swap_interleaved.py --analyze RUN`.
