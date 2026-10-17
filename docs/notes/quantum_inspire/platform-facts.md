# Quantum Inspire platform facts by source

Every per-backend constraint, retired-backend record, calibration and
maintenance rule, account rule and tooling fact the knowledge-base capture
establishes, each beside its source. Paths are relative to this directory;
`C<n>` refers to the reconciliations in
[knowledge-base.md](knowledge-base.md#contradictions-and-their-reconciliation).
Captures were retrieved 2026-10-16 UTC; the catalogue is
[catalogue.json](../../evidence/quantum_inspire/catalogue.json). The live
pages stay the authority, since they change without notice;
[backends.md](backends.md) and [usage.md](usage.md) carry the measured runs.

## Per-backend constraints

| Fact | QX emulator | Tuna-5 / Tuna-9 / Tuna-17 | Ry emulator | Source |
|---|---|---|---|---|
| Backend type id, identifier | 1, `QXsinglenodesimulator` | 4 `tuna_5`, 6 `tuna_9`, 7 `tuna_17` | 5, `Rydberg` | catalogue |
| Qubits (`nqubits`) | 10 | 5, 9, 17 | 9 | catalogue |
| Topology | 90 directed pairs (all-to-all on 10) | Tuna-5 star (center Q2, 4 couplers), Tuna-9 diamond (center Q4, 12 couplers), Tuna-17 ninja star (24 couplers); 8, 24, 48 directed pairs | 72 directed pairs (all-to-all on 9); atom positions set by `INIT` | catalogue `topology`; [Tuna page](site/kbase_tuna-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)) |
| Shots max (default) | 2048 (1024) | 131072 (8192) | 1024 (1024) | catalogue |
| Job execution time limit | 3600 s | 300 s | 3600 s | catalogue `job_execution_time_limit`; terms: over-limit runs are aborted |
| Batch jobs queued per user and backend type | 5 | 5 | 5 | catalogue `batchjobs_per_queue_limit`, OpenAPI definition (C1) |
| Jobs per batch job | 5 | 5 | 5 | catalogue `max_jobs_per_batch_job`; on hardware the repository submits at most 3 per batch, one queued batch at a time (C1) |
| Raw (per-shot) data | yes | yes | yes | catalogue `supports_raw_data` |
| Default compiler passes | none | SWAP2CZDecomposer, CZDecomposer | CNOTDecomposer, XZXDecomposer | catalogue `default_compiler_config` |
| `is_hardware`, location | false, Cloud | true, TU Delft | true (an emulator), TU/eindhoven | catalogue `backend_types`, `backends` (C2) |
| Native durations | n/a | 20 ns single-qubit, 60 ns CZ, 800 ns measurement, 500 or 200 us initialization | not stated | [Tuna page](site/kbase_tuna-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)) |
| Angle quantization | none | multiples of pi/36 (5 degrees) | not stated | Tuna page |
| Mid-circuit measurement | yes | yes | no; all qubits measured at end | Tuna page, [Ry page](site/kbase_ry-emulator-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/)), qx-simulator 0.7.1 |
| `wait` unit | cycle | one cycle = 20 ns, per qubit | n/a | Tuna page; spec |
| Status message at snapshot | none | Tuna-9: "Q8 is affected by a spurious two-level system (TLS)" | none | catalogue `messages` |

Register width: the executing page requires the declared qubit register to
equal the chip size on hardware; every retained Tuna-17 run declared
`qubit[17]`, so narrower declarations on Tuna are untested (C15). QX runs
declared `qubit[10]`; wider is untested (C3).

Retained-run evidence
([results/quantum_inspire/runs/](../../../results/quantum_inspire/runs/)):
QX and Tuna-17 accepted `H`, `CNOT`, `SWAP`, `X`, `X90`, `Y90`,
`wait(n) q[i]`, `barrier q` and `b = measure q`, and Tuna-17 also `S` and
`Sdag`; a Tuna-17 job of 16384
shots executed in 9.9 to 12.6 s. The Ry emulator rejected a 9-qubit
`H`/`CNOT` program with `bit[9] b` (job message "Quantum backend error: RSP
returned failure: error interpreting cQASM script") and ran a 2-qubit `X` program without a bit
register (1024 shots, 16.26 s); the cause of the rejection is open (C4).
Every job in [usage.json](../../evidence/quantum_inspire/usage.json) shows
`charged: 0`.

## Retired and offline backends

- Starmon-7: available February to December 2025
  ([transmons](site/backends_transmons.md) ([live](https://www.quantum-inspire.com/backends/transmons/))); 7 qubits, native durations 20 ns
  single-qubit, 60 ns CZ, 1 us measurement, 150 us initialization, angle
  quantization pi/28, compiled with OpenQL
  ([Starmon-7 page](site/kbase_starmon-7-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/))); the
  catalogue lists backend 3 offline with last heartbeat 2026-03-27 and no
  backend type.
- Starmon-5: April 2020 to December 2025 (transmons page); QI 1.0 limits
  were 16384 shots maximum, 8192 default
  ([release-notes-old](site/release-notes-old.md) ([live](https://www.quantum-inspire.com/release-notes-old/))).
- Spin-2+: taken offline ([backends](site/backends.md) ([live](https://www.quantum-inspire.com/backends/))); catalogue backend 2
  offline, last heartbeat 2025-12-10, no backend type. Fact sheet values:
  X90 56-84 ns, CZ 300 ns, register readout 100 us (PSB integration 37 us),
  T1 181-261 ms, T2* 1.5-6.4 us, X90 fidelity 99.8-99.9%, CZ 95.5%,
  readout 97-98%, 80 mT field, about 200 mK (fact sheet, sha256
  `aeaa1513ecebc7d8918066d11915fd74f13fd77362268b58c5c5e006f1811594`,
  live https://www.datocms-assets.com/119587/1738752183-4-technical-fact-sheet-quantum-inspire-spin-2-plus.pdf).

## Calibration, tuning and maintenance

- Hardware backends run an automated tuning program of a few seconds to
  30 minutes; a job scheduled during tuning waits longer
  ([faq](site/faq.md) ([live](https://www.quantum-inspire.com/faq/))). Spin-2+ full calibration took 5 to 30 minutes and
  kept the device calibrated for more than 24 h without intervention
  ([spin-2-plus](site/backends_spin-2-plus.md) ([live](https://www.quantum-inspire.com/backends/spin-2-plus/))). No page states a Tuna
  calibration cadence; the catalogue reported Tuna-17 `calibrating` at
  snapshot time (C20).
- Cost: no source states that calibration time is billed. The only cost
  evidence is `charged: 0` on every retained job in usage.json; the FAQ
  presents tuning as added waiting time.
- Maintenance: QI 2.0 has regular scheduled and unscheduled maintenance that
  may fail submitted jobs ([release-notes](site/release-notes.md) ([live](https://www.quantum-inspire.com/release-notes/))); backends
  also go offline for R&D, announced on the website where possible
  ([faq](site/faq.md) ([live](https://www.quantum-inspire.com/faq/))); the terms promise that normal downtime is scheduled
  and announced ([terms](site/terms-and-conditions.md) ([live](https://www.quantum-inspire.com/terms-and-conditions/)), item 21). QI 1.0's
  Wednesday 08:00-12:00 CET window is historical.
- Typical hardware job: 30 to 90 s with overhead; hybrid jobs up to 15 min or
  longer (FAQ). The status refreshes every 30 s in the web GUI.

## Account rules (terms of 6 Feb 2025)

From [site/terms-and-conditions.md](site/terms-and-conditions.md) ([live](https://www.quantum-inspire.com/terms-and-conditions/)) (PDF sha256
`64c49043f5467a61a9c2cf9f49713935d47e9bce0ada1faec938c99b33582b97`, live
https://www.datocms-assets.com/119587/1740490348-2025-02-06-terms-and-conditions-quantum-inspire.pdf):

- Non-commercial use only; commercial use needs prior written permission.
- Accounts and credentials are strictly personal and may not be shared.
- Use is limited to exploring, learning and sharing quantum algorithms;
  EU Russia sanctions screening applies.
- Shared resources: queued execution, per-backend limits on qubits, shots
  and run time; over-time executions are aborted; staff may reprioritize,
  relay jobs to external compute providers (who may see the code) or refuse
  and delete jobs.
- Uploaded algorithms, data and code are open to use and redistribution by
  QuTech under licenses of its choice unless agreed otherwise in writing
  before upload, and remain after account deletion.
- Users report detected errors and avoid wasting processor time (use the
  syntax checks).
- Free simulation up to 26 qubits, and in principle up to 37 qubits on the
  national supercomputer.
- One free account type in QI 2.0 ([managing-your-account](site/kbase_managing-your-account.md) ([live](https://www.quantum-inspire.com/kbase/managing-your-account/)));
  abuse of the queue leads to account removal (FAQ).

## Setup and tooling facts

- CLI: `qi login` opens a browser login and stores credentials in
  `~/.quantuminspire/config.json`, which both plugins read;
  `qi logout`; jobs with `qi run --file F --backend-type-id N [--num-shots]
  [--store-raw-data] [--name] [--persist]`; inspection with `qi jobs
  status|logs|results|final-result|inspect`; backends with `qi backends
  list|get`; compilation with `qi files compile` (default stage
  Decomposition) ([sdk/README.md](sdk/README.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/quantuminspire/054a4f0be22983a5d515c31a24881bc0d875463d/README.md)), 4.1.0). The kbase pages'
  `qi files upload` and `qi results get` are gone since 4.0.0 (C16).
- Hybrid `.py` files need the documented `execute`/`finalize` format
  ([qiskit hybrid basics](sdk/qiskit-quantuminspire/docs/hybrid/basics.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/qiskit-quantuminspire/fbe5256e6671a45cf2fc6557a111f0dc705cf6ac/docs/hybrid/basics.md))).
- PennyLane: `pennylane_quantuminspire.qi_device.QIDevice` wraps a
  `qiskit_quantuminspire.qi_provider.QIProvider` backend; only `expval` and
  `var` work on backends without per-shot results; `Asm` emits assembly
  declarations
  ([submitting.rst](sdk/pennylane-quantuminspire/docs/getting_started/submitting.rst) ([live](https://raw.githubusercontent.com/QuTech-Delft/pennylane-quantuminspire/0f7a6fffd39613bc9e14f6a735cc81cb667803ad/docs/getting_started/submitting.rst))).
- REST: OpenAPI at https://api.quantum-inspire.com/openapi.json (retained as
  [api/openapi.json](api/openapi.json) ([live](https://api.quantum-inspire.com/openapi.json))) and docs at `/docs`; the API root
  answers 404 (C17). Client package `qi-compute-api-client`.
- Results: histogram keys and raw data are decimal values of the bit
  register with `b[0]` as the least significant bit
  ([displaying results](site/kbase_displaying-and-downloading-your-results.md) ([live](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/))).

## Gate list entries

`ci/gates.json` runs `scripts/capture_qi_docs.py` under core-001 (ruff
check), core-002 (ruff format), core-039 (mypy) and core-346
(`"$PYTHON" -B -W error scripts/capture_qi_docs.py --check`, every captured
byte offline); `docs/verify_sources.py` checks the links in normal and `-O`
modes.
