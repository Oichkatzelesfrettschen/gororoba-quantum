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

At full fan-out the reachable pool is the build host plus five Kaggle CPU sessions and two Kaggle GPU sessions:
62 + 5 x 30 + 2 x 29 = 270 GB of RAM in eight separate machines, and 12 + 4 x 15 = 72 GiB of VRAM on five GPUs. The
largest single address space reachable without a spend case is the build host's 62 GiB plus swap; with a case it is
the Azure VM's 84 GB; a TPU VM's host RAM is larger once a queued session starts.

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
take 16-bit storage, so a prime near 32009 halves the matrix memory of a 31-bit prime. Each elimination therefore
goes to the largest single machine free: a Kaggle CPU session (30 GB) first, the Azure VM (84 GB) through a case
when 30 GB is exhausted.
