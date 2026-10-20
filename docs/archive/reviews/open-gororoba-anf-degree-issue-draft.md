The ANF degree of every Cayley-Dickson sign row and of every associator phase has a closed form with a written induction proof in gororoba-quantum ([cd_phase_degree.md](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/main/docs/notes/cd_phase_degree.md), merged in gororoba-quantum #137). No proof assistant has checked it. The proof runs on the `cd_sign` recursion, so `cd_sign_fuel` (with fuel at least n) is the natural Rocq target.

With phi_n(a, b) = [cd_sign(2^n, a, b) = -1] over F_2:

- **Sign rows.** For n >= 2 and m != 0, deg phi_n(m, .) = n - 1.
- **Associator phases.** g_ij(x) = phi_n(j, x) + phi_n(i, j^x) + phi_n(i^j, x) + phi_n(i, j) is the diagonal of W_ij = L_{e_i e_j}^dagger L_{e_i} L_{e_j}. For n >= 3 and distinct nonzero i, j, deg g_ij = max(1, bitlen(max(i, j)) - 2), independent of n.

Proposed statements, on `nat -> bool` truth tables of 2^n entries:

    Theorem sign_row_degree : forall n m,
      2 <= n -> 0 < m < 2 ^ n -> anf_degree n (phi n m) = n - 1.

    Theorem associator_phase_degree : forall n i j,
      3 <= n -> 0 < i < 2 ^ n -> 0 < j < 2 ^ n -> i <> j ->
      anf_degree n (assoc_phase n i j) = Nat.max 1 (Nat.log2 (Nat.max i j) - 1).

`Nat.log2 m - 1` equals bitlen(m) - 2 for m > 0, and truncated subtraction gives 0 below bitlen 2.

**Proof structure.**
- The recursion (R) is phi_n((a', alpha), (y, xi)) = phi'^(xi)(a', y) + alpha (N(y) + xi), with N(y) = [y != 0] and phi^(1) the transpose.
- Three per-level lemmas carry the induction:
  - the commutator lemma C(c, y) = N(c) + delta_0(y) + delta_c(y);
  - the involution lemma phi(a, x) + phi(a, a^x) = N(a);
  - the two-point lemma deg(delta_p + delta_q) = k - 1 for p != q.
- The key step: over the top index bit, the two halves of every associator phase differ by the constant N(i') + N(j') + N(i'^j').

Each per-level lemma is a finite identity that suits `vm_compute`. The induction needs (R) as a lemma about `cd_sign_fuel`, together with the ANF coefficient formula.

**Acceptance test.**
- Both theorems compile under the pinned toolchain, with `Print Assumptions` showing no axioms beyond the standard library.
- At n = 4, a `vm_compute` cross-check reproduces the census: 84 unordered pairs of degree 2, together with the 21 pairs of degree 1 already present at n = 3.

The gororoba-quantum replay `scripts/cd_phase_degree.py --max-n 8` checks every identity cell by cell through dimension 256.
