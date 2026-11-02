# Conway and Norton 1979: Monstrous moonshine (Bull. London Math. Soc. 11)

## Source copy and license

The [source PDF](https://content.openalex.org/works/W4244111325.pdf) remains external to the published library. It is the
OpenAlex content-cache copy of the version of record (OpenAlex work W4244111325; the best location carries no license and the
version is `publishedVersion`). PDF page 1 states the journal citation "[BULL. LONDON MATH. SOC., 11 (1979), 308-339]" and
the receipt date "Received 8 May 1979", and page 2 carries a vertical Wiley Online Library download notice in the right margin;
the PDF holds no redistribution grant, so the registry records it as external-only under `NOASSERTION`. The reading copy is
the ignored `docs/local_source_cache/conway-norton-1979-monstrous-moonshine.pdf`, with a second copy in the owner's private
documents repository. [SOURCES.json](../../SOURCES.json) binds the SHA-256 and the reading scope. Attribution to John H.
Conway and Simon P. Norton applies to every statement below.

Tag convention: [P] marks a statement of the paper; [I] marks repository interpretation. No machine check ran for this note.
Printed page numbers are the PDF page index plus 307 (PDF page 2 is printed page 309).

## Citation and provenance

- Authors: J. H. Conway, S. P. Norton. Subtitle on page 1: "A quick summary of the recent amazing discoveries about the
  Fischer-Griess 'MONSTER' simple group."
- Version of record: Bulletin of the London Mathematical Society 11(3) (1979), pp. 308-339, DOI
  [10.1112/blms/11.3.308](https://doi.org/10.1112/blms/11.3.308); the Crossref record (title, authors, venue, volume, issue,
  pages, year) is a registered retrieval receipt.
- Retained PDF: 32 pages, 1851000 bytes, SHA-256 `1baaa699c893f154d7b7bab1a189ccb039668a756cf5fd07526e3aa9572243e2`.
- Reading scope: printed pages 308-309 (PDF pages 1 and 2: the history section, observations (A) to (G) and the opening of
  Section 2) and the first column block of Table 1 on printed page 324 (PDF page 17), opened page by page. The remaining pages,
  including Table 1a, Table 2 and the conjecture tables, were not opened for this note.
- Status: published paper (version of record).

## Statements read

- [P] Section 1 (p. 308): in 1973 Fischer and Griess independently produced evidence for a simple group `M` of order
  `2^46 . 3^20 . 5^9 . 7^6 . 11^2 . 13^3 . 17 . 19 . 23 . 29 . 31 . 41 . 47 . 59 . 71`, printed in decimal as
  8080,17424,79451,28758,86459,90496,17107,57005,75436,80000,00000; the authors proposed the name MONSTER and a representation of
  degree 196883, Fischer, Livingstone and Thorne computed the character table on that assumption, and Thompson proved uniqueness
  under similar assumptions; existence had not been proved at the time of writing.
- [P] Observations (A) to (G) (pp. 308-309): (A) Guy's symmetry in the character table of `2^12 M_24`; (B) "balanced" cycle shapes of
  `M_24`; (C) for each prime `p` with `(p - 1) | 24` a class `p-` with centralizer `p^(1+2d) . G_p`; (D) the characters of `p+` and `p-`
  in the minimal faithful representation differ by `p^d`; (E) Ogg's observation that the primes dividing `|M|` are those for which the
  function field of the normalizer of `Gamma_0(p)` in `PSL_2(R)` has genus zero; (F) McKay's observation that a coefficient in
  `j = q^-1 + 744 + 196884 q + 21493760 q^2 + ... = sum a_r q^r` is `196883 + 1`, with Thompson's finding that the later `a_r` are simple
  linear combinations of the character degrees `f_r` of `M`: `a_-1 = f_1`, `a_1 = f_1 + f_2`, `a_2 = f_1 + f_2 + f_3`,
  `a_3 = 2 f_1 + 2 f_2 + f_3 + f_4`; (G) the Lie group `E_8` has dimension `248 = 744/3`.
- [P] Section 2 (p. 309): the normalized function is `J = j - 744 = q^-1 + 0 + a q + b q^2 + ...`; Thompson's proposal replaces the
  coefficients by representations `H_r` of `M` (head representations; `H_-1` trivial and `H_1` the sum of the trivial and the degree
  196883 representation), and the character values give the series `T_m = q^-1 + 0 + H_1(m) q + H_2(m) q^2 + ...`; the authors conjecture
  that `T_m` is the normalized generator of a genus zero function field arising from a group between `Gamma_0(N)` and its normalizer in
  `PSL_2(R)`.
- [P] Table 1 (p. 324): the degrees of the irreducible characters of `M`; the first four entries read 1, 196883, 21296876 and
  842609326.

## Mapping to this repository

- [I] The paper is background for the moonshine and exceptional-structure claims that circulate around the Cayley-Dickson program
  (E8 as the 248-dimensional Lie algebra of the `J - 744` coincidence, the Monster as a symmetry of the moonshine module). It
  contains no Cayley-Dickson content; the repository connects the exceptional Lie algebras to the octonions through the
  [adjacent-algebras survey](../packages/adjacent-algebras.md) and the Albert algebra, and no statement of the pages opened ties
  the Monster to those algebras.
- [I] Corrections the pages support: the series `q^-1 + 196884 q + 21493760 q^2 + ...` is `J = j - 744`, the coefficients are not
  dimensions of irreducible Monster representations (196884 is not among the printed degrees; it equals `196883 + 1`), and
  `T_m` begins `q^-1 + 0 + H_1(m) q + ...` with character values as coefficients.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none to low (a reference for claims about moonshine, to be checked against it).
- [I] Factoring resource estimates: none.

## Boundaries

[I] Pages 3 to 16 and 18 to 32 were not read, so Table 1a, the conjectured conjugacy-class table and every statement beyond the
opening and Table 1 are not asserted. The paper states the conjectures; the proof by Borcherds is outside it.
