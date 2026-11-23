No FATAL findings. The retained results support the scoped numerical claims, but the boost replay gate has a serious fail-open gap and the induced-map proof needs sharper algebra.

## SERIOUS

1. `docs/evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-family-p32029/run_boost.sh:14` can print `run_boost: PASS` while several claimed invariants are false.

Evidence: lines 14–21 check completion, Hilbert data, radicality, and frame consistency, but omit:

- `adjugate_identity 1`
- `pivot_pfaffian_at_origin_nonzero 1`
- `selected_count 10`
- `normal_form_size 21`
- the exact minimal-prime multiset

The line-18 regular expression accepts two identical matching prime lines and ignores extra unexpected prime lines. Thus a replay with two `(4,3,4)` primes, an extra component, or a failed Schur identity can exit zero. The retained logs themselves contain the correct distinct rows `(4,3,4)` and `(4,4,3)` and all omitted predicates equal one, so A5-600’s present data remain sound.

Fix: check every named predicate and compare all `RESULT prime` lines against an exact two-line expected file or sorted literal.

## SLOPPY

2. `docs/evidence/a5-exceptional-fibers/working/runs/e8-induced-slice-map/README.md:26` states the localization and truncation argument too strongly.

Evidence:

- Inverting the product of the two axis restrictions does not make the full header pivot Pfaffian a unit in that polynomial localization. A focused Singular check on the retained N− script reports `pBH == pBH0` as false.
- “Killed by `s2` and zero in the local ring implies zero” needs the omitted grading/support hypotheses; it is false for a general module.
- Gradedness alone does not justify discarding the high-weight terms of an inhomogeneous header Pfaffian.

The calculation is nevertheless repairable with facts already present: the weight pivot equals its axis restriction and is inverted; the Pfaffian identity then puts every header Pfaffian in the graded weight ideal \(I\); components above the largest generator weight lie in \(\mathfrak m I\); and \(I/(J+\mathfrak m I)\) is killed by the full maximal ideal, making localization at the origin faithful.

Fix: replace lines 26–29 with that argument. State that the full header pivot is a unit only in the local ring, not necessarily in the displayed polynomial localization.

3. `docs/notes/topics/a5-exceptional-fiber-status.md:37` still lists the E8-bar header/weight slice map as open.

This contradicts the same document at lines 58, 65, and 95, which assign it to A5-598. The line also calls A5-597 “this change,” although this commit adds A5-598 through A5-601.

Fix: remove the E8-bar map from that Open cell, retain the W8/Iso/X maps and the boost direction, and remove “this change” from A5-597.

## COSMETIC

4. All twelve retained `bf-*.sing` files contain an extra blank line at EOF; for example `docs/evidence/a5-exceptional-fibers/working/runs/e8-vb-boost-family-p32029/bf-w1.sing:212`. `git diff --check` reports each one.

Fix: make the generator emit one terminal newline and regenerate the twelve files and manifest.

## Claims verified as sound

- `induced_slice_map.py` reuses the header producer’s frame, matches its lexicographic ordering of the 126 quadruples, and verifies the Pfaffian-adjugate sign convention. If \(H=W L\), its `inverse(transpose(L))` substitution correctly expresses weight generators in header coordinates.
- Both 21×21 maps are constant and invertible. Their weight selections and 148-relation digests match the retained Q(i) record.
- All six modular checks report mutual zero reductions, 148 minimal generators, dimension 5, multiplicity 11, and nonzero determinant. Identity, single-entry, and coordinate-swap controls all fail. These checks establish ideal equivalence, but symmetry means they cannot alone prove that the map is the induced one; the repaired local-class argument supplies that identification.
- The Macaulay2 results exactly equal `expected-results.txt`; all five retained logs show the ledger’s dimensions, degrees, primes, primary components, nilradical data, and controls.
- The twelve boost logs contain the claimed two distinct minimal primes, ten selected generators, valid Schur identities, invertible adapted frames, and one common normal-form digest. This certifies exactly twelve samples, not a generic boost.
- The bordered-matrix probe’s \(z/w\) split is correct: the split-coordinate phase is applied to \(z\), while \(w\) remains free. Its tangent space is the hypersurface tangent in \(z\) plus all \(w\) directions. The differential ranks are 15 with zero tangency failures. The ranks 3,887 and 4,022 are correctly stated as lower bounds, not Hilbert-function equalities.
- `run_induced.sh` and `run_m2.sh` are fail-closed against their declared verdicts.

All three SHA-256 manifests verify, regenerated induced and boost scripts match the retained files byte-for-byte, and ShellCheck, Ruff lint, Ruff formatting, and the applicable mypy check pass. I did not rerun the multi-minute Singular, Macaulay2, or 7,000-point Gauss computations.