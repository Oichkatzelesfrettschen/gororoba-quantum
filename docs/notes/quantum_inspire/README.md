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
| [qx-runs.md](qx-runs.md) | what a QX result contains (the measurement register, by qubit), the root cause and its consequences, and the procedures for a local qxelarator run, a remote QX dry run and a QX run |
| [ry-emulator.md](ry-emulator.md) | the Ry emulator: the neutral-atom model and why the API flags it hardware, geometry against the all-to-all topology, gate set and what the compiler does to each gate, qubit-0-leftmost result order, limits and cost, the measured "error interpreting cQASM script" failure, the procedure for a run, and unmeasured capabilities with probes |
| [tuna-9.md](tuna-9.md) | Tuna-9: live status, adjacency and bipartition, the facts shared with every Tuna backend, the Q8 two-level system and which designs exclude it, the absence of any retained run, which generators emit Tuna-9 cases, the procedure for a run once online, and unmeasured capabilities with probes |
| [backends.md](backends.md) | one constraint sheet per machine, emulator and processor alike: qubits, couplings, gate sets, durations, angle grid, shots, run-time limits, compiler passes, bit order, measured cost |
| [usage.md](usage.md) | the transaction ledger and what it charged, structural limits, measured seconds per job and shot, queue rules, calibration and maintenance, the conditions of use |
| [shot-record-literature.md](shot-record-literature.md) | the registered flux-CZ, control-stack, shot-record noise and readout-crosstalk sources for the Tuna-17 periodic line and context-dependent state-1 misassignment: what each establishes, where the literature stops, and the measurement each candidate mechanism invites |
| [platform-facts.md](platform-facts.md) | every fact the knowledge-base capture establishes, each with its source: per-backend constraints, retired backends, calibration, maintenance, account rules, tooling |
| [tuna-17.md](tuna-17.md) | Tuna-17 result registers, the retained record of its readout drift, the readout ring-down verdicts and the runner and account rules the series established |
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
