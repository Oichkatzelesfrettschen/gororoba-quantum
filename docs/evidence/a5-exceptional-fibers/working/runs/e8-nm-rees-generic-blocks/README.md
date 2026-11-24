# Generic fiber of the Rees ideal of E8-bar at N- over the s2-line: y-degree 1, two primes

Row A5-542 states a count that until now rested on scratch runs: over the function field in s2, the Rees ideal of
E8-bar -> N- on the weight slice needs 32 minimal generators of y-degree 1 beyond the products of the germ ideal
with the y_a and the 2 x 2 minors y_a G_b - y_b G_a, in 11 bidegrees. This record retains the producer and the
logs, and adds a second prime.

## Result

| Prime, i | s2 | Occupied blocks | Minimal generators | Bidegrees |
|---|---|---|---|---|
| 32009, 10754 | 7013, 21890, 3567 | 75 | 32 | 11 |
| 32009, 10754 | transcendental | 75 | 32 | 11 |
| 32029, 9115 | 7013, 21890, 3567 | 75 | 32 | 11 |
| 32029, 9115 | transcendental | 75 | 32 | 11 |

In all eight units the generators sit in the bidegrees (4, 2), (5, 1), (5, 2), (5, 3), (5, 4), (6, 2), (6, 3),
(6, 4), (7, 3), (7, 4), (8, 4) with 2, 1, 6, 6, 1, 3, 5, 3, 2, 2, 1 generators, the germ at fixed s2 has dimension
4 and multiplicity 8, and the two consistency counters (kernel module against evaluation rank, and the M1 count)
are 0. The bidegree is (tw, t3) with tw = (1, 0, 3, 2, 2, 1, 4, 4, 3) and t3 = (1, 0, 2, 1, 1, 0, 2, 2, 1) on the
slice coordinates; s2 has bidegree (0, 0).

## Method

`stage_a.tmpl` is the stage that reduces the E8-bar germ at N- to its components through the origin and selects
the 21 Pfaffian generators G (13 germ generators, dimension 5, multiplicity 10 with s2 a variable). `gen_blocks.py`
substitutes its J and G into `deg1.tmpl` with s2 a number or the parameter z of the field GF(p)(z). The block
script counts, bidegree by bidegree, the rank of the evaluation y_a -> G_a through an explicit parametrization of
the germ and the standard monomials of three modules; the minimal generators of a block are the standard monomials
of M + m K less that rank.

## Cost

One core of an aarch64 host, Singular 4.4.1: stage A 3 s; a point value 21 s at 19 MiB; a function-field unit
19 min at 0.23 GiB.

## Scope

- Two primes, one root of -1 each; y-degree 1; the basepoint N-.
- The count over GF(p)(z) holds at all but finitely many values of s2 in the algebraic closure of GF(p); the
  exceptional set is not computed, and s2 = 0 is in it (A5-506).
- The box. The blocks read are those with tw at most 14 and t3 at most 8, twice the largest bidegree (7, 4) of a
  generator G, which covers the 2 x 2 minors. A minimal generator of y-degree 1 outside the box would not be seen,
  and no logged quantity bounds the bidegrees of the kernel.
- The split over bidegrees. The total 32 is a rank identity. The count per block reads standard monomials of
  M + m K in an ordering that sees tw only; the same reading for the kernel module is checked block by block
  against the evaluation rank (counter 0 in all eight units), and the t3-homogeneity of the kernel generators is
  not logged.
- The header comment of each generated script names "entry 0" of the value list whatever the value; the value
  substituted is the right one.
- Characteristic 0 is not computed. Two primes with one answer are evidence for it, not a proof.
- The parametrization and the block reading are those of the scratch runs of 2026-11-14; no second system
  recomputes them.

## Reproduce

    sh docs/evidence/a5-exceptional-fibers/working/runs/e8-nm-rees-generic-blocks/run_blocks.sh

The two stage-A units run first, then the eight block units, each set through `gororoba_quantum/run_commands.py`
(`parallel.ordered_map`). `GOROROBA_WORKERS` caps the units that run at once and defaults to the available CPUs;
`GOROROBA_WORKERS=2` serves a shared host. The two function-field units start first, so the wall time is
20 min 9 s at 2 workers on a 4-core aarch64 host (the serial run took about 40 minutes) and tends to the longest
unit's 19 minutes at 4 or more. Peak
memory is the sum over the running units: 0.23 GiB per function-field unit and 19 MiB per point-value unit, so at
the default 8 workers (all eight units at once) about 1.0 GiB in total. The run writes its scripts and logs under
`rerun/` beside the script (or the directory named by `OUT`), each unit also writes its own `.want` comparison
file, and the RESULT lines of each log are compared with the retained one, leaving out the timing and memory lines,
which differ between runs. `sing-sha256.txt` holds the digests of the scripts of the retained run.
