# Quantum Inspire guides

Quantum Inspire (QuTech, TU Delft and TNO) is the repository's second
hardware provider. These guides cover the account, the machines, their
limits, the toolchain and the experiments run on them; the root AGENTS.md
section "Quantum Inspire" carries the binding rules and the gated backend
table. The live pages at <https://www.quantum-inspire.com/kbase/> and the
account's catalogue stay the authority, because both change without notice:
refresh the catalogue with
`"$QI_PYTHON" scripts/qi_platform.py snapshot --out docs/evidence/quantum_inspire`
and the captures with `"$PYTHON" scripts/capture_qi_docs.py`.

| Guide | Content |
|---|---|
| [setup.md](setup.md) | the Python 3.13 environment and its lock, OAuth device login, the `qi` CLI command map, REST, SDK, Qiskit, PennyLane and hybrid routes, result bit order |
| [backends.md](backends.md) | one constraint sheet per machine, emulator and processor alike: qubits, couplings, gate sets, durations, angle grid, shots, run-time limits, compiler passes, bit order, measured cost |
| [usage.md](usage.md) | the transaction ledger and what it charged, structural limits, measured seconds per job and shot, queue rules, calibration and maintenance, the conditions of use |
| [platform-facts.md](platform-facts.md) | every fact the knowledge-base capture establishes, each with its source: per-backend constraints, retired backends, calibration, maintenance, account rules, tooling |
| [experiments.md](experiments.md) | the Tuna-17 spectator-drive, teleportation and zero-divisor runs, their analyses and the Kingston-noise comparison |
| [mcp.md](mcp.md) | the `quantum-inspire` MCP server: tools, permissions, registration |
| [cqasm.md](cqasm.md) | a working cQASM 3.0 reference with per-backend support |
| [knowledge-base.md](knowledge-base.md) | a digest of every captured page, its link audit and the reconciled contradictions between pages, API and runs |
| [citing.md](citing.md) | how to cite Quantum Inspire, its backends and tools, with BibTeX from registration records |
| [release-notes.md](release-notes.md) | platform and component release history, newest first, with the backend timeline |
| [cli-reference.md](cli-reference.md) | the `--help` of every quantuminspire 4.1.0 `qi` command |
| [requirements-qi.txt](requirements-qi.txt) | the full environment lock |

## Captured sources

`scripts/capture_qi_docs.py` keeps each source under a header naming its
URL, retrieval time and digest, with `MANIFEST.json` in each directory;
gate core-346 rechecks every byte offline.

| Directory | Source |
|---|---|
| [site/](site/) | every page of quantum-inspire.com reachable from the knowledge-base sidebar, footer and body links, with code examples as fenced cQASM |
| [cqasm-spec/](cqasm-spec/) | the cQASM 3.0 specification site at a pinned commit |
| [sdk/](sdk/) | the quantuminspire, qiskit-quantuminspire and pennylane-quantuminspire documentation at pinned release commits |
| [releases/](releases/) | GitHub and GitLab release notes of every component the release-notes page links |
| [api/](api/) | the compute job manager OpenAPI description |

## Evidence and records

- [docs/evidence/quantum_inspire/](../../evidence/quantum_inspire/): the
  account catalogue and usage ledger snapshot, which retains no team,
  member or user identifier in any form.
- [results/quantum_inspire/](../../../results/quantum_inspire/): generated
  cases under `cases/` and every submitted run under `runs/`, each with its
  circuits, digests, receipt, raw shots, results and analysis.
- [docs/state/RESEARCH_STATE.md](../../state/RESEARCH_STATE.md): the
  Quantum Inspire acquisitions and claims beside the IBM ones.
