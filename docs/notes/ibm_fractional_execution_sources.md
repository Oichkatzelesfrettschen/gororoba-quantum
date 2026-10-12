# IBM fractional gates, execution policy, and source qualification

[P] identifies official documentation; [I] identifies a repository inference.
The reading on 2026-10-12 concerns public documentation and source identities.
Backend availability, calibration, installed client acceptance and paid execution
remain run-specific observations.

## Source and reading record

| Source | Inspected scope | Captured response SHA-256 |
| --- | --- | --- |
| [Fractional gates](https://quantum.cloud.ibm.com/docs/en/guides/fractional-gates) | Target opt-in, angle constraints, synthesis, unsupported mitigation, backend discovery | `37ba7ab7171fcb8da6441992b7bcca6313f13743abd5731f8ef8faff7c6c1b9a` |
| [Sampler options](https://quantum.cloud.ibm.com/docs/en/guides/sampler-options) | Shots precedence and expanded Feature compatibility, read in browser | Notebook identity below |
| [Official Sampler notebook](https://quantum.cloud.ibm.com/endpoints-docs-learning/raw/docs/en/guides/sampler-options.ipynb) | Markdown source for the same shots and compatibility sections | `ce2611335c165e167178e718cc37ee063a3aac20de3a43ab031f4a2d59cfed17` |
| [Maximum execution time](https://quantum.cloud.ibm.com/docs/en/guides/max-execution-time) | QPU usage, ceilings, final metrics, Open Plan window | `d35ff79aeade66e539231ed7ef9768923ed14f98ede7ba5533117d31e47ffc5d` |
| [Batch execution](https://quantum.cloud.ibm.com/docs/en/guides/run-jobs-batch) | Independent jobs, scheduler ordering and intervening calibration | `486e0617277ee2de886e87e54177f1594ecb0148abfa1d8334260e4c2859e653` |
| [Compute-service changelog](https://quantum.cloud.ibm.com/docs/en/guides/changelog-quantum-compute-service) | 3 February 2025 pulse-control removal entry | `583b05a287531af3c957a3d557d4c9d2c2a3f5e72e66acdccd81bb049b0210b5` |

The captures identify mutable web responses, not pinned software releases.
Direct HTTP retrieval of Sampler options returned 403; the public browser page
and its linked notebook succeeded and agreed on the sections above. The library
retains citations, hashes and reading scope for these external web documents;
this audit establishes no blanket rehosting grant for their full contents.

## Supported gates and compatibility

[P] The fractional-gate guide describes directly executed RX and RZZ rotations
on supported backends. Loading a backend with `use_fractional_gates=True`
includes those operations in its Target. The RZZ hardware angle range is
`0 <= theta <= pi/2`; ordinary constant-angle transpilation can apply
`FoldRzzAngle`. Parameterized RZZ circuits assume that later PUB bindings stay
inside the supported range. An invalid binding fails the job.

[P] Sampler's Feature compatibility section allows fractional gates with dynamic
circuits from Runtime 0.42.0. It excludes dynamical decoupling with dynamic
circuits and gate twirling with fractional gates. Dynamic gate twirling applies
only outside conditional blocks; measurement twirling applies only to terminal
measurements. The same section excludes gate twirling with non-Clifford
entanglers. These are scoped policy statements, not guarantees that every
client-side transformation accepts every circuit.

[I] The repository's Runtime 0.50.0/samplomatic `if_else` boxing limitation
remains an independently tested client boundary. The public compatibility table
cannot supersede the [installed-runtime audit](../../AGENTS.md#qiskit-skills).
Any fractional implementation needs a supported import path, live Target,
parameter binding, complete routed-unitary check and actual client dry run.
Copied or scalar gate-error metadata alone cannot establish fidelity for a
specific angle or concurrent workload.

[P] IBM's 3 February 2025 changelog reports removal of pulse-level control on
all IBM Quantum processors. [I] A gate-accessible delay/rate experiment must use
the supported interface; a proposal requiring tunable analog boundary flux or
pulse-level waveguide access needs separate hardware and calibration.

## Cost and dispatch

[P] PUB-specific shots take precedence over `run(shots=...)`, then twirling
options and `default_shots`. Explicit twirling allocation must have sufficient
randomizations times shots-per-randomization for the requested shot count.
`max_execution_time` caps QPU usage, rather than wall time. Final
`job.metrics()['usage']['quantum_seconds']` supplies charged usage. The Open
Plan allows ten minutes per rolling 28-day window.

[I] Unequal shots can save time only after setup costs, fused critical paths,
repetition delay, calibration/control shots and job splits are included.
Sampler PUBs and batch scheduling provide execution organization; disjoint
circuit composition creates qubit-level parallelism. Use the
[parallel-design accounting](quantum_experiment_design_sources.md) for the
packed-versus-isolated comparison and preserve paired shot covariance.

[I] The execution owner compares all three accessible QPUs using freshly
fetched Targets/properties in the deciding process. A broken mock backend
cannot qualify a physical submission. Selection should maximize the declared
endpoint's supported precision per complete workload cost, subject to the
approved design and ceiling; qubit count or least queue length alone cannot
establish the best machine.
