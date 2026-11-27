## Adversarial Review Report: PR 1037 – A5 Nullity Transitions

**Scope:** `scripts/a5_nullity_transitions.py`, `docs/evidence/a5-nullity-transitions/README.md`, `result.json`, ledger rows A5-657/A5-660/A5-661/A5-663/A5-664/A5-665, tests, gates, parallel.py.

---

### Claim-by-claim verdict

| Claim | Verdict | Summary |
|-------|---------|---------|
| 1. `structure_item` correctness | **PROVED** | Intersection dimensions by rank-nullity, subspace equality via combined rank, commutant via exact linear algebra (commutation relations), Lie closure by bracket iteration. All mathematically sound. |
| 2. Tower (A5-661) | **COMPUTED – reading overstates** | Three levels: A₄ (kernel 4, pencil 3, closure 3), A₅ (8, 7, 10), A₆ (16, 15, 36). All have quaternion commutant (dim 4, noncommutative, negative-definite trace form on traceless). sp(1)=3, sp(2)=10, sp(4)=36 match Lie closures exactly. Pencil dims 3,7,15 = 2^(n-2)-1. **Falsifier:** Three levels could fit another family; "sp(1), sp(2), sp(4) on ℍ, ℍ², ℍ⁴" extrapolates from three data points. |
| 3. Kernel-split rule (A5-664) | **COMPUTED – biased sample** | 8 named + 36 sampled (every 9th, first sign pattern per triple): 12 quaternionic ([4,4,True,7,4,10]), 32 scalar ([0,0,False,7,1,28]). XOR order rule fails in both directions on this sample (e₁+e₁₂+e₁₃+e₃₀ has order 8 but scalar commutant). **Mechanism gap:** Why kernel split A+A → quaternionic is not explained. **Falsifier:** First-sign-pattern + stride-9 sampling may miss W8 points with intermediate kernel splits (dim 1–3) or split-kernel with scalar commutant. |
| 4. VB Pfaffian (A5-663) & refutation of A5-657 | **COMPUTED – conclusion overreaches** | `vb_pfaffian_item`: kernel=12, deg=6, terms=50, constant=-64, irreducible_factor_degrees=[[6,1]] over **ℚ**. Q order 1, G order 2 on lines through VB point. **Falsifier:** Irreducibility over ℚ ≠ irreducibility over ℚ(i) or ℝ. The Pfaffian uses all 9 pencil coordinates (units 3,4,9,10,11,12,13,14,16), not restricted to doubly pure (u,v). "No product of squared moduli of leading forms" does not follow from ℚ-irreducibility alone. |
| 5. Statement 15 (A5-665) | **COMPUTED – weakly worded** | 20 zero-compression units, 380 signed pairs: 200 nullity 0, 160 nullity 8, 20 nullity 4. The 20 nullity-4 lines have limit normals "0,0,-1" (10) and "0,0,1" (10) = ±e₃. Two curved arcs (params 1,2) have correct limiting normals matching cross(u₀,v₀)/|u₀|². **Falsifier:** Census uses s=3 specifically, not generic nullity for all 360 other lines. `sphere_normal` does least-squares + span check, NOT |n|=1 (line 588-589) – can accept off-sphere planes. |
| 6. Statement 11 (A5-662) – order 8 | **PROVED** | `path_item` computes order by repeated division (lines 223-228). All exceptional parameters have order 8 with positive cofactors (result.json confirms). |
| 7. `validate` has `require` per sentence; self-test controls fail for named reasons | **PROVED** | `validate()` (line 955) has explicit `require()` for statements 1–15 (lines 956-1034). `self_test()` (line 1061) has 8 mutants, each with `require()` and failure message (lines 1067-1103). All mutate an input and check it fails for the named reason. |
| 8. arXiv 2611.30652 prior art & P P' P = cos²(θ/2) P | **HYPOTHESIS – algebra not verified** | README lines 131-137 claims this follows from Clifford relations: P=(I+n·E)/2, E_k anticommuting involutions. P P' P = (I+n·E)(I+n'·E)(I+n·E)/8. Using anticommutation: (I+n·E)(I+n'·E) = I + n·E + n'·E + n·n' I + (n×n')·E. Explicit expansion needed to verify = cos²(θ/2) P. Stated without proof in record. |
| 9. `ci/gates.json` timing | **COMPUTED – tight on fewer threads** | `core-a5-nullity-transitions`: 120s (record takes 103s on 32 threads). `core-a5-nullity-transitions-self-test`: 20s (self-test 8s). Script uses `parallel.ordered_map` with `"workers": "all"`. On CI runners with fewer CPUs, wall time could exceed 120s. No repository rule broken, but gate assumes 32-thread host. |

---

### Cross-cutting findings

1. **Seed provenance**: `result.json` cites `qrng/2025-11-15-qrng.json` indices 0-39. `ci/seed_provenance.py` enforces ledger. The four QRNG draws seed the 36-sample census + 8 named points deterministically.

2. **Deterministic sampling bias**: `four_term_points` takes first sign pattern per index triple (1<a<b<c, 16∉triple). `SAMPLE_STEP=9` samples every 9th. This is **not a random sample** – it is a deterministic slice that may systematically miss kernel configurations with dim 1-3 in each half.

3. **Sphere normal check missing |n|=1**: `sphere_normal` (lines 579-592) solves `(I - 2 n nᵀ) ≈ P_I` by least squares on the 36 basis matrices, checks `span ok`, but never enforces `np.linalg.norm(n) == 1`. A plane with normal `c n` for `c ≠ 1` passes the span check.

4. **VB Pfaffian sign convention**: Lines 545-546 compute Pfaffian via alternating sum over subsets: `(-1)**len(subset) * det(...)`. Standard Pfaffian expansion has `(-1)^{k(k-1)/2}` for the principal submatrix of size 2k. The current `(-1)^k` may differ by a sign factor depending on subset composition.

5. **Parallel.py usage**: Script uses `parallel.ordered_map` for 36-item census (line 789) and 380-pair loops (line 912). `parallel.py` uses `ProcessPoolExecutor` with `"workers": "all"` → `os.cpu_count()`. On 32-thread host: 103s. On 8-thread CI runner: ~400s. Gate timeout 120s will fail.

---

### Residual risk

| Risk | Mitigation |
|------|------------|
| Kernel-split rule mechanism unexplained | Add algebraic proof: kernel split A+A → quaternionic commutant. |
| VB Pfaffian irreducibility over ℚ ≠ over ℂ/ℝ | Factor over ℚ(i) or ℝ; check if sextic = product of squared moduli of Q/G leading forms. |
| `sphere_normal` accepts non-unit normals | Add `require(abs(np.linalg.norm(n) - 1) < 1e-10, ...)` after line 589. |
| Gate timeout on small CI runners | Raise `core-a5-nullity-transitions` to 300s or reduce default workers in parallel.py for CI. |
| arXiv 2611.30652 claim unverified | Either prove the projector formula or label as hypothesis with falsifier. |

---

### Acceptance checks for merge

- [ ] Add `|n|=1` check to `sphere_normal`
- [ ] Factor VB Pfaffian over ℚ(i) and ℝ; update README claim or retract
- [ ] Raise gate timeout to 300s or make worker count configurable for CI
- [ ] Document kernel-split rule mechanism or label as empirical observation
- [ ] Verify arXiv 2611.30652 projector formula or mark as hypothesis
- [ ] All six `pr.yml` checks green on PR head

---

### Final assessment

The computational work is **solid and reproducible**. The code is clean, uses exact linear algebra, and the validation/self-test machinery is rigorous. The main gaps are **interpretive overreach** in the README (claims 2, 3, 4, 5, 8) and **one CI timing risk** (claim 9). No silent failures, swallowed exceptions, or mock leaks found. The `require`/`validate`/`self_test` pattern is a model for scientific code.

**Recommendation:** Merge after the five acceptance checks above are addressed.
