# Implicitization probes of the rank-locus germ (2026-10-23)

Python and FLINT probes of the 32-dimensional rank-locus germ, retained as they ran. The logs record 127 quadrics of
rank 401 at witness 5 in degree 2 (107 quadrics of rank 421 after the fresh-direction filter, none failing at order
48), 65 quadrics of rank 463 at witness 4, 142 at witness 2 and 126 at witness 3, with 44 quadrics reconstructed
consistently across primes. No tracked note cites these counts; the open question they probe is stated in
[complex_skew_rank_geometry.md](../../../../../notes/complex_skew_rank_geometry.md). The
[Kaggle and local-run audit](../../../../../archive/reviews/kaggle-audit-2026-11-09/README.md) lists this directory as
undecided: no claim rests on it.

`quadric_q.py`, the producer of `quadrics_w1.json`, is not retained: it seeds its generator with a literal integer
that predates the QRNG rule, and the reproduction-seed ledger (`ci/reproduction_seeds.json`) admits no new row.
