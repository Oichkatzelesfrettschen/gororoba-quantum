# Conditional Ramsey power under the Kingston calibration

`result.json` is the output of `scripts/conditional_ramsey_power.py
--trials 4000`. It ran as Kaggle kernel version 1 of
`gororoba-conditional-ramsey-power`, from the commit named in that run's
`submission.json` under `results/kaggle/2026-10-16T044107Z-gororoba-conditional-ramsey-power/`.

- **Machine and software.** A 4-core CPU machine with no accelerator, Python
  3.13.15, numpy 2.1.3, qiskit 2.5.2 and qiskit-aer 0.17.2
  (`kaggle_environment.json`).
- **Stack proof.** The kernel built the hypercomplex package stack before
  its entry ran, and it regenerated the retained tables byte for byte
  (`kaggle_hypercomplex.json`).
- **Noise.** `docs/evidence/calibration/ibm_kingston.json`, calibration
  2026-10-15T19:42:21-07:00. The held records were planned against the
  15:29:07 calibration, so this one is 4 h 13 min later.

## Question

The held conditional Ramsey case on pairs (A, B) = (68, 67) and (67, 66)
quotes delta-method standard errors from noisy laws with every rate at
zero, because the planner's noise model has no detuning and no Z Z term.
This run asks two things:

- whether those errors, the 95 percent intervals built from them, and the
  falsifier still hold once the rates the case measures are present;
- whether the estimator recovers those rates.

**Falsifier, stated before the run.** The quoted precision fails if any of
the following holds in any scenario:

- the Monte Carlo spread departs from the delta-method error by more than
  15 percent;
- interval coverage of the injected value falls below 0.93;
- more than 0.5 percent of trials slip a phase unwrap.

## Method

1. **Compile.** Each of the 50 circuits is compiled to the snapshot Target
   on the pair's physical qubits, at optimization level 1 with seed 11.
2. **Inject the Hamiltonian.** `exp(-i H t)` is inserted as a noise-free
   diagonal unitary after every idle, with
   `H / hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2`.
3. **Exact noisy laws.** Each law comes from an Aer density matrix with
   live_run's gate, idle relaxation and assignment noise, restricted to the
   pair. Inserting the Hamiltonian after the idle is exact, because the
   Hamiltonian is diagonal and the relaxation channels are phase covariant.
4. **Resample.** Each scenario is resampled 4000 times, as a whole job of
   1024 shots per circuit.
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

- The Monte Carlo spread divided by the delta-method error lies between 0.980 and 1.036
  for every parameter.
- Coverage of the injected value lies between 0.939 and 0.956.
- No trial slips an unwrap, including the 186.8 kHz wound rate.
- The noise-induced systematic error is at most 2.4 Hz for every rate and
  at most 8.2 Hz for the falsifier residual.
- With no departure, the falsifier rejects 4.7 to 5.3 percent of trials.
  The rejection rate is its power against a Stark shift on the conditional
  arms:

| Pair | delta-method SE of J (Hz) | SE of residual (Hz) | power at 300 Hz | 600 Hz | 1200 Hz |
| --- | ---: | ---: | ---: | ---: | ---: |
| (68, 67) | 118 to 133 | 358 to 398 | 0.347 | 0.886 | 1.000 |
| (67, 66) | 102 to 122 | 319 to 366 | 0.420 | 0.949 | 1.000 |

The case quoted 126 and 112 Hz for J and 384 and 356 Hz for the residual
at 1024 shots. Those values fall inside the ranges above.

Without the postselection, the estimator the held case's records were planned with fails
whenever J is nonzero (`unconditioned_systematic_hz`).

- **Mechanism.** B in `|1>` relaxes during the idle. A decayed shot carries
  A's phase at `omega_A + J` from the jump onward. That pulls the
  `A | B = 1` rate toward `A | B = 0`.
- **Bias in J.** At J = 3 kHz, J reads 304 Hz low on (68, 67) and 715 Hz low
  on (67, 66). The second pair is worse because qubit 66 has T1 = 121 us,
  against 273 us for qubit 67.
- **Bias in the residual.** The falsifier residual moves by -616 and
  -1435 Hz, 1.6 and 4.1 of its standard errors. A static model that holds
  is therefore rejected in most runs on the second pair.
- **Scaling.** At J = 20 kHz the biases change sign and size (+241 and
  +700 Hz in J), so no fixed correction replaces the postselection.

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

Gate core-291 reruns pair (68, 67) in the `split` and `stark_600`
scenarios on the CPU, at 400 trials. It requires two things:

- the exact-law estimates and delta-method errors match `result.json` to
  1e-8 relative;
- each spread-to-error ratio agrees within five standard errors of the
  difference of two independent spread estimates.

Gate core-290 lints and type-checks the script.
