# A_5 nullity strata on hardware and in algebra: one object, two instruments

Status: synthesis of 2026-11-07, living. This note joins the quantum-hardware programs (IBM pathion kernel and coset
maps, the IBM drain, Tuna-17, Ascella) to the A_5 exceptional-fiber program. It decomposes both to the object they
share, states which results carry over between them, records the conflicts found and how each resolved, and sets the
roadmap. Each fact has its home elsewhere: this note links the home and gives the decisive number. Ledger rows are in
[ledger.tsv](../../evidence/a5-exceptional-fibers/ledger.tsv), with the A5- prefix omitted below.

## The shared object

For a in the 32-dimensional Cayley-Dickson algebra A_5, the nullity of left multiplication L_a stratifies A_5. The
locus of nullity at least 8 is the union of twelve orbits of H = G_2(C) x SO(2, C) x C^* and the origin:

- nullity 8: W8, E8-bar, Iso, X+, X-;
- nullity 12: B9, V, VB, V^a+, V^a-;
- nullity 16: N+, N-.

The orbit table, closure equations and incidences are in
[a5-strata-regularity](../../evidence/a5-strata-regularity/README.md).

The two programs measure the same function from opposite sides:

- **Hardware** reads observables of L_a at a point. Only the IBM kernel and coset maps estimate the nullity directly,
  as N_hat (`gororoba_quantum/pathion_kernel_map.py`). Tuna-17 selector contrasts, Ascella conditional levels and the
  IBM rank-sector probes measure block or selector observables of operands whose nullity is computed classically.
- **Algebra** reads the attachment between strata. For each incidence Y -> Z, the fiber cone F(I) of the Pfaffian
  kernel-coordinate ideal on the closure of Y is the coordinate ring of the limit set. That limit set holds the
  directions by which Y approaches the nullity-12 or nullity-16 locus
  ([purpose](../../evidence/a5-exceptional-fibers/working/purpose.md)).

A point reading cannot see an attachment. A reading along a path that enters the boundary can.

## What the hardware establishes about the algebra

1. **Every measured operand of nullity at least 8 lies in a named orbit, exactly (rows 206 and 207).** The placement
   is a classical computation on the operands the hardware measured: closure equations, cd_core nullity and tangent
   rank.
   - W8: e1 +- e10.
   - E8-bar: C8 = e1 + e8 + e18 + e27.
   - B9: B12 = e1 + e10 + e20 + e31.
   - V: e1 + e24.
   - VB: e1 + e18 and e17 - e2.
   - N-: A16 = e1 + e10 + e18 - e25.

   cd_core nullity equals the orbit's nullity for every operand
   ([hardware-orbits](../../evidence/a5-exceptional-fibers/hardware-orbits/README.md)). On ibm_fez e1 + e18 reads
   N_hat 12.65 [11.87, 13.42], which resolves its nullity of 12. e1 + e10 reads 7.30 [0.85, 13.74], consistent with 8
   but unresolved, since the interval also holds 4 and 12 ([findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)).
2. **Two incidences of the fiber program have both ends measured.**
   - W8 -> N- along a(b) = e1 + e10 + b (e18 - e25) (row 208).
   - E8-bar -> VB along a(b) = e1 + e18 + b (e8 + e27) (row 209).

   Both lines are four-term operands, the block class the Ascella and IBM coset-block cases already run (row 199: IBM
   and Ascella agree within 0.07 on B12 and C8).
3. **The order of contact separates the two incidences in the exact matrices.**
   [contact_order.txt](../../evidence/a5-exceptional-fibers/hardware-orbits/contact_order.txt) shows what happens as
   the operand leaves the boundary by eps:
   - On W8 -> N-, eight singular values of L_a open linearly: four as 1.414 eps and four as 2.000 eps.
   - On E8-bar -> VB, four open quadratically, as 2.000 eps^2.

   This is a classical prediction about L_a. Hypothesis: a hardware contrast scanned toward the boundary shows the same
   orders. Testing it needs an observable-specific noisy forward model, because a probability can scale as an amplitude
   squared and normalization or a noise floor can change an exponent, and then a calibrated scan. Second hypothesis:
   the order is the order of the limit vectors in
   the arc certificates. The X certificate's limit vectors have order 2
   ([arcs-x](../../evidence/a5-exceptional-fibers/arcs-x/README.md)), and the quadratic opening on E8-bar -> VB is the
   same phenomenon. Falsifier: an incidence whose arc limit order differs from its singular-value order.
4. **Blind spots.**
   - Nullity 12 spans V, VB and B9, so an N_hat of 12 does not identify the orbit.
   - No measured operand lies in Iso, X+, X- or N+ (rows 211 and 212).
   - The doubling image e1 + e10 - e18 + e25 of A16 is the unmeasured N+ end.
   - The IBM rank path joins W8, VB and N- through nullity-4 points and probes no incidence (row 213).

## What the hardware establishes about the instruments

Every deviation found so far is a property of the instrument's realization, and none contradicts an ideal nullity.
The algebra's exact predictions therefore turn each run into a calibration of its instrument.

| Instrument | Finding | Rows and records |
|---|---|---|
| Ascella (photonic) | each served mesh carries a fixed error of rms about 0.025 in level, persistent at r 0.9966 under verbatim replay; the two-block mirror failure is that fixed error divided by one anchor mesh per slot; per-mode efficiencies carry most of a frozen map's reach, and a shifter map beyond them is not established (p 0.041 post hoc) | 200 to 204; [runbook](../../runbooks/ascella-block-run-design.md) |
| IBM Heron r2 | the null operand's selector reads zero within 0.006 on Fez and Kingston; the pooled X90 over-rotation is -0.0015 +- 0.0014 rad; no packing effect above 0.015 on the packed null-k0 minus arm at the tested one-hop layouts (90 percent intervals); the calibration's confusion matrix overstates the asymmetry the circuits see by about 0.09 (hypothesis) | 192 to 199 |
| Tuna-17 | the null selector offset +0.0164 is consistent with a coherent X90 over-rotation (+0.03 rad); IBM's own pooled angle sits 4.3 sigma below that value, so the offset is Tuna-specific; an assignment-level q12 readout flip is excluded at 14.5 se; the 6-CZ null-block case (named one-CZ), approved 2026-11-07 and acquiring on its case branch since 20:27Z (not part of this change; its retention change carries the approval, stamp and records), separates the coin-conditioned dropout from the bounded over-rotation, while a post-schedule q12 correlation stays open | 186; [c2_q12_bracket.txt](../../evidence/pathion-kernel-map/conjectures/c2_q12_bracket.txt) |

The design rule this yields for every platform: calibrate against an operand whose ideal nullity is exact and known,
on the same instrument realization (mesh, routing, readout context) as the measurement. One anchor mesh per slot
failed that rule and produced the two-block mirror failure. X-only readout preparations outside the template context
would have failed it (the design review caught it before any run), and a confusion matrix taken outside the circuit
context is the hypothesis of row 196.

## What the algebra establishes, and the new method

The Iso -> N- question is whether F(I) = k[y]/K2 (row 007). It reduces to one number.

- K2 holds the quadratic relations of F(I) (`k2_hilbert.py`).
- k[y]/K2 is a five-dimensional domain of degree 23 (rows 058 to 060).

So F(I) = k[y]/K2 holds exactly when the analytic spread is 5, and the multiplicity condition of row 011 is
redundant. The 23-variable blowup chart that tried to decide it failed six times (rows 070, 071, 174, 176, 181, 205;
the last ran 23.5 h to degree 15 with 37,018 basis elements at 25.7 GB).

The successor works in the six t-variables alone
([tslice](../../evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/README.md)):

- **Criterion.** The origin lies on the closure of V(J) minus V(I) cut by k generic forms in G exactly when
  dim E0 >= k.
- **Saturation.** The test saturates by t2, since L0 lies in {t2 = 0} (row 068).
- **Junk.** The 4-dimensional junk JK, the closure of V(J, G) minus V(t2), misses the origin at both primes.
- **Controls, all as predicted.** X+ and X- read on at k = 2 and off at k = 3 (row 214). Iso reads off at k = 5
  (272 s) and on at k = 3 (16 s) (rows 215 and 216).
- **Result (2026-11-08).** The preregistered Iso k = 4 rows (row 217) read on with two independent form families at
  p = 32009 and p = 32029, by both saturation routes, in 486 s each at 304 MB (twins 2,130 s), against the 23.5 h and
  25.7 GB of the last chart attempt. Row 067 moves to survives: E0 = V(K2), l(I) = 5 and F(I) = k[y]/K2 in every degree
  at both primes, as F_p statements without numerical confidence.
- **What "on" means.** One sampled slice that reads "on" is evidence consistent with dim E0 >= 4, not a certification:
  a special slice can meet a lower-dimensional E0. The slices meeting a 3-dimensional E0 form a hypersurface of
  degree about 4 deg(E0) in the form coefficients, and nothing in the record bounds deg(E0), so no numerical
  confidence is attached. The original family uses the same integer coefficients at both primes, so an independent
  ANU family per prime entered the preregistration and read on as well (result below).

Limits found while building it:

- The X controls are forced by linear algebra, since three generators make Q_3 = (J, G). They test the implementation
  and the t2 support, not genericity.
- The t2 saturation is guaranteed only at k >= 4.
- A slice of codimension l - 1 cannot decide a same-dimension component, so the W8 degree-30 component and the
  E8-bar -> VB degree-3 component need a point-count or branch-count variant (row 218, rejected for the plain ladder).

Quantum algorithms: the cited survey and the bounded addendum search found no algorithm with exact finite-field output
and an end-to-end speedup for a standard basis, a saturation or an exact rank over F_p, which are the ladder's and the
engine's stages. The quantum hardware's contribution to the ladder is the genericity of its
QRNG forms ([survey and addendum](quantum-linear-algebra-fit-a5.md)).

## Conflicts found and their resolution

| Conflict | Resolution | Where it stands |
|---|---|---|
| A5-202 recorded as refuted from a post-hoc decomposition without a null | seed-block permutation of the increment: gain p 0.28, offset p 0.041; status open | row 202 |
| the ladder brief expected Iso k = 3 to cost most | it cost 16 s against 272 s at k = 5; hypothesis: the saturation exponent (1 against 4) or the final standard-basis structure drives the cost | tslice README |
| "the X controls are the strongest check" (design review) | they are forced by linear algebra; Iso k = 5 off is a theorem; both test implementation, not genericity | tslice README |
| the Tuna Ry control quoted at 9 jobs per template | 33 jobs resolve 0.0164 at 3 se; 9 reach only +-0.03; Ry dropped by owner decision | Tuna CASE.md |
| the Tuna b0-like band admitted a wrong refutation in 48 percent of runs if Rz is not virtual | band narrowed to 2 se with doubled b0 shots: 7.7 percent; Rz on Tuna-17 stays unverified | Tuna CASE.md |
| an FX4 run extended past its limit was killed by a daily auto-shutdown schedule invisible to the run | records retained; the schedule is checked and moved before any run past its first day | row 205; [run rulebook](../../runbooks/run-rulebook.md) |
| row 011 states (spread, multiplicity) as the criterion | the multiplicity half follows from row 060's primality | row 011 basis |
| the Codex review read the one-CZ case as unapproved and unsubmitted | the case's status line predates the owner's approval; batches run since 20:27Z; the submitted case keeps its bytes and the retention change records approval and stamp | case branch run directories |

## Roadmap

1. Done 2026-11-08: the Iso k = 4 rows read on with two independent form families at both primes (row 217), and row
   067 survives as an F_p statement. Remaining strengthening: a genericity witness or a bound on deg(E0) that turns the
   reading into a certificate.
2. Iso characteristic zero (task umbrella, rows 042 and 073 to 075). Hypothesis: a two-prime rational reconstruction
   of the slice witness lifts the statement. Reduction mod p can change the analytic spread, so the lift needs its own
   argument.
3. A branch-count variant of the ladder for same-dimension components (W8 degree 30, E8-bar -> VB degree 3), with the
   X and E8-bar arc certificates as controls.
4. A hardware arc-probe case on the four-term lines of rows 208 and 209, one with the doubling N+ end. Its first
   steps are an observable-specific noisy forward model of the contrast against b, and a check of which instrument
   encodes a weighted four-term operand. IBM's coset-block sign circuits encode coefficients +-1 only; Ascella's mesh
   sets real coefficients. It would then scan b toward the boundary and fit the contrast's order (1 against 2). A written case and owner approval are required. Its value is an attachment invariant measured on hardware,
   with the algebraic order as the exact prediction.
5. Close the running acquisitions:
   - the Tuna-17 6-CZ null-block case separates dropout from the bounded over-rotation for row 186, with a
     post-schedule q12 correlation left open;
   - the IBM 64D/128D wide case extends the nullity readings to A_6 and A_7, outside this stratification.
