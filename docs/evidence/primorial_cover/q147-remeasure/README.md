# q147 two-read control: retained evidence

[PRIMORIAL_Q147_REMEASURE_CASE.md](../../../../results/live/PRIMORIAL_Q147_REMEASURE_CASE.md) is the case, approved
by the owner on 2026-10-27. It follows the shot-history analysis of
[case 3](../case3/README.md): q147's preparation excess on ibm_kingston, read through two measurements in a row.

## Run

| item | value |
| --- | --- |
| binding dry run | `results/live/2026-10-27T204540.839611Z`, record.json sha256 `d72a0deb434ea9513d9611a87aba126d7ca268d58ebc86de8acc27d70e065054` |
| submitted and collected run | `results/live/2026-10-27T204605.871056Z` |
| job | `dbggr6giudkc73e4fijg`, ibm_kingston, backup instance `f59f9992321c` |
| code | commit f38f9c8, `sources_modified` false |
| shots | 32768 per PUB, 20 us repetition delay, twirling and dynamical decoupling off |
| billed | 5 s against 4.6 s estimated and a 12 s ceiling |
| execution | 2026-10-27T20:46:22Z to 20:46:26Z, calibration label 2026-10-27T13:21:35-07:00, unchanged during the shots |
| execution order | `executor.chunk_timing` records one chunk holding PUBs 0, 1, 2 in submitted order |

## Files

- `snapshot.json`: `calibration_snapshot.py --export ibm_kingston --at 2026-10-27T20:46:22.189071+00:00`; 1131
  channels equal to live_run's. q147 reads e01 0.0090, e10 0.0024, T1 350.2 us, measure 2.18 us.
- `remeasure-history.json`: `scripts/remeasure_history.py RUN --e01 0.009033203125 --t1-us 350.21147492944344`,
  the preregistered analysis.

## Results

**The two-read model fails on q147.** The case's readings rest on a second measurement reading back the state the
first one found. On q147 it does not:
- x_remeasure prepares |1> with an X. When its first read is 1, its second read is 1 again in only 0.775 of the
  shots (22882 of 29531). The model predicts 0.985 from e01 and T1 over one measurement. q147's five neighbors read
  between 0.980 and 0.988.
- When remeasure's first read on q147 is 0, its second read is 1 in 0.0465 of the shots (1419 of 30502). The
  calibrated e10 is 0.0024. The neighbors read 0.0003 to 0.0059, except q142 at 0.019, whose e10 is 0.033.

Every q147 measurement therefore moves population in both directions. The 0.985 population prediction printed in
the report is falsified on q147.

**Preregistered readings.**
1. *Persistence.* On q147, remeasure's first read is 1 in 0.0692 of the shots (2266). Its persistence
   pi = P(second read 1 | first read 1) is 0.815, with a 99 percent interval of [0.793, 0.836]. The rule reads
   *population*. The in-job references carry the claim, not the prediction. A known |1> persists at 0.775 and a
   misassigned |0> at 0.047, on opposite sides of 0.5, and pi lies beside the |1> reference. pi exceeds that
   reference by 0.040 +- 0.0085 (4.7 standard errors), a difference that has no explanation yet (below).
2. *The |1> shots read as 0.* x_remeasure's first read calls q147 0 in 0.099 of the shots (3237). The calibrated
   e01 is 0.009, and case 3's stage-2 |1> arms read 0.17 to 0.19. Of those shots, 0.205 (664) read 1 on the second
   measurement, with a 99 percent interval of [0.187, 0.224]. The script labels this "misassignment"; in the case's
   words, most |1> shots read as 0 are not in |1> at the second read. Given the failed model above, this does not
   separate decay before the first read from a transition caused by it.
3. *The readout-event link.* After an x_remeasure first read of 0, remeasure's first read on q147 is 1 in 0.089
   of the shots, against 0.067 after a read of 1 (z -4.68). The one-shot-later null arm is flat (z -0.23), so the
   verdict reads forward_link, with the sign of case 3's stage-2 link (0.095 against 0.051). Conditioning on
   x_remeasure's second read instead, 0.096 against 0.059 (z -12.0), is descriptive and was not preregistered.
4. *The successor.* q147's prep0 at shot s + 1 reads 1 in 0.0825 of the shots after a remeasure first read of 1 at
   shot s, against 0.020 after a 0 (z 18.7). That is the within-job result. Across jobs, prep0 here reads 0.0243
   against 0.0008 in case 3's prep0 control at the same delay. That comparison spans jobs, days, calibrations and
   per-shot measurement counts (five q147 reads per shot here, one there), so it is descriptive.
5. *q142.* The prediction fails. remeasure's first read is 0.0408 against prep0's 0.0393, with overlapping
   intervals, and its persistence is 0.50, undecided. q142's e10 rose from 0.0178 at case 3's stage 2 to 0.0327
   here, so its stage-2 reading of 0.085 is not reproduced at this calibration.

**Reference qubits.** 141, 148 and 149 give 27 to 38 first reads of 1 on remeasure, so their persistence intervals
straddle 0.5 (undecided). Their successor rows rest on those few conditioning shots: prep0 reads 1 at the next shot
in 8 of 28 (q141), 2 of 38 (q148) and 7 of 27 (q149), against base rates near 0.001. The normal approximation
behind the printed z does not hold at those counts, so these rows are counts, not tests. q143 reads persistence
0.586 [0.516, 0.653] (population) and a forward link (z -3.34) with a flat null arm (z -0.38).

## Inference

Low confidence: q147's readout is not quantum-nondemolition at this calibration. Each measurement excites a |0>
in a few percent of shots and depopulates a |1> in about a fifth, and the excitation outlives the 20 us
repetition delay and the implicit initialization. Case 3's shot-history finding fits this reading: the excess
followed the previous circuit's readout event rather than its end state. Raising the confidence would take the
second read's departure from the first changing with the measurement itself while the time between reads stays
fixed. Lowering it would take a reading that tracks the elapsed time instead.

The persistence of remeasure's excited shots (0.815) above a freshly prepared |1> (0.775) has no explanation. One
candidate is a state outside the computational subspace that reads as 1, persists through a measurement and is
not cleared by initialization; the rare but persistent excitations on q141 and q149 would fit it too. Confidence
is low; a third read on the same shot, or a successor read after a longer delay, would show whether those shots
decay on a T1 scale.

A successor that varies the measurement belongs in its own case. `measure_2` is a different physical measurement
with its own assignment error ([ibm_heron_platform.md](../../../notes/ibm_heron_platform.md), measurement
variants) and needs its own control, so it can compare readouts but does not by itself isolate the q147 mechanism.

## Registration

The backup instance's inventory predates this submission, so the retention audit
(`results/live/qpu-job-retention-audit.f59f9992321c.json`) lists the raw archive under `awaiting_observation`.
The run enters `docs/state/research_state.json` in the change that re-observes the backup inventory, with the
case-2 and case-3 runs of issue #585.
