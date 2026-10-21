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
| Simulation | Kaggle CPU and GPU kernels, host Aer build | [kaggle/README.md](notes/kaggle/README.md) |
| Packages and tools | hypercomplex stack, quantum tool manuals, Aer packaging | [packages/README.md](notes/packages/README.md) |
| CI and gates | gate list, ledger, runtime measurements | [ci/AGENTS.md](../ci/AGENTS.md) |
| State and records | claim registry, run census, roadmap | [RESEARCH_STATE.md](state/RESEARCH_STATE.md) |
| Archive | handoffs, handbacks, review reports | [archive/reviews/README.md](archive/reviews/README.md) |

## Start here by task

| Task | Read in order |
|---|---|
| IBM hardware run | [AGENTS.md](../AGENTS.md) "QPU time and calibration", [qpu-submission.md](notes/ibm_quantum/qpu-submission.md), [QPU_EXECUTION_ROADMAP.md](../gororoba_quantum/QPU_EXECUTION_ROADMAP.md) |
| Quantum Inspire run | [README](notes/quantum_inspire/README.md), [usage.md](notes/quantum_inspire/usage.md), [tuna-17-run-design.md](notes/quantum_inspire/tuna-17-run-design.md) |
| Open Quantum run | [README](notes/open_quantum/README.md), `scripts/oq_platform.py` estimate |
| Quandela run | [README](notes/quandela/README.md), [platform-specifications.md](notes/quandela/platform-specifications.md), [strategy.md](notes/quandela/strategy.md) |
| IQM run | [README](notes/iqm/README.md), [os-4.7-emerald.md](notes/iqm/os-4.7-emerald.md) |
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
| [aflow-a_cf4-225-a.md](notes/papers/aflow-a_cf4-225-a.md) | AFLOW crystallographic prototype A_cF4_225_a |
| [elkies-2013-m256.md](notes/papers/elkies-2013-m256.md) | Elkies 2013 course page on error-correcting codes |
| [pmc-4957665-nonlinearity-measures.md](notes/papers/pmc-4957665-nonlinearity-measures.md) | nonlinearity measures for Boolean functions |

### Algebra and proofs

| File | Contents |
|---|---|
| [topics/box-kites/README.md](notes/topics/box-kites/README.md) | box-kite experiment program index |
| [c5-zero-divisor-code-falsification.md](notes/topics/c5-zero-divisor-code-falsification.md) | zero-divisor code, falsified thought experiment |
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
| [design/et-rows.md](design/et-rows.md) | ET-row device experiment |
| [design/hybrid-shor.md](design/hybrid-shor.md) | hybrid Shor architecture for IBM Heron r2 |
| [design/factoring-notes.md](design/factoring-notes.md) | factoring and the Cayley-Dickson ladder |
| [design/numpy-validation.md](design/numpy-validation.md) | numerical environment validation |
| [design/bdsc-qualification.md](design/bdsc-qualification.md) | Belenos dark-subspace certificate: provider contracts and qualification measurements |
| [runbooks/bdsc-qualification-case.md](runbooks/bdsc-qualification-case.md) | order, prerequisites and stop conditions of the BDSC six-state consistency case |
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
