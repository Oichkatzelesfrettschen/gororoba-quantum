# QX emulator runs: result semantics, dry runs and runs

The QX emulator (backend type 1, `QXsinglenodesimulator`) is a state-vector
simulator of cQASM 3.0. It parses circuits with libqasm and executes them
without compiler passes: no decomposition, mapping, routing or scheduling
(the catalogue's `default_compiler_config`, [backends.md](backends.md)). It
is noiseless unless a circuit declares `error_model depolarizing_channel, p`,
one symmetric depolarizing rate for the whole circuit
([knowledge-base.md](knowledge-base.md)). For this account it takes 10
qubits, at most 2048 shots per job and 3600 s per job. qxelarator 0.10.0 is
its local twin: the same simulator as a Python module in the QI environment
(`$QI_PYTHON`, [setup.md](setup.md)).

## The result is the measurement register

A QX result string has one character per declared qubit, ordered by qubit
index with qubit 0 rightmost. Each character is that qubit's last measured
outcome, and a qubit that is never measured reports 0 whatever its state.
The bit a measurement assigns to (`b[k] = measure q[j]`) does not enter the
result: QX returns its measurement register, not the cQASM bit register.
qxelarator 0.10.0 and the remote emulator behave identically.

| Circuit (QX 0.10.0, qxelarator) | Bit register under the cQASM 3.0 semantics | QX result |
|---|---|---|
| `X q[0]`, `b[2] = measure q[0]`, `X q[0]`, `b[0:1] = measure q` (`qubit[2]`, `bit[4]`) | `0100` | `00` |
| `X q[0]`, `b[0] = measure q[1]`, `b[1] = measure q[0]` | `10` | `01` |
| `X q[0]`, `b[0] = measure q[1]` (q[0] unmeasured) | `00` | `00` |
| `X q[0]`, no measurement | `00` | `00` |
| `X q[0]`, `b[0] = measure q[0]`, `X q[0]`, `b[1] = measure q[0]` | `01` | `00` |
| `qubit[3]`, `bit[1]`, `X q[2]`, `b[0] = measure q[2]` | `1` | `100` |

The remote emulator returned the same shape on the readout ring-down dry run:
circuits declaring `bit[20]` on `qubit[10]`, with mid-circuit outcomes written
to `b[10..19]`, came back as 10-character strings in both `results` and
`raw_data` (batch job 869986,
`results/quantum_inspire/runs/2026-10-17T030006Z-readout_ringdown_qx_P-batch-01`).
`scripts/qi_platform.py collect` stores `raw_data` verbatim, so the width is
the service's.

### Root cause

qx-simulator's `SimulationResult` carries `results`, a histogram of the
measurement register, and `state`; it has no bit-register field
(`qxelarator.execute_string` returns exactly `results`, `shots_done`,
`shots_requested`, `state`). Release 0.7.3 took the measurement register out
of `QuantumState`, and no release through 0.10.0 exposes the bit register
([releases/qx-simulator.md](releases/qx-simulator.md)). The knowledge base
states the opposite: the bit register "can have an arbitrary size. This
allows you to store for instance the results of intermediate measurements",
and the histogram shows "the contents of the binary register"
([site/kbase_hello-quantum-world.md](site/kbase_hello-quantum-world.md)).
The emulator is the authority for what it returns; the contradiction is C21
in [knowledge-base.md](knowledge-base.md).

### Consequences

- A mid-circuit outcome on QX survives only if its qubit is not measured
  again; an analysis that needs it cannot run on QX.
- An analysis that reads a QX result by bit index reads the wrong character
  whenever a circuit assigns `b[k]` from `q[j]` with `k != j`. Read QX
  results by qubit index.
- A circuit that measures a subset of qubits returns zeros for the rest;
  those characters carry no information.
- Every retained QX run before the ring-down pilot used `b[k] = measure q[k]`
  or a whole-register measurement of equal width, so their analyses read the
  correct characters.
- Tuna returns results "as a shots x bits array in bit-register order"
  ([site/kbase_tuna-operational-specifics.md](site/kbase_tuna-operational-specifics.md)).
  Tuna-17 confirms it: `bit[34]` circuits on `qubit[17]` returned
  34-character strings with every mid-circuit outcome present (batch job
  870030, `results/quantum_inspire/runs/2026-10-17T032034Z-readout_ringdown_tuna_17_P-batch-00`). A QX dry run therefore cannot rehearse a Tuna analysis
  that reads mid-circuit bits.

### Resolution in the readout ring-down pilot

`scripts/qi_readout_ringdown_cases.py` estimates every rate from all shots
and uses the mid-circuit bits only as a cross-check where a backend returns
them. A target left in |1> after its mid-circuit readout, with probability
eps, runs the same single-qubit unitary U as one left in |0>, and
|<1|U|1>|^2 = |<0|U|0>|^2 for every U in SU(2); its X and Y probabilities
become eps + (1 - 2 eps) p0, so after readout correction both quadratures
scale by (1 - 2 eps). The fringe shrinks and its phase, every rate and every
delta(tau) stay unbiased. Where the full register returns (2n characters),
the analysis also reports the estimate postselected on the mid-circuit
outcome; disagreement beyond the standard errors falsifies the invariance.
`--sanity` accepts n or 2n characters, records which, and rejects any other
width.

## Run QX locally (qxelarator)

A local run needs no account, queue or approval and records nothing.

1. Activate nothing: call the QI interpreter directly,
   `QI_PYTHON=${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}`.
2. Execute one circuit:
   `"$QI_PYTHON" -I -c 'import qxelarator, sys; print(qxelarator.execute_string(open(sys.argv[1]).read(), iterations=2048).results)' FILE.cq`,
   or call the MCP tool `qi_run_local` with the cQASM text and shots.
3. Read the result by qubit index (qubit 0 rightmost); the tool returns
   counts, never shots, so expand counts into a shot list before feeding an
   analysis that expects `raw/<file>.json`.
4. Treat agreement as a syntax and plumbing check: qxelarator shares QX's
   simulator, so it reproduces QX's register shape but says nothing about
   Tuna's.
5. Keep `reset` out of any circuit whose law qxelarator must reproduce.
   qxelarator 0.10.0's `reset` on a qubit with weight on |1> discards the
   relative phase of the rest of the register: with q0 in |1> and q1 in
   |->, `reset q[0]` followed by H on q1 reads q1 = 0 in 1000 of 1000 shots,
   where a phase-preserving reset reads 1 (the same program with X in place
   of the reset reads q1 = 1 in 1000 of 1000). Issue #223 holds the
   amplitude-level evidence. The remote QX emulator applies the same map:
   `scripts/qx_reset_phase_probe.py` read q1 = 0 in 2048 of 2048 shots
   (batch job 872957, `results/quantum_inspire/runs/2026-10-18T161620Z-qx_reset_phase-batch-00`,
   gates core-455 to core-457), so a QX dry run of a reset circuit checks
   syntax and plumbing, never its law (knowledge-base.md C22); the upstream
   report is https://github.com/QuTech-Delft/qx-simulator/issues/217. No
   box-kite dialect maps `reset` (`box_kite_cases.DIALECTS`), so `emit`
   refuses it for every generated case.

## Do a QX dry run (remote emulator)

A dry run validates a hardware case end to end on the emulator before any
Tuna batch: syntax as the platform parses it, submission and collection,
result width and order, and the analysis on noiseless data with a known
answer. Quantum Inspire spends no metered quota on it, and it still waits
for the owner's approval of the written case (root AGENTS.md, "Hardware
services").

1. Generate the cases with the experiment's generator
   (`--write results/quantum_inspire/cases`) and run its `--check`; a QX
   profile keeps every circuit within 10 qubits and 2048 shots.
2. State the expected noiseless outcome of every circuit and of the
   analysis verdict in the case or PR text before submitting.
3. Write the case: what the dry run checks, the batch list, the shots, and
   the register width each circuit returns on QX (one character per qubit).
4. Wait for the owner's approval and quote it verbatim.
5. Confirm QX is idle and that none of the account's batches is queued:
   MCP `qi_backends` and `qi_jobs`, or `qi_platform.py snapshot`.
6. For each batch in order: copy the batch directory to
   `results/quantum_inspire/runs/<UTC stamp>-<case>-batch-NN/`, then
   `"$QI_PYTHON" scripts/qi_platform.py submit RUN_DIR --backend-type-id 1 --approval "QUOTE"`,
   `"$QI_PYTHON" scripts/qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`,
   and the generator's `--sanity RUN_DIR`. Stop the series at the first
   failure; never resubmit a directory that holds `submission.json` or
   `submission-state.json` (use `qi_platform.py reconcile`).
7. Run the generator's `--analyze OUT RUN_DIR...` and compare the verdict
   with the stated noiseless expectation; a mismatch is a defect in the
   case, the analysis or the platform, and blocks the hardware series.
8. Commit the run directories, the analysis and its `--replay` gate in the
   change that retains them, and register the runs in
   `docs/state/research_state.json` (root AGENTS.md, "Records").

## Do a QX run (an experiment on the emulator)

A QX run is an experiment whose answer the emulator itself supplies: an
ideal reference distribution for a circuit too wide for an exact
calculation in the repository, or a depolarizing-channel study at one
global rate. It follows the dry-run procedure with three changes:

1. The case states the question QX answers and why a noiseless or uniformly
   depolarized state vector answers it; a question about calibrated noise
   goes to the repository's Aer noise models (Kaggle or the build host), and
   a question about a device goes to that device.
2. An `error_model depolarizing_channel, p` line follows the `qubit`
   declaration when the case studies depolarizing noise; p is part of the
   case and of its digest.
3. The analysis reads results by qubit index and never relies on a
   mid-circuit outcome.

## Toolchain

| Component (QI environment) | Version | Use it for |
|---|---|---|
| libqasm | 1.2.1 | parse and analyze every generated circuit before any submission, as QX and OpenSquirrel parse it |
| OpenSquirrel | 0.9.1 | apply a backend's `default_compiler_config` passes locally and read the compiled circuit the platform executes |
| qxelarator | 0.10.0 | local QX emulation |
| quantuminspire | 4.1.0 | the `qi` CLI and API client behind `scripts/qi_platform.py` |
| qiskit-quantuminspire | 0.18.5 | Qiskit targets of the QI backends; its cQASM writer emits a multi-qubit barrier as per-qubit barriers, so timing-sensitive cases write cQASM directly |
| pennylane-quantuminspire | 0.15.5 | not installed (PennyLane >= 0.43, < 0.46) |

The repository's Python 3.14 stack never imports these (they cap Python
below 3.14), so a toolchain check runs under `$QI_PYTHON` and retains its
output; the gate shards compare the retained output, and CI's `qi-stack` job
reruns the toolchain under `$QI_PYTHON` and requires the same bytes.
