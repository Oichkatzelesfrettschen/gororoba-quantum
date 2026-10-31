# gororoba-quantum agent guide

This file carries the repository's own rules and overrides the user-level
guide where they differ. CLAUDE.md loads it. [docs/README.md](docs/README.md)
maps every document, [docs/PYTHON.md](docs/PYTHON.md) holds the interpreter
and dependency inventory, and [ci/AGENTS.md](ci/AGENTS.md) holds the gate
machinery.

## Layout and gates

- The modules run as scripts from gororoba_quantum/ and form no installable
  package.
- The `pr.yml` checks `lint`, `types`, `tests` and `gates` green on the head
  admit a merge. No local gate run or premerge replay is required before a
  push, which overrides the user-level guide's local replica of the slowest
  CI lanes; `sh ci/pr_checks.sh tests PATH` runs touched tests under the
  hosted environment.
- Before each push, every touched Python file passes through
  `"$PYTHON" ci/pinned_tool.py` for ruff format, ruff check and mypy
  ([ci/AGENTS.md](ci/AGENTS.md#code-style-tools)).
- Python starts with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` in
  local shells too; the combined Qiskit Rust and Aer OpenMP extensions
  require it.
- Every CPU-bound loop over independent items runs through parallel.py, and
  a serial loop over such items is a defect review rejects. Items that share
  a seeded generator draw every input first, then map. A batched replicate
  estimator keeps the scalar arithmetic bits
  ([vectorized-fits](docs/runbooks/vectorized-fits.md)).
- Every command whose cost or correctness depends on its options (solvers,
  simulators, Python pools, compilers, cloud launchers, resource limiters)
  runs only after the review in
  [compute-flags](docs/runbooks/compute-flags.md).
- Mock outcomes (`--native-dry-run` timing) never enter scientific analysis
  or measured visualizations.
- A change to live_run.py or experiments.py also gets a dry run,
  `"$PYTHON" live_run.py --out ../results/live`.
- A change to `proofs/`, a replay bundle or its receipts follows the Rocq
  replay of [ci/AGENTS.md](ci/AGENTS.md#layout-and-gates).

## Seeds

Every new random seed, on any provider or simulator, comes from a quantum
random number generator: a numpy or `random` generator seed,
`seed_transpiler`, `seed_simulator`, a Perceval `compilation_seed`, a
bootstrap or null-calibration seed. The ANU QRNG serves first
(`"$PYTHON" scripts/anu_qrng.py draw --out docs/evidence/anu_qrng`);
[docs/notes/qrng/README.md](docs/notes/qrng/README.md) holds the fallback
order, quotas, key files and approval rule of every source. The code or case
cites the draw file and the index of every value it takes, in index order,
each value used once. A seed that reproduces a retained record, an approved
plan or a known compiled mesh is an identifier and keeps its value, because
the record's replay and the approved-record comparison depend on it. The seed
follows the job's question, not the circuit: a job that reproduces an earlier
result imports the earlier seed constant by name, and a new job on an earlier
circuit that needs its own randomness takes new values from a draw. A CLI
seed goes through `qrng_seeds.add_seed_argument`.
`ci/seed_provenance.py`, run by the `tests` check, enforces the ledger
([ci/AGENTS.md](ci/AGENTS.md#seed-ledger)).

## Grounding and algebra

Never guess or estimate hardware specifications, timing budgets, algebraic
conventions or mathematical invariants; import or validate against the
registered repository artifact (`docs/notes/ibm_quantum/`,
[ibm_heron_platform](docs/notes/ibm_heron_platform.md),
`docs/evidence/heron_platform/targets.json`, `proofs/`).

- `a -> L_a` is a linear encoding, never an algebra homomorphism.
- `|0>` is `e_0 = 1`, the identity, never the zero vector. A zero product is
  a heralded branch of zero probability while the full state keeps norm 1.
- Algebra index bit `b` sits on register qubit `b` (little-endian, as in
  Qiskit outcome strings).
- A sign register needs `|->` for phase kickback; `|0>` records a which-path
  label.
- Certify every zero-divisor pair with `cd_core` before circuit work.
  `gororoba_quantum/cd_core.py` is the specification, and a package result
  enters evidence only through a declared map onto it, checked on every
  basis pair.
- A hardware probe of an algebraic property passes the mutation test (the
  ideal observable changes when the property is removed), lists its arms +,
  -, -, + and decides against a null arm
  ([Hardware probes](docs/notes/algebra_circuit_rules.md#hardware-probes)).
- The account reaches ibm_fez, ibm_kingston and ibm_marrakesh, all Heron r2:
  156 qubits, heavy-hex, basis cz, id, rz, sx, x and xslow. The live Target
  is the timing authority (dt 4 ns), and `service.backends()` precedes naming
  a backend. IBM removed pulse-level control on 3 February 2025.
- Exact replays compute in global monomial orderings only
  ([computer-algebra](docs/runbooks/computer-algebra.md)).

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- The default saved account is primary. A second saved account named
  `backup-ibm-quantum-platform` holds a different IBM Cloud instance with its
  own 600 s rolling quota, and quotas never pool. `GOROROBA_IBM_ACCOUNT`
  selects the account for every script (unset or empty selects the default)
  and stays the same for a case's dry run, `--submit` and `--collect`.
- Routing. A simulation of 14 qubits or fewer runs on Kaggle kernels through
  `scripts/kaggle_run.py` ([docs/notes/kaggle/README.md](docs/notes/kaggle/README.md)),
  each notebook session under an approved written case (see Hardware
  services). A 15-qubit run waits for the user's approval of a written case
  naming its substrate (an optimized Aer run on the build host or a Kaggle
  T4 x2, or Tuna-17 through Quantum Inspire) and why that one answers the
  question. IBM hardware serves 16 or more qubits, or a smaller run whose
  question concerns the device itself; its case states why Aer cannot answer
  it.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. The binding dry run and `--submit` run back to back as
  `sh scripts/approved_run.sh --check CMD -- FLAGS`. A fresh plan that
  differs from the approved record writes an `approval_required` record and
  sends nothing ([qpu-submission](docs/notes/ibm_quantum/qpu-submission.md)).
- Calibration is a property of the run. live_run.py fetches each backend's
  Target and properties afresh in the process that decides, compiles,
  simulates and submits, and no calibration value is cached or read back
  from a file to drive a submission. Calibration reads, transpilation, local
  noise simulation, result retrieval and `--preserve-raw` need no approval.

## Hardware services

- Every job on a provider (QPU, emulator, simulator or mock), every Kaggle or
  other provider notebook session, every upload, every timeslot booking and
  every provider QRNG read waits for the user's approval of a written case:
  what it measures, why a simulation cannot answer it, the backend, shots,
  expected seconds and expected credits. The free ANU and Outshift QRNG draws
  need none, per the QRNG guide above; a local noise simulation needs none. A
  Quantum Inspire hardware batch also keeps its pause and queue limits, and
  Open Quantum Public Compute makes every uploaded circuit and result public
  and non-confidential (the upload in `prepare_job` is itself the
  publication), so unpublished methods stay off it.
- An account-wide queue grants no authority to cancel another worker's job;
  acquisition decision statements and cancellation authority follow
  [evidence-closure](docs/runbooks/evidence-closure.md).
- Tokens and keys live outside every checkout and never enter a commit, log
  or memory. Provider environments, MCP names and key files:
  [providers](docs/notes/providers.md).

## Qiskit skills

Run `/migrate-qiskit-ibm-runtime` with scope gororoba_quantum/ on any change
that touches qiskit-ibm-runtime (primitives, options, jobs, service,
backends, sessions or batches), on any change to its pin in requirements.txt
and after every monthly skill update
([qiskit-skills](docs/runbooks/qiskit-skills.md)).

## Records

- Raw files under `raw/<job_id>/` are never rewritten by a later collection
  or analysis. A retained run enters docs/state/research_state.json, with a
  claim citing it and a refreshed ledger or inventory, in the change that
  retains it ([results-index](docs/runbooks/results-index.md)).
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`. Account identifiers are credentials, account
  and instance ids, CRNs and email addresses. A public platform handle (the
  GitHub owner in every repository URL, the Kaggle username in a kernel or
  dataset slug `owner/slug`) names published work, and records keep it so
  `collect` and `status` resolve the kernel.
- External-only sources (`redistribution: excluded_without_permission`) go
  only to the owner's private repository gororoba-quantum-documents, never
  into this tree ([docs/README.md](docs/README.md#source-cache-and-reading-copies)).

## Documents

[docs/README.md](docs/README.md) is the map and decides where a document
lives; read it before writing one.

- Extend before adding. A fact has one home; a second area that needs it
  gets a link, and a deduplication merges the fact up to the nearest home
  every reader reaches, never into sibling copies.
- A new document gets its map row or an inbound link in the same change;
  `scripts/check_markdown_links.py` fails on a broken link or anchor.
- Retained bytes are immutable: a file a ledger, record or digest binds keeps
  its path and bytes, and a correction lands in a new document that the old
  one's map row links.
- A move runs through `git mv` and updates every reference, ledger and gate
  in the same change. Session-local scratch stays in the ignored `docs/local/`.
- JSON plan records own work status; run `scripts/plan_tracker.py check`
  ([plan-tracker](docs/runbooks/plan-tracker.md)).
- An AGENTS.md holds rules a session cannot derive from the tree, kept short;
  reference tables, procedures and measurements live in the docs they
  describe, with a pointer.

## Reviews and merges

- Codex is the only hosted reviewer, and it reviews only on request: the
  operator posts the issue comment `@codex review` right after opening a PR
  and after every push that needs review. Copilot reviews are billed to the
  owner, so no pull request requests one; when the Codex app reports
  exhausted code-review quota, the owner decides how the PR proceeds.
- Reply to each thread's root comment beginning `Fixed in <commit>`,
  `Refuted:` followed by the refuting source line, or `Boundary:` followed by
  the documented limit and the follow-up issue, then run
  `scripts/resolve_answered_threads.sh PR`. Never resolve a thread whose
  finding has not been read and answered.
- Merge with a merge commit (`merge_method=merge`), which overrides the
  user-level guide's squash option. Merge stacked PRs bottom-up, and retarget
  the next PR to main before deleting a merged base branch, because deleting
  a base closes every PR that targets it. The full loop is in
  [codex-review-loop](docs/runbooks/codex-review-loop.md).
