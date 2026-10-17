# Handoff: cuStateVec in the host Aer build

Status: both packages built and verified from extracted trees; neither installed.
No makepkg run is active.

## Root cause

The installed python-qiskit-aer-cuda 0.17.2-1 has no AER_CUSTATEVEC code path
(no libcustatevec in NEEDED; the "does not support cuStateVec" string is
compiled in). Its recipe is not retained anywhere. Aer enables cuStateVec only
with AER_THRUST_BACKEND=CUDA, AER_ENABLE_CUQUANTUM=ON and a CUQUANTUM_ROOT.
Arch has no cuquantum package; the build needs cuquantum 26.09.0.8 for CUDA 13
(libcustatevec 1.15.0, libcutensornet 2.14.0) plus cutensor 2.8.1 (installed).
Aer 0.17.2 also needs three source-level changes for CUDA 13.4: C++20 (CCCL 3
needs C++17, fmt 12 under nvcc needs C++20), a replacement for removed
thrust::unary_function, and a CMake edit so BLAS/LAPACK come from the AOCL
virtuals instead of libopenblas. Details: custatevec.md.

## Recipes and artifacts

- ~/Github/PKGBUILDs/cuquantum/PKGBUILD and
  cuquantum-26.09.0.8-1-x86_64.pkg.tar.zst
  (sha256 01e90ced7ae9a155e51cfdfd0bd577f5241de593fe071cc76a06041dda22a22c)
- ~/Github/PKGBUILDs/python-qiskit-aer-cuda/PKGBUILD, aer-cccl3-unary-function.patch
  and python-qiskit-aer-cuda-0.17.2-2-x86_64.pkg.tar.zst
  (sha256 4418c8fa18b6dbbe8f41aaf67164f78e7b97b0f7223db8787bf0d3850f1b37fc)
- Copies of both recipes and the patch: recipes/ in this directory.
- Rebuild before the cuquantum package is installed:
  `CUQUANTUM_ROOT=$HOME/Github/PKGBUILDs/cuquantum/pkg/cuquantum/usr AER_BUILD_JOBS=6 nice -n 19 makepkg -fC --nodeps --nocheck`
  (after install, plain `nice -n 19 makepkg -s --nocheck`).

## Verification (extracted package, not installed)

cuStateVec runs on the 4070 Ti (metadata true, 75079 logged API calls); CPU
seeded-count digests equal the installed Aer's; gates core-279, 109, 110, 111,
302 pass; cuStateVec is 1.25x (20 qubits) and 1.18x (26 qubits) faster than
the plain GPU statevector on noisy trajectories, measured under a device load
average of 42 to 46. Not run: CPU at 26 qubits, the full aer_gpu_probe sweep,
the plain-GPU row of the 7-qubit dynamic circuit, a rebuild with the final
PKGBUILD from a clean tree on a quiet host. method="tensor_network" is flaky
(CUTENSORNET_STATUS_INTERNAL_ERROR about every second run on one circuit).

## Next commands

```sh
cd ~/Github/PKGBUILDs
SUDO_ASKPASS=/usr/bin/unified-askpass sudo -A pacman -U \
  cuquantum/cuquantum-26.09.0.8-1-x86_64.pkg.tar.zst \
  python-qiskit-aer-cuda/python-qiskit-aer-cuda-0.17.2-2-x86_64.pkg.tar.zst
python3 -c "import qiskit, qiskit_ibm_runtime, qiskit_aer"
```

Then rerun the GPU benchmarks against the installed package, and optionally
remove the orphaned openblas.

## Kaggle (cu11)

The qiskit-aer-gpu-cu11 0.17.2 wheel already links libcustatevec.so.1 through
its cuquantum-cu11 dependency (24.8.0, sm_75 cubins present), so the T4 kernel
has the library; no retained run enabled cuStateVec_enable. The branch pins
cuquantum-cu11==24.8.0 in KERNEL_PINS, records the three package versions, and
adds `--only ... gpu_statevector_custatevec` to scripts/aer_gpu_probe.py. The
push command (not run) is in docs/notes/kaggle/substrates.md.
