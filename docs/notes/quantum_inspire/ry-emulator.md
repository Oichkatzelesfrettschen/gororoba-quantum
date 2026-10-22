# Ry emulator runs: neutral-atom model, compiled gates, result order and failure modes

The Ry emulator (backend type 5, identifier `Rydberg`, location TU/eindhoven)
emulates a neutral-atom processor: atoms in optical tweezers, a computational
qubit in two clock states, and a Rydberg state that blockades neighbors
([neutral-atom example](site/kbase_code-example-getting-started-with-the-neutral-atom-platform.md)
([live](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform/))).
Two things set it apart from QX and Tuna: a program places atoms and drives
them with a global pulse inside an `asm(Rydberg)` block, and the emulator
measures every qubit at the end of the program with no measure statement
([operational specifics](site/kbase_ry-emulator-operational-specifics.md)
([live](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/))).
This guide extends the Ry section of [backends.md](backends.md) and the Ry
rows of [cqasm.md](cqasm.md); numbers carry their authority, and a statement
marked "inferred" has no page or run behind it.

## What it is and why the API says hardware

- **Model** (KB): qubits are two clock states of an atom such as rubidium or
  strontium plus a Rydberg state; control lasers drive single-qubit gates and
  the Rydberg laser acts on all atoms at once. An atom excited to the Rydberg
  state shifts nearby atoms out of resonance, the Rydberg blockade, which
  produces the conditional dynamics and the entanglement. The KB calls the
  backend an emulator throughout; no page states the solver (state vector,
  density matrix or pulse-level master equation), the interaction law or the
  noise model.
- **Location and class** (API, `GET /backend_types/5` and `/backends`): the
  instance is "Ry emulator", location TU/eindhoven, infrastructure
  On-premise, `is_hardware: true`, status idle, heartbeat current at the
  2026-10-17T03:25Z read. The KB says an actual neutral-atom hardware backend
  is planned ("in the near future"), so the flag is inferred to mark a
  site-hosted backend reached through a remote service. The job error
  "RSP returned failure" names a remote service process whose expansion no
  page gives.
- **Consequence of the flag** (`scripts/qi_platform.py`, `submit`):
  `is_hardware` selects the hardware submission rules, so a Ry batch holds at
  most `HARDWARE_BATCH_CIRCUITS` = 3 circuits and goes in only when none of
  the account's batches is queued, although the Ry emulator costs no metered
  quota ([usage.md](usage.md)). Code that filters backends on `is_hardware`
  must also read the identifier.
- **Shared pause.** The same flag puts Ry under the account-wide hardware
  guard of `submit`: a batch is refused while any job on an `is_hardware`
  backend type, Ry or Tuna-17, is unfinished or finished less than
  `HARDWARE_PAUSE_SECONDS` ago (30 s by default, [usage.md](usage.md#pause-escalation)). Ry and Tuna-17 batches therefore
  interleave on one clock, and a Ry submit inside a Tuna batch's window is
  refused before any remote write ("wait N more seconds") and retried, as
  [tuna-17.md](tuna-17.md) describes.

## Qubits, geometry and topology

- **Qubits**: 9 (API `nqubits`; KB "at most 9 atoms to a rectangular lattice
  for a circuit"). `submit` refuses a declared width above 9.
- **Placement** (KB, neutral-atom example): `INIT(x, y) q[i]` inside an
  `asm(Rydberg) '''...'''` block assigns qubit i to lattice position (x, y).
  `INIT` is legal only before any operation; a later `INIT` returns an error
  message, and an atom without `INIT` is placed by the backend. The KB gives
  no lattice spacing, no length unit and no blockade radius, so a position
  fixes only which atoms are nearer than which.
- **API topology**: 72 directed pairs, every ordered pair of the 9 qubits
  (36 undirected), the same all-to-all shape the API reports for QX
  ([catalogue.json](../../evidence/quantum_inspire/catalogue.json),
  retrieved 2026-10-16T23:08Z, and a fresh `qi_backend` read on
  2026-10-17T03:25Z). The default compiler config has no mapping and no
  routing pass, so the platform never rewrites a two-qubit gate to fit a
  coupling map.
- **Which binds**: the physics is geometric. The KB states that blockade
  strength "depends on the physical range of the atomic qubits" and that
  positions determine which atoms lie in blockade range, so the distances
  chosen with `INIT` bind what a `RYD` pulse does to a pair. The API's
  complete graph binds only the compiler and `submit`: nothing rejects a
  gate for its operands. The KB's phrase "arbitrary connectivity" describes
  the platform class, not a measured coupling. Confidence in this reading:
  moderate (inferred from the two KB pages and the empty routing config; no
  run exercised an `INIT` position or a `CNOT` on this backend, and no page
  says how a `CNOT` is realized or what it costs). A run that places two
  atoms far apart and drives `RYD` would falsify the geometric reading if the
  pair still entangled.

## Gate set and the Rydberg pulse

| Source | Gates |
|---|---|
| API `gateset` | X Z Rx Rz T S H CNOT |
| KB operational specifics | single-qubit X, Z, T, S, Rx, Rz; directives `INIT`, `RYD` |
| KB neutral-atom example | X, plus `INIT` and `RYD` in `asm(Rydberg)` |

The KB omits H and CNOT; the API lists both and its compiler config
decomposes them (C4 in [knowledge-base.md](knowledge-base.md)). No retained
run executed an H or a CNOT successfully on this backend, so the API list is
a statement about the compiler and not a measured capability.

- **`RYD(rabi_frequency, detuning, dt)`** (KB): one discrete step of the
  global Rydberg pulse. The parameters are normalized to a reference Rabi
  frequency of 1.0 in dimensionless units; the KB states no unit for `dt`,
  no sign convention for the detuning and no relation between a step and a
  rotation angle. Consecutive steps are merged into one pulse (KB, maximum
  independent set example). The KB example is ten steps of `dt` 0.069 with
  Rabi frequency rising from 0.066 to 0.696 and back to 0 and detuning
  rising from -0.733 to 1.669, a total duration of 0.69 in those units
  (sum of the ten listed `dt`).
- **Compiler** (API `default_compiler_config`): `CNOTDecomposer`, then
  `XZXDecomposer`, no mapping, optimization or routing. The cQASM
  specification passes an `asm` block to its named backend verbatim and
  moves no statement across it ([cqasm.md](cqasm.md)).

### What the Ry configuration does to a gate

`scripts/qi_toolchain_check.py` reads only the batch manifests under
`results/quantum_inspire/cases/` (its `--help` offers `--check` and nothing
else) and holds no Rydberg case, so it cannot compile an ad-hoc file. The
table comes from OpenSquirrel 0.9.1 under `$QI_PYTHON`, applying the
catalogue's two passes in the same loop as the script's `compile_circuit`,
on one-gate programs in a scratch directory outside the repository. It shows
what the passes return locally; the platform's own compile step was not
observed for these programs.

| Source gate | After CNOTDecomposer, XZXDecomposer (rotations in radians) |
|---|---|
| `H q[0]` | `Rx(pi/2)`, `Rz(pi/2)`, `Rx(pi/2)` |
| `CNOT q[0], q[1]` | `CNOT q[0], q[1]` (kept) |
| `Rz(-pi/2) q[0]` | `Rz(-pi/2)` (kept) |
| `X q[0]` | `Rx(pi)` |
| `S q[0]`, `T q[1]` | `Rz(pi/2)`, `Rz(pi/4)` |
| `Sdag q[0]` | `Rz(-pi/2)` |
| `Ry(0.3) q[0]` | `Rx(pi/2)`, `Rz(0.3)`, `Rx(-pi/2)` |
| `CZ q[0], q[1]` | `Rz(pi)`, `Rx(pi/2)`, `Rz(pi/2)`, `Rx(-pi/2)` on q[1]; `CNOT`; the mirrored sandwich |
| `SWAP q[0], q[1]` | `SWAP` (kept; not in the API gateset) |
| `asm(Rydberg)` blocks | preserved verbatim, in place |

Consequences: every compiled program is built from Rx, Rz, CNOT and the
`asm` blocks. `SWAP` and any gate outside the API list pass the compiler
unchanged, so the emulator's interpreter is the first place they can fail;
the repository's teleport generator writes a SWAP as three CNOTs
(`scripts/qi_crosstalk_teleport_cases.py`, `gate`). The failed teleport job
below contains H and CNOT, so its compile output would be Rx-Rz-Rx for each
H and CNOT unchanged, matching the Rx-Rz-Rx decomposition noted in
[backends.md](backends.md).

libqasm 1.2.1 under `$QI_PYTHON` analyzes the failed teleport program, the
X-only program and the KB example (two `INIT` lines, ten-step `RYD` block
shortened to two steps) without a single error, so no cQASM grammar rule
explains the failure below.

## Measurement and result order

- **Measurement** (KB): no mid-circuit measurement, no measure statement
  from the user, one implied measurement of every qubit at the end of the
  run. The repository's teleport generator comments that the emulator
  "rejects measure statements"; no retained run tests a measure statement,
  so that claim is unsourced (the failed teleport program contains none).
- **Result order** (measured,
  [runs/2026-10-16T213823Z-Rydberg-diagnostic](../../../results/quantum_inspire/runs/2026-10-16T213823Z-Rydberg-diagnostic/)):
  the program is `qubit[2] q` and `X q[0]`, with no bit register and no
  measurement. All 1024 shots returned `10` (`results.json`, `raw/x-only.cq.json`).
  Qubit 0 is the leftmost character, the reverse of QX and Tuna, where qubit
  0 is rightmost. The test is one asymmetric preparation on a 2-qubit
  register: it fixes the order for width 2 and says nothing about a
  register of 9, about qubits above 1, or about a program with a declared
  `bit` register. Read every Ry result by qubit index and validate the order
  again with an asymmetric X on a new width.
- **Noise**: the X-only run returned the ideal outcome in 1024 of 1024 shots,
  so the emulated single-qubit X is noiseless within that sample; the
  emulator's noise model, if any, is unstated.

## Limits and measured cost

| Limit | Value | Authority |
|---|---|---|
| Qubits | 9 | API `nqubits` |
| Shots, default and maximum | 1024 and 1024 | API `default_number_of_shots`, `max_number_of_shots` |
| Execution limit | 3600 s | API `job_execution_time_limit` |
| Circuits per batch, batches per queue | 5, 5 (the repository holds a Ry batch to 3 circuits) | API; `qi_platform.py submit` |
| Queue at 2026-10-17T03:25Z | 0 jobs, 0 s wait | API `queue` |

**Measured cost.** The completed X-only job reports `execution_time_in_seconds`
16.257528 for 1024 shots, 15.9 ms per shot if cost is linear in shots. The
failed teleport job, which executed no shot, ran from `queued_at`
21:16:47.296 to `finished_at` 21:17:03.337, 16.04 s, and the completed job
from 21:38:29.189 to 21:38:45.572, 16.38 s. A job that never reached a shot
took as long as one that ran 1024, so a large fixed cost per job, not a
per-shot cost, may account for most of the 16 s. The 15.9 ms per shot figure
in [backends.md](backends.md) and [usage.md](usage.md) is therefore an upper
bound from one point, and the scaling in shots is unmeasured. The ledger
recorded no transaction (`transactions: []` in both collections).

## Failure modes

[runs/2026-10-16T211635Z-Rydberg](../../../results/quantum_inspire/runs/2026-10-16T211635Z-Rydberg/)
(`submission.json`, `results.json`, `teleport.cq`) submitted one job of 1024
shots with `backend_status_at_submit` idle. The job status is `failed`,
`results` is empty, `logs.logs` is empty, and `message` reads "Quantum
backend error: RSP returned failure: error interpreting cQASM script".

The program differs from the completed one in every dimension at once:

| Property | Failed `teleport.cq` | Completed `x-only.cq` |
|---|---|---|
| Declared qubits | 9 | 2 |
| Bit register | `bit[9] b` declared, never assigned | none |
| Gates | H (4), CNOT (10), X (1); no Rz | X |
| `asm(Rydberg)` block, `INIT` | none | none |
| Measure statement | none | none |

Both are accepted by libqasm. The construct probe
(`scripts/qi_ry_probe_cases.py`, runs
`results/quantum_inspire/runs/2026-10-17T034952Z-ry_probe-batch-00` to
`-02`, analysis `results/quantum_inspire/ry_probe_analysis.json`) adds one
construct at a time to the X-only program on two qubits and names the cause:

| Circuit | Construct added | Result |
|---|---|---|
| x-baseline | none | completed: `10` in 1024 of 1024 |
| x-bitreg | `bit[2] b`, never assigned | failed: "Quantum backend error: RSP returned failure: error interpreting cQASM script" |
| x-measure | `bit[2] b` and `b = measure q` | failed: "Compilation error: the following gates are not in the primitive gate set: measure" |
| h | H | completed: `00` 501, `10` 523 |
| x-cnot | X, CNOT | completed: `11` 1000, `10` 24 |
| rz-x | Rz(pi/2), X | completed: `10` in 1024 of 1024 |
| h-cnot | H, CNOT | completed: `00` 541, `11` 477, `10` 6 |
| h-cnot-bits | H, CNOT, `bit[2] b` | failed: the reader error above |
| init-h-cnot | `asm(Rydberg)` INIT block, H, CNOT | completed: `00` 493, `11` 516, `10` 15 |

- The emulator's reader rejects every program that declares a bit register,
  assigned or not, so the declaration suffices to cause the teleport
  failure; H, CNOT, Rz and the INIT block run. The probe used two qubits;
  the box-kite ladder below settles the 9-qubit width.
- `measure` is outside the primitive gate set, so the platform's compile step
  rejects it before the emulator reads the program: the Ry emulator takes no
  measurement statement and measures every qubit at the end, as the KB
  states.
- The emulator is noisy: CNOT on `10` leaves the target unflipped in 24 of
  1024 shots (2.3 %), and the Bell pairs carry 0.6 % and 1.5 % of `10`.
- A failed job still spends about 16 s between `queued_at` and
  `finished_at`, so the reader runs after the job's setup.

A Ry case therefore declares no bit register and no measure statement, and
reads the result as the whole register with qubit 0 leftmost.

The repository's generator emits no Ry case because the native form of the
teleport program (no bit register, `RYD` blockade gates) is not built
([experiments.md](experiments.md), `NOT_GENERATED` in
`scripts/qi_crosstalk_teleport_cases.py`).

## Box-kite runs, 2026-10-17

`scripts/box_kite_cases.py` writes Ry cases with no bit register, no
measure statement and no comment, and reads every result with qubit 0
leftmost; `scripts/box_kite_analysis.py` judges them
(`results/quantum_inspire/box_kite_ry_analysis.json`, gate core-425; claim
`qi-ry-emulator-boxkite-capability`).

- **The bit-register fix holds at width 9.** R1 (`qubit[9]`, X on q0) and
  R2 (a `//` comment line) read their ideal outcome in all 1024 shots, and
  R9, the failed `teleport.cq` with its bit register and comments removed,
  completes: the reader error came from the declaration, not from width,
  comments or the teleport gates.
- **Error grows with depth.** Shallow reduced-LCU replicas (one CNOT each)
  read their ideal outcome at a fraction of 0.978 to 1.000, and P = 1/2
  replicas stay inside |z| < 4.5. R9 (10 CNOT) puts 77 of 1024 shots (7.5%)
  outside its 16-outcome ideal support. The full Design B witness of
  (1,10)(4,15) (35 CNOT) reads P(selector = 0) 0.270 dark and 0.656 bright,
  a contrast of 0.387, below the 0.9 ideal-fraction floor, so the smoke
  series stops there; the negative fixture (P = 1/2) conforms. The loss is
  reported as an emulator rate: the error model is undocumented.
- Execution took 15.2 to 23.5 s per 1024-shot job, again independent of
  depth to within the spread.

## What experiments fit

- **Fits**: a question about Rydberg blockade or a global drive on at most 9
  atoms with a chosen geometry: the number of excitations after a `RYD`
  sweep (the KB maximum-independent-set example reads the count of 1s per
  string against the blockade), the dependence of a result on `INIT`
  distances, a detuning or Rabi sweep across several jobs within one batch,
  and the result order test above. The answer comes from a final
  Z-basis string only.
- **Does not fit**: mid-circuit measurement, reset or feed-forward;
  anything that reads a classical bit register; a result wider than 9
  qubits; more than 1024 shots per job (repeat jobs instead); a statement
  about a device, since the backend emulates one and its noise model is not
  published; timing or calibration questions; and any circuit built on H or
  CNOT until one runs.
- **Routing** (root AGENTS.md): a simulation of 14 qubits or fewer runs on
  Kaggle. A Ry run answers a question about this emulator's own behavior
  (its pulse model, the geometry, the result order), and the case says why
  Aer cannot.

## Do a Ry emulator run

A Ry run spends no metered quota and still waits for the owner's approval of
a written case (root AGENTS.md, "Hardware services").

1. Write the case. No generator emits a Ry case; a new one follows the
   pattern of the others (a `cases.json` with `backend` `Rydberg`,
   `backend_type_id` 5, `nqubits`, `shots` at most 1024, and one `.cq` per
   circuit listed with its sha256, under
   `results/quantum_inspire/cases/<name>/batch-NN/`) and joins
   `ci/gates.json` in the same change.
2. Write each circuit in the form that has run: `version 3.0`, `qubit[n] q`,
   no `bit` register, no measure statement, `INIT` lines first inside one
   `asm(Rydberg)` block, then X, Z, Rx, Rz, T, S, and `RYD` steps. Add H or
   CNOT only as the single variable of a probe in the table below.
3. Analyze every circuit with libqasm and compile it with the Ry
   `default_compiler_config` under `$QI_PYTHON`
   (`QI_PYTHON=${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}`);
   the analyzer's JSON needs `json.loads(..., strict=False)` because it
   embeds `asm` text with control characters.
4. State the expected outcome of every circuit and of the analysis in the
   case, and the result order: qubit 0 leftmost. For a new width, include
   one asymmetric X circuit.
5. Hold a batch to 3 circuits and 1024 shots, and write the cost estimate
   as unknown within 16 s per job to 16 s per 1024 shots until a scaling
   probe runs.
6. Wait for the owner's approval and quote it verbatim.
7. Confirm Ry is idle and none of the account's batches is queued:
   MCP `qi_backends`, `qi_hardware_status` and `qi_jobs`, or
   `"$QI_PYTHON" scripts/qi_platform.py snapshot --out DIR` with DIR outside
   `docs/`.
8. For each batch in order: copy it to
   `results/quantum_inspire/runs/<UTC stamp>-<case>-batch-NN/`, then
   `"$QI_PYTHON" scripts/qi_platform.py submit RUN_DIR --backend-type-id 5 --approval "QUOTE"`,
   `"$QI_PYTHON" scripts/qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`,
   the case's sanity check, and a pause before the next batch. Stop the
   series at the first failure and keep its `message` verbatim. Never
   resubmit a directory that holds `submission.json` or
   `submission-state.json`; use `qi_platform.py reconcile`.
9. Decode strings with qubit 0 leftmost, record the order beside the
   analysis, commit the runs with the analysis and register them in
   `docs/state/research_state.json`.

## Unmeasured capabilities and the smallest probe for each

Rows marked measured ran in the construct probe of 2026-10-17; every other probe is a proposal.

| Capability | Why it is open | Smallest probe |
|---|---|---|
| Which property triggers "error interpreting cQASM script" | measured: a `bit` declaration (construct probe, 2026-10-17) | none |
| H runs | measured: yes, `00` 501 and `10` 523 of 1024 | none |
| CNOT runs | measured: yes, with `10` left in 24 of 1024 shots (2.3 %) | none |
| Width 9 runs | the failure used 9 | `qubit[9] q`, `X q[0]` only; the string should have 9 characters with 1 first |
| Result order at width 9 | order measured at width 2 only | the same program; the position of the 1 |
| Bit register is the cause | measured: yes, `bit[2] b` alone fails | none |
| Time per shot versus fixed cost | failed and completed jobs both took 16 s | the X-only program at 1, 64 and 1024 shots in one batch of 3 |
| `INIT` positions accepted and used | accepted (measured: init-h-cnot completed); whether the positions change the result is unmeasured, since no run used `RYD` | the KB two-qubit example verbatim (two `INIT`, ten `RYD`, two X) |
| Blockade depends on distance | geometry versus all-to-all graph | the KB example at `INIT` separations 1 and 4, both atoms driven; compare the `11` fraction |
| `RYD` pulse area and sign convention | no unit stated | one `RYD(1, 0, dt)` step at a few `dt` after an X-prepared atom; read the oscillation of P1 |
| Measure statement accepted or rejected | generator comment unsourced | X-only program plus `b = measure q` and `bit[2] b` |
| Noise or sampling model | X-only returned 1024 of 1024 | `Rx(pi/2) q[0]` on 2 qubits (ideal 50 percent) at 1024 shots; the spread against binomial |
| Maximum `INIT` coordinate and lattice limits | not stated | one atom at a large coordinate; read the error text |
