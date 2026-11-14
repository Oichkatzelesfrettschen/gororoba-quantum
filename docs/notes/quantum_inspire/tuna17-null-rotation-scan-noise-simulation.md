# Tuna-17 injected-rotation scan under physical noise: simulation case

Status: numerical simulation on Kaggle, run under the standing approval for Kaggle sessions below 12 hours (root
AGENTS.md, "Hardware services"). It submits nothing to Quantum Inspire. Entry:
`scripts/qi_pathion_null_rotation_scan_noise.py`. Subject: the written case
[pathion_null_rotation_scan_tuna_17](../../../results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/CASE.md).

## What the run measures

The written case's operating characteristics draw each truth from a noise model its fit contains, admit every
batch and leave the bridge out. This run draws whole series of counts from gate noise and reads each one with the
case's own decision (`count_statistics`, `decide`, `outcome` of
`scripts/qi_pathion_null_rotation_scan_cases.py`), through the readout guard, the bridge and the per-batch fit:

- five one-parameter noise families on the five region qubits (two-qubit depolarizing per CZ, phase damping per
  pulse, phase damping per CZ, amplitude damping per CZ, amplitude with phase damping on pulses and CZ), each set
  to the center-arm visibility 0.44 of the retained b0 runs;
- per family the planted truths: no offset; every root of an x rotation on all pulses and on q8's pulses, of a y and
  of a z rotation on all pulses, and of an amplitude scale on every pulse angle, each at center contrast +0.0164; a
  selector flip conditioned on q12 and a selector dropout conditioned on the coin at that contrast; a CZ
  conditional-phase error of -0.08 and +0.08 rad;
- three regimes per truth. `stable`: the mean retained bracket rates held fixed, the fit carrying all five
  families. `retained_walk`: the readout walks through the sixteen retained brackets of the one-CZ series in
  recorded order (q11's e10 moves between 0.03 and 0.43 there), same fit. `stable_family_left_out`: stable
  readout, and the fit carries the four families other than the one the truth was drawn from, so the truth's
  noise is absent from the fit's noise models;
- 12 series per family, truth and regime at the case's shots (131,072 per data circuit, 32,768 per readout
  circuit), all 21 batches.

Cross-checks inside the kernel: the noisy laws against Qiskit Aer's density-matrix method on the T4
(`GOROROBA_AER_DEVICE=GPU`), and the ten circuits of the QX twin on qxelarator 0.10.0 at 131,072 shots against
their `ideal` laws.

## Scan set

The earlier scan set (all pulses at +-5 and +-10 degrees, q8's pulses at +-5 and +-10 degrees) was read by a fit
of two contractions. Under amplitude damping per CZ its expected-value labels read a y and a z rotation as
`pulse_x` (at -0.0727 rad, that computation's sizing of the center contrast +0.0164). With the damping family in the fit the labels turn undecided: a y rotation at
-0.0711 rad (the case's sizing at the design readout) and an x rotation of q8's pulses differ by a chi-square of
15 at expected values, below the separation of 25. The shot-level run sizes the same truth at -0.0716 rad
(visibility 0.44 through the mean retained brackets).

Two repairs follow. The fit carries the five gate-noise families as noise models beside its 13 contraction shares
(`noise_models` in the scan module). The scan set is chosen among five candidates of four scan kinds each by
expected-value decisions under seven noise truths (95 planted truths), once with every family in the fit and once with the truth's own
family left out (67 planted truths). The gap is the smallest chi-square distance between a truth's class and the
nearest other class; a decision needs 25.

| Scan set | Undecided of 95 | Smallest gap | Undecided of 67, family left out | Smallest gap, family left out |
|---|---|---|---|---|
| all +-5, q8 +-5, q8 +-10, all +-10 (earlier set) | 4 | 10.4 | 3 | 13.4 |
| all +-5, all +-15, q8 +-10, all +-10 | 0 | 28.2 | 2 | 16.6 |
| all +-5, q4 +-10, q8 +-10, all +-10 | 3 | 9.7 | 2 | 16.3 |
| all +-5, q8 +-15, q8 +-10, all +-10 | 3 | 10.5 | 2 | 8.7 |
| all +-10, q4 +-10, q8 +-10, all +-20 (adopted) | 0 | 55.1 | 0 | 50.3 |

No candidate reads a wrong class at expected values. Every candidate holds four scan kinds, so the
batch count stays at 21. The adopted set's +-20 degree arms lean on the premise that `Rx(pi/2 + k pi/36)` is
the X90 pulse at a scaled amplitude, which the bridge tests at k = 0 only.

## Falsifiers

- A truth whose class the decision names wrongly in more than 1 of 12 series, in any regime, falsifies the case's
  statement that no simulated run reads a class other than its truth's, for that noise family. Over one family and
  regime (about 17 truths, 204 series) more than 3 wrong series falsify it as well.
- A `stable` scenario whose x truth on all pulses reads `pulse_x` in fewer than 10 of 12 series falsifies the
  case's operating-characteristic row (at least 0.9983) for that family.
- A `retained_walk` regime in which fewer than half of the series admit all eight scan batches and both bridge
  batches falsifies the guard and bracket layout as a workable design at the retained readout behavior.
- A `stable_family_left_out` scenario may read `unresolved_none`: the adequacy limit refuses a fit whose noise
  models miss the truth's noise. A wrong class there, under the first falsifier's count, shows that the limit
  fails to protect the decision against a noise family outside the fit.

Measured on the build host before the push, four series per regime under amplitude damping per CZ: no offset reads
`offset_absent` in 12 of 12; a y rotation at -0.0716 rad reads `pulse_other` in 4 (stable), 3 (walk, one
`unresolved_bridge`) and 2 (family left out, two `unresolved_none`); a y rotation at +0.0621 rad reads
`pulse_other` in 4, 4 and 3 (one `unresolved_none`). The `unresolved_bridge` series holds two bridge differences
of -2.1 and -2.3 standard errors, whose pooled value passes 3; the bridge rule refuses 7 of 2,000 walk series
drawn with equal `Rx(pi/2)` and `X90` laws (0.35 percent).

## What the simulation cannot answer

The channel Tuna-17 applies during b0 is unpublished, and the retained b0 histograms deviate from every modeled
world by a deviance of 880 to 7,900 on 31 outcomes, so the five families are sensitivity points, not an estimate of
the device. T1, T2, leakage, residual ZZ and pulse shapes are outside the run.

## Machine, time, quota

Kaggle `NvidiaTeslaT4` (two T4, 4 CPU cores), `--with qx-emulator --with exact-arithmetic`, `--timeout 39600`.
Measured on the build host: the strength-grid tables of the five families take 99 CPU-minutes, built once at the
start of the run; one series takes about 20 s of one core (36 series and 6 expected-value labels in 357 s on four
cores). 85 scenarios at 12 series and three regimes give about 61,000 core-seconds, 4.7 hours on four cores at the
build host's rate with the tables; the 11-hour limit leaves a factor of 2.3 for slower cores. The damping families
run first. The entry rewrites its record after every scenario. GPU quota used: at most 11 of the weekly hours.

```sh
export PYTHON="${PYTHON:-python3}"
STOPPED=results/quantum_inspire/runs/2026-11-06T221626Z-pathion_coset_block_tuna_17
"$PYTHON" scripts/kaggle_run.py push scripts/qi_pathion_null_rotation_scan_noise.py \
	--slug gororoba-null-rotation-scan-noise --machine NvidiaTeslaT4 --timeout 39600 \
	--with qx-emulator --with exact-arithmetic \
	--include results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json \
	--include results/quantum_inspire/cases/pathion_coset_coin_tuna_17/batch-02 \
	--include results/quantum_inspire/cases/pathion_null_rotation_scan_qx \
	--include results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/batch-01/cases.json \
	--include docs/evidence/anu_qrng/draw-2026-11-13T172143Z.json \
	--include "$STOPPED-batch-00/raw/readout-0.cq.json" \
	--include "$STOPPED-batch-01/raw/readout-1.cq.json" \
	--include "$STOPPED-batch-02" \
	--include "$STOPPED-batch-03/raw/readout-1.cq.json" \
	-- --run /kaggle/working/output/null-rotation-scan-noise.json --series 12 --cross-check \
	--kinds cz_damping damping_and_dephasing cz_depolarizing pulse_dephasing cz_dephasing
```
