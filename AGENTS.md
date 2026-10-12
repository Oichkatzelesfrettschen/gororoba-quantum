# gororoba-quantum agent guide

This file carries the repository's own rules; the user-level agent guide
supplies what it leaves unstated. CLAUDE.md loads it.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only. Before any push, these exit 0:

The rank-sector image gate also uses the plotting-only pin
`matplotlib==3.11.2`, documented in [results/ripple/README.md](results/ripple/README.md).

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  ruff check gororoba_quantum scripts/python_call_graph.py scripts/left_mult_sign_rank.py \
    scripts/mod15_signed_multiplier_census.py scripts/associator_walsh_classes.py \
    results/live/verify_source_closure.py results/live/folded_raw_analysis.py \
    results/live/test_folded_raw_analysis.py results/local_compute/mixed_pub_client \
    results/local_compute/verify_evidence.py \
    results/local_compute/check_verify_evidence.py results/local_compute/cpu_branching_reuse_analysis.py \
    results/local_compute/n21_shared_predicate/probe.py results/local_compute/n21_shared_predicate/check_probe.py \
    scripts/render_ripple_visualization.py scripts/render_rank_sector_norms.py \
    scripts/review_folded_jobs.py scripts/render_folded_job_review.py \
    scripts/check_render_folded_job_review.py scripts/diagnose_qiskit_mock.py \
    scripts/check_diagnose_qiskit_mock.py \
    scripts/check_review_folded_jobs.py scripts/check_render_rank_sector_norms.py \
    scripts/check_render_ripple_visualization.py \
    scripts/extract_measured_ripple.py scripts/check_extract_measured_ripple.py \
    scripts/render_measured_ripple.py scripts/check_render_measured_ripple.py \
    docs/sources/open_gororoba/check_signed_kite_switching.py
  ruff format --check gororoba_quantum scripts/python_call_graph.py scripts/left_mult_sign_rank.py \
    scripts/mod15_signed_multiplier_census.py scripts/associator_walsh_classes.py \
    results/live/verify_source_closure.py results/live/folded_raw_analysis.py \
    results/live/test_folded_raw_analysis.py results/local_compute/mixed_pub_client \
    results/local_compute/verify_evidence.py \
    results/local_compute/check_verify_evidence.py results/local_compute/cpu_branching_reuse_analysis.py \
    results/local_compute/n21_shared_predicate/probe.py results/local_compute/n21_shared_predicate/check_probe.py \
    scripts/render_ripple_visualization.py scripts/render_rank_sector_norms.py \
    scripts/review_folded_jobs.py scripts/render_folded_job_review.py \
    scripts/check_render_folded_job_review.py scripts/diagnose_qiskit_mock.py \
    scripts/check_diagnose_qiskit_mock.py \
    scripts/check_review_folded_jobs.py scripts/check_render_rank_sector_norms.py \
    scripts/check_render_ripple_visualization.py \
    scripts/extract_measured_ripple.py scripts/check_extract_measured_ripple.py \
    scripts/render_measured_ripple.py scripts/check_render_measured_ripple.py \
    docs/sources/open_gororoba/check_signed_kite_switching.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" scripts/python_call_graph.py >/dev/null
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/verify_evidence.py
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/check_verify_evidence.py
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/cpu_branching_reuse_analysis.py --check
  (cd results/local_compute && sha256sum -c SHA256SUMS)
  (cd results/local_compute/aer_delay_sentinels && sha256sum -c SHA256SUMS)
  (cd results/local_compute/n21_shared_predicate && sha256sum -c SHA256SUMS)
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/n21_shared_predicate/check_probe.py
  PYTHONOPTIMIZE=1 PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/n21_shared_predicate/check_probe.py
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
    docs/sources/open_gororoba/check_signed_kite_switching.py | \
    cmp - docs/sources/open_gororoba/signed_kite_switching.json
  (cd docs/sources/open_gororoba && sha256sum -c SHA256SUMS)
  (cd results/live
    PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error -m unittest test_folded_raw_analysis
    PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error -m unittest test_folded_raw_analysis)
  (cd results/live/2026-10-12T055624.091217Z && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error results/live/folded_raw_analysis.py \
    results/live/2026-10-12T055624.091217Z | \
    cmp - results/live/2026-10-12T055624.091217Z/supplemental-shot-order.json
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_diagnose_qiskit_mock.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_diagnose_qiskit_mock.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_render_folded_job_review.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_render_folded_job_review.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_review_folded_jobs.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_review_folded_jobs.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_render_rank_sector_norms.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_render_rank_sector_norms.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_render_ripple_visualization.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_render_ripple_visualization.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_extract_measured_ripple.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_extract_measured_ripple.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/check_render_measured_ripple.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error scripts/check_render_measured_ripple.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error scripts/review_folded_jobs.py \
    --run-dir results/live/2026-10-12T055624.091217Z --check
  PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error \
    MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/folded-review-mplconfig}" \
    "$PYTHON" scripts/render_folded_job_review.py \
    --png results/ripple/folded-job-review.png --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error \
    results/local_compute/mixed_pub_client/probe.py >/dev/null
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error \
    results/local_compute/mixed_pub_client/probe.py >/dev/null
  (cd results/local_compute/mixed_pub_client
    PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error -m unittest check_probe
    PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error -m unittest check_probe
    sha256sum -c SHA256SUMS)
  cd gororoba_quantum
  mypy boolean_anf.py cd_core.py verify.py designs.py factoring.py \
    correction_circuits.py correction_circuits_contracts.py \
    correction_schedule.py correction_schedule_contracts.py \
    correction_statistics.py correction_statistics_contracts.py \
    correction_preparation.py correction_preparation_contracts.py \
    correction_planning.py correction_planning_contracts.py \
    correction_collection.py correction_collection_contracts.py correction_case_contracts.py \
    hybrid_shor.py modular_arithmetic.py compile_evidence.py packing.py \
    parallel.py predict.py select_lcu.py experiments.py live_run.py order_finding.py \
    runtime_contracts.py parameter_binding_contracts.py variance.py target_flip.py target_flip_certificate.py \
    qpe_diagnostics.py experiment_optimizer.py diagnostic_experiments.py \
    qpu_planning.py qpu_planning_contracts.py qpu_cases.py \
    qpu_case_allocation_contracts.py local_compute.py \
    algebra_planning.py algebra_planning_contracts.py \
    pub_shot_allocation.py pub_shot_allocation_contracts.py pub_shot_runtime_contracts.py \
    ripple_experiments.py ripple_contracts.py rank_sector_experiments.py rank_sector_contracts.py \
    native_preflight.py native_preflight_contracts.py \
    placement_feasibility.py placement_feasibility_contracts.py \
    aer_delay_sentinels.py \
    affine_residual.py affine_residual_challenger.py adjudicate.py claim_boundaries.py \
    sedenion_bundle.py annihilator_strata.py \
    rank_polynomials.py rank_charts.py rank_attachments.py \
    integral_homology.py rank_path_topology.py ripple_dynamics.py \
    four_support_rank.py four_support_geometry.py \
    four_support_doubling.py four_support_homology.py skew_schur_charts.py \
    principal_skew_atlas.py \
    schur_acceleration.py \
    ../scripts/python_call_graph.py ../scripts/left_mult_sign_rank.py \
    ../scripts/mod15_signed_multiplier_census.py ../scripts/associator_walsh_classes.py \
    ../results/live/verify_source_closure.py ../results/live/folded_raw_analysis.py \
    ../results/local_compute/verify_evidence.py \
    ../results/local_compute/check_verify_evidence.py ../results/local_compute/cpu_branching_reuse_analysis.py \
    ../results/local_compute/n21_shared_predicate/probe.py ../results/local_compute/n21_shared_predicate/check_probe.py \
    ../scripts/render_ripple_visualization.py ../scripts/render_rank_sector_norms.py \
    ../scripts/review_folded_jobs.py ../scripts/render_folded_job_review.py \
    ../scripts/check_render_folded_job_review.py ../scripts/diagnose_qiskit_mock.py \
    ../scripts/check_diagnose_qiskit_mock.py \
    ../scripts/check_review_folded_jobs.py ../scripts/check_render_rank_sector_norms.py \
    ../scripts/check_render_ripple_visualization.py \
    ../scripts/extract_measured_ripple.py ../scripts/check_extract_measured_ripple.py \
    ../scripts/render_measured_ripple.py ../scripts/check_render_measured_ripple.py \
    ../docs/sources/open_gororoba/check_signed_kite_switching.py
  "$PYTHON" verify.py       # needs the open_gororoba checkout at GOROROBA_ROOT
  "$PYTHON" designs.py
  "$PYTHON" claim_boundaries.py >/dev/null
  "$PYTHON" sedenion_bundle.py >/dev/null
  "$PYTHON" annihilator_strata.py --max-dimension 256 >/dev/null
  "$PYTHON" rank_polynomials.py >/dev/null
  "$PYTHON" rank_charts.py >/dev/null
  "$PYTHON" rank_attachments.py >/dev/null
  "$PYTHON" integral_homology.py >/dev/null
  "$PYTHON" rank_path_topology.py >/dev/null
  "$PYTHON" rank_path_topology.py --stage 6 >/dev/null
  "$PYTHON" ripple_dynamics.py --check ../results/ripple/evidence.json
  "$PYTHON" ../scripts/render_ripple_visualization.py \
    --evidence ../results/ripple/evidence.json \
    --out ../results/ripple/cayley-dickson-ripples.html --check
  PYTHONWARNINGS=error MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/rank-sector-mplconfig}" \
    "$PYTHON" ../scripts/render_rank_sector_norms.py \
    --png ../results/ripple/rank-sector-norms.png --check
  "$PYTHON" -W error schur_acceleration.py >/dev/null
  "$PYTHON" -O -W error schur_acceleration.py >/dev/null
  "$PYTHON" factoring.py
  "$PYTHON" target_flip.py
  "$PYTHON" target_flip_certificate.py --check
  "$PYTHON" affine_residual.py
  "$PYTHON" modular_arithmetic.py
  "$PYTHON" order_finding.py
  "$PYTHON" compile_evidence.py --seeds 20261010 \
    --candidate one_clean_cycle >/dev/null
  "$PYTHON" ../scripts/mod15_signed_multiplier_census.py
  "$PYTHON" ../scripts/associator_walsh_classes.py --max-dim 64 >/dev/null
  "$PYTHON" runtime_contracts.py
  "$PYTHON" parameter_binding_contracts.py
  "$PYTHON" correction_circuits_contracts.py
  "$PYTHON" correction_statistics_contracts.py
  "$PYTHON" correction_schedule_contracts.py
  "$PYTHON" correction_preparation_contracts.py
  "$PYTHON" correction_planning_contracts.py
  "$PYTHON" correction_collection_contracts.py
  "$PYTHON" correction_case_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_circuits_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_statistics_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_schedule_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_preparation_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_planning_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_collection_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" correction_case_contracts.py
  "$PYTHON" qpe_diagnostics.py
  "$PYTHON" experiment_optimizer.py
  "$PYTHON" qpu_planning_contracts.py
  "$PYTHON" algebra_planning_contracts.py
  "$PYTHON" pub_shot_allocation_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" pub_shot_allocation_contracts.py
  "$PYTHON" pub_shot_runtime_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" pub_shot_runtime_contracts.py
  "$PYTHON" ripple_contracts.py
  "$PYTHON" rank_sector_contracts.py
  "$PYTHON" native_preflight_contracts.py
  "$PYTHON" placement_feasibility_contracts.py
  PYTHONOPTIMIZE=1 "$PYTHON" placement_feasibility_contracts.py
  "$PYTHON" qpu_cases.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error qpu_case_allocation_contracts.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error qpu_case_allocation_contracts.py
  "$PYTHON" local_compute.py
  "$PYTHON" aer_delay_sentinels.py >/dev/null
  "$PYTHON" ../results/live/verify_source_closure.py --check
  "$PYTHON" variance.py
  "$PYTHON" adjudicate.py --check
  "$PYTHON" cd_core.py >/dev/null
  "$PYTHON" ../scripts/left_mult_sign_rank.py --max-n 8
  "$PYTHON" ../scripts/left_mult_sign_rank.py --max-n 5 --mutate high-low-unconditional
  "$PYTHON" ../scripts/left_mult_sign_rank.py --max-n 5 --mutate high-high-no-early-return
  "$PYTHON" hybrid_shor.py simulate 15 --shots 256 --seed 7
)
```

CPU-bound loops over independent items (embedding scores in replica
placement, operator checks, registry parsing) run through parallel.py, an
order-preserving process pool started with spawn on every platform, so a
parallel run returns exactly what the serial loop returns.
`GOROROBA_WORKERS=N` caps the worker count and `GOROROBA_WORKERS=1` runs
serially; the default is the CPUs available to the process. Aer runs batch
every replica of a choice in one call and parallelize experiments itself.

A change to live_run.py or experiments.py also gets a dry run,
`"$PYTHON" live_run.py --out ../results/live`, whose audit record lands under
results/live/.

The matched diagnostic families and statistical design contracts are documented
in [QPU_OPTIMIZATION.md](gororoba_quantum/QPU_OPTIMIZATION.md). Their local
gates exercise exact labeled laws, bounded inference, fake-backend layouts,
aggregate budgets, and negative dry-run records; hardware claims require
separately approved results.

The independently admitted packed ripple and rank-sector families are described
in [PACKED_ALGEBRA.md](gororoba_quantum/PACKED_ALGEBRA.md). `--native-dry-run`
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
pinned Rocq 9.1.1 toolchain. The replay compiles in temporary storage,
treats warnings as errors, kernel-checks, and compares raw assumptions.
The [bundle](docs/evidence/formal_certificates/README.md) distinguishes
real foundations, deterministic interval premises and unproved coverage.

## Source library and research replay

`docs/` owns source notes, retained PDFs, retrieval identities and research
replays. `literature -> docs` preserves recorded paths; new Markdown links use
`docs/`. Immutable source ledgers retain their recorded bytes. Source changes
also pass these local gates before push:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  ruff check --no-cache docs/verify_sources.py docs/check_verify_sources.py docs/evidence
  ruff format --check --no-cache docs/verify_sources.py docs/check_verify_sources.py docs/evidence
  MYPYPATH=docs mypy --explicit-package-bases docs/verify_sources.py docs/check_verify_sources.py docs/evidence
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/verify_sources.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/verify_sources.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/check_verify_sources.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/check_verify_sources.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/local_schur/probe.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/local_schur/probe.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/folding_proofs/fold_projection_counterexamples.py | cmp - docs/evidence/folding_proofs/fold_projection_counterexamples.json
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/folding_proofs/fold_projection_counterexamples.py | cmp - docs/evidence/folding_proofs/fold_projection_counterexamples.json
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/four_support_rank/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/four_support_rank/replay.py --check
  (cd docs/evidence/four_support_rank && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/four_support_geometry/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/four_support_geometry/replay.py --check
  (cd docs/evidence/four_support_geometry && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/four_support_doubling/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/four_support_doubling/replay.py --check
  (cd docs/evidence/four_support_doubling && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/four_support_homology/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/four_support_homology/replay.py --check
  (cd docs/evidence/four_support_homology && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/dimension32_skew_schur/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/dimension32_skew_schur/replay.py --check
  (cd docs/evidence/dimension32_skew_schur && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/principal_skew_atlas/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/principal_skew_atlas/replay.py --check
  (cd docs/evidence/principal_skew_atlas && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/schur_acceleration/replay.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/schur_acceleration/replay.py --check
  (cd docs/evidence/schur_acceleration && sha256sum -c SHA256SUMS)
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/folding_proofs/check_compiler_gate.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/folding_proofs/check_compiler_gate.py
  shellcheck docs/evidence/folding_proofs/replay_rocq.sh
  shellcheck docs/evidence/formal_certificates/replay_rocq.sh
  (cd docs/evidence/formal_certificates && sha256sum -c SHA256SUMS)
  sha256sum -c docs/evidence/formal_certificates/source_hashes.sha256
  (cd docs/evidence/local_schur && sha256sum -c SHA256SUMS)
  (cd docs/evidence/folding_proofs && sha256sum -c SHA256SUMS)
)
```

Changes to proof replay inputs also follow the pinned Rocq replay in
`docs/evidence/folding_proofs/README.md`. Imported paper parser diagnostics
remain source limitations in the registry; checksum admission preserves the
original bytes and differs from a fresh mathematical proof check.

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. The case is written against a submit-free dry run, and the
  `--submit` command names that run with `--approved-record`, its record.json
  digest with `--approved-record-sha256`, and the case's seconds with
  `--max-execution-seconds` (the Sampler's max_execution_time, which the
  service enforces; the dry run is made with the same value, since the
  policy carries it). `--max-total-execution-seconds` caps the sum of all
  job ceilings, and `--reserve-seconds` names the retained quota. The fresh
  plan must match the record in experiment
  digest, shots, policy (twirling, DD, budget floor, execution ceiling),
  dependency versions, IBM Cloud instance, groups, backends, seeds, layouts,
  replica qubits, fused PUB manifests, calibration at the refresh and again
  at each batch, and QPY bytes, or the run writes an `approval_required`
  record and sends nothing. The first batch consumes the approval by writing
  `approval-consumed.json` into the approved record's directory, so a second
  invocation on the same record sends nothing. Calibration reads,
  transpilation, noise simulation, result retrieval, and `--preserve-raw`
  need no approval.
- Calibration is a property of the run. live_run.py fetches each backend's
  Target and properties afresh in the process that decides, compiles,
  simulates, and submits; no calibration value is cached or read back from a
  file to drive a submission.

## Qiskit skills

The Qiskit agent skills come from https://github.com/Qiskit/skills, installed
by copy into `~/.claude/skills/`:

| skill | installed path | upstream commit |
|---|---|---|
| migrate-qiskit-ibm-runtime | `~/.claude/skills/migrate-qiskit-ibm-runtime/` | a5499c7c24f51633cbd0a5e7ea5902841e5b983e |

Upstream also publishes them as a Claude Code plugin:
`/plugin marketplace add Qiskit/skills`, then
`/plugin install qiskit-ai-skills@qiskit`.

**Monthly check.**
1. Compare `git ls-remote https://github.com/Qiskit/skills HEAD` with the
   pinned commit above.
2. On a difference, clone the new commit into a scratch directory and read
   every changed or added file in full before installing: skills are
   instructions an agent executes, so they get the review any code gets.
3. Copy the skill directories into `~/.claude/skills/`, update the table above
   in a PR, and rerun the audit below. A new skill on the upstream roadmap
   (mitigation evaluation, layout selection, circuit optimization) also gets a
   written decision on whether it replaces anything in live_run.py.

**When to invoke.** Run `/migrate-qiskit-ibm-runtime` with scope
gororoba_quantum/ in these cases, and follow its phases, grounding, and report
format:
- any change that touches qiskit-ibm-runtime: primitives, options, jobs,
  service, backends, sessions, or batches;
- any change to the qiskit-ibm-runtime pin in requirements.txt;
- after every monthly skill update.

The skill sets the destination as the client-side
`qiskit_ibm_runtime.executor_sampler.Sampler` from runtime 0.50.0. It forbids
inventing an API path that its guides and the API reference do not enumerate,
so such a path is validated at run time and named in the error when absent.

**Rules the audit established.** The skill's local verification ran circuits
through the client-side Sampler and established the job split live_run.py
uses. In runtime 0.50, gate twirling sends circuits through samplomatic
boxing, which rejects `if_else`, and IBM's Sampler rejects dynamical
decoupling on dynamic circuits. So live_run.py sends circuits with
mid-circuit measurement, reset, or feed-forward in their own job, with
twirling and dynamical decoupling off.

## Reviews and merges

Codex, the chatgpt-codex-connector app, supplies the default pull-request
review. It reviews on open, and an issue comment `@codex review` requests a
review of the current head.

When the hosted Codex app reports exhausted code-review quota, request Copilot
instead. The user authorizes that substitution. Submit a REST review request
to `pulls/PR/requested_reviewers` with
`{"reviewers":["copilot-pull-request-reviewer[bot]"]}` and verify that the
`copilot-pull-request-reviewer` check starts. An empty `requested_reviewers`
response can accompany an accepted request; the check confirms execution.
Read the completed Copilot review and every review thread. Admission requires
a review by that app on the current commit, zero open findings, a successful
current-commit Copilot check, and resolved review threads. General expert-review
cautions retain their scientific scope; concrete findings require the same
triage and fixes below. The Codex status script reports Codex clean signals;
Copilot admission uses its REST reviews/checks and GraphQL review threads.
Return to the default reviewer when hosted Codex review becomes available.

- *Progress.* The bot keeps one summary comment per PR, marked
  `codex-pull-request-review-summary`, which reads Running while a review is in
  progress.
- *Outcome.* A review with findings publishes inline review comments with P1 or
  P2 badges. A clean review either posts an issue comment beginning "Codex
  Review: Didn't find any major issues" with a reviewed commit matching the PR
  head, or adds an app-owned `+1` reaction after the completed summary update
  for the current head. A prior reaction cannot qualify a later review round.
- *Status tool.* `scripts/codex_review_status.sh PR...` prints each PR's head,
  summary head, review state, and head-bound clean signal, then every unresolved
  thread with its root comment id and full body. It accepts comments and
  reactions only from the stable app and bot identities, requires the clean
  comment to follow the current review request and the reaction to occur
  strictly after the completed summary update. It paginates every issue,
  reaction, thread, and thread-comment connection, then re-reads the head and
  PR update marker, and summary to reject a changing snapshot.

**One round, per PR:**
1. Wait until the selected review completes: the Codex summary stops reading
   Running, or the Copilot check completes. Then read every unresolved thread
   in full from `codex_review_status.sh` or the GraphQL thread connection.
   Threads can arrive between rounds and attach to the newest commit, so the
   open-thread list,
   not memory of the last round, is the work queue.
2. Triage each thread against reachability.
   - A defect a user reaches through a documented interface (the CLI, the
     record files the program writes, the default flow) gets a fix.
   - A claim the source refutes gets the refuting line in the reply.
   - Malformed or adversarial input outside the documented domain gets a reply
     naming the boundary and a follow-up issue.
3. Fix every reachable thread on the PR's own branch in one commit, and run the
   gates. A change to live_run.py or experiments.py also gets a live dry run,
   and a change to qiskit-ibm-runtime usage also gets `/migrate-qiskit-ibm-runtime`.
   Then push.
4. Reply to each thread's root comment with
   `gh api repos/OWNER/REPO/pulls/PR/comments/ID/replies -f body=...`. The reply
   begins with one of three markers, then says what changed or why:
   - `Fixed in <commit>`
   - `Refuted:` followed by the refuting source line
   - `Boundary:` followed by the documented limit and the follow-up issue
5. Run `scripts/resolve_answered_threads.sh PR`. It resolves only threads
   carrying a reply from the authenticated operator that begins with one of
   those markers, and lists every other open thread as unanswered. A comment
   such as "will fix" or a question resolves nothing. Never resolve a thread
   whose finding has not been read and answered.
6. Request the selected reviewer again and start at step 1. A PR leaves the
   loop when the current-head Codex status reports `verdict=clean-comment...`
   or `verdict=clean-reaction...`, or the authorized Copilot admission above
   passes, and every review thread is resolved.

**Stacked PRs.**
- Each branch builds on the one below it, so a fix lands on the lowest branch
  that holds the code and then merges upward, branch by branch, with
  `git merge --no-ff`.
- Rebasing is out because the permission harness denies force-push.
- When one file conflicts heavily, take the lower branch's reviewed version and
  re-apply the upper branch's own changes on top. Then rerun the gates and a dry
  run on every branch the merge touched.

**Merging.** A PR merges when its latest review is clean, every thread is
resolved, and GitHub reports mergeable_state clean. Bottom-up, for each PR:
1. Merge it with a merge commit:
   `gh api -X PUT repos/OWNER/REPO/pulls/PR/merge -f merge_method=merge`.
2. Retarget the next PR to main: `gh api -X PATCH repos/OWNER/REPO/pulls/NEXT -f base=main`.
   Deleting a base branch closes every PR that targets it, so the retarget
   comes first.
3. Delete the merged remote branch:
   `gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH`.
4. Pull main in the primary checkout, then `git worktree remove` and
   `git branch -d` the merged branch.

**API use.** Everything goes through REST with `gh api`, except review
threads, which only GraphQL exposes: both scripts list them through the
reviewThreads connection, and resolution uses resolveReviewThread and
unresolveReviewThread.

## Records

- results/ holds audit records: hw_estimate/ for the fixed ibm_fez compile and
  live/ for live runs.
- A collected run keeps its lossless result under `raw/<job_id>/` (every
  classical register as shot-ordered bit strings, each PUB's metadata with
  the backend scheduler table, the result metadata, the job metrics, and an
  index of sha256s), written by `--collect` before any analysis and
  recoverable with `--preserve-raw DIR` for a record collected under an
  earlier revision. collect.json is the preregistered analysis at the run's
  experiment digest; `adjudicate.py DIR` writes adjudication-<digest>-seed<seed>.json, a second
  analysis of the same raw files named by its own analysis digest, beside
  any earlier one. Raw files
  are never rewritten by a later collection or analysis.
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers, and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`.
