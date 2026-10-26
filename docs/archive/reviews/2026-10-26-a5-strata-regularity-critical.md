# Critical review of the A_5 strata-regularity record

**Artifact.** [README.md](../../evidence/a5-strata-regularity/README.md): Theorems 1-6, Conventions, Computations, Falsifiers. It is read against
[strata_regularity.py](../../evidence/a5-strata-regularity/strata_regularity.py), the helpers it imports from
`docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py`, and the independent check
([verification.md](../../evidence/a5-strata-regularity/verification.md), [verify_regularity_independent.py](../../evidence/a5-strata-regularity/verify_regularity_independent.py),
[verification.json](../../evidence/a5-strata-regularity/verification.json)). The imported results are Lemma 5 and Theorems 3 and 6 of the strata record, and
Theorem C of the equations record. **Field.** Commutative algebra and singularity theory: orbit decomposition, Serre
normality, Whitney stratification and links of complex germs. The computational evidence is Singular and python-flint.
**Rubric.** `field-rubrics.md` of the review-work-critically skill has no mathematics section. This review applies its
"Proofs / formal" row (the checker is the review, so the script's checks must cover the claim). It weights the
repository's grounding rule above that row: a claim must rest on a registered artifact. **Visibility.** The whole
README, the whole author script, verification.md, and Lemma 5 and Theorem 3 of the strata record are read in full. The
independent verifier was not read line by line; its methods are taken from verification.md. `result.json` does not exist
yet, and `strata_regularity.py --out` was not run, per the brief.

**Mechanical layer (SOUND).** The pinned `ruff check` and `ruff format --check --target-version py313` (via
`ci/pinned_tool.py`) pass on both scripts, and so does the pinned `mypy`.

**Probes run for this review.** Each probe imports the author's helpers and writes only to the session scratchpad.
- `probe_meet.py` computes, in the author's own coordinate slice, the reduced meet of the two sheets. For E8-bar along
  V^a_+ and along V^a_-, the meet has one minimal prime through p, and its local ring has dimension 1, multiplicity 1
  and embedding dimension 1. For E8-bar along V and for X_+ along V^a_+, the meet is the reduced point.
- `probe_irr.py` runs global `minAssGTZ` on the X_+ and X_- ideals. It did not finish within 600 s and was moved to
  the background; its result is `not run to completion`. The irreducibility findings below rest on other evidence.

## Findings, worst first

No finding is FATAL. Every statement of the seven-statement summary survives once the evidence of the verifier and the
probes is admitted. Two SERIOUS defects concern what the README's own proof and its own `pass` flag deliver.

### SERIOUS 1. The irreducibility of X_+ and X_- does not follow from the argument given

*Barb.* The proof covers X_+ minus its lower closures and then declares all of V(I) irreducible. A component sitting
entirely inside B9, VB, V^a_+ or N_+ would pass every check the script runs.

*Grounding.* Theorem 2 says: "X_+ and X_- because their independent part outside the lower closures is G_2 times one
irreducible slice component on P3a and one on P3b (computation 5), and the P3b component maps into the P3a one under
the element of G_2 sending e'_1 to -e'_1 (the strata record, Theorem 6), while their dependent part lies in V^a_+,
V^a_-, VB and N_+- by the case list above."

That argument establishes X_+ = closure(G_2 . C_a) union (X_+ n lower closures). Irreducibility also needs
X_+ n lower closures to lie in closure(G_2 . C_a). The README never shows that inclusion. Saying that the dependent
part "lies in V^a_+, V^a_-, VB and N_+-" is the opposite of what is needed: it places those points in the lower
closures, and does not place them in the closure of the open part.

The checks the script does run cannot see such a component:
- `closure_dims` reads only the Krull dimension 10. A component of dimension 9 or less leaves that number unchanged.
- The open-component count saturates by det Mc and then discards every prime inside a lower closure.

This gap breaks the chain to statement 3. "The closure of each orbit is the closed set of the table" needs
V(I_X+) = closure(orbit). The closure-order table is computed by `lower_sets` as "the representative of Y lies in
V(I_X)", which is ideal membership, not orbit-closure membership.

*What saves the claim.* The claim is true.
- verification.md gives a complete argument. X_+ n {d != 0} is the image of G_2 x F, where the fiber F over
  d = e'_1 + e'_3 is a linear 4-space. X_+ n {d = 0} = V^a_+, and V^a_+ is reached along the explicit curve
  (e'_1 + eps A, 0, e'_1 - eps A).
- The author's germ data close the gap as well. Each component of an H-stable variety is H-stable, because H is
  connected. A stray component Z inside the lower closures would therefore be the closure of one orbit O. It would then
  appear in the slice at the representative of O as a component through p of dimension below dim X - dim O, and the
  germ rows report no such component. The script never asserts this, however.

*Remedy.* Replace the sentence with the verifier's fiber argument. Also assert, in `germs()`, that every minimal prime
through p has local dimension dim X - dim O. That assertion proves equidimensionality, and with it irreducibility given
the open orbit, for every closure, including the closures imported from the earlier records.

### SERIOUS 2. The `pass` flag does not guard the tables the summary states

*Barb.* The record says the pass flag certifies every value. For the germ, singular-locus and link tables it certifies
one integer per row.

*Grounding.* Computations section: "Each part of `result.json` is an exact computation; `pass` requires every listed
value."
- `germs()` (strata_regularity.py, lines 570-577) sets `pass` from two conditions: no Singular error, and germ
  dimension equal to `expected_germ_dim`. Multiplicity, embedding dimension, quadric rank, sheet count, component
  invariants and meet dimensions are computed and written, but nothing compares them with the germ table. A
  regression that turns "A_1, quadric rank 3" into "rank 2" would still pass.
- `classify_germ` writes a type string. No expected type exists in the source to compare it against.
- `representatives()` computes `in_VQ` and `in_VG` but never checks them. Theorem 5 uses exactly those memberships for
  the frontier condition of the nullity-4 strata.
- `certificate()` checks `drop_escapes` and `open_components`. It never compares r_G or dim s with the table of
  computation 5. This one is harmless, because the rank formula uses the computed values whatever they are. The
  README sentence still claims more than the code does.

So the singular-locus table of Theorem 3, the germ table of Theorem 6, and statement 7 ("The transverse germ of each
closure along each orbit has the invariants of the germ table") are hand transcriptions with no guard in the record's
own replay. `result.json` is not written yet. Until it is, the Falsifiers sentence "None occurred." rests on
`verification.json` alone.

*Remedy.* Put the germ table in the script as expected tuples: (dim, mult, embdim, quadric rank, number of sheets, meet
dimensions) per (closure, orbit) pair, plus "smooth" for every other pair. Make `pass` compare against them, and do the
same for `in_VQ`/`in_VG` and the (r_G, dim s) table. Add a self-test mutation of one expected germ row. Admit the README
only after `result.json` exists and its rows are diffed against the tables.

### SLOPPY 3. "Two S^7 glued along a circle" is asserted from a dimension count

*Grounding.* The germ table row "E8-bar along V^a_+- | 4 | 2 | 7 | two smooth sheets meeting in a curve | two S^7 glued
along a circle". The script computes only `dim(std(C[i] + C[j]))` (line 502), the dimension of a sum ideal that is not
radical. A one-dimensional meet can have several analytic branches, and its link is then several circles.

`probe_meet.py` shows the reduced meet is one smooth curve germ (dimension 1, multiplicity 1, embedding dimension 1)
at both V^a_+ and V^a_-. Its link is therefore one unknotted S^1, and the stated link is correct.

*Remedy.* Have `germ_job` compute the radical of each meet, its primes through p and its local invariants, and assert
that the meet is smooth wherever the table names a link.

### SLOPPY 4. The tangent-space statement at x0 rests on the verifier only

*Grounding.* "the tangent spaces of V (real dimension 16, unit dimension 15) and B9 (18, unit 17) meeting in the
tangent space of VB (14, unit 13)." This requires the tangent line of the V-curve and the tangent plane of the B9-surface
in the slice to be independent. `strata_regularity.py` never computes a germ of R_12 = V u B9 or that intersection.
verification.md checks it ("their Zariski tangent spaces meet in 0"). The link S^1 disjoint union S^3 itself needs only
smoothness of both germs and a set-theoretic meet at the point, and both are delivered.

*Remedy.* Cite the verifier as the source for the tangent-space statement, or add the check to the script.

### SLOPPY 5. The dependent-pair case list invokes Q = 0, but W8 is not contained in V(Q)

*Grounding.* "eta(w) != 0, m = 0: Q = 0 forces alpha = +-beta" and "w null: Q = 0 forces m = 0". At the W8
representative (e'_1, 0, e'_3), eta(s, d) = eta_1 - eta_3 = -2, so Q is not 0 there and W8 is not inside V(Q). The
conclusion still holds:
- A dependent point (alpha w, 0, beta w) of W8 has (alpha + beta)^2 eta(w) = (alpha - beta)^2 eta(w) = 0.
- So either w is null or alpha = beta = 0.
- In either case Q = (alpha^2 - beta^2) eta(w) = 0.

The text also never walks the closures one by one to show that the dependent part of each X lies in its lower closures.
Each case is a one-line check: Iso, B9 and W8 force w null; X_+ excludes V^a_- because eta(d) = 4 eta(u') != 0.

*Remedy.* Add the W8 line and a per-closure sentence.

### SLOPPY 6. The Whitney sentence calls the (b)-bad set "a proper closed subset"

*Grounding.* "the set of points of Y where it fails is a proper closed subset of Y (Whitney's theorem for algebraic
strata)". Whitney's theorem gives a bad set that is nowhere dense in Y. That set is semialgebraic and lies in a proper
closed subvariety; the theorem does not say it is closed. The argument needs only "nowhere dense" plus H-stability. An
H-stable subset of a single orbit is empty or the whole orbit, so a nowhere-dense one is empty.

For the origin stratum the cleanest justification is the cone property. Every stratum is C^*-stable, so the radial
vector x lies in T_x X, and the secant from 0 to x is that radial line. Condition (b) at 0 therefore holds. The README
leaves this case implicit, and verification.md says only "the origin is a point stratum".

*Remedy.* Say "nowhere dense" and add the cone sentence.

### COSMETIC 7. Statement 5 overreaches in its last clause

"... smooth off R_8, along which V(Q) and V(G) cross transversally." Read literally, "along which" refers to
V(Q) n V(G). At points of Iso, dQ and dG are dependent (computation 7), so the two hypersurfaces do not cross
transversally there. Write "and off R_8 V(Q) and V(G) cross transversally along it."

### COSMETIC 8. "Contains the line C w"

Theorem 2 says the G_2-orbit of w "contains the line C w exactly when w is null". The orbit of a nonnull w contains -w,
which lies on that line. The argument that follows (eta(g w, w) = 0) concerns the tangent space. Write "its tangent
space at w contains w".

## SOUND

- **Transverse slices and the transfer to the orbit.** `transverse_columns` tries all 15 unit vectors and keeps each one
  that raises the rank over the 16 H-generators at p. The kept columns therefore complete T_p O to C^15, and
  `expected_germ_dim` checks slice_dim = 15 - dim O against the germ dimension. Because the slice is a complement, the
  action map from a local section of H through p, times the slice, is a local biholomorphism at p. X is H-stable, so X
  is locally O x (X n S). Smoothness of the reduced slice germ (embdim = dim) is then equivalent to smoothness of X
  along O. Radicality survives localization, so the global radical computed in `r1` is the reduced structure of the
  local germ.
- **Certificate algebra.** With Mc invertible:
  - the G_2-tangent at (u', v') is Mc . T(A, B);
  - its meet with pairs in span(A, B) is Mc . s;
  - the boost is Mc (Mc^-1 J Mc);
  - for m = 0 the scaling is Mc . I.

  The orbit rank r_G + [m != 0] + rank{N, [m = 0] I mod s} and the minor thresholds t0 and t1 are therefore right, and
  replacing Mc^-1 by adj(Mc) is harmless on det != 0. The escape test discards primes containing det. For each
  remaining prime P it requires I_Y to lie in P for some lower closure Y, which is V(P) inside V(I_Y). That test is
  exactly "every component of the drop locus on det != 0 lies in a lower closure". `fit` handles the degenerate
  thresholds correctly.
- **Slice coverage.** Lemma 5 of the strata record treats Gram rank 2, Gram rank 1, isotropic planes and lines. Every
  w in C^7 is G_2-equivalent to a vector on some slice plane, so the slices (with det Mc = 0 allowed) also cover the
  dependent pairs. The `iso` and `nullity4` jobs run on whole slices, so they cover all of C^15 up to G_2.
- **Openness step.** An orbit of dimension n in an irreducible n-dimensional X is open. Two such orbits meet, so they
  are equal. The representative is not in any lower closure, because the pattern check together with the
  strict-dimension check forbids mutual membership.
- **Serre normality, twice.**
  - Iso: dimension 11 = 15 - 4, Jacobian rank 4 off VB, singular locus of codimension 4.
  - V(Q) n V(G): Q does not divide G, and the dependence locus has dimension at most 11 inside dimension 13. Q and G
    are absolutely irreducible (strata record, Theorem 3), so the connectedness of the two 14-dimensional strata
    holds.

  In both cases the ring is Cohen-Macaulay and R1 holds, so it is normal. A graded normal ring with degree-zero part C
  is a domain.
- **Germ identifications.**
  - The holomorphic Morse lemma applies to a hypersurface germ in its embedding with a nondegenerate quadratic part. The
    reduction of the quadric modulo the linear leading forms is the quadratic part on the embedding manifold, because
    the eliminated coordinates are O(2).
  - The link of the sum of x_i^2 = 0 is V_2(R^m), and V_2(R^3) = SO(3) = RP^3.
  - "Two smooth sheets meeting at the point" gives S^5 disjoint union S^5. Multiplicity 2 from two multiplicity-1
    components forces both to have top dimension, and smooth algebraic components are analytically irreducible.
- **Theorem 1.** A linear derivation preserving I preserves each I n (degree <= d), so exp(tX) preserves I. The values
  of (cosh t, sinh t) for t in C cover SO(2, C).
- **Whitney and Thom-Mather.** H acts by linear automorphisms preserving every stratum, and condition (b) is
  invariant under diffeomorphism. Pairs inside S_4 lie in the manifolds V(Q) minus 0 and V(G) minus (W8 u V). The open
  stratum satisfies (b) trivially. Every pair with Y in R_8 is covered by homogeneity. The isotopy lemma then gives
  constant germs along the three S_4 strata, and homogeneity alone already gives them along the orbits.
- **Real and complex.** Complex smoothness is real smoothness, and a complex Whitney stratification is a real one. The
  radial field is tangent to every cone stratum, so S^29 is transverse to every stratum. All of this is correct, given
  the imported R-linear identification R^30 to C^15.
- **x0.** u' = e'_2 - i e'_1 has eta(u') = eta_2 - eta_1 = 0, so it lies on the null cone. F3 and C^* carry x0 to (n,
  0, 0). The link S^1 disjoint union S^3 follows from two smooth germs of dimensions 1 and 2 that meet only at p.

## Steelman

The record reduces a 15-dimensional singularity question to one exact computation per orbit, and the reduction is
correct:
- the symmetry group is verified on every ideal;
- the orbit-rank certificate is a sound reduction from GL_2 to s, with an escape test that proves what it says;
- the transverse slices complement the orbit tangent space;
- the normality and link arguments are textbook-correct.

The independent verifier reproduces every table row by different algebra (deformation to the normal cone, orthogonal
slices, a finite boost element). It also repairs the one real hole in the proof, the irreducibility of X_+-. Every
numerical claim probed here held.

## Verdict

The core is sound, and every statement of the summary is true on the evidence available, with the verifier and the meet
probe counted in. The record does not yet prove its claims by itself.
- Its own proof of the irreducibility of X_+ and X_- skips the components inside the lower closures. Statement 3
  depends on that step.
- Its `pass` flag guards the germ dimension and nothing else in the germ, singular-locus and link tables, so statement
  7 is currently a transcription.

The most important fix is mechanical: encode the germ table and the in_VQ/in_VG patterns as expected values, and assert
that every prime through p has the full transverse dimension. With that check, the record's own replay proves the
irreducibility of every closure and certifies every row of the tables. Then wait for `result.json` and diff it against
the README. Until then the record's evidence is verification.json plus the hand arguments, which is strong
corroboration and short of a replayable certificate.

## Disposition

The review ran against the draft of [the record](../../evidence/a5-strata-regularity/README.md). Each finding was
resolved in the record before admission:

- SERIOUS 1 (irreducibility of X_+-): Theorem 2 now gives the fiber-over-null-d argument of the verification and a
  second argument from the record's own data. H is connected and fixes each minimal prime, so a lower-dimensional
  component would be the closure of a lower orbit and would appear as a short sheet in that orbit's germ, and
  `germs` requires every sheet to have the full germ dimension.
- SERIOUS 2 (`pass` did not guard the tables): the script now carries the closure order, the plane table and the germ
  table as constants. `representatives`, `certificate` and `germs` fail on any deviation, and representatives also
  check the memberships in V(Q) and V(G). The germ table constant takes its values from the independent
  verification's rows, and the record's run reproduces all 63.
- The germ computation moved from local standard bases to the deformation to the normal cone in global orderings, with
  meets taken as the largest minimal prime of the sum through p (this answers the unreduced-meet remark). The local
  computation needed over an hour and tens of GiB for the E8-bar germs, against seconds for the global one. A per-orbit
  column order at VB keeps the primary decomposition tractable there.
- SLOPPY 5 (Q = 0 on dependent points of W8) and SLOPPY 6 (Whitney's bad set "nowhere dense"; the origin by the cone
  argument): the text now carries both steps.
- The two COSMETIC findings (transversality off R_8 in statement 5; the tangent space contains w) were applied as
  worded.
- SLOPPY on the link "two S^7 glued along a circle": the record now states that the circle rests on the review's probe
  finding the reduced meet a smooth curve.

