# Second primorial coherence case: path selection and excitation inputs

These files carry the offline inputs of
[PRIMORIAL_COHERENCE_CASE_2.md](../../../../results/live/PRIMORIAL_COHERENCE_CASE_2.md):

- `kingston-snapshot.json`: the ibm_kingston calibration snapshot of 2026-10-26T00:48:55-07:00
  (`gororoba_quantum/calibration_snapshot.py --export ibm_kingston`).
- `path-ranking.json`: every three-qubit path ranked by its worst joint tilt and CZ-phase max_z at its own
  gate-error bounds, and the 23 separated paths the case pins:
  `"$PYTHON" scripts/primorial_probe_case.py --rank-paths kingston-snapshot.json --exclude 0 --out path-ranking.json`.
- `probe-excitation.json`: on path 58-71-72 at the decision thresholds, an initial X error of probability 0.015
  on every qubit moves no probe estimate by more than 0.016 of its standard error at 800 shots, so the probes'
  in-job readout inversion, which treats that excitation as a readout flip, leaves no material bias:
  `"$PYTHON" scripts/primorial_probe_case.py --excitation-check 0.015 --snapshot kingston-snapshot.json
  --layout 58,71,72 --probe-shots 800 --out probe-excitation.json`.

## Run results

The case ran on ibm_kingston through the backup account at a 20 us repetition delay and spent 22 s: two
controls at 3 s each, stage 1 at 5 s and stage 2 at 11 s.

- `retained-paths.json`: the prep0 control drops 82-83-96 (q96 reads 0.281 after a |0> history and 0.286 after
  a |1> history) and retains 22 paths
  (`scripts/primorial_probe_case.py --retained-paths results/live/2026-10-26T190449.023973Z`).
- `stage1-snapshot.json`: the calibration at stage 1's execution start, 2026-10-26T22:05:50Z
  (`calibration_snapshot.py --export ibm_kingston --at`); it reads 14:25:32 PDT.
- `stage1-decision.json`: `--decide-paths` on stage 1 with each path's state-prep eps
  (`results/live/2026-10-26T215024.737181Z/state-prep-excess.json`); 21 of 22 paths proceed at 2700 shots,
  and 147-148-149 needs 3500 against the 3200 cap.
- `stage2-snapshot.json`: the calibration at stage 2's execution start, 2026-10-26T22:20:39Z. It carries the
  label 15:03:42 PDT, which the submit-time read did not yet see, and all 5010 channel values equal
  `stage1-snapshot.json`'s: Kingston republished the label without a value change.
- `stage2-crosstalk.json`: the packed-against-isolated test of the first gap-88 arm on 58-71-72 reads
  consistent (chi-square 9.35, 7 degrees of freedom); it tests that one arm and path only.
- `stage2-falsification.json`: the claim is descriptive under the calibration label mismatch. 58-71-72 (01,
  02), 15-19-35 (01, 02) and 100-101-102 (01) fall below their bands; these are two of the three largest-eps
  paths and the fourth (132-133-134, the third largest, stays inside).
- `excitation-ablation.json`, from `excitation_ablation.py` run at the repository root: a descriptive
  ablation of the excitation term on those four paths, chosen after reading the stage-2 data. Applying each
  path's maximum eps to all three of its qubits produces the misses on 15-19-35 and 100-101-102; replacing the
  Clopper-Pearson upper bound with the point estimate moves little; 58-71-72 enters its bands only when the
  history-independent excess (prep0 minus calibration e10) enters as terminal readout error and only the
  history-dependent excess (x_history minus prep0) as an initial X error. Terminal readout excess alone
  reproduces the zero-excitation law, because the in-job inversion absorbs it.
- [The Codex review of these results](../../../archive/reviews/primorial-coherence-case-2-results-codex-review.md)
  finds the band construction, not the coherent-error model, falsified, and q147's history difference
  (21 against 1584 excited of 32768) real but confounded with job identity.
