# Levratti 2026 -- Active Stabilizers in Reed-Muller CSS Codes from Cayley-Dickson Zero-Divisors (author-hosted page)

Tag convention: [P] marks a statement or number given in the paper; [I] marks an
inference or a computation by the note author, with its basis named. Relevance
ratings and numbered action items are the note author's judgment and count as [I].
Citation and provenance bullets are bibliographic facts from the PDF, the download
record, or the hosting page. Every experimental figure below is author-reported
and unverified; [P] on such a figure records only that the page says it.

## Citation and provenance

- Title: Active Stabilizers in Reed-Muller CSS Codes from Cayley-Dickson Zero-Divisors.
- Author: Giovanni Levratti, Independent Researcher, Modena, Italy. Single author.
- Stated date: none. The page gives "Version: v1 - Year: 2026" and states a hardware date of 27 May 2026 inside the abstract.
- Hosting URL: https://www.informationalidentityboundary.info/paper5.html (author-hosted site). The page lists the work as "Paper 5" of the series "Zero-Divisors in Cayley-Dickson Algebras" and links a "Download PDF" and a DOI, https://doi.org/10.5281/zenodo.20431754.
- sha256 of the saved HTML page: 0676656c1339f869853edc8993a902b8ae07071a6610e7980e445548bee8ac81. No PDF exists for this note.
- Local copy: kept outside this repository; fetch from the URL above and verify the sha256. The page changes without notice, so the hash identifies only the capture read here.
- Pages read: the page text only, about 340 words (abstract, series line, citation block); no figures, tables, theorem statements, proofs, or experimental sections were retrievable.
- Provenance caveat: author-hosted web page, not peer reviewed, not an arXiv record or journal article. The PDF behind the "Download PDF" link was not retrieved and the Zenodo record (10.5281/zenodo.20431754) was not retrieved. Everything below states what the page text says and nothing more.
- Numbering: the series places this work as Paper 5, while the manuscript in the note levratti-2026-fano-css.md cites this work as its reference [4] and a different manuscript ("A Clifford Representation of the Fano Zero-Divisors") as [5]. The DOI string on the page equals the DOI of that manuscript's reference [4] [I].

## Main claims

[P] The abstract states three results connecting zero-divisor structure of the Cayley-Dickson algebras A_n to the stabilizer formalism of quantum error-correcting codes.

- [P] Step 1 (bijection, n = 4). The 7 lo-flats of ZD(4), defined on the page as weight-4 subsets {a, b, c, d} of {1..7} with a xor b xor c xor d = 0, biject explicitly with the 7 non-identity elements of the X-stabilizer group of the Steane [[7,1,3]] code. All 7 lo-flats carry the same sign-parity pattern: pi(EE|FF) = -1 (inactive), pi(EF_1) = pi(EF_2) = +1 (active).
- [P] Step 2 (operator translation). For every mixed flat F = {i, j, 8+k, 8+l} in A_4, the identity pi_A pi_B pi_C = -1 translates into the Clifford-group identity (Z_alpha Z_beta)(X_alpha X_gamma)(X_beta X_gamma) = -Y_alpha Y_beta. The page calls the global phase -1 "the precise Clifford avatar" of the sign-parity identity. The operator -Y_alpha Y_beta is called a detectable error with full-group syndrome weight 2^(n-2), "proved for all n >= 4 and verified on QPU".
- [P] Step 3 (extension to n = 5, "verified on QPU"). The 15 Fano planes of PG(3, F_2) biject with the 15 non-identity elements of the X-stabilizer group S_X of the [[15,7,3]] code (4 generators). The phase identity and the syndrome formula extend to all n >= 4 (a "Universal Phase Lemma").
- [P] Author-reported hardware claim: "Syndrome structure verified on ibm_kingston (156-qubit QPU, job d8bm67ijki0s73aq6idg, 27 May 2026)". The page gives no circuit, shot count, qubit selection, calibration, error bar, or result table. Unverified here.
- [P] Classification claim: a Fano plane W in PG(3, F_2) is Type-B if and only if 8 is in W or W = {1..7}, where 8 = (1, 0, 0, 0) is "the bridge element between A_3 and A_4 in the Cayley-Dickson tower". The Type-A and Type-B definitions are not on the page.
- [P] The page carries a BibTeX block citing the work as a Zenodo record, "Paper 5 in the series Zero-Divisors in Cayley--Dickson Algebras, v1", year 2026.

## Mapping to this repository

Relevance ratings. (a) Calibration-aware or noise-adaptive compilation: none [I]. (b) Cayley-Dickson, octonion, zero-divisor, nonassociative structure: low for what can be assessed from the page, with substantial content unassessed [I]. (c) Shor's algorithm and factoring resource estimates: none [I].

- [I] Consistency across the two Levratti sources. The manuscript in levratti-2026-fano-css.md describes its reference [4] as supplying Theorem 3.1 (lo-flat supports equal the supports of the 7 non-identity stabilizer elements), Theorem 4.2 (the Clifford phase -1 and the product -Y_alpha Y_beta of three balanced half-operators), and Theorem 5.1 (n = 5). Those three descriptions align with Steps 1, 2, and 3 of this page. The alignment is textual agreement between two documents by one author and adds no independent evidence.
- [I] Step 1 against the repository's "Reference: Fano plane and the Steane code" in gororoba_quantum/DESIGN_NOTES.md. The lo-flats are the complements of the Fano lines, which are the weight-4 supports of the non-identity elements of the dual code of the [7,4,3] Hamming code, so Step 1 restates the incidence the repository already calls standard and not novel. Whether tying those flats to the zero-divisor set ZD(4) is new cannot be assessed from the page; that content lives in the unretrieved manuscript.
- [I] Step 2 checked by hand. With ZX = iY on each qubit and Z, X on distinct qubits commuting, (Z_alpha Z_beta)(X_alpha X_gamma)(X_beta X_gamma) = (Z_alpha X_alpha)(Z_beta X_beta)(X_gamma X_gamma) = (iY_alpha)(iY_beta) = -Y_alpha Y_beta for any three distinct qubits alpha, beta, gamma. The Pauli identity is an identity of the Pauli group and carries no zero-divisor structure. The page's claim is the connection of this identity to the sign-parity product pi_A pi_B pi_C, and that connection requires the paper.
- [I] Overlap with Designs B and D, assessable from the page. Designs B and D (gororoba_quantum/DESIGN_NOTES.md) use sedenion zero-divisor pairs (e_i + t e_j)(e_k + s e_l) = 0 from cd_core.sedenion_zero_divisor_corpus. Computed against the page's mixed-flat shape {i, j, 8+k, 8+l} with indices xor to zero (the page defines the xor rule for lo-flats only, so the rule is assumed for mixed flats): all 336 corpus rows have i xor j xor k xor l = 0 and exactly two indices below 8 and two at or above 8; the 336 rows use 42 distinct four-index supports. The index shape of the repository's zero divisors coincides with the page's mixed flats. This is the only overlap visible from the page.
- [I] Not assessable from the page: the sign convention of the page's pi (the repository's signs come from the cd_sign recursion in cd_core.py, following the open_gororoba kernel), the definition of "flat" and of "active" and "inactive" for mixed flats, the definition of Type-A and Type-B, whether the page's A_4 zero divisors are the products (e_i + t e_j)(e_k + s e_l) = 0 or a different set, the proof of the syndrome weight 2^(n-2), the construction of the stabilizer code for n = 5, and every property of the QPU runs.
- [I] The hardware statement concerns syndrome structure of the stabilizer code. The page describes no circuit that realizes a zero-divisor product, annihilation, or interference, so it overlaps none of the observables of Design B (P_zd over P_control) or Design D (the phase fringe) visibly. The reported job on ibm_kingston is a backend the repository also targets and is no evidence about the repository's circuits.
- [I] Label for Designs B and D against this source: no prior overlap is visible for the construction or the observables; the index-shape coincidence above is the extent of what the page text supports. The repository's own label for the circuits and compile records stays new implementation or measurement. Label for the page's Step 1 against the repository's reference section: known theorem reproduced (standard incidence), with the zero-divisor tie unassessed.
- [I] Every hardware figure on the page ("verified on QPU", 156 qubits, ibm_kingston, the job identifier, 27 May 2026) is author-reported and unverified. The job cannot be looked up without the author's account and the page gives no data, so it enters no estimate or comparison in this repository.

## Action items

1. Retrieve the PDF and the Zenodo record 10.5281/zenodo.20431754, record their sha256, and replace this note's page-only reading. Acceptance: Theorems 3.1, 4.2, and 5.1 read in full, the definitions of flat, Type-A, and Type-B read, and the hardware section's circuit and counts located or reported absent. Source: the page abstract and levratti-2026-fano-css.md, Section 1.
2. Add a classical self-test to the cd_core self-check that every row of the signed sedenion corpus has four indices with xor zero, two below 8 and two at or above 8, and that the corpus uses 42 distinct supports. Acceptance: 336 of 336 rows and 42 supports, exact. Source: Step 2's mixed-flat shape.
3. Cite none of the page's hardware figures and write no claim in DESIGN_NOTES.md that depends on them. Acceptance: no occurrence of the job identifier or the "verified on QPU" wording in repository text. Source: the abstract's Step 3 paragraph.
4. The page creates no QPU case under the repository's approval rule and imposes no new calibration reading.
5. Add the README.md table row for this note with ratings (a) none, (b) low, (c) none, and the caveat that only about 340 words of page text were read. Source: this note.
