# Exploratory reanalysis of the Tuna-17 null rotation scan

Scripts and outputs behind
[tuna17-null-rotation-scan-line-phase.md](../../notes/quantum_inspire/tuna17-null-rotation-scan-line-phase.md).
Every script reads the retained runs
`results/quantum_inspire/runs/2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-*` and the retained
analysis, changes neither, and writes its JSON beside itself. Evidence class: exploratory; candidates and
falsifiers stand in each docstring or opening `print` and were fixed before the fit. No random draw is used.

Run from the repository root under the pinned interpreter:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=6
systemd-run --user --scope -q -p MemoryMax=14G -p MemorySwapMax=0 \
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
| `line_phase_bins.py` | `line_phase_bins.json`, `line_phase_bins_pooled.json` | selector contrast in 8 bins of the line's phase per job; pooled harmonics per arm |
| `line_phase_split.py` | `line_phase_split.json` | the same fold with the phase from odd shots and the contrast from even shots; error over jobs and exact sign-flip null |
| `line_phase_conditionals.py` | `line_phase_conditionals.json` | first harmonic of the conditional and marginal probabilities and of the contrast by q4's read value |
| `line_parity_amplitude.py` | `line_parity_amplitude.json` | line-band amplitude of the selector-coin parity bit and of q4's bit per job, with an off-line band; no phase reference |
| `phase_resolved_fit.py` | `phase_resolved_fit.json` | one parameter that follows the line, fitted to the phase-bin contrasts |
| `phase_resolved_two_source.py` | `phase_resolved_two_source.json` | two parameters driven by one line phase |
| `d2_split_worlds.py` | `d2_split_worlds.json` | the retained d2 splits of the 24 scan arms against three worlds at fixed parameters |
| `followup_predictions.py` | `followup_predictions.json` | model contrasts of the draft follow-up arms under three worlds |

Each script is a driver: it lists its independent items (candidates, pairs, jobs or batches), maps a worker over
them through `parallel.ordered_map` of `gororoba_quantum/parallel.py`, and orders, prints and writes in the parent
process. `GOROROBA_WORKERS` caps the worker count.

- `gororoba_quantum/elementary_error_laws.py` holds the state-vector model with explicit inputs (operations,
  register, outcome order, pulse angles, error items); `tests/gororoba_quantum/test_elementary_error_laws.py` fixes
  its conventions on hand-derived circuits.
- `scan_forward.py` binds it to the retained b0 circuit and the scan's arms; the result equals `forward_laws` of
  the scan module where both apply.
- `scan_fits.py` selects the retained records and holds the per-candidate workers of the forward-model fits.
- `line_fold.py` holds the per-job workers of the line analyses and the bracket reader.
- `line_scan.py` maps `scan_file` of `docs/evidence/hardware-residuals/tuna-quandela/worker1.py`.
