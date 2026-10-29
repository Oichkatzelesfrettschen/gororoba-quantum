# qiskit-aer and qiskit-aer-gpu

qiskit-aer 0.18.2 is the simulator behind every local primitive in this
repository: `AerSimulator`, `qiskit_aer.primitives.SamplerV2` and
`EstimatorV2`, and the noise models built from a backend's calibration.

PyPI publishes two distributions from one source tree. `qiskit-aer` carries
the CPU build. `qiskit-aer-gpu` carries a CUDA 12 build, which pulls the
`nvidia-*-cu12` wheels and `cuquantum-cu12<24.11`. The host installs neither
wheel. It builds one Arch package, `python-qiskit-aer-cuda`, from the same
sdist against the system CUDA 13.4 toolkit, cuQuantum 26.09 and OpenBLAS.
That package provides and conflicts with `python-qiskit-aer`, so a single
module serves both CPU and GPU (`AerSimulator().available_devices()`
returns `('CPU', 'GPU')`). The CPU-only PKGBUILD `python-qiskit-aer` stays
in `~/Github/PKGBUILDs` for hosts without a GPU.
[custatevec.md](../build_host/custatevec.md) holds the build and its probes.

## Provider name collision on GPU builds

Upstream Aer, through 0.18.2 and its main branch, has two defects in how it names backends:

- `AerProvider._get_backends` (qiskit_aer/aerprovider.py) registers the
  automatic method under the bare name `aer_simulator` once per available
  device. On a GPU-capable module that name matches a CPU and a GPU entry, and
  `Aer.get_backend("aer_simulator")` raises `QiskitBackendNotFoundError: More
  than one backend matches the criteria`. A `device=` keyword does not
  disambiguate, because `AerProvider.backends` ignores its keyword arguments.
  `CUDA_VISIBLE_DEVICES=` does not hide the GPU entry either, because
  `available_devices()` reports the compiled devices.
- `AerSimulator.set_option`, which the provider calls with `device`, rebuilds
  the name without the device suffix whenever the method is automatic. The
  constructor applies the suffix, so the two paths disagree, and the GPU
  backend reports the name `aer_simulator`.

python-qiskit-aer-cuda 0.18.2-3 carries `aer-provider-unique-names.patch`, which fixes
both defects:

- The GPU entry of the automatic method registers as `aer_simulator_gpu`,
  matching the existing `aer_simulator_statevector_gpu` naming.
- `set_option` derives the name with the constructor's rule: a method suffix
  unless the method is automatic, then a device suffix unless the device is the CPU.

After the patch, every provider key equals its backend's `name`, and the 16
names are unique. `get_backend("aer_simulator")` returns the CPU backend and
`get_backend("aer_simulator_gpu")` the GPU backend. qiskit 2.6.1's suite,
including `TestSabreSwap.test_no_infinite_loop`, passes. A wheel install of
upstream Aer on a GPU host still has both defects, and
`AerSimulator(device=...)` works on both builds.

## Connections

- Executes the circuits of [qcog](qcog.md), [qubasic](qubasic.md),
  [quantum-pipeline](quantum-pipeline.md) (Aer 0.17.2 in its own stack) and
  [eigenkit](eigenkit.md).
- pauli-prop requires `qiskit-aer>=0.17.1` for its `PauliLindbladError`
  channel type ([qiskit-addon-slc](qiskit-addon-slc.md)).
- A primitive wrapped by [qiskit-resume](qiskit-resume.md) records and
  replays Aer results like any other `BaseSamplerV2`.
- The isolated stacks each carry their own Aer: 0.17.2 in the Quantum
  Inspire and quantum-pipeline stacks, 0.12.1 in the qiskit-debugger stack.

## Flags

[library-flags.md](../../runbooks/library-flags.md) carries Aer's thread,
BLAS and GPU settings, including `CUDA_VISIBLE_DEVICES` in place of the
absent `target_gpus` option.
