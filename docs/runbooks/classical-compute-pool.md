# Classical compute pool

The repository's exact algebra (Singular, msolve) and exact linear algebra (FLINT, the GPU modular product) run on
the build host and, when a job outgrows it, on the free classical capacity the project's accounts hold. This page
lists that capacity with its source, decomposes what "pooling" can and cannot buy, names how each tool installs on
each substrate, and records the memory the A_5 Rees eliminations measured. Offloading a classical job is a standing
owner authorization; spending trial credit (an Azure VM) is a written case with expected hours and a deallocation
step, like any spend ([provider-credits.md](provider-credits.md)).

## Capacity

| Substrate | CPU | RAM | GPU / VRAM | Per-run limit | Concurrency | Cost | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Build host | Ryzen 5 5600X3D, 12 threads | 62 GiB, 63 GiB swap | RTX 4070 Ti, 12 GiB | none | shared with every local session | none | measured ([substrates.md](../notes/kaggle/substrates.md)) |
| Kaggle CPU session | 4 cores (Xeon 2.20 GHz, no AVX-512) | 30 GB | none | 12 h | 5 batch sessions per account | unmetered | measured ([workflow.md](../notes/kaggle/workflow.md), [substrates.md](../notes/kaggle/substrates.md)) |
| Kaggle GPU session | 4 cores | 29 GB | 2 x T4, 15 GiB each | 12 h | 2 batch sessions per account | 30 GPU-hours a week | measured |
| Kaggle TPU VM | 96 cores (v3-8, documented) | 330 GB (v3-8, documented); the v5e-8 host is unmeasured | TPU only | 9 h | one | 20 TPU-hours a week | the account is identity-verified, but v5e-8 batch sessions queue for hours (one read `QUEUED` 7 h 08 min after its push) and none has started yet; queued time draws no quota ([tpu-research.md](../notes/kaggle/tpu-research.md)) |
| GitHub Actions, public repository | 4 vCPU | 16 GB | none | 6 h per job | matrix fan-out | free | documented (GitHub hosted-runner reference); allowed offload, logs are public |
| Azure trial, `Standard_FX4mds_v2` | 4 vCPU | 84 GB | none | until deallocated | one (4-vCPU regional cap) | trial credit by the hour | quota read ([azure/README.md](../notes/azure/README.md)); GPU families have quota 0 |
| AWS free plan | - | - | - | - | - | credits | `ec2:RunInstances` is denied by the project's policy ([aws/README.md](../notes/aws/README.md)) |
| qBraid Lab, included server (Free plan) | 1.8 vCPU limit | 4 GB | none | 100 CPU-hours a month | one subscription server | included | `GET /compute-sessions/usage`, `GET /compute/profiles` ([qbraid/README.md](../notes/qbraid/README.md)); the 25 GB `8vCPU_25GB` server is tagged Pro (100 USD a month) |
| qBraid on-demand instances | 4 to 96 vCPU | 6 to 384 GB | GPU profiles exist | until stopped | per instance | 15 to 576 credits an hour (100 credits = 1 USD) | the wallet holds 0 credits with auto-recharge off, so none can start without a purchase |

At full fan-out the reachable pool is the build host plus five Kaggle CPU sessions and two Kaggle GPU sessions:
62 + 5 x 30 + 2 x 29 = 270 GB of RAM in eight separate machines, and 12 + 4 x 15 = 72 GiB of VRAM on five GPUs. The
largest single address space reachable without a spend case is the build host's 62 GiB plus swap; with a case it is
the Azure VM's 84 GB; a TPU VM's host RAM is larger once a queued session starts.

## Access audit

Read 2026-10-28 between 19:30 and 20:10 UTC with each service's own read-only call.

| Service | State at the read | What it allows now |
| --- | --- | --- |
| Kaggle | GPU 0.07 of 30 h and TPU 0 of 20 h used, both reset 2026-10-31T00:00Z; AI models 1.48 of 10 USD daily (refill 2026-10-29T18:25Z) and of 100 USD monthly | five CPU and two GPU batch sessions; one TPU batch session, queued; Model Proxy tasks on the full catalog |
| GitHub Actions | the repository is public | standard hosted runners at no cost; logs and artifacts are public |
| Azure | subscription Enabled; eastus total regional vCPU 0 of 4 used, `StandardFXmdsv2Family` 0 of 4, low-priority 0 of 3 | one 4-vCPU VM, the 84 GB `Standard_FX4mds_v2` the largest, after a spend case |
| AWS | `aws sts get-caller-identity` fails: the browser session expired | nothing until `aws login --profile gororoba`; instance launch stays denied by policy |
| qBraid | tier Free; 0 credits, auto-recharge off; Lab CPU 0 of 100 h (renews 2026-11-10); server stopped; AI 0 of 5 USD (resets 2026-11-18, all models) | the 4 GB included server, started from the Lab web page (the read routes include no start call), and the 5 USD AI allowance |

## What pooling buys

Pooling decomposes into four levels, and only the first three work across these machines:

1. **Job-level.** Independent computations run on separate machines at once: each Rees elimination of a different
   incidence, each source orbit. Every machine must hold its own job's working set. This is the main lever.
2. **Field-level.** The same computation at different split primes, or under the two square roots of -1 modulo one
   prime, runs on separate machines; the results combine by comparison or by Chinese remaindering.
3. **Block-level linear algebra.** Degree pieces of a fiber cone, or row blocks of a Macaulay matrix, are independent
   rank problems; each goes to its own GPU (the T4s, the 4070 Ti) through the exact INT8 product
   (the GPU exact modular linear algebra design on branch `tools/gpu-modular-linalg`).
4. **One address space across machines.** It does not work here. An F4 or Buchberger run touches its matrix and pair
   set at random; network-backed memory (swap over NBD or iSCSI, distributed shared memory) serves pages at about
   0.1 to 1 GB/s against roughly 50 GB/s of local DRAM, a 50- to 500-fold slowdown, and Kaggle sessions accept no
   inbound connection to export a block device. A job larger than one machine needs a larger machine, a smaller
   formulation, or a block decomposition of level 3.

## Installing the tools on each substrate

| Tool | Build host | Kaggle, GitHub Actions, Azure VM |
| --- | --- | --- |
| msolve | Arch package (0.11.0) | `pip install passagemath-msolve==10.8.13`; the wheel ships a standalone `sage_wheels/bin/msolve` (0.10.1) with FLINT, GMP, MPFR and libgomp bundled, run directly |
| Singular | Arch package (4.4.1) | `pip install passagemath-singular`, or `conda-forge::singular` (4.4.1) through micromamba |
| FLINT | Arch package; python-flint 0.9.0 | `pip install python-flint` |
| GPU product and PLUQ | CUDA 13, torch, CuPy | Kaggle T4: torch and CuPy preinstalled; `torch._int_mm` needs `M` a multiple of 32 and `K`, `N` multiples of 16 |

A Kaggle kernel needs internet enabled for the pip install. msolve takes one input file (variable line,
characteristic line, comma-separated polynomials) and `-e 1 -g 2` returns the reduced basis of the ordering that
eliminates the first variable.

## Measured memory of the A_5 Rees eliminations

| Elimination | Solver | Result |
| --- | --- | --- |
| E8-bar to `VB`, 27 generators in 19 variables | Singular, `F_{32003^2}` | exhausted 24 GiB after 4 h 45 min |
| E8-bar to `VB` | Singular, split prime 32009, homogenized | under 4 GiB, degree 16 after 3.5 h, pair queue flat near 55,000 |
| E8-bar to `VB` | msolve 0.11, prime 1073741789, 8 threads | exhausted 24 GiB after 25 min |
| Iso to `N+`, 18 generators in 24 variables | Singular, split prime, `dp` or direct `eliminate` | no basis in 20 min at 6 GiB |
| Iso to `N+` | msolve 0.11, prime 32009, 4 threads | degree 8 reached in 3 min; matrix allocation exceeded the 12 GiB cap |

msolve reaches in minutes the degrees Singular reaches in hours, and its limit is memory. Coefficients below 2^16
take 16-bit storage, so a prime near 32009 halves the matrix memory of a 30-bit prime such as 1073741789. Each elimination therefore
goes to the largest single machine free: a Kaggle CPU session (30 GB) first, the Azure VM (84 GB) through a case
when 30 GB is exhausted.

## Sample optimizations (measured here; yours may vary)

Each sample below carries the date and the conditions it was measured under, because Kaggle images, queues and quotas
change without notice.

**Where to run what.**

- A Kaggle CPU session has 30 GB, 4 cores and a 12 h limit, so one elimination fits one session, and five sessions
  run at once per account (2026-10-28, Kaggle CPU batch session)
- A Kaggle GPU session's host is also a 29 GB, 4-core machine, so a CPU elimination runs there when the weekly GPU hours
  (30 h, reset Saturday 00:00 UTC) would otherwise expire unused (2026-10-28, Kaggle GPU batch session)
- The Azure trial VM (`Standard_FX4mds_v2`, 84 GB) is the next step up and needs a written spend case with expected
  hours and a deallocation step (2026-10-28, Azure trial account)

**msolve.**

- A prime below 2^16 (32009 here) stores coefficients in 16 bits, about half the matrix memory of a prime above 2^16
  such as 1073741789, which lies below 2^30 (2026-10-28, msolve)
- The [install table](#installing-the-tools-on-each-substrate) lists the passagemath-msolve 10.8.13 wheel; it ships a
  standalone msolve 0.10.1 binary at `sage_wheels/bin/msolve` with FLINT, GMP, MPFR and libgomp bundled, and it runs on
  any host where pip installs it (2026-10-28, passagemath-msolve 10.8.13 wheel)
- The Kaggle kernel used for these runs embeds the input file, installs the wheel, runs `msolve -e 1 -g 2` with `-t` set
  to every core, logs `MemAvailable` and the solver's resident set every 30 s, and writes the gzipped basis and a
  `result.json` (2026-10-28, Kaggle CPU batch session)
- msolve on the Iso Rees graph ideal (18 generators, 24 variables) reached degree 8 in 3 minutes before a 12 GiB cap,
  while Singular had not finished the same ideal in 20 minutes; the
  [measured-memory table](#measured-memory-of-the-a_5-rees-eliminations) records the same numbers (2026-10-28, msolve
  and Singular)

**Singular pitfalls (Singular 4.4.1).**

- Over an algebraic extension such as `(32003,I)` with `minpoly = I^2+1`, `eliminate` skips its Hilbert-driven path and
  runs a plain sugar-strategy `std`; use a split prime `p = 1 mod 4` with `i` as a field element, for example 32009 with
  `i = 10754`, whose square is -1 modulo 32009 (2026-10-28, Singular 4.4.1)
- An explicit `homog(...)` before `eliminate` also skips the Hilbert step (2026-10-28, Singular 4.4.1)
- `std(Graph)` before `eliminate` was the bottleneck of the Rees fiber scripts: a 3-generator graph ideal in 11
  variables did not finish `std(Graph)` in 15 minutes (2026-10-28, Singular 4.4.1)
- Selecting Nakayama-lemma generators (minimal generators chosen in `I/(mI+J)`, a vector space over `R/m`) by the prefix
  rank of the normal-form coefficient matrix replaces a `std` per candidate and gives the same selection; one phase went
  from a 300 s timeout to 14 s (2026-10-28, Singular 4.4.1)
- `ord` is a reserved name and cannot name a variable (2026-10-28, Singular 4.4.1)
- Singular string literals do not interpret `\n`; put a literal newline inside the string (2026-10-28, Singular 4.4.1)

**Kaggle Model Proxy (AI inference).**

The daily and monthly quota reader is in [provider-credits.md](provider-credits.md).

- `kaggle benchmarks auth` mints a local token that lasts about 2 h and is limited to the 8 models in `LLMS_AVAILABLE`;
  the full catalog (Claude Opus 5.5, GPT-6 Sol and Astra, Gemini 4 Argon and others) runs only through
  `kaggle benchmarks tasks push` and `kaggle benchmarks tasks run -m MODEL` (2026-10-28, Kaggle CLI)
- Set an output-token cap on each prompt, because the proxy reserves the worst-case cost from the default cap up front:
  a GPT-6 Astra run failed with a 403 when that reservation (6.41 USD) exceeded the remaining quota
  (2026-10-28, Kaggle Model Proxy)
- The daily 10 USD allowance refills on a rolling 24 h clock from first use and the monthly 100 USD on a rolling month,
  so an unspent day is lost (2026-10-28, Kaggle Model Proxy)
- `grok-4.6` is listed by `kaggle benchmarks tasks models`, but the proxy answers 404 for it (2026-10-28, Kaggle Model
  Proxy)
- `kaggle benchmarks tasks download TASK` fetches every model's run JSON, which holds the response
  (2026-10-28, Kaggle CLI)
- One six-model question of about 1,000 input words cost 1.48 USD (2026-10-28, Kaggle Model Proxy)

**Storage.**

- The API reports usage (the sum of `totalBytes` over the account's datasets and models), but no call reports the
  214.75 GB private dataset and model caps, which come only from the account settings page; the
  [Kaggle guide](../notes/kaggle/README.md) records them as read from that page
  (2026-10-28, Kaggle API and settings page)
