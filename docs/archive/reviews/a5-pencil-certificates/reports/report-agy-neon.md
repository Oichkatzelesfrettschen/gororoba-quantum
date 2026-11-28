I launched the 18-vs-30-unit invariance check and commutant-structure inspection on `the compute workstation`; waiting for the job to finish.
# Red-Team Report: `gororoba-quantum` PR 1045 (`a5-pencil-certificates`, head `e9e3c33f0`)

Environment note (`measured`): `the compute workstation` checkout `WORKTREE` sits at `b68c42da3` (one commit behind local `e9e3c33f0`, which added `determinant_item` and prior-art text); `scripts/a5_pencil_certificates.py --self-test` passed (`self-test passed: 7 controls`). No files were modified.

---

## Findings Ranked by Consequence

### 1. Claim 4 & Claim 5 (`A5-671`) — **FALLS IN PART** (unproved upper bound; prior art understated)

- **Unproved premise (`dim ker L_p <= 4`)** (`proved` by inspection): README.md:181-184 and ledger.tsv:649 (`A5-671`, marked `proved`) derive `dim(ker L_p n ker L_q) in {0, 2, 4}` from the basis anticommutation check (`L_(e_8)`-invariance) and Moreno's multiple-of-4 theorem. Moreno's theorem alone allows `dim ker L_p in {4, 8, 12}` in $A_4$; the script checks `nullity == 4` only on the 26,096 census points (a5_pencil_certificates.py:513-523), not all sedenion zero divisors. Closing the upper bound requires citing Biss–Dugger–Isaksen **Proposition 9.10** ($\dim\mathrm{Ann}(x) \le 2^n - 4n + 4 = 4$ for $n=4$, `math_0511691.pdf`, pp. 17, 22).
- **Prior art already proves the full statement** (`proved` by inspection of `math_0511691.pdf`): README.md:178-181 and `A5-671` cite only Proposition 5.3 and Lemma 6.4 of Biss–Dugger–Isaksen and frame the evenness of `ker L_p n ker L_q` as a corollary drawn here. In `math_0511691.pdf`:
  - **Lemma 9.5** (pp. 15–16) proves every zero divisor in $A_n$ is orthogonal to $C_n$ ($p_0 = p_8 = 0$ at $n=4$);
  - **Lemma 9.6** (p. 16) proves $\mathrm{Ann}(x)$ is a $C_n$-vector space;
  - **Lemma 9.9** (p. 17) states verbatim: *"Finally, $\mathrm{Ann}(a, b)$ and $\mathrm{Ann}(a) \cap \mathrm{Ann}(b)$ are both complex vector spaces (see Lemma 9.6), so their real dimensions are even."*
  The entire algebraic content of Claim 4 is contained in BDI (Prop. 5.3, Lemmas 6.4, 9.5, 9.6, 9.9, Prop. 9.10) for every $n \ge 4$; PR 1045 contributes only the basis-matrix check and the 26,096-point / 3,523,095-pair census.

### 2. Claim 3 & Claim 5 (`A5-657`) — **SURVIVES MATHEMATICALLY; 18-vs-30 SCOPE GAP IN `strata_item` / `A5-657`**

- **Scope gap in the PR** (`proved` by inspection): ledger.tsv:636 (`A5-657`, now `proved`) states *"restricted to the doubly pure coordinate units, the Pfaffian ... is a constant times |lead Q|^2 |lead G|^2."* In a5_pencil_certificates.py:340-390, `strata_item` proves the polynomial identity only on the **18** doubly pure units chosen by the greedy basis loop; `determinant_item` (a5_pencil_certificates.py:453-510) checks all **30** doubly pure units only at 60 integer points.
- **Decisive check upgrades 18 units to all 30 units** (`proved` via exact symbolic computation on `the compute workstation`):
  ```
  STRATA VB: rk_pure=8, rk_all=9, ker_dim=22, ord_q=1, ord_g=2, dq_nonzero=0, dg_nonzero=0
  STRATA N-: rk_pure=18, rk_all=19, ker_dim=12, ord_q=1, ord_g=3, dq_nonzero=0, dg_nonzero=0
  STRATA N+: rk_pure=18, rk_all=19, ker_dim=12, ord_q=1, ord_g=3, dq_nonzero=0, dg_nonzero=0
  ```
  At `VB`, `N-`, and `N+`, all 30 doubly pure compression forms lie in the span of the greedy doubly pure basis (`rk_pure = rk_all - 1`, so no omitted doubly pure unit carries an $e_{16}$ component), and every basis vector of $\ker(w \mapsto K^T L_w K)$ on $\mathbb{R}^{30}$ annihilates both $\mathrm{lead}\,Q$ and $\mathrm{lead}\,G$ identically (`dq_nonzero = dg_nonzero = 0`). Thus the 18-unit polynomial identity strictly implies the full 30-unit polynomial identity. Adding this linear-invariance check to `strata_item` and `validate` closes the scope gap in `A5-657`.
- **Definitions, normalization, and independence survive** (`proved`): `Q` and `G` in `strata_item` (a5_pencil_certificates.py:343-353) match docs/evidence/a5-zero-divisor-strata/README.md:34-37. For $K = K_2 A$ with $K_2^T K_2 = 2I$, $\det(K^T K) = 2^{\mathrm{size}}(\det A)^2$ and $\mathrm{Pf}(K^T L_w K) = (\det A)\,\mathrm{Pf}(K_2^T L_w K_2)$, so $c_2^2 = c^2 \cdot 2^{\mathrm{size}} / \det(K^T K)$ (a5_pencil_certificates.py:392,502) is exact. `determinant_item` shares no multiplication table, SymPy expansion, or Pfaffian code with `strata_item` (only `STRATA[name]`, `fmpz_mat`, and the hand-coded `Q`/`G` and normalization formulas).

### 3. Claim 5 (`validate` guard gaps) — **FALLS ON MINOR GUARDS**

- **Calibration guards** (a5_pencil_certificates.py:616-621, `proved` by inspection): `validate` omits `require(r_row["forms_skew"])` and `require(c_row["forms_skew"])` (required for `closure_upper` to be a valid upper bound), omits `require(r_row["commutant_lower"] == 1)` (`commutant_verified` alone would accept `elements = [0]`), and omits `require(c_row["commutant_trace_form_negative_definite"])` (without which `c_row` only rules out noncommutativity, not $\mathbb{R} \oplus \mathbb{R}$). In certificates.json:32, `commutant_trace_form_negative_definite` is vacuously `true` at type R because `kept` is empty (a5_pencil_certificates.py:287).
- **Determinant guards** (a5_pencil_certificates.py:641-644): `validate` omits checks on `len(result["determinant"]) == 2`, point labels `{"N-", "N+"}`, `row["points"] == 60`, and `row["zero_targets"] == 0`.
- `A5-670` (ledger.tsv:648) and `A5-667` (ledger.tsv:646, `survives`) match their `validate` guards and loop bounds.

### 4. Claim 1 (Tower $A_4 \dots A_8$) — **SURVIVES**

- All three bound directions in `structure_item` (a5_pencil_certificates.py:228-316) are valid (`proved`):
  - **(a) Commutant upper bound**: `residue` enforces $P$-integrality of `inverse` ($P = 32749$), and $\dim_{\mathbb{Q}} \mathrm{Comm}(\text{pencil}) \le \dim_{\mathbb{Q}} \mathrm{Comm}(G_1, G_2, G_3) \le \mathrm{nullity}_{\mathbb{F}_P}(\text{commutation\_system})$ because $\mathrm{rank}_{\mathbb{F}_P} \le \mathrm{rank}_{\mathbb{Q}}$.
  - **(b) Closure lower bound**: `Echelon.add` (a5_pencil_certificates.py:200-216) maintains an RREF basis mod $P$ of iterated brackets of $G_1, G_2, G_3 \in \mathrm{span}_{\mathbb{Z}}(\text{operators\_q}) \subset M_s(\mathbb{Z}_{(P)})$, with max `int64` product $\le 528 \cdot 32748^2 < 5.7 \times 10^{11} \ll 2^{63}-1$; $\dim_{\mathbb{F}_P}((V \cap \mathbb{Z}_{(P)}^N) \bmod P) \le \dim_{\mathbb{Q}} V$.
  - **(c) Closure upper bound**: `skew_system` (a5_pencil_certificates.py:181-190) and `commutation_system` (a5_pencil_certificates.py:175-178) encode $X^T G + G X = 0$ and $X M - M X = 0$ in row-major `vec(X)` exactly; `verified` (a5_pencil_certificates.py:267) checks every reconstructed commutant element over $\mathbb{Q}$ against all pencil basis operators. Since $m^* = G^{-1} m^T G = -m$, $\mathrm{Comm}_{\mathbb{R}}$ is a $*$-algebra, hence semisimple; dimension 4, noncommutativity, and positive-definite $-\mathrm{tr}(ab)$ on the 3-dim traceless subspace uniquely select $\mathbb{H}$ over $M_2(\mathbb{R})$.
- Minor note: `table_mismatches` (a5_pencil_certificates.py:119) checks only a 16-row stride of `p` when `dimension > 16`.

### 5. Claim 2 (Calibration points R and C) — **SURVIVES (AND TYPE C CAN BE TIGHTENED)**

- The bounds (`1`, `28` at type R; `2`, `15..16` at type C) mean exactly what README.md:161-163 states (`proved`).
- **Tightening mechanism** (`computed` on `the compute workstation`): at `C e1+e10+2(e20+e31)`, the traceless commutant element $J$ ($J^2 = -I$, $G$-skew) satisfies `tr(J * m) = [0, 0, 0, 0, 0, 0, 0]` on all 7 pencil basis elements. Since $\mathrm{tr}(J[A, B]) = \mathrm{tr}([J, A]B) = 0$ on $\mathfrak{u}(4)$, adding the single linear equation $\mathrm{tr}(J X) = 0$ to `closure_upper` whenever $\mathrm{tr}(J m) = 0$ for all $m$ closes the type-C upper bound from `16` to `15`.

---

## Conjectures, Proof Route for the Three-Type Rule (`A5-667`), and Falsifiers

### Mechanism for `A5-667` (`dim A = 0, 2, 4 <-> types R, C, H`)

The common-kernel complex structure $L_{e_8}$ of Claim 4 does **not** commute with the $W_8$ compression pencil; it only restricts $\dim A \in \{0, 2, 4\}$. Instead, the commutant complex structure for $\dim A \ge 2$ comes from **Biss–Dugger–Isaksen Theorem 14.6** (`math_0511691.pdf`, pp. 23–25):

1. Every $W_8$ point $y = (p, q)$ with $A = \ker L_p \cap \ker L_q \ne 0$ is, up to $G_2 = \mathrm{Aut}(O)$ and scaling, of the form $p = (t, kt)$, $q = (\alpha t, (\alpha k)t)$ with $H = \langle 1, i, j, k \rangle \subset O$, $k = a_1 a_2 / |a_1 a_2|$, $t \in H^\perp$ unit, and $\alpha \in H$ with $\alpha^2 + 1 \ne 0$ (BDI Case 1).
2. With $\Omega = H \times H \subset A_4$, $y \in \Omega^\perp \times \Omega^\perp$, so $\ker L_y$ splits orthogonally as $(\ker L_y \cap (\Omega \times \Omega)) \oplus (\ker L_y \cap (\Omega^\perp \times \Omega^\perp))$ (4 + 4 dimensions).
3. Define $J_k = \mathrm{diag}(+L_k \text{ on } \Omega \times \Omega,\; -L_k \text{ on } \Omega^\perp \times \Omega^\perp)$ (componentwise on the four octonion slots). Tested on `the compute workstation` across 6 points of the BDI Theorem 14.6 family (`computed`):
   ```
   BDI alpha=2:       dimA=4, ker=8, pencil=7, comm=(4,4), clos=(10,10), preserves_K=True, J3^2=-I_on_K=True, commutes_all_31_forms=True
   BDI alpha=2k:      dimA=4, ker=8, pencil=7, comm=(4,4), clos=(10,10), preserves_K=True, J3^2=-I_on_K=True, commutes_all_31_forms=True
   BDI alpha=2i:      dimA=2, ker=8, pencil=7, comm=(2,2), clos=(15,16), preserves_K=True, J3^2=-I_on_K=True, commutes_all_31_forms=True
   BDI alpha=1+i:     dimA=2, ker=8, pencil=7, comm=(2,2), clos=(15,16), preserves_K=True, J3^2=-I_on_K=True, commutes_all_31_forms=True
   BDI alpha=i+k:     dimA=2, ker=8, pencil=7, comm=(2,2), clos=(15,16), preserves_K=True, J3^2=-I_on_K=True, commutes_all_31_forms=True
   BDI alpha=1+i+j+k: dimA=2, ker=8, pencil=7, comm=(2,2), clos=(15,16), preserves_K=True, J3^2=-I_on_K=True, commutes_all_31_forms=True
   ```
   - $\alpha \in \langle 1, k \rangle \iff \dim A = 4$: $q \in C_4 p$, the full $SU(2) = \mathrm{Stab}_{G_2}(\langle 1, t, kt \rangle)$ commutes with the pencil, giving $\mathrm{Comm} = \mathbb{H}$ and $\mathfrak{sp}(2)$.
   - $\alpha \in H \setminus \langle 1, k \rangle \iff \dim A = 2$: $J_k$ commutes with all 31 compression forms and satisfies $\mathrm{tr}(J_k K^T L_w K) = 0$, giving $\mathbb{C} \subseteq \mathrm{Comm}$ and closure $\subseteq \mathfrak{su}(4)$.

### Open Conjectures with Falsifiers and Cheapest Tests

1. **Conjecture 1 (Symbolic proof of $\dim A \ge 2 \implies \mathbb{C} \subseteq \mathrm{Comm}$ and $\mathrm{closure} \subseteq \mathfrak{su}(4)$)** (`hypothesis`): For symbolic $\alpha = a_0 + a_1 i + a_2 j + a_3 k$ with $\alpha^2 + 1 \ne 0$, $J_k$ preserves $\ker L_y$, satisfies $K^T L_w J_k K + (J_k K)^T L_w K = 0$ and $\mathrm{tr}(J_k K^T L_w K) = 0$ for all $w \in 1..31$, and for $(a_1, a_2) \ne (0, 0)$ the commutant has dimension exactly 2.
   - *Falsifier*: a nonzero symbolic entry in $K^T L_w J_k K + (J_k K)^T L_w K$ or $\mathrm{tr}(J_k K^T L_w K)$ for any $w \in 1..31$, or a specialization $(a_1, a_2) \ne (0, 0)$ with $\dim \mathrm{Comm} > 2$.
   - *Cheapest test*: SymPy identity over $\mathbb{Q}(a_0, a_1, a_2, a_3)$ on the explicit 8-column Case 1 kernel basis from BDI Theorem 14.6 (< 5 s on `the compute workstation`).
2. **Conjecture 2 (Converse: $\dim A = 0 \implies \mathrm{Comm} = \mathbb{R}$ on $W_8$)** (`hypothesis`): Every $W_8$ point $(p, q)$ with $\dim A = 0$ has scalar commutant and closure $\mathfrak{so}(8)$, including the boundary case where $a_1 a_2 \parallel b_1 b_2$ yet $\dim A = 0$ (if nonempty in $W_8$).
   - *Falsifier*: a $W_8$ point with $\dim A = 0$ and $\dim \mathrm{Comm} > 1$ (most plausibly one with $a_1 a_2 \parallel b_1 b_2$).
   - *Cheapest test*: deterministic enumeration of pairs $(p, q)$ of sedenion zero divisors with $a_1 a_2 = b_1 b_2 = e_3$ and $\dim A = 0$ (checking nullity 8 and `commutant_upper`).
3. **Conjecture 3 (Tight type-C certificate via $\mathrm{tr}(J X) = 0$)** (`hypothesis`): Adding $\mathrm{tr}(J X) = 0$ for every traceless verified commutant element $J$ orthogonal to the pencil makes `closure_lower == closure_upper` across all three $W_8$ types (R, C, H).
   - *Falsifier*: a type-C point where `tr(J m) != 0` for some pencil element `m`, or where `closure_lower < 15`.
   - *Cheapest test*: run the augmented `closure_upper` on all 4 type-C points of the scan and the 4 BDI $\dim A = 2$ points above (< 2 s on `the compute workstation`).
