# Candidate loss channels for the walk readout0 floors

`result.json` is the output of `scripts/walk_scaffold_channels.py`. It ran
as Kaggle kernel version 2 of `gororoba-walk-scaffold-channels` in 8,902 s,
and the run is retained under
`results/kaggle/2026-10-16T102614Z-gororoba-walk-scaffold-channels/`.

- **Machine and software.** Two Tesla T4 GPUs, Python 3.13.15, qiskit 2.5.2
  and qiskit-aer-gpu-cu11 0.17.2, with four workers
  (`kaggle_environment.json`).
- **Stack proof.** The kernel built the hypercomplex package stack and
  regenerated the retained tables byte for byte before its entry ran
  (`kaggle_hypercomplex.json`).
- **Inputs.** `members.json` and `members.qpy` hold the 56 walk members
  of the Fez ripple run 2026-10-13T025444.603480Z and the Kingston run
  2026-10-15T031229.371738Z. For each member they give its circuit on its
  four qubits with the template's layer barriers, its hardware counts and
  the recorded replay, with the sha256 of every source file.

## Question

Every ripple walk member executes the same 252-CZ scaffold on its lane
(`docs/evidence/walk-control-scaffolding/README.md`). The readout0
member's floor, P(0000) of 0.064 to 0.336 on hardware against 0.540 to
0.666 in the calibrated replay, comes from structured, non-depolarizing loss
(hypothesis 3 there). This run asks which single extra channel, added to
live_run's calibrated noise model, reproduces that floor.

**Falsifier, stated before the run.**
- A candidate passes the readout0 gate when its deviance G^2 against the
  saturated law has p >= 0.01.
- It reproduces the floor only when its parameters, fitted on readout0 and
  frozen, also predict the lane's 13 other members with G^2 p >= 0.01 and a
  higher log-likelihood than the scheduled baseline.

## Method

1. **Per-member model.** Each member keeps its layer barriers and is
   scheduled as late as possible against the Target durations of the
   calibration it executed under (`docs/evidence/calibration/history/`).
   It is then simulated with live_run's gate, idle and assignment noise on
   its four qubits.
2. **Candidates.** Six candidates are added on top of that scheduled model,
   each with one parameter per qubit (per CZ edge for the conditional phase):

| Candidate | Operation | Bounds |
| --- | --- | --- |
| end_flip | 0 -> 1 flip of each qubit before readout (a hidden readout fault, or leakage read as 1) | 0 to 0.5 |
| sx_overrotation | RX(eps) after every SX | +-0.15 rad |
| cz_local_phase | RZ(zeta) on each qubit after every CZ it joins | +-0.15 rad |
| cz_conditional_phase | CP(phi) after every CZ on an edge | +-0.15 rad |
| extra_damping | amplitude damping after every CZ on its qubits | 0 to 0.2 |
| extra_depolarizing | depolarizing after every CZ on its qubits | 0 to 0.2 |

   A coherent angle error delta per gate costs about delta^2 / 4 of gate
   infidelity, so the calibrated CZ and SX errors near 2e-3 and 3e-4 put
   |delta| near 0.09 and 0.035 rad. The coherent bounds sit above both.
3. **Fit and score.** Each candidate is fitted to the lane's readout0
   counts by maximum likelihood. The coherent likelihood winds with the
   angle accumulated over about 100 gates per qubit, so the three coherent
   candidates take a seeded global search: differential evolution from a
   Sobol population (seed 20261016, population 10 per parameter, 60
   generations), polished by L-BFGS-B. The incoherent candidates run
   L-BFGS-B from two fixed starts at 0.05 and 0.3 of the bound. The fitted
   parameters are then frozen and scored on readout1 and the 12 depth
   members of the same lane.

**Checks on the pipeline**, all enforced by the run:
- **Algebra.** Every member's noiseless law equals its `cd_core` ideal to
  4.4e-15: `ripple_experiments._walk_ideal` for the depth members, a point
  mass for the readout controls.
- **Zero parameters.** With every parameter at zero, each candidate
  reproduces the scheduled baseline to 5.0e-16.
- **Baseline against the record.** The unscheduled baseline reproduces each
  member's recorded replay. The largest of the 56 multinomial deviances is
  37.3 on 15 degrees of freedom, p = 0.06 after the 56-fold correction.
- **Algebra packages.** The 80 distinct dim-32 products behind the two walk
  pairs' associator patterns agree with `cd_core.cd_sign` in
  python-hypercomplex 0.3.4 (exact `Fraction` coefficients) and in
  python-hypercomplex-engine 0.5.0, under the identity map
  `docs/notes/packages/` declares.

## Result

No candidate reproduces the floor in any lane. Held-out G^2 runs from 2,955
to 31,661 on 195 degrees of freedom, so every held-out p is 0.

| Lane | Hardware P(0000) | Scheduled baseline | Passes the readout0 gate (p) | Best held-out candidate (log-likelihood gain over baseline) |
| --- | ---: | ---: | --- | --- |
| Fez 1-4 | 0.064 | 0.543 | cz_local_phase (0.018) | extra_depolarizing (+4,679) |
| Fez 13-15, 19 | 0.131 | 0.593 | none (best sx_overrotation, p = 9e-7) | extra_depolarizing (+3,774) |
| Kingston 80-83 | 0.336 | 0.560 | none (best extra_damping, p = 2e-17) | extra_depolarizing (+1,296) |
| Kingston 59, 73-75 | 0.251 | 0.675 | cz_local_phase (0.30), end_flip (0.028) | extra_depolarizing (+2,325) |

1. **The floor's shape and the depth members' loss disagree.**
   - Kingston 59, 73-75: both candidates that fit its readout0 floor
     predict its held-out members worse than no extra channel, by 2,716
     (cz_local_phase) and 384 (end_flip) in log-likelihood.
   - Fez 1-4: cz_local_phase fits readout0 and raises the held-out
     log-likelihood by 3,947, yet leaves held-out G^2 at 7,202 on 195
     degrees of freedom.
   - Extra depolarizing improves the held-out members most in all four
     lanes while failing every readout0 gate (p <= 4e-5).
   - So the structure of the identity-equivalent floor and the loss the
     depth members show are not one single-parameter-per-qubit mechanism of
     any of these forms.
2. **Many fits run to their bounds.**
   - Nine of the twelve coherent fits reach +-0.15 rad on at least one
     qubit or edge, the Fez 1-4 cz_local_phase pass among them (-0.15 rad
     on qubit 4). The coherent exclusion therefore holds within +-0.15
     rad, and a fit at the bound asks for more coherent error than the
     calibration reports.
   - Damping reaches 0.2 per CZ in three lanes, flips reach 0.5 on qubits 2
     and 3 of Fez 1-4, and depolarizing reaches 0.2 per CZ on qubit 1 there:
     rates no calibrated device shows.
3. **End-of-circuit flips** model a hidden readout fault and leakage read as
   1 alike. This run cannot separate the two. The held scaffold A/B case
   (measure-only against the 252-CZ template on Kingston 80-83) does,
   because a readout fault survives without the scaffold and leakage does
   not.
4. **Scheduled idles help, but little.** Scheduling the idles, which the
   recorded replay omits, raises the held-out likelihood in every lane by 519
   to 1,166. It leaves readout0's P(0000) near the replay's (0.543 to 0.675).

## Limits

- **Single-mechanism candidates only.** Each candidate is one mechanism with
  one parameter per qubit or edge. Combinations (for example depolarizing
  plus a local phase), crosstalk from spectators outside the lane, and
  non-Markovian or drifting errors are outside this run.
- **Calibration identity.** Each member uses the snapshot of the
  calibration it executed under. Errors the calibration did not report are
  exactly what the candidates stand in for.
- **What it establishes.** An exploratory reanalysis of hardware counts seen
  before the candidates were chosen: it rules out these six single channels,
  within the stated bounds, as the whole explanation. It identifies no
  mechanism on the device.

## Replay

Gate core-311 runs four checks:
- it requires `result.json` to be byte-identical to the output recorded in
  the run's `collect.json` ledger;
- it re-derives `members.json` byte for byte and compares all 56 loaded
  extracted circuits with the retained runs under the current SDK;
- it recomputes the `cd_core` signs behind the recorded package agreement,
  without importing any package;
- on the CPU it re-derives Kingston lane 0's laws for all 14 members under
  every model to 1e-8, recomputes each model's held-out log-likelihood and
  deviance and each candidate's reproduces-the-floor decision, and requires
  each recorded optimum to be a local minimum: no single parameter moved by
  1e-3 of its bound width, in either direction the bounds allow, raises the
  readout0 log-likelihood by more than 1e-3.

Gate core-310 lints and type-checks the script.

Gate `core-walk-extract` runs `--check-extract`
under the recorded Qiskit 2.5.2 producer. That check requires exact JSON and QPY
bytes. Qiskit 2.6 emits QPY format 18 where the producer emitted format 17, so
current-SDK circuit equivalence and producer byte identity have separate gates.
Gate `core-walk-extract-contract` mutates circuit content and metadata to verify
that the semantic extraction check rejects scientific changes.
