# Iso -> N- degree-2 kernel ideal K2 is radical at p = 32009 (chart criterion)

**Criterion.** For a homogeneous ideal K of k[y] and a linear form l with K : l = K, the ring A = k[y]/K injects into
its localization A_l, and A_l is isomorphic to C[l, 1/l] with C = k[y]/(K + (l - 1)); `subst(K, y_i, 1)` in the 17-variable ring presents C[y_i], which is reduced exactly when C is. A Laurent ring over a reduced
ring is reduced, so A is reduced when the affine chart C is reduced.

**Checks (Singular 4.4.1, p = 32009).**

| Check | Script and log | Result |
|---|---|---|
| The chart file and the Azure radical script carry one ideal | `same.sing` | `iso_k2.rel` (sha256 53852d5c...) and the ideal of `iso-global.sing` (the stopped global radical job) contain each other |
| Every coordinate is a nonzerodivisor | `colon.sing`, `colon.log` | K : y_i = K for i = 1..17, about 1 s in total; K has dim 5, degree 23 |
| Chart y_2 = 1 and chart y_3 = 1 are reduced | `chart2-bound.sing` (reads the digest-bound `iso_k2.rel`), `chart3.sing` (laptop), `chart2-bound.log`, `chart3.log`; `chart2.sing` read a cwd-relative copy | radical(Kc) reduces to 0 modulo Kc in 1 s and 5 s |
| Second prime p = 32029 | `p32029.sing`, `p32029.log` (relations of `a5-p2-iso/iso_p2/d2/`, 68 quadrics, degree-certified) | K : y_i = K for every coordinate; charts y_2 = 1 and y_3 = 1 reduced in 2 s and 9 s |
| Retained corroboration | `chart-iso-long-summary.json` (Kaggle kernels from `working/distribute/make_kernel.py`) | 12 of 17 coordinate charts reduced (1-5, 7, 8, 11-13, 15, 17); the 8,000 s timeouts fell in the minAssChar step after the radical |

**Conclusion.** K2 is radical at p = 32009 and at p = 32029. Chart 2 carries the proof at each prime; chart 3 is redundancy (a chart-1 reproduction was stopped unfinished after 3 minutes as unnecessary). The global `radical(K)` (13 h on the westus3 VM, Singular 4.3.2, plus about
8 h of an earlier local attempt) answers a question this settles in seconds. The prime decomposition of K2 remains
open: whole-ideal minAssGTZ and minAssChar exceeded about 40,000 s (both timed out at 41,000.1 s on a Kaggle kernel,
A5-332), and chart minAssChar did not finish in 8,000 s.
