### Red-Team Report: PR 929 (`75e830cdb`)

**Baseline checks on remote (`75e830cdb`)**:
- `"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_plane_incidence.py --check && "$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_rational_charts.py --check` -> `pass: 6 incidence Jacobians, 4 complement frames` and `pass: 2 boost families, 2 further precisions` (`computed`).
- `"$PYTHON" -m pytest -v tests/test_a5_nullity4_qg_plane_incidence.py tests/test_a5_nullity4_real_polar_rational_charts.py` -> `56 passed in 4.49s` (`computed`).

---

#### 1. Critical — `A5-551` / `A5-561` precision leak in `evaluation_at` (`ctx.prec` overwritten to `200`)
- **Claim falsified (`proved`, `computed`)**: `"with the precision passed to every evaluation"` (ledger.tsv line 530, ledger.tsv line 540, and nullity4_real_polar_rational_charts.py).
- **Mechanism**: evaluation_at sets `ctx.prec = precision` (line 380), computes the matrix exponential, and then calls `ff._pairing_factors()` (line 384). ff._pairing_factors sets `ctx.prec = PRECISION` (`200`) on line 286 and caches `(z, line)`. On the first call in every fresh worker (and in the parent), the multiplications `z * pi * line` and `z * derivative * line` (line 385) run at **200 bits**, not `precision`, and `(z, line)` stay cached at 200 bits for subsequent calls (`400` bits included).
- **Evidence (`computed` on remote)**:
  - Calling `rc.evaluation_at((400, 0, 2))` before `_pairing_factors` is cached returns with `ctx.prec == 200`; `call1 == call2` is `False` (`call1` ball radius exponent `-223` vs `-425` at genuine 400 bits). Calling `rc.evaluation_at((131, 0, 2))` after `ff._pairing_factors.cache_clear()` likewise leaves `ctx.prec == 200` (`first_131 == gen_131` is `False`, radius exponent `-157` vs `-156`).
  - Why the final verdict survives (`proved`, `computed`): every entry of `_pairing_factors` (`ff._exact()`) is a Gaussian integer (`non-integer entries: []`), so 200-bit construction introduces zero rounding error in `z, line`. Re-running `krawczyk_at(131)` and `krawczyk_at(400)` with `ctx.prec` restored after `_pairing_factors()` still returns `{'interior': True, 'contraction_bits': 13, 'pairing_bound_bits': 36}`.
  - Line-by-line check (`proved`): `krawczyk_at` (lines 388-412) matches `ff.krawczyk` (lines 389-417) apart from precision, except `precision_record` (line 416) omits `min_items=2` on `parallel.ordered_map(krawczyk_at, list(PRECISIONS))`, running the 2-item outer map serially in the parent (because `MIN_PARALLEL_ITEMS = 64` in parallel.py).
  - Test gap: test_evaluation_at_200_bits_is_the_evaluation_of_the_certificate only tests at `ff.PRECISION` (`200`), where the overwrite to `200` is invisible.

---

#### 2. High — Claim 1 (`A5-559` & `A5-558`): `"in every fiber"` is false at `s = +-1` and on a codimension-2 locus at `s = 2`; `A5-559` & `A5-558` drop qualifiers
- **Claim falsified (`proved`, `computed`)**: nullity4_qg_plane_incidence.py:12-13 and A5-559 assert that inside `"each fiber K minus J (real dimension 6)"` the real points with kernel plane `P_j` form a `"complex line minus the points of J (real dimension 2): real codimension 4 in every fiber, so real codimension 4 in S"`.
- **Two counterexamples**:
  1. At `s = +-1` inside `S`, `A5-555` and `A5-560` prove `(g P_j)^{perp_H} \cap g K \subset g J` for all `j in {x, y, z}` and all `g`, so the intersection with `g K \ g J` is **empty** (not real dimension 2) (`proved`).
  2. Off `s = +-1` at `s = 2`, `(g P_y)^{perp_H} \cap g K \subset g P_x \subset g J` is one complex equation `det([c_perp, C_px]) = 0` in Hermitian `g in G_2(C)`. At 50 digits (`computed` on remote with `mpmath`), `g = exp(i (t_0 D_6 + t_1 D_7))` with `(t_0, t_1) = (0.62766209930455420893..., 0.23537328723920782835...)` satisfies `||g - g^H|| = 0`, `|det([c_perp, P_x])| = 0`, `||c_perp||_2 = 22874.86...`, `M(g k_perp)` has 7 singular values `< 3.4e-11` (`8th = 7.979e+04`, so `nullity = 7`, inside `g J`), and the `2x2` real Jacobian of `det([c_perp, P_x])` has `det J = 1.614e7`. Thus `{P = P_y}` is **empty** on a smooth real-codimension-2 family of fibers even over `s = 2`.
- **What actually holds (`proved`, `computed`)**: For fixed `K`, `k -> (<k, p_1>, <k, p_2>)` is onto `C^2` so the orthogonal line is real dimension 2 in `K`, hence real dimension 2 in `K \ J` on the **dense open set of fibers** where it misses `J`; locally at the 6 witnesses of `s in {0, 2}`, the real `4x36` incidence Jacobian has rank 4 on a 13-complex-dimensional (`26`-real-dimensional) tangent space of `S` (INCIDENCE_ROW), so `"real codimension 4 in S"` holds locally there and on that open locus.
- **Ledger text defects**:
  - `A5-559` (ledger.tsv:538) claims `dim L = 4` is `(kernel plane P_y or P_z)`, dropping `"away from the roots of D1 D2"` (`s^2 +- 4 i s - 1 = 0`, where `P_y = P_x` or `P_z = P_x` gives `dim L = 6`) present in nullity4_qg_plane_incidence.py:15.
  - `A5-558` (ledger.tsv:537) strengthens `A5-559` by omitting `"fiber by fiber"` (`"each have real codimension 4 in the stratum (A5-559)"`).

---

#### 3. Medium — Claim 3 (`A5-561`): bounded-negative code skips finite roots and symbolic boost equivariance
- **Gap 3a — Nilpotent root subgroups only test identical vanishing (`proved`, `computed`)**: root_subgroup checks `not any((z0.H * pi * line).applyfunc(sp.expand))`, testing only whether `F(t, tb)` is the zero polynomial. It never checks whether `F(t, conj(t)) = 0` has nonzero solutions `t != 0` on the remaining 76 nilpotent `D_a +- i D_b`.
  - **Independent closure (`computed` on remote)**: Solving `Re F = Im F = 0` in `(tr, ti) in R^2` via `sp.groebner` (`lex`) and `sp.real_roots` / `sp.solve` across all 76 non-identically-zero nilpotent subgroups yields **0 nonzero real roots** (every univariate eliminant root other than `0` is strictly non-real, e.g. `ti*(ti**2 + 2) = 0`). The mathematical conclusion for all 100 nilpotent charts holds once this check is added.
- **Gap 3b — Boost equivariance only checked at one rational point; `C_R = -1` branch omitted (`proved`, `computed`)**: family_structure never verifies `M(g t) = g M(t) g^T` symbolically on the families (only at `INSTANCE` in family_instance:342). Also family_incidence_at_zero hardcodes `CHR = 1`, omitting `CHR = -1` when `S_R = 0`.
  - **Independent closure (`computed` on remote)**: `M(diag(A,1,A) t) - diag(A,1,A) M(t) diag(A,1,A)^T` vanishes identically modulo `_reduced` for both `"4, 7"` and `"5, 6"` (`0` nonzero entries), and remains `True` at `CHR = -5/3, SHR = 4/3`. At `S_R = 0, C_R = -1`, `A_R = -P_4 + P_3` still lies in `G_2(C)`, leaves `F` identical to `C_R = 1` (because `A_R^2 = I` and `[a_left, P_4] = 0`), forces `S_L = 0`, and gives `R = 0`.
- **Gap 3c — Basis mislabeling (`proved`, `computed`)**: Docstrings at line 4 and line 313 write `C = span(z_0, c_2, c_3)` and `"rows of c_2 and c_3"` of `polar()`. Actually none of `polar()`'s 3 columns equals `z_0` (`z_0 = i k_0 + 3 k_1 + 5 k_2`). Because `z_0 in span(k_0, k_1, k_2)` and `F = 0`, any nonzero `2x2` minor of `R = C^* Pi l` still implies `rank N = rank R = 2`.

---

#### 4. Claims & Defect Classes Attacked and Not Broken
- **Claim 1 item 2 (`nullity4_qg_plane_incidence.py:157-215`) (`proved`, `computed`)**: Verified `frame_ds` and `z_ds` differentiate the chart correctly, `directions` span 13 inside `ker dQ n ker dDelta` (`rank(dQ, dDelta) = 2`), compact columns vanish, and frame changes at `F = 0` left-multiply `dF` by an invertible `2x2` matrix so rank 4 is frame-independent.
- **Claim 2 / `A5-560` (`nullity4_qg_plane_incidence.py:24-37`) (`proved`, `computed`)**: Could not break. `q in P_y cap P_z` holds (`nullity4_qg_orbit_types.py`), `E_+` and `E_-` are Hermitian-orthogonal and invariant under `G_2(C)`, the 120-degree rotation (`ot.rotation_acts_by_scalars_on_the_eigenlines`), and `C^*`-scaling — covering every point of the `s = +-1` complex orbit type, not just `exp(D_0 + i D_9)`.
- **Edited rows `A5-551`, `A5-555`, `A5-558` (`ledger.tsv:530, 534, 537`)**: `git diff` vs `origin/main` confirms `A5-552` and `A5-557` are untouched; `A5-551` and `A5-555` preserve their prior basis and narrow/close hypotheses cleanly.
- **Other defect classes checked (`proved`)**:
  - *Gates / CI*: ci/gates.json:5512-5533 and ci/pr_checks.sh:79-81,120-122 do not mask failures; `test_a_low_precision_is_refused_and_a_wide_box_fails` restores `ff.RADIUS_BITS` via `monkeypatch`.
  - *Test mocking*: `test_pinned_record_passes_its_rules` (incidence test:79, charts test:116) monkeypatches `_inputs` to `record["inputs"]`, which matches `verdict` rules only for comparing pinned record vs module constants (input sha256 verification itself runs in `--check`, not those two unit tests).

---

#### 5. Conjecture (`hypothesis` + 50-digit `computed` witness): `rank N = 1` on a 3-parameter rational `SL(3, C) < G_2(C)` Hermitian chart
- **Structure missed by `A5-561`**: Over `C`, `Stab_{G_2(C)}(e_4) = SL(3, C)` preserves the `1 + 3 + 3` splitting `C e_4 + V_+ + V_-` (`V_+-` the `+-i` eigenspaces of `J = L_{e_4}` with Gaussian-integer basis `W = [e_1 + i e_5, e_2 + i e_6, e_3 + i e_7]`). For any `3x3` Hermitian matrix `A = L D L^H` (`det A = 1`, `L` unit lower-triangular, `D = diag(d_1, d_2, 1/(d_1 d_2))`),
  `g(A) = e_4 e_4^T + (1/2)(W A W^H + conj(W) L_inv^T D^{-1} conj(L_inv) W^T)`
  is **strictly Hermitian**, **rational** in the 8 real parameters (no `exp`/trig), and **identically in `G_2(C)`** (`M(g t) = g M(t) g^T` verified symbolically across all 8 parameters on remote in `36.12s`, `computed`).
- **3-parameter rational slice (`proved` vanishing + 50-digit `computed` witness)**: Fix `d_1 = 1, y_{21} = x_{31} = x_{32} = 0, y_{32} = -1/2`, leaving `(d_2, x_{21}, y_{31}) in R^3`. Symbolically, `Im F_0 = Im F_1 = Im m_{12} = 0` identically (`computed`), reducing `F = 0, det N = 0` to **3 polynomials** `(Re F_0, Re F_1, Re m_{12})` in `(d_2, x_{21}, y_{31})` of total degrees `(8, 8, 16)` (`40, 42, 126` terms).
  - Generic `F = 0` point (`d_2 = 27/20`): `(x_{21}, y_{31}) = (-0.166698..., 0.737144...)` gives `|F| < 4e-50`, `|m_{12}| = 0.72975`, `sv(R) = [25.00, 0.1727]` (`rank R = 2`).
  - Proper closed `rank N = 1` point: `(d_2, x_{21}, y_{31}) = (1.3212711685928388..., -0.1676212608491096..., 0.7050563656608159...)` gives `|F_0| = 3.88e-50`, `|F_1| = 2.14e-50`, `|m_{12}| = 1.60e-49`, `sv(R) = [19.9078602, 1.00e-17]` (`rank R = 1`), with transverse Jacobian `det J_3 = -3034.4`.
- **Falsifier**: Eliminating `(Re F_0, Re F_1, Re m_{12})` in `Q[d_2, x_{21}, y_{31}]` (clearing `d_2` denominators) yields `1` or leaves no real component with `R != 0`.
- **Cheapest test & cost**: `python-flint` `3x3` Krawczyk enclosure around `(1.321271, -0.167621, 0.705056)` certifies an exact algebraic point in `< 0.5 s` without `expm`; exact `grevlex` elimination (`Singular std/elim` on 3 vars of degs `8, 8, 16`; SymPy `groebner` timed out at `15 s` without Singular).
