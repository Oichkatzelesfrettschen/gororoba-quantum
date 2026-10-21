# Python stack on the build host

requirements.txt and
ci/requirements-ci.txt pin what CI runs; the build host runs Arch packages
at those versions, except the linters.

| Arch package | Pin it carries |
|---|---|
| python-qiskit | qiskit 2.5.2 |
| python-qiskit-ibm-runtime | qiskit-ibm-runtime 0.50.0 |
| python-qiskit-aer-cuda (provides python-qiskit-aer) | qiskit-aer 0.17.2, pkgrel 2: CUDA Thrust backend for sm_89 with cuQuantum, so `AerSimulator(device="GPU", cuStateVec_enable=True)` runs |
| cuquantum | cuquantum 26.09.0.8 for CUDA 13, repackaged from the vendor archive: libcustatevec.so.1 1.15.0 and libcutensornet.so.2 2.14.0, the two libraries python-qiskit-aer-cuda 0.17.2-2 links |
| cutensor | cutensor 2.8.1.0, the tensor library libcutensornet.so.2 loads |
| cuda | cuda 13.4.2 (nvcc 13.4.92): the toolkit both packages build against and the libcublas and libcusolver the module loads from /opt/cuda/lib64 |
| python-samplomatic | samplomatic 0.21.0, the runtime 0.50 floor |
| python-ibm-quantum-schemas | ibm-quantum-schemas 0.12.20260921, the runtime 0.50 floor |
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
python-qiskit-ibm-runtime. Those PKGBUILDs replace `blas-openblas` with the
`blas` and `lapack` virtuals that the installed AMD AOCL libraries provide,
which leaves AOCL in place; a package without a local PKGBUILD comes from
the distribution repositories through pacman or paru. python-qiskit-experiments
has a local PKGBUILD over the PyPI sdist: the AUR builds the GitHub tag
archive, which lacks the randomized-benchmarking `.npz` tables, so
`qiskit_experiments.library` fails to import. After a rebuild,
`"$PYTHON" -c "import qiskit, qiskit_ibm_runtime, qiskit_aer"` and a
submit-free dry run confirm the stack. python-qiskit-aer-cuda builds against
the cuquantum package of the same directory tree and installs in one
`pacman -U` with it; its PKGBUILD links Aer's BLAS and LAPACK calls to the
AOCL providers and builds the module as C++20, which CUDA 13's CCCL 3
headers and fmt 12 require. `readelf -d` on
`qiskit_aer/backends/controller_wrappers.cpython-314-x86_64-linux-gnu.so`
lists libcustatevec.so.1 and libcutensornet.so.2 among its NEEDED entries;
a module without them raises `Simulation device "GPU" does not support
cuStateVec on this system` on `cuStateVec_enable=True`.
`docs/notes/build_host/custatevec.md` holds the requirement list, the build
and install commands and the probe results. A Kaggle kernel installs qiskit 2.6.0,
qiskit-ibm-runtime 0.50.0 (its fake backends, such as FakeFez, need no
account) and qiskit-aer-gpu-cu11 0.17.2 (the CUDA 12 `qiskit-aer-gpu` wheel
stops at 0.15.1) over the Kaggle image's numpy and scipy, records every
version in `environment.json`, and holds no IBM credential
(`kaggle_kernel/AGENTS.md`).