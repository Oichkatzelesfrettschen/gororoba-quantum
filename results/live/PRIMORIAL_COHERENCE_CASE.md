# Case: coherent-error probes and gap-88 phase-gradient tomography on an ibm_kingston path

Status: approved by the user on 2026-10-26 for the envelope below with both stages under the
calibration-identity gate and N1 = 800 probe shots. The approval takes effect on the submit-free dry runs
made from main after this change merges; stage 2 additionally needs stage 1's decision to proceed.

## What it measures

[primorial-cover-joint-coherent-bounds.md](../../docs/design/primorial-cover-joint-coherent-bounds.md)
reduces the primorial gap-88 device question to four coherent quantities of the chosen three-qubit path:
the drive-axis tilt of each qubit's sx and x pulses, the conditional phase of each coupler's CZ, the static
detuning of each qubit and the partner-in-0 ZZ of each coupler. At their gate-error bounds tilt and CZ phase
together bias the null-subtracted coefficient fit by max_z 2.61 to 2.84; at the scales the repository has
measured on Fez (5 to 30 kHz detuning, 0.04 rad CZ phase) the predicted max_z is 0.07 to 0.10. The case
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
errors bound tilt and CZ phase only from above, and the bound reaches max_z 1.29 even on the path the
calibration ranks best. The probe-case record (docs/evidence/primorial_cover/probe_case.json) shows that the
probes recover injected values of every family at once and that the decision rule separates the measured
scales (proceed) from the decision thresholds (stop); which side a real path sits on is the device
question, the AGENTS.md criterion for IBM hardware below 16 qubits.

## Design

- **Backend and path.** ibm_kingston (Heron r2), `--pin-layout ibm_kingston:0,1,2`, logical wires 0, 1, 2 on
  physical 0, 1, 2 with couplers (0, 1) and (1, 2). The path ranks first of 226 working paths of the
  calibration of 2026-10-25T16:43:36-07:00 by the worst joint tilt-and-CZ-phase max_z at its own gate-error
  bounds (1.29; sx errors 2.3, 1.7 and 1.3 x 10^-4, CZ errors 1.2 and 0.9 x 10^-3). A dry run on another
  path needs a new approval.
- **Compilation.** Every member carries the compilation contract `structure-preserving-native-v1`, which
  live_run compiles at optimization level 0 on the pinned layout: single-qubit fusion would collapse each
  identity cell, CZ cancellation would remove each pair, and both would remove the zero-angle network of the
  null arms. The retained dry runs (results/live/ of this change) compile 4, 16 and 64 CZ per CZ arm and 8
  per gap-88 arm, and place their one replica on physical qubits 0, 1 and 2.
- **One member per PUB.** The probe job packs 98 PUBs and the gap-88 job 104, one member each.
- **One replica, no co-run.** live_run refuses `--max-replicas` other than 1, a missing `--pin-layout` and any
  other group beside either campaign.
- **Twirling off, dynamical decoupling none.** Gate twirling turns the coherent CZ phase the pair probe
  reads into a stochastic channel. With one member per PUB, `--twirl` would give the gap-88 signal and null
  arms independent randomizations, and the probe-case record shows 32 such randomizations raising the joint
  max_z at the bounds to 5.4 against 2.6 untwirled. A DD pulse would refocus the Ramsey idles. live_run
  refuses `--twirl` and `--dd` for both campaigns.
- **Repetition delay.** The backend default, 250 us.
- **Stage 1 circuits.** 98: 32 tilt (x and sx; outer pair and middle qubit run separately, so no two driven
  qubits flip together across a coupler; 4 depths; Z and X readout), 32 CZ (2 couplers, control 0 and 1, 4
  depths, X and Y), 32 Ramsey (outer pair, and middle with outers 00, 10, 01; 4 delays; X and Y) and 2
  readout calibrations.
- **Stage 1 shots.** The noise design on path 0-1-2 at the 19:08:38 calibration resolves, at three
  standard deviations, CZ phase at 0.7 of its bound with 2 to 3 shots per circuit, tilt at 0.2 of its sx and
  x bounds with 10 to 21, detuning of 5 kHz with 48 to 58 and partner-in-0 ZZ of 2 kHz with 613. The
  decision barely depends on the probe shots: at 200 shots against 800 the decision's 95th-percentile max_z
  moves by at most 0.03 in every outcome below. The case offers 800 (ZZ resolved to 2 kHz) or 200 (ZZ to
  about 4 kHz); see the user's choice below.
- **Stage 2 circuits and shots.** 104 circuits. Each reading averages two executions (gap-88 with its
  repeat, null with its repeat), so a reading holds twice the shots per circuit. Stage 2's shots per circuit
  are set from stage 1's decision record as ceil(p95 identification shots / 2), rounded up to a multiple of
  100 and held between 1600 and 3200; `--decide` is re-run at that count and stage 2 proceeds only if it
  still proceeds. The approval covers that envelope.

## Expected seconds

The planner's form is 2.3 s of job overhead plus shots x (rep_delay + schedule) per circuit, to which the
per-shot INIT/FINI sequence adds about 8.85 us (N21_SPECTATOR_RAMSEY_CASE.md); the retained Fez ground split
billed 1.12 times its planned circuit time, and a sub-job split adds about 2 s.

| | stage 1 at 800 | stage 1 at 200 | stage 2 at 1600 | stage 2 at 3200 |
| --- | ---: | ---: | ---: | ---: |
| circuits x shots | 78,400 | 19,600 | 166,400 | 332,800 |
| column period (rep_delay + schedule) | 25.0 ms | 25.0 ms | 26.3 ms | 26.3 ms |
| shot time | 20.0 s | 5.0 s | 42.1 s | 84.2 s |
| INIT/FINI | 0.7 s | 0.2 s | 1.5 s | 2.9 s |
| x 1.12, + 2.3 s overhead, + one 2 s split | 27.5 s | 10.2 s | 53.2 s | 101.8 s |
| ceiling `--max-execution-seconds` | 60 s | 30 s | 90 s | 160 s |

Account: the backup instance (`GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`). The gap-88 dry run read
450 s remaining of 600 at 2026-10-26T02:12:56Z (its record's `budget_plan.remaining_seconds`); the primary
read 117 s at 2026-10-26T00:03:42Z. The whole case costs between about 63 s (200 and 1600) and 129 s (800
and 3200) and caps at 220 s. No credit-billed provider is involved.

## Interleave and calibration identity

IBM runs a batch column-wise, every circuit once per shot in order, with no guarantee of order across PUBs
or of one batch per job ([repetition-rate-execution.md](../../docs/notes/ibm_quantum/repetition-rate-execution.md)).
Within a batch the gap-88 and null arms of a setting execute 26.3 ms apart at most, against the
signal-arm-only tolerances of the bound record: a q0 detuning difference of 2.2 to 2.4 kHz, a tilt
difference of 2.2 mrad or a CZ-phase difference of 6.1 mrad reaches one standard deviation. No retained
Kingston record measures a drift rate, so each setting runs gap-88, null, null, gap-88, the estimate
averages the two executions of each, and each repeated pair is fitted against its first copy; the
monitor's noise floor is about 0.024 in the largest coefficient at 3200 shots, so it flags a drift several
times the tolerance.

The hardware-probe rules ask that a first-order observable's coherent parameters be measured in the same
job. live_run refuses to co-run the two campaigns, so the case runs them as two jobs and closes the gap
with a calibration-identity gate:

1. Both dry runs are made back to back under one calibration. Every key their records'
   `calibration_fingerprint` values share must be equal, and each coupler's CZ error and duration must agree
   between the orientations the two campaigns compile (the retained dry runs at 19:08:38 share 44 keys,
   all equal, and differ only in the orientation of coupler (1, 2)).
2. Immediately before stage 1's `--submit`, `"$PYTHON" calibration_snapshot.py --export ibm_kingston --out
   STAGE1_DIR/calibration-snapshot.json` retains the calibration `--decide` uses; its calibration timestamp
   must equal the stage-1 dry run's.
3. Stage 1's submission and stage 2's each pass live_run's approval preflight, which refuses when any
   calibration value bound in its dry run changed. Stage 2 is sent only if the calibration it reads at
   submission equals stage 1's; otherwise stage 1 is re-run under the new calibration before stage 2.
4. `--collect` records the calibration at each PUB's execution start; a stage whose execution calibration
   differs from the other's is reported as such and voids the decision.

## Preregistered analysis

1. **Stage 1 estimates.** `coherence_probes.summarize` on the readout-inverted distributions: tilt_x_q*,
   tilt_sx_q* (rad), cz_phase_c* (rad, the measured ZZ share added back), detuning_q* and zz_c* (Hz), each
   with a delta-method standard error at one shot. Voiding rules: a wire whose readout calibration gives
   1 - e10 - e01 below 0.8 voids its estimates; a CZ arm whose control postselection keeps under half its
   shots voids that coupler; a void estimate stops the case.
2. **Decision.** `"$PYTHON" scripts/primorial_probe_case.py --decide --snapshot
   STAGE1_DIR/calibration-snapshot.json --layout 0,1,2 --probe-summary SUMMARY --probe-shots N1
   --gap88-shots N2 --out STAGE1_DIR/decision.json`. It builds path 0-1-2's coefficient variances from the
   snapshot under the noise model, maps the estimates to the coherent families (tilt on pulses, detuning on
   idles and CZs only), samples the estimates' uncertainty at 128 unscrambled Sobol points, and takes the
   coefficient standard deviations at 2 N2 shots per reading. Stage 2 proceeds only when the 95th percentile
   of max_z is below 1 and the 95th percentile of the shots that identify all seven coefficients is at most
   2 N2. On path 0-1-2 at the 19:08:38 calibration the rule proceeds at zero error (p95 max_z 0.0005), at
   the measured scales (0.10 at N2 = 3200) and at the decision thresholds with N2 = 3200 (0.95; identification
   3971 shots), and stops at the thresholds with N2 = 1600 (identification 3971 above 3200).
3. **Stage 2 analysis.** `primorial_campaigns.summarize`: the null-subtracted coefficients c_S from the
   averaged signal and null readings, each bias against its exact value, identification (every |bias| below
   1/16) and both drift monitors. The gap-88 identification claim fails when any coefficient misses the
   radius. The probe-based prediction fails when the measured largest bias lies outside `decision.json`'s
   `falsifier_band`: the 2.5 to 97.5 percent range of the predicted largest bias over the Sobol points,
   widened on each side by three of the largest coefficient standard deviations at 2 N2 shots and by the
   path's incoherent bias (0.003 at 19:08:38).
4. **Bound sources.** The decision and the stage-2 prediction run through these files; the approval binds
   their sha256 at the commit the approved dry runs report, which the operator writes into the approval
   record beside the dry-run digests: scripts/primorial_probe_case.py, scripts/primorial_bound_residuals.py,
   scripts/primorial_cover_noise.py, scripts/primorial_null_residuals.py,
   gororoba_quantum/primorial_tomography.py, gororoba_quantum/coherence_probes.py,
   gororoba_quantum/primorial_campaigns.py, gororoba_quantum/conditional_ramsey.py,
   gororoba_quantum/calibration_snapshot.py and gororoba_quantum/snapshot_laws.py. `experiment_digest`
   covers the gororoba_quantum files.

## Assumptions the result rests on

- Coherent errors are static over a job. A sub-job split leaves the arms protected only by the drift
  monitors; stage 2 reads its job metrics for the sub-job count and reports it.
- The prediction schedules the arms ALAP from the Target's durations. IBM's execution timing can differ, and
  the detuning and ZZ terms depend on where the idles fall; `--collect`'s scheduler timing records it.
- Amplitude error is not probed. The gate error bounds it, and alone at its bound it stays below max_z 0.27.
- Static ZZ is measured in the partner-in-0 frame, the frame the CZ calibration fixes; the symmetric-frame
  pairs of the bound record stay below 0.92.

## Hardware-probe rules

([algebra_circuit_rules.md](../../docs/notes/algebra_circuit_rules.md#hardware-probes))

- Null arm: every gap-88 setting has its zero-angle arm bound from the same parametrized circuit, and the
  decision reads the null-subtracted fit.
- Order: each contrast runs +, -, -, + within one job.
- Same job: the coherent parameters are measured in the job before the gap-88 job under the
  calibration-identity gate above, each through its own readout calibration; this is the case's one
  deviation from the rule.
- Noise model: the decisive coherent scenarios were run through the snapshot's noise model; on this 8-CZ
  compile the noisy null-subtracted bias at the joint bound is 0.051 against 0.049 noise-free, the
  difference the incoherent floor, so the noise-free derivative is not inflated.

## Approval record and envelope

The binding approved records are submit-free dry runs made from main after this change merges, back to back
immediately before stage 1's `--submit`, with the commands below minus `--submit` and the approval flags;
stage 2's dry run is repeated after stage 1 with the shots the decision sets, and must keep stage 1's
calibration.

```sh
cd gororoba_quantum
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" live_run.py --groups coherence_probes --pin-layout ibm_kingston:0,1,2 --max-replicas 1 \
  --backends ibm_kingston --shots N1 --max-execution-seconds C1 --out ../results/live \
  --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
"$PYTHON" live_run.py --groups primorial_gap88 --pin-layout ibm_kingston:0,1,2 --max-replicas 1 \
  --backends ibm_kingston --shots N2 --max-execution-seconds C2 --out ../results/live \
  --submit --approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256
```

This case approves the envelope: the two campaigns above on ibm_kingston path 0-1-2, their member
structure, the policy (twirl off, dd none, default repetition delay, the structure-preserving contract),
N1 of 800 or 200 with C1 of 60 s or 30 s, N2 between 1600 and 3200 set by the decision with C2 of 90 s to
160 s, and an expected bill of at most about 130 s. A dry run on another path, with other circuits, with a
different calibration between the stages or with an estimated charge above those needs a fresh approval.
