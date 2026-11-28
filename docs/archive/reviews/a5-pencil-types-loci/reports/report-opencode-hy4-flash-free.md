I'll start by reading the required instruction files, then examine the PR diff and materials.

Now let me examine the PR diff and the key files.

Now let me connect to the compute host and verify the checkout state, then start targeted computations.

The multiprocessing needs a `__main__` guard. Let me rerun with a proper guard.

I need to compress the resolved exploration before continuing.

Now I'll run the decisive checks on the remote host. First, extra alphas and J_k commutation.

# Red-team report: PR 1053 (`a5-pencil-types-loci`, head `f917aa07b`)

No claim falls inside its stated scope. All six reproduce under independent checks on `the compute workstation`. The residual risks are three proof gaps the PR already declares open, plus minor record-fidelity gaps.

All computations used:
the compute workstation → `cd WORKTREE` → `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON" SCRATCH/<script>.py` → Singular 4.4.1, flint 0.9.0, sympy 1.14.0. No file in either checkout changed.

---

## Ranked by consequence

### 1. Claim 2 — W8 type rule — **computed; general proof open (hypothesis)** — largest residual risk

- Record: `scripts/a5_pencil_types_and_loci.py:59,117-129,132-162`; `docs/evidence/a5-nullity-transitions/README.md:216-220`; ledger `docs/evidence/a5-exceptional-fibers/ledger.tsv:646,651`.
- Recomputed: full census reproduces 4,268 dim-2 pairs, 417 dim-4 pairs, 3,005 dim-0 sampled pairs; W8 tally 177 R / 3,282 C / 139 H; 33 type-R through the sympy route, 0 mismatches.
- Sampling stress (`offsample.py`): independently rescanned dim-0 pairs with `(131i + j) % 1171 == 1` (residue 1, not the recorded 0): 3,005 pairs → S0 2,242, S4_VQ 545, W8 180, Iso 38; `type_item` on all 180 W8 → 147 bounds route, 33 sympy route, **mismatches 0**. A different residue does not hide a family (`computed`).
- Real gap: the type rule for dim A = 0 has no BDI normal form. Theorem 14.6 of Biss–Dugger–Isaksen (`math_0511691.pdf`, pp. 23–25) assumes `Ann a ∩ Ann b ≠ 0`; its cases cover dim A = 16/12/8 only. The PR's `dim A = 0` evidence is finite census, and ledger A5-667 says "survives" (`scripts/AGENTS.md` grounding, ledger `:646`).
- Conjecture: the rule holds for all real W8 points. Falsifier: a W8 point whose commutant/closure disagrees with dim A. Cheapest test: prove the pairing identity `(ker L_p ∩ H×H) = (ker L_p ∩ H'×H')` for arbitrary zero divisors, or extend `offsample.py` to every residue in `[0,1170]` (3,005 points each; roughly 4 minutes per residue).

### 2. Claim 3 — BDI normal form and `J_k` — **computed; symbolic proof open (hypothesis)**

- Record: `scripts/a5_pencil_types_and_loci.py:62-70,197-238,241-245,444-451`; README `:221-230`; ledger `:652`.
- Theorem name: Biss–Dugger–Isaksen Theorem 14.6, proof pp. 23–25. All seven recorded alphas satisfy `alpha² + 1 ≠ 0` (Case 1). Reading checked: `t = e_4`, `k = e_3`, `y = t + kt + alpha t + (alpha k)t`, half-slots `[0-3]` / `[4-7]`, `J_k = +L_k` on H-part.
- Independent alphas (`extra_alpha.py`, sequential `normal_form_item`): `1, 3, 5k, 2+k, 1+k, 2i+k` → kernel 8, `dim_a = 4` for the five inside `<1,k>`, `2` for `2i+k`; `preserves_kernel`, `square=-I`, `commutes_with_all_31`, `kernel_splits` all **True**. `alpha = k` and `alpha = i` (Case 2) give kernel 16/12 and fail commutation — outside the stated Case 1 scope.
- Span check (`extra_alpha3.py`, `rec.same_span` vs alpha `2`): inside `<1,k>` → omega and perp spans unchanged; `2i+k` → perp span changed, omega unchanged. "Moves exactly when alpha leaves `<1,k>`" survives (`computed`).
- Conjecture: the identities hold for every Case-1 alpha. Falsifier: a Case-1 alpha where `J_k` fails. Cheapest test: symbolic solve of the Theorem 14.6 system S1/S2 over `alpha = a + bi + cj + dk` with `a² - b² - c² - d² + 1 ≠ 0`, reusing the script's `alpha²+1` case split.

### 3. Claim 5 — statement 23, order-3 arc equations — **derivation verified (computed); higher order open**

- Record: `scripts/a5_pencil_types_and_loci.py:364-423,453-474`; README `:233-241`; ledger `:654`.
- Re-derived effective forms independently: with `A = L_0`, `B = L_w`, `C = L_v`, and `K` the 24-dim kernel basis, `F2 = Kᵀ B K - Kᵀ A A⁺ A K`; `F3 = Kᵀ C K - (Kᵀ B A⁺ A + Kᵀ A A⁺ B) + Kᵀ A A⁺ A A⁺ A K`. Signs match README "minus mixed, plus cubic". No order-3 gap: the gauge `n1` is fixed once `F2 = 0`, and `v ↦ Kᵀ L_v K` has image exactly the 7-dim pencil, which is why all 300 quadratic + 744 mixed + 2,600 cubic terms land in the span. Reproduced `outside = 0` for all three blocks; identity mutant leaves the span (`computed`).
- Decisive subtlety checked (`arc_sym.py`): choosing `w = 3` (zero compression) and solving rational `v` with `forms[v] = Q + target` reproduces `F2 = target` of rank 4, but finite-s nullity of `L(y_0 + s w + s² v)` at `s = 1/8, 1/32` is **0**. This is **not** a counterexample: order-2 solvability alone does not put the arc in the zero-divisor variety; statement 23 assumes an arc exists. With `F2 = 0` solved, `F3` is rank 0 and finite-s nullity is also 0 — effective order > 3, explicitly out of scope.
- Conjecture: every nullity-4 arc of effective order ≤ 3 limits on the A5-655 2-sphere. Falsifier: such an arc with limiting plane off the sphere. Cheapest test: for each of the 100 nullity-8 VB lines, solve the order-3 solvability condition `F3 n0 ∈ im F2` for `u` in the 24-dim kernel; confirm the limiting plane stays `ker F2`.

### 4. Claim 4 — VB rank-4 locus and second-order line criterion — **proved (ideal membership); computed (line census)** — strongest claim

- Record: `scripts/a5_pencil_types_and_loci.py:71-72,248-299,302-316,319-361`; README `:222-232`; ledger `:653`.
- Reproduced: 768 nonzero 6×6 sub-Pfaffians; Singular `std` over Q in `dp`; ideal dimension 4; powers `m³`, `(x3²+x4²)²`, `(x11²+x12²)²` all present; two 4×4 sub-Pfaffians `-4(x9²+x14²)`, `4(x10²+x13²)`; 284 rank-4 unit sums with tally exactly `{nullity [8,8]:100, [0,0]:88, [4,4]:96}`.
- Off-family stress (`vb_off.py`, 114 integer plane directions with coefficients in `{1,2,3,-1,-2}`; `vb_broad.py`, 1,295 directions in `{-2,-1,0,1,2,3}` on all four plane units): **0 mismatches**, all rank 4 / nullity `[0,0]`. Pseudoinverse convention verified: `A A⁺ A = A`, `A⁺ A A⁺ = A⁺`, `Aᵀ ker = A ker`. No wrong pseudo-inverse or kernel convention (`proved` + `computed`).
- The sum-of-squares membership argument is decisive over R: `m³ = 0 ⇒ m = 0`, `u² + v² = 0 ⇒ u = v = 0`.

### 5. Claim 1 — full Pfaffian irreducibility — **computed**

- Record: `scripts/a5_pencil_types_and_loci.py:102-115`; README `:212-214`; ledger `:650`.
- Reproduced with `fmpz_mpoly factor`: VB content `-64`, degree 6, 50 terms, factor degrees `[[6,1]]`; N−/N+ content `-64/+64`, degree 8, 12,579 terms, `[[8,1]]` (19 units including `e_16`). No factorization found (`computed`). Self-test mutant at `:596-601` confirms the restricted VB Pfaffian *is* reducible, so the full-coordinate qualifier matters.

### 6. Claim 6 — ledger/README fidelity — **computed; minor gaps**

- `validate` (`scripts/a5_pencil_types_and_loci.py:484-551`) carries a `require` for every principal sentence in statements 19–23: term counts, degrees, factor degrees, census tallies, W8 type match, seven alphas' kernel/commutation/splitting, `dim_a`, Singular powers, plane ranks, exact 284-line tally, and `outside == 0`.
- Gaps worth a note: README `:227-229` ("e10 and e1+e10 have the same compression; e1 enters only at second order") and the derivation sentence in statement 23 lack dedicated `require`s; they are consequences of `vb_line_item` / `w8_schur_item` but not individually gated. P31 was written after six of eight nullities were read (ledger `:653` admits this). No sentence contradicts the computed scope (`computed`).

---

## Conjectures and cheapest tests

| Conjecture | Falsifier | Cheapest test |
|---|---|---|
| Type rule extends to all dim A = 0 W8 points | One W8 point with wrong commutant/closure | Extend `offsample.py` across all 1,171 residues; ~4 min per residue on `the compute workstation` |
| `J_k` commutes for every Case-1 alpha | One Case-1 alpha failing commutation | Symbolic solve of system S1/S2 with `alpha²+1 ≠ 0` over Q(a,b,c,d) |
| Statement 23 extends past effective order 3 | Higher-order arc with off-sphere limiting plane | Solve the order-3 solvability condition for `u` on each of the 100 VB nullity-8 lines |
| The VB rank≤4 locus is exactly that plane globally | A real rank≤4 direction off plane | Already decided by Singular ideal membership; no further test needed |

**Verdict:** merge-blocking falsification: none. Open proof items: dim A = 0 type rule, symbolic alpha proof, effective order > 3 arcs.
