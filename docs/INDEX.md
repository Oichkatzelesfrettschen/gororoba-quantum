# Source index

The source library separates repository-hosted papers from local reading copies.
All source notes, retrieval URLs, original byte identities, and reading scopes remain
public in [SOURCES.json](SOURCES.json) and the linked notes. License evidence
controls PDF hosting; availability for download alone supplies no downstream grant.

| Location | Contents | Git treatment |
| --- | --- | --- |
| `docs/pdf/` | 11 unchanged PDFs with source-specific CC BY 4.0 or CC0 evidence, plus two aliases | Tracked |
| `docs/local_source_cache/` | 40 optional original reading copies with restricted or unestablished rehosting permission | Ignored |
| `docs/notes/`, `docs/evidence/` | Research descriptions, provenance, and repeatable checks | Tracked |

The local cache lives inside `docs/`. A fresh checkout receives the public notes
and hosted PDFs; the verifier accepts an absent cache and checks each registered
local copy when present. Local filenames below appear as text so links also work
in a clean checkout. All retained originals preserve their registered SHA-256.
Historical Git commits can retain previously tracked PDF blobs; the folder split
changes the branch tip and performs no history rewrite.

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
| [Biss, Dugger, Isaksen 2005 -- Large annihilators in Cayley-Dickson algebras (arXiv math/0511691)](notes/math-0511691.md) | [PDF](https://arxiv.org/pdf/math/0511691v1) | `math-0511691v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0511691v1) |
| [Moreno 2005 -- Constructing zero divisors in the higher dimensional Cayley-Dickson algebras (arXiv math/0512517)](notes/math-0512517.md) | [PDF](https://arxiv.org/pdf/math/0512517v1) | `math-0512517v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0512517v1) |
| [Biss, Christensen, Dugger, Isaksen 2007 -- Large annihilators in Cayley-Dickson algebras II (arXiv math/0702075)](notes/math-0702075.md) | [PDF](https://arxiv.org/pdf/math/0702075v2) | `math-0702075v2.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/0702075v2) |
| [Albuquerque and Majid 1998 -- Quasialgebra structure of the octonions (arXiv math/9802116)](notes/math-9802116.md) | [PDF](https://arxiv.org/pdf/math/9802116v1) | `math-9802116v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/math/9802116v1) |
| [Decker and Wocjan 2007 -- Hidden quadratic and cubic polynomial function graphs (arXiv quant-ph/0703195)](notes/quant-ph-0703195.md) | [PDF](https://arxiv.org/pdf/quant-ph/0703195v3) | `quant-ph-0703195v3.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/quant-ph/0703195v3) |
| [Griffiths and Niu 1996 -- Semiclassical Fourier Transform for Quantum Computation (arXiv quant-ph/9511007)](notes/quant-ph-9511007.md) | [PDF](https://arxiv.org/pdf/quant-ph/9511007v1) | `quant-ph-9511007v1.pdf` | [Legacy arXiv hosting grant](https://arxiv.org/abs/quant-ph/9511007v1) |
| [Howard et al. -- Time-uniform confidence sequences](notes/1810.08240.md) | [PDF](https://arxiv.org/pdf/1810.08240v9) | `1810.08240v9.pdf` | [ArXiv-only distribution grant](https://arxiv.org/abs/1810.08240v9) |

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
formal second-order solutions; actual curves and complete tangent cones
require further analysis.

## Verification and research navigation

Run from the repository root:

```sh
set -eu
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/verify_sources.py
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/check_verify_sources.py
sha256sum -c docs/PDF_SHA256SUMS
```

[Library overview](README.md) maps paper relevance. The
[coordinated roadmap](RESEARCH_ROADMAP.md) retains the cumulative mathematics,
proof, optimizer, review, and hardware obligations. The next hardware priority
remains model discrimination followed by a measured optimizer decision before
broad atlas expenditure. Each new physical case requires its own approval.
