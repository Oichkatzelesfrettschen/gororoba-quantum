# A_5 partner-sphere attachments across the closure incidences: program goal

This file is the goal objective of the Codex program on branch `geometry/a5-kernel-attachments`, worktree
`~/worktrees/IBMQuantum/a5-kernel-attachments`. The orchestrator (a Claude Code session) updates it in place. Re-read
it at every item boundary and after every context compaction. The ledger
[docs/evidence/a5-kernel-attachments/ledger.md](../evidence/a5-kernel-attachments/ledger.md) records state, and this
file sets the order.

The task is roadmap item 6 of `dimension32-global-topology`, as stated in
[RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates):
"Determine how partner spheres specialize across every admitted closure incidence, including directions absent from
the polynomial path. A frontier matrix alone omits the attaching maps." Item 7 (a finite global model with a proved map
to `Z_5`) consumes this deliverable, so its shape matters as much as its content. The aim, as in the two earlier
programs, is to debug and decompose, and above all to surface structural facts and questions the orchestrator has not
thought to ask.

## 1. What is established (read before anything else)

Repository rules: root `AGENTS.md` (the **Computer algebra** paragraph is binding: global orderings only, local
invariants by the deformation to the normal cone) and `ci/AGENTS.md`.

| Fact | Authority |
| --- | --- |
| The partner incidence is `Z_5 = {(x, y) : x y = 0}` normalized; over a point `x` the partner sphere is `S(ker L_x)`. On the restricted polynomial path the attaching data are literal inclusions `S(W) -> S(K_i)` of a constant common kernel, and the model is a union of mapping cylinders | [RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#a-complete-topological-model-for-the-restricted-path) |
| Conventions; transport `ker L_y = (conj o phi)^-1 ker A(z, conj z)`; `J = L_(e_16)` acts as `i` under `phi`; the kernel symmetry algebra is compact `g_2` plus four central directions and the split boost has no lift | [kernel-bundle record](../evidence/a5-kernel-bundles/README.md) |
| Twelve orbits of `H = G_2(C) x SO(2, C) x C^*`, their closure equations, representatives and closure order; Whitney stratification; the transverse germ of every closure along every lower orbit (tangent cones, multiplicities, sheets) | [regularity record](../evidence/a5-strata-regularity/README.md), closure and closure-order tables, Theorems 3 and 6 |
| Nullity 12 and 16: compact moduli (`rho` on `V^a_+-`, `(lambda, rho)` on `V`, the Hermitian Gram ball for `B9`, `VB`, `N_+-`), stabilizer representations, and the observation that each passage to `N_+-` adds exactly one standard `SU(2)` doublet to the kernel (a representation comparison only; no limit planes and no path-dependence test exist at 12 -> 16) | kernel-bundle record, "boundary" and `V_(1,-1)` passages |
| Nullity 8: compact moduli of dimensions 8, 6, 6, 4, 4; stabilizer strata; 33 exact degenerating paths covering all 15 incidences 8 -> 12, all at one verified point per boundary orbit; the limit four-plane is `ker` of the first-order restriction `F^T A_1 F` on `K_0` when that has rank two, otherwise of the Schur-corrected second-order form `D_2 + C_1^T B_0^-1 C_1`; 13 incidences have unequal limits on two approaches; `X_+- -> B9` is canonical by the constant-rank lemma plus the verified identity `F^T A(i d) F = i F^T A(d) F` | [nullity-8 record](../evidence/a5-kernel-bundles-nullity8/README.md#thirteen-boundary-incidences-have-path-dependent-kernel-limits), `boundary_specializations.py` |
| Pitfall that bit three times: the recorded representatives are special points for the compact group. Always test points moved by non-compact `G_2(C)` unipotents and the boost (`nilpotent_derivations`, `expm_nilpotent`, `act_g2`, `act_boost` in `docs/evidence/a5-strata-regularity/verify_regularity_independent.py`) | both kernel-bundle records |

## 2. The objects and the incidences

For an open orbit `X` of nullity `k` and a lower orbit `Y` of nullity `k' > k` in its closure, the closed kernel Gauss
graph is `G_X = closure {(x, ker L_x) : x in X}` inside `cl(X) x Gr`. Its fiber `Lambda(X, p)` over `p in Y` is the
set of limiting `k`-planes inside the boundary kernel `K_p`. The attaching datum of the partner-sphere bundle is the
union of `S(P)` over `P in Lambda(X, p)` mapping into `S(K_p)`, together with the map from the link of `Y` in `cl(X)`
at `p` onto `Lambda(X, p)` that the Gauss map induces, and how all of this varies with `p` over `Y`.

The incidences in scope (from the closure-order table):

| Passage | Count | Grassmannian | Prior evidence |
| --- | --- | --- | --- |
| 8 -> 12 | 15 | `Gr_C(4, 6)` | two exact limits each; 13 unequal |
| 12 -> 16 | 8 (`B9`, `V`, `VB` to each `N_+-`; `V^a_+ -> N_+`; `V^a_- -> N_-`) | `Gr_C(6, 8)` | representation comparison only |
| 8 -> 16 | 10 (each nullity-8 orbit to each `N_+-` in its closure) | `Gr_C(4, 8)` | none |
| same nullity (`W8 > Iso`, E8-bar `> X_+-`, `B9 > VB`, `V > VB, V^a_+-`) | 7 | none | **Inferred, record once:** constant rank makes the kernel map continuous, so the attaching map is the identity inclusion; spend no further time here |

Nullity 4 is out of scope: item 5 has not been done there.

## 3. Where the gaps are

- **A1. Real versus complex.** The Gauss map is real-algebraic: along a real arc the first-order term is
  `d_z A dz + d_zbar A dzbar`, so the effective form on `K_0` is in general only real-linear in the normal direction.
  The limit set is a real semialgebraic subset of `Gr_C(r, K_0)` parameterized by the real-projectivized normal cone
  (real dimension `2 codim - 1`), and complex structure is a per-incidence fact to be tested. A saturation or
  normal-cone fiber computed over Q in real coordinates gives only an **upper bound**: the Euclidean closure of a
  semialgebraic graph can be strictly smaller than the real points of its Zariski closure.
- **A2. First order versus higher order.** Where the first-order effective form has rank equal to the codimension of
  the kernel drop, one blow-up resolves the Gauss map; where it degenerates on part of the normal cone, the Schur
  correction (and possibly further orders) contributes further limits. Which incidences resolve after one blow-up is
  unknown.
- **A3. Variation over the boundary orbit.** The non-compact part of `H` does not lift to kernels, so `Lambda(X, p)` is
  only `K_p`-equivariant and need not be transported along `Y`. Its variation over the compact moduli of `Y` is
  unknown; every prior limit sits at one special point per boundary orbit.
- **A4. 12 -> 16 and 8 -> 16.** No limit plane has been computed for any incidence into `N_+-`.
- **A5. Compatibility.** Whether limits composed through an intermediate stratum (8 -> 12 -> 16) agree with the direct
  8 -> 16 limit sets, which a consistent global model needs.
- **A6. Attaching maps proper.** The homotopy type of the link-to-`Lambda` map and of `Lambda`-sphere union into
  `S(K_p)`, as item 7 will need them (mapping cylinders, homotopy colimit data, degrees, the classes they pull back).

## 4. What we are looking for

Deliverables, in priority order, in `docs/evidence/a5-kernel-attachments/` as code plus written results with falsifiers:

1. For every incidence 8 -> 12: `Lambda(X, p)` as a semialgebraic set with a **two-sided certificate**: an exact
   upper bound (equations from the effective forms or an elimination in global orderings) and explicit exact real arcs
   whose limits fill it (curve selection). State its dimension, components and `K_p`-orbit structure, and its variation
   over the boundary moduli from points moved by unipotents and the boost.
2. The same for every incidence 12 -> 16 and 8 -> 16, starting with a cheap two-approach path-dependence test.
3. The compatibility relation among the three passages (A5).
4. The attaching maps (A6): the map from each link to `Lambda`, the sphere-union map into `S(K_p)`, and their homotopy
   data in the form item 7 can assemble.

## 5. Questions we did not think to ask

This section is a standing deliverable. Keep the ledger list, with why each question matters, the cheapest decisive
probe and the result, and run the cheap ones. Seeds:

- Per incidence, does the antiholomorphic first-order part vanish on `K_0`? If so the limit set is complex-algebraic;
  if not, what real structure replaces it? This is the first probe on every incidence.
- Is the closed Gauss graph over each closure the Nash blow-up, and is it smooth?
- Do all limit planes at `p` share a common subspace (a canonical partial inclusion), or does their intersection vanish?
- Is `Lambda(X, p)` a single `K_p`-orbit, finitely many, or a positive-dimensional family of orbits?
- Do the two sheets of E8-bar along `V` and `V^a_+-` give different limit sets?
- Does the order-two K-class on E8-bar and `X_+-` reappear as an obstruction in the attaching map into `N_+-`, whose
  bundle carries the same class?
- Is the 12 -> 16 passage canonical (constant-rank lemma) like `X_+- -> B9`, given that each such passage adds exactly
  one doublet?

## 6. Behavior required

- Exact arithmetic only (integers, Fractions, Gaussian rationals, python-flint, Singular over Q or Q(i) in global
  orderings). A numerical probe may suggest a conjecture and is labeled as such; it never enters a claim.
- State the falsifier before each probe, in the ledger, and separate observed from inferred. A step that is a proof is
  labeled **Inferred** with its argument and a standard citation.
- **Never certify a conclusion with a literal in a pass flag**: every number a README states is computed and compared
  by the producing script, or labeled as an argument. Mutation controls perturb **inputs** and must fail because a
  downstream computation changes. (Both earlier critical reviews found these defects:
  [nullity >= 12](../archive/reviews/2026-10-26-a5-kernel-bundles-critical.md),
  [nullity 8](../archive/reviews/2026-10-27-a5-kernel-bundles-nullity8-critical.md).)
- Code in `docs/evidence/a5-kernel-attachments/` only; never draft files at the worktree root or elsewhere. Scripts
  carry `--out`, a byte-exact `--check PATH`, and `--self-test`. They may import cd_core, the a5-strata-regularity and
  a5-rank-strata-equations helpers, and the committed scripts of both kernel-bundle records. Follow root `AGENTS.md`
  code style: ruff format, ruff check and mypy through `ci/pinned_tool.py`, plus the docs-wide check
  `MYPYPATH=docs "$PYTHON" ci/pinned_tool.py mypy --explicit-package-bases docs/verify_sources.py docs/`; no `assert`,
  explicit raises; records float-free. **Every loop over independent items goes through `parallel.ordered_map`**,
  including comprehensions that build work, baseline-plus-mutation records, and per-incidence comparisons: each earlier
  review round found exactly one serial loop. Start Python with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`
  and invoke it as `"$PYTHON"`. Keep each `--check` under 15 s where possible.
- No random seeds. If one becomes necessary, stop and record it as an owner decision.
- Write results as you go: a ledger row per sub-step, and `docs/evidence/a5-kernel-attachments/README.md` for durable
  statements with proofs, in the voice of the existing evidence READMEs: mechanism first, American spelling,
  emoji-free, no local absolute paths.
- The sandbox keeps git metadata and `~/.cache/gororoba-quantum` read-only, so the agent never stages or commits and
  never runs `ci/pr_checks.sh`. At each sub-step boundary it leaves the files in the worktree, adds the ledger row and
  continues. **A pending orchestrator commit never blocks the next sub-step.** The orchestrator reviews, replays and
  commits with the trailer `Assisted-by: Codex CLI (gpt-daybreak-blue-latest)`.

## Standing rules

- Authorized without asking: reading anything in the repository; creating and editing files under
  `docs/evidence/a5-kernel-attachments/` and the ledger; running Python, Singular, python-flint and local checks that
  need no shared cache lock; spawning no subagents.
- Owner-only decisions, recorded in the ledger as `BLOCKED: owner` and left for the orchestrator: adding or changing a
  claim in `docs/state/research_state.json`; editing any file outside `docs/evidence/a5-kernel-attachments/`; scope
  beyond item 6 (nullity 4, items 7-8 proper); any network access, provider job or QPU job.
- Hard boundaries: never `git push`, never open a pull request, never `git stash`, never `rm -rf` (use `trash-put`),
  never edit `gororoba_quantum/cd_core.py` or any retained evidence file of another record, never touch other worktrees,
  `~/.codex` or `/tmp` worktrees of other sessions. The host is shared (62 GiB): run every Singular process under
  `prlimit --as=8589934592` (8 GiB), set `GOROROBA_WORKERS=4` for pooled runs, and stop any computation that passes 15
  minutes, then record it and find a cheaper formulation (the transverse slice, a symmetry reduction, the effective
  form on `K_0` instead of the full matrix).
- Turn length: end each turn at a sub-step boundary, about an hour at most; the goal continues on its own.
- Cap any sub-step at three failed attempts, record its blocker, move on.
- Done when deliverables 1-4 are complete or blocked on a named owner decision, section 5 holds at least five
  investigated questions, and the README states every result with its falsifier and evidence path.

## Handoff state

- Branch `geometry/a5-kernel-attachments` from main after PR 578 (the nullity-8 record) merged, with this program file
  and the ledger stub added by the orchestrator.
- No jobs in flight.

## Order

1. **Incidence census and the real/complex probe (A1).** Enumerate all 33 incidences with exact boundary points,
   including moved points; on each, restrict the holomorphic and antiholomorphic first-order parts to `K_0` and record
   which are complex. Acceptance: one row per incidence. Falsifier: a declared incidence without an exact point, or a
   complex-linearity verdict that a second boundary point reverses without explanation.
2. **8 -> 12 limit sets (deliverable 1)**, first-order map from the real-projectivized normal cone, then higher-order
   contributions on its degeneracy locus, then the two-sided certificate and variation over the boundary moduli.
3. **12 -> 16 and 8 -> 16 (deliverable 2).**
4. **Compatibility (deliverable 3).**
5. **Attaching maps (deliverable 4).**
6. **Section 5 questions**, interleaved as soon as the tools exist.

## Orchestrator notes

- Item 1 (committed `ac03e96`): the antiholomorphic first-order part lives on the scalar border and every tested
  boundary-kernel frame has a zero scalar row. Test whether this is structural, for example whether every partner of a
  doubly pure `y` is itself pure (zero real part) on the whole nullity >= 8 locus. A proof promotes the complex-linearity
  verdict from 21 tested points to every boundary point at first order; record it as a section 5 question either way.
- Items 2b and 2c (committed `676a3a4` and the first-order image commit): both producers reuse the `W8`-to-`B9`
  middle-coordinate path mutation, which fails at closure membership before the new computation runs. Give each new
  producer at least one mutation of an input to its own core computation (the restricted first-order form, the tangent
  cone generators, a Schur block), so a reviewer sees the elimination or limit computation itself change.
- The seven higher-order rows (three identically zero at first order) are the substance of deliverable 1. Prefer the
  Schur-corrected effective form over the degeneracy locus, restricted to the transverse slice, before any full
  Gauss-graph elimination.
- Item 2d (committed `c7f3295`): on `W8` to `VB` the limit depends on the second jet at a fixed tangent-cone direction,
  so no direction-indexed upper bound is complete there. For the upper half of the two-sided certificate on the seven
  higher-order rows, eliminate the Gauss graph over the transverse slice itself: slice coordinates `s` (dimension the
  codimension of the boundary orbit, for example 5 for `W8` to `VB`), an affine chart of `Gr(4, K_0)` (eight
  coordinates), the incidence `A(s) F = 0` reduced to the effective form on `K_0`, saturation by the nullity-drop ideal,
  then `s = 0`, all in global orderings under `prlimit`. Report the fiber dimension and components, and compare them
  with the arc lower bound.
- Item 2e (blocked at 8 GiB on the 28- and 32-variable products): reformulate before retrying. Near `p`, split
  `C^16 = K_0 + K_0^perp` and take the Schur complement `E(s) = D(s) - C(s)^T B(s)^-1 C(s)` on `K_0`, with `B(0)`
  invertible. On the nullity-8 part of the slice germ `E(s)` is a rank-two skew 6 x 6 form, hence a decomposable
  bivector, and its kernel four-plane is the point `[E(s)]` of `Gr(2, 6)` in its Plucker embedding in `P^14`. The
  Gauss-graph fiber over `p` is therefore the exceptional fiber of the blow-up of the germ along the ideal of the 15
  entries of `det(B) E(s)`, saturated by `det(B)`: the Rees algebra in the slice coordinates (at most 5 after the linear
  eliminations already proved) plus 15 Plucker variables, then `s = 0`. Use a polynomial parameterization of the slice
  germ where the regularity record gives one (quadric cones, smooth sheets), so the base ring is a polynomial ring.
  Singular's `reesclos.lib` or a direct elimination in global orderings both fit. A single Singular process may use up
  to 16 GiB (`prlimit --as=17179869184`) for this item, one such process at a time; the 15-minute stop rule stands.
- Memory rule (supersedes the Singular-only cap): an inline `python3 -c` probe for item 2f reached 44 GB resident on
  the shared 62 GiB host and pushed the system into memory pressure. Run every Python, Singular or sympy computation,
  inline probes and background terminals included, under `prlimit --as=17179869184` (16 GiB) or less. A computation
  that hits the cap counts as a failed attempt and calls for a smaller formulation.

## Stepwise mode and the computation stack (owner direction, supersedes earlier pacing)

**Stepwise.** The goal no longer auto-continues. Each orchestrator message names exactly one sub-step. Do that
sub-step only: register its falsifier in the ledger, build or revise one producer, run it once under the resource rules
below, write its ledger outcome and README section, and end the turn idle. The orchestrator reviews, replays and
commits, then sends the next sub-step. Never start a second sub-step in the same turn, and never leave a background
terminal running at the end of a turn.

**Library choice.** [docs/PYTHON.md](../PYTHON.md) is the central routing page: its "Libraries by job" table and
optimization ladder bind, the [library register](../state/hypercomplex-libraries/libraries.md) lists every pinned
distribution's role, and [python-stack.md](../notes/build_host/python-stack.md) lists the build host's Arch (`paru`)
packages. Choose granularly, cheapest exact tool first:

- Ranks, null spaces and kernel frames: python-flint (`nmod_mat` rank modulo a word prime as a lower bound, then
  `fmpq_mat` RREF for the rational kernel, checked in integers), through `scripts/exact_rank.py` where it fits; sympy
  only as `DomainMatrix` on FLINT ground types, never generic `Matrix` arithmetic on large symbolic entries.
- Polynomials: python-flint `fmpz_mpoly` / `fmpq_mpoly` for construction, substitution and Pfaffians; avoid sympy
  expression trees beyond a few hundred terms, because expression swell is what reached 44 GB.
- Elimination, saturation, Rees algebras, primary decomposition: Singular in global orderings. Run the computation
  modulo a word-size prime first (`ring r = 32003, ...`) to predict the answer and its cost, then over Q; use
  `modStd` / `modSat` (modular methods) where available, and SageMath only for a cross-check whose output a gate
  retains.
- Numerical probes that only suggest a conjecture: numpy or scipy on CPU; CuPy, PyTorch (CUDA) or numba-cuda on the
  RTX 4070 Ti (12 GiB) only for a batched float sweep large enough to pay for the transfer. Exact claims never come from
  the GPU.

**Resources.** The host is shared: 12 cores, 62 GiB, one GPU.

- Every process, inline probes included, runs under `prlimit --as=17179869184` (16 GiB) or less, and the total of all
  concurrent workers stays under 16 GiB: with `GOROROBA_WORKERS=4`, each worker gets at most 4 GiB.
- Pool independent items with `parallel.ordered_map` (`GOROROBA_WORKERS=4` by default, at most 8). Leave BLAS and
  OpenMP threads at 1 inside pooled workers. A single Singular process is single-threaded, so parallelism comes from
  pooling independent incidences, never from oversubscription.
- Stream rather than accumulate: build a polynomial or matrix, reduce it, keep only the reduced form; compute
  Pfaffians and minors chart by chart; write intermediate exact results to the evidence directory instead of holding
  every incidence in memory.
- Measure before scaling (`/usr/bin/time -v` for peak RSS, `py-spy` for hot spots), and record each producer's peak
  RSS and wall time in its ledger row.

## Orchestrator note after 2g: the holomorphic kernel

Items 2e-2g failed on cost because they eliminate in real and imaginary parts at degree up to 26. The purity record
already gives a holomorphic formulation. With `A(z, conj z) = [[0, -conj(z)^T], [conj(z), C_z]]` and every kernel vector
of the form `(0, u)`, `ker A = {u : C_z u = 0, <z, u> = 0}` (Hermitian pairing). Since `C_z z = 0`,
`ker C_z = C z (+) ker A`, an orthogonal sum, so `dim ker C_z = dim_C ker A + 1`: 5, 7 and 9 at nullity 8, 12 and 16.
`C_z` is holomorphic and linear in `z`. Along an arc, `ker C_z(t) -> L` gives `ker A(t) -> L cap z_0^perp` with `z_0 != 0`,
and `P -> P (+) C z_0` inverts this. Hence, if the steps below verify:

- the Gauss fiber `Lambda(X, p)` is homeomorphic to the fiber `Lambda_hol(X, p)` of the closed graph of the
  holomorphic map `s -> ker C_(z(s))` into `{L in Gr(k+1, ker C_(z_0)) : L contains z_0} = Gr(k, ker C_(z_0) / C z_0)`;
- that fiber is complex-algebraic, and the Euclidean closure of the graph equals its Zariski closure, because the
  graph of an algebraic map on an irreducible complex germ is constructible. The real curve-selection obligation (A1)
  then reduces to this algebraic statement, and arcs serve as a check, not as the lower half of the certificate.

Sub-steps, one per turn:

- **2h. Verify the holomorphic kernel lemma.** At all nine path-supported basepoints and at the sampled arc points of
  every retained path, verify exactly (python-flint `fmpq_mat` or Gaussian-rational RREF) that `rank C_z` is 10, 8, 6
  at nullity 8, 12, 16, that `z in ker C_z`, and that `ker A` equals the Hermitian complement of `z` in `ker C_z`.
  Mutation: replace `z` in the pairing by a vector of `ker C_z` independent of `z`, so the complement changes and the
  comparison fails. Falsifier: any rank or equality failure.
- **2i. Holomorphic Gauss fibers by iterated blow-up** (after 2h is committed). On a complex polynomial parameterization
  of the transverse slice germ (complex coordinates only, no real or imaginary split), take the Schur complement of
  `C_z` on `ker C_(z_0)` (7 x 7 at nullity 12, rank two on the source orbit), cleared by the Pfaffian of the
  complementary 8 x 8 block. Its 21 entries have degree about 5 in `z`. Principalize the base ideal of the map to
  `P^20` by explicit blow-ups at the origin and at each base locus in affine charts, each step a substitution and a
  removal of the largest common power of the exceptional coordinate. The fiber is the union of the images of the
  exceptional divisors. Use the Rees algebra in Singular only as a cross-check on small incidences, modulo 32003
  first.

## Orchestrator note after 2h

- 2h is committed (`cce2f07`). The superseded real-coordinate drafts of 2e-2g are in the trash.
- Producer inputs: hash only files a computation reads (cd_core, the imported evidence scripts, upstream result
  records). Never hash this program file or the README; commit `1b38200` removed it from every producer because each
  steering note staled their records.
- The docs-wide type check is the gate's exact command, `MYPYPATH=docs "$PYTHON" ci/pinned_tool.py mypy
  --explicit-package-bases docs/verify_sources.py docs/check_verify_sources.py docs/evidence`, which must report no
  issues; mypy over all of `docs/` is a different, wider scope and is not the gate.
- Next sub-step: **2i** as specified above, starting with the eight first-order-resolved incidences (cheapest, a check
  of the method against the committed first-order images), then the seven higher-order rows in a later sub-step.

## Orchestrator note after 2j: the Nakayama-reduced Rees fiber (supersedes the 2i blow-up recipe for 2j)

The 2j draft (`higher_order_holomorphic_gauss_fibers.py`) is withdrawn. It wrote `sat(...)[1]` nine times; Singular
4.4 `sat` returns an ideal, so `[1]` kept one generator and every strict transform was a single hypersurface. Its
Rees graphs also carried all 21 target coordinates. Neither the draft nor its all-blocked record is retained.

The fiber of the closed Gauss graph over `p` is the special fiber `Proj (+)_d I^d / m I^d` of the blow-up of
`I = (f_1, ..., f_21)` in `k[t]/J` (`J` the germ ideal of path-supported-basepoints). Each graded piece is killed by
`m`, so the polynomial ring computes it exactly in a global ordering. The method, per incidence:

1. `SJ = std(J + maxideal(1) * I)` in the slice variables only. A greedy pass over `f_1..f_21` picks `g` whose
   normal forms modulo `SJ` are linearly independent; `s = size(g)` is the minimal generator count of `I` at `p`
   (Nakayama). Observed: `X+-` to `VB` 3, `Iso` to `VB` 4, `W8` to `VB` 5, `E8bar` to `V^a+-` 6, `E8bar` to `VB` 10.
2. `elimpart(J)` (presolve.lib) removes slice variables that `J` solves linearly; apply its map `EP[5]` to `J` and
   `g`, then reduce `g` modulo `std(J)`.
3. Rees ideal `eliminate(J + (y_i - a g_i), a)` in `k[a, t, y_1..y_s]`; the fiber is that ideal at `t = 0`,
   saturated by `(y)`, decomposed with `minAssGTZ`.
4. `lift(J + m I + (g), f)`; the constant terms of the `g` rows give the `21 x s` matrix `A` with
   `f = A g mod (m I + J)`. Require `rank A = s`; then `A` embeds the reduced fiber in `P^20`.
5. Every committed Schur arc limit `q` lies in the column span of `A` and its preimage lies in the fiber; a random
   point of `P^20` must fail the same test (negative control).

Orchestrator measurements, modulo 32003, under 4 GiB: six rows finish in under one second at about 42 MB. Fibers:
`X+-` to `VB` all of `P^2`; `Iso` to `VB` all of `P^3`; `W8` to `VB` all of `P^4`; `E8bar` to `V^a+-` two disjoint
planes `{y1=y2=y6=0}` and `{y3=y4=y5=0}`. All 12 committed arcs lie in their fibers; both `E8bar` to `V^a+-` arcs
lie in the second plane, so the first plane has no committed arc witness. `E8bar` to `VB` (`s = 10`) exhausts 4 GiB
in the Rees elimination and times out at 15 minutes with `slimgb`; it remains open in its own later sub-step.

- **2j-c.** One producer, `nakayama_rees_fibers.py`, on the six rows above, modulo 32003 and over `Q(i)`, with the
  standing producer rules (`--out`, byte-exact `--check`, `-O --self-test`, pooled rows, float-free record, input
  hashes excluding this file and the README). Record per row: `s`, the chosen indices, the eliminated variables,
  each fiber component (projective dimension, degree, generators), `rank A`, each arc's containment and the
  component that holds it, and the random-point control. Mutation on a core input: drop one `g_i` from the Rees
  ideal, which must change the fiber or break an arc containment. Every Singular call runs under
  `prlimit --as=4294967296` with a 300 s timeout; the whole run stays under one minute. Write the README section
  and ledger row; replace the withdrawn 2j text with the bounded `E8bar` to `VB` blocker and its measured costs.

- **Memory cap for msolve (owner decision).** One msolve process may run under `prlimit --as=25769803776` (24 GiB)
  when a modular elimination exhausts 16 GiB, with a guard that stops it when `MemAvailable` falls below 4 GiB.
  Singular processes keep the 16 GiB single-process cap. msolve works over prime fields only: take
  `p = 1073741789` (`p = 1 mod 4`) and `i = 140687844`, a square root of -1 modulo `p`.

## Orchestrator note after 2j-c: the incidences into nullity 16

`E8bar` to `VB` stays open after msolve (segmentation fault at the 24 GiB cap after 25 minutes), giac over `Q(i)`
(30-minute timeout at 300 MB), weighted tangent cones (non-reduced under every weighting of `t2, t3+t4, t5-t6, t8`)
and normalization (3 s, but 115 relations after presolve). Its germ behaves as a branched double cover of the 4-plane
`(t1, t4, t6, t7)`; it gets its own design round, and no sub-step reformulates it by brute force.

The 18 incidences into nullity 16 (`B9`, `V`, `VB`, `V^a+-` to `N+-`; `E8bar`, `Iso`, `W8`, `X+-` to `N+-`) have no
basepoints, slices or germ records; `path-supported-basepoints-result.json` and `first-order-normal-cones-result.json`
cover only the 15 incidences into nullity 12. At nullity 16 `rank C_z = 6`, so the Schur complement lives on the
9-dimensional `ker C_(z_0)`: rank 2 on a nullity-12 source, with its 36 entries as Plücker coordinates of the row
plane in `Gr(2,9)`; rank 4 on a nullity-8 source, with its 126 principal 4 x 4 Pfaffians as Plücker coordinates of
the row 4-plane in `Gr(4,9)`.

- **2k-a.** One producer, `nullity16_basepoints.py`: for each of the 18 incidences, an exact path-supported basepoint
  on the `N+-` orbit reached by a committed census path, a coordinate slice transverse to the boundary orbit, the
  source-closure germ there (dimension, multiplicity, embedding dimension, components; global orderings and the
  normal-cone deformation only), and the Nakayama count `s` of the Schur coordinates above at that basepoint. Pool
  the rows; every Singular call under `prlimit --as=4294967296` with a 300 s timeout. Report the measured cost per
  row; a row that exceeds the timeout is recorded as blocked with its stage, and the run continues.
