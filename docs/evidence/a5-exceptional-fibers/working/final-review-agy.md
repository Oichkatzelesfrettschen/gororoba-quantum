### 1. Attack on the Converged Arc-Family Plan

1. **Unnoticed Linear Forms in $\sqrt{K_2}$ and Nonreduced Structure (`X-`, `E8bar->N+`):**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L260-L265)`]` For `X-`, $h(K_2) = (15, 51, 122)$ while $h(\sqrt{K_2}) = (12, 45, 112, 225)$; for `E8bar->N+`, $h(K_2) = (21, 83)$ while $h(\sqrt{K_2}) = (16, 69, 195, 440)$.
   - `[Inferred]` Neither Codex consult noticed the degree-1 drop: $\sqrt{K_2}$ contains **3 independent linear forms** for `X-` ($15 - 12$) and **5 independent linear forms** for `E8bar->N+` ($21 - 16$). Thus $V(K_2)_{\text{red}}$ sits in a proper linear subspace ($\mathbf{P}^{11} \subset \mathbf{P}^{14}$ for `X-`; $\mathbf{P}^{15} \subset \mathbf{P}^{20}$ for `E8bar->N+`), while 3 (resp. 5) target directions in $F(I)_1$ are **purely nilpotent** mod $\sqrt{K_F}$.
   - `[Inferred]` Any reduced arc $x(s,u)$ over a reduced parameter ring produces limits $[F(u)] \in V(\sqrt{K_F})$ that vanish on those linear forms. Arc families are therefore **blind** to the nilpotent thickening of $F(I)$, which carries higher-order kernel-bundle attaching data `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L57-L74)`]`.

2. **The Truncated-Jet Fallacy vs. Symbolic Normalization Bottleneck:**
   - `[Inferred]` Finding an exact polynomial/rational family $t(s,u)$ with $J(t(s,u)) = 0$ identically requires $Y = V(J)$ to be explicitly unirational around $0$. Symbolic curve normalization `normal(C)` `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L737-L743)`]` over a function field $\mathbf{F}_p(u_1,u_2,u_3)$ computes integral closures via multi-variable Groebner bases and hits the same elimination frontier as saturation.
   - `[Inferred]` Conversely, solving $J(t(s,u)) \equiv 0 \pmod{s^{\nu+1}}$ by power-series truncation **without** an invertibility certificate on the Jacobian of the strict transform $\tilde{J}$ produces spurious tangent vectors whenever the jet lies in the singular locus of the tangent cone $C_0(Y)$, certifying directions outside $\operatorname{Proj} F(I)$.

3. **Exceptional Components Hidden in the Base Locus of $\operatorname{in}_{\mathfrak{m}}(G)$ (`E8bar->VB`):**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L264-L267)`]` `E8bar->VB` has prime $J$ through $0$, yet $V(K_2)$ has **two** minimal primes of projective dimension 3 (degrees 3 and 4).
   - `[Inferred]` First-order linear arcs $t(s,u) = s v(u) + O(s^2)$ with generic $v(u) \in C_0(Y)$ have common valuation $\nu = d_G$ and sweep out only the **strict transform** of $\mathbf{P}(C_0(Y))$ (at most one component when $C_0(Y)$ is irreducible). The second 3-dimensional component arises from blowing up the **base locus** $B = \mathbf{P}(C_0(Y)) \cap V(\operatorname{in}_{\mathfrak{m}}(G))$, where the $s^{d_G}$ term vanishes identically and $\nu \ge d_G + 1$ depends on $s^2$ normal-bundle parameters. Generic curve sections or order-1 arcs miss base-locus components completely.

4. **Arithmetic vs. Geometric Primality, Inseparability, and Missed Embedded Components:**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L103-L104)`]` `minAssChar` over $\mathbf{F}_{32009}$ certifies arithmetic primality only.
   - `[Inferred]` If an arithmetic prime $P \subset \mathbf{F}_p[y]$ splits over $\overline{\mathbf{F}}_p$ (or $\mathbf{Q}(i)$) into Galois-conjugate geometric components $P_1 \cap \dots \cap P_k$, no rational family over $\mathbf{F}_p(u)$ can dominate $V(P)$ (since $\mathbf{A}^3_{\overline{\mathbf{F}}_p}$ is geometrically irreducible), while a branch defined over $\mathbf{F}_{p^k}$ hits only one $V(P_j)$ unless Galois equivariance of $J$ and $(G)$ is proved.
   - `[Inferred]` Over $\mathbf{F}_p$, Jacobian rank $d_\alpha$ proves dominance (since $\operatorname{tr.deg}_{\text{sep}} \le \operatorname{tr.deg} \le d_\alpha$), but rank $< d_\alpha$ is ambiguous between a lower-dimensional fiber component (i.e. $V(P_\alpha)$ is a strict upper bound, not in $\operatorname{Proj} F(I)$) and p-divisibility/inseparability of the parameterization. Moreover, minimal-prime coverage never detects embedded primes of $F(I)$.

---

### 2. Concrete Newton-Hensel Arc Construction (`E8bar->VB` and `X-`, < 8 GiB Host)

- **Coordinate partition & mechanism `[Inferred]`:** For `E8bar->VB` ($e=8$ slice vars `t1..t8`, $n=10$ generators `G[1..10]`, germ dim $d_Y=4$) or `X-` ($e=7$ slice vars, $n=15$ generators, $d_Y=4$), write $t_i = s \tilde{t}_i$. Let $\tilde{J}_r(\tilde{t}, s) = s^{-m_r} J_r(s \tilde{t})$ where $m_r = \operatorname{ord}_t(J_r)$. At a smooth $\mathbf{F}_{32009}$-point $\tilde{t}^{(0)}$ of $\mathbf{P}(C_0(Y)) = V(\tilde{J}(\tilde{t},0))$, fix chart $\tilde{t}_{q_0} = 1$, choose $c = e - 4$ dependent variables $\tilde{t}_{\text{dep}}$ ($c=4$ for `VB`, $c=3$ for `X-`) with invertible Jacobian $M(\tilde{t}^{(0)}) = \frac{\partial \tilde{J}}{\partial \tilde{t}_{\text{dep}}}(\tilde{t}^{(0)},0)$, and parametrize the 3 free tangent coordinates by $\tilde{t}_{\text{free}} = \tilde{t}^{(0)}_{\text{free}} + (u_1,u_2,u_3)$.
- **Solving $J=0$ along the arc `[Inferred]`:** Clear denominators via the polynomial adjugate $M^{\text{adj}}(u)$ in the **3-variable ring** $\mathbf{F}_{32009}[u_1,u_2,u_3]$ (zero Groebner bases). By Hensel's Lemma over $\mathbf{F}_p(u)[[s]]$, $\det M(u) \neq 0$ certifies a unique exact formal lift $t(s,u) \in \mathbf{F}_p(u)[[s]]$ with $J(t(s,u)) = 0$.
- **Expected degree in $s$ `[Inferred]`:**
  - *Strict-transform component* ($\operatorname{in}(G)(\tilde{t}^{(0)}) \neq 0$): $\nu = d_G = \min_i \operatorname{ord}_t G_i$ (degree **1** in $s$ if $J, G$ are homogeneous at initial order; degree **2** in $s$ if $\nu = 2$ and $d_G = 1$).
  - *Base-locus component* (`VB` second prime, where $\tilde{t}^{(0)} \in V(\operatorname{in}(G)) \cap \mathbf{P}(C_0(Y))$ of dim $3-b$): put $3-b$ parameters $u_1,\dots,u_{3-b}$ into $\tilde{t}^{(0)}$ at order $s^1$ and $b$ normal-bundle parameters $u_{4-b},\dots,u_3$ into $\tilde{t}^{(1)}_{\text{free}}$ at order $s^2$; then $\nu = d_G + 1$ (requires degree **2** in $s$).

```python
# Run on host (<1 GiB, <30 s): systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0 "$PYTHON" arc_cert.py
# Requires: sagemath 10.10 / python-flint 0.9.0 (installed per lab-map.md sec 2-3)
import flint
from sage.all import GF, Matrix, PolynomialRing, SR, vector


def certify_arc_component(
    p, t_names, J_polys, G_polys, P_prime_polys, pt0, free_idx, dep_idx, chart_idx, max_s_deg=2
):
  F = GF(p)
  R_u = PolynomialRing(F, ['u1', 'u2', 'u3'])
  u1, u2, u3 = R_u.gens()
  R_us = PolynomialRing(R_u, 's')
  s = R_us.gen()
  R_t = J_polys[0].parent()
  t_gens = R_t.gens()

  # 1. Blowup strict transform J_tilde(t_tilde, s) = J(s * t_tilde) / s^m_r
  m_ords = [min(f.exponents(), key=sum) for f in J_polys]
  m_vals = [sum(e) for e in m_ords]

  # First-order tangent family around smooth point pt0 on V(in(J))
  t_tilde = [R_u(pt0[i]) for i in range(len(t_names))]
  for k, idx in enumerate(free_idx):
    t_tilde[idx] = R_u(pt0[idx]) + [u1, u2, u3][k]
  t_tilde[chart_idx] = R_u(1)

  # 2. Compute c x c Jacobian M(u) at s=0 and solve Newton-Hensel to s^max_s_deg
  J_in = [
      sum(c * R_t({e: 1}) for e, c in f.dict().items() if sum(e) == m)
      for f, m in zip(J_polys, m_vals)
  ]
  M0 = Matrix(
      F, [[f.derivative(t_gens[j])(pt0) for j in dep_idx] for f in J_in[: len(dep_idx)]]
  )
  assert M0.det() != 0, 'Falsified: chosen basepoint is singular on tangent cone chart'
  M_inv = M0.inverse()  # Exact F_p inverse for jet lift around pt0; lift in R_u[[s]]/(s^(max_s_deg+1))

  arc = [R_us(x) * s for x in t_tilde]
  for deg_step in range(1, max_s_deg + 1):
    # Evaluate J(arc) mod s^(m_r + deg_step + 1) and invert M0 on highest residual
    res = [
        f(arc).truncate(m + deg_step + 1)[m + deg_step - 1]
        for f, m in zip(J_polys[: len(dep_idx)], m_vals)
    ]
    corr = -M_inv * vector(R_u, res)
    for j_pos, idx in enumerate(dep_idx):
      arc[idx] += R_us(corr[j_pos]) * (s**deg_step)

  # 3. Evaluate G(arc), extract common leading s-valuation nu and leading vector F_vec(u)
  G_eval = [g(arc).truncate(max_s_deg + 3) for g in G_polys]
  nu = min(g_s.valuation() for g_s in G_eval if g_s != 0)
  F_vec = [g_s[nu] for g_s in G_eval]
  assert any(f != 0 for f in F_vec), 'Falsified: leading G-vector vanishes identically'

  # 4. Exact containment in minimal prime P_alpha of sqrt(K2) and 3x3 Jacobian rank over F_p(u)
  assert all(
      p_rel(F_vec) == 0 for p_rel in P_prime_polys
  ), 'Falsified: image not contained in P_alpha'
  q = next(i for i, f in enumerate(F_vec) if f(0, 0, 0) != 0)
  fq0_inv = F(F_vec[q](0, 0, 0)) ** (-1)
  # Specialize d(F_i/F_q)/du_j at u=(0,0,0): full rank 3 over F_p certifies rank 3 over F_p(u)
  jac_rows = []
  for i, fi in enumerate(F_vec):
    if i == q:
      continue
    row = [
        int(
            F(
                fi.derivative(u)(0, 0, 0) * F_vec[q](0, 0, 0)
                - fi(0, 0, 0) * F_vec[q].derivative(u)(0, 0, 0)
            )
            * fq0_inv**2
        )
        for u in (u1, u2, u3)
    ]
    jac_rows.append(row)
  rk = flint.nmod_mat(jac_rows, p).rank()
  assert rk == 3, f'Falsified: Jacobian rank {rk} < 3'
  return {'status': 'support-certified-component', 'nu': int(nu), 'jacobian_rank': rk}
```

---

### 3. Missed Routes Across `lab-map.md` (and Plain Non-Applicability)

1. **Missed Route A — Quotienting by the Linear Radical Forms of $\sqrt{K_2}$ (`Singular` + `python-flint`, Host):**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L262-L263)`]` $\sqrt{K_2}$ has 3 linear forms for `X-` and 5 for `E8bar->N+`.
   - `[Inferred]` Eliminating those 3 (resp. 5) redundant target variables mod nilpotents shrinks the mixed Rees ring from $22 \to 19$ variables (`X-`) and $30 \to 25$ variables (`E8bar->N+`), directly attacking the variable-count bottleneck of `std(L)` and Method B.
2. **Missed Route B — Direct Kernel-Bundle Limit over $\mathbf{F}_p(u)[[s]]$ (`SageMath 10.10` / `pyadic` / `cd_core.py`, Host):**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L72-L74)`, ` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L1234-L1240)`]` `purpose.md` accepts direct limits of $\ker L_y$ as $y \to Z$.
   - `[Inferred]` Along any Hensel arc $t(s,u)$, compute the Hermite/Smith normal form over $\mathbf{F}_p(u)[[s]]/(s^3)$ of the $32 \times 32$ Cayley-Dickson left-multiplication matrix $L_{y(t(s,u))}$ from `cd_core.py`. Dividing each kernel basis vector by its $s$-valuation and setting $s=0$ yields the limiting 8-plane in $\operatorname{Gr}(8,32)$ in $O(32^3)$ arithmetic operations—delivering item 6's attaching map even when $F(I)$ is nonreduced.
3. **Missed Route C — Affine-Chart Rabinowitsch Elimination (`msolve 0.11.0` AVX-512, Host / Azure `FX4mds_v2`):**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L228-L234)`, ` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L1553-L1555)`]` Old `msolve` ran on the 20-variable homogenized `a`-graph (`a, t, y, h`).
   - `[Inferred]` Dehomogenizing on the pivot chart $y_q = 1$ with Rabinowitsch relation $1 - w G_q(t) = 0$ and $G_j(t) - y_j G_q(t) = 0$ eliminates $(w, t_1,\dots,t_e)$ via `-e 9 -l 2 -s 24 -u 2` in 18 affine variables (`VB`) without homogenizing $h$ or post-std saturation.
4. **Missed Route D — AWS EC2 On-Demand in `us-east-2` and `Rocq 9.3` Certificates:**
   - `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L415-L416)`, ` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L547-L549)`]` Both Codex consults ignored AWS EC2 (`$99.91` credit in `us-east-2`, On-Demand `RunInstances` allowed after `aws login` and case approval) and `Rocq 9.3` (`proofs/`), which can formally verify finite candidate/Jacobian identities.
5. **Plainly Inapplicable Capabilities:**
   - **Quantum backends (IBM Heron r2, Quantum Inspire, Open Quantum, Quandela, IQM, IonQ, BlueQubit, Quafu, Origin, qBraid, Azure Quantum):** `[Inferred]` Do **not** apply to exact commutative algebra over $\mathbf{F}_{32009}$.
   - **QRNG (ANU, Outshift, Quandela, QCi):** `[Inferred]` Do **not** apply to proving density; needed only if a new randomized seed literal is introduced (`ci/seed_provenance.py`). Use deterministic coordinates or existing `repro:<int>` seeds.
   - **Cloud/Local LLMs (Bedrock, Codex, OpenCode, Grok, Agy, Ollama):** `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L580)`]` Never mathematical evidence.
   - **Local RTX 4070 Ti (Aer/cuQuantum) & Kaggle GPU/TPU:** `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L362)`, ` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L542)`]` No GPU/TPU path for Singular/M2/msolve; Kaggle TPU v5e-8 is only a CPU/RAM host with a measured 6+ h queue penalty. Only a custom PyTorch/cuTensor mod-$p$ Macaulay block-Wiedemann solver could use the RTX 4070 Ti.

---

### 4. Stepwise Execution Plan

All host/Azure runs use `systemd-run --user --scope -p MemoryMax=... -p MemorySwapMax=0`, `MALLOC_ARENA_MAX=2`, no `RLIMIT_AS`, keeping host concurrent caps $\le 24\text{ GiB}$ `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L273-L274)`, ` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L368)`]`.

| Step | Target & Method | Resource, Memory Cap, Time Limit | Result Yielded | Falsifier (Stops Step) |
|---|---|---|---|---|
| **P1** | **Collect running `VB` $h_4$ diagnostic** `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L332)`]` | Host, 8 GiB cgroup, 1 h | Exact $h_4(\text{VB})$ vs quadratic bound 155 and quartic relations $K_4$ `[Inferred]` | $h_4 > 155$ (code/Nakayama error); if $h_4 < 155$, $F(I) \neq k[y]/K_2$ is proved `[Inferred]` |
| **P2** | **Newton-Hensel arc certificates for `E8bar->VB` (both dim-3 primes) & `X-` (dim-3 prime)** + geometric irreducibility check (`absFactorize` / Frobenii) `[Inferred]` | Host (`SageMath` + `python-flint`), 4 GiB cgroup, 30 min | `support-equal` receipt over $\mathbf{F}_{32009}$ for `VB` (deg 3 + 4 components) and `X-` (deg 12 reduced component) `[Inferred]` | $\det M_0 = 0$ on all charts, $P_\alpha(F(u)) \neq 0$, or Jacobian rank $< 3$ on both $s^1$ (strict transform) and $s^2$ (base locus) arcs `[Inferred]` |
| **P3** | **Direct kernel-plane limit $\lim_{s\to 0} \ker L_{y(t(s,u))}$ on `VB` and `X-` arcs** (`cd_core.py` over $\mathbf{F}_p(u)[[s]]/(s^3)$) `[Inferred]` | Host (`$PYTHON` + `SageMath`), 4 GiB cgroup, 30 min | Explicit 3-parameter limiting 8-plane family in $\operatorname{Gr}(8,32)$ (item-6 attaching datum `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L72-L74)`]`) | Generic nullity of $L_{y(t(s,u))}$ over $\mathbf{F}_p(u)((s))$ differs from 8 `[Inferred]` |
| **P4** | **Linear-radical quotient + syzygy/candidate check on `VB` and reduced `X-`** (quotient `X-` by the 3 linear forms in $\sqrt{K_2}$ `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L262)`]`) | Host (`M2` / `Singular`), 8 GiB cgroup, 1 h each | Reduced scheme presentation $L_{\text{red}}$ ($22 \to 19$ vars on `X-`) or Jacobian-dual syzygy structure `[Inferred]` | `std` exceeds 8 GiB / 1 h or $L : g \neq L$ `[Inferred]` |
| **P5** | **Projective-chart radical + `minAssChar` of $K_2$ for `E8bar->N-`, `Iso`, `W8->N-`** `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L107)`, ` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L265)`]` | Host, 8 GiB cgroup, 45 min per pair (chart by chart $y_q = 1$) | Minimal primes of $\sqrt{K_2}$ (and linear radical forms $h_1(\sqrt{K_2})$) for all remaining pairs `[Inferred]` | Single affine chart `radical(K2)` + `minAssChar` exceeds 45 min `[Inferred]` |
| **P6** | **Newton-Hensel arc + kernel-limit certificates for `E8bar->N+-`, `Iso`, `W8->N-`** across all minimal primes from P5 `[Inferred]` | Host, 8 GiB cgroup, 1 h per pair | Reduced-support equality + limiting 8-plane families for all remaining nullity-8 pairs `[Inferred]` | Any component prime fails containment or reaches max Jacobian rank $< \dim P_\alpha$ `[Inferred]` |
| **P7** | **Second-prime replay ($p=32029, r=9115$) of Method A & arc certificates** from producer headers `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L320)`]` + regenerate `nullity16-rees-fibers-result.json` at $p=32009$ `[Observed:` [final-plan-bundle.md](file://SCRATCH/final-review/final-plan-bundle.md#L331)`]` | Host (or GitHub Actions `ubuntu-26.04` 16 GB), 12 GiB cgroup, 2 h | Prime-agreement receipt on $h_d$, component degrees, and Jacobian ranks; clean nullity-16 JSON digest `[Inferred]` | Any $h_d$, component count/degree, or Jacobian rank disagrees between $p=32009$ and $p=32029$ `[Inferred]` |
| **P8** | *(Conditional: only if full scheme $F(I)$ is still required after P4)* **Affine-chart Rabinowitsch `msolve 0.11.0` AVX-512 pilot on `VB`** `[Inferred]` | Host (or approved Azure `FX4mds_v2`), 12 GiB cgroup, 2 h | Exact affine chart $y_3=1$ of $F(I)$ for `VB` without `a`-graph homogenization `[Inferred]` | Degree matrix RSS exceeds 12 GiB or reproduces post-pivot stall `[Inferred]` |
