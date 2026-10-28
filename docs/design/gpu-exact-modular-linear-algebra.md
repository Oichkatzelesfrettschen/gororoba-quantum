# Exact F_p linear algebra on GPU tensor cores with an HMM memory hierarchy

## Purpose

The algebraic-geometry replays spend their time in two kinds of work: Gröbner bases, which Singular, msolve, giac
and Macaulay2 run on the CPU, and large exact linear algebra over a prime field `F_p`: ranks of normal-form
matrices for Nakayama counts, the degree pieces `I^d / m I^d` of a fiber cone, embedding matrices, and the
Macaulay-matrix reductions inside F4. The second kind is dense or blockwise-dense matrix arithmetic with exact
integer semantics. This design moves it onto the build host's RTX 4070 Ti through exact integer tensor-core
products, and lets operands exceed device memory by addressing ordinary host memory through Heterogeneous Memory
Management (HMM), including pages the kernel has swapped out.

## Measured host facts

All figures come from probes on the build host (RTX 4070 Ti, compute capability 8.9, NVIDIA open kernel module
615.78.08, CUDA 13.4, torch 2.14.1, CuPy 14.2.0) on 2026-10-27; cuBLAS dense GEMM at `n = 2048`, best of five.

| Number type | Throughput | Exact integer use |
| --- | --- | --- |
| FP64 | 0.47 TFLOP/s | exact while `k * p^2 < 2^53` |
| FP32 | 26.3 TFLOP/s | exact while sums stay below `2^24` |
| TF32 tensor | 33.3 TFLOP/s | 10-bit mantissa; no use |
| FP16 / BF16 tensor | 68.6 / 71.5 TFLOP/s | 11- and 8-bit significands; no use beyond small digits |
| INT8 to INT32 tensor | 62.8 to 68.6 TOP/s | exact by construction; bit-identical to an int64 reference |
| FP8 E4M3 tensor | 98.7 TFLOP/s | exact on digits in `[-8, 8]` with FP32 accumulation |

- `nvidia-smi -q` reports `Addressing Mode: HMM` and a 16 GiB BAR1 (Resizable BAR on). CUDA device attributes:
  `cudaDevAttrPageableMemoryAccess = 1`, `cudaDevAttrConcurrentManagedAccess = 1`,
  `cudaDevAttrPageableMemoryAccessUsesHostPageTables = 0`. So the GPU dereferences `malloc` memory through page
  migration, not shared page tables (ATS).
- cuBLAS ran an `n = 4096` FP32 GEMM directly on two numpy buffers wrapped as device pointers, with no copy, at
  0.24 TFLOP/s cold and 0.57 TFLOP/s warm, results matching a device copy; after `cudaMemAdvise(ReadMostly)` and
  `cudaMemPrefetchAsync` through CuPy the same GEMM ran at 0.28 TFLOP/s. Warm HMM access therefore runs about 45x
  below device-resident FP32, and the prefetch as issued did not help: either the pages are read across PCIe
  without migrating, or CuPy calls the pre-CUDA-13 `cudaMemPrefetchAsync` signature and migrates nothing.
- `cudaMallocManaged` oversubscription worked (1.69 GiB of operands on 599 MiB free) but ran at 0.09 TFLOP/s: a
  GEMM's access order migrates pages back and forth across PCIe.
- The exact INT8 modular product (below) ran 34x and 51x faster than FLINT `nmod_mat` multiplication at
  `n = 1024` and `2048`, exact against FLINT on every sampled row.
- An out-of-core version with operands in pinned host memory, int16 transfers, int32 device arithmetic and a
  second copy stream computed `n = 16384` in 14.1 s through 89 MiB of free device memory, exact on 1024 sampled
  entries.
- With pageable operands and two pinned staging buffers, the same product took 27.6 s at `n = 16384` (tile 8192)
  and 145.6 s at `n = 32768` (8 GiB of host operands), exact on sampled entries: the single-threaded pageable to
  pinned host copy halves throughput against fully pinned operands.

## Layer 1: the exact modular product

`C = A B mod p` for `p < 2^15`. Each residue `a` in `[0, p)` becomes signed base-256 digits `a = 256 a1 + a0` with
`a0` in `[-128, 127]` and `a1` in `[-64, 64]`, stored as int8. The product is four INT8 GEMMs with INT32
accumulation, `A1 B1`, `A0 B1 + A1 B0`, `A0 B0`, recombined with weights `2^16 mod p` and `256`. Digit products
are at most `2^14` in magnitude, so an inner dimension `k <= 32768` keeps every GEMM entry within `2^29` and the
two-term cross sum within `2^30`; each partial reduces mod `p` before scaling by a weight below `p`, so every
device value stays inside int32. Device arithmetic never touches int64, which the GPU emulates.

Wider primes extend the digit count: `p < 2^23` takes three digits and nine GEMMs; `p < 2^31` takes four digits and
sixteen. The alternative for wide primes is the residue-number-system route of Ozaki Scheme II: products modulo
several word-size primes, each one INT8 GEMM, recombined by the Chinese remainder theorem.

An FP8 backend uses base-16 digits in `[-8, 8]`, which E4M3 holds exactly; four digits cover `p < 2^15` at sixteen
GEMMs. On this card it computes about 6 effective TOP/s against about 16 for INT8, so INT8 is the default. FP8 is
kept because Blackwell-generation parts deprioritize INT8. A one-time timed product selects the backend.

## Layer 2: the memory hierarchy

The operands live in ordinary pageable host memory (numpy arrays from `malloc`), which the kernel may swap. Under
HMM the device addresses those pages directly, so no staging copy exists in the program; the driver migrates pages
on first touch and on prefetch.

- **Tiled layout.** Matrices are stored as contiguous square tiles (default 4096 x 4096 int16, 32 MiB), tile-major,
  so each tile is one address range. A row-major matrix would turn a tile into thousands of separate row segments,
  one prefetch each.
- **Advice.** `cudaMemAdvise(ReadMostly)` on the input tiles lets the driver keep read-only copies on both sides;
  `cudaMemAdvise(PreferredLocation = device)` on the accumulator tile pins its pages to VRAM while it is live.
- **Prefetch pipeline.** Before tile `t` runs, `cudaMemPrefetchAsync` on a dedicated stream moves tile `t+1`'s
  operand ranges to the device; an event orders the compute stream after it. Finished output tiles prefetch back to
  the host, which frees VRAM for the next tiles without an explicit eviction pass.
- **Swap tier.** A tile whose pages sit in swap faults in through the kernel when the prefetch touches it. The
  pipeline reads swap at NVMe speed, a few GB/s, so a run spanning swap is bound by disk, not by tensor throughput;
  the design keeps working, only slower.
- **Fallback.** When HMM is absent (`cudaDevAttrPageableMemoryAccess = 0`), the same pipeline uses two pinned staging
  buffers per operand: a host-side copy from pageable memory into a pinned buffer, then an asynchronous device copy
  that overlaps the previous tile's GEMMs. That path already runs (`n = 16384` above) and reaches swap through its
  pageable operands as well.

## Layer 3: elimination

Rank, echelon form and the PLUQ factorization follow the recursive scheme of FFLAS-FFPACK. Split the columns in
half; factor the left half recursively; apply the row permutation to the right half; solve the triangular system for
the top right block by recursive modular TRSM, which again reduces to modular GEMM; update the bottom right block
with one modular GEMM (the Schur complement); recurse on it. Almost every operation becomes a Layer 1 product. The
base case (blocks of 64 to 256 columns) runs as one fused CUDA kernel (CuPy `RawKernel`) that performs the pivot
search and row operations mod `p` in int32 on the device, with no per-column round trip to Python. A first
prototype that looped over columns in Python lost to FLINT (8.27 s against 0.35 s at `n = 1024`); the same blocked
algorithm with FP64 trailing updates already tied FLINT at `n = 4096` (10.3 s against 9.9 s), and the INT8 product
replaces that FP64 update at 146 times the FP64 rate.

## Layer 4: where it enters the replays

- Nakayama counts: the rank of normal forms modulo `std(J + m I)` across the selected Schur coordinates.
- Fiber cones: the rank of each degree piece `I^d / m I^d` as a Macaulay-style matrix over the monomials of the
  germ ring, the route that ran out of 8 GiB at degree 3 on the CPU for `E8bar` to `VB`.
- F4-style reduction of Macaulay matrices in a Gröbner computation, where the matrices are sparse with dense blocks.
- Embedding matrices and Freivalds checks of any product the replays rely on.

## Verification

- **Products.** Freivalds' check, `A (B x) = C x mod p` for random `x`, costs two matrix-vector products and fails
  with probability at most `1/p` per vector for a wrong `C`; every product the replays retain passes it with several
  vectors, and sampled entries match an int64 reference exactly.
- **Factorizations.** `P L U Q = A` passes the same check; ranks below a few thousand also match FLINT `nmod_mat`.
- **Backends.** INT8, FP8 and the FP64 route must agree bit for bit on the same inputs.
- **Falsifiers.** A Freivalds failure; a disagreement between backends; an HMM pipeline slower than the staging
  fallback at every size, which would retire the HMM path; a measured swap-tier throughput far below NVMe read
  speed, which would locate a defect in the prefetch pipeline.

## Monitoring

Long runs use the monitored runner (verbose progress log, 10 s memory and CPU samples, a host `MemAvailable`
floor). Device-side views: `nvidia-smi -q -d MEMORY` (framebuffer and BAR1), `nvidia-smi dmon -s mu` (per-second
memory and utilization), and Nsight Systems 2026.3 with `--cuda-um-gpu-page-faults=true
--cuda-um-cpu-page-faults=true`, which places every HMM fault and migration on the timeline beside the GEMM
kernels. Nsight Compute 2026.3 profiles the base-case elimination kernel.

## Delivery

The code starts as a Python package (`numpy`, `torch` for `_int_mm` and `_scaled_mm`, `cupy` for `RawKernel`,
prefetch and advise) under `~/Github`, with a test suite against FLINT and the measurement probes above. The
replays import it as a pinned dependency. Publishing to PyPI waits for the owner's decision on name, license and
contents. A Rust port fits `open_gororoba`, which already depends on `cudarc` 0.19 (cuBLAS, cuSOLVER, NVRTC).

## Order

1. Establish that HMM pages migrate: issue `cudaMemPrefetchAsync` through the CUDA 13 signature (location struct
   and flags, via `cuda-python` bindings rather than CuPy's wrapper), trace one GEMM under Nsight Systems with
   page-fault and migration tracing, and require warm HMM GEMM throughput within 2x of device-resident. If the
   migrations do not occur, the HMM path stays a fallback and the staging path (with a multithreaded host copy)
   carries Layer 2.
2. Layer 2 with the tiled layout and the prefetch pipeline, measured against staging; Nsight Systems confirms the
   prefetches remove demand faults.
3. Layer 3: fused base-case kernel, then recursive PLUQ; rank against FLINT up to `n = 8192`.
4. Layer 4: the fiber-cone degree ranks for `E8bar` to `VB`.
5. Package, tests, the owner's PyPI decision.
