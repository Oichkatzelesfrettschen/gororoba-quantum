# Case: coherent-error probes and gap-88 phase-gradient tomography on an ibm_kingston path

Status: written case awaiting the user's approval. Nothing in this file authorizes a submission.

## What it measures

[primorial-cover-joint-coherent-bounds.md](../../docs/design/primorial-cover-joint-coherent-bounds.md)
reduces the primorial gap-88 device question to four coherent quantities of the chosen three-qubit path:
the drive-axis tilt of each qubit's sx and x pulses, the conditional phase of each coupler's CZ, the static
detuning of each qubit and the partner-in-0 ZZ of each coupler. At their gate-error bounds tilt and CZ phase
together bias the null-subtracted coefficient fit by max_z 2.61 to 2.84; at the scales the repository has
measured on Fez (5 to 30 kHz detuning, 0.04 rad CZ phase) the predicted max_z is 0.069 to 0.072. The case
measures the four quantities on one path and decides from them whether the gap-88 tomography identifies all
seven Walsh coefficients of the gap-88 cost there.

- **Stage 1, the coherence probes** (campaign `coherence_probes`, `gororoba_quantum/coherence_probes.py`):
  identity cells x, rz(pi), x, rz(pi) and rz(pi), sx, sx, rz(pi), sx, sx at 0, 4, 16 and 64 cells read the x
  and sx tilt; CZ pairs at 0, 2, 8 and 32 pairs with the control in 0 and in 1 read each coupler's
  conditional phase as the difference of the target's phase slopes; Ramsey idles of 0, 1, 4 and 16 us read
  each qubit's detuning and, with an outer qubit in 1, each coupler's ZZ.
- **Stage 2, the gap-88 tomography** (campaign `primorial_gap88`, `gororoba_quantum/primorial_campaigns.py`):
  the 24 phase-gradient settings of the gap-88 cost, each as gap-88, null, null and gap-88 arms in that
  order, and 8 basis preparations.

## Why simulation cannot answer it

Every quantity is a property of named physical qubits and couplers. The noise model live_run builds from the
calibration carries depolarizing gate errors, relaxation and readout; it holds no coherent tilt, conditional
phase, detuning or ZZ, so a simulation returns whatever coherent values it is given. The reported gate
errors bound tilt and CZ phase only from above, and the bound reaches max_z 1.29 even on the path the fresh
calibration ranks best. The probe-case record (docs/evidence/primorial_cover/probe_case.json) shows that
the probes recover injected values of every family at once and that the decision rule separates the
measured scales (proceed) from the decision thresholds (stop); which side a real path sits on is the device
question, the AGENTS.md criterion for IBM hardware below 16 qubits.

## Design

- **Backend and path.** ibm_kingston (Heron r2), `--pin-layout ibm_kingston:0,1,2`, logical wires 0, 1, 2 on
  physical 0, 1, 2 with couplers (0, 1) and (1, 2). The path ranks first of 226 working paths of the
  calibration of 2026-10-25T16:43:36-07:00 by the worst joint tilt-and-CZ-phase max_z at its own
  gate-error bounds (1.29; sx errors 2.3, 1.7 and 1.3 x 10^-4, CZ errors 1.2 and 0.9 x 10^-3). The approval
  dry run re-reads the calibration; a dry run on another path needs a new approval.
- **Compilation.** Every member carries the compilation contract `structure-preserving-native-v1`, which
  live_run compiles at optimization level 0 on the pinned layout: single-qubit fusion would collapse each
  identity cell, CZ cancellation would remove each pair, and both would remove the zero-angle network of
  the null arms. The probe dry run's compiled CZ counts are 4, 16 and 64 per CZ arm and 0 elsewhere; the
  gap-88 dry run's are 8 per arm.
- **One replica, no co-run.** live_run refuses `--max-replicas` other than 1 and any other group beside
  either campaign.
- **Twirling off, dynamical decoupling none.** Gate twirling turns the coherent CZ phase the pair probe
  reads into a stochastic channel, and the probe-case record shows 32 independent randomizations of the
  gap-88 signal and null arms raising the joint max_z to 5.4 against 2.6 untwirled at the bounds; a DD
  pulse would refocus the Ramsey idles. live_run refuses `--twirl` and `--dd` for both campaigns.
- **Repetition delay.** The backend default, 250 us.
- **Stage 1 circuits and shots.** 98 circuits: 32 tilt (x and sx, outer pair and middle qubit, 4 depths,
  Z and X readout), 32 CZ (2 couplers, control 0 and 1, 4 depths, X and Y), 32 Ramsey (outer pair and
  middle with outers 00, 10, 01, 4 delays, X and Y) and 2 readout calibrations. 800 shots per circuit:
  the design needs 757 on the record's best path, set by the partner-in-0 ZZ of 2 kHz at three standard
  deviations; tilt at 0.2 of its bound needs at most 18, CZ phase at 0.7 of its bound 2, detuning of 5 kHz
  60.
- **Stage 2 circuits and shots.** 104 circuits, 3200 shots per circuit. The decision rule's noise analysis
  of path 0-1-2 at the 16:43:36 calibration (`--decide` with zero probe estimates) gives a budget of 2877
  shots per setting to identify all seven coefficients, an incoherent bias of 0.0030 and coefficient
  standard deviations of 0.010 to 0.018 at 3200 shots; the zero-error decision proceeds at a 95th
  percentile max_z of 0.0005.

## Expected seconds

The planner's form is 2.3 s of job overhead plus shots x (rep_delay + schedule) per circuit, to which the
per-shot INIT/FINI sequence adds about 8.85 us (N21_SPECTATOR_RAMSEY_CASE.md); the retained Fez ground split
billed 1.12 times its planned circuit time.

| | stage 1 probes | stage 2 gap-88 |
| --- | ---: | ---: |
| circuits x shots | 98 x 800 = 78,400 | 104 x 3200 = 332,800 |
| column period (rep_delay + schedule over every circuit) | 25.0 ms | 26.3 ms |
| shot time | 20.0 s | 84.2 s |
| INIT/FINI | 0.7 s | 2.9 s |
| scaled by 1.12, plus 2.3 s overhead | 25.5 s | 99.8 s |
| plus one sub-job split (2 s) | 27.5 s | 101.8 s |
| ceiling `--max-execution-seconds` | 60 s | 160 s |

Account: the backup instance (`GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`), 450 s remaining of 600 at
2026-10-26T00:0x UTC against 117 s on the primary; both stages together expect about 130 s and cap at
220 s. No credit-billed provider is involved.

## Interleave schedule

IBM runs a batch column-wise, every circuit once per shot in order, with no guarantee of order across PUBs
or of one batch per job ([repetition-rate-execution.md](../../docs/notes/ibm_quantum/repetition-rate-execution.md)).
Within a batch the gap-88 and null arms of a setting execute 26.3 ms apart at most, against the
signal-arm-only tolerances of the bound record: a q0 detuning difference of 2.2 to 2.4 kHz, a tilt
difference of 2.2 mrad or a CZ-phase difference of 6.1 mrad reaches one standard deviation. No retained
Kingston record measures a drift rate, so the design carries its own monitors: each setting runs gap-88,
null, null, gap-88, the estimate averages the two executions of each, and each repeated pair is fitted
against its first copy. The monitor's noise floor at 3200 shots is about 0.024 in the largest coefficient
(the dry run's simulated readout), so it flags a drift several times the tolerance; a split across
sub-jobs is detected only through it.

## Preregistered analysis

1. **Stage 1 estimates.** `coherence_probes.summarize` on the readout-inverted distributions: tilt_x_q*,
   tilt_sx_q* (rad), cz_phase_c* (rad, with the measured ZZ share added back), detuning_q* and zz_c* (Hz),
   each with a delta-method standard error. Falsifiers: a probe circuit whose readout calibration shows
   1 - e10 - e01 below 0.8 voids its estimates; a CZ arm whose control postselection keeps under half its
   shots voids that coupler.
2. **Decision.** `scripts/primorial_probe_case.py --decide` with the run's calibration snapshot, the path,
   the stage-1 summary, 800 probe shots and 3200 gap-88 shots. It builds the path's own coefficient budget
   under the snapshot's noise model, maps the estimates to primorial_bound_residuals' families (tilt on
   pulses, detuning on idles and CZs only) and samples the estimates' uncertainty at 128 unscrambled Sobol
   points. Stage 2 proceeds only when the 95th percentile of the predicted max_z is below 1.
3. **Stage 2 analysis.** `primorial_campaigns.summarize`: the null-subtracted coefficients c_S from the
   averaged signal and null readings, each bias against its exact value, identification (every |bias| below
   1/16) and the two drift monitors. Falsifiers: the gap-88 claim fails when any coefficient misses the
   identification radius; the probe-based prediction fails when the measured largest bias lies outside the
   predicted interval widened by the incoherent bias of the path's noise analysis.
4. The prediction the decision uses is bound into this case by the sha256 of scripts/primorial_probe_case.py,
   gororoba_quantum/coherence_probes.py, primorial_campaigns.py and primorial_tomography.py at the approved
   dry run's commit; experiment_digest covers the gororoba_quantum files.

## Hardware-probe rules

([algebra_circuit_rules.md](../../docs/notes/algebra_circuit_rules.md#hardware-probes))

- Null arm: every gap-88 setting has its zero-angle arm with the same pulse stream, bound from one
  parametrized circuit, and the decision reads the null-subtracted fit.
- Order: each contrast runs +, -, -, + within one job.
- The coherent parameters the first-order observable depends on are measured by the same case, each
  through its own readout calibration (stage 1).
- Noise model: the decisive coherent scenarios were run through the snapshot's noise model; on this 8-CZ
  compile the noisy null-subtracted bias at the joint bound is 0.0510 against 0.0487 noise-free, the
  difference the incoherent floor of 0.0026, so the noise-free derivative is not inflated here.

## Approval record and envelope

The binding approved records are the submit-free dry runs made from main after this change merges,
immediately before `--submit`, with the commands below minus `--submit` and the approval flags.

```sh
cd gororoba_quantum
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" live_run.py --groups coherence_probes --pin-layout ibm_kingston:0,1,2 --max-replicas 1 \
  --backends ibm_kingston --shots 800 --max-execution-seconds 60 --out ../results/live \
  --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
"$PYTHON" live_run.py --groups primorial_gap88 --pin-layout ibm_kingston:0,1,2 --max-replicas 1 \
  --backends ibm_kingston --shots 3200 --max-execution-seconds 160 --out ../results/live \
  --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
```

This case approves the envelope: the two campaigns above on ibm_kingston path 0-1-2, their member structure,
shots, policy (twirl off, dd none, default repetition delay, the structure-preserving contract) and ceilings,
and an expected bill of at most about 30 s for stage 1 and 105 s for stage 2. A dry run on another path,
with other circuits or with an estimated charge above those needs a fresh approval.
