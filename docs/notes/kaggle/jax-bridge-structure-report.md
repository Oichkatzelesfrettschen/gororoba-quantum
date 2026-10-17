# JAX bridge sweep: export once per structure, rescale CZ stacks, sample parity

The restructured `scripts/jax_bridge_sweep.py` reproduces the per-factor
export sweep. On the 105-replica dark/bright run the CPU time drops from
1389 s to 22 s, and JAX replay becomes the largest share of what remains.

## Mechanism

- **Structure key** (`jax_bridge.structure_key`). It holds `num_qubits`,
  `num_clbits`, and, for each instruction, its name, physical qubits, clbits
  and parameters. An angle gate (a `Gate` whose parameters are all bound
  reals; `rz` on these ISA circuits) contributes only its parameter count.
  Every other operation keeps its parameters, plus `unit` for a delay,
  because `RelaxationNoisePass` builds the delay's channel from its
  duration. The sweep keys templates by (snapshot, structure key).
  Equal keys under one noise model give equal channels at equal positions,
  because `insert_noise` selects errors by name and qubits and the custom
  passes act on `Delay` only. The programs differ only in the angle-gate
  unitaries.
- **Template** (`jax_bridge.template` / `instantiate`). Each angle-gate
  parameter becomes a `Parameter` named after its instruction index. The
  index therefore follows the gate through the relaxation pass's DAG round
  trip, and `instantiate` puts `Operator(op)` from the replica at the
  recorded position.
- **CZ channel** (`jax_bridge.CzChannel`). `NoiseModel.from_backend`
  (Aer 0.17.2, `_basic_device_target_gate_errors`) builds
  `depolarizing_error(p, 2).compose(relax)`: depolarizing first, then the
  tensor product of each qubit's `thermal_relaxation_error` over the gate
  duration. T2 is truncated to 2 T1 and the population is 0 at temperature
  0. p is `4 (e - r) / (4 F - 1)`, where r = 1 - F is the relaxation
  infidelity and F its average gate fidelity. e is capped at 4/5 and p at
  16/15, and p = 0 when e <= r.
  - The channel is (1 - p) R + p (rho -> Tr(rho) R(I)/4). Its Choi matrix is
    therefore affine in p, and the p = 1 term is I (x) R(I)/4.
  - A stack at any factor is the eigendecomposition of that 16x16 Choi
    matrix, keeping eigenvalues above 1e-13.
  - The sweep applies ghost_error_scale.scaled's rule
    e = min(factor * reported, 1) and replaces only the positions in
    `Program.cz`.
  - Readout scaling stays classical.
- **Kraus cache.** The cache is shared across exports only for the noise
  model's own errors, keyed by `id`. Relaxation errors that the delay pass
  creates are collected after each export, so their ids recur. Those errors
  are converted per export, and the template contract caught this collision.
- **Parity.** `--parity-sample N|all` (default 2) and `--parity-seed`
  (default 20261016) choose the replicas. The generator is
  `default_rng([seed, sha256(run)[:8]])` over the sorted `member#k` labels.
  `parity_checked` records each label with its deviation, and the Aer
  simulator is built once per snapshot.
- **Replay.** The sweep groups every replica x factor program of a run by
  (n, qargs sequence) and reads each group's largest rank per operation from
  the stack shapes (`jax_bridge.stack_ranks`). It calls each group in
  fixed-size chunks of at most `--batch-bytes` (default 2^28): per program,
  one complex64 density matrix plus its complex64 Kraus stacks padded to the
  group's ranks. Each call builds the padded stacks of its own programs only
  (`stack_programs(rows, ranks, complex64)`), so the host holds one call's
  stacks at a time and each structure compiles once. The output schema is
  `jax-bridge-sweep-v2`.
  - The padded Kraus stacks outweigh the density matrices 13x at n = 5
    (107,584 against 8,192 bytes per program on 070853) and 314x at n = 4
    (643,296 against 2,048 on 025444's 1998-operation groups).
  - At the default budget every group of 070847, 070853, 025444 and 031229
    fits one call, so the chunk sizes equal those of the state-only budget.
  - The group with the largest stacks in the 929-replica runs holds 140
    programs of 1998 operations: 90 MB of padded complex64 stacks in one
    call at the default budget, and less per call under a smaller
    `--batch-bytes`. Padding the whole group in complex128 before chunking
    held 180 MB plus each call's 90 MB complex64 copy.
  - Per-call stacks leave the sweep output of 070847 and 070853 at
    `--parity-sample 2` byte-identical once `seconds` is removed. Peak RSS
    of 070853 (`/usr/bin/time -v`) is 1,319,884 KB, against 1,310,348 KB
    with whole-group stacking. Its largest group (220 programs) held 71 MB
    of stacks under whole-group stacking and holds 24 MB per call, and
    neither sets the process peak.

## Contracts (`--self-test`, gates core-327 and core-337)

The reduced case is 31 replicas from snapshot
ibm_kingston/20261015T0003150700:

- run 070853, members design_b_dark, design_b_bright and design_d phase_0of8:
  24 replicas, 8 keys of 3 with differing rz angles;
- run 070847, all 7 baseline replicas, which carry delays.

The case has 15 structure keys in all.

| Contract | Measured | Bound |
|---|---|---|
| template instance vs direct export, every replica | bit-identical (array_equal) | exact |
| CZ slots found vs noisy CZ gates | equal | exact |
| rescaled CZ superop vs fresh Aer model, 72 couplers x factors 1e-3, 0.5, 12, 1000 | 3.0e-15 | 1e-12 |
| branches reached: zero-depolarizing / interior / error cap / depolarizing cap | 66 / 142 / 80 / 80 | each > 0 |
| non-CZ channels of the scaled models vs the factor-1 model | equal (QuantumError ==) | exact |
| restructured vs per-factor export, factors 0.5, 1, 12, all readout factors (numpy) | 6.3e-15 | 1e-9 |
| sampled parity vs Aer density matrix (numpy) | 1.9e-9 | 1e-8 |
| chunked replay at 2^20 bytes, largest group (60 programs, 7 calls of 9, last partial): each call's stacks vs the whole group's complex64 rows, numpy diagonals vs one call | bit-identical (array_equal) | exact |
| JAX CPU vs numpy diagonals (`--device cpu`, local only; the numpy references run through `parallel.ordered_map`) | 2.9e-6 | 1e-5 |
| chunked JAX CPU vs one call, same group (`--device cpu`, local only) | 0.0 | 1e-5 |

The 72 couplers are those the case drives, plus every coupler whose
reported error already exceeds 4/5. A self-test run takes 61 s on this
host in either `-W error` or `-O` mode before the chunking contract, which
adds 4.1 s (its section timer, `GOROROBA_WORKERS=6`). The self-test
imports no JAX, since no CI requirements file pins it.

## Reproduction of the earlier sweep's outputs

Both sweeps ran on the host CPU with JAX. The earlier output was retained
from the same host; run 070847 was also rerun with the HEAD script today.

| Run | Replicas | max abs TV difference | Mean-grid difference | Parity |
|---|---|---|---|---|
| 070847 | 7 | 0 (all 350 cells equal) | 0 | 5.1e-8 sampled (old 6.0e-8 full) |
| 070853 | 105 | 1.0e-6 (767 of 5250 cells move one unit in the sixth decimal) | 1.0e-6 | 3.9e-7 sampled, 1.03e-6 full (old 1.10e-6) |
| 080216 | 0 (both replicas dynamic, skipped with the same reasons) | | | |

The 070853 differences come from complex64 batching: 105 x 10 programs
run in one vmap, against 10 before. The numpy contract bounds the
restructure itself at 6e-15.

## Time split (seconds, host CPU, JAX on CPU)

The self-test's member subset has no sweep entry point. The timed reduced
case is therefore run 070847 in full (7 replicas), which the HEAD script
reran today on the same host. Run 070853 (105 replicas) is compared with
the earlier retained sweep.

| Case | export | parity | replay |
|---|---|---|---|
| 070847 before (HEAD script) | 40.3 | 48.3 | 0.78 |
| 070847 after, sample 2 | 3.7 | 6.7 | 0.80 |
| 070847 after, `--parity-sample all` | 3.8 | 7.9 | 0.81 |
| 070853 before (retained) | 463.2 | 894.9 | 31.2 |
| 070853 after, sample 2 | 2.8 | 1.4 | 17.7 |
| 070853 after, `--parity-sample all` | 2.9 | 2.1 | 18.5 |

The export after the change is mostly the one-time snapshot load, about
3.7 s for the factor-1 noise model, which the first run pays. The parity
after the change is the one-time Aer simulator build, about 3.7 s per
snapshot, plus one Aer call for every sampled replica of a snapshot. With
batching, full parity on 070853 costs 2.1 s, so `--parity-sample all` is
affordable at these widths. On 070853, replay is now 80 percent of the time
(17.7 of 21.9 s), which is the share a TPU can shorten.

Tool versions: jax 0.9.0, jaxlib 0.9.0.dev0+selfbuilt, numpy 2.5.4,
qiskit 2.5.2, qiskit-aer 0.17.2, Python 3.14, AMD Ryzen 5 5600X3D
(12 threads). Every command ran with `JAX_PLATFORMS=cpu
CUDA_VISIBLE_DEVICES=`.

## Commands

```sh
PYTHON=${PYTHON:-python3}
"$PYTHON" -B -W error scripts/jax_bridge_sweep.py --self-test
JAX_PLATFORMS=cpu "$PYTHON" -B -W error scripts/jax_bridge_sweep.py --self-test --device cpu
```

A TPU kernel goes through `scripts/kaggle_run.py push`, which bundles the
entry's import closure (jax_bridge, ghost_run, ghost_error_scale,
calibration_snapshot, parallel and packing among it). The sweep also reads
at run time:

- the retention audit that `--runs all` reads;
- the calibration history and its index.json (2.5 MB);
- record.json, isa.qpy and collect.json of each audited run, about 93 MB in
  all, 51 MB of it run 031229.

The gororoba-retained-runs dataset already carries every one of these files
with the tree's sha256 (its four absent history snapshots are ones no audited
run executed under), and 93 MB inline in run.py would exceed what SaveKernel
accepts, so the push attaches the dataset (the command is in the script's
docstring):

```sh
"$PYTHON" scripts/kaggle_run.py push scripts/jax_bridge_sweep.py --slug gororoba-jax-bridge-sweep-tpu \
  --dataset gororoba-retained-runs --machine TpuV5E8 --timeout 3600 \
  -- --device tpu --runs all --parity-sample 2 --out results/kaggle_out/jax-bridge-sweep-tpu.json
```

`--device tpu` raises when no TPU platform is visible. Since the account's
identity verification a TpuV5E8 push is TPU-classified (`isTpuEnabled`) and
queues for the account's single batch TPU slot
(docs/notes/kaggle/tpu-research.md), so this push follows the probe that
holds the slot.

## Not done

- The TPU run, for the slot reason above; the push command is not run.
- The 2-vCPU CI seconds for core-327 and core-337. The 61 s recorded is this
  12-thread host's measurement (59 s in each mode) without the chunking
  contract. With it, core-327 measured 73 and 98 s and core-337 69 and 75 s
  under a concurrent load average of 8 to 22, so no quiet-host figure
  exists for the gates as they stand.
- A full sweep over all audited runs. Only 070847, 080216 and 070853 were
  rerun; the wide runs 025444 and 031229 (929 replicas each) are not timed.
