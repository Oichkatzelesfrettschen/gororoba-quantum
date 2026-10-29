# Python in this repository: multi-environment audit and governance

This document is the central governance and routing authority for Python libraries,
environments, dependency manifests and interpreters across the repository.
Versions live in the locked manifests and machine-audited inventories, never in
prose:
- [requirements.txt](../requirements.txt) (tested core runtime);
- [ci/requirements-ci.txt](../ci/requirements-ci.txt) (gate tools and testing);
- [ci/requirements-browser.txt](../ci/requirements-browser.txt) (browser validation of the measured explorer);
- [ci/requirements-replay.txt](../ci/requirements-replay.txt) (historical Qiskit 2.5.2 replays);
- [packaging/qiskit-aer-cuda/build-requirements.txt](../packaging/qiskit-aer-cuda/build-requirements.txt) (qiskit-aer CUDA wheel packaging);
- the build host's Arch packages in [python-stack.md](notes/build_host/python-stack.md), and the Qiskit-adjacent packages and `/opt` stacks beyond the core in [qiskit-packages/README.md](notes/qiskit-packages/README.md);
- the isolated provider environments: [Quantum Inspire](notes/quantum_inspire/README.md), [Open Quantum](notes/open_quantum/README.md), [Quandela](notes/quandela/README.md) ([quandela/python-stack.md](notes/quandela/python-stack.md)), [IQM](notes/iqm/README.md) ([iqm/python-stack-versions.json](notes/iqm/python-stack-versions.json)), and [Kaggle](notes/kaggle/README.md) ([kaggle_kernel/AGENTS.md](../kaggle_kernel/AGENTS.md)).

The central [library register](state/hypercomplex-libraries/libraries.md) lists every
distribution (362 distributions across all source surfaces) with its role, and its sibling
[libraries.json](state/hypercomplex-libraries/libraries.json) records each
tracked file that imports it (`imported_by`); gate
core-630 (`scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries --check`)
compares it with a fresh AST scan of `gororoba_quantum/`, `scripts/`, `ci/` and
`kaggle_kernel/`, so a new import in those trees enters the register in the same change.


## Multi-environment architecture

The repository segregates Python execution across six distinct runtime environments
to prevent dependency conflicts, preserve bit-for-bit historical replay, and respect
platform boundaries:

1. **Build Host (Arch Linux / CachyOS System Environment, `$PYTHON`)**
   - Python 3.14 (system interpreter).
   - Package management: Arch system packages (`pacman`, `paru`) and custom PKGBUILDs
     in `~/Github/PKGBUILDs`, all linking the system OpenBLAS (`blas-openblas`) as BLAS and LAPACK.
   - Hardware acceleration: NVIDIA RTX 4070 Ti (SM 89), CUDA 13.4.3, cuQuantum 26.09.0.8
     (libcustatevec.so.1 and libcutensornet.so.2), and cutensor 2.8.1.0.
   - Locally compiled packages: `python-qiskit` (2.6.1), `python-qiskit-aer-cuda` (0.18.2-3 with cuStateVec support and unique provider names),
     `python-samplomatic` (0.21.0), and `python-qiskit-ibm-runtime` (0.51.0); the library wiring
     is in [python-stack.md](notes/build_host/python-stack.md).
   - Computer algebra: System `sagemath` (10.10) for exact algebraic geometry and
     rotation-composite audits.
   - Local hypercomplex verification stack: 17 packages extracted and validated against
     `gororoba_quantum/cd_core.py` by `scripts/algebra_package_tables.py`.

2. **Hosted CI / Pull-Request Verification (`ci/`)**
   - Python 3.14.7 container environment.
   - Strictly locked dependencies from `requirements.txt` and `ci/requirements-ci.txt`.
   - Tool pinning: `ci/pinned_tool.py` runs pinned `ruff==0.17.1` and `mypy==2.4.0` via uv.
   - Browser checks: `ci/requirements-browser.txt` installs `playwright==1.64.0` for
     headless validation of rendered explorer artifacts.

3. **Historical / Replay Runtime (`REPLAY_PYTHON`)**
   - Interpreter satisfying `ci/requirements-replay.txt`: Qiskit 2.5.2, pydantic 2.13.5,
     ibm-quantum-schemas 0.12.20260921, and samplomatic 0.21.0.
   - Gates marked `"runtime": "qiskit-2.5"` execute under this runtime to verify
     bit-for-bit equivalence of retained historical evidence, circuit routing, and receipts.

4. **Isolated Provider Virtual Environments**
   - **Quantum Inspire (`QI_PYTHON`, Python 3.13)**: Located in `~/.local/share/quantum_inspire/`
     or `QI_ENV`. Isolates `quantuminspire`, `qxelarator`, `libqasm`, `opensquirrel`, and
     `qiskit-quantuminspire` from main Qiskit versions.
   - **Open Quantum (`OQ_PYTHON`, `OQ_ENV`)**: Located in `~/.local/share/open_quantum/`. Runs
     `openquantum-sdk`, `openquantum-sdk-qiskit`, and `openquantum-mcp`.
   - **Quandela (`QD_PYTHON`)**: Dedicated environment in `~/.local/share/quandela/` for the
     Quandela MCP server (`scripts/qd_mcp_server.py`). Perceval itself runs on `$PYTHON`.
   - **IQM Resonance (`iqm-python`)**: Independent Python 3.13 environment under
     `/opt/iqm-resonance-stack` running IQM OS 4.7 (`iqm-client`, `qiskit 2.1.2`, `cirq-core`,
     `qrisp`, `iqm-pulla`, `iqm-pulse`).
   - **Other Providers**: Pinned venvs under `~/.local/share/<provider>/venv` for IonQ,
     BlueQubit, Quafu, and Origin Quantum.

5. **Kaggle Kernel Multi-Substrate Execution (`kaggle_kernel/`, `scripts/kaggle_run.py`)**
   - **CPU Kernels**: Kaggle Python 3.13 container, image numpy/scipy/sympy/torch,
     pip `--no-deps` hypercomplex stack from pinned archives (`hypercomplex.json`),
     and optional `quantum-tools` group (`PIN_GROUPS`).
   - **GPU Kernels (Tesla T4)**: `qiskit-aer-gpu-cu11` 0.17.2, `cuquantum-cu11` 24.8.0,
     `cutensor-cu11` 2.2.0, or custom CUDA 13 Aer wheel (`qiskit-aer-gpu-cu13`).
   - **TPU Kernels (`TpuV5E8`, `TpuV6E8`)**: JAX differentiable array sweeps only;
     Aer has no TPU backend.

6. **Native Packaging and Wheel Building (`packaging/`)**
   - Locked build-system dependencies in `packaging/qiskit-aer-cuda/build-requirements.txt`
     (`build==1.6.0`, `scikit-build==0.19.1`, `pybind11==3.1.0`, `setuptools==84.0.0`, `wheel==0.48.0`).


## Locally installed vs. otherwise used libraries

The repository audit recognizes four operational statuses across all Python distributions:

1. **Locally Installed and Directly Imported on Build Host**
   - *Core runtime*: `numpy`, `scipy`, `sympy`, `python-flint`, `rustworkx`, `qiskit`,
     `qiskit-aer`, `qiskit-ibm-runtime`, `pydantic`, `qiskit-mitigation`, `samplomatic`,
     `ibm-quantum-schemas`.
   - *CI and verification*: `mypy`, `ruff`, `matplotlib`, `pytest`, `pytest-xdist`,
     `threadpoolctl`, `perceval-quandela`, `exqalibur`, `cvxpy`, `clarabel`, `mcp`,
     `playwright`.
   - *Local computer algebra*: `sagemath`.
   - *In-tree specifications*: `gororoba_quantum/cd_core.py` (canonical Cayley-Dickson multiplication),
     `gororoba_quantum/parallel.py` (order-preserving spawn process pool).

2. **Locally Installed for Hardware Acceleration, Probes and Negative Controls**
   - *Host CUDA/BLAS support*: `cuquantum` (libcustatevec, libcutensornet), `cutensor`,
     `cuda`, OpenBLAS (`blas-openblas`) as the BLAS and LAPACK provider.
   - *Algebra reference packages*: Installed as Arch packages and bound by SHA256 digests in
     `docs/evidence/algebra_packages/tables.json` to verify `cd_core`:
     `hypercomplex`, `hypercomplex-engine`, `hypercomplex-algebra`, `cayley-calculator`,
     `cayley-dickson`, `octonion`, `splitoct` (split-signature negative control), `mathdunders`,
     `numpy-quaternion`, `quaternionic`, `pyquaternion`, `clifford`, `kingdon`, `galgebra`,
     `pyoctonion`, `octonion-sedenion`, `hyprat`.
   - *Exact arithmetic backends*: `python-flint` (modular rank, rational null spaces) and
     `pyadic` (finite-field and p-adic valuations), which define no Cayley-Dickson table.

3. **Otherwise Used in Isolated Virtual Environments or Containers**
   - Distributions that would create conflicting requirements if installed into the main host
     environment:
     - Quantum Inspire: `quantuminspire`, `qxelarator`, `libqasm`, `opensquirrel`, `qiskit-quantuminspire`
       (requires isolated Python 3.13 venv).
     - IQM Resonance: `iqm-client 36.0.0`, `qiskit 2.1.2`, `cirq-core 1.7.0`, `qrisp 0.9.10`
       (pinned in `/opt/iqm-resonance-stack`).
     - Open Quantum: `openquantum-sdk`, `openquantum-sdk-qiskit`, `openquantum-mcp`.
     - Kaggle GPU simulation: `qiskit-aer-gpu-cu11`, `cuquantum-cu11`, `cutensor-cu11`
       (containerized T4 runtime).

4. **Documented Ecosystem Candidates and Evaluated Alternatives**
   - Distributions evaluated during architectural surveys and cataloged in
     [docs/notes/packages/candidates.md](notes/packages/candidates.md) and
     [docs/notes/qiskit-ecosystem.md](notes/qiskit-ecosystem.md).
   - Each carries a recorded status:
     - *Declined or not required*: `qiskit-addon-mpf` (declined multiproduct workflow; CVXPY presence does
       not establish admission), `qiskit-dynamics` (archived upstream), `benchpress` (unqualified oracle),
       `mapomatic` (unqualified against live Target), `pennylane`, `qutip`.
     - *Machine register tracking*: All 362 evaluated distributions are tracked with their
       retained roles, host presence, and citation records in
       [docs/state/hypercomplex-libraries/libraries.md](state/hypercomplex-libraries/libraries.md).


## Interpreters

| Interpreter | Runs | Authority |
| --- | --- | --- |
| `$PYTHON`, exported | default-stack scripts, gates and dry runs; a provider-dependent script or gate half runs under its provider interpreter below | [AGENTS.md](../AGENTS.md) "Layout and gates" |
| `--replay-python` or `REPLAY_PYTHON` | gates marked `"runtime": "qiskit-2.5"`; with neither, the running interpreter serves when it holds every replay pin, and an unresolved runtime exits 127 | [ci/AGENTS.md](../ci/AGENTS.md) |
| `QI_PYTHON` (Python 3.13) | Quantum Inspire SDK, qxelarator, cQASM, OpenSquirrel | [quantum_inspire/README.md](notes/quantum_inspire/README.md) |
| `OQ_PYTHON` | Open Quantum SDK | [open_quantum/README.md](notes/open_quantum/README.md) |
| `QD_PYTHON` | the Quandela MCP server; Perceval itself runs on `$PYTHON` | [quandela/README.md](notes/quandela/README.md) |
| `iqm-python` | IQM Resonance client stack | [iqm/README.md](notes/iqm/README.md) |
| `qi-stack-python`, `qi-stack` (Python 3.13) | the hash-locked Quantum Inspire stack: SDK, Qiskit provider and PennyLane plugin on qiskit 2.3.0 | [quantum-inspire-family.md](notes/qiskit-packages/quantum-inspire-family.md) |
| `qiskit-debugger-python` (Python 3.11) | qiskit-debugger on its pinned Qiskit 0.43.2 | [qiskit-debugger.md](notes/qiskit-packages/qiskit-debugger.md) |
| `quantum-pipeline-python`, `quantum-pipeline` (Python 3.13) | quantum-pipeline VQE runs on Aer 0.17.2 | [quantum-pipeline.md](notes/qiskit-packages/quantum-pipeline.md) |
| `QB_PYTHON` (Python 3.13) | qBraid SDK (`qbraid`, `qbraid-core`). The guide's venv is the portable default; the build host sets `QB_PYTHON` to `qbraid-python` from the `qbraid-stack` package | [qbraid/README.md](notes/qbraid/README.md) |
| Kaggle kernel | simulations of 14 qubits or fewer | [kaggle/README.md](notes/kaggle/README.md) |

Every interpreter starts with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, which the Qiskit Rust
and Aer OpenMP extensions need. Each gate's flags are the ones its command
in [ci/gates.json](../ci/gates.json) spells out; most pass `-B -W error` and
many also run under `-O`, so a check raises explicitly instead of using
`assert`.


## Dependency manifests and inventory verification

| Manifest / Register | Scope and purpose | Verification gate |
| --- | --- | --- |
| [requirements.txt](../requirements.txt) | Primary runtime dependencies (Qiskit 2.6.1, Aer 0.18.2, runtime 0.51.0, FLINT, SymPy, SciPy, NumPy) | `sh ci/pr_checks.sh tests` |
| [ci/requirements-ci.txt](../ci/requirements-ci.txt) | CI gate tools, testing plugins, Quandela adapters, CVXPY/Clarabel solvers, MCP | `sh ci/pr_checks.sh lint\|types\|tests` |
| [ci/requirements-browser.txt](../ci/requirements-browser.txt) | Headless Playwright browser automation for measured explorer verification | `scripts/validate_measured_explorer.py` |
| [ci/requirements-replay.txt](../ci/requirements-replay.txt) | Pinned Qiskit 2.5.2 compiler stack for bit-for-bit historical replay | `ci/run_gates.py --replay-python` |
| [packaging/qiskit-aer-cuda/build-requirements.txt](../packaging/qiskit-aer-cuda/build-requirements.txt) | Build tools (`build`, `scikit-build`, `pybind11`, `wheel`) for native Aer CUDA package | [notes/build_host/custatevec.md](notes/build_host/custatevec.md) |
| [state/hypercomplex-libraries/libraries.md](state/hypercomplex-libraries/libraries.md) | Exhaustive 362-distribution register of roles, host presence, and citations | `python3 scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries --check` |
| [state/hypercomplex-libraries/libraries.json](state/hypercomplex-libraries/libraries.json) | Machine-readable AST import scan, declared pins, and unresolved roots | `test_retained_inventory_*` in behavioral suite |


## Libraries by job

| Job | Library | Use it when | Rule and evidence |
| --- | --- | --- | --- |
| Cayley-Dickson products and signs | `cd_core` (in tree) | always: it is the specification | [algebra_circuit_rules.md](notes/algebra_circuit_rules.md) |
| Arrays, batched linear algebra | numpy | any float work; vectorize before pooling | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Least squares, decompositions, statistics, sparse | scipy | `lstsq` or pivoted QR, never normal equations; `scipy.sparse` for structured systems | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Exact rank modulo p, rational null spaces | python-flint through `scripts/exact_rank.py` | every rank or nullity certificate | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Symbolic algebra, exact matrices | sympy, as `DomainMatrix` for integer products; its ground types are FLINT on the pinned stack | polynomial identities and charts | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Arbitrary precision | mpmath; python-flint `arb_mat` and `acb_mat` for ball arithmetic | refining a float estimate past float64 rounding. FLINT's `eig` returns rigorous enclosures, and a cluster of near-equal eigenvalues widens its balls | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| p-adic and finite-field arithmetic | pyadic, galois | rational reconstruction, F_p linear algebra beyond FLINT, exact Hensel lifts whose valuation reads the order of an obstruction ([pyadic.md](notes/packages/manual/pyadic.md#hensel-lifting)) | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Gate-model circuits and transpilation | qiskit | IBM and other Qiskit-compatible circuits; the live Target is the timing authority. Provider-native circuits (Perceval, cQASM) follow their provider guides | [ibm_heron_platform.md](notes/ibm_heron_platform.md) |
| Noise simulation | qiskit-aer, CPU or the host's CUDA build | 14 qubits or fewer on Kaggle; 15 qubits only through an approved case naming the substrate; 16 or more go to IBM hardware through an approved case | [AGENTS.md](../AGENTS.md) "QPU time and calibration", [substrates.md](notes/kaggle/substrates.md) |
| IBM hardware | qiskit-ibm-runtime, client-side `executor_sampler` | `--submit` only after an approved case; `--collect`, `--preserve-raw`, calibration reads and transpilation need no approval | [qpu-submission.md](notes/ibm_quantum/qpu-submission.md) |
| Convex modeling and tomography SDPs | cvxpy, clarabel, scs, osqp | PSD-constrained state/process tomography and classical teleportation benchmarks; inspect residuals and solver status | [quandela/python-stack.md](notes/quandela/python-stack.md), [solver-role-grounding.json](state/hypercomplex-libraries/solver-role-grounding.json) |
| Layout and graph search | rustworkx | replica placement (`vf2_mapping`) | `gororoba_quantum/` |
| Batched density-matrix sweeps | jax | error-scale sweeps in `jax_bridge` on CPU | [jax-bridge-structure-report.md](notes/kaggle/jax-bridge-structure-report.md) |
| Tensor networks, contraction order | quimb, cotengra, opt_einsum | networks beyond a few tensors | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Photonic circuits | perceval, exqalibur | Quandela runs and their simulations | [quandela/README.md](notes/quandela/README.md) |
| qBraid sessions and device calls | qbraid, qbraid-core | a call through the qBraid SDK. The credit snapshot uses the default interpreter's HTTP client and does not import these packages. Pins stay in the qBraid requirements file; the library register marks both distributions separate | [qbraid/README.md](notes/qbraid/README.md), [requirements-qbraid.txt](notes/qbraid/requirements-qbraid.txt), [libraries.md](state/hypercomplex-libraries/libraries.md) |
| Cayley-Dickson cross-checks | hypercomplex (recursive products, `Fraction` witnesses); hyprat (exact rational coefficients, annihilators, regular representations); hypercomplex-engine (fast basis signs above dimension 16; hypercomplex-algebra wraps it and is not independent); cayley-dickson (recursive products), cayley-calculator, octonion-sedenion, pyoctonion, octonion (PyTorch batches) | an independent witness for a `cd_core` result, through a declared map checked on every basis pair; splitoct serves as the split-signature negative control | [packages/README.md](notes/packages/README.md), `scripts/algebra_package_tables.py` |
| Quaternions | numpy-quaternion (vectorized fields), quaternionic (Numba arrays), pyquaternion (scalar rotations) | quaternion subalgebra checks and rotation bookkeeping | [packages/README.md](notes/packages/README.md) |
| Clifford and geometric algebra | clifford, galgebra (symbolic), kingdon (generated operators) | associative envelopes and rotor controls; they never supply an octonion or sedenion product | [packages/README.md](notes/packages/README.md) |
| Audits that need SageMath | sage | build-host audits whose retained output a pinned gate checks | [rank_locus_rotation_composite](evidence/rank_locus_rotation_composite/README.md#symmetry) |
| Plots | matplotlib | measured figures, and exact or prospective model figures labeled as such; mock outcomes never enter either | [AGENTS.md](../AGENTS.md) "Layout and gates" |
| Tests | pytest, pytest-xdist | the behavioral suite | [ci/AGENTS.md](../ci/AGENTS.md) |
| Thread accounting | threadpoolctl | recording the BLAS and OpenMP runtimes a gate used | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Provider MCP servers | mcp | `scripts/*_mcp_server.py` | provider guides |
| Kaggle control, browser checks | kaggle, kagglesdk, requests; playwright, selenium | kernel push and status; rendered-viewer and session checks | [kaggle/README.md](notes/kaggle/README.md), [ci/requirements-browser.txt](../ci/requirements-browser.txt) |
| Process pools | `gororoba_quantum/parallel.py` | every CPU-bound loop over independent items; dask and joblib stay unused | below |

A gate that needs a library outside the pin files retains its output with
`--out` and checks that output with the pinned stack, as core-489 does for
pyadic.


## Qiskit-adjacent packages and stacks

The build host carries these distributions beyond the pinned core of
requirements.txt, each built from a PKGBUILD in `~/Github/PKGBUILDs`. This
table registers them. Each linked note in
[notes/qiskit-packages/](notes/qiskit-packages/README.md) gives the package's
usage, commands, flags, hazards and connections, and that directory's README
maps how the packages connect. `"$PYTHON"
docs/notes/qiskit-packages/probe_packages.py --stacks` reruns the offline
probes after any upgrade.

| Surface | Interpreter | Core it carries | Packages |
|---|---|---|---|
| system, `$PYTHON` | Python 3.14 | qiskit 2.6.1, runtime 0.51.0, Aer 0.18.2 (CUDA build) | [qiskit-aer](notes/qiskit-packages/qiskit-aer.md), [ibm-quantum-schemas](notes/qiskit-packages/ibm-quantum-schemas.md), [qiskit-noise-learning](notes/qiskit-packages/qiskit-noise-learning.md), [pauli-prop and qiskit-addon-slc](notes/qiskit-packages/qiskit-addon-slc.md), [qiskit-serverless and qiskit-ibm-catalog](notes/qiskit-packages/qiskit-functions.md), [qiskit-connector](notes/qiskit-packages/qiskit-connector.md), [qiskit-resume](notes/qiskit-packages/qiskit-resume.md), [qiskit-waveform-sim](notes/qiskit-packages/qiskit-waveform-sim.md), [qcog](notes/qiskit-packages/qcog.md), [qubasic](notes/qiskit-packages/qubasic.md), [eigenkit](notes/qiskit-packages/eigenkit.md), [quantum-al](notes/qiskit-packages/quantum-al.md), [perceval-quandela and perceval-interop](notes/qiskit-packages/perceval-interop.md) |
| `quantuminspire-qiskit-stack` | `qi-stack-python`, Python 3.13 | qiskit 2.3.0, Aer 0.17.2 | [quantuminspire, qiskit-quantuminspire, pennylane-quantuminspire](notes/qiskit-packages/quantum-inspire-family.md) |
| `qiskit-debugger-stack` | `qiskit-debugger-python`, Python 3.11 | qiskit 0.43.2 (terra 0.24.1), Aer 0.12.1 | [qiskit-debugger](notes/qiskit-packages/qiskit-debugger.md) |
| `quantum-pipeline-stack` | `quantum-pipeline-python`, Python 3.13 | qiskit 2.6.1, runtime 0.51.0, Aer 0.17.2 | [quantum-pipeline](notes/qiskit-packages/quantum-pipeline.md) |

Each package's placement follows from one requirement:

- The Quantum Inspire family requires Python below 3.14, and pennylane-qiskit
  caps qiskit at 2.3.0.
- qiskit-debugger pins `qiskit==0.43.2` and imports `qiskit.Aer` and
  `qiskit.execute`, both of which Qiskit 1.0 removed.
- quantum-pipeline caps qiskit-aer below 0.18.
- qiskit-serverless caps qiskit-ibm-runtime below 0.51, and its system
  package relaxes that cap.

Four packages carry host hazards that their notes spell out:
- qiskit-connector loads `.env` files on import and overwrites the default
  IBM account.
- qiskit-resume unpickles checkpoint files.
- qubasic's `SHELL` statement runs shell commands.
- qiskit-waveform-sim takes only timing from the Target; its pulse shapes
  and amplitudes are placeholders.

The environments, caches and build trees that these surfaces leave on the
host, and the rules for cleaning them, are in
[runbooks/cache-locations.md](runbooks/cache-locations.md).


## Optimization ladder

Climb in this order and stop at the first rung that meets the budget.

1. **Measure.** `py-spy record` for Python stacks, `perf` for native code,
   `hyperfine` for whole commands. A long run writes its full log to a file.
2. **Vectorize.** Broadcasting, batched `@` and stacked `np.linalg` replace
   Python loops over elements; preallocate and keep dtypes concrete.
3. **Batch replicates.** A null calibration or bootstrap runs across
   replicates as arrays, with a gate proving the batched path returns the
   scalar reference's bits ([vectorized-fits.md](runbooks/vectorized-fits.md)).
4. **Pool independent items.** `parallel.ordered_map(function, items)` with a
   module-level `function` and picklable items. Items that share a seeded
   generator draw every input first, in the generator's order, and then map,
   so pooled and serial runs write the same bytes. The pool spawns, so an
   entry script calls it only under `if __name__ == "__main__":` and runs
   from a file rather than stdin. The pool sets each unset BLAS and OpenMP
   thread variable to one for its workers and keeps a value the caller
   exported, which can oversubscribe native threads.
5. **Move exact work to FLINT.** `scripts/exact_rank.py` gives
   `rank_mod` (FLINT `nmod_mat`, a rank modulo a word-size prime, which
   bounds the rational rank from below) and `rational_kernel` (FLINT
   `fmpq_mat` reduced row echelon form, a rational null space). A finite-field
   null space certifies nothing over the rationals; the certifying caller,
   such as `d_locus_nullity.nullity`, checks each rational kernel vector in
   Python integers.
6. **Use an accelerator only where a run qualified it.** The host's CUDA Aer
   build and Kaggle GPUs serve the circuits their notes measured; small
   dynamic circuits stay on CPU ([substrates.md](notes/kaggle/substrates.md)).
7. **Shard.** A pooled, batched run that still exceeds one host's budget
   shards to Kaggle CPU sessions by item range, once the user has approved
   the written case every simulator job and notebook session needs
   ([AGENTS.md](../AGENTS.md) "Hardware services"). The successor null also
   shards to the public repository's hosted runners
   ([null-shards.md](runbooks/null-shards.md)).


## Emulating another CPU with Intel SDE

numpy's dispatched loops, OpenBLAS's `DYNAMIC_ARCH` kernel choice and glibc's
libm ifuncs all pick their code path from CPUID, so one float64 computation can
round differently on an AVX-512 runner than on the build host, an AMD Ryzen 5
5600X3D (Zen 3, AVX2, no AVX-512). The Intel Software Development Emulator
runs an unmodified process under a chosen Intel CPU's CPUID and instruction
set, AVX-512 included, so the host reproduces an AVX-512 machine's natural code
path without capping the dispatch (`OPENBLAS_CORETYPE`,
`NPY_DISABLE_CPU_FEATURES`; [ci/AGENTS.md](../ci/AGENTS.md)).

The host carries `intel-sde` 10.13.1 (chaotic-aur), installed at
`/opt/intel-sde/sde64`. A run names the chip and passes the command after `--`:

```sh
/opt/intel-sde/sde64 -icx -- "$PYTHON" -B scripts/n21_dose_decisions.py RUN_DIR --out OUT.json
```

- `-icx` is an Ice Lake server and `-skx` a Skylake server; `-clx`, `-cpx`,
  `-spr` and `-gnr` name other AVX-512 server chips, `-hsw` an AVX2-only
  Haswell, and `/opt/intel-sde/sde64 -help` lists every chip. Emulate the
  model the runner reports: `ci/run_gates.py` prints a `numeric stack:` line
  with the CPU model, numpy's enabled dispatch targets and each loaded
  OpenBLAS core before the first gate. SDE emulates Intel chips only, so an
  AMD runner has no emulated counterpart.
- The process sees the emulated CPUID, so numpy reports `AVX512F` and
  `X86_V4` and dispatches its AVX-512 loops, and OpenBLAS selects its kernel
  for that chip. Exported caps still apply, so one emulated run can take the
  capped path and another the uncapped one.
- The emulator executes each instruction with the hardware's IEEE semantics,
  so the bits match a real chip of that generation wherever the result
  depends only on the instruction path. Cache sizes, core counts and timing
  are the host's, so a library that sizes its blocking from the cache or
  threads by core count can still diverge from real hardware. Pin
  `OPENBLAS_NUM_THREADS=1` and compare against a real run before treating an
  emulated replay as that chip's result.
- Cost: importing numpy and threadpoolctl took 12.8 s, and the n21 dose
  decisions run (about 5 s native) took 147 s, about 30 times native.

Measured on the n21 dose-decisions record
`results/live/2026-10-27T014354.701394Z/dose-decisions.json` (written in the
runner image, `scripts/n21_dose_decisions.py`, whose replica covariance is
`psi.T @ psi`, an OpenBLAS product):

| Emulated chip | `OPENBLAS_CORETYPE=Haswell` | numpy cap | Fields that differ from the record |
|---|---|---|---|
| `-icx` | set | set | 0 |
| `-icx` | set | unset | 0 |
| `-icx` | unset | set | 85 |
| `-icx` | unset | unset | 85 |
| `-skx` | unset | unset | 85 |

OpenBLAS's AVX-512 kernel alone moves the record under emulation, and
numpy's dispatch leaves it unchanged. On the hosted runners of audit run
40824932629, every shard reports numpy dispatching `X86_V3` and both
OpenBLAS copies on the `Haswell` core, so both pins apply. The Intel Xeon
Platinum 8573C shard (AVX-512) replays the record exactly. The AMD EPYC 9V74
and 9V45 shards (Zen 4 and Zen 5, AVX-512) differ in 95 fields. Their
`.arms.n21_orbit_window_dose_d7000_feedback_contrast.sigma` equals the
emulated value of the unpinned Intel AVX-512 kernel, and their d10500 arm's
sigma moves in no emulated run. So on those AMD CPUs a CPU-dependent path
outside the reported numpy dispatch and OpenBLAS core still changes the
rounding, and SDE cannot reproduce it. A record that depends on BLAS rounding
replays on the host under emulation only after a real-hardware comparison
has shown the two agree.

## Correctness rules

- Seed every generator and record the seed. Byte replay also needs the
  pinned generator algorithm and dependency versions and a gate that
  compares bytes: NumPy's seeded `Generator.binomial` changed between
  releases (`scripts/atlas_fringe_amplitudes.py`).
- float64 suffices wherever sampling sets the error. An exact claim uses
  exact arithmetic, and extended precision only refines a float estimate.
  A ball enclosure that excludes zero proves a minor nonzero and so bounds a
  rank from below; no precision proves a value zero, so rank deficiency and
  membership in a rank locus need exact arithmetic.
- Float tolerances decide nothing about rank, nullity or local dimension.
  A floating projection stops once a residual falls under its tolerance, so
  a direction along which the residual vanishes to high order passes
  uncorrected; such a test needs a scale where that order exceeds the
  tolerance, or extended precision.
- Run ruff and mypy through `ci/pinned_tool.py` on every touched Python file, and mypy over gate core-039's scope when a change alters a signature another module imports.
- Record the versions a result depends on inside the result.
- Mock outcomes (`--native-dry-run`) never enter an analysis or a figure.
