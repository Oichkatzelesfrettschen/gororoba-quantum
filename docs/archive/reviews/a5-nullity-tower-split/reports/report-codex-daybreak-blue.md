**Ranked Findings**
1. **High — proved:** A5-657 remains open; the patch marks a broader claim refuted than the computation reaches. The claim existentially permits *an* invariant at VB and N±. The record factors only the VB Pfaffian and excludes the specific product `|Q₁|²|G₂|²`; it neither computes the N± Pfaffians nor excludes another strata invariant. Restore A5-657 to open, or narrow it to the rejected Q/G product. The overstatement propagates through `docs/evidence/a5-exceptional-fibers/ledger.tsv:636`, `docs/notes/topics/a5-exceptional-fiber-status.md:189`, and `docs/design/a5-nullity-transitions-program.md:52`.
2. **High — proved:** The A5-664 denominator is misstated. `four_term_points()` keeps only the first nullity-8 sign pattern for each support triple, then `sampled_structure()` takes every ninth retained representative (`scripts/a5_nullity_transitions.py:476`, `scripts/a5_nullity_transitions.py:483`, `scripts/a5_nullity_transitions.py:510`). The README and ledger call these “the 474 four-term points,” concealing both the sign-choice filter and stride bias (`docs/evidence/a5-nullity-transitions/README.md:104`, `docs/evidence/a5-exceptional-fibers/ledger.tsv:643`). A5-664 may remain `survives`, but its evidence must say “474 support representatives, one lexicographically first qualifying sign pattern per support; 53 stride-nine representatives tested.”
3. **High — proved:** The assertion that every sentence has a `require` is false (`docs/evidence/a5-nullity-transitions/README.md:27`, `docs/design/a5-nullity-transitions-program.md:74`). Missing guards include:
   - Exact cofactors `2^40`, `2^32`, and `2^52`; validation requires only positivity (`scripts/a5_nullity_transitions.py:1000`).
   - The N+ upper-half dimension and equality flag; validation copies only selected N− fields (`scripts/a5_nullity_transitions.py:1017`).
   - The statement that the XOR rule fails in both directions; `P15 == false` requires only one counterexample, and the self-test checks only the order-8/scalar direction (`scripts/a5_nullity_transitions.py:910`, `scripts/a5_nullity_transitions.py:1094`).
   - Gram `2 I` at VB; `frame_gram_scalar` tests diagonality, then returns the first diagonal entry without testing equality of all diagonal entries (`scripts/a5_nullity_transitions.py:570`).
4. **Medium — proved:** Statement 15 overstates 160 pair lines. The code evaluates every signed pair only at `s = 3` (`scripts/a5_nullity_transitions.py:615`). It computes a generic certificate only for the 20 lines reading nullity 4 there (`scripts/a5_nullity_transitions.py:622`). Therefore “160 give nullity 8” means “160 read nullity 8 at `s = 3`,” not generic nullity 8. Add that parameter to `docs/evidence/a5-nullity-transitions/README.md:115` and the claim text at `docs/evidence/a5-exceptional-fibers/ledger.tsv:644`.
5. **Medium — proved:** The producer violates the repository’s parallel-loop rule. Independent heavy loops remain serial in operator construction and Lie brackets (`scripts/a5_nullity_transitions.py:341`, `scripts/a5_nullity_transitions.py:368`), four-term support classification (`scripts/a5_nullity_transitions.py:480`), and the 380 pair ranks (`scripts/a5_nullity_transitions.py:615`). A top-level `"workers": "all"` cannot parallelize the single A6 `structure_item`. The gate values exist as claimed (`ci/gates.json:4894`, `ci/gates.json:4905`), but the 103-second wall measurement at `README.md:160` does not justify a `seconds` field governed by CPU seconds (`ci/AGENTS.md:460`). Measure user plus system time before accepting 120 and 20.
6. **Low — computed, guard incomplete:** The current retained N+ row does contain the claimed `(4,4,equal)` split (`docs/evidence/a5-nullity-transitions/result.json:2414`), and the VB frame likely is `2 I`; the defects above concern acceptance guards, not contradictory retained values.
7. **Low — source boundary:** The Clifford consequence in the prior-art paragraph is proved below. The exact Koebisu theorem remains supported only by the README’s “abstract read” transcription (`docs/evidence/a5-nullity-transitions/README.md:131`); this checkout holds no local primary-source note for arXiv 2611.30652. Treat that bibliographic clause as source-reported rather than independently verified.

**Kernel-Split Rule**
- **Proved mechanism:** Write `y=(a,b)` and a kernel vector as `(c,d)`. The doubling law gives
  `ac − conjugate(d)b = 0` and `da + b conjugate(c) = 0`.
  Hence
  `K∩(A₄⊕0) = {c : ac=0, b conjugate(c)=0}` and
  `K∩(0⊕A₄) = {d : da=0, conjugate(d)b=0}`.
  These are exactly the dimensions computed by `size-upper.rank()` and `size-lower.rank()` at `scripts/a5_nullity_transitions.py:343`. The equality test at lines 347–349 correctly compares the two coordinate subspaces under the canonical identification of the halves.
- **Hypothesis:** The split type means that the two halves possess one common four-dimensional annihilator plane; since the two intersections already total eight dimensions, `ker L_y=A⊕A`. A proof must then construct the quaternion action on `A⊕A` and prove that every nonsplit W8 graph has scalar centralizer. The current correlation does not supply either step.
- **Counterexample outside scope:** N± have the same `(4,4,equal)` split but scalar commutant and closure `so(16)` (`docs/evidence/a5-nullity-transitions/README.md:107`). This proves that the rule is neither definitional nor valid beyond W8.

The cheapest complete test that removes both sampling biases is the exhaustive 29,232-point signed-support census on the compute workstation:

```sh
cat >/tmp/a5_split_exhaustive.py <<'PY'
from itertools import combinations, product
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / "scripts"))
import a5_nullity_transitions as m

def main():
    points = [
        tuple(zip((1, *triple), (1, *signs), strict=True))
        for triple in combinations(range(2, m.DIMENSION), 3)
        if 16 not in triple
        for signs in product((1, -1), repeat=3)
    ]
    rows = m.parallel.ordered_map(m.sampled_item, points, 1)
    allowed = ([4, 4, True, 7, 4, 10], [0, 0, False, 7, 1, 28])
    bad = [row for row in rows if row["orbit"] == "W8" and row["type"] not in allowed]
    print(len(points), sum(row["orbit"] == "W8" for row in rows), len(bad))
    if bad:
        print(bad[0])
        raise SystemExit(1)

if __name__ == "__main__":
    main()
PY
export PYTHON="${PYTHON:-python3}"
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 \
GOROROBA_WORKERS=32 "$PYTHON" -B -W error /tmp/a5_split_exhaustive.py
```

Any printed `bad` row refutes A5-664. A clean census strengthens only this finite four-term family; it does not prove the universal W8 claim.

**Sound Claims**
- **Claim 1 — proved from source; values computed:** `structure_item` correctly handles a nonorthogonal frame through `G⁻¹KᵀL_wK`; its commutant, trace-form test, Lie closure, intersection dimensions, and equality test are mathematically sound (`scripts/a5_nullity_transitions.py:323`).
- **Claim 2 — computed and bounded:** The recorded dimensions 3, 10, 36 plus quaternion commutants identify the closures with `sp(1)`, `sp(2)`, `sp(4)`, because each closure lies inside the full quaternion-linear skew algebra of the same dimension. They establish three levels only.
- **Claim 4 — proved narrowly:** The subset recurrence has the standard Pfaffian signs (`scripts/a5_nullity_transitions.py:540`). A product `|Q₁|²|G₂|²` has two nonconstant rational factors, so an irreducible rational sextic cannot equal it. Absolute irreducibility is unnecessary for this narrow exclusion.
- **Claim 5 — computed with the wording correction above:** The 20 generic-nullity-4 lines and two curved arcs have the recorded unit normals. Exact projector and Clifford identities also force any represented normal to have norm one, so the missing explicit norm check does not invalidate these 22 cases.
- **Claim 6 — proved from source:** Repeated exact division in `path_item` counts multiplicity correctly (`scripts/a5_nullity_transitions.py:223`). The retained cofactors match `2^40`, `2^32`, and `2^52`; validation needs exact guards.
- **Claim 7 — partly false:** All eight self-test controls are nonvacuous for their stated local mutation. Validation coverage of every README sentence is false.
- **Claim 8 — proved algebraically:** For `E(n)=n·E`, `P(n)=(I+E(n))/2`, and `n·n'=cos θ`, the Clifford relation gives `P(n)E(n')P(n)=cos θ P(n)`. Therefore `P(n)P(n')P(n)=(1+cos θ)P(n)/2=cos²(θ/2)P(n)`. All four principal cosines equal `cos(θ/2)`.
- **Claim 9 — configuration computed, cost unverified:** The gate fields are correct. Run `"$PYTHON" -B ci/run_gates.py --gates core-a5-nullity-transitions,core-a5-nullity-transitions-self-test --timings /tmp/a5-gates.json`; user plus system time exceeding 120 or 20 seconds refutes the estimates.

**New Conjectures**
- **Hypothesis:** Quaternionic W8 points are exactly those whose two A4 halves share one four-dimensional annihilator plane. Falsifier: a split kernel whose half operands lack that common plane. Cheapest test: add both half-annihilator intersections to the 44 recorded rows.
- **Hypothesis:** The scalar-centralizer type is generic on real W8, while the quaternionic split type is a proper algebraic sublocus. Falsifier: a dominant real parametrization whose generic point splits. Cheapest test: evaluate the half-projection minors on a rational parametrization of W8.
- **Hypothesis:** The 160 signed pair directions reading nullity 8 at `s=3` are constant W8 lines. Falsifier: any one reads nullity 0 or 4 at another rational parameter. Cheapest test: exact ranks at `s=1,2,4` before computing characteristic polynomials.

`git diff --check origin/main...HEAD` passed. Tests and record replays were not run, as the brief prohibited computation.
