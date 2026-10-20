# Boyar, Find, Peralta 2016 -- On Various Nonlinearity Measures for Boolean Functions (PMC4957665)

Tag convention: [P] marks a statement or number given in the paper; [I] marks an
inference or a computation by the note author, with its basis named. Relevance
ratings and numbered action items are the note author's judgment and count as [I].
Citation and provenance bullets are bibliographic facts from the saved page, the
download record, or the source text.

## Citation and provenance

- Title: On Various Nonlinearity Measures for Boolean Functions.
- Authors (3): Joan Boyar (Department of Mathematics and Computer Science, University of Southern Denmark), Magnus Gausdal Find, Rene Peralta (both listed with the Information Technology Laboratory, National Institute of Standards and Technology, USA; the page states that most of Find's work was done at the University of Southern Denmark).
- Venue and year: Cryptography and Communications 8(3):313-330, issue date 2016 Jul, printed on the page as "Cryptogr Commun. 2015 Jul 28;8(3):313-330" (published in final edited form), DOI 10.1007/s12095-015-0150-9, PMCID PMC4957665, PMID 27458499, NIHMSID NIHMS797706. The PMC copy is the NIH author manuscript, available in PMC from 2017 Jul 1; its footnote calls it a preliminary version of the accepted article, and states that parts appeared in the CIAC 2013 paper "Four measures of nonlinearity" (reference [2]). The page carries both dates, 28 Jul 2015 and issue 2016; the publisher's version is not read here.
- Working URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC4957665/
- sha256 of the saved HTML snapshot: 35ece83404bb1034270285b74aa0c71c4b8c5c79c8e7cc27c7cff55edf8149a0. The hash identifies the saved snapshot only; a later fetch of the live page may differ.
- Local copy: kept outside this repository; fetch from the URL above and compare against the sha256 with the caveat just stated.
- Pages read: the whole article text, Sections 1 to 8, Tables 1 and 2, footnotes, and the reference list (the saved text is a single flattened line, and Table 1 was additionally read from the HTML table markup). The extracted layout of Table 1 does not fix which function of a pair belongs to the row measure and which to the column measure, so the attributions below rest on the values of Table 2 and the text of Sections 2 and 3.

## Main claims

[P] Six common nonlinearity measures for Boolean functions -- nonlinearity, algebraic degree, annihilator immunity, algebraic thickness, normality, and multiplicative complexity -- are pairwise incomparable: for every pair there exist two functions that the two measures rank in opposite order.

- [P] Definitions (Sec. 1, 2.1): the ANF of f in B_n is the sum over S of alpha_S times the product of x_i for i in S. Nonlinearity is the Hamming distance to the nearest affine function, between 0 and 2^(n-1) - ceil(2^(n/2-1)); bent functions attain 2^(n-1) - 2^(n/2-1) and exist iff n is even. Algebraic degree is the largest |S| with alpha_S = 1. Annihilator immunity AI(f) is the least degree of a nonzero g with f g = 0 or (f + 1) g = 0; 0 <= AI(f) <= ceil(n/2). Multiplicative complexity is the least number of AND gates over (XOR, AND, 1). Algebraic thickness and normality are as defined in Sec. 2.1. All six measures are invariant under invertible affine maps of the inputs.
- [P] Sec. 2.4: low nonlinearity implies low annihilator immunity [16]; bent functions have degree at most n/2; since f + 1 is an annihilator of f, AI(f) is at most the degree; adding a linear function to f changes AI by at most 1 [12]; a function of degree d has normality at least Omega(n^(1/(d-1))); weakly k-normal f has nonlinearity at most 2^(n-1) - 2^(k-1) (Proposition 1).
- [P] Sec. 2.3: almost every function has AI = (1 - o(1)) n/2, nonlinearity close to 2^(n-1) - 2^(n/2-1) sqrt(2 n ln 2), and normality at most 1.01 log n; the fraction of functions with degree at least n - 1 is 1 - 2^(-(n+1)).
- [P] Sec. 3 and Table 2: the elementary symmetric function Sigma_2^n (sum of all x_i x_j) is bent for even n, with degree 2, annihilator immunity 2, and multiplicative complexity floor(n/2). The function Sigma_n^n = x_1 ... x_n has nonlinearity 1 (distance 1 to the zero function), annihilator immunity 1 (x_1 + 1 annihilates it), degree n, multiplicative complexity n - 1, algebraic thickness 1, and normality n - 1. MAJ_n has annihilator immunity ceil(n/2) and, for n a power of 2, degree n.
- [P] Sec. 3 remark: for f with high degree and high multiplicative complexity, g(x_1, ..., x_n) = f(x_1, ..., x_(n-1)) x_n has high degree and high multiplicative complexity, annihilator immunity 1, and normality n - 1: "annihilator immunity and normality fail to capture the intuitive notion of nonlinearity".
- [P] Sec. 4: Theorem 2: nonlinearity s > 1 implies multiplicative complexity at most min(s (n - 1), (2 + o(1)) s n / log s). Corollary 1: multiplicative complexity M implies nonlinearity at most 2^(n-1) - 2^(n-M-1). Sec. 5: Theorem 3 relates algebraic thickness to multiplicative complexity. Sec. 6: Theorem 4: a collision-resistant function from n to m bits has multiplicative complexity at least n - m.
- [P] Sec. 7 (Lemmas 5 and 6): the symmetric functions F_n = sum over k >= 3 of Sigma_k^n and G_n = Sigma_2^n + Sigma_n^n, with nonlinearity one below the symmetric optimum and degree n, have annihilator immunity at most 2.

## Mapping to this repository

- [I] Repository claim: "degree alone carries no security claim" (literature/notes/topics/open_gororoba_handoff.md, Boolean functions row).
  - Source: Abstract and Sec. 3; Table 2 rows Sigma_2^n and Sigma_n^n.
  - Model map: Sigma_2^n has degree 2 with maximal nonlinearity (n even) and AI 2; Sigma_n^n has degree n with nonlinearity 1 and AI 1. This one pair ranks degree against nonlinearity and against annihilator immunity in opposite order, so neither measure follows from degree. Roetteler's footnote (note 0811.3208) states the degree-nonlinearity point for bent functions of degree 2. The bound AI <= degree is a one-directional inequality, not an implication in the other direction.
  - Label: known theorem reproduced.
  - Not established by the source: any statement about hidden-shift or other quantum query cost. All six measures are classical cryptanalytic distances from linearity.
- [I] Repository claim: "f(u, t) = [u != 0] + t stays the permanent negative control (degree n - 1, nonlinearity 2, algebraic immunity 2, verified through n = 11 in the replay)" (literature/notes/topics/open_gororoba_handoff.md, Boolean functions row).
  - Source: Table 2 row Sigma_n^n; Sec. 2.4 (adding a linear function changes AI by at most 1).
  - Model map: with u in F_2^(n-1), [u != 0] = OR_(n-1)(u) = 1 + Sigma_(n-1)^(n-1)(u + 1), a translate and complement of the AND function. The six measures are affine invariants, and nonlinearity, degree, and AI are unchanged by adding 1, so OR_(n-1) has the profile of Sigma_(n-1)^(n-1): degree n - 1, nonlinearity 1 on n - 1 variables, AI 1. Adding the linear variable t keeps the degree at n - 1 and, by the Sec. 2.4 bound, gives AI at most 2, which is the pattern of the repository's values (degree n - 1, AI 2). The nonlinearity 2 is the repository's measurement. The function f is not in the paper.
  - Label: new implementation or measurement (the values of nonlinearity and annihilator immunity for this specific f, through n = 11).
  - Not established by the source: the exact values for f(u, t), or any property beyond the profile of the AND function and the AI-plus-linear bound.
- [I] Repository claim: "Its phase is the OR of those bits" (gororoba_quantum/verify.py, docstring of check_associator_walsh_hierarchy; the check requires the exact ANF coefficient set for the pair (1, 2^(n-1)), n = 3 through 7).
  - Source: Table 2 row Sigma_n^n; Sec. 2.4 (bent functions have degree at most n/2).
  - Model map: the phase is OR_m on the m = n - 2 live bits, with bits 0 and n - 1 absent from the ANF. On n variables its degree is m = n - 2 and its AI is 1 (x_1 annihilates the complement 1 + OR_m = [live bits = 0]). Its distance to the constant 1 is the weight of [live bits = 0] on n variables, 2^(n-m) = 4, and no affine function is closer for m >= 2, so its nonlinearity on n variables is 4 for n >= 4 (a note author's computation). For n >= 5 the degree n - 2 exceeds n/2, so the rung is not bent; at n = 4 it is a rank-2 quadratic on 4 variables, also not bent. The rung therefore has the high-degree, low-nonlinearity, AI-1 profile of Sigma_n^n.
  - Label: new implementation or measurement (the exact-ANF check for n = 3 through 7).
  - Not established by the source: any statement about measured circuits. The profile says the "degree up to n - 2" of the Design C ladder (gororoba_quantum/DESIGN_NOTES.md) carries no strength information for this rung.
- [I] No repository claim: Cross-source remark on the direction of "strength". In note 0811.3208 and note 1103.3017 the bent functions, the maximum of nonlinearity, are the hidden-shift instances a quantum computer solves in O(n) or constant queries, while the delta-type extreme (OR and AND functions, nonlinearity 1) is unstructured search with Theta(sqrt(2^m)) quantum queries. The measure that controls the quantum algorithm there is the minimum influence, which is not one of the six measures of this paper. A strength ordering by the six measures does not predict hidden-shift cost in either direction.

## Action items

1. Cite Table 2 (rows Sigma_2^n and Sigma_n^n) and the Sec. 3 remark when stating that degree carries no strength claim; do not cite a specific Table 1 cell until the pair attribution is re-read from the publisher's PDF.
2. Compute the six measures that are finite computations (nonlinearity, degree, annihilator immunity) for the rung omega_(1, 2^(n-1)) at n = 4 to 7 and for f(u, t) at the same n. Acceptance: nonlinearity 4, degree n - 2, AI 1 for the rung (n >= 4); degree n - 1, nonlinearity 2, AI 2 for f(u, t); both agree with the profile above.
3. Add the sentence "the measure that governs hidden-shift cost is the minimum influence" to any repository statement that ranks oracle functions by nonlinearity or degree.
