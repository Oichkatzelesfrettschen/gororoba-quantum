# Documentation map

This page is the single entry to the repository's documents. Rules live in the agent guides, measured facts in the
provider and platform notes, claims in the research notes, and retained bytes under `evidence/` and `../results/`.
`scripts/check_markdown_links.py` keeps every relative link and anchor below resolving.

Placement, naming, linking and immutability rules for every new or moved document: [AGENTS.md, "Documents"](../AGENTS.md#documents).

## Areas

| Area | Owns | Entry |
|---|---|---|
| Rules | agent doctrine, gate machinery, provider tables | [AGENTS.md](../AGENTS.md), [ci/AGENTS.md](../ci/AGENTS.md) |
| Sources and papers | PDFs, licenses, one note per source, verifier, reading-copy links | [INDEX.md](INDEX.md), [sources/README.md](sources/README.md), [sources/reading-copies.md](sources/reading-copies.md) |
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
| Planck Technologies | account closed; audited SDK, key rejected and simulator returns random bits | [planck/README.md](notes/planck/README.md) |
| AWS | free-plan project account; Braket unavailable; CLI, Agent Toolkit and pinned AWS MCP server | [aws/README.md](notes/aws/README.md) |
| Azure | free-trial subscription; Quantum workspace with free Quantinuum, Pasqal and Rigetti emulator plans; 4-vCPU trial compute | [azure/README.md](notes/azure/README.md) |
| QRNG seed sources | ANU, Outshift and Quandela draws for every new seed | [qrng/README.md](notes/qrng/README.md) |
| Simulation | Kaggle CPU and GPU kernels, host Aer build | [kaggle/README.md](notes/kaggle/README.md) |
| Local simulator cross-check | full-output photonic probabilities and precision-preserving cQASM export | [simulation evidence](../results/local-simulation/README.md), [complete optical outputs](../results/local-simulation/optical-operator-replay.json), [serialized Ascella request](../results/local-simulation/ascella-serialized-order-replay/README.md), [compiler replay provenance](../results/local-simulation/compiler-replay-provenance.md) |
| Packages and tools | hypercomplex stack, quantum tool manuals, Aer packaging | [packages/README.md](notes/packages/README.md) |
| Python | interpreters, library roles, optimization ladder | [PYTHON.md](PYTHON.md) |
| CI and gates | gate list, ledger, runtime measurements | [ci/AGENTS.md](../ci/AGENTS.md) |
| Planning | work records, next actions, blockers and completion receipts | [planning entrance](state/plans.md), [commands](runbooks/plan-tracker.md), [migration evidence](evidence/plan-reconciliation/README.md) |
| State and records | claim registry, run census, roadmap | [RESEARCH_STATE.md](state/RESEARCH_STATE.md) |
| Evidence closure | source-relative job identities, denominators, dependencies and acquisition decisions | [derived view](evidence/evidence-closure/README.md), [operator procedure](runbooks/evidence-closure.md), [derivation-led synthesis source](notes/topics/algebra_measurement_synthesis.tex) |
| Results index and archive copies | run, job, acquisition and claim lookups; Software Heritage and git bundle copies | [results index](runbooks/results-index.md), [archive copies](runbooks/repository-archive.md), [archive observations](evidence/repository-archive/README.md) |
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
| [2609.11588.md](notes/papers/2609.11588.md) | Lemley 2026 quasilinear multiplication: Algorithm 3.5 replayed for 2 to 256 dimensions and the multiplication-count bound (hosted, CC BY 4.0) |
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

### Algebra and proofs

| File | Contents |
|---|---|
| [topics/box-kites/README.md](notes/topics/box-kites/README.md) | box-kite experiment program index |
| [bdsc-pauli-readout.md](notes/topics/bdsc-pauli-readout.md) | BDSC target and blade effects as three-term four-qubit Pauli sums; local readout and 13-basis cover |
| [algebra-hardware-probe-principles.md](notes/topics/algebra-hardware-probe-principles.md) | first principles of algebra hardware probes: mutation test, eigen-observable, interleaving, null arm, noisy coherent response; findings ledger of the Garnet runs |
| [primorial-cover-defects.md](notes/topics/primorial-cover-defects.md) | missing primorial-wheel gaps 20, 32, 86, 88 as restricted covers: exhaustive defect certificates, capacity and LP bounds, singleton repair, slice Walsh Hamiltonians, the eight-CNOT parity network and the reproduction of Ziller Table 1 for `k <= 20` |
| [c5-zero-divisor-code-falsification.md](notes/topics/c5-zero-divisor-code-falsification.md) | zero-divisor code, falsified thought experiment |
| [cd-star-lattice-tower.md](notes/topics/cd-star-lattice-tower.md) | Tuna-17 as the Gaussian-integer star lattice; lifts to dimensions 3, 4, 8, 16, the Paley identification of their symmetry groups and the sedenion zero divisors |
| [evidence/cd-star-lattice/README.md](evidence/cd-star-lattice/README.md) | exact star-lattice census bound to the Tuna-17 catalogue topology, with SL(2, q) and PGL(2, 7) certificates and a nauty replay |
| [evidence/albuquerque-majid-convention/README.md](evidence/albuquerque-majid-convention/README.md) | replay of the Albuquerque-Majid cochain recursion against cd_sign: transposed map exact on 5,460 pairs, untransposed control fails, associators agree on 37,448 triples |
| [evidence/cd-imaginary-sum-conference/README.md](evidence/cd-imaginary-sum-conference/README.md) | Rocq proof, for every Cayley-Dickson dimension, that right multiplication by the imaginary sum is a skew conference matrix, with its kernel receipts and the bridge to cd_sign |
| [evidence/sedenion-automorphisms/README.md](evidence/sedenion-automorphisms/README.md) | Exact computation of `Aut(O) = G2` and `Aut(S) = G2 x S3` for `cd_core` (derivations, commutant, Groebner roots) deciding Wilmot's two `Aut(S)` statements, the Rocq tower's evaluated sedenion table, and the 11 corrected Gresnigt Table 5 cells with the erratum report |
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
| [evidence/a5-strata-regularity/README.md](evidence/a5-strata-regularity/README.md) | orbit stratification of the A_5 rank strata under G_2(C) x SO(2, C) x C^* (R_8 minus 0 is twelve orbits), the singular locus of every closure and of V(Q), V(G), a Whitney stratification, transverse germs and the normal link S^1 disjoint union S^3 of R_12 at x0, with an independent cd_core verification ([verification.md](evidence/a5-strata-regularity/verification.md)) |
| [evidence/a5-kernel-bundles/README.md](evidence/a5-kernel-bundles/README.md) | kernel bundles of the A_5 strata of nullity at least 12 (roadmap item 5): kernel symmetry algebra, compact-orbit moduli, stabilizer representations, exact transition cocycle and equivalence classes, with an independent cd_core verification ([verification.md](evidence/a5-kernel-bundles/verification.md)) |
| [design/a5-kernel-bundles-program.md](design/a5-kernel-bundles-program.md) | program goal for roadmap item 5, the kernel bundles of the A_5 zero-divisor strata: established facts, gaps (the kernel symmetry group, closed-form frames, unit-section topology, structure group), deliverables, behavior rules, and the [ledger](evidence/a5-kernel-bundles/ledger.md) the program keeps |
| [coherent-error-families-report.md](notes/topics/coherent-error-families-report.md) | coherent error families, drift and Rocq replays |
| [relativistic-metrology-scale.md](notes/topics/relativistic-metrology-scale.md) | the Belenos light cone as a mode-reachability set; relativistic and astronomical phases against the measured device instabilities, with the falsifiers of an astronomical coupling |
| [pais-claims-falsification.md](notes/topics/pais-claims-falsification.md) | the Pais Superforce (c^4/G as unification) decomposed into Planck-unit identities, the measured alpha_s(M_Pl) shortfall, the Friedmann identity and the active-mass and Cherenkov refutations of permittivity engineering; the Pais patent equations against Maxwell, QED and general-relativity bounds; the NAWCAD null; the QET passivity ladder and its information-excess endpoint as the QPU-testable mechanism |
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
| [design/measurement-sequence-pinching.md](design/measurement-sequence-pinching.md) | `measurement-sequence` and `measurement-sequence-diagnostic` families: N rotations each followed by a mid-circuit measurement against an elapsed-time-matched delay, ideal pinching law, endpoints, the preregistered decision rule with its model and Aer validation tables, the diagnostic that measures the gate-model scatter floor (qubit rule, floor rule, Aer validation), and Tuna-17 port |
| [design/measurement-sequence-adaptive-envelope.md](design/measurement-sequence-adaptive-envelope.md) | calibration-adaptive approval envelope for the measurement-sequence family: layout rule re-applied at submit, 20 us repetition delay with a 50 us fallback, herald postselection, in-job gate-model floor, scaling to about 50 qubits |
| [design/hybrid-shor.md](design/hybrid-shor.md) | hybrid Shor architecture for IBM Heron r2 |
| [design/provider-access-requests.md](design/provider-access-requests.md) | access-request drafts for Quantinuum, D-Wave, Classiq, OQC, Rigetti, SuperQ and Kipu, with the review checklist |
| [design/factoring-notes.md](design/factoring-notes.md) | factoring and the Cayley-Dickson ladder |
| [design/numpy-validation.md](design/numpy-validation.md) | numerical environment validation |
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
| [design/ascella-belenos-entanglement-teleportation.md](design/ascella-belenos-entanglement-teleportation.md) | Ascella-Belenos entanglement and teleportation: claim levels, gates, ideal dual-rail instrument ([qd_network_protocol.py](../scripts/qd_network_protocol.py)), decision statistics, the single-chip Belenos rehearsal case ([qd_teleportation_rehearsal.py](../scripts/qd_teleportation_rehearsal.py)) and the unsent provider request |
| [runbooks/bdsc-qualification-case.md](runbooks/bdsc-qualification-case.md) | order, prerequisites and stop conditions of the BDSC six-state consistency case |
| [runbooks/bdsc-tuna17-pauli-pilot.md](runbooks/bdsc-tuna17-pauli-pilot.md) | build, dry run and submission order of the Tuna-17 four-qubit Pauli readout pilot |
| [runbooks/quandela-credit-optimization.md](runbooks/quandela-credit-optimization.md) | Quandela billing rule measured per job, packing limits and cost planning |
| [runbooks/quandela-scheduled-runs.md](runbooks/quandela-scheduled-runs.md) | unattended submission of approved, spaced Quandela jobs from a committed schedule through GitHub Actions |
| [runbooks/provider-credits.md](runbooks/provider-credits.md) | read-only daily snapshot of every provider's free allotment, alert thresholds and the systemd user timer |
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
| [learning-quantum-teleportation.md](notes/ibm_quantum/learning-quantum-teleportation.md) | IBM Quantum Learning teleportation lesson: outcome-to-correction table |
| [qiskit-ecosystem.md](notes/qiskit-ecosystem.md) | Qiskit ecosystem audit |
| [qiskit-ecosystem-install-plan.md](notes/qiskit-ecosystem-install-plan.md) | Qiskit ecosystem install plan |

### Providers

| File | Contents |
|---|---|
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
| [belenos-recovery-watch.md](archive/handoffs/belenos-recovery-watch.md) | Belenos recovery watch, issue #556 procedure and the job-01 rehearsal build |
| [handoff-notes-2026-10-15.md](archive/handoffs/handoff-notes-2026-10-15.md) | chat-session decisions and falsification results |
| [handoff-notes.md](archive/handoffs/handoff-notes.md) | program handoff sections |
| [archive/reviews/README.md](archive/reviews/README.md) | review and audit reports; [docs audit](archive/reviews/docs-audit.md) |
