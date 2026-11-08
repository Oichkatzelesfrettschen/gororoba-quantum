# Pre-run checklist: least-squares precision and speed sweep (docs/runbooks/compute-flags.md)

Run: `python fp_sweep.py fp-inputs.npz sweep.jsonl 2` in docs/local/fp-precision, system Python 3.14.9.

1. Memory cap: cgroup v2 `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` per configuration, one at a
   time; not an address-space cap. Small-slice peak 140 MB, full-size peak 141 MB (fp-backends.log, /usr/bin/time -v).
2. Wall-time cap: `timeout -k 10 900` inside the scope and `RuntimeMaxSec=960` on the scope.
3. Threads: OpenBLAS 1, 2, 4, 6, 10; QuadBLAS 1, 4, 10; FLINT 1, 4, 10; x87 Householder worker processes 1-10.
   The capsule shows 10 CPUs (6 cores, 12 threads); other sessions' pytest workers held 4-5 CPUs at the start
   (load average 16.5), so timings carry contention and each row records the load average before its runs.
4. Solver options: numpy `pinv` (SVD, default rcond), numpy `lstsq` (gelsd), scipy `lstsq` drivers gelsd, gelsy,
   gelss; x87 refinement steps 1-3; Householder QR and normal equations with Cholesky in longdouble and binary128
   (quaddtype backends sleef and longdouble); arb normal equations at 64, 128, 192, 256 bits.
5. Environment: `MALLOC_ARENA_MAX=2`, `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `OPENBLAS_NUM_THREADS`,
   `FP_*` knobs per row; OpenBLAS 0.3.34 DYNAMIC_ARCH selected core `Zen`, USE_OPENMP; numpy 2.5.4 baseline X86_V3;
   quaddtype 1.0.0 built `-march=native -O3`, meson release, SLEEF 3.9.0 PURECFMA scalar quad path.
6. Exactness: every backend is deterministic for a fixed configuration; the reference is arb 256-bit with rigorous
   radius (max 9.4e-73), certified independently by mpmath at 80 digits (solution error bound 1.7e-76).
7. Progress trace: one JSON line per configuration in sweep.jsonl, flushed; stdout to sweep.log.
8. Falsifier for a cap failure: a row whose error names exit 137 or 124, or a returncode -9, rather than a backend
   exception.
9. Measured-combinations row: none exists for this workload; the sweep adds one row per backend family.
10. Checkpoints: sweep.jsonl is appended per configuration; a rerun skips finished configurations.
11. End state: local results only; nothing to deallocate.
12. Run rulebook: expected under 30 minutes; an entry follows only if it runs longer.
