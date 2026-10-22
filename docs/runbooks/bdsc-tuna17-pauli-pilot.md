# BDSC Tuna-17 Pauli pilot

This runbook orders the series that
[bdsc-tuna17-pauli-pilot.md](../design/bdsc-tuna17-pauli-pilot.md) designs and
`scripts/qi_bdsc_pauli_cases.py` builds: twelve witness circuits, three
quadrature circuits and nine readout references in eight batches of three
circuits on Tuna-17 (24 jobs), each witness carrying three disjoint patches,
and a QX twin that packs two patches per circuit onto the emulator's 10 qubits.
No step that reaches a provider is authorized until its written case is
approved ([AGENTS.md](../../AGENTS.md#hardware-services)).

## Build and check

1. `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --select-placement` prints the
   ranking of the 156 disjoint placements and exits 0 when `PLACEMENT` is the
   first. A change to the exclusions of `scripts/qi_zero_divisor_cases.py`
   re-ranks it.
2. `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --write results/quantum_inspire/cases`
   writes `bdsc_pauli_tuna_17/` and `bdsc_pauli_qx/` after checking every
   preparation circuit and every emitted circuit against its target with a
   Qiskit Statevector, the native pulses against the cQASM spec, the balance
   tables and the reference sets; `--check` regenerates both byte for byte
   (gate `core-626`) and `--self-test` runs the ideal, depolarized,
   readout-biased, coherent, branch-phase, drift, breach, context and twin
   series through the analysis (gate `core-627`).
3. `"$QI_PYTHON" scripts/qi_toolchain_check.py` rewrites
   `docs/evidence/quantum_inspire/toolchain_check.json` for the new circuits;
   `"$PYTHON" scripts/qi_toolchain_check.py --check` compares it.

## Dry run

1. Run the identical cQASM on qxelarator, which needs no account or queue,
   once per series: `"$QI_PYTHON" -I scripts/qx_local_series.py results/quantum_inspire/cases/bdsc_pauli_tuna_17 OUT/tuna 4096`
   and the same for `bdsc_pauli_qx` into `OUT/qx`, with
   `QI_PYTHON=$HOME/.local/share/quantuminspire/venv/bin/python`
   ([qx-runs.md](../notes/quantum_inspire/qx-runs.md)). Each writes
   `OUT/.../batch-NN/` with a cases.json that records the shots run, the
   simulator version and `control: local_qxelarator`, and `raw/<file>.json`
   for every circuit.
2. `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --analyze OUT/tuna/batch-* --out OUT/tuna-analysis.json`
   (and `OUT/qx`). The claim kind reads "emulator control". Every witness
   cell reads its ideal score (0, 1/2 or 1) within its empirical-Bernstein
   interval, the quadrature phase reads 0 within three standard errors, the
   readout references read their preparation exactly, and no contraction
   statistic flags.
3. The remote QX twin is a job and joins the written case with its own
   budget: backend QXsinglenodesimulator (backend type 1), the
   `bdsc_pauli_qx` series of 12 batches and 36 jobs at 2048 shots. Retained
   QX jobs on this account executed in 0.006 to 10.4 s each (median 0.06 s,
   108 jobs), so the twin needs at most about 6 minutes of execution and
   starts within seconds; the account's transaction ledger has recorded no
   credits for QX jobs ([usage.md](../notes/quantum_inspire/usage.md)), so its
   expected credits are 0, restated from a fresh `qi_platform.py snapshot`.
   The QX twin runs before the first Tuna-17 batch, and the hardware pause does
   not apply to it.

## Submission order

1. Write the case: what the pilot measures, why noise simulation cannot answer
   it (the device's own preparation and readout define the physical effect),
   the backend, 32768 shots, 24 jobs of 19.97 s (479.2 s of execution, 1319.2 s
   of wall time with seven 120 s pauses), expected seconds and credits. Wait
   for the owner's approval and quote it verbatim.
2. Take the placement, readout rates and calibration from a fresh read.
3. For each batch in order: copy the batch directory to
   `results/quantum_inspire/runs/<UTC stamp>-bdsc_pauli_tuna_17-batch-NN/`,
   then `qi_platform.py submit RUN_DIR --backend-type-id 7 --approval "QUOTE"`
   and `qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`. The platform
   enforces the 120 s account pause and the three-circuit batch limit; stop at
   the first failed job or short shot list, and never resubmit a directory that
   holds `submission.json` or `submission-state.json`.
4. After batch 00 and after each later batch that carries a reference, run
   `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --references RUN_DIR...` over the
   run directories so far. Stop the series when a patch qubit of batch 00 reads
   P(1|0) or P(0|1) above 0.15, or when its P(1|0) between two successive
   readout-0 circuits (or P(0|1) between two successive readout-1 circuits)
   moves by more than 0.02, and redraw the placement.
5. After the last batch, `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --analyze RUN_DIR... --out FILE`
   over all eight run directories; a short shot list makes the analysis refuse
   and name the file. Patches are read separately, and the pooled value names
   its equal-weight estimand and includes the within-circuit covariance of the
   patches. The corrected scores carry bootstrap intervals beside the raw
   intervals; correction covers an assignment bias that the contraction law
   cannot see. The quadrature phase of each patch reads the branch phase that
   the contraction law cannot see.
6. Retain the run directories, the analysis and a replay gate in the change
   that retains them, and register the runs in `docs/state/research_state.json`
   ([AGENTS.md](../../AGENTS.md#records)). The result qualifies no device and
   no Belenos measurement.
