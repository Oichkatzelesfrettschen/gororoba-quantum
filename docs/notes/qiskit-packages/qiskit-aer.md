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
