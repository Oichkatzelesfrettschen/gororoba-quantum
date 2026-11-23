# Review brief: gororoba-quantum PR 994, head f4633658f

Read first: AGENTS.md, then gororoba-quantum/AGENTS.md. You are read-only: change no file, run no long job, spawn no agents.

Tree under review: the tree under review (branch a5-induced-slice-map-and-orbit-checks, one commit over origin/main). See it with: git -C the tree under review show --stat HEAD.

## What the change claims

1. Ledger row A5-598 (docs/evidence/a5-exceptional-fibers/ledger.tsv) and docs/evidence/a5-exceptional-fibers/working/runs/e8-induced-slice-map/: the 21 header-slice Pfaffian generators of E8-bar -> N+-, restricted to the weight slice, are constant combinations of the 21 weight-slice generators modulo J + m I over Q(i); the resulting 21 x 21 map, reduced at (32009, 10754), (32009, 21255), (32029, 9115), (32057, 8059), carries the weight-slice quadric ideal onto the retained header quadric ideals (six checks). The README argues this is the map the change of slice induces (Pfaffian-ideal lemma, localization by v u - 1, weight truncation, product structure).
2. A5-599 and runs/quadric-ideals-macaulay2-p32009/: Macaulay2 reproduces invariants of five quadric ideals.
3. A5-600 and runs/e8-vb-boost-family-p32029/: one normal form of the E8-bar -> VB quadric ideal at twelve boost values.
4. A5-601 and docs/evidence/a5-kernel-bundles-residuals/probes/bordered_kernel_gauss_image.py: degree-2 ranks 3887 and 4022 of two Gauss images modulo 32009, differential rank 15.
5. docs/notes/topics/a5-exceptional-fiber-status.md updated.

## What to attack

- Is the mathematical argument in the e8-induced-slice-map README sound? In particular: the claim that an element killed by s2 that vanishes in the local ring is zero in Q(i)[s,v]/(v u - 1) modulo the ideal; the use of the weight truncation on inhomogeneous header Pfaffians; whether "constant combination modulo J + m I + truncation" really yields the induced map on I / m I; whether the six modular checks could pass for a wrong map.
- Does induced_slice_map.py compute what the README says (frame, Pfaffian adjugate signs, index order of the 126 quadruples, direction of the map G = inverse transpose)? Are the controls able to fail?
- Are the drivers fail-closed (run_induced.sh, run_m2.sh, run_boost.sh)? Does any path exit 0 without its verdict?
- Does each ledger row claim only what its logs show? Check numbers in the READMEs and rows against the retained .log and .json files.
- boost_family.py: is the claim that the Schur form of a principal block does not depend on the kernel frame right, and is the adapted-frame extraction valid? Is "certified" justified for twelve samples?
- bordered_kernel_gauss_image.py: is the z / w split of the bordered matrix right, is the tangent space right, are the ranks lower bounds as stated?
- Status note: any statement that overstates what was shown.

## Output

Findings ordered by severity (FATAL, SERIOUS, SLOPPY, COSMETIC), each with file and line, the evidence, and a concrete fix. State plainly which claims you verified and found sound. If you find nothing fatal, say so.
