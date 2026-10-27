# A_5 kernel bundles on the nullity-8 strata: program goal

This file is the goal objective of the Codex program on branch `geometry/a5-kernel-bundles-nullity8`, worktree
`~/worktrees/IBMQuantum/a5-kernel-bundles-nullity8`. The orchestrator (a Claude Code session) updates it in place.
Re-read it at every item boundary and after every context compaction. The ledger
[docs/evidence/a5-kernel-bundles-nullity8/ledger.md](../evidence/a5-kernel-bundles-nullity8/ledger.md) records state,
and this file sets the order.

The task extends roadmap item 5 of `dimension32-global-topology` from the strata of nullity 12 and 16, which are done,
to the five orbits of nullity exactly 8. It determines the kernel bundles there: compact-orbit moduli, stabilizer
representations, transition data, equivalence classes, and how each bundle specializes into the nullity-12 pieces in
its closure. That last part is the input roadmap item 6 needs. As before, the aim is to debug and decompose, and above
all to surface structural facts and questions the orchestrator has not thought to ask.

## 1. What is established (read before anything else)

Repository rules: root `AGENTS.md` (the **Computer algebra** paragraph is binding: global orderings only, local
invariants by the deformation to the normal cone) and `ci/AGENTS.md`.

| Fact | Authority |
| --- | --- |
| Conventions, transport ker L_y = (conj o phi)^-1 ker A(z, conj z), J = L_(e_16) acting as i under phi | [kernel-bundle record](../evidence/a5-kernel-bundles/README.md), Conventions and "The transport uses the conjugated input" |
| The constant kernel symmetry algebra is compact g_2 + base phase + base scaling + fiber scaling (0, I, I) + fiber rotation (0, J, -J). The split boost has no lift. A visible S_3 x Z_2 occupies twelve components (exhaustiveness open) | kernel-bundle record, `kernel_symmetry.py`, `result.json` |
| Nullity-8 orbits of H = G_2(C) x SO(2, C) x C^* and their complex dimensions: W8 (12), E8-bar (11), Iso (11), X_+ (10), X_- (10). Closure equations and representatives (split coordinates) are in the closure table. Closures strictly below: W8 > Iso, B9, VB, N_+-; E8-bar > X_+-, B9, V, VB, V^a_+-, N_+-; Iso > B9, VB, N_+-; X_+ > B9, VB, V^a_+, N_+, N_-; X_- symmetric | [regularity record](../evidence/a5-strata-regularity/README.md), closure and closure-order tables; `REPS` in `strata_regularity.py` |
| Singular loci and transverse germs of the nullity-8 closures along every lower orbit (for example E8-bar along V is two smooth sheets meeting at the point; Iso along VB is a rank-5 quadric cone) | regularity record, Theorems 3 and 6 |
| At nullity 8 the complex kernel rank under J is 4 | strata record Theorem 2 (nullity = 28 - 2 rank C_z) |
| Results at nullity >= 12 to build on: compact-orbit moduli (rho on V^a_+-, (lambda, rho) on V, the Hermitian Gram ball for B9 / VB / N_+-); stabilizer representations (SU(2): 2 V_0 + 2 V_1 principal; SU(3): 3 + conj(3) at rho = 1; U(1): 3 C_(-1) + 3 C_(-2) on B9; U(2) on VB and N_+-); all five nullity-twelve complex bundles trivial; N_+- complex bundle C^2 + 3 xi with the order-two class in reduced K^0(V_2(R^7)) = Z/2; every real kernel bundle trivial | kernel-bundle record, its README sections and result files |
| Methods that worked at nullity >= 12: exact Lie-algebra solves for stabilizers; Casimir and commutant projectors for decompositions; orbit invariants proved complete by level-set rank plus normal forms; Pfaffian-chart frames with free-row transitions; Hodgkin and Atiyah-Hirzebruch for K-theory; stable cancellation only within its stated range | kernel-bundle record |
| Pitfall that bit twice: the recorded H-orbit representatives can be special points for the compact group. Always test points moved by non-compact G_2(C) unipotents and the boost (helpers `nilpotent_derivations`, `expm_nilpotent`, `act_g2`, `act_boost` in `docs/evidence/a5-strata-regularity/verify_regularity_independent.py`) | kernel-bundle record; orchestrator check |

## 2. Where the gaps are

- **N1. Generic compact-orbit dimensions and moduli** on the unit sections of W8 (real dimension 23), E8-bar (21), Iso
  (21) and X_+- (19). Their dimensions at the recorded representatives versus at generic points are unknown. Expect
  larger moduli than at nullity 12.
- **N2. Stabilizer types and their strata** inside each nullity-8 orbit: which stabilizers occur, where they jump, and
  how the jump loci sit relative to the closure order.
- **N3. Fiber representations** of each stabilizer on the complex rank-4 kernel, and their restrictions at the
  boundary of each moduli space. A boundary orbit of nullity 12 must contain the nullity-8 representation plus two
  extra dimensions; the shape of that specialization is the attaching data for item 6.
- **N4. Unit-section topology** of each nullity-8 orbit, as far as the invariants need it.
- **N5. Transition data, structure group and classes** of each nullity-8 kernel bundle. A rank-4 complex bundle over a
  base of real dimension 19 to 23 lies outside the stable range of cancellation for most pieces, so triviality needs
  explicit arguments, and genuinely new invariants are plausible.
- **N6. E8-bar and its sheets.** E8-bar is singular along V and B9, with two smooth sheets along V and along V^a_+-.
  Whether the kernel bundle over the open E8-bar orbit extends over the sheets differently on each sheet is unasked.

## 3. What we are looking for

Deliverables, in priority order, in `docs/evidence/a5-kernel-bundles-nullity8/` as code plus written results with
falsifiers:

1. Generic K-orbit dimensions, orbit invariants proved complete, and moduli spaces for W8, E8-bar, Iso and X_+- (N1).
2. Stabilizer types, their strata, and the fiber representations on the rank-4 kernel, with every boundary
   restriction into the adjacent nullity-12 pieces (N2, N3).
3. Unit-section topology needed for the invariants (N4).
4. Transition data, structure groups, characteristic classes and K-classes, and decided equivalence classes (N5, N6).

## 4. Questions we did not think to ask

This section is a standing deliverable. Keep the ledger list, with why each question matters, the cheapest decisive
probe and the result, and run the cheap ones. Seeds:

- Is the nullity-8 kernel ker L_y a subspace of the kernel at a nearby nullity-12 boundary point in a canonical way, so
  that the attaching data reduces to an inclusion of representations?
- Does the order-two class of N_+- propagate upward, so that some nullity-8 bundle carries a nonzero torsion class
  restricting to it?
- Is there a nullity-8 orbit on which the compact group is transitive (homogeneous), as N_+- was at nullity 16?
- Do the two sheets of E8-bar along V carry kernel bundles that differ as bundles, which would make the attaching map
  sheet-dependent?
- Does W8, which lies outside V(Q), behave differently from the four orbits inside V(Q) n V(G)?

## 5. Behavior required

- Exact arithmetic only (integers, Fractions, Gaussian rationals, python-flint, Singular over Q or Q(i) in global
  orderings). A numerical probe may suggest a conjecture and is labeled as such; it never enters a claim.
- State the falsifier before each probe, in the ledger, and separate observed from inferred. A step that is a proof
  (homotopy, spectral sequence, cancellation) is labeled **Inferred** with its argument and a standard citation.
  **Never certify a conclusion with a literal in a pass flag**: every number a README states is either computed and
  compared by the producing script or labeled as an argument. Mutation controls perturb inputs and must fail because
  a downstream computation changes. (The critical review of the nullity >= 12 record found exactly these defects:
  [review](../archive/reviews/2026-10-26-a5-kernel-bundles-critical.md).)
- Code in `docs/evidence/a5-kernel-bundles-nullity8/`. Scripts carry `--out`, a byte-exact `--check PATH`, and
  `--self-test`. They may import cd_core, the a5-strata-regularity and a5-rank-strata-equations helpers, and the
  committed scripts of `docs/evidence/a5-kernel-bundles/`. Follow root `AGENTS.md` code style: ruff format, ruff check
  and mypy through `ci/pinned_tool.py`, no `assert`, explicit raises. Every loop over independent items goes through
  `parallel.ordered_map`, including comprehensions that build work and the mutation builds inside `self_test`.
  Start Python with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` and invoke it as `"$PYTHON"`. Keep each
  `--check` under 15 s on this host where possible.
- No random seeds. If one becomes necessary, stop and record it as an owner decision.
- Write results as you go: a ledger row per sub-step, and `docs/evidence/a5-kernel-bundles-nullity8/README.md` for
  durable statements with proofs. Use the voice of the existing evidence READMEs: mechanism first, American spelling,
  emoji-free, no local absolute paths.
- The sandbox keeps git metadata and `~/.cache/gororoba-quantum` read-only, so the agent never stages or commits and
  never runs `ci/pr_checks.sh`. At each sub-step boundary it leaves the files in the worktree, adds the ledger row and
  continues with the next item. **A pending orchestrator commit never blocks the next sub-step.** The orchestrator
  reviews, replays and commits with the trailer `Assisted-by: Codex CLI (gpt-daybreak-blue-latest)`.

## Standing rules

- Authorized without asking: reading anything in the repository; creating and editing files under
  `docs/evidence/a5-kernel-bundles-nullity8/` and the ledger; running Python, Singular, python-flint and local checks
  that need no shared cache lock; spawning no subagents.
- Owner-only decisions, recorded in the ledger as `BLOCKED: owner` and left for the orchestrator: adding or changing a
  claim in `docs/state/research_state.json`; editing any file outside `docs/evidence/a5-kernel-bundles-nullity8/`;
  scope beyond nullity 8 (items 6-8 proper, nullity 4); any network access, provider job or QPU job.
- Hard boundaries: never `git push`, never open a pull request, never `git stash`, never `rm -rf` (use `trash-put`),
  never edit `gororoba_quantum/cd_core.py` or any retained evidence file of another record (including everything in
  `docs/evidence/a5-kernel-bundles/`), never touch other worktrees, `~/.codex` or `/tmp` worktrees of other sessions.
  The host is shared (62 GiB): run every Singular process under `prlimit --as=8589934592` (8 GiB), set
  `GOROROBA_WORKERS=4` for pooled runs, and stop any computation that passes 15 minutes, then record it and find a
  cheaper formulation (smaller slice, better coordinates, a symmetry reduction).
- Turn length: end each turn at a sub-step boundary, about an hour at most; the goal continues on its own.
- Cap any sub-step at three failed attempts, record its blocker, move on.
- Done when deliverables 1-4 are complete or blocked on a named owner decision, section 4 holds at least five
  investigated questions, and the README states every result with its falsifier and evidence path.

## Handoff state

- Branch `geometry/a5-kernel-bundles-nullity8` from main after PR 571 (the nullity >= 12 record) merged, with this
  program file and the ledger stub added by the orchestrator.
- No jobs in flight.
- Orchestrator note: an earlier draft of `compact_orbit_ranks.py` appeared at the worktree root; it is moved to the
  trash. Create every file inside `docs/evidence/a5-kernel-bundles-nullity8/` only, scratch drafts included. The
  first sub-step (compact ranks 12, 12, 15, 12, 12 at the representatives, 15 generically) is reproduced by the
  orchestrator's independent rank check.

## Order

1. **Generic orbits and moduli (deliverable 1).** For each of W8, E8-bar, Iso, X_+-: compact tangent ranks at the
   representative and at moved points, candidate invariants, completeness proofs, moduli spaces. Acceptance: exact
   orbit dimensions at generic and special points and a completeness argument per invariant. Falsifier: two points
   with equal invariants in different orbits, or a generic dimension that disagrees with an independent rank.
2. **Stabilizers and fiber representations (deliverable 2)**, including every boundary restriction into nullity 12.
3. **Unit-section topology (N4).**
4. **Transitions, structure groups, classes (deliverable 3-4).**
5. **Section 4 questions**, interleaved as soon as the tools exist.

## Round 2: review fixes (orchestrator, 2026-10-27)

Deliverables 1-4 are complete and committed (through b5f9c71). The critical review at
[docs/archive/reviews/2026-10-27-a5-kernel-bundles-nullity8-critical.md](../archive/reviews/2026-10-27-a5-kernel-bundles-nullity8-critical.md)
found no fatal defect and confirms every stated class. Fix the following in the existing scripts and README; the
orchestrator adds the replay gates (the review's SERIOUS 2) and folds in the independent verifier's result when it
arrives.

1. **SERIOUS 1, component groups.** The element (1, boost(pi), phase(pi)) fixes every mu = 0 point and lies outside
   the identity component of the W8 compact stabilizer, so the README sentence "no additional finite stabilizer
   component remains" and "the phase circle supplies the remaining circle on W8" are false as stated, and the ledger's
   item-4 Observed label overstates a Lie-algebra projection. Compute the component group of the full compact
   stabilizer exactly on every orbit (W8, E8-bar including whether finite boost elements other than boost(pi) occur,
   Iso, X_+-). Replace the W8 class argument by the mapping-torus argument: the core is homotopy equivalent to
   V_2(R^7) x S^1 with constant monodromy 1 (x) m, m in the connected GL(2, C), so the bundle is pr^*(2 xi) with
   reduced class 0. Correct the ledger labels.
2. **SLOPPY 3, X_+- -> B9 canonicity.** Replace the group-curve argument (those curves have no lift) by the
   constant-rank lemma: first-order limits depend only on the normal direction, and F^T A(i d) F = i F^T A(d) F makes
   every complex normal direction give the same plane; compute that identity exactly in the script.
3. **SLOPPY 4.** State in the README that path dependence shows the attaching datum is not an inclusion and that the
   set of all limits (the attaching data item 6 needs) is not yet computed.
4. **SLOPPY 5 and the literals.** Label in the README every JSON entry the script marks inferred (free K-coordinates,
   the Iso row, characteristic classes). Give the reason for R^4 + xi_R = R^8 (xi_R plus the span of
   (x_1, x_2, x_1 x_2) is the trivial R^7), not cancellation. Rebuild `remove_e8_path_dependence` so it perturbs an
   input and fails through a downstream computation.
5. **SLOPPY 6.** Argue that the X fiber representation is constant along its stratum and that the stratum is connected,
   or compute it at a Mostow-adapted point.
6. **SLOPPY 8.** Check the Mostow citation for stabilizers with a unipotent radical (the 1962 sequel is the likely
   source) and cite the standard G_2 isotropy facts.
7. **Serial loops.** Pool the baseline runs with their mutations in `boundary_specializations.py` (and its incidence-row
   comprehension), `kernel_transition_atlas.py`, `unit_section_topology.py` (and avoid recomputing the coassociative
   enumeration per core), `stabilizer_strata.py` and `kernel_bundle_classes.py`.
8. **Cosmetic.** The README introduction's "Transition data and bundle classes remain open", stale timings, the 45
   double overlaps including 15 identities, the unreachable `elif` in `_compact_stabilizer_row`, and the
   open-to-generic analyticity sentence.

After the fixes, rerun every `--out` in dependency order until every `--check` holds, every `--self-test` (normal and
-O), ruff and mypy, and record a ledger row per fix. Same rules: no staging or commits, files only inside the evidence
directory.

Verifier result (committed): [verification.md](../evidence/a5-kernel-bundles-nullity8/verification.md) confirms all
five statement groups at independent moved points; no refutation. Add to Round 2: link `verification.md` from the
evidence README; for SLOPPY 6 use the verifier's explicit X_+- compact-core points (m + e3, 0, -+i m +- i e3),
m = e1 - i e2, where the compact stabilizer is su(2) + u(1) and the fiber is 2 V_0 + V_1. Do not edit the verifier's
three files.
