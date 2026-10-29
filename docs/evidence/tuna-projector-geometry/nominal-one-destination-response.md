# Tuna nominal-one destination response: retained acquisition

The separately approved [nominal-one case](../../design/tuna-readout-destination-one-admission.md)
completed all three serial jobs. The [canonical analysis](../../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/analysis-canonical.json)
returns **objective established within scope**: all 12 selected response intervals and all 12 baseline
endpoint intervals fit inside the preregistered margin of ±0.10. The retained response sequence supports
that bounded descriptive comparison. Physical attribution remains unresolved, and the report admits
neither an automatic retry nor further hardware.

## Acquisition and queue observations

| Nominal-one control | Provider job / batch | Shots | Reported execution seconds | Creation to `queued_at` |
|---|---|---:|---:|---:|
| Baseline before | 1620359 / 896259 | 4096 | 5.672132 | 8 min 16.451396 s |
| Rotated early destinations | 1620485 / 896287 | 4096 | 5.576922 | 8 min 23.073686 s |
| Baseline after | 1620614 / 896316 | 4096 | 5.534805 | 32 min 16.258985 s |

The [execution state](../../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/execution-state.json)
records completion at 00:20:24.860757 UTC on 28 October 2026. The three acquisitions retain **12,288
ordered width-20 shots**, **16.783859 reported execution seconds**, and empty transaction lists in all
three collected records. Account-wide ledger reconciliation is a separate retention check.

Each case retains its initial admission, under-lock admission, manifest, source, submission, complete raw
shots, histogram and completion receipt. Each successor's provider creation followed the preceding
finish by 46.329855 or 45.412798 seconds, exceeding the required 30-second pause, and followed collection
of the preceding job. The [execution window](../../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/execution-window.json)
ran from 23:29:08.080935 UTC to 01:29:08.080935 UTC. Every dispatched job completed within that window.
The creation-to-`queued_at` intervals describe provider timestamp fields; they do not measure pulse
starts or analog settling.

Global monitoring recorded Tuna as `benchmarking` at
[23:57:46 UTC](destination-one-queue-observations/queue-20261027235746.json)
and [00:08:19 UTC](destination-one-queue-observations/queue-20261028000819.json),
then `executing` at
[00:16:19 UTC](destination-one-queue-observations/queue-20261028001619.json).
The first observation falls on 27 October; the latter two fall on 28 October. Those observations lie
between the rotated job's completion and the final baseline's completion. The status labels identify
provider activity; they do not establish that a recalibration occurred or which settings changed.

## Bounded comparison and repeated-readout anomaly

The [frozen uncertainty contract](destination-one-response-uncertainty.md) defines, for each physical
qubit and early/final binary cell, the response target
`D = P(rotated) − (P(before) + P(after))/2` and endpoint target `R = P(after) − P(before)`.
The quantities `P` are realized averages of conditional response probabilities along the acquired
history. The deterministic weights and conditional Hoeffding bound allow arbitrary adapted shot
dependence. The simultaneous 99% guarantee covers 12 response and 12 endpoint contrasts, with
upward-rounded radii 0.039396318627 and 0.045490950328, respectively.

| Selected-cell summary | Maximum absolute empirical contrast | Maximum absolute interval endpoint |
|---|---:|---:|
| Rotated minus arithmetic baseline average | 0.019287109375 | 0.058683428002 |
| Baseline after minus baseline before | 0.021728515625 | 0.067219465953 |

Every endpoint interval admits the baseline comparison; every response interval admits the ±0.10
tolerance. The guarantee concerns the selected early/final cell marginals of physical qubits 4, 11
and 6, rather than the full joint distribution across the device. Three jobs remain three intervention
units. The endpoint screen cannot bound a transient during the rotated job, establish stationarity,
or convert the response labels into calibrated populations or a causal destination effect.

The following counts use the inverse destination decoder and denominator 4096 per job. Each triple
follows actual order: baseline before / rotated destinations / baseline after. Disagreement means that
the decoded early and terminal binary labels differ in the same retained shot. Direct recomputation
from the raw strings reproduces all nine four-cell tables in the canonical analysis.

| Physical qubit | Early-one counts | Terminal-one counts | Early/terminal disagreement counts |
|---|---|---|---|
| 4 | 3221 / 3311 / 3278 | 3797 / 3829 / 3862 | 952 / 898 / 896 |
| 11 | 1320 / 1404 / 1361 | 3794 / 3763 / 3745 | 2788 / 2687 / 2762 |
| 6 | 3633 / 3663 / 3673 | 3395 / 3326 / 3366 | 892 / 945 / 929 |

Qubit 11's early and terminal labels disagree in roughly two-thirds of shots under each destination
assignment. The source prepares the nominal-one control with `X` on all 17 qubits. Qubit 6's early
measurement and a barrier separate qubit 11's early measurement from terminal register readout; the
source has zero explicit inter-readout delay. A source barrier does not specify the served
measurement duration or acquisition schedule. The anomalous repeated-readout labels persist while the
selected response contrasts meet the coarse destination tolerance. The completed comparison leaves
the [projector qualification refusal](tuna-qualification.md) intact.

The [nominal-zero prefix](ordered-response-acquisition.md) had a maximum empirical qubit-6 cell contrast
of 0.43896484375; the nominal-one case's maximum across all selected cells is 0.019287109375. That
cross-case contrast is **retrospective**. Preparation, acquisition time, queue conditions and apparatus
history differ between the cases. Pooling their observations cannot establish a preparation interaction
or repair the old six-job endpoint, which remains **implementation route unavailable**.

## Serialization and remaining evidence

The executor retained [analysis.json](../../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/analysis.json)
with one-space indentation. The frozen analysis CLI uses sorted keys and two-space indentation;
the [canonical copy](../../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/analysis-canonical.json)
retains that encoding separately. The [serialization receipt](../../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/analysis-serialization-receipt.json)
checks both exact byte contracts and equality of the parsed objects. The encoding difference changes
neither the numerical endpoint nor the acquired evidence. The runtime file retains its original bytes.

The [job-specific upstream request](../../notes/quantum_inspire/destination-response-upstream-request.md)
owns the acquisition-index-to-bit mapping, thresholds, integration windows, served schedules,
calibration history and retained IQ requirements. An upstream replay of stored IQ and acquisition
indices could test reconstruction without another quantum execution. Binary labels alone leave
physical readout effects, timing, reconstruction and apparatus memory unresolved.

Any further hardware requires a newly approved written case. The operational allowance must account
for the measured 32 min 16.258985 s creation-to-queue interval and observed benchmarking context,
alongside execution ceilings, admission reads, collection and account pauses. A measured wait is a
planning input rather than a service-time guarantee. A causal successor also needs qualified job-level
assignment and carryover controls; extra shots within the same three jobs do not supply them.
