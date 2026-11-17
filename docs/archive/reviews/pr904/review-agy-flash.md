# Review of PR 904: Orbit Normal Forms of the Nullity-4 Strata

### Executive Verdict
**Approval blocked on one type-check gate failure (`pr.yml` / `ci/pr_checks.sh types`).** The mathematical foundations, algebraic reductions, and geometric arguments in A5-530 through A5-536 are sound, elegant, and verified. The open hypotheses (A5-537–A5-540) and superseded row dispositions (A5-433, A5-443–A5-445) are properly tracked.

---

### 1. Defects (Ranked by Consequence)

1. **[Defect / Blocking Gate Failure] Mypy typing failure in test suite** [measured]
   - **Location:** `tests/test_a5_nullity4_orbit_normal_forms.py:97`
   - **Command:** `sh ci/pr_checks.sh types`
   - **Output:**
     ```text
     ../tests/test_a5_nullity4_orbit_normal_forms.py:97: error: Unsupported operand types for * ("list[int]" and "object")  [operator]
     Found 1 error in 1 file (checked 1109 source files)
     Command exited with code 1.
     ```
   - **Mechanism:** In `forms.CERTIFICATE`, heterogeneous values (`int`, `list[bool]`) cause `forms.CERTIFICATE["entries"]` to infer as `object`. In line 97, `[0] * forms.CERTIFICATE["entries"]` fails type checking.
   - **Remedy:** Cast to integer: `[0] * int(forms.CERTIFICATE["entries"])`.

2. **[Defect / Algebraic Parameter Degeneracy] Degeneracy of tangent-line parameterization at $\varepsilon = 0$** [proved]
   - **Location:** `docs/evidence/a5-kernel-bundles-residuals/nullity4_orbit_normal_forms.py:44-47`, `370-385`
   - **Mechanism:** In docstring item 4 and `tangent_line_restrictions()`, the pencil $\alpha p_0 + \lambda (\mu, \rho, 0)$ with $p_0 = (\rho, -\mu, \varepsilon)$ is evaluated modulo $\varepsilon^2 - (1 + v_1^2)$. When $1 + v_1^2 = 0$ ($\varepsilon = 0$), $\rho^2 + \mu^2 = 0$, so $(\mu, \rho, 0)$ becomes linearly dependent on $p_0$ ($(\mu, \rho, 0) = \pm i p_0$), collapsing the pencil to a single point.
   - **Audit:** The docstring prose correctly notes that for $\varepsilon = 0$ the tangent line to $n=0$ at $p_0$ is identically $r = \mu c_0 + \rho s = 0$ (which was excluded in Case B1 by the $-2\rho^2$ mixed monomial of $q$). However, `tangent_line_restrictions()` tests only the generic ring and lacks an explicit assert/test verifying that $p_0 \cdot (c_0, s, t) = \rho c_0 - \mu s = 0$ is collinear with $r = 0$ when $\varepsilon = 0$.

3. **[Defect / Identifier Collision] Symbol `W` shadows matrix identifier `W`** [code inspection]
   - **Location:** `docs/evidence/a5-kernel-bundles-residuals/nullity4_orbit_normal_forms.py:65`, `181`, `506`
   - **Mechanism:** Docstring item 7 defines the $8 \times 8$ matrix $W = M_C(h)\Omega$. In line 181, `W = sp.symbols("w")` is allocated as a scalar slack variable for Rabinowitsch's trick in `common_kernel_certificate()` (`1 - W * factor`). In code the matrix is named `product`. Harmless to execution, but misleading for code audits.

---

### 2. Verification of Claims Under Review

1. **A5-530 [proved]:** *Orbit normal form and decoupling.*
   - Transitivity of $G_2(\mathbb{C})$ on orthonormal pairs in $\mathbb{C}^7$ follows from the transitive action of $G_2$ on the quadric $Q_5 \subset \mathbb{C}^7$ (stabilizer $SL_3(\mathbb{C})$) and $SL_3(\mathbb{C})$ on unit vectors in $e_1^\perp \cong \mathbb{C}^3 \oplus (\mathbb{C}^3)^*$ with fixed pairing.
   - For $\Delta \neq 0$, $\operatorname{span}(u, v)$ is nondegenerate, admitting an orthonormal basis mapped to $(e_1, e_2)$. The 120-degree rotation $g$ in $(u_j, v_j)$ satisfies $M(g t) = g M(t) g^T$ (`rotation_by_120_degrees_is_an_automorphism`) and ensures $u \cdot u \neq 0$ because both rotations can vanish only if $u \cdot v = v \cdot v = 0$ ($\Delta = 0$). An $SO_2(\mathbb{C}) \subset SO_3(\mathbb{C}) = \operatorname{Aut}(\mathbb{H}_0) \subset G_2(\mathbb{C})$ rotation aligns $u$ along $e_1$, and scaling gives $u = e_1$, $v = v_1 e_1 + \rho e_2$ ($\rho \neq 0$).
   - Block decoupling and $\operatorname{Pf}(M_C(t)) = G(t)$ confirmed exact over $\mathbb{Q}$ (`fixed_and_complement_blocks_decouple`, `complement_pfaffian_is_plus_or_minus_g`, sign $= 1$).

2. **A5-531 [proved]:** *Kernel quartic and line-freeness on $V(Q) \setminus V(G)$.*
   - Every zero of $G$ on $K(z)$ is a higher zero divisor: $K(z) \subset V(Q)$, and rank 12 on $V(Q) \cap V(G)$ would give an abelian kernel $K(k) = K(z)$ (A5-479), contradicting the Heisenberg algebra on $K(z)$ (A5-487).
   - Binary form case analysis: On a line $L \subset \mathbb{P}^2$, $n(n + r^2) = -q^2$.
     - *Case A (coprime):* $n = \alpha A^2$, $n + r^2 = \beta B^2 \implies r^2 = \beta B^2 - \alpha A^2$, which factors into two linear forms; their product being a square forces $A \propto B$, refuting coprimality.
     - *Case B1 ($r|_L = 0$):* $q = \pm i n$. Parameterizing $r=0$ by $(c_0, s, t) = (\rho \tau, -\mu \tau, \theta)$ yields mixed term $-2\rho^2 \tau \theta$ in $q$, whereas $n$ has no $\tau \theta$ term. Excluded since $\rho \neq 0$.
     - *Case B2 ($r|_L \neq 0$):* $r \mid n \implies n|_L = c r^2$, forcing $L$ tangent to $n = 0$ at $p_0 \in \{r = 0\}$. If $\varepsilon \neq 0$, $q(p_0) = 2\rho^2(v_1 - \varepsilon) \alpha^2 \neq 0$ because $(v_1 - \varepsilon)(v_1 + \varepsilon) = -1$. If $\varepsilon = 0$, the tangent line is $r = 0$, excluded by Case B1.

3. **A5-532 [proved]:** *Common kernel $C(P) = \mathbb{C} z$, $\dim L = 2$, injective immersion.*
   - $P$ avoids $z \implies [p_1, p_2] = \omega(p_1, p_2) z \neq 0$. Because $M(p_1)p_2$ lies in the center $\mathbb{C} z'$ of $K(z')$ for all $z' \in C(P)$, $\mathbb{C} z' = \mathbb{C} z$, so $C(P) = \mathbb{C} z$.
   - **Tangent space containment:** $Q \equiv 0$ on $C(P) = \mathbb{C} z \implies C(P) \subset T_z V(Q) = \{d : z \cdot d = 0\}$. Thus $L = L_z \times L_w \subset T_z V(Q) \times T_w V(\bar{Q})$.
   - **Constant-rank immersion:** In a constant-rank family $A(t) P(t) = 0$, differentiating yields $A(d) p + A p' = 0$. The derivative of $P(t) \in \operatorname{Gr}(2, 16)$ vanishes if and only if $p' \in P \implies A(d) P = 0$. Hence $\ker(d(\text{Gauss})) = L$. For real points $w = \bar{z}$, $(d, \bar{d}) \in L \iff d \in L_z = \mathbb{C} z$. Modulo projective scalings, the projective differential has trivial kernel, proving injective immersion.

4. **A5-533 [proved]:** *Singular scheme of quartic and semicontinuity.*
   - Base points of $x \times y$ correspond to roots of $\chi(\lambda) = \det(\lambda I - [x \to y]) = 0$ (`node_pencil_determinant`).
   - **Semicontinuity step:** For the closed subscheme $\operatorname{Sing}(G|_{K(z)}) \subset \mathbb{P}^2$, fiber length is upper semicontinuous under specialization. At the 12 fixtures, length modulo 32029 is 3 (A5-442). Since specialization cannot decrease length, $\operatorname{length}_{\operatorname{char} 0} \le 3$. Since $\chi$ has 3 roots off the discriminant, $\operatorname{length}_{\operatorname{char} 0} \ge 3$, establishing exact length 3 at generic points. The locus $\{\operatorname{length} > 3\}$ is therefore a proper closed subvariety.
   - **Irreducibility:** Since the quartic contains no line (A5-531), any reducible decomposition must be two smooth conics $Q_1 \cup Q_2$. By Bézout's theorem, $Q_1 \cap Q_2$ has length 4, which is contained in $\operatorname{Sing}(Q_1 Q_2)$. A quartic of singular length 3 cannot decompose into two conics and is therefore irreducible.

5. **A5-534 [proved]:** *Higher zero divisors on $V(G) \setminus V(Q)$ equal $l_z$.*
   - $SL_2$ fixes $z$ and acts transitively on $P(l_z) \cong \mathbb{P}^1$ and on $\mathbb{P}(K(z)) \setminus (\{[z]\} \cup P(l_z))$. Higher zero divisors form a closed, $SL_2$-invariant subvariety missing $z$ (rank 12), so they cannot meet the dense open orbit.
   - For $p \in l_z$, $Q(p) = G(p) = 0$. If $\operatorname{rank} M(p) = 12$, $K(p)$ would have trivial product (A5-479), forcing $K(p) = K(z)$ and contradicting the nonzero product on $K(z)$ (A5-492). Thus $\operatorname{rank} M(p) \le 10$, proving all of $l_z$ consists of higher zero divisors.

6. **A5-535 [proved]:** *Common kernel of off-polar planes and Gröbner certificates.*
   - Any plane $P \neq l_z$ avoiding $z$ is spanned by $z + p_1, p_2$. Writing $z' = a + b$ ($a \in \text{FIXED}, b \in \text{COMPLEMENT}$), $SL_2$-equivariance forces $M_C(a)|_{l_z} = 0$, $b \propto p_2$, and $M(z) a \propto \operatorname{grad} G(z)$.
   - Solvability requires $a = -c M(z) \operatorname{grad} G(z) / Q(z) + \tau z$. Killing $l_z = \operatorname{col}(\Omega)$ is equivalent to $W = M_C(h)\Omega = 0$.
   - Three Gröbner bases in $\mathbb{Q}[y, w, \mu, v_1, \rho]$ against $1 - y\rho$ and $1 - w \cdot \{v_1, \mu, \rho - \sigma\}$ equal $\langle 1 \rangle$ for both $\sigma = \pm 1$ (`common_kernel_certificate`). This isolates the sole zero to $(v_1, \mu, \rho) = (0, 0, \sigma)$, which has rank 10 and lies outside the nullity-4 stratum. Thus $W \neq 0$ on the stratum, proving $C(P) = \mathbb{C} z$ and dim $L > 2 \implies P = l_z$.

7. **A5-536 [proved]:** *Quaternion subalgebra implies $P = l_z$ and $\dim L \ge 6$.*
   - Compact $G_2$ commutes with complex conjugation and aligns the quaternion subalgebra into $\mathcal{O}'$ (FIXED). Then $K(z) \cap \bar{z}^\perp = l_z \subset \text{COMPLEMENT}$, so $P = l_z$ and $P' = \bar{l}_z \subset \text{COMPLEMENT}$.
   - For $a \in \text{FIXED} \cong \mathbb{C}^7$, $a \perp P'$ holds automatically. The intertwiner map $a \mapsto M_C(a)|_{l_z} \in \operatorname{Hom}_{SL_2}(\mathbb{C}^2, (\mathbb{C}^2)^4) \cong \mathbb{C}^4$ has kernel dimension at least $7 - 4 = 3$. Hence $\dim L_z \ge 3$, yielding $\dim L = 2 \dim L_z \ge 6$.

8. **A5-537 to A5-540 [hypotheses]:** *Open status verified.*
   - All four rows are designated `status: open` and `primes: 32029`. Their bases cite exact fixture counts and modular tallies without overclaiming proof in characteristic 0.

9. **Dispositions [superseded]:**
   - **A5-433:** Part (a) $\to$ A5-536 (proved $\dim L \ge 6$), A5-539 (open); part (b) $\to$ A5-532 (proved); part (c) $\to$ A5-538 (open).
   - **A5-443:** No line $\to$ A5-531 (proved); $\dim L = 2 \to$ A5-532 (proved).
   - **A5-444:** Higher zero divisors $= l_z \to$ A5-534 (proved); fiber condition $\to$ A5-535 (proved), A5-538 (open); quaternion locus $\to$ A5-536 (proved), A5-539 (open).
   - **A5-445:** Proper closed subset $\to$ A5-533 (proved); no line $\to$ A5-531 (proved); discriminant scheme length and irreducibility $\to$ A5-540 (open).
   - No clause dropped; successor mapping is complete and rigorous.

---

### 3. Conjectures Suggested by Evidence

1. **[Conjecture / Invariant Polarization] Uniform rank on polar line via $SL_2$ transitivity** [proved]
   - *Statement:* At every nullity-4 point $z \in V(G) \setminus V(Q)$, $\operatorname{rank} M(p)$ is strictly constant for all nonzero $p \in l_z$.
   - *Mechanism:* $l_z$ is an irreducible $\mathbb{C}^2$-module under the stabilizer $SL_2 \subset G_2(\mathbb{C})$. $SL_2$ acts transitively on $\mathbb{P}(l_z) \cong \mathbb{P}^1$ and acts by algebra automorphisms preserving matrix rank.
   - *Falsifier:* Any point $z$ and pair $p_1, p_2 \in l_z \setminus \{0\}$ with $\operatorname{rank} M(p_1) \neq \operatorname{rank} M(p_2)$.
   - *Cheapest test:* Symbolic rank computation of $M(\alpha p_1 + \beta p_2)$ in Singular over $\mathbb{Q}(v_1, \rho, \alpha, \beta)$.

2. **[Conjecture / Subspace Splitting] Extra common-kernel dimensions when $\mu = 0$** [computed]
   - *Statement:* At normal form with $\mu = 0$, the jump of $\dim C(l_z)$ from 3 to 6 arises because $M_C(z)$ decouples into two $4 \times 4$ skew blocks of rank 2 on COMPLEMENT coordinates $(4, 7, 12, 15)$ and $(5, 6, 13, 14)$. The complementary nullvectors commute with $l_z$, contributing a 2-plane in COMPLEMENT to $C(l_z)$, while $\dim(C(l_z) \cap \text{FIXED})$ increases from 3 to 4.
   - *Falsifier:* A normal-form point with $\mu = 0$ whose $C(l_z)$ meets COMPLEMENT in dimension other than 2.
   - *Cheapest test:* Evaluated via `forms._common_kernel` on $\mu = 0$ normal-form points (confirmed: 4 in FIXED, 2 in COMPLEMENT, rank 4 joint span with $l_z$).

3. **[Conjecture / Absolute Irreducibility] Universal irreducibility of the kernel quartic** [computed]
   - *Statement:* The kernel quartic $4(n(n+r^2) + q^2)$ on $V(Q) \setminus V(G)$ is absolutely irreducible on the discriminant of $\chi$ as well, including at the triple root $v_1 = 0, 2\rho^2 + 1 = 0$ ($\operatorname{length} = 5$).
   - *Mechanism:* Since the quartic contains no lines anywhere (A5-531), reducible decomposition requires two smooth conics intersecting in 4 points. On the discriminant, roots of $\chi$ merge into cusps ($A_2$) or tacnodes rather than 4 transversal $A_1$ nodes.
   - *Cheapest test:* Factorization executed in Singular 4.4.1:
     - At all 5 sample points on the discriminant modulo 32029: irreducible (degree 4 factor, multiplicity 1).
     - At the triple root over $\mathbb{Q}(\rho)$ ($\minpoly = 2\rho^2 + 1$): `factorize(quartic)` yields an irreducible quartic with rational coefficients:
       $$c_0^4 - 2 c_0^3 s + 2 c_0^2 s^2 - 2 c_0 s^3 + s^4 - c_0^2 t^2 - 2 c_0 s t^2 + 3 s^2 t^2 + 2 t^4.$$
   - *Falsifier:* A point on $\operatorname{disc}(\chi)$ where Singular's `factorize()` returns degree-2 factors over $\overline{\mathbb{Q}}$.

---

### Summary Recommendation
Fix the typing defect at `tests/test_a5_nullity4_orbit_normal_forms.py:97`. Once `sh ci/pr_checks.sh types` is green, PR 904 meets all repository quality gates and mathematical criteria for merge.
