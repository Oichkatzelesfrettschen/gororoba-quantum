# qiskit-mitigation

## NAME

qiskit-mitigation 0.1.1 -- error-mitigation tasks (TREX, PEC, PEA, ZNE with
gate folding) that build a `QuantumProgram` for the runtime `Executor` and
post-process its results.

## SYNOPSIS

```python
from qiskit_mitigation import TREX, PEC, PEA, GateFolding, MitigationTask
```

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit-mitigation 0.1.1 (Arch) |
| Kaggle | `qiskit-mitigation==0.1.1` in the `quantum-tools` group (`scripts/kaggle_run.py` `PIN_GROUPS`); one of the seven pins added to the group after the retained CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu`, whose `pin_groups.json` records the twelve earlier members only; not yet installed on a kernel |

## CAPABILITIES IN THIS REPOSITORY

Per the class docstrings (read from the installed source, not run):

- `TREX`: mitigates readout error in expectation values with the Twirled
  Readout Error eXtinction method, adding a readout-calibration item to a
  `QuantumProgram` shared by one or more mitigation tasks.
- `PEC` and `PEA`: probabilistic error cancellation and amplification.
- `GateFolding`: zero-noise extrapolation by gate folding.
- `MitigationTask`: the base class that prepares a `QuantumProgram` and
  post-processes `Executor` results.
- All of them target the hardware `Executor`; they were not run because an
  executor call contacts IBM. This is the readout-mitigation route for hardware
  jobs, while [mthree.md](mthree.md) and qiskit-experiments mitigators work
  on counts.
- docs/notes/ibm_heron_platform.md notes that fractional gates support TREX and not Pauli
  twirling, PEC or PEA.

## API ENTRY POINTS

`qiskit_mitigation` public names (12), by introspection:

classes:

```text
  GateFolding, MitigationTask, PEA, PEC, TREX
```

functions:

```text
  find_combined_unique_layers, load_tasks_from_result
```

modules:

```text
  mitigation_task, pec, trex, utils, zne
```

## EXAMPLES

Introspection only (names above). No example runs: the tasks need the
runtime `Executor`.

## INTEROP WITH QISKIT

Qiskit `QuantumCircuit` and `SparsePauliOp` observables in; runtime
`QuantumProgram` out. Not run.

## CPU AND GPU

CPU client code.

## TRAPS

- Using it submits jobs and consumes QPU time; it falls under the
  approved-case rule of the root AGENTS.md.
- Version 0.1.1 is an early release; check the docstrings before relying on
  signatures.

## LICENSE

Apache-2.0.
