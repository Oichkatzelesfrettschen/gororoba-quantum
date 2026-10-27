# A_5 kernel bundles at nullity eight: critical review of the evidence record

Target: `docs/evidence/a5-kernel-bundles-nullity8/README.md` and `ledger.md` on branch
`geometry/a5-kernel-bundles-nullity8` at `b5f9c71`. The review reads them against the nine producers in that
directory, their retained results, `docs/design/a5-kernel-bundles-nullity8-program.md`, and the prior record
`docs/evidence/a5-kernel-bundles/README.md` with its review `docs/archive/reviews/2026-10-26-a5-kernel-bundles-critical.md`.

## Phase 0: artifact, field and visibility

The artifact is a mathematics record. Its subjects are the compact-orbit geometry of the five nullity-eight orbits
`W8`, E8-bar, `Iso`, `X_+` and `X_-`, the homotopy theory of homogeneous spaces (the Mostow fibration and cellular and
Kunneth computations), and the K-theory of rank-four complex bundles. Every proof is paired with an exact-arithmetic
Python producer. The rubric is the proofs/formal row of the review skill, with the repository's grounding rules. No
proof assistant certifies this record, so the written arguments carry the proofs.

The review read the whole README and ledger and the whole of `kernel_bundle_classes.py`,
`unit_section_topology.py` and `kernel_transition_atlas.py`. It also read the path construction, limit, comparison
and canonical-certificate sections of `boundary_specializations.py`, the classification core of
`stabilizer_strata.py`, and the pooling and pass-flag sections of the other producers. The Lie-algebra solves,
Casimir decompositions and invariant differentials were replayed rather than re-derived.

Deterministic layer, run with the pinned tools:
- Ruff check and format over the directory: clean.
- mypy over the nine producers: clean.
- `git diff --check origin/main...HEAD`: clean.

Replay, with `GOROROBA_WORKERS=4` on the shared build host: every `--check` reproduced its retained result byte for
byte, and every `--self-test` passed in normal and `-O` Python. Wall times in seconds:

| Producer | `--check` | `--self-test` |
| --- | ---: | ---: |
| `compact_orbit_ranks.py` | 3.1 | 4.9 |
| `w8_orbit_moduli.py` | 2.6 | 2.0 |
| `remaining_orbit_moduli.py` | 1.9 | 4.7 |
| `stabilizer_fiber_samples.py` | 4.1 | 10.2 |
| `stabilizer_strata.py` | 3.0 | 3.2 |
| `boundary_specializations.py` | 7.3 | 7.3 |
| `unit_section_topology.py` | 4.4 | 4.5 |
| `kernel_transition_atlas.py` | 7.6 | 7.6 |
| `kernel_bundle_classes.py` | 0.7 | 0.7 |

Every check and self-test runs within the 15 s `pr.yml` gate budget. No producer invokes Singular; the computer
algebra is sympy, `DomainMatrix`, python-flint and `Fraction`.

## Independent checks run for this review

- **Extra stabilizer component on `W8` (exact algebra).** The compact boost generator in
  `_compact_boost_tangent` is `X(u,v)=(i v, i u)`, so `X^2=-I` and the boost at angle `pi` is `-I` on `(u,v)`. The
  phase at angle `pi` multiplies `z` by `-1`. The `W8` representative has `mu=0`, so the element
  `gamma = (1, boost(pi), phase(pi))` fixes it. `unit-section-topology-result.json` records the `W8` compact
  stabilizer projection rows `[[0,0],[0,0],[0,0],[0,-1]]` in (phase, boost) order. The identity component therefore
  projects onto the boost circle `{(s,1)}`. `gamma` projects to `(-1,-1)`, outside that circle, so `gamma` lies in a
  second component of the full stabilizer. The same element lies in the identity component on `X_+` and `X_-`, whose
  stabilizer circle passes through `(-1,-1)`, and on `Iso`, whose identity component projects onto the whole torus
  and whose compensating `G_2` element is unique. E8-bar has `mu != 0`, so `gamma` does not fix it.
- **Canonical `X_+-` to `B9` limits under stress.** The record's evidence for these two canonical inclusions is two
  approach lines. The review computed the limit planes of three further approach families with the producer's own
  `_kernel_limit` and `_boundary_frame_data`:
  - first-order velocities `d + w` and `d + i w`, with `d` the recorded normal velocity and `w` each of the 16 `H`
    tangents at the `B9` point, plus the scalar multiples `i d`, `(1+i) d` and `-d`;
  - the ten square-zero `G_2(C)` unipotent images `exp(tN)(p + t d)`;
  - 57 tangential second-order approaches `exp(tN)(p + t^2 d)`, one for each nonzero `N p` among the 60
    nilpotent derivations, plus the boost.
  Every approach on both branches gives the recorded plane: 35 of 35 first-order, 10 of 10 unipotent and 57 of 57
  tangential. These families are not independent evidence. They confirm the constant-rank lemma (SLOPPY 3), which
  forces them: orbit directions add nothing to the restricted form at first order, and the tangential paths reduce
  to `F^T A(d) F` at second order. The decisive check concerns complex multiples of the normal direction. The
  restricted forms satisfy `F^T A(i d) F = i F^T A(d) F` exactly on both branches. The ratio is `i` at every nonzero
  entry, and no entry is zero in one form and nonzero in the other. So `F^T A(s d) F = s F^T A(d) F` is nonzero, with
  the same kernel, for every complex `s != 0`, and no normal direction drops to second order.
- **Same boundary point.** For every incidence, all approaches share one boundary coefficient `c_0`; each
  incidence has exactly one distinct boundary point. The unequal pairs intersect in dimension 2 or 3.
- **Skewness.** `A(z, conjugate(z))` is exactly skew at all five representatives, at `B9`, and at a unipotent-moved
  and a boosted `W8` point. The principal-Pfaffian charts and the skew effective forms are therefore well posed.
- **Serial-loop costs**, timed alone with `GOROROBA_WORKERS=4` (see SLOPPY 7).

## Findings, worst first

### SERIOUS 1: the `W8` compact stabilizer is disconnected, contrary to the README

**Barb.** The README says "the ordered frame and external torus element determine the compensating `G_2`
element, so no additional finite stabilizer component remains". On `W8` a second component exists, and it acts
trivially on every point with `mu=0`.

**Grounding.**
- The element `gamma` of the first independent check fixes the `W8` representative and lies outside the identity
  component.
- Composing `gamma` with the identity-component element over `boost(pi)` gives `gamma' = (h', 1, phase(pi))`. Here
  `h'` is `-1` on the real two-plane of the frame, a rotation by `pi` inside the quaternion subalgebra. The README's
  own completeness theorem also forces `h'` to exist: negation fixes the Gram matrix of a rank-two frame, and every
  three- and four-form value vanishes there.
- The sentence quoted in the barb proves only that the fiber over each external element is a coset. It never shows
  that the image of the full stabilizer in the external torus is connected; for `W8` that image is
  `{(s, +-1)}`.

Consequences:
- The true core is `(V_2(R^7) x S^1)/(Z/2)`, with the involution `(g SU(2), theta) -> (g h', theta + pi)`.
- The README sentence "Thus the phase circle supplies the remaining circle on `W8` and each `X` branch" is false for
  `W8`: the full phase loop is twice the generator of `pi_1` of the core.
- The ledger's item-4 row files "The external projections leave the phase circle on `W8`" as **Observed**. Only the
  Lie-algebra projection was computed, and the group statement drawn from it is wrong.
- `kernel_bundle_classes.py` checks `W8_phase_is_remaining_circle` from the Lie-algebra row alone, so no pass flag
  can see the component.

The conclusions survive by an argument the record does not contain.
- Choose `h'` in the centralizer `Sp(1)'` of the `SU(2)`, and join it to the identity by `exp(tY)` inside
  `Sp(1)'`.
- The map `(g SU(2), t) -> [g exp(tY) phase(t)]` for `0 <= t <= pi` is well defined and closes up at `t = pi`. It
  identifies the core with a mapping torus of `V_2(R^7)` under the identity.
- The bundle is then the mapping torus of the constant fiber automorphism `1 (x) m` of `xi (x) C^2`, where
  `m in GL(2,C)` is the action of `gamma'` on the multiplicity space. `GL(2,C)` is connected, so the bundle is
  `pr^*(2 xi)`.
- The homotopy type `V_2(R^7) x S^1`, `pi_1 = Z`, the reduced K-class `(0,0)` and the ordinary class `2 xi` all
  stand.

The component group of the full stabilizer is never computed on any orbit:
- `X_+-` and `Iso` close by the one-line arguments in the first independent check.
- On E8-bar, the phase is forced to 1 by the weight-one coordinate `mu`, and `boost(pi)` composed with any `G_2`
  element is excluded, because it would reverse the nonzero associative three-form value.
- Other finite boost elements `boost(theta)` on E8-bar are not examined, so the product `V_2(R^7) x T^2` rests on an
  unchecked absence.

The severity is SERIOUS, not FATAL, because every stated bundle class survives. The record nonetheless contains a
false structural sentence, and its pass flags could not have caught it.

**Remedy.**
- For each orbit, compute the image of the full compact stabilizer in the external torus at its finite-order points.
  At minimum, test `(boost(theta), phase(phi))` for `theta, phi` in `{0, pi/2, pi, 3pi/2}` against the complete
  invariants of the moved frame.
- Record `pi_0(L)`.
- Replace the quoted sentence with the `W8` mapping-torus argument above, and relabel the ledger's external-circle
  clause as **Inferred**.

### SERIOUS 2: no gate runs any of the nine replays

**Barb.** Every producer has a byte-exact `--check`, and nothing ever calls it.

**Grounding.** `git diff origin/main...HEAD` leaves `ci/gates.json` untouched, and no `tests/` file names the
directory. The prior record's producers are registered gates (`ci/gates.json`, from line 4558). AGENTS.md makes the
`sources` suite of `ci/gates.json` the owner of "the evidence replays and their checksum ledgers".

`kernel_bundle_classes.py` binds seven upstream script and result digests. A later edit to
`stabilizer_fiber_samples.py` or `nullity_sixteen_bundle.py` would make it raise "is stale". Neither `pr.yml` nor
the nightly audit would notice, because neither runs it.

The README sentence this concerns is "Each producer carries a byte-exact `--check` and mutation-bearing
`--self-test`." It is true of the scripts and empty in CI. Gate registration belongs to the orchestrator's merge
step under the program file, so this is a merge blocker, not a defect in the mathematics.

**Remedy.** Register a `--check` and a normal-plus-`-O` `--self-test` gate for each producer, with their `inputs`
lists, before merge. Every one fits the 15 s budget (table above). The fiber-sample self-test, at 10.2 s, has the
least margin.

### SLOPPY 3: the canonical `X_+-` to `B9` inclusion is argued through a group action that has no lift

**Barb.** The canonicity argument moves the kernel along "group curves tending to the identity". The program file
itself records that the split boost has no constant lift, and the noncompact `G_2(C)` directions have none either.

**Grounding.** README: "**Inferred:** the inclusion is canonical because the committed reduced transverse germ is a
smooth one-dimensional normal line, rescaling its nonzero normal parameter leaves the restricted-matrix kernel
unchanged, changes along the orbit arise from group curves tending to the identity, and the full three-dimensional
constant-lift stabilizer of the boundary point preserves the limiting plane."

- A kernel map that is discontinuous at `p` is not controlled by `g -> e` unless `g` acts linearly on kernels.
- Stabilizer invariance is necessary for canonicity, not sufficient.
- The recorded evidence is two approaches, and approaches tangent to `B9` with a second-order normal component are
  not covered.

The conclusion survives, by the argument below and the complex-multiple check of the second independent check.

The correct argument is short.
- If `A(t)` has constant rank along a curve in the boundary orbit, then `F^T A'(0) F = 0` on the kernel. First-order
  limits therefore depend only on the normal component of the velocity.
- The normal space is one complex line. Write `R(v) = F^T A(v) F`. Sharing a kernel between `R(n)` and `R(i n)` is
  not enough. On the two-dimensional quotient, `R(i n) = lambda R(n)`, and a real `lambda` would make
  `R((-lambda + i) n) = 0`, so that direction would drop to second order. Here `lambda = i` exactly, so
  `R(s n) = s R(n)` is nonzero for every complex `s != 0`.
- A tangential approach `h(t)(p + t^2 n)` has effective second-order form `R(n)`, because the orbit curve contributes
  nothing at constant rank. The 57 tangential probes confirm this.

**Remedy.**
- State the constant-rank lemma and the check `R(i n) = i R(n)`.
- Make the producer compute that ratio and fail when it is real.
- Drop the group-curve sentence.

### SLOPPY 4: path dependence is established; the attaching data item 6 needs is not

**Barb.** Two unequal limits refute a canonical inclusion. They do not describe the set of limits, and that set is
what an attaching map is made of.

**Grounding.**
- The thirteen path-dependence results are genuine: same boundary point, same boundary kernel, exact planes meeting
  in dimension 2 or 3 (SOUND below).
- The program file, section 2 (N3) and deliverable 2, asks for "every boundary restriction into the adjacent
  nullity-12 pieces" as "the attaching data for item 6".
- The record delivers 33 sampled limits and the path-stabilizer representations on them.
- The README says the E8-bar sheet equality "supplies local attaching data", but the limit set inside
  `Gr(4, K_0)` is not computed for any incidence. That set is the fiber of the closure of the graph of the Gauss map
  over the boundary point.

By the constant-rank lemma of SLOPPY 3, first-order limits factor through the projectivized normal space of each
transverse germ. The regularity record already lists those germs (Theorems 3 and 6), so the first-order part of
every attaching map is a finite computation. Item 6 cannot start from "path-dependent" alone.

**Remedy.** For each incidence, map the projectivized normal cone of the committed transverse germ to `Gr(4, K_0)`
through `ker(F^T A(n) F)`. Record the image's dimension and its stabilizer orbits, and flag the incidences where
tangential second-order approaches add limits.

### SLOPPY 5: the bundle-class section states inferred results without the label, and one real-bundle equality without a reason

**Barb.** The README presents the bundle-class table, "Each bundle has total Chern class one" and
"`R^4+xi_R=R^8`" as plain statements. In the producer these are string literals.

**Grounding.**
- The program file, section 5, requires that "every number a README states is either computed and compared by the
  producing script or labeled as an argument".
- `kernel_bundle_classes.py` computes the doublet multiplicities from the bound fiber rows, the residue
  `doublets % generator_order`, the phase square and the external projections. That is a real improvement on the
  prior record's SERIOUS 1.
- Still literal:
  - the free K-coordinates `[0]` and `[0,0,0]`;
  - the entire `Iso` row (`"reduced_K0": "Z"`, class `[0]`);
  - the reduced-group strings;
  - `real_bundle = "R^4 + xi_R = R^8"`, selected by the pair (2 lines, 1 doublet);
  - `_zero_characteristic_classes`.
- The JSON labels these as written arguments (`inference_scope`), and the ledger's item-4 row says
  **Inferred**. The README section "The order-two Stiefel class occurs on E8-bar and both `X` branches" carries no
  **Inferred** label.
- `R^4 + xi_R = R^8` is true, but not by cancellation: real stable-range cancellation needs rank at least the
  dimension, and `8 < 12` and `8 < 13`. The reason is an explicit frame:
  `xi_R + span(x_1, x_2, x_1 x_2) = R^7`, because `xi_R` is the orthogonal complement of the associative
  three-plane. The README gives no reason at all.
- The `remove_e8_path_dependence` mutation flips the bound boolean and detects the flip by counting that same
  boolean. It proves that the certificate reads the field, not that any geometry changed.

**Remedy.**
- Label the class table and the characteristic-class paragraph **Inferred**.
- Add the frame argument for `xi_R + R^3 = R^7`.
- Either derive the `Iso` and free coordinates from the bound topology rows, or say in the README that the JSON
  restates them.

### SLOPPY 6: the X-branch class uses the fiber at a point the record itself calls non-adapted

**Barb.** `_representation_counts` reads the `X_+-` representations at the recorded representatives. The topology
section calls those points not Mostow-adapted, and they are not core points.

**Grounding.**
- The class argument needs the `SU(2)` representation at a core point. The README's own strata table supplies it:
  associative rank three gives `2 V_0 + V_1`.
- The table holds at every point of the stratum only if the representation is constant along a connected stratum.
- Neither the connectedness of the associative-rank-three locus nor the constancy is argued; the prior record argued
  constancy explicitly.
- The nontriviality conclusion does not depend on this step (SOUND below). The ordinary-class identification does.

**Remedy.** Add the constancy argument for each stratum (integer multiplicities on a constant-rank kernel along a
connected locus), and prove the stratum connected or treat its components separately.

### SLOPPY 7: serial loops over independent items outside `parallel.ordered_map`

**Barb.** The program file, section 5, puts "mutation builds" and "comprehensions that build work" through the
pool. Four producers keep one serial step each, in the same `build_record` that pools the rest.

**Grounding.** Times were measured alone with `GOROROBA_WORKERS=4`.
- `boundary_specializations.py`, `build_record`: `incidence_rows = [_incidence_row(...) for incidence in
  sorted(by_incidence)]` runs serially over 15 independent incidences (0.47 s). `_path_mutation_control` and
  `_schur_mutation_control` are two independent mutation builds, called one after the other outside the pool
  (0.21 s).
- `kernel_transition_atlas.py`, `build_record`: the baseline `transition_atlas_checks()` runs before, and outside,
  the pool that maps the three mutations. It costs 1.77 s of the 7.6 s check.
- `unit_section_topology.py`, `build_record`: the baseline `_core_record("")` runs outside the two-mutation pool
  (0.81 s). Each `_compact_stabilizer_row("Iso", ...)` also recomputes the coassociative enumeration in every core
  record. That is duplicate work, not a serial loop.
- `stabilizer_strata.py`, `build_record`: the `W8` canonical point `_analyze_canonical_point(...)` runs serially
  before the pooled `Iso` canonical rows (0.92 s).
- `kernel_bundle_classes.py`, `build_record`: the baseline `class_checks()` runs outside the four-mutation pool
  (0.01 s, negligible).

`compact_orbit_ranks.py`, `w8_orbit_moduli.py`, `remaining_orbit_moduli.py`, `stabilizer_fiber_samples.py` and
`stabilizer_strata.py` pool the baseline together with their mutations, so the convention exists in the same
directory. The per-fixture inner loops run inside pooled workers and qualify for no finding. No check is near the
budget, so the cost is small. The rule has no cost threshold.

**Remedy.** Map the baseline with the mutations in one `ordered_map` call, as the first five producers do. Pool the
incidence rows and the two boundary mutation controls, and add the `W8` canonical point to the `Iso` task list.

### SLOPPY 8: the homotopy and `G_2` inputs are cited loosely or not registered

**Barb.** The Mostow step carries one 1955 citation, for a stabilizer with a unipotent radical of dimension 2 or 3.
The standard `G_2` isotropy facts behind the strata and the completeness proofs carry none.

**Grounding.**
- I believe the general non-reductive form of the covariant-fibering theorem is in Mostow's sequel ("Covariant
  fiberings of Klein spaces II", *Amer. J. Math.* 84, 1962) rather than the 1955 paper. Verify the 1955
  hypotheses before keeping the citation; confidence is about 60%.
- The standard route avoids the question. Write `S = L_C` semidirect `U`. Then `H/L_C -> H/S` has contractible
  fibers `U`, and Mostow for the reductive pair `(H, L_C)` gives `K/L`. That route also needs `pi_0(L)`, which
  SERIOUS 1 shows is not trivial.
- The facts that `G_2` is transitive on orthonormal two-frames, that `SU(2)` is transitive on the unit sphere of the
  quaternionic complement, and the list of pointwise stabilizers are all used without a source.
- No reference is registered in `docs/SOURCES.json`. The prior review's SLOPPY 5 and 6 asked for exactly this.

**Remedy.** Register Mostow, Hodgkin, Mimura-Toda and a `G_2` geometry source (for example Harvey-Lawson,
"Calibrated geometries", *Acta Math.* 148, 1982, chapter IV; verify the chapter). Cite them at the point of use.

### COSMETIC 9

- The introduction still says "Transition data and bundle classes remain open", and its producer list names three
  of the nine scripts.
- The replay timings are stale. The README gives 7.84 s for the compact-rank check, measured here at 3.1 s, and
  9.19 s for the fiber samples, measured at 4.1 s.
- "All 45 ordered double-overlap matrices" counts the 15 identity matrices `g_II`; 30 are genuine overlaps. The
  same applies to the 135 triple identities.
- In `unit_section_topology.py`, `_compact_stabilizer_row` contains `elif mutation != "delete_boost": raise`, which
  repeats the `if` condition and can never run, so an unknown mutation name is silently ignored there.
- "Persists on an open neighborhood. Therefore ... generic": genericity needs the zero set of a nonzero real-analytic
  minor on the connected unit section to be nowhere dense. That one sentence is missing.

## SOUND

- **Path dependence is established.** Each of the thirteen incidences has two exact approaches with the same boundary
  coefficient and the same six-dimensional boundary kernel, and their limit planes meet in dimension 2 or 3. The
  curves are certified inside the closure by polynomial vanishing at one parameter beyond the degree bound. The
  degenerate second-order case uses the correct Schur form `D_2 + C_1^T B_0^-1 C_1`, which the review rederived:
  `F^T A_1 E = -(E^T A_1 F)^T` for skew `A_1`. Formal first-order lift solvability is verified. The Schur-deletion
  mutation changes the effective rank from two to six.
- **The order-two class on E8-bar and `X_+-` is robust.** The restriction to a `V_2(R^7)` factor is well defined.
  It is the pullback along the `G_2`-orbit `G_2/SU(2) -> orbit` through any associative-rank-three point, and that
  pullback is `G_2 x_SU(2) F = C^2 + xi`. The bundle is `G_2`-equivariant through the constant lift.
  - On `V_2(R^7) x S^1` and `V_2(R^7) x T^2`, the projection splits the fiber inclusion, so `x != 0` on the factor
    forces a nonzero class.
  - The detection uses neither Mostow, nor the boost, nor the core identification, so SERIOUS 1 cannot reach it.
  - The torsion coordinates `(x,0)` on `V_2(R^7) x T^2` (in `(Z/2)^2`) and `(0,x)` in `Z + Z/2` follow once the
    pullback is granted.
  - The E8-bar boost-circle argument is valid: boost commutes with `G_2`, the stabilizer is constant along the loop,
    and the multiplicity bundles over `S^1` are trivial.
- **The `W8` class is stated correctly.** The README declines `2 xi = C^4` because `11 > 2*4`. It records the
  stable class `2x = 0`, and it leaves the real question for `2 xi_R` open. That is the right call: on the 6-skeleton
  `2 xi` is trivial, and what remains is an obstruction on the 11-cell. I believe it lies in
  `pi_10(BU(4)) = pi_9(U(4)) = Z/2` (verify), so it is a genuine unstable question. The Chern classes vanish,
  because `c(2 xi) = c(xi)^2` and `H^2(V_2(R^7)) = H^4(V_2(R^7)) = 0`.
- **The completeness of the frame invariants is proved.** For an orthonormal four-frame with `alpha = phi(f_1,f_2,f_3)`,
  the identity `lambda^T G lambda + psi^2 = det G` makes the three mixed three-form values and `psi` an orthogonal
  coordinate system, of radius `sqrt(1-alpha^2)`, on the unit sphere of the complement of `span(f_1,f_2,f_3)`. So
  `f_4` is determined, and the `|alpha| = 1` and rank-two and rank-three cases close as the README states. The
  phase action and its quarter-turn check are exact.
- **The connected stabilizer strata are exhaustive** for the connected group, given the cited `G_2` isotropy:
  - the phase projection is killed by a nonzero weight-one or weight-two invariant;
  - the associativity criterion `phi^2 = det G_ijk` is exact;
  - `Iso` has frame rank four, since a complexified positive three-plane has maximal isotropic dimension one;
  - the `Iso` circle locus is exactly `tau = 0`, because the third exterior power of `diag(R(t), R(t))` fixes no
    nonzero vector.
- **The K-group arithmetic is correct**: `K^*(V_2(R^7)) = (Z + Z/2, Z)`, the Kunneth products with `S^1` and `T^2`,
  and `K^*(G_2) = (Z^2, Z^2)`. The cellular cohomology tables match.
- **The atlas is well posed.** `A(z, conjugate(z))` is skew at every tested point, the cocycle and Hermitian transport
  are rational identities, and the `U(4)` reduction is correctly scoped.
- **The prior review's main defects are mostly repaired.** Multiplicities and residues are now computed from bound
  rows. Mutations perturb inputs: a doublet in the bound fiber row, the bound generator order, an entry of the
  computed phase matrix. Branching restrictions upstream are now Casimir-computed. Ruff, format and mypy are clean,
  replays are byte-identical, and no Singular is used.

## Steelman

The record does the hard things right. It never feeds a rank-four bundle on an 11- or 12-dimensional base to the
cancellation inequality; the `W8` question stays explicitly open. The order-two class on E8-bar and `X_+-` is
detected by a restriction that survives every structural doubt raised here. Path dependence is shown by exact
counterexamples at a single boundary point, not by sampling. The invariant completeness proofs are correct and
checked by level-set ranks at every full-rank fixture. The two canonical inclusions the record claims are true. The
constant-rank lemma, together with the exact relation `R(i n) = i R(n)`, proves them, although the record argues
them differently. The record also caught that the `X` representatives are not Mostow-adapted, an error that
would otherwise have added a spurious circle.

## Verdict

The core is sound, and every stated bundle class is true:
- `W8` carries the pullback of `2 xi`, with reduced class zero;
- E8-bar, `X_+` and `X_-` carry `C^2 + xi`, with the nonzero order-two class;
- `Iso` is trivial;
- every characteristic class vanishes.

What the record gets wrong is structural. It claims the stabilizers have no finite components, and on `W8` they
have one, created by `(1, boost(pi), phase(pi))`, so the "phase circle" core is a double cover. Its canonical-limit
argument leans on group motions that have no lift. And no gate replays any of it.

Fix these first:
1. Compute `pi_0` of every full compact stabilizer, and replace the `W8` core argument with the mapping-torus
   argument.
2. Register the nine replays as gates.

The bundle classification is then earned. For item 6, the decisive next computation is the first-order limit map
from each transverse normal cone to `Gr(4, K_0)`: the constant-rank lemma makes it finite, and path dependence alone
says nothing about its image.
