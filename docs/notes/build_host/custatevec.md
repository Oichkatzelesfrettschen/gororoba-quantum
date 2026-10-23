# cuStateVec in the host Aer build

The installed python-qiskit-aer-cuda 0.17.2-1 was compiled without cuQuantum,
so `AerSimulator(device="GPU", cuStateVec_enable=True)` raises
`RuntimeError: Simulation device "GPU" does not support cuStateVec on this
system`. python-qiskit-aer-cuda 0.17.2-2, built against a repackaged
cuquantum 26.09.0.8, enables the option. Its verification ran on the
extracted package tree and again on the installed package.

## Cause chain

1. The installed `controller_wrappers` module lists no libcustatevec or
   libcutensornet among its NEEDED libraries (`readelf -d`) and contains the
   Aer string "does not support cuStateVec on this system", which Aer
   compiles in when `AER_CUSTATEVEC` is undefined. It carries sm_89 cubins and
   PTX, links libopenblas.so.0, and was built 2026-10-12 by an unknown
   packager. No pacman package, AUR clone, or makepkg cache retains its
   recipe, so the exact flag set is unrecoverable; the binary shows the
   outcome.
2. qiskit-aer 0.17.2 enables the libraries only under the CUDA Thrust backend
   (`AER_THRUST_BACKEND=CUDA`) with `AER_ENABLE_CUQUANTUM=ON` and a
   `CUQUANTUM_ROOT` holding `include/` and `lib/` (CMakeLists.txt, non-wheel
   branch). That switch defines `AER_CUSTATEVEC` and `AER_CUTENSORNET`
   together, so cuTensorNet comes along.
3. Arch carries no cuquantum package (`pacman -Ss cuquantum` and
   `paru -Si cuquantum` find none). Upstream's wheel route pins
   `cuquantum-cu12<24.11.0`, which has no CUDA 13 build. NVIDIA publishes a
   CUDA 13 redistributable archive for cuQuantum 26.09.0.8.
4. Aer 0.17.2 does not compile unchanged with CUDA 13.4 (nvcc 13.4.92, GCC
   16.2.1, fmt 12, spdlog 1.17):
   - the module is pinned to C++14, and CCCL 3 (`cub/util_cpp_dialect.cuh`)
     errors below C++17;
   - `thrust::unary_function` is gone (three functors in
     `thrust_kernels.hpp`);
   - nvcc rejects fmt 12's constexpr `accessor` over
     `std::back_insert_iterator` below C++20;
   - Aer's CMake takes OpenBLAS whenever libopenblas is installed, so the
     module links libopenblas.so.0 outside the blas/lapack virtuals.
5. Every custatevec symbol Aer calls (25 names) and every cutensornet symbol
   (81 names) exists in the cuStateVec 1.15 and cuTensorNet 2.14 headers, and
   the sources compile against them without an API patch.

## Requirements

- cuquantum 26.09.0.8 for CUDA 13, installed under /usr (libcustatevec.so.1,
  libcutensornet.so.2 and headers), built from the vendor archive.
- cutensor >= 2.8 (installed 2.8.1.0) for libcutensornet.
- Aer build: `AER_THRUST_BACKEND=CUDA`, `AER_CUDA_ARCH="8.9+PTX"` (sm_89
  cubin plus compute_89 PTX, as installed), `AER_ENABLE_CUQUANTUM=ON`,
  `CUQUANTUM_ROOT=/usr`, C++20, the CCCL 3 patch, generic BLAS/LAPACK.
- Build at nice 19 with six jobs (`CMAKE_BUILD_PARALLEL_LEVEL`; MAKEFLAGS
  alone does not bound ninja).

## Sources and checksums

| Artifact | Identity | sha256 |
|---|---|---|
| cuquantum-linux-x86_64-26.09.0.8_cuda13-archive.tar.xz | vendor redist manifest redistrib_26.09.0.json | 92ecbba2b5783db20a966aa67e24206501eef3907ec09dd51cfb4753aea65731 |
| qiskit-aer-0.17.2.tar.gz | GitHub tag 0.17.2 (b2sum equals the PKGBUILD's) | 0231c74ae23d7dcaef664c39e57f800ee5174f73821a60f328ca3fe542266950 |
| nlohmann-json-3.10.2.tar.gz | GitHub tag v3.10.2 | 081ed0f9f89805c2d96335c3acfa993b39a0a5b4b4cef7edb68dd2210a13458c |
| custatevec_cu13-1.15.0 wheel | PyPI, headers inspected only | b129d32ee3a0104ba1c3a70f934d143ed99003dd24997278bdd57729d338b028 |
| cutensornet_cu13-2.14.0 wheel | PyPI, headers inspected only | 3e84b020f203fedf7e3baff8c0a37ebcfd41afe211103f6c200c5bd6c6a34f24 |
| qiskit_aer_gpu_cu11-0.17.2 cp313 wheel | PyPI, metadata and ELF read only | 2684a4bf8dc719157ba24046a22d749842abdfe1a9f30a3d9b47b732aedf2892 |
| cuquantum-26.09.0.8-1-x86_64.pkg.tar.zst | built here | 01e90ced7ae9a155e51cfdfd0bd577f5241de593fe071cc76a06041dda22a22c |
| python-qiskit-aer-cuda-0.17.2-2-x86_64.pkg.tar.zst | built here | 4418c8fa18b6dbbe8f41aaf67164f78e7b97b0f7223db8787bf0d3850f1b37fc |

Toolchain: cmake 4.4.4, ninja 1.13.2, nvcc 13.4.92, GCC 16.2.1, pybind11
3.1.0, scikit-build 0.19.1, Python 3.14.7. Recipes: `recipes/` beside this
note (live copies in ~/Github/PKGBUILDs/cuquantum and
~/Github/PKGBUILDs/python-qiskit-aer-cuda). The module links
libblis-mt.so.5 and libflame.so (AOCL), libcustatevec.so.1,
libcutensornet.so.2, and no libopenblas.

## Verification on the extracted package

Probe: `probe_custatevec.py` in this directory, run with PYTHONPATH on the
extracted site-packages and LD_LIBRARY_PATH on the extracted cuquantum
libraries; `qiskit_aer.__file__` pointed into the extracted tree.

- `import qiskit, qiskit_ibm_runtime, qiskit_aer` succeeds.
- Installed Aer reproduces the failure above. The rebuilt module runs
  `cuStateVec_enable=True` with `metadata.cuStateVec_enable` true, and
  `CUSTATEVEC_LOG_LEVEL=5` logs 75079 calls (ApplyMatrix, ApplyGeneralized
  PermutationMatrix, Abs2Sum) for a 20-qubit run; the plain GPU run logs none.
- CPU seeded counts (noisy statevector, density_matrix, matrix_product_state,
  an if_else circuit, an ideal 12-qubit MPS circuit) have the same sha256
  digests as the installed Aer, in two repeated runs, for the OpenBLAS-linked
  and the AOCL-linked build. Repository gates `core-record-check-01` (`tests/test_cli_record_checks.py`) (seeded probe counts),
  core-109, core-110, core-111 and the snapshot_laws gate core-302 pass on it.
- GPU counts with and without cuStateVec have equal digests (noisy 20 and 26
  qubits, ideal, 1-qubit if_else).

Timing, noisy depolarizing statevector trajectories of a depth-8 random
circuit, RTX 4070 Ti, device load average 42 to 46 from other jobs (a
nvidia-smi compute-apps listing showed only desktop processes), two runs each:

| Qubits | Shots | GPU plain ms/shot | GPU cuStateVec ms/shot | CPU ms/shot |
|---|---|---|---|---|
| 20 | 256 | 7.98, 7.85 | 6.23, 6.36 | 82.6 (64 shots) |
| 26 | 16 | 564.9, 566.4 | 479.7, 486.1 | not run |

cuStateVec is 1.25x faster at 20 qubits and 1.18x at 26. A 1-qubit if_else
circuit costs 0.035 and 0.078 ms/shot with cuStateVec against 0.017 and 0.035
without, so tiny circuits pay a fixed overhead. The 7-qubit N=21 two-round
circuit with feed-forward, run alone through the probe's
`gpu_statevector_custatevec` configuration, ran 1859 shots at 39.8 ms/shot under that load;
its plain-GPU counterpart is not measured.

## Verification on the installed package

With both packages installed by `pacman -U`, `noise_simulator(snapshot,
"GPU", method="statevector", custatevec=True)` on a 4-qubit GHZ circuit under
the ibm_kingston snapshot's noise reports `metadata.cuStateVec_enable` true,
and its 2000 seeded shots equal the `custatevec=False` counts outcome for
outcome; `custatevec=True` with `batched_shots=True` raises ValueError. The
seeded-count gates core-109, core-110, core-111, core-273, `core-record-check-01`,
core-287, core-288, core-302, core-304, core-311 and core-313 pass under
`GOROROBA_AER_DEVICE=CPU` on the AOCL-linked module.

## Findings outside the goal

- `method="tensor_network", device="GPU"` now runs (the installed build
  rejects it) but `cutensornetContractionOptimize` returned
  CUTENSORNET_STATUS_INTERNAL_ERROR on about every second run of an
  8-qubit, 4096-shot circuit. Treat tensor_network as unqualified.
- `cuStateVec_enable` with `batched_shots_gpu` reports `cuStateVec_enable`
  False in the result metadata, so `noise_simulator(custatevec=True,
  batched_shots=True)` raises.
- The CPU recipe python-qiskit-aer in ~/Github/PKGBUILDs links libopenblas.so.0
  the same way whenever openblas is installed; the BLAS patch in the cuda
  recipe applies to it unchanged.
- The 0.17.2-2 module has no openblas dependent, so openblas is orphaned
  unless another package needs it.

## Kaggle

The qiskit-aer-gpu-cu11 0.17.2 wheel lists libcustatevec.so.1 and
libcutensornet.so.2 as NEEDED, with RPATH `$ORIGIN/../../cuquantum/lib`, and
requires `cuquantum-cu11>=23.3.0,<24.11.0` (24.8.0, custatevec-cu11
1.6.0.post1, cutensornet-cu11 2.5.0). Kernels that pip-install with
dependencies therefore already carry the library; the retained T4 probe
imported the wheel and ran. Cubins cover sm_70 through sm_87 (T4 is sm_75).
No retained run sets `cuStateVec_enable`, so the T4 path is unmeasured.
`KERNEL_PINS` pins `cuquantum-cu11==24.8.0` and `cutensor-cu11==2.2.0`, and
the kernel reports the five cuQuantum-chain wheel versions in
`environment.json`. `calibration_snapshot.noise_simulator(...,
custatevec=True)` sets the option, and `scripts/aer_gpu_probe.py` carries the
`gpu_statevector_custatevec` configuration.
`docs/notes/kaggle/custatevec.md` holds the wheel chain, the T4 push command
and how to read its result.

## Build and install

```sh
cd ~/Github/PKGBUILDs
SUDO_ASKPASS=/usr/bin/unified-askpass sudo -A pacman -U \
  cuquantum/cuquantum-26.09.0.8-1-x86_64.pkg.tar.zst \
  python-qiskit-aer-cuda/python-qiskit-aer-cuda-0.17.2-2-x86_64.pkg.tar.zst
"$PYTHON" -c "import qiskit, qiskit_ibm_runtime, qiskit_aer; from qiskit_aer import AerSimulator; print(AerSimulator(method='statevector', device='GPU', cuStateVec_enable=True).available_devices())"
```

A rebuild runs `nice -n 19 makepkg -s --nocheck` in
~/Github/PKGBUILDs/python-qiskit-aer-cuda with the cuquantum package
installed; before that package is installed, the build takes
`CUQUANTUM_ROOT=$HOME/Github/PKGBUILDs/cuquantum/pkg/cuquantum/usr
AER_BUILD_JOBS=6 nice -n 19 makepkg -fC --nodeps --nocheck`.
