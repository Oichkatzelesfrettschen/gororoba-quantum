# A_5 attaching data: are characteristic 0 and the kernel limits reachable from first principles?

Hypothesis under test (2026-11-09): the A_5 program cannot reach characteristic-0 statements or the kernel-plane
limits from first principles. This page tests it against the retained records of both A_5 programs, the
exceptional-fiber track ([findings](a5-exceptional-fiber-findings.md), [status](a5-exceptional-fiber-status.md)) and
the kernel-attachments track ([`evidence/a5-kernel-attachments/`](../../evidence/a5-kernel-attachments/README.md),
[program](../../design/a5-kernel-attachments-program.md)). Verdict: refuted for both, with three named gaps that
remain.

## The kernel limits are already the object both tracks compute

- **Identification (documented).** The decision record of the exceptional-fiber track adopts I = (G) as the
  Pfaffian kernel-coordinate ideal and states that "the fiber of (G) is what the attachment needs (the kernel limit
  set)" ([`working/decision-record.md`](../../evidence/a5-exceptional-fibers/working/decision-record.md), section 1).
  A point of Proj F(I) is the limit, along an arc, of the vector of Pfaffian kernel coordinates, and the embedding
  matrix of the Nakayama generators (`nakayama_rees_fibers.py`, `nullity16_rees_fibers.py`) carries it into the
  Pluecker space of the kernel. The status page's split of "directions" (layers 1 to 3) from "planes" (layer 4)
  therefore separates two presentations of one set, and its "not started" entry for layer 4 understates the record.
- **Kernel limits computed exactly (measured, both characteristics).** The kernel-attachments track gives the
  limit sets:
  - eight first-order-resolved incidences of nullity 8 to 12, by one holomorphic Schur blow-up, with dimension,
    degree and components equal modulo 32003 and over Q(i) (README, "Holomorphic Schur blow-ups");
  - seven higher-order incidences, by Schur-corrected second-order forms on exact arcs, including the finding that
    the first-order direction does not fix the limit plane for W8 -> VB (README, "Second jets");
  - six higher-order Rees fibers (X+- -> VB all of P^2, Iso -> VB all of P^3, W8 -> VB all of P^4, E8-bar -> V^a_+-
    two disjoint planes), equal modulo 32003 and over Q(i) (README, "Nakayama-reduced Rees fibers");
  - eight nullity-16 Rees fibers (B9, V, VB, V^a_+- into N+-), equal over Q(i) and modulo 32009 under both roots
    of -1 (README, "The nullity-16 Rees fibers").
- **The ten nullity-8 -> nullity-16 rows** (E8-bar, Iso, W8, X+-, into N+-) blocked at the 300-second Rees gate in
  that track, and the exceptional-fiber track carries them by the degree-by-degree rank. For W8 the result is a
  kernel limit set: Proj F(I) = V(K2) = C20 cup C30 over F_32009 and F_32029 (A5-062, A5-066, A5-008).

## Characteristic 0 is reachable, and partly reached

- **Reached:** every kernel-attachments row above that completed over Q(i) is a characteristic-0 statement, with
  the modular fibers as the cross-check.
- **Reachable for the ten blocked rows (inference with a stated mechanism).** The headers of the exceptional-fiber
  track are specializations: `a5-kernel-attachments/fiber_inputs.py` regenerates them from the Q(i) producer
  (`nullity16_rees_fibers` phase one) at p = 32009, i = 10754, so J and G exist exactly over Q(i). An h_d proved
  modulo p transfers to Q(i) under three checks, each a finite computation:
  1. **Good reduction of J and G:** the reduced standard basis of J over Q(i) has p-integral coefficients and
     reduces to the header's J, and G reduced modulo J reduces to the header's G. Ran 2026-11-09 (A5-247).
  2. **Upper bound over Q(i):** the degree-2 fiber relations, the quadrics q with q(G) in J + m I^2 (the membership
     the modular receipts compute; q(G) in J alone is far stronger and would reject correct lifts), computed
     over (0, i). The direct computation (the receipts' membership driver run over (0, i), `quadric_lift.py`) stalled
     at the 3-hour cap on X- -> N- (A5-248), so the route avoids the Q(i) standard basis: compute each relation's cofactors in J + m * products modulo
     several primes, reconstruct them over Q(i), and check q(G) = sum a_k J_k + sum b x P as a polynomial identity. Rank is lower semicontinuous under reduction, so a Q(i)
     space of relations reducing onto K2 mod p has dimension at least that of K2 mod p, which gives h_d over Q(i)
     at most HF(k[y]/K2 mod p, d), the certified value, in every degree K2 generates.
  3. **Lower bound over Q(i), repaired criterion:** good reduction of the
     ambient quotient J + m^N does NOT by itself transfer truncated fiber ranks.
     The computed quantity is a rank difference
     r_N(d) = rank([W_N | P_d]) - rank(W_N), where W_N is the image of
     m I^d in the truncated ambient space, and P_d denotes the columns from
     I^d. Specialization can lower BOTH ranks; their difference need not be
     lower semicontinuous. The ideal under "Failure mode" below is an exact
     counterexample at both 32009 and 32029 with the same degree-2 relation space.

     **Correct finite-matrix transfer gate.** Establish a common integral
     truncated ambient matrix model, compatible source-generator and column
     reduction, and the equality

         rank_Q(i)(W_N) = rank_Fp(W_N).

     Then rank_Q(i)([W_N | P_d]) >= rank_Fp([W_N | P_d]),
     so r_N,Q(i)(d) >= r_N,Fp(d). The bound on the full fiber dimension
     follows from the truncated-fiber lower-bound construction.
     This is a sufficient, not necessary, condition. It must be checked
     separately for each pair, degree, order, and prime used.

     **Implementation.** Run scripts/a5_char0_rank_gate.py with a JSON
     object containing 'prime', 'i_root', 'W', and 'P'. Rows represent
     common ambient coordinates; matrices share their row count.
     Coefficients are integers, rational strings, or [real, imaginary]
     Gaussian-rational pairs. The checker reduces the same exact matrices
     modulo the requested split prime, rejects noninvertible denominators,
     and reports both ranks and both differences. Use --require-stable to
     reject unverified subtracted-rank equality. The checker does NOT
     establish that supplied matrices represent the original ideal,
     or certify the common integral ambient model: retain those witnesses
     separately. The regression test reproduces the two-prime rank-loss
     mechanism and a stable positive instance.

  **Repaired proposition (one pair, one degree d, one split prime p).**
  Suppose (a) the retained original J and G admit compatible integral
  specializations in a common truncated ambient R-module, (b) exact
  characteristic-zero quadratic relations reduce to enough rows to prove
  the desired upper bound, (c) W_N and P_d are represented by common
  integral matrices in the same ambient basis, and (d) the rank of W_N
  is unchanged at p. If the modular truncated lower bound equals the
  modular quadratic upper bound, the characteristic-zero fiber dimension
  equals that common value. Claims about radicality, components, real
  arcs, or all degrees require independent certificates.

  **Failure mode.** For I =
  (x^7, y^7, x^4*y^2*(c+x)), with c = 32009*32029,
  the degree-3 order-22 difference is 9 over Q but 10 at both
  primes: (c + x)^3 g1^2 g2 = x^2 y g3^3 puts c^3 g1^2 g2 into m I^3 over Z,
  so that class dies wherever c is a unit and survives modulo a prime dividing c.
  Good ambient reduction and unchanged quadratic relations
  do not prevent the discrepancy. This tree holds no producer or record of that computation. No unverified modular lower bound
  may be labeled a characteristic-zero result.

## What stays open

1. **The real semialgebraic limit set.** The kernel-attachments program requires a two-sided certificate: which
   limits real arcs realize, which can be strictly smaller than the real points of the complex fiber (program,
   deliverable 1). No record supplies it for any incidence.
2. **The ten blocked rows over Q(i):** check 1 ran on 2026-11-09 and survives on all ten pairs at both primes
   ([`evidence/a5-char0-transfer/`](../../evidence/a5-char0-transfer/README.md), ledger A5-247): J has an
   integer reduced standard basis over Q(i) whose reduction equals the F_p basis, G matches, and a corrupted
   coefficient breaks the equality. The ambient good-reduction component of check 3 survives for X- -> N- at N = 4, 8, 11, 15 and 18 (A5-249; `truncation_check.py`), but the subtracted-rank equality remains unproved; check 2 stalled on that pair at the 3-hour cap (A5-248, `quadric_lift.py`; the next attempt checks modular cofactors reconstructed over Q(i) as polynomial identities, avoiding the Q(i) standard basis). The opposite-sign X incidences need neither check: their arc certificate replays exactly over Q(i) and gives F(I) = Q(i)[y1, y2, y3] in every degree (A5-270, `x_opposite_qi.py`), the first all-degree fiber statement in characteristic 0 on the fiber track. Conjecture for check 2: the degree-2 relation space
   {q : q(G) in J + m I^2} over Q(i) has the dimension of K2 mod p and reduces onto it at both primes; the
   cheapest instance is X- -> N-, falsified by a dimension or a reduced basis that differs.
3. **The fiber-track open cells:** E8-bar -> N+- degree 6, the VB degree-3 component (A5-016), and the all-degree
   claims for Iso, X and E8-bar.

## Scope in the roadmap

The findings-note roadmap item 10 (characteristic 0) is the Q(i) transfer above; item 6 (attaching maps) consumes
the limit sets. The kernel-attachments program orders the same work as deliverables 1 (8 -> 12 limit sets), 2
(12 -> 16 and 8 -> 16), 3 (compatibility) and 4 (attaching maps): deliverable 2 is complete for eight nullity-16
rows and for W8 modulo p, and blocked for nine rows.

## Hurwitz and Gurvits: where each theorem meets this work

Each statement below is checked against the cited source and marked documented (a theorem of the source), computed
(a record in this repository) or hypothesis.

- **Hurwitz, zeros of uniform limits** (A. Hurwitz, "Ueber die Nullstellen der Bessel'schen Functionen", Math. Ann.
  33 (1889) 246-266, doi:10.1007/BF01443855; zbMATH JFM 20.0502.02). Documented: if holomorphic g_nu converge
  uniformly to f on a domain, the zeros of f are the accumulation points of the zeros of the g_nu, and an r-fold zero
  of f carries exactly r zeros of g_nu nearby for large nu; the corollary is that a limit of nowhere-zero functions
  on a connected domain is nowhere zero or identically zero. Alignment:
  - Analogy, not a theorem transfer: the first-order maps are not literally uniform limits of nowhere-zero maps on
    a fixed domain. The scalar dichotomy describes each Pfaffian kernel coordinate along an arc, a holomorphic
    function of the arc parameter. A vector-valued dichotomy does not describe the data: the first-order image table of
    `a5-kernel-attachments` shows limits of rank-two forms whose zero set on the tangent cone is a proper subvariety
    of projective dimension 0 to 3, so the base locus of the coordinate map, not a dichotomy, decides where a further
    blow-up is needed (the table is computed; the comparison is a hypothesis).
  - The zero-count clause is the one-variable form of conservation of number. Its algebraic counterpart in this
    work is the degree of the special fiber equal to the multiplicity of the family (W8: multiplicity 50, A5-066;
    the length-equals-degree Cohen-Macaulay tests of `k2_cm.py`) (documented analogy; no theorem transfers).
- **Hurwitz, rational approximation** ("Ueber die angenaeherte Darstellung der Irrationalzahlen durch rationale
  Brueche", Math. Ann. 39 (1891) 279-284, doi:10.1007/BF01206656; JFM 23.0222.02). Documented: every irrational alpha
  has infinitely many reduced p/q with |alpha - p/q| < 1/(sqrt(5) q^2), proved through the continued-fraction
  convergents, and sqrt(5) cannot be enlarged. Alignment:
  - The characteristic-0 lift of the quadrics K2 rebuilds Gaussian-rational coefficients from residues modulo the
    split primes (rational reconstruction). For a rational a/b recovered from a residue modulo M, the extended
    Euclidean algorithm walks the continued-fraction convergents of r/M, and the recovered fraction is unique when
    |a|, |b| <= sqrt(M/2). The governing bound is Legendre's (a p/q with |x - p/q| < 1/(2 q^2) is a convergent),
    the rational-number companion of Hurwitz's constant (documented; Hurwitz's sqrt(5) concerns irrationals and
    sets no reconstruction bound here).
  - Over Q(i) the same reconstruction runs in Z[i], whose continued-fraction algorithm Hurwitz also introduced
    (A. Hurwitz, "Ueber die Entwicklung complexer Groessen in Kettenbrueche", Acta Math. 11 (1888) 187-200; citation
    not verified in this session: zbMATH and OpenAlex return no record).
  - With the two primes M = 32009 x 32029, about 1.03e9, reconstruction recovers numerators and denominators up to
    about 22,600; a coefficient beyond that needs a third split prime (computed bound). The germ ideal J of X- -> N-
    needs none of this: its reduced standard basis over Q(i) has Gaussian-integer coefficients (below).
- **Gurvits, permanent approximation** (L. Gurvits, "On the complexity of mixed discriminants and related problems",
  MFCS 2005, LNCS 3618, 447-458, doi:10.1007/11549345_39; Aaronson and Hance, QIC 14 (2014) 541-559, arXiv:1212.0025).
  Documented: Glynn's identity perm(A) = E over x in {+-1}^n of prod x_i prod (Ax)_i gives an unbiased estimator with
  samples bounded by ||A||^n, so O(1/eps^2) samples estimate perm(A) to within +-eps ||A||^n. The retained Ascella
  measurement (`evidence/quandela/permanent-estimators/permanent_probe.json`) confirms it on 6 x 6 unitary blocks
  (99.3 percent coverage at 10^4 iterations) and shows its half-width exceeding |perm| by 185 times at n = 20
  (computed). Alignment:
  - It supports the statement that no retained QPU measurement certifies an F_p rank (the workload row is
    A5-320): a photonic estimate of any amplitude that is a permanent of a norm-bounded matrix is matched
    classically to the same additive error in polynomial time, and every fiber invariant here is an exact rank,
    which sampling cannot certify (documented plus inference).
  - The fiber computations themselves use Pfaffians and exact ranks over F_p, both polynomial time; the
    permanent's #P-hardness and Gurvits's estimator do not enter them (documented).
  - Shared structure, hypothesis without a mechanism: Glynn's estimator averages over the characters of
    (Z/2)^n, the group whose characters also produce the Klein sign blocks and the Walsh-character N_hat estimator
    (A5-238). No result transfers between them yet.
- **Hurwitz, composition of quadratic forms** (A. Hurwitz, "Ueber die Composition der quadratischen Formen von beliebig vielen Variablen", 1898;
  gororoba-documents-public manifest sha256 ecad36c4cccf71b71a54ed0023d85bfade2f3bd2f5330db65a7cea7fb7b282e8). Documented: a composition algebra exists only in dimensions 1, 2, 4 and 8. The
  Cayley-Dickson algebras of dimension 16 and up therefore carry zero divisors, and the A_5 zero-divisor strata whose
  attaching data this program computes exist because of that theorem.


## Exact physical-kernel projection lemma

Let z be a nonzero physical complex vector, with zbar its actual complex
conjugate, and let C_z be the kernel matrix satisfying C_z z = 0 and
z^T C_z = 0. Consider the bordered matrix

    A(z,zbar) = [ 0       -zbar^T ]
                [ zbar      C_z   ].

Write q = zbar^T z = ||z||^2 > 0. Then

    ker A(z,zbar) = {0} x (ker C_z intersect ker zbar^T)

and the following decomposition is canonical:

    ker C_z = C z direct-sum (ker C_z intersect ker zbar^T).

**Proof.** If A(a,u)=0, the lower block says a zbar+C_z u=0.
Multiplication by z^T and z^T C_z=0 gives a q=0. Thus a=0,
C_z u=0; the upper equation gives zbar^T u=0. Conversely those
conditions clearly imply A(0,u)=0. Define

    Pi_z(v) = v - z (zbar^T v)/q.

Since C_z z=0, Pi_z maps ker C_z into ker C_z, and its image lies
in ker zbar^T. Every v in ker C_z decomposes as
v=z (zbar^T v)/q+Pi_z(v); the intersection of the two summands
is zero because q != 0. QED.

**Domain and limitation.** This is an exact pointwise statement for
actual conjugate coordinates and z != 0. It is continuous where q
stays nonzero, so it supplies the algebraic transport in a sufficiently
small neighborhood of a nonzero physical base point. It does not
establish the source-stratum graph closure, curve selection, or
realizability of every complex fiber point by a physical real arc.
If z and zbar are treated as independent formal variables, q may be
zero and the division is not available. Prove those separate conditions
before identifying complex exceptional-fiber points with physical
limiting kernel planes.
