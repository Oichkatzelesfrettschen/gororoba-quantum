# OpenAI 2026 -- The maximum number of mutually unbiased bases in dimension six (openai/math family 266)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026.pdf)
sits in the openai/math repository under its root Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit), a repository-wide
software license with no source-specific CC BY 4.0 or CC0 grant for the manuscript. Under the `source_rights_policy`
of [SOURCES.json](../../SOURCES.json) the PDF stays external: its optional personal reading copy is
`docs/local_source_cache/openai-math-266-mub-dimension-six.pdf`.

Tag convention: [P] marks paper statements; [I] marks repository interpretation. Printed page numbers equal the
PDF page indices.

## Citation and provenance

- Author: "OpenAI"; an unreleased internal OpenAI model produced the manuscript, per the openai/math README, which
  calls the collection "raw research data". The manuscript is unrefereed.
- Version read: the manuscript dated 24 September 2026, as held at openai/math commit
  `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). The family's companion is
  [openai-2026-hadamard-order-six-fourier-certificates.md](openai-2026-hadamard-order-six-fourier-certificates.md).
  A Crossref bibliographic search by title on 27 October 2026 returned no record of this paper.
- Commit-pinned PDF, 76 pages, 817,737 bytes.
- SHA-256: `b4cc74c840c902494d589b51c8e9706490f37cf2735e69a0486122131c6b7446`
- Reading scope: pp. 1-6 (contents, introduction, Lemma 1.2, Corollary 1.3), pp. 50 and 52-55 (Section 7.1
  platform and build, Theorem 7.1 and its proof, Section 7.5, Tables 1 and 2, Section 8, Appendix A.1) in full,
  and the directory README and `verification/saved-run/VERIFY.md`. Sections 2-6 and Appendices A.2-A.12 were read
  for section titles and result labels only; no geometric lemma or arithmetic bound was checked.

## Transcribed statements

- [P] Theorem 1.1 (Computer-assisted, pp. 2-3): under the arithmetic and compiler conditions of Appendix A, the
  complete execution of Section 7.5 certifies that no four pairwise mutually unbiased orthonormal bases exist in
  `C^6`; consequently `N(6) = 3`.
- [P] Lemma 1.2 (pp. 5-6): three mutually unbiased bases exist in `C^6 = C^2 (x) C^3`, from
  `A_0 = I_2`, `A_1 = (1/sqrt 2)[[1, 1], [1, -1]]`, `A_2 = (1/sqrt 2)[[1, 1], [i, -i]]` and
  `B_0 = I_3`, `B_1 = F`, `B_2 = D F` with `D = diag(1, omega, omega)`, `U_r = A_r (x) B_r`.
- [P] Corollary 1.3 (p. 6): under the same contract, three is the maximum number of pairwise Killing-orthogonal
  Cartan subalgebras of `sl_6(C)` closed under one standard adjoint.
- [P] Strategy (p. 4): a seed cover of nine phases of the second basis `H / sqrt 6`; Stage A covers every completion
  of each seed through a closed cover of `U(2)`; Stage B shrinks phase balls in approximate tangent coordinates with
  a bounded normal displacement; Stage C covers the vectors unbiased to the first two bases by vector balls and
  excludes two disjoint six-cliques of the orthogonality graph with all 36 cross edges in the unbiasedness graph.
  "A failed certification or an exhausted search cap retains an unresolved region; it cannot prove nonexistence."
- [P] Platform (p. 50): x86-64 Intel Xeon Platinum 8573C, Ubuntu GCC 13.3.0, glibc 2.39, builds with
  `-O3 -march=native -ffp-contract=off`. The assumptions are binary64 round-to-nearest, no contraction or fast-math
  reassociation, correctly rounded square root, masked exceptions, no flush-to-zero or denormals-are-zero. Probes
  recorded `FLT_EVAL_METHOD=0` and MXCSR `0x1f80`; the text calls these "limited evidence for the stated platform
  conditions, not a proof". The two `pow(..., 2)` expressions of `coverSeeds::run` must lower to separate binary64
  multiplications, checked by disassembly of the recorded binary.
- [P] Theorem 7.1 (p. 52): with the seven source files and the Appendix A conditions, invocations meeting every
  terminal condition of Section 7.2 exclude four mutually unbiased bases.
- [P] Section 7.5 and Table 1 (p. 53): the run of 4 October 2026, 03:10:26 to 04:24:56 UTC, covered 151,744,086 seed
  pairs into 249,878 centers; Stage A emitted 3,083 records over four shards; B fine emitted 22,379; initial C left
  163 unresolved records (all graph caps), which the fallback resolved into 1,127 records with zero unresolved
  across four final shards; 100 native invocations in all. Table 2 (p. 54) lists SHA-256 digests of the principal
  data files. The earlier run of 7 September 2026 "has not been authenticated" and carries no weight in the proof.
- [P] Appendix A.1 (p. 55): the primitive-operation model is IEEE 754 binary64; rounding is bounded with
  `u = 2e-16` and an additive allowance `tau = 1e-300`.
- [P] `VERIFY.md` (saved-run directory): `execution/check_records.py` checks the saved numerical records for parsing,
  bounds, shard and batch partitions, ordered failure subsequences and complete final coverage. It "does not run
  the numerical C++ programs" and is "a numerical consistency check, not an authentication of the historical
  archive, a proof of the C++ implementation, or a verification of compiler and hardware behavior". The directory
  README states that `VERIFY.md` supersedes the package instructions on pp. 49-54.

## Formal statement

- [P] [`lean/docs/266.md`](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/266.md)
  states that the formalization proves at most five bases and "does not establish the paper's upper bound of three
  or its computer-assisted exclusion of four arbitrary bases". `ComparatorChallenges/MUBSix.lean` states
  `fourier_and_family_bound`: Fourier vanishing for every order-six Hadamard matrix inequivalent to the cubic matrix,
  and `Attainable n -> n <= 5`.
- [I] The value three therefore rests on the binary64 execution and its stated contract; the formal check reaches
  the five-basis bound of the companion paper. The Lean build and Comparator run were not run here.

## Mapping to this repository

- [I] Evidence shape. The paper separates a proposed numerical object from its certification and treats compiler and
  hardware semantics as stated premises. That is the distinction this repository draws between a checksum-matched
  replay and an independent proof check, and between exact rational certificates (for example the C5 exact replay)
  and floating-point evidence.
- [I] Hardware. The circuits here prepare and measure qubit Pauli bases, which are the three mutually unbiased bases
  of `C^2`. Dimension six and complex Hadamard matrices of order six enter no circuit, record or algebra check.
- [I] Hadamard matrices. The Cayley-Dickson sign tables of [cd-star-lattice-tower.md](../topics/cd-star-lattice-tower.md)
  are real Hadamard matrices of order `2^n`; order six has no real Hadamard matrix, and the paper's matrices are
  complex.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] No geometric lemma of Sections 2-6, no arithmetic bound of Appendix A and no saved record was checked here; the
saved-record checker and the C++ build were not run. The manuscript is unrefereed.
