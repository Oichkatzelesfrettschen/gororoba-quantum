# Aer GPU configuration on the build host

`result.json` is `scripts/aer_gpu_probe.py` run on the build host (Ryzen 5
5600X3D, 12 threads; RTX 4070 Ti, CUDA UMD 13.4; Arch python-qiskit-aer-cuda
0.17.2-1, built with `-DAER_ENABLE_CUQUANTUM=OFF`). Gate `core-record-check-04` (`tests/test_cli_record_checks.py`)
(`--check`) recomputes every derived value from the retained timings,
samples and counts and replays the CPU readout-toy and lowering contracts.

Host figures carry foreign load: other sessions held the CPUs during most
rows (1-minute load up to 65 on 12 CPUs, recorded per row at start and end,
and rows above 12 flagged `contended`), and the desktop compositor holds
about 4.6 GB and 15 to 45 percent utilization of the GPU, recorded per row
as the baseline. Absolute ms per shot is therefore pessimistic, mostly for
CPU rows; the configuration decision rests on ratios between GPU rows. The
T4 section below is the same probe without foreign load.

## Mechanism

- Aer's unbatched GPU executor runs noisy trajectories one shot at a time
  (metadata `gpu_parallel_shots_ = 1`), launching one kernel per operation
  on a 128-amplitude state: 11.0 ms per shot for the two-round N=21
  feed-forward circuit, against 1.27 ms on the CPU's shot threads. The
  utilization counter reads 75 percent because a kernel is resident, while
  each kernel occupies a few threads.
- `batched_shots_gpu` applies each operation to all shots of a batch:
  0.32 ms per shot on the control-flow-free two-round circuit with seeded
  counts identical to the CPU's at every tier, and 3.8 and 2.7 times faster
  than unbatched at 7 and 10 static qubits; at 14 qubits it is 2.2 times
  slower, so `BATCHED_SHOTS_MAX_QUBITS` is 10.
- The batched executor rejects `jump` (every if_else). Lowering if_else into
  bfunc-conditioned gates runs, but the readout toy shows the batched
  executor then evaluates the condition on the outcome before the readout
  channel (`01` 9489 against 1000 expected), so feed-forward circuits run
  unbatched (`calibration_snapshot.SnapshotSimulator`).
- Shot branching (`shot_branching_enable` with
  `shot_branching_sampling_enable`) drops the readout channel of a
  mid-circuit measurement on CPU and GPU, statevector and density matrix
  (toy z scores 100 to 2060); it changes the model and is excluded from
  every noisy replay, beyond being 2 to 5 times slower.
- cuStateVec: the 0.17.2-1 build this record ran on has no cuQuantum
  (`Simulation device "GPU" does not support cuStateVec on this system`), so
  its `gpu_statevector_custatevec` rows fail. python-qiskit-aer-cuda 0.17.2-2
  links libcustatevec (`docs/notes/build_host/custatevec.md`), and the
  Kaggle kernel's cu11 wheel loads cuquantum-cu11 24.8.0
  (`docs/notes/kaggle/custatevec.md`), so the T4 rerun measures the row.
- Two GPUs: `target_gpus` and batched shots spread over every visible GPU
  (`batched_shots_optimization_parallel_gpus`); the host has one GPU, so the
  `gpu_statevector_batched_gpu0` row runs only on the T4 x2.

## Readout toy (200,000 shots, e10 = 0.05, e01 = 0.10, expected 00 = 180,500)

| Configuration | Counts (c1 c0) | Keeps law |
|---|---|---|
| CPU or GPU, statevector or density matrix, unbatched; GPU default | 00 180526, 01 1043, 10 9502, 11 8929 | yes |
| CPU statevector, shot branching | 00 183334, 11 16666 | no |
| CPU density matrix, shot branching | 00 166667, 10 16666, 11 16667 | no |
| GPU statevector, shot branching | 11 200000 | no |
| GPU density matrix, shot branching | 00 200000 | no |
| GPU batched with lowered if_else (statevector and density matrix) | 00 180526, 01 9489, 10 9502, 11 483 | no |

## Crossover

Feed-forward trajectories under the correct configuration (unbatched GPU):
CPU 0.17 / 0.46 / 8.3 ms per circuit-shot at 7 / 10 / 14 qubits against GPU
0.50 / 0.95 / 1.51, so the GPU wins between 10 and 14 qubits. Circuits
without control flow batch: GPU 0.13 / 0.30 at 7 / 10 against CPU 0.18 /
0.46, and unbatched GPU 1.51 against CPU 6.6 at 14. At the 7-qubit N=21
widths the per-shot executor is the limit for feed-forward circuits, and
the CPU stays the faster correct substrate.

## Kaggle T4 x2

`results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config` ran
`--workloads toy,width --widths 7,10 --require-gpu` under `--gpu-env` on two
Tesla T4s (15,360 MiB each, compute capability 7.5, driver 580.178.04) with
4 Xeon CPUs at 2.00 GHz: Python 3.13.15, numpy 2.5.4 on scipy-openblas
0.3.34, qiskit 2.5.2, qiskit-aer-gpu-cu11 0.17.2 as the only owner of
`qiskit_aer`, cuquantum-cu11 24.8.0 (custatevec-cu11 1.6.0.post1). The
preflight in `gpu_env.json` lists no failure, and both Bell runs report
device GPU. Every GPU row reports device GPU, every cuStateVec row
`cuStateVec_enable` true, and no row is contended. Gate `core-record-check-04` runs
`--check` on the record.

ms per shot at 2048 shots:

| Configuration | static 7 | static 10 | dynamic 7 | dynamic 10 |
|---|---|---|---|---|
| statevector, unbatched | 1.005 | 1.657 | 1.024 | 1.636 |
| statevector, batched | 0.287 | 0.438 | 0.290 | 0.440 |
| statevector, cuStateVec | 1.238 | 1.964 | 1.318 | 2.022 |
| density matrix, unbatched | 0.164 | 0.190 | 1.707 | 19.089 |
| density matrix, batched | 0.166 | 0.193 | 1.698 | 19.403 |
| density matrix, cuStateVec | 0.169 | 0.186 | 1.185 | 11.729 |

- Batched statevector trajectories run 3.5 and 3.8 times faster than
  unbatched at 7 and 10 static qubits, the host's ratio, so the batched
  default holds on Kaggle. The dynamic batched rows time lowered
  conditions, which the batched executor evaluates before the readout
  channel; they are timing rows, and feed-forward circuits stay unbatched.
- cuStateVec runs the dynamic density matrix 1.44 and 1.63 times faster
  than the plain GPU executor at 7 and 10 qubits, and statevector
  trajectories 1.19 to 1.29 times slower. A measurement-sampled static
  density matrix evolves once, so its rows agree within 4 percent across
  configurations.
- Aer spreads per-shot and batched runs over both T4s: batched rows report
  `batched_shots_optimization_parallel_gpus` 2, and unbatched trajectories
  and dynamic density matrices `gpu_parallel_shots_` 2. A run that
  measurement sampling serves (a static density matrix, a noise-free static
  statevector) evolves one state on one GPU.
