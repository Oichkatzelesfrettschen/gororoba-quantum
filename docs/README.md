# Documentation map

This page is the single entry to the repository's documents. Rules live in the agent guides, measured facts in the
provider and platform notes, claims in the research notes, and retained bytes under `evidence/` and `../results/`.
`scripts/check_markdown_links.py` keeps every relative link and anchor below resolving.

Placement, naming, linking and immutability rules for every new or moved document: [AGENTS.md, "Documents"](../AGENTS.md#documents).

## Areas

| Area | Owns | Entry |
|---|---|---|
| Rules | agent doctrine, gate machinery, provider tables | [AGENTS.md](../AGENTS.md), [ci/AGENTS.md](../ci/AGENTS.md) |
| Sources and papers | PDFs, licenses, one note per source, verifier, reading-copy links | [INDEX.md](INDEX.md), [sources/README.md](sources/README.md), [reading-copy-locations.tsv](sources/reading-copy-locations.tsv) |
| Algebra and proofs | Cayley-Dickson conventions, rank strata, Rocq certificates | [algebra_circuit_rules.md](notes/algebra_circuit_rules.md) |
| A5 quantum-claim contracts | Exact natural LCU, complete kernel projectors, modular-rank and isotropy counterexamples | [A5 quantum contracts](evidence/a5-quantum-contracts/README.md) |
| A5 Gram operators | Exact cubic kernel filters, Gaussian Jordan types, scalar and coefficient-phase controls | [Gram-operator witnesses](evidence/a5-gram-operator-witnesses/README.md) |
| A5 and photonic candidates | Exact rank witnesses, heralding limits and retained Ascella and Belenos results | [A5 photonic cross-checks](evidence/a5-photonic-crosschecks/README.md) |
| A5 associator observables | exact rank and spectrum of the left alternative associator operator over the twelve rank strata, with automorphism controls | [A5 associator observables](evidence/a5-associator-observables/README.md) |
| Hardware residuals | exploratory offline passes for residual structure in retained IBM, Tuna-17 and Quandela records | [hardware-residuals/README.md](evidence/hardware-residuals/README.md) |
| Circuit and QPU design | circuit designs, claim boundaries, QPU budgets | [DESIGN_NOTES.md](../gororoba_quantum/DESIGN_NOTES.md) |
| IBM Heron r2 | Targets, transpilation, dynamic circuits, submission | [ibm_quantum/README.md](notes/ibm_quantum/README.md) |
| Quantum Inspire | Tuna devices, QX and Ry emulators | [quantum_inspire/README.md](notes/quantum_inspire/README.md) |
| Open Quantum | brokered IonQ, Rigetti, IQM and AQT backends | [open_quantum/README.md](notes/open_quantum/README.md) |
| Quandela | Belenos and Ascella photonic campaign | [quandela/README.md](notes/quandela/README.md) |
| Photonic estimation | Gurvits/root and Husimi estimates, fixed-mode marginals and Gaussian references | [Gurvits computational boundaries](notes/topics/gurvits-computational-boundaries.md) |
| IQM Resonance | Emerald, Garnet and Sirius | [iqm/README.md](notes/iqm/README.md) |
| qBraid | broker, Lab compute profiles, free CPU/GPU simulators, and the hosted MCP server; captured docs, REST OpenAPI and pins | [qbraid/README.md](notes/qbraid/README.md) |
| IonQ | cloud simulator with IonQ noise models; Forte QPUs without credit | [ionq/README.md](notes/ionq/README.md) |
| BlueQubit | free CPU statevector, MPS and Pauli-path simulators; credit-only GPU and QPU | [bluequbit/README.md](notes/bluequbit/README.md) |
| Quafu | BAQIS ScQ superconducting QPUs and a 10-qubit simulator | [quafu/README.md](notes/quafu/README.md) |
| Origin Quantum | Wukong 180 QPU and four simulators; 60 s registration grant | [originquantum/README.md](notes/originquantum/README.md) |
| Planck Technologies | account closed; audited SDK, key rejected and simulator returns random bits | [planck/README.md](notes/planck/README.md) |
| AWS | free-plan project, a tooling cloud with Braket unavailable; the host Python packages | [aws/README.md](notes/aws/README.md) |
| Azure | Quantum workspace with free Quantinuum, Pasqal and Rigetti emulator plans | [azure/README.md](notes/azure/README.md) |
| zbMATH Open | REST, OAI-PMH and citation-matching client; API audit with replayable findings | [zbmath/README.md](notes/zbmath/README.md) |
| QRNG seed sources | ANU, Outshift and Quandela draws for every new seed | [qrng/README.md](notes/qrng/README.md) |
| Simulation | Kaggle CPU and GPU kernels, host Aer build | [kaggle/README.md](notes/kaggle/README.md) |
| Local simulator cross-check | full-output photonic probabilities and precision-preserving cQASM export | [simulation evidence](../results/local-simulation/README.md), [complete optical outputs](../results/local-simulation/optical-operator-replay.json), [serialized Ascella request](../results/local-simulation/ascella-serialized-order-replay/README.md), [compiler replay provenance](../results/local-simulation/compiler-replay-provenance.md) |
| Packages and tools | hypercomplex stack, quantum tool manuals, Aer packaging | [packages/README.md](notes/packages/README.md) |
| Python | interpreters, library roles, optimization ladder | [PYTHON.md](PYTHON.md) |
| CI and gates | gate list, ledger, runtime measurements | [ci/AGENTS.md](../ci/AGENTS.md) |
| Planning | work records, next actions, blockers and completion receipts | [plan records](state/plans/), [commands](runbooks/plan-tracker.md), [migration evidence](evidence/plan-reconciliation/README.md) |
| Repository layout | measured checkout shape, producer-side record slimming, document and code homes, package hierarchy waves, owner decisions | [layout reconciliation](design/repository-layout-reconciliation.md) |
| Operating rules | the six failures the rules prevent, the operating data, the forty-line contract, checks that replace text, falsifiers, what the CI is for | [operating rules contract](design/operating-rules-contract.md) |
| State and records | claim registry, run census, roadmap, on-demand renders | [research_state.json](state/research_state.json), [generated views](runbooks/generated-views.md) |
| Evidence closure | source-relative job identities, denominators, dependencies and acquisition decisions | [derived view](evidence/evidence-closure/README.md), [operator procedure](runbooks/evidence-closure.md), [derivation-led synthesis source](notes/topics/algebra_measurement_synthesis.tex) |
| Measurement observability | attempted-population contracts, full score and prediction covariance, nested heralds and Hermitian completion | [measurement contracts](design/measurement-observability.md) |
| Results index and archive copies | run, job, acquisition and claim lookups; Software Heritage and git bundle copies | [results index](runbooks/results-index.md), [archive copies](runbooks/repository-archive.md), [archive observations](evidence/repository-archive/README.md) |
| Archive | handoffs, handbacks, review reports | [archive/reviews/README.md](archive/reviews/README.md) |

## Placement by kind

A source note lives in `docs/notes/papers/` with its `docs/SOURCES.json`
record; a research note in `docs/notes/topics/`; a provider guide in
`docs/notes/<provider>/`; a design or plan in `docs/design/`; operator commands
in `docs/runbooks/`; a replay and its retained output in `docs/evidence/<name>/`;
generated registries in `docs/state/`; handoffs, session logs and review
reports in `docs/archive/`. Session-local scratch stays in the ignored
`docs/local/`. Names state target and mechanism in lowercase with hyphens; a
date or phase label appears only under `docs/archive/`.

## Source cache and reading copies

External-only sources (`redistribution: excluded_without_permission`) stay out of
this tree and keep their reading copies in the owner's workspace documents
repositories, cloned beside this checkout:
[gororoba-documents-public](https://github.com/Oichkatzelesfrettschen/gororoba-documents-public)
when the file's own license allows redistribution, and
[gororoba-documents-private](https://github.com/Oichkatzelesfrettschen/gororoba-documents-private)
otherwise. Both file every document under `<field>/<subject>/` by the public
repository's `TAXONOMY.md`, keep a Markdown transcription beside its PDF, and
list every file with its sha256, license, license evidence and kind in
`manifest.tsv`.
`"$PYTHON" scripts/fetch_source_cache.py --missing --from-documents DIR`,
repeatable for both checkouts, restores the ignored `docs/local_source_cache/`
by sha256, and the same command without `--from-documents` fetches the
registered URLs.
The git-ignored `sources/reading-copies.md` ([generated views](runbooks/generated-views.md)) links each
source to its reading copy beside its public source. `scripts/source_reading_copies.py --locate`
resolves every registered digest through both manifests into
[sources/reading-copy-locations.tsv](sources/reading-copy-locations.tsv), and a
plain run renders that index on demand. The `sources`
suite in ci/gates.json covers the source registry, the evidence replays and their checksum
ledgers on demand; no workflow runs it.

## Start here by task

The [quantum task artifact inventory](evidence/quantum-task-artifact-retention/README.md)
retains sanitized operator analyses and explicit scratch/build dispositions for
the Quandela repair and local photonic/compiler validation.

Selected zero-divisor hardware witnesses have retained acquisitions on
[IBM Kingston](../results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md) and
[Tuna-17](notes/quantum_inspire/experiments.md). The
[hardware-witness review](notes/topics/sedenion_hardware_witness_review.md) has an explicit historical cutoff.
The [matched-response case](design/tuna17-zero-divisor-matched-response.md) is prospective and unsubmitted.
Its [historical catalogue](evidence/quantum_inspire/matched-zero-divisor-catalogue.json) retains the
exact bytes bound by the archived compiler receipt; a newer live catalogue still requires case review.
The [reduced QX destination case](design/tuna-destination-qx-conformance.md) defines
a separate simulator conformance proposal, pending review and approval.
The [exact QX dispatch-guard design](design/tuna-qx-exact-dispatch-guard.md) specifies
the approval, live-admission, single-use and recovery boundaries still required.
The [sequential destination evidence case](design/tuna-destination-sequential-evidence-case.md)
sets a working two-response acquisition and optional-stopping envelope, pending admission.
The [sequential destination uncertainty design](design/tuna-sequential-destination-uncertainty.md)
quantifies job-level precision without a finite-memory assumption.
The [randomized destination-block draft](design/tuna-destination-randomized-blocks.md) proposes
a job-level falsification test with explicit dependence and queue limitations.
The [Tuna early-label map replay](evidence/tuna-projector-geometry/early-label-map-analysis.md)
bounds fixed relabeling by the retained terminal-label differences.
The [Tuna readout identifiability design](design/tuna-readout-mapping-identifiability.md) constructs
observationally equivalent stage models and identifies the independent traces that can separate them.
The [sequential-projector geometry case](design/tuna-projector-geometry.md) derives its observables and
links the [calibration datasource diagnosis](evidence/tuna-projector-geometry/README.md).
The approved [QX conformance batch](evidence/tuna-projector-geometry/qx-conformance.md) passes all 18 frozen checks;
The user-authorized [Tuna qualification](design/tuna-projector-qualification-admission.md)
[completed with qualification refusal](evidence/tuna-projector-geometry/tuna-qualification.md):
all shots were retained, while contrast and repeated-readout consistency screens failed.
The [ordered readout-response successor](design/tuna-readout-ordered-response-admission.md)
qualifies a bounded descriptive comparison with serial single-job dispatch and explicit drift limits;
its [upstream report](notes/quantum_inspire/upstream-readout-report.md) remains unsent.
The [receipt-chain repair admission](evidence/tuna-projector-geometry/readout-ordered-response-reviewed-admission.json)
binds the repaired campaign; the earlier `readout-ordered-response-admission.json` is a historical pre-review observation.
The [verification receipt](evidence/tuna-projector-geometry/readout-ordered-response-verification.json)
records 116 passing focused tests, static checks, compiler replay and the 59-file historical-byte comparison.
The [requested high-effort peer review](archive/reviews/tuna-ordered-response-admission-review.md)
accepts the exact descriptive case for owner approval while retaining its causal limits.
The [approval-time observation](evidence/tuna-projector-geometry/readout-ordered-response-approval-admission.json)
refreshes availability for the same case; every dispatch still requires fresh admission.
The [source-scope revalidation](evidence/tuna-projector-geometry/source-scope-revalidation.md)
corrects historical prospective/unmeasured wording through an addendum while preserving retained source bytes.
The approved [ordered-response acquisition](evidence/tuna-projector-geometry/ordered-response-acquisition.md)
ended at its request deadline after three nominal-zero jobs. All 12,288 submitted shots were retained;
the whole-case endpoint is unavailable and the descriptive prefix leaves causal attribution unresolved.
The separately approved [nominal-one destination case](design/tuna-readout-destination-one-admission.md)
uses three serial jobs, a measured-wait allowance and its own
[12-cell uncertainty contract](evidence/tuna-projector-geometry/destination-one-response-uncertainty.md).
The [final admission verification](evidence/tuna-projector-geometry/destination-one-admission-verification.json)
retains the exact packet, 279 focused tests, historical-file comparison and requested high-effort
[peer-review acceptance](archive/reviews/tuna-destination-one-admission-review.md).
The [completed nominal-one acquisition](evidence/tuna-projector-geometry/nominal-one-destination-response.md)
retains 12,288 shots and bounded response equivalence, while the repeated-readout anomaly persists.
The [upstream evidence request](notes/quantum_inspire/destination-response-upstream-request.md) records
the verified API/datasource limits and the unsent acquisition-map, settings and IQ request.
The [lossless final-result projection replay](evidence/tuna-projector-geometry/destination-final-result-projection-replay.md)
makes the six endpoint-equivalence observations independently checkable from retained acquisition data.
The [retention verification](evidence/tuna-projector-geometry/destination-one-retention-verification.json)
binds the acquired evidence, final reviews, focused checks and measured preservation comparisons.
The [joint-response reanalysis](evidence/tuna-projector-geometry/joint-response-analysis.md) replays
six-bit outcome distributions and post-acquisition parity bounds without changing either frozen decision.
The [package-checked joint algebra analysis](evidence/tuna-projector-geometry/joint-algebra-package-analysis.md)
compares exact data-derived associators, retained package tables and an installed split-algebra control.
The [provider API/billing audit](evidence/provider-api-audit/README.md) separates physical capacity,
native execution limits, billing units and MCP observations. The
[provider-counter audit](evidence/provider-counter-audit/README-v2.md) names the population every retained shot,
sample and exposure counter counts, traces each to its scientific sinks and reconciles the claims they support. The
[current-balance packed-response case](design/packed-pauli-response-current-balance.md) compares randomized
density interventions and a separately labeled trapped-ion qualification; every generated program remains
unsubmitted and native-unadmitted. Its [implementation plan](design/provider-api-billing-research-plan.md)
retains the historical checklist; the [plan records](state/plans/) own reconciled work status.
The [publication-status ledger](SOURCES.json) distinguishes journal identities from preprint versions;
the [bibliographic reconciliation](notes/papers/hypercomplex_quantum_crossref_records.md) records reading scopes.

The active [C5 exact replay](evidence/c5_zero_divisor_code/replay-exact.py) uses rational products
and matrices for certificates, retaining numerical noisy decoding and the original result bytes.
The checksum-bound historical README and replay keep their bytes. The active source ledgers
for [kernel determinants](evidence/kernel_determinant/SHA256SUMS-ordered-map-cancel),
[projective limits](evidence/projective_kernel_limits/SHA256SUMS-ordered-map-cancel) and
[real frontiers](evidence/real_frontier_graphs/SHA256SUMS-ordered-map-cancel) bind the
`parallel.py` whose `ordered_map` cancels its queued chunks once an item raises, and preserve every
other identity of their `SHA256SUMS-exact-int-dimension` predecessors, which bind the `cd_core.py`
whose dimension guard admits only exact int, and of the earlier `SHA256SUMS-exact-contracts` and
historical `SHA256SUMS` files.

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
| Quandela run | [README](notes/quandela/README.md), [platform-specifications.md](notes/quandela/platform-specifications.md), [strategy.md](notes/quandela/strategy.md) (section 1b: building and running a case), [credit optimization](runbooks/quandela-credit-optimization.md) (job shape and cost) |
| IQM run | [README](notes/iqm/README.md), [os-4.7.md](notes/iqm/os-4.7.md) |
| Simulation and Kaggle | [README](notes/kaggle/README.md), [substrates.md](notes/kaggle/substrates.md), [gpu-runbook.md](notes/kaggle/gpu-runbook.md) |
| Algebra and proofs | `gororoba_quantum/cd_core.py`, [algebra_circuit_rules.md](notes/algebra_circuit_rules.md), [formal_certificates](evidence/formal_certificates/README.md) |
| Sources and papers | [INDEX.md](INDEX.md), [SOURCES.json](SOURCES.json), `verify_sources.py` |
| CI and gates | [ci/AGENTS.md](../ci/AGENTS.md), [ci-runtime.md](runbooks/ci-runtime.md) |
| Pull-request reviews | [AGENTS.md](../AGENTS.md) "Reviews and merges", [copilot-instructions.md](../.github/copilot-instructions.md), [codex-review-loop.md](runbooks/codex-review-loop.md), [codex-review-stalls.md](runbooks/codex-review-stalls.md), `scripts/codex_review_wait.sh` |
| State and records | [research_state.json](state/research_state.json), [QPU_RUN_CENSUS.md](state/QPU_RUN_CENSUS.md), [AGENTS.md](../AGENTS.md) "Records" |

## Files by area

### Rules

| File | Contents |
|---|---|
| [design/readout-information-context-and-budget.md](design/readout-information-context-and-budget.md) | Classical information-order controls and prospective provider-budgeted experiments |
| [gororoba_quantum/AGENTS.md](../gororoba_quantum/AGENTS.md) | module guide for the circuit and runner code |
| [scripts/AGENTS.md](../scripts/AGENTS.md) | guide for the platform, replay and census scripts |
| [kaggle_kernel/AGENTS.md](../kaggle_kernel/AGENTS.md) | Kaggle kernel program and its bundle rules |

### Sources and papers

| File | Contents |
|---|---|
| [notes/papers/](notes/papers/) | one note per registered source, named by arXiv-style id or author-year |
| [casimir-warp-primary-sources.md](notes/papers/casimir-warp-primary-sources.md) | Five primary-source identities, actual response receipts and reading scopes for the Casimir/warp claim and local stress distinction |
| [quaternionic-foundational-source-review.md](notes/papers/quaternionic-foundational-source-review.md) | historical QQM citation identities and remaining reading obligations |
| [quaternionic-optical-bound-reading.md](notes/papers/quaternionic-optical-bound-reading.md) | model-specific optical bound and Procopio/Adler exchange body-reading addendum |
| [aflow-a_cf4-225-a.md](notes/papers/aflow-a_cf4-225-a.md) | AFLOW crystallographic prototype A_cF4_225_a |
| [1602.06402.md](notes/papers/1602.06402.md) | Hinuma et al. 2017 HPKOT band paths: the crystallographic k-point convention SeeK-path implements and its departures from Setyawan-Curtarolo |
| [1808.01590.md](notes/papers/1808.01590.md) | Togo, Shinohara and Tanaka spglib: iterative tolerance-driven space-group search |
| [elkies-2013-m256.md](notes/papers/elkies-2013-m256.md) | Elkies 2013 course page on error-correcting codes |
| [mckay-hadamard-matrices.md](notes/papers/mckay-hadamard-matrices.md) | McKay Hadamard equivalence-class data and the retained order-16 list |
| [schafer-1954-cayley-dickson-flexible.md](notes/papers/schafer-1954-cayley-dickson-flexible.md) | Schafer 1954 flexibility of Cayley-Dickson algebras, metadata and secondary statement |
| [2205.07986.md](notes/papers/2205.07986.md) | Ren and Zhao 2023 closed-form Cayley-Dickson twist function and its convention map |
| [1107.1375.md](notes/papers/1107.1375.md) | Bales 2003 twisted group algebras and the recursive Cayley-Dickson twist, with its index and product convention |
| [2103.12805.md](notes/papers/2103.12805.md) | Flaut and Boboescu 2021 twist-tree recursion and the twisted-group-algebra theorem for the Cayley-Dickson process (hosted, CC BY 4.0) |
| [1003.0429.md](notes/papers/1003.0429.md) | Morier-Genoud and Ovsienko 2011 cubic twisted group algebras; the octonion cochain and the Cayley-Dickson algebras outside the cubic class |
| [2608.26890.md](notes/papers/2608.26890.md) | Zhilina 2024 diameter 3 of the commutativity graph of the real sedenion zero divisors (arXiv 2026 posting, external-only) |
| [guterman-zhilina-2023-split-algebras.md](notes/papers/guterman-zhilina-2023-split-algebras.md) | Guterman and Zhilina 2023 split-algebra zero divisors and relation graphs, abstract only (no open copy) |
| [cawagas-2004-sedenion-structure.md](notes/papers/cawagas-2004-sedenion-structure.md) | Cawagas 2004 sedenion loop census, quasi-octonions and Proposition 2, read in full from the archived PDF and recomputed against `cd_core` (external-only) |
| [2512.07210.md](notes/papers/2512.07210.md) | Wilmot 2026 sedenion automorphisms: the graded sedenion table and 35-term calibration (both agree with `cd_core`), and the Schafer and Brown discrepancy for `Aut(S)` |
| [2609.10569.md](notes/papers/2609.10569.md) | Gresnigt 2026 review of the sedenion `S3` family symmetry: Table 5 (11 printed defects against `cd_core`) and the `S3` maps `epsilon` and `psi`, certified on basis pairs |
| [sources/cayley-dickson-2n-ion-survey.md](sources/cayley-dickson-2n-ion-survey.md) | survey of Cayley-Dickson sources at dimension 16 and above: candidate table, dispositions, convention map and mismatches |
| [0804.3416.md](notes/papers/0804.3416.md) | de Marrais 2008 box-kite emanation tables: rules 0 to 2 and the CPO trip counts to 256 dimensions replayed, Brocade Table 1 (42 of 42 cells), and the emanation-table formula |
| [0907.2047.md](notes/papers/0907.2047.md) | Cawagas et al. 2009 the 373 subloops of the 32-dimensional Cayley-Dickson loop, the Moufang counts per order-16 subloop and their tie to the associator census |
| [math-0404395.md](notes/papers/math-0404395.md) | Moreno 2004 alternative elements: the two-term alternative elements equal the nullity-0 two-term elements (126 at 16, 342 at 32) |
| [math-0512516.md](notes/papers/math-0512516.md) | Moreno 2005 monomorphisms between Cayley-Dickson algebras and the Theorem 2.5 dichotomy |
| [math-0405424.md](notes/papers/math-0405424.md) | Moreno 2004 the exponential map on the Cayley-Dickson algebras and the centralizer identity of Remark 2 |
| [math-0404172.md](notes/papers/math-0404172.md) | Moreno 2004 Hopf construction in higher dimensions and the associator identity of Lemma 4.4 |
| [1102.5151.md](notes/papers/1102.5151.md) | Kirshtein 2011 automorphism groups of Cayley-Dickson loops: orders 2, 24, 1344, 2688 and the unsound third claim of Lemma 36 |
| [1405.6888.md](notes/papers/1405.6888.md) | Saniga et al. 2014 finite geometry of the Cayley-Dickson tower: Tables 1 to 3 against `cd_core` (opposite algebra on the basis) and the line counts for 8 to 64 dimensions |
| [2606.27798.md](notes/papers/2606.27798.md) | Aryapoor, Back and Pautrel 2026 involutions in the Cayley-Dickson construction: alpha and beta involutions, nuclei and commuter of dimension 1 at 8, 16 and 32 |
| [2609.11588.md](notes/papers/2609.11588.md) | Lemley 2026 quasilinear multiplication: Algorithm 3.5 replayed for 2 to 256 dimensions and the multiplication-count bound (hosted, CC BY 4.0); version 2 generalizes to commutative rings, adds the tensor-rank corollary and an octonion base case that lowers the counts at 16 dimensions and above |
| [skiouris-2026-algebraic-hiddenness.md](notes/papers/skiouris-2026-algebraic-hiddenness.md) | Skiouris 2026 algebraic hiddenness in the sedenions: the determinant identity det L_p = (|p|^2)^4 T^2, the 4-8-4 Gram spectrum and R_l centrality against `cd_core`, and the unchecked bundle and holonomy layer (hosted, CC BY 4.0) |
| [skiouris-2026-aphanics-pathion.md](notes/papers/skiouris-2026-aphanics-pathion.md) | Skiouris 2026 aphanics at the pathion level: 15, 126 and 84 basis pairs by Gram spectrum, the Clifford triad and the octonion and sedenion identities against `cd_core` (hosted, CC BY 4.0) |
| [levratti-2026-sign-parity-zero-divisors.md](notes/papers/levratti-2026-sign-parity-zero-divisors.md) | Levratti 2026 sign-parity classification: the closed count 336 x [n-1 choose 3]_2 equals 336 at 16 and 5040 at 32 dimensions under `cd_core`, weight-3 invertibility and kernel dimensions (hosted, CC BY 4.0) |
| [1505.05210.md](notes/papers/1505.05210.md) | Kustin, Polini and Ulrich 2017 blowup algebras of height three Gorenstein ideals: Rees ideal J = L + I_d(B) + C(phi), the special fiber equations and the A_5 fiber-cone hypotheses it needs |
| [1207.1060.md](notes/papers/1207.1060.md) | Branco Correia and Zarzuela 2013 divisors of a module and blow up: Fitting, determinant and Bourbaki ideals, analytic spread bounds and universal flattening |
| [2302.07486.md](notes/papers/2302.07486.md) | Kumar and Venugopal 2023 Rees algebra of maximal order Pfaffians: linear type, the quadratic Rees relations, Koszul diagonals and the nonquadratic sparse 7 x 7 case against the A_5 fiber cones (hosted, CC BY 4.0) |
| [2104.13811.md](notes/papers/2104.13811.md) | Cooper and Price 2021 degree bounds for Rees equations of determinantal and Pfaffian ideals: Proposition 5.1.2 and Theorems 5.4.3 and 5.4.5 and why no bound reaches the A_5 fiber-cone equations (hosted, CC BY 4.0) |
| [alg-geom-9707001.md](notes/papers/alg-geom-9707001.md) | Bertram 1997 complete skew forms: the closure of the Pfaffian map and Theorem 3.3 as the container of the limiting kernels of the A_5 strata |
| [1803.09011.md](notes/papers/1803.09011.md) | Massarenti 2020 spaces of complete skew-forms: Construction 2.3, Theorems 1.1 and 1.2 and the corank-one frame of the kernel map |
| [math-0105151.md](notes/papers/math-0105151.md) | Ghorpade and Krattenthaler 2003 Hilbert series of Pfaffian rings: equation (9), Theorem 2 and the h-vector (1, 6, 6, 1) of the cone over G(2, 6) |
| [1308.0582.md](notes/papers/1308.0582.md) | Jeffries, Montano and Varbaro 2015 j-multiplicity and fiber cone degree: Theorems 3.1 and 6.3 for the algebra of Pfaffians and why they fix only the ambient degree |
| [math-0302241.md](notes/papers/math-0302241.md) | Corso, Ghezzi, Polini and Ulrich 2004 Cohen-Macaulay special fibers: Theorem 2.2 and the relation-count obstruction for the A_5 fibers |
| [math-0212119.md](notes/papers/math-0212119.md) | D'Cruz, Raghavan and Verma 1999 Cohen-Macaulay fiber cones: the Hilbert series criterion of Theorem 2.1 and the numerator test on the tracked A_5 fiber Hilbert functions |
| [2512.16165.md](notes/papers/2512.16165.md) | Ansaldi, Lira, Mostafazadehfard, Saloni and Seccia 2025 special fibers of Hankel coordinate sections: the Main Theorem and the method of identifying a fiber with that of 2-minors |
| [conca-herzog-valla-1996-sagbi-bases.md](notes/papers/conca-herzog-valla-1996-sagbi-bases.md) | Conca, Herzog and Valla 1996 Sagbi bases and the blow-up algebras of rational normal scrolls (introduction read) |
| [conca-herzog-trung-valla-1997-diagonal-subalgebras.md](notes/papers/conca-herzog-trung-valla-1997-diagonal-subalgebras.md) | Conca, Herzog, Trung and Valla 1997 diagonal subalgebras of bigraded algebras (JSTOR and Project MUSE downloads; abstract and definition read) |
| [math-0402345.md](notes/papers/math-0402345.md) | Gannon 2006 moonshine survey: the moonshine module, Borcherds proof and the Norton series, as the citation for moonshine statements |
| [1208.6254.md](notes/papers/1208.6254.md) | Carnahan 2016 monstrous Lie algebras and Norton's generalized moonshine conjecture (abstract and introduction read) |
| [1812.08439.md](notes/papers/1812.08439.md) | Cunha and Elduque 2020 codes, S-structures and the exceptional Lie algebras E7 and E8 (abstract and introduction read) |
| [2504.16513.md](notes/papers/2504.16513.md) | Kollross 2026 explicit E8 bracket from triality and oct-octonions (abstract and introduction read) |
| [2009.00390.md](notes/papers/2009.00390.md) | Dray, Huerta and Kincaid 2014 the 2 x 2 magic square of Lie groups (abstract and introduction read) |
| [math-0411104.md](notes/papers/math-0411104.md) | Krutelevich 2007 Freudenthal construction on cubic Jordan algebras and Bhargava composition (abstract and contents read) |
| [2605.09333.md](notes/papers/2605.09333.md) | Corradetti 2026 Coxeter-Dickson order, para-octonions and the Okubo algebra on the E8 lattice (hosted, CC BY 4.0; abstract and introduction read) |
| [2204.04996.md](notes/papers/2204.04996.md) | Wilson, Dray and Manogue 2023 3 x 3 matrix construction of E8 over octonions (abstract and introduction read) |
| [2401.10534.md](notes/papers/2401.10534.md) | Dray, Manogue and Wilson 2024 E7 and its 56-dimensional representation inside E8: Albert algebra H_3(O), equations (15) to (20) |
| [0909.0551.md](notes/papers/0909.0551.md) | Baez and Huerta 2010 division algebras and supersymmetry in dimensions 3, 4, 6 and 10 (abstract and introduction read) |
| [1102.4857.md](notes/papers/1102.4857.md) | Ferrara, Marrani and Yeranyan 2011 Freudenthal duality in generalized special geometry (abstract read) |
| [1402.0206.md](notes/papers/1402.0206.md) | Flaut 2014 survey of algebras from the Cayley-Dickson process over fields (abstract and introduction read) |
| [2311.16704.md](notes/papers/2311.16704.md) | Chapman and Vishkautsan 2025 polynomial roots and left eigenvalues over Cayley-Dickson algebras; the doubling coincides with cd_core at gamma = -1; the PDF carries a CC BY-SA 4.0 notice |
| [1307.3641.md](notes/papers/1307.3641.md) | Flaut and Shpakivskyi 2015 Dirac-operator holomorphic functions on Cayley-Dickson algebras (abstract and introduction read) |
| [math-0403263.md](notes/papers/math-0403263.md) | Cohn and Kumar 2009 the Leech lattice is the densest lattice in R^24 and E8 in R^8 (abstract and introduction read) |
| [2307.02505.md](notes/papers/2307.02505.md) | Tang and Tang 2023 sedenion model of lepton generations: the abstract's claim of three octonion subalgebra types, unverified (hosted, CC BY 4.0) |
| [2304.01213.md](notes/papers/2304.01213.md) | Singh 2023 exceptional Jordan algebra essay on gravitation (abstract read; claims unverified) |
| [2606.15235.md](notes/papers/2606.15235.md) | Baez and Schwahn 2026 Standard Model gauge group from F4 acting on Jordan subalgebras of h_3(O) (abstract and introduction read) |
| [hep-th-0301037.md](notes/papers/hep-th-0301037.md) | Boya 2003 octonions in M-theory review (abstract and introduction read) |
| [2112.09698.md](notes/papers/2112.09698.md) | D'Andrea, Landi and Lizzi 2022 tolerance algebras: Proposition 7 and the statement that Cayley-Dickson algebras of dimension 8 and above are not tolerance algebras |
| [2410.14267.md](notes/papers/2410.14267.md) | Fox and Tkachev 2024 Hsiang and quasicomposition algebras and the tripling construction as an analogue of doubling (hosted, CC BY 4.0) |
| [2208.03285.md](notes/papers/2208.03285.md) | Aurisano and Whitehead 2022 deep-learning image classification in high-energy physics; no hypercomplex content (hosted, CC BY 4.0) |
| [conway-norton-1979-monstrous-moonshine.md](notes/papers/conway-norton-1979-monstrous-moonshine.md) | Conway and Norton 1979 monstrous moonshine: observations (A) to (G), the series J and T_m, and the degrees of Table 1 |
| [0811.4523.md](notes/papers/0811.4523.md) | Tuite 2009 exceptional vertex operator algebras: abstract and introduction (Deligne series, Moonshine module, Griess algebra) |
| [hep-th-0205068.md](notes/papers/hep-th-0205068.md) | Gaberdiel, Olive and West 2002 Lorentzian Kac-Moody algebras (abstract read) |
| [0810.2088.md](notes/papers/0810.2088.md) | Connes 2013 Theorems 1.1 and 1.2 on spectral triples of manifolds |
| [hep-th-9209099.md](notes/papers/hep-th-9209099.md) | Lada and Stasheff 1993 sh Lie structures: skew symmetric l_n of degree 2 - n (cochain) and n - 2 (chain) |
| [math-ph-0507015.md](notes/papers/math-ph-0507015.md) | Fernandez Nunez, Garcia Fuertes and Perelomov 2005 E7 Calogero-Sutherland Hamiltonian (5), ground state and the kappa = 1 characters |
| [2207.14076.md](notes/papers/2207.14076.md) | Lin 2024 orbifolds of the Monster CFT and topological modular forms (abstract read) |
| [math-0404517.md](notes/papers/math-0404517.md) | Eisenbud, Green, Hulek and Popescu 2006 small schemes: Theorems 0.2 and 0.4 (2-regular = small = linearly joined varieties of minimal degree) applied to the E8-bar to VB fiber candidate |
| [1404.7403.md](notes/papers/1404.7403.md) | Weinstein and Yekutieli 2020 selective sign-determining confidence intervals: BY FCR-adjusted selection (Definition 1), directional BH sign selection with FCR at most q (Definition 2, Theorem 1), selection on independent data (Theorem 3) |
| [efron-2011-tweedie-formula.md](notes/papers/efron-2011-tweedie-formula.md) | Efron 2011 Tweedie's formula and selection bias: E{mu given z} = z + sigma^2 l'(z), the normal-normal and James-Stein forms (3.7)-(3.9), regret and the widened empirical Bayes interval (7.26) |
| [2603.20495.md](notes/papers/2603.20495.md) | Chapman and Levin 2026 central products of Cayley-Dickson loops: associativity degree for 4 to 64 dimensions (hosted, CC BY 4.0) |
| [2501.00123.md](notes/papers/2501.00123.md) | Chapman, Levin, Vishne and Zaninelli 2024 loops with involution: the automorphism-group statement of the abstract against exact counts |
| [1707.07318.md](notes/papers/1707.07318.md) | Bales 2017 the eight doubling products: `P3T` equals `cd_core`, four of the eight are not octonionic, and the twist rules reproduce to 64 dimensions |
| [1107.1301.md](notes/papers/1107.1301.md) | Bales 2011 catalog of 32 Cayley-Dickson-like products: the eight quaternion-property products, the label map to 1707.07318 and the Table 7 title |
| [hep-th-0601033.md](notes/papers/hep-th-0601033.md) | Kuwata, Fujii and Nakashima 2006 alternativity and reciprocity: the Gram operator spectrum of alternative pairs (4/8/4 sectors at 16, five clusters at 32) |
| [2505.06011.md](notes/papers/2505.06011.md) | Wilmot 2025 G2 and the 30 primary 3-forms: Table 1 classes, the 12 zero divisors of the pseudo-octonion algebras, the 15-dimensional counts and the unsupported isomorphism claim |
| [2205.05605.md](notes/papers/2205.05605.md) | Chapman, Guterman, Vishkautsan and Zhilina 2022 roots and critical points of polynomials: the sedenion counterexamples of Example 2.6 and spherical roots |
| [2512.22134.md](notes/papers/2512.22134.md) | Gazeau 2026 the (R+L) mnemonic matrix rule for octonions and the Cayley-Dickson tower, the opposite algebra of `cd_core` (hosted, CC BY 4.0) |
| [brown-1967-generalized-cayley-dickson.md](notes/papers/brown-1967-generalized-cayley-dickson.md) | R. B. Brown 1967 generalized Cayley-Dickson algebras: Aut(A_t) = Aut(A_(t-1)) x S3 for t = 4 to 6 and the order-3 map psi |
| [chan-dokovic-2006-sedenion-subalgebras.md](notes/papers/chan-dokovic-2006-sedenion-subalgebras.md) | Chan and Dokovic 2006 conjugacy classes of subalgebras of the real sedenions: the subalgebra census and the 6-dimensional zero-divisor subspace |
| [1907.07024.md](notes/papers/1907.07024.md) | Heikoop et al. 2020 morphisms of skew Hadamard matrices: the field-isomorphism map from quaternary unit Hadamard matrices to real Hadamard matrices |
| [ocathain-2012-nonaffine-hadamard.md](notes/papers/ocathain-2012-nonaffine-hadamard.md) | O Cathain 2012 doubly transitive automorphism groups of Hadamard matrices: Ito's classification, Paley matrices and `PSL_2(q)`, skew difference sets (deposited text) |
| [kivunge-2013-sign-matrices-2n-ons.md](notes/papers/kivunge-2013-sign-matrices-2n-ons.md) | Kivunge 2013 conference slides on sign matrices of the `2^n`-ons: Hadamard and skew Hadamard claims, Smith-Conway sign matrices equal to the `cd_core` transpose |
| [0709.1447.md](notes/papers/0709.1447.md) | Luhn, Nasri and Ramond 2007 `PSL_2(7)`: presentation, classes, character table, subgroups and the Klein quartic |
| [2007.01808.md](notes/papers/2007.01808.md) | Ziller 2020 differences between consecutive numbers coprime to primorials: the restricted-covering reduction, the table of missing differences for `k <= 44` and the Jacobsthal-function conjecture |
| [erdos-854-consecutive-coprime-gaps.md](notes/papers/erdos-854-consecutive-coprime-gaps.md) | Erdos Problem 854 (Bloom's database): the smallest even integer missing from the gaps between consecutive integers coprime to a primorial, status at retrieval and cited literature |
| [openai-2026-jacobsthal-quadratic-bound.md](notes/papers/openai-2026-jacobsthal-quadratic-bound.md) | OpenAI 2026 (openai/math family 021, unrefereed, model-generated) quadratic bound `h(k) << k^2/(log log 3k)^2` for Jacobsthal's function: non-explicit constant, Lean statement under Erdos Problem 970, and the map from Ziller's primorial `h(k)` |
| [openai-2026-mub-dimension-six.md](notes/papers/openai-2026-mub-dimension-six.md) | OpenAI 2026 (openai/math family 266, unrefereed) computer-assisted `N(6) = 3` for mutually unbiased bases: binary64 and compiler contract, the 4 October 2026 execution, and a Lean check that reaches only five bases |
| [openai-2026-hadamard-order-six-fourier-certificates.md](notes/papers/openai-2026-hadamard-order-six-fourier-certificates.md) | OpenAI 2026 (openai/math family 266, unrefereed) exact rational certificates: Fourier vanishing for order-six complex Hadamard matrices outside the cubic class and no seven mutually unbiased bases in `C^6` |
| [openai-2026-exact-quantum-factoring.md](notes/papers/openai-2026-exact-quantum-factoring.md) | OpenAI 2026 (openai/math family 279, unrefereed) probability-one factoring over NOT, CNOT, Toffoli, H and S: dyadic order trials, one amplification step at success 1/4, and its distance from the hybrid Shor gate model |
| [openai-2026-torsion-free-zero-divisors.md](notes/papers/openai-2026-torsion-free-zero-divisors.md) | OpenAI 2026 (openai/math family 196, unrefereed) zero divisors in F_2[G] for a finitely presented torsion-free G by odd-degree graph parity over projective-plane label types; probabilistic, Lean Comparator statement |
| [openai-2026-torsion-free-not-directly-finite.md](notes/papers/openai-2026-torsion-free-not-directly-finite.md) | OpenAI 2026 (openai/math family 197, unrefereed) ab = 1, ba != 1 in F_2[G] for a finitely presented torsion-free G, with seven extra labels on the complements of the Fano lines; unformalized |
| [openai-2026-kadison-kaplansky-projection.md](notes/papers/openai-2026-kadison-kaplansky-projection.md) | OpenAI 2026 (openai/math family 285, unrefereed) a projection of trace in (0, 1/2) in the reduced C*-algebra of a finitely generated torsion-free group, absent from its group ring; unformalized |
| [pmc-4957665-nonlinearity-measures.md](notes/papers/pmc-4957665-nonlinearity-measures.md) | nonlinearity measures for Boolean functions |
| [2306.00874.md](notes/papers/2306.00874.md) | Maring et al. 2024 Quandela Ascella platform: source, chip, phase-voltage model and gate benchmarks |
| [2310.15349.md](notes/papers/2310.15349.md) | Fyrillas et al. 2024 clear-box machine-learning characterization of a 12-mode photonic chip: imperfection model and amplitude fidelities (hosted, CC BY 4.0) |
| [2506.05988.md](notes/papers/2506.05988.md) | Fyrillas et al. 2025 induced phase shifters and the acyclic-pruned-graph crosstalk-robustness criterion (hosted, CC BY 4.0) |
| [2606.18408.md](notes/papers/2606.18408.md) | Tully et al. 2026 Walsh parity-check filters on Belenos: fixed-pattern bias, compilation-dependent leakage and a calibration-linked HOM episode (unrefereed) |
| [2005.01743.md](notes/papers/2005.01743.md) | Ollivier et al. 2021 Hong-Ou-Mandel visibility with multi-photon noise: separation of g2 and indistinguishability |
| [quant-ph-0302031.md](notes/papers/quant-ph-0302031.md) | Horodecki, Shor and Ruskai 2003 entanglement-breaking channels: measure-and-prepare form and the Choi-state separability test |
| [quant-ph-9807091.md](notes/papers/quant-ph-9807091.md) | Horodecki et al. 1999 teleportation channel: average fidelity from singlet fraction, `f = (F d + 1)/(d + 1)`, and the classical bound `2/(d + 1)` |
| [1210.4583.md](notes/papers/1210.4583.md) | Chitambar et al. 2014 LOCC survey: the inclusion of LOCC in separable operations |
| [quant-ph-0007058.md](notes/papers/quant-ph-0007058.md) | Calsamiglia and Lutkenhaus 2001 linear-optical Bell-state analyzer: the 50 percent bound and its assumptions |
| [quant-ph-9605038.md](notes/papers/quant-ph-9605038.md) | Horodecki et al. 1996 separability criterion: positive partial transpose is exact for 2x2 and 2x3 |
| [2411.12387.md](notes/papers/2411.12387.md) | Laneve et al. 2024 teleportation between two dissimilar quantum dots over fiber and a 270 m free-space link: sources, tuning, measured fidelities |
| [1103.1528.md](notes/papers/1103.1528.md) | Specht et al. 2011 single-atom memory: the N-copy measure-and-prepare bound (N+1)/(N+2), its Poisson average and the efficiency-simulating classical memory |
| [1201.4149.md](notes/papers/1201.4149.md) | Gündoğan et al. 2012 solid-state polarization-qubit storage: the efficiency-constrained classical benchmark for weak coherent inputs (Eq. 1, Appendix A) |
| [quant-ph-0301059.md](notes/papers/quant-ph-0301059.md) | Gill 2003: martingale treatment of time and memory in Bell tests and its finite-statistics bound |
| [1108.2468.md](notes/papers/1108.2468.md) | Zhang, Glancy and Knill 2011: prediction-based-ratio test factors, p-values valid under memory and drift |
| [1312.2999.md](notes/papers/1312.2999.md) | Bierhorst 2015: a Clauser-Horne trial model with memory and exact supermartingale p-values against Azuma-Hoeffding |
| [2310.20521.md](notes/papers/2310.20521.md) | Polacchi et al. 2024 quantum-dot single-rail teleportation: its measure-and-prepare benchmark under loss |
| [1301.1170.md](notes/papers/1301.1170.md) | Chiribella and Xie 2013: probabilistic measure-and-prepare benchmarks, the fidelity of a trace-nonincreasing operation conditioned on success (Theorems 2 and 5) |
| [1901.02260.md](notes/papers/1901.02260.md) | Anderson et al. 2020 telecom quantum-dot teleportation: g2 0.177, temporal postselection, six inputs against 2/3 |
| [1210.1282.md](notes/papers/1210.1282.md) | Ma et al. 2012 high-loss free-space teleportation: six inputs and the stated same-quality-for-all-bases assumption |
| [2411.12904.md](notes/papers/2411.12904.md) | Strobel et al. 2024 remote quantum-dot teleportation at telecom wavelengths: purity model, three-fold coincidence ratio, temporally postselected mean against 2/3 |
| [1302.0932.md](notes/papers/1302.0932.md) | van Enk and Blume-Kohout 2013 common-state assumption of tomography and the Akaike test for source drift |
| [2004.14018.md](notes/papers/2004.14018.md) | White et al. 2020 process-tensor characterization and the intervention-based memory lower bound on IBM devices |
| [riley-2008-nist-sp-1065.md](notes/papers/riley-2008-nist-sp-1065.md) | Riley 2008 NIST SP 1065: Allan, overlapping Allan and modified Allan variances and the noise types they separate |
| [quant-ph-0501020.md](notes/papers/quant-ph-0501020.md) | Toth and Guhne 2005 stabilizer entanglement witnesses and the two-qubit Bell-fidelity form F > 1/2 |
| [jafferis-2022-traversable-wormhole.md](notes/papers/jafferis-2022-traversable-wormhole.md) | Jafferis et al. 2022 traversable wormhole dynamics on a quantum processor: abstract-level record of a closed article |
| [2302.07897.md](notes/papers/2302.07897.md) | Kobrin, Schuster and Yao 2023 comment on the wormhole-dynamics experiment (hosted, CC BY 4.0) |
| [2303.15423.md](notes/papers/2303.15423.md) | Jafferis et al. 2023 reply to the comment: counterfactual scenarios, size winding and random-Hamiltonian null (hosted, CC BY 4.0) |
| [2310.16903.md](notes/papers/2310.16903.md) | Silvestri et al. 2024 -- fiber Sagnac interferometer with two-photon entanglement measures Earth's rotation (715 m^2; 2.8 and 5.5 mrad) |
| [1807.06205.md](notes/papers/1807.06205.md) | Planck 2018 results I: solar-system dipole velocity relative to the CMB (369.82 km/s) and its direction |
| [2206.00570.md](notes/papers/2206.00570.md) | Dreissen et al. 2022 -- Yb+ composite-pulse Ramsey bounds on Lorentz violation at the 10^-21 level, sidereal modulation |
| [ioannidis-2005-false-findings.md](notes/papers/ioannidis-2005-false-findings.md) | Ioannidis 2005 positive predictive value of a significant finding under bias and repeated testing, with the Table 4 reproduction |
| [munafo-2017-reproducible-science.md](notes/papers/munafo-2017-reproducible-science.md) | Munafo et al. 2017 manifesto: preregistration, outcome switching, disclosure arithmetic, data masking and registered reports |
| [asa-2016-p-value-statement.md](notes/papers/asa-2016-p-value-statement.md) | ASA 2016 six principles on p-values, from the ASA release (statement body unread) |
| [diedenhofen-musch-2015-cocor.md](notes/papers/diedenhofen-musch-2015-cocor.md) | Diedenhofen and Musch 2015 cocor: tests for comparing independent and dependent correlations, Williams, Steiger, Meng and Zou formulas with a reproduction check |
| [1910.06343.md](notes/papers/1910.06343.md) | Eisert et al. 2020 quantum certification and benchmarking: information, assumptions and complexity of each protocol family |
| [2407.08828.md](notes/papers/2407.08828.md) | Proctor et al. benchmarking quantum computers: benchmark properties, drift and non-Markovian error, compilation gaming and error-mitigated results |
| [quantum-journal-referee-instructions.md](notes/papers/quantum-journal-referee-instructions.md) | Quantum journal referee questions and editorial policies (web receipts) |
| [quant-ph-0203033.md](notes/papers/quant-ph-0203033.md) | Peres, Scudo and Terno 2002 -- spin entropy of a free spin-1/2 particle is not Lorentz covariant |
| [2109.12238.md](notes/papers/2109.12238.md) | Bothwell et al. 2022 -- gravitational redshift gradient resolved within a millimeter strontium sample (-1.09e-19 per mm predicted) |
| [1105.4531.md](notes/papers/1105.4531.md) | Zych et al. 2011 -- interferometric visibility as a witness of general-relativistic proper time, V = |cos(Delta E Delta V Delta T / 2 hbar c^2)| |
| [1311.1095.md](notes/papers/1311.1095.md) | Pikovski et al. 2015 -- decoherence of a composite particle from gravitational time dilation, tau_dec formula and estimate |
| [1707.01339.md](notes/papers/1707.01339.md) | Yin et al. 2017 -- satellite entanglement distribution over 1203 km, CHSH S = 2.37 +- 0.09 |
| [ashby-nelson-2009-gps-relativity.md](notes/papers/ashby-nelson-2009-gps-relativity.md) | Ashby and Nelson 2009 -- free-fall cancellation of solar gravity and the tidal terms in terrestrial clock comparisons (NIST author PDF) |
| [ashby-2018-null-test-lpi.md](notes/papers/ashby-2018-null-test-lpi.md) | Ashby, Parker and Patla 2018 -- local position invariance null test, beta = (2.2 +- 2.5)e-7 (NIST-hosted PDF) |
| [s10052-019-7542-5.md](notes/papers/s10052-019-7542-5.md) | Ejlli et al. 2019 -- graviton-photon mixing `M = kappa k B/(omega + k)` with `kappa^2 = 16 pi G_N`, flux Eq. 2, and the 6e-26 and 5e-28 amplitude limits above 1 THz (open-access version of record) |
| [pais-us-10135366-b2-electromagnetic-field-generator.md](notes/papers/pais-us-10135366-b2-electromagnetic-field-generator.md) | Pais US 10,135,366 B2 -- Eq. 1 to 3 with column and line locators, the 1e24 W/m^2 example, claim 1 |
| [pais-us-10144532-b2-craft-inertial-mass-reduction.md](notes/papers/pais-us-10144532-b2-craft-inertial-mass-reduction.md) | Pais US 10,144,532 B2 -- non-relativistic Eq. 1 and 2, pair-production Eq. 3, zero-point Eq. 4, Hayasaka Eq. 5 and 6, claim 1 |
| [pais-us-10322827-b2-high-frequency-gravitational-wave-generator.md](notes/papers/pais-us-10322827-b2-high-frequency-gravitational-wave-generator.md) | Pais US 10,322,827 B2 -- Eq. 1 to 4, the Gertsenshtein power law and the claimed 1e10 W output, claim 1 |
| [pais-us-2019-0058105-a1-room-temperature-superconductor.md](notes/papers/pais-us-2019-0058105-a1-room-temperature-superconductor.md) | Pais US 2019/0058105 A1 -- London depth, Meissner condition and flux-quantum equations, claim 1, no measurement |
| [pais-us-2019-0295733-a1-plasma-compression-fusion-device.md](notes/papers/pais-us-2019-0295733-a1-plasma-compression-fusion-device.md) | Pais US 2019/0295733 A1 -- Lawson, scaling, flux and field equations, the 1e6 T and 1e18 gain claims, claim 1 |
| [pais-superforce-sources.md](notes/papers/pais-superforce-sources.md) | Pais Superforce preprints (c^4/G) and their supporting references: retained CC0, CC BY PDFs, external-only reading copies, Crossref receipts |
| [2001.09190.md](notes/papers/2001.09190.md) | Vepsäläinen et al. 2020 -- ionizing radiation limits transmon T1 to about 4 ms; power density and shield test |
| [2402.03208.md](notes/papers/2402.03208.md) | Harrington et al. 2025 -- cosmic rays cause 17.1 % of correlated qubit errors; coincidence rates, qubit participation, recovery times |
| [2104.05219.md](notes/papers/2104.05219.md) | McEwen et al. 2022 -- chip-wide cosmic-ray error bursts, one per 10 s, 25 ms recovery, 26 qubits |
| [2111.08152.md](notes/papers/2111.08152.md) | Costa, An, Sanders, Su, Babbush and Berry 2021: discrete adiabatic theorem and the O(kappa log(1/epsilon)) quantum linear-system solver |
| [2305.11352.md](notes/papers/2305.11352.md) | Jennings, Lostaglio, Pallister, Sornborger and Subasi 2023: randomized adiabatic quantum linear solver with an explicit 837 kappa query bound |
| [2406.12086.md](notes/papers/2406.12086.md) | Dalzell 2024: kernel-reflection quantum linear-system solver with an explicit 56 kappa leading constant |
| [2410.18178.md](notes/papers/2410.18178.md) | Low and Su 2024: quantum linear-system algorithm with optimal state-preparation queries (Tunable VTAA) |
| [2601.16697.md](notes/papers/2601.16697.md) | Mori, Kikuchi, Benedetti and Rosenkranz 2026: Omega(kappa sqrt(s)) lower bound for sparse quantum linear-system solvers |
| [2609.22445.md](notes/papers/2609.22445.md) | Patel 2026: joint Omega(kappa sqrt(s) log(1/epsilon)) lower bound for sparse quantum linear-system solvers |
| [2502.11239.md](notes/papers/2502.11239.md) | Tu, Dubynskyi, Mohammadisiahroudi, Riashchentceva, Cheng, Ryashchentsev, Terlaky and Liu 2025: fault-tolerant space, time and energy estimates for HHL against conjugate gradient |
| [2411.02522.md](notes/papers/2411.02522.md) | Morales, Pira, Schleich, Koor, Costa, An, Aspuru-Guzik, Lin, Rebentrost and Berry 2024: survey and taxonomy of quantum linear-system solvers |
| [1910.06151.md](notes/papers/1910.06151.md) | Chia, Gilyen, Li, Lin, Tang and Wang 2019: dequantized singular value transformation for low-rank inputs under sampling access |
| [1712.06239.md](notes/papers/1712.06239.md) | Chen and Gao 2017: Macaulay-matrix HHL for Boolean polynomial systems, runtime in the condition number |
| [2111.00405.md](notes/papers/2111.00405.md) | Ding, Gheorghiu, Gilyen, Hallgren and Li 2021: condition-number lower bound that limits Macaulay-matrix HHL against Grover search |
| [2510.05588.md](notes/papers/2510.05588.md) | Li 2025: instance-aware quantum linear-system algorithm and its polynomial-system application |
| [1712.07211.md](notes/papers/1712.07211.md) | Faugere, Horan, Kahrobaei, Kaplan, Kashefi and Perret 2017: Grover-accelerated hybrid solver for Boolean multivariate quadratic systems, O(2^(0.462n)) gates |
| [2609.28901.md](notes/papers/2609.28901.md) | Lee, Jeong and Kim 2026: garbage-free reversible Gaussian elimination over GF(p^l), same field-operation count as classical elimination |
| [2608.23929.md](notes/papers/2608.23929.md) | Maeda and Yano 2026: quantum additive-error torus point counting of a Laurent polynomial over F_q, and its #P-hardness |
| [math-0411623.md](notes/papers/math-0411623.md) | Kedlaya 2004: quantum algorithm for zeta functions of curves over F_q, polynomial in genus and log q |
| [quant-ph-0405081.md](notes/papers/quant-ph-0405081.md) | van Dam 2004: zeros of finite-field zeta functions as eigenvalues of efficient unitaries (Fermat hypersurfaces) |
| [2408.08292.md](notes/papers/2408.08292.md) | Jordan, Shutty, Wootters, Zalcman, Schmidhuber, King, Isakov, Khattar and Babbush 2024: decoded quantum interferometry: optimization over F_p reduced to decoding |
| [quant-ph-0409035.md](notes/papers/quant-ph-0409035.md) | Buhrman and Spalek 2004: quantum walk verification of matrix products in O(n^(5/3)) time over an integral domain |
| [1103.0842.md](notes/papers/1103.0842.md) | Belovs 2011: span program for the rank problem (query complexity) |
| [0811.3171.md](notes/papers/0811.3171.md) | Harrow, Hassidim and Lloyd 2009: HHL algorithm, estimating x^dagger M x for a sparse system in poly(log N, kappa) time |
| [1511.02306.md](notes/papers/1511.02306.md) | Childs, Kothari and Somma 2017: Fourier and Chebyshev series inversion giving poly(log(1/epsilon)) precision for sparse linear systems |
| [1810.12030.md](notes/papers/1810.12030.md) | van Apeldoorn and Gribling 2018: Omega(n) quantum query lower bound for Simon's problem restricted to linear functions over F_p |
| [2102.11349.md](notes/papers/2102.11349.md) | Childs, Hung and Li 2021: Omega(n) quantum query bounds for trace, determinant, rank testing and linear systems with matrix-vector product access |
| [2404.15407.md](notes/papers/2404.15407.md) | Hayakawa, Chen and Hsieh 2026: oriented-simplex quantum walk encoding the combinatorial Laplacian and a projector onto harmonic homology |
| [2412.12762.md](notes/papers/2412.12762.md) | Daskin 2025: eigenvalue perturbation of linear combinations of permutations under bit-flip and phase-flip errors |
| [2506.01432.md](notes/papers/2506.01432.md) | Nghiem 2026: block-encoded Laplacians, Betti number estimation and homology tracking and testing for quantum topological data analysis |
| [2508.21667.md](notes/papers/2508.21667.md) | Setty 2026: coherent-permutation index mapping for sparse block encodings and IBM-backend circuit-depth analysis |
| [2603.16492.md](notes/papers/2603.16492.md) | Li, Zhang and Zhang 2026: (11/12) 2^n C-NOT state preparation and a single-ancilla block encoding with alpha equal to the spectral norm |
| [2605.27430.md](notes/papers/2605.27430.md) | Daskin 2026: phased Birkhoff-von Neumann decomposition cutting LCU terms from O(N^2) to O(N log(N/epsilon)) with alpha equal to 1 |
| [2609.12777.md](notes/papers/2609.12777.md) | Strelchuk, Subramanian and Wesolowski 2026: planted-clique reduction giving average-case hardness of additive Betti number estimation |
| [2609.28058.md](notes/papers/2609.28058.md) | Nghiem, Babbush, Zalcman, Berry, Phan, Wei and Hayakawa 2026: Mayer homology (d^N = 0) Betti number estimation and a resource estimate of sixty million Toffoli gates |
| [2609.28112.md](notes/papers/2609.28112.md) | Nghiem, Berry and Phan 2026: NP-hardness of p-torsion in clique-complex homology and a one-sided quantum torsion witness |
| [2610.03686.md](notes/papers/2610.03686.md) | Summer and Jamet 2026: permute-act-unpermute block encoding with 8 S N T gates, separating the support address from the operator label |
| [2611.03348.md](notes/papers/2611.03348.md) | Rua Munoz, Mahecha Gomez and Pineda Montoya 2025: quaternionic quantum computation is polynomially equivalent to the complex model; octonionic obstructions and mitigations |
| [1005.5663.md](notes/papers/1005.5663.md) | Idrees, Pfister and Steidel 2011 modular standard bases: Theorem 2.4 (lifting a candidate basis from one prime, stated without a homogeneity hypothesis) with a counterexample to the statement as printed, lucky primes and the modStd algorithm (pp. 1-9 read) |
| [1207.1651.md](notes/papers/1207.1651.md) | Boehm, Decker, Fieker and Pfister 2015 bad primes in rational reconstruction: five types of bad primes, error tolerant lifting and the type-5 prime of Example 5.12 (all pages read) |
| [1504.04564.md](notes/papers/1504.04564.md) | Boku, Decker, Fieker and Steenpass 2015 Groebner bases over number fields: Theorem 5.1, admissible and lucky primes, Algorithms 2 and 3 of nfmodstd.lib and the verification only for homogeneous ideals or local orderings (all pages read) |
| [arnold-2003-modular-groebner.md](notes/papers/arnold-2003-modular-groebner.md) | Arnold 2003 modular Groebner bases: Hilbert lucky primes, Theorem 5.3 (HF_I <= HF_(I_p)) and the verification criterion of Theorem 7.1 for homogeneous ideals (pp. 403-410 and 415-419 read) |
| [1111.7263.md](notes/papers/1111.7263.md) | Bruns, Conca and Varbaro 2013 relations between minors of a generic matrix: quadrics f_(u,v), cubics in Theorems 2.4 and 2.7, Conjecture 2.12 and Theorem 3.1 (pp. 1-28 read) |
| [1909.11705.md](notes/papers/1909.11705.md) | Huang, Perlman, Polini, Raicu and Sammartano 2021 the case t = 2 of the Bruns-Conca-Varbaro conjecture: Theorems 1.1 and 1.2 and the fiber-type question of Section 7 (pp. 1-4 and 18-20 read) |
| [1303.6874.md](notes/papers/1303.6874.md) | De Negri and Gorla 2011 invariants of pfaffian ideals of ladders: multiplicity formulas, regularity and the resolution of the maximal pfaffian ideal M_t (all pages read) |
| [bruns-simis-trung-1991-straightening-closed.md](notes/papers/bruns-simis-trung-1991-straightening-closed.md) | Bruns, Simis and Trung 1991 straightening-closed ideals: Hodge algebra structure of the Rees algebra, Theorem 2.2.2 and Theorems 3.1.1 to 3.2.1 (pp. 507-518 read) |
| [math-0303268.md](notes/papers/math-0303268.md) | Ein, Lazarsfeld and Mustata 2004 contact loci in arc spaces: Theorems A and C relating arc loci to log resolutions and divisorial valuations (pp. 1-5 read) |
| [math-9810140.md](notes/papers/math-9810140.md) | Landsberg and Manivel 2003 projective geometry of rational homogeneous varieties: adjoint varieties in Proposition 4.17 and Remark 4.18 and the lead on the degree-20 W8 fiber component (all pages read) |
| [0803.2369.md](notes/papers/0803.2369.md) | Lejeune-Jalabert and Teissier 2008 integral closure of ideals: Theorem 2.1 (arcs, normalized blow-up), Theorem 4.1.6 and the arc formula of Theorem 5.2 (pp. 1-48 of 78 read, in French) |
| [mumford-1999-red-book-varieties-schemes.md](notes/papers/mumford-1999-red-book-varieties-schemes.md) | Mumford 1999 Red Book of Varieties and Schemes, second edition: Section I.10 on complex varieties, the strong topology, Theorem 1 (density of a nonempty open subvariety) and Corollary 1 (Zariski closure equals strong closure for a constructible set) with the definitions of variety and constructible set (printed pp. 1, 16-18, 20-27, 33-34, 36-39, 50-54, 57-63 and 65-66 read) |
| [huneke-swanson-2006-integral-closure-ideals-rings-modules.md](notes/papers/huneke-swanson-2006-integral-closure-ideals-rings-modules.md) | Huneke and Swanson 2006 Integral Closure of Ideals, Rings, and Modules (LMS Lecture Note Series 336): the Rees algebra, fiber cone and analytic spread (Definition 5.1.5, Proposition 5.1.6), the kernel of T_i -> x_i t and its linear part (Section 5.5, p. 110), the blowup as Proj of the Rees algebra (Definition 5.6.2), reductions and analytic spread (Theorem 8.2.1, Corollary 8.2.5, Proposition 8.3.7, Corollary 8.3.9) and Rees valuations (Theorems 10.1.6 and 10.2.2); no statement of the fiber of the blowup over a point or of the blowup as a graph closure on the pages read (PDF pages 1-14 and printed pp. 99-102, 110-118, 157-166, 195-203 and 439-449 read) |
| [vasconcelos-1994-arithmetic-blowup-algebras.md](notes/papers/vasconcelos-1994-arithmetic-blowup-algebras.md) | Vasconcelos 1994 Arithmetic of Blowup Algebras (LMS Lecture Note Series 195): the special fiber F(I) and analytic spread (Definition 5.1.2, p. 100), the presentation of the Rees algebra and the sequence 0 -> A -> S(I) -> R(I) -> 0 (Chapter 8, pp. 195-196), the Rees ideal by elimination (Propositions 10.2.11 and 10.2.12), saturation and the regularity criterion (Propositions 10.2.3 and 10.2.5) and homogenization (p. 264) (PDF pages 1-10 and printed pp. 1-6, 99-101, 130-137, 195-198, 253-266 and 327-329 read) |
| [greuel-pfister-2008-singular-introduction-commutative-algebra.md](notes/papers/greuel-pfister-2008-singular-introduction-commutative-algebra.md) | Greuel and Pfister 2008 A Singular Introduction to Commutative Algebra, second edition: ideal membership, elimination (Lemma 1.8.3), radical membership, intersection, quotient (Lemma 1.8.12), saturation (Section 1.8.9, Lemma 1.8.14, Example 1.8.15), the kernel of a ring map by elimination (Lemma 1.8.16) and Theorem 7.5.1 with Proposition 7.5.3 on weighted homogenization and flatness of standard bases (PDF pages 1-18 and printed pp. 67-71, 77-86 and 404-411 read) |
| [baetica-1998-rees-algebra-pfaffians.md](notes/papers/baetica-1998-rees-algebra-pfaffians.md) | Baetica 1998 Rees algebra of ideals generated by pfaffians: for the ideal of 2t-pfaffians of a generic alternating matrix, normality of the Rees algebra, its Cohen-Macaulay property outside the exceptional characteristic (Theorem 3.4), the special fiber as the subalgebra generated by the pfaffians (proof of Lemma 1.4, Corollary 3.7) and the divisor class group for 2t <= n - 2 (Corollary 1.7); no statement on specializations (PDF pages 1-11 read in full, printed pp. 1769-1778) |
| [jozefiak-pragacz-1979-ideals-generated-pfaffians.md](notes/papers/jozefiak-pragacz-1979-ideals-generated-pfaffians.md) | Jozefiak and Pragacz 1979 ideals generated by Pfaffians: the height and depth bound mu(p, n) over any commutative Noetherian ring (Theorem 2.1, Corollary 2.2), equality for generic matrices (Theorem 2.3, Corollary 2.5), the reduction of a Pfaffian ideal at a unit entry (Lemma 1.2) and the free resolution of the ideal of (n-2)-Pfaffians with 2 invertible (Theorem 3.2, Corollary 3.8 for G(2, 6)) (PDF pages 1-10 read in full, printed pp. 189-198) |
| [eisenbud-harris-2000-geometry-of-schemes.md](notes/papers/eisenbud-harris-2000-geometry-of-schemes.md) | Eisenbud and Harris 2000 The Geometry of Schemes: the blow-up by its universal property (Definition IV-16), the blow-up of an affine scheme as the closure of the graph of the map to projective space given by generators of the ideal (Example IV-17, Propositions IV-18 and IV-22), strict transforms and base change (Proposition IV-21), the blow-up as Proj of the Rees algebra (Theorem IV-23) and the Rees algebra of a regular sequence (Proposition IV-25); no description of the fiber over a point of the center beyond an exercise (PDF pages 1-10 and printed pp. 162-176 read) |
| [hartshorne-1977-algebraic-geometry.md](notes/papers/hartshorne-1977-algebraic-geometry.md) | Hartshorne 1977 Algebraic Geometry, Section II.7: the blowing-up of a noetherian scheme along a coherent ideal sheaf as Proj of the sum of its powers, the invertible inverse image ideal sheaf (Proposition 7.13), the universal property with the equations of the blowing-up of an affine scheme (Proposition 7.14), strict transforms (Corollary 7.15), the blowing-up of a variety (Proposition 7.16) and birational projective morphisms as blowings-up (Theorem 7.17); no graph-closure sentence and no description of the fiber over the center (PDF pages 1-6 and printed pp. 162-171 read) |
| [fulton-1998-intersection-theory.md](notes/papers/fulton-1998-intersection-theory.md) | Fulton 1998 Intersection Theory, second edition, Appendix B: cones and projective cones of graded algebras with their pull-back (B.5.1), the normal cone (B.6.1), the blow-up as Proj of the sum of the powers of the ideal with exceptional divisor the projective normal cone (B.6.3), integrality, birationality, pure dimension and flatness of blow-ups (B.6.4 to B.6.7) and the blow-up of a pulled-back center inside the fiber product (B.6.9); the fiber over a point as Proj of the fiber cone is an inference of the note (PDF pages 1-6 and printed pp. 432-437 read) |
| [kleppe-laksov-1980-pfaffian-schemes.md](notes/papers/kleppe-laksov-1980-pfaffian-schemes.md) | Kleppe and Laksov 1980 pfaffian schemes: primes, height and perfection of the ideals of pfaffians of a generic alternating matrix and of its sub-blocks (Sections 2 to 4), generic pfaffian schemes and their deformations (Section 5), the Hilbert function and the Gorenstein property (Section 6) and factoriality (Section 7); three printed statements are recorded with the note's reading of them (PDF pages 1-23 read in full, printed pp. 167-189) |
| [buchsbaum-eisenbud-1977-finite-free-resolutions-codimension-3.md](notes/papers/buchsbaum-eisenbud-1977-finite-free-resolutions-codimension-3.md) | Buchsbaum and Eisenbud 1977: algebra structures on finite free resolutions (Section 1), the structure theorem for Gorenstein ideals of grade 3 as ideals of maximal-order pfaffians of an alternating matrix (Sections 2 and 3), the multiplication on the minimal resolution (Section 4), linkage and almost complete intersections (Section 5); the 4-pfaffians of a 9 x 9 matrix are outside the theorem (PDF pages 1-40 read in full, printed pp. 447-485) |
| [hartshorne-1962-complete-intersections-connectedness.md](notes/papers/hartshorne-1962-complete-intersections-connectedness.md) | Hartshorne 1962 complete intersections and connectedness: connectedness in codimension k (Section 1), depth and connectedness (Section 2) and the application to complete intersections with its examples (Section 3) (PDF pages 1-13 read in full, printed pp. 497-508) |
| [northcott-rees-1954-reductions-ideals-local-rings.md](notes/papers/northcott-rees-1954-reductions-ideals-local-rings.md) | Northcott and Rees 1954 reductions of ideals in local rings: reductions and minimal reductions (Sections 1 and 2), the analytic spread as the dimension of the fiber ring (Section 3), minimal reductions and analytic independence over an infinite residue field (Section 4), and the bound of the spread by the dimension for ideals primary to the maximal ideal (Section 6) (PDF pages 1-15 read in full, printed pp. 145-158) |
| [swanson-2011-rees-valuations.md](notes/papers/swanson-2011-rees-valuations.md) | Swanson 2011 Rees valuations: definition, existence, uniqueness and constructions of the Rees valuations of an ideal (Sections 1 and 2), one-fibered ideals (Section 3), bounds on the number of Rees valuations (Section 4), the Izumi-Rees theorem (Section 5) and adjoints (Section 6); the held file is the author's typescript with its own pagination (PDF pages 1-23 read in full) |
| [pfister-2007-modular-computation-standard-basis.md](notes/papers/pfister-2007-modular-computation-standard-basis.md) | Pfister 2007 modular computation of standard bases: the Hilbert-function criteria for lucky primes and for equality of ideals (Proposition 2.2, Corollary 2.3), homogeneous for a global ordering and through the Hilbert-Samuel function for a local one, the remark that the final test otherwise proves an inclusion only (Remark 2.8), and the algorithm `modstd` (PDF pages 1-10 read in full, printed pp. 129-138) |
| [kaji-ohno-yasukura-1999-adjoint-varieties-secant-varieties.md](notes/papers/kaji-ohno-yasukura-1999-adjoint-varieties-secant-varieties.md) | Kaji, Ohno and Yasukura 1999 adjoint varieties: the graded decomposition of a simple Lie algebra and the adjoint variety (Sections 1 and 2), its quadric equations (Section 3), the secant variety and its dimension by type (Section 5) and contact loci (Section 6); no degree, Hilbert function or positive-characteristic statement (PDF pages 1-13 read in full, printed pp. 45-57) |
| [bruns-herzog-1998-cohen-macaulay-rings.md](notes/papers/bruns-herzog-1998-cohen-macaulay-rings.md) | Bruns and Herzog 1998 Cohen-Macaulay Rings: Hilbert functions and Hilbert series over homogeneous rings (Section 4.1), Macaulay's theorem on Hilbert functions (Section 4.2), Rees rings and associated graded rings (Section 4.5) and the Hilbert-Samuel function, reduction ideals and the analytic spread (Section 4.6) (PDF pages 1-14 and printed pp. 147-166 and 182-191 read) |
| [fulton-harris-2004-representation-theory.md](notes/papers/fulton-harris-2004-representation-theory.md) | Fulton and Harris 2004 Representation Theory: the construction of the Lie algebra g_2 and its representations (Lecture 22, Sections 22.1 to 22.3), the octonions and the algebraic constructions of g_2 (Section 22.4), and homogeneous spaces and closed orbits with the G_2 examples (Section 23.3) (PDF pages 1-17 and printed pp. 339-365 and 382-394 read) |
| [kato-1995-perturbation-theory-linear-operators.md](notes/papers/kato-1995-perturbation-theory-linear-operators.md) | Kato 1995 Perturbation Theory for Linear Operators: the eigenvalue problem, resolvent and eigenprojections in finite dimension (Chapter One, Section 5), analytic perturbation of eigenvalues with the Puiseux expansions and the holomorphic total projection (Chapter Two, Section 1) and the opening of the perturbation series (Section 2); no statement on a limit of the kernel (PDF pages 1-18 and printed pp. 34-43 and 62-78 read) |

### Algebra and proofs

| File | Contents |
|---|---|
| [topics/a5-exceptional-fiber-findings.md](notes/topics/a5-exceptional-fiber-findings.md) | A_5 exceptional fibers of the nullity-8 closures along their boundary orbits: Hilbert functions by degree-by-degree membership rank, quadric-scheme structure, formal-arc support certificate, retired elimination routes, and the hypotheses that survive falsification |
| [topics/a5-methods-and-sources.md](notes/topics/a5-methods-and-sources.md) | Methods of the A_5 fiber-cone program mapped to the registered source and numbered statement that justifies each: fiber cone and analytic spread, equations of the Rees algebra and of the blow-up, limits along arcs and closures, standard bases over Q(i) and modulo primes, Pfaffian ideals, homogeneous varieties; with the gap where the printed statement is narrower than the use |
| [topics/cd-annihilator-varieties-prior-art.md](notes/topics/cd-annihilator-varieties-prior-art.md) | Prior-art search of 2026-11-13 on annihilator varieties and zero-divisor strata of the 16- and 32-dimensional Cayley-Dickson algebras: the published identifications are topological (V_2(R^7), G_2, the top stratum of A_5), no work found identifies a variety of limiting annihilators or computes a fiber cone of a stratum; hits by class and the full query log |
| [topics/a5-exceptional-fiber-status.md](notes/topics/a5-exceptional-fiber-status.md) | The A_5 fiber program's goal (the attaching data of `dimension32-global-topology`), the status of its four layers by ledger count, what the latest results change and the next computation per layer |
| [topics/quantum-linear-algebra-fit-a5.md](notes/topics/quantum-linear-algebra-fit-a5.md) | quantum access-model and output contracts against the current A5 fiber workload; known counterexamples to blanket impossibility, finite-ring ideal boundaries, exact LCU/filter constructions and the 140-dimensional E8 degree-six target |
| [topics/a5-hardware-algebra-synthesis.md](notes/topics/a5-hardware-algebra-synthesis.md) | the A_5 nullity strata as measured by the quantum hardware (point readings, operand orbits, arc-probe lines, contact orders, instrument findings) and by the exceptional-fiber program (the t-space slice ladder), with conflicts, resolutions and roadmap |
| [topics/finite-field-qlsa-alternatives.md](notes/topics/finite-field-qlsa-alternatives.md) | a finite-field quantum linear-system proposal for the fiber program, refuted claim by claim (isotropic vectors for kernels, non-unitary oracle, register size, misattributed citations) |
| [topics/box-kites/README.md](notes/topics/box-kites/README.md) | box-kite experiment program index |
| [topics/a5-terms-for-outside-readers.md](notes/topics/a5-terms-for-outside-readers.md) | draft: A_5 as the 32-dimensional Cayley-Dickson algebra and nullity as dim ker L_x, against the group-theory and graph-theory readings of the same words |
| [topics/strata-gauss-bottleneck.md](notes/topics/strata-gauss-bottleneck.md) | draft: the objects of a Gauss-map classification of the kernel bundle at the stratum V into Gr(4, 6), with unverified formulas marked |
| [bdsc-pauli-readout.md](notes/topics/bdsc-pauli-readout.md) | BDSC target and blade effects as three-term four-qubit Pauli sums; local readout and 13-basis cover |
| [algebra-hardware-probe-principles.md](notes/topics/algebra-hardware-probe-principles.md) | first principles of algebra hardware probes: mutation test, eigen-observable, interleaving, null arm, noisy coherent response; findings ledger of the Garnet runs |
| [primorial-cover-defects.md](notes/topics/primorial-cover-defects.md) | missing primorial-wheel gaps 20, 32, 86, 88 as restricted covers: exhaustive defect certificates, capacity and LP bounds, singleton repair, slice Walsh Hamiltonians, the eight-CNOT parity network and the reproduction of Ziller Table 1 for `k <= 20`, and the ungated `k = 24` gap-234 and gap-236 cover decisions |
| [c5-zero-divisor-code-falsification.md](notes/topics/c5-zero-divisor-code-falsification.md) | zero-divisor code, falsified thought experiment |
| [cd-star-lattice-tower.md](notes/topics/cd-star-lattice-tower.md) | Tuna-17 as the Gaussian-integer star lattice; lifts to dimensions 3, 4, 8, 16, the Paley identification of their symmetry groups and the sedenion zero divisors |
| [cd_associator_defect_census.md](notes/topics/cd_associator_defect_census.md) | ordered basis triples whose two bracketings differ, per Cayley-Dickson level (168, 1848, 15960, 130200 non-associating at D = 8 to 64; the same count under every triple rule because repeated indices and e0 always associate), from `cd_core.cd_sign`; the basis sign is a 2-cochain whose coboundary is this associator phase, a 2-cocycle only through D = 4 ([cd-tower verification](archive/reviews/cd-tower/pasted-analyses-verification.md)); record [census.json](evidence/cd_associator_defect_census/census.json) |
| [cd-one-sided-inverses.md](notes/topics/cd-one-sided-inverses.md) | every Cayley-Dickson algebra has ker L_a = ker R_a, so a b = 1 forces b a = 1 and each zero divisor carries an affine family of two-sided inverses; the trace-form identities behind it and the exhaustive sedenion and dimension-32 checks |
| [evidence/cd-one-sided-inverses/README.md](evidence/cd-one-sided-inverses/README.md) | exact replay of the annihilator equality and two-sided inverse law on every signed two-blade, three-unit sum and doubly pure grid element at dimensions 16 and 32, with the basis identities through dimension 128 |
| [evidence/cd-annihilator-symmetry/README.md](evidence/cd-annihilator-symmetry/README.md) | Rocq proof, for every Cayley-Dickson dimension, that a z = 0 exactly when z a = 0 on the integer pair tower (Corollary 9.3 of math/0511691 through the purity of annihilators), with the norm and adjoint identities, direct finiteness and the integer-cleared right-inverse family, and its kernel receipts |
| [evidence/cd-annihilator-symmetry-real/README.md](evidence/cd-annihilator-symmetry-real/README.md) | Rocq proof of the same kernel equality on the real pair tower of `CdTowerReal.v`, through Lemma 9.2 of math/0511691 and its identity x (conj(x) y) = conj(x) (x y), with Lemmas 2.6 and 2.8 on real parts, Corollary 2.9 (the flexible law (x y) x = x (y x)), the purity lemmas, Lemma 9.5 (zero divisors and annihilators are orthogonal to span(1, i_n)), direct finiteness and the affine right-inverse family conj(a)/<a, a> + ker L_a, and its kernel receipts |
| [evidence/cd-tower-domain/README.md](evidence/cd-tower-domain/README.md) | Rocq functor `CdTowerDomain.v` stating the pair tower once over an abstract ordered integral domain and proving the annihilator theorems (Lemmas 3.4, 3.6, 2.6, 2.8, 9.2, 9.4, 9.5, Corollaries 2.9 and 9.3, direct finiteness) on it, instantiated at Z and R with bridges to the integer and real tower files and a field extension for the affine inverse family, and its kernel receipts |
| [evidence/cd-half-fold/README.md](evidence/cd-half-fold/README.md) | Rocq proof of the half-operand fold of the Cayley-Dickson kernel, on the ordered-domain functor and the real tower: (a, 0)(c, d) = 0 exactly when a c = 0 and a d = 0, and (0, b)(c, d) = 0 exactly when b c = 0 and b d = 0, so the nullity of a half operand doubles from the level below, with the basis-count form of the doubling (`RealHalfFoldDimension`); the cross-operand fold stays an open target, and its kernel receipts |
| [evidence/cd-twisted-product/README.md](evidence/cd-twisted-product/README.md) | Rocq proof, over a commutative ring with i i = -1 and 1/2, that the W8 equations of A_5 are the real and imaginary parts of the sedenion zero-divisor equations of z = x + i x', with f(z) = Re f + i Im f, f(z') = Re f - i Im f, Re f = (f(z) + f(z'))/2 and Im f = (f(z) - f(z'))/(2 i) as polynomial identities and the ideal exchange for every ideal; the product of varieties, the dimension and the degree stay computed evidence (ledger row A5-223); its kernel receipts |
| [evidence/cd-tower-ring/README.md](evidence/cd-tower-ring/README.md) | Rocq functor `CdTowerRing.v` stating the pair tower over a commutative ring with no order: conjugation maps ker L_a onto ker R_(conj a), so ker R_a = conj(ker L_a) for pure a; the map (a, b) -> (a, -b) is an involutive automorphism at every level; and over a ring with a square root of -1 the swap a z = 0 -> z a = 0 of Corollary 9.3 holds at a level of at least 2 exactly when 2 = 0, with the witness a = e_1 + i e_2, w = a e_1 in the Gaussian integers and in Zmod 5; `CdTowerRingDomain.v` identifies the tower with the ordered-domain functor's at Z and R; its kernel receipts and the cd_core test of the witness |
| [evidence/cd-tower-ring-base-change/README.md](evidence/cd-tower-ring-base-change/README.md) | Rocq files `CdTowerRingBasis.v` (a linear or bilinear identity on the commutative-ring tower follows from its values on basis vectors), `CdTowerRingBaseChange.v` (a ring homomorphism carried through every level, so a check computed on the basis over Z or Z[sqrt 3] holds for all elements over every ring that receives it, for derivations and for product-preserving maps) and `CdTowerOrderThreeMap.v` (the order-three map psi of Gresnigt's Eq. 61 preserves products at level 4 over every commutative ring with a square root of 3 and an inverse of 2, and its diagonal extension preserves the product of level 5); bijectivity and the order of psi stay computed; its kernel receipts, the Rocq-printed image table and the cd_core test bound to it |
| [evidence/cd-tower-kernel-certificates/README.md](evidence/cd-tower-kernel-certificates/README.md) | Rocq files `CdTowerKernelCertificate.v` (three finite checks over a source ring, annihilated vectors, a splitting d z = back(y z) + sum f_j(z) v_j on the basis and dual functionals, give the kernel of z -> y z over every commutative ring that receives it, free on the vectors where d is invertible, and the vectors independent where d is a nonzero divisor) and `CdTowerCanonicalKernels.v` (the certificates over Z at one integer point of each of the twelve A_5 orbits of nullity 8, 12 and 16, with d = 2 at eleven points and 50 at the point of V); constancy of the nullity on an orbit and the list of orbits stay computed; its integer certificate data, generator and check against cd_core, kernel receipts and test |
| [formalization.yaml](../formalization.yaml) | index of the twenty-nine Rocq proof sources in the mathlib-initiative `formalization.yaml` schema: the note or paper each formalizes and selected main-result declarations with their files and Print Assumptions lists |
| [evidence/formalization-yaml-schema/README.md](evidence/formalization-yaml-schema/README.md) | retained bytes of the mathlib-initiative v0.4 schema with its checksum and the validation command for `formalization.yaml` |
| [kaplansky-mechanisms-cayley-dickson.md](notes/topics/kaplansky-mechanisms-cayley-dickson.md) | Kaplansky's zero-divisor, direct-finiteness and idempotent conjectures against the Cayley-Dickson twisted group algebras: zero products as an F_2 XOR skeleton times the gauge-invariant cocycle cross-ratio chi, the Fano plane in openai/math families 196 and 197, the GHZ qubit reading of the zero divisors |
| [evidence/cd-star-lattice/README.md](evidence/cd-star-lattice/README.md) | exact star-lattice census bound to the Tuna-17 catalogue topology, with SL(2, q) and PGL(2, 7) certificates and a nauty replay |
| [evidence/seekpath-lattice-crosscheck/README.md](evidence/seekpath-lattice-crosscheck/README.md) | spglib and SeeK-path replay: the D14 coordinate projection spans Z^3 (Pm-3m), the S_3 and S_2 point groups match the star-lattice census, cubic Brillouin-zone shapes |
| [evidence/albuquerque-majid-convention/README.md](evidence/albuquerque-majid-convention/README.md) | replay of the Albuquerque-Majid cochain recursion against cd_sign: transposed map exact on 5,460 pairs, untransposed control fails, associators agree on 37,448 triples |
| [evidence/kaplansky-cd-mechanisms/README.md](evidence/kaplansky-cd-mechanisms/README.md) | exact replay of the Kaplansky mechanisms note: chi predicts every two-blade zero product at D = 8, 16, 32 (0, 336, 5040), none off the XOR skeleton, Fano complements as subgroup cosets, pure two-sided annihilators, zero Bloch vectors on the support of i xor j |
| [evidence/cd-imaginary-sum-conference/README.md](evidence/cd-imaginary-sum-conference/README.md) | Rocq proof, for every Cayley-Dickson dimension, that right multiplication by the imaginary sum is a skew conference matrix, with its kernel receipts and the bridge to cd_sign |
| [evidence/sedenion-automorphisms/README.md](evidence/sedenion-automorphisms/README.md) | Exact computation of `Aut(O) = G2` and `Aut(S) = G2 x S3` for `cd_core` (derivations, commutant, Groebner roots) deciding Wilmot's two `Aut(S)` statements, the Rocq tower's evaluated sedenion table, and the 11 corrected Gresnigt Table 5 cells with the erratum report |
| [evidence/demarrais-8192d-cross-platform/README.md](evidence/demarrais-8192d-cross-platform/README.md) | The DeMarrais-labelled Tuna-17 and QX campaign, replayed as CZ-graph Pauli propagation: every circuit's outcome is the CZ-neighbour parity of its X'd hubs, the Cayley-Dickson labels set no gate, and the runs measure Tuna-17's Clifford-circuit fidelity |
| [evidence/cd-tower-basis-sign/README.md](evidence/cd-tower-basis-sign/README.md) | Rocq proof, for every Cayley-Dickson dimension, that the tower's basis products are e_a e_b = sigma_k(a, b) e_(a XOR b) with sigma_k the cd_sign loop, the arc-matrix entries, and the Albuquerque-Majid Corollary 4.3 sign, with its kernel receipts |
| [evidence/cd-sign-row-anf/README.md](evidence/cd-sign-row-anf/README.md) | Rocq proof, for every Cayley-Dickson dimension, of the ANF of the sign rows: Moebius inversion and uniqueness, the leading layer and exact degree of the left rows, and the exact degree of the right rows, with its kernel receipts |
| [evidence/cd-associator-anf/README.md](evidence/cd-associator-anf/README.md) | Rocq proof, for every Cayley-Dickson dimension, of the exact ANF degree of the associator phases (Theorem 2 of the degree note), tied to the cd_sign factors of `predict.associator_phase` and to the tower product, with its kernel receipts |
| [evidence/cd-sign-python-semantics/README.md](evidence/cd-sign-python-semantics/README.md) | Rocq proof, for every Cayley-Dickson dimension, that the syntax tree of `cd_core.cd_sign`, run under a semantics of the Python int subset it uses, returns the tower sign sigma and raises on invalid int arguments, with the extractor contract and kernel receipts |
| [evidence/cd-sign-python-translation/README.md](evidence/cd-sign-python-translation/README.md) | Certified raw-AST translation, an independent source interpreter and all-integer execution preservation for cd_sign, with explicit parsing and helper trust boundaries |
| [evidence/cd-associator-point-indicators/README.md](evidence/cd-associator-point-indicators/README.md) | All-dimension Rocq proof of Proposition 5's point-indicator phase formula and exact degree, with kernel receipts |
| [evidence/cd-associator-census/README.md](evidence/cd-associator-census/README.md) | Rocq proof, for every Cayley-Dickson dimension, of the census of unordered basis pairs by associator-phase ANF degree (21, then 3 2^d (2^(d+1) - 1) at degree d), with its kernel receipts |
| [evidence/a5-stiefel-pfaffian-germs/README.md](evidence/a5-stiefel-pfaffian-germs/README.md) | exact Pfaffian factorization Pf A = -(z.t) Q G proving every A_5 Stiefel element a zero divisor, and the tangent-bound germs at the twelve non-zero-divisor gap witnesses |
| [evidence/stiefel-pfaffian-higher/README.md](evidence/stiefel-pfaffian-higher/README.md) | exact Pfaffian transport and cofactor polynomial f_n for doubly pure elements of A_6 to A_8, the irreducibility of f_n, the failure of Pf A = 0 on the Stiefel set above A_5, Stiefel witnesses at A_7 and A_8, and the zero-divisor Stiefel locus |
| [evidence/a5-zero-divisor-strata/README.md](evidence/a5-zero-divisor-strata/README.md) | exact rank strata of the A_5 zero-divisor set: V(Q) u V(G), nullity = 28 - 2 rank C_z, two irreducible pieces per stratum, closure incidences and connected components, with an independent cd_core verification ([verification.md](evidence/a5-zero-divisor-strata/verification.md)); explicit equations and an independent covering in [a5-rank-strata-equations](evidence/a5-rank-strata-equations/README.md) |
| [evidence/a5-rank-strata-equations/README.md](evidence/a5-rank-strata-equations/README.md) | explicit equations for every A_5 rank stratum (R_8 = W8 u Ehat with Ehat = E8-bar = {Q = 0, Delta = 0, rank [u; v; u ^ v] <= 2}, irreducible of dimension 11 and degree 24), the covering re-derived over Q with Singular and independent G_2 orbit facts, and ideal-membership certificates for every piece |
| [evidence/a5-exceptional-fibers/README.md](evidence/a5-exceptional-fibers/README.md) | retained working record of the A_5 exceptional-fiber computations on the nullity-8 closures: run inputs and logs, relations and receipts, Kaggle and cloud outputs, consultant briefs and answers, scrubbed, with files above 50 MB split into 45 MB parts |
| [evidence/a5-exceptional-fibers/memory-bounded/README.md](evidence/a5-exceptional-fibers/memory-bounded/README.md) | memory-bounded A_5 fiber-rank route: retained engine v14 W8 N = 16 acceptance with its launch manifest, raw records and reproduction command; engine v15 conservative three-copy product-row admission and the conditional selected-array model of the W8 degree-6, N = 19 route |
| [evidence/pathion-kernel-map/README.md](evidence/pathion-kernel-map/README.md) | the A_5 kernel map on hardware: nullity as the aligned XOR-pair count, the coset decomposition, package agreement with cd_core (`packages.json`), and the IBM, Tuna-17 and Ascella program with the IBM written case |
| [evidence/pathion-kernel-map/evidence_pivots.md](evidence/pathion-kernel-map/evidence_pivots.md) | every measured pathion reading on IBM, Quantum Inspire and Quandela in one long table (`evidence_table.csv`, built by `scripts/pathion_evidence_table_build.py`), with pivots by backend and observable, across platforms, sim against QPU, and per claim-ledger row |
| [evidence/pathion-kernel-map/nhat-bias/README.md](evidence/pathion-kernel-map/nhat-bias/README.md) | audit of the kernel-map nullity estimator N_hat: the exact bias identity N_hat - N = \|B+\|\|B-\|/\|B\| (Vbar+ - Vbar-)/V_hat, the all-aligned blocks that read 4 on any hardware, the block-profile census against the H-orbits, and the same readings on the parallel coset and 64- and 128-dimensional runs (`result.json`, `result_wide.json`, `nhat_bias.py`, ledger rows A5-228 to A5-234) |
| [evidence/hhl-qsvt-falsify/README.md](evidence/hhl-qsvt-falsify/README.md) | retained Pauli-encoding measurements and corrected scope: natural signed-permutation LCU, singular kernel filters, modular-output mismatch and state-preparation costs |
| [evidence/a5-strata-regularity/README.md](evidence/a5-strata-regularity/README.md) | orbit stratification of the A_5 rank strata under G_2(C) x SO(2, C) x C^* (R_8 minus 0 is twelve orbits), the singular locus of every closure and of V(Q), V(G), a Whitney stratification, transverse germs and the normal link S^1 disjoint union S^3 of R_12 at x0, with an independent cd_core verification ([verification.md](evidence/a5-strata-regularity/verification.md)) |
| [evidence/a5-w8-a4-restriction/README.md](evidence/a5-w8-a4-restriction/README.md) | the A_5 W8 closure ideal restricted to the embedded A_4 coordinates (J = (y_0, y_8, U - V, W), prime of dimension 12 and degree 4) against the A_4 nullity >= 4 Pfaffian ideals over F_32009: equal radical, degree and multiplicity for the realified order-6 Pfaffians of the doubly pure encoding, which carry embedded components and a different Hilbert series, and larger complex loci for the real 16 x 16 and Im-block Pfaffians |
| [evidence/a5-w8-twisted-product/README.md](evidence/a5-w8-twisted-product/README.md) | the A_5 W8 closure ideal as the twisted product J(z) + J(z') of two sedenion zero-divisor ideals over F_32009 (dimension 24, degree 16, Hilbert numerator N_J^2, real slice J), the nullity-fold spectrum on the 512 mixed basis pairs (the sum rule n_32 = n_16(z) + n_16(z') fails on 480, the mixed law n_32 = 12 - 2 n_16(e_i + s e_j) holds on 420) and 800 seeded random points |
| [evidence/a5-kernel-bundles/README.md](evidence/a5-kernel-bundles/README.md) | kernel bundles of the A_5 strata of nullity at least 12 (roadmap item 5): kernel symmetry algebra, compact-orbit moduli, stabilizer representations, exact transition cocycle and equivalence classes, with an independent cd_core verification ([verification.md](evidence/a5-kernel-bundles/verification.md)) |
| [evidence/a5-kernel-bundles-nullity8/README.md](evidence/a5-kernel-bundles-nullity8/README.md) | kernel bundles of the A_5 nullity-8 strata: compact-orbit moduli, stabilizer strata, path-dependent boundary limits into nullity 12, unit-section cores, U(4) transition data and classes (the order-two class on E8-bar and X_+-), with an independent cd_core verification ([verification.md](evidence/a5-kernel-bundles-nullity8/verification.md)) |
| [design/a5-kernel-bundles-nullity8-program.md](design/a5-kernel-bundles-nullity8-program.md) | program goal for the kernel bundles of the A_5 nullity-8 strata (W8, E8-bar, Iso, X_+-): established inputs from the nullity >= 12 record, gaps, deliverables, behavior rules, and the [ledger](evidence/a5-kernel-bundles-nullity8/ledger.md) the program keeps |
| [design/a5-kernel-attachments-program.md](design/a5-kernel-attachments-program.md) | program goal for roadmap item 6 of the A_5 topology: how partner spheres specialize across the 33 closure incidences 8 -> 12, 12 -> 16 and 8 -> 16 (closed kernel Gauss-graph fibers, two-sided real certificates, attaching maps), with the [ledger](evidence/a5-kernel-attachments/ledger.md) the program keeps |
| [design/a5-open-tasks-and-compute-scope.md](design/a5-open-tasks-and-compute-scope.md) | open tasks of roadmap item 6 by blocker, with next computation, host, measured cost basis and falsifier; the hardware pool and run policy |
| [design/hilbert-function-rank-certificates.md](design/hilbert-function-rank-certificates.md) | design proposal for Rocq certificates of single values of a Hilbert function through ranks of Macaulay matrices: sizes for the Iso fiber cone (degree 3 is 1,156 x 969 of rank 704), why the enumerating rank checker of gororoba-open cannot take them, a reflection checker over a prime field, what a modular rank does and does not give in characteristic 0, and the open questions that decide whether it is built |
| [design/a5-vb-degree7-and-w8-char0-plan.md](design/a5-vb-degree7-and-w8-char0-plan.md) | E8-bar -> VB degree 7 (preregistered predictions, std(J + m^N) cost, slimgb and other export levers) and the W8 -> N- characteristic-0 transfer (canonical check-2 route, all-degree hypothesis); review in [archive/reviews/a5-vb7-w8-char0/](archive/reviews/a5-vb7-w8-char0/README.md) |
| [design/dimension32-global-topology-program.md](design/dimension32-global-topology-program.md) | open work of the dimension-32 classification after items 3-5: the three kernel-bundle residuals (with the argument that `xi_R` is actually nontrivial), attachments, nullity-4 kernel bundles, the finite global model of `Z_5` and the uniform structure in n, each with method, falsifier and substrate |
| [evidence/a5-kernel-bundles-residuals/README.md](evidence/a5-kernel-bundles-residuals/README.md) | kernel-bundle residuals: the quaternionic four-plane `xi_R` over `V_2(R^7)` is actually nontrivial (exact G_2 stabilizer action on `H^perp` plus the `SU(3)/SU(2)` clutching), gate core-756 |
| [design/a5-kernel-bundles-program.md](design/a5-kernel-bundles-program.md) | program goal for roadmap item 5, the kernel bundles of the A_5 zero-divisor strata: established facts, gaps (the kernel symmetry group, closed-form frames, unit-section topology, structure group), deliverables, behavior rules, and the [ledger](evidence/a5-kernel-bundles/ledger.md) the program keeps |
| [coherent-error-families-report.md](notes/topics/coherent-error-families-report.md) | coherent error families, drift and Rocq replays |
| [casimir-warp-evidence.md](notes/topics/casimir-warp-evidence.md) | Nanoscale warp claim reconciliation, existing-work boundary and native full-tensor counterexample with an active validation plan |
| [relativistic-metrology-scale.md](notes/topics/relativistic-metrology-scale.md) | the Belenos light cone as a mode-reachability set; relativistic and astronomical phases against the measured device instabilities, with the falsifiers of an astronomical coupling |
| [pais-claims-falsification.md](notes/topics/pais-claims-falsification.md) | the Pais Superforce (c^4/G as unification) decomposed into Planck-unit identities, the measured alpha_s(M_Pl) shortfall, the Friedmann identity and the active-mass and Cherenkov refutations of permittivity engineering; the Pais patent equations against Maxwell, QED and general-relativity bounds; the NAWCAD null; the QET passivity ladder and its information-excess endpoint as the QPU-testable mechanism |
| [psi-ontology-falsification.md](notes/topics/psi-ontology-falsification.md) | finite witnesses and identifiability boundaries around the quantum-state ontology question: the CHSH bound by enumeration, finite ontic-overlap witnesses, coherent apparatus dilations against classical records, and the nuisance geometry that leaves an extra dephasing rate unidentified in a Ramsey decay; states what no witness here decides |
| [persona-corpus-verified-results.md](notes/topics/persona-corpus-verified-results.md) | what survives of an LLM-persona corpus once checked from first principles: E8, triality and the Albert algebra (f4 derivations, e6 norm group, magic-square rows), corrected L-infinity, spectral-triple and affine definitions, the Sugawara central charge, the Coulomb gas and the Kac determinant with its constant to level 5, verified Casimir, QED and zero-point figures; the runs they admit (two-photon octonion associator on Ascella, QX-checked QET ladder on Tuna-17, IQM and IBM follow-ups), corrections to earlier notes, the quaternion encoding of the sl(2) bracket in the Ascella order interferometer, Cl(8) from octonion left multiplication failing on the 42 sedenion zero-divisor pairs, the associator characters with a Cl(0,3) mutation, the two independent decompositions reconciled by definition, and the removed claims |
| [chatgpt-archive-verified-results.md](notes/topics/chatgpt-archive-verified-results.md) | what survives of four ChatGPT brainstorm conversations (moonshine and pulsars, E7 and E8, L-infinity algebras and spectral triples, sedenion research articles) once checked against held sources and by computation, the claims that fail, the reference audit of the whole export (arXiv ids and DOIs resolved, fabricated and placeholder citations), and the results with repository content: the XOR-line Jacobiator zero set and the tolerance-algebra corollary |
| [open_gororoba_survey_deep_notes.md](notes/topics/open_gororoba_survey_deep_notes.md) | deep notes on the gororoba-open Rocq corpus |
| [prior_work_synthesis.md](notes/prior_work_synthesis.md) | what is known, what is new, labeled per claim |
| [koebisu_rank_stratum_research.md](notes/koebisu_rank_stratum_research.md) | dimension-32 rank question |
| [principal_skew_atlas.md](notes/principal_skew_atlas.md) | principal skew charts; chain continues in the four_support and schur notes |
| [formal_evidence_dependencies.md](notes/formal_evidence_dependencies.md) | formal evidence: algebra, measured counts, prospective checks |
| [open_gororoba_survey.md](notes/open_gororoba_survey.md) | survey of the sister repository |
| [topics/](notes/topics/) | unpinned research notes by subject; [notes/](notes/) holds the notes retained records name |

### Circuit and QPU design

| File | Contents |
|---|---|
| [design/belenos-suppression-law-case.md](design/belenos-suppression-law-case.md) | written case for two qpu:belenos jobs: three photons through the six-mode Fourier matrix with a cyclic input (12 of 20 collision-free outputs suppressed) against a non-periodic control; preregistered suppressed-fraction decision against the distinguishable and mean-field models, forecasts at the live HOM and g2, credits and seconds |
| [design/ascella-two-photon-associator-case.md](design/ascella-two-photon-associator-case.md) | written case for one qpu:ascella job: two photons through L_a L_b against L_(ab) (a = (e6+e7)/sqrt2, b = (e5+e7)/sqrt2) with a quaternion control; the associator appears only in two-photon interference; preregistered Delta endpoints, HOM-visibility model, credits, seconds and the HOM-floor decision |
| [design/ascella-pathion-four-term-blocks-case.md](design/ascella-pathion-four-term-blocks-case.md) | written case for one sim:ascella and one qpu:ascella job of 88 single-photon iterations: the pathion-only 4 x 4 coset blocks of the four-term A_5 operands B12 and C8 (classes absent at D = 16) through a Halmos dilation of B/4, with an A16 rank-1 anchor, dark normalization, cocycle-free, negated-entry and flipped-input mutation arms in +, -, -, + order, a basis-input null, preregistered thresholds, credits and the November pool |
| [design/ascella-cz-process-tomography-case.md](design/ascella-cz-process-tomography-case.md) | written case for two qpu:ascella jobs of 72 template iterations: process tomography of the postselected Ralph CZ on two dual-rail qubits (16 Pauli-eigenstate inputs x 9 readouts, 144 settings, one service-compiled mesh each); linear inversion of absolute outcome rates over nb_shots_used with a QRNG-seeded bootstrap; forecast process fidelity 0.786 under Perceval's noise model at the live HOM and g2; 4.0 credits ceiling; both jobs ran on 2026-10-31 and the Outcome section reports the exploratory fit |
| [design/ascella-cz-tomography-reference-case.md](design/ascella-cz-tomography-reference-case.md) | written case for two qpu:ascella jobs repeating the CZ process tomography at any HOM within 90 ± 6.8420696 points as the ensemble's reference: fresh ANU QRNG seeds, one 1,567,000-shot cap per iteration with per-setting samples (5.134 credits, process-fidelity spread 0.0040 against 0.0104), a submit gate on the HOM band, transmittance floor, idle token and frozen body, a forecast over the band, the two-photon overlap law F = (1 + M)/(2(2 - M)) with two overlap estimators, and thirteen preregistered conjectures with the retained pair's verdicts; built by `scripts/ascella_cz_tomography_reference_case.py`, nothing sent |
| [notes/topics/ascella-cz-tomography-ledgers.md](notes/topics/ascella-cz-tomography-ledgers.md) | photonic sources by manifest digest and the workspace's algebraic lineages, each judged on whether it predicts a rate of the two-photon CZ tomography; only the permanent and determinant do |
| [notes/topics/ascella-cz-tomography-band-results.md](notes/topics/ascella-cz-tomography-band-results.md) | the 2026-11-09 band pair: each preregistered verdict held against a post-data decomposition (unphysical-prediction cells, the gate-independent Z sector, rail transmission, two-click patterns), the overlap routes, and the retained-count tests of what the measurement raises: per-job output weights and the g2 law in the component model, the weighted model-check reference and the SPAM-separated process fit |
| [design/ascella-cz-compilation-ensemble-case.md](design/ascella-cz-compilation-ensemble-case.md) | design for two qpu:ascella jobs of 60 iterations: the postselected CZ through two complementary truth tables (Hofmann bound on the process fidelity), each of 8 settings under 10 compilation seeds for the between-mesh variance, with 4 anchor settings repeated on identical meshes across both jobs as the drift and job-effect test; built by `scripts/ascella_cz_ensemble_case.py` with frozen requests, plan reads and forecast, nothing sent or approved |
| [design/ascella-pathion-coset-block-pairs-case.md](design/ascella-pathion-coset-block-pairs-case.md) | written case for one sim:ascella and one qpu:ascella job of 52 single-photon iterations, the successor of the four-term block case: two coset blocks per photon on 9 modes at one common scale (all D = 32-only classes, the D = 16 reference, T, F, C, N arms per block), per-slot A16 anchor and kernel dark, crosstalk and independence arms, a palindromic order with every setting in both slot orientations, and a preregistered test of whether the predecessor's C8 spread follows the block or the mode slot |
| [design/ascella-pathion-mesh-persistence-case.md](design/ascella-pathion-mesh-persistence-case.md) | written case (executed 2026-11-07: the sim:ascella gate run and qpu:ascella job 6bc382af; readings in the pathion findings; execution record and corrections in [design/ascella-pathion-mesh-persistence-execution.md](design/ascella-pathion-mesh-persistence-execution.md)) for one sim:ascella mesh gate and one qpu:ascella job of 84 single-photon iterations, the successor of the two-coset-block case: the original 52 settings replayed verbatim, seven fresh anchor seeds, the eight failing settings at fresh seeds and a fresh dark, with preregistered persistence, anchor, fresh-mesh, frozen-map and correction decisions that separate per-mesh fixed errors from a static per-shifter map (ledger A5-191) |
| [design/belenos-associator-visibility-case.md](design/belenos-associator-visibility-case.md) | written case for two qpu:belenos jobs: the Ascella associator closure design on the teleportation source pairs (18, 20) and (20, 22), measuring in-situ two-photon visibility against the reported HOM and the 0.81 that reproduces teleportation job-01's correctness; forecast table, credits and seconds |
| [design/belenos-mode-swap-interleaved-case.md](design/belenos-mode-swap-interleaved-case.md) | written case for nine qpu:belenos jobs (job-00 cut after set 0; job-03 to job-10 five iterations each): the packed and swapped box-kite layouts interleaved with mesh-identical primary repeats and replicate compilation seeds, testing placement in claim qd-belenos-packed-mode-swap against the measured per-seed mesh variance and drift; analysis rules, Monte Carlo rates, credits and seconds |
| [design/ascella-associator-thermal-seismograph.md](design/ascella-associator-thermal-seismograph.md) | written prospective case for one 32-iteration qpu:ascella job: two photons through octonion associator and quaternion control under counterbalanced Hot (pi), Cold (0), and Wrapped (2*pi) predecessor phase conditioning with 12-mode spatial sentinel monitoring |
| [design/tuna-order-pilot-adversarial-admission.md](design/tuna-order-pilot-adversarial-admission.md) | descriptive pilot preregistration, adversarial findings and execution admission |
| [design/hypercomplex-operator-evidence.md](design/hypercomplex-operator-evidence.md) | algebra falsifiers, operator encodings, library roles and device evidence |
| [design/heron-idle-readout-attribution.md](design/heron-idle-readout-attribution.md) | own-partner, near-field and far-field split of the Kingston idle readout phase rate, by complementary reader classes |
| [runbooks/hypercomplex-operator-cases-v2.md](runbooks/hypercomplex-operator-cases-v2.md) | frozen provider cases, pacing, costs and approval boundary |
| [state/hypercomplex-libraries/libraries.md](state/hypercomplex-libraries/libraries.md) | expanded Python distribution roles and documented candidates |
| [evidence/submitted_circuits/README.md](evidence/submitted_circuits/README.md) | complete retained IBM job-input comparison and immutable replay successor |
| [evidence/sedenion-clifford-envelope/README.md](evidence/sedenion-clifford-envelope/README.md) | exact eight-generator Cl(0,8) envelope spanning M16(R) |
| [evidence/hypercomplex-operators/README.md](evidence/hypercomplex-operators/README.md) | exact replay, probability explorer and distribution inventory |
| [evidence/ascella-associator-predecessor/README.md](evidence/ascella-associator-predecessor/README.md) | Ascella two-photon octonion associator predecessor-conditioning benchmark on qpu:ascella (job e13e5ed0): massive non-associative contrast (1.6127, > 204 sigma), strict physical null control (0.000136), in situ closure (-0.0447), fail-closed TOST thermal carryover, zero background drift, and spatial sentinel monitoring across modes 4..11 |
| [evidence/ascella-associator-predecessor/job-01-deep-seismograph.md](evidence/ascella-associator-predecessor/job-01-deep-seismograph.md) | Ascella deep associator seismograph on qpu:ascella (job 7ae2af4b): scaled 2.5x depth to 653,485 physical events (122 s execution), decisively resolving the Codex fail-closed TOST predecessor carryover gap to EQUIVALENT (+0.0070 Hot, +0.0049 Wrapped in [-0.02, +0.02]), associator contrast 1.5859 (> 522 sigma), null control 0.0099, closure -0.0292 |
| [evidence/ascella-associator-character/README.md](evidence/ascella-associator-character/README.md) | Ascella 8-mode octonion associator character interferometer on qpu:ascella (job e2bf833e): 21-pair octonion character kernel theorem and single-photon character transfer across 4 primary triads on 8-mode Clements mesh embedded into 12-mode Ascella QPU, physical contrast 1.99732 (99.87% of ideal 2.0), sentinel leakage 2.32% |
| [evidence/ascella-sim-twin-falsification/README.md](evidence/ascella-sim-twin-falsification/README.md) | Ascella simulation campaigns (sim:ascella jobs fe44988c and 7d70a2d2), 3-qubit baseline twin model for Qiskit Aer and QX emulator, live platform audit (Tuna-17 executing, Belenos optical recovery), and multi-technology falsification matrix across photonics, transmons, flux, Rydberg, and trapped ions |
| [design/et-rows.md](design/et-rows.md) | ET-row device experiment |
| [design/measurement-sequence-pinching.md](design/measurement-sequence-pinching.md) | `measurement-sequence` and `measurement-sequence-diagnostic` families: N rotations each followed by a mid-circuit measurement against an elapsed-time-matched delay, ideal pinching law, endpoints, the preregistered decision rule with its model and Aer validation tables, the diagnostic that measures the gate-model scatter floor (qubit rule, floor rule, Aer validation), and Tuna-17 port |
| [design/measurement-sequence-adaptive-envelope.md](design/measurement-sequence-adaptive-envelope.md) | calibration-adaptive approval envelope for the measurement-sequence family: layout rule re-applied at submit, 20 us repetition delay with a 50 us fallback, herald postselection, in-job gate-model floor, scaling to about 50 qubits |
| [design/measurement-sequence-envelope-successor.md](design/measurement-sequence-envelope-successor.md) | successor of the measurement-sequence envelope run: a carryover screen sized from the endpoint sensitivity and measured by single-circuit history jobs, descriptive settle gap, per-qubit report below 8 kept qubits |
| [design/hybrid-shor.md](design/hybrid-shor.md) | hybrid Shor architecture for IBM Heron r2 |
| [design/retention-bookkeeping-per-record.md](design/retention-bookkeeping-per-record.md) | retained-run bookkeeping bound per job record instead of per aggregate file: measured cost of a retention, the invariants each binding proves, and the levers with predicted effects and falsifiers |
| [design/n21-orbit-window-dose-envelope.md](design/n21-orbit-window-dose-envelope.md) | calibration-adaptive approval envelope, bounds and decisions D1-D3 of the N=21 orbit window-dose sweep |
| [design/n21-orbit-detuning-sign-envelope.md](design/n21-orbit-detuning-sign-envelope.md) | calibration-adaptive approval envelope, bounds and decisions D1-D3 of the N=21 orbit detuning-sign test (orbit phase rate against work-bit Ramsey offsets) |
| [design/provider-access-requests.md](design/provider-access-requests.md) | access-request drafts for Quantinuum, D-Wave, Classiq, OQC, Rigetti, SuperQ and Kipu, with the review checklist |
| [design/factoring-notes.md](design/factoring-notes.md) | factoring and the Cayley-Dickson ladder |
| [design/gpu-exact-modular-linear-algebra.md](design/gpu-exact-modular-linear-algebra.md) | exact F_p linear algebra on the build host's tensor cores: INT8 and FP8 digit products, an HMM and pinned-staging memory hierarchy, recursive PLUQ, Freivalds verification, measured throughput |
| [design/numpy-validation.md](design/numpy-validation.md) | numerical environment validation |
| [design/native-numeric-replay.md](design/native-numeric-replay.md) | identity-scoped replay of retained float records once producers and CI runners compute on native numeric paths: exact within an identity, bounded with exact decisions across |
| [evidence/least-squares-precision/README.md](evidence/least-squares-precision/README.md) | bits each arithmetic gets right on the Ascella CZ tomography prediction (float64 drivers and threads, x87, binary128, arb) against a certified arb reference, the sweep under memory-capped scopes, two numpy-quaddtype defects, and the certified-rounding producer |
| [design/bdsc-tuna17-pauli-pilot.md](design/bdsc-tuna17-pauli-pilot.md) | Tuna-17 pilot of the BDSC target as a four-qubit local Pauli readout: bank, placement, analysis |
| [design/iqm-garnet-timing-pilot.md](design/iqm-garnet-timing-pilot.md) | IQM Garnet billing pilot: per-job, per-shot, per-circuit and active-reset cost |
| [design/heron-latency-logical-recovery.md](design/heron-latency-logical-recovery.md) | Heron r2 feed-forward against Pauli-frame recovery of a bit-flip-coded Bell pair: latency and window cost of logical fidelity, arms, contracts, power |
| [design/iqm-garnet-signed-kernel-probe.md](design/iqm-garnet-signed-kernel-probe.md) | signed sedenion kernel probe on IQM Garnet: odd dilation overlap, heralded active reset, prediction |
| [design/iqm-garnet-kernel-cancellation-probe.md](design/iqm-garnet-kernel-cancellation-probe.md) | kernel cancellation probe on IQM Garnet: zero-divisor sign at 37 CZ, bright control, over-rotation trains, H1-H5 |
| [design/iqm-garnet-qet-compensated-ladder.md](design/iqm-garnet-qet-compensated-ladder.md) | phase-compensated QET ladder on IQM Garnet: cc_prx lowering of the Kingston compensated ladder, five packed pairs, non-pi angle qualification, H1-H4 |
| [design/iqm-garnet-idle-schedule-train-readout.md](design/iqm-garnet-idle-schedule-train-readout.md) | IQM Garnet idle schedule (ASAP or ALAP, from a pulsed qubit's relaxation beside an uncoupled identity train) and QB6/QB11 train over-rotation fitted with each qubit's own readout, H1-H2 |
| [design/iqm-garnet-measurement-sequence-pinching.md](design/iqm-garnet-measurement-sequence-pinching.md) | IQM Garnet measurement-sequence pinching: Zeno build-up of recorded mid-circuit measurements against a unitary null, a delay control and a settled-readout control on six uncoupled qubits, with pi/2-pair steps, the diagnostic-based qubit exclusions and the pre-flight stop rule |
| [design/iqm-garnet-measurement-sequence-diagnostic.md](design/iqm-garnet-measurement-sequence-diagnostic.md) | IQM Garnet diagnostic of the unitary-arm excess: axis phase per small-angle prx pulse against |1> loss before the readout, eight circuits on the pinching qubits, with a preregistered decision rule |
| [design/primorial-cover-defect-probes.md](design/primorial-cover-defect-probes.md) | primorial cover-defect circuits: Grover quotient, phase-gradient tomography with a zero-angle null arm, the gap-86 and gap-88 repair contrasts against the mutation test, the Kingston noise prediction and the static-ZZ and axis-tilt residuals; its single-family hardware decision is superseded by [primorial-cover-joint-coherent-bounds.md](design/primorial-cover-joint-coherent-bounds.md) |
| [design/primorial-cover-joint-coherent-bounds.md](design/primorial-cover-joint-coherent-bounds.md) | primorial gap-88 tomography under joint tilt, amplitude and CZ-phase gate-error bounds: per-coefficient z, the coherent-fraction boundary that decides the device question, arm-mismatch tolerances, the twirled-CZ model, the every-path sweep and the probes that precede any hardware case |
| [design/bdsc-qualification.md](design/bdsc-qualification.md) | Belenos dark-subspace certificate: provider contracts and qualification measurements; [principal-angle replay](notes/quandela/bdsc.md) |
| [design/quantum-experiment-conformance.md](design/quantum-experiment-conformance.md) | five evidence-gated proposals: dimension-six transitions, sedenion heralding, Fano and projection counterexamples, quarter-mass amplification |
| [design/ascella-belenos-entanglement-teleportation.md](design/ascella-belenos-entanglement-teleportation.md) | Ascella-Belenos claim levels, physical gates, ideal dual-rail instrument, certified benchmark, local rehearsal outcomes and the dated provider-response assessment |
| [runbooks/ascella-belenos-network-case.md](runbooks/ascella-belenos-network-case.md) | Strict offline case and normalized joint-record contracts, typed attempts, separate fidelity estimands, exact byte binding, CLI usage and the remaining provider/physical gates |
| [design/fixed-route-teleportation-benchmark.md](design/fixed-route-teleportation-benchmark.md) | prospective, unsubmitted fixed-route six-state teleportation design on Tuna-17: every Pauli eigenstate crossed with every selected route in randomized complete blocks, the frame decode, the Hoeffding sampling bound against the 2/3 measure-and-prepare comparison, and the `qi_records` analysis path ([contract module](../gororoba_quantum/teleportation_contract.py), [CLI](../scripts/qi_teleportation_design.py)) |
| [evidence/teleportation-publication/README.md](evidence/teleportation-publication/README.md) | source-bound checks of the two teleportation and Kingston energy-control SVG plates: the manifest of record blobs and master digests, the displayed-value derivation, layout checks and the on-demand render ([builder](../scripts/publication_plates.py), [validator](../gororoba_quantum/publication_evidence.py)) |
| [design/belenos-best-mesh-design-investigation.md](design/belenos-best-mesh-design-investigation.md) | design investigation of a per-input best-mesh screen and replay on qpu:belenos from the retained job-02 and job-03 data: exact compiler, between-mesh spread and shrinkage, replay power, the acceptance filter, source shift and structural predictors; verdict and the persistence question it leaves ([script](../scripts/belenos_best_mesh_first_principles.py)) |
| [design/belenos-best-mesh-teleportation-case.md](design/belenos-best-mesh-teleportation-case.md) | unapproved draft case, superseded by the design investigation above: screen six compilation seeds per teleportation input on qpu:belenos, select the best mesh per input, replay it in two confirm jobs; four built screen cases, no job sent ([script](../scripts/belenos_teleportation_best_mesh.py)) |
| [design/belenos-herald-leak-analysis.md](design/belenos-herald-leak-analysis.md) | preregistered offline analysis of the herald rejections of the split teleportation rehearsal on qpu:belenos: whether a compiled mesh changes where herald clicks land, against a same-mesh null arm |
| [design/belenos-mesh-persistence-case.md](design/belenos-mesh-persistence-case.md) | written case, awaiting approval, for one qpu:belenos job that replays the four retained meshes of the mode-swap packed set-4 group after recalibration: seed-to-mesh identity by decoded unitary first, then the persistence slope of each mesh's centered share deviation with its relabeling upper bound; the teleportation replay as an optional second case ([script](../scripts/belenos_mesh_persistence.py)) |
| [runbooks/bdsc-qualification-case.md](runbooks/bdsc-qualification-case.md) | order, prerequisites and stop conditions of the BDSC six-state consistency case |
| [runbooks/bdsc-tuna17-pauli-pilot.md](runbooks/bdsc-tuna17-pauli-pilot.md) | build, dry run and submission order of the Tuna-17 four-qubit Pauli readout pilot |
| [runbooks/quandela-credit-optimization.md](runbooks/quandela-credit-optimization.md) | Quandela job sizing for case design: the billing rule measured per job, the per-iteration time of each qpu:belenos job shape, packing limits, the shape rule and cost planning; the [billing-rule successor](evidence/quandela-billing-rule-successor/README.md) names the pinned records that state the older rule |
| [runbooks/ascella-block-run-design.md](runbooks/ascella-block-run-design.md) | living design and reading guide for photonic block cases on qpu:ascella: the served-mesh facts (byte-identical meshes, fixed per-mesh error, per-seed correction), why the four-term case passed and the two-coset-block case failed, the mesh-persistence reading module with the review finding behind each mechanism, design rules for the next case, open questions and a revision log |
| [runbooks/quandela-scheduled-runs.md](runbooks/quandela-scheduled-runs.md) | unattended submission of approved, spaced Quandela jobs from a committed schedule through GitHub Actions |
| [runbooks/generated-views.md](runbooks/generated-views.md) | the plan, research-state and reading-copy views that render on demand, their commands and why none is committed |
| [runbooks/classical-compute-pool.md](runbooks/classical-compute-pool.md) | free classical capacity per substrate (build host, Kaggle, GitHub Actions, Azure trial), what pooling across machines buys, tool installs per substrate, measured memory of the A_5 Rees eliminations |
| [runbooks/critical-peer-review.md](runbooks/critical-peer-review.md) | reviewer checklist for quantum-hardware results: preregistration, multiplicity, effect size, dependent correlations, drift, provenance, simulation boundary and claim wording |
| [QUANTUM_DISPATCH.md](../plans/QUANTUM_DISPATCH.md) | quantum dispatch plan |
| [coherence-case-science-review.md](../plans/reviews/coherence-case-science-review.md) | coherence-window case, science review |
| [coherence-case-submission-review.md](../plans/reviews/coherence-case-submission-review.md) | coherence-window case, submission-path review |
| [qpu_run_economy.md](notes/qpu_run_economy.md) | information per billed second |

### IBM Heron r2

| File | Contents |
|---|---|
| [ibm_heron_platform.md](notes/ibm_heron_platform.md) | measured Targets and current documentation |
| [hardware-controls.md](notes/ibm_quantum/hardware-controls.md) | every control reachable through qiskit-ibm-runtime |
| [evidence/local_idle_padding/README.md](evidence/local_idle_padding/README.md) | list-schedule idle written into ISA circuits before submission: issue 526's falsifier over the retained dynamic runs, ALAP against the service schedule, and idle-scale, CZ-factor, event and placebo controls |
| [learning-quantum-teleportation.md](notes/ibm_quantum/learning-quantum-teleportation.md) | IBM Quantum Learning teleportation lesson: outcome-to-correction table |
| [qiskit-ecosystem.md](notes/qiskit-ecosystem.md) | Qiskit ecosystem audit |
| [qiskit-ecosystem-install-plan.md](notes/qiskit-ecosystem-install-plan.md) | Qiskit ecosystem install plan |
| [qiskit-packages/README.md](notes/qiskit-packages/README.md) | installed Qiskit-adjacent packages: install surfaces, per-package notes, interconnections, open items |

### Providers

| File | Contents |
|---|---|
| [providers.md](notes/providers.md) | provider interpreter variables and MCP server names, with the guide of each provider |
| [tuna17-bipartite-designs.md](notes/quantum_inspire/tuna17-bipartite-designs.md) | Tuna-17 cubic Walsh classes and box-kite packing |
| [quandela/literature.md](notes/quandela/literature.md) | published methods for characterizing a Belenos-class mesh |
| [quandela/quickstart.md](notes/quandela/quickstart.md) | Quandela Cloud quick start |
| [quandela/roadmap-2026-03.md](notes/quandela/roadmap-2026-03.md) | Quandela March 2026 roadmap and the Welinq interconnect announcement: networking and modular-system statements with page and target year |
| [iqm/python-stack.md](notes/iqm/python-stack.md) | Python stack for IQM Resonance |

### Simulation

| File | Contents |
|---|---|
| [build_host/custatevec.md](notes/build_host/custatevec.md) | cuStateVec in the host Aer build |
| [build_host/python-stack.md](notes/build_host/python-stack.md) | build-host Python stack |
| [competition-requirements.md](notes/kaggle/competition-requirements.md) | entry status, deadlines, submission formats, scoring, limits prizes and the entry audit of ten Kaggle competitions |
| [jax-bridge-structure-report.md](notes/kaggle/jax-bridge-structure-report.md) | JAX bridge sweep, export once per structure |
| [simulation-cost-levers.md](runbooks/simulation-cost-levers.md) | planner, ghost replay and package costs |
| [compute-flags.md](runbooks/compute-flags.md) | pre-run flag review: memory caps, threads and solver options for Singular and msolve |
| [library-flags.md](runbooks/library-flags.md) | per-library flags: BLAS threads, Aer, JAX, torch, sympy, FLINT, cvxpy and executable options, verified against the installed packages |

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
| [cache-locations.md](runbooks/cache-locations.md) | cache, venv, build-tree and run-output locations outside the checkout; cleanup classes and the future `make clean` and `make distclean` targets |
| [vectorized-fits.md](runbooks/vectorized-fits.md) | batched classical fits across replicates |
| [codex-review-loop.md](runbooks/codex-review-loop.md) | Codex review rounds, reply markers, stacked PRs, merge sequence and the REST/GraphQL split |
| [qiskit-skills.md](runbooks/qiskit-skills.md) | installed Qiskit agent skills, upstream pin, monthly check and when to invoke the migration skill |
| [computer-algebra.md](runbooks/computer-algebra.md) | computer-algebra foundations: global orderings, local invariants by the normal cone, the cheapest decisive computation for radicality, Cohen-Macaulayness, components and fibers, numeric search before symbolic certification, saturation rules and Singular pitfalls |
| [run-rulebook.md](runbooks/run-rulebook.md) | per-run record on top of the foundations: question and decisive outcome, formulation, launch line, departures and why, parallelism, limits, checkpoints, end state, outcome |
| [null-shards.md](runbooks/null-shards.md) | the successor null through one pool, Kaggle kernels and hosted-runner shards |
| [idle-falsifier.md](runbooks/idle-falsifier.md) | the local idle falsifier through resumable per-run parts and hosted-runner jobs |

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
| [belenos-recovery-watch.md](archive/handoffs/belenos-recovery-watch.md) | Belenos recovery watch, issue #556 procedure and the job-01 rehearsal build |
| [2026-10-30-quandela-next-cases.md](archive/handoffs/2026-10-30-quandela-next-cases.md) | Ascella matched-mesh third acquisition and Belenos teleportation job-01: written cases, live plans and the case-identity gate blocker |
| [provider-counter-audit.md](archive/handoffs/provider-counter-audit.md) | provider-counter audit: merged PRs, collection-boundary tasks, coverage gaps, closure and open provider questions |
| [handoff-notes-2026-10-15.md](archive/handoffs/handoff-notes-2026-10-15.md) | chat-session decisions and falsification results |
| [handoff-notes.md](archive/handoffs/handoff-notes.md) | program handoff sections |
| [archive/reviews/README.md](archive/reviews/README.md) | review and audit reports; [docs audit](archive/reviews/docs-audit.md) |
