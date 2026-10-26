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
