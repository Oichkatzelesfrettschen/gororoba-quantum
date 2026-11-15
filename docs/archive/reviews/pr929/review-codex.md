# Review of PR 929

Reviewed head `75e830cdb8f141d0f10e96cab589a5093d1d859c`. The exact claims of A5-560 and the bounded-negative part of A5-561 survive. A5-559 overstates its global codimension result, and A5-561’s “every evaluation at the requested precision” mechanism is false despite the corrected calculation producing the retained verdict.

## Ranked findings

1. **SERIOUS — proved: A5-559 establishes fiberwise codimension, not codimension in the whole stratum.**

   nullity4_qg_plane_incidence.py:7 proves that each fixed kernel fiber is \(K\setminus J\), real dimension six, and that \(P(z)=P_j\) cuts a complex line, real dimension two. Line 14 then infers codimension four in \(S\).

   That implication needs a missing global lemma: the kernel map
   \[
   \kappa:S\to \operatorname{Gr}(3,15),\qquad z\mapsto K(z)
   \]
   must be regular with equidimensional image, and the exceptional planes must form constructible line subbundles, or finite-monodromy families, over dense subsets of every relevant component. A set can have codimension four in every occupied fiber yet have larger total codimension when it occurs only over a lower-dimensional base subset.

   The Jacobian code at nullity4_qg_plane_incidence.py:185 proves local codimension four at its witnesses, not this global bundle lemma. The review added nine deterministic witnesses at \(s=-2,3,4\); all reproduced the retained row:
   ```text
   [True, 12, 13, 11, 2, True, True, 4, 4, 4]
   ```
   This gives 15 exact local checks, still a finite sample.

   The defensible claim is: codimension four inside every fixed fiber, and local codimension four at the checked smooth points. ledger.tsv:537 should retain its former hypothesis until the kernel-map lemma lands; ledger.tsv:538 may state the fiberwise result.

2. **MEDIUM — computed: A5-561 does not pass the requested precision to every evaluation.**

   nullity4_real_polar_rational_charts.py:376 sets `ctx.prec` to 131 or 400, computes the exponential, then calls `ff._pairing_factors()`. On its first uncached call, nullity4_real_polar_fiber_four.py:283 resets the process-global context to 200 bits.

   Remote probe:
   ```text
   precision=131 after_first=200 after_second=131 equal=True
   precision=400 after_first=200 after_second=400 equal=True
   ```

   The serialized balls remain equal because the pairing factors are exact. A replay with the factors pre-cached, leaving all arithmetic at the requested precision, produced:
   ```text
   precision=131 ... corrected={'interior': True, 'contraction_bits': 13,
                                'pairing_bound_bits': 36} equal=True
   precision=400 ... corrected={'interior': True, 'contraction_bits': 13,
                                'pairing_bound_bits': 36} equal=True
   ```

   Thus the 131/400-bit outcome survives, but the producer docstring and A5-561 basis falsely describe the executed mechanism. Retrieve the factors before setting `ctx.prec`, or restore the requested precision immediately afterward, and add a cache-cold assertion on `ctx.prec`.

3. **LOW — computed: the \(G_2\)-membership mutant fails for four mechanisms and cannot protect membership by itself.**

   test_a5_nullity4_real_polar_rational_charts.py:63 plants a generator outside \(\mathfrak g_2\) and expects `family_structure()` to fail. The same mutation also breaks three unrelated predicates aggregated at nullity4_real_polar_rational_charts.py:285:
   ```text
   in_g2=[False, True, True, True] commute=False left=False right=True
   hermitian=False structure=False
   ```
   The test would remain green if the membership check disappeared. Test the `in_g2` predicate separately, or choose a mutant satisfying the other structural identities.

4. **LOW — proved: one independent symbolic loop remains serial.**

   nullity4_real_polar_rational_charts.py:152 computes 14 independent symbolic matrix-vector products in a list comprehension. AGENTS.md:47 requires every CPU-bound independent loop to route through `parallel.py`. The three outer stabilizer jobs are parallel, but this inner item loop does not follow the stated repository rule.

5. **LOW — proved: one failure diagnostic states the opposite relation.**

   nullity4_real_polar_rational_charts.py:143 accepts rank three for `[C(l), z_0]`, which proves \(z_0\in C(l)\), but its error says “`z_0 is outside C(l)`.” This affects diagnostics only.

## Claim dispositions

- **A5-559 — partly proved.** The fiber decomposition, Hermitian-line description, surjectivity \(K\to\mathbb C^2\), frame independence, and local Jacobian calculation are sound. The conjugate-linear slot is handled correctly by moving both arguments along \(iD_k\). Since \(Q=0\) gives \(G=-4\Delta\), gradient rank two plus a 13-dimensional contained span proves that span is the complex tangent space at each checked witness. The global codimension statement remains unproved.

- **A5-560 — proved.** The retained computation of \(q\in P_y\cap P_z\) is at nullity4_qg_orbit_types.py:401. Preservation and Hermitian orthogonality of \(E_+\) and \(E_-\) are checked at lines 217–262. These facts make the orthogonal-sum argument valid for every \(g\in G_2(\mathbb C)\), independently of unitarity. The tested unipotent adds a nonunitary regression only; it is not the universal proof. Rotation, scaling, and the orbit classification cover the remaining representatives.

- **A5-561 — proved as a bounded negative.** Lie-algebra membership and the minimal-polynomial identities make \(A_L,A_R\) the stated exponentials; only the rational-point equivariance is directly recomputed. On \(F=0\), the \(z_0\) row of \(R\) vanishes, so `rank R = rank N`. The exact minor makes rows \(c_2,c_3\) independent when \(S_R\ne0\); at \(S_R=0\), the incidence equations force the identity and \(R=0\). `_reduced` performs exact quotient-ring reduction, and the retained factored strings preserve their signs. The row correctly excludes only the enumerated root subgroups and two boost families.

- **A5-551/A5-555/A5-558 edits.** A5-551 drops no prior basis; its added precision outcome is correct, while its precision-control explanation is not. A5-555’s strengthening is supported by A5-560. A5-558’s promotion of global codimension four is the unresolved A5-559 gap.

- **Gate integrity.** Both new gates execute their producers directly, propagate failure status, replay retained text, and passed. No failed-process pass, void public certificate input, or two-pinned-constants tautology was found.

## Verification

On the specified remote checkout at the reviewed head:

```text
$ "$PYTHON" -B ci/run_gates.py --gates \
    core-a5-nullity4-qg-plane-incidence,\
core-a5-nullity4-real-polar-rational-charts
PASS core-a5-nullity4-qg-plane-incidence              2.0s
PASS core-a5-nullity4-real-polar-rational-charts      3.3s
2 passed, 0 skipped, 0 failed
```

```text
$ "$PYTHON" -B -m pytest -n 4 --dist loadgroup -p no:cacheprovider \
    tests/test_a5_nullity4_qg_plane_incidence.py \
    tests/test_a5_nullity4_real_polar_rational_charts.py
56 passed in 4.59s
```

```text
ruff check: All checks passed!
ruff format --check: 4 files already formatted
mypy: Success: no issues found in 4 source files
```

`git diff --check` produced no output. Both local and remote worktrees remained clean.

## New hypotheses

- **Hypothesis — mixed-root rational rank-one chart.** A six-real-parameter product of noncommuting rational nilpotent root subgroups has an incidence surface \(F=0\) on which `det N = 0`, `N != 0` is a proper closed divisor containing a rational point. This would give an exact algebraic A5-551 witness. The 24 incidence-preserving single-root groups all keep \(N=0\), while the two commuting boost families jump from rank zero to rank two, so rank one likely requires mixed noncommuting directions.

  **Falsifier:** exact saturation of the deterministic six-root chart,
  \[
  (F,\det N):\langle\text{entries of }N\rangle^\infty,
  \]
  has empty real locus, or its incidence quotient forces \(N=0\) or rank two.

  **Cheapest test and cost:** select directions by exact Jacobian pivots from the existing 182 candidates, compute the second-order incidence-reduced jet, then run one six-variable saturation only if the jet admits rank one. The existing 182-root tally is contained in the measured 3.3-second gate; the saturation cost is unmeasured and should receive a ten-minute cap.

- **Hypothesis — kernel-image bundle structure.** The kernel image is an irreducible complex ten-dimensional family, \(S\) is the open part of its rank-three tautological bundle, and the exceptional-plane families are line bundles up to finite monodromy over dense open subsets. Their closures would then have complex dimension eleven and real codimension four.

  **Falsifier:** the differential of the kernel/Plücker map has rank other than ten on an orbit component, or an additional kernel-image component lacks the corresponding exceptional line.

  **Cheapest test and cost:** compute the exact Plücker differential on the finite normal-form types \(s=0,\pm1,\infty\) and the \(D_1D_2\) roots, then prove the generic rank symbolically in \(s\). The nine extra rational-point incidence checks took 2.7 seconds; the global symbolic rank calculation is unmeasured and should receive a ten-minute cap.

**Verdict:** A5-560 and the bounded A5-561 result are sound. PR 929 should not treat global codimension four as proved until the kernel-map dimension lemma is supplied or the records are narrowed to the fiberwise and sampled-local statements.