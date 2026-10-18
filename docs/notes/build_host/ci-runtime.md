# CI runtime and affected replay selection

The CI runner spent most of its time computing replays, with an uneven
critical path. Rewriting the small shell setup scripts would address a
minor share of the measured cost. The Python runner now selects long replays
by their inputs, constrains native-library threads, and retains machine-readable
per-gate timing artifacts.

## Measured baseline

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
- Each shard uploads actual durations, estimates, exit codes and wall time
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
