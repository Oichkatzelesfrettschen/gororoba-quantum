# CI and gate guide

This file applies to the pull-request workflow, the gate machinery under ci/,
and the replay and cost rules of the gates. The repository's root
AGENTS.md carries the short form of the code-style commands and the merge
flow; CLAUDE.md loads this file.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only.

**Pull requests.** [.github/workflows/pr.yml](../.github/workflows/pr.yml)
runs on every pull-request push, on every push to main (so the merged result is
checked once) and on `workflow_dispatch`, cancels the run a newer pull-request
push replaces, and holds four jobs that call
[ci/pr_checks.sh](pr_checks.sh) with its environment (loader TLS, one thread
per native library, `GOROROBA_PINS_REQUIRED=1`):
- `lint` installs the Ruff pin of ci/requirements-ci.txt and runs `ruff check`
  and `ruff format --check` over ci/, tests/, gororoba_quantum/, scripts/ and
  kaggle_kernel/;
- `types` runs mypy over the same directories from gororoba_quantum/;
- `tests` runs `pytest -n auto --dist loadgroup -m "not audit"` over tests/
  under a 5-minute step timeout and writes the 25 slowest tests to the job
  summary;
- `gates` runs every entry of [ci/gates.json](gates.json) through
  `ci/run_gates.py`, concurrently on the runner's CPUs: no selection by diff, no
  budget and no ledger, so a green job states that every listed gate passed. A
  gate that carries `"runtime": "qiskit-2.5"` runs under the replay venv, which
  the job restores from the cache of an earlier run and builds on a miss.
  Concurrent gates run mypy, so `ci/pinned_tool.py` gives each mypy
  invocation its own `.mypy_cache/KEY` directory unless the caller names one.
`lint`, `types` and `tests` time out at 8 minutes and `gates` at 30.
`types`, `tests` and `gates` restore the pinned venv through
.github/actions/pins-venv, under a cache key that hashes the venv's inputs, and
build it with ci/install_pins.sh on a miss; a push to main saves it where later
pull requests restore it. Branch protection on main requires `lint`, `types`, `tests`
and `gates` green on the head, for administrators too, without requiring the branch to
be current with main. A pull request that `GITHUB_TOKEN` opened starts no
`pull_request` workflow, so its author dispatches pr.yml on the branch
(scripts/qd_schedule_tick.sh does so when a schedule finishes); a branch whose
pr.yml predates `workflow_dispatch` gets its checks from merging main into it
and pushing. With the Codex
review loop the checks admit a merge
([Merging](../AGENTS.md#reviews-and-merges)); a local gate run or a premerge
check is never a merge requirement, and the Rocq compile of
[proofs.yml](../.github/workflows/proofs.yml) is not a required check. Locally,
`sh ci/pr_checks.sh tests tests/path/test_x.py` runs one module under the
hosted environment, and `sh ci/pr_checks.sh tests -m audit tests/path/test_x.py`
runs its audit-marked tests (pytest keeps the last `-m`). Each lane first
resolves its interpreter through `ci/pins.py lane LANE`: an explicit `PYTHON`
runs only when it holds the lane's pins (ruff for lint, every current pin for
types and tests), an unset one takes the host environment, and a drifted one
exits 2 naming the differing pins and the command that runs the lane under
the host environment.

No workflow runs a schedule. The two crons that remain, quandela-schedule.yml
and quandela-record-watch.yml, operate provider jobs and check no gate.
`ci/premerge_gates.py` runs the fast gates of ci/gates.json on the merge of a
branch into main, locally, to catch two branches that merge without a textual
conflict and break a record derived from the whole tree.

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

[ci/gates.json](gates.json) lists each gate as one command with its
working directory; [ci/run_gates.py](run_gates.py) runs them on
a thread pool sized to the runner's CPUs and keeps going past failures, so a
red run lists every failing gate. Every gate runs on every pull request and every
push to main. A gate's `seconds` is the estimate that `ci/run_gates.py --max-seconds`
and `ci/premerge_gates.py` filter by, and `"tier": "pr"` marks the gates
`ci/premerge_gates.py` considers; an entry that takes more than 30 s of hosted wall belongs in
[ci/replays.json](replays.json) (Replays below). Gate concurrency follows the runner's detected allocation.
Disposable
build trees, task virtual environments, package caches and probes belong in
the system temporary directory, normally `/tmp`, so temporary-file cleanup
can reclaim them. Keep durable code, evidence and documentation in the
repository. Never create task repositories or scratch stores in
`~/.local/share`. Preserve existing shared provider environments and credentials.
Gate seconds are cost estimates, independent of tier membership.
[CI runtime analysis](../docs/runbooks/ci-runtime.md) records the timing
denominators and bottlenecks of the CI that preceded this one. Runner-spec logs
record the allocation; the retained runs measured four affinity CPUs and
about 16 GB on ubuntu-latest. CI uses Ubuntu 26.04 and pins
Node 24 action commits. Jobs use Python 3.14.7
with the pins in requirements.txt and ci/requirements-ci.txt (mypy, ruff and
the plotting-only `matplotlib==3.11.2`). A gate that ci/gates.json
tags `"requires": ["qi"]` replays its retained record unless the caller exports
`GOROROBA_QI_REQUIRED=1` with `QI_PYTHON` naming the Quantum Inspire interpreter, which
makes it take its live path or fail
([Quantum Inspire](../docs/notes/quantum_inspire/README.md#binding-rules)). A gate tagged
`"requires": ["singular"]` skips unless Singular 4.4.1 is on PATH (the `passagemath-singular==10.8.13` wheel
installs it into a separate virtual environment; Singular reads stdin even for `--version`, so run it with stdin
from `/dev/null`); `GOROROBA_SINGULAR_REQUIRED=1` turns the skip into a failure. `verify.py` checks the
gororoba-open commit named in [ci/open_gororoba.pin](open_gororoba.pin) by hand:
`ci/fetch_open_gororoba.sh` sparse-checks out the paths it is given, and
`scripts/materialize_gororoba_csv.py` rewrites the git-ignored `data/csv`
files from the registry records, whose sha256 pins `verify.py` rechecks. A
pin bump is a reviewed commit. A new contract lands as a test function
under tests/ (Behavioral suite below); a new evidence replay joins the gate
list in ci/gates.json in the same change.
The `lint` and `types` jobs of pr.yml (`sh ci/pr_checks.sh lint|types`) cover
gororoba_quantum/, scripts/, ci/, tests/ and kaggle_kernel/ whole, so a module
there is linted and type-checked without a list edit; a checked file elsewhere
in the tree, such as an evidence replay under results/ or docs/, is named in
that lane's command. They run ruff and mypy through
`ci/pinned_tool.py TOOL ARGS`, which uses the installed tool when it reports
the ci/requirements-ci.txt pin and otherwise runs the pinned release through
uv: ruff through `uv tool run`, mypy layered over `"$PYTHON"`'s
site-packages, so a host mypy run type-checks against that host's packages,
which can hold other releases than CI's pins.

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
stay at one inside each slot. A producer computes on its platform's native
path, AVX-512 included, and records that path (CPU model, numpy dispatch
targets, OpenBLAS cores, any cap set); a result computed on an Intel chip
replays on the build host under Intel SDE emulating that chip
([docs/PYTHON.md](../docs/PYTHON.md#emulating-another-cpu-with-intel-sde)), and
one computed on an AMD Zen 4 or Zen 5 runner replays on such a CPU. The
byte-replayed records of the runner-image ledger keep the caps until each is
re-bound with its platform: for their gates `ci/run_gates.py` defaults
`OPENBLAS_CORETYPE` to Haswell and caps numpy's dispatch at x86-64-v3 with
`NPY_DISABLE_CPU_FEATURES`, the kernel set every runner and build host
executes. Such a record is written in the runner's userland, which supplies
both caps, through
`"$PYTHON" ci/runner_image_records.py write sh -c '"$PYTHON" PRODUCER ...'`:
it runs `ci/runner_image.sh` (podman) over a snapshot of the tree, which no
host process writes, then copies back and receipts each file the command
wrote there. `ci/runner_image_records.json` binds the record to that
image and its pins through `ci/runner_image_records.py add`, which refuses
bytes without a receipt, and gate core-635 checks the ledger. A gate that
byte-compares a retained record lists it under `"replays"` in its entry of ci/gates.json or ci/replays.json,
and the unmarked pr test `test_every_replayed_record_is_declared_bound_float_free_or_exempt`
requires each listed record (each file of a listed directory) to be bound in
the ledger, float-free JSON, or covered by a reason under the ledger's
`exempt` map, and each bound record to be listed by some gate of either manifest;
`ci/replay_check.py`, `| cmp -` and `--out` beside `--check` or `--replay`
must be listed.
`ci/replay_check.py` compares such a record with a fresh run bit for bit,
skipping only the paths that name the analyzer (core-613, core-617).
Only an AVX-512 CPU exercises the dispatch cap, and GitHub assigns runner CPUs
of both kinds, so a replay gate that differs in the last bit on an AVX-512
runner is re-run by hand on an `avx512f` CPU.
A gate whose command ends in `ci/replay_check.py RETAINED --skip .tools.singular`
compares a Singular producer's record without the version banner, whose build
date differs between the distribution binary and the wheel binary; the
gate's `GOROROBA_SINGULAR_REQUIRED=1` branch asserts the 4.4.1 version tuple.
The library inventory `docs/state/hypercomplex-libraries` (documented in
the central Python guide [docs/PYTHON.md](../docs/PYTHON.md)) retains authored
roles, declared pins, source digests and the host-observed import-root
mapping; the importing files and unresolved roots of each distribution are
computed from `git ls-files` and each file's AST at check time
(`current_imports`), so an import of an already mapped root regenerates
nothing. An import of a root the mapping lacks fails the unmarked test
`test_retained_inventory_maps_every_tracked_import_root` and core-630 until
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON"
scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries`
runs under the pinned CI venv extended with the new distribution (the
regeneration keeps every retained mapping and host version). A change to a
role, a declared pin or a hashed source regenerates it the same way.
`parallel.default_threads()` and `workers()`
share the affinity/quota-bounded `GOROROBA_WORKERS` cap. Spawned pool children
receive one slot through a child-only initializer, so nested maps and simulator
defaults stay within the outer allocation. Timings retain wall time, user/system CPU time,
peak RSS and allocated workers. Ruff formats shared code for Python 3.13.

Current contracts use Qiskit 2.6.1. Gates marked `"runtime": "qiskit-2.5"`
recompile retained historical evidence under an interpreter holding every pin
of `ci/requirements-replay.txt`: `ci/run_gates.py --replay-python PATH` (also
accepted by `ci/premerge_gates.py`), else `REPLAY_PYTHON`, verified against
those pins in a `-I` subprocess. With neither, the running interpreter serves
when it holds every pin, then the host environment below. Current-runtime
gates take an explicit `$PYTHON` as named, else the running interpreter when
it holds every pin of requirements.txt and ci/requirements-ci.txt, else the
host environment. Every premerge run refuses an
explicit `$PYTHON` that differs from those pins, since a verdict under another
runtime says nothing about the pinned one. The runner prints each
choice before the first gate, and a selection with an unresolved runtime runs
no gate and exits 2 naming the differing versions; premerge refuses the same
way with exit 2, since such gates fail on both trees and read as shared
failures that hide a gate the branch breaks. Premerge otherwise exits 0 when
every gate passes on the merge, 1 when the merge introduces a failure and 3
when every failure also fails on the base.
pr.yml installs the replay environment only when the gate plan requires it
and passes it as `REPLAY_PYTHON`.

**Host environments.** A system interpreter drifts from the pins as the host
upgrades packages, so local runs use `sh ci/build_host_envs.sh`, which builds
`ci-py3.14.7` (requirements.txt and ci/requirements-ci.txt) and
`replay-py3.14.7` (ci/requirements-replay.txt) under
`${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/` on the Python of the pins-venv
action's setup-python step, through ci/install_pins.sh as CI does. `pins.HOST_ENVS`
names them, and a rerun repairs a venv whose packages drifted. A rebuild
holds `host-envs.lock` beside them exclusively, while `ci/pr_checks.sh` and
`ci/run_gates.py` hold it shared (`pins.hold_host_envs`), so a rebuild waits
for running checks and never swaps packages under a verdict.
`GOROROBA_PINS_REQUIRED=1`, which ci/pr_checks.sh sets, turns every version
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
check verifies retained hashes. The proofs.yml job `rocq` replays the
formal_certificates, c881_exhaustive, folding_proofs, TargetFlipN21 and
the other Rocq bundles under the opam switch of `ci/rocq_toolchain.pin` (Rocq
9.3.0 on OCaml 5.5.1 with Stdlib 9.2.0). The workflow triggers on a pull request
or a push to main whose diff touches a proof source, a replay bundle, the replay
driver or a pin (its `paths:` lists), and on manual dispatch. A pull request
replays the bundles under two minutes; a push to main and a manual run add the
stiefel_witness bundle. The path filter leaves the workflow unrun on other
changes, so it is not a required check.
tests/ci/test_rocq_ci_pins.py holds the pin, the toolchain.txt banners, the
`paths:` lists and the gororoba-open fetch in agreement and rejects each mutation
of them. The manual procedure remains the local replay.

**Behavioral suite.** tests/ holds one pytest suite with two selections.
`pr.yml` runs every test the `audit` marker (pyproject.toml) leaves
unmarked, so a new test needs no gate entry, timing entry or group and runs
on every pull request. The rules that keep that run small:
- A bug fix adds a focused unmarked test that fails before the fix.
- A pull-request test builds its input in the test or reads it from
  tests/**/data/ or a retained file it checks in at most 3 s of CPU on the
  build host (the hosted runner takes about twice that against the bound
  below). A test that replays a retained record end to end, reads a large
  retained bundle, runs the gate machinery over the whole manifest, or takes
  more than 3 s on the build host carries `audit`, on the function or on the
  module through `pytestmark = pytest.mark.audit`, and runs through gate
  core-615 of ci/replays.json. Provider clients are mocked; no pull-request
  test reaches the network.
- tests/conftest.py targets `CALL_BUDGET_SECONDS` (10 s) for the call phase
  of an unmarked test and fails it past `CALL_BUDGET_TOLERANCE` (1.5) times
  that target, so hosted-runner jitter around 10 s passes;
  `GOROROBA_TEST_CALL_SECONDS` replaces the target on a contended host and 0
  lifts the bound. An exhaustive or slow check carries `audit` and gets a small unmarked
  counterpart that tests the same rule on a small input.
- Setup that several tests share is a `scope="module"` or `"session"`
  fixture. Each xdist worker builds its own copy, and `--dist loadgroup`
  places tests in any order, so a shared fixture returns immutable data or a
  fresh copy per test.
- Cases that differ in kind are `pytest.mark.parametrize` rows of one test;
  a numeric sweep belongs in an audit test.
- The job summary lists the 25 slowest tests. Hosted pytest time at about
  2 minutes is the point to shrink or mark tests, well inside the 5-minute
  step timeout; the PR job adds no coverage or other plugin.
The behavioral-suite gates select by path and ignore the marker, so they run
every marked test they name. Gates core-behavior-01 and core-behavior-02 of
ci/gates.json run on every pull request; core-behavior-03 (the segmented-sweep fits,
a single node over 30 s) and core-615 of ci/replays.json run on demand. Gate core-615 runs
`pytest -n auto --dist loadgroup` over tests/ in one process pool, so each worker
imports the repository modules once, and with no `-m` filter it is the one runner of
the audit-marked nodes that no other gate names; issue #291 carries the migration
plan and its falsifier, a planted mutant per moved contract. core-615 ignores the
paths its sibling gates `core-behavior-NN` run, each a list of test modules or
directories sized under the 30 s pr budget, or a full gate for a test whose single
node exceeds it (core-behavior-03);
tests/ci/test_behavioral_gates.py requires every ignored path on exactly one
sibling and no module on two gates, so a new test module runs on core-615
until a measurement moves it. tests/test_cli_self_tests.py and
tests/test_cli_record_checks.py call scripts' `--self-test` and `--check`
modes in process through each script's `main`, in groups that gates
`core-self-test-NN` (ci/gates.json, every pull request) and `core-record-check-NN`
(ci/replays.json, on demand) run one each (tests/ci/test_self_test_gates.py); a check a research-state claim cites, or
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
and child interpreters.
tests/test_evidence_ledgers.py checks each retained `SHA256SUMS`-style ledger a `sha256sum -c` gate once
checked, one test id per ledger, resolving names against the gate's working directory as sha256sum does; a
ledger whose gate a research-state claim cites keeps that gate and is also a row of the test, and
the test requires every remaining single-ledger `sha256sum -c` gate to be a row. Each
ledger row runs in the pull-request suite, and an unmarked counterpart checks the
ledger rule on a bundle it builds.

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
- Check with an explicit raise, never `assert`. `python -O` strips every
  assert, and ruff `S101` (pyproject.toml) rejects one at lint time, so each
  check holds in every interpreter mode and each gate runs its command once.
  The files whose bytes retained evidence pins keep their asserts under
  per-file ignores.

## Replays

[ci/replays.json](replays.json) holds the entries that reproduce a
retained record byte for byte (the `ci/replay_check.py`, `--check`, `--replay`
and `cmp` gates), the pytest wrappers that batch those checks
(`core-record-check-NN`), the behavioral suite without its marker filter
(`core-615`) and the full-tier checks whose hosted wall exceeds 30 s. Its entries
keep the shape of ci/gates.json; the two files share one namespace of gate ids,
and [ci/manifest.py](manifest.py) is the only reader of either, so a claim of
docs/state/research_state.json cites a gate of either file and
`scripts/research_state.py --check`, `ci/runner_image_records.py check` and
`scripts/results_index.py` follow a gate that moves. No workflow runs
ci/replays.json. A replay runs on demand, after a numpy, qiskit, Singular or
interpreter pin changes or when a producer script or its input changes:
`"$PYTHON" ci/run_gates.py --manifest ci/replays.json [--gates NAME,...]`, inside the
runner image (`ci/runner_image.sh`, podman) for a record that the runner-image
ledger binds, because those records are tied to the image's libm and Python
build. A replay sets the environment its record names (the caps below, thread
counts) and runs on the machine whose CPU the record's platform matches:
- a record with no AVX-512 dispatch, or written under the CI caps
  (`OPENBLAS_CORETYPE=Haswell`, `NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL
  AVX512_SPR"`, set by `ci/pr_checks.sh` and `ci/run_gates.py`), including the
  AMD EPYC 7763 (Zen 3) runners, replays on the AVX2 build host, the reference
  machine;
- a record from an AMD Zen 4 or Zen 5 runner with AVX-512 dispatch replays on
  a Zen 4 CPU (numpy's AVX-512 dispatch groups resolve the same on both), with
  the record's recorded `OPENBLAS_CORETYPE` set, because OpenBLAS core
  detection can differ;
- a record from an Intel server replays on a Zen 4 CPU when the record's
  dispatch groups are ones Zen 4 has, and under Intel SDE (`sde64 -icx` or `-spr
  -follow_subprocess`) otherwise and always for the FP16 group; SDE emulates the
  chip at about 3x slowdown, so it answers a single question and never the
  whole set.
A producer records the platform it computed on (CPU model, numpy dispatch
targets, OpenBLAS cores, any cap set), and the routing keys on that record, not
on the vendor alone.

## Code style tools

Every Python file a change touches passes, before each push, through
`"$PYTHON" ci/pinned_tool.py TOOL ARGS` (the versions of
ci/requirements-ci.txt):
- `ruff format --target-version py313` (120-column lines from pyproject.toml;
  the Python 3.13 target is the Quantum Inspire interpreter's);
- `ruff check` (pycodestyle, pyflakes, import order, bugbear, pyupgrade, S101);
- `mypy` on the touched files, and over gororoba_quantum/, scripts/, ci/,
  tests/ and kaggle_kernel/ (from gororoba_quantum/: `mypy . ../scripts ../ci
  ../tests ../kaggle_kernel`) when a change alters a signature another module
  imports.

A gate command run outside ci/run_gates.py needs `PYTHON` exported
(`export PYTHON="${PYTHON:-python3}"`); an unexported assignment expands empty
and every gate exits 127 in 0.0 s.

## Seed ledger

`ci/seed_provenance.py`, run by the `tests` check, requires every integer seed
literal in the code directories and in every git-tracked Python file under
docs/ to be a row of ci/reproduction_seeds.json, which only shrinks against
main, or an entry of docs/evidence/qrng_seeds/allocations.json naming a
registered source's draw that no case manifest owns and the index holding that
value. A tracked file that takes a draw value the literal scan cannot key (a
helper alias, a mapping) gets a `reserved` row there instead. A seed a CLI takes
at run time goes through `qrng_seeds.add_seed_argument`, which accepts
`qrng:<draw>#<index>`, the flag's default or `repro:<integer>` and refuses any
other integer; the run record's `seed_source` names the spelling, and the
change that retains a qrng-seeded run adds its ledger row with
`"$PYTHON" ci/seed_provenance.py --add-runtime`. The seed sources and their
draw rules are in [docs/notes/qrng/README.md](../docs/notes/qrng/README.md).
