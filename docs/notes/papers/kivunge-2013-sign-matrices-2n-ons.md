# Kivunge 2013 -- Sign Matrices for Frames of 2^n-ons under Smith-Conway and Cayley-Dickson Multiplications (conference slides)

## Source copy and license

The [slide deck](https://cs.du.edu/~petr/milehigh/2013/Kivunge.pdf) is a conference presentation, not a paper:
a LaTeX Beamer file of 91 PDF pages whose overlay builds repeat frames, leaving 44 distinct content frames. It is
listed under "Talks" on the
[Third Mile High Conference on Nonassociative Mathematics page](https://cs.du.edu/~petr/milehigh/2013/) (University
of Denver, 11 to 17 August 2013). Neither the PDF nor that page states a license or a copyright notice, so the
slides stay external under a manual audit with license identifier `NOASSERTION`: the optional personal reading copy
is `docs/local_source_cache/kivunge-2013-sign-matrices.pdf`, and [SOURCES.json](../../SOURCES.json) records the
SHA-256 of the bytes read, the SHA-256 of the conference page and the reading scope. The repository retains no
capture of the conference page.

Tag convention: [P] marks slide statements; [I] marks repository interpretation. Locators are PDF page indices
(frames repeat across pages, so the first page of the final build is cited).

## Citation and provenance

- Author: Benard Kivunge, Department of Mathematics, Kenyatta University, Kenya.
- Presented 13 August 2013 (title frame). PDF metadata: creator LaTeX Beamer 3.10, created 13 August 2013;
  the server reports the file last modified 15 August 2013.
- Publication status: no proceedings record or journal article was located. The conference page announces a
  proceedings deadline of 31 October 2013 and the repository searched no further.
- URL read: https://cs.du.edu/~petr/milehigh/2013/Kivunge.pdf, 91 pages.
- SHA-256: `859183fca2c0ef330c322af5b9f3e3807eb8e2ce29a38873d2a81c46b90a2e5d`
- Reading scope: every distinct frame (text layer), with the doubling-formula frames (pp. 7 and 9) also read as page
  images because the text layer drops conjugation bars. The deck has no bibliography frame. Proofs appear as frame
  sketches; none was rechecked line by line.

## Transcribed statements

Index and sign convention [P]: the frame (basis) of the `2^n`-ons is built by doubling, `e_{0mnk} = (e_{mnk}, 0)` and
`e_{1mnk} = (0, e_{mnk})` (p. 24), so the binary subscript is the basis index read most significant bit first and
rows and columns run through the subscripts in increasing order. The sign matrix of a frame (p. 16) is
`S_ij = +1` if `a_i a_j = a_k` and `S_ij = -1` if `a_i a_j = -a_k`, for a multiplicative quasigroup `{a_1, ..., a_n}`
with `a_i a_j in {a_k, -a_k}`.

- [P] Doubling formulas (pp. 7-8): the Cayley-Dickson formula `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`
  (bars read from the page image); the Smith-Conway formula I, `(a, b)(c, d) = (ac, conj(a) d)` for `b = 0` and a
  longer expression with `b^(-1)` for `b != 0`; and a modified Smith-Conway formula II (p. 8). On basis elements
  (p. 9) the rules read `(a, 0)(c, 0) = (ac, 0)`, `(a, 0)(0, d) = (0, conj(a) d)`, and two further rules with
  conjugates for `(0, b)(c, 0)` and `(0, b)(0, d)`.
- [P] Hadamard matrix (p. 14): a `+-1` matrix `H` of degree `n` with `H H' = n I_n`; normalized if the first row and
  column are all `+1`.
- [P] Smith-Conway sign matrices: complex numbers `S_C = [[1, 1], [1, -1]]` (p. 17); quaternions
  `S_H = [[1, 1, 1, 1], [1, -1, -1, 1], [1, 1, -1, -1], [1, -1, 1, -1]]` (p. 19); octonions `S_K`, an 8 x 8 matrix
  with `S_K S_K' = 8 I` (pp. 21-22); sedenions `S_S` as four 8 x 8 blocks `A, B, C, D` (pp. 26-29) with
  `S_S S_S' = 16 I` (p. 33).
- [P] Theorem (p. 36): "The sign matrix for the frame in the `2^n`-ons under the Smith-Conway multiplication is a
  `2^n x 2^n` Hadamard matrix." The proof (pp. 36-53) takes `n <= 4` "as shown above" and inducts through the block
  form of the doubled matrix (pp. 43-47), a row permutation (p. 49) and the computation
  `H H' = 2^(n+1) I` (p. 53).
- [P] Cayley-Dickson sign matrices (pp. 56-61): also Hadamard; identical to the Smith-Conway matrix for the complex
  numbers and different for the quaternions, octonions and higher doublings; "equivalent (similar) via permutation of
  rows/columns", the quaternion case by `C3 <-> C4` then `R3 <-> R4` (p. 61). The quaternion matrix under
  Cayley-Dickson is `[[1, 1, 1, 1], [1, -1, 1, -1], [1, -1, -1, 1], [1, 1, -1, -1]]` (p. 58).
- [P] Skew Hadamard (pp. 62-68): a Hadamard matrix `H = S + I` with `S' = -S` is skew; its kernel `W` is defined by
  `S = [[0, e], [-e', W]]`. Theorem (p. 64): "The sign matrices of the `2^n`-ons under the Smith-Conway or
  Cayley-Dickson multiplication is equivalent to a skew Hadamard matrix"; the proof multiplies all rows but the
  first by `-1` (p. 67).
- [P] Kronecker products (pp. 70-90): `S_C (x) S_C` is equivalent to `S_H` by `R2 <-> R4`; `S_C (x) S_H`,
  `S_H (x) S_C` and `S_C (x) S_C (x) S_C` are each equivalent to `S_K` by listed row permutations (p. 86). The last
  frame (p. 90) poses an open question: whether `S_C (x) S`, with `S` the sign matrix of the `2^(n-1)`-ons, is
  always equivalent to the sign matrix of the `2^n`-ons, and by which permutation.

## Mapping to this repository

- [I] Index map: the subscript of `e_{abc...}` read as a binary numeral is the `cd_core` index, and the Cayley-Dickson
  doubling of p. 7 is the doubling `cd_core.cd_sign` implements.
- [I] Check results, from a scratch script under the ignored `docs/local/`, with matrices read from the text layer
  (the 16 x 16 and 8 x 8 matrices pass the Hadamard test, which validates the reading):
  - the Smith-Conway sedenion matrix `S_S` (pp. 26-29, 256 cells) is Hadamard and equals `cd_core.cd_sign(16, j, i)`
    on all 256 cells (210 disagreements with `cd_sign(16, i, j)`); the octonion matrix `S_K` (p. 21) equals
    `cd_sign(8, j, i)` on all 64 cells (42 disagreements with `cd_sign(8, i, j)`). The Smith-Conway sign matrices
    are therefore the transposes of the `cd_core` sign matrices, which is the sign table of the opposite algebra;
    the mechanism (the conjugate in `(a, 0)(0, d) = (0, conj(a) d)` against `da` in the Cayley-Dickson rule) is not
    derived here.
  - the Cayley-Dickson quaternion matrix (p. 58) equals `cd_sign(4, i, j)` on all 16 cells: map found, no
    mismatch. The deck prints no Cayley-Dickson matrix for the octonions or sedenions.
  - The `cd_core` sign matrix `[cd_sign(n, i, j)]` is Hadamard for `n = 2, 4, ..., 64`; the matrix with every row
    but the first negated, minus `I`, is skew-symmetric for `n = 4, ..., 64`, the content of the theorem on p. 64
    for the Cayley-Dickson rule.
- [I] The repository already holds these facts for `cd_core`: the skew conference matrix `W_n` and its skew
  Hadamard matrix `I + W_n` are proved for every `n`
  ([cd-star-lattice-tower](../topics/cd-star-lattice-tower.md#the-boundary-as-a-paley-matrix)), and that note places
  `I + W_16` and the transpose of the sedenion sign table in two Hadamard classes of the retained
  [McKay](mckay-hadamard-matrices.md) list that form a transpose pair. The deck's theorem on p. 36 adds the
  statement for the Smith-Conway rule, which the check reads as the transposed table, and no new claim for
  `cd_core`. The deck's `n <= 4` base case plus an induction sketch is not a proof the repository relies on.
- [I] Certificate status: the deck states no automorphism, signed-permutation map or group order, and supplies no
  `T(e_i e_j) = T(e_i) T(e_j)` check.

## Relevance

- [I] Cayley-Dickson structure: high for the sign-matrix object (`S` equals the `cd_core` sign table or its
  transpose); the theorems add no result beyond the repository's proofs.
- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] Conference slides carry no peer review, and the deck gives sketches in place of proofs; the repository cites
it for the definitions and matrices it prints. The Smith-Conway formulas for `b != 0` (pp. 7-8) are transcribed
only in outline because their conjugation and inverse marks were not recoverable from the text layer. The block
form on pp. 43-47 and the Kronecker equivalences on pp. 81-90 were not checked.
