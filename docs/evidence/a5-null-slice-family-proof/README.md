# A_5 null-slice families: proof for every n

The two so(m,1) families of the null slices hold for every level of the Cayley-Dickson tower:
- the slice with time 7 * 2^(n-3) and space [1, 2^(n-2)) without 2^(n-3), for n >= 4;
- the slice with time 2^(n-1) + 2^(n-2) + 8 and space e_1..e_7, for n >= 6.

The proof goes through the commutation-set lemma of the
[left-table census](../a5-left-table-census/README.md) (statement 6, ledger A5-636) and the cd_sign recursion. Ledger
rows A5-618, A5-626 and A5-636 now read proved.
[`scripts/a5_null_slice_family_proof.py`](../../../scripts/a5_null_slice_family_proof.py) checks every lemma case
exhaustively at the levels named below.

## Notation

- s_n(p, q) = cd_core.cd_sign(2^n, p, q), and H = 2^(n-1).
- chi_n(a, tau, k) = s(tau, k) s(a, tau ^ k) s(a, k) s(tau, a ^ k) is +1 exactly where L_a and L_tau commute on e_k.
- C(a, tau) = {k : chi = +1}.

## Proof

**Step 0, the recursion.** The first pass of the cd_sign loop either returns or leaves indices below H, so:
- (LL) s_n(p, q) = s_(n-1)(p, q) for p, q < H;
- (LH) s_n(p, H + q') = s_(n-1)(q', p);
- (HL) s_n(H + p', q) = -s_(n-1)(p', q) for q != 0, and s_(n-1)(p', 0) for q = 0;
- (HH) s_n(H + p', H + q') = -1 for q' = 0, and s_(n-1)(q', p') otherwise.

The table these cases build equals cd_core.cd_sign at n = 1 to 10.

**I1 to I3.** s(x, 0) = s(0, x) = 1; s(x, x) = -1 for x != 0; s(x, y) = -s(y, x) for distinct nonzero x, y. Each
follows by induction on n through Step 0, splitting on whether x and y are below H.

**Lemma T.** chi_n(a, H, k) = -1 for every a outside {0, H} and every k, so L_a and L_H anticommute everywhere.
Expanding the four factors with Step 0 splits on a below or above H, and k below or above H. In each part, the
generic case and the cases k (or k') in {0, a} each give -1.

**Lemma U.** If a, t < H are distinct and nonzero, then chi_n(a, t, k) = chi_(n-1)(a, t, k mod H).
- For k < H, every argument stays low (LL).
- For k = H + k', LH transposes each of the four factors. The four transpositions are antisymmetric for generic k'
  (I3), and exactly two of them are symmetric for k' in {0, t, a, a ^ t}. Either way the product is +1.

**Lemma R, the peel.** Let a, t < H with a != 0 and t outside {0, a}, and let S = {0, a, t, a ^ t}. Then
chi_n(a, H + t, k) = sigma_S(k mod H) chi_(n-1)(a, t, k mod H), with sigma_S = +1 on S and -1 elsewhere.
- For k < H, HL contributes -1 unless k is in {0, a}, and LH turns s(a, H + (t ^ k)) into s'(t ^ k, a). That
  differs from s'(a, t ^ k) by -1 unless k is in {t, t ^ a} (I3). The product is -1 for generic k and +1 on S.
- For k = H + k', three transpositions and the HH exception (which fires at k' = 0 and k' = a) give the same
  sigma_S.

In set form, C_n is the set of k whose residue mod H lies in the symmetric difference of S and the complement of
C_(n-1).

**First family (n >= 4).** Take h = 2^(n-3), tau = 7h and a in [1, 2h) without h.
1. Peel at level n with t = 3h, so S = {0, a, 3h, a ^ 3h}.
2. Peel at level n - 1 with t = h, so S1 = {0, a, h, a ^ h}.
3. At level n - 2, tau = h is the top unit, and Lemma T gives chi = -1.

So chi_n = -sigma_S(k mod 4h) sigma_S1(k mod 2h). S reduces mod 2h into S1, so chi_n = +1 exactly when
k mod 4h lies in {h, 2h, a ^ h, a ^ 2h}. That makes C_a = {h, 2h, 5h, 6h} u {a ^ h, a ^ 2h, a ^ 5h, a ^ 6h}, which is
T u (T ^ a ^ tau) with T = {h, 2h, 6h, 5h}.

**Second family (n >= 6).** Take Q = 2^(n-2), tau = 3Q + 8 and a in 1..7.
1. Peel at level n with t = Q + 8.
2. Peel at level n - 1 with t = 8.
3. Lemma U from level n - 2 down to level 5, since a and 8 lie below every H >= 16.
4. At level 4, tau = 8 is the top unit, and Lemma T gives chi = -1.

The same composition gives C_a = T u (T ^ a ^ tau) with T = {8, Q, 3Q, 2Q + 8}.

**Consequences.**
- The lemma gives disjoint stars by the XOR sums of census statement 6, so the sufficient direction of A5-617
  gives the so(m,1) relations at every n.
- The supports leave a common kernel of 2^n - 4 - 4 (2^(n-2) - 2) = 4 in the first family and 2^n - 4 - 28 =
  2^n - 32 in the second.
- The second family's space is Clifford at every n: Lemma U carries chi(a, b, k) for distinct a, b < 8 down to the
  octonions, where alternativity makes L_a and L_b anticommute.

## Evidence classes

- **Proved.** Step 0, read from the cd_sign loop; I1 to I3, Lemma T and the lower half of Lemma R, by the case
  splits above; the composition and the consequences.
- **Proved by case split and checked exhaustively.** The upper-half cases of Lemmas R and U (k = H + k'). Each case is
  a sign identity independent of n, and the record checks every a, t and k at n = 2 to 9.
- **Computed corroboration.** The family claim from the recursion table at n = 4 to 12; the census record's own check
  through the vectorized signs; and the direct relation checks to 4096
  ([family relations](../a5-null-slice-family-relations/README.md)).

## Controls

`--self-test` runs three paired controls:

| Control | Baseline | Mutant |
|---|---|---|
| peel sign | sigma_S matches at n = 5 | the inverted sign does not |
| top unit | Lemma T at tau = 16 | tau = 16 + 5 is not empty |
| recursion table | equals cd_sign at n = 5 | one negated entry does not |

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_null_slice_family_proof.py --check docs/evidence/a5-null-slice-family-proof/result.json
"$PYTHON" -B -W error scripts/a5_null_slice_family_proof.py --self-test
```
