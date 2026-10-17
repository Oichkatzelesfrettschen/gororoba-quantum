# Aer GPU configuration on the build host

`result.json` is `scripts/aer_gpu_probe.py` run on the build host (Ryzen 5
5600X3D, 12 threads; RTX 4070 Ti, CUDA UMD 13.4; Arch python-qiskit-aer-cuda
0.17.2-1, built with `-DAER_ENABLE_CUQUANTUM=OFF`). Gate core-367
(`--check`) recomputes every derived value from the retained timings,
samples and counts and replays the CPU readout-toy and lowering contracts.

Host figures carry foreign load: other sessions held the CPUs during most
rows (1-minute load up to 65 on 12 CPUs, recorded per row at start and end,
and rows above 12 flagged `contended`), and the desktop compositor holds
about 4.6 GB and 15 to 45 percent utilization of the GPU, recorded per row
as the baseline. Absolute ms per shot is therefore pessimistic, mostly for
CPU rows; the configuration decision rests on ratios between GPU rows. The
clean measurement is the T4 rerun of the same probe.

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
- cuStateVec: the host build has no cuQuantum (`Simulation device "GPU" does
  not support cuStateVec on this system`). qiskit-aer-gpu-cu11 0.17.2 on
  Kaggle declares `cuquantum-cu11<24.11.0,>=23.3.0`, so the T4 rerun has a
  cuStateVec row; it is unmeasured here.
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
