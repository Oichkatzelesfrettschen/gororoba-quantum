# Engine v12: the per-block echelon basis on the CUDA device

`replay/engine/fiber_rank_v12.py` is engine v11 (`fiber_rank_v11.py`, sha256 `7849cbc71ccf1787...`, bytes unchanged) with
its `Echelon` class replaced by `gororoba_quantum/modular_echelon.py`. The flag `--echelon flint|gpu` (default `flint`)
selects the backend. The record format gains one key, `echelon`, which names the backend; every other field keeps
its name, type and order. `--echelon gpu` keeps each character block's reduced row echelon basis on the device as int32
residues and runs the reduction, the new-row echelonization and the update of the old rows there: an exact INT8
tensor-core modular product (signed base-256 digits, four products, int32 accumulation, inner dimension at most 32,768
per chunk) and a recursive PLUQ factorization with a blocked back substitution. The reduced row echelon form of a row
space is unique, so `--echelon flint` and `--echelon gpu` return the same basis, pivots and ranks for the same
insertion sequence. The table products `X @ T` of the closure stay on the host in both modes, and so does the
Singular export.

## Acceptance

Workstation (RTX 4090 Laptop GPU, 16 GiB, under WSL; Python 3.14.4, torch 2.14.1+cu130, CuPy 14.2.0, python-flint 0.9.0,
numpy 2.5.4, scipy 1.18.1; Singular 4.4.1 from the passagemath wheel). The host carried other sessions' jobs
(load average 5 to 10), so wall times scatter by tens of percent between identical runs; the rank fields do not. Every
run used `GOROROBA_WORKERS=8` and `GOROROBA_GPU_GIB=13.4`, which caps the process at 13.4 GiB of device memory
(`modular_echelon.py`, "Device memory"). Device memory is the `nvidia-smi` reading every 5 s (`logs/*.gpu`), taken on an
idle device (first sample 0 MiB). `echelon insert` is the time inside `Echelon.insert` over the closure
(the last line of each `.err` file).

| Cell | Engine, backend | Closure | Echelon insert | Wall | Peak device | Peak RSS |
|---|---|---|---|---|---|---|
| W8 -> N- degree 4, N = 13, p = 32009 | v11 | 201.9 s | n/a | 367 s | 0 | 3.75 GiB |
| | v12 flint | 207.1 s | 178.5 s | 378 s | 0 | 3.74 GiB |
| | v12 gpu | 44.8 s | 14.0 s | 213 s | 7.3 GiB | 2.61 GiB |
| Iso -> N- degree 6, N = 19, p = 32009, raw | v12 flint | 1,621.2 s | 1,452.7 s | 2,227 s | 0 | 19.6 GiB |
| | v12 gpu | 276.3 s | 92.0 s | 740 s | 12.1 GiB | 19.6 GiB |

The speedup is 4.6x on the W8 closure (12.8x on the echelon work inside it) and 5.9x on the Iso closure (15.8x on the
echelon work); the closure that remains is the host table products and the row transfers. The wall-time gain is 1.8x
on W8, where the host products stage (159 to 161 s) dominates, and 3.0x on Iso. The device path does not lower host
memory: the Iso peak RSS is equal in both backends.

Results, equal to the retained records:

- W8 degree 4 at N = 13: r = 1,725; per-block r_N 450 / 435 / 420 / 420; rank_W 5,036 / 4,973 / 4,999 / 4,999
  (`logs/w8d4n13-*.out`).
- Iso degree 6 at N = 19: r = 2,422; blocks 632 / 610 / 590 / 590; rank_W 7,195 / 7,162 / 7,119 / 7,119
  (`logs/iso-d6n19-*.out`).

Equality of the rank-bearing fields (not of the records: the production records hold ranks, not bases or pivots;
the bases and pivots are compared with flint in `tests/test_modular_echelon.py`). `compare_rank_fields.py` serializes every field of each record with sorted keys except `seconds`,
`echelon` and, inside `export`, `computed_seconds` and `reused`, and compares the sha256 of the result
([`compare-w8d4n13.txt`](compare-w8d4n13.txt), [`compare-iso-d6n19.txt`](compare-iso-d6n19.txt)). The v12 gpu and v12
flint records agree on every cell. Across engine versions (`--across-engines` also drops `engine_sha256_16`) the W8
records of v11, v12 flint and v12 gpu agree, and both Iso v12 records agree with the retained laptop record
[`../iso-d6-n19-laptop/isonm_d6_n19_p32009.json`](../iso-d6-n19-laptop/isonm_d6_n19_p32009.json) (engine v11), whose
export fields (standard-basis and table file digests, chunking) equal theirs.

## What remains on the host and what v12 does not change

- The host table products `X @ T` bound the closure: about 30 s of the 44.8 s W8 closure and about 185 s of the 276 s
  Iso closure. Moving them needs device-resident tables (about 3.6 GB of int32 for the dense W8 tables; the Iso tables
  are sparse).
- The preflight terms stay those of v11 (`fiber_rank_v12.py`, `walk_temporaries` and `echelon_bases` of the preflight
  dictionary), which the engine map measures 2.3 to 2.7 times above the peak, and under `--echelon gpu` the host
  basis term counts memory the device holds. A `--max-gb` launch of W8 degree 6 or Iso degree 7 stops at the
  preflight until they change. In-place update, streamed L and free-column storage are also not done.
- An earlier uncapped revision gave a W8 closure of 35.8 s with equal ranks; the Iso v11 baseline was not rerun (the
  flint backend is v11's code).

## Memory cap

`GOROROBA_GPU_GIB` limits torch's caching allocator and CuPy's pool and leaves 0.5 GiB for the context. An uncapped
revision of the module read 15.8 GiB on the 16 GiB card in the Iso run and took 1,217.7 s in the closure against 276.3 s
under the cap; the likely cause is a spill of device allocations to shared system memory under WDDM (hypothesis, no
measurement of the spill itself). The logs of that revision are not retained, and the table above cites only the runs
of the final bytes. Set the variable for every long device run.

## Bytes that ran

| File | sha256 prefix |
|---|---|
| `replay/engine/fiber_rank_v12.py` | `ef40c640497080d6` |
| `gororoba_quantum/modular_echelon.py` | `d5bf4f187ca441ae` |
| `accept.sh` | `7486aa4ceb6387fa` |
| `accept-iso.sh` | `b71ed16962aade82` |

`accept.sh ROOT TAG ENGINE D N [FLAGS]` and `accept-iso.sh ROOT TAG ENGINE [FLAGS]` take an absolute ROOT: both export
`GOROROBA_PARALLEL_DIR="$ROOT/gororoba_quantum"` and then change into ROOT, so a relative ROOT resolves beneath itself
and the engine cannot import its modules (the retained bytes stay as they ran; every recorded run used a `$HOME` path).
They ran each cell under a 20 GiB (W8)
or 40 GiB (Iso) cgroup scope with `/usr/bin/time -v` and the device sampler; the logs hold the home directory as
`$HOME`. The inputs are `working/build/inputs/p32009-r10754/w8-nm.sing` (sha256 `585a946d...`) with the degree-2
receipt of `working/distribute/out/a5-w8-receipt-p1/w8_p1/d2/`, and the Iso header of `iso-d6-n19-laptop/`
(`isop1/iso-nm.sing`, sha256 `1f1757d5...`). The Iso cell ran in raw mode (no receipt) on a copy of the finished N = 19
export of the laptop run.

## Tests

`tests/test_modular_echelon.py` compares the device `rref` with `flint.nmod_mat.rref` (rows and pivots) on 300 x 700,
700 x 300, 257 x 513, 64 x 64, 5 x 7 and degenerate matrices at p = 32009 and 32029, a chunked inner dimension of
36,868 against an int64 reference, and the `Echelon` insertion sequence of both backends (pivots, rows, reduction);
`tests/test_a5_fiber_rank_v12.py` runs the engine on two small headers and requires equal rank fields across v11, v12
flint and v12 gpu. The device tests skip without CUDA. The seeds are indices 1002 to 1007 of the ANU draw
`draw-2026-11-08T170257Z` (`docs/evidence/qrng_seeds/allocations.json`).
