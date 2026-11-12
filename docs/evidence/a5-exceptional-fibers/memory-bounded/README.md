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
  literal the run used; p = 32009 never reaches a guard. The compact echelon of those commits sat in
  `gororoba_quantum/modular_echelon.py`; the head holds it in `gororoba_quantum/modular_echelon_compact.py` and leaves
  `modular_echelon.py`, which engine v12 pins by digest, at its pinned bytes.
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
  `--stream-products` or `--echelon compact|gpu` is set, and `CompactEchelon(..., "compact")` of
  `modular_echelon_compact.py` refuses it at construction. The uint16
  residues alone admit p <= 2^16 and the 4,096-term float64 tiles admit p <= 1,482,911; the shared bound is the one the
  device backend already needs.
- Products upcast only a bounded inner tile to float64. `tiled_mod_product` and the compact echelon check
  `tile * (p - 1)^2 < 2^53` before each product, reduce modulo p after every tile and refuse a product outside that
  bound.
- A compact echelon row has an implicit unit pivot. Only its nonpivot coefficients are stored, in 1,024-column
  uint16 panels. Insertion takes an exact FLINT RREF on the free columns and rebuilds each panel modulo p, releasing
  the old panel before the next one is touched, so the basis never exists twice; the transient beyond the basis is
  a few panels (`insert_panel_bytes`).
- The standard-monomial receipt restricts the product rows. Its nonstandard controls must add zero rank.
- The cell runner binds the engine and header hashes, field, degree and truncation order, and through its resource
  record the engine arguments (repeated options keep their order, since the engine's parser keeps the last one; a file
  outside the checkout is bound by the SHA-256 of its contents, a path inside by its repository-relative path). It
  publishes JSON by flush and atomic rename only after engine exit 0 and
  record validation, and it terminates the engine's process group on SIGTERM, SIGINT or `--timeout`.

Small exact tests compare streamed and cached uint16 operators with engine v13's dense operator on a two-block
fixture with a nonzero variable character, compare v14's closure with v13's on a four-round, four-block cell, and
compare the compact echelon with FLINT `nmod_mat.rref` across a reduced tile width and panel width
(`tests/test_modular_echelon_compact.py`; every matrix comes from integer arithmetic, so no random draw is consumed).
One test traces the allocations of an insertion into an 800-row basis and requires the peak to stay below half the
basis, which fails when old panels are retained; one audit test crosses the default 4,096-term tile.

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
| v14 products stage (layers, retained uint16 rows, walk and tile temporaries) | at most 12.293 GiB, plus the accumulate-line arrays below |
| v14 closure stage (compact basis, rows, chunk temporaries, one insertion's panels) | at most 10.416 GiB |
| selected-array headroom inside 16 GiB | at least 3.707 GiB before the accumulate-line arrays |

The last three bounds are stage-local. Summing the operator and echelon terms would count arrays that are never live
together. Conversely, the 3.707 GiB is not guaranteed RSS headroom: sparse tables, Python objects, the FLINT entry
lists of each insertion and allocator state are outside the model. An instrumented process-group peak at or above
16 GiB falsifies the 16 GiB route. The model is arithmetic on named arrays under the Cauchy block-size bound; it is
neither a measurement nor a proof that an N = 19 run fits.

Closure stage. `CompactEchelon._insert_compact` replaces one panel at a time and drops each old panel before the next
is touched, so one basis is live. Beyond it an insertion holds the old panel, its column-selected copy and the grown
panel (3 x 1,024 columns x about 59,187 rows x 2 bytes), the reduction coefficients and the rebuilt panels of a mixed
state (at most `block x chunk` uint16 beyond the final basis, because `(r + k)(n - r - k) <= n^2 / 4` for r rows, k new
pivots and n columns), and the float64 tiles of the update: 0.391 GiB in all (`insert_panel_bytes`). Holding every old
panel until the last replacement is built would have added one block copy, at most 1.628 GiB at the 59,123-column
bound.

Products stage. The retained rows dictionary and the stacked inputs are the two uint16 copies of the product-row term:
prefix rows and new rows are distinct dictionary entries, so the dictionary, the inputs and the outputs of one call stay
inside two copies of the wanted rows. The accumulate line of `streamed_generator_product`,
`((outputs.astype(uint32) + contribution) % p).astype(uint16)`, holds per element of one call's contribution the
contribution (2 bytes) and two uint32 temporaries (4 + 4 bytes) beside the old output; the gathered input and the
contribution under construction in `tiled_mod_product` need 4 bytes per element and lie below that maximum. The term
is `10 x prefix_rows x block_size` bytes, where `prefix_rows` is the largest row count of one generator call
(`streamed_prefix_peak` of the engine: the wanted tuples of a level whose extension is wanted one level up, taken from
the receipt). The retained v11 terms do not carry that count, so the figure above omits the term (hypothesis: the
N = 19 receipt keeps `prefix_rows` small enough); the model reports that the stage stays inside 16 GiB for
`prefix_rows <= 6,732`. The engine's preflight computes the term from the receipt before any product is built, lists it
as `streamed_loop_arrays` in `preflight_terms` and refuses a run whose stage exceeds `--max-gb`, which settles the
hypothesis for the N = 19 cell. Walk temporaries (`streamed_walk_temporaries_bytes`, 0.147 GiB) are in the figure.

The W8 degree-6 rank itself is a diagnostic, not a missing theorem: A5-066 already gives the all-degree presentation,
and A5-291 rejected the old 129--223 GiB v11 rerun as mathematically redundant. The memory-bounded route remains useful
for falsifying the engine forecast and for unresolved E8 closure cells.
