# Conditional Ramsey power under the Kingston calibration

`result.json` is the output of `scripts/conditional_ramsey_power.py` at its
defaults: 4000 resamples, 400 of them with plug-in errors. It ran as Kaggle
kernel version 2 of `gororoba-conditional-ramsey-power`, and the run is retained
under `results/kaggle/2026-10-16T055350Z-gororoba-conditional-ramsey-power/`.

- **Machine and software.** Two Tesla T4 GPUs, CUDA 13.0, Python 3.13.15,
  numpy 2.1.3, qiskit 2.5.2 and qiskit-aer-gpu-cu11 0.17.2, with four
  workers (`kaggle_environment.json`).
- **Stack proof.** The kernel built the hypercomplex package stack before
  its entry ran, and it regenerated the retained tables byte for byte
  (`kaggle_hypercomplex.json`).
- **Noise.** `docs/evidence/calibration/ibm_kingston.json`, calibration
  2026-10-15T19:42:21-07:00. The held records were planned against the
  15:29:07 calibration, so this one is 4 h 13 min later.

Version 1 of the kernel ran on a CPU machine with each Hamiltonian placed
after a whole idle. It is retained under
`results/kaggle/2026-10-16T044107Z-gororoba-conditional-ramsey-power/` as
history only, and this result replaces it.

## Question

The held conditional Ramsey case on pairs (A, B) = (68, 67) and (67, 66)
quotes delta-method standard errors from noisy laws with every rate at
zero, because the planner's noise model has no detuning and no Z Z term.
This run asks three things once the rates the case measures are present:

- whether those errors still hold;
- whether the intervals a collected run would report still hold;
- whether the falsifier still works.

**Falsifier, stated before the run.** The quoted precision fails if any of
the following holds in any scenario:

- the Monte Carlo spread departs from the delta-method error by more than
  15 percent;
- interval coverage of the injected value falls below 0.93;
- more than 0.5 percent of trials slip a phase unwrap.

## Method

1. **Compile.** Each of the 50 circuits is compiled to the snapshot Target
   on the pair's physical qubits, at optimization level 1 with seed 11.
2. **Slice and inject.** Every idle is cut into slices of at most 125 dt
   (0.5 us). Each slice is followed by its share of `exp(-i H t)` as a
   noise-free diagonal unitary, with
   `H / hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2`. Amplitude
   damping on B does not commute with `Z_A Z_B`, so the slices keep a B
   decay inside the idle where it happens.
3. **Exact noisy laws.** `gororoba_quantum/snapshot_laws.py` simulates each
   compiled arm on the qubits it touches with live_run's gate, idle
   relaxation and assignment noise. Its self-check (gate core-302) equates
   that restricted law with the statevector law and with the whole-device
   simulation.
4. **Resample.** Each scenario is resampled 4000 times, as a whole job of
   1024 shots per circuit, in 16 seeded blocks through `parallel.py`. The
   first 25 trials of each block also carry their own plug-in errors from
   `conditional_ramsey.summarize_distributions`, the figure a collected run
   emits.
5. **Scenarios** (Hz):

| Scenario | omega_A | omega_B | J | conditional-arm Stark shift |
| --- | ---: | ---: | ---: | ---: |
| zero | 0 | 0 | 0 | 0 |
| window_on_a | -40,900 | 0 | 0 | 0 |
| split | -20,450 | 15,000 | 3,000 | 0 |
| wound | 186,787 | -10,000 | 20,000 | 0 |
| stark_300, _600, _1200 | -20,450 | 15,000 | 3,000 | 300, 600, 1200 |

The coherence window's rotation was 40.9 kHz modulo 227.7 kHz. In
`window_on_a` that rotation sits on A alone, and in `wound` it is one turn
up.

## Result

The conditional arms keep only the shots whose B readout equals B's
preparation (`conditional_ramsey.conditioned`). With that postselection,
across all 14 pair-scenarios:

- The Monte Carlo spread divided by the delta-method error lies between
  0.977 and 1.023 for every parameter.
- Coverage of the injected value lies between 0.944 and 0.957 with the
  quoted error, and between 0.927 and 0.973 with each trial's plug-in error.
  The second range is over 400 trials per scenario, where coverage has a
  standard error of about 0.011.
- No trial slips an unwrap, including the 186.8 kHz wound rate.
- The noise-induced systematic error is at most 1.7 Hz for J and at most
  8.9 Hz for the falsifier residual.
- With no departure, the falsifier rejects 5.0 to 5.5 percent of trials
  with the quoted error, and 3.5 to 6.0 percent with plug-in errors.
  The rejection rate is its power against a Stark shift on the conditional
  arms:

| Pair | delta-method SE of J (Hz) | SE of residual (Hz) | power at 300 Hz | 600 Hz | 1200 Hz |
| --- | ---: | ---: | ---: | ---: | ---: |
| (68, 67) | 118 to 133 | 358 to 398 | 0.350 | 0.885 | 1.000 |
| (67, 66) | 102 to 122 | 319 to 366 | 0.430 | 0.943 | 1.000 |

The case quoted 126 and 112 Hz for J and 384 and 356 Hz for the residual
at 1024 shots. Those values fall inside the ranges above.

Without the postselection, the summary the held records were planned with fails whenever J is nonzero
(`unconditioned_systematic_hz`).

- **Mechanism.** B in `|1>` relaxes during the idle. A decayed shot carries
  A's phase at `omega_A + J` from the jump onward, which pulls the
  `A | B = 1` rate toward `A | B = 0`.
- **Bias at J = 3 kHz.** J reads 178 Hz low on (68, 67) and 397 Hz low on
  (67, 66). The falsifier residual moves by -364 and -800 Hz, 0.9 and 2.3
  of its standard errors. The second pair is worse because qubit 66 has
  T1 = 121 us, against 273 us for qubit 67.
- **Bias at J = 20 kHz** (`wound`). J reads 45 and 118 Hz low. The phase a
  decayed shot carries winds faster and averages out, so the bias does not
  scale linearly with J and no fixed correction replaces the
  postselection.

`slice_convergence` gives the unconditioned J bias on (67, 66) in `split`.
It reads -715 Hz with the Hamiltonian after a whole idle, -411 Hz at 500 dt
slices and -402 Hz at 250 dt slices, against -397 Hz at the 125 dt slices
used here. The postselected bias stays within 1.1 Hz throughout.

## Limits

- **Model scope.** The model has the planner's noise only. Coherent
  over-rotation, crosstalk, leakage, readout crosstalk that depends on B, and
  rates that drift within the job are absent.
- **What the run establishes.** It shows that the design and its summary
  recover a static diagonal Hamiltonian at this noise level with honest
  errors. It says nothing about the rates on the device.
- **Held records.** Their summaries were computed with the unconditioned
  estimator. Any submission needs a fresh dry run, so that the record
  carries the postselected summary and its errors.

## Replay

Gate core-301 first requires `result.json` to be byte-identical to the
output recorded in the run's `collect.json` ledger. It then reruns pair
(68, 67) in the `split` and `stark_600` scenarios on the CPU, at 400 trials
(32 with plug-in errors), and requires two things:

- the exact-law estimates, the delta-method errors and the unconditioned
  biases match `result.json` to 1e-8 relative;
- each spread-to-error ratio agrees within five standard errors of the
  difference of two independent spread estimates.

Gate core-300 lints and type-checks the script.
