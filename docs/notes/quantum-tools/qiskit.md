# qiskit

## NAME

qiskit 2.5.2 -- circuits, Targets, the transpiler, `quantum_info`, OpenQASM
2/3 import and export.

## SYNOPSIS

```python
from qiskit import QuantumCircuit, transpile, qasm2, qasm3
from qiskit.quantum_info import Operator, Statevector, Clifford, SparsePauliOp
isa = transpile(circuit, backend_v2, initial_layout=[...], optimization_level=1, seed_transpiler=1)
```

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit 2.5.2 (Arch) |
| Kaggle | `qiskit==2.5.2` in `KERNEL_PINS`, installed by every kernel |

## CAPABILITIES IN THIS REPOSITORY

- CZ-basis ISA circuits. Transpiling against the Target rebuilt from
  `docs/evidence/calibration/ibm_kingston.json` (`calibration_snapshot.noise_model(snapshot)[0]`
  is a `BackendV2` carrying only that Target) yields `rz`, `sx`, `cz` (and `x`);
  the example shows the operation counts by optimization level for a CCZ.
  Pin `seed_transpiler` and `initial_layout` to make the result replayable.
- Exact references: `Operator(qc)` and `Statevector(qc)` give the ideal
  unitary and state of up to roughly 14 qubits on the host; every package
  manual in this directory compares against them.
- Clifford identification: `qiskit.quantum_info.Clifford(qc)` raises
  `QiskitError` on a non-Clifford gate, a quick test before sending a circuit
  to [stim.md](stim.md).
- Dynamic circuits: `QuantumCircuit.if_test`, `while_loop`, `switch`, `store`,
  `Reset`, mid-circuit `measure`. The snapshot Target lists `if_else` under
  `omitted_operations`, so `transpile` against it rejects control flow
  (example in [qiskit-ibm-runtime.md](qiskit-ibm-runtime.md)); Heron r2 limits are in
  docs/notes/ibm_heron_platform.md "Execution facts".
- QASM exchange with the other tools: QASM 2 for unitary circuits into
  [quimb.md](quimb.md) and [pyzx.md](pyzx.md); QASM 3 into stim's output and
  `qasm3.loads` ([qiskit-qasm3-import.md](qiskit-qasm3-import.md)).
- Little-endian ordering: qubit 0 is the least significant bit of a counts key
  and of `Statevector.data`'s index (docs/notes/algebra_circuit_rules.md, "Encoding and
  representation").

## API ENTRY POINTS

`qiskit` public names (32), by introspection:

classes:

```text
  AncillaRegister, ClassicalRegister, MissingOptionalLibraryError,
  QiskitError, QuantumCircuit, QuantumRegister
```

functions:

```text
  generate_preset_pass_manager, transpile
```

modules:

```text
  capi, circuit, compiler, converters, dagcircuit, exceptions, importlib,
  os, passmanager, primitives, providers, qasm2, qasm3, qiskit, qpy,
  quantum_info, result, synthesis, sys, transpiler, user_config, utils,
  version, visualization
```

`qiskit.quantum_info` public names (60), by introspection:

classes:

```text
  CNOTDihedral, Chi, Choi, Clifford, DensityMatrix, Kraus, Operator, PTM,
  Pauli, PauliLindbladMap, PauliList, PhasedQubitSparsePauli,
  PhasedQubitSparsePauliList, Quaternion, QubitSparsePauli,
  QubitSparsePauliList, ScalarOp, SparseObservable, SparsePauliOp,
  StabilizerState, Statevector, Stinespring, SuperOp, Z2Symmetries
```

`qiskit.transpiler` public names (39), by introspection:

classes:

```text
  AnalysisPass, CircuitTooWideForTarget, ConditionalController,
  CouplingError, CouplingMap, DoWhileController, InstructionDurations,
  InstructionProperties, InvalidLayoutError, Layout, LayoutError,
  OptimizationMetric, PassManager, PassManagerCliffordTConfig,
  PassManagerConfig, PropertySet, QubitProperties, StagedPassManager,
  Target, TransformationPass, TranspileLayout, TranspilerAccessError,
  TranspilerError, WrapAngleRegistry
```

## EXAMPLES

```python
import json, sys
sys.path.insert(0, "gororoba_quantum")
import qiskit
from qiskit import QuantumCircuit, qasm2, qasm3, transpile
from qiskit.quantum_info import Clifford, Operator, Statevector
import calibration_snapshot as cs

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
view = cs.noise_model(snap)[0]
t = view.target
print("qiskit", qiskit.__version__, "| target qubits", t.num_qubits, "| operations", sorted(t.operation_names))
print("dt", t.dt, " timing granularity", t.granularity, " min_length", t.min_length)

qc = QuantumCircuit(3)
qc.h(2); qc.ccx(0, 1, 2); qc.h(2)
for level in (0, 1, 3):
    isa = transpile(qc, view, initial_layout=[0, 1, 2], optimization_level=level, seed_transpiler=1)
    print(f"optimization_level={level}: {dict(isa.count_ops())}")

tq = QuantumCircuit(1); tq.t(0)
try:
    Clifford(tq)
except Exception as e:
    print("Clifford(T):", type(e).__name__, e)

isa = transpile(qc, view, initial_layout=[0, 1, 2], optimization_level=1, seed_transpiler=1)
print(qasm2.dumps(isa).splitlines()[:4])
print(qasm3.dumps(isa).splitlines()[:4])
back = qasm3.loads(qasm3.dumps(isa))
print("qasm3 round trip with physical qubits:", back.num_qubits, "qubits,", dict(back.count_ops()))
```

Output:

```text
qiskit 2.5.2 | target qubits 156 | operations ['cz', 'delay', 'id', 'measure', 'reset', 'rz', 'sx', 'x']
dt 4e-09  timing granularity 1  min_length 1
optimization_level=0: {'rz': 39, 'sx': 28, 'cz': 12}
optimization_level=1: {'sx': 22, 'rz': 21, 'cz': 12}
optimization_level=3: {'sx': 20, 'rz': 15, 'cz': 10}
Clifford(T): QiskitError 'Cannot update Clifford with non-Clifford gate t'
['OPENQASM 2.0;', 'include "qelib1.inc";', 'qreg q[156];', 'rz(pi/2) q[2];']
['OPENQASM 3.0;', 'include "stdgates.inc";', 'rz(pi/2) $2;', 'sx $2;']
qasm3 round trip with physical qubits: 3 qubits, {'sx': 22, 'rz': 21, 'cz': 12}
```

## INTEROP WITH OTHER TOOLS

| Tool | Path verified on this host | Where |
| --- | --- | --- |
| stim | gate-name table (Clifford) and `to_qasm(open_qasm_version=3)` back | [stim.md](stim.md) |
| quimb | `qasm2.dumps` then `from_openqasm2_str` | [quimb.md](quimb.md) |
| pyzx | `qasm2.dumps` / `qasm3.dumps` then `Circuit.from_qasm`; `qasm2.loads` back | [pyzx.md](pyzx.md) |
| mthree | Aer backend from the snapshot; `final_measurement_mapping` | [mthree.md](mthree.md) |
| qiskit-experiments | experiments run on the snapshot `AerSimulator` | [qiskit-experiments.md](qiskit-experiments.md) |

## CPU AND GPU

qiskit itself runs on the CPU (transpiler passes are Rust or Python).
Simulation on the GPU belongs to [qiskit-aer.md](qiskit-aer.md).

## TRAPS

- `qasm2.dumps(isa)` on a 156-qubit Target circuit writes `qreg q[156]`; compact the
  register before importing it into tools that allocate one site per qubit.
- `qasm3.dumps(isa)` writes physical qubits as `$2`; `qasm3.loads` reads them
  back (3 qubits in the example), quimb's importer does not.
- The snapshot Target reports `granularity` 1 and `min_length` 1 and omits
  `measure_2`, `reset_2`, `measure_reset`, `xslow` and control flow
  (`omitted_operations`); it is a noise-modeling input, and the live Target is
  the timing authority (docs/notes/ibm_heron_platform.md).
- `Statevector` and `Operator` memory is 2^n and 4^n complex numbers; do not use
  `Operator` above about 12 qubits.
- `optimization_level` 3 reduced the CCZ's `cz` count from 12 to 10 in the
  example; compare compiled counts, not nominal gates, when quoting a cost
  (the ccz-reduction evidence does this with level 3 and seed 11).

## LICENSE

Apache-2.0.
