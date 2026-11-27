# Red team: gororoba-quantum PR 1032, A_5 nullity transitions

Verdict: claims 1-3, 5-7 survive with qualifications; claim 4's dimensions survive but its Pfaffian is misstated as intrinsic; claim 8 is false as written; claim 9 is internally consistent. Ranked by consequence.

## Findings

**F1. Claim 8 is false: the README's own specificity is not gated. [proved by reading]**
`validate` (scripts/a5_nullity_transitions.py:397-470) never requires the limits' `exceptional_polynomial == [1,0,1,0]`, the four compression kernel dimensions 8/12/16/16, the count of four junctions, the pencil basis units `[1,2,8,16,17,18,24]`, the `skew_units` content, or the repeat/vanish counts of the twenty zero units. It also never requires README statement 7's "the statement-3 planes are one orthogonal pair with normals ±e_3" nor statement 6's "exactly when". Each is a README sentence with no require, contradicting README:9 ("Each statement has a require"). Cheapest fix: add those equality checks; the current result.json passes them, so the gate would be honest.

**F2. Self-test mutant 5 does not test its named claim. [proved]**
Script:523-530 sets `u = v = e_1` and requires only `rank != 4`. README:44 claims that point has rank 8; the mutant would also pass for rank 0, 2 or 6. Make it `require(rank == 8)`. This is a self-test passing for a weaker reason than named.

**F3. Self-test mutant 3's message names the wrong side. [proved]**
Script:516-520 calls `gram_identity_item((32, 26))` and reports "a unit below the doubling unit"; 26 is above the doubling unit 16. The mutant's cross-term failure is real; the message misdescribes it. Fix the message to "a unit above the doubling unit" or use unit 15.

**F4. The Pfaffian coefficient is frame-dependent, and README:38 states it as intrinsic. [proved by algebra]**
For a skew form `A` and frame `B`, `Pf(B^T A B) = det(B) Pf(A)`. The script's `frame_gram_scalar` is true with Gram 2I (norm sqrt 2), so `det(K)^2 = 2^4 = 16`; the 16 in `16((u.u+m^2+v.v)^2 - 4 Delta)` is `det(K)^2`-normalized, not a coordinate-free constant. A different kernel frame rescales it. Claim 4's dimension results (7, 4, 10) are intrinsic; the printed identity is not. README should say "in the frame K with Gram 2I" and the ledger A5-654 "proved" should read "computed at one W8 point in the frame K".

**F5. The Pfaffian is a restriction of A5-357's G, not a consequence of it. [proved]**
A5-357 gives `G = Q^2 - 4Delta` on the 15 imaginary coordinates. The script's `generic` is a 7-parameter form on the 8-dimensional kernel, and the identity is checked only after mapping through `K`. The map from the kernel to the 15 coordinates is nowhere written down, so the identity cannot be derived from A5-357 alone. This is the answer to the second question: it is neither a tangent-cone nor a transversal-slice statement as recorded; it is an unrecorded restriction map. New content is the map and the 7/4/10 dimensions, not the polynomial.

**F6. Claim 5 is argued, not computed, and the "rank-4 cone" includes the apex. [proved by reading]**
README:46-52 gives the Lagrange chain `2|u x v| <= 2|u||v| <= u.u + v.v`; the script never checks the converse ("exactly when"). At `u = v = m = 0` the Pfaffian vanishes and the rank is 0, so the real zero set is the cone including its apex; "rank-4 cone" is the cone minus the apex. State both.

**F7. Claim 6's "depends only on u x v" is under-tested. [proved by reading]**
`SAME_NORMAL = (6, 7)` tests one parallel-normal pair (script:180, 351). The law is checked on 55 pairs, but invariance under scaling and sign of `n` is checked at one pair only. Cheapest test: add the pair `(2u, 2v)` and `(-u, v)` for one Stiefel pair and require equal planes.

**F8. Claim 1 is sound; no break found. [proved]**
For real `s`, `L^T L` is symmetric PSD, so `dim ker L^T L = nullity L`, and the multiplicity of `x` is that dimension. The generic nullity is the minimum `x`-power over `Q(s)`; the exceptional real `s` are exactly the real roots of the lowest nonzero coefficient. `reduced = lead / gcd(lead, lead')` and `distinct_real_roots == len(rational_roots)` force every real root rational, so an irrational real root would fail the gate rather than escape it. Tried: a higher coefficient with a real root raising nullity without a root of `c_k`; this would violate the PSD argument, and the code's `min` over `x`-powers rules it out.

**F9. Claim 3 is sound; no break found. [proved]**
`projector_constant_on_branch` is an exact rational identity after `cancel`; `product_zero`, `sum_rank == 8`, and `sum_inside_endpoint_kernel` with an 8-dimensional endpoint kernel give orthogonality and spanning. `self_product_zero` is trivially false for a nonzero projector and adds nothing; drop it or replace it with `P^2 == P`.

**F10. Claim 2 holds. [computed]**
result.json paths match `PATH_EXPECTED`; gamma3 has roots `{-1, 1}`, both with nullity 16. The P3 failure is correctly retained.

**F11. Claim 7's hypothesis label is appropriate. [proved by reading]**
Dimensions 4 and 10 fit `H` and `sp(2)`, but the script never checks that the commutant is a division algebra or that the Lie closure is simple. Not implied or refuted by the stated facts. A5-656 "open" is right.

**F12. Claim 9 is internally consistent. [proved by reading]**
The review's corrections match ledger A5-620 (superseded, no CD/Clifford map) and A5-628 (boundary, one abelian generator). The section-at-`mu=i` correction matches `section_item`. The left/right annihilator note is supported for pure elements by `conj(xy) = conj(y)conj(x)`. arXiv 2611.34924 is not in the tree; I cannot check its text.

**F13. `three_form_item`'s label overstates. [proved]**
Script:378-395 counts all ordered `(j,k)` with `i = j^k` without checking the product is nonzero; `nonzero_ordered_triples` is a count of index pairs, not of nonzero values. Rename or add the value check.

**F14. Design T1's acceptance is unmet. [proved]**
docs/design/a5-nullity-transitions-program.md T1 requires a symbolic identity expanded to zero; the record checks 55 rational pairs. Mark T1 "partially met" or add the symbolic pair test (see C1).

## Conjectures the evidence suggests

**C1. The overlap law holds for every Stiefel pair, symbolically.** Falsifier: a pair off the law. Cheapest test: substitute `u = (cos t, sin t, 0)`, `v = (0, 0, 1)` and expand `trace(P P') - 2(1 + n.n'/|n||n'|)` to zero; or test the one rational pair `((1,1,0),(1,-1,0))` not in the ten. [hypothesis]

**C2. The six two-term planes are exactly the three antipodal axis pairs ±e_1, ±e_2, ±e_3.** Falsifier: a rank-4 two-term direction with a non-axis normal. Cheapest test: list the 32 rank-4 directions and their normals. [hypothesis]

**C3. Every W8 point in the H-orbit has pencil dimensions 7/4/10 and the same Pfaffian form in a Gram-2I frame (design T2).** Falsifier: a second W8 point with different dimensions. Cheapest test: run `pencil_item` at `e_1 + e_10 + e_3 + e_20` (the other W8 point) and compare. [hypothesis]

**C4. The commutant is isomorphic to H, not R^4 or C^2.** Falsifier: a commutant element with no square root of -1, or zero divisors. Cheapest test: find `J` in the commutant with `J^2 = -I` and check the algebra generated by two such. [hypothesis]

**C5. The plane map `n -> N(n)` is injective on directions, giving a Veronese embedding of S^2.** Falsifier: two non-parallel normals with equal planes. Cheapest test: compare planes for `n = e_1` and `n = e_1 + e_2`; already distinct in the six. [hypothesis]

**C6. The nullity-4 stratum's Gauss map is the Hopf/Veronese map and its image is all of S^2.** Falsifier: a nullity-4 arc into W8 whose first-order form has rank 0 (design T3). Cheapest test: a direction `w` with `K^T L_w K = 0`, then compute the second-order form and its plane. [hypothesis]

**C7. A real section with `mu` real has real zero divisors at `a = ±b`, `mu = 0`.** Falsifier: no real solution of `Q = G = 0`. Cheapest test: solve `a^2 + b^2 + mu^2 = 0` and `G = 0` over the reals; `a = b`, `mu = 0` gives `Q = 2a^2`, so only `a = 0`, the apex. The section at `mu = i` is complex and its "real points" are not real ambient points; this is the review's correction, and it leaves the real-section question open. [hypothesis]

## Answers

- Defects: F1-F4, F13, F14 are record or gate defects; F5-F7, F10 are claim-scope qualifications; F8, F9, F11, F12 survive.
- Pfaffian: not a known consequence of Q and G as recorded. The identity is `Pf(K^T A K) = det(K) Pf(A)` applied to a 7-parameter restriction; the missing derivation is the explicit map from the 8-dimensional kernel to the 15 imaginary coordinates. Until that map is written, claim 4's polynomial is new only as a computed restriction at one point.
- Conjectures: C1-C7 above, each with its falsifier and cheapest test.
