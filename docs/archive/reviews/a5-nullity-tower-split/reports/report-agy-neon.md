# Red-Team Review: PR 1037 (`a5-nullity-tower-split`)

Head reviewed: `7a688b9ad4b9fadbbe7dc08194a7c2e9cd078e10` (worktree `WORKTREE-NAME`, read-only, no local execution).

## Ranked Defects in Code, Claims, and Records

1. **Critical (`proved`): `vb_pfaffian_item` does not restrict to `c_16 = 0`, so A5-657 is not refuted on the doubly pure slice.**
   - `result.json:2779-2789` lists `vb_pfaffian.coordinate_units = [3, 4, 9, 10, 11, 12, 13, 14, 16]`, which includes the doubling unit `e_16`.
   - `scripts/a5_nullity_transitions.py:535-551` computes and factors the 9-variable Pfaffian *with* `e_16` present, while `lines 556-558` drop `e_16` (`if w % 16:`) when computing the vanishing orders of `Q` and `G`.
   - At `W8` (`e_1 + e_10`), the full Pfaffian with `m` (`e_16`) is also irreducible over `Q` (`(u.u + m^2 + v.v)^2 - 4|u x v|^2`); it becomes `|lead(G)|^2` only after setting `m = 0`. Irreducibility of the 9-variable VB Pfaffian therefore does not imply irreducibility of its `c_16 = 0` doubly pure restriction (`README.md:111-113`, `ledger.tsv:636` A5-657).
   - Secondary gap (`proved`): `sp.factor_list` (`line 551`) factors over `Q`. A single squared modulus `|f|^2` of a complex cubic `f` is generically irreducible of degree 6 over `Q` and `R` (just as `|zeta.zeta|^2` at `W8` is irreducible of degree 4 over `Q`). Irreducibility over `Q` refutes a *product* `|Q_lead|^2 |G_lead|^2` (which must split as degree `2 * 4` over `Q`) only after setting `c_16 = 0`.
   - Decisive check (run on workstation): evaluate `sp.factor_list(value.as_expr().subs(symbols[-1], 0))` inside `vb_pfaffian_item`. A degree-2 factor (or full split) refutes the current A5-657 rationale; an irreducible degree-6 polynomial over `Q` at `c_16 = 0` restores the refutation of `|Q_lead|^2 |G_lead|^2` (still check over `Q(i)` before ruling out a single `|f|^2`).

2. **High (`proved`): Serial CPU-bound loops violate `AGENTS.md:47-48` and squeeze `ci/gates.json` to 16% headroom.**
   - `gororoba-quantum/AGENTS.md:47-48` rejects any serial CPU-bound loop over independent items (`parallel.py` required).
   - `four_term_points()` (`scripts/a5_nullity_transitions.py:479-488`) runs a serial loop over `C(29, 3) = 3654` triples (up to `29,232` `32x32` FLINT ranks). `arcs_item()` (`lines 613-647`) runs serial loops over 20 units, 380 signed pairs, and 22 `kernel_limits.certify_kernel_limit` calls.
   - `ci/gates.json` raises `core-a5-nullity-transitions` to `120 s` (`103 s` measured on 32 threads) and `self-test` to `20 s` (`workers: "all"` itself conforms to `ci/AGENTS.md`). Moving `four_term_points()` and the 22 `certify_kernel_limit` calls onto `parallel.ordered_map` removes the policy violation and restores timeout margin.

3. **Medium (`proved`): `validate()` omits four claims of Statements 11, 13, and 14, and `self_test()` omits two new computations.**
   - Statement 11 (`README.md:95-96`, `ledger.tsv:641` A5-662): `validate()` (`scripts/a5_nullity_transitions.py:1001`) checks `order == 8 and cofactor > 0`, never verifying `2^40`, `2^32`, `2^52`.
   - Statement 13 (`README.md:107`, `ledger.tsv:643` A5-664): *"fails in both directions"* for the XOR-order rule is unchecked in `validate()` (`line 1058` checks only `P15 in FAILED_PREDICTIONS`); `self_test()` (`lines 1094-1097`) tests only the order-8/scalar-commutant witness (`e1+e12+e13+e30`), never the order-16/quaternion witness (`e1+e2+e11+e12`).
   - Statement 14 (`scripts/a5_nullity_transitions.py:1018-1020`): `same` omits `kernel_halves_equal` and `kernel_in_upper_half`, leaving `N+` `kernel_halves_equal` unchecked.
   - `self_test()` (`lines 1061-1104`) has no mutation control for `vb_pfaffian_item` or the order-8 cofactor loop.

4. **Low-Medium (`proved`): `arcs_item` evaluates `s = 3` only, and `ledger.tsv:644` drops the `s = 3` qualifier.**
   - `scripts/a5_nullity_transitions.py:613-620` checks `integer_nullity` at `s = 3` only. Nullity 0 at `s = 3` proves generic nullity 0 (by upper semicontinuity of nullity), and the 20 nullity-4 pairs get full `certify_kernel_limit` certificates (`line 624`). For the 160 pairs with nullity 8 at `s = 3`, `s = 3` proves only generic nullity `<= 8`. `README.md:115-116` correctly writes *"at s = 3"*; `ledger.tsv:644` (A5-665) omits *"at s = 3"* from its statement column.
   - Decisive check: run `integer_nullity` at a second parameter (e.g. `s = 5`) on the 160 pairs; any drop below 8 refutes generic nullity 8.
   - `sphere_normal` (`lines 581-590`) does not explicitly assert `|n| = 1`, which is harmless (`proved`): for a certified rank-4 orthogonal projector `P` inside `ker L_y`, `(2P - I)^2 = I` and `E_i E_j + E_j E_i = 2 delta_ij I` force `(n.E)^2 = |n|^2 I = I`, hence `|n| = 1`.

## Kernel-Split Rule (Statement 13) and Tower (Statement 12): Exact Proof and Remaining Gap

- **Half-equality is automatic on doubly pure points (`proved`).** For any nonzero doubly pure `y = (p, q)` in `Im A_4 + Im A_4 e_16`, `(p, q)(c, 0) = (pc, q bar(c))` and `(p, q)(0, d) = (-bar(d) q, dp)`. Conjugation gives `bar(-bar(d) q) = qd` and `bar(dp) = -p bar(d)`, and `pc = 0` or `q bar(c) = 0` with `(p, q) != 0` forces `c_0 = 0`, so `bar(c) = -c`. Thus `A_lo = ker L_p n ker L_q = A_up` for *every* nonzero doubly pure `y`; `kernel_in_lower_half == kernel_in_upper_half` and `kernel_halves_equal` (when `> 0`) hold identically.
- **Forward direction of Statement 13 (`proved`).** When `dim A_lo = 4`, `ker L_y = (A, 0) + (0, A)` with `A` a 4D sedenion kernel in `Im A_4`. On `A`, `bar(c) = -c` implies `<d', da> = <-d', ad> = -<d', L_a d>`, so `P_A R_a P_A = -P_A L_a P_A =: -M_a`, where `{M_a}` spans `sp(1)` (dim 3) with commutant `H_opp` (dim 4). On `(A, 0) + (0, A)`:
  - lower-half units `(a, 0)` compress to `diag(M_a, -M_a)` (3 dims);
  - `e_16 = (0, 1)` compresses to `antidiag(I_A, -I_A)` (1 dim);
  - upper-half imaginary units `(0, b)` compress to `antidiag(-M_b, -M_b)` (3 dims).
  These 7 forms are linearly independent (pencil dim 7). Commuting with `antidiag(I, -I)` forces `[[X, Y], [-Y, X]]`; commuting with `diag(M_a, -M_a)` forces `X in H_opp` and `Y M_a = -M_a Y` for all `M_a in sp(1)`, which forces `Y = 0` (since `J_1 J_2 = +-J_3`). Thus the commutant is `H` (dim 4) and the Lie closure is `sp(2)` (dim 10).
- **Full Tower (Statement 12, A5-661) for every `n >= 4` (`proved`).** Applying the exact same doubling step inductively to `y = e_1 + e_10` from `A_n` to `A_{n+1}` gives `ker_{n+1} = ker_n + ker_n e_{2^n}` (dim `2^{n-2}`), `P_{n+1} = 2 P_n + 1 = 2^{n-2} - 1` (`3, 7, 15, ...`), commutant `H` (dim 4), and Lie closure `sp(2^{n-4})` of dim `2^{n-4}(2^{n-3} + 1)` (`3, 10, 36, 136, ...`).
- **Remaining gap and sampling bias in Statement 13 (`hypothesis`).** `four_term_points()` (`lines 476-488`) fixes `e_1`, restricts coefficients to `+-1`, keeps only the first sign pattern per triple, and samples every 9th (`36` `W8` points). Two parts of A5-664 remain unproved: (a) whether any `W8` point has `dim(ker L_p n ker L_q) = 2` (two sedenion zero divisors whose 4D kernels meet in a 2-plane), and (b) the converse (`A_lo = 0` implies scalar commutant).
- **Cheapest decisive computation (workstation, < 5 s):**
  1. Fix `p = e_1 + e_10` in `A_4`, scan all 84 two-term sedenion zero divisors `q` in `A_4` with `dim(ker L_p n ker L_q) == 2`, form `y = p + lambda q e_16` (`lambda in {1, 2}`), and run `integer_nullity`, `hardware_orbits.classify`, and `structure_item`. Any `W8` hit refutes A5-664's dichotomy (`in_lower in {0, 4}`).
  2. Run `sampled_item` on all 474 points of `four_term_points()` (removing `::SAMPLE_STEP`) plus unequal-coefficient `W8` points `p + 2 q e_16` with `A_lo = 0`; any `A_lo = 0` point with commutant dim `> 1` refutes the converse.

## Claims Not Broken (One Line Each)

- **Claim 1 (`structure_item`, `scripts/a5_nullity_transitions.py:323-388`, `proved`):** `gram.inv() * frame.T * L_w * frame` is basis-invariant and `gram`-skew-adjoint; `in_lower`, `in_upper`, `equal`, and Sylvester's criterion on the traceless commutant are sound.
- **Claim 6 (`path_item` order/cofactor loop, `lines 222-228`, `proved`):** Repeated exact `sp.quo` in `QQ[s]` is sound; `gamma1`'s order 8 and cofactor `2^40` match `result.json:220-278`.
- **Claim 8 (`P P' P = cos^2(theta/2) P`, `README.md:133-135`, `proved`):** From `E_i E_j + E_j E_i = 2 delta_ij I` and `(n.E)(n'.E)(n.E) = 2(n.n')(n.E) - (n'.E)`, expanding `4 P P' P` gives `2(1 + n.n') P = 4 cos^2(theta/2) P`, so all four principal cosines equal `cos(theta/2)`. (Koebisu `arXiv:2611.30652` attribution unchecked: no PDF in worktree.)

## Unrecorded Conjectures

1. **Conjecture (`hypothesis`): Every `W8` point `y = (p, q)` with `dim(ker L_p n ker L_q) = 2` fails to lie in `W8` (or has nullity `!= 8`), and every `A_5` point with `dim ker L_y = 2k` whose kernel contains a 4D-split summand `(A, 0) + (0, A)` loses its `H` commutant precisely when mixed kernel vectors (`c != 0, d != 0`) are present (as at `N+-`, `result.json:2389-2425`, where `kernel = 16` has 8 split + 8 mixed dimensions and scalar commutant).**
   - Falsifier: a `W8` point with `kernel_in_lower_half = 2`, or an `N+-` point whose compression restricted to its 8D split sub-kernel `(A, 0) + (0, A)` fails to have commutant `H`.
   - Cheapest test: the 84-pair `A_4` scan above, plus `structure_item` restricted to the 8D split sub-kernel of `N-` (`e_3 + e_20 + e_12 - e_27`).
2. **Conjecture (`hypothesis`): At `VB` (`e_3 + e_20`), the `c_16 = 0` restriction of the 12x12 compression Pfaffian is divisible by `|Q_lead|^2` (a quadratic factor over `Q`) or by `|f|^2` over `Q(i)`.**
   - Falsifier: `Pf|_{c_16 = 0}` stays irreducible of degree 6 over `Q(i)`.
   - Cheapest test: `sp.factor(value.as_expr().subs(symbols[-1], 0), extension=[sp.I])` in `vb_pfaffian_item` (< 1 s on workstation).
