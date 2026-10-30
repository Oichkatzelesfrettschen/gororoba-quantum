# OpenAI 2026 -- Exact Fourier certificates for complex Hadamard matrices of order six (openai/math family 266)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/Exact-Fourier-certificates-for-complex-Hadamard-matrices-of-order-six-September-24-2026/Exact-Fourier-certificates-for-complex-Hadamard-matrices-of-order-six-September-24-2026.pdf)
sits in the openai/math repository under its root Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit), a repository-wide
software license with no source-specific CC BY 4.0 or CC0 grant for the manuscript. Under the `source_rights_policy`
of [SOURCES.json](../../SOURCES.json) the PDF stays external: its optional personal reading copy is
`docs/local_source_cache/openai-math-266-hadamard-order-six-fourier-certificates.pdf`.

Tag convention: [P] marks paper statements; [I] marks repository interpretation. Printed page numbers equal the
PDF page indices.

## Citation and provenance

- Author: "OpenAI"; an unreleased internal OpenAI model produced the manuscript, per the openai/math README. The
  manuscript is unrefereed.
- Version read: the manuscript dated 24 September 2026 (PDF creation date 5 October 2026), as held at openai/math
  commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). It is the companion of
  [openai-2026-mub-dimension-six.md](openai-2026-mub-dimension-six.md). A Crossref bibliographic search by title on
  27 October 2026 returned no record.
- Commit-pinned PDF, 35 pages, 396,915 bytes.
- SHA-256: `6bc2448ff13557610112e91ae6e713d0b469588cd9e1e3f9b44c04fc422fd612`
- Reading scope: pp. 1-4 (introduction, proof strategy, Sections 2 and 3.1), p. 24 (end of Section 7.4) and p. 25
  (Appendix A expected output) in full, and the directory README. Sections 3.2-7.3 were read for result labels only.
  The verifier of Appendix A was inspected for its imports (standard-library `itertools`, `functools`, `fractions`,
  `math`, `collections`) and then run once (see [Verifier replay](#verifier-replay)).

## Transcribed statements

- [P] Definitions (pp. 1-4): a complex Hadamard matrix of order six is `H` in `T^(6x6)` with `H* H = 6 I`; the
  normalized character is `g_H(a) = (1/6) sum_k prod_i H(i, k)^(a_i)` for balanced charges `a` in `Z^6`; the charge
  `alpha = (1, 1, 1, -1, -1, -1)`; equivalence allows row and column permutations and unit phases. The cubic matrix
  `T = (omega^(t_ij))` with `omega = exp(2 pi i / 3)` has exponent 1 on adjacent and -1 on nonadjacent distinct
  indices of the five-cycle `1..5` and 0 on the first row, first column and diagonal (equation 2); it is `S_6` in the
  Hadamard literature.
- [P] Theorem 1.1 (Fourier vanishing, p. 2): every order-six complex Hadamard matrix inequivalent to `T` has
  `g_H(pi alpha) = 0` for every coordinate permutation `pi`, which is Conjecture 2.3 of Matolcsi, Ruzsa and Weiner.
- [P] Theorem 1.2 (No complete family, p. 2): no seven mutually unbiased orthonormal bases of `C^6` exist; with
  Weiner's completion theorem this gives `N(6) <= 5`. The sharper `N(6) = 3` belongs to the companion paper under
  its binary64 contract (p. 3).
- [P] Corollary 3.1 (Dichotomy, p. 4): every order-six Hadamard matrix has either (M) `g_(H_pi)(alpha) = 0` for every
  row permutation or (C) an entrywise square `H o2` that is itself Hadamard. Proposition 4.1 (p. 8) classifies (C) as
  equivalent to `T`, which also proves Phangara's conjecture on order-six S-Hadamard matrices.
- [P] Method (p. 3): the certificates are finite rational identities; modular elimination locates substitutions
  and exact integer multiplication proves them for every actual moment vector, which need not be rational.
- [P] Proposition 6.3 (p. 24): the residual expansion has constant term `c_0 = -613302797399911/6480` and absolute
  coefficient sum `179721388988719/6480`, so the nonnegative form `Q` satisfies
  `0 <= Q <= -2007321335237/30 < 0`, a contradiction; all 98 pivots of the six positive matrices pass.
- [P] README: `python3 verification/run.py` with assertions enabled; `run.py` refuses `-O` and checks the
  verifier digest `104a7306205b8544c8f913f6afdb59603f2e04a207c9ac592c383b80eb0e2aa9` before running it.

## Verifier replay

- [E] On 27 October 2026 the commit-pinned `verification/run.py` (sha256
  `670e627fc97030104873c26572c0d1f6d1cb3d969cc99c95d2de9e26619a495e`) and `verification/verify.py` (sha256
  `104a7306205b8544c8f913f6afdb59603f2e04a207c9ac592c383b80eb0e2aa9`, the digest the wrapper and p. 25 print) ran
  as `python3 -I verification/run.py` from a directory holding only those two files, with `PYTHONOPTIMIZE` and
  `PYTHONPATH` unset, under CPython 3.14.7 (Clang 22.1.3) on x86_64 Linux with an 8 GiB address-space limit.
- [E] The run exited 0 in 58 s wall time (57.2 s user) at 341 MB peak resident memory, and its standard output is
  byte-identical to the three lines p. 25 prints:

  ```text
  rank table: 8871 909 897
  rank table: 46041 3429 2767
  -613302797399911/6480 179721388988719/6480 5000000000000000
  ```

- [I] The replay establishes that the two exact rational certificates of Propositions 3.4 and 6.3, as encoded in
  the verifier, hold in integer and rational arithmetic on this interpreter. It does not establish that the verifier
  encodes the paper's moment identities faithfully, nor the cubic character counts, which the paper specifies by
  finite sums and loops outside the program.

## Formal statement

- [P] [`lean/docs/266.md`](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/266.md)
  links `ComparatorChallenges/MUBSix.lean`, whose `fourier_and_family_bound` states Theorem 1.1 and the five-basis
  bound, and `HadamardCubeFiber.lean`, a supporting cancellation lemma. The Lean build and Comparator run were not
  run here.

## Mapping to this repository

- [I] Evidence shape. The certificate is exact rational arithmetic over a finite identity, the same evidence class as
  this repository's exact replays. The verifier's checks are `assert` statements, so it is valid only without `-O`,
  the failure mode behind this repository's rule that checks raise explicitly; `run.py` closes that gap by refusing
  `sys.flags.optimize`.
- [I] Hardware and algebra: the [transition-conformance design](../../design/quantum-experiment-conformance.md)
  uses the explicit cubic Tao matrix as an offline overlap comparator. Its exact residuals against the three
  product bases establish a candidate-specific comparison; the prospective hardware suite uses the three
  reference bases and makes no universal fourth-basis exclusion claim.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] No proof step of Sections 3-7 was checked by hand. The Appendix A verifier ran once with the owner's approval
([Verifier replay](#verifier-replay)); its scope is the encoded certificates, not the derivation of the identities
they certify. The manuscript is unrefereed.
