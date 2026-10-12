# Folded-QPE hardware results and next experiment decisions

The approved Kingston case completes two jobs and all sixteen PUBs at 8192
shots each. Both jobs report DONE and final charges: dynamic
`db67fqsvf2bc73d0pk4g` consumes 29 seconds; static
`db67frimb58s738bci4g` consumes 11 seconds. Total charge is 40 seconds against
39.632399872 modeled seconds and 120 seconds of enforced combined ceilings.
The [settled account read](settled-account-usage.json) reports 551 seconds
remaining and an empty pending-job list at 2026-10-12T06:07:45Z.

[record.json](record.json) binds the source, calibration, submitted manifests,
QPY digest, approval, and accepted job IDs. [collect.json](collect.json)
contains preregistered contrasts and CPU replay. The two raw directories retain
all 131072 ordered PUB-shots before analysis. The
[supplemental result](supplemental-shot-order.json) verifies the submission
ledger, QPY hash, all sixteen member mappings, and twenty indexed result and
metric files. Its digest map establishes retained-file consistency; service
execution and circuit semantics use the separate runner evidence.

## Measured terminal accuracy

Values are uncorrected percentages of the label-specific expected terminal
bit. Each arm preserves its own full labeled distribution.

| Arm | s0 | s1 | s2 | s3 |
|---|---:|---:|---:|---:|
| archived | 81.348 | 78.528 | 75.073 | 76.184 |
| delay | 83.264 | 78.198 | 75.476 | 77.686 |
| no feed forward | 82.300 | 63.818 | 75.623 | 59.949 |
| coherent | 87.524 | 84.351 | 86.011 | 84.009 |

The twelve preregistered contrast intervals use family alpha 0.05 and
half-width `2*sqrt(log(960)/(2*8192)) = 0.040945053228709165`.
The following table uses percentage points.

| Contrast | Estimate | Simultaneous interval |
|---|---:|---|
| delay minus archived s0 | +1.917 | [-2.178, +6.011] |
| delay minus archived s1 | -0.330 | [-4.424, +3.765] |
| delay minus archived s2 | +0.403 | [-3.692, +4.497] |
| delay minus archived s3 | +1.501 | [-2.593, +5.596] |
| no feed forward minus archived s0 | +0.952 | [-3.142, +5.047] |
| no feed forward minus archived s1 | -14.709 | [-18.804, -10.615] |
| no feed forward minus archived s2 | +0.549 | [-3.545, +4.644] |
| no feed forward minus archived s3 | -16.235 | [-20.330, -12.141] |
| coherent minus archived s0 | +6.177 | [+2.082, +10.271] |
| coherent minus archived s1 | +5.823 | [+1.728, +9.917] |
| coherent minus archived s2 | +10.938 | [+6.843, +15.032] |
| coherent minus archived s3 | +7.825 | [+3.730, +11.919] |

All coherent intervals exclude zero positively. The odd-label no-feed-forward
intervals exclude zero negatively. Delay and even-label no-feed-forward
intervals include zero; inclusion establishes neither equivalence nor a
negligible effect. The precision contracts leave `reject_null` and
`detection_radius` null. The interval interpretation assumes stationary,
independent repetitions within each PUB while allowing arbitrary within-shot
dependence and using union bounds across PUBs.

All sixteen execution entries report known chunk windows and the same
calibration `2026-10-11T22:36:25-07:00`. The dynamic chunk runs from
06:02:55.490780Z to 06:03:23.029452Z; the static chunk runs from
06:03:23.034275Z to 06:03:32.682926Z on 2026-10-12. Those job-wide windows
support the calibration checks; they supply neither individual-PUB shot times
nor evidence that every repetition is independent and stationary.

The supplemental 512-shot blocks retain each PUB's order. Late-minus-early
accuracy ranges from -1.3916 to +2.4902 percentage points. Lag-one correlations
range from -0.01405 to +0.01927. Those exploratory summaries provide neither
significance tests nor a stationarity certificate.

## The model discrepancy changes sign with the intervention

Hardware terminal success falls below CPU replay for archived, delay,
coherent, and even no-feed-forward labels. Odd no-feed-forward hardware
success exceeds replay by 13.4644 and 10.4248 percentage points for s1 and s3.
A uniform subtractive accuracy penalty cannot reproduce that signed pattern.
A model revision must retain labels and interventions, then face an independent
validation set. The supplemental [binary-channel check](TERMINAL_CHANNEL_HYPOTHESIS.md)
excludes one additional common stochastic terminal postprocessing channel as
a complete repair, conditional on its separate sampling and multiplicity
contract. It leaves replacement of modeled readout noise as a distinct
hypothesis. Extra CPU sampling can reduce Monte Carlo error; extra QPU
shots alone cannot repair systematic model error.

The coherent-minus-archived difference measures the complete implementations.
Coherent terminal readout uses qubit 94, whereas dynamic terminal readout uses
qubit 93; routing and the extra control also differ. Delay replaces the first
measurement with a calibrated delay and retains reset. The prepared label
supplies an unconditional `P(-pi/2)` for odd labels instead of measured
feed-forward. The delay arm therefore changes both measurement and the source
of correction information. Odd no-feed-forward labels
already lose 0.5 terminal success in the ideal law. Consequently, these
contrasts isolate neither one controller error mechanism nor a universal
benefit from removing measurement. A crossover with matched terminal sites and
routed schedules tests those hypotheses more directly.

## Billing agrees while component accounting needs refinement

| Component | Dynamic seconds | Static seconds | Total seconds |
|---|---:|---:|---:|
| Final charged usage | 29 | 11 | 40 |
| Service circuit execution metric | 26.793335040 | 8.778279424 | 35.571614464 |
| Charge minus circuit metric | 2.206664960 | 2.221720576 | 4.428385536 |

The sum of `scheduled_circuit_duration_dt * dt_seconds * shots` over the
sixteen PUBs is 2.804154368 seconds. Adding the declared 250-microsecond
repetition delay across 131072 executions gives 35.572154368 seconds, exceeding
the retained service circuit metric by 0.000539904 seconds. The small residual
remains unattributed; the two timing surfaces retain their own values. The
arithmetic is specific to this run.
The metric contains more than circuit gate time, and charge minus that metric
remains an empirical residual rather than an independently identified overhead.

The original model contains 32.768 seconds repetition delay, 1.609039872
seconds Target circuit duration, 0.65536 seconds declared classical latency,
and 4.6 seconds modeled overhead. The executed schedule exceeds the Target
circuit sum by 1.195114496 seconds. The difference between final charge and
model is only +0.367600128 seconds (+0.928%), partly because component errors
compensate. Accurate aggregate billing therefore does not validate the
20-microsecond per-stage latency assumption.

At `dt = 4 ns`, scheduler residuals are 9.516 microseconds for archived,
8.984 for delay and coherent, and 8.988 for no-feed-forward. The archived
residual exceeds delay by 0.532 microseconds and no-feed-forward by 0.528.
Instruction-table attribution must precede treating either difference as a
physical feedback latency. Fresh Target reads remain mandatory for every
future submitted case; these observations cannot become cached calibration.

## Ranked optimization decisions

1. Reuse these raw results across chats and fit labeled model hypotheses
   locally. Remove redundant CPU preparation through early stale-approval
   checks and a prepared-process approval boundary that preserves the final
   live checks. The rejected record retains 132.5 seconds of Aer batch timings;
   its captured initial candidate pass adds a separate 70.7 seconds. Earlier
   approval mismatch checks avoid part of this repeated work and reduce
   approval churn, without changing billed quantum time. The unique retained
   batches total 203.253045914 seconds across the captured checkpoint and
   rejection record; revalidation replaces the initial candidate timings in
   the final record.
2. Choose the next question's precision before buying shots. With the same
   modeled circuits and all controls, 4096 shots give half-width 0.057905 and
   nominal charge 22.116199936 seconds. That sensitivity saves about 44.2%
   relative to the executed plan's model by accepting wider intervals.
   A fresh case must reprice calibration, placement, and all ceilings.
3. Qualify shorter repetition delay against explicit preparation-error and
   temporal-dependence tolerances. Repetition delay supplies 32.768 seconds of
   the current forecast. A hypothetical qualified 100-microsecond setting
   gives 19.971599872 nominal seconds at 8192 shots; the saving remains
   conditional on hardware qualification and includes no pilot cost.
4. Qualify compatible static and dynamic PUBs in one unmitigated job. The
   [local Runtime probe](../../local_compute/mixed_pub_client/README.md)
   establishes ordered CPU execution through one client call. One fewer
   modeled job overhead gives 37.332399872 nominal seconds. Service acceptance,
   internal subjob count, and physical savings remain unmeasured. Production
   support must separate intrinsic PUB kind from job policy across approval,
   manifests, recovery, costs, and collection; relabeling circuits loses that
   distinction.
5. Test matched readout/routing crossovers before attributing the coherent
   advantage. Qualify native mid-circuit measurement and scheduled echoes
   using the IBM manuals linked in the [roadmap](../../../gororoba_quantum/QPU_EXECUTION_ROADMAP.md).
   CPU-exact laws precede every physical variant.

These are scoped engineering hypotheses and sensitivities. The measured
advance is a complete, reproducible mechanism ladder with charge and scheduler
evidence. An unrestricted topology classification remains on the classical
proof path; QPU observations do not establish that theorem.

## Approval and access history

The [first prepared record](../2026-10-12T054229.702537Z/record.json) passes
CPU preparation. Sandbox DNS failure initially appears as Qiskit's
`InvalidAccountError`; a network-enabled read authenticates. Native server
mock validation then fails because the account lacks `mock_kingston`, before
any job ID exists. The owner explicitly approves physical execution using the
local checks and live guards.

The [guarded attempt](../2026-10-12T055017.711575Z/record.json) rejects changed
calibration/layout/QPY and records zero submitted jobs. Its genuine initial
planner checkpoint is captured as the
[refreshed prepared case](../2026-10-12T055017.711575Z-prepared/checkpoint-provenance.json).
The owner approves its exact record digest
`2f87de38661a484bb0e09625b25e363acdc1eed1aba408ef5c2bea1bd6a1092a`.
The successful invocation consumes that approval once and accepts the two
job IDs above. Proposal filenames stay unchanged; separate APPROVAL.md files
record the later authorization.

## Offline replay

From the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error results/live/folded_raw_analysis.py \
  results/live/2026-10-12T055624.091217Z | \
  cmp - results/live/2026-10-12T055624.091217Z/supplemental-shot-order.json
(cd results/live && PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error \
  -m unittest test_folded_raw_analysis)
(cd results/live/2026-10-12T055624.091217Z && sha256sum -c SHA256SUMS)
```

The decoder supports completed schema-7 folded runs with sixteen separate
PUBs, one member per PUB, and one replica per member. Twenty-two synthetic
checks cover widths, label/bit order, malformed payloads, raw/metric hashes,
ledger/QPY identity, member coverage, unsafe paths, block boundaries, odd
halves, and lag-one zero variance. Normal and optimized Python execute the
same validation. The decoder writes its result to stdout and leaves raw
measurement files unchanged.
