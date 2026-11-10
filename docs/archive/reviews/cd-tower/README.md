# Cayley-Dickson tower reviews

| File | Holds |
|---|---|
| [report.md](report.md) | one agent's analysis of the A_5 exceptional fibers against the Cayley-Dickson tower: 13 conjectures with falsifiers and survivors; no outside review |
| [pasted-analyses.md](pasted-analyses.md) | two unreviewed model analyses of the tower (associators, zero divisors, INT/FLOAT bit widths, GPU exact arithmetic, Ascella), pasted by the owner on 2026-11-09, verbatim |
| [pasted-analyses-verification.md](pasted-analyses-verification.md) | every factual statement of the pasted analyses checked against `gororoba_quantum/cd_core.py` and the repository records: 58 claims, 28 hold, 16 partly, 9 wrong, 4 hypothesis, 1 cannot check, with the scripts that decide them |
| [twisted-tower-verification.md](twisted-tower-verification.md) | a second pasted audit of the tower and the `cd_kernel` twisted-tower module it committed to gororoba-open: 19 claims checked by exact enumeration (12 hold, 4 partly, 2 wrong, 1 hypothesis), and the corrections to the module |

Corrections the verification establishes, each reproduced by its scripts:
- Ordered distinct imaginary basis triples associate in 6/0, 42/168, 882/1848, 11010/15960 cases at D = 4, 8, 16, 32
  (associating / non-associating). The non-associating share falls from 0.80 toward 0.5.
- The basis sign sigma_k is a 2-cochain, not a 2-cocycle, from D = 8 on: sigma(p,q) sigma(p^q,r) = sigma(q,r)
  sigma(p,q^r) fails on 168 of 512, 1848 of 4096 and 15960 of 32768 triples at D = 8, 16, 32. Its coboundary is the
  associator phase.
- A_5 holds 5040 signed ordered two-blade zero products on 588 signed two-blade elements; 252 is the count of
  nullity-12 elements in the nullity histogram {4: 168, 8: 168, 12: 252}.
- float64 products of residues in [0, p) stay exact while k (p - 1)^2 < 2^53: k <= 8,791,696 at p = 32009 and
  k <= 8,780,720 at p = 32029.
- The two Ascella associator contrasts belong to different jobs: +1.6127 (null +0.0001) to e13e5ed0 and +1.5859 (null
  +0.0099, itself nonzero at p = 0.0098) to 7ae2af4b.

Provenance limits of the verification: its scripts ran as `python3` (the repository convention is `"$PYTHON"`), and
the floating-point associator maxima of script s5 use `random.seed(3)`, not a QRNG draw, so those maxima are
illustrations; every count and verdict in the claim table is exact and seed-free.
