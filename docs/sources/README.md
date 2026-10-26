# Sources and research notes

[INDEX.md](../INDEX.md) distinguishes hosted papers from ignored local reading copies
and links every PDF source to its note and hosting evidence.

One note per paper under [notes/papers/](../notes/papers/); a note that a retained record
names by path stays in [notes/](../notes/). Each note:
- carries the citation, the URL that served the PDF, and its sha256;
- tags every statement as from-paper or inference;
- rates relevance to (a) calibration-aware compilation on IBM hardware,
  (b) Cayley-Dickson structure, and (c) factoring resource estimates.

The canonical source library lives under `docs/`: paper descriptions in
`notes/`, retained primary PDFs in `pdf/`, and repeatable research checks in
`evidence/`. [SOURCES.json](../SOURCES.json) records each PDF's URL, SHA-256,
byte count, page count, acquisition status, owning note, and exact-version
license evidence. The library publishes 44 licensed PDFs and two aliases;
186 external sources retain citations and optional ignored local reading copies.
Five licensed original software archives retain upstream notices under
`source_archives/`; the verifier checks their inspected members and licenses.
[PDF_SHA256SUMS](../PDF_SHA256SUMS) verifies the published PDF set from the
repository root with `sha256sum -c docs/PDF_SHA256SUMS`.

The `literature -> docs` compatibility link preserves historical paths used
in source comments, verification manifests, and retained parallel-experiment checksum
paths. Both names identify the same retained files. New browser links use `docs/`, since
GitHub displays a directory symlink as a link blob. The two implementation-audit
ledgers and the two mathematical guides named by their manifests retain their original
bytes. Per-paper notes retain the scope and dates of their original readings;
older references to an ignored/local cache describe that acquisition history.
The registry records the retained copies and their fresh hash checks.

Most Nature articles are paywalled. The retained arXiv preprints remain distinct
from the versions of record, including the two explicitly named PDF aliases.
Two open-access Nature-family versions of record (s41586-026-10423-9 and
s41567-026-03466-2) carry article-level CC BY 4.0 grants and are retained.
HTML-only sources and their reading scopes appear in the registry and notes.
Explicit CC BY 4.0 or CC0 permission supports the published PDFs. ArXiv-only
hosting grants, personal-copy permissions, and sources without an established
rehosting grant receive external records and ignored local copies under
`local_source_cache/`. The registry retains first-party evidence URLs and hashes.
Downloaded documents retain their authors' notices and licenses; repository
licensing does not relabel third-party papers. The source verifier checks local
copies when present and permits a fresh checkout without those optional files.
[`scripts/fetch_source_cache.py`](../../scripts/fetch_source_cache.py) restores
those copies from the registered URLs or from a checkout of the owner's private
gororoba-quantum-documents repository, which also holds their Markdown
transcriptions, and admits a file only when its size and SHA-256 match the
registry.

The [Cayley-Dickson survey at dimension 16 and above](cayley-dickson-2n-ion-survey.md) records every candidate source and its disposition.

The [coordinated research roadmap](../RESEARCH_ROADMAP.md) consolidates the
cumulative objectives, verified results, ownership, ordering, and remaining
proof and hardware gates.

The [rank-stratum research decomposition](../notes/koebisu_rank_stratum_research.md)
connects Koebisu's Question 4, exact rank predicates, local kernel reductions,
attachment geometry, and bounded hardware measurements. The
[folding and Rocq audit](../notes/open_gororoba_folding_proofs.md) identifies which
dimensional reductions preserve the algebraic information and which formal
statements the sister repository actually proves. The
[model-discrimination decision](../notes/model_discrimination_optimizer.md)
sets the hardware priority before broad atlas expenditure.

The [reality-ripple measurement design](../notes/reality_ripple_measurement_design.md)
joins the Cayley-Dickson sources to the planned atlas, walk, rank-sector, and
joint-error views. The [current campaign preparation](../../results/ripple/CAMPAIGN_PREPARATION.md)
qualifies the correction, ripple and rank cases against one audited runtime
source closure; reviewed
merge, fresh live bindings and independent family execution admission remain
gates. The completed folded-QPE archive supplies the measured evidence.
The [de Marrais source note](../notes/math-0403113.md) records
the bounded box-kite reading and the local PDF identity. A
[version-bound open_gororoba evidence contract](open_gororoba/README.md)
retains the sister repository's algebraic corrections with its provenance
and license text.

The [formal-evidence dependency plan](../notes/formal_evidence_dependencies.md)
connects faithful fold repairs, checked arithmetic, prospective count
certificates, tomography and adaptive stopping to explicit assumptions.
Its [Rocq replay bundle](../evidence/formal_certificates/README.md) retains
the new scalar obstruction and rational/real terminal-channel certificates.
The [migration validation](../VALIDATION.json) preserves the earlier 50-source
snapshot; the Howard note adds the 51st source and records its separate audit.

| note | paper | (a) | (b) | (c) |
|---|---|---|---|---|
| s41567-023-02340-9 | Glick et al., Covariant quantum kernels for data with group structure, Nat. Phys. 20, 479 (2024); preprint arXiv:2105.03406 | medium | low | low |
| [s41586-026-10423-9](../notes/papers/s41586-026-10423-9.md) | Matsumoto et al., Two-qubit logic and teleportation with mobile spin qubits in silicon, Nature 653, 391 (2026) | low | none | none |
| [s41567-026-03466-2](../notes/papers/s41567-026-03466-2.md) | Wu et al., Simultaneous high-fidelity single-qubit gates in a spin qubit array, Nat. Phys. (2026) | low | none | none |
| [2102.01682](../notes/2102.01682.md) | Corcoles et al., Exploiting dynamic quantum circuits in a quantum algorithm with superconducting qubits, PRL 127, 100501 (2021) | high | none | low |
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
| mckay-hadamard-matrices | McKay, Hadamard matrices: equivalence-class representatives (combinatorial data page) | none | medium | none |
| schafer-1954-cayley-dickson-flexible | Schafer, On the algebras formed by the Cayley-Dickson process (1954) | none | medium | none |
| [2205.07986](../notes/papers/2205.07986.md) | Ren and Zhao, The explicit twisted group algebra structure of the Cayley-Dickson algebra (2023) | none | high | none |
| [1003.0429](../notes/papers/1003.0429.md) | Morier-Genoud and Ovsienko, A series of algebras generalizing the octonions and Hurwitz-Radon identity (2011) | none | medium | none |
| [2512.07210](../notes/papers/2512.07210.md) | Wilmot, Automorphisms of Sedenions (2026) | none | high | none |
| [2609.10569](../notes/papers/2609.10569.md) | Gresnigt, Sedenions, Clifford Algebras, and Three Fermion Generations: A Focused Review (2026) | none | medium | none |
| [1907.07024](../notes/papers/1907.07024.md) | Heikoop, Nunez Ponasso, O Cathain and Pugmire, Morphisms of Skew Hadamard Matrices (2020) | none | low | none |
| [ocathain-2012-nonaffine-hadamard](../notes/papers/ocathain-2012-nonaffine-hadamard.md) | O Cathain, Difference sets and doubly transitive actions on Hadamard matrices, J. Combin. Theory Ser. A 119, 1235 (2012) | none | medium | none |
| [kivunge-2013-sign-matrices-2n-ons](../notes/papers/kivunge-2013-sign-matrices-2n-ons.md) | Kivunge, Sign matrices for frames of 2^n-ons under Smith-Conway and Cayley-Dickson multiplications (conference slides, 2013) | none | high | none |
| [0709.1447](../notes/papers/0709.1447.md) | Luhn, Nasri and Ramond, Simple finite non-abelian flavor groups, J. Math. Phys. 48, 123519 (2007) | none | low | none |
| [2007.01808](../notes/papers/2007.01808.md) | Ziller, On differences between consecutive numbers coprime to primorials (2020) | none | none | none |
| [erdos-854-consecutive-coprime-gaps](../notes/papers/erdos-854-consecutive-coprime-gaps.md) | Bloom, Erdos Problem 854: missing even gaps between consecutive integers coprime to a primorial (web record) | none | none | none |
| [1107.1375](../notes/papers/1107.1375.md) | Bales, Cayley-Dickson and Clifford algebras as twisted group algebras (2003; arXiv 2011) | none | medium | none |
| [2103.12805](../notes/papers/2103.12805.md) | Flaut and Boboescu, A twisted group algebra structure for an algebra obtained by the Cayley-Dickson process (2021) | none | medium | none |
| [0804.3416](../notes/papers/0804.3416.md) | de Marrais 2008: Voyage by Catamaran, zero-divisor ensembles of the 2^N-ions | none | high | none |
| [0907.2047](../notes/papers/0907.2047.md) | Cawagas et al. 2009: subalgebra structure of the 32-dimensional Cayley-Dickson algebra | none | high | none |
| [math-0404395](../notes/papers/math-0404395.md) | Moreno 2004: alternative elements in the Cayley-Dickson algebras (arXiv math/0404395) | none | high | none |
| [math-0512516](../notes/papers/math-0512516.md) | Moreno 2005: monomorphisms between Cayley-Dickson algebras (arXiv math/0512516) | none | medium | none |
| [math-0405424](../notes/papers/math-0405424.md) | Moreno 2004: the exponential map on the Cayley-Dickson algebras (arXiv math/0405424) | none | medium | none |
| [math-0404172](../notes/papers/math-0404172.md) | Moreno 2004: the Hopf construction map in higher dimensions (arXiv math/0404172) | none | medium | none |
| [1102.5151](../notes/papers/1102.5151.md) | Kirshtein 2012: automorphism groups of Cayley-Dickson loops | none | high | none |
| [1405.6888](../notes/papers/1405.6888.md) | Saniga, Holweck and Pracna 2014: Cayley-Dickson algebras and finite geometry | none | medium | none |
| [2606.27798](../notes/papers/2606.27798.md) | Aryapoor, Back and Pautrel 2026: involutions in the Cayley-Dickson construction | none | medium | none |
| [2609.11588](../notes/papers/2609.11588.md) | Lemley 2026: quasilinear multiplication in the real Cayley-Dickson tower (arXiv 2609.11588) | none | high | none |
| [2603.20495](../notes/papers/2603.20495.md) | Chapman and Levin 2026: central products of Cayley-Dickson loops (arXiv 2603.20495) | none | high | none |
| [2501.00123](../notes/papers/2501.00123.md) | Chapman, Levin, Vishne and Zaninelli 2024: loops with involution and the Cayley-Dickson doubling process | none | high | none |
| [1707.07318](../notes/papers/1707.07318.md) | Bales: the Cayley-Dickson doubling products (arXiv 1707.07318) | none | high | none |
| [1107.1301](../notes/papers/1107.1301.md) | Bales 2011: a catalog of Cayley-Dickson-like products (arXiv 1107.1301) | none | high | none |
| [hep-th-0601033](../notes/papers/hep-th-0601033.md) | Kuwata, Fujii and Nakashima 2006: alternativity and reciprocity in the Cayley-Dickson algebra (arXiv hep-th/0601033) | none | medium | none |
| [2505.06011](../notes/papers/2505.06011.md) | Wilmot 2025: exceptional Lie algebra G2 and non-associative algebras from Clifford algebra (arXiv 2505.06011) | none | medium | none |
| [2205.05605](../notes/papers/2205.05605.md) | Chapman, Guterman, Vishkautsan and Zhilina 2022: roots and critical points of polynomials over Cayley-Dickson algebras (arXiv 2205.05605) | none | medium | none |
| [2512.22134](../notes/papers/2512.22134.md) | Gazeau 2026: a mnemonic matrix rule for octonionic multiplication and its extension to the Cayley-Dickson tower (arXiv 2512.22134) | none | medium | none |
| [brown-1967-generalized-cayley-dickson](../notes/papers/brown-1967-generalized-cayley-dickson.md) | R. B. Brown 1967: on generalized Cayley-Dickson algebras (Pacific J. Math. 20) | none | high | none |
| [chan-dokovic-2006-sedenion-subalgebras](../notes/papers/chan-dokovic-2006-sedenion-subalgebras.md) | Chan and Dokovic 2006: conjugacy classes of subalgebras of the real sedenions | none | high | none |
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
| [das-2019-multiprogramming](../notes/papers/das-2019-multiprogramming.md) | Das et al., A Case for Multi-Programming Quantum Computers (MICRO 2019) | high | none | low |
| [2112.07091](../notes/papers/2112.07091.md) | Ohkura, Satoh, Van Meter, Simultaneous execution of quantum circuits (palloq) | high | none | low |
| [2109.01714](../notes/papers/2109.01714.md) | Resch et al., Accelerating Variational Quantum Algorithms Using Circuit Concurrency (CQCS) | high | none | low |
| [2112.00387](../notes/papers/2112.00387.md) | Niu and Todri-Sanial, How Parallel Circuit Execution Can Be Useful for NISQ Computing? (QuCP) | high | none | low |
| [1204.6308](../notes/papers/1204.6308.md) | Gambetta et al., Characterization of addressability by simultaneous randomized benchmarking (2012) | high | none | low |
| [1810.08240](../notes/papers/1810.08240.md) | Howard et al., Time-uniform confidence sequences (2021 journal; inspected v9, 2022) | high | none | low |
| [1810.05651](../notes/papers/1810.05651.md) | Rudinger et al., Probing Context-Dependent Errors in Quantum Processors (2019) | high | none | low |
| [1908.09855](../notes/papers/1908.09855.md) | Sarovar et al., Detecting crosstalk errors in quantum information processors (2020) | high | none | low |
| [1907.13608](../notes/papers/1907.13608.md) | Proctor et al., Detecting and tracking drift in quantum information processors (2020) | high | none | low |
| [1504.07999](../notes/papers/1504.07999.md) | Bremner, Montanaro, Shepherd, Average-case complexity versus approximate simulation of commuting quantum computations (2016) | low | medium | low |
| 1904.00633 | Kissinger and Meijer-van de Griend, CNOT circuit extraction for topologically-constrained quantum memories (2019) | medium | none | medium |
| 1806.01838 | Gilyen, Su, Low, Wiebe, Quantum singular value transformation and beyond (2018) | low | low | none |
| 1811.08580 | Freedman, Shokrian-Zini, Wang, Quantum computing with octonions (2018) | none | medium | none |
| levratti-2026-fano-css | Levratti, Fano duality, projective orthogonality and the CSS bridge (author-hosted, 2026) | none | high | none |
| levratti-2026-active-stabilizers | Levratti, Active stabilizers in Reed-Muller CSS codes from Cayley-Dickson zero-divisors (author-hosted manuscript, 2026) | none | low | none |
| [2102.01682](../notes/2102.01682.md) | Corcoles et al., Dynamic phase estimation on superconducting qubits, PRL 127, 100501 (2021) | high | indirect | limited |
| [2608.08232](../notes/2608.08232.md) | Koebisu, Dimension-32 determinant factorization and rank-stratum Question 4 (2026 preprint) | none | high | none |
| [2608.26893](../notes/2608.26893.md) | Zhilina, Doubly alternative zero divisors (2023 journal; 2026 arXiv posting) | none | high | none |
| [2608.28176](../notes/papers/2608.28176.md) | Zhilina, Orthogonality graphs Part I (2021 journal; 2026 arXiv posting) | none | high | none |
| [2608.28163](../notes/papers/2608.28163.md) | Zhilina, Orthogonality graphs Part II (2021 journal; 2026 arXiv posting) | none | high | none |
| [2608.26890](../notes/papers/2608.26890.md) | Zhilina, Diameter of the commutativity graph of the real sedenions (2024 journal; 2026 arXiv posting) | none | high | none |
| [guterman-zhilina-2023-split-algebras](../notes/papers/guterman-zhilina-2023-split-algebras.md) | Guterman and Zhilina, Cayley-Dickson split-algebras: doubly alternative zero divisors and relation graphs (J. Math. Sci. 2023; abstract only, no open copy) | none | low | none |
| [cawagas-2004-sedenion-structure](../notes/papers/cawagas-2004-sedenion-structure.md) | Cawagas, On the structure and zero divisors of the Cayley-Dickson sedenion algebra (DMGAA 2004; journal host unreachable, metadata only) | none | medium | none |
| [2103.03008](../notes/papers/2103.03008.md) | Rudinger et al., Quantum-instrument GST (2021 preprint, 2022 journal) | high | none | none |
| [2602.03938](../notes/papers/2602.03938.md) | Wysocki et al., Interpretable mid-circuit measurement errors (2026 preprint) | high | none | none |
| [Coste](../notes/coste-semialgebraic-geometry.md) | Semialgebraic geometry: compatible triangulation, Hardt triviality and local conic structure (2002) | none | method | none |
| [Hatcher](../notes/hatcher-algebraic-topology.md) | Algebraic Topology, Chapter 0, attachment and quotient hypotheses | none | method | none |
| [Carlstrom](../notes/wheels-carlstrom.md) | Wheels: total division by zero, the wheel of fractions and its axioms (2001 report; MSCS 2004) | none | method | none |
| [1903.02492](../notes/papers/1903.02492.md) | Rol et al., Net Zero bipolar flux-pulse CZ gate (2019) | high | medium | low |
| [2008.07411](../notes/papers/2008.07411.md) | Negirneac et al., Sudden Net Zero CZ gate (PRL 126, 220502, 2021) | high | medium | low |
| [2102.13071](../notes/papers/2102.13071.md) | Marques et al., logical-qubit operations on a Surface-7 transmon processor (Nat. Phys. 18, 80, 2022) | medium | low | low |
| [1708.07677](../notes/papers/1708.07677.md) | Fu et al., QuMA experimental control microarchitecture (2017) | medium | none | none |
| [1808.02449](../notes/papers/1808.02449.md) | Fu et al., eQASM executable QISA with explicit timing (HPCA 2019) | medium | none | none |
| [2310.01120](../notes/papers/2310.01120.md) | van der Schoot et al., quantum metrics on Quantum Inspire Starmon-5 (2023) | high | none | medium |
| [1809.01043](../notes/papers/1809.01043.md) | Klimov et al., T1 fluctuations from two-level-system spectral diffusion (PRL 121, 090502, 2018) | medium | medium | none |
| [1901.05352](../notes/papers/1901.05352.md) | Schloer et al., low-frequency burst noise from single fluctuators in a transmon (PRL 123, 190502, 2019) | medium | medium | none |
| [1903.01043](../notes/papers/1903.01043.md) | Sung et al., non-Gaussian noise spectroscopy with a flux qubit sensor (Nat. Commun. 10, 3715, 2019) | low | medium | none |
| [2006.14044](../notes/papers/2006.14044.md) | Bravyi et al., tensor-product and CTMP readout-error mitigation (PRA 103, 042605, 2021) | medium | high | low |
| [2108.12518](../notes/papers/2108.12518.md) | Nation et al., matrix-free measurement mitigation (M3; PRX Quantum 2, 040326, 2021) | medium | high | low |
| [1801.07904](../notes/papers/1801.07904.md) | Heinsoo et al., rapid multiplexed readout and its crosstalk (PR Applied 10, 034040, 2018) | medium | medium | low |
| [2002.01471](../notes/papers/2002.01471.md) | Geller, rigorous justification of transition-matrix measurement correction (QST 5, 03LT01, 2020) | low | high | low |
| [1606.05721](../notes/papers/1606.05721.md) | Sank et al., measurement-induced state transitions (PRL 117, 190503, 2016) | low | low | low |
| [2403.09514](../notes/papers/2403.09514.md) | Baeumer et al., Quantum Fourier transform using dynamic circuits, PRL 133, 150602 (2024) | high | none | medium |
| [2403.06852](../notes/papers/2403.06852.md) | Seif et al., Suppressing correlated noise via context-aware compiling, ISCA 2024 | high | none | low |
| [1101.4707](../notes/papers/1101.4707.md) | Bylander et al., Noise spectroscopy through dynamical decoupling with a superconducting flux qubit, Nat. Phys. 7, 565 (2011) | medium | none | none |
| [1612.00858](../notes/papers/1612.00858.md) | McKay et al., Efficient Z gates for quantum computing, PRA 96, 022330 (2017) | high | none | low |
| [1207.1655](../notes/papers/1207.1655.md) | Granade et al., Robust online Hamiltonian learning, NJP 14, 103013 (2012) | medium | none | none |
| [1504.06597](../notes/papers/1504.06597.md) | Sheldon et al., Characterizing errors on qubit operations via iterative randomized benchmarking, PRA 93, 012301 (2016) | medium | none | none |
| [1502.02677](../notes/papers/1502.02677.md) | Kimmel, Low and Yoder, Robust calibration via robust phase estimation, PRA 92, 062315 (2015); erratum PRA 104, 069901 (2021) | medium | none | none |
| [1301.7007](../notes/papers/1301.7007.md) | Smolin, Smith and Vargo, Oversimplifying quantum factoring, Nature 499, 163 (2013) | low | none | high |
| [0907.3740](../notes/papers/0907.3740.md) | Maurer and Pontil, Empirical Bernstein bounds and sample variance penalization, COLT 2009 | medium | none | none |
| [2010.09686](../notes/papers/2010.09686.md) | Waudby-Smith and Ramdas, Estimating means of bounded random variables by betting, JRSSB 86, 1 (2024) | medium | none | none |
| [hoeffding-1963](../notes/papers/hoeffding-1963.md) | Hoeffding, Probability inequalities for sums of bounded random variables, JASA 58, 13 (1963) | high | none | none |
| [2306.00874](../notes/papers/2306.00874.md) | Maring et al., A versatile single-photon-based quantum computing platform, Nature Photonics 18, 603 (2024) | none | none | none |
| [2310.15349](../notes/papers/2310.15349.md) | Fyrillas et al., Scalable machine learning-assisted clear-box characterization for optimally controlled photonic circuits, Optica 11, 427 (2024) | low | none | none |
| [2506.05988](../notes/papers/2506.05988.md) | Fyrillas et al., Resource-efficient crosstalk mitigation for the high-fidelity operation of photonic integrated circuits with induced phase shifters (2025) | low | none | none |
| [2606.18408](../notes/papers/2606.18408.md) | Tully, Washburn and Simons, Characterization of nested Walsh parity-check filters in a single-photon eight-mode register on a cloud photonic processor (2026, unrefereed) | none | low | none |
| [2005.01743](../notes/papers/2005.01743.md) | Ollivier et al., Hong-Ou-Mandel interference with imperfect single photon sources, Phys. Rev. Lett. 126, 063602 (2021) | none | none | none |
| [2004.14018](../notes/papers/2004.14018.md) | White et al., Demonstration of non-Markovian process characterisation and control on a quantum processor, Nat. Commun. 11, 6301 (2020) | low | none | none |
| [riley-2008-nist-sp-1065](../notes/papers/riley-2008-nist-sp-1065.md) | Riley, Handbook of Frequency Stability Analysis, NIST SP 1065 (2008) | low | none | none |
| [quant-ph-0501020](../notes/papers/quant-ph-0501020.md) | Toth and Guhne, Entanglement detection in the stabilizer formalism, Phys. Rev. A 72, 022340 (2005) | none | none | none |
| [jafferis-2022-traversable-wormhole](../notes/papers/jafferis-2022-traversable-wormhole.md) | Jafferis et al., Traversable wormhole dynamics on a quantum processor, Nature 612, 51 (2022) | none | none | none |
| [2302.07897](../notes/papers/2302.07897.md) | Kobrin, Schuster and Yao, Comment on "Traversable wormhole dynamics on a quantum processor" (2023) | none | none | none |
| [2303.15423](../notes/papers/2303.15423.md) | Jafferis et al., Comment on "Comment on 'Traversable wormhole dynamics on a quantum processor'" (2023) | none | none | none |
| [2310.16903](../notes/papers/2310.16903.md) | Silvestri et al., Experimental observation of Earth's rotation with quantum entanglement, Sci. Adv. 10, eado0215 (2024) | none | none | none |
| [1807.06205](../notes/papers/1807.06205.md) | Planck Collaboration, Planck 2018 results. I. Overview and the cosmological legacy of Planck, A&A 641, A1 (2020) | none | none | none |
| [2206.00570](../notes/papers/2206.00570.md) | Dreissen et al., Improved bounds on Lorentz violation from composite-pulse Ramsey spectroscopy in a trapped ion, Nat. Commun. 13, 7314 (2022) | none | none | none |
| [quant-ph-0203033](../notes/papers/quant-ph-0203033.md) | Peres, Scudo and Terno, Quantum entropy and special relativity, PRL 88, 230402 (2002) | none | none | none |
| [2109.12238](../notes/papers/2109.12238.md) | Bothwell et al., Resolving the gravitational redshift across a millimetre-scale atomic sample, Nature 602, 420 (2022) | none | none | none |
| [1105.4531](../notes/papers/1105.4531.md) | Zych, Costa, Pikovski and Brukner, Quantum interferometric visibility as a witness of general relativistic proper time, Nat. Commun. 2, 505 (2011) | none | none | none |
| [1311.1095](../notes/papers/1311.1095.md) | Pikovski, Zych, Costa and Brukner, Universal decoherence due to gravitational time dilation, Nat. Phys. 11, 668 (2015) | none | none | none |
| [1707.01339](../notes/papers/1707.01339.md) | Yin et al., Satellite-based entanglement distribution over 1200 kilometers, Science 356, 1140 (2017) | none | none | none |
| [ashby-nelson-2009-gps-relativity](../notes/papers/ashby-nelson-2009-gps-relativity.md) | Ashby and Nelson, The global positioning system, relativity, and extraterrestrial navigation, Proc. IAU 5(S261), 22 (2009) | none | none | none |
| [ashby-2018-null-test-lpi](../notes/papers/ashby-2018-null-test-lpi.md) | Ashby, Parker and Patla, A null test of general relativity based on a long-term comparison of atomic transition frequencies, Nat. Phys. 14, 822 (2018) | none | none | none |
| [2001.09190](../notes/papers/2001.09190.md) | Vepsäläinen et al., Impact of ionizing radiation on superconducting qubit coherence, Nature 584, 551 (2020) | low | none | low |
| [2402.03208](../notes/papers/2402.03208.md) | Harrington et al., Synchronous detection of cosmic rays and correlated errors in superconducting qubit arrays, Nat. Commun. 16, 6428 (2025) | low | none | low |
| [quant-ph-0302031](../notes/papers/quant-ph-0302031.md) | Horodecki, Shor and Ruskai, Entanglement breaking channels, Rev. Math. Phys. 15, 629 (2003) | none | none | none |
| [quant-ph-9807091](../notes/papers/quant-ph-9807091.md) | Horodecki, Horodecki and Horodecki, General teleportation channel, singlet fraction and quasidistillation, Phys. Rev. A 60, 1888 (1999) | none | none | none |
| [1210.4583](../notes/papers/1210.4583.md) | Chitambar, Leung, Mancinska, Ozols and Winter, Everything you always wanted to know about LOCC, Commun. Math. Phys. 328, 303 (2014) | none | none | none |
| [quant-ph-0007058](../notes/papers/quant-ph-0007058.md) | Calsamiglia and Lutkenhaus, Maximum efficiency of a linear-optical Bell-state analyzer, Appl. Phys. B 72, 67 (2001) | none | none | none |
| [quant-ph-9605038](../notes/papers/quant-ph-9605038.md) | Horodecki, Horodecki and Horodecki, Separability of mixed states: necessary and sufficient conditions, Phys. Lett. A 223, 1 (1996) | none | none | none |
| [2411.12387](../notes/papers/2411.12387.md) | Laneve et al., Quantum teleportation with dissimilar quantum dots over a hybrid quantum network (2024 preprint) | none | none | none |
| [1103.1528](../notes/papers/1103.1528.md) | Specht et al., A single-atom quantum memory (2011) | none | none | none |
| [1201.4149](../notes/papers/1201.4149.md) | Gündoğan et al., Quantum storage of a photonic polarization qubit in a solid (2012) | none | none | none |
| [quant-ph-0301059](../notes/papers/quant-ph-0301059.md) | Gill, Time, finite statistics, and Bell's fifth position (2003) | medium | none | none |
| [1108.2468](../notes/papers/1108.2468.md) | Zhang, Glancy and Knill, Asymptotically optimal data analysis for rejecting local realism (2011) | medium | none | none |
| [1312.2999](../notes/papers/1312.2999.md) | Bierhorst, A robust mathematical model for a loophole-free Clauser-Horne experiment (2015) | medium | none | none |
| [2310.20521](../notes/papers/2310.20521.md) | Polacchi et al., Teleportation of a genuine single-rail vacuum-one-photon qubit from a quantum dot (2024) | none | none | none |
| [1301.1170](../notes/papers/1301.1170.md) | Chiribella and Xie, Optimal design and quantum benchmarks for coherent state amplifiers (2013) | none | none | none |
| [1901.02260](../notes/papers/1901.02260.md) | Anderson et al., Quantum teleportation using telecom C-band quantum dots (2020) | none | none | none |
| [1210.1282](../notes/papers/1210.1282.md) | Ma et al., Experimental quantum teleportation over a high-loss free-space channel (2012) | none | none | none |
| [2411.12904](../notes/papers/2411.12904.md) | Strobel et al., Quantum teleportation with telecom photons from remote quantum emitters (2024 preprint) | none | none | none |
| [1302.0932](../notes/papers/1302.0932.md) | van Enk and Blume-Kohout, When quantum tomography goes wrong: drift of quantum sources and other errors, New J. Phys. 15, 025024 (2013) | low | none | none |
| [roadmap-2026-03](../notes/quandela/roadmap-2026-03.md) | Quandela, Roadmap 2026-2033 (March 2026) and the Quandela-Welinq interconnect announcement (provider documents) | none | none | none |
| [2104.05219](../notes/papers/2104.05219.md) | McEwen et al., Resolving catastrophic error bursts from cosmic rays in large arrays of superconducting qubits, Nat. Phys. 18, 107 (2022) | low | none | low |

The [parallel-experiment synthesis](../notes/quantum_experiment_parallelism.md)
connects these sources to fixed and varied companions, patch/time blocking,
joint-shot inference, billed usage, and IQP claim boundaries. The
[design and execution documentation note](../notes/quantum_experiment_design_sources.md)
records NIST, Qiskit and IBM sources with capture hashes. The two retained parallel-experiment
PDFs have [replayable checksums](../parallel_experiment_pdfs.sha256); direct,
version-pinned retrieval links and reading scopes live in each paper note.
The remaining parallel-experiment papers retain direct URLs, hashes, and
reading notes as external sources. The Das notice expressly requires permission
for server redistribution; an arXiv-only grant also differs from permission to
rehost a PDF. The source registry records each individual decision.

Every note from the prior-work review labels each overlapping repository
claim as known theorem reproduced, new proof or formalization, new
implementation or measurement, or candidate new result.
[prior_work_synthesis.md](../notes/prior_work_synthesis.md) owns current status
and experiment priority. The [archive/handbacks/](../archive/handbacks/) directory preserves the
delegates' original findings and disclosures with explicit current-status
links. Its [A] labels identify the original scratch checks; later retained
gates carry their own evidence links.

The per-paper notes own current citations, hypotheses, theorem locators, and
typographical corrections: [BDI 2005](../notes/math-0511691.md),
[BCDI 2007](../notes/math-0702075.md), [BCDI 2009](../notes/0905.2987.md), and
[Reggiani 2024](../notes/papers/2411.18881.md). The
[shared sparse census](../notes/topics/cayley_dickson_sparse_census.md) owns count
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

docs/design/factoring-notes.md re-checks the sign recursion and the
defect count independently.

The first eight quantum and factoring papers in the table contain no Cayley-Dickson,
octonion, sedenion, zero-divisor, or nonassociative content. The
[annihilator source ledger](../notes/cayley_dickson_annihilator_sources.md) and
[rank-topology source ledger](../notes/cayley_dickson_rank_topology_sources.md)
remain historical implementation-audit snapshots. Their source retrievals,
theorem applications, and local derivations retain the provenance of the
corresponding implementation. Current per-paper notes consolidate overlapping
paper facts; the snapshots retain their original bytes because execution
manifests bind their hashes.

| Snapshot | Source revision | SHA-256 | Manifest binding |
| --- | --- | --- | --- |
| Annihilator ledger | `bd5d6b2e97165d560df588084098056fce5a2fd1` | `02f4cf4fb7dee46e5fd87052cf5d4c0a81087c848948bad17af246b764f080d5` | [topology verification](../../results/hw_estimate/cayley_dickson_topology_verification.json), `source_sha256` |
| Rank-topology ledger | `f4eda251822b380d695564fcf39a7a9e528f994e` | `bd478146132ddade390396b5b330f3a08091b2ebae83d9bacab1d23644756a30` | [rank verification](../../results/hw_estimate/rank_topology_verification.json), `documentation_sha256` |

[FACTORING_NOTES.md](../design/factoring-notes.md) carries the factoring
analysis.


The [proof and experiment dependency synthesis](../notes/research_proof_experiment_dependencies.md)
connects curve realization, exact matrix certificates, circuit/instrument
semantics, tomography, stopping and full-workload allocation to primary sources.
The [field-model opportunity map](../notes/vacuum_field_run_opportunities.md)
separates physical device-noise sensing, encoded field simulation, and calibrated
force/radiation measurements. Its [finite CPU reference](../evidence/vacuum_models/README.md)
retains cutoff, coherence, synthesis and SPAM-identifiability checks; future
hardware cases retain their independent admission gates.

| Additional source group | Notes and application |
| --- | --- |
| Curve realization | [Basu--Roy](../notes/1803.00505.md), [Greenberg](../notes/papers/greenberg-henselian-lifting.md), expanded [BCDI II](../notes/math-0702075.md) and [Coste](../notes/coste-semialgebraic-geometry.md); real-arc and lifting hypotheses |
| Formal interfaces | [SQIR/VOQC](../notes/papers/sqir-voqc-proof-interfaces.md), [MathComp/CoqEAL](../notes/papers/mathcomp-coqeal-matrix-certificates.md), [CoqInterval](../notes/papers/coqinterval-certified-enclosures.md); checked semantics, rank witnesses and numerical enclosures |
| Identification and resource design | [GST](../notes/papers/2009.07301.md), expanded [QILGST](../notes/papers/2103.03008.md), [optimal design](../notes/papers/quant-ph-0411093.md), [SHOALS](../notes/papers/2201.13438.md), [shadows](../notes/papers/2002.08953.md); gauge, measurement choice and complete costs |
| Device noise | [Schoelkopf](../notes/cond-mat-0210247.md), [Clerk](../notes/0810.4729.md), [Jin](../notes/1412.2772.md); spectral convention, residual populations and calibrated inference |
| Encoded field models | [Digital optics](../notes/1909.04408.md), [Gaussian coherence](../notes/papers/1610.03272.md), [lattice Casimir](../notes/papers/2105.02032.md), [Gaussian simulation](../notes/papers/quant-ph-0109047.md), [collision models](../notes/2106.11974.md); encoding, model bias and classical baselines |
| Physical interpretation and execution | [Physical DCE](../notes/papers/1105.4714.md), [real-material Casimir](../notes/papers/0902.4022.md), [circuit QED](../notes/papers/2005.12667.md), [IBM policy](../notes/papers/ibm_fractional_execution_sources.md); apparatus, observable and runtime boundaries |
| Vacuum, dark sector and negative energy | [ALPS II](../notes/papers/2512.14110.md), [Dark SRF](../notes/papers/2510.02427.md), [dielectric haloscope](../notes/papers/2503.23354.md), [qubit haloscope](../notes/papers/2503.18315.md), [atom interferometry](../notes/papers/2511.09750.md), [LZ](../notes/papers/2609.02823.md), [DES Y6](../notes/papers/2601.14559.md), [worldline DCE](../notes/papers/2604.13237.md), [magnetic-fluid Casimir](../notes/papers/2601.00483.md), [quantum inequalities](../notes/papers/gr-qc-9607003.md), [QET theory](../notes/papers/1002.0200.md) and [hardware](../notes/papers/2301.02666.md), [journal and IBM pages](../notes/papers/casimir-dark-sector-web-sources.md), [Pais patents, NAWCAD record and gyroscope nulls](../notes/papers/pais-patent-web-sources.md); exclusions, nuisances and energy accounting before any new-physics reading |
| Cayley-Dickson associator structure | [defect census](../notes/topics/cd_associator_defect_census.md), [Wilmot](../notes/papers/2505.11747.md), [Kirshtein](../notes/1207.4230.md); closed forms, subspace types and the sufficient conditions of Lemma 3 |
| Sedenion automorphisms, sign matrices and Hadamard groups | [Wilmot automorphisms](../notes/papers/2512.07210.md), [Gresnigt review](../notes/papers/2609.10569.md), [Kivunge slides](../notes/papers/kivunge-2013-sign-matrices-2n-ons.md), [skew Hadamard morphisms](../notes/papers/1907.07024.md), [O Cathain](../notes/papers/ocathain-2012-nonaffine-hadamard.md), [PSL_2(7)](../notes/papers/0709.1447.md); printed sedenion tables checked against `cd_core`, the `S3` maps certified on basis pairs, the sign-matrix and Paley statements linked to the [star-lattice tower](../notes/topics/cd-star-lattice-tower.md) |
| External algebra packages | [package index](../notes/packages/README.md): measured relation of eight hypercomplex packages to cd_core, independence, licenses and correct use |
| Octonion structure checks | [associator codes, box-kite frustration and walk sectors](../notes/topics/octonion_structure_checks.md): RM(1,3) and E8 from the associator slices, shared-sign and shared-phase frustration minima 4 and 3, exact walk sector weights by Ramanujan sums, and the doubling-convention bridge |
| Sedenion hardware witnesses | [review of an external proposal](../notes/topics/sedenion_hardware_witness_review.md): the encoding Designs A to D measure, exact corrections (the annihilator of e1 + e10, the degree-4 sign, the post-selected zero-divisor observable), the measured Design C verdicts and the zero-divisor test's price |
| Review reconciliation | [QPU, Cayley-Dickson and vacuum review claims](../notes/topics/qpu_vacuum_cd_review_reconciliation.md); each claim with its status and settling artifact |
| Singular sectors and dilation | [sector split, census link and dynamics](../notes/singular_sector_dynamics.md): dark, bright and anticommuting sectors of every two-term element, the Hermitian dilation's frequencies, product-formula exactness, the frozen Design B walk and its echo-matched control; [LCU](../notes/papers/1202.5822.md), [oblivious amplification](../notes/papers/1312.1414.md), [Hamiltonian block encoding](../notes/papers/2510.06316.md), [QSVT](../notes/papers/1806.01838.md) |
| Measurement foundations | [coherence decay](../notes/papers/0909.4585.md), [trajectories](../notes/papers/1305.7270.md), [efficient tomography](../notes/papers/1101.4366.md), [pulse removal, tomography API and early superconducting tomography](../notes/papers/measurement_foundations_web_sources.md); which laboratory reconstructions transfer to the cloud gate set |
| Relativistic metrology and radiation | [Earth-rotation Sagnac phase](../notes/papers/2310.16903.md), [CMB dipole](../notes/papers/1807.06205.md), [Lorentz-violation bounds](../notes/papers/2206.00570.md), [spin entropy under boosts](../notes/papers/quant-ph-0203033.md), [gravitational redshift](../notes/papers/2109.12238.md), [proper-time visibility](../notes/papers/1105.4531.md), [time-dilation decoherence](../notes/papers/1311.1095.md), [satellite entanglement](../notes/papers/1707.01339.md), [solar gravity in clock comparisons](../notes/papers/ashby-nelson-2009-gps-relativity.md), [local position invariance](../notes/papers/ashby-2018-null-test-lpi.md), [radiation limit on T1](../notes/papers/2001.09190.md), [cosmic-ray coincidences](../notes/papers/2402.03208.md), [cosmic-ray error bursts](../notes/papers/2104.05219.md); the size of each relativistic effect against the repository's observed instability and the sidereal, orientation or coincidence signature a real astronomical coupling needs |
| Hypercomplex theory and operational encodings | [normed division algebras](../notes/papers/math-0105155.md), [single-photon hypercomplex test](../notes/papers/1602.01624.md) with [Adler's critique](../notes/papers/1604.04950.md) and [the reply](../notes/papers/1607.01648.md), [superconducting](../notes/papers/2210.10255.md) and [trapped-ion](../notes/papers/2305.03766.md) non-Abelian anyons, [Crossref records](../notes/papers/hypercomplex_quantum_crossref_records.md), [associator audit](../evidence/reviewer_associator_audit/PROVENANCE.md); encoding an algebra in complex quantum mechanics against testing a hypercomplex theory |
| Dark-subspace certificate | [source map](../notes/quandela/bdsc_sources.md): [eigentheory](../notes/0905.2987.md), [detector tomography](../notes/papers/0807.2444.md), [GST](../notes/papers/2009.07301.md), [optical dilation](../notes/papers/1712.01413.md), [interferometer design](../notes/papers/1603.08788.md), [matrix Bernstein](../notes/papers/1004.4389.md), [subspace verification](../notes/papers/2410.12551.md); target spectrum, Kraus dilation, confidence radii and the preparation premise |
| Photonic characterization, drift, witness and wormhole dispute | [Ascella platform](../notes/papers/2306.00874.md), [clear-box characterization](../notes/papers/2310.15349.md), [induced phase shifters](../notes/papers/2506.05988.md), [Belenos Walsh filters](../notes/papers/2606.18408.md), [HOM with imperfect sources](../notes/papers/2005.01743.md), [process tensor](../notes/papers/2004.14018.md), [NIST SP 1065](../notes/papers/riley-2008-nist-sp-1065.md), [stabilizer witnesses](../notes/papers/quant-ph-0501020.md), [the wormhole article](../notes/papers/jafferis-2022-traversable-wormhole.md) with its [comment](../notes/papers/2302.07897.md) and [reply](../notes/papers/2303.15423.md); device error model, Belenos acceptance and routing controls, drift-series statistics, the two-qubit fidelity witness and the emulation-claim controls |

## Historical action items and current status

The list below records the source review's original proposals. The
[execution roadmap](../../gororoba_quantum/QPU_EXECUTION_ROADMAP.md) owns live
completion status. The folded mechanism ladder completes in two retained jobs;
native static mitigation and coherent/dynamic option separation exist in the
runner. Dynamic DD/twirling compatibility, N21 admission, initialization-delay
qualification, and fresh hardware approval retain their documented gates.
The [decision note](../notes/model_discrimination_optimizer.md) supersedes any
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
