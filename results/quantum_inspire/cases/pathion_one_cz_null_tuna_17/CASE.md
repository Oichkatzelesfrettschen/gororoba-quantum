# Case: Tuna-17 selector offset of the null block, joint readout characterization and 6-CZ routing

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
`scripts/qi_pathion_one_cz_null_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of this
directory except this one, and the QX twin `../pathion_one_cz_null_qx/`). Ledger row: A5-186.

## What the run measures

The coin series read the null block b0 (operand e1 + e17, coset 0, 21 routed CZ) at a raw selector contrast of
+0.0164 +- 0.0039, where every arm-symmetric product readout and every unital or relaxation channel gives 0. Three
hypotheses reproduce the size (`docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt`, sized to +0.0164 on b0):

| hypothesis | b0 | 6-CZ blocks k4, k8, k12 | joint readout of coin q2, selector q8, q12 |
|---|---|---|---|
| coherent X90 over-rotation, about +0.03 rad | +0.0167 | 0 | no conditional selector effect |
| selector dropout when the coin reads 1 (an arm-asymmetric readout), x 0.036 | +0.0164 | +0.0164 | selector 1 misread more often with the coin prepared 1 by 0.036 |
| selector flip when q12 reads 0 (a readout correlation), x 0.036 | +0.0164 | 0 | misassignment of the selector larger with q12 prepared 0 by 0.036 |

A 1-CZ test does not exist on this device: a coin block compiles to 3 CZ at all-to-all connectivity, and with b0's whole
role map held it routes to 12 CZ, where the over-rotation itself predicts +0.028 (0.0279 to 0.0549 over every candidate
of the search). With only the selector on q8 and the coin on q2 held (data qubits d0 q4, d1 q12, d2 q11), the blocks k4,
k8 and k12 route to 6 CZ and the over-rotation predicts 0. The 6-CZ block therefore separates the over-rotation from a
coin-conditioned readout offset but not from a q12 correlation, because q12 holds d1 and not d0 there. The joint
readout characterization closes that gap by measuring the selector's misassignment conditioned on the coin and on q12
directly, so the series has two independent observables per hypothesis.

Circuits (Tuna-17, 17 qubits measured in every circuit):
- batches 00 to 02: the eight computational-basis preparations of (q2, q8, q12) with X gates only, every other
  register qubit in |0>, at 32,768 shots each (`joint-abc.cq`, a, b, c the prepared q2, q8, q12);
- batches 03 to 06: [readout-0, template, readout-1] for b0 (byte-equal replay of the retained
  `pathion_coset_coin_tuna_17/batch-02/b0.cq`, transpiler seed and role map of the coin series), k4, k8 and k12, at
  65,536 shots, each template corrected with the assignment its own batch measured. The routing seeds are values 0, 64
  and 128 of `docs/evidence/anu_qrng/draw-2026-11-07T163258Z.json`; no new draw was needed.

The QX twin (`../pathion_one_cz_null_qx/`, one batch, the four templates at 2,048 shots) predicts the ideal laws
exactly.

## Why simulation cannot answer it

The simulation fixes what each hypothesis predicts (the table above); which one the device obeys is a device fact: the
X90 calibration of Tuna-17 and the conditional misassignment of the selector given the states of the coin and of q12 are
not published, and the retained readout circuits excite all 17 qubits, so they cannot separate a conditional effect from
the context of the others. A noise simulation of a calibration that is not known reproduces any of the three.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7, `tuna_17`), region q2, q4, q8, q11, q12 (the excluded qubits of the coin series, q15 and q13, stay out).
  QX emulator (type 1) for the twin.
- Jobs and shots: 20 jobs in 7 batches of at most 3 circuits, 1,048,576 shots in all (joint 8 x 32,768; templates
  4 x 3 x 65,536).
- Expected execution: 569 to 619 s at the 0.54 to 0.59 ms per shot of the coin series' nine 65,536-shot jobs
  (`results.json` `execution_time_in_seconds`), plus six 30 s pauses between batches (the coin series ran its pause at
  30 s): about 13 minutes with queueing.
- Quota: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this account.
- Precision (`prediction.json`, `design`): the raw selector contrast of a template at 65,536 shots has a standard
  error of 1/256 = 0.0039. The joint statistics have standard errors of 0.0010 (selector prepared 0) and 0.0008 (selector
  prepared 1) at 32,768 shots under the retained readout of q8, so the 0.036 effect sits 37 and 44 standard errors out,
  and three standard errors stay under the 0.012 exclusion threshold. A statistic coarser than 0.004 (joint) or 0.0045
  (template selector) reads "uninformative".

## Preregistered decision rules

Z = 3 standard errors. The raw counts are read; the coin read gives the arm.

1. Control: b0's raw selector contrast above 3 se (expected 0.0164 against 0.0117, probability about 0.89). Otherwise
   the offset has drifted away and nothing about the mechanism is decided.
2. 6-CZ class from the inverse-variance mean s of the raw selector contrasts of k4, k8, k12 (se about 0.0023) and b0's
   contrast s0: zero when |s| is within 3 se of 0 and s - s0 is beyond 3 combined se; b0-like when s - s0 is within 3
   combined se and |s| is beyond 3 se; otherwise unresolved.
3. Coin class from D, the misassignment of a prepared selector 1 with the coin prepared 1 minus the coin prepared 0
   (each pooled over the two q12 preparations): large when D >= 0.036 - 3 se and D >= 3 se; small when |D| + 3 se < 0.012
   at a prepared selector 0 and at a prepared selector 1; otherwise mid.
4. q12 class from G(s), the misassignment of the selector prepared s with q12 prepared 0 minus q12 prepared 1: large
   when either G(0) or G(1) is >= 0.036 - 3 se and >= 3 se; small when |G| + 3 se < 0.012 at both; otherwise mid.

| 6-CZ | coin | q12 | outcome | effect on A5-186 |
|---|---|---|---|---|
| zero | small | small | over-rotation supported; both readout offsets excluded | survives, falsifier unmet |
| b0-like | large | small or mid | coin-conditioned selector dropout supported | refuted as an over-rotation: an arm-asymmetric readout effect |
| zero | small or mid | large | q12 correlation supported | weakened: a measured readout correlation explains the offset |
| b0-like | small | small | neither an over-rotation nor a measured readout offset | refuted as stated; mechanism open |
| any other | | | unresolved, numbers reported | unchanged |

Falsifiers: the over-rotation row fails if the 6-CZ mean reads b0-like or a joint effect reaches 0.036; the dropout row
fails if the 6-CZ mean reads zero. The control must hold in the same series: a b0 below 3 se reads "offset absent". QX:
every template within twice its sampling floor of its ideal law (`qx_control.pass`). The readout-corrected N_hat of
each template, the coin read fraction and the readout drift between brackets are reported beside the decision and
stop nothing.

IBM reference for the same question (`results/live/pathion_parallel_coset_analysis.json` and `d1_ibm_overrotation.txt`
on branch `pathion/interpret-tuna-ascella-runs`; ibm_fez 17 and ibm_kingston 16 parallel placements): the 20-CZ k0
selector contrast reads -0.0020 +- 0.0015 and -0.0000 +- 0.0011, and the 1-CZ blocks average -0.0008 +- 0.0007 and
-0.0001 +- 0.0010. IBM shows no over-rotation (-0.0036 +- 0.0027 and -0.0000 +- 0.0019 rad; pooled with the earlier two
readings -0.0015 +- 0.0014 rad, 4.3 combined standard errors below the Tuna angle +0.0295 +- 0.0070 rad, under the
0.57 per rad response of the written k0 compile; no ibm_kingston compile was simulated).

## What made the coin series succeed, and its challenges

- Coin interleaving of both arms in one job: one routed CZ puts both orientation arms into every shot, so one job, one
  routing and one calibration carry the contrast (the series' resolution, pattern and cocycle-free decisions all held:
  `ba` selector 0.2350 +- 0.0038, `xor_ba` -0.7181 +- 0.0054).
- A readout-0 and readout-1 bracket in every data batch: a drift between batches is a stratum to correct, not a stop.
  The stopped predecessor halted on q11 e10 moving from 0.2762 to 0.1066 (limit 0.02).
- Region exclusions: q15 (P(0|1) 0.270) and q13 (its |1> misassignment doubles beside an excited q11) are left out, and
  the five-qubit region keeps every coupler under the residual coupling limit.
- Challenges: the null block read +0.0164 where every symmetric channel gives 0; the readout-corrected agreement with
  IBM failed on `ba` bins 1, 5 and 7 (the misses follow the logical bit d2, `c3_walsh.txt`); the retained readout
  circuits excite all 17 qubits, which this case's joint preparations replace by three-qubit preparations. A drift of
  the offset itself between 2026-11-07 00:10Z and the run is the control's risk.

## Not built

- The Ry emulator: the circuits are expressible (X90 as Rx(pi/2), CZ as H-CNOT-H on `qubit[5]` with no bit register and
  no measure statement, qubit 0 leftmost), but a coarse +-0.03 check at 3 se needs 9 jobs of 1,024 shots per template
  (27 jobs of 16 s in 9 batches on the shared hardware pause, about 12 minutes) on a noise model that is
  undocumented, so it is left out with this reason.
- A series gate for this series: `scripts/qi_pathion_coset_coin_series.py --submit-next` names the coin series.
  The commands below use `qi_platform.py` directly, with `--sanity` binding each collected batch to this case.

## Submission commands (not run)

The owner's approval is quoted in `--approval` (written case: what it measures, why simulation cannot answer it, the
backend, shots and expected seconds above; no credits).

```sh
export PYTHON=/home/eirikr/.cache-wsl-capsule/gororoba-quantum/ci-py3.14.7/bin/python3
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)

"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --check "$CASES"
"$QI_PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: one batch, then its control analysis.
qx="$RUNS/$STAMP-pathion_one_cz_null_qx-batch-00"
cp -R "$CASES/pathion_one_cz_null_qx/batch-00" "$qx"
"$QI_PYTHON" scripts/qi_platform.py submit "$qx" --backend-type-id 1 --approval "QUOTE"
"$QI_PYTHON" scripts/qi_platform.py collect "$qx" --poll 15 --timeout 3600
"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --analyze "$qx" --out results/quantum_inspire/pathion_one_cz_null_qx_analysis.json

# Tuna-17: seven batches in order; each after the previous collection and sanity check and the 30 s pause.
for n in 00 01 02 03 04 05 06; do
	run="$RUNS/$STAMP-pathion_one_cz_null_tuna_17-batch-$n"
	cp -R "$CASES/pathion_one_cz_null_tuna_17/batch-$n" "$run"
	"$QI_PYTHON" scripts/qi_platform.py submit "$run" --backend-type-id 7 --approval "QUOTE"
	"$QI_PYTHON" scripts/qi_platform.py collect "$run" --poll 15 --timeout 3600
	"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --sanity "$run"
done
"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json
```

Stop the series at the first platform failure and never resubmit a directory that holds `submission.json`
(`qi_platform.py reconcile` recovers its receipt); see `docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The
retention change that follows holds the run directories, both analyses, a refreshed `usage.json` and the
`docs/state/research_state.json` registration.
