# Memory-bounded A5 fiber-rank route

This directory separates mathematical size from representation size. The retained W8 degree-6, N = 19 v11
preflight is a correct forecast for that engine's simultaneous float64 arrays, but it is not a lower bound on memory
for the rank problem. Engine v14 instead uses exact uint16 residues, streams generator operators by total degree,
stores only nonpivot echelon coefficients and materializes closure rows one chunk at a time.

## Run configuration and tool versions

The acceptance run used `GOROROBA_WORKERS=4`, `OPENBLAS_NUM_THREADS=4` and `OMP_NUM_THREADS=1`: independent
sign-mask checks use the repository process pool, tiled dense products use four BLAS threads, and nested OpenMP does
not oversubscribe them. The active exact stack is Python 3.14.7, NumPy 2.5.4, SciPy 1.18.1, python-flint 0.9.0,
SymPy 1.14.0, Singular 4.4.1 and msolve 0.10.1. `msolve -t 4` is the bounded setting for a separate msolve process.

Julia/Groebner.jl and LinBox are not runtime dependencies of v14 and were not installed for it. They are candidate
successor backends, not prerequisites hidden from this replay.

## W8 N = 16 acceptance

[`w8-n16-acceptance.json`](w8-n16-acceptance.json) summarizes one run of W8 -> N- at degree 5, N = 16, p = 32009.
The summary agrees with the retained v11 receipt run: `r_16 = 4116`; block contributions 1,017 / 1,005 / 1,047 /
1,047; closure ranks 15,364 / 15,264 / 15,315 / 15,315; all 265 nonstandard controls add zero rank. V14 reports four
frontier rounds rather than v11's five because rows are materialized lazily after intervening RREF updates; the fixed
closure space and every final block rank agree.

Provenance of the summary:

- The run executed `fiber_rank_v14.py` as committed in `f8092f967` (sha256 `0c006242b544c0cb...`, the record's
  `engine_sha256`). The engine at `a84b82772` has another digest. `git diff f8092f967 a84b82772` of the engine shows
  line wrapping, two stderr progress prints (`products built`, `closure round`), the `preflight_stages` output
  field, the function `compact_stage_peaks` and an admission rule that tests the larger of the products and closure
  stages where `f8092f967` tested their sum; the same diff of `gororoba_quantum/modular_echelon.py` shows line
  wrapping and one docstring word. No line of the rank arithmetic differs between those two commits. A later change
  adds the `PMAX` prime guards and the `inner_tile` parameter of `tiled_mod_product`, whose default, 4,096, equals the
  literal the run used; p = 32009 never reaches a guard.
- The run used the cached uint16 operator (`product_operator: uint16-cached`, `operator_cache_gib: 6`). The streamed
  route without the cache, on which the N = 19 model below rests, was not exercised at this size; the unit tests and
  the smaller cells compare it with the dense operator.
- The engine's stdout record, its stderr and the resource file of that run are not retained in the tree, so no file
  here reproduces the summary's numbers except by rerunning the cell. A rerun at the branch head through
  [`rank_cell.py`](../replay/engine/rank_cell.py) would retain all three and takes about 100 minutes on four workers;
  it has not been performed.
- The fields `swap_bytes` and `oom_kills` were removed from the summary: no producer wrote them.

| Quantity | retained v11 | v14 compact |
| --- | ---: | ---: |
| wall | 7,841.2 s (two workers on a cloud VM, beside a second job) | 5,993.6 s (four workers, another machine) |
| products | 2,201.4 s | 1,239.2 s |
| closure | 4,751.3 s | 4,515.6 s |
| peak memory | 24.9 GiB (largest single-process RSS, GNU `time`) | 4.98 GiB (RSS summed over the process group) |
| preflight selected arrays | 58.9 GiB | 5.69 GiB (sum of every selected-array term) |

The memory rows are two statistics: a single-process maximum and a process-group sum that counts pages shared by
forked workers once per process, so the ratio 0.200 errs against v14. The wall rows come from two machines with
different worker counts, and v11 shared its VM with a second job, so the ratio 0.764 carries no hardware-neutral
meaning. On this cell the measured v14 peak lies below the v11 peak; the equality of ranks is a finite-field result
and does not transfer to characteristic zero.

## Exactness invariants

- The prime is an odd prime below 2^15 (`PMAX` in `modular_echelon.py`). The engine refuses a larger prime when
  `--stream-products` or `--echelon compact|gpu` is set, and `Echelon("compact")` refuses it at construction. The uint16
  residues alone admit p <= 2^16 and the 4,096-term float64 tiles admit p <= 1,482,911; the shared bound is the one the
  device backend already needs.
- Products upcast only a bounded inner tile to float64. `tiled_mod_product` and the compact echelon check
  `tile * (p - 1)^2 < 2^53` before each product, reduce modulo p after every tile and refuse a product outside that
  bound.
- A compact echelon row has an implicit unit pivot. Only its nonpivot coefficients are stored, in 1,024-column
  uint16 panels. Insertion takes an exact FLINT RREF on the free columns and clears each panel modulo p.
- The standard-monomial receipt restricts the product rows. Its nonstandard controls must add zero rank.
- The cell runner binds the engine and header hashes, field, degree and truncation order, and through its resource
  record the canonical engine arguments. It publishes JSON by flush and atomic rename only after engine exit 0 and
  record validation, and it terminates the engine's process group on SIGTERM, SIGINT or `--timeout`.

Small exact tests compare streamed and cached uint16 operators with engine v13's dense operator on a two-block
fixture with a nonzero variable character, compare v14's closure with v13's on a four-round, four-block cell, and
compare the compact echelon with FLINT `nmod_mat.rref` across a reduced tile width and panel width. The two older
insertion tests (`test_echelon_compact_equals_flint_insertion_sequence` and
`test_echelon_compact_crosses_storage_panels`) use seeded `numpy` generators on registered test seeds, and one audit
test crosses the default 4,096-term tile.

## N = 19 selected-array bound

[`w8_n19_memory_model.py`](w8_n19_memory_model.py) regenerates
[`w8-n19-memory-model.json`](w8-n19-memory-model.json) from the retained v11 terms and quotient degree counts. The
block-size bound does not assume equal character blocks: from D = sum c_b and Q = sum c_b^2, Cauchy gives
`max c_b <= ceil(D/4 + sqrt(3 (Q - D^2/4) / 4)) = 59,123`.
The model's target memory limit is 16 GiB, the `memory_limit` of the script.

| Representation or stage | Selected arrays |
| --- | ---: |
| v11 float64 generator blocks | 103.34 GiB |
| one full uint16 generator operator | 25.84 GiB (does not fit) |
| two adjacent streamed operator layers | at most 8.664 GiB |
| v14 products stage (layers plus retained uint16 rows) | at most 12.146 GiB |
| v14 closure stage (compact basis, rows and chunk temporaries) | at most 10.025 GiB |
| selected-array headroom inside 16 GiB | at least 3.854 GiB |

The last three bounds are stage-local. Summing the operator and echelon terms would count arrays that are never live
together. Conversely, the 3.854 GiB is not guaranteed RSS headroom: sparse tables, Python objects and allocator state
are outside the model. An instrumented process-group peak at or above 16 GiB falsifies the 16 GiB route.
The model is arithmetic on named arrays under the Cauchy block-size bound; it is neither a measurement nor a proof that
an N = 19 run fits.

## Current algorithmic options

The sources below are cited by identifier or address. None is registered in `docs/SOURCES.json` (msolve appears only
in repository notes) and the descriptions were not verified against the texts: cited by identifier; not registered,
descriptions unverified.

- [Groebner.jl's interface](https://sumiya11.github.io/Groebner.jl/interface/) exposes learn/apply tracing across
  coefficient specializations. The 2026 paper [*Groebner.jl: Fast Groebner Tracing in
  Julia*](https://arxiv.org/abs/2607.06372) records zero reductions once and applies the trace in batches, including
  SIMD tuples of modular coefficients. This is relevant when the same leading structure is evaluated at many good
  primes; an exact characteristic-zero verification is still required after reconstruction.
- [Massively Parallel Modular Methods](https://arxiv.org/abs/2401.11606) uses independent modular images,
  stabilization and error-tolerant rational reconstruction. For these fibers the independent jobs can be scheduled
  one prime at a time under a 16 GiB cap. Modular agreement alone does not prove a Q(i) presentation: reconstruct
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
