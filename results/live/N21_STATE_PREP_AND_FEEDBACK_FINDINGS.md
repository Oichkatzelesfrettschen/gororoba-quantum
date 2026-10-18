# n21 feedback on ibm_kingston: initialization bound and endpoint

Program and approvals: [N21_STATE_PREP_CONTROL_CASE.md](N21_STATE_PREP_CONTROL_CASE.md).
All five jobs ran on 2026-10-18 under the ibm_kingston calibration
2026-10-18T01:38:20-07:00 and billed 48 s.

## Endpoint: feedback changes no measured outcome

n21-feedback-encoded ran at 50 us with 100,000 shots per arm on qubits 104,
105, 106, 117, 124, 125 and 126 (`2026-10-18T090603.530638Z/collect.json`,
job `dba8r7k24mrc738527d0`).

| Quantity | Measured | Model replay at execution calibration |
|---|---|---|
| feedback signed contrast | -0.0042 | +0.0059 |
| no-feedback signed contrast | -0.0069 | -0.0285 |
| contrast difference | +0.0027, 95 % interval [-0.0129, +0.0184] | +0.0344 |
| labeled TVD between arms | 0.0038 | 0.0193 |

The preregistered endpoint does not reject zero: the detection radius is
0.0147 under the empirical-Bernstein split, and the plan held power 0.8 at
the planned effect 0.0310. The model's difference, 0.0344, lies above the
interval's upper end, so the device suppresses the effect the calibration
noise model predicts. Both arms read near-uniform four-outcome
distributions, (0.269, 0.245, 0.237, 0.249) and (0.265, 0.245, 0.237,
0.252). Each lies 0.026 and 0.029 TVD from its own replay, which carries
the bounded initial excitation 0.0144 on every active qubit. A channel
outside the model therefore removes the feedback-dependent structure.
Readout correction is skipped for feed-forward circuits, so these values are
raw.

The run separates no mechanism. Candidates the retained data can test
next: mid-circuit measurement error above the reported assignment error,
feed-forward latency beyond the 20 us classical allowance, and dephasing
during the conditional branch.

## Initialization bound that set the plan

`scripts/state_prep_excess.py` bounds the initial excitation of the
placement from the four control jobs (149 qubits each,
`2026-10-18T0834*`): eps50 0.014392 and eps250 0.015745, both at q125, from
447 simultaneous Clopper-Pearson bounds at alpha 0.01. The fixed point
converged on the first re-plan (`2026-10-18T085924.738302Z/state-prep-excess.json`).
On q125, x_history at 50 us reads 249/32768 and prep0 at 250 us 118/16384,
against e10 0.0073 in both the model and the execution calibration.

## Control survey (descriptive)

Point estimates over the 149 controlled qubits:

| Arm | Median | Mean | Maximum |
|---|---|---|---|
| prep0 at 50 us | 0.0045 | 0.0096 | 0.0800 (q58) |
| prep0 at 250 us | 0.0047 | 0.0089 | 0.0685 (q131) |
| x_history at 50 us | 0.0058 | 0.0107 | 0.0797 (q58) |
| x_history at 250 us | 0.0051 | 0.0089 | 0.0699 (q131) |

The shot-history effect (x_history minus prep0) averages +0.0011 at 50 us
and +0.00003 at 250 us. A `|1>` end state leaves measurable excitation only
at the short delay: q62 reads +0.030 there. The delay effect on prep0 is
largest on q58, 0.080 at 50 us against 0.030 at 250 us. Each history
difference spans a dynamic and a static job as well as the shot history.
Shots with two or more excited qubits match the independent-qubit
expectation within counting error (70 against 58.3 at prep0 50 us, 74
against 67.9 at x_history 50 us).
