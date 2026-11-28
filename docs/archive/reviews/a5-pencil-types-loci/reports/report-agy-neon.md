I am running the VB off-unit-sum check (`probe_d`) and the symbolic BDI normal-form check (`probe_e`) on `the compute workstation`; waiting for both to finish before running the follow-up checks on total $F_4$ and $W_8$ outside the census.
Waiting for `probe_k.py` on `the compute workstation` (independent verification of the VB and N+- full Pfaffians, all 100 `VB + 2w` nullity-8 lines, and 15 diverse Case-1 $\alpha$ plus global $J_k$ commutation on $\mathbb{R}^{32}$).
# Red-team report: gororoba-quantum PR 1053 (`a5-pencil-types-loci`, head `f917aa07b`)

All computations ran read-only over the compute workstation in `WORKTREE` (`f917aa07b`, clean) under `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON"` with Singular 4.4.1, scratch under `SCRATCH`. No repository files were modified.

## Verdict by claim (ranked by consequence)

### 1. Claim 6 (Ledger and README vs `validate` and loop bounds) — **FALLS IN PART** (`proved` by source inspection)

1. **Overstated scope in `A5-677` (`docs/evidence/a5-exceptional-fibers/ledger.tsv:651`)**:
   - The statement column claims *"every point y = (p, q) of W8 built from a census pair of sedenion zero divisors (statement 18) has the pencil type its dim (ker L_p n ker L_q) names ... with matched bounds"*.
   - **Defect A (unsampled qualifier missing)**: Statement 18 (`certificates.json`) has 3,518,410 `dim A = 0` pairs; `scripts/a5_pencil_types_and_loci.py:117-129` checks only 3,005 of them (`(131 * i + j) % 1171 == 0`, 0.085%). The sampling restriction appears in the script docstring, README statement 20, and the ledger evidence column, not in `A5-677`'s statement column.
   - **Defect B ("with matched bounds")**: 33 of the 177 type-R points do not use two-sided bounds; `scripts/a5_pencil_types_and_loci.py:143-155` catches `ValueError` from `a5_pencil_certificates.structure_item` (`ENTRY_BOUND`) and falls back to `a5_nullity_transitions.structure_item`, storing `[d, d]` from exact SymPy dimensions as if they were matched bounds. Catching bare `ValueError` at line 148 would also mask any future `ValueError` in `structure_item` beyond `ENTRY_BOUND` (`scripts/a5_pencil_certificates.py:266`).
2. **README sentences lacking a `require` in `validate()` (`scripts/a5_pencil_types_and_loci.py:484-552`)** despite `docs/evidence/a5-nullity-transitions/README.md:34` (*"Each statement has a `require` in the script's `validate`"*):
   - Statement 19 (`README.md:202-203`): `validate()` lines 486–489 omit `16 in full["VB"]["units"]` (checked for `N-`/`N+` at line 492).
   - Statement 20 (`README.md:206-212`): `validate()` lines 499–508 check `pairs_by_dim["0"] > 2000` and `dim0_distinct_p > 1000` rather than `== 3005`, omit checks on the W8 counts (`177`, `3,282`, `139`), the 33 `sympy` fallbacks, and the named non-W8 orbits (`Iso`, `S0`, `S4_VQ`, `B9`, `N+-`).
   - Statement 22 (`README.md:223-232`): `validate()` lines 520–526 check `v > 0` for ideal membership rather than exponents `3, 2, 2`, omit `ideal_dimension == 4`, never check the printed `lead Q` / `lead G` formulas (independently confirmed in `probe_a.py`: `2*x3 + 2*I*x4` and `4*(x3 + I*x4)^2 + 4*(x11 + I*x12)^2`), and never check the `e_10` vs `e_1 + e_10` comparison (`README.md:231-232`).
3. **Citation and boilerplate slips**:
   - `README.md:214` cites the proof of Theorem 14.6 of Biss, Dugger, and Isaksen (`math_0511691.pdf`) as pages 23 to 25; the proof runs through page 26 (Subcase 2 and the (S1)/(S2) block matrices; the normal form sits on pages 23–24).
   - `ledger.tsv:650-652,654` (`A5-676`, `A5-677`, `A5-678`, `A5-680`) carry boilerplate *"one Singular standard basis over Q in dp"* in their evidence columns; only `A5-679` (`vb_singular`) invokes Singular.

### 2. Claim 5 (Order-3 arc limits at `e_1 + e_10`, Statement 23, `A5-680`, `A5-660`) — **HOLDS AS STATED; ORDER-4 OBSTRUCTION AND CANCELLATION FOUND** (`proved` + `computed`)

- **Derivation audit (`proved`)**: For $L(s) = L_0 + s L_w + s^2 L_v + s^3 L_u + O(s^4)$ with $w \in Z$ ($K^T L_w K = 0$), Rellich's theorem on the real symmetric family $L(s)^T L(s)$ guarantees an analytic kernel branch $x(s) = \sum s^j x_j$.
  - Order 1: $x_1 = -L_0^+ L_w K c_0 + K c_1$.
  - Order 2 projected by $K^T$: $F_2 c_0 = 0$ with $F_2 = K^T(L_v - L_w L_0^+ L_w)K$; $c_1$ drops out because $K^T L_w K = 0$.
  - When $F_2 = 0$, $x_2 = -L_0^+(L_v - L_w L_0^+ L_w)K c_0 - L_0^+ L_w K c_1 + K c_2$.
  - Order 3 projected by $K^T$: $F_3 c_0 + F_2 c_1 + (K^T L_w K) c_2 = 0$, so both $c_1$ and $c_2$ drop out identically, leaving $F_3 = K^T(L_u - L_w L_0^+ L_v - L_v L_0^+ L_w + L_w L_0^+ L_w L_0^+ L_w)K$.
  - Real ($e_0$) and $e_{16}$ components vanish on any zero-divisor arc (BDI Lemmas 9.4–9.5, `math_0511691.pdf`, pp. 15–16). `pinv` (`scripts/a5_pencil_types_and_loci.py:375`) is the exact Moore–Penrose pseudoinverse $L_0^+$, and `set(permutations(triple))` (line 415) produces exact multinomial weights for the 2,600 cubic terms. Because every nonzero pencil element has rank 4 or 8 (quaternion commutant), the first nonzero $F_m$ ($m \le 3$) on a nullity-4 arc has rank 4 and its kernel lies on the 2-sphere.
- **Order-4 stress test (`computed`, `probe_b.py`, `probe_c.py`, `probe_f.py`, `probe_h.py`, `probe_i.py`)**:
  - The standalone 4th-order term $m_4(w) = K^T L_w L_0^+ L_w L_0^+ L_w L_0^+ L_w K$ **leaves both the 7-dim pencil and $\mathfrak{sp}(2)$** on 8/24 basis vectors of $Z$ and 20/20 dense $w \in Z$ (`probe_c.py`: `in_pencil=0, in_sp2_not_pencil=0, outside_sp2=20`). A naive term-by-term extension of `w8_schur` to order 4 therefore fails.
  - However, when $L_2, L_3$ cancel $F_2 = F_3 = 0$, the **total** effective form $F_4$ returns to the 7-dim pencil on all 8 basis vectors (`probe_c.py`) and 20/20 dense arcs (`probe_f.py`: `in_pencil=20`), and $F_5, F_6$ likewise stay in the 7-dim pencil on 3/3 dense arcs with arbitrary $Z$-components (`probe_i.py`).

### 3. Claim 4 (VB rank-4 locus and second-order form, Statement 22, `A5-679`) — **HOLDS** (`proved` + `computed`)

- **Rank-4 locus (`proved`)**: Vanishing of all 768 nonzero $6 \times 6$ principal sub-Pfaffians characterizes rank $\le 4$ for skew matrices; `m^3`, `(x3^2+x4^2)^2`, `(x11^2+x12^2)^2` in `std(I)` over $\mathbb{Q}$ (`dp`) force real points of rank $\le 4$ onto `m = x3 = x4 = x11 = x12 = 0`, and the $4 \times 4$ sub-Pfaffians `-4(x9^2+x14^2)` and `4(x10^2+x13^2)` force rank $\ge 4$ off the origin.
- **Off-unit-sum stress test (`computed`, `probe_b.py`, `probe_d.py`, `probe_g.py`, `probe_j.py`)**: Across 324 multi-term combinations, 100 dense plane+$Z$ directions, 1,305 pairs `w1 + c w2` of nullity-8 directions, and 297 `e_1 + e_10 + z` perturbations, zero counterexamples appeared: all 396 four-term combinations and 28 `e_1 + e_10 + z` directions with `sec_rk == 0` had nullity `(8, 8, 8, 8)` at $s = 2, 3, 5, 7$; all directions with `sec_rk > 0` had `sec_rk == 4` and nullity 0 or 4. The general converse (`sec_rk == 0 => nullity 8` for arbitrary real plane directions) remains unproved outside the tested families.

### 4. Claim 3 (BDI normal form and $J_k$, Statement 21, `A5-678`) — **HOLDS** (`computed`)

- **Convention check (`proved`)**: `cd_core` doubling matches BDI Definition 2.1 (`math_0511691.pdf`, p. 3), and `normal_form_item` (`scripts/a5_pencil_types_and_loci.py:203`) matches $a = (t, kt)$, $b = (\alpha t, (\alpha k)t)$ (pp. 23–24).
- **Extended Case-1 and Case-2 checks (`computed`, `probe_a.py`, `probe_k.py`)**: On 15 additional Case-1 $\alpha \in \mathbb{H}$ (including norm-1 $(3+4i)/5$, $\alpha = 0$, pure imaginary $i+j$ and $3i+4j$, generic $1-2i+3j-4k$), 15/15 passed: $J_k$ preserves $\ker L_y$, squares to $-I$, commutes with all 31 compressions, and commutant/closure are `(4, 10)` iff $\alpha \in \langle 1, k \rangle$, else `(2, 15)`. In Case 2 ($\alpha^2 + 1 = 0$: $\alpha = k \in N^-$, $\alpha = i \in B_9$, $\alpha = (3i+4j)/5 \in B_9$), $J_k$ fails to preserve $\ker L_y$ (`pres=False`) and commutant drops to 1. On all of $\mathbb{R}^{32}$, $J_k$ commutes with only $L_{e_3}$ and anticommutes with none (`probe_k.py`), so commutation with the other 30 compressions is a genuine kernel-projection phenomenon.

### 5. Claim 2 (W8 type census, Statement 20, `A5-677`) — **HOLDS ON CENSUS AND NON-CENSUS `dim A = 0` POINTS** (`computed`)

- **Route agreement (`computed`, `probe_g.py`)**: `a5_pencil_certificates.structure_item` (`bounds`) and `a5_nullity_transitions.structure_item` (`sympy`) agree on H `(4, 10)`, R `(1, 28)`, and C `(2, 15)`.
- **Outside-census stress test (`computed`, `probe_k.py`)**: Across all 100 nullity-8 lines `VB + 2w` through VB, 64 lie in `W8` (36 in `Iso`). All 64 have `nul_p = nul_q = 0` (neither half is a sedenion zero divisor, disjoint from the census), `dim A = 0`, and matched bounds `commutant = [1, 1]`, `closure = [28, 28]` (type R). Zero counterexamples found.

### 6. Claim 1 (Full Pfaffians at VB, N-, N+, Statement 19, `A5-676`) — **HOLDS** (`computed`)

- Independently recomputed (`probe_k.py`, 1.5 s): VB degree 6, 50 terms, content `-64`, `[[6, 1]]`; N- degree 8, 12,579 terms, content `-64`, `[[8, 1]]`; N+ degree 8, 12,579 terms, content `64`, `[[8, 1]]`. `self_test()` passed 5/5 controls (`probe_a.py`).

## Conjectures, falsifiers, and cheapest tests

1. **All-order Schur pencil closure at `e_1 + e_10` (`hypothesis`, route to A5-660)**: Whenever $F_1 = \dots = F_{m-1} = 0$, the leading Schur term $F_m$ lies in the 7-dim pencil for every $m \ge 1$ because the exact Schur complement satisfies $S(s) = U(s)^T P(s) U(s)$ with $P(s)$ in the pencil and $U(s) = I + O(s)$ (explaining why standalone $m_4 \notin \mathfrak{sp}(2)$ when $F_2 \neq 0$, yet $F_4, F_5, F_6$ all return to the pencil once lower orders cancel).
   - *Falsifier*: An arc with $F_1 = \dots = F_{m-1} = 0$ whose $F_m$ leaves the 7-dim pencil, or a point $y_0 + \Delta y \in ZD_4(A_5)$ near $e_1 + e_{10}$ whose exact Schur complement $S(\Delta y)$ has kernel off the 2-sphere.
   - *Cheapest test*: Check whether $m_4(w) \in \text{pencil}$ on the quadratic cone $\{w \in Z : F_2(w) = 0\}$, and evaluate $\ker S(\Delta y)$ on 20 small-perturbation nullity-4 points near $e_1 + e_{10}$.
2. **Uniform $J_k$ commutation across Case 1 of BDI Theorem 14.6 (`hypothesis`, route to `dim A > 0` half of A5-667)**: For every $\alpha \in \mathbb{H}$ with $\alpha^2 + 1 \neq 0$, $J_k$ preserves $\ker L_{y(\alpha)}$, squares to $-I$, and commutes with all 31 compressions; the commutant is $\mathbb{H}$ iff $\alpha \in \langle 1, k \rangle$ and $\mathbb{C} = \langle I, J_k \rangle$ otherwise.
   - *Falsifier*: A Case-1 $\alpha \notin \langle 1, k \rangle$ with $K^T(L_w J_k - J_k L_w)K \neq 0$ for some $w$ or commutant dimension $> 2$.
   - *Cheapest test*: Solve the $4 \times 4$ quaternionic system (S2) (`math_0511691.pdf`, p. 24) in closed form over $\mathbb{Q}(a_0, a_1, a_2, a_3)$ (avoiding naive $16 \times 16$ SymPy `nullspace()`) and check $K(\alpha)^T(L_w J_k - J_k L_w)K(\alpha) = 0$ identically for all 31 units $w$.
3. **Graph-kernel proof route for `dim A = 0 => type R` on $W_8$ (`hypothesis`, route to `dim A = 0` half of A5-667)**: For $y = (p, q) \in W_8$ with $\dim(\ker L_p \cap \ker L_q) = 0$, $\ker L_y$ meets both $A_4 \times 0$ and $0 \times A_4$ trivially, so $\ker L_y = \{(x, T x) : x \in V\}$ is the graph of an isomorphism $T: V \to W$ between 8-dim subspaces of $A_4$ with $T^2 = -I$ (from $\mathbb{C}_5 = \langle 1, e_{16} \rangle$-invariance, BDI Lemma 9.6), and the absence of any $A_4$-half-invariant subspace forces the 7-dim pencil to have trivial commutant $\mathbb{R}$ and closure $\mathfrak{so}(8)$.
   - *Falsifier*: A real $W_8$ point $(p, q)$ with $\dim(\ker L_p \cap \ker L_q) = 0$ and commutant dimension $\ge 2$.
   - *Cheapest test*: Sample $W_8(\mathbb{R})$ points with mixed half-nullities ($\operatorname{nul} p = 4, \operatorname{nul} q = 0$) and generic ($\operatorname{nul} p = \operatorname{nul} q = 0$) from `strata_regularity.py`, check commutant dimension 1, and test whether the compressions of $L_{e_{16}}$ and $L_{e_8}$ already obstruct any $J \neq \pm I$ commuting with the pencil when $\ker L_y$ is a graph.
