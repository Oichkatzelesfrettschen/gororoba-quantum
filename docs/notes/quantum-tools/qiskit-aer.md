# qiskit-aer

## NAME

qiskit-aer 0.17.2 -- Qiskit simulators: statevector, density matrix,
stabilizer, matrix product state, extended stabilizer, unitary, superoperator,
tensor network; noise models; CPU and GPU devices.

## SYNOPSIS

```python
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError
sim = AerSimulator.from_backend(view, noise_model=noise, method="density_matrix", device="CPU")
sim.run(transpiled, shots=20000, seed_simulator=4).result().get_counts()
```

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit-aer-cuda 0.17.2 (Arch, CUDA build; provides python-qiskit-aer); `available_devices()` returns `('CPU', 'GPU')` and the RTX 4070 Ti runs the GPU path |
| Kaggle | `qiskit-aer-gpu-cu11==0.17.2` in `KERNEL_PINS`; it lists `GPU` in `available_devices()` even on a CPU-only kernel, so check `environment.json` |

## CAPABILITIES IN THIS REPOSITORY

- Density-matrix noise replay. `calibration_snapshot.noise_model(snapshot)`
  builds `NoiseModel.from_backend(view, readout_error=False)` and adds one
  `ReadoutError([[1 - e10, e10], [e01, 1 - e01]])` per qubit;
  `noise_simulator(snapshot, device)` wraps it as
  `AerSimulator.from_backend(view, noise_model=noise, method="density_matrix", device=device)`.
  The example prints the model's basis gates and its 1131 channels
  (`channel_table`).
- Device choice. `device="GPU"` reproduces the CPU counts exactly for the
  same seed in the example. Memory sets the size: 16 x 4^n bytes for a
  double-precision density matrix, 14 qubits on a 12 GiB or 16 GB card
  (`docs/notes/kaggle/substrates.md`).
- Methods without a density matrix: `stabilizer` (Clifford, the Aer sibling
  of [stim.md](stim.md)) and `matrix_product_state` both ran a 40-qubit GHZ
  circuit in the example; `statevector` at 40 qubits fails with
  insufficient memory. `tensor_network` appears in `available_methods()`; it was not run.
- Dynamic circuits with feed-forward run on Aer (`if_test` circuits in
  [qiskit-ibm-runtime.md](qiskit-ibm-runtime.md) execute under the same
  noise model).
- Noise API: `NoiseModel.add_quantum_error`, `add_readout_error`,
  `add_basis_gates`, `noise_instructions`, `basis_gates`, and
  `_local_quantum_errors` / `_local_readout_errors` (private, read by
  `channel_table`).

## API ENTRY POINTS

`qiskit_aer` public names (33), by introspection:

classes:

```text
  AerError, AerJob, AerProvider, AerSimulator, QasmSimulator,
  StatevectorSimulator, UnitarySimulator
```

modules:

```text
  aer_compiler, aer_simulator, aerbackend, aererror, aerprovider,
  backend_utils, backendconfiguration, backendproperties, backends,
  compatibility, controller_wrappers, jobs, library, name_mapping, noise,
  platform, primitives, qasm_simulator, quantum_info, statevector_simulator,
  sys, unitary_simulator, utils, version, warnings
```

other:

```text
  Aer
```

`qiskit_aer.noise` public names (22), by introspection:

classes:

```text
  LocalNoisePass, NoiseModel, PauliError, PauliLindbladError, QuantumError,
  ReadoutError, RelaxationNoisePass
```

functions:

```text
  amplitude_damping_error, coherent_unitary_error, depolarizing_error,
  kraus_error, mixed_unitary_error, pauli_error,
  phase_amplitude_damping_error, phase_damping_error, reset_error,
  thermal_relaxation_error
```

modules:

```text
  device, errors, noise_model, noiseerror, passes
```

`qiskit_aer:AerSimulator` public names (25), by introspection:

functions:

```text
  available_devices, available_methods, clear_options, configuration,
  from_backend, properties, qubit_properties, run, set_max_qubits,
  set_option, set_options
```

other:

```text
  coupling_map, dt, dtm, instruction_durations, instructions, max_circuits,
  meas_map, num_qubits, operation_names, operations, options, provider,
  target, version
```

## EXAMPLES

Marked as a GPU example: it runs `device="GPU"` on the host card.

```python
# gpu
import json, logging, sys
sys.path.insert(0, "gororoba_quantum")
import numpy as np
import qiskit_aer
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import calibration_snapshot as cs

logging.getLogger("qiskit_aer").setLevel(logging.CRITICAL)
print("qiskit-aer", qiskit_aer.__version__)
sim0 = AerSimulator()
print("methods:", sim0.available_methods())
print("devices:", sim0.available_devices())

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
view, noise = cs.noise_model(snap)
print("noise basis gates:", sorted(noise.basis_gates))
print("noisy instructions:", sorted(noise.noise_instructions))
table = cs.channel_table(noise)
print("channels:", len(table), " sample keys:", sorted(table)[:2], sorted(k for k in table if k.startswith("readout"))[:2])

# the snapshot simulator and the same circuit on each device and each method
sim = cs.noise_simulator(snap)
print("snapshot simulator method:", sim.options.method, " device:", sim.options.device)
ghz = QuantumCircuit(3, 3)
ghz.h(0); ghz.cx(0, 1); ghz.cx(1, 2); ghz.measure([0, 1, 2], [0, 1, 2])
tc = transpile(ghz, sim, initial_layout=[0, 1, 2], optimization_level=1, seed_transpiler=1)
cpu = sim.run(tc, shots=20000, seed_simulator=4).result().get_counts()
gpu_sim = cs.noise_simulator(snap, device="GPU")
try:
    gpu = gpu_sim.run(tc, shots=20000, seed_simulator=4).result().get_counts()
    print("GPU counts:", dict(sorted(gpu.items())))
except Exception as e:
    print("GPU run failed:", type(e).__name__, str(e)[:200])
print("CPU counts:", dict(sorted(cpu.items())))

# ideal methods beyond the density-matrix limit
big = QuantumCircuit(40, 1)
big.h(0)
for k in range(39):
    big.cx(k, k + 1)
big.measure(39, 0)
for method in ("stabilizer", "matrix_product_state"):
    r = AerSimulator(method=method).run(transpile(big, AerSimulator(method=method)), shots=1000, seed_simulator=1).result()
    print(f"{method}: 40-qubit GHZ, last-qubit counts", dict(sorted(r.get_counts().items())))
r = AerSimulator(method="statevector").run(big, shots=10).result()
print("statevector at 40 qubits fails with insufficient memory:", "Insufficient memory" in r.results[0].status)
```

Output:

```text
qiskit-aer 0.17.2
methods: ('automatic', 'statevector', 'density_matrix', 'stabilizer', 'matrix_product_state', 'extended_stabilizer', 'unitary', 'superop', 'tensor_network')
devices: ('CPU', 'GPU')
noise basis gates: ['cz', 'delay', 'id', 'measure', 'reset', 'rz', 'sx', 'x']
noisy instructions: ['cz', 'id', 'measure', 'reset', 'sx', 'x']
channels: 1131  sample keys: ['cz[0, 1]', 'cz[1, 0]'] ['readout[0]', 'readout[100]']
snapshot simulator method: density_matrix  device: CPU
GPU counts: {'000': 9836, '001': 46, '010': 45, '011': 129, '100': 56, '101': 81, '110': 170, '111': 9637}
CPU counts: {'000': 9836, '001': 46, '010': 45, '011': 129, '100': 56, '101': 81, '110': 170, '111': 9637}
stabilizer: 40-qubit GHZ, last-qubit counts {'0': 482, '1': 518}
matrix_product_state: 40-qubit GHZ, last-qubit counts {'0': 482, '1': 518}
statevector at 40 qubits fails with insufficient memory: True
```

## INTEROP WITH QISKIT

Aer is a Qiskit provider. `AerSimulator.from_backend(view, ...)` takes a
`BackendV2`; the snapshot `SnapshotBackend` is one. Circuits must be
transpiled to the noise model's basis (`cz`, `sx`, `x`, `rz`, `id`, `delay`,
`measure`, `reset`), otherwise `AerError: unknown instruction: h` follows
(observed with an untranspiled circuit through the local Sampler).

## CPU AND GPU

| Method | CPU | GPU |
| --- | --- | --- |
| statevector, density_matrix, unitary, superop | yes | yes (`device="GPU"`) |
| tensor_network | listed | listed in `docs/notes/kaggle/substrates.md` for GPU; not run |
| stabilizer, matrix_product_state, extended_stabilizer | yes | CPU only (root `docs/notes/kaggle/substrates.md`) |

The 156-qubit Target did not enlarge the state in any example here: 2- to
3-qubit circuits on the 156-qubit simulator ran at the cost of their own width.

## TRAPS

- `AerSimulator.available_devices()` lists `GPU` on a CPU-only Kaggle kernel; a
  run then fails (`RuntimeError: No CUDA device available!` is what a host run
  with `CUDA_VISIBLE_DEVICES=""` printed here).
- The snapshot's `e10` and `e01` are reported backend properties, so the replay applies the reported readout channel and not the measured one. `results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md` records Kingston qubits 0 and 1 misassigning the ground state 39 and 27 percent of the time and the excited state 14 and 12 percent on a device run, against reported readout errors below 1 percent, with Ramsey visibilities near readout factors of 0.47 and 0.60. A replay therefore carries no information about that fault. Mitigating or interpreting a retained job needs assignment matrices from that job's own preparation baselines.
- A noisy 15-qubit density matrix was killed on a T4 and needs 16 GiB; the
  routing rule sends 15 qubits and more to IBM.
- `NoiseModel.from_backend` relaxes gates and delays with T1 and T2 but gives
  no coherent or crosstalk error; the readout channel is added separately and
  `readout_error=False` avoids doubling it.
- Statevector failure at width reports through `result.results[0].status`
  (`ERROR: ... Insufficient memory`), and the call prints the error to
  stderr instead of raising.
- Use `seed_simulator` and `seed_transpiler` to make counts replayable.

## LICENSE

Apache-2.0.
