# Compute flags: memory caps, threads and solver options

This runbook is the flag review that precedes every command whose cost or
correctness depends on its options: computer algebra (Singular, msolve,
Macaulay2), simulators (Aer, cuStateVec), Python pools, compilers, CI tools,
cloud launchers and resource limiters, on the build host, Azure VMs, Kaggle
kernels or any other substrate. The tool sections below cover the tools
measured so far; a tool without a section gets one the first time it runs long. An agent or operator fills in the
checklist at the end before the run starts and records the filled checklist
beside the run's log. A run launched without it gets stopped and relaunched.

## Why the review exists

Every msolve run on the A_5 Rees-fiber eliminations died with exit 139 under a
`prlimit --as` cap while its resident set sat far below that cap:

| Cap | msolve flags | Death | Peak resident set |
|---|---|---|---|
| `prlimit --as` 80 GiB | `-t 4 -e 1 -g 2` | degree 7, "Allocating memory for hash-column lookup table failed" | 33.6 GB |
| `prlimit --as` 28 GiB | `-t 3 -m 200000 -s 24 -l 1 -e 1 -g 2` | degree 6, "Enlarging exponent vector for hash table failed for esz = 268435456" | 28.0 GB |
| `prlimit --as` 28 GiB | `-t 3 -s 24 -u 2 -e 1 -g 2` | same point, same message | 18.1 GB |

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

Set `MALLOC_ARENA_MAX=2` in the environment of every multithreaded C program
so glibc keeps two arenas instead of one per thread; this shrinks address-space
growth and fragmentation at no measured cost to these workloads.

## msolve 0.10.1

Authority: `msolve -h` of the binary in use. The passagemath wheel 10.8.13
ships msolve 0.10.1 linked to libgomp, FLINT and GMP.

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

## Singular 4.4

Singular's `std`, `slimgb`, `syz`, `eliminate` and `minAssGTZ` run on one
thread and expose no thread or vector flags. Parallelism comes from separate
processes through `parallel.py` or separate hosts.

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
| same | same | same | `-t 3 -s 24 -u 2 -e 1 -g 2`, cgroup `MemoryMax` 30 GiB, address space 1 TiB | running | death at resident 30 GiB means real memory need; passing degree 7 confirms the address-space diagnosis | candidate |

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
