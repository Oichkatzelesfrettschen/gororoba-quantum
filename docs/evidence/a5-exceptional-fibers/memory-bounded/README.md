# Memory-bounded A5 fiber-rank route

This directory separates mathematical size from representation size. The retained W8 degree-6, N = 19 v11
preflight is a correct forecast for that engine's simultaneous float64 arrays, but it is not a lower bound on memory
for the rank problem. Engine v14 instead uses exact uint16 residues, streams generator operators by total degree,
stores only nonpivot echelon coefficients and materializes closure rows one chunk at a time.

## Host and tool contract (2026-11-11)

The managed host exposes five CPUs but `cpu.max = 400000 100000`, hence a four-core quota; the memory cgroup is
16 GiB with no swap. The run uses `GOROROBA_WORKERS=4`, `OPENBLAS_NUM_THREADS=4` and `OMP_NUM_THREADS=1`: independent
sign-mask checks use the repository process pool, tiled dense products use four BLAS threads, and nested OpenMP does
not oversubscribe them. The active exact stack is Python 3.14.7, NumPy 2.5.4, SciPy 1.18.1, python-flint 0.9.0,
SymPy 1.14.0, Singular 4.4.1 and msolve 0.10.1. `msolve -t 4` is the bounded setting for a separate msolve process.

Julia/Groebner.jl and LinBox are not runtime dependencies of v14 and were not installed into the remaining 1.9 GiB
workspace. They are candidate successor backends, not prerequisites hidden from this replay.

## W8 N = 16 acceptance

[`w8-n16-acceptance.json`](w8-n16-acceptance.json) retains the hash-bound result and process-group measurement. The
exact result agrees with the retained v11 receipt run: `r_16 = 4116`; block contributions 1,017 / 1,005 / 1,047 /
1,047; closure ranks 15,364 / 15,264 / 15,315 / 15,315; all 265 nonstandard controls add zero rank. V14 reports four
frontier rounds rather than v11's five because rows are materialized lazily after intervening RREF updates; the fixed
closure space and every final block rank agree.

| Quantity | retained v11 | v14 compact |
| --- | ---: | ---: |
| wall | 7,841.2 s | 5,993.6 s |
| products | 2,201.4 s | 1,239.2 s |
| closure | 4,751.3 s | 4,515.6 s |
| peak RSS | 24.9 GiB | 4.98 GiB process group |
| preflight selected arrays | 58.9 GiB | 5.69 GiB (conservative cross-stage sum) |

Thus the old RAM requirement is falsified for the same algebraic cell: v14 uses 20.0% of v11's measured memory and
76.4% of its wall time. This does not turn a finite-field equality into a characteristic-zero theorem.

## Exactness invariants

- The prime is below 2^15, so every residue fits uint16.
- Products upcast only a bounded inner tile to float64. The code checks `inner * (p - 1)^2 < 2^53`, reduces modulo p
  after every tile and refuses a product outside that bound.
- A compact echelon row has an implicit unit pivot. Only its nonpivot coefficients are stored, in 1,024-column
  uint16 panels. Insertion takes an exact FLINT RREF on the free columns and clears each panel modulo p.
- The standard-monomial receipt restricts the product rows. Its nonstandard controls must add zero rank.
- The cell runner binds the engine and header hashes, field, degree and truncation order; it publishes JSON by atomic
  rename only after engine exit 0 and record validation.

Small exact tests compare streamed and cached uint16 operators with the retained dense operator, including a
restricted receipt-style prefix set. Compact echelon insertion/reduction is compared with FLINT across repeated
random insertions and across the 1,024-column panel boundary.

## N = 19 selected-array bound

[`w8_n19_memory_model.py`](w8_n19_memory_model.py) regenerates
[`w8-n19-memory-model.json`](w8-n19-memory-model.json) from the retained v11 terms and quotient degree counts. The
block-size bound does not assume equal character blocks: from D = sum c_b and Q = sum c_b^2, Cauchy gives
`max c_b <= ceil(D/4 + sqrt(3 (Q - D^2/4) / 4)) = 59,123`.

| Representation or stage | Selected arrays |
| --- | ---: |
| v11 float64 generator blocks | 103.35 GiB |
| one full uint16 generator operator | 25.84 GiB (does not fit) |
| two adjacent streamed operator layers | at most 8.664 GiB |
| v14 products stage (layers plus retained uint16 rows) | at most 12.146 GiB |
| v14 closure stage (compact basis, rows and chunk temporaries) | at most 10.025 GiB |
| selected-array headroom inside 16 GiB | at least 3.854 GiB |

The last three bounds are stage-local. Summing the operator and echelon terms would count arrays that are never live
together. Conversely, the 3.854 GiB is not guaranteed RSS headroom: sparse tables, Python objects and allocator state
are outside the model. An instrumented process-group peak at or above 16 GiB falsifies this host route.

## Current algorithmic options

- [Groebner.jl's interface](https://sumiya11.github.io/Groebner.jl/interface/) exposes learn/apply tracing across
  coefficient specializations. The 2026 paper [*Groebner.jl: Fast Groebner Tracing in
  Julia*](https://arxiv.org/abs/2607.06372) records zero reductions once and applies the trace in batches, including
  SIMD tuples of modular coefficients. This is relevant when the same leading structure is evaluated at many good
  primes; an exact characteristic-zero verification is still required after reconstruction.
- [Massively Parallel Modular Methods](https://arxiv.org/abs/2401.11606) uses independent modular images,
  stabilization and error-tolerant rational reconstruction. For these fibers the independent jobs can be scheduled
  one prime at a time under the 16 GiB cap. Modular agreement alone does not prove a Q(i) presentation: reconstruct
  the coefficients and verify both ideal memberships or retained exact cofactor identities.
- [Parallelization of Modular Algorithms](https://arxiv.org/abs/1005.5663) gives the modular Singular pattern:
  compute at several primes, combine by CRT/rational reconstruction, then verify over the original coefficient field.
- [LinBox](https://linalg.org/linbox/linbox/) provides sparse black-box Wiedemann/Lanczos linear algebra. It can
  replace dense residency when the action remains sparse, but a rank used in the characteristic-zero transfer still
  needs a checkable upper and lower certificate (for example verified nullspace plus an independent nonzero minor),
  not just a probable modular rank.
- [msolve](https://msolve.lip6.fr/) supplies multithreaded F4-style prime-field and rational computations. Its
  `-m` pair cap and exact sparse linear algebra variants are useful bounded alternatives; the repository's exact
  coordinate order, field model and reverse-membership witnesses remain part of the certificate.

The W8 degree-6 rank itself is a diagnostic, not a missing theorem: A5-066 already gives the all-degree presentation,
and A5-291 rejected the old 129--223 GiB v11 rerun as mathematically redundant. The memory-bounded route remains useful
for falsifying the engine forecast and for unresolved E8 closure cells.
