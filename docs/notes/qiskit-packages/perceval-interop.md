# perceval-quandela and perceval-interop

perceval-quandela 1.3.1 (`python-perceval-quandela`, with exqalibur 1.4.2)
is the photonic framework that the Quandela Belenos and Ascella work uses
([docs/notes/quandela/README.md](../quandela/README.md)). perceval-interop
1.3.1 (`python-perceval-interop`) converts other circuit formats into
Perceval processors:
- `QiskitConverter`, `StatevectorConverter` and `CircuitToGraphConverter`
  from Qiskit;
- myQLM's `MyQLMConverter`;
- `CQASMConverter` from cQASM through libqasm;
- a QuTiP bridge.

perceval-interop 1.3.1 defines `MyQLMCommunicationLayer` only when myQLM is
installed, while its package `__init__` imports the name unconditionally.
`import perceval_interop` therefore fails on every host without myQLM. The
Arch package (pkgrel 2) adds the missing `MissingDependency` placeholder in
`prepare()`. Its setup.py derives the version through scmver from git
metadata, which the sdist lacks, so the wheel would report 0.0.0;
`prepare()` substitutes the release version, and pkgrel 3 reports 1.3.1.
The Qiskit converter then turns a two-qubit H-CX circuit into a
four-mode processor on the host.

The upstream `qiskit` extra pins `qiskit~=2.1.2`, which excludes the
system's qiskit. The converter runs regardless, and the package declares
Qiskit as an optdepend rather than enforcing the pin (README Open item 2).

## Connections

- Perceval runs on the system interpreter. The Quandela MCP server runs on
  `QD_PYTHON`.
- `CQASMConverter` needs libqasm 1.2.1. The rebuilt libqasm of the
  [Quantum Inspire stack](quantum-inspire-family.md) sits in that stack's
  environment and does not reach the system interpreter.
- A converted circuit re-enters the Belenos transpiler, which re-transpiles
  every submission. Only the processor that the platform reports is the
  circuit that ran.
