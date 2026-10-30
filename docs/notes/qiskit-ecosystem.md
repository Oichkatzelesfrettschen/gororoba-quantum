# Qiskit ecosystem audit

The host-installed set beyond the pinned core, with its install surfaces
and interconnections, is [qiskit-packages/README.md](qiskit-packages/README.md);
the version columns below record the 2026-10-16 survey.

Scope: Python packages that bear on noise simulation of circuits up to 14
qubits against IBM Heron r2 calibration, dynamic circuits, readout
mitigation, characterization, transpilation, algebra circuits and sampling
statistics. The pinned core is qiskit 2.5.2, qiskit-ibm-runtime 0.50.0,
qiskit-aer 0.17.2 (host `python-qiskit-aer-cuda`; Kaggle GPU kernels
`qiskit-aer-gpu-cu11`, CPU and TPU kernels `qiskit-aer`), samplomatic 0.21.0
and ibm-quantum-schemas
0.12.20260921. The host runs Python 3.14 (Arch); a Kaggle kernel runs Python
3.13.15 with numpy 2.1.3 and scipy 1.16.3.

Evidence sources and dates. PyPI JSON (`pypi.org/pypi/NAME/json`) and the
GitHub REST API (repository, releases, tags, archived flag) were read on
2026-10-16. The AUR RPC (`/rpc/v5/info`) and `pacman -Q/-Si` give Arch
availability. The conda-forge column comes from the anaconda.org package API
(HTTP 404 means no package of that exact name). Host versions come from
`importlib.metadata`. Kaggle state comes from `scripts/kaggle_run.py`
(`KERNEL_PINS`, `CPU_KERNEL_PINS`, `PIN_GROUPS`) and the retained
`environment.json`, `pin_groups.json` and `submission.json` records of kernel
runs. Admission of the pinned
core is computed by evaluating each `requires_dist` specifier against the pin
(prereleases allowed); an extra-only requirement is ignored.

## Findings that change a decision

1. `qiskit-ibm-runtime==0.50.0` hard-requires
   `ibm-quantum-schemas<1,>=0.12.20260921`, `samplomatic>=0.21.0` and
   `qiskit-mitigation>=0.1.1`, and ibm-quantum-schemas 0.13.20261016 was
   uploaded on 2026-10-16, so an unpinned kernel resolves a newer schema
   release than the host's 0.12.20260921. `PIN_GROUPS["quantum-tools"]` pins
   all three at the host versions (`samplomatic==0.21.0`,
   `ibm-quantum-schemas==0.12.20260921`, `qiskit-mitigation==0.1.1`), so a
   group kernel imports the host's releases.
2. `qiskit.qasm3.loads` needs `qiskit-qasm3-import`, which needs `openqasm3`
   with its antlr4 parser. The group pins `qiskit-qasm3-import==0.6.0`,
   `openqasm3==1.0.1` and `antlr4-python3-runtime==4.13.2`, so a kernel
   pushed `--with quantum-tools` parses OpenQASM 3.
3. `environment.json` lists a fixed package set (qiskit, the Aer build,
   numpy, scipy, sympy, pandas, torch and the algebra packages), and a kernel
   pushed `--with GROUP` also writes `pin_groups.json` with the installed
   version of every group member. The CPU kernel run
   `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` declared the group when it
   held twelve pins, and its `pin_groups.json` records all twelve at their
   versions. The seven pins added since (findings 1 and 2, plus
   `qiskit-addon-utils==0.4.0`) have not been installed on a kernel.
4. qiskit 2.6.0 was uploaded on 2026-10-16 (abi3 manylinux wheel). Runtime
   0.50.0 (`qiskit<3,>=2.3.0`), aer 0.17.2, samplomatic, mitigation,
   experiments, mthree, addon-utils and schemas all admit it. qiskit-fermions
   (`qiskit~=2.5.0`) does not. No Arch package exists yet; the pin stays at
   2.5.2.
5. `qiskit-ibm-transpiler` 0.18.0 cannot join the core on either substrate:
   `requires_python` is `<3.14` (host is 3.14), and it requires
   `qiskit-serverless~=0.30.0`, whose 0.30.1 requires
   `qiskit-ibm-runtime<0.46.0` and `networkx==2.8.5`. Installing it moves
   runtime from 0.50.0 to below 0.46.
6. `qiskit-serverless` 0.37.0 and `qiskit-ibm-catalog` 0.21.0 admit runtime
   0.50.0 (`<0.51.0,>=0.50.0`) but require `numpy>=2.2.6`, which conflicts
   with the Kaggle image's numpy 2.1.3.
7. `mthree` 3.0.0 ships wheels for cp310 to cp312 only (no cp313 or cp314).
   The host package is built locally; a Kaggle cp313 kernel compiles the
   sdist (`cython>=3.0.10` and a C++ toolchain).
8. Host import health: every installed ecosystem package imports. `pip check`
   reports one ecosystem-relevant defect, `quimb 1.15.0 requires
   cytoolz>=0.8.0, but cytoolz 0.0.1 is installed`: the Arch package
   `python-cytoolz 1.1.0-2.1` ships a dist-info that reads 0.0.1.
   `quimb.tensor` imports and runs regardless.

## Table A: four-way version comparison

Columns: Host = Arch package and importlib version; Kaggle = how a kernel
gets it; PyPI = latest release and first upload date; Beyond PyPI =
GitHub-only or IBM-hosted releases, Arch repo or AUR, conda-forge.
"KP" is `KERNEL_PINS` (GPU kernels); "CP" is `CPU_KERNEL_PINS` (CPU and TPU
kernels); "QT" is the opt-in `quantum-tools` group
(`push --with quantum-tools`).

### Core

| Package | Host | Kaggle | PyPI | Beyond PyPI |
|---|---|---|---|---|
| qiskit | python-qiskit 1:2.5.2-1 / 2.5.2 | KP `qiskit==2.5.2` | 2.6.0 (2026-10-16) | GitHub release 2.6.0; AUR 1:2.5.2-1; conda-forge 2.5.2 |
| qiskit-aer | python-qiskit-aer-cuda 0.17.2-1 / 0.17.2 (devices CPU, GPU) | CP `==0.17.2` on CPU and TPU kernels | 0.17.2 (2025-09-17); cp313 and cp314 wheels | GitHub release 0.17.2; AUR python-qiskit-aer 0.17.2-3; local PKGBUILD; conda-forge 0.17.2 |
| qiskit-aer-gpu-cu11 | none | KP `==0.17.2` on GPU kernels | 0.17.2 (2025-09-17); cp313 wheel only | none |
| qiskit-aer-gpu | none | not used (CUDA 12 build stops at 0.15.1, no Python 3.13 wheel) | 0.15.1 (2024-09-13); no cp313 or cp314 wheel | none |
| qiskit-ibm-runtime | python-qiskit-ibm-runtime 0.50.0-1 / 0.50.0 | QT `==0.50.0` | 0.50.0 (2026-09-24) | GitHub release 0.50.0; AUR 0.50.0-1; local PKGBUILD; conda-forge 0.50.0 |
| samplomatic | python-samplomatic 0.21.0-1 / 0.21.0 | QT `==0.21.0` | 0.21.0 (2026-08-25) | GitHub release 0.21.0; AUR 0.21.0-1; local PKGBUILD; conda-forge 0.21.0 |
| ibm-quantum-schemas | python-ibm-quantum-schemas 0.12.20260921-1 / 0.12.20260921 | QT `==0.12.20260921` | 0.13.20261016 (2026-10-16) | GitHub release 0.13.20261016; AUR 0.12.20260921-1 |
| qiskit-mitigation | python-qiskit-mitigation 0.1.1-1 / 0.1.1 | QT `==0.1.1` | 0.1.1 (2026-09-24) | GitHub release 0.1.1 with a wheel asset; AUR 0.1.1-1; conda-forge 0.1.1 |
| qiskit-qasm3-import | python-qiskit-qasm3-import 0.6.0-1 / 0.6.0 | QT `==0.6.0` | 0.6.0 (2025-06-10) | GitHub latest release is v0.5.0 (2024-06-18), behind PyPI; AUR 0.6.0-1; conda-forge 0.6.0 |
| openqasm3 | python-openqasm3 1.0.1-1 / 1.0.1 | QT `==1.0.1`, with QT `antlr4-python3-runtime==4.13.2` | 1.0.1 (2025-02-19) | AUR 1.0.1-1; conda-forge 1.0.1 |
| rustworkx | python-rustworkx 0.18.1-1 / 0.18.1 | image-supplied (not recorded) | 0.18.1 (2026-07-30); cp314 and abi3 wheels | AUR 0.18.1-1; conda-forge 0.18.1 |

### Characterization, mitigation, simulation tools

| Package | Host | Kaggle | PyPI | Beyond PyPI |
|---|---|---|---|---|
| qiskit-experiments | python-qiskit-experiments 0.14.2-2 (local PKGBUILD) / 0.14.2 | QT `==0.14.2` | 0.14.2 (2026-08-25) | AUR 0.14.2-1 (lacked .npz data; replaced by the local PKGBUILD); conda-forge 0.14.2 |
| mthree | python-mthree 3.0.0-1 (local PKGBUILD) / 3.0.0 | QT `==3.0.0` (sdist build on cp313) | 3.0.0 (2025-03-27) | GitHub release v3.0 (Qiskit/qiskit-addon-mthree); no AUR package; not on conda-forge. PyPI name `qiskit-addon-mthree` does not exist |
| runningman | python-runningman 2.3.0-1 (local PKGBUILD) / 2.3.0 | QT `==2.3.0` | 2.3.0 (2025-03-18); sdist only | no AUR package |
| stim | python-stim 1.16.0-1 (local PKGBUILD) / 1.16.0 | QT `==1.16.0` | 1.16.0 (2026-05-22); cp313 and cp314 wheels | no AUR package; conda-forge lists 0.4.0 under the name `stim`, which does not track PyPI |
| pymatching | none | none | 2.4.0 (2026-05-22); cp313 and cp314 wheels | no AUR package; no conda-forge package under that name |
| sinter | none | none | 1.16.0 (2026-05-22); sdist only | no AUR package |
| quimb | python-quimb 1.15.0-1 / 1.15.0 | QT `==1.15.0` | 1.15.0 (2026-08-10) | AUR 1.15.0-1; conda-forge 1.15.0 |
| cotengra | python-cotengra 0.8.2-1 / 0.8.2 | QT `==0.8.2` | 0.8.2 (2026-06-22) | AUR 0.8.2-1; conda-forge 0.8.2 |
| autoray | python-autoray 0.11.0-1 / 0.11.0 | QT `==0.11.0` | 0.11.0 (2026-08-22) | AUR 0.11.0-1 |
| pyzx | python-pyzx 0.10.7-1 / 0.10.7 | QT `==0.10.7` | 0.10.7 (2026-10-01) | AUR 0.10.7-1; no conda-forge package |
| galois | python-galois 0.4.11-1 / 0.4.11 | QT `==0.4.11` | 0.4.11 (2026-05-02) | AUR 0.4.11-1; conda-forge 0.4.11 |
| lmfit | python-lmfit 1.3.4-1 / 1.3.4 | QT `==1.3.4` | 1.3.4 (2025-07-19) | AUR 1.3.4-1 |
| numba | python-numba 0.68.0-1.1 / 0.68.0 (Arch extra 0.68.0-1) | QT `==0.68.0` | 0.68.0 (2026-09-30); cp313 and cp314 wheels | Arch extra repository |

### IBM addon family (github.com/Qiskit)

| Package | Host | Kaggle | PyPI | Beyond PyPI |
|---|---|---|---|---|
| qiskit-addon-utils | python-qiskit-addon-utils 0.4.0-1 / 0.4.0 | QT `==0.4.0` | 0.4.0 (2026-07-15) | AUR 0.4.0-1; no conda-forge package |
| qiskit-addon-obp | none | none | 0.3.0 (2025-05-22) | AUR 0.3.0-1; no conda-forge package |
| qiskit-addon-mpf | none | none | 0.3.0 (2025-03-20) | AUR 0.3.0-1; no conda-forge package |
| qiskit-addon-aqc-tensor | none | none | 0.3.1 (2026-07-16) | no AUR package; no conda-forge package |
| qiskit-addon-cutting | none | none | 0.10.0 (2025-03-28) | AUR 0.10.0-1; no conda-forge package |
| qiskit-addon-sqd | none | none | 0.14.0 (2026-10-08) | GitHub release 0.14.0 with a wheel; no AUR package; conda-forge 0.14.0 |
| qiskit-addon-slc | none | none | 0.1.0 (2025-11-06) | no AUR package; no conda-forge package |
| qiskit-addon-pna | none | none | 0.2.0 (2025-11-13) | no AUR package; no conda-forge package |
| qiskit-addon-opt-mapper | none | none | 0.1.0 (2025-11-03) | no AUR package |
| pauli-prop | none | none | 0.2.1 (2026-08-20); abi3 wheel | GitHub release 0.2.1; no AUR package |
| qiskit-paulice | none | none | 0.2.1 (2026-06-25); abi3 wheel | GitHub release 0.2.1; no AUR package |
| qiskit-fermions | none | none | 0.2.0 (2026-09-11); abi3 wheel | GitHub release 0.2.0; no AUR package |
| qiskit-noise-learning | none | none | not on PyPI | GitHub only (Qiskit/qiskit-noise-learning, pushed 2026-10-16, no tag or release; version from `_version.py` at build) |
| qiskit-device-benchmarking | none | none | not on PyPI | GitHub only (qiskit-community/qiskit-device-benchmarking, pushed 2026-08-24, no tag or release) |
| qiskit-addon-sqd-hpc | none | none | not on PyPI | GitHub only (Qiskit/qiskit-addon-sqd-hpc, pushed 2026-10-12) |
| qiskit-addon-dice-solver | none | none | 0.0.0.dev0 placeholder (2024-09-10) | GitHub repository, no release |

### IBM cloud clients and transpiler services

| Package | Host | Kaggle | PyPI | Beyond PyPI |
|---|---|---|---|---|
| qiskit-ibm-transpiler | none | none | 0.18.0 (2026-03-10); cp310 to cp313 wheels | GitHub release 0.18.0; AUR 0.13.1-1 flagged out of date |
| qiskit-ibm-ai-local-transpiler | none | none | 0.5.5 (2025-12-01); cp313 and cp314 wheels | none |
| qiskit-ibm-catalog | none | none | 0.21.0 (2026-10-15) | GitHub release v0.21.0 |
| qiskit-serverless | none | none | 0.37.0 (2026-10-15) | GitHub release v0.37.0 with a Helm chart asset |
| qiskit-ibm-experiment | none | none | 0.4.8 (2024-09-05) | GitHub repository archived 2026-01-29 |
| qiskit-ibm-provider | none | none | 0.11.0 (2024-04-17) | GitHub repository archived |
| qiskit-gym | none | none | 0.4.2 (2026-10-15); cp313 and cp314 wheels | AUR 0.4.1-1 |
| qiskit-mcp-servers, qiskit-ibm-runtime-mcp-server, qiskit-ibm-transpiler-mcp-server, qiskit-code-assistant-mcp-server, qiskit-docs-mcp-server, qiskit-gym-mcp-server | none | none | 0.12.1, 0.6.2, 0.4.1, 0.4.0, 0.3.0, 0.4.2 (2026-04 to 2026-10) | github.com/Qiskit/mcp-servers |

### Community libraries

| Package | Host | Kaggle | PyPI | Beyond PyPI |
|---|---|---|---|---|
| qiskit-algorithms | none | none | 0.4.0 (2025-08-29) | AUR 0.4.0-2; conda-forge 0.4.0 |
| qiskit-machine-learning | none | none | 0.9.1 (2026-08-19) | AUR 0.9.1-1; conda-forge 0.9.1 |
| qiskit-optimization | none | none | 0.7.0 (2025-08-20) | GitHub repository archived (last push 2026-07-12); AUR 0.7.0-3; conda-forge 0.7.0 |
| qiskit-nature | none | none | 0.8.0 (2026-06-01) | AUR 0.8-1 |
| qiskit-finance | none | none | 0.4.1 (2024-02-29) | AUR 0.4.1-4 |
| qiskit-dynamics | none | none | 0.6.0 (2025-10-07) | GitHub repository archived; AUR 0.5.1-4; conda-forge 0.6.0 |

## Table B: compatibility, licensing and recommendation

Wheels: "pure" is a `py3-none-any` wheel; "cp313+cp314" lists binary wheels
for both interpreters; "abi3" is a stable-ABI wheel covering both. Admits
columns evaluate `requires_dist` against qiskit 2.5.2 and runtime 0.50.0;
"-" means the package does not require that distribution. "Moves core"
records whether installation forces a change of a pinned core package.
Recommendation vocabulary: both (host and Kaggle, exact pin), host only,
skip.

### Core and tools

| Package | requires_python | Wheels | qiskit 2.5.2 | runtime 0.50.0 | Moves core | License | Repo status | Recommendation and reason |
|---|---|---|---|---|---|---|---|---|
| qiskit | >=3.10 | abi3 | self | requires <3,>=2.3.0: yes | no | Apache-2.0 | active | both, 2.5.2 (hold below 2.6.0 until a host package and gates exist) |
| qiskit-aer | >=3.7 | cp313+cp314 | >=1.1.0: yes | - | no | Apache-2.0 | active | host (CUDA build); Kaggle CPU and TPU kernels, 0.17.2 |
| qiskit-aer-gpu-cu11 | >=3.7 | cp313 only | >=1.1.0: yes | - | no | Apache-2.0 | active | Kaggle GPU kernels only, 0.17.2; a Python 3.14 kernel would lose GPU Aer |
| qiskit-ibm-runtime | >=3.10 | pure | <3,>=2.3.0: yes | self | no | Apache-2.0 | active | both, 0.50.0; import for local option and fake-backend objects, never a service call in Kaggle |
| samplomatic | >=3.10 | pure | >=2.3.0: yes | requires >=0.21.0: yes | no | Apache-2.0 | active | both, 0.21.0 (QT pin) |
| ibm-quantum-schemas | >=3.10 | pure | <3.0.0,>=2.3.0: yes | requires <1,>=0.12.20260921: 0.13.20261016 also admitted | no | Apache-2.0 | active | both, 0.12.20260921 (QT pin, matches the host) |
| qiskit-mitigation | >=3.10 | pure | <3,>=2.3.0: yes | hard dependency of runtime | no | Apache-2.0 | active | both, 0.1.1 (QT pin) |
| qiskit-qasm3-import | none | pure | >=0.37.0: yes | - | no | Apache-2.0 | active (latest GitHub release lags PyPI) | both, 0.6.0 (QT pin) |
| openqasm3 | none | pure | - | - | no | Apache-2.0 | active | both, 1.0.1 (QT pin, with `antlr4-python3-runtime==4.13.2` for the `parser` extra) |
| rustworkx | >=3.10 | cp314+abi3 | requires >=0.15.0 | - | no | Apache-2.0 | active | both; Kaggle keeps the image copy, 0.18.1 on host |
| qiskit-experiments | >=3.10 | pure | >=1.3: yes | >=0.34.0: yes | no | Apache-2.0 | active | both, 0.14.2 (RB, readout-error and coherence experiments run on Aer) |
| mthree | >=3.9 | cp310 to cp312 only | >=1.0: yes | - | no | Apache-2.0 | active | both, 3.0.0 (matrix-free readout mitigation; `M3Mitigation` is the class name) |
| runningman | >=3.9 | sdist only | - | >=0.22: yes | no | Apache-2.0 | unverified | both, 2.3.0 (mthree dependency) |
| stim | >=3.6 | cp313+cp314 | - | - | no | Apache-2.0 | active | both, 1.16.0 (Clifford and stabilizer checks) |
| pymatching | >=3.8 | cp313+cp314 | - | - | no | Apache-2.0 | active | skip until a repetition-code decoding case exists |
| sinter | >=3.7 | sdist only | - | - | no | Apache-2.0 | active | skip, same reason as pymatching |
| quimb | >=3.11 | pure | - | - | no | Apache-2.0 | active | both, 1.15.0; needs scipy>=1.16.0 (Kaggle has 1.16.3, no margin) |
| cotengra | >=3.10 | pure | - | - | no | Apache-2.0 | active | both, 0.8.2 |
| autoray | >=3.11 | pure | - | - | no | Apache-2.0 | active | both, 0.11.0 |
| pyzx | >=3.10 | pure | extras only | - | no | Apache-2.0 | active | both, 0.10.7 |
| galois | >=3.7 | pure | - | - | no | MIT | active | both, 0.4.11 |
| lmfit | >=3.9 | pure | - | - | no | BSD-3-Clause | active | both, 1.3.4 (qiskit-experiments fits) |
| numba | >=3.10 | cp313+cp314 | - | - | numpy<2.6 | BSD | active | both, 0.68.0 |

### IBM addon family

| Package | requires_python | Wheels | qiskit 2.5.2 | runtime 0.50.0 | Moves core | License | Repo status | Recommendation and reason |
|---|---|---|---|---|---|---|---|---|
| qiskit-addon-utils 0.4.0 | >=3.10 | pure | <3,>=2.2: yes | - | no | Apache-2.0 | active | both, 0.4.0 (QT pin): circuit slicing and coupling-map helpers |
| qiskit-addon-obp 0.3.0 | >=3.9 | pure | <3,>=1.2: yes | >=0.27: yes | no | Apache-2.0 | active | skip: operator backpropagation targets observable estimation of Trotter circuits |
| qiskit-addon-mpf 0.3.0 | >=3.9 | pure | <3,>=1.2: yes | - | cvxpy | Apache-2.0 | active | skip: Trotter error reduction, pulls cvxpy (not installed) |
| qiskit-addon-aqc-tensor 0.3.1 | >=3.9 | pure | <3,>=1.3.0: yes | - | no | Apache-2.0 | active | skip: approximate quantum compilation with tensor networks; quimb and cotengra already cover contraction |
| qiskit-addon-cutting 0.10.0 | >=3.9 | pure | <3,>=1.3.1: yes | >=0.24.0: yes | no | Apache-2.0 | active | skip: circuits stay within 14 qubits, so wire cutting has no use |
| qiskit-addon-sqd 0.14.0 | >=3.10 | pure | <3,>=2.0: yes | - | jax, jaxlib, pyscf | Apache-2.0 | active | skip: chemistry configuration recovery, pulls pyscf (not installed) |
| qiskit-addon-slc 0.1.0 | >=3.10 | pure | <3,>=2.2: yes | - | pauli-prop~=0.1.0, pyscf | Apache-2.0 | active | skip: PEC overhead reduction; pins pauli-prop below 0.2 |
| qiskit-addon-pna 0.2.0 | >=3.10 | pure | <3,>=2.1.2: yes | - | no | Apache-2.0 | active | skip: global-noise-channel mitigation of observables |
| qiskit-addon-opt-mapper 0.1.0 | >=3.10 | pure | <3: yes | - | cvxpy, docplex | Apache-2.0 | active | skip: optimization modeling |
| pauli-prop 0.2.1 | >=3.10 | abi3 | <3,>=2.1.2: yes | - | no | Apache-2.0 | active | skip: Pauli propagation for large observables |
| qiskit-paulice 0.2.1 | >=3.10 | abi3 | <3,>=2.1.2: yes | - | no | Apache-2.0 | active | skip: spacetime Pauli checks target error detection at scale |
| qiskit-fermions 0.2.0 | >=3.10 | abi3 | ~=2.5.0: yes | - | blocks qiskit 2.6 | Apache-2.0 | active | skip: fermionic systems |
| qiskit-noise-learning | >=3.11 | GitHub source only | >=2.5.0,<3: yes | - (dev extra >=0.50) | xarray>=2025.7 | Apache-2.0 | active (pushed daily) | host plus Kaggle candidate via commit-pinned source: randomization-based Pauli noise characterization against the Aer replay; needs samplomatic>=0.21, numpy>=2 |
| qiskit-device-benchmarking | setup.py, no floor | GitHub source only | >=1.0: yes | >=0.28: yes | pandas, networkx | Apache-2.0 | active | host only: benchmarks that submit to IBM backends; needs an IBM credential |
| qiskit-addon-sqd-hpc, qiskit-addon-dice-solver | - | GitHub only or placeholder | - | - | - | - | active | skip: chemistry HPC solvers |

### IBM cloud clients, community libraries and out-of-scope packages

| Package | requires_python | Wheels | qiskit 2.5.2 | runtime 0.50.0 | Moves core | License | Repo status | Recommendation and reason |
|---|---|---|---|---|---|---|---|---|
| qiskit-ibm-transpiler 0.18.0 | <3.14,>=3.10 | cp310 to cp313 | <3,>=1.4.2: yes | indirect: serverless~=0.30 needs runtime<0.46 | yes: drops runtime to <0.46, networkx==2.8.5 | Apache-2.0 | active | skip: cloud AI passes (credential) and a hard conflict with the pin |
| qiskit-ibm-ai-local-transpiler 0.5.5 | >=3.10 | cp313+cp314 | >=1.4.2: yes | >=0.37.0: yes | networkx==2.8.5 | unstated | active | skip: no consumer in the repository; pins an old networkx |
| qiskit-ibm-catalog 0.21.0 | >=3.9 | pure | via serverless | via serverless: yes | numpy>=2.2.6 | Apache-2.0 | active | host only, installed: Qiskit Functions client, cloud only; never on Kaggle ([qiskit-functions.md](qiskit-packages/qiskit-functions.md)) |
| qiskit-serverless 0.37.0 | >=3.10 | pure | <3,>=2.2: yes | <0.51.0,>=0.50.0: yes | numpy>=2.2.6; 15 exact or tight pins | Apache-2.0 | active | host only, installed with the runtime cap and image pins relaxed; exceeds Kaggle numpy ([qiskit-functions.md](qiskit-packages/qiskit-functions.md)) |
| qiskit-ibm-experiment 0.4.8 | >=3.8 | pure | >=0.32: yes | - | no | Apache-2.0 | archived | skip: archived |
| qiskit-ibm-provider 0.11.0 | >=3.8 | pure | >=0.45.0: yes | - | no | Apache-2.0 | archived | skip: replaced by runtime |
| qiskit-gym 0.4.2 | >=3.10 | cp313+cp314 | <3,>=2.1: yes | - | twisterl, gymnasium | Apache-2.0 | active | skip: reinforcement-learning synthesis |
| mcp-server family | <3.15 or <3.14, >=3.10 | pure | varies | runtime server: >=0.40.0 | no | Apache-2.0 | active | skip: agent tooling, no consumer in the gates |
| qiskit-algorithms 0.4.0 | >=3.9 | pure | >=1.0: yes | - | no | Apache-2.0 | active | host only, optional: phase and amplitude estimation references for algebra-circuit cross-checks; no current consumer |
| qiskit-machine-learning 0.9.1 | >=3.10 | pure | >=2.0: yes | - | numpy>=2.0 | Apache-2.0 | active | skip |
| qiskit-optimization 0.7.0 | >=3.9 | pure | <3,>=1.1: yes | - | no | Apache-2.0 | archived | skip: archived |
| qiskit-nature 0.8.0 | >=3.10 | pure | <3.0,>=1.4: yes | - | numpy>=2 | Apache-2.0 | active | skip: chemistry |
| qiskit-finance 0.4.1 | >=3.8 | pure | >=0.45: yes | - | no | Apache-2.0 | active | skip: finance |
| qiskit-dynamics 0.6.0 | >=3.10 | pure | <=1.3: no | - | blocks qiskit 2.5.2 | Apache-2.0 | archived | skip: requires qiskit<=1.3; pulse-level control was removed by IBM on 2025-02-03 |

Out of scope, one line each: qiskit-braket-provider, qiskit-ionq,
qiskit-superstaq and qiskit-aqt-provider (non-IBM hardware providers;
qiskit-aqt-provider 2.0.0 also requires `qiskit<=2.4.1`); qiskit-qir 0.5.0
(`qiskit<2.0`); qiskit-research (`qiskit==1.1.1`); circuit-knitting-toolbox
(`qiskit<2.0`, superseded by qiskit-addon-cutting); qiskit-transpiler-service
(`qiskit~=1.0`); pennylane-qiskit (`qiskit<=2.3.0`, `qiskit-ibm-runtime~=0.45.0`);
qiskit-metal (`numpy==1.24.2`); qiskit-cold-atom, qiskit-ignis, qiskit-aqua,
qiskit-ibmq-provider, qiskit-terra, qiskit-toqm, qiskit-honeywell-provider,
qiskit-quantinuum-provider, qiskit-rigetti (superseded, archived or Python
ceilings); mapomatic (layout search; sdist only, no `requires_python`);
qbraid, coheriq, benchpress (outside the IBM Heron workflow).

## Host import health

Imports ran with `python -I` from a neutral directory. All 20 packages
imported without error: qiskit, qiskit_aer, qiskit_ibm_runtime, samplomatic,
ibm_quantum_schemas, qiskit_qasm3_import, openqasm3, qiskit_experiments,
mthree, qiskit_mitigation, runningman, stim, quimb, cotengra, pyzx, galois,
rustworkx, lmfit, autoray, numba.

Functional probes beyond import:

| Probe | Result |
|---|---|
| `qiskit_experiments` 2-qubit StandardRB circuit generation and an Aer run (exercises the Clifford `.npz` data) | pass |
| `mthree.M3Mitigation.cals_from_system` and `apply_correction` on an Aer readout-error model | pass; `mthree.M3` does not exist in 3.0.0 |
| `qiskit.qasm3.loads` of a 2-qubit OpenQASM 3 program | pass |
| `stim` compile_sampler, `galois.GF(2**3)` product, `quimb.tensor`, `cotengra`, `pyzx`, `numba` imports | pass |
| `AerSimulator().available_devices()` | `('CPU', 'GPU')` |
| `pip check`, ecosystem lines | `quimb 1.15.0 has requirement cytoolz>=0.8.0, but you have cytoolz 0.0.1.` (Arch dist-info version defect, no runtime effect) |

Not run: any `QiskitRuntimeService` call (no credential is used by this
audit), Kaggle-side imports (no kernel was pushed), and PKGBUILD builds.

## IBM-specific Qiskit

A Kaggle kernel holds no IBM credential, so a package that opens an IBM
Cloud or Runtime session cannot function there and must never be called
from kernel code. Importing a package for its local data classes is allowed;
constructing a service or submitting a job is not.

| Package | Touches IBM Cloud or Runtime | Local computation | Kaggle rule |
|---|---|---|---|
| qiskit-ibm-runtime | `QiskitRuntimeService`, `Session`, `Batch`, the Sampler and Estimator submission path, `backend.run`, `properties(datetime=...)`, `target_history` | options and noise-model objects, fake-backend classes, `executor_sampler` input construction | import only; no service construction |
| qiskit-ibm-catalog | IBM Quantum Platform Qiskit Functions login and job calls | none | never |
| qiskit-serverless | remote function upload and run on the IBM serverless service | local Ray mode only | never |
| qiskit-ibm-transpiler | AI transpiler passes call the IBM cloud service with a token | none | never |
| qiskit-ibm-ai-local-transpiler | none | runs the AI transpiler models locally | skip (pins) |
| qiskit-ibm-experiment (archived) | experiment service upload | none | never |
| qiskit-device-benchmarking | submits benchmark jobs to IBM backends through runtime | analysis of retained data | host only |
| qiskit-experiments | `IBMBackend` jobs when handed an IBM backend | circuit generation and fitting; runs on Aer when handed an Aer backend | allowed with Aer backends only |
| mthree | `cals_from_system` runs calibration jobs on whichever backend it receives | correction solve | allowed with Aer backends only |
| samplomatic | none | box, template and samplex construction and sampling | allowed |
| ibm-quantum-schemas | none (dependency list names no network client) | schema models (role inferred from the name; dependencies are qiskit, samplomatic, numpy) | allowed |
| qiskit-mitigation | none (post-processing; hard dependency of runtime) | mitigation numerics | allowed |
| qiskit-noise-learning | experiments run through primitives on a backend | fitting and analysis | allowed with Aer backends only |
| qiskit-addon-cutting, qiskit-addon-obp | import `qiskit-ibm-runtime` primitives | cutting, reconstruction and backpropagation numerics | not installed |
| qiskit-addon-utils | none | circuit slicing and coupling-map helpers | allowed; QT pin 0.4.0 |
| qiskit-addon-slc, pauli-prop | none | shaded-lightcone PEC bounds and Pauli propagation | host only, installed ([qiskit-addon-slc.md](qiskit-packages/qiskit-addon-slc.md)) |
| qiskit-addon-sqd, -pna, -mpf, -aqc-tensor, qiskit-paulice | none | local numerics (chemistry, mitigation, tensor networks) | not installed |
| MCP server family | network calls to IBM services | none | never |

## Retained Kaggle environment records

The records under `results/kaggle/*/output/output/environment.json` report
Python 3.13.15, numpy 2.1.3, scipy 1.16.3, sympy 1.14.0, pandas 2.3.3,
torch 2.11.0 (`+cpu` on CPU machines, `+cu128` on T4s), qiskit 2.5.2 and
either qiskit-aer-gpu-cu11 0.17.2 or, on CPU kernels pushed after
`CPU_KERNEL_PINS`, qiskit-aer 0.17.2. The package list is a fixed key set;
a kernel pushed `--with GROUP` writes `pin_groups.json` beside it with every
group member's installed version, as `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` does for the twelve-pin
group.
