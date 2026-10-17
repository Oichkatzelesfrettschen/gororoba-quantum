# Quantum Inspire backends: per-machine constraint sheets

Every number below comes from one of three sources, named on each line:

- **API**: the account's authenticated catalogue,
  [docs/evidence/quantum_inspire/catalogue.json](../../evidence/quantum_inspire/catalogue.json),
  read through `GET /backend_types/`, `/backend_types/{id}/queue` and
  `/backends` by `scripts/qi_platform.py snapshot` (retrieved
  2026-10-16T21:24Z). It is the authority for what this account can submit
  to and with which limits. Refresh it before relying on a limit:
  `"$QI_PYTHON" scripts/qi_platform.py snapshot --out docs/evidence/quantum_inspire`.
- **KB**: the knowledge-base page captured under [site/](site/) (the live page
  is linked; it changes without notice).
- **Measured**: a retained run under
  [results/quantum_inspire/runs/](../../../results/quantum_inspire/runs/).

Status, queue length and heartbeat are snapshot values that change between
reads (Tuna-17 read `executing`, `calibrating` and `benchmarking` within half an hour); limits,
gate sets, topology and compiler passes are the structural facts that
AGENTS.md carries under gate core-347.

## Summary

| Backend type (API id) | Technology | Qubits for this account | Status at snapshot | Shots default / max | Per-job execution limit | Queue at snapshot |
|---|---|---|---|---|---|---|
| QX emulator (1) | state-vector simulator, cloud | 10 (API); the API description says 34 on the Lisa supercomputer, the KB says 26 on a 4 GB server | idle | 1024 / 2048 | 3600 s | 1 job; reported wait 19031-20258 s, while this account's QX jobs started within seconds |
| Ry emulator (5) | neutral-atom (Rydberg) emulator, TU/e | 9 | idle | 1024 / 1024 | 3600 s | empty |
| Tuna-5 (4) | 5 flux-tunable transmons, 4 tunable couplers | 5 | offline (last heartbeat 2026-03-09) | 8192 / 131072 | 300 s | 8 jobs waiting 7-86 days |
| Tuna-9 (6) | 9 transmons, 12 tunable couplers | 9 | offline (heartbeat current) | 8192 / 131072 | 300 s | 8 jobs waiting 11-54 days |
| Tuna-17 (7) | 17 transmons, 24 tunable couplers | 17 | executing, calibrating, benchmarking | 8192 / 131072 | 300 s | 2-8 jobs, 4-213 s wait |

Every type reports `max_jobs_per_batch_job` 5 and `batchjobs_per_queue_limit`
5 (API); the FAQ limits a user to 3 queued jobs per hardware backend (KB,
[faq](site/faq.md), <https://www.quantum-inspire.com/faq/>). On hardware
the repository applies the reading that satisfies the FAQ whether its "job"
means a batch or a circuit: at most three circuits per batch and one queued
batch at a time (`qi_platform.py submit`, root AGENTS.md "Quantum Inspire").

Backend instances behind the types (API `/backends`): QX emulator (Cloud),
Spin-2+ (TU Delft, offline, last heartbeat 2025-12-10), Starmon-7 (TU Delft,
offline, last heartbeat 2026-03-27), Tuna-5, Ry emulator (TU/eindhoven),
Tuna-9, Tuna-17. Spin-2+ and Starmon-7 have no backend type this account
can submit to: no spin-qubit hardware is reachable from this account.

Availability dates (KB, [backends/transmons](site/backends_transmons.md),
<https://www.quantum-inspire.com/backends/transmons/>): Starmon-5 April 2020
to December 2025, Starmon-7 February 2025 to December 2025, Tuna-9 since
December 2025, Tuna-17 since April 2026.

## QX emulator

- **Qubits**: 10 for this account (API `nqubits`); coupling map complete
  (45 pairs), so no routing constraint.
- **Gate set** (API): H I S Sdag T Tdag X X90 Y Y90 Z Z90 mX90 mY90 mZ90 Rx Ry
  Rz U Rn CNOT CR CRk CZ SWAP, plus init, measure, reset, barrier, wait.
- **Compiler** (API `default_compiler_config`): no decomposition, mapping,
  optimization or routing pass.
- **Shots**: default 1024, maximum 2048; raw per-shot data supported.
- **Execution limit**: 3600 s per job.
- **Result order** (Measured): qubit 0 is the rightmost character of a result
  string (asymmetric X tests in the teleport and diagnostic runs).
- **Measured cost**: 2048 shots in 0.028-0.289 s of execution
  (results/quantum_inspire/runs/2026-10-16T211635Z-QXsinglenodesimulator);
  no ledger transaction.
- **Result register** (Measured): one character per qubit, ordered by qubit
  index, each the qubit's last outcome (0 if unmeasured); the bit a
  measurement names is ignored, so mid-circuit outcomes and bit
  assignments other than `b[k] = measure q[k]` do not survive (C21,
  [qx-runs.md](qx-runs.md)).
- **Local twin**: qxelarator 0.10.0 runs the same cQASM locally
  (`qi_run_local` on the MCP server).

## Ry emulator (neutral atoms)

- **Qubits**: 9 (API), placed on a rectangular lattice; `INIT(x, y) q[i]`
  inside an `asm(Rydberg) '''...'''` block at the start of the program sets
  positions, otherwise the backend chooses (KB,
  [neutral-atom example](site/kbase_code-example-getting-started-with-the-neutral-atom-platform.md)).
- **Gate set**: API lists X Z Rx Rz T S H CNOT; the KB lists X, Z, T, S, Rx,
  Rz plus the global Rydberg pulse `RYD(rabi_frequency, detuning, dt)` in an
  asm block, normalized to a reference Rabi frequency of 1.0.
- **Compiler** (API): CNOTDecomposer then XZXDecomposer; no mapping or routing.
- **Measurement**: no measurement statements; every qubit is measured at the
  end; no mid-circuit measurement (KB).
- **Shots**: default and maximum 1024. Execution limit 3600 s.
- **Measured cost**: the 2-qubit X-only diagnostic took 16.26 s of execution
  for 1024 shots, and the failed teleport job spent 16 s between `queued_at`
  and `finished_at` with no shot done, so a fixed per-job cost of about 16 s
  fits both runs; 15.9 ms per shot is an upper bound from one run, not a
  per-shot rate. No ledger transaction.
- **Result order** (Measured): qubit 0 is the **leftmost** character: X on
  q[0] read `10` in 1024 of 1024 shots
  (runs/2026-10-16T213823Z-Rydberg-diagnostic), the reverse of QX and Tuna.
- **Failure mode** (Measured): a 9-qubit teleport circuit with an
  unassigned `bit[9]` register, H (4), CNOT (10) and X (1), and no measure
  statement or `INIT` block, failed at execution (OpenSquirrel 0.9.1 under
  this configuration turns H into Rx-Rz-Rx and keeps CNOT, by a local
  compile; no remote compile output is retained): the job's `message`
  reads "Quantum backend error: RSP returned failure: error interpreting
  cQASM script" while its log stays empty
  (runs/2026-10-16T211635Z-Rydberg). libqasm 1.2.1 accepts the program, so
  the emulator's own reader rejects it; the X-only form of the KB example
  ran, which leaves the unassigned bit register, H, CNOT and the missing
  `INIT` block as candidates ([ry-emulator.md](ry-emulator.md)).
- **API classification**: `is_hardware` is true although the backend is an
  emulator; code that filters on `is_hardware` must also read the name, and
  `qi_platform.py submit` applies the hardware batch rule (at most three
  circuits, no batch while one of the account's batches is queued) to it.

## Tuna-5, Tuna-9, Tuna-17 (transmons)

Common to all three (KB, [tuna-operational-specifics](site/kbase_tuna-operational-specifics.md),
<https://www.quantum-inspire.com/kbase/tuna-operational-specifics/>; API):

- **Native gates**: Rx, Ry, Rz, X90, Y90, mX90, mY90, X, Y, Z, I, S, Sdag,
  T, Tdag, CZ, init, measure, reset. Decomposed: H, CNOT, CR, CRk, SWAP, Rn.
  Not allowed: Display, Display_binary, Not, binary-controlled `c-` gates,
  Toffoli. Without binary control there is no feed-forward: a protocol that
  needs a measurement-conditioned correction applies it to the recorded
  outcomes.
- **Angles**: every single-qubit rotation angle is quantized to the nearest
  multiple of pi/36 (5 degrees).
- **Durations**: single-qubit gate 20 ns, CZ 60 ns, measurement 800 ns,
  initialization 500 or 200 us.
- **Scheduling**: as late as possible (KB); `wait(n) q[i]` idles qubit i
  for n cycles of 20 ns (per qubit, independently); `barrier` bounds a
  scheduling domain. Measurements on several qubits are scheduled too, so
  parallel readout needs a barrier. In OpenSquirrel 0.9.1 the ALAP schedule
  comes from `QuantifySchedulerExporter`, which no backend's
  `default_compiler_config` lists, so the platform applies it after
  compilation; the exporter gives every operation one cycle unless the
  caller supplies operation lengths, so the 800 ns measurement in the
  executed schedule rests on the platform's own length table, which no local
  check reproduces. Compilation rewrites `barrier q` as one barrier per
  qubit in the same order, which the exporter aligns as a run
  (`scripts/qi_toolchain_check.py`,
  [toolchain_check.json](../../evidence/quantum_inspire/toolchain_check.json)).
- **Compiler** (API): SWAP2CZDecomposer then CZDecomposer; the configuration
  lists no mapping and no routing pass, so a circuit keeps every two-qubit
  gate on a coupled pair itself.
- **Mid-circuit measurement**: allowed.
- **Shots**: default 8192, maximum 131072; raw per-shot data supported.
  Execution limit 300 s per job.
- **Control electronics** (KB, backends/transmons): a Qblox cluster with one
  QRM-RF readout module, three QCM-RF modules for single-qubit gates and three
  QCM modules for flux; each transmon has its own drive and flux line and its
  own Purcell-filtered readout resonator pair.
- **Result order** (Measured): qubit 0 is the rightmost character.
- **Calibration**: automated tuning runs between user jobs and can take from
  seconds to 30 minutes, adding to queue wait (KB, faq and
  displaying-and-downloading-your-results); no ledger transaction records it.

| Device | Couplings (API topology, undirected) | Notes |
|---|---|---|
| Tuna-5 | 0-2 1-2 2-3 2-4 (star around Q2) | No four-qubit path exists, so the teleport case has no circuit here. Used in Valles-Sanclemente et al. on coupler frequency placement against spectator effects (KB, backends/transmons). |
| Tuna-9 | 0-1 0-2 1-3 1-4 2-4 2-5 3-6 4-6 4-7 5-7 6-8 7-8 | API message: "Q8 is affected by a spurious two-level system (TLS)". |
| Tuna-17 | 0-1 0-2 1-4 2-4 2-5 3-5 3-6 4-7 4-8 5-8 5-9 6-9 7-10 7-11 8-11 8-12 9-12 10-13 11-13 11-14 12-14 12-15 14-16 15-16 | Measured below. |

**Tuna-17 measured** (runs/2026-10-16T211635Z-tuna_17, 16384 shots per job):

- Execution 9.87-12.57 s per job, 0.60-0.77 ms per shot: the 500 us
  initialization dominates a shot of a few microseconds of gates. At that
  rate the 300 s limit admits the 131072-shot maximum (about 90 s) for
  circuits of this length.
- Queue: the batch's first job started 40 s after creation; the five jobs
  ran back to back, about 11 s each.
- Coherent single-qubit error: after 40 X gates (an identity) a driver read
  P1 up to 0.883 (Q9), which depolarizing, relaxation and readout error cannot
  produce; the implied per-X over-rotation is at least 0.050-0.061 rad on Q6,
  Q8 and Q9.
- Simultaneous-drive crosstalk: driving Q1 and Q2 together raised Q2's P1
  from 0.046 (alone) to 0.893 and Q1's from 0.062 to 0.259, although Q1 and
  Q2 share no coupler. See [experiments.md](experiments.md).

## Starmon-7 (discontinued)

KB ([starmon-7-operational-specifics](site/kbase_starmon-7-operational-specifics.md)):
7 transmons, two rhombi sharing Q3, 8 fixed-frequency couplers; native X, Y,
Z, I, Rx, Ry, X90, Y90, mX90, mY90, S, Sdag, T, Tdag, CZ, init, measure,
reset; decomposed Rz, H, CNOT, SWAP; not allowed CR, CRk, Display, Not,
binary control, Toffoli; angles quantized to pi/28; 20 ns single-qubit
gates, 60 ns CZ, 1 us measurement, 150 us initialization; compiled and
scheduled by OpenQL (ALAP); mid-circuit measurement allowed. No backend type
for this account (API); offline since its last heartbeat 2026-03-27.

## Spin-2+ (offline, not reachable from this account)

KB ([spin-2-plus-operational-specifics](site/kbase_spin-2-plus-operational-specifics.md),
[backends/spin-2-plus](site/backends_spin-2-plus.md)): six quantum dots in
isotopically purified Si-28/SiGe; two single-electron data qubits plus a
three-electron ancilla for Pauli-spin-blockade readout; natives X90, mX90,
Y90, mY90, virtual Rz and an exchange CZ, compiled to X90, Rz and CZ by
OpenSquirrel (McKay virtual-Z decomposition); `qubit[1-4]` register
required, no `reset`, bit registers and measure statements accepted and
ignored, both qubits always measured at the end; single-qubit operations on
two qubits run in sequence, never in parallel; T2* above 5 us and T1 above
200 ms; automated calibration 5-30 minutes. Last heartbeat 2025-12-10 (API).
