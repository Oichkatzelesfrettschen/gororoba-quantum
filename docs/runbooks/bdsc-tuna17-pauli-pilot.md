# BDSC Tuna-17 Pauli pilot

This runbook orders the series that
[bdsc-tuna17-pauli-pilot.md](../design/bdsc-tuna17-pauli-pilot.md) designs and
`scripts/qi_bdsc_pauli_cases.py` builds: twelve witness circuits and six
readout references in six batches of three circuits on Tuna-17, each witness
carrying three disjoint patches. No step that reaches a provider is authorized
until its written case is approved ([AGENTS.md](../../AGENTS.md#hardware-services)).

## Build and check

1. `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --select-placement` prints the
   ranking of the 156 disjoint placements and exits 0 when `PLACEMENT` is the
   first. A change to the exclusions of `scripts/qi_zero_divisor_cases.py`
   re-ranks it.
2. `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --write results/quantum_inspire/cases`
   writes `bdsc_pauli_tuna_17/` after checking every preparation circuit and
   every emitted witness against its target state with a Qiskit Statevector;
   `--check` regenerates it byte for byte (gate `core-626`) and `--self-test`
   runs the ideal, depolarized, readout-biased and coherent synthetic series
   through the analysis (gate `core-627`).

## Dry run

1. Run the identical cQASM on qxelarator, which needs no account or queue:
   `"$QI_PYTHON" -I scripts/qx_local_series.py results/quantum_inspire/cases/bdsc_pauli_tuna_17 OUT 4096`
   with `QI_PYTHON=$HOME/.local/share/quantuminspire/venv/bin/python`
   ([qx-runs.md](../notes/quantum_inspire/qx-runs.md)). It writes
   `OUT/batch-NN/` with `raw/<file>.json` for every circuit.
2. `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --analyze OUT/batch-0* --out OUT/analysis.json`.
   Every cell must read its ideal score (0, 1/2 or 1) within its
   empirical-Bernstein interval, the readout references must read 0 and 1
   exactly, and no contraction statistic may flag.
3. A remote QX twin is a job and joins the written case.

## Submission order

1. Write the case: what the pilot measures, why noise simulation cannot answer
   it (the device's own preparation and readout define the physical effect),
   the backend, 32768 shots, 18 jobs of about 20 s each, expected seconds and
   credits. Wait for the owner's approval and quote it verbatim.
2. Take the placement, readout rates and calibration from a fresh read; the
   series stops and the placement is redrawn when a patch qubit reads
   P(1|0) or P(0|1) above 0.15 in batch-00's references.
3. For each batch in order: copy the batch directory to
   `results/quantum_inspire/runs/<UTC stamp>-bdsc_pauli_tuna_17-batch-NN/`,
   then `qi_platform.py submit RUN_DIR --backend-type-id 7 --approval "QUOTE"`
   and `qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`. The platform
   enforces the 120 s account pause and the three-circuit batch limit; stop at
   the first failed job or short shot list, and never resubmit a directory that
   holds `submission.json` or `submission-state.json`.
4. After the last batch, `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --analyze RUN_DIR... --out FILE`
   over all six run directories. Patches are read separately, and the pooled
   value names its equal-weight estimand. The readout-corrected scores sit
   beside the raw ones; correction covers an assignment bias that the
   contraction law cannot see (a parity residual stays near zero under
   P(1|0) 0.03 and P(0|1) 0.08).
5. Retain the run directories, the analysis and a replay gate in the change
   that retains them, and register the runs in `docs/state/research_state.json`
   ([AGENTS.md](../../AGENTS.md#records)). The result qualifies no device and
   no Belenos measurement.
