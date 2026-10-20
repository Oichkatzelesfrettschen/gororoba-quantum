# Experimental-design and execution documentation for parallel quantum work

[P] marks a statement in the cited documentation. [I] marks a repository
adaptation or engineering proposal. These are web sources, separate from the
version-pinned paper PDFs. Captures were read on 2026-10-11,
America/Los_Angeles. HTML hashes identify those inspected responses; mutable
documentation can return different bytes on later retrieval.

## Source provenance

| Source | Inspected material | SHA-256 of captured HTML |
| --- | --- | --- |
| [NIST randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm) | Section 5.3.3.2, blocking rationale, example, model and randomization | `eb81809c48bd5519b493ff31bf197b80334b0685562afa22ce914ec2403d333e` |
| [NIST Latin squares](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3321.htm) | Section 5.3.3.2.1, design, additive model, assumptions and randomization | `a5b261f31b2cba8c72df386396baca05af452cd5e458192504696066f66110d5` |
| [Qiskit ParallelExperiment](https://qiskit-community.github.io/qiskit-experiments/stubs/qiskit_experiments.framework.ParallelExperiment.html) | API overview and result handling, documentation version 0.14.2 | `3216acaf361db2652b5efae03b5b33b7275128d3d994e1ded5c4347ddeedc457` |
| [Qiskit TiledExperiment](https://qiskit-community.github.io/qiskit-experiments/stubs/qiskit_experiments.framework.TiledExperiment.html) | API overview, example and correctness warning, version 0.14.2 | `521bd2f06f6e2ced55c40da9eaa80117ad31914757aa357a538725756da9177b` |
| [Qiskit partition_qubits](https://qiskit-community.github.io/qiskit-experiments/stubs/qiskit_experiments.framework.partition_qubits.html) | API distance contract, version 0.14.2 | `1bd6c56a7b29cdb1578a1d42bffdbe5a2f69a3868d4f3da38823d7bd59ebc52d` |
| [Qiskit BatchExperiment](https://qiskit-community.github.io/qiskit-experiments/stubs/qiskit_experiments.framework.BatchExperiment.html) | API composition contract, version 0.14.2 | `4fd0ac375e5064a41e456ee1daafbf763bb8d8777cda5e433131d408399ed4c0` |
| [IBM workload usage](https://quantum.cloud.ibm.com/docs/en/guides/estimate-job-run-time) | Job, batch and session usage; estimation formula; schedule/billing distinction | `5e3b281c89639cf36bdf6fde73b4dbebbc44f9c58270e73e3f613c1b67c65156` |
| [IBM execution modes](https://quantum.cloud.ibm.com/docs/en/guides/execution-modes) | Job, batch and session semantics and scheduling limitations | `c074a1e488274bd98170784bc8d5501afd14d0ec50d222a3e789979292b7f142` |

[I] Relevance: calibration-aware compilation high; Cayley-Dickson structure
none; factoring resource estimates medium through execution accounting only.
The documentation establishes API/design contracts. Installed compatibility
and hardware performance require their own checks.

## Blocking and crossover design

- [P] NIST blocks experiments to control identifiable nuisance factors and
  randomizes against the remaining nuisance variation. Its examples include
  run-to-run variation and time of day.
- [P] A Latin square assigns each treatment once per row and once per column.
  Its additive model has treatment, row and column effects. NIST explicitly
  assumes absent interactions between the blocking factors and between
  treatments and blocks; the factors also require matching level counts.
- [I] Diagnostic arm, physical patch and execution period can be mapped to
  treatment, row and column. A repeated randomized crossover could separate
  arm effects from location and drift. Label: adaptation of known design.
  A simple additive Latin square cannot identify arbitrary patch-by-arm or
  companion-by-arm interactions. Specify the estimand and add replication or
  an interaction-aware design before interpreting such effects.
- [I] Recompute each patch's compiled measurement writer and matching delay.
  Balance actual executions and shot counts, retain schedule order, and
  distinguish planned randomization from the order the backend executes.

## Existing composition APIs

- [P] `ParallelExperiment` combines component circuits on disjoint qubit
  subsets. `CompositeAnalysis` marginalizes their data for component analyses.
- [P] `BatchExperiment` appends component circuits into a batch. Appending
  circuits differs from composing their operations onto disjoint qubits.
- [P] `TiledExperiment` transpiles a template once and remaps it. Its warning
  lists connectivity, gate directionality, qubit-specific gate availability,
  and duration-dependent parameters as correctness risks. Its groups contain
  parallel subgroups executed in batches.
- [P] `partition_qubits` provides coupling-graph distance separation.
- [I] These APIs are implementation precedents. The repository's exact ISA,
  QPY, per-member register, timing and approval contracts determine whether
  adopting an API preserves the scientific experiment. Graph distance alone
  establishes a placement condition; measured context effects require the
  [characterization sources](papers/1908.09855.md).
- [I] Preserve joint shot alignment before marginal analysis. Separate
  component histograms discard information needed to estimate covariance
  between simultaneous outcomes.

## Quantum-time accounting

- [P] IBM's approximate job-usage model is sub-job overhead plus
  `(rep_delay + circuit_length) * number_of_executions`. The page gives an
  approximate two-second sub-job overhead and a 250-microsecond default
  repetition delay on most backends; actual values belong to the run.
- [P] Lowering repetition delay can increase state-preparation error.
  `scheduler_timing` reports circuit time, which differs from billed usage.
- [P] Job usage measures QPU locking time. Batch usage accumulates job
  execution locking times. An active session reserves capacity and charges
  for the active elapsed interval. Batch mode permits intervening calibration
  and does not guarantee submission order. Documented scheduling possibilities
  do not establish a particular pair of user jobs' physical simultaneity.
- [I] A fused shot shares repetition overhead. Its critical path and shared
  controller/readout contention determine the circuit duration. A cost model
  must use the compiled fused workload and final job usage, rather than add
  per-qubit sample counts to a billed-shot metric.

## Implementation gates

1. Verify supported APIs against the installed environment before integration;
   the documentation version alone supplies neither import nor runtime proof.
2. Test disjoint mappings, register provenance, timing reconstruction, repeated
   arm/patch identities, and joint-shot recovery with local fixtures.
3. Preregister endpoint precision or degradation margins and the analysis of
   dependence, drift and multiple comparisons. A nonsignificant difference
   supplies weaker evidence than a sufficiently powered equivalence result.
4. Produce a fresh compiled and costed dry-run record for any changed physical
   design. Submission remains subject to the repository's owner-approval gate.

The [parallel-experiment synthesis](quantum_experiment_parallelism.md) maps
these sources to the existing algebra, hardware evidence and paper notes.
