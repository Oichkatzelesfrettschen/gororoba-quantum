# Docs audit and restructure options

This audit inventories every tracked Markdown file outside results/ (2,706 files), maps what binds each file's path or bytes, and proposes a docs layout with one map. The companion [docs-move-plan.json](docs-move-plan.json) lists every proposed move with its bindings and reference-edit count. Nothing in the tree moves in this step.

## 1. Method and legend

- Inventory source: `git ls-files` on the audited tree (9,633 tracked files, 2,873 Markdown files, 167 of them under results/).
- Binding search: every tracked text file was scanned for the path (`docs/` and `literature/` spellings), for the 64-hex sha256 of the file, and for glob patterns that match it. Searched classes: ci/gates.json, ci/full_gate_inputs.json, docs/SOURCES.json, docs/VALIDATION.json, every `*SHA256SUMS`, `*.sha256`, results/**/submission.json and cases.json, docs/evidence/**, and every `*.py`.
- Link graph: relative Markdown links and reference-style links, with fenced code removed, resolved against the file's directory and normalized through `literature -> docs`.
- Binding legend in the inventory:
  - `P:` a retained record (results/**, docs/evidence/**, SHA256SUMS, MANIFEST.json, a sha-pinned plans file, or an inbound link from a sha-pinned Markdown file) names the path or the bytes. A move breaks the record or leaves its link dangling. Pinned files stay.
  - `L:` a mutable ledger or code file (SOURCES.json, research_state.json, a script, a gate command) names the path. A move edits that file in the same change.
  - `-` no binding beyond Markdown links.
- `in` is the number of distinct Markdown files that link the file. A path mention in prose or backticks counts as a reference edit in the plan, not as an inbound link.
- Measurement limits: bare file names (`README.md`, `AGENTS.md`) match every directory, so the six agent and entry files carry hand-written binding notes. A script that builds a path from parts (`NOTES / "x.md"`) shows only through its basename and counts as `L:` when the basename is unique. `docs/VALIDATION.json` and `results/ripple/*-validation.json` hold hashes of earlier file versions that no script recomputes; they do not pin the current bytes.

## 2. Inventory

### 2.1 Groups (listed as counts, not rows)

| Group | Files | Bytes | Binding |
|---|---:|---:|---|
| Paper notes named by arXiv-style id (docs/notes/<id>.md) | 128 | 786203 | `note` field in docs/SOURCES.json (L); verify_sources.py regex `docs/notes/[A-Za-z0-9_.-]+\.md`; INDEX.md links; 9 Python files cite `literature/notes/<id>.md` or `docs/notes/<id>.md` (5 are comments in gororoba_quantum/live_run.py and variance.py); results/ripple/source-integration-validation.json records paths and hashes of 2 notes (P) |
| docs/evidence/**/*.md (README and result notes) | 71 | 394217 | P: SHA256SUMS, MANIFEST.json and replay.py read them; gates select them by glob in ci/full_gate_inputs.json |
| Captured vendor documentation (table below) | 2262 | 9988223 | P: each directory holds a MANIFEST.json with repo-relative paths and sha256 per page; capture_*_docs.py --check reads it |
| results/**/*.md | 167 | - | retained audit records, excluded from this inventory |
| Individually listed below | 245 | 3791735 | per row |

Captured directories:

| Directory | Files | Bytes |
|---|---:|---:|
| docs/notes/iqm/changelog/ | 1 | 52753 |
| docs/notes/iqm/docs/ | 1925 | 7760836 |
| docs/notes/kaggle/cli/ | 18 | 163843 |
| docs/notes/kaggle/site/ | 13 | 341506 |
| docs/notes/open_quantum/docs/ | 56 | 268981 |
| docs/notes/open_quantum/site/ | 21 | 120576 |
| docs/notes/packages/manual/ | 21 | 132183 |
| docs/notes/quandela/guide/ | 32 | 150960 |
| docs/notes/quandela/legal/ | 4 | 85605 |
| docs/notes/quandela/perceval/ | 17 | 164256 |
| docs/notes/quantum_inspire/cqasm-spec/ | 66 | 187355 |
| docs/notes/quantum_inspire/releases/ | 9 | 220669 |
| docs/notes/quantum_inspire/sdk/ | 12 | 28705 |
| docs/notes/quantum_inspire/site/ | 67 | 309995 |

`literature` is the only symbolic link to a directory (`literature -> docs`); `docs/pdf/` entries `s41567-023-02340-9.pdf` and `s42254-024-00770-9.pdf` are the two PDF aliases. The `CLAUDE.md` files in the root, ci/, scripts/ and gororoba_quantum/ are 11-byte loader files that import `AGENTS.md`.

### 2.2 Individually listed files (245)

Columns: path, bytes, first heading, kind, binding, inbound Markdown links, proposed target (`[A]`, `[B]` or `[C]` names the first option that moves it; `stay` keeps the path).

| Path | Bytes | Title | Kind | Binding | In | Target |
|---|---:|---|---|---|---:|---|
| AGENTS.md | 21338 | gororoba-quantum agent guide | agent instructions | L:ci/check_agents_sections.py, ci/gate_inputs.py, qi_platform.py, ibm_runtime_options_inventory.py read it | 9 | stay |
| CLAUDE.md | 11 | (loader: @AGENTS.md) | agent instructions | L:loader file (@AGENTS.md) | 0 | stay |
| HANDOFF_NOTES.md | 20417 | Handoff notes | chronology/handoff | - | 0 | docs/archive/handoffs/handoff-notes.md [A] |
| README.md | 49789 | gororoba-quantum | entry point | L:research_state.py rewrites its research-state block; links 0 inbound (landing page) | 0 | stay |
| ci/AGENTS.md | 18218 | CI and gate guide | agent instructions | L:py | 4 | stay |
| ci/CLAUDE.md | 11 | (loader: @AGENTS.md) | agent instructions | L:loader file (@AGENTS.md) | 0 | stay |
| docs/INDEX.md | 49640 | Source index | index (sources) | P:listed by plans/quantum_dispatch.json (sha pinned by results/live/local-audit-provenance) | 4 | stay |
| docs/README.md | 28522 | Sources and research notes | index (sources) | L:path in historical results/ripple/*-validation.json with stale hashes | 3 | stay |
| docs/RESEARCH_ROADMAP.md | 31011 | Coordinated mathematical research and QPU optimization | state/ledger (roadmap) | P:results/live/local-audit-provenance records; L:scripts/research_state.py rewrites sections | 6 | stay |
| docs/handoff-notes-2026-10-15.md | 10422 | Handoff Notes: Chat Session 2026-10-15 (Ferreton -> Claude | chronology/handoff | L:research_state | 0 | docs/archive/handoffs/handoff-notes-2026-10-15.md [B] |
| docs/notes/aflow-a_cf4-225-a.md | 1663 | AFLOW crystallographic prototype A_cF4_225_a (FCC Cu-type) | paper note | L:SOURCES | 1 | docs/notes/papers/aflow-a_cf4-225-a.md [B] |
| docs/notes/annihilator_determinant_line.md | 7426 | Determinant lines of annihilator bundles | topical research note | P:evidence,ledger,retained-link | 5 | stay |
| docs/notes/annihilator_kernel_limits.md | 19786 | Limiting annihilators along polynomial paths | topical research note | P:evidence,ledger,plans-json,results,retained-link | 8 | stay |
| docs/notes/box_kites/HANDOFF-case-generator.md | 9778 | Box-kite case generator: handoff | chronology/handoff | - | 0 | docs/archive/handoffs/box-kite-case-generator.md [A] |
| docs/notes/box_kites/README.md | 1030 | Box-kite experiment program | topical research note | - | 0 | docs/notes/topics/box-kites/README.md [A] |
| docs/notes/box_kites/experiment-program.md | 54102 | Box-kite experiment program: QX, Ry emulator and Tuna-17 | topical research note | P:evidence,ledger | 5 | stay |
| docs/notes/box_kites/inventory-monographs.md | 33011 | Cayley-Dickson zero-divisor and box-kite claims in the Mon | topical research note | - | 2 | docs/notes/topics/box-kites/inventory-monographs.md [A] |
| docs/notes/box_kites/inventory-open-gororoba.md | 4564 | open_gororoba inventory: box-kites, assessors, zero diviso | topical research note | - | 1 | docs/notes/topics/box-kites/inventory-open-gororoba.md [A] |
| docs/notes/box_kites/inventory-quantum-inspire-backends.md | 6875 | Backend constraints for the box-kite program (QX, Ry, Tuna | topical research note | - | 2 | docs/notes/topics/box-kites/inventory-quantum-inspire-backends.md [A] |
| docs/notes/box_kites/inventory-repository.md | 9470 | Repository inventory: zero divisors, box-kites, algebra wi | topical research note | - | 1 | docs/notes/topics/box-kites/inventory-repository.md [A] |
| docs/notes/brown-1972-dissertation.md | 1480 | Brown 1972 -- Structure of Zero Divisors, and Other Algebr | paper note | L:SOURCES | 1 | docs/notes/papers/brown-1972-dissertation.md [B] |
| docs/notes/build_host/ci-runtime.md | 25981 | CI runtime and affected replay selection | runbook | - | 1 | docs/runbooks/ci-runtime.md [A] |
| docs/notes/build_host/custatevec.md | 9467 | cuStateVec in the host Aer build | runbook | P:evidence,results | 0 | stay |
| docs/notes/build_host/simulation-cost-levers.md | 10676 | Simulation cost: planner, ghost replay and the packages th | runbook | - | 1 | docs/runbooks/simulation-cost-levers.md [A] |
| docs/notes/build_host/vectorized-fits.md | 10194 | Batched classical fits across synthetic replicates | runbook | L:py | 1 | docs/runbooks/vectorized-fits.md [B] |
| docs/notes/c5-zero-divisor-code-falsification.md | 5866 | C5: zero-divisor code -- falsified thought experiment (202 | topical research note | - | 0 | docs/notes/topics/c5-zero-divisor-code-falsification.md [A] |
| docs/notes/c881_exhaustive_proof.md | 3200 | Exhaustive C881 proof at the latest audited source | topical research note | P:evidence,ledger | 8 | stay |
| docs/notes/casimir-dark-sector-web-sources.md | 4134 | Journal and documentation sources without an arXiv copy: C | paper note | L:SOURCES | 5 | docs/notes/papers/casimir-dark-sector-web-sources.md [B] |
| docs/notes/cayley_dickson_annihilator_sources.md | 11856 | Cayley-Dickson annihilator topology: sources and implement | topical research note | P:ledger,results,retained-link,sha256 | 10 | stay |
| docs/notes/cayley_dickson_rank_topology_sources.md | 10393 | Cayley-Dickson rank loci and attachment topology: source l | topical research note | P:ledger,results,retained-link,sha256 | 9 | stay |
| docs/notes/cayley_dickson_sparse_census.md | 4084 | Cayley-Dickson sparse census: domain, evidence, and count  | topical research note | - | 10 | docs/notes/topics/cayley_dickson_sparse_census.md [A] |
| docs/notes/cd_associator_defect_census.md | 9016 | Non-associating basis triples along the Cayley-Dickson lad | topical research note | L:py,research_state | 6 | docs/notes/topics/cd_associator_defect_census.md [B] |
| docs/notes/cd_phase_degree.md | 11834 | Algebraic degree of Cayley-Dickson sign rows and associato | topical research note | L:py,research_state | 3 | docs/notes/topics/cd_phase_degree.md [C] |
| docs/notes/coherent-error-families-report.md | 21986 | Coherent error families, calibration drift and Rocq replay | topical research note | - | 0 | docs/notes/topics/coherent-error-families-report.md [A] |
| docs/notes/complex_skew_rank_geometry.md | 10891 | Complex skew coordinates for Cayley-Dickson rank geometry | topical research note | P:evidence,ledger,retained-link | 7 | stay |
| docs/notes/conditional_ramsey_hamiltonian.md | 8023 | Conditional Ramsey: identifying the diagonal pair Hamilton | topical research note | P:ledger,results | 2 | stay |
| docs/notes/coqinterval-certified-enclosures.md | 6127 | CoqInterval: certified numerical premises for count-based  | paper note | L:SOURCES | 3 | docs/notes/papers/coqinterval-certified-enclosures.md [B] |
| docs/notes/coste-semialgebraic-geometry.md | 7325 | Coste: semialgebraic triangulation and triviality | paper note | P:ledger,retained-link | 9 | stay |
| docs/notes/cross_experiment_scope.md | 7331 | Cross-experiment exposure and the next diagnostic set | topical research note | L:research_state | 1 | docs/notes/topics/cross_experiment_scope.md [B] |
| docs/notes/das-2019-multiprogramming.md | 7131 | Das et al. 2019 -- A Case for Multi-Programming Quantum Co | paper note | L:SOURCES | 3 | docs/notes/papers/das-2019-multiprogramming.md [B] |
| docs/notes/dimension32_skew_schur_charts.md | 11878 | Dimension-32 skew-Schur charts and curved rank changes | topical research note | P:evidence,ledger,retained-link | 9 | stay |
| docs/notes/elkies-2013-m256.md | 11039 | Elkies 2013 -- Math 256x, The Theory of Error-Correcting C | paper note | L:SOURCES | 0 | docs/notes/papers/elkies-2013-m256.md [B] |
| docs/notes/formal_evidence_dependencies.md | 24953 | Formal evidence: algebra, measured counts, and prospective | topical research note | P:evidence | 4 | stay |
| docs/notes/four_support_cellular_homology.md | 14728 | Cellular homology of the four-coordinate zero-product inci | topical research note | P:evidence,ledger | 5 | stay |
| docs/notes/four_support_doubling.md | 10505 | Ordinary doubling of the fixed-support incidence model | topical research note | P:evidence,ledger,retained-link | 6 | stay |
| docs/notes/four_support_incidence_geometry.md | 13516 | Smooth strata and partner incidence on the four-coordinate | topical research note | P:evidence,ledger,retained-link | 7 | stay |
| docs/notes/four_support_rank_loci.md | 9095 | Exact rank loci on the support {1, 10, 18, 25} | topical research note | P:evidence,ledger,retained-link | 8 | stay |
| docs/notes/greenberg-henselian-lifting.md | 5455 | Greenberg: lifting approximate polynomial solutions | paper note | L:SOURCES | 4 | docs/notes/papers/greenberg-henselian-lifting.md [B] |
| docs/notes/handbacks/boolean_functions_and_hidden_shift.md | 5739 | Handback: Boolean functions and hidden-shift sources | chronology/handoff | - | 0 | docs/archive/handbacks/boolean_functions_and_hidden_shift.md [A] |
| docs/notes/handbacks/cayley_dickson_group_theory.md | 7233 | Handback: Cayley-Dickson group theory sources | chronology/handoff | - | 1 | docs/archive/handbacks/cayley_dickson_group_theory.md [A] |
| docs/notes/handbacks/levratti_manuscripts.md | 5081 | Handback: Levratti author-hosted manuscripts | chronology/handoff | - | 0 | docs/archive/handbacks/levratti_manuscripts.md [A] |
| docs/notes/handbacks/quantum_systems_and_synthesis.md | 8805 | Handback: quantum systems and synthesis sources | chronology/handoff | - | 0 | docs/archive/handbacks/quantum_systems_and_synthesis.md [A] |
| docs/notes/handbacks/repository_reconciliation_2026-10-17.md | 94309 | Repository reconciliation -- 17 October 2026 | chronology/handoff | P:evidence | 0 | stay |
| docs/notes/handbacks/sedenion_geometry_and_twists.md | 5741 | Handback: sedenion geometry and Cayley-Dickson twist sourc | chronology/handoff | - | 0 | docs/archive/handbacks/sedenion_geometry_and_twists.md [A] |
| docs/notes/hatcher-algebraic-topology.md | 1652 | Hatcher: attachment and quotient topology | paper note | P:ledger,retained-link | 4 | stay |
| docs/notes/heron_spatial_multiprogramming.md | 21682 | Heron r2 tile packing, wide-circuit composition and Target | topical research note | P:evidence,ledger | 2 | stay |
| docs/notes/hoeffding-1963.md | 1636 | Hoeffding 1963 -- Probability inequalities for sums of bou | paper note | L:SOURCES | 2 | docs/notes/papers/hoeffding-1963.md [B] |
| docs/notes/hypercomplex_quantum_crossref_records.md | 2299 | Crossref records for the hypercomplex-theory and anyon sou | paper note | L:SOURCES | 3 | docs/notes/papers/hypercomplex_quantum_crossref_records.md [B] |
| docs/notes/ibm-runtime-execution-guides.md | 4194 | IBM Quantum Runtime execution guides | paper note | P:ledger,results | 3 | stay |
| docs/notes/ibm_fractional_execution_sources.md | 5268 | IBM fractional gates, execution policy, and source qualifi | paper note | L:SOURCES | 3 | docs/notes/papers/ibm_fractional_execution_sources.md [B] |
| docs/notes/ibm_heron_platform.md | 9935 | IBM Heron r2 platform: measured Targets and current docume | platform guide | P:ledger,results | 3 | stay |
| docs/notes/ibm_quantum/README.md | 4012 | IBM Quantum Heron & ISA Reference Documentation | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/account-access.md | 4775 | IBM account access and the job inventory | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/calibration-jobs.md | 7081 | Monitoring, calibrations, and benchmarking | platform guide | P:results-record(1) | 1 | stay |
| docs/notes/ibm_quantum/estimate-job-run-time.md | 7500 | Workload usage | platform guide | L:py | 1 | stay |
| docs/notes/ibm_quantum/execute-dynamic-circuits.md | 15299 | Execute dynamic circuits | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/fractional-gates.md | 12114 | Fractional gates | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/hardware-controls.md | 86887 | IBM Quantum hardware controls: audit and configuration per | platform guide | L:py | 2 | stay |
| docs/notes/ibm_quantum/heron-r2-readout-resonator.md | 33559 | Heron r2 readout resonator: public evidence for ibm_fez, i | platform guide | L:SOURCES.json,py | 2 | stay |
| docs/notes/ibm_quantum/processor-types.md | 2954 | Processor types | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/qiskit-runtime-circuit-timing.md | 10695 | Visualize circuit timing | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/qpu-information.md | 28994 | View backend details | platform guide | L:py | 1 | stay |
| docs/notes/ibm_quantum/qpu-submission.md | 8412 | QPU time, calibration and submission mechanics | platform guide | - | 2 | stay |
| docs/notes/ibm_quantum/repetition-rate-execution.md | 4163 | Qubit initialization | platform guide | L:py | 1 | stay |
| docs/notes/ibm_quantum/stretch.md | 10148 | Deferred timing resolution using stretch | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/transpile-with-pass-managers.md | 10097 | Transpile with pass managers | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/transpile.md | 7867 | Introduction to transpilation | platform guide | - | 1 | stay |
| docs/notes/ibm_quantum/transpiler-stages.md | 19279 | Transpiler stages | platform guide | - | 1 | stay |
| docs/notes/iqm/README.md | 24222 | IQM Resonance | platform guide | L:gates.json | 2 | stay |
| docs/notes/iqm/hardware-pre-4.7.md | 4843 | IQM Resonance hardware before IQM OS 4.7 | platform guide | - | 2 | stay |
| docs/notes/iqm/os-4.7-emerald.md | 3664 | What IQM OS 4.7 changed on Emerald | platform guide | - | 2 | stay |
| docs/notes/iqm/python-stack.md | 4384 | Python stack for IQM Resonance | platform guide | - | 0 | stay |
| docs/notes/kaggle/README.md | 12946 | Kaggle guides | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/kaggle/custatevec.md | 15321 | cuStateVec on the Kaggle GPU kernel | platform guide | P:results-record(24) | 2 | stay |
| docs/notes/kaggle/gpu-runbook.md | 18527 | GPU kernel runbook | runbook | P:results-record(10) | 1 | stay |
| docs/notes/kaggle/hypercomplex-stack.md | 3214 | The hypercomplex package stack on every substrate | platform guide | P:results-record(51) | 1 | stay |
| docs/notes/kaggle/interfaces.md | 72112 | Kaggle interfaces: CLI, kagglesdk, MCP and the web API | platform guide | P:results-record(45) | 3 | stay |
| docs/notes/kaggle/jax-bridge-structure-report.md | 11021 | JAX bridge sweep: export once per structure, rescale CZ st | platform guide | P:results-record(32) | 0 | stay |
| docs/notes/kaggle/libraries.md | 7772 | Kaggle Python packages | platform guide | P:results-record(45) | 2 | stay |
| docs/notes/kaggle/substrates.md | 17505 | Substrates: measured capacity and what runs where | platform guide | P:results-record(69) | 1 | stay |
| docs/notes/kaggle/tpu-research.md | 24358 | Kaggle TPU access: sources, measured routes and root-cause | platform guide | P:results-record(45) | 4 | stay |
| docs/notes/kaggle/workflow.md | 14997 | Kaggle GPU simulation for design validation | runbook | P:results-record(51) | 3 | stay |
| docs/notes/koebisu_rank_stratum_research.md | 23520 | Koebisu's dimension-32 rank question: geometry, reduction, | topical research note | P:evidence,results,retained-link | 14 | stay |
| docs/notes/left_mult_sign_rank.md | 13041 | Sign subgroup of the Cayley-Dickson left-multiplication gr | topical research note | L:py,research_state | 3 | docs/notes/topics/left_mult_sign_rank.md [C] |
| docs/notes/levratti-2026-active-stabilizers.md | 10269 | Levratti: active stabilizers and Cayley-Dickson zero-divis | paper note | L:SOURCES | 2 | docs/notes/papers/levratti-2026-active-stabilizers.md [B] |
| docs/notes/levratti-2026-fano-css.md | 19162 | Levratti 2026 -- Fano Duality, Projective Orthogonality an | paper note | L:SOURCES | 4 | docs/notes/papers/levratti-2026-fano-css.md [B] |
| docs/notes/mathcomp-coqeal-matrix-certificates.md | 6282 | MathComp and CoqEAL: sound exact matrix certificates | paper note | L:SOURCES | 3 | docs/notes/papers/mathcomp-coqeal-matrix-certificates.md [B] |
| docs/notes/measurement_foundations_web_sources.md | 3595 | Documentation and journal records without a retained copy: | paper note | L:SOURCES | 5 | docs/notes/papers/measurement_foundations_web_sources.md [B] |
| docs/notes/model_discrimination_optimizer.md | 6847 | Model discrimination before atlas spending | topical research note | P:retained-link | 8 | stay |
| docs/notes/n21_feedforward_backends.md | 27163 | N=21 feed-forward: backends besides IBM Heron r2 | topical research note | - | 1 | docs/notes/topics/n21_feedforward_backends.md [A] |
| docs/notes/nebe-lattices-d14-a13.md | 2369 | Nebe--Sloane lattice catalogue: D14 and A13 entries | paper note | L:SOURCES | 1 | docs/notes/papers/nebe-lattices-d14-a13.md [B] |
| docs/notes/nullity_twelve_local_geometry.md | 14065 | Nullity-twelve tangent cone at e1+e18 | topical research note | P:evidence,ledger | 10 | stay |
| docs/notes/numerics_best_practice.md | 13105 | Numerics: conditioning, precision, vectorization and runti | topical research note | - | 1 | docs/notes/topics/numerics_best_practice.md [A] |
| docs/notes/octonion_structure_checks.md | 9154 | Octonion associator codes, box-kite frustration and walk s | topical research note | - | 4 | docs/notes/topics/octonion_structure_checks.md [A] |
| docs/notes/open_gororoba_folding_proofs.md | 23135 | Folding, exact rank geometry, and Rocq proof audit | topical research note | P:evidence,ledger | 10 | stay |
| docs/notes/open_gororoba_handoff.md | 10883 | Handoff to open_gororoba: corrected claims and bounded del | chronology/handoff | - | 5 | docs/notes/topics/open_gororoba_handoff.md [A] |
| docs/notes/open_gororoba_survey.md | 56858 | open_gororoba survey for factoring and higher-dimensional  | topical research note | P:retained-link | 2 | stay |
| docs/notes/open_gororoba_survey_deep_notes.md | 54064 | open_gororoba survey -- deep notes | topical research note | - | 0 | docs/notes/topics/open_gororoba_survey_deep_notes.md [A] |
| docs/notes/open_quantum/README.md | 18522 | Open Quantum | platform guide | L:gates.json | 2 | stay |
| docs/notes/packages/README.md | 7691 | External hypercomplex packages: conventions, independence  | platform guide | P:results-record(51) | 7 | stay |
| docs/notes/packages/adjacent-algebras.md | 10944 | Algebras adjacent to the Cayley-Dickson tower | platform guide | P:results-record(47) | 1 | stay |
| docs/notes/packages/candidates.md | 10740 | Candidate packages beyond the qualified set | platform guide | P:results-record(47) | 1 | stay |
| docs/notes/packages/cayley-calculator.md | 2307 | Cayley-Calculator 1.3.1 | platform guide | P:results-record(51) | 4 | stay |
| docs/notes/packages/cayley-dickson.md | 1603 | cayley-dickson (thoppe), commit abf96e707e2a | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/clifford.md | 1551 | clifford 1.5.1 | platform guide | P:results-record(51) | 4 | stay |
| docs/notes/packages/galgebra.md | 1265 | galgebra 0.6.0 | platform guide | P:results-record(51) | 3 | stay |
| docs/notes/packages/hypercomplex-algebra.md | 1615 | hypercomplex-algebra 0.2.0.2 | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/hypercomplex-engine.md | 2159 | hypercomplex-engine 0.5.0 | platform guide | P:results-record(51) | 5 | stay |
| docs/notes/packages/hypercomplex.md | 2293 | hypercomplex 0.3.4 | platform guide | P:results-record(51) | 4 | stay |
| docs/notes/packages/interplay.md | 17747 | Algebra package interplay: where the packages overlap, whe | platform guide | P:results-record(45) | 22 | stay |
| docs/notes/packages/kingdon.md | 1034 | kingdon 3.0.0 | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/mathdunders.md | 771 | mathdunders 0.4.2 | platform guide | P:results-record(51) | 3 | stay |
| docs/notes/packages/numpy-quaternion.md | 1378 | numpy-quaternion 2024.0.13 | platform guide | P:results-record(51) | 3 | stay |
| docs/notes/packages/octonion-sedenion.md | 2224 | Octonion-Sedenion 1.0.0 | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/octonion.md | 1771 | octonion 0.1.0 (PyTorch) | platform guide | P:results-record(51) | 3 | stay |
| docs/notes/packages/pyoctonion.md | 1161 | pyoctonion 3.12 | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/pyquaternion.md | 792 | pyquaternion 0.9.9 | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/quaternionic.md | 1117 | quaternionic 1.0.18 | platform guide | P:results-record(51) | 2 | stay |
| docs/notes/packages/sagemath.md | 1779 | SageMath 10.10 octonions | platform guide | P:results-record(51) | 4 | stay |
| docs/notes/packages/splitoct.md | 1374 | SplitOct, commit e29e72f805c2 | platform guide | P:results-record(51) | 4 | stay |
| docs/notes/patch_window_staged_plan.md | 6702 | Staged patch-window characterization and validation | design doc | L:py | 9 | docs/notes/topics/patch_window_staged_plan.md [C] |
| docs/notes/principal_skew_atlas.md | 11357 | Principal skew charts with a small covering family | topical research note | P:evidence,ledger,results,retained-link | 9 | stay |
| docs/notes/prior_work_synthesis.md | 9541 | Prior-work synthesis: what is known, what is ours, what th | topical research note | P:retained-link | 10 | stay |
| docs/notes/projective_kernel_frontiers.md | 12023 | Projective kernel limits and real frontier graphs | topical research note | P:evidence,ledger,retained-link | 5 | stay |
| docs/notes/qiskit-ecosystem-install-plan.md | 5978 | Qiskit ecosystem install plan | platform guide | P:ledger,results | 0 | stay |
| docs/notes/qiskit-ecosystem.md | 26269 | Qiskit ecosystem audit | platform guide | P:ledger,results,retained-link | 1 | stay |
| docs/notes/qpu_run_economy.md | 13915 | QPU run economy: information per billed second | design doc | P:results | 2 | stay |
| docs/notes/qpu_vacuum_cd_review_reconciliation.md | 23579 | Reconciliation of the patch-window, campaign and vacuum/da | topical research note | - | 2 | docs/notes/topics/qpu_vacuum_cd_review_reconciliation.md [A] |
| docs/notes/quandela/README.md | 35887 | Quandela Cloud | platform guide | L:gates.json | 6 | stay |
| docs/notes/quandela/bdsc.md | 9339 | Belenos dark-subspace certificate | topical research note | - | 7 | stay |
| docs/notes/quandela/bdsc_sources.md | 7978 | Sources of the dark-subspace certificate | topical research note | - | 5 | stay |
| docs/notes/quandela/belenos-first-load-hypothesis-2026-10-18.md | 13901 | Belenos first-load hypothesis -- Ferreton's notes on the 2 | chronology/handoff | - | 0 | docs/archive/handoffs/belenos-first-load-hypothesis-2026-10-18.md [A] |
| docs/notes/quandela/calibration.md | 9622 | Quandela QPU calibration | topical research note | - | 4 | stay |
| docs/notes/quandela/form-dwell-decomposition.md | 10090 | Form versus dwell on qpu:belenos: decomposition of D1 to D | topical research note | L:json-other | 2 | stay |
| docs/notes/quandela/literature.md | 86392 | Published methods for characterizing and controlling a Bel | topical research note | - | 0 | stay |
| docs/notes/quandela/platform-specifications.md | 8637 | Quandela Cloud platform specifications | platform guide | - | 3 | stay |
| docs/notes/quandela/python-stack.md | 29684 | Python stack for photonic (Belenos) design and analysis | platform guide | - | 1 | stay |
| docs/notes/quandela/quickstart.md | 5029 | Quandela Cloud quick start | runbook | - | 0 | stay |
| docs/notes/quandela/setup-verification.md | 10540 | Quandela software: installation, configuration and verific | runbook | - | 2 | stay |
| docs/notes/quandela/strategy.md | 80035 | Quandela Belenos strategy guide | topical research note | P:docs/evidence(2) | 7 | stay |
| docs/notes/quantum-tools/README.md | 13690 | Quantum and numerics tools: usage manuals | platform guide | P:results-record(45) | 0 | stay |
| docs/notes/quantum-tools/galois.md | 6519 | galois | platform guide | P:results-record(45) | 3 | stay |
| docs/notes/quantum-tools/gpu-arrays.md | 4628 | torch, cupy, jax (and numba CUDA) | platform guide | P:results-record(45) | 2 | stay |
| docs/notes/quantum-tools/ibm-quantum-schemas.md | 4304 | ibm-quantum-schemas | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/lmfit.md | 6927 | lmfit | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/mthree.md | 9381 | mthree | platform guide | P:results-record(45) | 4 | stay |
| docs/notes/quantum-tools/numpy-scipy-sympy.md | 4449 | numpy, scipy, sympy | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/pyzx.md | 8259 | pyzx | platform guide | P:results-record(45) | 5 | stay |
| docs/notes/quantum-tools/qiskit-addon-utils.md | 3162 | qiskit-addon-utils | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/qiskit-aer.md | 9835 | qiskit-aer | platform guide | P:results-record(45) | 4 | stay |
| docs/notes/quantum-tools/qiskit-experiments.md | 10204 | qiskit-experiments | platform guide | P:results-record(45) | 3 | stay |
| docs/notes/quantum-tools/qiskit-ibm-runtime.md | 8499 | qiskit-ibm-runtime | platform guide | P:results-record(45) | 3 | stay |
| docs/notes/quantum-tools/qiskit-mitigation.md | 2443 | qiskit-mitigation | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/qiskit-qasm3-import.md | 5004 | qiskit-qasm3-import and openqasm3 | platform guide | P:results-record(45) | 2 | stay |
| docs/notes/quantum-tools/qiskit.md | 7151 | qiskit | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/quimb.md | 15267 | quimb (with cotengra and autoray) | platform guide | P:results-record(45) | 5 | stay |
| docs/notes/quantum-tools/rustworkx.md | 10465 | rustworkx | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/samplomatic.md | 3907 | samplomatic | platform guide | P:results-record(45) | 1 | stay |
| docs/notes/quantum-tools/stim.md | 18055 | stim | platform guide | P:results-record(45) | 7 | stay |
| docs/notes/quantum_experiment_design_sources.md | 7176 | Experimental-design and execution documentation for parall | paper note | P:ledger,retained-link | 6 | stay |
| docs/notes/quantum_experiment_parallelism.md | 11322 | Parallel experiments: prior work, scientific controls and  | topical research note | P:retained-link | 17 | stay |
| docs/notes/quantum_inspire/README.md | 15994 | Quantum Inspire guides | platform guide | L:gates.json | 3 | stay |
| docs/notes/quantum_inspire/backends.md | 14336 | Quantum Inspire backends: per-machine constraint sheets | platform guide | L:py | 8 | stay |
| docs/notes/quantum_inspire/citing.md | 14497 | Citing Quantum Inspire | platform guide | - | 2 | stay |
| docs/notes/quantum_inspire/cli-reference.md | 33619 | qi CLI reference (quantuminspire 4.1.0) | platform guide | - | 2 | stay |
| docs/notes/quantum_inspire/cqasm.md | 22335 | cQASM 3.0 on Quantum Inspire | platform guide | L:py | 3 | stay |
| docs/notes/quantum_inspire/experiments.md | 52007 | Quantum Inspire experiments: spectator-drive crosstalk and | topical research note | L:json-other | 10 | stay |
| docs/notes/quantum_inspire/knowledge-base.md | 81494 | Quantum Inspire knowledge base digest | platform guide | - | 7 | stay |
| docs/notes/quantum_inspire/mcp.md | 5702 | Quantum Inspire MCP server | platform guide | - | 1 | stay |
| docs/notes/quantum_inspire/platform-facts.md | 10680 | Quantum Inspire platform facts by source | platform guide | - | 1 | stay |
| docs/notes/quantum_inspire/qx-runs.md | 10772 | QX emulator runs: result semantics, dry runs and runs | topical research note | L:json-other,py | 8 | stay |
| docs/notes/quantum_inspire/release-notes.md | 11002 | Quantum Inspire release digest | platform guide | - | 2 | stay |
| docs/notes/quantum_inspire/ry-emulator.md | 20722 | Ry emulator runs: neutral-atom model, compiled gates, resu | topical research note | L:json-other | 5 | stay |
| docs/notes/quantum_inspire/setup.md | 7750 | Quantum Inspire setup: environment, login, CLI and Python  | runbook | L:py | 2 | stay |
| docs/notes/quantum_inspire/shot-record-literature.md | 17366 | Tuna-17 shot-record literature | topical research note | - | 15 | stay |
| docs/notes/quantum_inspire/tuna-17-run-design.md | 24400 | Tuna-17 run design: platform configuration and the packed  | topical research note | L:json-other,py | 6 | stay |
| docs/notes/quantum_inspire/tuna-17.md | 12374 | Tuna-17: result registers, readout drift and operating rul | topical research note | L:json-other,py | 7 | stay |
| docs/notes/quantum_inspire/tuna-9.md | 17363 | Tuna-9 runs: status, topology, the Q8 two-level system and | topical research note | - | 2 | stay |
| docs/notes/quantum_inspire/tuna17-bipartite-designs.md | 6506 | Tuna-17 bipartite designs: cubic Walsh classes and box-kit | topical research note | - | 0 | stay |
| docs/notes/quantum_inspire/tuna17-walsh-exemplars.md | 10162 | Tuna-17 Walsh exemplars: the two cubic classes and the q13 | topical research note | L:json-other | 2 | stay |
| docs/notes/quantum_inspire/tuna_zz_map.md | 20748 | Tuna-17 conditional Ramsey: a proposed cross-check of effe | topical research note | L:json-other | 4 | stay |
| docs/notes/quantum_inspire/tuna_zz_qx_preflight.md | 5397 | Compact QX preflight for the Tuna-17 ZZ proposal | topical research note | L:json-other | 3 | stay |
| docs/notes/quantum_inspire/usage.md | 10485 | Quantum Inspire usage, limits and cost | platform guide | - | 6 | stay |
| docs/notes/rank_locus_two_dimension_gap.md | 12684 | The two-dimension gap of the A_5 rank loci and the route t | topical research note | P:evidence,ledger | 5 | stay |
| docs/notes/real_circle_frontier_graphs.md | 13131 | Real kernel-graph closures and unit-partner evaluation | topical research note | P:evidence,ledger | 4 | stay |
| docs/notes/reality_ripple_measurement_design.md | 19255 | Cayley-Dickson geometry, measured interference, and shared | topical research note | P:results,retained-link | 6 | stay |
| docs/notes/research_proof_experiment_dependencies.md | 8849 | Proof and experiment dependencies after the source audit | topical research note | P:plans-json | 3 | stay |
| docs/notes/reviews/README.md | 1402 | Review and audit reports | chronology/handoff | - | 0 | docs/archive/reviews/README.md [A] |
| docs/notes/reviews/audit-dangling-docs-references.md | 29004 | Audit: dangling docs references on main (942319f) | chronology/handoff | - | 1 | docs/archive/reviews/audit-dangling-docs-references.md [A] |
| docs/notes/reviews/audit-kaggle-aer-runner.md | 7910 | Audit: tools/kaggle-aer-runner (adb795d) vs main and kaggl | chronology/handoff | - | 1 | docs/archive/reviews/audit-kaggle-aer-runner.md [A] |
| docs/notes/reviews/open-gororoba-anf-degree-issue-draft.md | 2423 | (no heading) | chronology/handoff | - | 1 | docs/archive/reviews/open-gororoba-anf-degree-issue-draft.md [A] |
| docs/notes/reviews/open-issue-triage.md | 8221 | Open issue triage (read-only), main at 942319f | chronology/handoff | - | 1 | docs/archive/reviews/open-issue-triage.md [A] |
| docs/notes/reviews/pr-147-ghost-error-scale.md | 25124 | Review: PR #147 kaggle/ghost-error-scale (head 1a099fe) | chronology/handoff | - | 1 | docs/archive/reviews/pr-147-ghost-error-scale.md [A] |
| docs/notes/reviews/pr-148-substrate-routing-libraries.md | 26196 | Review: PR #148 kaggle/substrate-routing-libraries (head 2 | chronology/handoff | - | 1 | docs/archive/reviews/pr-148-substrate-routing-libraries.md [A] |
| docs/notes/reviews/pr-149-jax-bridge-and-atlas-fringe.md | 10111 | Review: PR #149 (jax_bridge_sweep structure) and branch si | chronology/handoff | - | 1 | docs/archive/reviews/pr-149-jax-bridge-and-atlas-fringe.md [A] |
| docs/notes/reviews/quantum-inspire-branch-pair-map.md | 4317 | Quantum Inspire branch pair map | chronology/handoff | - | 1 | docs/archive/reviews/quantum-inspire-branch-pair-map.md [A] |
| docs/notes/schur_acceleration_certificates.md | 10238 | Schur acceleration certificates and necessary tangent cond | topical research note | P:evidence,ledger,results,retained-link | 7 | stay |
| docs/notes/sedenion_hardware_witness_review.md | 7078 | Sedenion hardware witnesses: review of an external proposa | topical research note | - | 2 | docs/notes/topics/sedenion_hardware_witness_review.md [A] |
| docs/notes/signed_kernel_probe.md | 7072 | Signed perturbation of a certified kernel | topical research note | P:evidence,ledger | 1 | stay |
| docs/notes/singular_sector_dynamics.md | 16929 | Singular sectors of two-term Cayley-Dickson elements and t | topical research note | P:evidence,ledger | 10 | stay |
| docs/notes/sqir-voqc-proof-interfaces.md | 6466 | SQIR and VOQC: checked circuit semantics and their integra | paper note | L:SOURCES | 3 | docs/notes/papers/sqir-voqc-proof-interfaces.md [B] |
| docs/notes/stiefel_generic_invertibility.md | 4883 | Generic invertibility of normalized A_6 Stiefel elements | topical research note | P:evidence,ledger | 3 | stay |
| docs/notes/vacuum_field_run_opportunities.md | 15519 | Field-model experiments: source support, finite checks, an | topical research note | P:evidence,plans-json,results | 8 | stay |
| docs/notes/wheel-rust-crate.md | 4104 | The Rust `wheel` crate 0.1.0: wheel arithmetic on binary64 | paper note | P:evidence,ledger | 2 | stay |
| docs/notes/wheels-carlstrom.md | 4986 | Carlstrom: wheels, total division by zero | paper note | P:evidence,ledger | 5 | stay |
| docs/sources/open_gororoba/README.md | 2408 | Retained Cayley-Dickson evidence contracts | evidence README | P:results record | 2 | stay |
| docs/state/QPU_RUN_CENSUS.md | 10557 | QPU and simulation run census | state/ledger | L:docs/state/research_state.json | 0 | stay |
| docs/state/RESEARCH_STATE.md | 293102 | Research state | state/ledger | L:scripts/research_state.py renders it | 5 | stay |
| gororoba_quantum/AGENTS.md | 21222 | gororoba_quantum agent guide | agent instructions | L:check_agents_sections.py; many py | 3 | stay |
| gororoba_quantum/CLAIM_BOUNDARIES.md | 20100 | Cayley-Dickson circuit evidence and mathematical claim bou | design doc | P:ledger,results,sha256 | 4 | stay |
| gororoba_quantum/CLAUDE.md | 11 | (loader: @AGENTS.md) | agent instructions | L:loader file (@AGENTS.md) | 0 | stay |
| gororoba_quantum/DESIGN_NOTES.md | 48227 | Cayley-Dickson quantum circuits | design doc | P:ledger,retained-link | 3 | stay |
| gororoba_quantum/ET_ROWS.md | 6106 | ET-row device experiment | design doc | - | 0 | docs/design/et-rows.md [C] |
| gororoba_quantum/FACTORING_NOTES.md | 30754 | Factoring and the Cayley-Dickson ladder | design doc | - | 1 | docs/design/factoring-notes.md [C] |
| gororoba_quantum/HARDWARE_PLAN.md | 20272 | Hardware plan | design doc | P:results | 4 | stay |
| gororoba_quantum/HYBRID_SHOR.md | 49524 | Hybrid Shor architecture for IBM Heron | design doc | - | 1 | docs/design/hybrid-shor.md [C] |
| gororoba_quantum/LOCAL_COMPUTE.md | 30401 | Local simulation and precision under a QPU budget | design doc | P:results,retained-link | 4 | stay |
| gororoba_quantum/MODEL_DISCRIMINATION.md | 14577 | Measured-feedback versus known-label correction | design doc | P:results,retained-link | 6 | stay |
| gororoba_quantum/MODULAR_SYNTHESIS.md | 20205 | Exact N=21 synthesis and the boundary of impossibility | design doc | P:evidence,ledger,results | 3 | stay |
| gororoba_quantum/N21_USAGE_BUDGET.md | 22957 | N=21 feedback-encoded run: QPU usage budget | design doc | P:evidence,ledger,results | 2 | stay |
| gororoba_quantum/NUMPY_VALIDATION.md | 3981 | Numerical environment validation | design doc | - | 1 | docs/design/numpy-validation.md [C] |
| gororoba_quantum/PACKED_ALGEBRA.md | 12725 | Packed algebra experiments and independent admission | design doc | P:results,retained-link | 8 | stay |
| gororoba_quantum/QPU_EXECUTION_ROADMAP.md | 26913 | QPU execution and optimization roadmap | design doc | P:results,retained-link | 7 | stay |
| gororoba_quantum/QPU_OPTIMIZATION.md | 45282 | Bounded QPU experiment design | design doc | P:results,retained-link | 8 | stay |
| gororoba_quantum/RANK_STRATUM_TOPOLOGY.md | 22194 | Exact rank strata and restricted Cayley-Dickson attachment | design doc | P:evidence,ledger,results,retained-link,sha256 | 18 | stay |
| gororoba_quantum/RIPPLE_CAMPAIGN.md | 21059 | Integrated ripple research and execution directive | design doc | P:results,retained-link | 5 | stay |
| gororoba_quantum/RIPPLE_DYNAMICS.md | 7932 | Cayley-Dickson interference and recurrence | design doc | P:results,retained-link | 4 | stay |
| kaggle_kernel/AGENTS.md | 11205 | Kaggle kernel agent guide | agent instructions | P:results/kaggle submission.json bundles; L:kernel_main.py | 0 | stay |
| packaging/qiskit-aer-cuda/README.md | 7449 | Native Aer CUDA package | runbook | - | 0 | stay |
| packaging/qiskit-aer-cuda/rollback/README.md | 3791 | Verified Aer CPU rollback package | runbook | - | 0 | stay |
| plans/QUANTUM_DISPATCH.md | 7606 | Quantum dispatch | design doc | P:sha256 in results/live/local-audit-provenance/central-reviewed-sync/verification.json | 1 | stay |
| plans/reviews/coherence-case-science-review.md | 13027 | Coherence-window case: science review | chronology/handoff | P:results | 0 | stay |
| plans/reviews/coherence-case-submission-review.md | 14512 | Coherence-window case: submission-path review | chronology/handoff | P:results | 0 | stay |
| scripts/AGENTS.md | 11973 | scripts agent guide | agent instructions | L:check_agents_sections.py | 0 | stay |
| scripts/CLAUDE.md | 11 | (loader: @AGENTS.md) | agent instructions | L:loader file (@AGENTS.md) | 0 | stay |

Non-Markdown note-like files: `plans/quantum_dispatch.json` is listed by `docs/INDEX.md` and pinned by sha256 in `results/live/local-audit-provenance/central-reviewed-sync/verification.json` (P, stays). Directories named notes, plans, handbacks and reviews are `docs/notes/`, `plans/`, `docs/notes/handbacks/`, `docs/notes/reviews/` and `plans/reviews/`; no tracked directory is named `handoff*`.

## 3. Findings

### 3.1 Competing entry points

| Entry | Lines | What it presents | Conflict |
|---|---:|---|---|
| README.md | 359 | project statement, preparation history, generated research-state table (scripts/research_state.py), gate and branch history | no inbound link; GitHub landing page; mixes orientation with a generated registry |
| docs/README.md | 297 | source-library rules, licensing, then prose digests of Koebisu, folding, model-discrimination and ripple notes | claims the title "Sources and research notes" yet routes to roadmap and research notes |
| docs/INDEX.md | 384 | source index: PDF table with licenses, local-cache rules, per-paper links | repeats the library counts (26 PDFs, 101 cache copies, 5 archives) that docs/README.md states |
| docs/RESEARCH_ROADMAP.md | 291 | cumulative objectives and gates; sections regenerated by research_state.py | a third place for "what is established" beside README.md and RESEARCH_STATE.md |
| docs/state/RESEARCH_STATE.md | - (293 KB) | rendered claim registry | generated; no human entry path into it |
| HANDOFF_NOTES.md | 356 | 18 program sections (gate list, premerge cache, N=21, Belenos, open items, closing conditions) | top-level chronology with no inbound link; its "Gate list on main" and "Merges without CI" sections restate rules that AGENTS.md and ci/AGENTS.md own |
| docs/handoff-notes-2026-10-15.md | 218 | chat-session decisions and falsification results | chronology outside archive; bound only by research_state.json |
| AGENTS.md (+ ci/, scripts/, gororoba_quantum/, kaggle_kernel/) | 21 KB root | rules, gate machinery, provider facts, record conventions | the only file that states provider tables (Quantum Inspire, Open Quantum, Quandela, IQM, Heron); gates core-347, core-382, core-502, core-590 keep those tables equal to evidence |
| docs/notes/{quantum_inspire,open_quantum,quandela,iqm,kaggle,packages,quantum-tools}/README.md | 4-36 KB | one provider guide each | eight provider and tool entries (with ibm_quantum/README.md) and no common index; quantum-tools/README.md has no inbound link |
| gororoba_quantum/*.md | 17 design docs, 4-50 KB | design docs | DESIGN_NOTES.md, CLAIM_BOUNDARIES.md, QPU_EXECUTION_ROADMAP.md, HARDWARE_PLAN.md and RIPPLE_CAMPAIGN.md each act as a hub for part of the set |

Resolution: root README.md keeps the project statement and the generated block and links `docs/README.md`; `docs/README.md` becomes the only map; `docs/INDEX.md` keeps the source index and drops the roadmap prose; HANDOFF_NOTES.md and the 2026-10-15 notes move to `docs/archive/handoffs/`.

### 3.2 Duplicate and overlapping documents

Overlap is judged from headings, sizes and cross-links; pairs marked "same subject" repeat facts that one file should own.

| Pair or set | Overlap | Disposition |
|---|---|---|
| docs/README.md and docs/INDEX.md | both state the library rules, PDF and cache counts and license policy | merge rules into INDEX.md; README.md becomes the map |
| HANDOFF_NOTES.md, ci/AGENTS.md, AGENTS.md "Layout and gates", docs/notes/build_host/ci-runtime.md | CI doctrine, premerge cache, gate ledger in four places; HANDOFF_NOTES states the assert-ban review as owed while AGENTS.md states CI disabled | ci/AGENTS.md owns gate rules; ci-runtime.md owns measurements; HANDOFF_NOTES archives |
| docs/notes/open_gororoba_survey.md (57 KB) and open_gororoba_survey_deep_notes.md (54 KB) | same Rocq corpus inventory, admission scans and replay commands; deep notes has no inbound link | keep survey as topic, fold deep notes in as an appendix section or archive |
| open_gororoba_survey.md, open_gororoba_folding_proofs.md, open_gororoba_handoff.md, box_kites/inventory-open-gororoba.md | four views of the sister repository | one topic index entry; pinned files stay |
| docs/notes/kaggle/custatevec.md and docs/notes/build_host/custatevec.md | same library chain and CUDA 13 build, two substrates | cross-link; keep both, runbooks/ holds the host one |
| docs/notes/kaggle/{workflow,gpu-runbook,substrates}.md and AGENTS.md "Simulation on Kaggle" | machine choice, GPU push, cuStateVec and cache-blocking facts | AGENTS.md states the rule, kaggle/ states the measurement |
| docs/notes/packages/ , kaggle/hypercomplex-stack.md, AGENTS.md package table | package conventions and pins repeated three times | packages/README.md owns; AGENTS.md table is gate-checked |
| docs/notes/qiskit-ecosystem.md, qiskit-ecosystem-install-plan.md, quantum-tools/README.md | tool inventories and install guidance | quantum-tools/ owns tool manuals; ecosystem notes cross-link (all three pinned by results/kaggle bundles) |
| plans/QUANTUM_DISPATCH.md, gororoba_quantum/QPU_EXECUTION_ROADMAP.md, HARDWARE_PLAN.md, QPU_OPTIMIZATION.md, docs/notes/qpu_run_economy.md, ibm_quantum/qpu-submission.md | QPU budget, submission and design rules across six files | map assigns one owner per question (section 4) |
| docs/notes/ibm_heron_platform.md, ibm_quantum/hardware-controls.md, heron-r2-readout-resonator.md, ibm_fractional_execution_sources.md, ibm_quantum/fractional-gates.md, AGENTS.md "Heron execution facts" | Heron r2 targets, measure_2, xslow, fractional gates | gate core-254 keeps AGENTS.md equal to the snapshot; the notes cite the snapshot |
| docs/notes/quandela/README.md (36 KB), strategy.md (80 KB), platform-specifications.md, quickstart.md, python-stack.md, setup-verification.md | platform description, setup and campaign narrative interleave | README = entry; strategy = campaign record; quickstart has no inbound link |
| docs/notes/quantum_inspire/tuna-17.md, tuna-17-run-design.md, tuna17-walsh-exemplars.md, tuna17-bipartite-designs.md, tuna_zz_map.md, tuna_zz_qx_preflight.md | one device family across six notes; bipartite-designs has no inbound link | add a Tuna-17 subsection to the provider README |
| docs/notes/handbacks/repository_reconciliation_2026-10-17.md (94 KB), qpu_vacuum_cd_review_reconciliation.md (24 KB), docs/handoff-notes-2026-10-15.md | reconciliation of the same branches and claims | archive the first and third; the second moves to topics |
| docs/notes/reviews/ and plans/reviews/ | two directories of orchestrator reviews | one archive/reviews/ |
| four_support_* (4), principal_skew_atlas, dimension32_skew_schur_charts, schur_acceleration_certificates, complex_skew_rank_geometry, annihilator_* | one proof chain split over 10 notes, each bound to its own evidence directory | topic index in the map; files stay (P) |
| docs/state/QPU_RUN_CENSUS.md and docs/state/RESEARCH_STATE.md | run census against claim registry | cross-link; no inbound link to the census |
| gororoba_quantum/DESIGN_NOTES.md, CLAIM_BOUNDARIES.md, HYBRID_SHOR.md, FACTORING_NOTES.md, MODULAR_SYNTHESIS.md | factoring and circuit design chain | map orders them; five of them stay (P) |

### 3.3 Orphans (no inbound Markdown link)

Files named by a loader or generator are excluded: README.md (landing), the `AGENTS.md` family, `docs/notes/reviews/README.md` (index of its own directory).

- Unpinned, movable at Option A: HANDOFF_NOTES.md, docs/handoff-notes-2026-10-15.md (B: bound by research_state.json), box_kites/HANDOFF-case-generator.md, box_kites/README.md, c5-zero-divisor-code-falsification.md, coherent-error-families-report.md, open_gororoba_survey_deep_notes.md, handbacks/{boolean_functions_and_hidden_shift,levratti_manuscripts,quantum_systems_and_synthesis,sedenion_geometry_and_twists}.md, quandela/belenos-first-load-hypothesis-2026-10-18.md.
- Pinned, stay and gain a map entry: build_host/custatevec.md, elkies-2013-m256.md (SOURCES.json), handbacks/repository_reconciliation_2026-10-17.md, iqm/python-stack.md, kaggle/jax-bridge-structure-report.md, qiskit-ecosystem-install-plan.md, quandela/literature.md, quandela/quickstart.md, quantum-tools/README.md, quantum_inspire/tuna17-bipartite-designs.md, docs/state/QPU_RUN_CENSUS.md, gororoba_quantum/ET_ROWS.md, plans/reviews/coherence-case-{science,submission}-review.md, kaggle_kernel/AGENTS.md, packaging/qiskit-aer-cuda/{README,rollback/README}.md, scripts/AGENTS.md.

The docs/README.md map removes every orphan by linking one owner per area.

### 3.4 Stale chronology outside docs/archive

- HANDOFF_NOTES.md: 18 program sections; it describes the gate list as awaiting a first CI run and a Codex review as owed, while AGENTS.md states CI is disabled and Codex review is the merge gate.
- docs/handoff-notes-2026-10-15.md: session decisions, bound only to docs/state/research_state.json.
- docs/notes/handbacks/ (6 files, 94 KB reconciliation) and docs/notes/reviews/ (9 files, PR-head reviews), plans/reviews/ (2 files): all describe a commit or branch head and carry no live rule.
- docs/notes/quandela/belenos-first-load-hypothesis-2026-10-18.md: dated hypothesis note beside the platform guide.
- README.md "Earlier preparations keep their original text as history" links four preparation documents under results/ripple/ and gororoba_quantum/RIPPLE_CAMPAIGN.md.
- docs/VALIDATION.json (schema `source-library-validation-v1`, base commit c4e2074, 11 PDFs) disagrees with docs/README.md and INDEX.md (26 PDFs); no script reads VALIDATION.json.

### 3.5 Broken links

- Relative Markdown links between tracked files: 0 broken. The six unresolved targets sit inside captured vendor pages (`docs/notes/kaggle/site/notebooks.md`: `scheduling-notebooks`; `docs/notes/quantum_inspire/site/kbase_spin-2-plus-operational-specifics.md`: five cQASM grammar placeholders such as `bit-name:ID`) and keep their captured bytes.
- Path mentions to untracked files (4): `docs/notes/kaggle_gpu_simulation.md` (docs/notes/reviews/audit-kaggle-aer-runner.md; docs/evidence/archive_imports/README.md, retained), `docs/notes/ghost-event-scale-report.md` (pr-147 review), `docs/notes/atlas-fringe-amplitudes-report.md` (pr-149 review), `docs/local/plans/pr206-f4-r1-restart.md` (HANDOFF_NOTES.md; docs/local/ is ignored).
- Mentions of sister-repository paths (`docs/THEOREMS.md`, `docs/SEDENION_ATLAS.md`, `docs/book/src/algebra/box-kites.md`, `docs/external_sources/*`, `docs/physics/*`) and vendor-relative paths (`docs/concepts/credits.md`, `docs/iqm-pulse/changelog.md`) name external trees; they are not links to this repository.
- No gate checks Markdown links. Add one (`ci/check_docs_links.py`, tier pr) in the change that adopts any option, so the map cannot decay.

### 3.6 Binding summary

- 80 files with a move target are pinned and stay: 78 by a retained record or retained-file link, 2 as fixed-path entries.
- Directory corpora bound by retained records: docs/notes/kaggle (880 retained references), docs/notes/packages (2,141), docs/notes/quantum-tools (855), docs/notes/quantum_inspire (67), docs/notes/ibm_quantum (4), docs/notes/quandela (3). Each stays in place with a map entry.
- Directory corpora with no retained reference: docs/notes/iqm (1,960 files, 1,956 mutable references) and docs/notes/open_quantum (90 files, 94 mutable references). Only these two can move as units (Option C).
- results/kaggle/*/submission.json bundles record sha256 of bundled notes (about 60 notes appear in the largest records); the bundles pin the notes whether or not a script re-reads them.

## 4. Target layout

```
README.md                       project statement + generated research-state block; links docs/README.md
AGENTS.md  CLAUDE.md            rules (unchanged)
docs/
  README.md                     the map (at most 200 lines)
  INDEX.md                      source index: PDFs, licenses, local cache (unchanged path)
  RESEARCH_ROADMAP.md           objectives and gates (unchanged path, generated sections)
  SOURCES.json VALIDATION.json verify_sources.py check_verify_sources.py PDF_SHA256SUMS ...   (unchanged)
  pdf/ source_archives/ local_source_cache/                                                    (unchanged)
  notes/
    papers/                     one note per registered source        [B]
    topics/                     research notes by subject; box-kites/ [A]
    platforms/<provider>/       iqm, open_quantum                     [C]; other providers stay in notes/<provider>/
    <flat pinned notes>         retained-record-bound notes stay at docs/notes/*.md
  design/                       relocatable gororoba_quantum design docs [C]
  runbooks/                     host build, CI runtime, cost levers   [A]
  evidence/                     retained replays and results          (unchanged)
  state/                        RESEARCH_STATE.md, QPU_RUN_CENSUS.md, research_state.json (unchanged)
  archive/handoffs/ handbacks/ reviews/                               [A]
```

| Directory | Why |
|---|---|
| docs/README.md | one map replaces five competing entries; the table below keeps it under 200 lines |
| docs/INDEX.md | plans/quantum_dispatch.json lists it and results records pin that file |
| docs/notes/papers/ | SOURCES.json is the registry of 150 source notes; one directory matches one ledger |
| docs/notes/topics/ | research notes read by subject, not by source; pinned notes stay flat and the map lists them |
| docs/notes/platforms/<provider>/ | one place per provider; kept only where no retained record names the path |
| docs/design/ | design docs that no retained record or digest-bearing script names |
| docs/runbooks/ | commands an operator runs (host build, CI replay, cost levers) separate from findings |
| docs/evidence/, docs/state/ | retained bytes and generated registries keep their paths |
| docs/archive/ | chronology and review heads stay readable and leave the live tree |
| `literature -> docs` | unchanged; `literature/notes/<file>.md` resolves for every file that stays at docs/notes/ and for the two source ledgers whose spelling results/hw_estimate records |

Move rule: a file with a path or byte binding in a retained record stays and appears in the map. A moved file keeps its basename. No per-file symbolic links are added.

### 4.1 Draft of docs/README.md (map)

Areas table (one row each, entry file in the last column):

| Area | Owns | Entry |
|---|---|---|
| Rules | agent doctrine, gate machinery, provider tables | AGENTS.md, ci/AGENTS.md |
| Sources and papers | PDFs, licenses, per-source notes, verifier | docs/INDEX.md, docs/SOURCES.json |
| Algebra and proofs | Cayley-Dickson conventions, rank strata, Rocq certificates | gororoba_quantum/AGENTS.md, docs/notes/topics/, docs/evidence/formal_certificates/README.md |
| Circuit and QPU design | designs, claim boundaries, QPU budgets | gororoba_quantum/DESIGN_NOTES.md, QPU_EXECUTION_ROADMAP.md |
| IBM | Heron r2 facts, transpile, dynamic circuits | docs/notes/ibm_quantum/README.md, docs/notes/ibm_heron_platform.md |
| Quantum Inspire | Tuna, QX, Ry emulators | docs/notes/quantum_inspire/README.md |
| Open Quantum | brokered IonQ, Rigetti, IQM, AQT | docs/notes/open_quantum/README.md |
| Quandela | Belenos photonic campaign | docs/notes/quandela/README.md |
| IQM Resonance | Emerald, Garnet, Sirius | docs/notes/iqm/README.md |
| Simulation | Kaggle CPU and GPU, host Aer build | docs/notes/kaggle/README.md, docs/runbooks/ |
| Packages and tools | hypercomplex stack, quantum tools | docs/notes/packages/README.md, docs/notes/quantum-tools/README.md |
| CI and gates | gate list, ledger, runtime | ci/AGENTS.md, docs/runbooks/ci-runtime.md |
| State and records | claim registry, run census, results layout | docs/state/RESEARCH_STATE.md, docs/state/QPU_RUN_CENSUS.md |
| Archive | handoffs, handbacks, reviews | docs/archive/ |

Start-here paths by task:

| Task | Read in order |
|---|---|
| IBM hardware run | AGENTS.md "QPU time and calibration" -> docs/notes/ibm_quantum/qpu-submission.md -> gororoba_quantum/QPU_EXECUTION_ROADMAP.md -> gororoba_quantum/live_run.py dry run |
| Quantum Inspire run | docs/notes/quantum_inspire/README.md -> usage.md -> tuna-17-run-design.md -> scripts/qi_platform.py |
| Open Quantum run | docs/notes/open_quantum/README.md -> scripts/oq_platform.py estimate |
| Quandela run | docs/notes/quandela/README.md -> platform-specifications.md -> strategy.md -> scripts/qd_platform.py plan |
| IQM run | docs/notes/iqm/README.md -> os-4.7-emerald.md -> scripts/iqm_platform.py |
| Simulation | docs/notes/kaggle/README.md -> substrates.md -> gpu-runbook.md -> docs/runbooks/ |
| Algebra and proofs | gororoba_quantum/cd_core.py -> AGENTS.md "Algebra circuit design rules" -> docs/notes/packages/README.md -> docs/evidence/formal_certificates/README.md |
| Sources and papers | docs/INDEX.md -> docs/SOURCES.json -> docs/verify_sources.py |
| CI and gates | ci/AGENTS.md -> ci/gates.json -> docs/runbooks/ci-runtime.md |
| State and records | docs/state/RESEARCH_STATE.md -> README.md research-state block -> results/ conventions in AGENTS.md "Records" |

The pinned topical notes (37 files) and design docs (13 files) that stay in place appear in one table per area beneath these two tables; the map stays at or below 200 lines by listing each pinned note on one row of at most 100 characters. The move plan marks them `stay: true`.

## 5. Restructure options

Counts come from `docs-move-plan.json` (`options`). A reference edit is one text change in a link, path mention, ledger field, gate command or script path. Edits between two moved files that keep the same relative link count zero.

| | Option A | Option B | Option C |
|---|---|---|---|
| Content | map + archive/runbook/topic moves of unpinned files | A + all movable paper notes to notes/papers/ + files bound by mutable ledgers | B + design docs, digest-bound topics, iqm and open_quantum directories |
| Files moved | 34 | 162 | 171 + 2050 (two directories) |
| Markdown reference edits | 164 in 45 files | 707 in 158 files | 750 in 165 files |
| Ledger, gate and script edits | 0 | 154 in 5 files | 171 in 11 files |
| Support edits (verifier, fixtures, comments) | 0 | 5 | 13 |
| Platform directory edits | 0 | 0 | 2050 |
| Total reference edits | 164 | 866 | 2984 |
| Pinned files touched | none | docs/SOURCES.json (147 `note` path occurrences), docs/state/research_state.json, 3 scripts | adds gororoba_quantum/live_run.py, variance.py, verify.py, patch_characterization.py; 5 capture and platform scripts; 2 MANIFEST sets |
| Retained evidence bytes rewritten | none | none | none (captured page bytes and their sha256 unchanged; MANIFEST path strings change) |
| Pinned files left in place | 80 | 80 | 80 plus 6 provider and package directories |

Option contents:

- Option A (34 moves): archive/handoffs (HANDOFF_NOTES.md, box-kite case-generator handoff, Belenos first-load note), archive/handbacks (5 of 6), archive/reviews (9 from docs/notes/reviews, none from plans/reviews because retained results link them), runbooks (ci-runtime.md, simulation-cost-levers.md), topics (15 notes including box_kites/). Rewrite docs/README.md as the map, fold its library rules into docs/INDEX.md, add one link line to README.md outside the generated block. Add `ci/check_docs_links.py`.
- Option B (+128 moves): 124 paper notes to notes/papers/, plus docs/handoff-notes-2026-10-15.md, vectorized-fits.md and two topics bound by research_state.json or a script. 24 paper notes stay flat because retained records pin them, so notes/papers/ holds 126 of 150 and verify_sources.py accepts both `docs/notes/<n>.md` and `docs/notes/papers/<n>.md`.
- Option C (+9 moves and 2 directories): ET_ROWS, FACTORING_NOTES, HYBRID_SHOR, NUMPY_VALIDATION to docs/design/; cd_phase_degree, left_mult_sign_rank and patch_window_staged_plan (path strings in gororoba_quantum/*.py); two paper notes cited in live_run.py and variance.py comments; docs/notes/iqm and docs/notes/open_quantum to docs/notes/platforms/. Any edit to gororoba_quantum/*.py changes the source digest that approved QPU records bind (AGENTS.md, QPU time and calibration), so C waits until no approved record is outstanding.

Gates to rerun:

| Gate | Why | A | B | C |
|---|---|:-:|:-:|:-:|
| core-250, core-253 (check_agents_sections) | AGENTS.md edits | x | x | x |
| core-265 (check_gate_inputs) | full-gate input declarations name docs paths | x | x | x |
| core-270 (research_state.py --check) | README.md and RESEARCH_ROADMAP.md generated sections; research_state.json paths | x | x | x |
| sources-123, sources-125 (verify_sources, its checks) | note path regex and fixtures | | x | x |
| core-347, core-382, core-502, core-590 (platform checks over AGENTS.md tables) | AGENTS.md and README link edits | x | x | x |
| core-346, core-380, core-500, core-588 and core-283 (capture --check) | capture roots and manifests | | | x |
| core-403 (rocq pins), sources-216 (package tables) | path lists | | x | x |
| every gate whose ledger key reads a moved script or gororoba_quantum module | ledger keys change | | scripts only | all importing live_run, variance, verify |
| new docs-link gate | prevents dangling links | x | x | x |

Ranking by value against risk:

1. Option A: removes the five competing entry points, the orphan set and the top-level chronology at 164 edits, no ledger edit and no digest impact. Risk: topics/ holds only the 15 unpinned notes (box-kites/ included) while 37 pinned notes stay flat; the map table resolves that split.
2. Option B: gives SOURCES.json a matching directory and shrinks docs/notes/ to the pinned set. Cost: 866 edits, regeneration of README.md, RESEARCH_ROADMAP.md and the 293 KB RESEARCH_STATE.md through research_state.py, and a 126/24 split of the paper notes. Value is cosmetic for readers who use INDEX.md.
3. Option C: completes the layout. Cost: 2984 edits, source-digest change in gororoba_quantum, 2,050 manifest and reference rewrites for two vendor-doc corpora that no reader navigates by path. Not recommended until the gate redesign settles the manifest format.

Recommendation: adopt A, add the docs-link gate, and keep B as a follow-up that moves the 126 papers in one commit with the SOURCES.json and verifier edits.
