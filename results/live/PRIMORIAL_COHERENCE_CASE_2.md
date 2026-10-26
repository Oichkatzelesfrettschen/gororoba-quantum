# Case: primorial coherence case on 23 ibm_kingston paths at a short repetition delay

Status: written case awaiting the user's approval. Nothing in this file authorizes a submission.

This case repeats [PRIMORIAL_COHERENCE_CASE.md](PRIMORIAL_COHERENCE_CASE.md) on 23 three-qubit paths at once and at
a repetition delay below the 250 us default. It keeps that case's probe and gap-88 circuits, its estimators, its
stage-2 decision criterion and its calibration-identity gate. The first case's stage 1 ran one path and voided on
physical qubit 0, which read |0> as 1 in 79 percent of its in-job readout calibration while the backend reported
0.6 percent (`results/live/PRIMORIAL_COHERENCE_FINDINGS.md` on branch `primorial/coherence-run`, which lands after
pull request #516). Two reviews shaped this design:
[primorial-coherence-case-2-review.md](../../docs/archive/reviews/primorial-coherence-case-2-review.md) and
[primorial-coherence-case-2-codex-review.md](../../docs/archive/reviews/primorial-coherence-case-2-codex-review.md).

## What it measures and why simulation cannot answer it

The question is the first case's: whether a coherent error on a real Heron r2 path survives the gap-88 null
subtraction that cancels each single error family to first order. The answer rests on each path's drive-axis
tilt, CZ conditional phase, static detuning and ZZ rates. The backend's calibration reports none of them, and the
joint-bound analysis showed they can reach max_z 2.6 to 2.8 together at gate-error bounds. Simulation holds only
those bounds; the probes measure the values.

## The paths

IBM bills shots times (repetition delay plus circuit) per job, independent of how many qubits a PUB measures
([qpu_run_economy.md](../../docs/notes/qpu_run_economy.md), rule 11). Every member therefore runs on 23 paths at
once, one replica per path in each PUB. The paths come from the 226-path joint-bound ranking at the calibration of
2026-10-26T00:48:55-07:00, taken greedily in ranking order. Each avoids qubit 0, reads at a reported
1 - e10 - e01 of at least 0.9 on every qubit, admits the gap-88 fit, and keeps one CZ hop from every other path,
so no coupler joins qubits of two paths
(`primorial_probe_case.py --rank-paths`, retained in
[docs/evidence/primorial_cover/case2/](../../docs/evidence/primorial_cover/case2/README.md)). Middle qubit second:

58-71-72, 33-39-53, 3-16-23, 17-27-28, 141-142-143, 15-19-35, 60-61-62, 151-152-153, 82-83-96, 38-49-50,
105-106-107, 118-129-128, 100-101-102, 55-59-75, 78-89-90, 66-67-68, 42-43-44, 10-11-12, 79-93-92, 132-133-134,
124-125-126, 98-111-110, 147-148-149.

Their worst joint max_z at their own gate-error bounds spans 1.36 to 2.57, so the set does not favor the paths
where a bounded coherent error is least visible. The pin is `--pin-layout ibm_kingston:58,71,72/33,39,53/...` in
this order. live_run maps each member onto every path with that path's own calibration score. It refuses a path
that is inadmissible or within one CZ hop of another, and it adds the isolated reference PUB: the group's first
member on the first path alone.

## Repetition delay and its control

The delay is the approver's choice among three options:

| delay | preparation control | expected total | cap |
| --- | --- | ---: | ---: |
| 20 us, falling back to 50 us (recommended) | prep0 and x_history at 20 us; at 50 us after a fallback | 19.7 to 25.1 s; 35.3 to 45.7 s after a fallback | 84 s |
| 20 us | prep0 and x_history at 20 us, unmeasured on this account before | 19.7 to 25.1 s | 68 s |
| 50 us | prep0 and x_history at 50 us | 28.7 to 39.1 s | 68 s |
| 250 us default | none: the calibration's reported readout carries the default-delay excitation (rule 5) | 69.5 to 113.5 s | 180 s |

Under the fallback option, a 20 us control that fails the timing canary below, or whose excitation stops a path
the 50 us rule would keep, moves the case to 50 us with its own two controls. That costs the spent 20 us
controls (at most their two 8 s ceilings) and needs no second approval.

A delay below the default carries a preparation control on the run's own qubits (rule 1). It is the repository's
`state-prep-control` family: two jobs at the chosen delay over all 69 path qubits, each one PUB, 32768 shots.
- prep0 (initialize, measure) reads each qubit's excited fraction after a near-|0> history.
- x_history (initialize, measure, x) reads it after an all-|1> history.

Each arm runs in a job of its own, so the shot history each arm reads holds by construction; IBM guarantees no PUB
order within a job.

`scripts/state_prep_excess.py` turns the two controls into a per-qubit excitation bound eps. It applies the
single-delay rule to a pinned-campaign plan at any delay. That rule takes one-sided Clopper-Pearson bounds,
simultaneous over every controlled qubit at family-wise alpha 0.01, and corrects for the x_history end state.
Every decision then simulates each path with an X error of probability eps, the path's largest eps, on every qubit
before the circuit (`dynamic_density.with_prep_excitation`). That is the channel the n21 planner uses, applied in
the noisy law beside the reported readout error. The probes need no such term: at the decision thresholds on
58-71-72, an excitation of 0.015 on every qubit moves no probe estimate by more than 0.016 of its standard error at
800 shots, because the in-job inversion absorbs it as a readout flip
(`--excitation-check`, [probe-excitation.json](../../docs/evidence/primorial_cover/case2/probe-excitation.json)).

## Stages

- **Stage 0, controls.** prep0 and x_history at the chosen delay, submitted back to back without waiting for
  either to finish. `primorial_probe_case.py --retained-paths`
  drops every path with a qubit whose prep0 excited fraction exceeds 0.2, a readout of |0> as 1 that alone puts
  1 - e10 - e01 below 0.8. It would have dropped the first case's qubit 0 at 0.79. The two controls form a timing
  canary. A control job that ends in error 1305, the failure of the 0 us attempt, or bills above its 8 s ceiling
  stops the case before stage 1.
- **Stage 1, probes** (`coherence_probes`, 800 shots per circuit) on the retained paths. `state_prep_excess.py`
  bounds eps on the stage-1 approval dry run, the plan whose placement it reads.
  `primorial_probe_case.py --decide-paths` then applies the stage-2 rule:
  - it requires the snapshot to carry the calibration every probe member executed under, with no change during
    the shots; the snapshot is exported after collection at stage 1's recorded execution start
    (`calibration_snapshot.py --export ibm_kingston --at START`, the `properties(datetime=)` and
    `target_history(datetime=)` pair live_run's collection reads), so it is what ran by construction;
  - it requires the excess output to name the run's approved record and delay;
  - it voids a path whose in-job readout calibration falls below 0.8 on any wire;
  - it decides every other path at 3200 gap-88 shots from that path's own per-replica summary, with its eps;
  - it sets N2 to the smallest multiple of 100 between 1600 and 3200 that covers the largest 95th-percentile
    identification need among the paths that proceed, and decides those paths again at N2.
- **Stage 2, gap-88** (`primorial_gap88`, N2 shots per circuit) on the paths that proceed.
  - **Prediction.** Each path predicts every null-subtracted coefficient's shift: the mean coherent shift over the
    128 joint draws of its probe estimates plus the signed incoherent shift of its noisy budget, which already
    holds eps.
  - **Band.** The band is that prediction plus or minus z times the quadrature sum of the coefficient's stage-2
    standard deviation and the draws' spread, with z = z(1 - 0.025/(7k)) for k paths in stage 2, and at least 3.
    The bands hold simultaneously over all 7k coefficients at family-wise level 0.05 under a Gaussian
    approximation of both spreads.
  - **Falsification.** `--falsify` compares each path's collected `bias_<coefficient>` (recovered minus exact on
    the in-job assignment-corrected readings, the quantity the bands predict) with its band. A coefficient
    outside its band falsifies the coherent-error model on that path, and the device-question claim names every
    such path and coefficient. The claim stands only when every stage-2 member executed under the decision's
    calibration with no change and the crosstalk check reads consistent; otherwise the result is descriptive.
  - **Assumptions.** The coherent and incoherent shifts add to first order; the probe case's noise-model check
    measured a null-subtracted bias of 0.051 under the snapshot's noise against 0.049 noise-free, the difference
    the incoherent floor (`docs/evidence/primorial_cover/probe_case.json`). Path selection uses only probe shots,
    which are independent of the stage-2 shots, so it leaves the bands' level intact.

## Crosstalk

Paths one CZ hop apart share no coupler, so no static ZZ acts directly between qubits of two paths. Drive crosstalk
and next-nearest ZZ through a shared neighbor remain. The gap-88 and null members are one parametrized circuit:
every path's physical pulse stream (sx, x, CZ and their timing) is identical in both, and only the virtual-Z frames
differ. Drive crosstalk is therefore common to the signal and null arms, and only the state-dependent next-nearest
ZZ can differ between them.

`--crosstalk RUN --group primorial_gap88` tests the first path's gap-88 counts in the packed PUB against the
isolated reference with a chi-square homogeneity test at 0.01. Before the test it merges every outcome whose
expected count falls below 5 into one rest column, since the gap-88 law sits on two outcomes. It covers the
gap-88 member only, so it bounds half of the null-subtracted crosstalk term. If it detects crosstalk or returns
indeterminate, the stage-2 result is reported as descriptive and makes no device-question claim. The same check on
stage 1 is reported and binds nothing.

## Stops and path drops

The approved envelope covers any subset of the 23 paths that these rules leave, in the listed order:
- a path a binding dry run refuses, because live_run's quality policy excludes one of its qubits at that
  calibration;
- a path the prep0 control drops;
- a path stage 1 voids or that does not proceed.

The case stops and returns to the user in any of these cases:
- fewer than 12 paths remain at any stage;
- a control fails the timing canary;
- `state_prep_excess.py` refuses its inputs;
- its `calibration_scope.matched` is false, meaning the controls and the stage-1 plan read different calibrations;
- `--decide-paths` refuses its bindings;
- the calibration-identity gate between the stage-1 and stage-2 dry runs fails.

A 23-path decision takes 85 s on the build host, so `--decide-paths` adds about 3 minutes between stage 1's
collection and the stage-2 dry run. The Kingston queue held 79 pending jobs at 2026-10-26T17:53Z, and a long queue
wait before stage 2 exposes the identity gate to a recalibration. Stage 1's seconds then stay spent, its estimates
stand as descriptive results, and the case returns to the user. The controls carry the same exposure:
`calibration_scope.matched` fails when Kingston recalibrates between the controls and the stage-1 approval dry
run.

## Expected seconds

Stage 1 of the first case billed 23 s for 78,400 executions at 250 us. That is 264 us per execution against a
mean probe circuit of 5.1 us, which leaves about 9 us of fixed time per execution (2 to 15 us within the bill's
whole-second rounding). The dry runs give one PUB per control, 99 probe PUBs at a mean 5.0 us and 105 gap-88 PUBs
at 3.0 us, each count including the isolated reference.

| delay | each control (32768 shots) | stage 1 (79,200 executions) | stage 2 at N2 = 1600 | stage 2 at N2 = 3200 | total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20 us | 3.3 s | 5.0 s | 7.7 s | 13.1 s | 19.7 to 25.1 s |
| 50 us | 4.3 s | 7.4 s | 12.7 s | 23.1 s | 28.7 to 39.1 s |
| 250 us | none | 23.2 s | 46.3 s | 90.3 s | 69.5 to 113.5 s |

The ceilings (`--max-execution-seconds` and `--max-total-execution-seconds`) hold the 15 us fixed-time edge at
20 and 50 us:
- each control 8 s;
- stage 1 15 s;
- stage 2 30 s.

That totals 68 s. At 250 us: stage 1 40 s and stage 2 140 s. The backup instance held 412 s after the first case's
stage 1.

The raw archive grows with the width: stage 2 at 3200 shots holds about 105 x 3200 shot strings of 69 bits, near
25 MB of JSON, and stage 1 about 6 MB.

## Representative dry runs

The design's dry runs at 20 us, made from this change's tree at the calibration of 2026-10-26T11:06:06-07:00, are
retained in `results/live/`:

| record | campaign | PUBs | shots | calibration | record.json sha256 |
| --- | --- | ---: | ---: | --- | --- |
| `2026-10-26T182259.060781Z` | state-prep-control prep0 | 1 | 32768 | 2026-10-26T11:06:06-07:00 | `88ea106aca9b9964ff42322c06c17216a2ade1f0c9dfc2d1046016e005c1067d` |
| `2026-10-26T182322.084422Z` | state-prep-control x_history | 1 | 32768 | 2026-10-26T11:06:06-07:00 | `e21f7fc3805d293ff1c621eb42b9e1774a5a6eb5507de1b5dc663bb74fb04b16` |
| `2026-10-26T182345.638824Z` | coherence_probes, 23 paths | 99 | 800 | 2026-10-26T11:06:06-07:00 | `f827887b6abd4bcb01b26936b4daf9d3780ee21c843e42b0ffd946c477617a12` |
| `2026-10-26T182501.844592Z` | primorial_gap88, 23 paths | 105 | 3200 | 2026-10-26T11:06:06-07:00 | `bffff85d88b17061b60b068aeb4621c03e38620d56c388b7ab1ffe64638fdd9f` |

live_run's cost model, which omits the fixed per-execution time, predicts 3.03 s for each control.

The binding dry runs are re-made from main after this change merges, at each stage's path subset, delay and
calibration. Each stage's submission carries its own as the approved record. They must match these representatives
in campaign, member structure, policy and shots.

## Commands

From `gororoba_quantum/`, with `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`,
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `D` the delay in seconds, `PATHS` the `/`-joined surviving
paths, `K` their count and `QUBITS` their qubits. Each submission is the dry-run command plus `--submit
--approved-record RECORD_DIR --approved-record-sha256 RECORD_SHA256`, after a usage read; `--max-pending` is set
to the queue observed at submission.

```sh
for arm in prep0 x_history; do
  "$PYTHON" live_run.py --family state-prep-control --layout QUBITS --state-prep-arms $arm --max-replicas 1 \
    --backends ibm_kingston --shots 32768 --rep-delay D --max-execution-seconds 8 \
    --max-total-execution-seconds 8 --out ../results/live
done
"$PYTHON" ../scripts/primorial_probe_case.py --retained-paths PREP0_RUN --paths PATHS --out RETAINED
"$PYTHON" live_run.py --groups coherence_probes --pin-layout ibm_kingston:PATHS --max-replicas K \
  --backends ibm_kingston --shots 800 --rep-delay D --max-execution-seconds 15 \
  --max-total-execution-seconds 15 --out ../results/live
"$PYTHON" ../scripts/state_prep_excess.py --n21-record STAGE1_APPROVAL_RECORD --control PREP0_RUN \
  --control X_HISTORY_RUN
"$PYTHON" calibration_snapshot.py --export ibm_kingston --at STAGE1_EXECUTION_START --out SNAPSHOT
"$PYTHON" ../scripts/primorial_probe_case.py --decide-paths STAGE1_RUN --excess EXCESS --snapshot SNAPSHOT \
  --out DECISION
"$PYTHON" live_run.py --groups primorial_gap88 --pin-layout ibm_kingston:PATHS --max-replicas K \
  --backends ibm_kingston --shots N2 --rep-delay D --max-execution-seconds 30 \
  --max-total-execution-seconds 30 --out ../results/live
"$PYTHON" ../scripts/primorial_probe_case.py --crosstalk STAGE2_RUN --group primorial_gap88 --out CROSSTALK
"$PYTHON" ../scripts/primorial_probe_case.py --falsify STAGE2_RUN --decision DECISION \
  --crosstalk-verdict CROSSTALK --out FALSIFICATION
```

STAGE1_EXECUTION_START is the `start` that stage 1's collect.json records for its first probe member. At the 250 us
default the controls, `--retained-paths` and `state_prep_excess.py` are skipped, and every live_run command omits
`--rep-delay` and `--decide-paths` omits `--excess`: the run then records no repetition delay, and `--decide-paths`
decides with zero excitation, the reported readout carrying the default-delay excitation.

`state_prep_excess.py` takes the plan through its `--n21-record` flag, which reads a pinned-campaign plan as well.
`--fetch-readout` on each control precedes it, as for the n21 controls.

## Envelope

This case approves the following envelope:
- the state-prep controls and the two campaigns on any rule-made subset of the 23 listed paths, with their member
  structure;
- the policy: twirl off, dd none, the structure-preserving contract, and the delay the approver chooses, with the
  20-to-50 us fallback when that option is chosen;
- the shots: 32768 per control, 800 in stage 1, and the decision's N2 between 1600 and 3200 in stage 2;
- the ceilings above, with an expected bill within the chosen delay's row.

A fresh approval is needed for any of: a path outside the list, other circuits, another delay, a calibration
change between stages 1 and 2, or an estimated charge above those. A preregistration binds the decision sources'
digests at this case's merge commit, written beside the stage-1 approval dry run before stage 0 is submitted.
