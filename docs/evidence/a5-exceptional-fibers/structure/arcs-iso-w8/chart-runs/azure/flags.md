# Flag review: Iso one-chart saturation on Azure FX4mds_v2 (westus3), passagemath Singular 4.4.1

Question: dim A/(t) for A = k[t, z]/((J, a0 z_i - G_i) : a0^infinity), a0 = l0(G), Iso -> N- at p = 32009 and 32029.
Measured so far (lab-a1, aarch64, apt Singular 4.4.1, `sat` of elim.lib, option(redSB), no l0(z) relation up front):
p = 32029 died at 5.2 GB (prlimit 5 GB) after 57 min inside `sat`; p = 32009 at 6 GB after 70 min, still inside `sat`.

| Knob | Choice | Reason |
|---|---|---|
| Host | Standard_FX4mds_v2: 4 vCPU, 84 GB, high-frequency Xeon | Singular's std/sat is single-threaded; FX has the fastest single core in the quota; 84 GB clears the lab-a1 wall by 8x |
| Binary | passagemath-singular 10.8.13 wheel (Singular 4.4.1) in a venv | measured 1.55x faster than apt 4.3.2 on this workload class (memory note `compute-placement`); same version as the laptop runs |
| Parallelism | portfolio of 4 single-threaded processes: {32009, 32029} x {sat, elim} | uses all 4 vCPUs; two independent algorithms per prime cross-check each other; the first to finish decides, the second confirms |
| Saturation, method sat | `sat(C, a0)` of elim.lib (iterated quotients) | the method that ran on lab-a1, for comparability |
| Saturation, method elim | `eliminate(C + (1 - w a0), w)` in ring (w, t, z) with block ordering (dp(1), dp(23)) | Rabinowitsch elimination: one std instead of a quotient chain; often faster when the saturation exponent is high |
| l0(z) - 1 | added to C before saturating, both methods | a0 (l0(z) - 1) = l0(a0 z - G) lies in C, so the saturation is unchanged and one z coordinate becomes dependent, shrinking the std |
| option(redTail) | off (`option(noredTail)`) during sat/elim and the fiber std; one final `std` with redSB only for the written ideal | tail reduction of every new element dominates many std runs; dim and mult need only a standard basis |
| option(prot) | on, to the log | progress trace: degree steps and pair counts show where a crash or timeout happened |
| Checkpoints | write the saturated ideal, its dimension and l0(z) check, then the fiber ideal, each to its own prime- and method-specific file the moment it exists | a crash or timeout after the saturation keeps the expensive part |
| Memory guard | none per process (84 GB shared, four processes); a per-minute RSS and free-memory log; the job script kills the largest process only if MemAvailable drops below 4 GB, so the others survive | one runaway process cannot take down the portfolio |
| Timeout | 8 h per process (`timeout 28800`), `/usr/bin/time -v` | owner-approved cost bound (8 h x $0.547/h) |
| End state | local watcher copies every result with sha256 comparison, then `az vm deallocate` (not delete); DevTestLab auto-shutdown at deadline + 30 min deallocates if no watcher is online | a guest OS shutdown leaves the VM allocated and billed; deallocation stops compute billing and keeps the OS disk with the results |
| Transparent huge pages | `madvise` (Ubuntu default) left as is | omalloc manages its own pages; no measured gain recorded |
