# BDSC Tuna-17 Pauli pilot

This runbook orders the series that
[bdsc-tuna17-pauli-pilot.md](../design/bdsc-tuna17-pauli-pilot.md) designs and
`scripts/qi_bdsc_pauli_cases.py` builds: twelve witness circuits, three
quadrature and two cosine circuits and ten readout references in nine batches
of three circuits on Tuna-17 (27 jobs), each witness carrying three disjoint
patches,
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
   readout-biased, coherent, branch-phase, matched-visibility,
   unresolved-phase, drift, breach, context and twin series through the
   analysis and every refusal of `--submit-next` offline (gate `core-627`).
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
   interval, every quadrature and cosine parity reads its ideal, the phase
   reads 0 within three standard errors, and `control_verdict.pass` is true.
3. The remote QX twin is a job and joins the written case with its own
   budget: backend QXsinglenodesimulator (backend type 1), the
   `bdsc_pauli_qx` series of 14 batches and 41 jobs at 2048 shots. Retained
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
   the backend, 32768 shots, 27 jobs of 19.97 s (539.1 s of execution, 1499.1 s
   of wall-time ceiling with eight pauses at the top 120 s step, plus the
   shared queue), expected
   seconds and credits. Wait for the owner's approval and quote it verbatim.
2. The platform publishes no Tuna calibration data
   ([tuna-17.md](../notes/quantum_inspire/tuna-17.md#readout-calibration-drift)).
   The fresh surfaces before batch 00 are the backend's identity, status,
   topology, gate set, default compiler configuration and queue; batch 00's
   readout-0 and readout-1 are the first fresh assignment measurement, and its
   stop clears before any witness is sent.
3. The QX twin first, one batch at a time:
   `"$QI_PYTHON" scripts/qi_bdsc_pauli_cases.py --submit-next results/quantum_inspire/cases/bdsc_pauli_qx --approval "QUOTE"`,
   then `"$QI_PYTHON" scripts/qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`
   on the run directory it names, and again until every batch is collected.
   `--analyze` over the twin's run directories writes `TWIN_ANALYSIS`; its
   `control_verdict` must pass.
4. Tuna-17, one batch at a time:
   `"$QI_PYTHON" scripts/qi_bdsc_pauli_cases.py --submit-next results/quantum_inspire/cases/bdsc_pauli_tuna_17 --control TWIN_ANALYSIS --approval "QUOTE"`,
   then `collect` on the run directory it names. `--submit-next` refuses
   until the previous batch is collected with every job completed and every
   shot list full, the batch-00 assignment stop (P(1|0) or P(0|1) above 0.15)
   and the bracket drift stop (more than 0.02 between successive references of
   one kind) are clear, the twin's control verdict passes, and the live
   topology, gate set and compiler configuration match the cases. It waits out
   the account pause (30 s by default; on a platform failure set
   `QI_HARDWARE_PAUSE_SECONDS` to the next step of 60, 90, 120,
   [usage.md](../notes/quantum_inspire/usage.md#pause-escalation)), copies the batch to
   `results/quantum_inspire/runs/<UTC stamp>-bdsc_pauli_tuna_17-batch-NN/` with
   one stamp for the series, writes `series-gate.json` and submits through
   `qi_platform.submit`. A refused stop ends the series; a directory holding
   `submission.json` or `submission-state.json` is never resubmitted.
   `"$QI_PYTHON" scripts/qi_series_watch.py bdsc_pauli_tuna_17` prints each
   job's queue wait and run time and each collected batch's execution times,
   applied pause, idle gap and stop metrics while the series runs.
5. After the last batch, `"$PYTHON" scripts/qi_bdsc_pauli_cases.py --analyze RUN_DIR... --out FILE`
   over all nine run directories. The raw scores are primary; tensor-model
   mitigated scores carry Jeffreys-posterior intervals conditional on
   independent single-qubit assignment and are withheld on a patch whose
   references flag a neighbor-context shift. The primary endpoints are the pair
   chi-square and the branch phase of each patch; everything else is
   exploratory.
6. Retain the run directories, the analysis and a replay gate in the change
   that retains them, and register the runs in `docs/state/research_state.json`
   ([AGENTS.md](../../AGENTS.md#records)). The result qualifies no device and
   no Belenos measurement.
