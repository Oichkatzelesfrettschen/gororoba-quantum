# IQM Garnet diagnostic of the unitary-arm excess

This case separates two causes of the unitary-n16 excess that the pinching case's pre-flight stop rule reported
([pinching design, "Pre-flight stop rule"](iqm-garnet-measurement-sequence-pinching.md#pre-flight-stop-rule)): an axis
phase per small-angle prx pulse, and |1> loss during the 2 us pre-readout idle and the readout. The case directory is
[results/iqm/cases/measurement-sequence-diagnostic](../../results/iqm/cases/measurement-sequence-diagnostic/cases.json),
built by `scripts/iqm_measurement_diagnostic.py build DIR --live` from Garnet's default calibration set
`be070414-7624-4943-ac7e-1e2678f05684` (not retired at the build). It runs one job of eight circuits at 1000 shots on
QB5, QB7, QB11, QB14, QB17 and QB19 with the options of the window probes (one active-reset cycle, no heralding).

## Why a comparison in the right space comes first

The stop rule compared the probes' raw P(0) of the unitary-n16 circuit (0.19, 0.21, 0.25, 0.14, 0.22, 0.38) with the
pinching case's corrected planning values (0.053 to 0.094). Those two live in different spaces: the circuit ends near
|1>, so the raw reading carries the assignment error e10, the 2 us of relaxation, and the 6.8 % of shots that start
excited and flip to |0> under the pulses. Against the raw model of the same circuit (0.182, 0.218, 0.172, 0.169, 0.164,
0.177 at the calibration and an assumed excitation p = 0.068) the probe readings sit at +0.2, -0.2, +2.1, -0.8, +1.5 and
+5.3 binomial standard errors (100 shots) on QB5, QB7, QB11, QB14, QB17 and QB19. Only QB19 is far from its model on the
final key alone, QB11 and QB17 are marginal, and the fixed 0.00 to 0.20 stop band sits below the raw model of four of
the six qubits. The diagnostic below therefore measures the readout in situ (D1 to D3) before it reads any excess.

## Circuits

Every circuit acts on the six qubits in parallel, ends with the 2 us pre-readout delay and a final `measure` keyed
`f` over all six, except D3.

| circuit | pulses | purpose |
|---|---|---|
| D1 `d1-ro0` | none | the initialized state read after the idle |
| D2 `d2-ro1` | `prx(pi, 0)` | the in-situ P(0\|1) after the idle |
| D3 `d3-ro1-now` | `prx(pi, 0)`, no idle | against D2, separates idle relaxation from readout error |
| D4 `d4-unitary-n16` | 16 x `prx(pi/18, 0)` | instruction for instruction the probe circuit |
| D5 `d5-single` | `prx(8 pi/9, 0)` | one pulse of the full angle |
| D6 `d6-pair-n16` | 32 x `prx(pi/2, phase)` | 16 steps of RX(pi/18) from two pi/2 pulses |
| D7 `d7-n8` | 8 x `prx(pi/9, 0)` | pulse-count ladder |
| D8 `d8-n4` | 4 x `prx(2 pi/9, 0)` | pulse-count ladder |

Every circuit's ideal P(0) is cos(4 pi/9)^2 = 0.0302. In D6, step k plays `prx(pi/2, a_k)` then
`prx(pi/2, a_k + pi + alpha)` with a_k = pi/2 + k alpha and alpha = pi/18: each pair is RZ(g) RX(alpha) RZ(h) with
the Z rotations carried as the phases (a virtual frame), the frames cancel between steps, and the 16-step product is
RZ(zeta) RX(16 alpha) up to a global phase, which the self-test checks to 1e-12 (the final Z rotation leaves P(0)
unchanged). The sign convention of the phase does not matter for P(0).

## Predicted P(0)

The Bloch model of `scripts/iqm_measurement_sequence.py` (prx depolarizing error, T1 and T2 over each 40 ns layer
and the idle, the calibration readout errors, p = 0.068) predicts the raw reading below, in the order D1 to D8:

| qubit | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 |
|---|---|---|---|---|---|---|---|---|
| QB5 | 0.931 | 0.136 | 0.097 | 0.182 | 0.160 | 0.211 | 0.171 | 0.165 |
| QB7 | 0.926 | 0.148 | 0.107 | 0.218 | 0.171 | 0.268 | 0.194 | 0.182 |
| QB11 | 0.924 | 0.129 | 0.092 | 0.172 | 0.153 | 0.196 | 0.162 | 0.157 |
| QB14 | 0.924 | 0.119 | 0.080 | 0.169 | 0.144 | 0.203 | 0.156 | 0.150 |
| QB17 | 0.927 | 0.122 | 0.084 | 0.164 | 0.146 | 0.185 | 0.155 | 0.150 |
| QB19 | 0.902 | 0.130 | 0.102 | 0.177 | 0.154 | 0.208 | 0.165 | 0.159 |

After the in-situ correction by D1 and D2 (the value the correction recovers at q = 1/(1 - 2 p)), D4 to D8 predict:

| qubit | D4 | D5 | D6 | D7 | D8 |
|---|---|---|---|---|---|
| QB5 | 0.060 | 0.032 | 0.096 | 0.045 | 0.038 |
| QB7 | 0.094 | 0.034 | 0.157 | 0.063 | 0.047 |
| QB11 | 0.056 | 0.032 | 0.087 | 0.044 | 0.037 |
| QB14 | 0.063 | 0.031 | 0.105 | 0.047 | 0.039 |
| QB17 | 0.053 | 0.032 | 0.079 | 0.042 | 0.036 |
| QB19 | 0.061 | 0.031 | 0.101 | 0.046 | 0.038 |

D6 predicts above the others because 32 pulses carry the depolarizing error and 32 layers of relaxation.

## Billing

The execution model of the pinching case (compiled schedule + 0.141 s + 7.967 us per circuit-shot) gives a compiled
schedule of 0.051 s (51.3 us per shot over the eight circuits), 0.256 s of execution and a worst-case runtime of
0.846 s, billed as 1 s, or 0.50 credits at 0.50 credits/s. `max_credits` is 1.0 on `garnet` (2 billed seconds) and 0.0
on `garnet:mock`; `collect` cancels at 1.0 s of runtime, so the worst case sits 0.15 s below it and the expected
runtime (about 0.4 s, 0.22 s and 0.28 s for the 100-shot probes) well below.

## Decision rule (preregistered before any submission)

D1 and D2 correct D4 to D8 per qubit, as `ro0` and `ro1` do in the pinching case: the corrected z is (Zobs - o)/s
with o and s from the pair, and the model's corrected value is the response of the chain to a unit initial z plus its
response to the relaxation source times q. A z is (measured - model)/SE, with binomial standard errors propagated by
the delta method through the correction and a systematic of 100 % of the calibrated prx error. Z_DECIDE = 3.

- **L** is the set of qubits whose raw D4 P(0) exceeds its raw model by more than 3 standard errors.
- **No excess:** L is empty. The probe excess does not reproduce, and no cause is chosen.
- **Readout-loss cause:** on every qubit of L, D2's raw P(0) exceeds its model (the calibration e10 plus T1 decay over the
  idle) by more than 3 standard errors, and the corrected D4 lies within 3 standard errors of its model. D3 against D2
  then says whether the loss is in the idle (D2 high, D3 at its model) or in the readout (both high).
- **Phase cause:** on every qubit of L, D2 does not exceed its model by 3 standard errors, the corrected D4 exceeds its
  model by more than 3, the corrected D5 lies within 3, and the pooled corrected excess ranks D4, D7, D8 without a
  significant inversion (D4 - D7 and D7 - D8 not below -3 standard errors).
- **Rebuild criterion:** if the corrected D6 lies within 3 standard errors of its model on all six qubits, the main case
  is rebuilt with pi/2-pair steps, whatever the cause.
- **Neither:** L is not empty and neither pattern holds. The readings are reported without a choice.

The model compared against uses the calibration and the assumed excitation, so a disagreement in D1 and D2 themselves
(the in-situ readout) is reported (`raw` z per circuit) and enters the verdict only through the rules above. Mock
outcomes are random and never enter the analysis.

## Sequence

1. `check` the case, run the self-test, and run the job on `garnet:mock` at 0.00 credits: it settles that the circuits are
   accepted and every key is returned (retained as evidence; `analyze --mock` exercises the pipeline).
2. Submit on `garnet` after approval, then `collect`, then `analyze RUN_DIR --out FILE`.
