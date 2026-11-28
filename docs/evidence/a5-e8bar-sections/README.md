# Zero-dimensional sections of the E8-bar closure ideal modulo 32009

A5-605 records that equidimMax, radical and minAssGTZ of the 37-generator E8-bar closure ideal Y stopped at 1 h and
4.3 GiB without a result. This record decides the top-dimensional part of V(Y) from five random zero-dimensional
linear sections instead, in 1.2 s of wall time at 82 MiB for all ten Singular runs (the five sections and the five
control sections) together with the producer run that emits Y. Ledger row A5-673.
[`scripts/a5_e8bar_sections.py`](../../../scripts/a5_e8bar_sections.py) runs Singular 4.4.1.

## Method

Y is the line `ideal Y=` that the retained producer
[`derivation_stability.py`](../a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability/README.md)
prints in its `rad` mode at p = 32009 (root of -1 = 10754). The script runs that producer and leaves its bytes
unchanged. A section substitutes z = b + A w with a random 15 x 4 matrix A and a random vector b over F_p, so
Y(b + A w) is an ideal in four variables. Each section reports the dimension, vdim, the vdim of the radical, and the
factorization over F_p of the eliminant of a random linear form. Each irreducible factor of degree d is one Frobenius
orbit of d points.

Seeds come from `docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json`, indices 16 to 20, one per section. Each seeds
`random.Random` for the A, b and linear form of its section.

## Decision rule (written before the run) and result

The rule required all of the following for K = 5 sections:

- every section has dimension 0, vdim 24, radical vdim 24, and a squarefree eliminant of degree 24;
- the proper sub-sums of the orbit lengths have an empty intersection over the five sections;
- the orbit lengths have gcd 1.

Any other outcome would have been inconclusive.

| Seed index | Orbit lengths | dim, vdim, radical vdim (each section's direction cone Y(A w) has dimension 0) |
|---|---|---|
| 16 | 2, 4, 5, 13 | 0, 24, 24 |
| 17 | 1, 2, 5, 16 | 0, 24, 24 |
| 18 | 1, 2, 3, 18 | 0, 24, 24 |
| 19 | 24 | 0, 24, 24 |
| 20 | 1, 3, 20 | 0, 24, 24 |

All five sections pass. The section of index 19 is one Frobenius orbit of 24 points, so it alone leaves no proper
sub-sum. The rule therefore supports the claim.

## What the test supports, and its gap

Suppose the top-dimensional part of V(Y) were a union of two F_p-defined pieces of degrees d and 24 - d. Then every
section in general position would have d as a sub-sum of its orbit lengths. Suppose instead it were F_p-irreducible but
split into m > 1 conjugate components over F_p-bar. Then every orbit of such a section would have length divisible
by m. An empty common sub-sum and gcd 1 exclude both cases. Radical vdim = vdim = 24 excludes a top component along
which Y is not reduced.

Each section's direction cone Y(A w) (b = 0) has dimension 0, so the affine 4-space meets the closure of V(Y) in no
point at infinity, and by Bezout each top-dimensional component of degree e meets it in exactly e points counted with
multiplicity. So, modulo 32009, the top-dimensional (dimension 11) part of V(Y) is irreducible over F_p-bar and Y is
generically reduced along it, without a general-position assumption on that part. Embedded and lower-dimensional components of Y are not tested: a section of dimension 0
misses them. Characteristic 0 is not addressed either. The global equidimMax and radical of A5-605 remain unfinished.

## Control

The same five sections of Y * (z_1, z_2, z_3, z_4), whose top-dimensional part adds a linear 11-space of degree 1, read
25 reduced points with an orbit of length 1 in every section. The common sub-sums are {1, 24}, and the rule rejects
irreducibility. The self-test also checks the rule on synthetic partitions (a common sub-sum, and orbit gcd 2).

```sh
"$PYTHON" -B -W error scripts/a5_e8bar_sections.py --check docs/evidence/a5-e8bar-sections/result.json
"$PYTHON" -B -W error scripts/a5_e8bar_sections.py --self-test
```
