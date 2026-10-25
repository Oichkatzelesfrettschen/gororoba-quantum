# DAS MERGUS companion: adversarial review of the algebra and geometry claims

Reviewed 2026-10-25 against current main `90339b6` (registry) and the proof
baseline `ec75554` (cd_core, witness records; cd_core is byte-identical on
both). Scope: chapters 02, 03, 05 and 06 of the companion and the
algebra/geometry statements of its README and abstract. The claim ledger is
[2026-10-25-das-mergus-algebra-claims.json](2026-10-25-das-mergus-algebra-claims.json).

## Findings

The central mathematics holds. An independent determinant test, built from
`cd_core.cd_sign` with flint and none of the companion's code, confirms
`det_R L_y = N^4 |Q(z) G(z)|^4` for doubly pure y in dimension 32
(z = p + iq, Q = z^T z, G = Q^2 - 4 Delta). It agrees at 30 random integer
points in [-1e6, 1e6] and 200 points in [-1, 1]. Each of three mutations
breaks agreement at 10 of 10 points: one flipped structure constant
(e3 e5), a swapped coordinate pairing, and mu^2 replaced by -mu^2. The
Schwartz-Zippel bound is below 1.6e-5 per large-range point, so this is a
randomized proof of the polynomial identity, not a deterministic one. The
companion's coefficient-exact Pfaffian certificate supplies the
deterministic version. Its rerun is reproduction only.

Two companion results answer questions the registry marks open.

- **Universal A_5 Stiefel inclusion (Theorem G10).** This bears on
  `a5-stiefel-universal` (open). The written proof survives a step-by-step
  audit:
  - a nonzero Delta gives a nondegenerate quaternion subalgebra H of the
    complexified octonions, even when u and v are isotropic;
  - B = H + H is closed under the product and alternative;
  - z^2 = -Q, and zw + wz = -2 z.w for pure z and w;
  - the open set Delta != 0 is dense in the irreducible quadric Q = 0;
  - the transport step is already certified in `a5-nullity12-quadric-germ`.

  Supporting computations:
  - 40 random Gaussian-rational Stiefel points all have exact nullity 4.
  - Three random A_6 Stiefel points have nullity 0, consistent with
    `a6-stiefel-generic-invertibility`.
  - The decisive chain runs through the registry's own reduction. The
    large-range determinant identity, combined with the registry identity
    |det L_(a,b)| = |Pf(L_a + i R_b)|^4 (`a5-stiefel-pfaffian-reduction`),
    gives |Pf(L_a + i R_b)| = N |Q G|. That polynomial vanishes on the whole
    Stiefel set, which is exactly what the registry boundary says a proof
    needs.
  - Corroboration only: det_C(L_a + i R_b) = (N conj(Q G))^2 holds at 8
    small-range exact points. The Schwartz-Zippel bound is weak there, about
    0.25 for all 8 together.
- **Two-dimension gap at the twelve witnesses.** This bears on
  `a5-nonzero-divisor-two-dimension-gap` (open). At the twelve
  non-zero-divisor witnesses, my own exact Jacobian ranks of the companion's
  defining equations equal my own Schur tangent dimensions, as cone
  dimensions:

  | Rows | Equations | Cone dimension | Unit dimension |
  |---|---|---:|---:|
  | 1, 8, 15 | V | 16 | 15 |
  | 4, 11, 18 | Q plus the 35 quartics | 22 | 21 |
  | 5, 12, 19 | G = 0 | 28 | 27 |
  | 6, 13, 20 | Q = 0 | 28 | 27 |

  The global inclusions come from three sources:
  - the determinant identity, for nullity 4;
  - 15 exact and 5 floating chart points, all of nullity 8, for the
    incidence family;
  - the established quadric-germ claim, for nullity 12.

  For the incidence family, the Jacobian rank of 74 equations bounds the
  dimension only from above. The lower bound comes from the chart itself:
  - its holomorphic Jacobian has complex rank 11 (real 22) at rows 4, 11 and
    18 (`check_chart_dim.py`);
  - it reproduces each witness to within 4e-16.

  Rows 1, 8 and 15 are e1+e25, e2+e26 and e3+e27, the points
  `a5-nullity12-quadric-germ` already establishes. The nullity-8
  universal inclusion rests on imported G2(C) transitivity and the
  companion's 455-Pfaffian certificate. I did not re-derive either; my
  random points are strong but not universal evidence.

Act on both by admitting them as new evidence. Each needs its own
source-bound record and gate before either registry status changes. The
companion did not modify the registry.

The README's two "historical repairs" correct nothing the repository asserts.

- **Associator constant 4.** No constant-2 associator claim exists in the
  places searched: the registry, docs/notes (md and tex), docs/evidence,
  proofs, gororoba_quantum, scripts and
  `docs/sources/open_gororoba/cayley_dickson_evidence_contracts.txt`. The
  theorem is still correct:
  - Exact cd_core arithmetic on a = e1+e10, b = e4+e15, c = e2-e9 gives
    [a,b,c] = -8e7 + 8e12 and a squared ratio of 16.
  - The sign mutation c = e2+e9 gives 0.
  - The two-term maximum is 4.000, and a random ascent reaches 3.926.
  - The upper bound follows from kappa_4 <= sqrt2, attained at e1+e10.
- **Fold/average is not a homotopy transfer.** This is already stated in
  `docs/notes/open_gororoba_folding_proofs.md` lines 44-57, with
  `MinimalUncurvedObstruction.v`. The new and correct content is narrower:
  - m2(x, y) = yx, exhaustive on 64 basis pairs;
  - the decomposition [x,y,z]_m2 = p[ix,iy,iz] - T3, holding on 512 of 512
    triples. Dropping the first term breaks it on 336 of the 512 triples.

## Verdict counts

| Verdict | Count |
|---|---:|
| confirmed | 37 |
| already-in-repo | 16 |
| refuted | 1 |
| unproven | 1 |
| stale | 0 |
| **total** | **55** |

Of the 37 confirmed items, 36 rest on an independent check. The
reproduction-only item is `G-minors-4096`: the 12x12 kernel-minor
determinant -4096 and the 20x20 pivot determinant 16 at e1+e25. All five
companion scripts reran byte-identically to the delivered records
(`das-mergus-checks/algebra/companion-rerun/`). Nine confirmed items rest on a
written-argument audit without a dedicated computation: G7, G8, G13,
C2-prop1.4, C2-MMdagger, C2-lemma3, C5-standard, C5-lower-bound-higher and
G-3.7-composition. The other 27 confirmed items have an independent
computation behind them.

Actions:
- 2 registry corrections, pending admission: `a5-stiefel-universal` and
  `a5-nonzero-divisor-two-dimension-gap`.
- 6 new-evidence candidates:
  - the explicit QG factorization;
  - the singular locus of V;
  - the exact rank-transition paths;
  - the rank-boundary sector;
  - m2 = yx;
  - the Walsh discrimination propositions.
- 1 reject.

## Refuted

- **21^17 in 03-rank-geometry.md line 1169.** The chapter prints
  30,041,942,495,081,690,076,421. Exact integer arithmetic (python, bc)
  gives 30,041,942,495,081,691,894,741, and the float rounding gives
  ...690,824,704; the printed digits match neither. The error is cosmetic:
  the bound is an order-of-magnitude multiplicity, and 29^5 and 25^11 are
  correct. The repository states only "about 3.0e22". Correct the digits
  before any reuse.

## Registry-affecting items with their decisive computations

| Claim | Registry entry | Decisive independent computation | Mutation or control |
|---|---|---|---|
| G12 membership, det L_y = N^4 abs(QG)^4 | none (extends `sedenion-determinant-membership` to 32D) | 30/30 + 200/200 exact agreements (`check_det_membership.py`) | 3 mutations, each 10/10 disagree |
| G10 Stiefel inclusion | `a5-stiefel-universal` open | 40/40 Stiefel points nullity 4; abs(Pf(L_a + iR_b)) = N abs(QG) from the determinant identity and the registry reduction | A_6 random Stiefel points nullity 0 |
| Twelve witness germs | `a5-nonzero-divisor-two-dimension-gap` open | Jacobian rank = Schur tangent at all 12 rows (`check_witnesses.py`) | G.I9: y4 with Q=G=Delta=0 has nullity 4, y8 has 8 |
| G16 incidence chart in R_8 | same | 15/15 exact chart points nullity 8 (`check_strata.py`); 5/5 float at generic complex u (`check_cz_ranks.py`); chart complex rank 11 at rows 4, 11, 18 (`check_chart_dim.py`) | eigenspace-mixed y4 (G.I9) |
| G6/G.37 singular locus | extends `a5-nullity12-quadric-germ` | S+- nullity 16 at 10/10 points; V regular nullity 12 at 15/15 | isotropic w with lambda = 2i gives 12 |
| G14 Z component in R_8 | none | 15/15 random Z points nullity 8 | none |

Further independent confirmations:
- Pfaffian cofactors (G.P2, G.P3) agree to relative error 1.2e-14 at 10
  float points; the mutation 4Delta -> 3Delta leaves an error of at least
  0.042.
- The rank law nu = 28 - 2 rank C_z (G.P6) holds on six strata.
- On V, rank B = rank C_z - 2 (G.40): 6 on the regular part, 4 on the
  singular set.
- The characteristic polynomials (G.I11) and (G.50a) agree at 40 rational
  parameter values. Every coefficient has degree at most 32 in the
  parameter, so 40 agreements prove the identities.
- The chapter-5 sedenion characteristic polynomials for L_z and C_z agree at
  20 exact random points.

## Opposition

- **Membership criterion.** "Central new exact result" over-states novelty.
  Two parts are already published and cited in the repository:
  - Koebisu 2608.08232 Theorem 5.3 and Corollary 7.1: det L_x = N^2 E7^2,
    with E7 = 0 exactly on the zero divisors in dimension 32;
  - BDI Corollary 9.3: zero divisors are doubly pure.

  The new content is the closed form E7 = N |Q|^2 |G|^2 on the doubly pure
  space. Q and G are the sedenion factors D1 and D2 (Koebisu Theorems 3.7
  and 3.9, registry `sedenion-determinant-membership`) evaluated at the
  complex point z = p + iq. The cross-link above shows the same thing
  through the registry's L_a + i R_b. The supported reading: "the 32D
  determinant factor is the complexified sedenion factorization, giving two
  real irreducible 28-dimensional components {Q=0} and {G=0}." Literature
  priority for that closed form was not checked.
- **Stiefel theorem.** The written proof imports standard facts:
  - Artin's theorem;
  - alternativity of the doubled quaternion algebra over C;
  - irreducibility of a rank-15 quadric.

  The G12 identity gives a second, independent route. Moreno's question may
  have a published answer that this review did not search for. Neither
  route is formalized.
- **Germ results.** These are statements at finitely many retained
  witnesses, not a stratification. For the nullity-8 piece the chart is the
  open set U != 0, n != 0; points with U = 0 are untreated, as the chapter
  says. The weaker statement the evidence supports without imported
  transitivity: "the incidence chart lies in R_8 at every tested exact
  point, and the germ equality holds at rows 4, 11 and 18 given that
  inclusion."
- **"Proof" labels.** G12 is a finite symbolic certificate plus written
  algebra. G16 adds imported group theory. G8, G7 and G13 are written
  arguments. None is Rocq-formalized. The companion says so, and the
  abstract's "written proofs and exact computational certificates" is
  accurate.
- **Associator 4.** It is correct but elementary: the sqrt2 sedenion norm
  bound plus one witness. Present it as a new small note, not as a repair.
- **Fold/average.** The repository already holds the verdict, so present
  only m2 = yx and the decomposition identity as new.
- **Chapter 3.2-3.4 and 3.6.** These sections re-present the established
  claim `a5-nullity12-quadric-germ`: the 168-coefficient identity, the
  transport, the containment of V in R_12, the cubic kernel, the Hilbert
  series, degrees 14 and 196, the A15 germ and the path (G.43). Credit them
  to the repository.
- **Documentation drift.** `docs/notes/topics/cd-star-lattice-tower.md`
  lines 212-216 still list the Rocq basis-sign bridge as open, while
  `cd-sign-python-semantics-rocq` proves it. Fix the note; the mathematics
  stays unchanged.

## Method and replay

The independent scripts live in [das-mergus-checks/algebra/](das-mergus-checks/algebra/), with
their outputs beside them. They import cd_core from the checkout `REVIEW_REPO` names (ec75554) and run under the CI
interpreter (Python 3.14.7; numpy 2.5.4, sympy 1.14.0, python-flint 0.9.0):

| Script | Checks |
|---|---|
| `check_det_membership.py` | determinant identity, mutations, purity, Stiefel points, A_6 control |
| `check_strata.py` | V, S+-, Z and incidence-chart nullities; G.I9; characteristic polynomials; sector identities; chapter-5 characteristic polynomials |
| `check_witnesses.py` | witness membership, Jacobian ranks, Schur tangents |
| `check_pf_crosslink.py`, `check_pf_cofactors.py`, `check_cz_ranks.py`, `check_chart_dim.py` | Pfaffian cross-checks, rank laws, nullity-8 chart rank |
| `check_small.py` | chapter-2, chapter-5 and chapter-6 items |

Every random seed comes from the ANU QRNG draw
`docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json`, cited at each use;
the reseeded rerun left every verdict field unchanged. Floating checks
(`check_cz_ranks.py`, `check_pf_cofactors.py`) corroborate and certify
nothing.

## Scope cut

- **Narrative skipped.** 12 narrative or methodological blocks carried no
  checkable assertion:
  - ch2: scope paragraph, Section 10 boundary prose, Section 11 synthesis
    paragraph;
  - ch3: 3.13 obligations, closing synthesis;
  - ch5: opening, moving-kernels discussion, gate-set tomography paragraph,
    integration paragraph;
  - ch6: fractional levels and K-theory, physical-interpretation section,
    surreal set-theory remark.
- **Out of scope.**
  - Chapter 5's identifiability rank 87 with 171 null directions: ledgered
    `unproven`, arithmetic only.
  - Its raw-count affine rejection and the chapter-6 relativistic scale
    numbers: optics and physics reviewers.
  - The README census counts (225 claims, 414 bindings, 18,277 files):
    provenance reviewer.
- **Not run.**
  - An independent re-derivation of the 455 canonical Pfaffians and of the
    G2/SL3 equivariance step.
  - A Groebner verification of primeness, normality and Gorenstein claims
    (G5-G7, G13).
  - A literature search for prior answers to Moreno's Stiefel question or
    for the explicit QG factorization.
