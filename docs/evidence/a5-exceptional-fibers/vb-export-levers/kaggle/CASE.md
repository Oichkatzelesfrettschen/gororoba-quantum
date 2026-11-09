# Case: Kaggle CPU kernels for the E8-bar -> VB degree-7 export and the variable-order screen

Approval: the owner's standing ruling of 2026-11-09 for Kaggle sessions that finish under 12 hours (AGENTS.md,
"Hardware services"). Substrate: two Kaggle CPU sessions (4 cores, 30 GB each), passagemath Singular 4.4.1. Cost: free.

| kernel | jobs | measures | estimate |
|---|---|---|---|
| `a5-vb-d7-slimgb-p32009` | `slimgb` of J + m^21 and J + m^22; the identity order and six rotations of the variable order at N = 15 | the degree-7 export on a second host, and whether the variable order moves the export cost | N = 21 about 2 to 9 h, N = 22 about 3 to 11.4 h (the `std` extrapolation of the plan divided by the measured `slimgb` factor, times the 1.6 slower Kaggle Xeon); N = 15 about 6 to 10 min each |
| `a5-vb-d7-slimgb-p32029` | `slimgb` of J + m^21 and J + m^22 | the same at the second prime | as above |

Falsifiers:
- A reduced basis whose sha256 differs from `s.txt` of the engine-v13 export on the Windows workstation at the same
  prime and N refutes host independence of the export.
- A rotation whose N = 15 kbase size differs from 6,105 refutes the order change as a relabeling.
- A rotation that is no faster than the identity order refutes the variable-order lever.

Each job stops at 41,000 s, so the session ends inside Kaggle's 12-hour limit. A job stopped there records its
`rc` (124) and wall time in `summary.json` as a lower bound on the cost.
