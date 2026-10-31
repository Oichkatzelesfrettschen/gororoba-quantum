# Provider environments, MCP servers and key files

Each provider guide holds the environment, credential handling, MCP
registration, backend table, limits, gates and run procedure; the live provider
pages stay the authority because they change. Tokens and keys live outside every
checkout and never enter a commit, log or memory. Every job, upload, notebook
session and provider QRNG read still waits for the user's approved written case
(root [AGENTS.md](../../AGENTS.md#hardware-services)).

- Quantum Inspire: [quantum_inspire/README.md](quantum_inspire/README.md);
  interpreter `QI_PYTHON` (Python 3.13 venv `QI_ENV`); MCP `quantum-inspire`;
  tokens in `~/.quantuminspire/config.json` through `qi login`.
- Open Quantum: [open_quantum/README.md](open_quantum/README.md);
  interpreter `OQ_PYTHON` (venv `OQ_ENV`); MCP `openquantum`; key file named by
  `OPENQUANTUM_SDK_KEY` (`~/.config/openquantum/sdk-key.json`).
- Quandela Cloud: [quandela/README.md](quandela/README.md);
  Perceval on the system Python, `QD_PYTHON` for the MCP server; MCP `quandela`;
  token file named by `QUANDELA_TOKEN_FILE`.
- IQM Resonance: [iqm/README.md](iqm/README.md);
  interpreter `iqm-python` of the iqm-resonance-stack package; MCP `iqm`; token
  pair file named by `IQM_TOKENS_FILE`.
- IonQ, BlueQubit, Quafu and Origin Quantum: one guide each under
  `docs/notes/<provider>/` (`ionq`, `bluequbit`, `quafu`, `originquantum`),
  each with a pinned venv under `~/.local/share/<provider>/venv` and a
  one-line key file under `~/.config/<provider>/`; no MCP server. Planck's
  account is closed, and [its guide](planck/README.md) keeps the source audit.
