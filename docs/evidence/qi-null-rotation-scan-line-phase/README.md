# Exploratory reanalysis of the Tuna-17 null rotation scan

Scripts and outputs behind
[tuna17-null-rotation-scan-line-phase.md](../../notes/quantum_inspire/tuna17-null-rotation-scan-line-phase.md).
Every script reads the retained runs
`results/quantum_inspire/runs/2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-*` and the retained
analysis, changes neither, and writes its JSON beside itself. Evidence class: exploratory; candidates and
falsifiers stand in each docstring or opening `print` and were fixed before the fit. No random draw is used.

Run from the repository root under the pinned interpreter:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 OPENBLAS_NUM_THREADS=2
systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 \
	"$PYTHON" -B docs/evidence/qi-null-rotation-scan-line-phase/SCRIPT.py
```

The forward-model scripts read the gate-noise tables of `scripts/qi_pathion_null_rotation_scan_cases.py`, which
that module builds on first use (about thirty minutes) and caches.

| Script | Output | Content |
|---|---|---|
| `exact_pulse_residuals.py` | `exact_pulse_residuals.json` | measured contrast less the exact-pulse law per arm and gate-noise family |
| `time_bins.py` | `time_bins.json` | contrast of each data job in 8 consecutive shot bins; heterogeneity of the centers |
| `bracket_drift.py` | `bracket_drift.json` | readout rates per bracket against elapsed time; read-value dependence between qubits |
| `widened_worlds.py` | `widened_worlds.json` | one shared parameter per elementary error, forward fit and mirror score |
| `widened_worlds_round2.py` | `widened_worlds_round2.json` | phases tied to CZ gates; one parameter per batch |
| `widened_worlds_round3.py` | `widened_worlds_round3.json` | two-parameter composites of the two leading worlds |
| `full_histogram_fit.py` | `full_histogram_fit.json` | Pearson chi-square of all 96 outcome counts per batch (contraction model) |
| `line_scan.py` | `line_scan.json` | the shot-order line scan of `scripts/qi_shot_record_line.py` on all 62 jobs |
| `line_phase_bins.py` | `line_phase_bins.json` | selector contrast in 8 bins of the line's phase per job |
| `line_phase_split.py` | `line_phase_split.json` | the same fold with the phase from odd shots and the contrast from even shots |
| `phase_resolved_fit.py` | `phase_resolved_fit.json` | one parameter that follows the line, fitted to the phase-bin contrasts |
| `phase_resolved_two_source.py` | `phase_resolved_two_source.json` | two parameters driven by one line phase |
| `followup_predictions.py` | `followup_predictions.json` | model contrasts of the draft follow-up arms under three worlds |

`line_scan.py` imports `worker1` from `docs/evidence/hardware-residuals/tuna-quandela`. The round-2, round-3 and
later forward-model scripts repeat the state-vector routine of `widened_worlds.py` with their own candidate lists.
