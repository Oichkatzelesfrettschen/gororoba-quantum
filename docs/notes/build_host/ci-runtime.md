# CI runtime and affected replay selection

The CI runner spent most of its time computing replays, with an uneven
critical path. Rewriting the small shell setup scripts would address a
minor share of the measured cost. The Python runner now selects long replays
by their inputs, constrains native-library threads, and retains machine-readable
per-gate timing artifacts.

## Measured baseline

The sampled ubuntu-latest runners exposed four logical/affinity CPUs and
roughly 16 GB of memory. CPU models varied among AMD EPYC 7763, 9V45 and
9V74. The reports retain each job's runner-spec lines; the worker count
follows the allocation rather than the guide's earlier two-CPU assumption.

The retained analyses name successful GitHub runs and derive elapsed seconds
from the jobs API and each gate's printed duration. Both runs used Python
3.14.7; the Quantum Inspire job used its separate 3.13 interpreter.

| Measurement | Main run 39081984593 | PR run 39084161537 |
|---|---:|---:|
| Workflow-created to final job-completed interval | 2,885 s | 674 s |
| Workflow-created to first job-created delay | 1,040 s | 0 s |
| First job-created to final job-completed interval | 1,845 s | 674 s |
| Sum of runner job intervals | 8,262 s | 2,678 s |
| Sum of dependency-install steps | 446 s | 253 s |
| Sum of primary gate-shard steps | 6,959 s | 2,133 s |
| Sum of gate subprocess elapsed times, including QI lane | 18,091.8 s | 8,277.2 s |

Subprocess elapsed times overlap. They include contention and are neither
CPU seconds nor billable runner seconds. The main run spent 17 minutes 20 seconds before its jobs were created.
The workflow concurrency policy serialized main runs, so a new tree waited
behind an exhaustive run. The API samples establish these two runs, rather
than a distribution of queue delays. The main shards ranged from 174 to
1,780 seconds; the PR shards ranged from 165 to 612 seconds. Static gate
estimates understated several PR gates by factors of five to seven.
The repaired manifest uses the median observed primary-lane duration from
these two samples where a sample exists. Native-thread limits and code
changes require fresh hosted samples before claiming a workflow speedup.

[Main timing records](../../evidence/ci_runtime/main.json) and
[PR timing records](../../evidence/ci_runtime/pr.json) retain job/step totals
and every parsed gate sample. The reports keep the QI lane distinct.

## Compiler construction cost

The critical main gate, core-379, recompiles six circuits at eight seeds on
three snapshot Targets in normal and optimized Python: 288 compile jobs.
Each job called `calibration_snapshot.noise_model`, discarded the resulting
Aer channels, and used only the Target. `n21_conjugation_noise._backend` now
calls `build_target` directly, through the same SnapshotBackend constructor.
Every seed still runs through the same pass manager and retained comparisons.

`scripts/check_n21_conjugation_target.py` compares instruction durations and
errors, qubit properties, dt, operation names and backend names against the
noise-model construction for all three snapshots. Its patched noise-model
constructor raises if the compilation-only path attempts channel creation.
The contract runs in normal and optimized Python. The full all-seeds replay
checks retained routed gates, layout, feedback stages, selected seeds, depth,
duration and count-derived summaries separately.

[Target construction timings](../../evidence/ci_runtime/target_build.json)
measure one retained snapshot on the build host. The measurement isolates
construction cost; the end-to-end hosted comparison remains a separate check.
The normal-mode all-seeds replay reproduced all 144 compilations and
derived fields in 102.33 seconds on the build host; optimized Python
reproduced the same denominator in 82.07 seconds.
[Local replay records](../../evidence/ci_runtime/local_replay.json) bind the
commands and results to the script digest and tool versions. The historical hosted
gate took 1,779.9 seconds for both Python modes on a different machine;
those two measurements establish different execution boundaries.

Exact symbolic/rational certificates retain their arithmetic. Float NumPy
arrays cannot replace those certificates' exact domains. Large statistical
replicate loops follow the existing batched NumPy and scalar-equivalence
contracts; transpilation uses Qiskit's compiler rather than a numerical fit.

## Pinned runner infrastructure

The primary workflow pins Ubuntu 26.04 and runs a separate Ubuntu 24.04
compatibility job over native imports, Target equivalence and scheduling contracts.
The official runner-image announcement confirms Ubuntu 26.04 GA and the
October 19 to November 19 ubuntu-latest migration
([runner-images #14748](https://github.com/actions/runner-images/issues/14748)).
The setup-python manifest supplies Python 3.14.7 and 3.13.15 for that image. Official action manifests
verified Node 24 for checkout v7.0.1, setup-python v7.0.0, cache v6.1.0,
upload-artifact v7.0.2 and download-artifact v8.0.2. The workflow pins each
release by its resolved commit SHA, avoiding the deprecated Node 20 actions
reported by the initial hosted run.

## Selection and resource boundaries

- PRs always run the behavioral `pr` tier and add affected `full` gates.
  Main pushes apply that selection to their before/after diff. Nightly and
  manual events execute the entire manifest.
- `git diff --no-renames --name-only -z` retains both sides of renames,
  deleted paths and filenames containing whitespace. A missing base triggers
  exhaustive selection. Fetch/diff failures select exhaustive verification.
- `ci/gate_inputs.py` follows nested local imports and Python source literals.
  `ci/full_gate_inputs.json` owns reviewed dynamic data and source scopes.
  Broad scopes protect source manifests and raw-job censuses; they can select
  extra gates. The graph is conservative, rather than an exact read trace.
  New dynamic reads require an updated scope in the same change. Dependency
  and workflow changes select every full gate.
- The gate pool uses affinity bounded by ancestor cgroup quotas. Native BLAS,
  OpenMP and NumExpr each receive one thread in CI. Local explicit thread
  settings remain available. Independent gate processes supply parallelism.
- New pushes cancel stale checks for the same event and ref. Nightly and
  manual runs have separate concurrency groups so pushes preserve their
  exhaustive coverage.
- Each shard uploads actual durations, estimates, exit codes, user/system CPU
  time, peak RSS, allocated workers and wall time
  even when a gate fails. Completion lines appear immediately. A failed
  gate keeps the remaining gates running.

The behavioral contracts exercise import closure, added/deleted inputs,
source digests, manifest coverage, toolchain selection, thread settings,
keep-going execution, JSON timings and timing denominators in both Python
modes. Existing Rocq routing and pin contracts continue to bind proof replay.

## Reproduce the decomposition

From the repository root, export the intended interpreter as `PYTHON`.

```sh
export PYTHON="${PYTHON:-python3}"
run_id=39081984593
gh api "repos/Oichkatzelesfrettschen/gororoba-quantum/actions/runs/$run_id" > /tmp/ci-run.json
gh api "repos/Oichkatzelesfrettschen/gororoba-quantum/actions/runs/$run_id/jobs" \
    --paginate > /tmp/ci-jobs.json
gh run view "$run_id" --log > /tmp/ci-run.log
commit=$(gh run view "$run_id" --json headSha --jq .headSha)
git show "$commit:ci/gates.json" > /tmp/ci-manifest.json
"$PYTHON" ci/analyze_timings.py --jobs /tmp/ci-jobs.json --log /tmp/ci-run.log --run /tmp/ci-run.json \
    --run-id "$run_id" --manifest /tmp/ci-manifest.json --out /tmp/ci-analysis.json
# Add --refresh-estimates to update ci/gates.json from successful primary-lane samples.

git diff --no-renames --name-only -z origin/main HEAD > /tmp/ci-changed.bin
"$PYTHON" ci/run_gates.py --changed-files /tmp/ci-changed.bin --list
"$PYTHON" ci/check_gate_inputs.py
"$PYTHON" -O ci/check_gate_inputs.py
```

The remaining optimization frontier is measured per gate: split long,
independently checkable compile inventories across shards; profile exact
symbolic replays before changing algorithms; and refresh timings after
hosted resource limits apply. A reduced behavioral fixture complements the
exhaustive replay rather than establishing the full corpus's scientific claim.

## CPU scheduling and independent contracts

`parallel.available_cpus()` intersects scheduler affinity with the CPU quotas
of the process and its cgroup ancestors. The runner maintains that many CPU
slots across all active gates. Ordinary gates consume one slot; twelve gates
with independent inner work reserve the whole allocation using `workers: all`.
A reserved gate receives the slot count through `GOROROBA_WORKERS`. Other gates
wait until enough slots return. BLAS, OpenMP, NumExpr, Rayon and Qiskit process
counts default to one so nested native pools share the same finite allocation.
Explicit local native overrides remain visible in runner-spec output.

The runtime suite exposes 45 named cases in a static registry. CI expands the
registry before longest-first shard assignment, so independent cases can occupy
different runners. Default script execution retains every case in original
order through the spawn pool; case workers cap their own nested pools at one.
Rocq bundle replay similarly maps independent isolated bundle processes through
the detected pool and returns bundle records in request order.

An isolated POSIX Python collector measures user/system CPU seconds and maximum
resident set size through `resource.getrusage(RUSAGE_CHILDREN)` for one gate
process tree. Separate collectors prevent parallel gates from mixing counters
and remove the external GNU time dependency. macOS RSS bytes convert to KiB. Peak RSS is a process maximum, rather than a
sum of simultaneous child memory. These resource fields complement overlapping
elapsed times; elapsed totals remain distinct from billed runner intervals.

## Exact arithmetic and dependency qualification

[Rank-sector benchmark samples and program](../../evidence/ci_runtime/rank_sector.json)
retain the exact method and measured environment. Rank-sector success probabilities now accumulate 16 sparse rational products
into the full 32-coordinate image instead of constructing a dense SymPy matrix
per call. A 256-case contract compares exact Fractions with the independent full
symbolic matrix, including the adversarial rational `1 - 2^-60`. The local
224-evaluation benchmark measured median 4.1601 s before and 0.03065 s after;
the containing repetition-delay check measured median 1.4091 s and 0.5988 s.
These measurements describe the build host. Both Python modes passed the full
rank-sector circuit and exact-arithmetic contracts.

The [dependency audit](../../evidence/ci_runtime/dependencies.json) checks 78
packages against release metadata. Current pins advance Qiskit to 2.6.0,
Pydantic to 2.14.1, IBM schemas to 0.13.20261016, Ruff to 0.17.1, mypy to 2.4.0
and Playwright to 1.64.0; threadpoolctl 3.7.0 reports actual loaded native pools.
The Quantum Inspire lock retains upstream-required versions under Python
3.13.15. Ruff uses Python 3.13 formatting and a Python 3.13 lint target for
shared `qi_*.py` scripts.

Qiskit 2.6 changes seeded routing relative to the retained Qiskit 2.5 receipts.
Current behavioral and operator contracts run on 2.6. Source-recompilation gates
that compare historical costs or simulated responses declare the producer
runtime in the manifest. The GitHub and Kaggle shard planners request `ci/requirements-replay.txt` only
when a shard contains those gates; dispatch requires `REPLAY_PYTHON` and reports
the runtime in timing records. Historical raw costs and version labels retain
their recorded values.

The upgraded Rust extension needs more static TLS alongside Aer's libgomp.
CI and Kaggle configure `glibc.rtld.optional_static_tls=4096` before interpreter
startup. The glibc default is 512 bytes, so the explicit capacity reserves an
additional 3584 bytes per thread, plus loader alignment. The setting follows
[glibc's dynamic-linker documentation](https://sourceware.org/glibc/manual/latest/html_node/Dynamic-Linking-Tunables.html).
Fresh normal and optimized imports and SDK options inventories passed under
warnings-as-errors. Kaggle tests verify startup propagation offline; GPU
execution remains a separate measurement.

Rocq 9.3.0, OCaml 5.5.1 and independently versioned Stdlib 9.2.0 replace the
older toolchain. Fresh compilation, kernel checking and raw-assumption receipts
cover formal certificates, C881, folding, TargetFlipN21 and Stiefel. The four
short bundles passed concurrent replay; Stiefel passed separately in 331.6 s.
Raw kernel diagnostics include the additional Rocq 9.3 informational output.

The walk-scaffold replay separates two SDK contracts. The producer gate requires
byte-identical format-17 QPY and JSON extraction under Qiskit 2.5.2. The current
SDK gate requires the same JSON bytes, all 56 loaded circuits equal, and the
existing numerical law, likelihood, optimum and scientific decision checks.
Qiskit 2.6 writes format 18 with a changed binary representation; the original
extract and its source ledgers retain their recorded bytes.

## Optimizer coordinates and reproducible scientific results

Hosted run 39086132104 reproduced the orbit-window fit with control phase
-0.4676820606691535 instead of -0.4676843006565198 and second-round excess
0.17288122760296823 instead of 0.17287973432964707. The old replay compared
coordinates at 1e-6, so the gate failed. The coordinate shift changes total
G-squared by 2.66e-10 and the largest arm probability by 1.17e-7, equivalent
to 0.00048 expected counts at 4096 shots. The retained point's law Jacobian
has singular values 0.493, 0.122 and 0.0497: local rank is full. Statistical
non-significance therefore cannot justify calling the coordinates unidentified.

SciPy L-BFGS-B uses finite differences with default eps 1e-8, gtol 1e-5 and
ftol 2.220446049250313e-9. At retained G-squared 5.5921, the objective stopping
scale is about 1.24e-8. The measured objective shift lies below that stopping
scale; the fitter specifies less coordinate precision than the old assertion.

The replay now compares complete induced laws and likelihoods at the unchanged
1e-6 scientific replay tolerance. A separate check requires every pair-model
coordinate to stay inside its declared domain and reproduce its own stored laws
within 64 float64 epsilons. Parameter names, scientific decisions, structural
fields and measured counts retain their exact comparisons. Regression cases
accept the measured stopping drift and equivalent phase branches and reject
changed laws, corrupted coordinate/law bindings and out-of-domain coordinates.
Raw reports retain their original coordinates.

## Short PR contracts and stable shard plans

Fourteen expensive gates originally labeled PR checks now declare full-tier
input scopes: exhaustive geometry, archive-derived crosschecks, calibrated
channel replays and retained QX conformance. The full corpus still runs whenever
its code or declared evidence changes. Small atlas channel, JAX program and QX
emitter/parser contracts run on every PR in both Python modes. A regression
wraps file access and rejects any attempt by those contracts to read `results/`
or `docs/evidence/`, including reads during import. Hardware exclusion metadata
continues to come from the actual visibility analysis, loaded and cached on
first hardware use; importing pure emitters leaves the archives unopened.

Shard assignment balances estimated occupied CPU-slot seconds. A gate reserving
four slots for ten seconds contributes forty slot-seconds. The stable planning
profile defaults to the measured hosted four-CPU allocation (`--shard-cpus 4`);
every shard in a run uses the same profile, so heterogeneous host CPU limits
cannot change shard membership. Actual execution still uses every detected CPU
and respects the caller's worker cap. Plans and timing records retain the
planning profile alongside actual allocated resources.

Qiskit 2.6 emits elementary KG24 gates where 2.5 emitted named RCCX/CCX gates.
Order-finding resource checks lower both representations to the common declared
elementary basis and compare the same independent CX/T/T-dagger budgets. The
native shared-predicate probe recognizes only complete, exactly matched RCCX
endpoint spans and verifies full operators. Its current-SDK contract keeps the
original 1e-12 scientific bound and records current costs separately from the
producer's historical receipt. Historical QPY digest receipts and version-stamped
wide-control reports use their producer interpreter; raw reports remain intact.

The first broad upgraded PR replay completed 411 gates: 397 passed and 14
failed. The failures exposed historical serialization/synthesis comparisons,
renewed proof-receipt hashes and derived source identities. Focused qualification
renews only derived hashes after unchanged mathematical and hardware-statistic
results are verified. The rank-endpoint regeneration changed only its producer
source-hash map. Formal registry claims bind the freshly checked Rocq 9.3
receipts. Original raw archives, native probe result and archived probe retain
their recorded bytes.

All 45 current-SDK runtime cases passed together (323.14 s wall, 377.04 s user
CPU, 5.21 s system CPU, maximum process RSS 990824 KiB on the shared build host).
The fragmented-layout case triggers a native Sabre capacity-overflow panic on
a valid Target restricted to qubits 0-4. Existing compile isolation converts the
panic and successfully compiles the explicit layout [0,1,2]; an isolated replay
passed. The measurement qualifies the recovery boundary, rather than asserting
that the upstream router accepts every admission Target directly.

The planted-detuning contract draws all 20 random streams before dispatching
independent fits through the spawn pool. The fitter arithmetic remains identical.
[The retained benchmark](../../evidence/ci_runtime/patch_window.json) measured
83.956804 s serially and 29.859811 s with four workers, including spawn, on a
shared host. All result dictionaries and random streams match byte for byte.
The observed 2.81-fold speedup is one local sample.

The QI emitter contract checks availability through `qi_stack.live()` and runs
the synthetic emitter under both installed interpreters. A direct qxelarator
0.10.0 import with `-W error` reproduced exit 139 during interpreter shutdown;
the ordinary import and the existing isolated probe both exit successfully.
The probe applies the repository's narrowly scoped SWIG `__module__` warning
filter and checks the installed versions against the QI lock. The emitter
contract exercises serialization and parsing; live simulator conformance remains
a separate gate.
