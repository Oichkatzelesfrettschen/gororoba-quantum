# Tuna-9 runs: status, topology, the Q8 two-level system and the run procedure

Tuna-9 (backend type 6, identifier `tuna_9`, TU Delft) is a 9-transmon
processor with 12 flux-tunable couplers, available since December 2025
([transmon backends](site/backends_transmons.md)
([live](https://www.quantum-inspire.com/backends/transmons/))). It shares its
gate set, compiler passes, durations and result format with Tuna-5 and
Tuna-17 ([backends.md](backends.md)). No retained run has executed on it:
this guide states what the catalogue and the knowledge base fix, what the
Tuna-17 runs measured that the Tuna-9 design shares, and what stays open until
the device is online. A statement marked "inferred" has no page or run behind
it.

## Live status

Read through the MCP tools `qi_backend` (type 6) and `qi_hardware_status` at
2026-10-17T03:25Z:

| Field | Value |
|---|---|
| `status` | offline |
| Last heartbeat | 2026-10-17T03:25:10Z (current) |
| `messages` | "Please be aware that Q8 is affected by a spurious two-level system (TLS)" |
| Queue | 8 jobs; wait min 1009108 s (11.7 days), mean 3397597 s (39.3 days), max 4728363 s (54.7 days) |
| Limits | 9 qubits, shots 8192 default and 131072 maximum, 300 s per job, 5 circuits per batch, 5 batches per queue |

The heartbeat is current while the status is offline, so the control
software reports and the device accepts no execution; Tuna-5 differs, with
its last heartbeat on 2026-03-09 ([backends.md](backends.md)). The API gives
no reason for "offline" (maintenance, calibration failure or a withdrawn
device are all consistent with it) and no return date. The Q8 message is
attached to the backend type and carries no date. The wait statistics are
elapsed times of a queue that is not draining: the retained catalogue, whose
heartbeat fields read 2026-10-17T03:18:42Z, holds min 1008713, mean 3397202
and max 4727968 s for the same 8 jobs, and each statistic grew by 395 s by
the 03:25Z read (inferred: waits are measured from enqueue to now). The jobs
belong to other users or to this account; the account-scoped count comes from
`qi_jobs` or the `user_only` queue read in `submit`. A job submitted now
would queue behind them for at least the minimum wait if the queue is served
in order (inferred; no page states the discipline), and the FAQ lists
"limited online availability" during maintenance and tuning
([faq](site/faq.md) ([live](https://www.quantum-inspire.com/faq/))).
Refresh before relying on any line above: `qi_backend`, or
`"$QI_PYTHON" scripts/qi_platform.py snapshot --out /tmp/DIR` with a
directory outside `docs/`.

## Topology

The API reports 24 directed pairs, 12 undirected couplers
([catalogue.json](../../evidence/quantum_inspire/catalogue.json) and a fresh
`qi_backend` read). The KB calls the layout a diamond-like configuration
with Q4 at the center, 12 flux-tunable couplers connecting nearest neighbors
([tuna-operational-specifics](site/kbase_tuna-operational-specifics.md)
([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/))).

Adjacency (API, undirected, computed in a scratch script):

| Qubit | Neighbors | Degree |
|---|---|---|
| Q0 | 1, 2 | 2 |
| Q1 | 0, 3, 4 | 3 |
| Q2 | 0, 4, 5 | 3 |
| Q3 | 1, 6 | 2 |
| Q4 | 1, 2, 6, 7 | 4 |
| Q5 | 2, 7 | 2 |
| Q6 | 3, 4, 8 | 3 |
| Q7 | 4, 5, 8 | 3 |
| Q8 | 6, 7 | 2 |

Couplers: 0-1 0-2 1-3 1-4 2-4 2-5 3-6 4-6 4-7 5-7 6-8 7-8. Degrees sum to 24.

- **Bipartite**: yes, by two-coloring from Q0. Part A (even distance from
  Q0): Q0, Q3, Q4, Q5, Q8. Part B: Q1, Q2, Q6, Q7. Every coupler joins a
  qubit of A to one of B, so the graph has no odd cycle and no triangle; its
  four independent cycles are the squares {0,1,2,4}, {1,3,4,6}, {2,4,5,7}
  and {4,6,7,8}. The diameter is 4 (Q0 to Q8) and Q8 sits at distance 1
  from Q6 and Q7, 2 from Q3, Q4, Q5, 3 from Q1, Q2, 4 from Q0.
- **Against Tuna-5**: a star, Q2 joined to Q0, Q1, Q3, Q4 with 4 couplers,
  bipartite with parts {Q2} and {Q0, Q1, Q3, Q4}, no four-qubit path and no
  cycle (API; the KB: "starfish").
- **Against Tuna-17**: 24 couplers on 17 qubits, bipartite with parts of 8
  and 9, degrees 2 to 4 (API; the KB: "ninja-star"). Tuna-9 has one
  degree-4 qubit (Q4) where Tuna-17 has five (Q4, Q5, Q8, Q11, Q12), half the
  couplers, and four square cells, all of which contain Q4.
- **Fabrication** (KB, backends/transmons): Tuna-9 and Tuna-17 use a Ta base
  layer on sapphire with three readout feedlines and were designed by the
  DiCarlo lab at QuTech; Tuna-5 uses Ta on silicon, one common feedline and
  was fabricated by QuantWare. The Q8 numbers measured on Tuna-17 in
  [experiments.md](experiments.md) belong to a different chip's Q8 and say
  nothing about this one.

## Facts shared with every Tuna backend

| Fact | Value | Authority |
|---|---|---|
| Native gates | Rx, Ry, Rz, X90, Y90, mX90, mY90, X, Y, Z, I, S, Sdag, T, Tdag, CZ, init, measure, reset | KB tuna-operational-specifics (bold list) |
| Decomposed | H, Rn, CNOT, CR, CRk, SWAP | same |
| Not allowed | Display, Display_binary, Not, binary-controlled `c-` gates, Toffoli | same |
| API gateset | I Rx X X90 mX90 Ry Y Y90 mY90 Rz Z S T Sdag Tdag H CZ init measure reset barrier wait | catalogue; the omission of CNOT, SWAP, CR, CRk, Rn is C5 in [knowledge-base.md](knowledge-base.md) |
| Angle grid | single-qubit rotation angles quantize to the nearest multiple of pi/36 (5 degrees) | KB |
| Durations | single-qubit 20 ns, CZ 60 ns, measurement 800 ns, initialization 500 or 200 us | KB |
| Init time per shot | not stated which of 500 or 200 us applies to Tuna-9; Tuna-17 shots took 0.60-0.94 ms | KB; [usage.md](usage.md) |
| Scheduling | as late as possible; `wait(n)` idles a qubit n cycles of 20 ns, per qubit; `barrier` bounds a domain; multi-qubit measurements are scheduled too, so a `barrier` precedes parallel readout | KB; C6 for the `wait(n) q` syntax |
| ALAP provenance | OpenSquirrel 0.9.1 builds the schedule in `QuantifySchedulerExporter`, which no `default_compiler_config` lists; every operation lasts one cycle unless the platform supplies lengths, so the 800 ns measurement rests on the platform's table | [backends.md](backends.md); [toolchain_check.json](../../evidence/quantum_inspire/toolchain_check.json) |
| Compiler passes | `SWAP2CZDecomposer`, then `CZDecomposer`; no mapping, optimization or routing | catalogue `default_compiler_config` |
| Mid-circuit measurement | allowed | KB |
| Binary control | not allowed, so a feed-forward correction applies to the recorded outcomes | KB |
| Shots and limits | 8192 default, 131072 maximum, 300 s per job, raw data supported | catalogue |
| Result order | qubit 0 rightmost on Tuna-17 (measured); Tuna-9 inferred equal | [backends.md](backends.md), run 2026-10-16T211635Z-tuna_17 |
| Result shape | shots by bits, in bit-register order | KB; untested beyond the qubit width (C21) |
| Register width | declare `qubit[9]`; every retained Tuna-17 run declared its full width | C15 |
| Calibration | automated tuning between jobs, seconds to 30 minutes, delays the queue, no ledger charge | KB faq; [usage.md](usage.md) |

OpenSquirrel 0.9.1 under `$QI_PYTHON`, with the Tuna passes, rewrites
`CNOT q[0], q[1]` as `Ry(-pi/2) q[1]`, `CZ q[0], q[1]`, `Ry(pi/2) q[1]`, a
`SWAP` as three CZ with Ry sandwiches, and leaves `H`, `X`, `X90`, `Rz`, `S`
and `Ry` unchanged. H therefore reaches the platform's later stage as `H`,
where the KB says it is decomposed; that stage is not observable locally.
A two-qubit gate on an uncoupled pair is not rewritten, since no routing pass
runs, so each CNOT, CZ and SWAP operand pair must be a coupler listed above.

Shot cost, inferred from Tuna-17 (0.60-0.94 ms per shot, dominated by
initialization): about 0.7 ms per shot, so the 131072-shot maximum would take
about 90 s, inside the 300 s limit for circuits of a few microseconds. Tuna-9
has not confirmed the init time or the rate.

## The two-level system on Q8

A spurious TLS is a microscopic defect that behaves as a two-level system
near the qubit's frequency. The message states that it affects Q8 and states
nothing else, so every consequence below beyond the topology is inferred from
the general behavior of such defects and from the Tuna-17 spectator results
in [experiments.md](experiments.md): a TLS can shorten Q8's T1, make its
frequency or decay drift between calibrations, and degrade gates and readout
on it, and a coupled neighbor can inherit part of that noise.

- **Couplers that touch Q8**: Q6-Q8 and Q7-Q8, the only two (degree 2). A
  CZ on either couples to the defective qubit directly. Q6 and Q7 are the
  qubits whose couplers share Q8; their other neighbors are Q3, Q4 and Q4,
  Q5.
- **Exclude Q8 from**: any measured data qubit; any T1, T2, Ramsey, readout
  or coherence experiment whose answer is a property of the chip rather than
  of Q8 (a TLS shows up as a fluctuating or non-exponential decay and would
  enter every pooled fit); a spectator or ZZ map of the Q6-Q8 and Q7-Q8
  couplers unless the TLS is the subject; a path or star used for a fidelity
  claim; and any average over all 9 qubits.
- **Keep Q8 as**: an idle spectator only where the question is how a defect
  on a neighbor changes Q6 or Q7, and as a deliberate probe of the TLS (a
  question about the device itself, which is the kind of question a hardware
  run answers).
- **What the exclusion leaves**: Q0-Q7 with 10 couplers, connected, diameter
  4, degrees Q0 2, Q1 3, Q2 3, Q3 2, Q4 4, Q5 2, Q6 2, Q7 2; two disjoint
  four-qubit paths still exist (1-0-2-5 and 3-6-4-7, checked in a scratch
  script), and a third disjoint path does not exist with or without Q8.
- **Q8 stays initialized and measured.** On hardware every qubit is
  initialized at each shot start and measured at its end whether or not the
  program touches it (KB hardware-backends), and the program declares
  `qubit[9]`, so an excluded Q8 still produces a readout character. Drop that
  character from the analysis and do not treat it as a control. Whether Q8's
  defect disturbs the simultaneous readout of Q6 and Q7 is unmeasured.
- **Existing cases include Q8.** `results/quantum_inspire/cases/tuna_9/` is
  generated from the catalogue topology alone: batch-00 and batch-01 hold the
  star T=7 with drivers 5 and 8, and the second teleport path 3-6-8-7 runs
  its Bell pair through Q8 as P2. The generator has no exclusion option, so
  these cases do not avoid Q8 until it gains one.

## What no retained run on Tuna-9 measures

No run under `results/quantum_inspire/runs/` used Tuna-9, and
`docs/state/research_state.json` registers none. Everything measured about
Tuna in the repository comes from Tuna-17. The following are therefore
unmeasured on Tuna-9: its gate times, init time, per-shot cost, queue
behavior while online, result order, readout error, coherence, coupler ZZ,
spectator drive effects, angle quantization, and the effect of the Q8 TLS.
Six circuits are generated and CI-checked against libqasm and OpenSquirrel
(`toolchain_check.json`: `tuna_9/batch-00` and `batch-01`, all compiled),
which proves they parse and compile and nothing about the device.

## Which generators emit Tuna-9

- **`scripts/qi_crosstalk_teleport_cases.py`** writes
  `results/quantum_inspire/cases/tuna_9/batch-00/` (additivity-none, -A, -B)
  and `batch-01/` (additivity-none, -AB, teleport), 16384 shots each, from
  `BACKENDS["tuna_9"] = (16384, True, "tuna")`. `teleport.cq` is
  `batch-01/teleport.cq`. Tuna-9 holds two teleport paths (inputs `0` and
  `1`: 1-0-2-4 and 3-6-8-7) because the topology has no third disjoint
  four-qubit path, so the `+` and `+i` inputs do not appear. The gate
  `--self-test` covers `tuna_5`, `tuna_17`, `QXsinglenodesimulator`,
  `Rydberg` and the series reduction but not `tuna_9`.
- **`scripts/qi_readout_ringdown_cases.py`**, **`scripts/qi_coupler_zz_map.py`**
  and **`scripts/qi_zero_divisor_cases.py`** emit no Tuna-9 case: the first
  two hold `PROFILES` with `tuna_17` and `qx` only, the third a single
  `BACKEND = "tuna_17"`.
- **Adding a Tuna-9 profile** to a `PROFILES` generator: add an entry such as
  `"tuna_9": {"identifier": "tuna_9", "qubits": 9, "shots": 8192 or 16384,
  "directory": "<generator>_tuna_9"}`; pick the targets from the Tuna-9
  adjacency above with Q8 excluded (the generators draw couplings from the
  catalogue and need an explicit exclusion list); shorten any series that
  needs more than 9 qubits; extend `--check` and `--conformance` to the new
  directory; write it with `--write results/quantum_inspire/cases`; add the
  regenerated check and toolchain record to `ci/gates.json` in the same
  change. For the teleport generator the edit is a `--exclude-qubits`-style
  filter in `disjoint_stars` and `disjoint_paths`, which today pass every
  catalogue qubit.

## Do a Tuna-9 run once it is online

A run needs the owner's approval of a written case (root AGENTS.md,
"Quantum Inspire"); no metered quota is spent.

1. Confirm the device state now: `qi_backend` for type 6 and
   `qi_hardware_status`. Proceed only when `status` is idle (or executing and
   draining) and the queue's minimum wait is within what the case accepts.
   Re-read `messages`: if the Q8 message has changed or other qubits are
   named, rebuild the target list.
2. Choose targets from the adjacency above, excluding Q8 unless the TLS is
   the subject; state every coupled pair a two-qubit gate uses.
3. Generate the case with the experiment's generator (new profile or
   `qi_crosstalk_teleport_cases.py --write results/quantum_inspire/cases`)
   and run its `--check`, then
   `"$QI_PYTHON" scripts/qi_toolchain_check.py` to analyze and compile every
   circuit.
4. Write the case: the question, why Aer cannot answer it, the batch list at
   most 3 circuits each, shots (at most 131072; the 300 s limit admits about
   400000 at 0.7 ms, so it binds nothing), the expected noiseless outcome and
   the expected character order (qubit 0 rightmost, to be verified by an
   asymmetric X circuit in the first batch).
5. Run a QX dry run first (the procedure in [qx-runs.md](qx-runs.md)); a QX
   dry run cannot rehearse mid-circuit bits.
6. Wait for the owner's approval and quote it verbatim.
7. Confirm that none of the account's batches is queued on any hardware
   backend: `qi_jobs` or `snapshot`. The FAQ limits a user to 3 queued jobs
   per hardware backend, and `submit` refuses a batch while one of the
   account's batches is queued.
8. For each batch in order: copy it to
   `results/quantum_inspire/runs/<UTC stamp>-<case>-batch-NN/`, then
   `"$QI_PYTHON" scripts/qi_platform.py submit RUN_DIR --backend-type-id 6 --approval "QUOTE"`
   (at most 3 circuits), then
   `"$QI_PYTHON" scripts/qi_platform.py collect RUN_DIR --poll 15 --timeout 3600`,
   then the generator's `--sanity RUN_DIR`, then a pause for calibration to
   pass, and only then the next batch. Stop the series at the first failure;
   never resubmit a directory that holds `submission.json` or
   `submission-state.json` (use `qi_platform.py reconcile`).
9. Analyze with the generator's `--analyze OUT RUN_DIR...`, drop Q8's
   character unless it is the subject, commit the runs with the analysis and
   its `--replay` gate, refresh `usage.json` and register the runs in
   `docs/state/research_state.json` in the same change.

## Unmeasured capabilities and the smallest probe for each

The probes are proposals; none has run.

| Capability | Why it is open | Smallest probe |
|---|---|---|
| Result order on Tuna-9 | measured only on Tuna-17 | `qubit[9] q`, `X q[0]`, `barrier q`, `b = measure q`; the 1 should be the rightmost character |
| Register width below 9 | C15 untested | `qubit[2] q` on Tuna-9 with X on q[0]; accepted or rejected |
| Init time and per-shot cost | 500 or 200 us not assigned | 16384 shots of the order circuit; read `execution_time_in_seconds` per shot |
| Mid-circuit bit in the result | C21 on Tuna | `bit[18] b` with a mid-circuit measure into `b[9]` and a final measure into `b[0:8]`; count characters |
| Angle quantization | pi/36 stated, not observed | `Rx(0.3)` (about 3.44 steps) against `Rx(0.2618)` (3 steps) on one qubit; compare P1 |
| Readout error per qubit | none measured | prepare all-zeros and all-ones in two circuits, 16384 shots each; read P1 per qubit |
| Q8 T1 and decay shape | the TLS message has no numbers | `X q[8]`, `wait(n) q[8]` at five n, measure; compare Q3 on the same schedule |
| Q8 effect on Q6 and Q7 | neighbor inheritance inferred | Ramsey on Q6 and Q7 with Q8 idle versus `X q[8]` repeated, as in the Tuna-17 spectator series |
| Coupler ZZ | measured on Tuna-17 only | the Tuna-17 coupler ZZ map restricted to the 10 non-Q8 couplers |
| Spectator drive additivity | cases generated, never run | `tuna_9/batch-00` verbatim after the first order circuit passes |
| Coherent single-qubit error | Tuna-17 showed over-rotation on Q6, Q8, Q9 | 40 X gates on each of Q0-Q7, read P1 per qubit |
| Teleportation with two paths | cases generated, never run | `tuna_9/batch-01`, edited to avoid Q8 |
| CR, CRk, Rn | accepted by the KB, untested | one circuit per gate on a coupled pair, compiled and run |
| Binary-controlled gate rejection | KB says not allowed | a `c-` style program; the error text |
| Calibration cadence and downtime | no page states one | poll `qi_hardware_status` every 10 minutes for a day |
