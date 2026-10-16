# qiskit-qasm3-import and openqasm3

## NAME

qiskit-qasm3-import 0.6.0 -- the OpenQASM 3 importer behind
`qiskit.qasm3.loads`; openqasm3 1.0.1 -- the OpenQASM 3 parser and AST.

## SYNOPSIS

```python
from qiskit import qasm3
qc = qasm3.loads(text)        # needs qiskit_qasm3_import
text = qasm3.dumps(qc)        # exporter is part of qiskit
import openqasm3
ast = openqasm3.parse(text)   # AST: ast.statements
```

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit-qasm3-import 0.6.0 and python-openqasm3 1.0.1 (Arch) |
| Kaggle | not installed by KERNEL_PINS or the `quantum-tools` group: it is the `qasm3-import` extra of qiskit and appears in no hard requirement of the group's packages (host package metadata). A kernel that calls `qasm3.loads` needs it added (gap; see the README) |

## CAPABILITIES IN THIS REPOSITORY

- Reading dynamic circuits: mid-circuit `measure`, `if (c[0]) { ... }`,
  classical bits and gate calls import into `if_else` instructions.
- Exchange format for stim output (`Circuit.to_qasm(open_qasm_version=3)`) and
  for retained circuits; physical qubits (`$2`) round trip through Qiskit.
- AST inspection with `openqasm3.parse` for tools that need the statements
  (statement class names are printed in the example).
- Not covered: pulse-level `defcal`, which the importer does not turn into
  hardware control and which IBM removed on 3 February 2025.

## API ENTRY POINTS

`qiskit_qasm3_import` public names (11), by introspection:

classes:

```text
  ConversionError
```

functions:

```text
  convert, parse
```

modules:

```text
  api, converter, data, exceptions, expression, state, types
```

other:

```text
  VERSION_PARTS
```

`openqasm3` public names (9), by introspection:

functions:

```text
  dump, dumps, parse
```

modules:

```text
  ast, parser, printer, properties, spec, visitor
```

## EXAMPLES

```python
import importlib.metadata as md
import openqasm3
from qiskit import qasm3

print("qiskit-qasm3-import", md.version("qiskit-qasm3-import"), " openqasm3", md.version("openqasm3"))
src = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
if (c[0] == true) { x q[1]; }
c[1] = measure q[1];
"""
try:
    qasm3.loads(src.replace("== true", "== 1"))
except Exception as e:
    print("bit == int condition:", type(e).__name__, e)
qc = qasm3.loads(src)                      # parsed by qiskit_qasm3_import through the openqasm3 AST
print([(i.operation.name, [qc.find_bit(q).index for q in i.qubits]) for i in qc.data])
print("ops:", dict(qc.count_ops()))
prog = openqasm3.parse(src)
print("openqasm3 AST statements:", [type(s).__name__ for s in prog.statements])
print(qasm3.dumps(qc).splitlines()[-6:])
try:
    qasm3.loads("OPENQASM 3.0;\nqubit q;\nfrobnicate q;\n")
except Exception as e:
    print("unknown gate:", type(e).__name__, str(e).splitlines()[0][:100])
```

Output:

```text
qiskit-qasm3-import 0.6.0  openqasm3 1.0.1
bit == int condition: QASM3ImporterError "8,4: conditions must be 'bit == const bool' or 'bitarray == const int', not 'bit == const int'"
[('h', [0]), ('measure', [0]), ('if_else', [1]), ('measure', [1])]
ops: {'measure': 2, 'h': 1, 'if_else': 1}
openqasm3 AST statements: ['Include', 'QubitDeclaration', 'ClassicalDeclaration', 'QuantumGate', 'QuantumMeasurementStatement', 'BranchingStatement', 'QuantumMeasurementStatement']
['h q[0];', 'c[0] = measure q[0];', 'if (c[0]) {', '  x q[1];', '}', 'c[1] = measure q[1];']
unknown gate: QASM3ImporterError "3,0: gate 'frobnicate' is not defined."
```

## INTEROP WITH QISKIT

This is the Qiskit interop layer. Other tools' QASM 3 acceptance (measured on
this host): pyzx accepts a unitary QASM 3 circuit and rejects a dynamic one
(`TypeError: Phase expression 'c[0]' contains unbound variables`); quimb's
`from_openqasm3_str` rejects physical qubits and `if` blocks; stim emits QASM 3
for unitary and measure operations only ([stim.md](stim.md), [pyzx.md](pyzx.md),
[quimb.md](quimb.md)).

## CPU AND GPU

CPU, pure Python.

## TRAPS

- Conditions must compare a bit to a boolean (`c[0] == true`) or a register
  to an integer: `if (c[0] == 1)` fails with `conditions must be 'bit ==
  const bool' or 'bitarray == const int', not 'bit == const int'`
  (verbatim in the example).
- An undefined gate fails with `gate 'frobnicate' is not defined.`
- `qasm3.dumps` writes `if (c[0])` for a bit condition; the form differs from
  the accepted `== true` spelling but loads.
- `QuantumCircuit.draw` text output uses non-ASCII box characters and has no
  `encoding` argument (`TypeError: QuantumCircuit.draw() got an unexpected
  keyword argument 'encoding'`); the examples print operation and qubit lists
  from `circuit.data` for checked-in text.

## LICENSE

Apache-2.0 (both).
