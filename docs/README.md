# Sources and research notes

[INDEX.md](INDEX.md) distinguishes hosted papers from ignored local reading copies
and links every PDF source to its note and hosting evidence.

One note per paper under notes/. Each note:
- carries the citation, the URL that served the PDF, and its sha256;
- tags every statement as from-paper or inference;
- rates relevance to (a) calibration-aware compilation on IBM hardware,
  (b) Cayley-Dickson structure, and (c) factoring resource estimates.

The canonical source library lives under `docs/`: paper descriptions in
`notes/`, retained primary PDFs in `pdf/`, and repeatable research checks in
`evidence/`. [SOURCES.json](SOURCES.json) records each PDF's URL, SHA-256,
byte count, page count, acquisition status, owning note, and exact-version
license evidence. The library publishes 18 licensed PDFs and two aliases;
64 external sources retain citations and optional ignored local reading copies.
Four licensed original software archives retain upstream notices under
`source_archives/`; the verifier checks their inspected members and licenses.
[PDF_SHA256SUMS](PDF_SHA256SUMS) verifies the published PDF set from the
repository root with `sha256sum -c docs/PDF_SHA256SUMS`.

The `literature -> docs` compatibility link preserves historical paths used
in source comments, verification manifests, and retained parallel-experiment checksum
paths. Both names identify the same retained files. New browser links use `docs/`, since
GitHub displays a directory symlink as a link blob. The two implementation-audit
ledgers and the two mathematical guides named by their manifests retain their original
bytes. Per-paper notes retain the scope and dates of their original readings;
older references to an ignored/local cache describe that acquisition history.
The registry records the retained copies and their fresh hash checks.

The Nature articles are paywalled. The retained arXiv preprints remain distinct
from the versions of record, including the two explicitly named PDF aliases.
HTML-only sources and their reading scopes appear in the registry and notes.
Explicit CC BY 4.0 or CC0 permission supports the published PDFs. ArXiv-only
hosting grants, personal-copy permissions, and sources without an established
rehosting grant receive external records and ignored local copies under
`local_source_cache/`. The registry retains first-party evidence URLs and hashes.
Downloaded documents retain their authors' notices and licenses; repository
licensing does not relabel third-party papers. The source verifier checks local
copies when present and permits a fresh checkout without those optional files.

The [coordinated research roadmap](RESEARCH_ROADMAP.md) consolidates the
cumulative objectives, verified results, ownership, ordering, and remaining
proof and hardware gates.

The [rank-stratum research decomposition](notes/koebisu_rank_stratum_research.md)
connects Koebisu's Question 4, exact rank predicates, local kernel reductions,
attachment geometry, and bounded hardware measurements. The
[folding and Rocq audit](notes/open_gororoba_folding_proofs.md) identifies which
dimensional reductions preserve the algebraic information and which formal
statements the sister repository actually proves. The
[model-discrimination decision](notes/model_discrimination_optimizer.md)
sets the hardware priority before broad atlas expenditure.

The [reality-ripple measurement design](notes/reality_ripple_measurement_design.md)
joins the Cayley-Dickson sources to the planned atlas, walk, rank-sector, and
joint-error views. The [current campaign preparation](../results/ripple/CAMPAIGN_PREPARATION.md)
qualifies the correction, ripple and rank cases against one audited runtime
source closure; reviewed
merge, fresh live bindings and independent family execution admission remain
gates. The completed folded-QPE archive supplies the measured evidence.
The [de Marrais source note](notes/math-0403113.md) records
the bounded box-kite reading and the local PDF identity. A
[version-bound open_gororoba evidence contract](sources/open_gororoba/README.md)
retains the sister repository's algebraic corrections with its provenance
and license text.

The [formal-evidence dependency plan](notes/formal_evidence_dependencies.md)
connects faithful fold repairs, checked arithmetic, prospective count
certificates, tomography and adaptive stopping to explicit assumptions.
Its [Rocq replay bundle](evidence/formal_certificates/README.md) retains
the new scalar obstruction and rational/real terminal-channel certificates.
The [migration validation](VALIDATION.json) preserves the earlier 50-source
snapshot; the Howard note adds the 51st source and records its separate audit.

| note | paper | (a) | (b) | (c) |
|---|---|---|---|---|
| s41567-023-02340-9 | Glick et al., Covariant quantum kernels for data with group structure, Nat. Phys. 20, 479 (2024); preprint arXiv:2105.03406 | medium | low | low |
| [2102.01682](notes/2102.01682.md) | Corcoles et al., Exploiting dynamic quantum circuits in a quantum algorithm with superconducting qubits, PRL 127, 100501 (2021) | high | none | low |
| 2411.05760 | Deshpande et al., Dynamic parameterized quantum circuits | low | none | none |
| s42254-024-00770-9 | Abbas et al., Challenges and opportunities in quantum optimization, Nat. Rev. Phys. 6, 718 (2024); preprint arXiv:2312.02279 | high | none | low |
| 2501.09702 | Yu et al., Quantum-centric algorithm for sample-based Krylov diagonalization (ibm_fez) | medium | none | none |
| 2507.08088 | Cobos et al., Real-time dynamics in a (2+1)-D gauge theory (ibm_kingston, ibm_marrakesh) | high | none | low |
| 2505.22629 | Chen et al., Disambiguating Pauli noise in quantum computers, PRX Quantum 7, 033045 (2026) | high | none | low |
| 2509.18259 | Pokharel et al., Order from chaos with adaptive circuits on quantum hardware (ibm_fez) | medium | none | low |
| 2505.15917 | Gidney, How to factor 2048 bit RSA integers with less than a million noisy qubits | none | none | high |
| 1207.4230 | Kirshtein, Multiplication groups and inner mapping groups of Cayley-Dickson loops (2012) | none | high | none |
| 0905.2987 | Biss, Christensen, Dugger, Isaksen, Eigentheory of Cayley-Dickson algebras (2009) | none | high | none |
| math-0511691 | Biss, Dugger, Isaksen, Large annihilators in Cayley-Dickson algebras (2005) | none | high | none |
| math-0702075 | Biss, Christensen, Dugger, Isaksen, Large annihilators in Cayley-Dickson algebras II (2007) | none | high | none |
| math-0512517 | Moreno, Constructing zero divisors in the higher dimensional Cayley-Dickson algebras (2005) | none | high | none |
| 2411.18881 | Reggiani, The geometry of sedenion zero divisors (2024) | none | high | none |
| 2512.13002 | Koebisu, Determinant factorization for left multiplication in the sedenions (v2, 2026) | none | high | none |
| 1602.02843 | Bales, Periodicity of the Cayley-Dickson twists (2016) | none | high | none |
| 1602.02317 | Bales, An alternate Cayley-Dickson product (2016) | none | medium | none |
| math-9802116 | Albuquerque and Majid, Quasialgebra structure of the octonions (1998) | none | high | none |
| 0811.3208 | Roetteler, Quantum algorithms for highly non-linear Boolean functions (2008) | none | medium | none |
| 0911.4724 | Roetteler, Hidden shift for quadratics and functions of large Gowers norm (2009) | none | medium | none |
| 1103.3017 | Gavinsky, Roetteler, Roland, Quantum algorithm for the Boolean hidden shift problem (2011) | none | medium | none |
| quant-ph-0703195 | Decker and Wocjan, Hidden quadratic and cubic polynomial function graphs (2007) | none | low | none |
| 1107.2189 | Decker, Ivanyos, Santha, Wocjan, Hidden symmetry subgroup problems (2011) | none | low | none |
| 2202.08688 | Kaufman and Minzer, Improved optimal testing results from global hypercontractivity (2022) | none | medium | none |
| elkies-2013-m256 | Elkies, Math 256x course notes on error-correcting codes (2013) | none | medium | none |
| pmc-4957665-nonlinearity-measures | Boyar, Find, Peralta, On various nonlinearity measures for Boolean functions | none | medium | none |
| quant-ph-9511007 | Griffiths and Niu, Semiclassical Fourier transform for quantum computation (1996) | medium | none | high |
| 1111.4147 | Martin-Lopez et al., Shor's algorithm with qubit recycling (2012) | medium | none | high |
| 2102.05321 | Niu and Todri-Sanial, Multi-programming for NISQ quantum computing (QuMC) | high | none | none |
| [das-2019-multiprogramming](notes/das-2019-multiprogramming.md) | Das et al., A Case for Multi-Programming Quantum Computers (MICRO 2019) | high | none | low |
| [2112.07091](notes/2112.07091.md) | Ohkura, Satoh, Van Meter, Simultaneous execution of quantum circuits (palloq) | high | none | low |
| [2109.01714](notes/2109.01714.md) | Resch et al., Accelerating Variational Quantum Algorithms Using Circuit Concurrency (CQCS) | high | none | low |
| [2112.00387](notes/2112.00387.md) | Niu and Todri-Sanial, How Parallel Circuit Execution Can Be Useful for NISQ Computing? (QuCP) | high | none | low |
| [1204.6308](notes/1204.6308.md) | Gambetta et al., Characterization of addressability by simultaneous randomized benchmarking (2012) | high | none | low |
| [1810.08240](notes/1810.08240.md) | Howard et al., Time-uniform confidence sequences (2021 journal; inspected v9, 2022) | high | none | low |
| [1810.05651](notes/1810.05651.md) | Rudinger et al., Probing Context-Dependent Errors in Quantum Processors (2019) | high | none | low |
| [1908.09855](notes/1908.09855.md) | Sarovar et al., Detecting crosstalk errors in quantum information processors (2020) | high | none | low |
| [1907.13608](notes/1907.13608.md) | Proctor et al., Detecting and tracking drift in quantum information processors (2020) | high | none | low |
| [1504.07999](notes/1504.07999.md) | Bremner, Montanaro, Shepherd, Average-case complexity versus approximate simulation of commuting quantum computations (2016) | low | medium | low |
| 1904.00633 | Kissinger and Meijer-van de Griend, CNOT circuit extraction for topologically-constrained quantum memories (2019) | medium | none | medium |
| 1806.01838 | Gilyen, Su, Low, Wiebe, Quantum singular value transformation and beyond (2018) | low | low | none |
| 1811.08580 | Freedman, Shokrian-Zini, Wang, Quantum computing with octonions (2018) | none | medium | none |
| levratti-2026-fano-css | Levratti, Fano duality, projective orthogonality and the CSS bridge (author-hosted, 2026) | none | high | none |
| levratti-2026-active-stabilizers | Levratti, Active stabilizers in Reed-Muller CSS codes from Cayley-Dickson zero-divisors (author-hosted manuscript, 2026) | none | low | none |
| [2102.01682](notes/2102.01682.md) | Corcoles et al., Dynamic phase estimation on superconducting qubits, PRL 127, 100501 (2021) | high | indirect | limited |
| [2608.08232](notes/2608.08232.md) | Koebisu, Dimension-32 determinant factorization and rank-stratum Question 4 (2026 preprint) | none | high | none |
| [2608.26893](notes/2608.26893.md) | Zhilina, Doubly alternative zero divisors (2023 journal; 2026 arXiv posting) | none | high | none |
| [2608.28176](notes/2608.28176.md) | Zhilina, Orthogonality graphs Part I (2021 journal; 2026 arXiv posting) | none | high | none |
| [2608.28163](notes/2608.28163.md) | Zhilina, Orthogonality graphs Part II (2021 journal; 2026 arXiv posting) | none | high | none |
| [2103.03008](notes/2103.03008.md) | Rudinger et al., Quantum-instrument GST (2021 preprint, 2022 journal) | high | none | none |
| [2602.03938](notes/2602.03938.md) | Wysocki et al., Interpretable mid-circuit measurement errors (2026 preprint) | high | none | none |
| [Coste](notes/coste-semialgebraic-geometry.md) | Semialgebraic geometry: compatible triangulation, Hardt triviality and local conic structure (2002) | none | method | none |
| [Hatcher](notes/hatcher-algebraic-topology.md) | Algebraic Topology, Chapter 0, attachment and quotient hypotheses | none | method | none |

The [parallel-experiment synthesis](notes/quantum_experiment_parallelism.md)
connects these sources to fixed and varied companions, patch/time blocking,
joint-shot inference, billed usage, and IQP claim boundaries. The
[design and execution documentation note](notes/quantum_experiment_design_sources.md)
records NIST, Qiskit and IBM sources with capture hashes. The two retained parallel-experiment
PDFs have [replayable checksums](parallel_experiment_pdfs.sha256); direct,
version-pinned retrieval links and reading scopes live in each paper note.
The remaining parallel-experiment papers retain direct URLs, hashes, and
reading notes as external sources. The Das notice expressly requires permission
for server redistribution; an arXiv-only grant also differs from permission to
rehost a PDF. The source registry records each individual decision.

Every note from the prior-work review labels each overlapping repository
claim as known theorem reproduced, new proof or formalization, new
implementation or measurement, or candidate new result.
[prior_work_synthesis.md](notes/prior_work_synthesis.md) owns current status
and experiment priority. The notes/handbacks/ directory preserves the
delegates' original findings and disclosures with explicit current-status
links. Its [A] labels identify the original scratch checks; later retained
gates carry their own evidence links.

The per-paper notes own current citations, hypotheses, theorem locators, and
typographical corrections: [BDI 2005](notes/math-0511691.md),
[BCDI 2007](notes/math-0702075.md), [BCDI 2009](notes/0905.2987.md), and
[Reggiani 2024](notes/2411.18881.md). The
[shared sparse census](notes/cayley_dickson_sparse_census.md) owns count
conventions and routes the dimension-32 count to its canonical exact JSON.

Two notes survey the sister repository rather than a paper:

- notes/open_gororoba_survey.md maps open_gororoba at fe668020: its Rocq
  corpus graded proven, tested, or asserted; its dimension ladder from 16
  through 4096; its butterfly, Walsh, and zero-divisor chunking structure; and
  the candidate connections to factoring, with category errors named.
- notes/open_gororoba_survey_deep_notes.md holds the evidence trail behind every
  number: read-only commands, Rocq axiom scans, the GF(2) form of the sign
  recursion and its circuit, closed forms for the defect and edge counts, and
  replay scripts.

gororoba_quantum/FACTORING_NOTES.md re-checks the sign recursion and the
defect count independently.

The first eight quantum and factoring papers in the table contain no Cayley-Dickson,
octonion, sedenion, zero-divisor, or nonassociative content. The
[annihilator source ledger](notes/cayley_dickson_annihilator_sources.md) and
[rank-topology source ledger](notes/cayley_dickson_rank_topology_sources.md)
remain historical implementation-audit snapshots. Their source retrievals,
theorem applications, and local derivations retain the provenance of the
corresponding implementation. Current per-paper notes consolidate overlapping
paper facts; the snapshots retain their original bytes because execution
manifests bind their hashes.

| Snapshot | Source revision | SHA-256 | Manifest binding |
| --- | --- | --- | --- |
| Annihilator ledger | `bd5d6b2e97165d560df588084098056fce5a2fd1` | `02f4cf4fb7dee46e5fd87052cf5d4c0a81087c848948bad17af246b764f080d5` | [topology verification](../results/hw_estimate/cayley_dickson_topology_verification.json), `source_sha256` |
| Rank-topology ledger | `f4eda251822b380d695564fcf39a7a9e528f994e` | `bd478146132ddade390396b5b330f3a08091b2ebae83d9bacab1d23644756a30` | [rank verification](../results/hw_estimate/rank_topology_verification.json), `documentation_sha256` |

[FACTORING_NOTES.md](../gororoba_quantum/FACTORING_NOTES.md) carries the factoring
analysis.


The [proof and experiment dependency synthesis](notes/research_proof_experiment_dependencies.md)
connects curve realization, exact matrix certificates, circuit/instrument
semantics, tomography, stopping and full-workload allocation to primary sources.
The [field-model opportunity map](notes/vacuum_field_run_opportunities.md)
separates physical device-noise sensing, encoded field simulation, and calibrated
force/radiation measurements. Its [finite CPU reference](evidence/vacuum_models/README.md)
retains cutoff, coherence, synthesis and SPAM-identifiability checks; future
hardware cases retain their independent admission gates.

| Additional source group | Notes and application |
| --- | --- |
| Curve realization | [Basu--Roy](notes/1803.00505.md), [Greenberg](notes/greenberg-henselian-lifting.md), expanded [BCDI II](notes/math-0702075.md) and [Coste](notes/coste-semialgebraic-geometry.md); real-arc and lifting hypotheses |
| Formal interfaces | [SQIR/VOQC](notes/sqir-voqc-proof-interfaces.md), [MathComp/CoqEAL](notes/mathcomp-coqeal-matrix-certificates.md), [CoqInterval](notes/coqinterval-certified-enclosures.md); checked semantics, rank witnesses and numerical enclosures |
| Identification and resource design | [GST](notes/2009.07301.md), expanded [QILGST](notes/2103.03008.md), [optimal design](notes/quant-ph-0411093.md), [SHOALS](notes/2201.13438.md), [shadows](notes/2002.08953.md); gauge, measurement choice and complete costs |
| Device noise | [Schoelkopf](notes/cond-mat-0210247.md), [Clerk](notes/0810.4729.md), [Jin](notes/1412.2772.md); spectral convention, residual populations and calibrated inference |
| Encoded field models | [Digital optics](notes/1909.04408.md), [Gaussian coherence](notes/1610.03272.md), [lattice Casimir](notes/2105.02032.md), [Gaussian simulation](notes/quant-ph-0109047.md), [collision models](notes/2106.11974.md); encoding, model bias and classical baselines |
| Physical interpretation and execution | [Physical DCE](notes/1105.4714.md), [real-material Casimir](notes/0902.4022.md), [circuit QED](notes/2005.12667.md), [IBM policy](notes/ibm_fractional_execution_sources.md); apparatus, observable and runtime boundaries |
| Vacuum, dark sector and negative energy | [ALPS II](notes/2512.14110.md), [Dark SRF](notes/2510.02427.md), [dielectric haloscope](notes/2503.23354.md), [atom interferometry](notes/2511.09750.md), [LZ](notes/2609.02823.md), [DES Y6](notes/2601.14559.md), [worldline DCE](notes/2604.13237.md), [magnetic-fluid Casimir](notes/2601.00483.md), [quantum inequalities](notes/gr-qc-9607003.md), [QET theory](notes/1002.0200.md) and [hardware](notes/2301.02666.md), [journal and IBM pages](notes/casimir-dark-sector-web-sources.md); exclusions, nuisances and energy accounting before any new-physics reading |
| Cayley-Dickson associator structure | [defect census](notes/cd_associator_defect_census.md), [Wilmot](notes/2505.11747.md), [Kirshtein](notes/1207.4230.md); closed forms, subspace types and the sufficient conditions of Lemma 3 |
| External algebra packages | [package index](notes/packages/README.md): measured relation of eight hypercomplex packages to cd_core, independence, licenses and correct use |
| Review reconciliation | [QPU, Cayley-Dickson and vacuum review claims](notes/qpu_vacuum_cd_review_reconciliation.md); each claim with its status and settling artifact |

## Historical action items and current status

The list below records the source review's original proposals. The
[execution roadmap](../gororoba_quantum/QPU_EXECUTION_ROADMAP.md) owns live
completion status. The folded mechanism ladder completes in two retained jobs;
native static mitigation and coherent/dynamic option separation exist in the
runner. Dynamic DD/twirling compatibility, N21 admission, initialization-delay
qualification, and fresh hardware approval retain their documented gates.
The [decision note](notes/model_discrimination_optimizer.md) supersedes any
historical ordering that places a broad atlas before model discrimination.

The notes were written against the dense design B: 224 CZ, P_zd = 0.319. The
structural compile in gororoba_quantum/select_lcu.py supersedes it at 42 to 46
CZ, so the shot and gamma budgets the notes derive from 224 CZ overstate the
cost.

In place in `live_run.py`:
- Live layout scoring from calibration: ESP over gate and readout errors on
  every candidate (2509.18259 d1, s42254 d1).
- Per-run calibration record: backend medians, exclusions, timestamps, chosen
  layouts, and scheduled durations in results/live/ (s41567 d1, 2507.08088 d5,
  2509.18259 d2).
- Backend selection across the three reachable devices from live state
  (s42254 d4).
- Historical comparison through target_history at execution time (2501.09702
  d1).

Open, by task:
- Mirror-circuit ODR, one calibration per witness, at 16,384 or more shots
  (2507.08088 d1-d2).
- Twirling and dynamical decoupling through the client-side Sampler options,
  XpXm or XY4, DD on and off (2507.08088 d4, s41567 d2, s42254 d2).
- Dephased and depolarized null models, plus the uniform-random null
  (2509.18259 d3, 2501.09702 d2).
- A coherence factor exp(-t/T2) in the layout score (2509.18259 d1).
- At least three disjoint layouts per witness, with shot, instance, and layout
  variance separated (2507.08088 d3, 2509.18259 d4).
- Dynamic-circuit capability and feed-forward latency on each backend
  (2411.05760 d4), the precondition for the semiclassical-QFT test in
  FACTORING_NOTES.md.
- PEC: count distinct CZ layers and compute gamma before committing shots. The
  paper's learning settings take 740 to 1340 s at about 1 ms per shot, more
  than the 600 s monthly budget (2505.22629 d1-d5).
- Reproduce Gidney Table 5 at n = 2048 from the Zenodo code, and keep the Eq.
  22 deviation bound as a unit test (2505.15917 d2-d3; not run).
