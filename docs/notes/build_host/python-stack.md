# Python stack on the build host

requirements.txt and
ci/requirements-ci.txt pin what CI runs. The build host runs Arch packages
at those versions, except for the linters and for the Qiskit core: the host carries
qiskit 2.6.1, qiskit-ibm-runtime 0.51.0 and qiskit-aer 0.18.2 ahead of the
requirements.txt pins of qiskit 2.6.0 and runtime 0.50.0 until the pin bump lands.

| Arch package | Pin it carries |
|---|---|
| python-qiskit | qiskit 2.6.1, packaged without `check()`: its circuit-library tests fail on an mpmath DeprecationWarning raised inside `assertWarns`, and one Aer test fails on the provider name collision of [qiskit-aer.md](../qiskit-packages/qiskit-aer.md) |
| python-qiskit-ibm-runtime | qiskit-ibm-runtime 0.51.0; `check()` passes against qiskit 2.6.1 (2049 passed, 7 skipped) |
| python-qiskit-aer-cuda (provides python-qiskit-aer) | qiskit-aer 0.18.2, pkgrel 1: CUDA Thrust backend for sm_89 with cuQuantum, so `AerSimulator(device="GPU", cuStateVec_enable=True)` runs |
| cuquantum | cuquantum 26.09.0.8 for CUDA 13, repackaged from the vendor archive: libcustatevec.so.1 1.15.0 and libcutensornet.so.2 2.14.0, the two libraries python-qiskit-aer-cuda 0.18.2-1 links |
| cutensor | cutensor 2.8.1.0, the tensor library libcutensornet.so.2 loads |
| cuda | cuda 13.4.3 (nvcc 13.4.92): the toolkit both packages build against and the libcublas and libcusolver the module loads from /opt/cuda/lib64 |
| python-samplomatic | samplomatic 0.21.0, the runtime 0.50 floor |
| python-ibm-quantum-schemas | ibm-quantum-schemas 0.13.20261016, the runtime 0.51 floor |
| python-numpy, python-scipy | numpy 2.5.4, scipy 1.18.1 |
| python-rustworkx, python-sympy | rustworkx 0.18.1, sympy 1.14.0 |
| python-matplotlib | matplotlib 3.11.2 |
| python-stim, python-mthree (with python-runningman), python-qiskit-experiments, python-quimb, python-cotengra, python-pyzx, python-galois | stim 1.16.0, mthree 3.0.0, qiskit-experiments 0.14.2, quimb 1.15.0, cotengra 0.8.2, pyzx 0.10.7, galois 0.4.11: the `quantum-tools` group a Kaggle kernel installs with `push --with quantum-tools` (`scripts/kaggle_run.py` PIN_GROUPS) |
| python-flint | python-flint 0.9.0 (CI pin): exact rank modulo p (`nmod_mat`) and RREF null spaces (`fmpq_mat`) in `scripts/exact_rank.py`, and SymPy 1.14.0's ground types, which it selects when the version is on SymPy's tested list |
| iqm-resonance-stack | IQM OS 4.7 client stack (iqm-client 36.0.0, qiskit 2.1.2, cirq-core 1.7.0, qrisp 0.9.10) as a separate Python 3.13 environment under /opt/iqm-resonance-stack, interpreter `iqm-python` (docs/notes/iqm/README.md) |
| python-pytorch-opt-cuda, python-pandas | torch and pandas for python-octonion and python-cayley-dickson only |
| python-ruff, mypy | ruff 0.17.0 and mypy 2.3.1, behind the CI pins ruff 0.17.1 and mypy 2.4.0 (a `~/.local/bin` install of ruff 0.14.11 and mypy 1.19.1 precedes them on PATH); the lint gates run the pins through `ci/pinned_tool.py` and uv |

A broken or missing package is rebuilt and reinstalled from its PKGBUILD in
`~/Github/PKGBUILDs` with `makepkg -si --nocheck` in the package
directory: python-qiskit-aer and python-samplomatic before
python-qiskit-ibm-runtime. Those PKGBUILDs link the system OpenBLAS
(`blas-openblas` 0.3.34), which provides the `blas` and `lapack` virtuals;
a package without a local PKGBUILD comes from
the distribution repositories through pacman or paru. python-qiskit-experiments
has a local PKGBUILD over the PyPI sdist: the AUR builds the GitHub tag
archive, which lacks the randomized-benchmarking `.npz` tables, so
`qiskit_experiments.library` fails to import. After a rebuild,
`"$PYTHON" -c "import qiskit, qiskit_ibm_runtime, qiskit_aer"` and a
submit-free dry run confirm the stack. python-qiskit-aer-cuda builds against
the cuquantum package of the same directory tree and installs in one
`pacman -U` with it; its PKGBUILD links Aer's BLAS and LAPACK calls to
libopenblas.so.0 and builds the module as C++20, which CUDA 13's CCCL 3
headers and fmt 12 require. `readelf -d` on
`qiskit_aer/backends/controller_wrappers.cpython-314-x86_64-linux-gnu.so`
lists libopenblas.so.0, libcustatevec.so.1, libcutensornet.so.2 and libgomp.so.1 among its NEEDED entries;
a module without them raises `Simulation device "GPU" does not support
cuStateVec on this system` on `cuStateVec_enable=True`.
Aer's own GPU code runs Thrust kernels and calls no cuBLAS. It links the
CUDA runtime statically, so no libcudart.so loads. cuBLAS, cuBLASLt and
cuSOLVER load as dependencies of libcustatevec.so.1 (libcublas.so.13,
libcublasLt.so.13) and libcutensornet.so.2 (libcublas.so.13,
libcusolver.so.12, libcutensor.so.2). They resolve to the cuda and cutensor
packages and do work only inside cuStateVec and cuTensorNet calls. The pip
`nvidia/*/lib` rpaths that Aer's CMakeLists.txt writes match no directory on
the host. No pip-installed CUDA or BLAS wheel sits in the system
site-packages, and python-cupy 14.2.0 loads cuBLAS from the same cuda package.
NumPy links libcblas.so.3, and SciPy links libblas.so.3 and liblapack.so.3;
all three resolve to libopenblas.so.0.3. The user venvs and `/opt` stacks take PyPI
wheels instead, with their own bundled OpenBLAS (`numpy.libs`,
`qiskit_aer.libs`, `scipy_openblas32`) and a CPU-only Aer, so GPU simulation
runs on the system interpreter alone. The cuQuantum Python bindings
(`cuquantum-python`) are not installed, and no repository code imports them.
`docs/notes/build_host/custatevec.md` holds the requirement list, the build
and install commands and the probe results. A Kaggle kernel installs qiskit 2.6.0,
qiskit-ibm-runtime 0.50.0 (its fake backends, such as FakeFez, need no
account) and qiskit-aer-gpu-cu11 0.17.2 (the CUDA 12 `qiskit-aer-gpu` wheel
stops at 0.15.1) over the Kaggle image's numpy and scipy, records every
version in `environment.json`, and holds no IBM credential
(`kaggle_kernel/AGENTS.md`).