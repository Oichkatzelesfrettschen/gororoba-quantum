# Provider environments and MCP servers

Each provider guide holds the backend table, API behavior, gates and run
procedure; the live provider pages stay the authority because they change.
Every job, upload, notebook session and provider QRNG read waits for the
user's approved written case (root [AGENTS.md](../../AGENTS.md#hardware-services)).
Tokens, keys, key-file locations, MCP registrations, account state and access
limits are recorded in the private gororoba-infrastructure repository, never
in this one.

- Quantum Inspire: [quantum_inspire/README.md](quantum_inspire/README.md);
  interpreter `QI_PYTHON` (Python 3.13 venv `QI_ENV`); MCP `quantum-inspire`.
- Open Quantum: [open_quantum/README.md](open_quantum/README.md);
  interpreter `OQ_PYTHON` (venv `OQ_ENV`); MCP `openquantum`; key file named by
  `OPENQUANTUM_SDK_KEY`.
- Quandela Cloud: [quandela/README.md](quandela/README.md);
  Perceval on the system Python, `QD_PYTHON` for the MCP server; MCP `quandela`;
  token file named by `QUANDELA_TOKEN_FILE`.
- IQM Resonance: [iqm/README.md](iqm/README.md);
  interpreter `iqm-python` of the iqm-resonance-stack package; MCP `iqm`; token
  pair file named by `IQM_TOKENS_FILE`.
- qBraid: [qbraid/README.md](qbraid/README.md); interpreter `QB_PYTHON`; hosted
  MCP `qbraid` ([mcp.md](qbraid/mcp.md)).
- Kaggle: [kaggle/README.md](kaggle/README.md); hosted MCP `kaggle`.
- IonQ, BlueQubit, Quafu and Origin Quantum: one guide each under
  `docs/notes/<provider>/` (`ionq`, `bluequbit`, `quafu`, `originquantum`),
  interpreters `IONQ_PYTHON`, `BQ_PYTHON`, `QF_PYTHON` and `OG_PYTHON`; no MCP
  server. Planck's account is closed, and [its guide](planck/README.md) keeps the
  source audit.
- QRNG seed sources: [qrng/README.md](qrng/README.md).
- IBM Quantum: [ibm_quantum/account-access.md](ibm_quantum/account-access.md);
  no MCP server.
