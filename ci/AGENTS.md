# CI and gate guide

This file applies to the pull-request workflow, the audit's gate machinery
under ci/, and the replay and cost rules of the audit. The repository's root
AGENTS.md carries the short form of the code-style commands and the merge
flow; CLAUDE.md loads this file.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only.

**Pull requests.** [.github/workflows/pr.yml](../.github/workflows/pr.yml)
runs on every pull-request push and on `workflow_dispatch`, cancels the run a
newer push replaces, and holds four jobs that call
[ci/pr_checks.sh](pr_checks.sh) with its environment (loader TLS, one thread
per native library, `GOROROBA_PINS_REQUIRED=1`):
- `lint` installs the Ruff pin of ci/requirements-ci.txt and runs `ruff check`
  and `ruff format --check` over ci/, tests/, gororoba_quantum/, scripts/ and
  kaggle_kernel/;
- `types` runs mypy over the same directories from gororoba_quantum/;
- `tests` runs `pytest -n auto --dist loadgroup -m "not audit"` over tests/
  under a 4-minute step timeout and writes the 25 slowest tests to the job
  summary;
- `gates` diffs the head from its merge base with main and runs, through
  `ci/run_gates.py --affected-by`, every gate of at most 15 measured seconds
  (`GATES_MAX_SECONDS`) the diff reaches: a changed path in the gate's import
  closure, at or under a path its command names, in a full-tier gate's
  ci/full_gate_inputs.json scopes, or in the read set main's audit ledger
  traced for it, where an added or removed non-Python file also reaches a
  listed directory, glob or existence probe (`gate_inputs.affected`). It
  restores the replay runtime and the gate ledger from ci.yml's caches
  read-only and builds the runtime on a miss; slower gates stay with the
  audit.
`lint`, `types` and `tests` time out at 8 minutes and `gates` at 30.
`types`, `tests` and `gates` restore the pinned venv through
.github/actions/pins-venv, under ci.yml's cache key, and build it with
ci/install_pins.sh on a miss. Branch protection on main requires `lint`, `types` and `tests`
green on the head, for administrators too, without requiring the branch to
be current with main. A pull request that `GITHUB_TOKEN` opened starts no
`pull_request` workflow, so its author dispatches pr.yml on the branch
(scripts/qd_schedule_tick.sh does so when a schedule finishes); a branch whose
pr.yml predates `workflow_dispatch` gets its checks from merging main into it
and pushing. With the Codex
review loop the checks admit a merge
([Merging](../AGENTS.md#reviews-and-merges)); a local gate run, premerge
replay or Rocq replay is never a merge requirement. Locally,
`sh ci/pr_checks.sh tests tests/path/test_x.py` runs one module under the
hosted environment, and `sh ci/pr_checks.sh tests -m audit tests/path/test_x.py`
runs its audit-marked tests (pytest keeps the last `-m`). Each lane first
resolves its interpreter through `ci/pins.py lane LANE`: an explicit `PYTHON`
runs only when it holds the lane's pins (ruff for lint, every current pin for
types and tests), an unset one takes the host environment, and a drifted one
exits 2 naming the differing pins and the command that runs the lane under
the host environment.

**The audit.** `ci.yml` runs on its nightly schedule and on manual dispatch
only: every gate of both tiers on main with `--ledger-audit`, the
retained-evidence replays, the Rocq replays and the Quantum Inspire stack.
After a scheduled run, job `audit-issue` opens or comments on the issue
"Nightly audit failing" with the body [ci/audit_report.py](audit_report.py)
writes: each failing gate from the shard timing records beside the claims of
docs/state/research_state.json that cite it, and each failing job. A cited
claim is qualified until its gate passes again; the next all-green scheduled
run closes the issue. An audit failure blocks no unrelated pull request.
A branch's affected
gates run on request, `git diff --no-renames --name-only -z origin/main HEAD >
CHANGED` then `"$PYTHON" ci/run_gates.py --changed-files CHANGED`, or by
dispatching ci.yml on the branch. A gate over 30 s of measured wall sits in
the full tier with its non-imported inputs declared in
ci/full_gate_inputs.json, so `--changed-files` selects it when its own inputs
change and the nightly run covers the reads the tracer cannot see.

The numerical-model gates `core-600`, `core-603`, `core-605`, `core-612`,
`core-616`, `core-619` and `core-620` each select a distinct synthetic pytest
regression in `tests/scripts/test_n21_model_regressions.py`. Gate `core-615`
includes the same tests in the behavioral suite. These tests exercise model
laws, endpoint decisions and prospective geometry using synthetic counts and
parameters. The tests neither read historical run reports nor refit historical
acquisitions; their research-state role is regression rather than replay.

**Code style.** Every Python file a change touches passes, before each push:
- `ruff format --target-version py313` (formatting: 120-column lines from
  pyproject.toml, with the Python 3.13 target the shared modules keep for the
  Quantum Inspire interpreter);
- `ruff check` (lint: pycodestyle, pyflakes, import order, bugbear,
  pyupgrade, and S101, so checks raise explicitly instead of asserting);
- `mypy` (static type checking against the configuration in pyproject.toml):
  on the touched files, and over gororoba_quantum/, scripts/, ci/, tests/ and
  kaggle_kernel/ (from gororoba_quantum/: `mypy . ../scripts ../ci ../tests
  ../kaggle_kernel`) when a change alters a function, class or type
  signature another module imports, since a per-file run never reads the
  unchanged callers.
Run them through `"$PYTHON" ci/pinned_tool.py TOOL ARGS`, which uses the
versions ci/requirements-ci.txt pins. Formatting is only ruff format; mypy
checks types and ruff check catches defects, and neither rewrites code.

GitHub Actions ran every gate ([.github/workflows/ci.yml](../.github/workflows/ci.yml)).
[ci/gates.json](gates.json) lists each gate as one command with its
working directory; [ci/run_gates.py](run_gates.py) runs a shard of them on
a thread pool sized to the runner's CPUs and keeps going past failures, so a
red shard lists every failing gate. Shards are assigned longest-first by
occupied CPU-slot seconds: the measured wall seconds of
[ci/gate_timings.json](gate_timings.json) (`ci/merge_gate_timings.py`
folds shard `--timings` records into it, tests/ci/test_gate_timings.py holds
it to the manifest) times each gate's allocated slots, and the manifest estimate for
an unmeasured gate.
The stable `--shard-cpus` profile defaults to the recorded four-CPU runner;
actual gate concurrency follows each runner's detected allocation. Every
event runs twelve shards. Pull requests and pushes to main run the `pr` tier
and affected `full` gates; nightly and manual runs execute every gate. The changed-path selection follows
local Python imports and the dynamic data/source scopes in
[ci/full_gate_inputs.json](full_gate_inputs.json). Every full gate declares
its non-imported inputs there, including source digests and JSON-selected
raw evidence; a missing declaration fails selection. CI and dependency-pin
changes and an unavailable diff base select every gate, and the gate ledger
(Gate cost below) then skips each selected gate whose key is unchanged.
The import closure resolves against the files `git ls-files --cached --others
--exclude-standard` lists (`gate_inputs.checkout_files`), the modules a CI
clone of the same tree holds, so an ignored tree never widens it. Disposable
build trees, task virtual environments, package caches and probes belong in
the system temporary directory, normally `/tmp`, so temporary-file cleanup
can reclaim them. Keep durable code, evidence and documentation in the
repository. Never create task repositories or scratch stores in
`~/.local/share`. Preserve existing shared provider environments and credentials.
Gate seconds are scheduling estimates, independent of tier membership.
[CI runtime analysis](../docs/runbooks/ci-runtime.md) records the timing
denominators, measured bottlenecks and replay commands. Runner-spec logs
record the allocation; the retained audit measured four affinity CPUs and
about 16 GB on ubuntu-latest. CI uses Ubuntu 26.04, retains an Ubuntu 24.04 compatibility job, and pins
Node 24 action commits. Jobs use Python 3.14.7
with the pins in requirements.txt and ci/requirements-ci.txt (mypy, ruff and
the plotting-only `matplotlib==3.11.2`). The `qi-stack` job applies the same changed-input selection to the gates
that ci/gates.json
tags `"requires": ["qi"]`, under the Quantum Inspire interpreter
([Quantum Inspire](../docs/notes/quantum_inspire/README.md#binding-rules)). The
`external-ground-truth` job runs `verify.py` over the open_gororoba commit
named in [ci/open_gororoba.pin](open_gororoba.pin):
`ci/fetch_open_gororoba.sh` sparse-checks out the paths it is given, and
`scripts/materialize_gororoba_csv.py` rewrites the git-ignored `data/csv`
files from the registry records, whose sha256 pins `verify.py` rechecks. A
pin bump is a reviewed commit. A new contract lands as a test function
under tests/ (Behavioral suite below); a new evidence replay joins the gate
list in ci/gates.json in the same change.
The lint and type gates (core-000, core-001, core-002, core-039) cover
gororoba_quantum/, scripts/, ci/ and kaggle_kernel/ whole, so a module there
is linted and type-checked without a list edit; a checked file elsewhere in
the tree, such as an evidence replay under results/ or docs/, is named in
those gates' commands. They run ruff and mypy through
`ci/pinned_tool.py TOOL ARGS`, which uses the installed tool when it reports
the ci/requirements-ci.txt pin and otherwise runs the pinned release through
uv: ruff through `uv tool run`, mypy layered over `"$PYTHON"`'s
site-packages, so a host mypy run type-checks against that host's packages
(qiskit 2.5.2 on the build host against CI's 2.6.0).

Gate commands invoke `"$PYTHON"`. ci/run_gates.py sets it to its own
interpreter when the environment leaves it unset, and assigns
`GOROROBA_WORKERS=1` to ordinary gates when the caller leaves the cap unset.
An explicit worker cap also bounds gates that request the full allocation. A gate command run outside run_gates.py
needs `PYTHON` exported (`export PYTHON="${PYTHON:-python3}"`): a variable
assigned without `export` expands empty in the child shell, and every gate
then exits 127 in 0.0 s with `/bin/sh: line 1: : command not found`, which
reads as a gate failure.


The runner expands `runtime_contracts.CONTRACT_CASES` into independently sharded
cases. CPU slots cover outer gates and inner process pools together: ordinary
gates reserve one slot, while manifest `"workers": "all"` gates reserve the
detected allocation. Native BLAS, OpenMP, Rayon and Qiskit subprocess defaults
stay at one inside each slot. `OPENBLAS_CORETYPE` defaults to Haswell and
`NPY_DISABLE_CPU_FEATURES` caps numpy's dispatch at x86-64-v3, the kernel sets
every runner and build host executes, so a fitted value rounds one way on all
of them given one libm and Python build. A record a gate byte-replays is
written in the runner's userland, which supplies both, through
`"$PYTHON" ci/runner_image_records.py write sh -c '"$PYTHON" PRODUCER ...'`:
it runs `ci/runner_image.sh` (podman) over a snapshot of the tree, which no
host process writes, then copies back and receipts each file the command
wrote there. `ci/runner_image_records.json` binds the record to that
image and its pins through `ci/runner_image_records.py add`, which refuses
bytes without a receipt, and gate core-635 checks the ledger. A gate that
byte-compares a retained record lists it under `"replays"` in ci/gates.json,
and the unmarked pr test `test_every_replayed_record_is_declared_bound_float_free_or_exempt`
requires each listed record (each file of a listed directory) to be bound in
the ledger, float-free JSON, or covered by a reason under the ledger's
`exempt` map, and each bound record to be listed by some gate;
`ci/replay_check.py`, `| cmp -` and `--out` beside `--check` or `--replay`
must be listed.
`ci/replay_check.py` compares such a record with a fresh run bit for bit,
skipping only the paths that name the analyzer (core-613, core-617).
Only an AVX-512 CPU exercises the dispatch cap, so `ci/avx512_replay.sh` runs
every such replay gate on an `avx512f` CPU and reports not run, exit 0, on any
other; each CI gate shard runs it, since GitHub assigns runner CPUs of both
kinds.
The library inventory `docs/state/hypercomplex-libraries` maps each import
through the regenerating interpreter's installed distributions, so it is
written under the system python3, which holds every optional package:
`PYTHON=python3 python3 scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries`.
A change that adds a tracked Python file or an import regenerates it in the
same change. The unmarked tests `test_retained_inventory_*` compare its import
roots and their projection with the tree, which needs no installed
distribution, and fail the `tests` check until it does; core-630 resolves the
distributions in the audit.
`parallel.default_threads()` and `workers()`
share the affinity/quota-bounded `GOROROBA_WORKERS` cap. Spawned pool children
receive one slot through a child-only initializer, so nested maps and simulator
defaults stay within the outer allocation. Timings retain wall time, user/system CPU time,
peak RSS and allocated workers. Ruff formats shared code for Python 3.13.

Current contracts use Qiskit 2.6.0. Gates marked `"runtime": "qiskit-2.5"`
recompile retained historical evidence under an interpreter holding every pin
of `ci/requirements-replay.txt`: `ci/run_gates.py --replay-python PATH` (also
accepted by `ci/premerge_gates.py`), else `REPLAY_PYTHON`, verified against
those pins in a `-I` subprocess. With neither, the running interpreter serves
when it holds every pin, then the host environment below. Current-runtime
gates take an explicit `$PYTHON` as named, else the running interpreter when
it holds every pin of requirements.txt and ci/requirements-ci.txt, else the
host environment. A `--changed-files` run and every premerge run refuse an
explicit `$PYTHON` that differs from those pins, since a verdict under another
runtime says nothing about the pinned one. The runner prints each
choice before the first gate, and a selection with an unresolved runtime runs
no gate and exits 2 naming the differing versions; premerge refuses the same
way with exit 2, since such gates fail on both trees and read as shared
failures that hide a gate the branch breaks. Premerge otherwise exits 0 when
every gate passes on the merge, 1 when the merge introduces a failure and 3
when every failure also fails on the base.
CI installs the replay environment only for shards whose plan requires it
and passes it as `REPLAY_PYTHON`.

**Host environments.** A system interpreter drifts from the pins as the host
upgrades packages, so local runs use `sh ci/build_host_envs.sh`, which builds
`ci-py3.14.7` (requirements.txt and ci/requirements-ci.txt) and
`replay-py3.14.7` (ci/requirements-replay.txt) under
`${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/` on the Python of ci.yml's
setup-python step, through ci/install_pins.sh as CI does. `pins.HOST_ENVS`
names them, and a rerun repairs a venv whose packages drifted.
`GOROROBA_PINS_REQUIRED=1`, set workflow-wide in ci.yml, turns every version
fallback into a failure: the replay interpreter must be named, ruff and mypy
must be installed at their pins, and `ibm_runtime_options_inventory.py
--check` (core-533) must find the probe versions its inventory records.
Without it that check replays the retained inventory (canonical form,
backend schema, note blocks) and names the differing versions
(`ci/pins.py`, tests/ci/test_pins.py).
Before Python starts, CI and Kaggle reserve 4096 optional static TLS bytes with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, required by the combined
Qiskit Rust and Aer OpenMP extensions. Local shells use the same startup setting.

Every CPU-bound loop over independent items (embedding scores in replica
placement, operator checks, registry parsing, exact certificates, synthesis
searches) runs through parallel.py, an order-preserving process pool started
with spawn on every platform, so a parallel run returns exactly what the
serial loop returns; a serial loop over such items is a defect review
rejects. Items that share a seeded generator draw every item's inputs first,
in the generator's order, and then map, so pooled and serial runs write the
same bytes. The worker count comes from the host the process runs on:
`parallel.available_cpus()` takes the scheduler affinity mask bounded by the
CPU quota of the process's cgroup and every ancestor, so the build host, a
CI runner and a Kaggle kernel each use every CPU they grant.
`GOROROBA_WORKERS=N` caps the worker count and `GOROROBA_WORKERS=1` runs
serially; the default (`parallel.default_threads()`) also sets
`--simulation-threads`. A search too long for one host shards by item range
across Kaggle CPU sessions (five run concurrently), each running the same
pool, and merges the shard records in index order. Aer runs batch
every replica of a choice in one call and parallelize experiments itself.
`ci/run_gates.py --device GPU` exports `GOROROBA_AER_DEVICE=GPU` to every
gate, so a local run computes the simulation replays on the GPU while CI's
runners keep the CPU; a gate that passes locally and fails on CI exposes a
device-dependent result. Contracts that compare seeded shot counts keep
Aer's CPU sampler, whose counts their records retain.

A classical estimator evaluated over many synthetic replicates (a null
calibration, a parametric or resampling bootstrap) is batched across
replicates with numpy before it is pooled or sharded: one call fits a block
of replicates, and parallel.py maps the blocks. The scalar form stays as the
reference that analyses call, and a gate proves that the batched path
returns the reference's bits on the record's own streams and on adversarial
inputs. The bits agree when the batched code keeps the scalar arithmetic
order, repeats builtin `sum()`'s Neumaier compensation, and sends every
replicate-dependent `exp` and `** 2` through `math.exp` and `math.pow`;
[vectorized-fits.md](../docs/runbooks/vectorized-fits.md) gives the
rules, the equivalence gates and the measured speedup.

A change to live_run.py or experiments.py also gets a dry run,
`"$PYTHON" live_run.py --out ../results/live`, whose audit record lands under
results/live/.

The matched diagnostic families and statistical design contracts are documented
in [QPU_OPTIMIZATION.md](../gororoba_quantum/QPU_OPTIMIZATION.md). Their local
gates exercise exact labeled laws, bounded inference, fake-backend layouts,
aggregate budgets, and negative dry-run records; hardware claims require
separately approved results.

The independently admitted packed ripple and rank-sector families are described
in [PACKED_ALGEBRA.md](../gororoba_quantum/PACKED_ALGEBRA.md). `--native-dry-run`
calls Runtime with `dry_run=True` and retains mock timing in a separate sidecar.
Mock outcomes never enter scientific analysis or measured visualizations.

The measured folded-job figure uses `results/ripple/folded-job-review.json`.
After changing its renderer, run `"$PYTHON" scripts/render_folded_job_review.py
--png results/ripple/folded-job-review.png --check` from the root. Independent
raw replay uses `"$PYTHON" scripts/review_folded_jobs.py --run-dir "$FOLDED_RUN"
--check`, with `FOLDED_RUN` pointing to the retained archive in hardware
[evidence PR #37](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/37).
The raw archive remains owned by that evidence change.

The N=21 target-flip certificate gets a fresh Rocq compile and kernel check
when its generator, witnesses, or evaluator changes. Run the checks on a copy
under temporary storage so the checkout retains source files only:

```sh
(
  set -eu
  proof_tmp="$(mktemp -d)"
  cp proofs/TargetFlipN21.v "$proof_tmp/"
  (cd "$proof_tmp"
    rocq compile -q -w +all TargetFlipN21.v >compile.log 2>&1
    if rg -n "Warning:" compile.log; then exit 1; fi
    rocq check -silent -o TargetFlipN21)
)
```

The certificate proves finite Boolean permutation action. Operator checks in
modular_arithmetic.py establish Qiskit phase and clean-workspace behavior.

Changes to `proofs/FoldAverageDescent.v`, `proofs/TerminalChannelSeparation.v`,
`proofs/TerminalChannelSeparationReal.v`, or their receipts also run
`ROCQ="${ROCQ:-rocq}" sh docs/evidence/formal_certificates/replay_rocq.sh` with the
toolchain its `toolchain.txt` pins, Rocq 9.3.0 with OCaml 5.5.1 and Stdlib 9.2.0. The replay compiles in temporary storage,
treats warnings as errors, kernel-checks, and compares raw assumptions.
The [bundle](../docs/evidence/formal_certificates/README.md) distinguishes
real foundations, deterministic interval premises and unproved coverage.

The recovered wide-control acquisition uses
`scripts/review_wide_control_job.py --check` and `--self-test`.
`scripts/reconcile_qpu_inventory.py --check`
binds the complete recorded service inventory to every raw job archive,
each failed job's settled charge to the collection that records its
unavailable result (runs submitted after the observation are listed as
awaiting it, `docs/notes/ibm_quantum/account-access.md`), and
the account's consumed seconds to the final charges of the jobs that ran
inside its rolling usage period; its synthetic contract rejects
missing/duplicate jobs, altered denominators, off-window chronology and raw
corruption. `scripts/inventory_retained_runs.py` requires every job id a
runner record or retention file names to belong to that inventory, and
mock and local artifacts to declare no QPU execution. These replays and
measured extraction/render checks join `ci/gates.json`.

Changes to the C881 proof sources or receipts also run the pinned Rocq
procedure in `docs/evidence/c881_exhaustive/README.md`. The CI receipt
check verifies retained hashes. The ci.yml job `rocq-replay` replays the
formal_certificates, c881_exhaustive, folding_proofs and TargetFlipN21
bundles under the opam switch of `ci/rocq_toolchain.pin` (Rocq 9.3.0 on OCaml
5.5.1 with Stdlib 9.2.0) on the nightly schedule and on manual dispatch, the
only triggers ci.yml declares; both replay every bundle, stiefel_witness
included. The path selector of `ci/rocq_changed.sh` (`proofs/`, a replay
bundle, the replay driver, a pin or the workflow) applies to pull-request and
push events, which ci.yml declares no trigger for, so a pull request that
changes a proof input runs the local replay or dispatches ci.yml on its
branch, and the nightly run replays every bundle on main.
tests/ci/test_rocq_ci_pins.py holds the pin, the toolchain.txt banners, the
path list and the open_gororoba fetch in agreement and rejects each mutation
of them. The manual procedure remains the local replay.

**Behavioral suite.** tests/ holds one pytest suite with two selections.
`pr.yml` runs every test the `audit` marker (pyproject.toml) leaves
unmarked, so a new test needs no gate entry, timing entry or group and runs
on every pull request. The rules that keep that run small:
- A bug fix adds a focused unmarked test that fails before the fix.
- A pull-request test builds its input in the test or reads it from
  tests/**/data/. A test that reads a file other changes legitimately edit
  (a source note, a manifest, a research-state record), a large retained
  bundle, or the gate machinery and its manifests carries `audit`, on the
  function or on the module through `pytestmark = pytest.mark.audit`.
  Provider clients are mocked; no pull-request test reaches the network.
- tests/conftest.py fails an unmarked test whose call phase exceeds
  `CALL_BUDGET_SECONDS` (10 s, about twice the slowest hosted test;
  `GOROROBA_TEST_CALL_SECONDS` replaces it on a contended host and 0 lifts
  it). An exhaustive or slow check carries `audit` and gets a small unmarked
  counterpart that tests the same rule on a small input.
- Setup that several tests share is a `scope="module"` or `"session"`
  fixture. Each xdist worker builds its own copy, and `--dist loadgroup`
  places tests in any order, so a shared fixture returns immutable data or a
  fresh copy per test.
- Cases that differ in kind are `pytest.mark.parametrize` rows of one test;
  a numeric sweep belongs in an audit test.
- The job summary lists the 25 slowest tests. Hosted pytest time at about
  2 minutes is the point to shrink or mark tests, well inside the 4-minute
  step timeout; the PR job adds no coverage or other plugin.
The audit gates select by path and ignore the marker, so they still run every
marked test. In the audit, gate core-615 runs `pytest -n auto --dist
loadgroup` over tests/ in one process pool, so each worker imports the
repository modules once; issue #291 carries the migration plan and its
falsifier, a planted mutant per moved contract. core-615 ignores the paths
its sibling gates
`core-behavior-NN` run, each a list of test modules or directories sized
under the 30 s pr budget, or a full gate for a test whose single node
exceeds it (core-behavior-03, the segmented-sweep fits);
tests/ci/test_behavioral_gates.py requires every ignored path on exactly one
sibling and no module on two gates, so a new test module runs on core-615
until a measurement moves it. tests/test_cli_self_tests.py and
tests/test_cli_record_checks.py call scripts' `--self-test` and `--check`
modes in process through each script's `main`, in groups that gates
`core-self-test-NN` and `core-record-check-NN` run one each
(tests/ci/test_self_test_gates.py); a check a research-state claim cites, or
whose gate name a script or retained file carries, or whose gate declares a
`runtime` or `requires`, keeps its own gate. A test exercises a contract on a small fixed input
and fails by an explicit raise. Plugin autoload is off (pyproject.toml), so
only the pinned xdist plugin loads, and a run writes nothing inside the
checkout. tests/conftest.py sizes the pool by `parallel.workers()` and runs
each test process in one slot. A test module imports a ci/ module by bare
name; a moved `--self-test` body leaves the module's CLI. A unittest suite
that lives beside the code it checks joins `SUITES` in
tests/test_unittest_suites.py, which runs it in place with its own directory
on sys.path, and its single-script gate leaves ci/gates.json unless a claim in
docs/state/research_state.json cites that gate. The suite starts git
and child interpreters, so the gate ledger never skips it.

**Gate cost.**
- Measure a gate's cost in CPU seconds. The runner records user and system
  time beside wall time; wall time on a shared host grows with the host's
  load, and parallel code only divides the CPUs it is granted, so a gate
  that reads slow at a load above the CPU count is contended. Read its CPU
  seconds before tuning it.
- Spend CPU only on results that can change. `ci/premerge_gates.py` caches
  the base tree's passing gates under
  the system temporary directory's `gororoba-quantum/premerge`, keyed by the
  base commit, `--max-seconds`, each interpreter's real path, version and
  installed distributions, and every `GOROROBA_`, `QI_`, `OQ_`, `QD_`,
  `QISKIT_`, `PYTHON`, thread-count and `GLIBC_TUNABLES` variable. A flock
  serializes runs over one key, so concurrent sessions share one base run.
  Failures stay out of the cache: a merge failure absent from the cached
  passes reruns on the base through `ci/run_gates.py --gates`, so a failure
  under load never becomes a standing shared failure. `--no-cache` runs the
  base every time.
- Skip a gate only on evidence that its inputs are unchanged.
  `ci/run_gates.py --ledger-out` runs each gate with
  `ci/read_trace/sitecustomize.py` on PYTHONPATH, whose audit hook records
  the repository files every Python process of the gate opens (a `.pyc` as
  its source), the directories it lists, the glob patterns it expands, the
  paths it probes through os.stat and os.lstat (existence and file type) and
  every symbolic link those paths cross (its link text), from every thread
  and spawn-pool child. After a pass, `ci/gate_ledger.py` stores the
  gate's key: the manifest entry, allocated workers, tracer digest, host
  identity (`ci/host_identity.py`: interpreters, distributions, PATH tools
  and keyed variables, shared with the premerge cache) and the read set's
  content. `--ledger` reports SKIP when the recomputed key matches, so a pin
  change reruns every gate through the interpreter identity. A failure, or a
  run the trace cannot cover, stores nothing and removes the earlier entry:
  a shell command other than `"$PYTHON"` invocations joined by `&&` (a glob,
  tilde or parameter outside `"$PYTHON"` expands before any traced process), an `-I`,
  `-E` or `-S` interpreter, a write inside the repository outside
  `__pycache__`, a non-Python child or a child environment that drops the
  trace. CI saves the merged ledger from main only (job `ledger`), and the
  nightly run executes every gate with `--ledger-audit`, failing on a gate
  the ledger would have skipped that fails. That run bounds a missed read to
  one day on main; it is the only net for reads the tracer cannot see (the
  wall clock, C extensions opening files, stat through a dir_fd), so a check
  against an expiry or a rolling window relies on it.
  tests/ci/test_gate_ledger.py plants every read kind and every escape.
- Check with an explicit raise, never `assert`. `python -O` strips every
  assert, and ruff `S101` (pyproject.toml) rejects one at lint time, so each
  check holds in every interpreter mode and each gate runs its command once.
  The files whose bytes retained evidence pins keep their asserts under
  per-file ignores.
