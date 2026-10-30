# Native numeric paths and retained-record replay: adversarial review

Adversarial review by Codex CLI (gpt-daybreak-blue-latest, low effort), read-only, of the brief to keep byte-replay gates once producers and CI runners compute on native numeric paths. Line citations refer to the tree at origin/main 66d92ca plus the cap-removal working diff of branch ci/openblas-native-kernel. The design that adopts it is [design/native-numeric-replay.md](../../design/native-numeric-replay.md).

## Verdict

`Native everywhere` and universal cross-platform byte replay cannot both be repository invariants. Native dispatch deliberately permits different OpenBLAS kernels, NumPy SIMD reductions, LAPACK implementations, and libm functions to associate or round the same computation differently. `ci/replay_check.py` then demands identical `float.hex()` values, including the sign of zero (`ci/replay_check.py:56-61`). The AMD EPYC 9V74 and 9V45 failures under both old caps already falsify the premise that an AVX2 OpenBLAS label plus an `X86_V3` NumPy label defines one arithmetic path (`docs/PYTHON.md:333-358`).

The repository should adopt a hybrid contract: preserve immutable retained bytes; require byte-exact replay only inside a fully specified numeric-path equivalence class; require exact schemas, integers, strings, decisions, and threshold classifications across classes; compare non-decision floats under field-specific error bounds backed by decision-margin certificates; and replace only evidence-critical reductions with fixed-order arithmetic where measurement shows that the cost is acceptable. Platform coverage becomes an explicit, freshness-bounded audit result. Intel SDE remains a diagnostic and an Intel-path transfer check, never a substitute for AMD execution.

This recommendation explicitly rejects owner rule 2 in its universal form. An AVX-512 result from a named Intel path may be replayed under a matching SDE model after native-versus-SDE equivalence has been measured. Intel SDE cannot replay an AMD Zen 4 or Zen 5 path (`docs/PYTHON.md:312-329`), so "CI has AVX-512" does not supply a sufficient replay identity.

## Findings

### FATAL: the current design assigns a platform-independent meaning to platform-dependent bytes

The runner-image ledger binds 676 paths to one image digest, and the digest includes the arithmetic environment (`ci/runner_image_records.py:65-86`, `ci/runner_image_records.py:102-116`). The ledger stores only `path -> sha256`; it records neither a per-record producer nor an operation class. The replay checker claims exact floats because the image and caps establish one arithmetic path (`ci/replay_check.py:5-15`). Removing the caps invalidates that premise while retaining the exact comparator.

The failure is conceptual rather than an unlucky runner. A native computation can be reproducible on each path while producing different correct roundings across paths. Byte identity therefore proves deterministic reproduction only within an arithmetic identity class. Cross-class byte inequality alone proves neither a producer defect nor scientific disagreement.

Remedy: split exact same-class reproduction from cross-class semantic stability. Bind every decision-bearing record to producer identity, inputs, runtime and library identities, actual dispatch, thread/order settings, and comparator contract.

### FATAL: platform matching by `AVX-512` or CPU model is too coarse

The numeric-stack probe records the CPU model, the presence of `avx512f`, aggregate enabled NumPy dispatch targets, and each loaded OpenBLAS core (`ci/run_gates.py:74-98`). Those fields omit the selected implementation for each reduction or ufunc, glibc and libm identity, loaded-object hashes, microcode, and operation-specific LAPACK paths. The same advertised AMD model passed in one run and failed in another, so CPU model alone is already an inadequate key.

The dose producer exercises several independent surfaces. NumPy reduces `keep`, `weighted`, covariance, and blocks; `psi.T @ psi` performs the covariance product; `np.var` measures block dispersion (`scripts/n21_dose_decisions.py:164-186`). Later stages use PCHIP (`scripts/n21_dose_decisions.py:303-309`), inverses, `einsum`, matrix products, and SciPy chi-square survival functions (`scripts/n21_dose_decisions.py:377-416`). A single `Haswell` label cannot certify all of those paths.

Remedy: define equivalence from observed runtime and operation fingerprints, not marketing-level ISA labels. Treat fingerprints as admission evidence rather than proof that unprobed operations agree.

### SERIOUS: the old caps never established cross-CPU identity

The retained dose record isolates OpenBLAS as one cause under Intel emulation: changing the OpenBLAS core moves 85 fields, while changing the NumPy cap moves none (`docs/PYTHON.md:333-347`). The capped Intel Xeon 8573C replay passed, but capped AMD 9V74 and 9V45 replays moved 95 fields; one sigma matched the uncapped Intel result and another matched no emulated result (`docs/PYTHON.md:348-358`). The evidence narrows the search but does not identify one cause.

The earliest reported differing `.sigma` belongs to the measurement covariance path. Its inputs flow through NumPy sums, `psi.T @ psi`, covariance sums, block `np.var`, and finally `math.sqrt` (`scripts/n21_dose_decisions.py:164-186`, `scripts/n21_dose_decisions.py:350-364`). PCHIP and the later generalized least-squares fits cannot cause an already different sigma. Candidate causes remain an operation-specific NumPy reduction, an OpenBLAS path hidden by a coarse architecture label, libm `sqrt`, or an unrecorded build or host difference. Code inspection does not justify choosing among them.

Remedy: run one diagnostic staged trace on identical retained inputs in a passing reference and a failing AMD job. Hash the raw arrays and emit hexadecimal floats after `kept`, `weighted.sum`, `means`, `psi`, `psi.T @ psi`, covariance sums, block `np.var`, contract covariance, arm variance, and `sqrt`; continue through PCHIP, inverse, `einsum`, matrix multiplication, and `chi2.sf`. Record loaded-object build IDs and hashes, glibc, the full NumPy feature map, OpenBLAS files, CPU flags, and microcode. The first unequal checkpoint locates the responsible operation class.

### SERIOUS: the existing AVX-512 helper does not cover every byte replay

`ci/avx512_replay.sh` selects only gate commands that contain `ci/replay_check.py` (`ci/avx512_replay.sh:29-38`). The ledger validator also recognizes `cmp` and `--out` plus `--check` or `--replay` forms (`ci/runner_image_records.py:154-179`). The current helper therefore selects three gates, despite its comment claiming every byte-replay gate. The ledger has replay declarations across 86 gates and 101 declared replay roots; 634 of its 676 bound files belong to the quantum-experiment case directory. Repeating three gates on each AVX-512 shard cannot establish ledger-wide AVX-512 coverage.

Remedy: derive platform-coverage cases from the ledger declarations and comparator classes, then report covered, mismatched, and not-run cases separately. A successful shell exit after a platform skip cannot count as replay evidence.

### SERIOUS: SDE is bounded evidence, not a universal oracle

SDE presents a selected Intel CPUID and executes the corresponding instruction set, but cache sizes, core counts, and timing remain those of the host; library blocking can still differ (`docs/PYTHON.md:319-329`). SDE emulates Intel chips only (`docs/PYTHON.md:312-318`). The measured cost is 12.8 seconds for NumPy import and 147 seconds for a dose replay that takes about 5 seconds natively (`docs/PYTHON.md:330-331`).

For the three helper-selected gates, the manifest estimates total 9.9 native seconds. Applying the observed 30-fold factor estimates about 297 seconds per emulated job. Three emulated jobs would add about 14.9 billed runner-minutes and roughly five minutes to their critical paths; the dose gate alone costs 7.35 runner-minutes across three jobs. These are estimates, not measurements of an SDE-wrapped gate set. Adding SDE to the pull-request lane would also conflict with its affected-gate ceiling of 15 measured seconds (`ci/pr_checks.sh:91-104`).

Remedy: keep SDE off the required pull-request path. Use it for scheduled Intel transfer checks and root-cause diagnostics after measuring equivalence against the named real Intel path.

### SERIOUS: tolerance without a decision contract would launder numerical changes

The repository already uses a bounded cross-path comparison for the local idle falsifier: it keeps exact structure, computes the largest numeric deviation, and rejects deviations above `1e-9` (`scripts/local_idle_falsifier.py:215-260`). That precedent proves tolerance replay can be explicit. A global tolerance applied blindly to all floats would still be unsound. A one-ulp perturbation can flip a strict threshold, an argmin, an interval endpoint, or a verdict even when every scalar looks close.

Remedy: assign tolerances by field and scale; define non-finite and signed-zero behavior; keep discrete results exact; and retain the distance from every decision boundary. Fail when the error allowance overlaps a boundary. Tolerance then proves bounded semantic stability, not byte determinism.

### SERIOUS: the current ledger transition forces an unnecessary 676-record rewrite

Changing the arithmetic environment changes the image digest. The v1 ledger reports every old record as written under the old image (`ci/runner_image_records.py:126-150`) and `add` refuses the new image unless the command supplies every previously bound path (`ci/runner_image_records.py:301-321`). Retained bytes are immutable, so overwriting 676 paths to satisfy a new digest would conflate a new native baseline with the historical capped evidence.

Remedy: migrate the schema and comparator metadata before switching the digest. Preserve the v1 ledger and old paths as historical evidence. New native baselines use new paths and receipts.

### SLOPPY: the stated runner inventory has an unresolved denominator

The brief describes 12 shards but enumerates nine EPYC 7763 jobs, one Xeon 8573C job, and one EPYC 9V45 job: 11 jobs. The same brief describes the 7763 share as about 75%, which implies 9 of 12 and leaves one CPU unspecified. Coverage arithmetic can use the stated 9/12 share, but a report cannot invent the twelfth CPU.

Remedy: retain the per-job numeric-stack artifact and calculate coverage from all 12 observed job identities for each audit.

### SOUND: the repository already separates order, threads, and provenance in useful ways

The gate environment sets native-library thread counts to one (`ci/run_gates.py:263-296`). The producer pools independent members in a stable order (`scripts/n21_dose_decisions.py:198-218`). The ledger binds image inputs and arithmetic variables and refuses unreceipted additions (`ci/runner_image_records.py:246-321`). Those mechanisms establish valuable same-path determinism and provenance. They simply cannot promote one path's floating representation into a universal numerical invariant.

## Operation classes and affected records

The ledger does not contain enough provenance to exhaustively label all 676 records by operation class. `ci/runner_image_records.py` states that fitted bytes can depend on libm, Python, NumPy, SciPy, and OpenBLAS (`ci/runner_image_records.py:1-11`), but stores a path and digest rather than the producer closure. The following map is the evidence available from direct producer reads.

| Operation class | Code evidence | Bound-record examples and consequence |
|---|---|---|
| BLAS level 3/2 and LAPACK | `psi.T @ psi`, vector products, and covariance sums occur in the dose producer (`scripts/n21_dose_decisions.py:164-195`); later fits use inverse and matrix products (`scripts/n21_dose_decisions.py:377-416`). | `results/live/2026-10-27T014354.701394Z/dose-decisions.json`; OpenBLAS core selection demonstrably moves 85 fields under SDE. Small `@` operations require a call trace before being labelled BLAS rather than a NumPy kernel. |
| NumPy SIMD ufuncs and reductions | Dose means, sums, variance, and `np.sum` occur throughout the measurement and model paths (`scripts/n21_dose_decisions.py:164-186`, `scripts/n21_dose_decisions.py:283-299`). The numeric fingerprint exercises NumPy exp and power, stacked products, matrix power, and production fits (`scripts/numerics_fingerprint.py:77-105`). | Dose decisions and measurement-sequence records. The repository measured five of eleven default AVX-512 fingerprint digests differing from the build host (`docs/runbooks/vectorized-fits.md:289-295`). |
| libm and SciPy transcendental or special-function paths | The dose producer uses `math.sqrt` for sigma and SciPy `chi2.sf` for fit probabilities (`scripts/n21_dose_decisions.py:350-386`). | Dose decisions; measurement-sequence and cancellation analyses also contain `math.exp`, `math.pow`, `sqrt`, or SciPy statistics. These paths remain outside both old NumPy and OpenBLAS caps. |
| Pairwise or SIMD-width-dependent association | NumPy sums, means, and variances in the dose path can change association with implementation width (`scripts/n21_dose_decisions.py:164-186`). The repository measured `einsum` disagreeing with stacked `@` in 25,108 of 65,536 values (`docs/runbooks/vectorized-fits.md:281-285`). | Any bound fitted record using NumPy reductions, including dose and measurement-sequence outputs. One thread prevents threaded BLAS reordering; it does not fix NumPy's internal association. |
| Explicit fixed-order scalar arithmetic | Some producers deliberately use compensated or fixed scalar arithmetic; the vectorized-fit rule requires scalar arithmetic order, Neumaier compensation, and `math.exp` or `math.pow` (`docs/runbooks/vectorized-fits.md:269-277`). | These records reduce association risk, but libm remains part of the identity. The fixed-order rule should be extended only to decision-bearing reductions whose benchmark supports it. |
| Predominantly structural serialization | The quantum-experiment case replay root accounts for 634 bound files: 384 circuit files and 250 JSON files. Its producer uses matrix products and `math.sqrt` while constructing and checking cases, so the directory cannot be declared float-independent without field-level inspection. | The large count makes an undifferentiated 676-record rewrite expensive and scientifically uninformative. Inventory comparator needs before regeneration. |

## Candidate designs

| Design | What the design actually proves | Nightly coverage | Cost and latency | Maintenance and failure modes |
|---|---|---|---|---|
| Platform-matched replay under SDE | Exact reproduction under an emulated named Intel CPUID, fixed userland, and fixed thread/order settings; real-chip equivalence only after measurement. | Intel paths only. AMD Zen 4/5 coverage is zero. | About 30 times native in the measured dose case; roughly 297 seconds for the current three helper-selected gates by manifest estimate. | SDE installation and model selection; cache/core topology mismatch; no AMD model; false confidence from matching an ISA label. |
| Skip on mismatch | Exact replay retains its honest meaning when a matching runner appears. | A Zen 3/host record gets about 9/12, or 75%, coverage per ordinary one-shard gate under the stated mix. Repeating a case on all 12 jobs would make at least one match likely, but ordinary gates are sharded once. | Nearly free. | Silent evidence aging if skip exits green. Requires a coverage service-level objective and a red stale-coverage result. |
| Per-platform records | Conformance of each blessed numeric identity to its own baseline. | Native and cheap when a matching record exists; unavailable for AMD identities without real AMD hardware. | Record creation and storage multiply by identity count. | Baseline explosion; platform identity drift; contradictory decisions can be accidentally blessed; immutable corrections require new paths. |
| Tolerance replay | Bounded numerical stability across paths. | All native runners. | Lowest recurring cost; developer feedback remains native. | Unsound without field-specific bounds, exact discrete outputs, non-finite rules, and decision margins. Does not prove byte determinism. |
| Producer-side deterministic arithmetic | Cross-platform identity for the operations actually rewritten and tested. | All paths covered by the conformance matrix. | Unknown until measured. Fixed scalar or compensated reductions can be much slower than optimized BLAS; replacing every BLAS/libm path is disproportionate. | New arithmetic needs an accuracy oracle, mutation tests, and performance budgets. A fixed reduction does not standardize transcendental functions. |
| CI-produced AVX-512 record plus host SDE | Transfer between one real Intel producer and its measured SDE counterpart. | Intel AVX-512 only; runner draw controls production. | A 147-second host dose replay versus about 5 seconds native, plus acquisition delay. | Cannot represent AMD; host emulation is not nightly native coverage; new runner models require validation. |
| Hybrid: exact within class, semantic across classes, fixed order at decision bottlenecks | Same-class deterministic reproduction, cross-class scientific stability, and exact decision preservation. | Every native runner contributes semantic coverage; exact coverage is reported per identity and freshness window. | Native PR latency; scheduled same-class/SDE checks; targeted fixed-order overhead only where justified. | Requires schema and comparator inventory, but avoids record multiplication for irrelevant float formatting. |

The skip probability deserves careful wording. If runner draws were independent with a 75% match probability and all 12 jobs repeated the same replay, the probability of at least one match would be `1 - 0.25^12`, about 99.999994%. The current sharding does not provide that experiment for ordinary gates. Likewise, assuming a 25% AVX-512 probability would give `1 - 0.75^12`, about 96.83% for at least one AVX-512 job; one observed night and an unspecified twelfth CPU do not justify either the independence or the probability.

## Consistent formulation and minimal invariants

The consistent first-principles formulation is: every producer runs natively; immutable bytes describe the result of that named execution identity; byte replay is required only when the checker belongs to the same measured equivalence class; and other identities must reproduce the scientific semantics under a declared error contract.

The minimal invariants are:

1. Immutable input and output bytes with digests and retained historical linkage.
2. Producer source, dependency, Python, NumPy, SciPy, OpenBLAS, glibc/libm, and loaded-object identity.
3. Observed CPU model and flags, operation fingerprint, NumPy dispatch, OpenBLAS core, thread counts, worker count, reduction order, and seed provenance.
4. Byte-exact values within a validated identity class.
5. Exact schema, integers, strings, categorical outputs, decisions, and threshold classifications across classes.
6. Per-field absolute, relative, or ULP bounds for cross-class floats, including rules for NaN, infinities, and signed zero.
7. A retained margin from each threshold or branch boundary larger than the admitted numerical error; overlap fails closed.
8. Explicit platform coverage with last-success time, rather than a successful skipped check.

## Recommendation and migration order

Adopt the hybrid design. The design retains native performance and exposes actual platform variation, preserves byte replay where byte replay has a coherent meaning, and makes the scientific contract stronger than an accidental serialization match.

Migration should proceed in this order:

1. Freeze the v1 ledger, its 676 digests, and its capped image identity as historical evidence. Do not rewrite those paths.
2. Extend a successor ledger schema with producer, numeric identity, comparator class, decision fields, thresholds, margins, and coverage freshness. Keep v1 readable during migration.
3. Inventory every replay root as float-free exact, same-class byte exact, cross-class bounded, or decision-bearing. Expand directories to files and trace producer closures; the current ledger cannot supply this classification.
4. Add semantic comparators before removing exact coverage. Require exact non-floats and decisions, field-specific float bounds, and threshold-margin checks. Add mutation tests that move a decision across each boundary.
5. Add the staged dose diagnostic on passing and failing runners to locate issue 679. Record the first divergent intermediate and loaded arithmetic objects; keep the trace diagnostic rather than altering retained evidence.
6. Benchmark fixed-order alternatives for the decision-bearing reductions identified by the trace. Adopt them only when they meet accuracy, byte-conformance, and wall-time budgets. Retain optimized native BLAS for non-critical work.
7. Produce new native records at new mechanism-named paths, with receipts, on each available identity. Validate same-class bytes and cross-class decisions before changing gate declarations.
8. Switch gate declarations and the successor ledger atomically. Report each audit's exact, semantic, skipped, and stale platform coverage. Schedule measured Intel SDE transfer checks separately from required pull-request gates.
9. Retire a historical exact gate only after its successor covers the same scientific claim and the retained map links both artifacts.

## Falsifiers

The decisive recommendation test is a matrix over the same retained inputs on Zen 3 native, Intel AVX-512 native, matched Intel SDE, and AMD Zen 4 or Zen 5 native. Repeat every decision-bearing producer and measure wall time, byte equality inside each declared class, cross-class float errors, decision margins, and exact categorical outputs.

The recommendation is falsified if any exact decision or threshold classification changes while every declared float bound and margin check passes, or if two reruns inside one declared identity class fail byte equality. The first outcome proves that the semantic comparator omitted a decision dependency; the second proves that the identity or order contract is incomplete. The performance part is falsified if the scheduled semantic and same-class matrix exceeds its measured CI budget or if fixed-order decision reductions exceed their declared developer-latency budget without buying cross-platform stability.

The single measurement that locates the AMD failure is the staged hexadecimal-float and array-hash trace described above. Divergence at `psi.T @ psi` implicates the product path; divergence at covariance sums or `np.var` implicates reduction association; equal variance with unequal sigma implicates `sqrt`; equality through sigma moves the investigation to PCHIP, LAPACK, `einsum`, matrix products, or SciPy special functions. A whole-record diff cannot make that distinction.

## Steelman

The owner's native-everywhere rule correctly refuses to suppress available hardware and correctly demands that AVX-512 paths receive real scrutiny. The immutable-byte rule also protects provenance, and exact replay remains the strongest cheap detector of unannounced same-path drift. The defensible version combines those strengths without pretending that IEEE-754 specifies one association, one libm, or one BLAS kernel across machines: native execution produces path-specific bytes, exact replay guards that path, and semantic invariants guard the science across paths.
