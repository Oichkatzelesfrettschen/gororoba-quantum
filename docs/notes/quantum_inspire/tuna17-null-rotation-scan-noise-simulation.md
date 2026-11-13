# Tuna-17 injected-rotation scan under physical noise: simulation case

Status: numerical simulation on Kaggle, run under the standing approval for Kaggle sessions below 12 hours (root
AGENTS.md, "Hardware services"). It submits nothing to Quantum Inspire. Entry:
`scripts/qi_pathion_null_rotation_scan_noise.py`. Subject: the written case
[pathion_null_rotation_scan_tuna_17](../../../results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/CASE.md).

## What the run measures

The written case fits a noise model of two contractions and draws its operating characteristics from that same
model. This run draws the series from gate noise instead and reads each one with the case's own decision
(`count_statistics`, `decide`, `outcome` of `scripts/qi_pathion_null_rotation_scan_cases.py`):

- five one-parameter noise families on the five region qubits (two-qubit depolarizing per CZ, phase damping per
  pulse, phase damping per CZ, amplitude damping per CZ, amplitude with phase damping on pulses and CZ), each set
  to the center-arm visibility 0.44 of the retained b0 runs;
- per family the planted truths: no offset; every root of an x rotation on all pulses and on q8's pulses, of a y and
  of a z rotation on all pulses, and of an amplitude scale on every pulse angle, each at center contrast +0.0164; a
  selector flip conditioned on q12 and a selector dropout conditioned on the coin at that contrast; a CZ
  conditional-phase error of -0.08 and +0.08 rad;
- two readout regimes: the mean retained bracket rates held fixed, and a walk through the sixteen retained brackets
  of the one-CZ series in recorded order (q11's e10 moves between 0.03 and 0.43 there);
- 40 series per family, truth and regime at the case's shots (131,072 per data circuit, 32,768 per readout
  circuit), all 21 batches, guard and bridge applied.

Cross-checks inside the kernel: the noisy laws against Qiskit Aer's density-matrix method on the T4
(`GOROROBA_AER_DEVICE=GPU`), and the ten circuits of the QX twin on qxelarator 0.10.0 at 131,072 shots against
their `ideal` laws.

## Falsifiers

- A truth whose class the decision names wrongly in more than 1 of 40 series falsifies the case's statement that
  no simulated run reads a class other than its truth's, for that noise family.
- A stable-readout scenario whose x truth on all pulses reads `pulse_x` in fewer than 36 of 40 series falsifies the
  case's 99.8 percent row for that family.
- A retained-walk regime in which fewer than half of the series keep one admitted batch of each scan kind and both
  bridge batches falsifies the guard and bracket layout as a workable design at the retained readout behavior.

Expected-value labels computed on the build host before the push (no sampling noise, mean readout): every truth
reads its class under the three unital families; under amplitude damping per CZ the y and z rotations at -0.073 rad
read `pulse_x`, the q12 flip reads `x_excluded` and the dropout reads `unresolved_none`.

## What the simulation cannot answer

The channel Tuna-17 applies during b0 is unpublished, and the retained b0 histograms deviate from every modeled
world by a deviance of 880 to 7,900 on 31 outcomes, so the five families are sensitivity points, not an estimate of
the device. T1, T2, leakage, residual ZZ and pulse shapes are outside the run.

## Machine, time, quota

Kaggle `NvidiaTeslaT4` (two T4, 4 CPU cores), `--with qx-emulator --with exact-arithmetic`, `--timeout 28800`.
Measured on the build host: one stable-regime series takes about 10 s of one core (the per-batch retention fit);
85 scenarios at 40 series and two regimes give about 48,000 core-seconds, 3.3 hours on four cores at the build
host's rate. The entry rewrites its record after every scenario, so a session that ends early returns the
scenarios finished. GPU quota used: at most 8 of the weekly hours.

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/kaggle_run.py push scripts/qi_pathion_null_rotation_scan_noise.py \
	--slug gororoba-null-rotation-scan-noise --machine NvidiaTeslaT4 --timeout 28800 \
	--with qx-emulator --with exact-arithmetic \
	--include results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json \
	--include results/quantum_inspire/cases/pathion_coset_coin_tuna_17/batch-02 \
	--include results/quantum_inspire/cases/pathion_null_rotation_scan_qx \
	--include results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/batch-01/cases.json \
	--include docs/evidence/anu_qrng/draw-2026-11-13T172143Z.json \
	-- --run /kaggle/working/output/null-rotation-scan-noise.json --series 40 --cross-check
```
