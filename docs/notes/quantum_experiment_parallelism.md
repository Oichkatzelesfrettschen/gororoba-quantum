# Parallel experiments: prior work, scientific controls and integration gates

This note connects the existing literature collection to experiments that
share qubits in space and quantum time across useful endpoints. [P] identifies
published results through linked source notes; [I] identifies synthesis or
proposed repository work; [H] identifies retained hardware observations.
The [canonical claim ledger](prior_work_synthesis.md) retains experiment
priority. These connections add design candidates and acceptance gates;
they grant zero QPU execution approval.

## Read and reuse the existing foundations

| Engineering question | Sources | Established mechanism and bounded reuse |
| --- | --- | --- |
| Which workloads and regions should share a shot? | [Das](das-2019-multiprogramming.md), [QuMC](2102.05321.md), [palloq](2112.07091.md) | [P] Reliability-aware concurrency, calibrated partitions, scheduling and physical buffers precede this repository. [I] Reuse the mechanisms while qualifying Heron-specific timing and context effects. |
| Can one shot collect several required endpoints? | [CQCS](2109.01714.md), [QuCP](2112.00387.md) | [P] Concurrent copies, distinct VQE measurement settings and folded ZNE circuits have prior art. [I] Price endpoint acquisition separately from any claimed gain in effective independent samples. |
| How does neighboring activity change the target? | [Simultaneous RB](1204.6308.md), [context dependence](1810.05651.md), [crosstalk detection](1908.09855.md) | [P] Solo/simultaneous comparisons and independently varied neighboring contexts detect operational changes. [I] Preserve identical target mapping and controlled timing. |
| How can layout and drift be separated from intervention? | [Drift](1907.13608.md), [NIST blocking and Latin squares](quantum_experiment_design_sources.md) | [P] Shot-order analysis and balanced treatment assignment address different nuisance effects. [I] A patch/time crossover needs explicit interaction and execution-order treatment. |
| Which composition tools and usage model already exist? | [Qiskit and IBM documentation](quantum_experiment_design_sources.md) | [P] Parallel, batch and tiled experiments have distinct contracts; billing includes repetition and overhead. [I] Verify exact ISA, register, delay and approval semantics before adopting abstractions. |
| Does cubic Walsh sampling establish a hard task? | [IQP hardness](1504.07999.md), [Boolean hidden shift](0811.3208.md), [hidden-shift algorithms](1103.3017.md) | [P] Hardness and oracle-algorithm results have explicit instance and access assumptions. [I] Structured associator instances require their own classical comparison. |

## Preserve three result types

1. [I] Classical research can establish algebraic identities, exact finite
   classifications, proof certificates and cheaper synthesis. The
   [Cayley-Dickson source notes](../README.md) and
   [claim boundaries](../../gororoba_quantum/CLAIM_BOUNDARIES.md) already
   distinguish finite evidence, formal proof and candidate general results.
2. [I] Hardware research can identify model residuals, schedule effects,
   context sensitivity, or a control intervention that improves a specified
   endpoint. Classically predicted validation instances are appropriate for
   that task. The machine supplies physical evidence absent from the algebra.
3. [I] Computational advantage requires a defined output task and a complete
   resource comparison. Preparation, synthesis, shots, decoding and justified
   amortization remain in the ledger. Degree, occupied-qubit count, non-Clifford
   gates and quantum samples each provide narrower facts than an advantage claim.

## What the implementation and retained hardware already establish

- [I] `packing.pack` replicates an experiment and `packing.fuse` combines
  different experiments on disjoint qubits. `live_run.allocate_fusion_replicas`
  and `execution_pubs` provide the generic joint-placement/fusion path.
  Label: implementation of established multiprogramming techniques.
- [H] The [retained dynamic run](../../results/live/2026-10-11T152922.787095Z/ADJUDICATION.md)
  has a primary circuit with three folded-QPE and six hybrid-Shor replicas
  occupying 45 qubits. Its complete six-PUB job at 4096 shots/PUB charged
  nine seconds. The primary's nine streams added 187 dt, or 0.748 us, over
  the two-stream reference; the average execution cost was 250 us repetition
  delay plus 22.9 us circuit time. These observations belong to that workload.
- [H] The folded-QPE packing-equivalence result depends on the interval:
  the preregistered interval lies within the 0.03 margin, while the retained
  distribution-free Hoeffding interval crosses it. Preserve both analyses.
- [I] The matched-family design at source `338529734f0bfd7e7784c5fed7a9a9e508cef30b`
  uses separate folded-QPE arms on one shared physical patch: twelve dynamic
  PUBs and four coherent controls. N21 packs replicas within each of two
  separate arms. Those are source-bound observations; later implementations
  must be inspected again. The source's `qpu_planning.py` and
  `QPU_OPTIMIZATION.md` own the complete contracts.

## Acquisition savings and statistical gains are separate

[I] Concurrent acquisition of different required endpoints can save charged
time at unchanged per-endpoint shot counts. Dependence changes the joint
uncertainty calculation; it does not erase acquisition simultaneity.
Conversely, averaging `m` simultaneous replicas requires covariance accounting:

```text
Var(mean(X_1, ..., X_m))
  = (sum_i Var(X_i) + 2 sum_(i<j) Cov(X_i, X_j)) / m^2.
```

[I] For equal variances and common correlation `rho`, the expression becomes
`sigma^2 * (1 + (m - 1)*rho) / m`. Layout separation alone supplies neither
the covariance values nor independent samples. Preserve joint shot order to
investigate within-shot dependence and keep across-shot stationarity as a
separate assumption. Price required endpoint precision, family-wise coverage
and degradation margins rather than selecting maximum occupancy by itself.

## Candidate designs and their falsifiers

| Candidate | Reused prior work | Required design and acceptance evidence |
| --- | --- | --- |
| Fixed useful companions beside a diagnostic patch | Das/QuMC placement, Rudinger context controls | [I] Hold companions, mappings and relevant schedules constant across arms. Include solo/idle references. Reject admission when the prespecified endpoint degradation bound fails or marginal charge exceeds the useful separate workload it replaces. |
| Deliberately varied companion activity | Sarovar context sampling, simultaneous RB | [I] Treat neighboring settings as interventions. Repeat target circuits across active and idle contexts with randomized/interleaved timing. Attribute a context effect only within the tested setting/schedule domain. |
| Balanced arm/patch crossover | NIST blocking, Proctor drift analysis | [I] Run every relevant arm on every compared patch under a balanced schedule. Rebuild measurement-writer delays per patch; retain execution periods and arm-by-patch interactions. An additive fit that misses those interactions fails the intended explanation. |
| Concurrent distinct observables or mitigation circuits | CQCS and QuCP | [I] Preregister the estimator and uncertainty contract, including covariance. Choose analysis before hardware outcomes; selecting the extrapolator closest to an already known answer is a different evaluation procedure. |

[I] The existing one-patch ladder remains a useful baseline. Expanding its
physical footprint changes the experimental design and therefore requires
new validation. Repeated arm identities across multiple PUBs also need an
explicit representation in the optimizer and collection model; copying
circuits alone supplies an incomplete crossover implementation.

## Integrate through verifiable engineering units

1. **Specify the output and estimand.** Name endpoint laws, intervention,
   companion context, patch/time blocks, classical baseline, tolerated
   degradation, precision, and allowed inference. Declare either a hardware
   characterization result or a separate computational-advantage target.
2. **Construct the physical design.** Extend family members, placement and
   timing while preserving disjoint qubits, reference controls, dynamic/static
   option compatibility, and calibrated measurement writers. Reuse existing
   packing and source contracts before adding parallel machinery.
3. **Preserve provenance and observations.** Bind members, contexts, layouts,
   source/dependency identities, exact QPY, shot policy and cost to approval.
   Keep raw joint shot outcomes and actual execution timing before reduction
   to marginal counts. Price characterization and control overhead too.
4. **Verify locally.** Check exact labeled laws, malformed member/patch
   associations, lost shot alignment, incorrect timing remaps and budget
   violations. Noise simulation tests implementation hypotheses; measured
   crosstalk and hardware equivalence retain hardware evidence gates.
5. **Evaluate an approved physical comparison.** Compare endpoint precision
   and degradation at matched useful output, inspect drift and correlations,
   and reconcile final charge with the fused schedule estimate. Keep failed
   hypotheses and hardware/model residuals in the evidence record.

[I] A candidate contribution is an auditable, application-specific design
that demonstrates lower charged time under a declared scientific standard.
Basic packing, physical buffers, varied contexts and blocking each have
substantial prior art. The targeted reading supports those attributions;
it supplies neither an exhaustive novelty search nor a general optimality proof.

## Retrieve and verify source identities

Each linked per-paper note gives the direct PDF URL, inspected version,
SHA-256 and reading scope. The two published PDFs in this comparison live
under `docs/pdf/`; the compatibility link preserves their historical
`literature/pdf/` paths. From the repository root, verify that set with:

```sh
sha256sum -c docs/parallel_experiment_pdfs.sha256
```

Sarovar and QuMC carry verified CC BY 4.0 grants. The other eight papers
in the ten-paper comparison remain external sources with optional personal
reading copies under `docs/local_source_cache/`. Their source-specific
license and notice evidence stays in the registry and per-paper notes.
The ignored cache stays outside both published checksum inventories. The
[source registry](../SOURCES.json) retains the URL and exact identity.
Local download access and permission to republish are separate conditions.

For an optional personal reading copy, preserve the author's notice and
use the exact source URL. The source verifier accepts an absent cache and
checks the original byte count and SHA-256 when the copy is present:

```sh
mkdir -p docs/local_source_cache
curl --fail --location https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf \
  --output docs/local_source_cache/das-2019-multiprogramming.pdf
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/verify_sources.py
```

The [web-source note](quantum_experiment_design_sources.md) supplies direct
documentation links and capture hashes independently of the PDF set.
