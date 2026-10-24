# Quantum Inspire guides

Quantum Inspire (QuTech, TU Delft and TNO) is the repository's second
hardware provider. These guides cover the account, the machines, their
limits, the toolchain and the experiments run on them; the section
"Binding rules" below carries the binding rules and the gated backend
table. The live pages at <https://www.quantum-inspire.com/kbase/> and the
account's catalogue stay the authority, because both change without notice:
refresh the catalogue with
`"$QI_PYTHON" scripts/qi_platform.py snapshot --out docs/evidence/quantum_inspire`
and the captures with `"$PYTHON" scripts/capture_qi_docs.py`.

| Guide | Content |
|---|---|
| [tuna_zz_map.md](tuna_zz_map.md) | conditional-Ramsey design, frozen proposal and submission-source-bound successor; acquisition remains deferred |
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
| [mcp.md](mcp.md) | the `quantum-inspire` MCP server: tools, permissions, registration and [public Grafana status and calibration dashboards](mcp.md#public-performance-dashboards) |
| [cqasm.md](cqasm.md) | a working cQASM 3.0 reference with per-backend support |
| [knowledge-base.md](knowledge-base.md) | a digest of every captured page, its link audit and the reconciled contradictions between pages, API and runs |
| [citing.md](citing.md) | how to cite Quantum Inspire, its backends and tools, with BibTeX from registration records |
| [release-notes.md](release-notes.md) | platform and component release history, newest first, with the backend timeline |
| [cli-reference.md](cli-reference.md) | the `--help` of every quantuminspire 4.1.0 `qi` command |
| [requirements-qi.txt](requirements-qi.txt) | the full environment lock |

## Captured sources

`scripts/capture_qi_docs.py` keeps each source under a header naming its
URL, retrieval time and digest, with `MANIFEST.json` in each directory;
gate `core-record-check-05` (`tests/test_cli_record_checks.py`) rechecks every byte offline.

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

## Binding rules

Quantum Inspire (QuTech, TU Delft and TNO) is a hardware service the
repository reaches with one free account type that has access to every listed
hardware and emulator backend.

**Environment.** The quantuminspire SDK requires Python < 3.14 and
qiskit-quantuminspire caps Qiskit below 2.4, so the Quantum Inspire stack
lives in its own environment, never in the repository's Python 3.14 stack:
`QI_ENV=$HOME/.local/share/quantuminspire/venv`, interpreter
`QI_PYTHON=${QI_PYTHON:-$QI_ENV/bin/python}`, built with
`uv venv --python 3.13 "$QI_ENV"` and
`VIRTUAL_ENV="$QI_ENV" uv pip install -r docs/notes/quantum_inspire/requirements-qi.txt`.
No Arch package carries the stack. CI's `qi-stack` job installs the lock
exactly (`pip install --no-deps` and `pip check`) under Python 3.13.15 beside
Python 3.14.7 and exports `QI_PYTHON`; there qxelarator, libqasm and
OpenSquirrel run locally with no credential, and no SDK call reaches the
network. gororoba_quantum/qi_stack.py reads `QI_PYTHON` from the environment
alone and probes it once per process for the three modules at the lock's
versions. A gate tagged `"requires": ["qi"]` compares a live run with its
retained record where that probe passes; everywhere else (the gate shards,
premerge, a shell that has not exported `QI_PYTHON`)
it replays the record and prints one line naming the replay.
`ci/run_gates.py --requires qi` runs the tagged gates alone with
`GOROROBA_QI_REQUIRED=1`, which makes a replay a failure.

| Package | Version | Role |
|---|---|---|
| quantuminspire | 4.1.0 | `qi` CLI, `quantuminspire.api.Api`, OAuth device login |
| qi-compute-api-client | 0.63.0 | generated client of the compute job manager REST API |
| qiskit-quantuminspire | 0.18.5 | `QIProvider`, Qiskit backends, cQASM writer (per-qubit barriers) |
| qiskit | 2.3.1 | the newest release below the provider's < 2.4 cap; the repository runs 2.6.0 |
| opensquirrel | 0.9.1 | compiler: decomposition, mapping, routing, ALAP scheduling |
| libqasm | 1.2.1 | cQASM 3.0 parser and analyzer |
| qxelarator | 0.10.0 | local QX state-vector emulator |
| mcp | 2.3.0 | MCP server SDK for scripts/qi_mcp_server.py |

pennylane-quantuminspire 0.15.5 (PennyLane >= 0.43, < 0.46) is not
installed. The community bridge quantum-vibecoding-mcp 0.1.0 imports
quantuminspire 3.x and mcp 1.x modules absent from these pins and is not
used; scripts/qi_mcp_server.py serves the same role on SDK 4.1.

**Login.** `"$QI_ENV/bin/qi" login` runs the OAuth device flow: it prints a
verification URL and code that the user approves in a browser, then stores
access and refresh tokens in `~/.quantuminspire/config.json`, which the CLI
writes mode 644; `chmod 600` it after login, and scripts/qi_platform.py's
client narrows it to mode 600 before reading it. The
access token lives 3600 s; scripts/qi_platform.py renews it before expiry.
The SDK exchanges the refresh token only within 5 s of access-token expiry,
and its `refresh_tokens` keeps the rotated tokens in memory only. Every
process on the account read invalid_grant after one such expiry (2026-10-17,
two sessions and several MCP servers live); rotation with reuse detection is
the inferred mechanism, unconfirmed by a probe. `Client.refresh` therefore
holds an flock on `~/.quantuminspire/config.json.lock`, rereads the file,
exchanges only near expiry and writes the rotated tokens back atomically. A
long-lived process (an MCP server) started before that rule restarts before
QI work resumes.
An agent that finds no login prompts the user to run `qi login` and approve
the code; tokens never enter a commit, a log or memory. An invalid_grant
needs `qi login --force`, since plain `qi login` cannot recover it;
[setup.md](setup.md#login-failures) holds the triage table by error text,
the paths that spend a login and the exchange log that tells them apart.

**Backends.** `scripts/qi_platform.py snapshot --out docs/evidence/quantum_inspire`
reads the account's catalogue and ledger; gate core-347 renders this table
from the retained catalogue and fails when either changes alone:

<!-- quantum-inspire-facts:begin -->
| Backend type (id) | identifier | is_hardware | qubits | couplings | shots default / max | job limit (s) | jobs per batch | batch jobs queued |
|---|---|---|---|---|---|---|---|---|
| QX emulator (1) | QXsinglenodesimulator | false | 10 | 45 | 1024 / 2048 | 3600 | 5 | 5 |
| Tuna-5 (4) | tuna_5 | true | 5 | 4 | 8192 / 131072 | 300 | 5 | 5 |
| Ry emulator (5) | Rydberg | true | 9 | 36 | 1024 / 1024 | 3600 | 5 | 5 |
| Tuna-9 (6) | tuna_9 | true | 9 | 12 | 8192 / 131072 | 300 | 5 | 5 |
| Tuna-17 (7) | tuna_17 | true | 17 | 24 | 8192 / 131072 | 300 | 5 | 5 |

Backend instances: QX emulator (Cloud), Spin-2+ (TU Delft), Starmon-7 (TU Delft), Tuna-5 (TU Delft), Ry emulator (TU/eindhoven), Tuna-9 (TU Delft), Tuna-17 (TU Delft).
<!-- quantum-inspire-facts:end -->

The last two columns are the API's mechanical ceilings, not an allowance:
on hardware the FAQ's 3 queued jobs governs ([usage.md](usage.md#queue-rules-the-faq-governs)).

Status, queue length and heartbeat change between reads and live only in the
snapshot. Spin-2+ and Starmon-7 appear as backend instances without a backend
type this account can submit to.

**Execution facts.**
- Tuna: native single-qubit gates last 20 ns, CZ 60 ns, measurement 800 ns,
  initialization 200 or 500 us; H, CNOT and SWAP are decomposed, the other
  gates of the tuna dialect are native; rotation angles quantize to
  multiples of pi/36; the compiler passes decompose only, so a circuit runs
  in the gate order written; OpenSquirrel schedules as late as possible,
  `wait(n)` idles n cycles of 20 ns, and mid-circuit measurement is allowed
  while binary-controlled gates are not, so feed-forward is applied in
  post-processing ([tuna-17-run-design.md](tuna-17-run-design.md)).
- Bit order: QX and Tuna results put qubit 0 at the rightmost character; the
  Ry emulator puts it at the leftmost (an X on q[0] read `10` in all 1024
  shots). An analysis states the order of the backend it reads.
- The Ry emulator takes no measurement statements and measures every qubit
  at the end; a circuit that declares a bit register compiles remotely and
  fails at execution with the job message "error interpreting cQASM script"
  (its log stays empty), while H, CNOT, Z, S and Rz run in a circuit without
  one ([ry-emulator.md](ry-emulator.md)).
- The Qiskit provider writes a multi-qubit barrier as per-qubit barriers, so
  a timing-sensitive case writes cQASM directly with explicit `wait`.

**Usage and cost.** The account's transaction ledger (`/transactions/`,
`qi_platform.py snapshot` writes usage.json) recorded no entry for the
forty-two jobs of 2026-10-16 on QX, the Ry emulator and Tuna-17, so no metered seconds
or credits apply to this account as observed; the limits are structural: the
table's qubits, shots, per-job execution limit and batch and queue counts,
plus the FAQ's three queued jobs per hardware backend, which is stricter than
the API's five batch jobs. No provider page sets an interval between
submissions; [usage.md](usage.md#what-the-provider-requires) quotes every
provider rule with its page and capture line. Tuna-17 execution time fits 2.6 s per job plus
0.53 ms per shot over the retained jobs, so a 16384-shot job takes about 11 s
and the account pause and the shared queue, not the shots, set a batch's cost; QX finished 2048
shots in 0.03 to 10.4 s.
Calibration and tuning run between user jobs (Tuna-17 read `calibrating`
between two reads minutes apart), delay queued jobs and charge the account
nothing. The general conditions license every uploaded algorithm, datum and
code to QuTech for its own and third-party use, so nothing confidential is
submitted.

**Submission.** A Quantum Inspire hardware or emulator submission waits for
the user's approval of a written case, like an IBM run, though it spends no
metered quota. `"$QI_PYTHON" scripts/qi_platform.py submit CASE_DIR
--backend-type-id N --approval TEXT` verifies every circuit against its
cases.json digest, refuses an offline backend or a limit breach, records the
approval in submission.json and sends one batch; `collect CASE_DIR` writes
the raw shots, job records and charged transactions. On hardware a batch
holds at most three circuits and goes in only when none of the account's
batches is queued, so at most three jobs are ever queued (the FAQ's limit
under either reading of "job"; [usage.md](usage.md#queue-rules-the-faq-governs)
holds the rule, and the FAQ governs over the API's 5 and 5); a series runs a QX dry run first, then
submits each hardware batch only after the previous one is collected, passes
its sanity checks and a pause. `submit` also refuses a hardware batch while
any job of the account on a hardware backend type (`is_hardware`, whichever
session submitted it) is unfinished or finished less than
`HARDWARE_PAUSE_SECONDS` ago, so sessions that share the account
alternate. The pause is a repository rule: 30 s by default, raised to 60, 90
and then 120 s after a platform failure ([usage.md](usage.md#pause-escalation));
QX emulator batches skip the check, while the Ry emulator, which the API flags
`is_hardware`, takes it. The case generators emit each experiment as
a series of `batch-NN/` cases within that limit, and
`scripts/check_qi_platform_retention.py` passes every generated batch through
submit's checks up to the first request. Runs live under
results/quantum_inspire/runs/. A question about the Tuna devices themselves
(their crosstalk, coherent error, readout) is a hardware question; any
simulation of 14 qubits or fewer still runs on Kaggle.

**MCP.** scripts/qi_mcp_server.py, registered at user scope as
`quantum-inspire` for Claude Code and `quantum_inspire` for Codex, serves
catalogue, queue, hardware status, usage ledger, jobs, results and local
qxelarator emulation as read tools and asks before qi_compile (creates remote
resources) and qi_submit_case (executes through the retained-case runner).
The legacy raw-string qi_submit refuses execution. Failures return isError with the
service's message.

**Gates.** `core-record-check-05` (`capture_qi_docs.py --check`), core-347
(`qi_platform.py check docs/evidence/quantum_inspire --agents docs/notes/quantum_inspire/README.md`),
`core-record-check-05` (`qi_crosstalk_teleport_cases.py --check results/quantum_inspire/cases`),
core-331 (`--replay` of every retained analysis.json), core-348 and core-330
(`qi_zero_divisor_cases.py --check` and `--replay`), core-332 and core-333
(`qi_coupler_zz_map.py` case regeneration with conformance, and the replay of
the coupler map, its QX dry run and the spectator split), core-362
(`qi_readout_ringdown_cases.py` case regeneration with the post-readout
tail and excitation conformance), core-369 (the replay of its QX dry-run
analyses), core-368 (`qi_toolchain_check.py --check`: the libqasm and
OpenSquirrel record names every current case circuit at its sha256, and
under the stack the record regenerates byte for byte), core-527 and core-423
(`box_kite_qx_sweep.py --replay --live N`: the sweep records replay, and
under the stack 24 evenly spaced family a circuits plus each sub-family's
first rerun on qxelarator at their recorded seeds and must reproduce the
retained counts exactly; core-423 adds 8 family de circuits on the full tier),
core-499 (`n21_qx_conformance.py --check --live 0`: under the stack every
reset probe, deferred state and native branch run reruns on qxelarator at its
retained seed and must equal the retained result; each of the 36 sample jobs
takes minutes, so `--live N` adds N of them by hand and `--live 36` all), and
core-340 (`qi_ibm_noise_replay.py --check`, the Kingston-noise replay of
the Tuna-17 cases).
