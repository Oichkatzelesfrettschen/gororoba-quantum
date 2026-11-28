# A_5 nullity transitions: program

This note states what is established about passages between the annihilator dimensions of A_5, what is open, and
the next computations with their acceptance checks. The exact record is
[a5-nullity-transitions](../evidence/a5-nullity-transitions/README.md) (ledger rows A5-650 to A5-668, A5-670, A5-671); the
[review](../archive/reviews/a5-outside-transition-report/README.md) records where its paths come from. The
nullity-8 to nullity-12 and nullity-16 limits belong to the
[kernel-attachments program](a5-kernel-attachments-program.md) and the Lorentzian slice to the
[null-slice connections program](a5-null-slice-connections-program.md); this note links them and repeats none of
their tables.

## Four transitions, kept apart

| Transition | Map | Status |
|---|---|---|
| Algebra level, A_n to A_(n+1) | y -> (y, 0) doubles the kernel; a component on the doubling unit adds t^2 I to the Gram operator | proved for every level (A5-261); the Gram identity at levels 16 to 64 (A5-658) |
| Nullity inside A_5 | real lines 4 -> 8 -> 12 -> 16 with exact exceptional sets | proved (A5-650, A5-651) |
| First-order reduction at a junction | w -> K^T L_w K, a skew form on the endpoint kernel; its kernel is the limiting kernel when the rank is the nullity step | rank 4 at four junctions (A5-653); the full pencil at e_1 + e_10 (A5-654, A5-655) and its type at four W8 points (A5-659) |
| Description | Gram radical, skew two-form, kernel projector, Grassmannian point of one operator L_y | identities of A5-622 and A5-658; no new object |

## Mechanism at the W8 point e_1 + e_10

1. **Terms.** K is an orthogonal frame of ker L_y at y = e_1 + e_10 (dimension 8, Gram 2 I). For a direction w the
   line y + s w has L = L_y + s L_w, and the first-order condition for a kernel vector K c to persist is
   K^T L_w K c = 0.
2. **Coefficients.** Twenty imaginary units give the zero form. Units 9, 10, 25, 26 repeat units 2, 1, 18, 17 up to
   sign. Seven independent forms remain, on (e_1, e_2, e_8), e_16 and (e_17, e_18, e_24).
3. **Symmetry.** The commutant of the pencil is a quaternion algebra (dimension 4, noncommutative, negative-definite
   trace form) and the pencil generates sp(2), of dimension 10. A skew form with that commutant has rank 0, 4 or 8.
4. **Invariant.** Pf = 16 ((u.u + m^2 + v.v)^2 - 4 |u x v|^2). The coefficient 16 is the fourth power of the frame
   norm 2. With zeta = u + i v on (z_1, z_2, z_8), G = s^2 (zeta.zeta)(4 + 4 s zeta_1 + s^2 zeta.zeta) on the line,
   and Pf at m = 0 is |4 zeta.zeta|^2: the Pfaffian is the squared modulus of the tangent cone of G, and m, the
   coordinate on e_16, adds m^2 as the Gram identity of A5-658 requires.
5. **Real zeros.** m = 0 and zeta.zeta = 0: the isotropic vectors of C^3, a real 4-dimensional cone over
   V_2(R^3) = SO(3).
6. **Limits.** The limiting plane is the range of (I + n.E)/2 for three anticommuting involutions E_k and
   n = u x v / |u|^2, so the cone maps onto the conic of isotropic lines, a 2-sphere; the overlap 2 (1 + n.n') is 0
   for antipodal normals and 2 for perpendicular ones.
7. **Scope.** Of eight W8 points, six are quaternionic and two, both on gamma_2, have a scalar commutant and Lie
   closure so(8) (A5-659): the mechanism of item 3 belongs to the real point, and W8 is one orbit of the complex
   group only. The number of terms, the half the point lies in and proportionality of its halves each fail as the
   criterion.

## Deliverables

| # | Item | Depends on | Acceptance check |
|---|---|---|---|
| T1 | Proof of the overlap law over the whole Stiefel cone | A5-654 | done: the kernel identity modulo the Stiefel ideal and the Clifford relations (A5-655, proved) |
| T2a | done as a tested rule: the dimension of ker L_p n ker L_q (0, 2, 4) names the type R, C, H with closures so(8), su(4), sp(2) (A5-667, survives) | A5-659 | recorded |
| T2 | A proof of the three-type rule (the red-team derivation of the review record covers dimension 4; dimensions 1 and 3 never occur, since every common kernel of sedenion zero divisors is complex, A5-671, a result of Biss, Dugger and Isaksen). Two leads from the [certificate review](../archive/reviews/a5-pencil-certificates/README.md), both unrecorded computations. Hypothesis, reviewer-reported and not reproduced: in the normal form a = (t, kt), b = (alpha t, (alpha k) t) of the proof of Theorem 14.6 of Biss, Dugger and Isaksen, the operator J_k that acts as +L_k on H x H and -L_k on its complement commutes with all 31 compressions at six points, four of them with dim A = 2; falsifier: a nonzero entry of the symbolic commutator over alpha. Refutation, reviewer-reported and not reproduced: the elements of A do not generate the commutant, because their compressions on the kernel vanish. Then the real orbit structure behind it: the pencil type over the real orbits of W8 (the plane types of the strata record), and the rank-drop locus and limiting planes at a point with scalar commutant | A5-659 | a rule that predicts the type at points written before their runs, starting from the real G_2 invariants of the halves at the eight recorded points and from points drawn from a parametrization of the real points of W8; A5-660 decided in its second clause |
| T3 | Arcs into the W8 point beyond the 22 of A5-668 (twenty lines of zero first-order form, two curved arcs, all on the sphere): a proof for every arc, by the second-order Schur form of the nullity-8 record applied one stratum down | A5-668 | A5-660 decided |
| T4 | done for dimensions and algebras (A5-666) and for the Pfaffians at VB and N+-, each c \|lead Q\|^2 \|lead G\|^2 on the doubly pure coordinates (A5-657, proved; Q of order 1, G of order 2 at VB and 3 at N+-). Open: the locus of compression rank 4 at VB with its limiting kernels, and the full Pfaffian at N+- with the coordinate on e_16 | A5-666 | the real rank-4 locus tested on rational points |
| T5 | Closed Gauss graph of the nullity-4 stratum over a W8 point as a subset of Gr(4, 8), against the Nash blow-up question of the attachments program (section 5) | T1, T3 | the fiber over the point identified as a set with a two-sided certificate (A5-250 for this incidence) |
| T6 | done (A5-664, A5-670): sp(1), sp(2), sp(4), sp(8), sp(16) at levels 4 to 8, the last two by closure bounds that meet. Open: the statement for every level, pencil dimension 2^(n-2) - 1 and closure sp(2^(n-4)) at the embedded element; a derivation is in the review record | A5-664 | a machine proof in gororoba-math |
| T7 | Formal targets in gororoba-math: the Gram identity for the doubling unit at every level, the alternating three-form, the Pfaffian identity at e_1 + e_10, the anticommutation of L_(e_8) in A_4 with the evenness of common kernels (A5-671) | none | a pool row of the formal-proofs workgroup per target; proofs compile there |
| T8 | Hardware observable (hypothesis): overlaps of limiting planes read as contrasts of the coset-block kernel map on two nullity-4 operands near e_1 + e_10 | T1 | a written case and the owner's approval precede any device run |

## Track audit: how the parts connect, and the gaps

- **Chain.** `cd_core.cd_sign` fixes the product; `scripts/a5_*.py` build byte-stable records under
  `docs/evidence/a5-*`; each record has a gate pair in `ci/gates.json`; the claim ledger holds one row per
  statement; `docs/notes/topics/a5-exceptional-fiber-status.md` summarizes by date; gororoba-math holds the
  machine proofs and cites rows by path; open work sits in the pooled ledger of gororoba-infrastructure.
- **Gap 1.** The nullity-4 stratum has no kernel-limit record into any closure before this one (A5-389 open);
  T1 to T5 are the route.
- **Gap 2.** Closed: the pencils at VB and N+- are in the record (A5-666).
- **Gap 3.** The orbit classifier lives under an evidence directory and the record script imports it by path; a
  move into `gororoba_quantum/` is a separate change, since retained records bind the file's digest.
- **Gap 4.** The paper link stays a boundary (A5-628). A correspondence needs a non-abelian algebra or a positivity
  structure on the A_5 side that matches the corner charge; no deliverable here supplies one.

## Standard of the record as a data source

The record is byte-stable with source digests; its predictions precede the run and the failed clause is kept; each
README sentence has a `require`; controls fail on mutants; an implementation that shares no code reproduces the
first nine values; two red-team reports were reconciled against the source; scope is stated by the loop bounds (the
full pencil at one W8 point, its type at ten named points, 474 representatives and a census); novelty is bounded by the searches of
the prior-art note.
