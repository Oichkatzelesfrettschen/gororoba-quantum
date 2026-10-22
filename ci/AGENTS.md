# CI and gate guide

This file applies to the gate machinery under ci/ and to the gate, replay and
cost rules that every change follows. The repository's root AGENTS.md carries
the short form of the code-style commands and the merge flow; CLAUDE.md loads
this file.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only.

**CI runs nightly.** The GitHub Actions workflow `ci.yml` runs on its nightly
schedule and on manual dispatch only: every gate of both tiers on main with
`--ledger-audit`. A pull request's gates run by hand on the PR head before
merge, never per commit or push: the pr tier and every full gate whose
imports or declared inputs the branch changes,
`git diff --no-renames --name-only -z origin/main HEAD > CHANGED` then
`"$PYTHON" ci/run_gates.py --changed-files CHANGED`. The Codex review loop of
[Reviews and merges](../AGENTS.md#reviews-and-merges) is the merge gate. A pr
gate over 30 s of measured wall moves to the full tier with its non-imported
inputs declared in ci/full_gate_inputs.json, so a merge runs it when its own
inputs change and the nightly run covers the reads the tracer cannot see.

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
  on the touched files, and over the whole scope of gate core-039 when a
  change alters a function, class or type signature another module imports,
  since a per-file run never reads the unchanged callers.
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
written in the runner's userland through `ci/runner_image.sh` (podman), which
supplies both, and `ci/runner_image_records.json` binds it to that image and
its pins (`ci/runner_image_records.py add`; gate core-634 checks the ledger).
`ci/replay_check.py` compares such a record with a fresh run bit for bit,
skipping only the paths that name the analyzer (core-613, core-617).
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
host environment. The runner prints each choice before the first gate, and a
selection with an unresolved runtime runs no gate and exits 2 naming the
differing versions; premerge refuses the same way, since such gates fail on
both trees and read as shared failures that hide a gate the branch breaks.
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
5.5.1 with Stdlib 9.2.0) on a pull request that touches `proofs/`, a replay bundle, the replay
driver, a pin or the workflow (`ci/rocq_changed.sh` holds the path list), and
adds the stiefel_witness bundle on pushes to main and the nightly schedule.
tests/ci/test_rocq_ci_pins.py holds the pin, the toolchain.txt banners, the
path list and the open_gororoba fetch in agreement and rejects each mutation
of them. The manual procedure remains the local replay.

**Behavioral suite.** Gate core-615 runs `pytest -n auto --dist loadgroup`
over tests/ in one process pool, so each worker imports the repository modules
once; issue #291 carries the migration plan and its falsifier, a planted
mutant per moved contract. A test exercises a contract on a small fixed input
and fails by an explicit raise. Plugin autoload is off (pyproject.toml), so
only the pinned xdist plugin loads, and a run writes nothing inside the
checkout. tests/conftest.py sizes the pool by `parallel.workers()` and runs
each test process in one slot. A test module imports a ci/ module by bare
name; a moved `--self-test` body leaves the module's CLI. The suite starts git
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
