# Simulation cost: planner, ghost replay and the packages that move it

A submit-free `live_run.py` dry run, its `--submit` re-plan and a ghost
replay of a retained run all spend their time in local simulation of the
same Aer noise model. This note decomposes where that time goes, names
the package interface and the setting that remove each part, and records
which candidates were measured and rejected. QPU seconds belong to
[qpu_run_economy.md](../qpu_run_economy.md).

## Planner stages

| Stage | Function | Needs the network | Feeds the decision | Share before serialization reuse |
|---|---|---|---|---|
| discovery | `live_run.discover_snapshots`, `take_snapshot` | yes | eligibility, exclusions, calibration identity | under 1 % |
| candidates and compile | `qpu_planning.family_candidates`, `live_run._compile` | no | layouts, routed circuits, QPY bytes | under 1 % |
| planning simulation | `qpu_planning.prepare` -> `simulate_choice` -> `local_compute.run` | no | predicted laws for every candidate | 60 % |
| ideal validation | `ideal_compiled_probabilities` against each entry's oracle | no | refuses a miscompiled circuit | under 1 % |
| contracts, budget, selection | `qpu_planning` admission, `budget_plan` | no | shots, ceilings, the selected design | under 1 % |
| evaluation simulation | `live_run.evaluate` -> `simulate` | no | the record's fresh-seed predictions | 40 % |
| record | record.json, isa.qpy, UNAPPROVED_CASE.md | no | the digest the approval names | under 1 % |

Shares come from `py-spy record --subprocesses --idle -r 50 --format raw`
over one 151-group state-prep-control dry run, main-thread samples only.
Simulating one qubit for 32768 shots costs microseconds; each Aer call
spent seconds on the whole 156-qubit model: `NoiseModel.to_dict` plus a
JSON round trip (1.28 s), the C++ controller reading every qubit's errors
under the GIL (about 0.6 s), and a dill pickle of the RelaxationNoisePass
Target from `PassManager.run` on an empty list.

## The seed rule that fixes the batching boundary

Aer 0.17.2 seeds circuit `k` of one run as `seed_simulator + 2113 k`
(`src/controllers/controller_execute.hpp`, lines 203-224). Planning calls
`local_compute.run` once per choice, so each choice's first circuit draws
from `SEED_SIMULATOR`, and merging choices into one batch changes every
later choice's counts. A speedup that keeps the record bits keeps one Aer
call per choice and makes that call cheap.

## What removes the cost

| Interface | Setting or rule | Removes | Bits kept | Gate |
|---|---|---|---|---|
| `local_compute.SerializedNoiseSimulator` | one `to_dict` per configured model and process; the empty noise-pass run skipped | per-call serialization | yes | core-548 |
| restricted serialization with opset witnesses | each Delay-free batch gets the errors on its qubits plus the first error restoring each missing instruction name and the readout type | C++ assembly of unused qubits | yes: the controller reads the model globally only through `is_ideal`, `has_quantum_errors`, `has_nonlocal_quantum_errors` and the opset, and a statevector batch takes Kraus sampling when the opset holds kraus or superop | core-548, whose negative control drops the witnesses and changes a reset batch |
| nonlocal guard | a model with a nonlocal error runs unrestricted | a restriction that would drop the error | yes | core-548 |
| one simulator per pool thread and snapshot | `AerSimulator.from_backend` once per thread | about 30 ms of GIL-held Target conversion per build | yes | core-548 |
| submit-time reuse | `live_run.reuse_approved_predictions` when every planning input equals the approved record's | the whole re-plan at `--submit` | yes: the reused predictions are the record's | core-549 |
| `snapshot_laws.restrict_circuit` with `restrict(snapshot, qubits)` | circuit and model at the active width before any standalone Aer run | the full-width model on a 7-qubit circuit | counts change with the qubit labels; use it where a record's own draws are not replayed | none |
| `parallel.ordered_map` | spawn pool, items carry keys and circuit bytes, each worker caches one model per key | GIL contention between thread lanes | yes, order-preserving | per caller |
| Aer `max_parallel_experiments=0` | inside one batched call only | serial experiments of one call | yes: seeds are positional | none |

Measured on the build host: the offline 145-qubit state-prep-control dry
run fell from 1161 s to 65-73 s with all 580 batches bit-identical, and a
submit-free 146-qubit ibm_kingston dry run took 45 s of wall time against
11 minutes before.

## Dynamic circuits: sample or compute the law

Measured on the n21 feedback PUB of `results/live/2026-10-18T090603.530638Z`
(7 active qubits, 713 CZ, one mid-circuit measurement, reset and if_else)
under the ibm_kingston snapshot 20261015T2035330700, CPU, host load near 20:

| Route | Cost | Scales with shots |
|---|---|---|
| Aer statevector trajectories, full-width model | over 36 ms per shot: 10,000 shots ran past 6 minutes | yes |
| Aer statevector, `restrict_circuit` and `restrict` | 3.4 ms per shot, 340 s per 100,000-shot PUB | yes |
| Aer density_matrix, restricted | 181 ms per shot | yes |
| `dynamic_density.probabilities`, restricted | 8.0 to 8.4 s per PUB, 1.2 s more for the model | no |

The exact law plus `numpy.random.Generator(PCG64(seed)).multinomial(shots,
law)` replaces sampling in a ghost replay of a run whose record keeps no
Aer-drawn counts for that member (`scripts/ghost_run.py`, dynamic members
at 32768 shots or more). Planning under `--model-method exact` takes its
predictions from the law but still runs `--model-shots` of Aer sampling per
choice: `n21_exact_planning.exact_predictions` retains those frequencies
and rejects a law that leaves their sampling radius, so the sampled pass
stays the falsifier and its cost stays in the plan. `dynamic_density`
agrees with Aer's density-matrix method to 1.2e-15 on the cleaned noise
model and to 1.06e-9 on the raw calibration model, whose small error
components Aer truncates (gate core-487,
docs/notes/numerics_best_practice.md). Its cost grows with 4^n in the active qubits and
with the number of distinct recorded values, so it serves 7-qubit dynamic
circuits in seconds and wide one-qubit families not at all; a wide
one-qubit family is a batch of independent 2 x 2 laws instead.

## Ghost refresh: ghost only what coverage lacks

A ghost replay holds every retained run under every retained calibration
of its backend, so one new run or one new snapshot extends the grid by a
row or a column; it never requires rerunning the whole grid.

| Interface | Setting or rule | Removes | Gate |
|---|---|---|---|
| `ghost_calibrations.py --add` | indexes only the audited jobs `index.json` lacks, read-only IBM reads plus the export check against live_run's channels | a full calibration re-export | core-560 |
| `ghost_run.py --merge RESULT` | ghosts the (run, snapshot) pairs RESULT lacks, one pair per `parallel.ordered_map` item; a run whose inputs changed (`stale`) is ghosted again in full and its replaced entry's sha256 recorded | the full replay of every retained run | core-561 |
| `ghost_run.py --provenance RESULT BASE` | RESULT without its `merged` runs and pairs equals the kernel's BASE byte for byte | trust in a merged file the kernel never wrote | core-293 |
| `ghost_run.py --check --runs ...,merged` | replays the execution-snapshot ghost of every run a merge added, bit for bit on the merge's Aer device | an unreplayed merged run | core-287 |
| exact law at `EXACT_MIN_SHOTS` or more | dynamic members draw from `dynamic_density`'s restricted law and a PCG64 multinomial at the position's Aer seed | per-shot density-matrix evolution of a 100,000-shot PUB | core-561 |
| `max_parallel_experiments=0` (`PARALLEL_EXPERIMENTS`) | Aer runs one call's experiments in parallel | serial members of one snapshot | core-287 |

Measured on the build host: five 2026-10-18 Kingston runs and one new
Kingston snapshot took 2 min 20 s for `--add` and 7 min for `--merge`
(54 pairs, 346 % CPU, 1.0 GB RSS), where the retained Kaggle ghost spent
4207 s of T4 simulation on the first 14 runs. The pairs a merge adds to
already retained runs are not yet replayed in CI ([issue #274](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/274)).

## Candidates measured or rejected

| Candidate | Version | Verdict |
|---|---|---|
| qiskit-ibm-transpiler AI routing, local inference | 0.18.0 (qiskit-gym 0.4.2, torch 2.14.1) | no gain on n21: on the 7-qubit ibm_kingston tree it routed the 320-CX unitary part to 798 CZ against 786 to 799 for qiskit's own optimization level 3 over three seeds; live_run's search reaches 713 on the full circuit. It imports `qiskit.synthesis.linear.linear_matrix_utils`, which qiskit 2.5 removed, and raises CircuitError on any circuit carrying a classical register |
| JAX through `jax_bridge.make_jax_evolver` | jax 0.9.0 | complex64 storage; batches terminal-measurement programs of one structure (error-scale sweeps); `dynamic_density` stays on complex128 numpy |
| numba | 0.68.0 | `dynamic_density`'s einsum per operation is the only hot loop, and 8 s per PUB already fits a ghost refresh |
| stim | 1.16.0 | Pauli channels only; the model carries thermal relaxation and asymmetric readout |
| quimb, cotengra | 1.15.0, 0.8.2 | tensor networks pay at widths a 7-qubit density matrix never reaches |
| GPU (T4 on Kaggle, RTX 4070 Ti locally) | qiskit-aer-gpu 0.17.2 | slower per shot than the CPU on 7-qubit dynamic circuits (54.6 against 36 ms, docs/notes/kaggle/substrates.md) |
| Aer shot branching | 0.17.2 | drops a mid-circuit measurement's readout channel; never enabled |
| orjson | unpinned | serializing once removes the JSON cost |

## Falsifiers

- core-548 fails if any planned or evaluated distribution differs from the
  stock Aer path, or if dropping the witnesses leaves the reset batch
  unchanged.
- core-549 fails if a stubbed submit with unchanged values sends other PUB
  bytes than the full path, or if a changed calibration value fails to
  write `approval_required`.
- The exact-law route is wrong for a circuit if core-487's comparison
  with Aer's density-matrix method exceeds its tolerance on that circuit's
  instruction set, or if a planning law leaves the sampling radius of its
  own Aer-drawn frequencies.
