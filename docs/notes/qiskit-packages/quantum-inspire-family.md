# quantuminspire, qiskit-quantuminspire and pennylane-quantuminspire

The Quantum Inspire family takes circuits to Tuna-17. Three packages form it:
- **quantuminspire 4.2.0**: the SDK and `qi` CLI, for login, jobs and
  results.
- **qiskit-quantuminspire 0.18.6**: the Qiskit provider
  (`qiskit_quantuminspire.qi_provider.QIProvider`) and its cQASM 3 exporter.
- **pennylane-quantuminspire 0.15.6**: a PennyLane `QIDevice`, and
  `pennylane_quantuminspire.cqasm.dumps`, which exports a QNode through
  pennylane-qiskit to cQASM 3.

All three require Python below 3.14. qiskit-quantuminspire caps qiskit
below 2.4, and pennylane-qiskit caps it at 2.3.0. They therefore live in two
Python 3.13 environments with qiskit 2.3.0, Aer 0.17.2 and the
qiskit-ibm-runtime 0.45.1 that pennylane-qiskit pulls:

| Environment | Launcher | Notes |
|---|---|---|
| `/opt/quantuminspire-qiskit-stack` (Arch package, pkgrel 2) | `qi-stack-python`, `qi-stack` | hash-locked; libqasm 1.2.1 rebuilt with SWIG 4.5.1; four offline tests: versions, provider namespace, Qiskit cQASM export, PennyLane QNode export |
| `QI_ENV`, `~/.local/share/quantuminspire/venv` | `QI_PYTHON` | the repository's provider interpreter; PyPI libqasm 1.2.1, whose SWIG 4.3.1 build segfaults on import under `-W error::DeprecationWarning` and imports normally otherwise |

[docs/notes/quantum_inspire/README.md](../quantum_inspire/README.md) holds
credentials, the MCP server, the batch pause and the queue limits.

## Connections

- The cQASM 3 that both exporters produce is the format that
  `CQASMConverter` of [perceval-interop](perceval-interop.md) reads, so one
  circuit can reach both Tuna-17 and a Perceval processor.
- The qiskit 2.3.0 ceiling holds the stack apart from the system qiskit
  2.6.1; a circuit crosses between them as cQASM or QPY.
- PennyLane enters the host only here. qiskit-ecosystem.md lists pennylane
  as declined for the core, and that decision stands.
