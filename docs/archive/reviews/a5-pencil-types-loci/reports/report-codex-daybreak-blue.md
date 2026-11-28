No mathematical claim is refuted. The PR needs provenance, validation-contract, ledger-classification, and gate corrections before merge.

**Ranked Findings**
- **High — The PR body overstates pre-registration.** Its mechanism section says every claim was predicted before its run. `docs/evidence/a5-nullity-transitions/README.md:287` states P31 was written after six of its first eight nullities were read; the PR residual-risk section admits the same. `fourth-round-predictions.md` and the completed record also first enter Git together in `f917aa07b`, so Git history supplies no independent pre-run timestamp. Replace the blanket sentence with the exact per-prediction chronology.
- **Medium — The ledger collapses distinct evidence classes into `proved`.** `docs/evidence/a5-exceptional-fibers/ledger.tsv:650` marks the Pfaffian factorization proved rather than computed; line 651 does the same for the finite census; line 653 combines a proved real-locus argument with a computed line census; line 654 marks computed Schur membership plus a prose derivation proved. Preserve `computed`, `proved`, and mixed evidence explicitly.
- **Medium — Two ledger rows omit real falsifiers.** `ledger.tsv:650` gives A5-676 the falsifier `none`, although a nontrivial factor falsifies it. `ledger.tsv:654` says none exists through order three, although any Schur term outside the pencil or a failed order-three reduction falsifies A5-680. A5-679’s falsifier also covers only the sampled unit-sum clause, not the real-locus proof or pseudoinverse convention.
- **Medium — The README’s validation promise is false.** `docs/evidence/a5-nullity-transitions/README.md:34` says every statement has a `require`. The validator does not require VB’s `e_16` coordinate (`scripts/a5_pencil_types_and_loci.py:486` versus the N± check at line 492), the exact 3,005 dim-zero count and type tallies (`:498`), the exact seven-alpha key set (`:510`), or the reported Singular exponents (`:525`, which checks only positivity).
- **Medium — Statement 20 lacks route and sampling controls.** `type_item` silently substitutes the SymPy implementation after the integer-bound `ValueError` at `scripts/a5_pencil_types_and_loci.py:143`. No retained control compares the two implementations on shared inputs. The dim-zero spread checks at lines 499–500 constrain index counts, but cannot detect a hidden support or orbit family.
- **Medium — The reviewed gate lacks its Singular prerequisite.** At `f917aa07b`, `ci/gates.json:4939` invokes Singular indirectly but omits `"requires": ["singular"]`. The repository’s hosted workflow explicitly leaves record gates on demand at `.github/workflows/pr.yml:5`. A concurrent uncommitted edit now adds the missing prerequisite, but it is outside the reviewed head.
- **Low — README prediction text contradicts itself.** `docs/evidence/a5-nullity-transitions/README.md:285` says P28 held, while line 291 says P25—the same census type claim—is not run.
- **Low — Two mutation controls are weaker than their labels.** The “type-R point” control at `scripts/a5_pencil_types_and_loci.py:602` only requires “not H,” so C, unresolved, or `other` would pass. The off-plane control at lines 590–595 accepts any `None`, including a rank failure unrelated to plane recovery.
- **Low — Independent serial work remains.** The sub-Pfaffian loops at `scripts/a5_pencil_types_and_loci.py:264` and `:307` are parallel candidates. `w8_schur` serializes the three independent kind batches at line 428, limiting each phase to eight workers. The 133-second replay remains dominated by the already-parallel type census.
- **Low — The self-test timing estimate is host-dependent and low here.** `ci/gates.json:4950` records 20 seconds. `ci/run_gates.py --max-seconds 20 --gates core-a5-pencil-types-and-loci-self-test` selected it and measured 27.2 seconds on `the compute workstation`. The field controls gate selection rather than enforcing a timeout.

**Claim Verdicts**
- **1 — Computed, confirmed.** The full replay returned `record matches its recomputation`; elapsed 133.21 seconds. The record contains one degree-6 factor at VB and one degree-8 factor at each N±. A validator requirement for VB’s `e_16` membership remains missing.
- **2 — Computed, confirmed within the declared finite census.** The retained counts are 177 R, 3,282 C, and 139 H. An independent probe compared the bounds and SymPy routes on three shared points of each dimension; all nine matched. The first fallback reported the intended integer-bound failure and SymPy result `(commutant, closure) = (1, 28)`. The 33 fallback-only points still lack an independent second route.
- **3 — Computed, confirmed at seven α.** Biss–Dugger–Isaksen Theorem 14.6 and its proof on pages 23–25 give exactly `a=(t,kt)`, `b=(αt,(αk)t)`. The replay validates the split and `J_k` commutation at all retained α. This is not a uniform proof in α.
- **4 — Proved for the real rank locus; computed for the 284-line census.** Singular radical membership and the two sum-of-squares sub-Pfaffians establish the real plane and rank four off the origin. An independent SymPy block decomposition confirmed all four Penrose identities, equality of the pseudoinverse and range-block inverse, and the second-order formula. A supplementary probe evaluated all 284 directions at nine nonzero parameters from −5 through 5; it found the same `100/88/96` tally and zero parameter deviations.
- **5 — Computed plus derivation, confirmed through effective order three.** An independent block-Schur expansion constructed a deterministic zero-space direction, cancelled its order-two form with a pencil element, and returned `order2_zero=True`, `order3_formula_equal=True`, and `order3_in_pencil=True`. The `c1` and `c2` corrections contribute `F2 c1` and `F1 c2`; both vanish in the effective-order-three case.
- **6 — Falsified as written.** The record values reproduce, but the README, ledger, validator, and PR body do not state and enforce exactly the same scope and evidence class.

**PR Form**
- The three commit subjects and PR title follow `component: mechanism`; they contain no attribution trailer.
- The PR body has the required mechanism, validation, evidence, and residual-risk sections.
- The body abbreviates commands to flags rather than giving every exact invocation.
- The body says hosted checks are unread, while the PR page shows 10/10 checks green.
- The PR remains draft with zero conversation comments and no reviews. No comment-style violations exist yet.

**Structural Hypothesis**
- **Hypothesis:** At `e_1+e_10`, the block decomposition `R^32 = K ⊕ K⊥` forms an `Sp(2) × Sp(1)`-equivariant Jordan pair. The seven-dimensional pencil `V = im(KᵀL_(·)K)` is the unique target summand, while the 24-dimensional zero space `Z` supplies the complementary block. Equivariance forces the quadratic map `Z⊙Z → V` and its polarized triple composition back into `V`.
- **Falsifier:** One stabilizer generator violates equivariance of the quadratic tensor, the relevant representation contains another target summand, or one degree-four Schur coefficient leaves `V`.
- **Cheapest test:** Export the exact coefficient tensor of the 300 quadratic terms. Compute the induced action of the ten `sp(2)` generators and three quaternion-commutant generators on `Z` and `V`. Check the equivariance identity on every basis pair. This test separates a genuine Jordan/representation mechanism from an accidental degree-three closure.

**Validation Record**
- Full replay: pass, 133.21 seconds, 194,816 KiB peak.
- Self-tests: pass, five controls in 12.81 seconds; optimized mode passes in 15.39 seconds.
- Targeted pytest: `4 passed in 0.57s`.
- Route comparison: nine of nine shared points agree; first fallback matches the documented bound.
- Block-Schur probe: every pseudoinverse and order-three identity passes.
- Lint and mypy: not run on `the compute workstation`; `ci/pinned_tool.py` reports Ruff and `uv` absent.
- Tree boundary: the target was clean at review start. Concurrent edits later modified `ci/gates.json` and `docs/design/a5-nullity-transitions-program.md`; this report remains anchored to committed `f917aa07b`. Browser tooling also emitted its standard snapshot and console files under the existing workspace `.playwright-mcp/` directory.

