### 1. Defects in Code, Claims, and Records (Ranked by Consequence)

#### Defect 1: Premature loop termination in Singular reduction check via dynamic `size(I)`
- **Location:** [arcs/gen_family.py:141-143](../../../../docs/evidence/a5-exceptional-fibers/arcs/gen_family.py#L141-L143)
- **Classification:** [computed] / [proved]
- **Mechanism:** In Singular, `size(I)` returns the count of non-zero generators. When elements in the loop `for (jj=1;jj<=size(P2F);jj++) { P2F[jj]=reduce(P2F[jj],rel); }` reduce to 0, `size(P2F)` decreases dynamically. Once `jj > size(I)`, the loop terminates prematurely, leaving generators in the second half of the ideal unreduced.
- **Demonstrated Break:**
  ```sh
  Singular -q -c 'ring r=0,(x,y),dp; ideal I=x,x,x,x,x; int jj; for (jj=1; jj<=size(I); jj++) { I[jj]=0; } print(I);' </dev/null
  ```
  **Output:**
  ```text
  0, 0, 0, x, x
  ```
  Generators 4 and 5 were never zeroed out. While [relation_ideal_orders.py:35](../../../../docs/evidence/a5-exceptional-fibers/arcs/relation_ideal_orders.py#L35) recognized this (`"every loop over an ideal runs to ncols, since Singular's size counts only the nonzero generators"`), [gen_family.py:141-143](../../../../docs/evidence/a5-exceptional-fibers/arcs/gen_family.py#L141-L143) retains `size(P2F)`, `size(P1F)`, and `size(K2F)`. If leading generators vanish, trailing non-vanishing generators escape reduction.

#### Defect 2: Reducedness certificate failure mode on non-Cohen-Macaulay rings
- **Location:** [third-prime/quadric_rings.py:12-20, 151-166](../../../../docs/evidence/a5-exceptional-fibers/third-prime/quadric_rings.py#L12-L20)
- **Classification:** [computed] / [proved]
- **Mechanism:** A squarefree characteristic polynomial on an Artinian linear section chart $l_a = 1$ does *not* detect non-reducedness when $k[y]/K_2$ is non-Cohen-Macaulay. On $X^- \to N^-$ (3 nilpotent linear forms) and $E_8\text{-bar} \to N^-$ (5 nilpotent linear forms), the section chart reports `chart_reduced: True` with squarefree charpolys for all bases 7–10 ([quadric-rings-p32057.json:44, 461](../../../../docs/evidence/a5-exceptional-fibers/third-prime/quadric-rings-p32057.json#L44)). The codimension-4 section in $\mathbb{P}^{20}$ misses the dimension-4 non-reduced components $P_2$ and $A$ ($\dim V + \dim L - N = 3 + 16 - 20 = -1 < 0$).
- **Demonstrated Output:**
  ```sh
  python3 -c 'import json; d = json.load(open("docs/evidence/a5-exceptional-fibers/third-prime/quadric-rings-p32057.json")); print(d["cells"][0]["fiber"], "CM:", d["cells"][0]["cohen_macaulay"], "chart_reduced:", d["cells"][0]["chart_reduced"], "nilpotents:", d["cells"][0]["nilpotent_linear_forms"])'
  ```
  **Output:** `X- -> N- CM: False chart_reduced: True nilpotents: 3`
  The verdict is only saved from falsely asserting `reduced: True` because line 161 gates the chart verdict behind `cm_row["cohen_macaulay"]`. Consequently, [calibration-p32009.json](../../../../docs/evidence/a5-exceptional-fibers/third-prime/calibration-p32009.json) yields `chart_reduced: True` across all five cells (including both non-reduced cells), failing to exercise chart failure on non-reduced rings.

#### Defect 3: Gate replay pollutes repository with unmanaged artifact writes
- **Location:** [arcs/relation_ideal_orders.py:124-129](../../../../docs/evidence/a5-exceptional-fibers/arcs/relation_ideal_orders.py#L124-L129)
- **Classification:** [computed]
- **Mechanism:** In gate `core-a5-header-relation-ideal-orders`, `ci/replay_check.py` redirects JSON output `{out}` to a temporary directory, but `relation_ideal_orders.py:124-129` hardcodes writing `.sing` scripts and `.log` outputs directly to `HERE / "relation-ideal-orders" / target_name`. Running the gate mutates the repository tree, violating gate read-only hermeticity.

#### Defect 4: Asymmetric nilradical search leaves Iso and W8 unprobed for nilpotents
- **Location:** [third-prime/quadric_rings.py:200-202](../../../../docs/evidence/a5-exceptional-fibers/third-prime/quadric_rings.py#L200-L202)
- **Classification:** [computed]
- **Mechanism:** Line 200 hardcodes `nil = {"xm-nm", "xp-np", "e8-vb", "e8-nm"}`. For `iso-nm` and `w8-nm`, `NIL` (which computes `radical(sK)` and linear nilpotents) is skipped entirely. Their reducedness is inferred purely from `cohen_macaulay: True` and `chart_reduced: True`.

#### Defect 5: Mutation gap in test suite
- **Location:** [tests/test_a5_owed_falsifier_programs.py:86-95](../../../../tests/test_a5_owed_falsifier_programs.py#L86-L95)
- **Classification:** [computed]
- **Mechanism:** `MUTATIONS` checks `("top", "plain", "P1NONVAN", 2)` but lacks `("scroll", "plain", "P2NONVAN", 2)`. Moreover, `pytest` executes only against synthesized in-memory dicts; none of the committed JSON evidence records are validated by pytest.

---

### 2. Status Audit of Changed Ledger Rows

| Row | Claim Summary | Stated Status | Audit Verdict | Justification & Governing Principle |
|---|---|---|---|---|
| **A5-002** | Opposite-sign fiber linear because $X^+$ is smooth sheet of $E_8\text{-bar} \cap \{\mu'=0\}$ along $N^-$ and mult-2 along $N^+$ | `proved` | **EARNED** [proved] | `asymmetry.py` exact computation over $\mathbb{Q}$ confirms sheet multiplicities $1+2=3=\mathrm{mult}(E_8\text{-bar})$ and differentials. Replayed on build host byte-for-byte outside timing. |
| **A5-003** | Kernel-map base locus near target is $B_9$ slice with residual $VB$ curve or origin | `proved` | **EARNED** [proved] | `base_locus.py` exact computation across all 8 incidences in $F_{32009}$, $F_{32029}$, and $\mathbb{Q}(i)$ demonstrates the ideal factorization $I = t_2 I'$. Replay byte-identical. |
| **A5-009** | $\mathcal{F}(I) = k[y]/K_2$ for $E_8\text{-bar} \to N^\pm$ in all degrees | `proved` | **EARNED** [proved] | Conditional on $K_2 \subseteq L$. Settled in degrees $d \ge 8$ by A5-559. $K_2 \subseteq L$ holds at 32029 (receipts) and 32009 ($N^-$ receipt, $N^+$ by sign transport A5-013/A5-024). |
| **A5-024** | $E_8\text{-bar} \to N^\pm$ generators map under $(t_8,t_9) \to (-t_8,-t_9)$ as signed bijection over $\mathbb{Q}(i)$ | `proved` | **EARNED** [proved] | `npm_map_qi.py` proves generator-by-generator sign mapping $\sigma(J_k^+) = \pm J_k^-$, $\sigma(G_k^+) = \pm G_k^-$ as an exact bijection over $\mathbb{Q}(i)$, reducing to tracked headers. |
| **A5-032** | Diagonal Klein four-group sign symmetry on all pairs, no larger termwise diagonal group | `proved` | **EARNED** [proved] | Smith invariants $(1,\dots,1,2,2)$ on 27 headers prove torus order 4; exhaustive enumeration of diagonal sign vectors via `signed_perm_sweep.py` confirms no other symmetries exist. |
| **A5-548** | Quadric rings of the six fibers are Cohen-Macaulay iff reduced | `survives` | **EARNED** [hypothesis] | Tested at three split primes (32009, 32029, 32057). Status `survives` is exact: finite primes cannot decide characteristic 0 or general primes. |
| **A5-559** | Header slices $E_8\text{-bar} \to N^\pm$: relation ideal $L = K_2$ in every degree, given $K_2 \subseteq L$ | `proved` | **EARNED** [proved] | Monomial arcs reach $P_1, P_2$, and embedded $A$. Nilpotent linear form orders $\nu+1 = 5 < \nu+e_{min} = 6$ force any relation in $L/K_2$ to lie in $A$; torsion-freeness and rank 1 of $R/K_2$ over $S/A$ force $L = K_2$. |
| **A5-560** | Quadric rings at $p=32057$: $X^\pm, E_8\text{-bar} \to N^-$ non-CM/non-reduced; $E_8\text{-bar} \to VB, \mathrm{Iso}, W_8$ CM/reduced | `proved` | **EARNED** [computed] | Certified by `quadric_rings.py` at $p=32057$. CM checked via system of parameters length; non-reduced certified by nilpotents; reducedness of CM rings certified by section chart charpoly. |

---

### 3. Conjectures Suggested by Evidence

#### Conjecture 1: Outer doubling automorphism lifts to full fiber cone isomorphism in all degrees
- **Statement:** [hypothesis] The pair flip $\sigma: (t_8, t_9) \mapsto (-t_8, -t_9)$ for $E_8\text{-bar} \to N^\pm$ is the restriction of the outer doubling automorphism $\phi(a,b)=(a,-b)$ of $A_5$ to $V(J)$. Consequently, over $\mathbb{Q}(i)$, the fiber cones $\mathcal{F}(I^+)$ and $\mathcal{F}(I^-)$ are isomorphic as graded $k$-algebras via $y_k \mapsto c_k y_k$ ($c_k \in \{\pm 1\}$) in *every* degree $d \ge 1$.
- **Falsifier:** A degree-$d$ relation $F(y) \in L_d(N^-)$ such that $F(c_1 y_1, \dots, c_{21} y_{21}) \notin L_d(N^+)$.
- **Cheapest Test:** Check that the 231 degree-2 normal-form relations and degree-3 syzygy generators of $L(N^-)$ map under $y \mapsto c \cdot y$ directly to $L(N^+)$ over $\mathbb{Q}(i)$ ($< 5\text{ s}$, Python).

#### Conjecture 2: Nilradical defect module is Cohen-Macaulay over its support
- **Statement:** [hypothesis] For any non-Cohen-Macaulay exceptional fiber cone $k[y]/K_2$, the nilradical module $M = R/K_2$ is a maximal Cohen-Macaulay module over the coordinate ring of its embedded support $S/A$ (i.e., $\mathrm{depth}_{S/A}(M) = \dim(S/A) = 4$).
- **Falsifier:** $\mathrm{Ext}^i_{S/A}(k, M) \neq 0$ for some $i < 4$.
- **Cheapest Test:** Compute the projective dimension / depth of $R/K_2$ over $S/A$ via Singular on the existing $p=32009$ or $p=32057$ relation files ($\approx 15\text{ s}$, $< 300\text{ MB}$).

#### Conjecture 3: General linear sections miss codimension $\ge 2$ primary components
- **Statement:** [hypothesis] For any standard graded algebra $A = k[y]/K_2$ whose top-dimensional primary component $P_1$ is reduced and whose non-reduced primary components $Q_j$ have $\dim(S/Q_j) < \dim A$, a general linear section chart $A / (l_1, \dots, l_{a-1}, l_a - 1)$ is identically reduced with a squarefree multiplication-matrix characteristic polynomial.
- **Falsifier:** An Artinian linear section of $k[y]/K_2$ for $E_8\text{-bar} \to N^-$ that contains a non-zero nilpotent.
- **Cheapest Test:** Check dimension intersection theorem in $\mathbb{P}^{20}$: $V(A)$ has projective dimension 3, while $V(l_1, \dots, l_4)$ has projective dimension 16; $3 + 16 - 20 = -1 < 0$, forcing $V(A) \cap V(l_1, \dots, l_4) = \emptyset$ identically.

---

### 4. Remaining Work and Concrete Cost Estimates

#### A5-548: Fourth Prime ($p = 32069$, root $r = 4215$)
- **Required Steps:**
  1. `fiber_inputs.py emit --prime 32069 --root 4215` for 7 slugs (5 s, 50 MB).
  2. `fiber_cone_driver.py --degree 2` on 6 cells:
     - `xm-nm`, `xp-np`: 60 s and 13 s ($< 200\text{ MB}$).
     - `e8-vb`, `iso-nm`: 8 s and 14 s ($< 200\text{ MB}$).
     - `e8-nm`: 148 quadrics, ~2 h wall clock, 1.4 GB peak resident set.
     - `w8-nm`: 144 quadrics, ~1 h 52 min wall clock, 2.0 GB peak resident set.
  3. `quadric_rings.py` (CM + reducedness + defect probes): 45 s, 450 MB peak memory.
- **Total Cost:** ~4.0 hours serial (or ~2.0 hours with 2 parallel workers), peak memory **2.0 GB** (bounded by `w8-nm` normal-form stage; evidence: [third-prime/README.md:28-45](../../../../docs/evidence/a5-exceptional-fibers/third-prime/README.md)).

#### A5-548: Characteristic 0 over $\mathbb{Q}(i)$
- **Required Steps:** Run `quadric_rings.py` over $\mathbb{Q}(i)$ directly on the certified weight-slice relation files from A5-474 ([weight-slice-relation-membership-result.json](../../../../docs/evidence/a5-kernel-attachments/weight-slice-relation-membership-result.json)).
- **Cost & Memory:**
  - `e8-vb` (10 vars), `iso` (17 vars), `xm` (15 vars): 10–45 s each, $< 400\text{ MB}$.
  - `w8` (24 vars, 144 quadrics, degree 50): Artinian reduction over $\mathbb{Q}(i)$ incurs coefficient swelling in Singular: ~8–12 min, peak memory **2.5 GB**.
- **Evidence:** `weight_slice_relation_membership.py` took 100 s for 10 cells over $\mathbb{Q}(i)$; `e8_relation_ideal_orders.py` ran in 70 s per basepoint.

#### A5-559: Characteristic 0 on the Header Slices
- **Required Steps:**
  1. Prove $K_2 \subseteq L$ on the 9-variable affine header slice over $\mathbb{Q}(i)$ (unresolved in row A5-009 / `nullity8-fiber-import-result.json`). Computing 231 degree-2 normal forms modulo $J$ over $\mathbb{Q}(i)$ without weight-truncation requires rational arithmetic over 9 variables: estimated **12–18 hours**, peak memory **8–14 GB**.
  2. Prove $L = K_2$ via monomial arcs over $\mathbb{Q}(i)$: Order bounds ($\nu = 4, e_{min} = 2$) and Jacobian rank 4 hold over $\mathbb{Q}$. Primary decomposition component verification ($P_1 \cap P_2 \cap Q_A = K_2$) over $\mathbb{Q}(i)$: **15–30 minutes**, peak memory **3.5 GB**.
- **Alternative (Optimal Path):** Settle the premise of A5-423 (birational passage between the torus weight slice and header slice), inheriting the exact characteristic-0 proof from A5-457 without full rational elimination on the 9-variable germ.
