# IQM billing: schedule-duration terms on Garnet and Emerald jobs

`billing_v4.py` reads every retained completed active-reset QPU job through `iqm_records.read_run` (sixteen on Garnet and
two on Emerald; the two retained passive-reset Garnet jobs it scores and leaves out of every fit)
and writes `billing_v4.json`. Gate `core-iqm-billing-v4-replay` reruns it and compares the bytes. It decides nothing:
`BILLING_MODELS` gains a refit in the change that first sizes a case from it.

## Mechanism

- Duration of a circuit: the as-soon-as-possible critical path of its committed instructions. Each instruction starts
  when every qubit it touches is free. The gate durations are `DURATIONS` of `scripts/iqm_signed_probe.py` (cz 40 ns,
  measure 480 ns, Garnet prx 16 ns), the 24 ns prx of Emerald that `scripts/iqm_idle_schedule_probe.py` records from the
  retained static architecture, and each `delay` at its stated seconds. The Garnet fits of v3 price schedules with the
  server's own estimate; this script keeps that estimate as `schedule` and adds the durations on top.
- Target: execution - schedule, where schedule is the server's compile estimate less `JOB_SECONDS`, as in v3.
- Models: `v3` is fixed + per circuit-shot + per mid-circuit record. `v4_sum` adds the shots times the sum of the
  circuit durations. `v4_max` adds the shots times the longest circuit duration (the padding hypothesis of
  `docs/notes/iqm/emerald-idle-schedule-third-length-result.md`). `v4_pad` adds the circuit-shots times the longest
  duration (every circuit padded to the longest). A `_dev` suffix adds an Emerald fixed-term indicator.
- Two fit families: pooled over both devices (with and without the indicator), and Garnet only with the Emerald jobs
  held out and scored by the Garnet coefficients.
- Scores: largest leave-one-out residual over all jobs, the same over the jobs other than the one with the most
  mid-circuit records (`01a175ac-da6c`, anchor of the per-record term, as v3), and the root mean square of the latter.
- Falsifier of the padding hypothesis, fixed before the run: the sum model predicts `01a2058a` within its band while the
  maximum model does not, or the reverse. The band is the largest leave-one-out residual of the other jobs, the anchor
  aside.
- Case prices: `grover_plane_mirrored_features.json` holds the circuit durations and mid-circuit measure counts of the
  PR 987 case (`extract` subcommand, case `grover-plane-mirrored`, branch commit `1e9493ebe25d793085c47c15f357d6c790b41961`, cases.json
  sha256 `c382feb075abadd70531883204a9be99a71d834c276ad6f4b1ad256960f1b4e2`), so the gate replays without that branch. The schedule of the case comes from a Garnet
  schedule model, schedule = 0.000005387 s per circuit-shot + 1.257 s per second of
  shots-times-summed-duration, fitted to the sixteen Garnet jobs. No provider call prices it.

## Readings

- No duration term predicts `01a2058a`. Held out of the Garnet fits, the third-length Emerald job executes 9.505 s
  and is predicted 3.72 to 4.49 s under the four Garnet models, a residual of 5.0 to 5.8 s; its excess over
  the schedule is 6.56 s. In the pooled fits the job's leave-one-out residual is 5.2 to 5.8 s under every model
  and indicator choice. The band is 0.20 to 0.27 s (Garnet fits) or 0.66 to 3.4 s (pooled), so the padding hypothesis
  and the per-shot duration sum both fail the falsifier; the verdict field of the record reads "neither duration term
  predicts the job within the band" for the pooled, the offset and the Garnet-held-out family alike.
- The duration is not what separates the two Emerald jobs. The t1 job (`01a1ffe5-b55a`) has a summed duration of
  200.5 us and a longest circuit of 64.50 us and an excess of 0.866 s; the third-length job has
  406.9 us, 96.50 us and 6.56 s. The duration ratios are 2.0 and 1.5, the excess ratio 7.6. Doubling the Emerald
  prx to the 46.9 ns spacing the result note measures adds at most 0.3 s to the maximum model's term (1.177 s per
  shot-second times 4000 shots times 48 us). A nonlinear mechanism in train length (the third job adds the 250 and
  2000 pulse trains) or a change between the two days stays open; two Emerald jobs cannot separate them.
- On Garnet the duration terms help modestly. The sum term lowers the largest leave-one-out residual without the anchor
  from 0.2524 to 0.1986 s and its root mean square from 0.135 to 0.0902 s; the maximum term gives 0.1969 s and 0.103 s,
  and predicts the Emerald t1 job to -0.008 s where v3 reads 0.243 s. The padded term raises the residual to 0.274 s and
  fails. Over all jobs the anchor decides: the sum term gives 1.953 s, v3 4.043 s, the maximum term 4.168 s.
  Sixteen jobs and four terms leave the difference near the size of the band, so it stays a reading.

| Garnet fit (16 jobs) | largest residual | largest LOO, all | largest LOO, no anchor | rms LOO, no anchor | Emerald t1 held out | 01a2058a predicted (9.505 executed) | its residual |
|---|---|---|---|---|---|---|---|
| v3 | 0.2270 | 4.043 | 0.2524 | 0.135 | 0.243 | 3.716 | 5.79 |
| v4_sum | 0.1691 | 1.953 | 0.1986 | 0.0902 | 0.164 | 3.897 | 5.61 |
| v4_max | 0.1456 | 4.168 | 0.1969 | 0.103 | -0.00846 | 4.102 | 5.40 |
| v4_pad | 0.2064 | 5.609 | 0.2740 | 0.125 | -0.145 | 4.494 | 5.01 |

Coefficients (s): v3: fixed 0.1347, per_circuit_shot 0.000007620, per_mid_record 0.000006462; v4_sum: fixed 0.1913, per_circuit_shot 0.000005891, per_mid_record 0.000006097, per_shot_duration_sum 0.1657; v4_max: fixed 0.1338, per_circuit_shot 0.000006823, per_mid_record 0.000005751, per_shot_duration_max 1.177; v4_pad: fixed 0.1697, per_circuit_shot 0.000006435, per_mid_record 0.000001956, per_padded_shot_max 0.1039.

| Pooled fit (18 jobs) | largest residual | largest LOO, all | largest LOO, no anchor | 01a2058a predicted | its residual | its band |
|---|---|---|---|---|---|---|
| v3 | 5.433 | 10.84 | 5.774 | 3.731 | 5.77 | 0.660 |
| v3_dev | 2.768 | 5.742 | 5.546 | 3.959 | 5.55 | 5.55 |
| v4_max | 2.891 | 5.408 | 5.408 | 4.097 | 5.41 | 2.21 |
| v4_max_dev | 2.497 | 6.077 | 5.411 | 4.094 | 5.41 | 5.41 |
| v4_pad | 1.974 | 15.54 | 5.229 | 4.276 | 5.23 | 2.47 |
| v4_pad_dev | 1.008 | 17.56 | 5.156 | 4.349 | 5.16 | 5.16 |
| v4_sum | 4.294 | 20.88 | 5.582 | 3.923 | 5.58 | 3.40 |
| v4_sum_dev | 2.608 | 5.444 | 5.444 | 4.061 | 5.44 | 5.44 |

A `_dev` band equals the other Emerald job's residual: with two Emerald jobs the indicator is fixed by the one left in,
so the pooled offset fits carry no independent band.

## PR 987 case (52 circuits, 16000 shots, heralding zeros, `garnet`, 0.50 credits per second)

The Garnet fits price the case; the pooled fits, pulled up by the Emerald job, read 14.2 to 22.3 s of worst-case runtime
and stay out of the sizing. The surviving models are `v3` (the reference), `v4_sum` and `v4_max`; `v4_pad` raises
the residual and is dropped. Execution is the modeled schedule (6.33 s) plus the model's excess; the band adds the
model's largest leave-one-out residual without the anchor to the schedule model's relative error times the schedule
(0.440 over all Garnet jobs, set by the packed Pauli job and its barriers, or 0.0207 over the three Grover jobs); the
worst case adds the largest retained runtime over execution, 0.436857 s. The credits buy a cancel threshold
(`iqm_jobs.cancel_threshold_seconds`: billed seconds less one second of `CANCEL_MARGIN`) of 1.5 times the worst case.

| model | execution (s) | band, all-jobs schedule error (s) | worst-case runtime (s) | max_credits, 1.5x | band, Grover schedule error (s) | max_credits, 1.5x |
|---|---|---|---|---|---|---|
| v3 | 12.81 | 3.04 | 16.28 | 13 | 0.383 | 11 |
| v4_sum | 11.67 | 2.98 | 15.09 | 12 | 0.330 | 10 |
| v4_max | 12.21 | 2.98 | 15.63 | 12.5 | 0.328 | 10.5 |
| v4_pad | 12.16 | 3.06 | 15.65 | 12.5 | 0.405 | 10.5 |

The approved ceiling of the case is 13.0 credits (26 s billed, a 25 s cancel threshold). It covers 1.5 times the worst
case of `v4_sum` and `v4_max` with the conservative band, and equals the `v3` requirement.

## What this adopts and why

- For a Garnet case: `v4_sum` and `v4_max` as sizing alongside `v3`, taking the largest of the three credit values
  (13.0 for the PR 987 case, so no change to the approved ceiling). Both lower the leave-one-out residual on the Garnet
  jobs, and the largest costs one fixed credit step at most. `BILLING_MODELS` stays as it is; the change that builds
  the next Garnet case from a refit makes the entry.
- For Emerald: nothing. The 9.505 s of `01a2058a` remain unexplained by any circuit-duration term, and an Emerald case
  prices from `v3`'s coefficients plus a margin for the third-length job's 6.56 s excess over its schedule (84000
  circuit-shots) until a further Emerald job separates the candidates. hypothesis: Emerald execution grows
  faster than linearly in the longest train. Falsifier: an Emerald job at 2000 pulses whose excess falls on the
  line through the t1 job and a 1000 pulse job.

## Residual risk

- Two Emerald QPU jobs leave every Emerald reading at one degree of freedom; the Garnet coefficients carry the rest.
- The schedule model of the case is an extrapolation to deeper circuits than the retained Grover jobs (the longest circuit of
  the case lasts 3.50 us against 2.75 us for the longest retained Grover job); a garnet:mock compile estimate of the committed case would replace it.
- The anchor job alone fixes the per-record term, as in v3.

```sh
"$PYTHON" -B -W error docs/evidence/iqm-billing-v4/billing_v4.py OUT.json
"$PYTHON" -B -W error docs/evidence/iqm-billing-v4/billing_v4.py extract CASE_DIR GIT_COMMIT FEATURES.json
```
