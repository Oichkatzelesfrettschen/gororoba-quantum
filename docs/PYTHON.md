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
- the build host's Arch packages in [python-stack.md](notes/build_host/python-stack.md);
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
     in `~/Github/PKGBUILDs` replacing `blas-openblas` with AMD AOCL BLAS/LAPACK providers.
   - Hardware acceleration: NVIDIA RTX 4070 Ti (SM 89), CUDA 13.4, cuQuantum 26.09.0.8
     (libcustatevec.so.1 and libcutensornet.so.2), and cutensor 2.8.1.0.
   - Locally compiled packages: `python-qiskit-aer-cuda` (0.17.2-2 with cuStateVec support),
     `python-samplomatic` (0.21.0), and `python-qiskit-ibm-runtime` (0.50.0).
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
     `cuda`, AOCL 5 BLAS/LAPACK providers.
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
| [requirements.txt](../requirements.txt) | Primary runtime dependencies (Qiskit 2.6.0, runtime 0.50.0, FLINT, SymPy, SciPy, NumPy) | `sh ci/pr_checks.sh tests` |
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
