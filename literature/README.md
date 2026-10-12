# Literature notes

One note per paper under notes/. Each note:
- carries the citation, the URL that served the PDF, and its sha256;
- tags every statement as from-paper or inference;
- rates relevance to (a) calibration-aware compilation on IBM hardware,
  (b) Cayley-Dickson structure, and (c) factoring resource estimates.

The PDFs stay local under literature/pdf/, which is git-ignored. The Nature
articles are paywalled, so their notes read the arXiv preprints, which differ
from the version of record. Each of those notes says so at the top.

| note | paper | (a) | (b) | (c) |
|---|---|---|---|---|
| s41567-023-02340-9 | Glick et al., Covariant quantum kernels for data with group structure, Nat. Phys. 20, 479 (2024); preprint arXiv:2105.03406 | medium | low | low |
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
| [1810.05651](notes/1810.05651.md) | Rudinger et al., Probing Context-Dependent Errors in Quantum Processors (2019) | high | none | low |
| [1908.09855](notes/1908.09855.md) | Sarovar et al., Detecting crosstalk errors in quantum information processors (2020) | high | none | low |
| [1907.13608](notes/1907.13608.md) | Proctor et al., Detecting and tracking drift in quantum information processors (2020) | high | none | low |
| [1504.07999](notes/1504.07999.md) | Bremner, Montanaro, Shepherd, Average-case complexity versus approximate simulation of commuting quantum computations (2016) | low | medium | low |
| 1904.00633 | Kissinger and Meijer-van de Griend, CNOT circuit extraction for topologically-constrained quantum memories (2019) | medium | none | medium |
| 1806.01838 | Gilyen, Su, Low, Wiebe, Quantum singular value transformation and beyond (2018) | low | low | none |
| 1811.08580 | Freedman, Shokrian-Zini, Wang, Quantum computing with octonions (2018) | none | medium | none |
| levratti-2026-fano-css | Levratti, Fano duality, projective orthogonality and the CSS bridge (author-hosted, 2026) | none | high | none |
| levratti-2026-active-stabilizers | Levratti, Active stabilizers in Reed-Muller CSS codes from Cayley-Dickson zero-divisors (author-hosted page, 2026) | none | low | none |

The [parallel-experiment synthesis](notes/quantum_experiment_parallelism.md)
connects these sources to fixed and varied companions, patch/time blocking,
joint-shot inference, billed usage, and IQP claim boundaries. The
[design and execution documentation note](notes/quantum_experiment_design_sources.md)
records NIST, Qiskit and IBM sources with capture hashes. The ten-paper local
PDF set has [replayable checksums](parallel_experiment_pdfs.sha256); direct,
version-pinned retrieval links and reading scopes live in each paper note.
The Das paper uses the verified author-laboratory PDF URL and a content hash.

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

## Action items against the repository

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
