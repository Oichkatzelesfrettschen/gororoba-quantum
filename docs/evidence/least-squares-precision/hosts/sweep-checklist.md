# Pre-run checklist: portable least-squares sweep (docs/runbooks/compute-flags.md)

Run: `"$PYTHON" fp_sweep.py fp-inputs.npz hosts/LABEL-full.jsonl --host-label LABEL --idle-wait` and
`... hosts/LABEL-quick.jsonl --host-label LABEL --quick`, `$PYTHON` the system Python 3.14.9 of the build host.

1. Memory cap: `min(8 GiB, 0.6 x MemTotal)`. `fp_host.choose_cap` runs a trial `systemd-run --user --scope -p
   MemoryMax=N -p MemorySwapMax=0` and reads `memory.max` and `memory.swap.max` back from the scope's cgroup; a scope
   that reads back as requested is the cap (cgroup v2, not an address-space cap). Without it, `RLIMIT_AS` on Linux and
   macOS (never below 2 GiB, since OpenBLAS reserves address space at import), and no cap on native Windows. Every
   row records the mechanism, the bytes and whether the probe saw it enforced.
2. Wall-time cap: `subprocess` timeout 900 s per run, a process-group kill on expiry (returncode 124), and
   `RuntimeMaxSec=960` on a systemd scope.
3. Threads: 1, 2, 4, ... up to `min(os.cpu_count(), parallel.workers())`, plus that count when it is not a power of
   two; applied to OpenBLAS (`OPENBLAS_NUM_THREADS`, plus `VECLIB_MAXIMUM_THREADS` on macOS), QuadBLAS, FLINT and the
   x87 worker processes. Quick keeps `min(cpus, 4)`.
4. Solver options: as in the build-host sweep ([../sweep-checklist.md](../sweep-checklist.md)); quick keeps the three
   scipy drivers, two refinement steps and arb at 128 bits.
5. Environment: `MALLOC_ARENA_MAX=2` and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` on Linux, the `FP_*`
   knobs per row; every row embeds the host record (machine, OS family, CPU model, numpy SIMD lists, OpenBLAS core,
   package versions) from `fp_host.host_record`.
6. Exactness: reference arb 256-bit; the five `inputs_sha256` digests of every row must equal the retained
   `results/quandela/cases/ascella_cz_ensemble/forecast.json` digests on the build host (falsifier: any mismatch).
7. Progress trace: one JSON line per configuration, flushed; a rerun skips finished configurations.
8. Falsifier for a cap failure: a row whose error names exit 137 or 124, a returncode -9, or an OpenBLAS
   "Memory allocation still failed" message under `RLIMIT_AS`, rather than a backend exception.
9. Idle wait: each run waits for a 1 minute load average below 0.5 x `os.cpu_count()`, at most `--idle-timeout`
   seconds (3600), then exits 3; the wait is recorded per run.
10. Checkpoints and end state: local results only; nothing to deallocate.
