# Source index

The `publication_status` ledger in [SOURCES.json](SOURCES.json) separates verified journal
identities, arXiv-supplied journal references and unverified venues. The
[Crossref reconciliation](notes/papers/hypercomplex_quantum_crossref_records.md) records retrieval
identities and scopes; bibliographic verification differs from a mathematical proof check.

The source library separates repository-hosted papers from local reading copies.
All source notes, retrieval URLs, original byte identities, and reading scopes remain
public in [SOURCES.json](SOURCES.json) and the linked notes. License evidence
controls PDF hosting; availability for download alone supplies no downstream grant.

| Location | Contents | Git treatment |
| --- | --- | --- |
| `docs/pdf/` | 30 unchanged PDFs with source-specific CC BY 4.0 or CC0 evidence, plus two aliases | Tracked |
| `docs/local_source_cache/` | 114 optional original reading copies with restricted or unestablished rehosting permission | Ignored |
| `docs/source_archives/` | 5 licensed original software archives, with exact inspected members and notices | Tracked |
| `docs/notes/`, `docs/evidence/` | Research descriptions, provenance, and repeatable checks | Tracked |

The local cache lives inside `docs/`. A fresh checkout receives the public notes
and hosted PDFs; the verifier accepts an absent cache and checks each registered
local copy when present. Local filenames below appear as text so links also work
in a clean checkout. All retained originals preserve their registered SHA-256.
Historical Git commits can retain previously tracked PDF blobs; the folder split
changes the branch tip and performs no history rewrite.

The [annihilator determinant-line proof](notes/annihilator_determinant_line.md)
and [exact replay](evidence/kernel_determinant/README.md) apply the complex
skew framework to global determinant trivializations on each rank locus.
They retain full bundle and attachment classification as open obligations.
The [latest C881 audit](notes/c881_exhaustive_proof.md) and
[Rocq replay](evidence/c881_exhaustive/README.md) refresh the finite
separating-degree proof against the latest audited `open_gororoba` HEAD.

The [projective kernel-frontier construction](notes/projective_kernel_frontiers.md)
and [exact replay](evidence/projective_kernel_limits/README.md) recover leading
kernel planes through polynomial saturation and describe the full pair space
as a quotient of tautological sphere spaces over real frontier graphs.
Computing those graph closures and the global invariants remains open.

The [real circle-frontier graph](notes/real_circle_frontier_graphs.md) and
[replay](evidence/real_frontier_graphs/README.md) compute the complete named
cone slice closure, its trace inverse, and integral evaluation maps. Ambient
coverage and unrestricted topology remain open.
The [Moreno Stiefel note](notes/math-0512517.md) and its
[exact certificates](evidence/moreno_stiefel/README.md) give an integer Stiefel
element of A_6 with nullity 0, a negative answer to Moreno's open question at
A_6, against nullity 4 at every one of 32 exact A_5 points.

## Hosted papers

The notes attribute each source and link its exact-version license evidence.
The PDFs retain their original notices and bytes. Repository licensing leaves
each source license in force.

| Source note | Hosted PDF | Source license |
| --- | --- | --- |
| [Kissinger and Meijer-van de Griend 2019 -- CNOT circuit extraction for topologically-constrained quantum memories (arXiv 1904.00633)](notes/papers/1904.00633.md) | [1904.00633v2.pdf](pdf/1904.00633v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Sarovar et al. 2020 -- Detecting crosstalk errors in quantum information processors](notes/papers/1908.09855.md) | [1908.09855v3.pdf](pdf/1908.09855v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Corcoles et al. 2021 -- Exploiting dynamic quantum circuits in a quantum algorithm with superconducting qubits (arXiv 2102.01682)](notes/2102.01682.md) | [2102.01682.pdf](pdf/2102.01682.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Niu and Todri-Sanial 2023 -- Enabling Multi-programming Mechanism for Quantum Computing in the NISQ Era (arXiv 2102.05321)](notes/2102.05321.md) | [2102.05321v3.pdf](pdf/2102.05321v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Gidney 2025 -- How to factor 2048 bit RSA integers with less than a million noisy qubits (arXiv 2505.15917)](notes/papers/2505.15917.md) | [2505.15917.pdf](pdf/2505.15917.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Cobos et al. 2025 -- Real-Time Dynamics in a (2+1)-D Gauge Theory: The Stringy Nature on a Superconducting Quantum Simulator (arXiv 2507.08088)](notes/2507.08088.md) | [2507.08088.pdf](pdf/2507.08088.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Pokharel et al. 2025 -- Order from chaos with adaptive circuits on quantum hardware (arXiv 2509.18259)](notes/2509.18259.md) | [2509.18259.pdf](pdf/2509.18259.pdf) | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [Levratti: active stabilizers and Cayley-Dickson zero-divisor supports](notes/papers/levratti-2026-active-stabilizers.md) | [levratti-2026-active-stabilizers.pdf](pdf/levratti-2026-active-stabilizers.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [van der Schoot et al. 2023 -- quantum metrics on Quantum Inspire Starmon-5 (arXiv 2310.01120)](notes/papers/2310.01120.md) | [2310.01120v1.pdf](pdf/2310.01120v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Nation et al. 2021 -- scalable measurement-error mitigation, M3 (arXiv 2108.12518)](notes/papers/2108.12518.md) | [2108.12518v1.pdf](pdf/2108.12518v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Chen et al. 2025 -- Quantum subspace verification for error correction codes (arXiv 2410.12551)](notes/papers/2410.12551.md) | [2410.12551v1.pdf](pdf/2410.12551v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Levratti 2026 -- Fano Duality, Projective Orthogonality and the CSS Bridge (author-hosted manuscript)](notes/papers/levratti-2026-fano-css.md) | [levratti-2026-fano-css.pdf](pdf/levratti-2026-fano-css.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Covariant quantum kernels for data with group structure](notes/papers/s41567-023-02340-9.md) | [2105.03406.pdf](pdf/2105.03406.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Challenges and opportunities in quantum optimization](notes/papers/s42254-024-00770-9.md) | [2312.02279.pdf](pdf/2312.02279.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Baeumer et al. 2024 -- Quantum Fourier transform using dynamic circuits (arXiv 2403.09514)](notes/papers/2403.09514.md) | [2403.09514v2.pdf](pdf/2403.09514v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |

| [Proving Quantum Programs Correct](notes/papers/sqir-voqc-proof-interfaces.md) | [LIPIcs.ITP.2021.21.pdf](pdf/LIPIcs.ITP.2021.21.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Gate Set Tomography](notes/papers/2009.07301.md) | [2009.07301.pdf](pdf/2009.07301.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Latency considerations for stochastic optimizers in variational quantum algorithms](notes/papers/2201.13438.md) | [2201.13438.pdf](pdf/2201.13438.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Brotherton et al. 2025 -- Any Light Particle Searches with ALPS II: first science results](notes/papers/2512.14110.md) | [2512.14110v3.pdf](pdf/2512.14110v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Wei et al. 2026 -- New Constraints on Dark Photon Dark Matter with a Millimeter-Wave Dielectric Haloscope](notes/papers/2503.23354.md) | [2503.23354v2.pdf](pdf/2503.23354v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Fosco and Guntsche 2026 -- Dynamical Casimir effect in the worldline formulation](notes/papers/2604.13237.md) | [2604.13237v3.pdf](pdf/2604.13237v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Ma et al. 2026 -- Prediction of a measurable sign change in the Casimir force using a magnetic fluid](notes/papers/2601.00483.md) | [2601.00483v1.pdf](pdf/2601.00483v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Kang et al. 2025 -- Scalable architecture for dark photon searches: Superconducting-qubit proof of principle](notes/papers/2503.18315.md) | [2503.18315v1.pdf](pdf/2503.18315v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Google Quantum AI and Collaborators 2023 -- Non-Abelian braiding of graph vertices in a superconducting processor](notes/papers/2210.10255.md) | [2210.10255v2.pdf](pdf/2210.10255v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Matsumoto et al. 2026 -- Two-qubit logic and teleportation with mobile spin qubits in silicon (Nature 653, 391)](notes/papers/s41586-026-10423-9.md) | [s41586-026-10423-9.pdf](pdf/s41586-026-10423-9.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Wu et al. 2026 -- Simultaneous high-fidelity single-qubit gates in a spin qubit array (Nature Physics)](notes/papers/s41567-026-03466-2.md) | [s41567-026-03466-2.pdf](pdf/s41567-026-03466-2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Flaut and Boboescu 2021 -- A twisted group algebra structure for an algebra obtained by the Cayley-Dickson process (arXiv 2103.12805)](notes/papers/2103.12805.md) | [2103.12805v1.pdf](pdf/2103.12805v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Fyrillas et al. 2024 -- Scalable machine learning-assisted clear-box characterization for optimally controlled photonic circuits (Optica 11, 427)](notes/papers/2310.15349.md) | [2310.15349v2.pdf](pdf/2310.15349v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Fyrillas et al. 2025 -- Resource-efficient crosstalk mitigation for the high-fidelity operation of photonic integrated circuits with induced phase shifters (arXiv 2506.05988)](notes/papers/2506.05988.md) | [2506.05988v1.pdf](pdf/2506.05988v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Kobrin, Schuster and Yao 2023 -- Comment on "Traversable wormhole dynamics on a quantum processor" (arXiv 2302.07897)](notes/papers/2302.07897.md) | [2302.07897v1.pdf](pdf/2302.07897v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Jafferis et al. 2023 -- Comment on "Comment on 'Traversable wormhole dynamics on a quantum processor'" (arXiv 2303.15423)](notes/papers/2303.15423.md) | [2303.15423v1.pdf](pdf/2303.15423v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |

The two Nature aliases identify retained arXiv preprints, with their own
licenses and versions. The aliases do not identify the publisher versions.

## External papers and local reading copies

ArXiv-only hosting grants, personal-copy terms, and unresolved author permission
lead to external-only entries. The classification records the evidence inspected;
exclusion from hosting does not assert that every possible reuse is forbidden.

| Source note | Original download | Local filename in `docs/local_source_cache/` | Hosting evidence |
| --- | --- | --- | --- |
| [Lundeen et al. 2009 -- Tomography of quantum detectors (arXiv 0807.2444)](notes/papers/0807.2444.md) | [PDF](https://arxiv.org/pdf/0807.2444v1) | `0807.2444v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0807.2444v1) |
| [Roetteler 2008 -- Quantum algorithms for highly non-linear Boolean functions (arXiv 0811.3208)](notes/papers/0811.3208.md) | [PDF](https://arxiv.org/pdf/0811.3208v2) | `0811.3208v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0811.3208v2) |
| [Biss, Christensen, Dugger, Isaksen 2009 -- Eigentheory of Cayley-Dickson algebras (arXiv 0905.2987)](notes/0905.2987.md) | [PDF](https://arxiv.org/pdf/0905.2987v1) | `0905.2987v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0905.2987v1) |
| [Roetteler 2009 -- Hidden shift for quadratics and for functions of large Gowers norm (arXiv 0911.4724)](notes/papers/0911.4724.md) | [PDF](https://arxiv.org/pdf/0911.4724v1) | `0911.4724v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0911.4724v1) |
| [Morier-Genoud and Ovsienko 2011 -- A series of algebras generalizing the octonions and Hurwitz-Radon identity (arXiv 1003.0429)](notes/papers/1003.0429.md) | [PDF](https://arxiv.org/pdf/1003.0429v3) | `1003.0429v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1003.0429v3) |
| [Tropp 2012 -- User-friendly tail bounds for sums of random matrices (arXiv 1004.4389)](notes/papers/1004.4389.md) | [PDF](https://arxiv.org/pdf/1004.4389v7) | `1004.4389v7.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1004.4389v7) |
| [Gavinsky, Roetteler, Roland 2011 -- Quantum algorithm for the Boolean hidden shift problem (arXiv 1103.3017)](notes/papers/1103.3017.md) | [PDF](https://arxiv.org/pdf/1103.3017v1) | `1103.3017v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1103.3017v1) |
| [Bales 2003 -- Cayley-Dickson and Clifford algebras as twisted group algebras (arXiv 1107.1375)](notes/papers/1107.1375.md) | [PDF](https://arxiv.org/pdf/1107.1375v1) | `1107.1375v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1107.1375v1) |
| [Decker, Ivanyos, Santha, Wocjan 2011 -- Hidden Symmetry Subgroup Problems (arXiv 1107.2189)](notes/papers/1107.2189.md) | [PDF](https://arxiv.org/pdf/1107.2189v2) | `1107.2189v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1107.2189v2) |
| [Martin-Lopez et al. 2012 -- Experimental realization of Shor's quantum factoring algorithm using qubit recycling (arXiv 1111.4147)](notes/papers/1111.4147.md) | [PDF](https://arxiv.org/pdf/1111.4147v2) | `1111.4147v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1111.4147v2) |
| [Gambetta et al. 2012 -- Characterization of addressability by simultaneous randomized benchmarking](notes/papers/1204.6308.md) | [PDF](https://arxiv.org/pdf/1204.6308v2) | `1204.6308v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1204.6308v2) |
| [Kirshtein 2012 -- Multiplication groups and inner mapping groups of Cayley-Dickson loops (arXiv 1207.4230)](notes/1207.4230.md) | [PDF](https://arxiv.org/pdf/1207.4230v1) | `1207.4230v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1207.4230v1) |
| [Bremner, Montanaro and Shepherd -- approximate IQP sampling and cubic phases](notes/papers/1504.07999.md) | [PDF](https://arxiv.org/pdf/1504.07999v2) | `1504.07999v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1504.07999v2) |
| [Bales 2016 -- An alternate Cayley-Dickson product (arXiv 1602.02317)](notes/papers/1602.02317.md) | [PDF](https://arxiv.org/pdf/1602.02317v1) | `1602.02317v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1602.02317v1) |
| [Bales 2016 -- Periodicity of the Cayley-Dickson twists (arXiv 1602.02843)](notes/1602.02843.md) | [PDF](https://arxiv.org/pdf/1602.02843v3) | `1602.02843v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1602.02843v3) |
| [Clements et al. 2016 -- Optimal design for universal multiport interferometers (arXiv 1603.08788)](notes/papers/1603.08788.md) | [PDF](https://arxiv.org/pdf/1603.08788v2) | `1603.08788v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1603.08788v2) |
| [Tischler, Rockstuhl, Slowik 2018 -- linear optical transformations with loss and gain (arXiv 1712.01413)](notes/papers/1712.01413.md) | [PDF](https://arxiv.org/pdf/1712.01413v2) | `1712.01413v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1712.01413v2) |
| [Gilyen, Su, Low, and Wiebe 2018 -- Quantum singular value transformation and beyond: exponential improvements for quantum matrix arithmetics (arXiv 1806.01838)](notes/papers/1806.01838.md) | [PDF](https://arxiv.org/pdf/1806.01838v1) | `1806.01838v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1806.01838v1) |
| [Rudinger et al. 2019 -- Probing context-dependent errors in quantum processors](notes/papers/1810.05651.md) | [PDF](https://arxiv.org/pdf/1810.05651v1) | `1810.05651v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1810.05651v1) |
| [Freedman, Shokrian-Zini, and Wang 2019 -- Quantum computing with octonions (arXiv 1811.08580)](notes/papers/1811.08580.md) | [PDF](https://arxiv.org/pdf/1811.08580v5) | `1811.08580v5.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1811.08580v5) |
| [Proctor et al. 2020 -- Detecting and tracking drift in quantum information processors](notes/papers/1907.13608.md) | [PDF](https://arxiv.org/pdf/1907.13608v3) | `1907.13608v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1907.13608v3) |
| [Rudinger et al.: quantum-instrument tomography of mid-circuit measurement](notes/papers/2103.03008.md) | [PDF](https://arxiv.org/pdf/2103.03008v1) | `2103.03008v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2103.03008v1) |
| [Resch et al. 2021 -- Accelerating Variational Quantum Algorithms Using Circuit Concurrency (arXiv 2109.01714)](notes/papers/2109.01714.md) | [PDF](https://arxiv.org/pdf/2109.01714v1) | `2109.01714v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2109.01714v1) |
| [Niu and Todri-Sanial 2021 -- How Parallel Circuit Execution Can Be Useful for NISQ Computing? (arXiv 2112.00387)](notes/papers/2112.00387.md) | [PDF](https://arxiv.org/pdf/2112.00387v1) | `2112.00387v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2112.00387v1) |
| [Ohkura, Satoh and Van Meter 2021 -- Simultaneous execution of quantum circuits on current and near-future NISQ systems (arXiv 2112.07091)](notes/papers/2112.07091.md) | [PDF](https://arxiv.org/pdf/2112.07091v2) | `2112.07091v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2112.07091v2) |
| [Kaufman and Minzer 2022 -- Improved Optimal Testing Results from Global Hypercontractivity (arXiv 2202.08688)](notes/papers/2202.08688.md) | [PDF](https://arxiv.org/pdf/2202.08688v1) | `2202.08688v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2202.08688v1) |
| [Ren and Zhao 2023 -- The explicit twisted group algebra structure of the Cayley-Dickson algebra (arXiv 2205.07986)](notes/papers/2205.07986.md) | [PDF](https://arxiv.org/pdf/2205.07986v2) | `2205.07986v2.pdf` | [CC-BY-NC-ND-4.0](https://arxiv.org/abs/2205.07986v2) |
| [Dynamic parameterized quantum circuits: expressive and barren-plateau free](notes/papers/2411.05760.md) | [PDF](https://arxiv.org/pdf/2411.05760v3) | `2411.05760.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2411.05760v3) |
| [Reggiani 2024 -- The geometry of sedenion zero divisors (arXiv 2411.18881)](notes/papers/2411.18881.md) | [PDF](https://arxiv.org/pdf/2411.18881v1) | `2411.18881v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2411.18881v1) |
| [Quantum-Centric Algorithm for Sample-Based Krylov Diagonalization](notes/papers/2501.09702.md) | [PDF](https://arxiv.org/pdf/2501.09702v3) | `2501.09702.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2501.09702v3) |
| [Chen et al. 2025 -- Disambiguating Pauli noise in quantum computers (arXiv 2505.22629)](notes/2505.22629.md) | [PDF](https://arxiv.org/pdf/2505.22629v2) | `2505.22629.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2505.22629v2) |
| [Koebisu 2026 (v2) -- Determinant factorization for left multiplication in the sedenions (arXiv 2512.13002v2)](notes/papers/2512.13002.md) | [PDF](https://arxiv.org/pdf/2512.13002v2) | `2512.13002v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2512.13002v2) |
| [Wysocki et al.: interpretable mid-circuit measurement errors](notes/papers/2602.03938.md) | [PDF](https://arxiv.org/pdf/2602.03938v3) | `2602.03938v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2602.03938v3) |
| [Koebisu: determinant factorization in dimension 32](notes/2608.08232.md) | [PDF](https://arxiv.org/pdf/2608.08232v1) | `2608.08232v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.08232v1) |
| [Zhilina: doubly alternative zero divisors and anisotropic annihilators](notes/2608.26893.md) | [PDF](https://arxiv.org/pdf/2608.26893v1) | `2608.26893v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.26893v1) |
| [Zhilina: orthogonality graphs, Part II](notes/papers/2608.28163.md) | [PDF](https://arxiv.org/pdf/2608.28163v1) | `2608.28163v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.28163v1) |
| [Zhilina: orthogonality graphs, Part I](notes/papers/2608.28176.md) | [PDF](https://arxiv.org/pdf/2608.28176v1) | `2608.28176v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.28176v1) |
| [Coste: semialgebraic triangulation and triviality](notes/coste-semialgebraic-geometry.md) | [PDF](http://nicolas.patrois.free.fr/maths/agr%C3%A9gation/documents/semialgebraic-geometry-Coste.pdf) | `coste-semialgebraic-geometry-2002.pdf` | [Rehosting permission unestablished](https://perso.univ-rennes1.fr/michel.coste/polyens/SAG.pdf) |
| [Das et al. 2019 -- A Case for Multi-Programming Quantum Computers](notes/papers/das-2019-multiprogramming.md) | [PDF](https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf) | `das-2019-multiprogramming.pdf` | [Server redistribution requires permission](https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf) |
| [Hatcher: attachment and quotient topology](notes/hatcher-algebraic-topology.md) | [PDF](https://pi.math.cornell.edu/~hatcher/AT/ATch0.pdf) | `Hatcher-ATch0.pdf` | [Personal-copy permission](https://pi.math.cornell.edu/~hatcher/AT/ATcopyright.html) |
| [Carlstrom 2001 -- Wheels: On Division by Zero (Stockholm Research Reports in Mathematics 2001:11)](notes/wheels-carlstrom.md) | [PDF](https://www2.math.su.se/reports/2001/11/2001-11.pdf) | `carlstrom-wheels-2001-11.pdf` | [Rehosting permission unestablished](https://www2.math.su.se/reports/2001/11/) |
| [Biss, Dugger, Isaksen 2005 -- Large annihilators in Cayley-Dickson algebras (arXiv math/0511691)](notes/math-0511691.md) | [PDF](https://arxiv.org/pdf/math/0511691v1) | `math-0511691v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0511691v1) |
| [Moreno 2005 -- Constructing zero divisors in the higher dimensional Cayley-Dickson algebras (arXiv math/0512517)](notes/math-0512517.md) | [PDF](https://arxiv.org/pdf/math/0512517v1) | `math-0512517v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0512517v1) |
| [Biss, Christensen, Dugger, Isaksen 2007 -- Large annihilators in Cayley-Dickson algebras II (arXiv math/0702075)](notes/math-0702075.md) | [PDF](https://arxiv.org/pdf/math/0702075v2) | `math-0702075v2.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0702075v2) |
| [Albuquerque and Majid 1998 -- Quasialgebra structure of the octonions (arXiv math/9802116)](notes/math-9802116.md) | [PDF](https://arxiv.org/pdf/math/9802116v1) | `math-9802116v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/9802116v1) |
| [Decker and Wocjan 2007 -- Hidden quadratic and cubic polynomial function graphs (arXiv quant-ph/0703195)](notes/papers/quant-ph-0703195.md) | [PDF](https://arxiv.org/pdf/quant-ph/0703195v3) | `quant-ph-0703195v3.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/quant-ph/0703195v3) |
| [Griffiths and Niu 1996 -- Semiclassical Fourier Transform for Quantum Computation (arXiv quant-ph/9511007)](notes/papers/quant-ph-9511007.md) | [PDF](https://arxiv.org/pdf/quant-ph/9511007v1) | `quant-ph-9511007v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/quant-ph/9511007v1) |
| [Howard et al. -- Time-uniform confidence sequences](notes/papers/1810.08240.md) | [PDF](https://arxiv.org/pdf/1810.08240v9) | `1810.08240v9.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1810.08240v9) |
| [Seif et al. 2024 -- Suppressing correlated noise via context-aware compiling](notes/papers/2403.06852.md) | [PDF](https://arxiv.org/pdf/2403.06852v2) | `2403.06852v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2403.06852v2) |
| [Bylander et al. 2011 -- Noise spectroscopy through dynamical decoupling with a superconducting flux qubit](notes/papers/1101.4707.md) | [PDF](https://arxiv.org/pdf/1101.4707v1) | `1101.4707v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1101.4707v1) |
| [McKay et al. 2017 -- Efficient Z gates for quantum computing](notes/papers/1612.00858.md) | [PDF](https://arxiv.org/pdf/1612.00858v2) | `1612.00858v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1612.00858v2) |
| [Granade et al. 2012 -- Robust online Hamiltonian learning](notes/papers/1207.1655.md) | [PDF](https://arxiv.org/pdf/1207.1655v2) | `1207.1655v2.pdf` | [CC-BY-NC-SA-3.0](https://arxiv.org/abs/1207.1655v2) |
| [Sheldon et al. 2016 -- Characterizing errors on qubit operations via iterative randomized benchmarking](notes/papers/1504.06597.md) | [PDF](https://arxiv.org/pdf/1504.06597v1) | `1504.06597v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1504.06597v1) |
| [Kimmel, Low and Yoder 2015 -- Robust calibration of a universal single-qubit gate set via robust phase estimation](notes/papers/1502.02677.md) | [PDF](https://arxiv.org/pdf/1502.02677v3) | `1502.02677v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1502.02677v3) |
| [Smolin, Smith and Vargo 2013 -- Oversimplifying quantum factoring](notes/papers/1301.7007.md) | [PDF](https://arxiv.org/pdf/1301.7007v1) | `1301.7007v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1301.7007v1) |
| [Maurer and Pontil 2009 -- Empirical Bernstein bounds and sample variance penalization](notes/papers/0907.3740.md) | [PDF](https://arxiv.org/pdf/0907.3740v1) | `0907.3740v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0907.3740v1) |
| [Waudby-Smith and Ramdas 2024 -- Estimating means of bounded random variables by betting](notes/papers/2010.09686.md) | [PDF](https://arxiv.org/pdf/2010.09686v7) | `2010.09686v7.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2010.09686v7) |

| [Quantitative Curve Selection Lemma](notes/1803.00505.md) | [PDF](https://arxiv.org/pdf/1803.00505v3) | `1803.00505v3.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1803.00505v3) |
| [Rational points in henselian discrete valuation rings](notes/papers/greenberg-henselian-lifting.md) | [PDF](https://pmihes.centre-mersenne.org/item/10.1007/BF02684802.pdf) | `greenberg-1966-henselian-points.pdf` | [Source-specific rights audit](https://pmihes.centre-mersenne.org/articles/10.1007/BF02684802/) |
| [A Verified Optimizer for Quantum Circuits](notes/papers/sqir-voqc-proof-interfaces.md) | [PDF](https://arxiv.org/pdf/1912.02250v3) | `1912.02250v3.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1912.02250v3) |
| [Optimal Experiment Design for Quantum State and Process Tomography and Hamiltonian Parameter Estimation](notes/papers/quant-ph-0411093.md) | [PDF](https://arxiv.org/pdf/quant-ph/0411093v1) | `quant-ph-0411093v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/quant-ph/0411093v1) |
| [Predicting Many Properties of a Quantum System from Very Few Measurements](notes/papers/2002.08953.md) | [PDF](https://arxiv.org/pdf/2002.08953v2) | `2002.08953v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2002.08953v2) |
| [Qubits as Spectrometers of Quantum Noise](notes/cond-mat-0210247.md) | [PDF](https://arxiv.org/pdf/cond-mat/0210247v1) | `cond-mat-0210247v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/cond-mat/0210247v1) |
| [Introduction to Quantum Noise, Measurement and Amplification](notes/0810.4729.md) | [PDF](https://arxiv.org/pdf/0810.4729v2) | `0810.4729v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/0810.4729v2) |
| [Thermal and Residual Excited-State Population in a 3D Transmon Qubit](notes/1412.2772.md) | [PDF](https://arxiv.org/pdf/1412.2772v3) | `1412.2772v3.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1412.2772v3) |
| [Digital quantum simulation of linear and nonlinear optical elements](notes/1909.04408.md) | [PDF](https://arxiv.org/pdf/1909.04408v2) | `1909.04408v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1909.04408v2) |
| [Quantum coherence in the Dynamical Casimir Effect](notes/papers/1610.03272.md) | [PDF](https://arxiv.org/pdf/1610.03272v2) | `1610.03272v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1610.03272v2) |
| [Casimir energy with chiral fermions on a quantum computer](notes/papers/2105.02032.md) | [PDF](https://arxiv.org/pdf/2105.02032v1) | `2105.02032v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2105.02032v1) |
| [Efficient Classical Simulation of Continuous Variable Quantum Information Processes](notes/papers/quant-ph-0109047.md) | [PDF](https://arxiv.org/pdf/quant-ph/0109047v2) | `quant-ph-0109047v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/quant-ph/0109047v2) |
| [Circuit Quantum Electrodynamics](notes/papers/2005.12667.md) | [PDF](https://arxiv.org/pdf/2005.12667v1) | `2005.12667v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2005.12667v1) |
| [The Casimir force between real materials: experiment and theory](notes/papers/0902.4022.md) | [PDF](https://arxiv.org/pdf/0902.4022v1) | `0902.4022v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/0902.4022v1) |
| [Observation of the Dynamical Casimir Effect in a Superconducting Circuit](notes/papers/1105.4714.md) | [PDF](https://arxiv.org/pdf/1105.4714v1) | `1105.4714v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1105.4714v1) |
| [Kalia et al. 2026 -- Improved Dark Photon Sensitivity from the Dark SRF Experiment](notes/papers/2510.02427.md) | [PDF](https://arxiv.org/pdf/2510.02427v2) | `2510.02427v2.pdf` | [CC-BY-NC-SA-4.0](https://arxiv.org/abs/2510.02427v2) |
| [Banks et al. 2025 -- Searching for screened scalar forces with long-baseline atom interferometers](notes/papers/2511.09750.md) | [PDF](https://arxiv.org/pdf/2511.09750v1) | `2511.09750v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2511.09750v1) |
| [Ikeda 2023 -- Demonstration of Quantum Energy Teleportation on Superconducting Quantum Hardware](notes/papers/2301.02666.md) | [PDF](https://arxiv.org/pdf/2301.02666v5) | `2301.02666v5.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2301.02666v5) |
| [Hotta 2010 -- Energy-Entanglement Relation for Quantum Energy Teleportation](notes/papers/1002.0200.md) | [PDF](https://arxiv.org/pdf/1002.0200v2) | `1002.0200v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1002.0200v2) |
| [Ford and Roman 1997 -- Restrictions on Negative Energy Density in Flat Spacetime](notes/papers/gr-qc-9607003.md) | [PDF](https://arxiv.org/pdf/gr-qc/9607003v2) | `gr-qc-9607003v2.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/gr-qc/9607003v2) |
| [Wilmot 2025 -- Structure of the Cayley-Dickson algebras](notes/papers/2505.11747.md) | [PDF](https://arxiv.org/pdf/2505.11747v3) | `2505.11747v3.pdf` | [CC-BY-NC-SA-4.0](https://arxiv.org/abs/2505.11747v3) |
| [LZ Collaboration 2026 -- Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment](notes/papers/2609.02823.md) | [PDF](https://arxiv.org/pdf/2609.02823v1) | `2609.02823v1.pdf` | [CC-BY-NC-SA-4.0](https://arxiv.org/abs/2609.02823v1) |
| [DES Collaboration 2026 -- Dark Energy Survey Year 6 Results: Cosmological Constraints from Galaxy Clustering and Weak Lensing](notes/papers/2601.14559.md) | [PDF](https://arxiv.org/pdf/2601.14559v2) | `2601.14559v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2601.14559v2) |
| [Quantum collision models: open system dynamics from repeated interactions](notes/2106.11974.md) | [PDF](https://arxiv.org/pdf/2106.11974v2) | `2106.11974v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2106.11974v2) |
| [Childs and Wiebe 2012 -- Hamiltonian Simulation Using Linear Combinations of Unitary Operations](notes/papers/1202.5822.md) | [PDF](https://arxiv.org/pdf/1202.5822v1) | `1202.5822v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1202.5822v1) |
| [Berry, Childs, Cleve, Kothari and Somma 2014 -- Exponential improvement in precision for simulating sparse Hamiltonians](notes/papers/1312.1414.md) | [PDF](https://arxiv.org/pdf/1312.1414v2) | `1312.1414v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1312.1414v2) |
| [Kang and Su 2026 -- Quantum matrix arithmetics with Hamiltonian evolution](notes/papers/2510.06316.md) | [PDF](https://arxiv.org/pdf/2510.06316v3) | `2510.06316v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2510.06316v3) |
| [Wang et al. 2009 -- Decoherence Dynamics of Complex Photon States in a Superconducting Circuit](notes/papers/0909.4585.md) | [PDF](https://arxiv.org/pdf/0909.4585v1) | `0909.4585v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0909.4585v1) |
| [Murch, Weber, Macklin and Siddiqi 2013 -- Observing single quantum trajectories of a superconducting qubit](notes/papers/1305.7270.md) | [PDF](https://arxiv.org/pdf/1305.7270v2) | `1305.7270v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1305.7270v2) |
| [Cramer et al. 2010 -- Efficient quantum state tomography](notes/papers/1101.4366.md) | [PDF](https://arxiv.org/pdf/1101.4366v1) | `1101.4366v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1101.4366v1) |
| [Brown 1972 -- Structure of Zero Divisors, and Other Algebraic Structures, in Higher Dimensional Real Cayley-Dickson Algebras (PhD dissertation, Univ. of Missouri--Rolla)](notes/papers/brown-1972-dissertation.md) | [Dissertation record](https://scholarsmine.mst.edu/doctoral_dissertations/2088) | — | [Open access](https://scholarsmine.mst.edu/doctoral_dissertations/2088) |
| [Moreno 1997 -- The Zero Divisors of the Cayley-Dickson Algebras over the Real Numbers (arXiv q-alg/9710013)](notes/papers/q-alg-9710013.md) | [PDF](https://arxiv.org/pdf/q-alg/9710013v1) | `q-alg-9710013v1.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/q-alg/9710013v1) |
| [De Marrais 2000 -- The 42 Assessors and the Box-Kites They Fly (arXiv math/0011260)](notes/papers/math-0011260.md) | [PDF](https://arxiv.org/pdf/math/0011260v1) | `math-0011260v1.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0011260v1) |
| [Baez 2002 -- The Octonions](notes/papers/math-0105155.md) | [PDF](https://arxiv.org/pdf/math/0105155v4) | `math-0105155v4.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0105155v4) |
| [De Marrais 2002 -- Flying Higher Than a Box-Kite: Kite-Chain Middens, Sand Mandalas, and Zero-Divisor Patterns in the 2^n-ions Beyond the Sedenions (arXiv math/0207003)](notes/papers/math-0207003.md) | [PDF](https://arxiv.org/pdf/math/0207003v2) | `math-0207003v2.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0207003v2) |
| [De Marrais 2004 -- Box-Kites III: Quizzical Quaternions, Mock Octonions, and Other Zero-Divisor-Suppressing Structures (arXiv math/0403113)](notes/math-0403113.md) | [PDF](https://arxiv.org/pdf/math/0403113v1) | `math-0403113v1.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0403113v1) |
| [De Marrais 2006 -- Presto! Digitization, Part I (arXiv math/0603281)](notes/papers/math-0603281.md) | [PDF](https://arxiv.org/pdf/math/0603281v1) | `math-0603281v1.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0603281v1) |
| [De Marrais 2007 -- Placeholder Substructures I (arXiv math/0703745; Complex Systems 17, 125-142)](notes/papers/math-0703745.md) | [PDF](https://arxiv.org/pdf/math/0703745v3) | `math-0703745v3.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0703745v3) |
| [De Marrais 2007 -- Placeholder Substructures II (arXiv 0704.0026)](notes/papers/0704-0026.md) | [PDF](https://arxiv.org/pdf/0704.0026v3) | `0704.0026v3.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/0704.0026v3) |
| [De Marrais 2007 -- Placeholder Substructures III (arXiv 0704.0112)](notes/papers/0704-0112.md) | [PDF](https://arxiv.org/pdf/0704.0112v3) | `0704.0112v3.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/0704.0112v3) |
| [Guterman and Zhilina 2021 -- Relation Graphs of the Sedenion Algebra (J. Math. Sci. 255(3), 254-270, DOI 10.1007/s10958-021-05367-6; arXiv 2608.26903 is the same work)](notes/papers/2608-26903.md) | [PDF](https://arxiv.org/pdf/2608.26903v1) | `2608.26903v1.pdf` | [ArXiv non-exclusive distribution grant](https://arxiv.org/abs/2608.26903v1) |
| [Procopio et al. 2017 -- Experimental Test of Hyper-Complex Quantum Theories](notes/papers/1602.01624.md) | [PDF](https://arxiv.org/pdf/1602.01624v2) | `1602.01624v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1602.01624v2) |
| [Adler 2017 -- Does the Peres experiment using photons test for hyper-complex (quaternionic) quantum theories?](notes/papers/1604.04950.md) | [PDF](https://arxiv.org/pdf/1604.04950v3) | `1604.04950v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1604.04950v3) |
| [Procopio, Rozema, Dakic and Walther 2017 -- Comment on Adler's Peres-experiment critique](notes/papers/1607.01648.md) | [PDF](https://arxiv.org/pdf/1607.01648v1) | `1607.01648v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1607.01648v1) |
| [Iqbal et al. 2024 -- Non-Abelian Topological Order and Anyons on a Trapped-Ion Processor](notes/papers/2305.03766.md) | [PDF](https://arxiv.org/pdf/2305.03766v2) | `2305.03766v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2305.03766v2) |
| [Rol et al. 2019 -- Net Zero flux-pulsed CZ (arXiv 1903.02492)](notes/papers/1903.02492.md) | [PDF](https://arxiv.org/pdf/1903.02492v1) | `1903.02492v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1903.02492v1) |
| [Negirneac et al. 2021 -- Sudden Net Zero CZ (arXiv 2008.07411)](notes/papers/2008.07411.md) | [PDF](https://arxiv.org/pdf/2008.07411v1) | `2008.07411v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2008.07411v1) |
| [Marques et al. 2022 -- error-detecting surface code on a 7-transmon chip (arXiv 2102.13071)](notes/papers/2102.13071.md) | [PDF](https://arxiv.org/pdf/2102.13071v1) | `2102.13071v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2102.13071v1) |
| [Fu et al. 2017 -- QuMA control microarchitecture (arXiv 1708.07677)](notes/papers/1708.07677.md) | [PDF](https://arxiv.org/pdf/1708.07677v1) | `1708.07677v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1708.07677v1) |
| [Fu et al. 2019 -- eQASM executable instruction set (arXiv 1808.02449)](notes/papers/1808.02449.md) | [PDF](https://arxiv.org/pdf/1808.02449v3) | `1808.02449v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1808.02449v3) |
| [Klimov et al. 2018 -- T1 fluctuations and two-level-system defects (arXiv 1809.01043)](notes/papers/1809.01043.md) | [PDF](https://arxiv.org/pdf/1809.01043v1) | `1809.01043v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1809.01043v1) |
| [Schloer et al. 2019 -- burst noise from single fluctuators (arXiv 1901.05352)](notes/papers/1901.05352.md) | [PDF](https://arxiv.org/pdf/1901.05352v2) | `1901.05352v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1901.05352v2) |
| [Sung et al. 2019 -- non-Gaussian noise spectroscopy with a flux qubit (arXiv 1903.01043)](notes/papers/1903.01043.md) | [PDF](https://arxiv.org/pdf/1903.01043v2) | `1903.01043v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1903.01043v2) |
| [Bravyi et al. 2021 -- mitigating measurement errors (arXiv 2006.14044)](notes/papers/2006.14044.md) | [PDF](https://arxiv.org/pdf/2006.14044v2) | `2006.14044v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2006.14044v2) |
| [Heinsoo et al. 2018 -- multiplexed readout crosstalk (arXiv 1801.07904)](notes/papers/1801.07904.md) | [PDF](https://arxiv.org/pdf/1801.07904v1) | `1801.07904v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1801.07904v1) |
| [Geller 2020 -- rigorous measurement error correction (arXiv 2002.01471)](notes/papers/2002.01471.md) | [PDF](https://arxiv.org/pdf/2002.01471v2) | `2002.01471v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2002.01471v2) |
| [Sank et al. 2016 -- measurement-induced state transitions (arXiv 1606.05721)](notes/papers/1606.05721.md) | [PDF](https://arxiv.org/pdf/1606.05721v2) | `1606.05721v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1606.05721v2) |
| [Maring et al. 2024 -- A versatile single-photon-based quantum computing platform (arXiv 2306.00874; Nature Photonics 18, 603)](notes/papers/2306.00874.md) | [PDF](https://arxiv.org/pdf/2306.00874v1) | `2306.00874v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2306.00874v1) |
| [Tully, Washburn and Simons 2026 -- Characterization of nested Walsh parity-check filters on a cloud photonic processor (arXiv 2606.18408)](notes/papers/2606.18408.md) | [PDF](https://arxiv.org/pdf/2606.18408v2) | `2606.18408v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2606.18408v2) |
| [Ollivier et al. 2021 -- Hong-Ou-Mandel interference with imperfect single photon sources (arXiv 2005.01743)](notes/papers/2005.01743.md) | [PDF](https://arxiv.org/pdf/2005.01743v1) | `2005.01743v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2005.01743v1) |
| [White et al. 2020 -- Demonstration of non-Markovian process characterisation and control on a quantum processor (arXiv 2004.14018)](notes/papers/2004.14018.md) | [PDF](https://arxiv.org/pdf/2004.14018v2) | `2004.14018v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2004.14018v2) |
| [Toth and Guhne 2005 -- Entanglement detection in the stabilizer formalism (arXiv quant-ph/0501020)](notes/papers/quant-ph-0501020.md) | [PDF](https://arxiv.org/pdf/quant-ph/0501020v2) | `quant-ph-0501020v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/quant-ph/0501020v2) |
| [Riley 2008 -- Handbook of Frequency Stability Analysis (NIST Special Publication 1065)](notes/papers/riley-2008-nist-sp-1065.md) | [PDF](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication1065.pdf) | `riley-2008-nist-sp-1065.pdf` | [Rehosting permission unestablished](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications) |

## Licensed software source snapshots
The [Nebe--Sloane lattice catalogue note](notes/papers/nebe-lattices-d14-a13.md)
records the inspected D14 (dimension 14, determinant 4) and A13 (dimension
13, determinant 14) entries used as independent checks of the repository's
assessor-blade lattice identifications. The [AFLOW prototype
note](notes/papers/aflow-a_cf4-225-a.md) records the inspected A_cF4_225_a
face-centered-cubic (Cu-type, Fm-3m) designation used as the
crystallographic comparison prototype. Both are external web references;
response hashes identify the inspected bytes.


These archives preserve the exact original upstream bytes and license notices.
Source inspection supplies candidate proof interfaces and independent
implementations to cross-check; build compatibility remains a separate gate. Archive/member hashes and license text
are checked by `verify_sources.py` without extraction or execution.

| Source | Original archive | License |
| --- | --- | --- |
| [SQIR / VOQC](notes/papers/sqir-voqc-proof-interfaces.md) | [sqir-134fb94.tar.gz](source_archives/sqir-134fb94.tar.gz) | MIT |
| [CoqInterval](notes/papers/coqinterval-certified-enclosures.md) | [interval-4.11.5.tar.gz](source_archives/interval-4.11.5.tar.gz) | CECILL-C |
| [Mathematical Components](notes/papers/mathcomp-coqeal-matrix-certificates.md) | [mathcomp-9931c88.tar.gz](source_archives/mathcomp-9931c88.tar.gz) | CECILL-B |
| [CoqEAL](notes/papers/mathcomp-coqeal-matrix-certificates.md) | [coqeal-8fd26cf.tar.gz](source_archives/coqeal-8fd26cf.tar.gz) | MIT |
| [wheel (Rust crate)](notes/wheel-rust-crate.md) | [wheel-0.1.0.crate](source_archives/wheel-0.1.0.crate) | Apache-2.0 OR MPL-2.0 |

## Repository research certificates

The [continuous four-coordinate rank derivation](notes/four_support_rank_loci.md)
and its [exact replay](evidence/four_support_rank/README.md) classify a
specified real coefficient family and construct its kernel frames.
The [incidence geometry](notes/four_support_incidence_geometry.md) refines
the unit coefficient sphere into 96 connected smooth strata, certifies
their closures, and constructs an explicit partner-incidence homeomorphism.
Both derivations attribute the published annihilator results and keep
the wider topology obligations explicit.

The [ordinary-doubling proof](notes/four_support_doubling.md) extends
the same support and complete kernel model to every higher stage. Its
[replay](evidence/four_support_doubling/README.md) checks the finite expanded
identities separately from the structural induction. The
[cellular model](notes/four_support_cellular_homology.md) and
[integral replay](evidence/four_support_homology/README.md) identify 1,200 CW
cells, certify integral homology and zero torsion, and determine the
cohomology ring for the restricted pair space.

The [dimension-32 skew-Schur charts](notes/dimension32_skew_schur_charts.md)
and their [exact replay](evidence/dimension32_skew_schur/README.md) retain
rank-changing points in all 30 doubly-pure coefficient directions on each
admitted pivot domain. Complete kernel lifts, inverse coordinates and the
induced metric describe the local incidence. Two exact paths with the same
initial tangent and different nearby ranks expose the limit of linearization.
The [principal atlas](notes/principal_skew_atlas.md) and its
[replay](evidence/principal_skew_atlas/README.md) supply an explicit covering
family with 15 domains in dimension 32, a conditioned initial-pivot selector,
and verified kernel-restricted overlap identities. The same construction
covers every higher stage. Computed smooth strata, global attachments, and
unrestricted topology remain separate obligations.

The [Schur acceleration certificates](notes/schur_acceleration_certificates.md)
and their [replay](evidence/schur_acceleration/README.md) separate first-order
admission, second-order compatibility, and exact obstruction witnesses. A
nullity-12 example passes the linear constraints but fails a necessary
quadratic tangent condition. Compatible acceleration certificates describe
formal second-order solutions. The
[selected-center proof](notes/nullity_twelve_local_geometry.md) and
[replay](evidence/nullity_twelve_locus/README.md) also construct actual curves
and prove the complete Bouligand cone `A15 union B17`, with intersection
dimension thirteen, at `e1+e18` on the doubly-pure dimension-32,
norm-squared-two nullity-twelve locus. Exact CPU certificates and written
arguments establish that result; a Rocq port, other centers, neighborhood
branches and attachments remain separate obligations.
The [two-dimension gap design](notes/rank_locus_two_dimension_gap.md)
plans the exact computations that decide whether the A_5 rank-locus families
with a non-zero-divisor entry gain two dimensions through e_8 and e_24, and
orders roadmap items 3 to 8 behind D_(5,12).

The [finite field-model replay](evidence/vacuum_models/README.md) checks
invariant-sector encoding, observable-specific cutoff bias, synthesis error,
and a device-noise SPAM counterexample. The
[opportunity map](notes/vacuum_field_run_opportunities.md) declares controls,
classical references, physical boundaries, costs and next admission gates.
The [proof/experiment synthesis](notes/research_proof_experiment_dependencies.md)
connects those results to the geometry, Rocq and inference dependencies.

The [endpoint information replay](evidence/vacuum_endpoint_information/README.md)
records matched-shot precision, same-shot covariance and the four/seven/nine
product-Pauli setting distinctions. Its finite ideal-readout results leave
hardware fidelity and charged-time gains as separate measurement gates.
The [historical dispatch ledger](../plans/QUANTUM_DISPATCH.md) records owners,
dependencies, research scope and the human-supplied execution gates.

The [kernel attachment proof](notes/annihilator_kernel_limits.md) and its
[replay](evidence/kernel_limits/README.md) retain complete limiting projector
certificates, a three-coefficient real cone classification, global kernel
frames, actual mapping cylinders and restricted integral invariants. Ordinary
embedding extends this cone family to every higher stage. The attachment
image differs from the total incidence; unrestricted topology remains open.

The [complex skew rank geometry](notes/complex_skew_rank_geometry.md) and its
[exact replay](evidence/complex_skew/README.md) certify the all-stage
conjugate-linear representation, exhaustive Pfaffian predicates, coefficient
pair cover and metric-preserving kernel transitions. In dimension 32 the
cover uses fifteen domains and 16-by-16 complex matrices. Real components,
strata and unrestricted attachments remain open.

The [singular-sector note](notes/singular_sector_dynamics.md) and its
[FakeFez record](evidence/singular_sector_dynamics/fakefez_amplification.json)
split every two-term Cayley-Dickson element into dark, bright and anticommuting
sectors, derive the stratum census from one diagonal sign, and price the
frozen amplitude-amplification walk and its virtual-Z echo control.

## Ripple source supplement

The [De Marrais Box-Kites III note](notes/math-0403113.md) records a bounded
reading of an unversioned local copy, its content hash, and the box-kite
sign conventions used by the ripple experiment. The reading copy remains in
ignored `docs/local_source_cache/`; its unestablished version and publication
permission keep it outside the version-qualified PDF registry. The
[measurement-design synthesis](notes/reality_ripple_measurement_design.md)
connects that source to the circuit observables and prior work.

## Verification and research navigation

Run from the repository root:

```sh
set -eu
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/verify_sources.py
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/check_verify_sources.py
sha256sum -c docs/PDF_SHA256SUMS
```

[Library overview](sources/README.md) maps paper relevance. [Numerics](notes/topics/numerics_best_practice.md)
collects the conditioning, precision, vectorization and runtime-package rules. The
[coordinated roadmap](RESEARCH_ROADMAP.md) retains the cumulative mathematics,
proof, optimizer, review, and hardware obligations. The next hardware priority
remains model discrimination followed by a measured optimizer decision before
broad atlas expenditure. Each new physical case requires its own approval.

## IBM Runtime documentation

The [execution-guide note](notes/ibm-runtime-execution-guides.md) records nine IBM Quantum documentation pages
(workload usage, stretch, Sampler options, Sampler inputs and outputs, run-time minimization,
the client-side Sampler API, real-time backend-property refresh, circuit timing and execution modes) with retrieval SHA-256 and the use each page is cited for.

The [Heron r2 platform note](notes/ibm_heron_platform.md) records the live Targets of ibm_fez, ibm_kingston and ibm_marrakesh
(measurement variants, xslow, alignment, repetition-delay range, fractional-gate errors) retained in
[targets.json](evidence/heron_platform/targets.json), and nine further IBM pages (billing, repetition rate, calibration,
fractional gates, stretch, circuit timing, processor types, dynamic circuits, runtime release notes) with retrieval SHA-256.
The [Heron and ISA reference guides](notes/ibm_quantum/README.md) retain transcribed Markdown reference copies of the core
guides covering processor architectures, backend instruction sets, transpilation to ISA circuits, dynamic circuits, fractional gates,
timing, and calibration, each with an upstream link to the full online piece.
The [Heron r2 readout resonator note](notes/ibm_quantum/heron-r2-readout-resonator.md) records the public evidence
for ibm_fez, ibm_kingston and ibm_marrakesh readout, each source and value tagged by processor revision, and binds
nine arXiv HTML renderings (2604.25863v3, 2604.03360v2, 2606.00433v2, 2412.04053v2, 2305.10508v1, 2407.14431v3,
2308.13065v2, 2406.07611v2, 2402.17833v2) by SHA-256 in [SOURCES.json](SOURCES.json); the retained
[backend configuration snapshot](evidence/heron_platform/backend_configuration.json) holds the sorted configuration
key names of the three account backends.
The [hardware controls audit](notes/ibm_quantum/hardware-controls.md) inventories every option field, REST endpoint
and client-side restriction of the installed qiskit-ibm-runtime 0.50.0 in
[inventory.json](evidence/ibm_runtime_options/inventory.json) (gate core-533), records read-only backend limits
(max_shots, rep_delay range, measure_2, fractional angle bounds) in
[backends.json](evidence/ibm_runtime_options/backends.json), and states the configuration per workload type with the
gaps between live_run.py and it.
The [Heron r2 tile packing note](notes/heron_spatial_multiprogramming.md) packs guard-banded tiles on the
snapshot coupling map, composes one circuit per tile into one wide circuit, and states per-backend RZZ and
repetition-delay arithmetic from Target values, audited in
[spatial_multiprogramming_audit.json](evidence/heron_platform/spatial_multiprogramming_audit.json).
The [N=21 feed-forward backend note](notes/topics/n21_feedforward_backends.md) states the real-time conditioned-gate requirement of
the n21-feedback-encoded family, what IQM cc_prx and measure_ff express, the Open Quantum shot arithmetic on Garnet and
Emerald, and a provider survey with access terms, each web source dated.

The [Hoeffding note](notes/papers/hoeffding-1963.md) cites the 1963 inequality behind the admission contracts by DOI.
The [measurement-foundations web note](notes/papers/measurement_foundations_web_sources.md) records the 3 February 2025 removal
of pulse-level control, the Qiskit Experiments 0.14.2 tomography pages, and the Crossref identities of the
Steffen 2006 and Hofheinz 2009 superconducting tomography papers.
The [hypercomplex and anyon Crossref note](notes/papers/hypercomplex_quantum_crossref_records.md) binds the
versions of record of the hypercomplex-theory exchange and the two non-Abelian anyon experiments.
The [associator audit](evidence/reviewer_associator_audit/PROVENANCE.md) retains the arithmetic behind the
algebra circuit design rules of docs/notes/algebra_circuit_rules.md.

## Operational instrument source identities

The [instrument source note](notes/papers/operational-instrument-sources.md) records primary arXiv identities,
abstract reading scopes, the incorrect draft citation and the prior single-spin parity-time experiment.

## Hypercomplex operator audit sources

- [1806.00612v1](notes/papers/1806.00612.md): $SU(3)_C\times SU(2)_L\times U(1)_Y\left( \times U(1)_X \right)$ as a symmetry of division algebraic ladder operators
- [2409.17948v2](notes/papers/2409.17948.md): Three Generations and a Trio of Trialities
- [2607.18450v3](notes/papers/2607.18450.md): Standard Model Symmetries and the Nested Embeddings of $\mathbb{R}\subset\mathbb{C}\subset\mathbb{H}\subset\mathbb{O}$
- [2505.07923v4](notes/papers/2505.07923.md): A Superalgebra Within: representations of lightest standard model particles form a $\mathbb{Z}_2^5$-graded algebra
- [2604.24795v1](notes/papers/2604.24795.md): Higgs Sector and Flavour Structure in an Algebraic Three-Generation Model with S3 Family Symmetry
- [quant-ph/0307017v2](notes/papers/quant-ph-0307017.md): Quaternionic Computing
- [1709.09246v3](notes/papers/1709.09246.md): Quantum theory in quaternionic Hilbert space: How Poincar\&#39;e symmetry reduces the theory to the standard complex one
- [2608.20259v1](notes/papers/2608.20259.md): Operational Foundations for Quaternionic and Octonionic Quantum Models: Exact Quaternionic Channels and Error Correction, Para-Linear Operators, and Categorical Closure Boundaries Beyond Associativity

- [Quaternionic foundational source review](notes/papers/quaternionic-foundational-source-review.md): verified historical citation identities, abstract-level claims and explicit body-reading obligations.
- [Quaternionic optical bound reading](notes/papers/quaternionic-optical-bound-reading.md): exact-version Procopio/Adler exchange, reported 0.03-degree phase bound, insensitive case and scattering assumptions; successor reading scope to the three abstract notes.
