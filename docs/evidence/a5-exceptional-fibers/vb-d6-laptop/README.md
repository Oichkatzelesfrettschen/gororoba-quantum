# E8-bar -> VB degree 6 at both primes

[`run-cells.sh`](run-cells.sh) and [`run-cells-p2.sh`](run-cells-p2.sh) ran engine v11
(`../replay/engine/fiber_rank_v11.py`, sha256 7849cbc71ccf1787...) in quotient mode, raw, on the Windows compute
workstation on 2026-11-09, one process per prime at once, with sparse closure tables (`--dense-tables-gb 0`), five
export chunks and the engine's own `--max-gb 30` preflight limit; the runner comment's 36 GiB is the figure in force
when it ran, and the workstation budget is now 52.5 GB RAM plus 13.4 GiB GPU memory (owner, 2026-11-09). Headers:
`../working/build/inputs/p32009-r10754/e8-vb.sing` (sha256 4dbcb4676ca0821a...) and
`../working/build/inputs/p32029-r9115/e8-vb.sing` (6b3cea4923b4e0e2...). Both cells exited 0
([`cells.events`](cells.events)) with empty error streams.

| p | N | r_N | blocks 0 / 1 / 2 / 3 | Singular export | products | closure | wall, peak RSS |
|---|---|---|---|---|---|---|---|
| 32009 | 20 | 420 | 138 / 98 / 92 / 92 | 10,646.7 s | 31.6 s | 112.8 s | 10,795.8 s, 1.71 GiB |
| 32029 | 20 | 420 | 138 / 98 / 92 / 92 | 10,523.5 s | 42.0 s | 125.1 s | 10,696.1 s, 1.65 GiB |

r_20 = 420 = HF(k[y]/K2, 6) certifies h_6 = 420 at p = 32009 (ledger A5-107) and at p = 32029 (A5-113). The export
takes 98.6 percent of the wall time, so engine v12 and the GPU path leave these cells unchanged. N = 19 and N = 18 run
next at both primes and fix the closing order (3d + 1 = 19 if r_19 = 420 and r_18 < 420) and the last jump.
