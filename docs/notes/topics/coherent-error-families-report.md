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
| (1b) Fringe amplitude ratios as an observable | DONE (lane 4 of both runs; structure on all 14 lanes) | `scripts/atlas_fringe_amplitudes.py`, `docs/evidence/atlas_fringe_amplitudes/` (gates core-359, core-360) |
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
7. `calibration_median_drift: absolute per-qubit drift beside the signed
   median`. Each paired entry reports the median and 90th percentile of
   abs(rel) beside the signed median.
8. `atlas_coherent_families: |11> conditional-phase ZZ beside the
   symmetric RZZ frame`. Adds the `zz_symmetric` family and the ZZ frame
   anchor in core-325.
9. `atlas_coherent_families: rank and condition on every leave-one-out
   fold`. Marks underdetermined folds unidentified.
10. `atlas_coherent_families: retain the lane-4 fit bound to its input
    digests`. Adds `docs/evidence/atlas_coherent_families/` and gate
    core-329.
11. `docs: ZZ frame, fold identifiability and absolute drift in the audit
    note`. Rewrites this note from the retained lane-4 result.

`scripts/atlas_coherent_families.py` rebuilds every phase point as its
executed replica at its `scheduler_timing` pulse starts:

- Kingston plays a measurement as four consecutive play rows; the pairing
  consumes them as one.
- The families enter at executed times: detuning, CZ phase, static ZZ in
  two frames (below), drive amplitude (sx and x scaled together), polar axis
  tilt, and the in-plane drive-phase gauge.
- Static ZZ acts over start-to-start intervals on each CZ coupler, in two
  frames:
  - `zz` is the |11> conditional phase CPhase(-2 pi zeta t). This is the
    frame of qubit frequencies calibrated with the partner in |0>.
  - `zz_symmetric` is RZZ(pi zeta t). It equals `zz` plus a zeta/2 frame
    detuning on both qubits of the coupler.
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
    allows, compared with the RMS of the lane's offsets;
  - the count of fitted values beyond that bound;
  - a held-out contrast cross-prediction;
  - each single family refitted with a lane-constant phase term
    (`<family>_plus_mean`). The models without the term stay the ones
    comparable to the retained table;
  - the rank and condition number of every leave-one-out fold. A model
    whose folds train on no more edges than it has columns, or whose fold
    design loses rank, is reported unidentified;
  - the sha256 of every input file, which `--check` verifies first.
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

Self-test (core-325, 71 s for both modes at one worker on the build host):

- ZZ frame anchor. On a two-qubit Ramsey fringe of one qubit (sx, RZ(phi),
  sx 2 us later) at 50 kHz:
  - `zz` with the partner in |0> leaves the fringe phase unchanged (0 rad).
  - `zz` with the partner in |1> shifts the phase by +0.628 rad, the
    shift a -50 kHz detuning gives.
  - `zz_symmetric` shifts the phase by -0.314 and +0.314 rad, the shifts of
    +25 and -25 kHz detunings.
  This pins the sign and the timing of both frames to the detuning family,
  which the retained map anchors independently.
- Fez lane 4, 6 edges: the ideal-fringe mismatch is 8.9e-16 rad, the gauge
  null 1.9e-15, and the forward detuning and CZ slopes equal the retained
  map within 4.8e-10, its 9-decimal rounding.
- Injected values are recovered within 10 percent of the largest injected
  value:
  - detuning 3, -2, 4, -1.5, 2.5 kHz;
  - ZZ 2, -1.5, 1, -2.5 kHz in both frames;
  - SX amplitude on the odd columns;
  - axis tilt 0.002 to 0.005 rad.
- Two Kingston edges reproduce their record ideal fringe phase within
  1e-15 rad.

## Reduced case: lane 4 of both runs (42 s with 12 workers)

`docs/evidence/atlas_coherent_families/result.json` retains this case, and
gate core-329 recomputes it. Fez lane 4 fits all 12 edges. Kingston lane 4
fits 10, because 2 of its edges span a recalibration.

Falsifiers (script docstring):

- A family is refuted when its resimulated leave-one-out phase RMS is at or
  above the lane mean's.
- It accounts for the offsets when its linear leave-one-out RMS is at most
  1.5 times its own floor.
- A bounded family cannot account for the offsets when its phase reach at
  the gate-error bound is below the RMS of the lane's measured offsets.
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
| ZZ, partner-in-0 frame | 0.076 / 0.077 | 0.038 | 0.068 / 0.068 | 0.037 |
| ZZ, symmetric frame | 0.182 / 0.179 | 0.038 | 0.160 / 0.274 | 0.034 |
| SX amplitude (3 odd columns) | 0.192 / 0.192 | 0.037 | 0.241 / 0.311 | 0.034 |
| axis tilt | 0.118 / 0.114 | 0.041 | 0.099 / 0.104 | 0.044 |
| detuning + CZ phase | 0.264 / 0.304 | 0.076 | unidentified | |
| detuning + ZZ (partner-in-0) | 0.166 / 0.191 | 0.122 | unidentified | |
| detuning + ZZ (symmetric) | 0.159 / 0.191 | 0.123 | unidentified | |
| detuning + SX amplitude | 0.132 / 0.135 | 0.074 | 0.168 / 0.207 | 0.113 |
| detuning + axis tilt | 0.293 / 0.725 | 0.111 | unidentified | |
| detuning + constant | 0.125 / 0.128 | 0.048 | 0.132 / 0.167 | 0.054 |
| CZ phase + constant | 0.087 / 0.086 | 0.041 | 0.122 / 0.123 | 0.043 |
| ZZ (partner-in-0) + constant | 0.074 / 0.075 | 0.040 | 0.097 / 0.097 | 0.042 |
| ZZ (symmetric) + constant | 0.174 / 0.162 | 0.041 | 0.076 / 0.078 | 0.039 |
| SX amplitude + constant | 0.182 / 0.174 | 0.039 | 0.054 / 0.057 | 0.035 |
| axis tilt + constant | 0.137 / 1.492 | 0.082 | 0.179 / 1.336 | 0.092 |

The Fez detuning, CZ-phase and detuning + CZ-phase rows equal the retained
map's lane 4 to 1e-6. Fold condition numbers are in the evidence README.

Readings, per family:

- **ZZ: the verdict depends on the frame.**
  - In the symmetric frame, ZZ is refuted on both lanes, with fitted rates
    of 38 to 91 kHz on Fez and up to 273 kHz on Kingston.
  - In the partner-in-0 frame, ZZ alone on Fez lane 4 scores 0.077
    resimulated, against the lane mean's 0.136. That beats every other
    single family, CZ phase + constant (0.086) included. Its rates are
    17.6, 20.4, 37.0 and -6.1 kHz on couplers 50-51, 51-52, 51-58 and
    58-71.
  - The Fez result is 2.0 times its floor, so ZZ does not account for the
    offsets by the 1.5 criterion. Its held-out contrast RMS is 0.052
    against the lane mean's 0.057, with no contradicted edge.
  - On Kingston lane 4, partner-in-0 ZZ is refuted narrowly (0.068 against
    0.060), with rates 0.9, 24.1, -9.1 and 1.7 kHz on couplers 138-151,
    150-151, 151-152 and 152-153.
  - With a constant, the partner-in-0 frame reaches 0.075 on Fez. Its
    design has fold condition 2.0e3, and the coupler 50-51 rate moves from
    17.6 to -15.1 kHz against a 0.287 rad constant. The 50-51 column is
    nearly uniform over the edges (0.0077 to 0.0099 rad/kHz), so it trades
    off against the constant.
- **Which frame is physical is an inference, at moderate confidence.** The
  partner-in-0 frame is the physical one if IBM calibrates each qubit
  frequency with its neighbors in |0>, as a standard Ramsey frequency
  calibration does. `docs/notes/ibm_quantum/calibration-jobs.md` lists qubit
  frequency among the calibrated parameters but names no spectator state,
  and no repository source states one. Two things would settle it: an IBM
  statement of the spectator state during frequency calibration, or a
  conditional Ramsey run with the partner held in |0>
  (`proposed-conditional-ramsey-hamiltonian`). No repository source gives
  a static-ZZ magnitude for these Heron r2 couplers, so whether rates of 6 to
  37 kHz are plausible is unsourced.
- **Joint detuning + ZZ** depends on the frame only through the detuning
  block. With central detuning slopes, the two frames span the same columns
  and score 0.15604 and 0.15608 on Fez. The script uses the forward slope of
  the retained map, which differs by at most 1.2e-5 rad/kHz, and the scores
  move to 0.166 and 0.159. A 1e-5 perturbation of a column moving the score
  by 0.007 rad shows how weakly these 9-parameter fits are determined.
- **SX amplitude** is refuted on both lanes.
  - On Kingston it predicts more contrast loss than measured on 9 of 10
    edges, and fitted values exceed the bound on 2 qubits.
  - Its reach at the bound is 0.150 rad on Fez and 0.134 rad on Kingston.
    That is below the RMS of the measured offsets, 0.158 and 0.251 rad, so
    the bound alone excludes it as the whole explanation.
- **Axis tilt** beats the lane mean on Fez (0.114 against 0.136, 2.8 times
  its floor).
  - It needs -0.065 and -0.059 rad on qubits 50 and 52, about twice the
    0.0288 and 0.0341 rad their sx errors allow. A static axis tilt of that
    size is inconsistent with the calibration.
  - On Kingston it is refuted.
  - With a constant, its fold condition reaches 4.4e5 to 4.7e5. It fits
    tilts of hundreds of radians and fails on resimulation (1.3 to 1.5 rad).
    Some tilt column is nearly uniform over the edges, so it trades off
    against the constant.
- **CZ phase + constant** scores 0.086 resimulated on Fez, 2.1 times its
  floor. It needs a 0.133 rad constant and CZ phases of -0.04 rad on
  couplers 51-52 and 51-58, within their 0.10 and 0.15 rad bounds.
- **Kingston lane 4** offsets are a nearly uniform +0.245 rad, against a
  lane-mean held-out RMS of 0.060, 2.2 times its floor.
  - Only SX amplitude + constant improves on it (0.054 / 0.057), with a
    0.256 rad constant.
  - That fit needs eta = -0.029 on qubit 151 and -0.024 on qubit 153,
    beyond the 0.020 the sx errors allow on each, so it is inconsistent
    with the calibration.
  - No calibration-consistent family improves on the lane constant there.
- **Contrast.** The hardware contrast sits below the replay by log ratio
  -0.22 (Fez) and -0.14 (Kingston). Against the lane mean's held-out
  contrast RMS of 0.057 (Fez) and 0.055 (Kingston):
  - the largest improvement is 0.0061, from Fez detuning + constant
    (0.051);
  - partner-in-0 ZZ improves by 0.0055 and detuning alone by 0.0044;
  - the best Kingston model, CZ phase, improves by 0.0015;
  - the floor is 0.025 / 0.021.
  The edge-to-edge contrast deficit stays at 2 to 2.5 times its floor under
  every phase-fitted model, so it is not the coherent error these families
  carry.
- **Joint models** on Kingston lane 4 train each fold on 9 edges. Detuning +
  CZ phase and both detuning + ZZ models (9 columns) and detuning + axis
  tilt (10 columns) interpolate every fold and are unidentified. The same
  structure holds on all seven Kingston lanes of the pre-fix 14-lane Kaggle
  output, each fitting 10 edges. The Fez joint models have fold condition
  numbers from 1.0e3 to 4.4e4 on lane 4; across the seven Fez lanes of that
  output, detuning + axis tilt reaches 1.2e5 to 3.0e5 on lanes 2, 3, 5 and
  6. All identified joint models are refuted except detuning + SX amplitude
  on Fez, which only ties the lane mean (0.135 against 0.136). The retained
  map found the same for detuning + CZ phase.

**Exploratory ranking.** The `_plus_mean` models arrived after the first
fits, and the two ZZ frames add more models. The lowest resimulated score
over 18 models is therefore a selection, never a confirmed model:

| Rank | Fez lane 4 | Kingston lane 4 |
| ---: | --- | --- |
| 1 | ZZ (partner-in-0) + constant, 0.075 | SX amplitude + constant, 0.057 (beyond bound) |
| 2 | ZZ (partner-in-0), 0.077 | lane mean, 0.060 |
| 3 | CZ phase + constant, 0.086 | ZZ (partner-in-0), 0.068 |
| 4 | CZ phase, 0.091 | ZZ (symmetric) + constant, 0.078 |
| 5 | detuning, 0.104 | CZ phase, 0.082 |

These are two lanes. The full 14-lane fit decides whether partner-in-0 ZZ
or CZ phase beats the lane mean elsewhere, and whether the lane-uniform
offset recurs. A confirming test scores one named model on lanes it was not
selected on.

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
- The run `results/kaggle/2026-10-16T222749Z-gororoba-atlas-coherent-families`
  took about 19 minutes on four Kaggle cores and is retained, with its output
  as `docs/evidence/atlas_coherent_families/result.json` (gate core-334
  compares the bytes; core-329 recomputes lane 4 of both runs on CPU). The
  evidence README carries the per-lane table: the partner-in-0 ZZ frame
  scores below the symmetric frame on 13 of 14 lanes (14 of 14
  resimulated), `zz` is the best single family on 7 lanes, and only two
  lanes reach the 1.5x-floor criterion with any single family.
- An earlier kernel session, on the same Xeon 2.20 GHz CPU model, ran the
  script before its `--check` tolerance changed and wrote the same bytes, so
  the 14-lane fit repeats across sessions.

## Calibration drift (part 2)

`docs/evidence/calibration_median_drift/README.md` carries the result.

- One series row per (backend, identity) from records without an operator
  exclusion.
- Within one Kingston identity, operator-scoped records give median T2 from
  76 to 290 us over 1 to 8 qubits, which is the error a record-indexed
  series makes.
- Snapshots reproduce the record T1, T2 and CZ medians exactly.
- Between consecutive snapshots, over a fixed population, the signed median
  of the per-qubit relative change reaches at most 7.8 percent (T1), 3.1
  percent (T2), 8.5 percent (assignment error) and 6.1 percent (CZ error).
  That measures a device-wide shift, because qubits that move in opposite
  directions cancel in it.
- The per-qubit drift is larger. Over the pairs in which a quantity
  changed, the median absolute relative change is 0.15 to 0.25 (T1), 0.12 to
  0.30 (T2), 0.19 to 0.45 (assignment error) and 0.11 to 0.23 (CZ error).
  The 90th percentile is 0.41 to 2.5. On the 55-hour Fez pair, T1 has signed
  median 0.078, median absolute change 0.224 and 90th percentile 0.735.
- Neither source carries a qubit frequency.

## Registry

The claim `hw-atlas-coherent-families` in
[research_state.json](../../state/research_state.json) carries the ZZ-frame
comparison and the no-single-family result, bound to
`docs/evidence/atlas_coherent_families/result.json` and replayed by gate
core-329.

## Remaining

- **The x-versus-sx relative axis phase is not modeled.** x is 33 of 1765
  single-qubit pulses in the sampled replicas, too few to identify it.
- **Joint nonlinear fits are not attempted.** Examples are a quadratic
  SX-amplitude model, or contrast fitted jointly with phase. With 12 edges
  per lane and the conditioning above, the conditional-Ramsey design
  (`proposed-conditional-ramsey-hamiltonian`) is the direct measurement of
  detuning and ZZ on named qubits, and of the ZZ frame.
- **The full core-039 mypy gate** on the build host's newer mypy reports 24
  errors in `scripts/cd_phase_degree.py`, which this branch does not touch.
  The touched files pass both that mypy and the CI pin 1.19.1.

## Limitations

- **The Kingston exclusion rests on an identity change that changed no
  recorded value.** The 2026-10-14 19:47 and 20:25 snapshots agree on every
  qubit's t1, t2, e01 and e10, on all 156 sx errors and on all 352 CZ
  errors. Neither carries a qubit frequency, so the data neither support
  nor refute a frame change across the 14 excluded edges, which remain
  available as a control fit. `lane_fit` takes the gate bounds as a maximum
  over every calibration its included edges ran under and does not itself
  require one; every lane at present has one.
- **The held-out contrast constant leaks the held-out edge's phase.** The
  constant for edge e averages the other edges' residuals, each at fold
  parameters fitted with e's phase offset. e's contrast never enters, so
  the effect is small.
- **Failure paths outside the documented domain stop without a named
  message**:
  - a member that is not single-register and single-replica raises a bare
    `KeyError` in `kingston_series`;
  - `gate_bounds` raises `ValueError` for a reported error r >= 2/3, which
    placement excludes;
  - back-to-back measure rows on one qubit merge into one measurement.
  `relative_change` in the drift script now stops with a named error on a
  zero earlier value.
- **ZZ covers only the couplers that carry a CZ in the replica.** Spectator
  couplers and lane pairs without a CZ carry no ZZ. The start-to-start
  window includes the CZ pulse itself, whose ZZ belongs to the calibrated
  gate and overlaps `cz_phase`.
