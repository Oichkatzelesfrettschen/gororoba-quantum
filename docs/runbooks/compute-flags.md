# Compute flags: memory caps, threads and solver options

This runbook is the flag review that precedes every command whose cost or
correctness depends on its options: computer algebra (Singular, msolve,
Macaulay2), simulators (Aer, cuStateVec), Python pools, compilers, CI tools,
cloud launchers and resource limiters, on the build host, Azure VMs, Kaggle
kernels or any other substrate. The tool sections below cover the tools
measured so far; a tool without a section gets one the first time it runs long. An agent or operator fills in the
checklist at the end before the run starts and records the filled checklist
beside the run's log. A run launched without it gets stopped and relaunched.

[library-flags.md](library-flags.md) is the per-library companion: the environment
variables, API options and build facts of every package the repository imports.

## Why the review exists

Every msolve run on the A_5 Rees-fiber eliminations died with exit 139 under a
`prlimit --as` cap while its resident set sat far below that cap:

| Cap | msolve flags | Death | Peak resident set |
|---|---|---|---|
| `prlimit --as` 80 GiB | `-t 4 -e 1 -g 2` | degree 7, "Allocating memory for hash-column lookup table failed" | 33.6 GB |
| `prlimit --as` 28 GiB | `-t 3 -m 200000 -s 24 -l 1 -e 1 -g 2` | degree 6, "Enlarging exponent vector for hash table failed for esz = 268435456" | 28.0 GB |
| `prlimit --as` 28 GiB | `-t 3 -s 24 -u 2 -e 1 -g 2` | same point, same message | 18.1 GB |

Singular 4.4.1 reads standard input whenever it is not a terminal, even for `Singular --version`, so a
call from a background shell or a pipeline whose stdin stays open waits until its timeout (exit 124) before doing
anything. Every producer that spawns Singular, and every command that runs such a producer from a background job,
starts it with stdin from `/dev/null` (`< /dev/null`, or `stdin=subprocess.DEVNULL`). `sleep 20 | timeout 10
Singular --version` exits 124; the same command with `< /dev/null` returns in 0.01 s.

`RLIMIT_AS`, which `prlimit --as` and Python's
`resource.setrlimit(RLIMIT_AS, ...)` set, limits reserved virtual address
space, not resident memory. The msolve 0.10.1 source names the two failing
allocations: `enlarge_hash_table` in `src/neogb/hash.c` reallocates the whole
exponent block at each doubling (`esz * evl * sizeof(exp_t)` bytes, with the
old block still mapped until `realloc` returns), and `src/neogb/convert.c`
reallocates the hash-to-column map (`(esld - 1) * sizeof(hi_t)` bytes) once per
matrix. glibc also reserves one malloc arena per OpenMP thread. The address
space therefore runs far ahead of the resident set, and the cap refuses an
allocation that physical memory could serve, so the failure looked like a
fixed internal limit. Several debugging rounds, including a consultation of
five frontier models, went into msolve internals before reading the cap
itself. The confirming run under a cgroup memory cap with the address-space
limit lifted is recorded in the A_5 attachment evidence once it ends; until
then the address-space explanation is the leading one, not a measured fact.

The general rule: a resource limit, a default thread count, or an unexamined
solver default can masquerade as a property of the mathematics. Read every
flag of the launch line before blaming the algorithm.

## Memory caps

Every mechanism below is available; the review picks one memory limit and one
time limit per run from what the substrate supports and records why.

| Mechanism | What it limits | When it fits | Caveat |
|---|---|---|---|
| cgroup v2 `MemoryMax` (`systemd-run --user --scope -p MemoryMax=NG -p MemorySwapMax=0 CMD`) | resident memory plus page cache charged to the job; the kernel OOM-kills the job alone at the limit | default on the build host and Azure VMs | needs the `memory` controller delegated to the user manager (`cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers`) and lingering (`loginctl enable-linger USER`) so the scope survives logout |
| cgroup v2 `MemoryHigh` (same command, `-p MemoryHigh=NG`) | soft limit: the kernel reclaims and throttles above it instead of killing | pairing with `MemoryMax` to slow a job before it dies | throttling can stretch wall time severalfold |
| container limit (`docker run --memory`, Kaggle's own 32 GB) | the container's cgroup | runs that already sit in a container | the whole container dies, every job in it included |
| RSS watchdog (sample `VmRSS` of the job and its children, kill above N) | resident memory, at sample granularity | Kaggle kernels and other containers without a delegated cgroup; the multi-job template already samples every 30 s | a fast spike between samples escapes it |
| `prlimit --as=BYTES CMD`, `ulimit -v`, `resource.setrlimit(RLIMIT_AS, ...)` | virtual address space reserved by the process | single-threaded programs whose virtual-to-resident ratio was measured small | refuses allocations far below physical memory for msolve, OpenMP programs, JIT runtimes and anything that reserves before touching |
| `prlimit --rss`, `RLIMIT_RSS` | nothing on Linux since 2.6 | never | accepted and ignored by the kernel |
| `prlimit --data`, `RLIMIT_DATA` | heap and private anonymous mappings | rarely; counts reservations like `--as` | same caveat as `--as` |
| `timeout -k 10 SECONDS CMD` | wall time | every run, beside one memory limit | |
| `systemd-run -p RuntimeMaxSec=` | wall time of the scope or service | runs already under `systemd-run` | |

systemd-oomd on the build host acts on whole user-session cgroups: when
memory plus swap pressure passes about 90 %, it kills the entire session
slice, including the terminal that drives the agent and every job it
started. A job inside its own scope with `MemoryMax` and
`MemorySwapMax=0` dies alone at its limit before host pressure reaches the
oomd threshold, so every heavy job runs in such a scope, one heavy job at
a time, with the sum of the running scopes' `MemoryMax` below physical
memory.

A child process inherits `RLIMIT_AS` from its parent. A Python helper that
calls `resource.setrlimit(RLIMIT_AS, ...)` before spawning a solver caps the
solver's address space as well, and Singular then exits with "no more
memory" far below its cgroup limit; a driver that launches a solver sets no
address-space limit in its own process.

Set `MALLOC_ARENA_MAX=2` in the environment of every multithreaded C program
so glibc keeps two arenas instead of one per thread; this shrinks address-space
growth and fragmentation at no measured cost to these workloads.

## msolve

Authority: `msolve -h` of the binary in use. The passagemath wheel 10.8.13
ships msolve 0.10.1 linked to libgomp, FLINT and GMP; the build host's
system package is 0.11.0, so a measured row names its binary and holds only
for that version.

| Flag | Meaning | Setting for Rees eliminations |
|---|---|---|
| `-f FILE`, `-o FILE` | input, output | required |
| `-e N` | two-block DRL elimination order, first N variables eliminated | number of eliminated variables (`-e 1` for the variable `a`) |
| `-g 0/1/2` | print nothing / leading ideal / full reduced basis for the first prime | `-g 2` when the basis is the result |
| `-t N` | OpenMP threads | physical cores free for the job (2 on a Standard_FX4mds_v2 alone, 1 beside another job); hyperthreads add contention |
| `-s N` | initial hash table size 2^N (default 17) | `-s 24` skips early doublings |
| `-u N` | rebuild the hash table every N steps, dropping stale monomials (default 0, never) | `-u 2` when the monomial table drives memory |
| `-m N` | maximum pairs per matrix (default unlimited) | leave unlimited: it splits matrices without shrinking the monomial table |
| `-l 1/2/42/44` | exact sparse-dense / exact sparse (default) / probabilistic variants | `-l 2`; the probabilistic modes stay out of cited results |
| `-r 0/1` | reduce the final basis (default 1) | default |
| `-q 0/1` | signature-based F4 | experiment only |
| `-v 0/1/2` | verbosity; 2 prints per-step degree and matrix sizes | `-v 2`, the only progress trace |
| `-c`, `-d` | genericity handling for zero-dimensional solving | irrelevant to elimination |

There is no `-l 0`, no column-split option, and `-s` takes an exponent, not a
count.

Environment: `OMP_PLACES=cores OMP_PROC_BIND=close MALLOC_ARENA_MAX=2`.

Build: the wheel's F4 library (`libneogb`) carries no AVX-512 code and almost no
AVX2; its AVX2 and AVX-512 routines serve FGLM only. A Standard_FX4mds_v2
(Xeon Platinum 8573C) offers AVX-512 F/VL/BW/IFMA/VNNI. A native build
(`-O3 -march=native` on the target host) vectorizes the row reductions; the
expected speedup per step is unmeasured, and memory does not change.

Accuracy: computations over a prime field with `-l 1` or `-l 2` are exact and
deterministic.

Version pin. The build host runs the distribution package and each Azure VM a
native build of the same upstream release, so both sit on upstream's latest
tag. Read the tag with
`gh api repos/algebraic-solving/msolve/releases/latest -q .tag_name` and the
host's version with `msolve -V`; when they differ, update the host package and
rebuild on each VM:

```sh
sudo apt-get install -y build-essential autoconf automake libtool pkg-config libgmp-dev libmpfr-dev libflint-dev git
git clone --depth 1 --branch "$TAG" https://github.com/algebraic-solving/msolve.git "msolve-src-$TAG"
cd "msolve-src-$TAG" && ./autogen.sh
CFLAGS="-O3 -march=native -mtune=native -fopenmp -funroll-loops" ./configure --prefix="$HOME/msolve-$TAG"
nice -n 19 make -j2 && make install
"$HOME/msolve-$TAG/bin/msolve" -V
objdump -d "$HOME/msolve-$TAG/lib/libneogb.so" | grep -c zmm   # nonzero: AVX-512 kernels present
```

A launch line names the binary by its versioned prefix, never the wheel's
`sage_wheels/bin/msolve`. The v0.11.0 native build on a Standard_FX4mds_v2
carries 199 AVX-512 instructions in `libneogb`; the passagemath wheel carries
none.

## Singular 4.4

Singular's `std`, `slimgb`, `syz`, `eliminate` and `minAssGTZ` run on one
thread. `Singular --help` lists `--cpus`, `--threads` and `--flint-threads`;
they bound the parallel libraries (`parallel.lib`, `tasks.lib`) and FLINT or NTL
calls, not a single standard-basis computation. Parallelism for these
eliminations comes from separate processes through `parallel.py` or separate
hosts.

| Setting | Meaning |
|---|---|
| `option(redSB)` | reduced standard bases; set before the first `std` |
| `option(prot)` | prints progress only; no memory effect |
| `option(notWarnSB)` | silences warnings on non-standard-basis inputs |
| ordering | global (`dp`, `lp`, block orders) per the repository canon; local orderings (`ds`) run far slower on the A_5 strata |
| `GOROROBA_WORKERS` | worker count for the repository's process pools |

Cap: cgroup `MemoryMax` or the RSS watchdog. Singular's allocator reserves
little beyond its resident set, so an address-space cap usually works, but the
cgroup cap is the uniform rule.

## Substrate table

| Substrate | Cores | Memory cap | Notes |
|---|---|---|---|
| Build host | 6 cores, 12 threads | `systemd-run --user --scope -p MemoryMax` | the owner keeps it mostly idle |
| Azure Standard_FX4mds_v2 | 2 cores, 4 threads | `systemd-run --user --scope -p MemoryMax`, lingering on | 84 GB; two jobs share 2 physical cores |
| Kaggle CPU kernel | 4 vCPU (treated as 2 cores) | RSS watchdog in the kernel script | 32 GB, kernel death above about 31 GB |

## Measured combinations

Each row is a hypothesis: the best flag set found so far for one tool version,
host and workload, with the measurement behind it and the result that would
dethrone it. A new run that beats a row on the same workload replaces it in
the same change, and the old row moves to `superseded` with its measurement
kept, so the table records every combination tried and why it lost.

| Tool and version | Host | Workload | Flags and environment | Measured | Falsifier | Status |
|---|---|---|---|---|---|---|
| msolve 0.10.1 (passagemath 10.8.13) | Azure FX4mds_v2, beside one Singular job | A_5 E8bar->N+ Rees elimination | `-t 4 -e 1 -g 2`, `prlimit --as` 80 GiB | exit 139 in degree 7, resident 33.6 GB | | superseded: address-space cap |
| same | same | same | `-t 3 -m 200000 -s 24 -l 1 -e 1 -g 2`, `prlimit --as` 28 GiB | exit 139 in degree 6, resident 28.0 GB | | superseded: `-m` leaves the monomial table unchanged |
| same | same | same | `-t 3 -s 24 -u 2 -e 1 -g 2`, `prlimit --as` 28 GiB | exit 139 in degree 6, resident 18.1 GB; `-u 2` lowered the resident set by 10 GB at the same point | | superseded: address-space cap |
| same | same | same | `-t 3 -s 24 -u 2 -e 1 -g 2`, cgroup `MemoryMax` 30 GiB, address space 1 TiB | passed every point where the address-space-capped runs died; memory-cgroup OOM kill entering degree 7 at 31.4 GB resident, 36.2 GB virtual | | superseded: the 30 GiB cap itself; confirms the address-space diagnosis |
| msolve 0.11.0, native `-O3 -march=native` | same | same | `-t 2 -s 24 -u 2 -e 1 -g 2`, cgroup `MemoryMax` 38 GiB, `choom -n 1000`, `MALLOC_ARENA_MAX=2 OMP_PLACES=cores OMP_PROC_BIND=close` | memory-cgroup OOM kill entering degree 7 (first matrix 407116 x 432548), sampled peak 33.3 GB; reached degree 7 in 901 s against 841 s for the wheel at `-t 3`, both beside a Singular job | a run reaching degree 7 faster on the same thread count alone on the VM | superseded: degree 7 needs more than 38 GiB; the native build shows no measured speedup yet |
| OpenBLAS 0.3.34 (`blas-openblas`), numpy 2.5.4 | build host, Ryzen 5 5600X3D | 3000 x 3000 float64: matmul, `scipy.linalg.lu_factor`, `numpy.linalg.eigh` | `OPENBLAS_NUM_THREADS=6` | matmul 0.234 s, LU 0.341 s, eigh 4.24 s | a thread count or library beating all three | current best |
| same | same | same | `OPENBLAS_NUM_THREADS=1` | matmul 0.883 s, LU 0.358 s, eigh 3.17 s | | eigh is faster single-threaded at this size |
| AOCL-BLAS 5.3.0 (BLIS), numpy 2.5.4 | same | same | `BLIS_NUM_THREADS=6` | matmul 0.215 s, LU 0.715 s, eigh 7.60 s; checksum equal to OpenBLAS to ten digits | | superseded: removed from the host; LAPACK slower when threaded |
| same | same | same | `BLIS_NUM_THREADS=1` | matmul 0.856 s, LU 0.330 s, eigh 3.03 s | | superseded |
| Singular 4.4.1, python-flint 0.9.0 | build host | A_5 fiber cone, degree-by-degree membership rank (`fiber_cone_driver.py`), E8-bar->VB degree 4, 10 generators | `systemd-run --user --scope -p MemoryMax=9G -p MemorySwapMax=0`, `MALLOC_ARENA_MAX=2`, one thread, stage timeout 14400 s | 5,184 s in the products standard basis, 3.5 s linear algebra (155 x 20,339), peak 2.4 GB; a 3600 s stage timeout ends at exit 124 with 55 min of CPU | a run of the same degree under 5,184 s | current best; time-bound, not memory-bound |
| Singular 4.4.1 (passagemath-singular 10.8.13), python-flint 0.9.0 | Kaggle CPU session, 4 cores, about 30 GB | the same driver, three or one degree chains at once (one Singular per chain), p = 32029 | a `systemd-run` shim that drops the cgroup flags, `MALLOC_ARENA_MAX=2`, `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` | degree 3 of E8-bar->VB 784 s, X-+ 1,044-1,049 s each with three chains sharing the session, Iso 1,647 s alone; degree 2 of each 26-43 s | a session layout finishing the same chains sooner | current best for second-prime replays |
| Singular 4.4.1 | build host, then cloud VM | pivot saturation of the Rees ideal (`sat(H, g)`) on X-, Iso, E8-bar->VB, E8-bar->N+-, W8->N- | cgroup `MemoryMax` 10-78 GiB, one thread, 2-12 h | never finished: 9.4 GB at 12 h (X-), 72 GB at 10 h (E8-bar->N+) | a completion of any pair | superseded: the formulation stalls; caps change only the wait |
| Singular 4.4.1 (Arch package) | build host, one thread, alone | standard basis of J + m P_d inside the membership-rank products script (`d*-products.sing`): Iso degree 2 at p = 32009 and X- degree 3 at p = 32009 | `option(redSB)` then `std(Q)`, cgroup `MemoryMax=16G`, `MALLOC_ARENA_MAX=2` | Iso d2: 8.1 s with `redSB`, 11.5 s plain `std`, 14.7 s `slimgb`; X- d3: 415.8 s `redSB`, 421.2 s plain `std`, 1836.9 s `slimgb`; normal forms byte-identical across the three | a variant beating `redSB` std on X- d3 with identical nf.txt | current best: `slimgb` runs 4.4x slower at X- d3, and dropping `redSB` gains nothing; the Azure membership-rank runs keep `redSB` std |
| Singular 4.4.1 `radical` then `minAssChar` | build host | quadric relation ideal K2 of X-, E8-bar->N+, E8-bar->VB | cgroup 3 GiB, 600 s | X- in 1 s; Iso and W8 unfinished at 600 s | | current best; `minAssGTZ` ran 40,000 s on Iso without result |
| qiskit 2.5.2 `transpile` | build host, offline Heron r2 Targets (ibm_fez, ibm_kingston, ibm_marrakesh) | 7 families of `experiments.experiment_groups()` at 3-5 qubits, two dynamic; 8 ANU QRNG seeds per setting | `optimization_level=3`, default layout and routing (the `live_run.OPT_LEVEL` setting) | median routed cz equal to level 2 in every family (for example 98 against 291, 163, 98 at levels 0, 1, 2 on `design_c_32_1_16`); level 2 within 1-3 depth; `layout_method="dense"` worse by 1-53 cz; `routing_method="sabre"` identical to the default; seed spread up to 27 cz exceeds every level-2-versus-3 difference | a level, layout or routing setting with a lower median cz on these families, or a family above 5 qubits where level 3 and level 2 differ | current best; seed selection is the remaining lever |

A row records the tool version, the host, the workload, the full launch line
with environment, wall time, peak resident set, the furthest stage reached,
and the log path in the evidence directory that holds the run.

## Pre-run checklist

Record answers beside the run log:

1. Memory cap mechanism and value; for a multithreaded program, confirm it is
   not an address-space cap.
2. Wall-time cap.
3. Thread count against free physical cores on the host, other jobs included.
4. Every solver flag on the launch line, each checked against the binary's
   own `-h` or manual, with the reason for every non-default value.
5. Environment variables (`MALLOC_ARENA_MAX`, `OMP_*`, `GOROROBA_WORKERS`,
   `GLIBC_TUNABLES`).
6. Exactness: deterministic and exact, or probabilistic with the reason.
7. Progress trace (verbosity, RSS sampling) and where the log lands.
8. The falsifier: what the log shows if the run fails for the cap rather than
   the mathematics.
9. The measured-combinations row this run starts from, or a note that none
   exists; after the run, the row it adds, replaces or supersedes.
