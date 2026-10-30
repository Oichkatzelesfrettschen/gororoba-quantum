# Native numeric paths and retained-record replay

Every classical producer and every CI runner computes on its CPU's native numeric path: numpy's full
dispatch, the OpenBLAS kernel its `DYNAMIC_ARCH` selects, and the libm variants glibc's ifuncs pick,
AVX-512 included. Native paths round the same computation differently, and `ci/replay_check.py`
compares retained records by `float.hex()`, so byte replay keeps its meaning only between runs on one
measured numeric identity. This design replaces the capped single path with an identity-scoped
contract: exact bytes within an identity, exact decisions and bounded floats across identities.

## Measured facts

- The build host (AMD Ryzen 5 5600X3D, Zen 3, AVX2) selects the OpenBLAS `Haswell` core and numpy
  `X86_V3` with no cap, so its native path equals the capped one. All 36 gates that replay
  runner-image ledger records (`ci/runner_image_records.json`) pass on it with both caps unset.
- Under Intel SDE 10.13.1, the n21 dose-decisions record
  (`results/live/2026-10-27T014354.701394Z/dose-decisions.json`) replays exactly on emulated Emerald
  Rapids, Sapphire Rapids and Ice Lake server with both caps set, and all three agree on one different
  file without them; the OpenBLAS AVX-512 kernel moves 85 fields and numpy's dispatch none
  ([PYTHON.md](../PYTHON.md#emulating-another-cpu-with-intel-sde)).
- With both caps set, the same record fails on AMD EPYC 9V74 (Zen 4) and 9V45 (Zen 5) runners in 95
  fields by about one ulp, and passes on Intel Xeon Platinum 8573C (issue #679). The caps therefore
  never gave Zen 4/5 the build host's path, and SDE, which emulates Intel only, cannot reproduce it.
- Hosted `ubuntu-26.04` runners draw their CPU per job: one nightly audit drew nine AMD EPYC 7763
  (Zen 3, no AVX-512) shards, one Intel 8573C and one AMD 9V45; other runs drew Intel 8370C and AMD 9V74.
- SDE runs about 30 times slower than native (dose decisions 147 s against about 5 s), and its cache
  sizes and core count are the host's.
- `ci/avx512_replay.sh` selects only the gates whose command runs `ci/replay_check.py` (three gates),
  while ci/gates.json declares 101 replay roots across 86 gates; 634 of the 676 ledger records sit
  in the quantum-experiment case directory.

## Contract

1. Retained bytes stay immutable. The v1 ledger, its 676 digests and its capped image identity remain
   the historical record of the capped path; a native baseline is a new file at a new path.
2. A record names its numeric identity: CPU model and flags, numpy dispatch targets, each OpenBLAS
   library and selected core, glibc and libm version, Python build, the loaded arithmetic objects'
   hashes, thread and worker counts, and an operation fingerprint
   (`scripts/numerics_fingerprint.py`). Two runs share an identity when every field matches.
3. Within one identity, a replay compares bytes; a mismatch there is a determinism defect.
4. Across identities, a replay keeps schema, integers, strings, categorical outputs, decisions and
   threshold classifications exact, and compares each float within a per-field absolute, relative or
   ulp bound with explicit rules for NaN, infinities and signed zero.
5. Every decision-bearing field carries its margin from the threshold or branch boundary it decides;
   a bound that reaches the margin fails closed.
6. Each audit reports, per record and identity, the exact, bounded, skipped and stale coverage with
   the last success time; a skip never counts as a pass.
7. Intel SDE serves as a scheduled transfer check for named Intel identities after a real-chip
   comparison has shown agreement, and as a diagnostic; it stays off the pull-request lane, whose
   affected gates run within 15 measured seconds.

## Migration

The plan record [native-numeric-replay](../state/plans/native-numeric-replay.json) carries the order,
acceptance and receipts:

- freeze the v1 ledger digest on its recorded arithmetic environment, so removing the caps from the
  gate environment leaves `ci/runner_image_records.py` and gate core-635 working;
- classify every replay root as float-free exact, identity-exact, cross-identity bounded or
  decision-bearing, expanding directories to files and tracing each producer closure;
- extend the numeric-stack probe of `ci/run_gates.py` to the full identity of the contract;
- locate the Zen 4/5 dose divergence with a staged hexadecimal-float trace on identical inputs
  (kept sums, `psi.T @ psi`, covariance sums, block `np.var`, `math.sqrt`, then PCHIP, inverse,
  `einsum` and `chi2.sf`), where the first unequal checkpoint names the operation class;
- build the semantic comparator with mutation tests that move a decision across each boundary;
- benchmark fixed-order arithmetic for the decision-bearing reductions the trace implicates, adopted
  only within its accuracy and wall-time budgets;
- write native baselines with receipts, switch the gate declarations and the successor ledger in one
  change, and remove `OPENBLAS_CORETYPE` and `NPY_DISABLE_CPU_FEATURES` from `ci/run_gates.py`,
  `ci/pr_checks.sh` and the workflows.

## Falsifiers

The contract fails if a decision or threshold classification changes while every declared float bound
and margin check passes, which shows the comparator omitted a decision dependency, or if two runs
within one declared identity differ in bytes, which shows the identity or order contract is
incomplete. Its cost claim fails if the scheduled identity matrix exceeds the audit's CI budget.

The adversarial review that derived this contract is
[archive/reviews/2026-10-30-native-numeric-replay-review.md](../archive/reviews/2026-10-30-native-numeric-replay-review.md).
