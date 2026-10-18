# Exact branching ghost sweep: correctness, cost and GPU placement

`scripts/ghost_error_scale_branching.py` computes, for every replica of
every audited run, the exact law of its classical register at all fifty
(c, r) points of the ghost error-scale grid, under the calibration snapshot
in force when the replica's PUB began. `gororoba_quantum/branch_dm.py`
turns each replica into the quantum instrument Aer's density-matrix method
applies per shot and evolves it on numpy or torch. The Aer sweep
(`scripts/ghost_error_scale.py`) samples the same laws.

## What the gates hold

| Gate | Command | Holds |
| --- | --- | --- |
| core-363 | `--self-test`, normal and `-O` | (a) the analytic feed-forward law; (b) static laws equal jax_bridge's within 1e-12; (c) static diagonals equal Aer's `save_density_matrix` within 1e-9; (d) dynamic laws pass a G test against 200,000 Aer density-matrix shots at (1, 1) and (12, 3); (e) rescaled CZ superoperators equal freshly scaled noise models; (f) normalization; (g) torch complex128 equals numpy within 1e-12; (h) the restricted snapshot gives the full 156-qubit snapshot's laws exactly; (i) `error_superop` equals qiskit's SuperOp on every error those exports convert |
| core-364 | `--replay reduced.json` | the reduced case (run 2026-10-11T152922 at the grid corners) byte for byte |
| core-444 | `--check-converter` | `branch_dm.error_superop` equals `from_superop(SuperOp(error.to_quantumchannel()).data)` on all 1306 local errors the sweep of the 15 audited runs converts, across 11 snapshots; the largest entry gap is 1.4e-80 |
| core-441 | `ghost_branching_benchmark.py --check`, normal and `-O` | each benchmark record's derived fields from its raw rows, complex128 laws within 1e-10 of numpy, and process and split rows whose records equal the in-process complex128 row |

Behaviors these contracts fix:

- `if_else` reads the recorded, readout-noisy bit, as Aer does, so a
  splitting measurement branches on (true outcome m, recorded bit b) and
  carries P_r(b | m) as a symbol evaluated per readout factor.
- A local error's superoperator comes from its exact Kraus stacks. A Kraus
  form taken back from an eigendecomposition drops eigenvalues near zero
  (2.3e-9 on a pure-relaxation CZ channel), so `error_superop` never
  round-trips through one.
- `insert_noise` walks top-level instructions only, while Aer applies noise
  inside control-flow bodies, so each `if_else` body is exported through
  the same passes on its own.
- Aer 0.17.2's shot branching drops a mid-circuit measurement's readout
  channel, so no simulator call here enables it
  (`docs/evidence/aer_gpu_configuration/README.md`).

## Where the time goes

The sweep is one pool map over (run, slice) items (`RunSlicer`). A worker
prepares its run, takes the (snapshot, active qubits) pairs `assign()` gives
its slice, builds one noise model per pair and every group's plan under it,
and on numpy also evolves and samples, so only distances leave the worker.
On torch the plans return to the main process, which stages one group at a
time on the device; device memory then holds the widest group, not the
widest run.

Three rules bound the cost:

1. A local error's superoperator comes from `error_superop`; qiskit's
   SuperOp composes each error circuit through instruction conversions
   and stays the reference that core-444 compares.
2. One noise model serves every group on a (snapshot, active qubits) pair:
   the 420 groups of the audited runs share 115 pairs.
3. Only distances, or plans for the device, cross a process boundary.
   A worker keeps the 156-qubit circuits it prepares, and on numpy also the
   plans it builds. `packing.extract_many` places a fused PUB's members in
   one pass over the PUB.

The evolve and sample phases are a few seconds of either engine, so the
sweep is CPU-bound: a GPU shortens only the part that was already short.

## Benchmark records

`scripts/ghost_branching_benchmark.py` times numpy, torch CUDA complex128
and complex64 in one process and compares their unrounded laws with
numpy's; with two GPUs it adds one sweep process against one process per
GPU. Every row sweeps the 15 audited runs at all 50 grid points.

Kaggle T4 x2, 4 Xeon CPUs at 2.00 GHz, numpy 2.5.4, torch 2.14.1 on CUDA
13.0, driver 580.178.04, load average 2.1 to 2.4
(`results/kaggle/2026-10-18T041945Z-gororoba-ghost-branching-t4`, 0.19 GPU
hours):

| Row | Wall s | Pool map s | Device s (upload, evolve, sample) | Largest law gap to numpy |
| --- | --- | --- | --- | --- |
| numpy, 4 workers | 34.9 | 34.2 | none | reference |
| torch CUDA complex128 | 39.3 | 34.2 | 1.0, 2.0, 1.3 | 1.4e-15 |
| torch CUDA complex64 | 38.4 | 33.3 | 1.2, 1.7, 1.2 | 4.8e-7 |
| one sweep process, complex128 | 45.0 | 34.4 | 1.1, 2.0, 1.3 | records equal the in-process row |
| one process per T4, complex128 | 44.7 | 37.0 and 24.7 | per process | records equal the in-process row |

Build host RTX 4070 Ti, Ryzen 5 5600X3D with 12 workers, torch 2.14.1 on
CUDA 13.4 (`benchmark-host.json`): the same law gaps, 1.4e-15 and 4.8e-7,
and every best point equal to numpy's. Its walls (numpy 11.0 s, complex64
17.2 s, complex128 34.7 s) ran at load averages of 15 to 23 from other
sessions' gates, with another process holding 8 GB of the GPU's 12 GB, so
they bound the order and not the ratios.

What the rows settle:

- The pool map, preparation and export on the CPUs, takes the same 34 s
  in every T4 row; the GPU phases add about 4 s, while the numpy row's
  evolve and sample run inside the pool for about 3.6 s of wall. numpy over
  the pool is the fastest engine for this sweep, and torch on a GPU agrees
  with it to rounding.
- One process per T4 finished in 0.994 of one process's time, so the
  prediction (at least 0.95) held: the halves share the same 4 CPUs, and
  the halves split by isa.qpy bytes still ran 37.0 against 24.7 s.
- The sweep therefore belongs on a Kaggle CPU kernel or the build host.
  A GPU push of it spends quota for no gain, and a T4's 4 CPUs are slower
  than the build host's 12 workers.

## Running it on Kaggle

The sweep's route is a CPU kernel under CI's Python and pins, which spends
no GPU quota:

```sh
"$PYTHON" scripts/kaggle_run.py push --slug gororoba-ghost-branching-sweep \
    --machine cpu --ci-env --dataset gororoba-retained-runs \
    scripts/ghost_error_scale_branching.py -- --runs all \
    --out /kaggle/working/output/ghost_error_scale_branching.json
```

`results/kaggle/2026-10-18T055207Z-gororoba-ghost-branching-sweep` holds
that kernel's output: Python 3.14.7 with CI's pins (numpy 2.5.4 on pip's
OpenBLAS, qiskit 2.6.0) on 4 Xeon CPUs at 2.20 GHz.

- The pool map took 36.1 s on 4 workers, against 10.6 s on the build
  host's 12 (AOCL numpy, qiskit 2.5.2). The kernel's 286 s of wall is mostly
  the CI interpreter and pin install.
- Every run's laws, distances, sampled estimates and best points equal the
  build host's output exactly; the files differ only in `seconds`,
  `warmup_seconds` and `versions`. The sweep's arithmetic is therefore
  independent of the BLAS build and of the qiskit 2.5 to 2.6 step on these
  15 runs.
- `--compare-parts docs/evidence/ghost_error_scale/part_X.json --result
  OUTPUT` for parts a, b and c puts all 50 grid points of each of the 14
  runs the parts cover within the Aer sweep's tolerance. The sampled best
  point differs from Aer's on 3 runs (2026-10-13T080216, 2026-10-13T201757,
  2026-10-13T032011); on each, the sampled mean TVD at Aer's best point
  exceeds the sampled minimum by 0.0066, 0.0001 and 0.00004, below that
  run's tolerance of 0.079, 0.032 and 0.016.

The T4 x2 benchmark that settled the route reproduces as:

```sh
kaggle quota
"$PYTHON" scripts/kaggle_run.py push --slug gororoba-ghost-branching-t4 \
    --machine NvidiaTeslaT4 --timeout 2400 --gpu-env --gpu-env-with torch \
    --dataset gororoba-retained-runs scripts/ghost_branching_benchmark.py -- \
    --out /kaggle/working/output/ghost_branching_benchmark.json \
    --require-gpu "Tesla T4" --gpus 2
kaggle quota
```

- `--gpu-env --gpu-env-with torch` runs the entry in the pinned venv:
  numpy 2.5.4, qiskit 2.5.2 and torch 2.14.1, the host's versions.
- `gororoba-retained-runs` carries every run archive, the calibration index
  and the snapshots the sweep reads, at the tree's digests.
- `--require-gpu` stops the entry (exit 3) unless torch lists both T4s and
  a complex128 matmul on each matches numpy. The same push with
  `--machine cpu` stops at the venv preflight (exit 4) at no GPU cost.
