# A_5 kernel bundles: program goal (roadmap item 5)

This file is the goal objective of the Codex program on branch `geometry/a5-kernel-bundles`, worktree
`~/worktrees/IBMQuantum/a5-kernel-bundles`. The orchestrator (a Claude Code session) updates it in place. Re-read it at
every item boundary and after every context compaction. The ledger
[docs/evidence/a5-kernel-bundles/ledger.md](../evidence/a5-kernel-bundles/ledger.md) records state, and this file sets
the order.

The task is roadmap item 5 of `dimension32-global-topology`: determine the kernel bundles of the A_5 zero-divisor strata,
meaning their actual transition data, equivalence classes and invariants. The first deliverable covers every smooth
piece of D_(5,12). Item 5 is a debugging and decomposition program. Find out what is true, decompose it into checkable
statements, and above all surface the structural facts and questions the orchestrator has not thought to ask. A clever
reformulation that collapses the problem is worth more than a brute-force atlas.

## 1. What is established (read these before anything else)

Repository rules: `AGENTS.md` (root) and `ci/AGENTS.md`. The **Computer algebra** paragraph of `AGENTS.md` is binding:
Singular in global orderings only, local invariants by the deformation to the normal cone.

| Fact | Authority |
| --- | --- |
| Multiplication convention: (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)); `cd_core.cd_sign`, `cd_multiply_exact`, `left_mult_matrix_exact(32, y)` | `gororoba_quantum/cd_core.py` (never edit it: seven gates bind its bytes) |
| Every A_5 zero divisor is doubly pure, y_0 = y_16 = 0. Put z = p + i q in C^15, z_k = y_k + i y_(16+k), k = 1..15 | [strata record](../evidence/a5-zero-divisor-strata/README.md), Theorem 1 and Conventions |
| C_z is the 15 x 15 Im-block of left multiplication by z on Im(A_4)_C, skew, with C_z z = 0. nullity L_y = 28 - 2 rank C_z, so nullity 4, 8, 12, 16 means rank C_z = 12, 10, 8, 6 | strata record, Theorem 2 |
| Transport: phi(r, s) = r + i conj(s) is an R-linear bijection R^32 -> C^16 with phi(y x) = A(z, conj z) conj(phi(x)) (the outer conj coefficientwise), A(z, t) = [[0, -t^T], [t, C_z]]. So with psi = conj o phi, **ker L_y = psi^-1(ker_C A(z, conj z))** and phi(ker L_y) = conj(ker_C A), complex dimension k/2 for nullity k. Verified at the seven nullity >= 12 representatives (ledger row 1); phi(J x) = i phi(x) | [Pfaffian record](../evidence/a5-stiefel-pfaffian-germs/README.md), item 2 (gate core-690) |
| J = L_(e_16) has J^2 = -I and anticommutes with L_(e_k) for every k outside {0, 16}, so J L_y = -L_y J for doubly pure y and **J preserves ker L_y** | strata record, finite computation 1 |
| Split coordinates z'_k = i^(-popcount k) z_k: the 14 derivations of the split octonion table (Lie algebra of G_2(C)) act on u' = z'_1..7 and v' = z'_9..15 alike and fix mu' = z'_8; eta = diag(-, -, +, -, +, +, -) | strata record, Conventions |
| R_8 minus 0 is the disjoint union of twelve orbits of H = G_2(C) x SO(2, C) x C^*. SO(2, C) is the boost (u', v') -> (c u' + s v', s u' + c v') | [regularity record](../evidence/a5-strata-regularity/README.md), Theorem 2 |
| Orbits of nullity >= 12 (the scope of the first deliverable), with complex dimensions: B9 (9), V (8), VB = V n B9 (7), V^a_+ and V^a_- (7), N_+ and N_- (6, nullity 16). Representatives: `REPS` in [strata_regularity.py](../evidence/a5-strata-regularity/strata_regularity.py) (split coordinates) | regularity record, closure table |
| Orbits of nullity 8: W8 (12), E8-bar (11), Iso (11), X_+ and X_- (10) | same |
| Singular loci, closure order, Whitney stratification, transverse germs; normal link of R_12 at x0 = e_1 + e_18 is S^1 disjoint union S^3 | regularity record, Theorems 3-6 |
| D_(5,k) is the unit section of the cone S_k under y in R^30 = C^15. Unit section of N_+- is V_2(R^7) | strata record, Conventions; regularity record, Real and complex |
| Sedenion precedent: the unit zero-divisor pair bundle of A_4 has quaternion frames, and right quaternion multiplication gives a principal SU(2) action. The roadmap warns that this "does not automatically extend to every kernel bundle" | `gororoba_quantum/sedenion_bundle.py`, `gororoba_quantum/RANK_STRATUM_TOPOLOGY.md` (chart transitions, roadmap items 4-8) |
| Constant-rank charts with exact rational frames, `chart_transition(source, target)` and the Gram-metric transition rule | `gororoba_quantum/rank_charts.py`, RANK_STRATUM_TOPOLOGY.md |
| Earlier kernel-attachment work (sedenion and selected-center): annihilator kernel limits, attachment image S3*(S1 x S3); the selected-center Schur chart with V spanning ker L_x0 | [kernel_limits](../evidence/kernel_limits/README.md), `docs/notes/annihilator_kernel_limits.md`, `docs/notes/nullity_twelve_local_geometry.md`, `docs/notes/dimension32_skew_schur_charts.md` |

## 2. Where the gaps are (state of knowledge, not instructions)

- **G1. The orbit group does not obviously act on kernels.** The twelve orbits come from H acting on z
  holomorphically. Kernels are ker A(z, conj z), which depends on conj z, so an element g carries kernels to kernels only
  if conj(g z) is compatible with g: real forms, and only in the coordinates where they are real. Inference, unchecked:
  the subgroup acting on kernels is the compact G_2 (real in original coordinates, the octonion automorphisms) times
  U(1) (the phase z -> e^(i theta) z, which rescales the blocks of A) times R_+. Its real orbits on a complex orbit O
  have real dimension at most 16, against 2 dim_C O (up to 24), so each complex orbit would carry continuous moduli of
  real orbits. Then no homogeneous associated-bundle shortcut exists over a whole orbit.
- **G2. The boost has no linear lift.** The regularity record found no constant X, Y with C_(Az) = X C_z + C_z Y for the
  original-coordinate rotation of (u, v). Whether any real lift transports ker L_y is unknown.
- **G3. Orbit unit-section topology is unknown** except for N_+- (V_2(R^7)): no pi_1 or cohomology of the unit sections
  of B9, V, VB, V^a_+- (or the nullity-8 orbits) is computed.
- **G4. No closed-form kernel.** A basis of ker A(z, conj z) polynomial in (z, conj z) on an orbit would give global
  sections and decide triviality questions directly. None is written down. C_z z = 0 and the cross-product identities
  suggest candidates built from z, conj z, products and cross products.
- **G5. The complex structure.** J makes ker L_y complex of rank k/2. Under phi, J may act complex-linearly or
  conjugate-linearly on ker A. Whether there is a second anticommuting structure, which would make ker L_y quaternionic
  as in the sedenion case, is unknown.
- **G6. What "equivalence class" means.** It could mean real, complex, quaternionic or flat. It is undecided which
  structure group the transition data actually lands in: GL(k, R), U(k/2), Sp(k/4), a finite group, or a compact group
  with a flat connection.

## 3. What we are looking for

Deliverables, in priority order. Each lands in `docs/evidence/a5-kernel-bundles/` as code plus a written result with
falsifiers.

1. **The kernel symmetry group.** This is the largest real Lie group K of pairs (g, h), g real-linear on the doubly pure
   space R^30 and h in GL(32, R), with L_(g y) h = h' L_y for some h' and h mapping ker L_y onto ker L_(g y). Compute
   its identity component (Lie algebra by an exact linear solve), its finite part if visible, and the real dimension
   of its orbits on each complex orbit's unit section. This settles G1 and G2.
2. **A closed-form kernel frame** on each orbit of nullity >= 12, polynomial or rational in (z, conj z), verified
   exactly, with the locus where it degenerates. Settles G4.
3. **Transition data.** Give a finite atlas of exact local frames over each smooth piece of D_(5,12) (unit sections of
   B9, V, VB, V^a_+-, N_+-), transition functions verified exactly on overlaps, and the structure group they land in.
   Settles G6.
4. **Invariants.** Give the characteristic classes in the structure group found (Stiefel-Whitney, Chern under J,
   quaternionic if G5 holds), the monodromy over pi_1 of each unit section, and the unit-section topology needed to read
   them (G3). Then decide which bundles are trivial, which are isomorphic to a named bundle (tautological, tangent,
   Stiefel or Hopf), and how the bundles over adjacent strata compare.
5. **Stretch.** The same for the nullity-8 orbits, and how kernels of nullity 12 specialize to nullity 16 along
   N_+- (the input roadmap item 6 needs).

## 4. Questions we did not think to ask

This section is a standing deliverable. Keep a list in the ledger of questions the orchestrator did not pose. For each,
give why it matters, the cheapest decisive probe, and the result once run, and run the cheapest ones. Seeds, to be
replaced by better ones:

- Is ker L_y, for y in a nullity-12 or -16 orbit, the kernel of a smaller algebra structure (a quaternion or octonion
  subalgebra, an A_4 inside A_5, an annihilator ideal), so that the bundle is induced from a known one?
- Does ker L_y determine y, or the complex orbit point z, up to the kernel symmetry group (the kernel map
  y -> ker L_y into a Grassmannian)? What is the image, and is the map an embedding of each unit section?
- Do the left and right kernels (ker L_y and ker R_y) coincide, differ by J, or form a pair bundle? Do partner pairs
  (x, y) with x y = 0 form a correspondence whose fibers are kernels on both sides?
- Is there a flat structure, kernels locally constant along K-orbits, that reduces item 5 to a representation of
  pi_1 of each unit section?
- Does the orbit decomposition by H refine into a finer decomposition by the kernel symmetry group K? Would that finer
  stratification, not the twelve H-orbits, be the right base for items 5 and 6?

## 5. Behavior required

- Exact arithmetic only: integers, Fractions, Gaussian rationals, python-flint, Singular over Q or Q(i). A numerical
  probe may suggest a conjecture and is labeled as such; it never enters a claim.
- State the falsifier before each probe, in the ledger. A result that deviates from prediction is the finding.
  Separate observed from inferred, and mark a check that did not run as `not run` with the reason.
- Code lives in `docs/evidence/a5-kernel-bundles/` (scripts with `--self-test` mutation controls that must fail when the
  property is removed, and `--out result.json`). It imports cd_core and may import helpers from
  `docs/evidence/a5-strata-regularity/strata_regularity.py` and
  `docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py`. Follow the root `AGENTS.md` code style: ruff
  format, ruff check and mypy through `ci/pinned_tool.py` on every touched file, no `assert`, explicit raises,
  `parallel.ordered_map` for every loop over independent items (script builders included), Python started with
  `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` and invoked as `"$PYTHON"`.
- No random seeds are needed. If one becomes necessary, stop and record it as an owner decision; the repository
  requires QRNG seeds.
- Write results as you go: the ledger (a dated row per sub-step with probe, falsifier, outcome and evidence path), and
  `docs/evidence/a5-kernel-bundles/README.md` for durable statements with proofs. Use the voice of the existing evidence
  READMEs: mechanism first, American spelling, emoji-free, no local absolute paths.
- The sandbox keeps git metadata and `~/.cache/gororoba-quantum` read-only, so the agent does not stage or commit and
  does not run `ci/pr_checks.sh`. At each sub-step boundary it leaves the files in the worktree, adds the ledger row,
  and ends the turn. The orchestrator reviews, runs the repository lanes and commits with the trailer
  `Assisted-by: Codex CLI (gpt-daybreak-blue-latest)`. An uncommitted or staged completed sub-step never blocks the
  next one: continue immediately with the next item, keep each sub-step in its own new files where possible, and
  never treat a pending orchestrator commit as a blocker.

## Standing rules

- Authorized without asking: reading anything in the repository; creating and editing files under
  `docs/evidence/a5-kernel-bundles/` and the ledger; running Python, Singular, python-flint and the repository's local
  checks that need no shared cache lock; spawning no subagents.
- Owner-only decisions, recorded in the ledger as `BLOCKED: owner` and left for the orchestrator: adding or changing a
  claim in `docs/state/research_state.json`; editing any file outside `docs/evidence/a5-kernel-bundles/` and this
  file's ledger; scope beyond item 5 (items 6-8); any network access, provider job or QPU job.
- Hard boundaries: never `git push`, never open a pull request, never `git stash`, never `rm -rf` (use `trash-put`),
  never edit `gororoba_quantum/cd_core.py` or any retained evidence file of another record, never touch other
  worktrees or `~/.codex` or `/tmp` worktrees of other sessions. The host is shared (62 GiB): run every Singular
  process under `prlimit --as=8589934592` (8 GiB), set `GOROROBA_WORKERS=4` for pooled runs, and stop any computation
  that passes 15 minutes. Then record it and find a cheaper formulation (smaller slice, better coordinates, global
  ordering, a symmetry reduction).
- Turn length: end each turn at a sub-step boundary (a deliverable piece proved or refuted, a question run), about an
  hour at most. The goal continues on its own.
- Cap any sub-step at three failed attempts, record its blocker, move on.
- Done when deliverables 1-4 are complete or blocked on a named owner decision, section 4 holds at least five
  investigated questions, and the README states every result with its falsifier and evidence path.

## Handoff state (2026-10-26)

- Branch `geometry/a5-kernel-bundles` from main at 57ee0f9, with the AGENTS.md computer-algebra rule and this program
  file added by the orchestrator.
- Orchestrator correction: the transport identity carries the outer conjugation (Pfaffian record item 2); the facts
  table and item 1 now read psi = conj o phi. The `BLOCKED: owner` note of ledger row 1 is resolved.
- Committed after orchestrator review and replay: 1baaaee (transport with psi = conj o phi; J acts as i), a6268f8
  (constant symmetry algebra g_2 + four central directions, no boost lift, visible S_3 x Z_2 components). The
  orchestrator reproduced the unit-section orbit dimensions 14, 7, 11, 7, 7, 11, 11 with separate code.
- Consequence to build on: only N_+- is K-homogeneous. Correction (orchestrator, after the aligned-moduli result):
  the codimensions first written here were read at the recorded representatives, which are special points for K. An
  independent check at points moved by non-compact G_2 elements and the boost gives generic K-orbit dimensions on the
  unit sections B9 14 of 17, V 12 of 15, VB 11 of 13, V^a_+- 12 of 13: generic codimensions 3, 3, 2, 1 (B9 and VB
  unchanged at every tested point, V and V^a_+- jumping from 7). The recorded representatives of V and V^a_+- lie on
  a lower K-stratum (stabilizer su(3) at V^a_+-). So each piece is a family of K-orbits over a moduli space M, and
  each M carries its own stabilizer strata. The kernel bundle over a
  piece restricts to a homogeneous bundle on each K-orbit (stabilizer representation on the fiber) and varies over M.
  Item 2 and the transition data should exploit this: find M for each piece (explicit K-invariants separating
  orbits), the stabilizer type over each point of M, and whether the stabilizer representation on ker L_y is constant
  along M (then the bundle is pulled back from M times a homogeneous piece) or jumps (then the jump locus is a new
  stratum that the twelve H-orbits do not see). Exhaustiveness of the component group stays open and is not a
  blocker.
- Committed 7a8a329: Pfaffian-chart rational frames over N_+-. They are correct but generic (they frame any
  constant-rank skew family). Since N_+- is one K-orbit, its unit section is K / K_p with K_p the stabilizer of the
  representative, and the kernel bundle is K x_(K_p) ker L_p. The decisive output is the stabilizer K_p and its
  representation on ker L_p (complex dimension 8 under J), decomposed into irreducibles; global frames, triviality
  and characteristic classes then follow from representation theory. Prefer this over more chart atlases, and do the
  same on each K-orbit of the other pieces.
- Committed 453fd07: on N_+- the connected stabilizer is U(2) and ker L_p = V(0,-4) + 2 V(1,-3) + V(0,-2) +
  V(1,-1). Sharpest next question for N_+-: the unit section is V_2(R^7), whose integral cohomology is Z in
  degrees 0 and 11 and Z/2 in degree 6 and zero elsewhere (verify from a cited source or a cell structure before
  use). So the only possible nonzero Chern class of any complex summand is c_3 in H^6 = Z/2, and the only
  candidate obstruction to stable triviality beyond it lives in K-theory. Decide, per summand and for the total
  fiber: c_3 mod 2 (equivalently w_6), stable triviality, and actual triviality (rank versus dimension 11),
  using the homogeneous description G_2 x U(1) over U(2) (Borel-Hirzebruch weights) or an explicit
  clutching construction. Then the same for the nullity-twelve pieces along their K-orbits.
- No jobs in flight.

## Order

1. **Kernel symmetry group (deliverable 1, gaps G1, G2, G5).** Verify ker L_y = psi^-1(ker A(z, conj z)) and the
   action of J on it at every representative. Solve for the Lie algebra of K. Test the compact G_2, U(1) phase, R_+ and
   the boost explicitly, at least at one representative of each nullity >= 12 orbit. Acceptance: an exact Lie algebra
   with its dimension, a statement of which H-directions lift, and orbit dimensions. Falsifier: a non-lifting direction
   that transports kernels anyway, or a lifting direction that fails on one representative. Evidence:
   `kernel_symmetry.py`, `result.json`.
2. **Closed-form kernel frames (deliverable 2, G4).** Acceptance: exact verification L_y x = 0 for the frame vectors
   on a parameterized family covering each orbit, with the degeneracy locus. Falsifier: a point of the orbit where the
   frame loses rank outside the stated locus.
3. **Unit-section topology (G3)** for B9, V, VB, V^a_+-, as homogeneous spaces of the compact real forms where they
   are, or by explicit fibrations. Acceptance: pi_1 and the cohomology needed in item 4, each with its argument.
4. **Transition data and structure group (deliverable 3, G6).** Acceptance: an exact atlas, cocycle identities
   verified, structure group identified with a proof.
5. **Invariants and equivalence classes (deliverable 4).**
6. **Section 4 questions**, interleaved: run the cheapest probes as soon as the needed tools exist.
