# Red-team review: PR 1032 (`a5-nullity-transitions`, commit `b2a2d6d4d`)

Scope: read-only audit of PR 1032 in `a5-nullity-transitions` (`b2a2d6d4db32acce193b6e4b3eeadd7b07d28b52`). No local computation was executed; every finding rests on source inspection and hand derivation, with exact falsifying commands where computation is needed.

## Ranked findings

### 1. Commutant dimension 4 + Lie closure dimension 10 do not force `(H, sp(2))` alone, and the review record overstates `A5-654` (proved — moderate)
- **Claim 7 & Claim 9:** `docs/evidence/a5-nullity-transitions/README.md:71-73` and `docs/archive/reviews/a5-outside-transition-report/README.md:60` state as fact that *"the compression commutes with a quaternion algebra on the kernel (A5-654)"*. However, `scripts/a5_nullity_transitions.py:287-293` computes only `commutant_dimension == 4` and `lie_closure_dimension == 10`.
- **Counterexamples to `(4, 10) => (H, sp(2))` on `R^8` (proved):**
  1. `C = C + C` (commutative, dim 4) acting on `C^3 + C^1` has skew-symmetric commutant `u(3) + u(1)` of dimension `9 + 1 = 10`, which also admits rank-8 and rank-4 skew forms.
  2. `C = R^4` (dim 4) acting on `R^5 + R^3` has skew-symmetric commutant `so(5)` of dimension `10` (excluded only because max rank is 4 < 8).
- **Fix:** Either cite the irreducible quartic Pfaffian (which rules out proper invariant subspaces of dim `< 4`, excluding `C^3 + C^1` and `R^5 + R^3`) or check `commutant_is_commutative == False` and traceless trace-form signature `(0, 3)` in `pencil_item()` (refutes `H` if commutative or signature `(2, 1)`).

### 2. The `m = 0` Pfaffian is the squared modulus of the quadratic tangent cone of `G` (A5-357); `m e_16` and the symmetry/plane geometry are the new content (proved — structural)
- **Derivation (proved):** In `a5-zero-divisor-strata/README.md:34-37` coordinates `z_k = y_k + i y_(16+k)`, the base point `y_0 = e_1 + e_10` has `u_0 = e_1`, `v_0 = e_2`, `mu_0 = 0`, giving `Q_0 = 2`, `Delta_0 = 1`, `G_0 = 0` (`y_0 in W_8 \subset Sing{G = 0}`). Along a doubly pure pencil direction `w = u_1 e_1 + u_2 e_2 + u_3 e_8 + v_1 e_17 + v_2 e_18 + v_3 e_24` (`m = 0`), `v(s) = e_2` is unchanged, `u(s) = (1 + s(u_1 + i v_1)) e_1 + s(u_2 + i v_2) e_2`, `mu(s) = s(u_3 + i v_3)`. Expanding `Q(s) = 2 + 2 A + A^2 + B` and `4 Delta(s) = 4 + 8 A + 4 A^2` with `A = s(u_1 + i v_1)` and `B = s^2((u_2 + i v_2)^2 + (u_3 + i v_3)^2)` gives:
  `G(y_0 + s w) = Q(s)^2 - 4 Delta(s) = 4 s^2 (u + i v).(u + i v) + O(s^3)`.
  Its squared modulus is `|G_lead|^2 / 16 = |(u + i v).(u + i v)|^2 = (u.u - v.v)^2 + 4(u.v)^2 = (u.u + v.v)^2 - 4 |u x v|^2`, matching `Pf(K^T L_w K) / 16` at `m = 0` identically.
- **Obstacle / genuinely new content:** `M_UNIT = 16` (`e_16`) lies *outside* the doubly pure domain `y_0 = y_16 = 0` of A5-357 (`L_(e_16)` anticommutes with doubly pure `L_d` by A5-658, adding `m^2` to `u.u + v.v`). Thus the `m = 0` Pfaffian is a tangent-cone consequence of A5-357, while the `m e_16` extension, the `(7, 4, 10)` symmetry structure, and the Grassmannian overlap law (`A5-655`) are new.

### 3. `validate()` leaves README statements unchecked, and `self_test()` mislabels mutant 3 (code defects — moderate)
- **Claim 8 (`scripts/a5_nullity_transitions.py:475-516`):** No `require()` guards:
  - `len` / key sets of `convention` (`[8, 16, 32]`, line 476), `paths` (4 paths, line 477), `orbits` (7 points, line 483), `compressions` (4 junctions and `row["kernel"]` = `8, 12, 16, 16`, `README.md:43`, line 491), `gram_identity` (`[(16,8),(32,16),(64,32)]`, line 507), `three_form` (`[8,16,32,64]`, line 509), `pencil["stiefel"]` (`len == 10`, line 502) — empty lists pass.
  - `row["exceptional_polynomial"] == [1, 0, 1, 0]` (`README.md:40`, `ledger.tsv:629`, missing at lines 488–490).
  - `pencil["coordinate_units"] == [1, 2, 8, 16, 17, 18, 24]` and `pencil["skew_units"]` (`len == 11`, leaving 20 zero, `README.md:46-47`, missing at line 495).
- **Mislabeled mutant (`scripts/a5_nullity_transitions.py:534-535`, `ledger.tsv:635`):** `gram_identity_item((32, 26))` carries the message `"a unit below the doubling unit breaks the cross term"` (and `ledger.tsv:635` repeats `"a unit below h"`), but `26 > 16` is *above* the doubling unit `h = 16`, not below it.
- **`self_test()` global `PATHS` rebinding (lines 521–533):** Safe today because `self_test()` calls `path_item` and `limits_item` in-process, whereas `build_result()` uses `parallel.ordered_map` (`spawn` workers, `gororoba_quantum/parallel.py:3-5`), which would silently ignore rebound globals if ever called from a test. Also `self_test()` has no mutant for `pencil_item` (commutant/Lie closure/Pfaffian/overlap law), `orbit_item`, `compression_item`, or `three_form_item`.
- **Minor doc omission:** `docs/evidence/a5-nullity-transitions/README.md:13` lists `A5-650 to A5-657`, omitting `A5-658` (Statement 8).

### 4. Claims we tried to break and could not (one line each)
- **Claim 1 (`path_item`, lines 172–200, proved):** Tested higher-coefficient interference (impossible: `c_k(s_0) != 0` pins `ord_(x=0) = k`), repeated roots (removed by `gcd(lead, lead')` in char 0), and irrational real roots (caught by Sturm `reduced.count_roots() == len(rational_roots)`).
- **Claim 2 (`paths`, `result.json:143-486`, computed):** `gamma1` lowest coefficient is `2^40 s^8 (s^2+1)^16` (only real root `0`), `gamma3` is even in `s` (`+-1`); falsifier command: `"$PYTHON" -B -W error scripts/a5_nullity_transitions.py --check docs/evidence/a5-nullity-transitions/result.json` (nonzero exit or extra real root refutes).
- **Claim 3 (`limits_item`, lines 208–231, proved/computed):** `P(s) - P(0) == 0` in `Q(s)^(32x32)` with `verify_kernel_limit` (`kernel_limits.py:206`) genuinely certifies constancy on `R \ {0}` (only `exceptional_polynomial` lacks a `require()` in `validate()`).
- **Claim 4 (`pencil_item` mechanics, lines 250–305, proved):** Recursive Pfaffian signs, `gram.inv() * forms[w]` commutant, and `stacked.T.rref()` pivot-basis Lie-closure loop are algebraically sound.
- **Claim 5 (`README.md:53-55`, proved):** `2|u x v| <= 2|u||v| <= |u|^2 + |v|^2 <= |u|^2 + m^2 + |v|^2` has zero gaps.
- **Claim 6 (`STIEFEL_PAIRS` and law test, lines 90–101, 351–363, proved/computed):** `cosine^2 * norms == dot^2 and cosine * dot >= 0` is exact for `norms > 0`; the 10 pairs span 8 non-degenerate normals in `R^3`, and `G(y_0 + s w)` (degree 4, double root at `0`) vanishing at `s = 1, 2, 3` forces the whole line into `V(G)`.
- **Claim 9 (`a5-outside-transition-report/README.md`, consistent):** Fair to the outside report and consistent with `A5-620`, `A5-628`, `A5-646`, `A5-621`, aside from the `A5-654` quaternion-algebra overclaim in Finding 1.

## Unrecorded conjectures suggested by the evidence (hypothesis)

1. **Affine Clifford formula for the limiting 4-plane projector:** On `ker L_(e_1 + e_10)`, `P(u, v) = (I_8 + sum_{k=1}^3 n_hat_k E_k) / 2` where `n_hat = (u x v)/|u x v|` and `E_1, E_2, E_3` are three anticommuting symmetric involutions (`E_i E_j + E_j E_i = 2 delta_ij I_8`, `tr E_k = 0`) commuting with `H`. This proves `tr(P P') = 2(1 + cos angle)` in one line (`T1`).
   - *Falsifier & cheapest test:* Compute `E_k = 2 P(e_k) - I_8` from `STIEFEL_PAIRS[5], [4], [1]` and test `E_i E_j + E_j E_i == 2 delta_ij I_8` and `P(u, v) == (I_8 + sum n_hat_k E_k)/2` at `STIEFEL_PAIRS[6]` (`< 1 s` in SymPy).
2. **Orbit invariance across both `W_8 \ R_12` orbits:** The `(7, 4, 10)` pencil, `H` commutant, and `Pf|_{m=0} = c |G_lead|^2` hold not only on the hyperbolic-plane `W_8` orbit (`e_1 + e_10`) but also on the generic isotropic-plane `W_8` orbit of `a5-zero-divisor-strata` Theorem 8.
   - *Falsifier & cheapest test:* Run `pencil_item` at the generic isotropic `W_8` representative (`u' = e'_1 + e'_3, v' = e'_2 + e'_5` in real coordinates) and check dimensions `(7, 4, 10)` and commutant signature `(0, 3)` (`< 5 s` in SymPy).
