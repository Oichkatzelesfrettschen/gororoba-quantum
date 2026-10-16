# Coherent error families, calibration drift and Rocq replays: audit and status

This note audits the three replacements for the Kaggle starter notebooks
listed in `docs/evidence/simulation-notebook-audit/README.md`, records what
branch `sim/coherent-error-families` adds, and gives the reduced-case results
and the Kaggle command for the full fit.

## Audit

| Item | Status | Authority |
| --- | --- | --- |
| (1) Coherent forward model on the executed 84-edge atlas circuits | PARTIAL before this branch | `scripts/atlas_detuning_map.py`, `docs/evidence/atlas_detuning_map/` (gates core-285, core-293) |
| (1a) Fringe phase offsets as the observable | DONE (Fez) | same; leave-one-edge-out RMS, shot-noise and leave-one-out floors |
| (1b) Fringe amplitude ratios as an observable | ABSENT | the retained map fits phases only |
| (1c) Frame detuning per qubit | DONE (Fez) | core-285 |
| (1d) CZ conditional phase per coupler | DONE (Fez) | core-285 |
| (1e) Static ZZ during idle | ABSENT | the CZ-phase family is per gate, not per unit time |
| (1f) SX amplitude error | ABSENT | |
| (1g) Rotation-axis tilt | ABSENT | |
| (1h) Kingston | ABSENT from the fit; the data exist | `results/live/2026-10-15T031229.371738Z` ran the same 672 atlas members on 7 lanes, with calibration-bound replays in `collect.json` and 146 raw PUB files carrying `scheduler_timing`, all inside the `gororoba-retained-runs` dataset (659 files, every sha256 equal to the tree) |
| (2) Calibration drift from the record medians | ABSENT | the Ferret kernels crashed; `scripts/ghost_run.py --report` gives a per-run calibration change on the ghosted qubits only |
| (3) Z3 notebooks superseded by Rocq replays on Kaggle | DONE | `scripts/rocq_kaggle_replay.py`, `docs/evidence/rocq_kaggle_replay/result.json` (`passed: true`; formal_certificates, c881_exhaustive, stiefel_witness, folding_proofs and TargetFlipN21 all exit 0; open_gororoba 7d95d228), gate core-292 |

## What the branch adds

Commits, oldest first:

1. `atlas: rebuild executed replicas from any retained run directory`.
   `atlas_detuning_map.Executed` takes the run directory; core-285 still
   reproduces lane 4 of the retained map.
2. `atlas: fit ZZ, SX-amplitude and axis-tilt families to Fez and Kingston
   fringes`. Adds `scripts/atlas_coherent_families.py` and gate core-325, and
   registers the script in core-001, core-002 and core-039.
3. `calibration: drift series from the record medians, one row per
   identity`. Adds `scripts/calibration_median_drift.py`,
   `docs/evidence/calibration_median_drift/` and gate core-326.
4. `docs: audit the coherent-error, drift and Rocq replacements for the
   starter kernels`. Adds this note.
5. `calibration: bind the drift result to the snapshots it read`. The
   result names its 17 snapshots with their sha256, so a later export
   leaves core-326 green.
6. `atlas: lane-constant model variants and raw-verified Kingston
   marginals`. Adds `<family>_plus_mean` models, checks Kingston against
   the raw shots, and lists inert columns.

`scripts/atlas_coherent_families.py` rebuilds every phase point as its
executed replica at its `scheduler_timing` pulse starts:

- Kingston plays a measurement as four consecutive play rows; the pairing
  consumes them as one.
- The families enter at executed times: detuning, CZ phase, static ZZ
  (RZZ over start-to-start intervals on each CZ coupler), drive amplitude
  (sx and x scaled together), polar axis tilt, and the in-plane drive-phase
  gauge.
- Instructions are ordered by executed time, so ZZ sits correctly against
  the pulses of both qubits.
- The fits use the observables, scoring and floors of the retained map:
  leave-one-edge-out RMS, linear and resimulated, against the shot-noise
  and leave-one-out floors.
- Additions:
  - the log contrast ratio log(b_hw / b_replay) with its propagated
    binomial error;
  - central slopes and curvatures for every column;
  - each family's reach at the coherent bound its reported gate error
    allows;
  - the count of fitted values beyond that bound;
  - a held-out contrast cross-prediction;
  - each single family refitted with a lane-constant phase term
    (`<family>_plus_mean`). The models without the term stay the ones
    comparable to the retained table.
- Kingston observations come from the collector's `family_measurements`.
  Every atlas member's marginal must equal the zero count of its raw shot
  bit strings (`raw/<job>/pub_NN.json`). Fez reads `measured-ripple.json`,
  whose extractor made the same check.
- A column with no phase response at all is listed as inert and left out,
  so an undriven qubit cannot make a family rank-deficient.
- Edges whose 8 points span a recalibration are excluded and listed.
  Kingston has 14 such edges, 2 per lane.

Two structural results came out of building the model:

- The in-plane drive-phase offset is a gauge on these circuits. The virtual
  RZ and CZ commute with it, so only RZ on |0> and RZ before a Z readout
  remain. Its simulated shifts stay below 2e-15 rad, so a per-qubit
  in-plane axis error is unobservable here. The discarded
  `correlated-coherent` notebook was blind in a similar way.
- The SX-amplitude family has mixed parity. On Fez lane 4, qubits 50 and 52
  shift the fringe phase only at second order (1.98e-5 rad at
  eta = 0.004, matching curvature times eta^2 to 4e-8). Qubits 51, 58 and 71
  have linear slopes of 1.5 to 3.4 rad per unit fractional error. Even
  columns stay out of the linear fit and enter only through the reach.
  Every coherent family lowers the contrast at second order only, because
  the ideal fringe has the maximal contrast 1/2.

Self-test (core-325, about 32 s serial per mode on the build host):

- Fez lane 4, 6 edges: the ideal-fringe mismatch is 8.9e-16 rad, the gauge
  null 1.9e-15, and the forward detuning and CZ slopes equal the retained
  map within 4.8e-10, its 9-decimal rounding.
- Injected values are recovered within 10 percent of the largest injected
  value:
  - detuning 3, -2, 4, -1.5, 2.5 kHz;
  - ZZ 2, -1.5, 1, -2.5 kHz;
  - SX amplitude on the odd columns;
  - axis tilt 0.002 to 0.005 rad.
- Two Kingston edges reproduce their record ideal fringe phase within
  1e-15 rad.

ZZ has no anchor independent of the model's own slopes: its timing
convention is checked only through the injection round trip.

## Reduced case: lane 4 of both runs (48 s with 6 workers)

Fez lane 4 fits all 12 edges. Kingston lane 4 fits 10, because 2 of its
edges span a recalibration.

Falsifiers, fixed in the script docstring before the fit:

- A family is refuted when its resimulated leave-one-out phase RMS is at or
  above the lane mean's.
- It accounts for the offsets when its linear leave-one-out RMS is at most
  1.5 times its own floor.
- Its fit is inconsistent with the calibration when a fitted value exceeds
  the gate-error bound.
- Its contrast prediction is refuted when the held-out contrast RMS is at or
  above the lane mean's.
- It is contradicted on an edge when the predicted log contrast lies more
  than 3 standard errors below the measured one.

Leave-one-out RMS in rad, linear / resimulated, with each model's floor:

| Model | Fez lane 4 (qubits 50, 51, 52, 58, 71) | floor | Kingston lane 4 (138, 150-153; 10 edges) | floor |
| --- | --- | ---: | --- | ---: |
| lane mean | 0.136 | 0.030 | 0.060 | 0.027 |
| detuning | 0.103 / 0.104 | 0.044 | 0.109 / 0.140 | 0.045 |
| CZ phase | 0.091 / 0.091 | 0.039 | 0.082 / 0.082 | 0.036 |
| ZZ | 0.182 / 0.179 | 0.038 | 0.160 / 0.274 | 0.034 |
| SX amplitude (3 odd columns) | 0.192 / 0.192 | 0.037 | 0.241 / 0.311 | 0.034 |
| axis tilt | 0.118 / 0.114 | 0.041 | 0.099 / 0.104 | 0.044 |
| detuning + CZ phase | 0.264 / 0.304 | 0.076 | 0.886 / 1.095 | 0.297 |
| detuning + ZZ | 0.159 / 0.191 | 0.123 | 1.645 / 0.973 | 0.763 |
| detuning + SX amplitude | 0.132 / 0.135 | 0.074 | 0.168 / 0.207 | 0.113 |
| detuning + axis tilt | 0.293 / 0.725 | 0.111 | 0.180 / 0.204 | 0.168 |
| detuning + constant | 0.125 / 0.128 | 0.048 | 0.132 / 0.167 | 0.054 |
| CZ phase + constant | 0.087 / 0.086 | 0.041 | 0.122 / 0.123 | 0.043 |
| ZZ + constant | 0.174 / 0.162 | 0.041 | 0.076 / 0.078 | 0.039 |
| SX amplitude + constant | 0.182 / 0.174 | 0.039 | 0.054 / 0.057 | 0.035 |
| axis tilt + constant | 0.137 / 1.492 | 0.082 | 0.179 / 1.336 | 0.092 |

The Fez detuning, CZ-phase and joint rows equal the retained map's lane 4
to 1e-6.

Readings, per family:

- **ZZ** is refuted on both lanes. Its fitted rates (38 to 91 kHz on Fez,
  up to 273 kHz on Kingston) would also be far above any static ZZ a
  tunable-coupler Heron shows.
- **SX amplitude** is refuted on both lanes. On Kingston it predicts more
  contrast loss than measured on 9 of 10 edges, and fitted values exceed the
  bound on 2 qubits. Its reach at the bound (0.13 to 0.15 rad) is of the
  size of the offsets, so the bound alone does not exclude it; the
  held-out fit does.
- **Axis tilt** beats the lane mean on Fez (0.114 against 0.136, 2.9 times
  its floor) but needs 0.059 to 0.065 rad on qubits 50 and 52, about twice
  the 0.025 to 0.034 rad the sx errors allow. A static axis tilt of that
  size is inconsistent with the calibration. On Kingston it is refuted.
  With a constant, its design reaches condition 7e4, fits tilts of hundreds
  of radians and fails on resimulation (1.3 to 1.5 rad). Some tilt column
  is nearly uniform over the edges, so it trades off against the constant.
- **CZ phase + constant** is the best Fez model: 0.086 resimulated, 2.1
  times its floor. It needs a 0.133 rad constant and CZ phases of -0.04 rad
  on couplers 51-52 and 51-58, within their 0.10 and 0.15 rad bounds.
- **Kingston lane 4** offsets are a nearly uniform +0.245 rad, against a
  lane-mean held-out RMS of 0.060, 2.2 times its floor. Only SX amplitude +
  constant improves on it (0.054 / 0.057), with a 0.256 rad constant. Its
  fit needs eta = -0.029 on qubit 151 and -0.024 on qubit 153, beyond the
  0.020 the sx errors allow on each, so it is inconsistent with the
  calibration. No calibration-
  consistent family improves on the lane constant there.
- **Contrast.** The hardware contrast sits below the replay by
  log ratio -0.22 (Fez) and -0.14 (Kingston). No phase-fitted single family
  lowers the held-out contrast RMS by more than 0.005 below the lane mean's
  0.057 / 0.055, against a floor of 0.025 / 0.021, so the edge-to-edge
  contrast deficit is not the coherent error these families carry.
- **Joint models** with 8 to 10 parameters on 9 to 11 training edges have
  condition numbers from 160 to 5e4. All are refuted except detuning + SX
  amplitude on Fez, which only ties the lane mean (0.135 against 0.136).
  The retained map found the same for detuning + CZ phase.

These are two lanes. The full 14-lane fit decides whether CZ phase, with or
without the constant, beats detuning elsewhere, and whether the
lane-uniform offset recurs.

## Full fit on Kaggle

From a clean tree at the branch head:

```sh
"$PYTHON" scripts/kaggle_run.py push scripts/atlas_coherent_families.py \
  --slug gororoba-atlas-coherent-families --machine cpu --timeout 3600 \
  --dataset gororoba-retained-runs \
  --include docs/evidence/atlas_detuning_map/result.json \
  -- --runs ibm_fez,ibm_kingston --lanes all --out results/kaggle_out/atlas_coherent_families.json
```

- The dataset supplies both run directories, `measured-ripple.json` and the
  calibration snapshots. The `--include` supplies the retained map the Fez
  lanes are checked against.
- The reduced case used about 110 CPU-seconds per lane, so 14 lanes need
  about 26 CPU-minutes, about 7 minutes on four cores.
- Afterwards, `"$PYTHON" scripts/kaggle_run.py collect RUN_DIR` retains the
  output.

## Calibration drift (part 2)

`docs/evidence/calibration_median_drift/README.md` carries the result.

- One series row per (backend, identity) from records without an operator
  exclusion.
- Within one Kingston identity, operator-scoped records give median T2 from
  76 to 290 us over 1 to 8 qubits, which is the error a record-indexed
  series makes.
- Snapshots reproduce the record T1, T2 and CZ medians exactly.
- Paired drift over a fixed population stays within 7.8 percent (T1),
  3.1 percent (T2), 8.5 percent (assignment error) and 6.1 percent (CZ error)
  between consecutive snapshots.
- Neither source carries a qubit frequency.

## Remaining

- **The full 14-lane fit** is the Kaggle run above. After collection, add:
  - `docs/evidence/atlas_coherent_families/` with `result.json` and a README
    carrying the per-lane table;
  - a byte-identity gate against the kernel output (as core-293 does);
  - a CPU `--check ... --runs ibm_fez --lanes 4` gate. It takes 22 s with 6
    workers and about 110 s serial, so it sits near the pr-tier limit, and
    `--runs ibm_kingston --lanes 4` may suit the full tier.
- **research_state.json** gains claims only after that replay gate exists.
- **The x-versus-sx relative axis phase is not modeled.** x is 33 of 1765
  single-qubit pulses in the sampled replicas, too few to identify it.
- **Joint nonlinear fits are not attempted.** Examples are a quadratic
  SX-amplitude model, or contrast fitted jointly with phase. With 12 edges
  per lane and the conditioning above, the conditional-Ramsey design
  (`proposed-conditional-ramsey-hamiltonian`) is the direct measurement of
  detuning and ZZ on named qubits.
- **The full core-039 mypy gate** on the build host's newer mypy reports 24
  errors in `scripts/cd_phase_degree.py`, which this branch does not touch.
  The touched files pass both that mypy and the CI pin 1.19.1.
