# Documentation map

This page is the single entry to the repository's documents. Rules live in the agent guides, measured facts in the
provider and platform notes, claims in the research notes, and retained bytes under `evidence/` and `../results/`.
`scripts/check_markdown_links.py` keeps every relative link and anchor below resolving.

Placement, naming, linking and immutability rules for every new or moved document: [AGENTS.md, "Documents"](../AGENTS.md#documents).

## Areas

| Area | Owns | Entry |
|---|---|---|
| Rules | agent doctrine, gate machinery, provider tables | [AGENTS.md](../AGENTS.md), [ci/AGENTS.md](../ci/AGENTS.md) |
| Sources and papers | PDFs, licenses, one note per source, verifier | [INDEX.md](INDEX.md), [sources/README.md](sources/README.md) |
| Algebra and proofs | Cayley-Dickson conventions, rank strata, Rocq certificates | [algebra_circuit_rules.md](notes/algebra_circuit_rules.md) |
| Circuit and QPU design | circuit designs, claim boundaries, QPU budgets | [DESIGN_NOTES.md](../gororoba_quantum/DESIGN_NOTES.md) |
| IBM Heron r2 | Targets, transpilation, dynamic circuits, submission | [ibm_quantum/README.md](notes/ibm_quantum/README.md) |
| Quantum Inspire | Tuna devices, QX and Ry emulators | [quantum_inspire/README.md](notes/quantum_inspire/README.md) |
| Open Quantum | brokered IonQ, Rigetti, IQM and AQT backends | [open_quantum/README.md](notes/open_quantum/README.md) |
| Quandela | Belenos and Ascella photonic campaign | [quandela/README.md](notes/quandela/README.md) |
| IQM Resonance | Emerald, Garnet and Sirius | [iqm/README.md](notes/iqm/README.md) |
| qBraid | broker and free CPU/GPU simulators; captured docs, REST OpenAPI and pins | [qbraid/README.md](notes/qbraid/README.md) |
| IonQ | cloud simulator with IonQ noise models; Forte QPUs without credit | [ionq/README.md](notes/ionq/README.md) |
| BlueQubit | free CPU statevector, MPS and Pauli-path simulators; credit-only GPU and QPU | [bluequbit/README.md](notes/bluequbit/README.md) |
| Quafu | BAQIS ScQ superconducting QPUs and a 10-qubit simulator | [quafu/README.md](notes/quafu/README.md) |
| Origin Quantum | Wukong 180 QPU and four simulators; 60 s registration grant | [originquantum/README.md](notes/originquantum/README.md) |
| Planck Technologies | audited SDK; key rejected and simulator returns random bits | [planck/README.md](notes/planck/README.md) |
| QRNG seed sources | ANU, Outshift and Quandela draws for every new seed | [qrng/README.md](notes/qrng/README.md) |
| Simulation | Kaggle CPU and GPU kernels, host Aer build | [kaggle/README.md](notes/kaggle/README.md) |
| Local simulator cross-check | full-output photonic probabilities and precision-preserving cQASM export | [simulation evidence](../results/local-simulation/README.md), [complete optical outputs](../results/local-simulation/optical-operator-replay.json), [serialized Ascella request](../results/local-simulation/ascella-serialized-order-replay/README.md), [compiler replay provenance](../results/local-simulation/compiler-replay-provenance.md) |
| Packages and tools | hypercomplex stack, quantum tool manuals, Aer packaging | [packages/README.md](notes/packages/README.md) |
| Python | interpreters, library roles, optimization ladder | [PYTHON.md](PYTHON.md) |
| CI and gates | gate list, ledger, runtime measurements | [ci/AGENTS.md](../ci/AGENTS.md) |
| Planning | work records, next actions, blockers and completion receipts | [planning entrance](state/plans.md), [commands](runbooks/plan-tracker.md), [migration evidence](evidence/plan-reconciliation/README.md) |
| State and records | claim registry, run census, roadmap | [RESEARCH_STATE.md](state/RESEARCH_STATE.md) |
| Evidence closure | source-relative job identities, denominators, dependencies and acquisition decisions | [derived view](evidence/evidence-closure/README.md), [operator procedure](runbooks/evidence-closure.md), [derivation-led synthesis source](notes/topics/algebra_measurement_synthesis.tex) |
| Archive | handoffs, handbacks, review reports | [archive/reviews/README.md](archive/reviews/README.md) |

## Start here by task

The [quantum task artifact inventory](evidence/quantum-task-artifact-retention/README.md)
retains sanitized operator analyses and explicit scratch/build dispositions for
the Quandela repair and local photonic/compiler validation.

Selected zero-divisor hardware witnesses have retained acquisitions on
[IBM Kingston](../results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md) and
[Tuna-17](notes/quantum_inspire/experiments.md). The
[hardware-witness review](notes/topics/sedenion_hardware_witness_review.md) has an explicit historical cutoff.
The [matched-response case](design/tuna17-zero-divisor-matched-response.md) is prospective and unsubmitted.
The [provider API/billing audit](evidence/provider-api-audit/README.md) separates physical capacity,
native execution limits, billing units and MCP observations. The
[current-balance packed-response case](design/packed-pauli-response-current-balance.md) compares randomized
density interventions and a separately labeled trapped-ion qualification; every generated program remains
unsubmitted and native-unadmitted. Its [implementation plan](design/provider-api-billing-research-plan.md)
retains the historical checklist; the [planning catalogue](state/plan-catalogue.md) owns reconciled work status.
The [publication-status ledger](SOURCES.json) distinguishes journal identities from preprint versions;
the [bibliographic reconciliation](notes/papers/hypercomplex_quantum_crossref_records.md) records reading scopes.

The active [C5 exact replay](evidence/c5_zero_divisor_code/replay-exact.py) uses rational products
and matrices for certificates, retaining numerical noisy decoding and the original result bytes.
The checksum-bound historical README and replay keep their bytes. The active source ledgers
for [kernel determinants](evidence/kernel_determinant/SHA256SUMS-exact-int-dimension),
[projective limits](evidence/projective_kernel_limits/SHA256SUMS-exact-int-dimension) and
[real frontiers](evidence/real_frontier_graphs/SHA256SUMS-exact-int-dimension) bind the
`cd_core.py` whose dimension guard admits only exact int, and preserve every other identity of
their `SHA256SUMS-exact-contracts` predecessors and historical `SHA256SUMS` files.

The [rank-sector endpoint replay](../results/live/rank-sector-endpoint-decomposition-exact-contracts.json)
retains the scientific fields of the [historical report](../results/live/rank-sector-endpoint-decomposition.json)
with the exact-contract `cd_core.py` source identity. The historical report keeps its original bytes.
The [determinant-contract successor](../results/live/rank-sector-endpoint-decomposition-determinant-contracts.json)
also binds the extended `rank_polynomials.py`; its scientific fields remain identical. The
[exact-int-dimension successor](../results/live/rank-sector-endpoint-decomposition-exact-int-dimension.json)
differs from it only in the `cd_core.py` digest.

| Task | Read in order |
|---|---|
| IBM hardware run | [AGENTS.md](../AGENTS.md) "QPU time and calibration", [qpu-submission.md](notes/ibm_quantum/qpu-submission.md), [QPU_EXECUTION_ROADMAP.md](../gororoba_quantum/QPU_EXECUTION_ROADMAP.md) |
| Quantum Inspire run | [README](notes/quantum_inspire/README.md), [usage.md](notes/quantum_inspire/usage.md), [tuna-17-run-design.md](notes/quantum_inspire/tuna-17-run-design.md) |
| Open Quantum run | [README](notes/open_quantum/README.md), `scripts/oq_platform.py` estimate |
| Quandela run | [README](notes/quandela/README.md), [platform-specifications.md](notes/quandela/platform-specifications.md), [strategy.md](notes/quandela/strategy.md) |
| IQM run | [README](notes/iqm/README.md), [os-4.7.md](notes/iqm/os-4.7.md) |
| Simulation and Kaggle | [README](notes/kaggle/README.md), [substrates.md](notes/kaggle/substrates.md), [gpu-runbook.md](notes/kaggle/gpu-runbook.md) |
| Algebra and proofs | `gororoba_quantum/cd_core.py`, [algebra_circuit_rules.md](notes/algebra_circuit_rules.md), [formal_certificates](evidence/formal_certificates/README.md) |
| Sources and papers | [INDEX.md](INDEX.md), [SOURCES.json](SOURCES.json), `verify_sources.py` |
| CI and gates | [ci/AGENTS.md](../ci/AGENTS.md), [ci-runtime.md](runbooks/ci-runtime.md) |
| State and records | [RESEARCH_STATE.md](state/RESEARCH_STATE.md), [QPU_RUN_CENSUS.md](state/QPU_RUN_CENSUS.md), [AGENTS.md](../AGENTS.md) "Records" |

## Files by area

### Rules

| File | Contents |
|---|---|
| [gororoba_quantum/AGENTS.md](../gororoba_quantum/AGENTS.md) | module guide for the circuit and runner code |
| [scripts/AGENTS.md](../scripts/AGENTS.md) | guide for the platform, replay and census scripts |
| [kaggle_kernel/AGENTS.md](../kaggle_kernel/AGENTS.md) | Kaggle kernel program and its bundle rules |

### Sources and papers

| File | Contents |
|---|---|
| [notes/papers/](notes/papers/) | one note per registered source, named by arXiv-style id or author-year |
| [quaternionic-foundational-source-review.md](notes/papers/quaternionic-foundational-source-review.md) | historical QQM citation identities and remaining reading obligations |
| [quaternionic-optical-bound-reading.md](notes/papers/quaternionic-optical-bound-reading.md) | model-specific optical bound and Procopio/Adler exchange body-reading addendum |
| [aflow-a_cf4-225-a.md](notes/papers/aflow-a_cf4-225-a.md) | AFLOW crystallographic prototype A_cF4_225_a |
| [elkies-2013-m256.md](notes/papers/elkies-2013-m256.md) | Elkies 2013 course page on error-correcting codes |
| [mckay-hadamard-matrices.md](notes/papers/mckay-hadamard-matrices.md) | McKay Hadamard equivalence-class data and the retained order-16 list |
| [schafer-1954-cayley-dickson-flexible.md](notes/papers/schafer-1954-cayley-dickson-flexible.md) | Schafer 1954 flexibility of Cayley-Dickson algebras, metadata and secondary statement |
| [2205.07986.md](notes/papers/2205.07986.md) | Ren and Zhao 2023 closed-form Cayley-Dickson twist function and its convention map |
| [1107.1375.md](notes/papers/1107.1375.md) | Bales 2003 twisted group algebras and the recursive Cayley-Dickson twist, with its index and product convention |
| [2103.12805.md](notes/papers/2103.12805.md) | Flaut and Boboescu 2021 twist-tree recursion and the twisted-group-algebra theorem for the Cayley-Dickson process (hosted, CC BY 4.0) |
| [1003.0429.md](notes/papers/1003.0429.md) | Morier-Genoud and Ovsienko 2011 cubic twisted group algebras; the octonion cochain and the Cayley-Dickson algebras outside the cubic class |
| [pmc-4957665-nonlinearity-measures.md](notes/papers/pmc-4957665-nonlinearity-measures.md) | nonlinearity measures for Boolean functions |

### Algebra and proofs

| File | Contents |
|---|---|
| [topics/box-kites/README.md](notes/topics/box-kites/README.md) | box-kite experiment program index |
| [bdsc-pauli-readout.md](notes/topics/bdsc-pauli-readout.md) | BDSC target and blade effects as three-term four-qubit Pauli sums; local readout and 13-basis cover |
| [algebra-hardware-probe-principles.md](notes/topics/algebra-hardware-probe-principles.md) | first principles of algebra hardware probes: mutation test, eigen-observable, interleaving, null arm, noisy coherent response; findings ledger of the Garnet runs |
| [c5-zero-divisor-code-falsification.md](notes/topics/c5-zero-divisor-code-falsification.md) | zero-divisor code, falsified thought experiment |
| [cd-star-lattice-tower.md](notes/topics/cd-star-lattice-tower.md) | Tuna-17 as the Gaussian-integer star lattice; lifts to dimensions 3, 4, 8, 16, the Paley identification of their symmetry groups and the sedenion zero divisors |
| [evidence/cd-star-lattice/README.md](evidence/cd-star-lattice/README.md) | exact star-lattice census bound to the Tuna-17 catalogue topology, with SL(2, q) and PGL(2, 7) certificates and a nauty replay |
| [evidence/albuquerque-majid-convention/README.md](evidence/albuquerque-majid-convention/README.md) | replay of the Albuquerque-Majid cochain recursion against cd_sign: transposed map exact on 5,460 pairs, untransposed control fails, associators agree on 37,448 triples |
| [evidence/cd-imaginary-sum-conference/README.md](evidence/cd-imaginary-sum-conference/README.md) | Rocq proof, for every Cayley-Dickson dimension, that right multiplication by the imaginary sum is a skew conference matrix, with its kernel receipts and the bridge to cd_sign |
| [evidence/cd-tower-basis-sign/README.md](evidence/cd-tower-basis-sign/README.md) | Rocq proof, for every Cayley-Dickson dimension, that the tower's basis products are e_a e_b = sigma_k(a, b) e_(a XOR b) with sigma_k the cd_sign loop, the arc-matrix entries, and the Albuquerque-Majid Corollary 4.3 sign, with its kernel receipts |
| [evidence/cd-sign-row-anf/README.md](evidence/cd-sign-row-anf/README.md) | Rocq proof, for every Cayley-Dickson dimension, of the ANF of the sign rows: Moebius inversion and uniqueness, the leading layer and exact degree of the left rows, and the exact degree of the right rows, with its kernel receipts |
| [evidence/cd-associator-anf/README.md](evidence/cd-associator-anf/README.md) | Rocq proof, for every Cayley-Dickson dimension, of the exact ANF degree of the associator phases (Theorem 2 of the degree note), tied to the cd_sign factors of `predict.associator_phase` and to the tower product, with its kernel receipts |
| [evidence/cd-sign-python-semantics/README.md](evidence/cd-sign-python-semantics/README.md) | Rocq proof, for every Cayley-Dickson dimension, that the syntax tree of `cd_core.cd_sign`, run under a semantics of the Python int subset it uses, returns the tower sign sigma and raises on invalid int arguments, with the extractor contract and kernel receipts |
| [evidence/cd-associator-census/README.md](evidence/cd-associator-census/README.md) | Rocq proof, for every Cayley-Dickson dimension, of the census of unordered basis pairs by associator-phase ANF degree (21, then 3 2^d (2^(d+1) - 1) at degree d), with its kernel receipts |
| [coherent-error-families-report.md](notes/topics/coherent-error-families-report.md) | coherent error families, drift and Rocq replays |
| [open_gororoba_survey_deep_notes.md](notes/topics/open_gororoba_survey_deep_notes.md) | deep notes on the open_gororoba Rocq corpus |
| [prior_work_synthesis.md](notes/prior_work_synthesis.md) | what is known, what is new, labeled per claim |
| [koebisu_rank_stratum_research.md](notes/koebisu_rank_stratum_research.md) | dimension-32 rank question |
| [principal_skew_atlas.md](notes/principal_skew_atlas.md) | principal skew charts; chain continues in the four_support and schur notes |
| [formal_evidence_dependencies.md](notes/formal_evidence_dependencies.md) | formal evidence: algebra, measured counts, prospective checks |
| [open_gororoba_survey.md](notes/open_gororoba_survey.md) | survey of the sister repository |
| [topics/](notes/topics/) | unpinned research notes by subject; [notes/](notes/) holds the notes retained records name |

### Circuit and QPU design

| File | Contents |
|---|---|
| [design/tuna-order-pilot-adversarial-admission.md](design/tuna-order-pilot-adversarial-admission.md) | descriptive pilot preregistration, adversarial findings and execution admission |
| [design/hypercomplex-operator-evidence.md](design/hypercomplex-operator-evidence.md) | algebra falsifiers, operator encodings, library roles and device evidence |
| [runbooks/hypercomplex-operator-cases.md](runbooks/hypercomplex-operator-cases.md) | frozen provider cases, pacing, costs and approval boundary |
| [state/hypercomplex-libraries/libraries.md](state/hypercomplex-libraries/libraries.md) | expanded Python distribution roles and documented candidates |
| [evidence/submitted_circuits/README.md](evidence/submitted_circuits/README.md) | complete retained IBM job-input comparison and immutable replay successor |
| [evidence/sedenion-clifford-envelope/README.md](evidence/sedenion-clifford-envelope/README.md) | exact eight-generator Cl(0,8) envelope spanning M16(R) |
| [evidence/hypercomplex-operators/README.md](evidence/hypercomplex-operators/README.md) | exact replay, probability explorer and distribution inventory |
| [design/et-rows.md](design/et-rows.md) | ET-row device experiment |
| [design/hybrid-shor.md](design/hybrid-shor.md) | hybrid Shor architecture for IBM Heron r2 |
| [design/provider-access-requests.md](design/provider-access-requests.md) | access-request drafts for Quantinuum, D-Wave, Classiq, OQC, Rigetti, SuperQ and Kipu, with the review checklist |
| [design/factoring-notes.md](design/factoring-notes.md) | factoring and the Cayley-Dickson ladder |
| [design/numpy-validation.md](design/numpy-validation.md) | numerical environment validation |
| [design/bdsc-tuna17-pauli-pilot.md](design/bdsc-tuna17-pauli-pilot.md) | Tuna-17 pilot of the BDSC target as a four-qubit local Pauli readout: bank, placement, analysis |
| [design/iqm-garnet-timing-pilot.md](design/iqm-garnet-timing-pilot.md) | IQM Garnet billing pilot: per-job, per-shot, per-circuit and active-reset cost |
| [design/iqm-garnet-signed-kernel-probe.md](design/iqm-garnet-signed-kernel-probe.md) | signed sedenion kernel probe on IQM Garnet: odd dilation overlap, heralded active reset, prediction |
| [design/iqm-garnet-kernel-cancellation-probe.md](design/iqm-garnet-kernel-cancellation-probe.md) | kernel cancellation probe on IQM Garnet: zero-divisor sign at 37 CZ, bright control, over-rotation trains, H1-H5 |
| [design/bdsc-qualification.md](design/bdsc-qualification.md) | Belenos dark-subspace certificate: provider contracts and qualification measurements; [principal-angle replay](notes/quandela/bdsc.md) |
| [runbooks/bdsc-qualification-case.md](runbooks/bdsc-qualification-case.md) | order, prerequisites and stop conditions of the BDSC six-state consistency case |
| [runbooks/bdsc-tuna17-pauli-pilot.md](runbooks/bdsc-tuna17-pauli-pilot.md) | build, dry run and submission order of the Tuna-17 four-qubit Pauli readout pilot |
| [runbooks/quandela-credit-optimization.md](runbooks/quandela-credit-optimization.md) | Quandela billing rule measured per job, packing limits and cost planning |
| [runbooks/quandela-scheduled-runs.md](runbooks/quandela-scheduled-runs.md) | unattended submission of approved, spaced Quandela jobs from a committed schedule through GitHub Actions |
| [runbooks/provider-credits.md](runbooks/provider-credits.md) | read-only daily snapshot of every provider's free allotment, alert thresholds and the systemd user timer |
| [QUANTUM_DISPATCH.md](../plans/QUANTUM_DISPATCH.md) | quantum dispatch plan |
| [coherence-case-science-review.md](../plans/reviews/coherence-case-science-review.md) | coherence-window case, science review |
| [coherence-case-submission-review.md](../plans/reviews/coherence-case-submission-review.md) | coherence-window case, submission-path review |
| [qpu_run_economy.md](notes/qpu_run_economy.md) | information per billed second |

### IBM Heron r2

| File | Contents |
|---|---|
| [ibm_heron_platform.md](notes/ibm_heron_platform.md) | measured Targets and current documentation |
| [hardware-controls.md](notes/ibm_quantum/hardware-controls.md) | every control reachable through qiskit-ibm-runtime |
| [qiskit-ecosystem.md](notes/qiskit-ecosystem.md) | Qiskit ecosystem audit |
| [qiskit-ecosystem-install-plan.md](notes/qiskit-ecosystem-install-plan.md) | Qiskit ecosystem install plan |

### Providers

| File | Contents |
|---|---|
| [tuna17-bipartite-designs.md](notes/quantum_inspire/tuna17-bipartite-designs.md) | Tuna-17 cubic Walsh classes and box-kite packing |
| [quandela/literature.md](notes/quandela/literature.md) | published methods for characterizing a Belenos-class mesh |
| [quandela/quickstart.md](notes/quandela/quickstart.md) | Quandela Cloud quick start |
| [iqm/python-stack.md](notes/iqm/python-stack.md) | Python stack for IQM Resonance |

### Simulation

| File | Contents |
|---|---|
| [build_host/custatevec.md](notes/build_host/custatevec.md) | cuStateVec in the host Aer build |
| [build_host/python-stack.md](notes/build_host/python-stack.md) | build-host Python stack |
| [jax-bridge-structure-report.md](notes/kaggle/jax-bridge-structure-report.md) | JAX bridge sweep, export once per structure |
| [simulation-cost-levers.md](runbooks/simulation-cost-levers.md) | planner, ghost replay and package costs |

### Packages and tools

| File | Contents |
|---|---|
| [quantum-tools/README.md](notes/quantum-tools/README.md) | usage manuals of the quantum and numerics tools |
| [qiskit-aer-cuda/README.md](../packaging/qiskit-aer-cuda/README.md) | native Aer CUDA package |
| [rollback/README.md](../packaging/qiskit-aer-cuda/rollback/README.md) | verified Aer CPU rollback package |

### CI and gates

| File | Contents |
|---|---|
| [ci-runtime.md](runbooks/ci-runtime.md) | timing denominators, bottlenecks and replay selection |
| [vectorized-fits.md](runbooks/vectorized-fits.md) | batched classical fits across replicates |

### State and records

| File | Contents |
|---|---|
| [QPU_RUN_CENSUS.md](state/QPU_RUN_CENSUS.md) | QPU and simulation run census |
| [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) | objectives and gates; sections generated from the registry |
| [research_state.json](state/research_state.json) | claim registry behind the rendered state |

### Archive

| File | Contents |
|---|---|
| [archive/handoffs/](archive/handoffs/handoff-notes.md) | program handoff notes, 2026-10-15 chat notes, box-kite generator and Belenos handoffs |
| [boolean_functions_and_hidden_shift.md](archive/handbacks/boolean_functions_and_hidden_shift.md) | handback: Boolean functions and hidden shift |
| [levratti_manuscripts.md](archive/handbacks/levratti_manuscripts.md) | handback: Levratti manuscripts |
| [quantum_systems_and_synthesis.md](archive/handbacks/quantum_systems_and_synthesis.md) | handback: quantum systems and synthesis |
| [sedenion_geometry_and_twists.md](archive/handbacks/sedenion_geometry_and_twists.md) | handback: sedenion geometry and twists |
| [repository_reconciliation_2026-10-17.md](notes/handbacks/repository_reconciliation_2026-10-17.md) | repository reconciliation, 17 October 2026 |
| [belenos-first-load-hypothesis-2026-10-18.md](archive/handoffs/belenos-first-load-hypothesis-2026-10-18.md) | Belenos first-load hypothesis |
| [box-kite-case-generator.md](archive/handoffs/box-kite-case-generator.md) | box-kite case generator handoff |
| [handoff-notes-2026-10-15.md](archive/handoffs/handoff-notes-2026-10-15.md) | chat-session decisions and falsification results |
| [handoff-notes.md](archive/handoffs/handoff-notes.md) | program handoff sections |
| [archive/reviews/README.md](archive/reviews/README.md) | review and audit reports; [docs audit](archive/reviews/docs-audit.md) |
