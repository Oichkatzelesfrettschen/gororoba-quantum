Reviewer: `codex exec`, model `gpt-daybreak-blue-latest`, reasoning effort high, read-only sandbox, codex-cli 0.171.0, 2026-11-23, on [pr-brief.md](pr-brief.md) at head `acdcda581`. Local paths are rewritten to repository-relative paths.

## Findings

1. **SERIOUS — confirmed:** the retained outputs support the verdicts, but the replay programs fail open. [bridge_verify.py] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/bridge_verify.py` 29), [tail-qi-nm.sing] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-pfaffian-schur-identity/tail-qi-nm.sing` 5), and [tail-p32009-nm.sing] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-pfaffian-schur-identity/tail-p32009-nm.sing` 7) print failure and control counts, then unconditionally print `EXIT 0`. Both shell drivers use `set -u`, omit `-e`, and merely record return codes. The arc script likewise prints every criterion without enforcing it. The smooth-conic control is recorded at [fiber_coefficients.py:187] (`docs/evidence/a5-exceptional-fibers/coefficient-structure/fiber_coefficients.py` 187) but excluded from the final predicate at line 208.
   **Principle:** a verdict tool passes known-good input and rejects known-bad input before its verdict counts.
   **Remedy:** assert every expected count and control value inside each checker, exit nonzero on deviation, and make the shell drivers `set -eu`. The current retained logs remain valid evidence because their values were inspected directly.

2. **SLOPPY — confirmed:** A5-577, A5-583 and A5-594 misuse the ledger’s `certified` status at [ledger.tsv:556] (`docs/evidence/a5-exceptional-fibers/ledger.tsv` 556), [ledger.tsv:562] (`docs/evidence/a5-exceptional-fibers/ledger.tsv` 562), and [ledger.tsv:573] (`docs/evidence/a5-exceptional-fibers/ledger.tsv` 573). The definition reserves `certified` for matching lower and upper bounds, while an exact computation belongs under `proved` ([ledger.py:55] (`docs/evidence/a5-exceptional-fibers/ledger.py` 55)). These rows contain exact digest equality, an explicit invertible map with mutual ideal containment, and exact ideal-membership checks.
   **Principle:** status vocabulary follows its declared semantics.
   **Remedy:** mark these three rows `proved`, or revise the global definition if “certified witness” is intended.

3. **SLOPPY — confirmed:** the maximal-torus reduction lacks its hypotheses at [slice_bridge.py:8] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/slice_bridge.py` 8) and [README.md:27] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-slice-equivalence-p32009/README.md` 27). Conjugating the two chosen tori over `F_32009` requires them to be split maximal tori of the relevant connected automorphism-group components and rationally conjugate. A six-dimensional abelian Lie-algebra centralizer with 21 split eigenlines alone does not establish those group-level conditions.
   **Principle:** a reduction theorem states every condition that makes the search exhaustive.
   **Remedy:** describe the torus route as a discovery heuristic, or establish the automorphism groups, split maximality and rational conjugacy. This gap does not affect A5-583’s existence verdict because the resulting map is independently verified.

4. **SLOPPY — confirmed:** A5-595’s basis says “twelve cells with Hilbert data,” and its README implies all three families were checked modulo 32009. The output contains eight Hilbert cells: six over Q(i), plus only W8→N− and E8-bar→N− modulo 32009 ([fiber-coefficients.json:2] (`docs/evidence/a5-exceptional-fibers/coefficient-structure/fiber-coefficients.json` 2), [README.md:9] (`docs/evidence/a5-exceptional-fibers/coefficient-structure/README.md` 9)).
   **Principle:** evidence scope equals the inputs actually consumed.
   **Remedy:** state “six Q(i) cells and two modular cells,” or import the successor modular records and rerun.

5. **SLOPPY — confirmed:** [coefficient-structure/README.md:56] (`docs/evidence/a5-exceptional-fibers/coefficient-structure/README.md` 56) says the character data “single out the nodal form.” The check excludes one smooth-conic character assignment; it does not prove uniqueness among graded algebras or representations.
   **Principle:** a control excludes only the tested alternative.
   **Remedy:** say “the nodal model matches while this smooth model fails.” A5-596 correctly remains `survives`.

6. **SLOPPY — confirmed:** the results table attributes the extra factor of generators 10 and 16 without a field qualifier at [a5-exceptional-fiber-status.md:82] (`docs/notes/topics/a5-exceptional-fiber-status.md` 82). A5-594 establishes that attribution only modulo 32009.
   **Remedy:** append “modulo 32009.”

7. **COSMETIC — confirmed:** `git diff --check` reports a new blank line at EOF in [review-codex.md:129] (`docs/archive/reviews/a5-fiber-status/review-codex.md` 129).

## SOUND

- **A5-583:** SOUND within its stated one-prime scope. The explicit matrices are invertible and both Singular logs report mutual reduction to zero. The identity and perturbed-map controls reject for the intended reasons. `stabilizer()`, discrete logarithms, Hermite solving and `transport()` are only discovery machinery; any false map they produce is caught by the independent ideal check. The README correctly disclaims uniqueness and identification with the geometric slice map.
- **A5-593:** `proved` is earned. Both signs check all 126 nonzero polynomial identities exactly over Q(i), and the exponent-two mutation fails all 126.
- **A5-595:** `proved` is earned for the corrected eight-cell input scope and the exact component-numerator identity.
- **A5-597:** `proved` is earned. `K2 ⊂ L` comes from the degree-two relation stage. Each parameter space is irreducible; rank four of `[dF,F]` gives a four-dimensional image closure inside a four-dimensional prime component. Covering both components gives `V(L)=V(K2)`, and radicality then yields `L=K2`. Both mutations leave `V(J)` and invalidate the limit equations.
- **A5-577:** the regenerated relation digests, selections, dimensions and multiplicities match. Its drop-one-line control detects the intended omission.
- The status totals, 33-incidence count, `14 + 8 + 4 = 26` real-limit breakdown, and completion table agree with the cited rows.
- Ledger validation, all retained SHA-256 manifests, Python syntax, Ruff lint/format, and the text scan passed. Tracked additions contain no local absolute path, address, private hostname or emoji.