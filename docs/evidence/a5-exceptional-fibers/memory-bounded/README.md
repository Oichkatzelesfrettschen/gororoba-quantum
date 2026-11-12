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

[`w8-n16-acceptance.json`](w8-n16-acceptance.json) summarizes one run of W8 -> N- at degree 5, N = 16, p = 32009,
whose three records the directory [`w8-n16-acceptance/`](w8-n16-acceptance/) retains: the engine's stdout record
([`w8-nm-d5-n16-p32009.json`](w8-n16-acceptance/w8-nm-d5-n16-p32009.json)), its stderr
([`.err`](w8-n16-acceptance/w8-nm-d5-n16-p32009.err)) and the runner's resource file
([`.resources.json`](w8-n16-acceptance/w8-nm-d5-n16-p32009.resources.json)); the summary lists their sha256.
[`acceptance_summary.py`](acceptance_summary.py) regenerates the summary from those three records and the retained v11
comparator; `--check` compares the tracked file with a fresh one and also requires the engine file's sha256 to equal
the resource record's `engine_sha256`, so an edited engine fails it until the run is repeated. The launcher settings
that no record holds are constants of the script. The
summary agrees with the retained v11 receipt run: `r_16 = 4116`; block contributions 1,017 / 1,005 / 1,047 / 1,047;
closure ranks 15,364 / 15,264 / 15,315 / 15,315; all 265 nonstandard controls add zero rank. V14 reports four
frontier rounds rather than v11's five because rows are materialized lazily after intervening RREF updates; the fixed
closure space and every final block rank agree.

Provenance of the summary:

- The run executed `fiber_rank_v14.py` through [`rank_cell.py`](../replay/engine/rank_cell.py). The resource file's
  `engine_sha256` (`ba7bc490c9e986ab...`) equals the digest of the engine file at the head of the branch, as do the
  header and receipt digests of the files the command names; the runner exited 0 with an empty `validation_error`.
- The run used the cached uint16 operator (`product_operator: uint16-cached`, `operator_cache_gib: 6`). The streamed
  route without the cache, on which the N = 19 model below rests, was not exercised at this size; the unit tests and
  the smaller cells compare it with the dense operator.
- The worker count, BLAS and OpenMP thread settings and the memory scope (a systemd user scope with
  `MemoryMax=16G`, `MemorySwapMax=0`) come from the launch of the run; the resource file records the engine arguments
  and the process-group resident set, not the environment. The summary keeps them in a separate block.
- The resource file carries no swap or out-of-memory counter, so the summary reports none; the scope's
  `MemorySwapMax=0` leaves no swap to count.

| Quantity | retained v11 | v14 compact |
| --- | ---: | ---: |
| wall | 7,841.2 s (two workers on a cloud VM, beside a second job) | 5,881.9 s (four workers, the build host) |
| products | 2,201.4 s | 1,255.3 s |
| closure | 4,751.3 s | 3,966.0 s |
| peak memory | 24.9 GiB (largest single-process RSS, GNU `time`) | 5.01 GiB (RSS summed over the process group) |
| preflight selected arrays | 58.9 GiB (sum of every term) | 4.69 GiB (larger of the products and closure stages; the seven terms sum to 5.95 GiB) |

The memory rows are two statistics: a single-process maximum and a process-group sum that counts pages shared by
forked workers once per process, so the ratio 0.201 errs against v14. The wall rows come from two machines with
different worker counts, and v11 shared its VM with a second job, so the ratio 0.750 carries no hardware-neutral
meaning. On this cell the measured v14 peak lies below the v11 peak; the equality of ranks is a finite-field result
and does not transfer to characteristic zero.

### Reproducing the acceptance run

The command below runs from the repository root, takes about 98 minutes and writes the three records into a new
empty `OUT` directory (`rank_cell.py` skips a run whose existing record validates, so a populated `OUT` launches
nothing). It needs Singular 4.4.1 on `PATH` and the interpreter of the CI pins in `PYTHON`.

```sh
PYTHON=${PYTHON:-python3}; export PYTHON
FIB=docs/evidence/a5-exceptional-fibers
ENGINE=$FIB/replay/engine/fiber_rank_v14.py
HEADER=$FIB/working/build/inputs/p32009-r10754/w8-nm.sing
RECEIPT=$FIB/working/distribute/out/a5-w8-receipt-p1/w8_p1/d2/receipt-d2.json
OUT=PATH-TO-A-NEW-EMPTY-DIRECTORY
printf '%s  %s\n' \
    ba7bc490c9e986ab9e794973ac73f5f25e704dd1c6e21b9bf04808779ec3eca5 "$ENGINE" \
    585a946d2d75073e4a90f697417017f2c13f432556c89088aaabfb9dff02a760 "$HEADER" \
    6e464db695bd891e93bfde1689dfab9c0d5bc1afdc17da3df3c3a29bb0f76425 "$RECEIPT" | sha256sum -c -
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4 OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=1 SINGULAR=Singular
systemd-run --user --scope -q -p MemoryMax=16G -p MemorySwapMax=0 \
    "$PYTHON" -B $FIB/replay/engine/rank_cell.py --timeout 14400 \
    "$ENGINE" "$HEADER" 5 16 "$OUT/w8-nm-d5-n16-p32009.json" -- \
    --quotient --stream-products --operator-cache-gb 6 --echelon compact --chunk 64 --max-gb 12 \
    --dense-tables-gb 0 --k2-receipt "$RECEIPT" --singular "$SINGULAR"
```

A rerun is compared with the retained stdout record on `r_N`, `per_block` and `checks`; the `seconds` and `export`
timings vary with the host.

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
  record the engine arguments (repeated options keep their order, since the engine's parser keeps the last one; an
  existing file, named with or without a slash, is bound by the SHA-256 of its contents wherever it lies, a path that
  does not exist inside the checkout by its repository-relative path; `--option=VALUE` is split at the first `=` for
  both rules and for the path stored in the resource record). It publishes JSON by flush and
  atomic rename only after engine exit 0 and record validation, and it terminates the engine's process group on
  SIGTERM, SIGINT or `--timeout`, and any group member still alive when the engine exits, successfully or not. Each
  output holds an exclusive `flock` on `OUTPUT.lock` from the existing-record check through publication, so two
  invocations never share a `.part`, stderr or resource file; the second prints a message, touches no record file and
  exits 75. A record or resource file whose JSON is not an object fails validation like any other malformed record.

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

Cached-operator route. Building the cached uint16 operator (`compact_generator_blocks`) holds, per slice of `chunk`
rows and per element of a chunk x widest array, the gathered parent rows (2 bytes), the contiguous copy of their
transposition that scipy flattens (2), its float64 cast (8), the float64 sparse product (8), its modulo (8) and the
uint16 result (2): 30 bytes, bounded by 32 (`sparse_row_chunk_bytes`). The engine lists the bound as
`operator_build_temporaries`; the operator is complete before any tiled product runs, so the products stage adds the
larger of it and `tiled_product_temporaries` beside the operator and the product rows.

The W8 degree-6 rank itself is a diagnostic, not a missing theorem: A5-066 already gives the all-degree presentation,
and A5-291 rejected the old 129--223 GiB v11 rerun as mathematically redundant. The memory-bounded route remains useful
for falsifying the engine forecast and for unresolved E8 closure cells.
