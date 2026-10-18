# Source index

The source library separates repository-hosted papers from local reading copies.
All source notes, retrieval URLs, original byte identities, and reading scopes remain
public in [SOURCES.json](SOURCES.json) and the linked notes. License evidence
controls PDF hosting; availability for download alone supplies no downstream grant.

| Location | Contents | Git treatment |
| --- | --- | --- |
| `docs/pdf/` | 23 unchanged PDFs with source-specific CC BY 4.0 or CC0 evidence, plus two aliases | Tracked |
| `docs/local_source_cache/` | 85 optional original reading copies with restricted or unestablished rehosting permission | Ignored |
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
| [Kissinger and Meijer-van de Griend 2019 -- CNOT circuit extraction for topologically-constrained quantum memories (arXiv 1904.00633)](notes/1904.00633.md) | [1904.00633v2.pdf](pdf/1904.00633v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Sarovar et al. 2020 -- Detecting crosstalk errors in quantum information processors](notes/1908.09855.md) | [1908.09855v3.pdf](pdf/1908.09855v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Corcoles et al. 2021 -- Exploiting dynamic quantum circuits in a quantum algorithm with superconducting qubits (arXiv 2102.01682)](notes/2102.01682.md) | [2102.01682.pdf](pdf/2102.01682.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Niu and Todri-Sanial 2023 -- Enabling Multi-programming Mechanism for Quantum Computing in the NISQ Era (arXiv 2102.05321)](notes/2102.05321.md) | [2102.05321v3.pdf](pdf/2102.05321v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Gidney 2025 -- How to factor 2048 bit RSA integers with less than a million noisy qubits (arXiv 2505.15917)](notes/2505.15917.md) | [2505.15917.pdf](pdf/2505.15917.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Cobos et al. 2025 -- Real-Time Dynamics in a (2+1)-D Gauge Theory: The Stringy Nature on a Superconducting Quantum Simulator (arXiv 2507.08088)](notes/2507.08088.md) | [2507.08088.pdf](pdf/2507.08088.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Pokharel et al. 2025 -- Order from chaos with adaptive circuits on quantum hardware (arXiv 2509.18259)](notes/2509.18259.md) | [2509.18259.pdf](pdf/2509.18259.pdf) | [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [Levratti: active stabilizers and Cayley-Dickson zero-divisor supports](notes/levratti-2026-active-stabilizers.md) | [levratti-2026-active-stabilizers.pdf](pdf/levratti-2026-active-stabilizers.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Levratti 2026 -- Fano Duality, Projective Orthogonality and the CSS Bridge (author-hosted manuscript)](notes/levratti-2026-fano-css.md) | [levratti-2026-fano-css.pdf](pdf/levratti-2026-fano-css.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Covariant quantum kernels for data with group structure](notes/s41567-023-02340-9.md) | [2105.03406.pdf](pdf/2105.03406.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Challenges and opportunities in quantum optimization](notes/s42254-024-00770-9.md) | [2312.02279.pdf](pdf/2312.02279.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Baeumer et al. 2024 -- Quantum Fourier transform using dynamic circuits (arXiv 2403.09514)](notes/2403.09514.md) | [2403.09514v2.pdf](pdf/2403.09514v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |

| [Proving Quantum Programs Correct](notes/sqir-voqc-proof-interfaces.md) | [LIPIcs.ITP.2021.21.pdf](pdf/LIPIcs.ITP.2021.21.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Gate Set Tomography](notes/2009.07301.md) | [2009.07301.pdf](pdf/2009.07301.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Latency considerations for stochastic optimizers in variational quantum algorithms](notes/2201.13438.md) | [2201.13438.pdf](pdf/2201.13438.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Brotherton et al. 2025 -- Any Light Particle Searches with ALPS II: first science results](notes/2512.14110.md) | [2512.14110v3.pdf](pdf/2512.14110v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Wei et al. 2026 -- New Constraints on Dark Photon Dark Matter with a Millimeter-Wave Dielectric Haloscope](notes/2503.23354.md) | [2503.23354v2.pdf](pdf/2503.23354v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Fosco and Guntsche 2026 -- Dynamical Casimir effect in the worldline formulation](notes/2604.13237.md) | [2604.13237v3.pdf](pdf/2604.13237v3.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Ma et al. 2026 -- Prediction of a measurable sign change in the Casimir force using a magnetic fluid](notes/2601.00483.md) | [2601.00483v1.pdf](pdf/2601.00483v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Kang et al. 2025 -- Scalable architecture for dark photon searches: Superconducting-qubit proof of principle](notes/2503.18315.md) | [2503.18315v1.pdf](pdf/2503.18315v1.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Google Quantum AI and Collaborators 2023 -- Non-Abelian braiding of graph vertices in a superconducting processor](notes/2210.10255.md) | [2210.10255v2.pdf](pdf/2210.10255v2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Matsumoto et al. 2026 -- Two-qubit logic and teleportation with mobile spin qubits in silicon (Nature 653, 391)](notes/s41586-026-10423-9.md) | [s41586-026-10423-9.pdf](pdf/s41586-026-10423-9.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Wu et al. 2026 -- Simultaneous high-fidelity single-qubit gates in a spin qubit array (Nature Physics)](notes/s41567-026-03466-2.md) | [s41567-026-03466-2.pdf](pdf/s41567-026-03466-2.pdf) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) |

The two Nature aliases identify retained arXiv preprints, with their own
licenses and versions. The aliases do not identify the publisher versions.

## External papers and local reading copies

ArXiv-only hosting grants, personal-copy terms, and unresolved author permission
lead to external-only entries. The classification records the evidence inspected;
exclusion from hosting does not assert that every possible reuse is forbidden.

| Source note | Original download | Local filename in `docs/local_source_cache/` | Hosting evidence |
| --- | --- | --- | --- |
| [Roetteler 2008 -- Quantum algorithms for highly non-linear Boolean functions (arXiv 0811.3208)](notes/0811.3208.md) | [PDF](https://arxiv.org/pdf/0811.3208v2) | `0811.3208v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0811.3208v2) |
| [Biss, Christensen, Dugger, Isaksen 2009 -- Eigentheory of Cayley-Dickson algebras (arXiv 0905.2987)](notes/0905.2987.md) | [PDF](https://arxiv.org/pdf/0905.2987v1) | `0905.2987v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0905.2987v1) |
| [Roetteler 2009 -- Hidden shift for quadratics and for functions of large Gowers norm (arXiv 0911.4724)](notes/0911.4724.md) | [PDF](https://arxiv.org/pdf/0911.4724v1) | `0911.4724v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0911.4724v1) |
| [Gavinsky, Roetteler, Roland 2011 -- Quantum algorithm for the Boolean hidden shift problem (arXiv 1103.3017)](notes/1103.3017.md) | [PDF](https://arxiv.org/pdf/1103.3017v1) | `1103.3017v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1103.3017v1) |
| [Decker, Ivanyos, Santha, Wocjan 2011 -- Hidden Symmetry Subgroup Problems (arXiv 1107.2189)](notes/1107.2189.md) | [PDF](https://arxiv.org/pdf/1107.2189v2) | `1107.2189v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1107.2189v2) |
| [Martin-Lopez et al. 2012 -- Experimental realization of Shor's quantum factoring algorithm using qubit recycling (arXiv 1111.4147)](notes/1111.4147.md) | [PDF](https://arxiv.org/pdf/1111.4147v2) | `1111.4147v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1111.4147v2) |
| [Gambetta et al. 2012 -- Characterization of addressability by simultaneous randomized benchmarking](notes/1204.6308.md) | [PDF](https://arxiv.org/pdf/1204.6308v2) | `1204.6308v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1204.6308v2) |
| [Kirshtein 2012 -- Multiplication groups and inner mapping groups of Cayley-Dickson loops (arXiv 1207.4230)](notes/1207.4230.md) | [PDF](https://arxiv.org/pdf/1207.4230v1) | `1207.4230v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1207.4230v1) |
| [Bremner, Montanaro and Shepherd -- approximate IQP sampling and cubic phases](notes/1504.07999.md) | [PDF](https://arxiv.org/pdf/1504.07999v2) | `1504.07999v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1504.07999v2) |
| [Bales 2016 -- An alternate Cayley-Dickson product (arXiv 1602.02317)](notes/1602.02317.md) | [PDF](https://arxiv.org/pdf/1602.02317v1) | `1602.02317v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1602.02317v1) |
| [Bales 2016 -- Periodicity of the Cayley-Dickson twists (arXiv 1602.02843)](notes/1602.02843.md) | [PDF](https://arxiv.org/pdf/1602.02843v3) | `1602.02843v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1602.02843v3) |
| [Gilyen, Su, Low, and Wiebe 2018 -- Quantum singular value transformation and beyond: exponential improvements for quantum matrix arithmetics (arXiv 1806.01838)](notes/1806.01838.md) | [PDF](https://arxiv.org/pdf/1806.01838v1) | `1806.01838v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1806.01838v1) |
| [Rudinger et al. 2019 -- Probing context-dependent errors in quantum processors](notes/1810.05651.md) | [PDF](https://arxiv.org/pdf/1810.05651v1) | `1810.05651v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1810.05651v1) |
| [Freedman, Shokrian-Zini, and Wang 2019 -- Quantum computing with octonions (arXiv 1811.08580)](notes/1811.08580.md) | [PDF](https://arxiv.org/pdf/1811.08580v5) | `1811.08580v5.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1811.08580v5) |
| [Proctor et al. 2020 -- Detecting and tracking drift in quantum information processors](notes/1907.13608.md) | [PDF](https://arxiv.org/pdf/1907.13608v3) | `1907.13608v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1907.13608v3) |
| [Rudinger et al.: quantum-instrument tomography of mid-circuit measurement](notes/2103.03008.md) | [PDF](https://arxiv.org/pdf/2103.03008v1) | `2103.03008v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2103.03008v1) |
| [Resch et al. 2021 -- Accelerating Variational Quantum Algorithms Using Circuit Concurrency (arXiv 2109.01714)](notes/2109.01714.md) | [PDF](https://arxiv.org/pdf/2109.01714v1) | `2109.01714v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2109.01714v1) |
| [Niu and Todri-Sanial 2021 -- How Parallel Circuit Execution Can Be Useful for NISQ Computing? (arXiv 2112.00387)](notes/2112.00387.md) | [PDF](https://arxiv.org/pdf/2112.00387v1) | `2112.00387v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2112.00387v1) |
| [Ohkura, Satoh and Van Meter 2021 -- Simultaneous execution of quantum circuits on current and near-future NISQ systems (arXiv 2112.07091)](notes/2112.07091.md) | [PDF](https://arxiv.org/pdf/2112.07091v2) | `2112.07091v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2112.07091v2) |
| [Kaufman and Minzer 2022 -- Improved Optimal Testing Results from Global Hypercontractivity (arXiv 2202.08688)](notes/2202.08688.md) | [PDF](https://arxiv.org/pdf/2202.08688v1) | `2202.08688v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2202.08688v1) |
| [Dynamic parameterized quantum circuits: expressive and barren-plateau free](notes/2411.05760.md) | [PDF](https://arxiv.org/pdf/2411.05760v3) | `2411.05760.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2411.05760v3) |
| [Reggiani 2024 -- The geometry of sedenion zero divisors (arXiv 2411.18881)](notes/2411.18881.md) | [PDF](https://arxiv.org/pdf/2411.18881v1) | `2411.18881v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2411.18881v1) |
| [Quantum-Centric Algorithm for Sample-Based Krylov Diagonalization](notes/2501.09702.md) | [PDF](https://arxiv.org/pdf/2501.09702v3) | `2501.09702.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2501.09702v3) |
| [Chen et al. 2025 -- Disambiguating Pauli noise in quantum computers (arXiv 2505.22629)](notes/2505.22629.md) | [PDF](https://arxiv.org/pdf/2505.22629v2) | `2505.22629.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2505.22629v2) |
| [Koebisu 2026 (v2) -- Determinant factorization for left multiplication in the sedenions (arXiv 2512.13002v2)](notes/2512.13002.md) | [PDF](https://arxiv.org/pdf/2512.13002v2) | `2512.13002v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2512.13002v2) |
| [Wysocki et al.: interpretable mid-circuit measurement errors](notes/2602.03938.md) | [PDF](https://arxiv.org/pdf/2602.03938v3) | `2602.03938v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2602.03938v3) |
| [Koebisu: determinant factorization in dimension 32](notes/2608.08232.md) | [PDF](https://arxiv.org/pdf/2608.08232v1) | `2608.08232v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.08232v1) |
| [Zhilina: doubly alternative zero divisors and anisotropic annihilators](notes/2608.26893.md) | [PDF](https://arxiv.org/pdf/2608.26893v1) | `2608.26893v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.26893v1) |
| [Zhilina: orthogonality graphs, Part II](notes/2608.28163.md) | [PDF](https://arxiv.org/pdf/2608.28163v1) | `2608.28163v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.28163v1) |
| [Zhilina: orthogonality graphs, Part I](notes/2608.28176.md) | [PDF](https://arxiv.org/pdf/2608.28176v1) | `2608.28176v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2608.28176v1) |
| [Coste: semialgebraic triangulation and triviality](notes/coste-semialgebraic-geometry.md) | [PDF](http://nicolas.patrois.free.fr/maths/agr%C3%A9gation/documents/semialgebraic-geometry-Coste.pdf) | `coste-semialgebraic-geometry-2002.pdf` | [Rehosting permission unestablished](https://perso.univ-rennes1.fr/michel.coste/polyens/SAG.pdf) |
| [Das et al. 2019 -- A Case for Multi-Programming Quantum Computers](notes/das-2019-multiprogramming.md) | [PDF](https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf) | `das-2019-multiprogramming.pdf` | [Server redistribution requires permission](https://fast.cc.gatech.edu/papers/MICRO_2019_4.pdf) |
| [Hatcher: attachment and quotient topology](notes/hatcher-algebraic-topology.md) | [PDF](https://pi.math.cornell.edu/~hatcher/AT/ATch0.pdf) | `Hatcher-ATch0.pdf` | [Personal-copy permission](https://pi.math.cornell.edu/~hatcher/AT/ATcopyright.html) |
| [Carlstrom 2001 -- Wheels: On Division by Zero (Stockholm Research Reports in Mathematics 2001:11)](notes/wheels-carlstrom.md) | [PDF](https://www2.math.su.se/reports/2001/11/2001-11.pdf) | `carlstrom-wheels-2001-11.pdf` | [Rehosting permission unestablished](https://www2.math.su.se/reports/2001/11/) |
| [Biss, Dugger, Isaksen 2005 -- Large annihilators in Cayley-Dickson algebras (arXiv math/0511691)](notes/math-0511691.md) | [PDF](https://arxiv.org/pdf/math/0511691v1) | `math-0511691v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0511691v1) |
| [Moreno 2005 -- Constructing zero divisors in the higher dimensional Cayley-Dickson algebras (arXiv math/0512517)](notes/math-0512517.md) | [PDF](https://arxiv.org/pdf/math/0512517v1) | `math-0512517v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0512517v1) |
| [Biss, Christensen, Dugger, Isaksen 2007 -- Large annihilators in Cayley-Dickson algebras II (arXiv math/0702075)](notes/math-0702075.md) | [PDF](https://arxiv.org/pdf/math/0702075v2) | `math-0702075v2.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0702075v2) |
| [Albuquerque and Majid 1998 -- Quasialgebra structure of the octonions (arXiv math/9802116)](notes/math-9802116.md) | [PDF](https://arxiv.org/pdf/math/9802116v1) | `math-9802116v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/9802116v1) |
| [Decker and Wocjan 2007 -- Hidden quadratic and cubic polynomial function graphs (arXiv quant-ph/0703195)](notes/quant-ph-0703195.md) | [PDF](https://arxiv.org/pdf/quant-ph/0703195v3) | `quant-ph-0703195v3.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/quant-ph/0703195v3) |
| [Griffiths and Niu 1996 -- Semiclassical Fourier Transform for Quantum Computation (arXiv quant-ph/9511007)](notes/quant-ph-9511007.md) | [PDF](https://arxiv.org/pdf/quant-ph/9511007v1) | `quant-ph-9511007v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/quant-ph/9511007v1) |
| [Howard et al. -- Time-uniform confidence sequences](notes/1810.08240.md) | [PDF](https://arxiv.org/pdf/1810.08240v9) | `1810.08240v9.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1810.08240v9) |
| [Seif et al. 2024 -- Suppressing correlated noise via context-aware compiling](notes/2403.06852.md) | [PDF](https://arxiv.org/pdf/2403.06852v2) | `2403.06852v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2403.06852v2) |
| [Bylander et al. 2011 -- Noise spectroscopy through dynamical decoupling with a superconducting flux qubit](notes/1101.4707.md) | [PDF](https://arxiv.org/pdf/1101.4707v1) | `1101.4707v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1101.4707v1) |
| [McKay et al. 2017 -- Efficient Z gates for quantum computing](notes/1612.00858.md) | [PDF](https://arxiv.org/pdf/1612.00858v2) | `1612.00858v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1612.00858v2) |
| [Granade et al. 2012 -- Robust online Hamiltonian learning](notes/1207.1655.md) | [PDF](https://arxiv.org/pdf/1207.1655v2) | `1207.1655v2.pdf` | [CC-BY-NC-SA-3.0](https://arxiv.org/abs/1207.1655v2) |
| [Sheldon et al. 2016 -- Characterizing errors on qubit operations via iterative randomized benchmarking](notes/1504.06597.md) | [PDF](https://arxiv.org/pdf/1504.06597v1) | `1504.06597v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1504.06597v1) |
| [Kimmel, Low and Yoder 2015 -- Robust calibration of a universal single-qubit gate set via robust phase estimation](notes/1502.02677.md) | [PDF](https://arxiv.org/pdf/1502.02677v3) | `1502.02677v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1502.02677v3) |
| [Smolin, Smith and Vargo 2013 -- Oversimplifying quantum factoring](notes/1301.7007.md) | [PDF](https://arxiv.org/pdf/1301.7007v1) | `1301.7007v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1301.7007v1) |
| [Maurer and Pontil 2009 -- Empirical Bernstein bounds and sample variance penalization](notes/0907.3740.md) | [PDF](https://arxiv.org/pdf/0907.3740v1) | `0907.3740v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0907.3740v1) |
| [Waudby-Smith and Ramdas 2024 -- Estimating means of bounded random variables by betting](notes/2010.09686.md) | [PDF](https://arxiv.org/pdf/2010.09686v7) | `2010.09686v7.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2010.09686v7) |

| [Quantitative Curve Selection Lemma](notes/1803.00505.md) | [PDF](https://arxiv.org/pdf/1803.00505v3) | `1803.00505v3.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1803.00505v3) |
| [Rational points in henselian discrete valuation rings](notes/greenberg-henselian-lifting.md) | [PDF](https://pmihes.centre-mersenne.org/item/10.1007/BF02684802.pdf) | `greenberg-1966-henselian-points.pdf` | [Source-specific rights audit](https://pmihes.centre-mersenne.org/articles/10.1007/BF02684802/) |
| [A Verified Optimizer for Quantum Circuits](notes/sqir-voqc-proof-interfaces.md) | [PDF](https://arxiv.org/pdf/1912.02250v3) | `1912.02250v3.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1912.02250v3) |
| [Optimal Experiment Design for Quantum State and Process Tomography and Hamiltonian Parameter Estimation](notes/quant-ph-0411093.md) | [PDF](https://arxiv.org/pdf/quant-ph/0411093v1) | `quant-ph-0411093v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/quant-ph/0411093v1) |
| [Predicting Many Properties of a Quantum System from Very Few Measurements](notes/2002.08953.md) | [PDF](https://arxiv.org/pdf/2002.08953v2) | `2002.08953v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2002.08953v2) |
| [Qubits as Spectrometers of Quantum Noise](notes/cond-mat-0210247.md) | [PDF](https://arxiv.org/pdf/cond-mat/0210247v1) | `cond-mat-0210247v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/cond-mat/0210247v1) |
| [Introduction to Quantum Noise, Measurement and Amplification](notes/0810.4729.md) | [PDF](https://arxiv.org/pdf/0810.4729v2) | `0810.4729v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/0810.4729v2) |
| [Thermal and Residual Excited-State Population in a 3D Transmon Qubit](notes/1412.2772.md) | [PDF](https://arxiv.org/pdf/1412.2772v3) | `1412.2772v3.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1412.2772v3) |
| [Digital quantum simulation of linear and nonlinear optical elements](notes/1909.04408.md) | [PDF](https://arxiv.org/pdf/1909.04408v2) | `1909.04408v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1909.04408v2) |
| [Quantum coherence in the Dynamical Casimir Effect](notes/1610.03272.md) | [PDF](https://arxiv.org/pdf/1610.03272v2) | `1610.03272v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1610.03272v2) |
| [Casimir energy with chiral fermions on a quantum computer](notes/2105.02032.md) | [PDF](https://arxiv.org/pdf/2105.02032v1) | `2105.02032v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2105.02032v1) |
| [Efficient Classical Simulation of Continuous Variable Quantum Information Processes](notes/quant-ph-0109047.md) | [PDF](https://arxiv.org/pdf/quant-ph/0109047v2) | `quant-ph-0109047v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/quant-ph/0109047v2) |
| [Circuit Quantum Electrodynamics](notes/2005.12667.md) | [PDF](https://arxiv.org/pdf/2005.12667v1) | `2005.12667v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2005.12667v1) |
| [The Casimir force between real materials: experiment and theory](notes/0902.4022.md) | [PDF](https://arxiv.org/pdf/0902.4022v1) | `0902.4022v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/0902.4022v1) |
| [Observation of the Dynamical Casimir Effect in a Superconducting Circuit](notes/1105.4714.md) | [PDF](https://arxiv.org/pdf/1105.4714v1) | `1105.4714v1.pdf` | [Source-specific rights audit](https://arxiv.org/abs/1105.4714v1) |
| [Kalia et al. 2026 -- Improved Dark Photon Sensitivity from the Dark SRF Experiment](notes/2510.02427.md) | [PDF](https://arxiv.org/pdf/2510.02427v2) | `2510.02427v2.pdf` | [CC-BY-NC-SA-4.0](https://arxiv.org/abs/2510.02427v2) |
| [Banks et al. 2025 -- Searching for screened scalar forces with long-baseline atom interferometers](notes/2511.09750.md) | [PDF](https://arxiv.org/pdf/2511.09750v1) | `2511.09750v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2511.09750v1) |
| [Ikeda 2023 -- Demonstration of Quantum Energy Teleportation on Superconducting Quantum Hardware](notes/2301.02666.md) | [PDF](https://arxiv.org/pdf/2301.02666v5) | `2301.02666v5.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2301.02666v5) |
| [Hotta 2010 -- Energy-Entanglement Relation for Quantum Energy Teleportation](notes/1002.0200.md) | [PDF](https://arxiv.org/pdf/1002.0200v2) | `1002.0200v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1002.0200v2) |
| [Ford and Roman 1997 -- Restrictions on Negative Energy Density in Flat Spacetime](notes/gr-qc-9607003.md) | [PDF](https://arxiv.org/pdf/gr-qc/9607003v2) | `gr-qc-9607003v2.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/gr-qc/9607003v2) |
| [Wilmot 2025 -- Structure of the Cayley-Dickson algebras](notes/2505.11747.md) | [PDF](https://arxiv.org/pdf/2505.11747v3) | `2505.11747v3.pdf` | [CC-BY-NC-SA-4.0](https://arxiv.org/abs/2505.11747v3) |
| [LZ Collaboration 2026 -- Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment](notes/2609.02823.md) | [PDF](https://arxiv.org/pdf/2609.02823v1) | `2609.02823v1.pdf` | [CC-BY-NC-SA-4.0](https://arxiv.org/abs/2609.02823v1) |
| [DES Collaboration 2026 -- Dark Energy Survey Year 6 Results: Cosmological Constraints from Galaxy Clustering and Weak Lensing](notes/2601.14559.md) | [PDF](https://arxiv.org/pdf/2601.14559v2) | `2601.14559v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2601.14559v2) |
| [Quantum collision models: open system dynamics from repeated interactions](notes/2106.11974.md) | [PDF](https://arxiv.org/pdf/2106.11974v2) | `2106.11974v2.pdf` | [Source-specific rights audit](https://arxiv.org/abs/2106.11974v2) |
| [Childs and Wiebe 2012 -- Hamiltonian Simulation Using Linear Combinations of Unitary Operations](notes/1202.5822.md) | [PDF](https://arxiv.org/pdf/1202.5822v1) | `1202.5822v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1202.5822v1) |
| [Berry, Childs, Cleve, Kothari and Somma 2014 -- Exponential improvement in precision for simulating sparse Hamiltonians](notes/1312.1414.md) | [PDF](https://arxiv.org/pdf/1312.1414v2) | `1312.1414v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1312.1414v2) |
| [Kang and Su 2026 -- Quantum matrix arithmetics with Hamiltonian evolution](notes/2510.06316.md) | [PDF](https://arxiv.org/pdf/2510.06316v3) | `2510.06316v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2510.06316v3) |
| [Wang et al. 2009 -- Decoherence Dynamics of Complex Photon States in a Superconducting Circuit](notes/0909.4585.md) | [PDF](https://arxiv.org/pdf/0909.4585v1) | `0909.4585v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/0909.4585v1) |
| [Murch, Weber, Macklin and Siddiqi 2013 -- Observing single quantum trajectories of a superconducting qubit](notes/1305.7270.md) | [PDF](https://arxiv.org/pdf/1305.7270v2) | `1305.7270v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1305.7270v2) |
| [Cramer et al. 2010 -- Efficient quantum state tomography](notes/1101.4366.md) | [PDF](https://arxiv.org/pdf/1101.4366v1) | `1101.4366v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1101.4366v1) |
| [Baez 2002 -- The Octonions](notes/math-0105155.md) | [PDF](https://arxiv.org/pdf/math/0105155v4) | `math-0105155v4.pdf` | [Assumed arXiv 1991-2003 grant](https://arxiv.org/abs/math/0105155v4) |
| [Procopio et al. 2017 -- Experimental Test of Hyper-Complex Quantum Theories](notes/1602.01624.md) | [PDF](https://arxiv.org/pdf/1602.01624v2) | `1602.01624v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1602.01624v2) |
| [Adler 2017 -- Does the Peres experiment using photons test for hyper-complex (quaternionic) quantum theories?](notes/1604.04950.md) | [PDF](https://arxiv.org/pdf/1604.04950v3) | `1604.04950v3.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1604.04950v3) |
| [Procopio, Rozema, Dakic and Walther 2017 -- Comment on Adler's Peres-experiment critique](notes/1607.01648.md) | [PDF](https://arxiv.org/pdf/1607.01648v1) | `1607.01648v1.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1607.01648v1) |
| [Iqbal et al. 2024 -- Non-Abelian Topological Order and Anyons on a Trapped-Ion Processor](notes/2305.03766.md) | [PDF](https://arxiv.org/pdf/2305.03766v2) | `2305.03766v2.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/2305.03766v2) |

## Licensed software source snapshots

These archives preserve the exact original upstream bytes and license notices.
Source inspection supplies candidate proof interfaces and independent
implementations to cross-check; build compatibility remains a separate gate. Archive/member hashes and license text
are checked by `verify_sources.py` without extraction or execution.

| Source | Original archive | License |
| --- | --- | --- |
| [SQIR / VOQC](notes/sqir-voqc-proof-interfaces.md) | [sqir-134fb94.tar.gz](source_archives/sqir-134fb94.tar.gz) | MIT |
| [CoqInterval](notes/coqinterval-certified-enclosures.md) | [interval-4.11.5.tar.gz](source_archives/interval-4.11.5.tar.gz) | CECILL-C |
| [Mathematical Components](notes/mathcomp-coqeal-matrix-certificates.md) | [mathcomp-9931c88.tar.gz](source_archives/mathcomp-9931c88.tar.gz) | CECILL-B |
| [CoqEAL](notes/mathcomp-coqeal-matrix-certificates.md) | [coqeal-8fd26cf.tar.gz](source_archives/coqeal-8fd26cf.tar.gz) | MIT |
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

[Library overview](README.md) maps paper relevance. [Numerics](notes/numerics_best_practice.md)
collects the conditioning, precision, vectorization and runtime-package rules. The
[coordinated roadmap](RESEARCH_ROADMAP.md) retains the cumulative mathematics,
proof, optimizer, review, and hardware obligations. The next hardware priority
remains model discrimination followed by a measured optimizer decision before
broad atlas expenditure. Each new physical case requires its own approval.

## IBM Runtime documentation

The [execution-guide note](notes/ibm-runtime-execution-guides.md) records nine IBM Quantum documentation pages
(workload usage, stretch, Sampler options, Sampler inputs and outputs, run-time minimization,
the client-side Sampler API, real-time backend-property refresh, circuit timing and execution modes) with retrieval SHA-256 and the use each page is cited for.

The [Heron platform note](notes/ibm_heron_platform.md) records the live Targets of ibm_fez, ibm_kingston and ibm_marrakesh
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
The [Heron tile packing note](notes/heron_spatial_multiprogramming.md) packs guard-banded tiles on the
snapshot coupling map, composes one circuit per tile into one wide circuit, and states per-backend RZZ and
repetition-delay arithmetic from Target values, audited in
[spatial_multiprogramming_audit.json](evidence/heron_platform/spatial_multiprogramming_audit.json).

The [Hoeffding note](notes/hoeffding-1963.md) cites the 1963 inequality behind the admission contracts by DOI.
The [measurement-foundations web note](notes/measurement_foundations_web_sources.md) records the 3 February 2025 removal
of pulse-level control, the Qiskit Experiments 0.14.2 tomography pages, and the Crossref identities of the
Steffen 2006 and Hofheinz 2009 superconducting tomography papers.
The [hypercomplex and anyon Crossref note](notes/hypercomplex_quantum_crossref_records.md) binds the
versions of record of the hypercomplex-theory exchange and the two non-Abelian anyon experiments.
The [associator audit](evidence/reviewer_associator_audit/PROVENANCE.md) retains the arithmetic behind the
algebra circuit design rules of AGENTS.md.
