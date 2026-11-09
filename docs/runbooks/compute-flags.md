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
[computer-algebra.md](computer-algebra.md) holds the formulation foundations (which
computation to run at all), and the [run rulebook](run-rulebook.md) records each long
run's specific choices and every departure from these foundations, with the reason.

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
cgroup cap is the uniform rule. Several processes sharing one host share one
watchdog that stops only the largest process when available memory runs low, so
one runaway computation does not end the others.

Foundations for a long Singular run:

- Parallelism is a portfolio of independent single-threaded processes: different
  primes, different algorithms for the same ideal (`sat` against the Rabinowitsch
  elimination), or different QRNG choices. Count physical cores, not hyperthreads:
  a process sharing a core runs slower, which a portfolio accepts only for the
  cross-check it buys.
- `option(prot)` writes a progress trace to the log, so a timeout or memory death
  shows the stage it reached. On the membership-rank products `redSB` std was
  measured fastest (table below); `option(noredTail)` is a hypothesis for
  saturations and eliminations until a row measures it.
- Write each stage's result to its own file, named by the run's fiber, prime and
  method, the moment it exists; never a fixed name two concurrent runs share.
- Launch a remote job with `setsid nohup sh -c '...' > /dev/null 2>&1 < /dev/null &`
  so the ssh session returns; a wrapper timeout around an ssh that keeps the job's
  descriptors open exits 124 while the job itself runs on.

Cloud lifecycle: copy every result, compare sha256 between the VM and the local
copy, and only then end the VM. `az vm deallocate` stops compute billing and keeps
the OS disk with every result, for a later copy when no watcher was online; a guest
OS `shutdown` leaves the VM allocated and billed; `az group delete` removes the
results with the VM and follows only a verified copy. A DevTestLab auto-shutdown
schedule deallocates: set it past the last job's time limit as the backstop for an
absent watcher, never inside a run.

## Marker 1.10 (PDF transcription drafts)

`marker_single` (marker-pdf 1.10.2 with surya-ocr 0.17.1, torch 2.12.1+cu130, venv `~/.venvs/marker`) converts a
PDF to Markdown with layout, OCR and equation models, and selects CUDA on the build host by default
(`TORCH_DEVICE=cuda`). Its models download on first use. `MODEL_CACHE_DIR` places them (3.3 GB). Surya stages each
download through `tempfile`, so `TMPDIR` must sit on a volume with room for the 1.35 GB layout model. Both point at
`~/.venvs/marker/model-cache`, because `~/.cache` and `/tmp` are 4 GiB overlays in agent shells, where a first run
fails with `ENOSPC`.

| Flag | Reason |
|---|---|
| `--output_format markdown` | the transcription format of the documents repositories |
| `--disable_image_extraction` | figures stay in the PDF; the transcription carries text, tables and LaTeX |
| `--paginate_output` | page separators (`{N}` followed by dashes, zero-based) give every note a page locator |
| `--disable_tqdm` | keeps the per-paper log short |

On born-digital arXiv PDFs, prose, tables and inline mathematics come out exact on the pages compared against their
images. Display matrices can lose an arrow label or turn a product into a column separator. A transcription therefore
records which pages were compared against page images, and a note checks every display equation it cites against the
PDF. One job runs at a time: a 36-page paper peaks at 4.1 GB resident and about 7 GB of GPU memory. Cap: an RSS
watchdog that kills the process group above 16 GiB, where the shell has no `systemd --user` manager.

Marker reads a PDF's text layer wherever one exists, so a scanned PDF that carries an embedded OCR layer inherits that
layer's errors ("estímate", "de" for dc, "curren!" in 2403.18833v1). `--force_ocr` makes Surya read the page images
instead; it also needs `--paginate_output` and the same cache variables.

Other engines for display mathematics. Where arXiv holds the authors' TeX source, that LaTeX is the authority. Without
one, every Marker display equation is cropped at 300 dpi and read by three dedicated document-OCR models; Marker's
reading stays where one of them agrees with it, the models' common reading replaces it where all three agree with each
other and not with Marker, and every other equation goes to a page-image check. The measured row "math OCR on 180
display equations" below holds the evidence: on born-digital arXiv crops labeled with the authors' LaTeX, the three
models each read 153-160 of 180 exactly against Marker's 133, and where all three agreed they were exact on 143 of 149;
readings that differ in a sign, relation, arrow, accent, prime or digit no longer count as agreeing.
The pipeline and benchmark live in gororoba-infrastructure `transcribe/` (its README.md, "Math OCR engines").

| Engine | Environment | Input | Failure seen |
|---|---|---|---|
| MinerU2.5-Pro-2605 (1.2B, Apache-2.0) | `~/.venvs/docvlm` (torch 2.12.1+cu130, transformers 5.22.1, mineru-vl-utils 2.0.8), `HF_HOME` on the main disk, CUDA bf16 | one cropped equation, `content_extract(type="equation")` | misses 20 of 180, mostly bold notation (`\pmb`, a dropped `\mathbf`) and a trailing period |
| GLM-OCR (0.9B, MIT) | Ollama `glm-ocr`, prompt `Formula Recognition:`, `temperature` 0, `num_ctx` 4096 | one cropped equation | misses 25 of 180, mostly a dropped superscript or prime; writes `\tag {N}` with a space; 0.47 s per crop |
| PaddleOCR-VL-1.6 (0.9B, Apache-2.0) | `~/.venvs/docvlm`, prompt `Formula Recognition:`, processor defaults (the model card's `min_pixels` override fails under transformers 5.22) | one cropped equation | misses 27 of 180, mostly bold notation; puts `\eqno(N)` inside the display |
| qwythos-9b and Qwythos-9B-v2 (Ollama, vision) | `ollama`, prompt for exact LaTeX, `think` false, `num_ctx` 4096 (32k spills 17 % to the CPU) | one cropped equation | 58 and 78 of 180 exact; bold and spacing differences, `\begin{array}` wrappers |
| Nougat-base, pix2tex 0.1.4 (CPU) | `~/.venvs/mathocr` | page; crop | invented equation numbers; wide displays fail; not rerun on the 180 crops |

## Substrate table

| Substrate | Cores | Memory cap | Notes |
|---|---|---|---|
| Build host | 6 cores, 12 threads | `systemd-run --user --scope -p MemoryMax` | the owner keeps it mostly idle |
| Azure Standard_FX4mds_v2 | 2 cores, 4 threads | `systemd-run --user --scope -p MemoryMax`, lingering on | 84 GB; two jobs share 2 physical cores; a DevTestLab daily auto-shutdown schedule (`shutdown-computevm-NAME`) deallocates the VM and kills every job, so the launcher either disables it (`az vm auto-shutdown --off`, confirming no schedule remains) or sets it past the last job's time limit as the backstop for an absent watcher; a watcher that deallocates the VM at one job's end ends every other job on it, so it checks every job's marker first or co-located jobs run on separate VMs |
| Windows compute workstation (WSL) | 16 cores, 32 threads | none: the owner keeps no arbitrary memory cap on its jobs | 54 GB visible to WSL; one `systemd --user` unit per job |
| Kaggle CPU kernel | 4 vCPU (treated as 2 cores) | RSS watchdog in the kernel script, reading cgroup `memory.max` less `memory.current` | 31.35 GiB total, 29.5 GiB cgroup headroom; a job fits below about 27 GiB ([substrates](../notes/kaggle/substrates.md#weekly-budget-and-tandem-capacity)) |

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
| Singular 4.4.1 `mres(K, 0)` and `betti` | build host, one thread | Cohen-Macaulay test of the quadric rings k[y]/K2 at p = 32009 by minimal free resolution | cgroup `MemoryMax` 12 GiB, `timeout 1800` per fiber | E8-bar->VB 0 s and X- 163 s (projective dimension 14); Iso, E8-bar->N- and W8 stopped at 1,800 s each without a resolution | | superseded by the linear-section length test below |
| Singular 4.4.1 through `parallel.py` (`docs/evidence/a5-exceptional-fibers/k2_cm.py`) | build host | the same Cohen-Macaulay test on all 14 retained K2 sources at both primes: std of K2 plus a = dim general linear forms with Vandermonde coefficients, length against degree; minimal primes and spans for E8-bar->VB | one process per source, no cap needed | 1.05 s wall for all 14; byte-identical rerun | a source whose quotient by the forms is not zero-dimensional (the forms then fail to be a system of parameters, and the producer raises) | current best: decides Cohen-Macaulayness in either direction without a resolution |
| `fiber_cone_driver.py` with Singular 4.4.1 | build host | degree-2 membership receipt, W8->N- at p = 32009 (24 generators) | `--memory-gib 16 --timeout 21600`, the driver's own `systemd-run` unit with `MemorySwapMax=0` | the 32029 receipt measured 9,860 s in the products standard basis and 575 s in membership on a Kaggle CPU; the unreceipted 32009 degree-2 run peaked at 6.7 GB; this run: degree-certified in 6,904 s wall (products std 6,560 s, membership 325 s, linear algebra 19 s), peak 6.7 GB | a peak above 16 GiB or a products stage beyond 21,600 s | current best for degree 2 at 24 generators |
| Singular 4.4.1, fiber-rank engine v7 export (`reduce` called once per standard monomial) | Windows compute workstation (WSL, 54 GB) | quotient export of E8-bar->N- at p = 32009, N = 15: multiplication table of t1 on 31,599 standard monomials | one Singular process, no cap (workstation rule) | 6,961 s for the table, 31,599 calls of about 220 ms each | | superseded: one batched call computes the same table in 45 s |
| Singular 4.4.1, fiber-rank engine v9 export (one batched `reduce(var(k)*B, s)` per table or standard-monomial range) | Windows compute workstation (WSL, 54 GB) | the same export: `std(J + m^15)` (`option(redSB)`, dp), nine tables in three ranges each, generator normal forms | `--export-chunks 3`, worker pool of `parallel.py` | std 7,097 s on one thread; table ranges of about 10,500 entries 17-69 s each; batched t1 table from the saved basis 45 s, equal to the serial table in all 31,599 rows; products 3,569 s, closure 353 s, peak RSS 31.3 GiB against a 47.3 GiB preflight | a std variant or tool that reaches the same `qB.txt` in under 7,097 s | current best; `std` is the bottleneck and runs on one thread |
| fiber-rank engine v10 (`--k2-receipt`: products indexed by the standard monomials of k[y]/K2) | build host | E8-bar->N- products at degree d: 83 rows at d = 2 and 225 at d = 3 in place of 231 and 1,771; 495 at d = 4 and 952 at d = 5 in place of 10,626 and 53,130 | the degree-2 membership receipt of the same header and prime, 64 strided nonstandard check products per run | r_N and every per-block rank equal to engine v9 on the comparison grid in `docs/evidence/a5-exceptional-fibers/v10-comparison.jsonl` | a grid case whose r_N or block ranks differ from engine v9, or a check product that raises a rank | superseded by engine v11 for memory: the products term of the preflight shrinks by the ratio of the counts, and the D x D tables remain |
| fiber-rank engine v11 (per-block generator matrices built once in ascending generator order; closure over per-block variable tables) | build host, one process | E8-bar->N- d = 4 at p = 32009, N = 15 (D = 31,599), reusing a finished export, `--k2-receipt` | cgroup `MemoryMax=24G` (32G for dense tables), `MALLOC_ARENA_MAX=2`; sparse closure by default, `--dense-tables-gb 20` for dense | r 495 with blocks 158, 137, 100, 100; sparse tables: products 354 s, closure 1,158 s, peak 9.2 GiB (preflight 6.65 GiB undercounts); dense tables: products 497 s, closure 1,040 s, peak 9.9 GiB; engine v9 on the workstation: products 3,569 s, closure 353 s, peak 31.3 GiB | an engine reaching r_15 = 495 below 9.2 GiB peak, or a same-host closure much faster than 1,040 s | current best for N >= 15: memory is no longer the D^2 wall; the closure is the slowest stage on this host and dense tables gain about 10 % |
| Singular 4.4.1 `degBound` | build host, alone | std of J + m^11 for E8-bar->N- at p = 32009 | `option(redSB)`, dp; `degBound=11` against unbounded | 133.0 s against 144.8 s, identical bases (3,847 elements, vdim 7,887, mutual reduction to zero); Singular drops the standard-basis attribute on the bounded result | a larger-N run where degBound saves more than 8 %, or a basis that differs | candidate: 8 % on std; adoption needs the cross-reduction check in the export |
| msolve 0.11.0 (`/usr/bin/msolve`), Singular 4.4.1 | build host, each alone | dp/grevlex standard basis of J + m^N for E8-bar->N- at p = 32009, N = 7, 8, 9 (m^N given as C(N+8, 8) monomial generators to msolve) | msolve `-t 4 -g 1` (exact sparse linear algebra, the default `-l 2`), cgroup 16 GiB; Singular `option(redSB); std` | msolve 8.5, 33.1, 93.5 s at peak 0.47, 1.76, 6.24 GB; Singular 1.7, 6.0, 16.9 s at 18-35 MB; leading ideals equal at all three N (916, 1,376 and 1,996 elements); msolve at N = 11 (75,598 generators) hit a 20 GiB cgroup kill within 8 s | an msolve or other F4 run that beats Singular's std on J + m^N | superseded for this workload: F4 on four threads runs 5-6x slower than one-thread std and its memory grows about 3.5x per N; msolve serves as an independent leading-ideal check at small N |
| qiskit 2.5.2 `transpile` | build host, offline Heron r2 Targets (ibm_fez, ibm_kingston, ibm_marrakesh) | 7 families of `experiments.experiment_groups()` at 3-5 qubits, two dynamic; 8 ANU QRNG seeds per setting | `optimization_level=3`, default layout and routing (the `live_run.OPT_LEVEL` setting) | median routed cz equal to level 2 in every family (for example 98 against 291, 163, 98 at levels 0, 1, 2 on `design_c_32_1_16`); level 2 within 1-3 depth; `layout_method="dense"` worse by 1-53 cz; `routing_method="sabre"` identical to the default; seed spread up to 27 cz exceeds every level-2-versus-3 difference | a level, layout or routing setting with a lower median cz on these families, or a family above 5 qubits where level 3 and level 2 differ | current best; seed selection is the remaining lever |
| Singular 4.4.1 and python-flint 0.9.0 through `parallel.py` (`docs/evidence/a5-exceptional-fibers/arcs/replay.sh`) | build host, 12 CPUs, beside other sessions' Singular jobs | arc certificates of E8-bar->N- and E8-bar->N+ at p = 32009 and 32029: minimal primes of sqrt(K2), 1,296 symbolic arc families, 270-point numeric certificates and a 540-arc survey per target | `ulimit -v 8388608`, `GOROROBA_WORKERS=3`, Singular stdin closed, 900 s timeout per script, `PYTHON` of `ci-py3.14.7-qiskit261` | 8 min 4 s for the four targets (106-136 s each), a second replay byte-identical to the first; peak resident set not measured | a replay of the same four targets under 8 min with equal records | current best |
| Singular 4.4.1 (passagemath-singular 10.8.13) | Azure FX4mds_v2 (2 cores, 4 threads, 84 GB), four processes | saturation of a blowup chart of Iso -> N- with dense a0 = l0(G) (17 QRNG coefficients), 23 variables, p = 32009 and 32029 | `option(noredTail)`, `option(prot)`, l0(z) - 1 added first; `sat` of elim.lib against `eliminate(C + (1 - w a0), w)` with (dp(1), dp(23)); `timeout 28800`, shared RSS watchdog | no run finished: elimination 29.7 GB at 3:21 and 52.1 GB at 7:29 (watchdog), sat 15.1-15.8 GB at the 8 h limit; bases of 20,000-37,000 elements; lab-a1 sat died at 5.2 GB (57 min) and 10.5 GB (3:26) | a saturation of this chart finishing in 8 h on 84 GB | superseded: dense chart too large; `sat` grows about 3.4x slower in memory than the Rabinowitsch elimination here |
| Singular 4.4.1 (passagemath-singular 10.8.13) | build host capsule (AMD Ryzen 5 5600X3D, 10 CPUs visible, 47 GiB), up to three single-thread processes at once, each under 0.5 GB resident | saturation by t2 of Q_k = (J, k linear forms in G) for Iso -> N- at p = 32009 (six variables, global `dp`), k = 5 and k = 3, plus the four X controls | `prlimit --as` 20 GiB, `timeout -k 10` 3,600 s (k = 5) and 7,200 s (k = 3), `/usr/bin/time -v`, `MALLOC_ARENA_MAX=2`, `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `option(prot)` on Iso, no `redSB` or `noredTail`, stdin from `/dev/null`; `sat_with_exp(Q, t2)` against the `dp` standard basis of Q homogenized with h, a `dp` standard basis in the ring (other variables, h, t2), division of each element by its highest power of t2, h = 1 | k = 5: 3,022 s at 382 MiB (`sat_with_exp`) against 272 s at 377 MiB (homogenized); k = 3: 37 s at 74 MiB against 16 s at 81 MiB; X controls 6.7-9.7 s against 0.8-1.9 s; dimension, degree and reading identical in all six pairs (`docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/logs/`, `.time` files) | a saturation by t2 of the same Q_k that finishes sooner, or a pair that disagrees | current best: the homogenized saturation wherever the saturating function is a variable; `sat_with_exp` stays the twin that confirms |
| same | same | saturation by the dense QRNG form a0 = l0(G) of the same Q_k (a0 lies in I, so the saturation removes V(I) everywhere) | `sat_with_exp(Q, a0)`, limits as above (8 GiB, 3,600 s on the cross-checks) | Iso k = 5: 814 s at 330 MiB, dimension 0, degree 720, origin off; X k = 2: 177-187 s at 42 MiB against 2-10 s for t2; X k = 3: unit ideal in under 0.5 s (`docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/logs/`) | a faster a0 saturation, or a reading that differs from the t2 saturations | cross-check only: a0 costs 3 to 100 times the homogenized t2 saturation on the cases measured |
| Singular 4.4.1 (passagemath-singular 10.8.13) with a truncated-series Newton iteration over dual numbers (`docs/evidence/a5-exceptional-fibers/structure/c30-bounded/`) | build host capsule, one process at a time | fiber-cone plane of the point blowup of W8 -> N- at one QRNG point of P(L0): series order 10 in two variables, 24 x 4 matrix, K2 and K2 : P membership, Jacobian rank | `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0`, `timeout 300`, `dp` and one local `ds` ring of two variables, `MALLOC_ARENA_MAX=2` | 45 to 52 s at 26 MiB per point (five points, both primes); the controls take under 0.4 s | a plane that fails a K2 generator while every exactness check passes, or a faster formulation | current best |
| same | same | the global t-space slice of codimension 5 for W8 -> N- (saturation of (J, l_1(G), ..., l_5(G)) by t2 through the homogenized standard basis, five QRNG forms of degree 8) | `option(prot)`, `dp`, 8 GiB cgroup cap, `timeout 900` | no standard basis in 900 s (exit 124); degree bound 4 * 8^5 = 131,072; resident set in the retained `.rss` | a finished run at a larger limit | stalled |
| marker-pdf 1.10.2 (surya-ocr 0.17.1, torch 2.12.1+cu130) | build host, RTX 4070 Ti 12 GiB, one job at a time | 20 born-digital arXiv PDFs, 724 pages, to Markdown transcriptions | `TORCH_DEVICE=cuda`, `MODEL_CACHE_DIR` and `TMPDIR` on the main disk, `--output_format markdown --disable_image_extraction --paginate_output --disable_tqdm`, RSS watchdog 16 GiB | 6,862 s for the 20 (9.5 s per page, 145-746 s per paper), peak resident 5.4 GiB; prose, tables and inline mathematics exact on the 12 pages of 2609.28901 compared against their images, where two display equations came out garbled | a setting that converts the same pages faster with no more display errors | current best |
| marker-pdf 1.10.2 with `--force_ocr` | same | 2403.18833v1, 12 scanned pages with an embedded OCR layer | the flags above plus `--force_ocr` | 135 s; prose correct where the default run inherited the embedded layer's errors; against the page images, one strict inequality for a non-strict one (Eq. 22), a dropped norm in a table, most equation numbers dropped and one invented reference title | a run on the same pages with fewer image-check corrections | current best for scanned PDFs with an OCR layer |
| math OCR on five display equations with known ground truth (2609.28901 Eqs. 3 and 7, 1602.06402 p. 102, 2408.08292 Eq. 145, 2111.08152 Eq. E10) | build host; Ollama on the GPU, the rest on CPU | one equation per item, criteria per equation | Marker 1.10.2; pix2tex 0.1.4 on tight crops; Nougat-base on whole pages; qwythos-9b on tight crops | exactly right: Marker 1 of 5, pix2tex 0 of 5, Nougat 3 of 5 (one with an invented equation number), qwythos-9b 4 of 5 (Eq. 3 with its matrices and rotated labels right, "A =" misread); 5-91 s per item for qwythos, 21-197 s per page for Nougat | an engine that gets Eq. 3 right, or a test set on which qwythos falls below Nougat | superseded by the 180-equation row |
| math OCR on 180 display equations labeled with the authors' LaTeX (first ten pages of eight arXiv papers, born digital, crops located by Marker JSON and matched to the source through the PDF text layer) | build host; Ollama 0.40.13 and `~/.venvs/docvlm` on the GPU, one engine at a time except PaddleOCR-VL beside MinerU | one 300 dpi crop per display | Marker 1.10.2 (its page reading); MinerU2.5-Pro-2605, PaddleOCR-VL-1.6, Chandra 2 (transformers); GLM-OCR, DeepSeek-OCR, Qwen3-VL-8B-Instruct, Gemma-4-26B, qwythos-9b, Qwythos-9B-v2, Qwythos-27B (Ollama, `num_ctx` 4096, temperature 0) | exact by printed symbols (spellings that print alike count as equal): MinerU 160, GLM-OCR 155, PaddleOCR-VL 153, Marker 133, Qwen3-VL 108, DeepSeek-OCR 99, Qwythos-9B-v2 78, qwythos-9b 58 of 180; Gemma 43 of 60, Chandra 54 of 79, Qwythos-27B 5 of 12; 0.47 s per crop for GLM-OCR; with the three leading engines, Marker's reading kept on 144, replaced by their common reading (MinerU's first, then GLM-OCR's) on 28 and sent to a check on 8, 159 of the 172 kept or replaced exact (thresholds chosen on this set) | an engine above 160, a scanned-page set on which the verdict thresholds lose to Marker alone, or a CDM score that reorders the leading three | current best: MinerU2.5-Pro, GLM-OCR and PaddleOCR-VL as the cross-check engines; gororoba-infrastructure `transcribe/` README holds the table |
| numpy 2.5.4 `pinv`, scipy 1.18.1 `lstsq` on OpenBLAS 0.3.34 | build host capsule (10 CPUs), other sessions' pytest beside it (load 2 to 22) | least squares of the Ascella CZ tomography prediction, 576 x 256, 501 right-hand sides, scored against arb 256-bit | `OPENBLAS_NUM_THREADS` 1 to 10, drivers gelsd, gelsy, gelss; cgroup `MemoryMax=8G`, `MemorySwapMax=0`, `MALLOC_ARENA_MAX=2` | precision score 47.2 to 49.9, best `gelsy`; times 0.08-9 s, varying with load more than with threads; peak 141 MB | a float64 driver scoring above 49.9 on the same fit | superseded for retained records by certified arb ([least-squares precision](../evidence/least-squares-precision/README.md)) |
| numpy `longdouble` (x87 80-bit) Householder QR | same | same | worker processes 1 to 10 over the right-hand sides | precision score 59.5; 1.01 s at one worker, 0.62 s at eight | an x86 arithmetic scoring above 59.5 under 0.6 s | fastest beyond float64; x86 only |
| numpy-quaddtype 1.0.0 (SLEEF binary128) Householder and normal equations | same | same | QuadBLAS threads 1, 4, 10; contiguous operands | precision score 108.1 (Householder) and 109.7 (normal equations); 10.6 and 8.3 s, threads no faster | a quad configuration under 8 s | candidate: no error bound; outside the pinned venv |
| python-flint 0.9.0 `arb_mat` normal equations | same | same | precision 64, 128, 192, 256 bits; `flint.ctx.threads` 1, 4, 10 | 128 bits: precision score 120.7 with a rigorous radius, 2.6 s at one thread and 0.91 s at ten; 256 bits 1.2 s at ten | a certified solve faster than 0.91 s | current best: `tomography_prediction` certifies at 128 bits |
| Singular 4.4.1 `normal()` (normal.lib, default `equidim`), after `radical` as a primality check | OCI lab-a1 (2 ARM cores, 11.6 GiB), one process | normalization of the t7 = 1 chart of the strict transform of the E8-bar -> VB blowup at p = 32009 (8 variables, dp) | `Singular -q --no-rc`, `timeout 14400`, `/usr/bin/time -v`, no cap needed | 7,410 s CPU and 2 h 3 min wall in all, of which `normal()` 2,298 s; peak 5.2 GiB; one ring of 12 variables and 284 relations (`docs/evidence/a5-exceptional-fibers/working/build/arc/chart_t7.log`) | the `isPrim` run below returning the same ring sooner | superseded once the `isPrim` run matches: the primality check and the equidimensional decomposition are spent on an ideal already proved prime |
| Singular 4.4.1 `normal(S7, "isPrim")` | same | the same chart, primality taken from the run above, `norid`, `normap` and the ring written out | the same launch, no `radical` | running | a ring other than 12 variables and 284 relations | candidate |
| fiber-rank engine v11, quotient mode | Windows compute workstation (WSL, RTX 4090 Laptop) | E8-bar -> VB d = 4 at p = 32029, N = 12, 13, 14 | `--quotient --export-chunks 5 --dense-tables-gb 0`, no cap (workstation rule) | N = 13: 59.5 s, of which the Singular export 55.4 s, products 1.1 s, closure 2.7 s; r_13 = 155 | | current best; VB is export-bound, so engine v12 and the GPU leave it unchanged |
| GPU reduced row echelon form over F_p: the recursive PLUQ probe (INT8 four-GEMM Schur updates) plus a blocked back substitution through its exact product (a local probe; the code enters the repository with the engine v12 module and its FLINT tests) | Windows compute workstation, RTX 4090 Laptop 16 GiB under WSL; `gpuenv`: torch 2.14.1+cu130, CuPy 14.2.0, python-flint 0.9.0, numpy 2.5.4 | random low-rank matrices with a third of the columns zero, shaped like closure inserts: 300 x 700, 2,000 x 15,037 rank 1,800 and 4,000 x 20,000 rank 3,000 at p = 32009 and 32029; QRNG seed draw-2026-11-08T170257Z index 1001 | one process, no cap; the flint reference needs about 10 GB for its Python entry lists at 4,000 x 20,000 | rows and pivots equal to `flint.nmod_mat.rref()` on all six cases; 4,000 x 20,000: 3.5 s (p = 32009) and 2.1 s (p = 32029) against 69 s for flint; 2,000 x 15,037: 1.7 to 3.0 s against 21 to 24 s, first-call kernel compilation included | a case whose GPU rows or pivots differ from flint | candidate for the engine v12 echelon step; acceptance is the byte-equal W8 d = 4 rerun |

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
10. Checkpoints: the file each stage writes and its run-specific name.
11. End state: the verified copy, then deallocate or delete, and the backstop
    when no watcher is online.
12. The [run rulebook](run-rulebook.md) entry for a run over 30 minutes, a cloud
    VM, or any departure from these foundations.
