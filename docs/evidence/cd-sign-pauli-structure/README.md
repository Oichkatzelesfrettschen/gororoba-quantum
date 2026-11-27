# Cayley-Dickson sign table: Pauli phase plus sparse flips, and the residue decoupling

[`cd_sign_pauli_structure.py`](cd_sign_pauli_structure.py) computes, from `cd_core.cd_sign` (the specification), the F_2 degrees of the
sign function, the flip-set recursion of every row and the residue statement, for n = 3 to 8, and
[result.json](result.json) holds the record. `--check` recomputes it and compares bytes, and `--self-test` runs the controls.

Notation: s_n(p, q) = `cd_sign(2^n, p, q)`, f_n(p, q) in F_2 with s_n = (-1)^f_n, x . y = parity of x AND y, 1_F the
indicator of a set F, and L_a e_q = sum_p a_p s_n(p, q) e_(p XOR q) the left table of `cd_core`.

## Statements

1. **Degrees (S1).** The F_2 degree of f_n is 2, 2, 3, 4, 5, 6, 7, 8 for n = 1 to 8. Each row q -> f_n(p, q), p != 0,
   has degree n - 1 for n = 2 to 8. The associator sign f(p, q) + f(p ^ q, r) + f(q, r) + f(p, q ^ r) has degree n for
   n = 3 to 8, and its support has (D - 2)(D - 4)(D + 6)/2 points (168, 1848, 15960, 130200, 1046808, 8385048). Finite
   checks only; no proof for general n is recorded (open, item 1 below).
2. **Pauli phase plus sparse flips (S2), proved for every n >= 3.** Row p of A_n is f_n(p, q) = c_p + u_p . q + 1_(F_p)(q)
   with (u, c, F) given by the recursion below from the octonion seed. Hence
   L_(e_p) = (-1)^(c_p) X^p Z^(u_p) (I - 2 Pi_(F_p)), a signed Pauli operator times a diagonal reflection of rank |F_p|.
   For n >= 4, |F_p| <= 2^(n-2) - 2 and (u_p, c_p) is the unique closest affine function (script: 0 differences from the
   Walsh argmax, unique maximum, n = 4 to 8).
3. **Residue decoupling (S3), proved for every n >= 3.** For p mod 8 = r != 0, F_p lies in M_r = {q : q mod 8 in {0, r}}.
   For a supported on the class r, L_a e_q = P_a e_q on every q outside M_r (3/4 of the basis), where
   P_a = sum a_p (-1)^(c_p) X^p Z^(u_p), and the span V of e_q with q outside M_r is invariant under both.

The seed at n = 3 is u = [0,7,6,5,4,1,3,2], c = [0,1,1,1,1,1,1,1], F_3(p) = {0, p} for p != 0 and F_3(0) = {}. For
D = 2^m with m >= 3, level m + 1 follows from level m by
- p = 0: (0, 0, {});
- 0 < p < D: u = u_m(p) | D, c = c_m(p), F = F_m(p) U ((D + F_m(p)) symdiff {D, D + p});
- p = D: u = D, c = 1, F = {0, D};
- p = D + p', 0 < p' < D: u = u_m(p'), c = c_m(p') + 1, F = (F_m(p') symdiff {0}) U ((D + F_m(p')) symdiff {D + p'}).

## Proof

Each lemma is also an exhaustive check by the script (`lemmas` in result.json: 0 failures for the transposition identity at n = 1 to 8
and for the four doubling cases at n = 1 to 7).

**Lemma 1 (doubling cases).** For D = 2^m, 0 <= p', q' < D:
(a) s(p', q') = s_D(p', q'); (b) s(p', D + q') = s_D(q', p'); (c) s(D + p', q') = (-1)^[q' != 0] s_D(p', q');
(d) s(D + p', D + q') = (-1)^[q' = 0] s_D(q', p').
*Proof.* Read the first pass of the `cd_sign` loop, whose half is D. Both indices low: nothing changes. Only q high: the pair
becomes (q - D, p) with the sign unchanged, which is (b). Only p high: p -= D and the sign flips when q != 0, which is (c).
Both high with q - D = 0: the loop returns -sign, and s_D(0, p') = 1 gives (d) at q' = 0; with q' != 0 the pair becomes
(q', p') with the sign unchanged. The later passes compute s_D. []

**Lemma 2 (transposition).** s_m(q, p) = s_m(p, q) (-1)^t(p, q), where t(p, q) = [p > 0, q > 0, p != q].
*Proof.* Induction on m. At m = 0, s = 1 and t = 0. For 2D with p = (ph, p'), q = (qh, q'): both low is the hypothesis.
One high, say p low and q = D + q': Lemma 1 gives s(p, D + q') = s_D(q', p) and s(D + q', p) = (-1)^[p != 0] s_D(q', p),
a ratio (-1)^[p != 0] = (-1)^t(p, q), since p < D <= q. Both high: the ratio of s(q, p) to s(p, q) is
(-1)^([p' = 0] + [q' = 0]) s_D(p', q') s_D(q', p') = (-1)^([p' = 0] + [q' = 0] + t_D(p', q')), and the five cases
(p' = q' = 0; p' = q' > 0; exactly one of p', q' zero; both nonzero and distinct) give [p' != q'] = t_(2D)(p, q). []

**Row lemma.** For 0 < p < D, t(p, q') = 1 + [q' = 0] + [q' = p] mod 2, since the indicator of q' outside {0, p} is
1 minus the two disjoint indicators.

**Theorem (S2).** Suppose row p' of A_m equals c + u . q' + 1_F(q') for every p' with its (u, c, F). Then the stated recursion gives
rows of A_(m+1). *Proof.* Write q = (h, q') with h the bit D, so u . q = u . q' for u < D, and (u | D) . q = u . q' + h.
- 0 < p < D. For h = 0, Lemma 1(a) gives f_m(p, q'). For h = 1, Lemma 1(b) and Lemma 2 give f_m(q', p) = f_m(p, q') + t(p, q')
  = f_m(p, q') + 1 + [q' in {0, p}]. So f(p, q) = c + u . q' + h + 1_F(q') + h [q' in {0, p}], which is the affine function
  c + (u | D) . q with flips F at h = 0 and F symdiff {0, p} at h = 1, that is D + (F symdiff {0, p}) = (D + F) symdiff {D, D + p}.
- p = D. Lemma 1(c) at p' = 0 gives [q' != 0] for h = 0, and Lemma 1(d) gives [q' = 0] + f_m(q', 0) = [q' = 0] for h = 1, since
  s_m(q', 0) = 1. So f = 1 + h + [q' = 0], the affine function 1 + D . q with flips at q' = 0 for both h: F = {0, D}.
- p = D + p', 0 < p' < D. For h = 0, Lemma 1(c): f_m(p', q') + [q' != 0] = (c + 1) + u . q' + 1_F + [q' = 0]. For h = 1, Lemma 1(d),
  Lemma 2 and the row lemma: [q' = 0] + f_m(p', q') + 1 + [q' = 0] + [q' = p'] = (c + 1) + u . q' + 1_F + [q' = p']. So the affine part
  is (c + 1) + u . q with flips F symdiff {0} at h = 0 and D + (F symdiff {p'}) at h = 1.
- p = 0: f = 0. []

The seed is a finite fact (the script reproduces all 8 rows of A_3 exactly), so every level n >= 3 is represented exactly.

**Size bound and uniqueness.** For 0 < p < D, |F_(m+1)(p)| = |F| + |F symdiff {0, p}| <= 2|F| + 2; for p = D + p', at most
(|F| + 1) + (|F| + 1); for p = D, 2. At n = 4 every |F| equals 2 (script), so the maximum M_n obeys M_(n+1) <= 2 M_n + 2, whence
M_n <= 2^(n-2) - 2 for n >= 4. Two distinct affine functions on F_2^n differ in 2^(n-1) or 2^n points, so any affine g other than
(u_p, c_p) has distance at least 2^(n-1) - |F_p| > |F_p| from row p when |F_p| < 2^(n-2). The affine part is the unique closest one for
n >= 4. At n = 3 the seven imaginary rows have several closest affine functions (script), so the seed fixes the choice: the
recursion from another closest-affine seed still reproduces every row exactly (the theorem needs only a valid representation)
but leaves the closest affine function at n = 4 (control 3: 12 of 16 rows differ for the lexicographically last choice).

**Theorem (S3).** For n >= 3 and p mod 8 = r != 0, F_n(p) lies in M_r. *Proof.* Induction. At n = 3, F = {0, p} and p = r.
Step to level m + 1, D = 2^m >= 8, so D = 0 mod 8 and (D + x) mod 8 = x mod 8. Case 0 < p < D: F_m(p) is in M_r, D + F_m(p) is in M_r,
and D = 0 and D + p = r mod 8 are in M_r. Case p = D has r = 0, excluded. Case D + p': r = p' mod 8, F_m(p') is in M_r, 0 is in M_r,
D + F_m(p') is in M_r, and D + p' = r mod 8. []

**Corollary.** For a supported on the class r, take q outside M_r. No p in the support has q in F_p, so s(p, q) = (-1)^(c_p + u_p . q) and
L_a e_q = P_a e_q. If also s = q mod 8 is outside {0, r}, then (p XOR q) mod 8 = r XOR s is outside {0, r} (r XOR s = r only at s = 0 and r XOR s = 0
only at s = r), so P_a and L_a map V into V. The restriction L_a|V equals P_a|V, and its spectrum and nullity follow from the Pauli sum alone
(script: 0 mismatches and 0 leaving images, n = 3 to 8).

**Sharpness.** The modulus 8 is minimal for this form: p = 8 + r (r = 1 to 7) has F_4(p) = {r, 8}, which lies outside {0, p}
(control 4: the mod-16 version has 14 violating flip points, in rows 9 to 15 at n = 4). The flip points split evenly: in every level the number of flips
in the class r equals the number in the class 0 (result.json, `flips_in_class_r` and `flips_in_class_0`), so the residue statement is not vacuous.

## Controls (`--self-test`)

Each must fail and does: one flipped sign of A_5 (31 of 32 rows reproduced, 1 differs from the closest affine function); a seed with u_3(1) changed
(2 of 16 rows fail at n = 4); the alternate closest-affine seed (all 16 rows reproduced, 12 leave the closest affine function); the residue
statement at modulus 16; the transposition identity without t (fails at n = 3); and the degree engine on the zero function, parity, a monomial and a point
function (degrees -1, 1, 3, 4). The record carries the exact counts. The orchestration note of the same day reported 10 differing rows for an
arbitrary closest-affine choice; the count depends on the choice, 12 for the lexicographically last.

## Open items

1. S1 for general n: the degree of f_n and of its rows (finite to n = 8) and of the associator sign (finite to n = 8) lacks a proof. The row degree
   n - 1 does not follow from the recursion above, which controls the flip sets and not the algebraic normal form of 1_F.
2. Attainment of max |F_p| = 2^(n-2) - 2: observed at n = 4 to 8 (result.json, `max_flips`); only the upper bound is proved.
3. The closed form of |F_p| through the 2-adic valuation and a Gray-code index, reported by the red team, is not recomputed here.

## Prior work searched

OpenAlex (queries "Cayley-Dickson twisted group algebra", "Cayley-Dickson cocycle", "Cayley-Dickson Walsh", "Cayley-Dickson Boolean function",
"Cayley-Dickson sign", 2026-11-27) and zbMATH (documents, same queries). Records read, abstracts and metadata only, no full text opened:
Albuquerque and Majid (arXiv math/9802116) give the Cayley-Dickson product as a twisted group algebra with an explicit cochain recursion
(used by [the left-table census](../a5-left-table-census/README.md), A5-648); Bales (arXiv 1107.1375; Missouri J. Math. Sci. 28 (2016) 88-96, Zbl 1410.17004; arXiv 1602.02843)
studies the twist tree and its periodicity; Ren and Zhao (arXiv 2205.07986, Adv. Appl. Clifford Algebr. 33 (2023) 49; J. Math. Anal. Appl. 537 (2024) 128240) give an explicit twist function sigma(A, B)
and Hadamard transforms on these algebras; Hagmark and Lounesto (1986, Zbl 0595.15022) compute Clifford and Cayley-Dickson signs by Walsh functions. These
prior records name the sign as a twist or cochain with an explicit formula, so f_n itself is not new. The statements here are the degree table, the affine-plus-sparse-flip
decomposition with its recursion and the flip-size bound, the residue form of the flips and its operator consequence. None of the records read states them, and
a formula of Ren and Zhao may imply them; the comparison is open because their text was not opened. Zenodo preprints on sign evaluators and Pauli obstructions
(10.5281/zenodo.22051873, 10.5281/zenodo.21684256) were seen as titles and abstracts only.

## Commands

```
"$PYTHON" -B -W error docs/evidence/cd-sign-pauli-structure/cd_sign_pauli_structure.py --self-test
"$PYTHON" -B -W error docs/evidence/cd-sign-pauli-structure/cd_sign_pauli_structure.py --write
"$PYTHON" -B -W error docs/evidence/cd-sign-pauli-structure/cd_sign_pauli_structure.py --check
```
