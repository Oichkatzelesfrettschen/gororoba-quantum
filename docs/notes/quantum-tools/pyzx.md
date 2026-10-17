# pyzx

## NAME

pyzx 0.10.7 -- ZX-calculus circuit representation, rewriting, T-count
optimization and circuit extraction.

## SYNOPSIS

```python
import pyzx as zx
c = zx.Circuit.from_qasm(qasm_text)       # OpenQASM 2 (and unitary OpenQASM 3)
g = c.to_graph(); zx.simplify.full_reduce(g)
out = zx.extract_circuit(g.copy())        # back to gates
out.to_basic_gates().to_qasm()            # QASM 2 for qiskit.qasm2.loads
zx.compare_tensors(c.to_tensor(), out.to_tensor(), preserve_scalar=False)
```

| Substrate | Status |
| --- | --- |
| Build host | python-pyzx 0.10.7 (Arch) |
| Kaggle | `pyzx==0.10.7` in the `quantum-tools` group; installed at 0.10.7 on the CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` (`pin_groups.json`) |

## CAPABILITIES IN THIS REPOSITORY

- ZX rewriting of algebra circuits. The ISA form of `designs.design_a_associator(1, 2)`
  parses and reports T-count 0 (see the example in [stim.md](stim.md)); a
  graph simplifies with `full_reduce` (spider fusion, local complementation,
  pivoting) and extracts to a Clifford+phase circuit. `tcount` reports the non-Clifford resource; the
  CCZ of the cubic normal form is the T-count benchmark (example: 7 before and
  after).
- CZ-basis input: a Kingston ISA circuit (`sx`, `rz`, `cz`) parses
  (`Circuit.from_qasm` of a Qiskit QASM 2 dump). `rz` angles parse as
  phases; the ISA CCZ reports T-count 7.
- Equivalence checking of small circuits: `compare_tensors` and
  `Circuit.verify_equality` compare tensors up to a scalar; `Circuit.to_matrix`
  gives the unitary for a Qiskit `Operator` comparison (example: deviation 0.0).
- Phase-polynomial optimization: `zx.optimize.phase_block_optimize` and
  `zx.todd` (Third Order Duplicate and Destroy) work on the phase polynomial,
  the same F_2 structure as the ANF masks of `boolean_anf.py`
  ([galois.md](galois.md)). The CCZ stays at 7 T gates under both,
  consistent with the cubic normal form needing one CCZ.
- Not covered: noise, hardware routing (extraction emits arbitrary CZ/CNOT
  connectivity), dynamic circuits.

## API ENTRY POINTS

`pyzx.Circuit`:

`pyzx:Circuit` public names (35), by introspection:

functions:

```text
  add_circuit, add_gate, add_gates, adjoint, col_add, copy, depth,
  from_graph, from_qasm, from_qasm_file, from_qc, from_qc_file,
  from_qsim_file, from_quipper, from_quipper_file, initialize_qubits, load,
  postselect_qubits, prepend_gate, row_add, split_phase_gates, stats,
  stats_dict, tcount, tensor, to_basic_gates, to_emoji, to_graph, to_matrix,
  to_qasm, to_qc, to_quipper, to_tensor, twoqubitcount, verify_equality
```

`pyzx` top-level functions and classes (rewrite rules `unsafe_*`, `check_*`,
`match_*`, `safe_*` and `simp_*` omitted):

`pyzx` public names (270), by introspection:

classes:

```text
  CNOT_tracker, Circuit, EdgeType, GeneticOptimizer, Mat2, Scalar,
  VertexType
```

`pyzx.simplify`, selected simplifiers:

`pyzx.simplify` public names (237), by introspection:

## EXAMPLES

### Qiskit ISA circuit and CCZ through pyzx

```python
import json, sys
sys.path.insert(0, "gororoba_quantum")
import numpy as np
import pyzx as zx
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit.quantum_info import Operator
import calibration_snapshot as cs

view = cs.noise_model(json.load(open("docs/evidence/calibration/ibm_kingston.json")))[0]


def compact(isa, n):
    out = QuantumCircuit(n)
    for inst in isa.data:
        out.append(inst.operation, [isa.find_bit(q).index for q in inst.qubits])
    return out


def deviation(a, b):
    """Max entry difference of two unitaries after removing a global phase."""
    ua, ub = Operator(a).data, Operator(b).data
    k = np.argmax(abs(ua))
    return float(np.abs(ua - ua.flat[k] / ub.flat[k] * ub).max())


ccz = QuantumCircuit(3)
ccz.h(2); ccz.ccx(0, 1, 2); ccz.h(2)
isa = compact(transpile(ccz, view, initial_layout=[0, 1, 2], optimization_level=1, seed_transpiler=1), 3)
print("ISA gates:", dict(isa.count_ops()))

c = zx.Circuit.from_qasm(qasm2.dumps(isa))                   # sx, rz and cz parse
print("pyzx from ISA QASM: T-count", c.tcount(), " gates", len(c.gates))

# gate-level CCZ over the Clifford+T set: the 7-T phase polynomial
cl = transpile(ccz, basis_gates=["cx", "h", "t", "tdg"], optimization_level=0)
cc = zx.Circuit.from_qasm(qasm2.dumps(cl))
g = cc.to_graph()
zx.simplify.full_reduce(g)
out = zx.extract_circuit(g.copy())
print("CCZ Clifford+T: T-count", cc.tcount(), "-> full_reduce", zx.tcount(g), "-> extracted", out.tcount())
print("two-qubit gates: original", cc.twoqubitcount(), "-> extracted", out.twoqubitcount(), " Hadamards:", cc.stats_dict()["had"], "->", out.stats_dict()["had"])
print("tensors equal up to scalar:", zx.compare_tensors(cc.to_tensor(), out.to_tensor(), preserve_scalar=False))
back = qasm2.loads(out.to_basic_gates().to_qasm())
print("extracted circuit vs original CCZ, Qiskit Operator deviation:", round(deviation(cl, back), 12))
opt = zx.optimize.phase_block_optimize(cc)
print("phase_block_optimize T-count:", opt.tcount())
```

Output:

```text
ISA gates: {'sx': 22, 'rz': 21, 'cz': 12}
pyzx from ISA QASM: T-count 7  gates 55
CCZ Clifford+T: T-count 7 -> full_reduce 7 -> extracted 7
two-qubit gates: original 6 -> extracted 13  Hadamards: 4 -> 16
tensors equal up to scalar: True
extracted circuit vs original CCZ, Qiskit Operator deviation: 0.0
phase_block_optimize T-count: 7
```

## INTEROP WITH QISKIT

| Direction | Path | Result |
| --- | --- | --- |
| Qiskit to pyzx | `zx.Circuit.from_qasm(qasm2.dumps(qc))` | works for `rz`, `sx`, `cz`, `h`, `cx`, `t`, `tdg`; verified on the ISA CCZ |
| Qiskit to pyzx, QASM 3 | `zx.Circuit.from_qasm(qasm3.dumps(qc))` | works for a unitary circuit |
| pyzx to Qiskit | `qasm2.loads(out.to_basic_gates().to_qasm())` | works; unitary equal up to a global phase |
| dynamic circuit | via QASM 3 | fails: `TypeError: Phase expression 'c[0]' contains unbound variables` |
| pyzx to quimb | `pyzx.to_quimb_tensor` | listed, not run |

```python
import warnings
warnings.filterwarnings("ignore")
import pyzx as zx
import quimb.tensor as qtn
from qiskit import QuantumCircuit, qasm2, qasm3

qc = QuantumCircuit(2, 2)
qc.h(0); qc.measure(0, 0)
with qc.if_test((qc.clbits[0], 1)):
    qc.x(1)
qc.measure(1, 1)

for label, call in (
    ("qasm2.dumps", lambda: qasm2.dumps(qc)),
    ("pyzx.Circuit.from_qasm(qasm3)", lambda: zx.Circuit.from_qasm(qasm3.dumps(qc))),
    ("quimb from_openqasm3_str", lambda: qtn.Circuit.from_openqasm3_str(qasm3.dumps(qc))),
):
    try:
        call()
        print(label, "accepted")
    except Exception as e:
        print(f"{label}: {type(e).__name__}: {str(e).splitlines()[0][:110]}")

plain = QuantumCircuit(2); plain.h(0); plain.cx(0, 1)
print("pyzx from qasm3 (unitary):", zx.Circuit.from_qasm(qasm3.dumps(plain)).stats().splitlines()[0].strip())
print("quimb from qasm3 (unitary): N =", qtn.Circuit.from_openqasm3_str(qasm3.dumps(plain)).N)
```

Output:

```text
qasm2.dumps: QASM2ExportError: 'OpenQASM 2 only supports register-equality conditions'
pyzx.Circuit.from_qasm(qasm3): TypeError: Phase expression 'c[0]' contains unbound variables
quimb from_openqasm3_str: NotImplementedError: The following instruction is not supported: if (c[0]) {
pyzx from qasm3 (unitary): Circuit  on 2 qubits with 2 gates.
quimb from qasm3 (unitary): N = 2
```

## CPU AND GPU

CPU, single-threaded Python. No GPU path.

## TRAPS

- `full_reduce` then `extract_circuit` need not reduce gate count: in the CCZ
  example the extraction has more two-qubit gates and Hadamards than the
  input (printed above); the graph form wins on T-count, not on depth.
- Extracted two-qubit gates have no connectivity constraint; transpile the
  result to the Heron coupling map again.
- `extract_circuit` mutates its graph; pass `g.copy()`.
- A circuit built from `Circuit.from_qasm` on a 156-qubit register keeps all
  156 wires; compact the register first.
- `compare_tensors` allocates 2^n x 2^n tensors; it is a small-circuit check.
- ZX simplification preserves a unitary up to a global scalar; Hadamard-test
  controlled blocks must carry their relative phase explicitly
  (root AGENTS.md, "Signs, workspace and measurement basis").

## LICENSE

Apache-2.0.
