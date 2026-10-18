# gororoba_quantum agent guide

This file applies to the runnable modules, families, contracts and the live runner under `gororoba_quantum/`. The repository's root AGENTS.md
carries every other rule and loads first; the sections below repeat its
algebra circuit design rules and Heron execution facts byte for byte so they
bind work started here.
Paths are repository-relative.

<!-- algebra-circuit-rules:begin -->
## Algebra circuit design rules

These rules bind every circuit, case, analysis and note that encodes
Cayley-Dickson arithmetic on a qubit register. The root AGENTS.md,
gororoba_quantum/AGENTS.md and scripts/AGENTS.md carry this section with
identical bytes; `ci/check_agents_sections.py` fails on any difference.
`docs/evidence/reviewer_associator_audit/` replays the numeric claims below
(gates sources-240 and sources-241), and `scripts/algebra_circuit_fixtures.py`
(gates core-251 and core-252) runs the zero-product, Hadamard-basis and
workspace fixtures on the circuit builders of `designs.py`.

**Encoding and representation.**
- The map `a -> L_a` is a linear encoding, not an algebra homomorphism.
  Associative matrix composition represents a non-associative product through
  `(L_a L_b - L_ab) c = -(a, b, c)` with `(a, b, c) = (ab)c - a(bc)`: two
  wirings compared by an observable, never a claim that matrix products
  fail to associate. A faithful associative representation of a
  non-associative product does not exist.
- A sedenion-coefficient encoding states its coefficient domain (real or
  complex), normalization, basis convention (`cd_core.cd_sign`, doubling
  `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`) and scale. The basis
  state `|0>` is `e_0 = 1`, the multiplicative identity, never the zero
  vector. A unitary cannot output the zero vector: an algebraic zero product
  is a heralded branch of zero probability while the full state keeps norm 1.
- Algebra index bit `b` sits on register qubit `b` (`designs.left_mult_gate`),
  so qubit 0 carries the least significant bit, matching Qiskit's
  little-endian outcome strings; a register drawn or read in another order
  states its map.
- A product sign carried as the global phase of a block is unobservable on
  its own. A Hadamard test sees it only when the sign is set on the block
  before it is controlled, so the controlled block applies it as a relative
  phase on the control (`scripts/algebra_circuit_fixtures.py`).
- Norm multiplicativity `|ab| = |a||b|` holds for real coefficients in
  dimensions 1, 2, 4 and 8 only (Hurwitz). The real sedenions already have
  zero divisors, `(e1 + e10)(e4 - e15) = 0`, and the complex-linear extension
  has them even on associative subalgebras: `(e_0 + i e_1)(e_0 - i e_1) = 0`.

**Zero-product witnesses.**
- Certify every claimed zero-divisor pair with `cd_core` before circuit work.
  Four product terms that land on four distinct XOR labels cannot cancel:
  `(e1 + e10)(e2 - e13) = e3 + e7 + e8 - e12`, which is the repository's
  negative regression fixture (fixed-operand LCU `P(s = 0) = 1/2`). The
  corpus pair `(e1 + e10)(e4 - e15) = 0` is the dark witness, and
  `(e1 + e10)(e4 + e15)` is its bright control (`P(s = 0) = 1`).
- Read the selector's success outcome, not "output label unequal to zero".
  The fixed-operand LCU of Design B gives `P(s = 0) = ||x y||^2 / 2` for
  normalized `x = (e_i + t e_j)/sqrt2`, `t = +-1`, and normalized `y`;
  `designs.lcu_witness` builds `t = +1`, and `t = -1` adds a Z on the
  selector after its first H. The
  universal coefficient contraction of the D-dimensional algebra (D = 16 for
  the sedenions), `M|i, j> = sigma(i, j)|i xor j>`, has `M M^dagger = D I`,
  so its success Kraus operator is `M / sqrt(D)` and `P = ||x y||^2 / D`. Reports
  give success counts, attempts, the bright reference, the uncertainty and
  the implemented normalization; the dark floor carries preparation, coherent
  control, incoherent, readout and sampling contributions together.

**Signs, workspace and measurement basis.**
- A sign register prepared in `|0>` records the sign as a which-path label;
  phase kickback needs the register in `|->`, where `X|-> = -|->`. Every
  retained input or workspace register that differs between branches
  suppresses their interference and enters the overlap.
- Before two computation branches recombine, return every temporary register
  to a common state (undo branch-specific XORs), and include all registers in
  the overlap calculation.
- In a Hadamard test, `<X_c>` before the final H, or `<Z_c>` after it, equals
  `Re<psi_L|psi_R>`; `X_c` measured after the final H reads the pre-H `Z_c`,
  which is 0 for balanced branches.
- A uniform superposition over all `16^3` sedenion basis triples gives
  witness expectation `1 - 2(1848/4096) = 25/256` and `P(c = 1) = 231/512`;
  the deterministic `-1` belongs to a single non-associating triple or to
  input supported inside that sign sector.

**Observables and claims.**
- Associator-sign measurement, zero-product success and state-coherence
  reconstruction are three observables. The fixed-pair witness
  `W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j)` is diagonal, so its expectation
  `sum_k rho_kk omega(i, j, k)` reconstructs no coherence of the data
  register. A selected coherence `<x|rho|y>` needs the `2^w` settings with X
  or Y on the `w` bits where `x` and `y` differ and Z on the rest, with the
  register order fixed: four settings (XX, XY, YX, YY) for a two-qubit pair,
  and at most 16 for a sedenion register.
- Logical register counts: fixed-pair associator test, 4 data qubits plus 1
  control; fixed sparse operand zero-product LCU, 4 data qubits plus 1
  selector; two-input signed lookup, 8 input qubits plus 1 sign qubit; three
  independent input registers with coherent branch control, 12 input qubits
  plus 1 control plus workspace. Routed gate costs are measured separately.
- Name the interferometer an associator-sign interference witness; a
  holonomy claim needs a parameter space, transport rule and closed-loop
  observable. Non-Abelian braiding is noncommutative and associative and
  supports no non-associativity claim. A circuit construction establishes
  ideal implementability, hardware data establish performance under a stated
  implementation, and a priority claim needs a separate literature
  comparison.
- IBM removed pulse-level control on 3 February 2025; designs use the gate
  set, fractional gates and dynamic circuits.

**Cayley-Dickson, quaternion and Clifford packages.**
`gororoba_quantum/cd_core.py` is the specification. A package result enters
evidence only through a declared map onto it, identity or a signed
relabeling checked on every basis pair; majority agreement is never the
criterion. `scripts/algebra_package_tables.py` binds each installed package
to its pinned release and retains its tables in
`docs/evidence/algebra_packages/tables.json` (CI rechecks them without
importing any package), and `docs/notes/packages/` holds one note per
package. Each package is an Arch package; a broken or missing one is rebuilt
and reinstalled from its PKGBUILD in `~/Github/PKGBUILDs` (`makepkg -si
--nocheck` in the package directory), never patched in place, and the note's
pinned digest is checked again after the rebuild. A Kaggle kernel builds the
same seventeen packages from the same pinned archives (`--fetch` and
`--install` apply the PKGBUILD recipes) and runs its entry only after
`--extract` regenerates `tables.json` byte for byte; SageMath stays on the
build host (`docs/notes/kaggle/hypercomplex-stack.md`). A Clifford algebra
is associative, so clifford, kingdon and galgebra reach cd_core only through
Cl(0,1) and Cl(0,2) (the complex numbers and quaternions); an octonion or
sedenion statement never rests on them.

| Arch package | Import | Version | Relation to cd_core | Use it for | Trap |
|---|---|---|---|---|---|
| sagemath | `sage`, `OctonionAlgebra(QQ)` | 10.10 | opposite algebra in natural order; sign flip on e3, e5, e6 is an isomorphism | exact octonion reference, quadratic forms, G2 | ported code reverses every product unless mapped |
| python-hypercomplex | `hypercomplex` | 0.3.4 | identical table (D = 8, 16 exhaustive; 32, 64 sampled) | exact certificates with `cayley_dickson_algebra(n, fractions.Fraction)` | a basis product costs about 4x more per doubling; `inverse()` exists for zero divisors |
| python-hypercomplex-engine | `hypercomplex_engine` | 0.5.0 | identical (standard); its split variant shares every associator sign | fast basis-sign oracle at D = 4096 and beyond | takes and returns `(sign, index)` tuples; `dim` changes which doubling is split |
| python-hypercomplex-algebra | `hypercomplex_algebra` | 0.2.0.2 | identical; wraps the engine | parsing and formatting expressions | not an independent witness; `multiply_many_expressions` folds left |
| python-cayley-calculator | `Cayley_Calculator`, then `sedenion` and the other level modules | 1.3.1 | identical table at D = 16 (gamma = -1) | elementary functions (exp, log, trigonometric) through D = 128 | coerces every coefficient to float64; `from octonion import *` loads python-octonion |
| python-cayley-dickson | `cayley_dickson` | commit abf96e7 | identical table at D = 8, 16 | reading and cross-checking only; the source carries no license | installs a top-level `src` package, so `import src` resolves to it; its pandas table reads transposed |
| python-octonion | `octonion` | 0.1.0 | signed relabeling from a Fano labeling, `pi = (0, 1, 2, 4, 3, 6, 7, 5)` with a flip on e6 | batched octonion tensors in PyTorch | index i is not cd_core e_i; its tensors are float64 while torch defaults to float32; owns the `octonion` module name; AGPL |
| python-splitoct | `SplitOct` | 0.16 (commit e29e72f) | split octonions: the same 512 associator signs, signature (4, 4) | negative control for associator-only tests; SymPy symbolics | not the octonions; isotropic elements have no inverse; GPL |
| python-mathdunders | `mathdunders` | 0.4.2 | none | operator plumbing for python-hypercomplex | contributes no algebra evidence |
| python-pyoctonion | `pyoctonion` | 3.12 | identical table at D = 8 (doubling over pyquaternion) | a further independent octonion check | `cal_multiply` prints every product, use `*`; imports the undeclared pyquaternion; no license |
| python-octonion-sedenion | `Octonion_Sedenion` | 1.0.0 (wheel only) | identical tables at D = 8, 16 | a fourth independent sedenion table | `sedenion.py` imports the top-level `octonion`, which python-octonion owns, and fails as installed; no license |
| python-numpy-quaternion | `quaternion` | 2024.0.13 | identical table at D = 4 | quaternion arrays as a compiled numpy dtype | compiled: Kaggle takes the pinned wheel |
| python-quaternionic | `quaternionic` | 1.0.18 | identical table at D = 4 | numba quaternion arrays, rotations | `q[1]` on one quaternion raises; read `q.ndarray` |
| python-pyquaternion | `pyquaternion` | 0.9.9 | identical table at D = 4 | scalar rotation quaternions | the PyPI sdist lacks the VERSION.txt its setup.py reads; the recipe writes it |
| python-clifford | `clifford` | 1.5.1 | Cl(0,2) on (1, e1, e2, e12) identical at D = 4 | numerical geometric algebra: rotors, spinors, conformal GA | associative; `Cl(p, q)` puts the p positive squares first; numba compiles on first use |
| python-kingdon | `kingdon` | 3.0.0 | Cl(0,2) identical at D = 4 | geometric algebra on numpy, sympy or torch from one code path | product `keys()` are blade bitmasks; imports anywidget |
| python-galgebra | `galgebra` | 0.6.0 | Cl(0,2) identical at D = 4 | symbolic geometric algebra and calculus | a one-generator algebra needs coordinates; a scalar needs `sympy.S.One` |
| python-hyprat | `hyprat` | 0.2.0 (GitHub tag) | identical at D = 8, 16 (measured to 32) at mu = -1; signs (-1, -1, +1) give the split octonions | exact rational Cayley-Dickson algebras with a doubling parameter, Hurwitz quaternions | `Hy.from_array(coeffs, signs=...)` names the algebra, lowest level first |
<!-- algebra-circuit-rules:end -->

<!-- heron-execution-facts:begin -->
## Heron execution facts

The root AGENTS.md and gororoba_quantum/AGENTS.md carry this section with
identical bytes (gate core-250). The account reaches ibm_fez, ibm_kingston
and ibm_marrakesh, all Heron r2: 156 qubits, heavy-hex, native CZ, basis
cz, id, rz, sx, x and xslow. Heron r3 and Nighthawk (square grid) exist in
IBM's processor list and are absent from this account, so
`service.backends()` is the authority before a design names a backend.
`scripts/heron_target_snapshot.py --out` reads the live Targets into
`docs/evidence/heron_platform/targets.json`, and gates core-254 and core-255
recompute every per-backend fact below from it; a refreshed snapshot that
contradicts this section fails until the text changes with it. Measured
values and the documentation captures are in
`docs/notes/ibm_heron_platform.md`.

- **The Target is the timing authority.** dt is 4 ns and the timing
  constraints read granularity 1, min_length 2, pulse and acquire alignment
  1; a design reads them from the Target and assumes no 16-sample
  alignment. live_run.py binds them into the calibration identity.
- **Measurement variants.** `measure_2` (`MidCircuitMeasure`) is the shorter
  mid-circuit readout IBM recommends where supported, with a higher reported
  assignment error than `measure`. `reset` lasts exactly as long as
  `measure_reset` and `reset_2` as long as `measure_reset_2` on every qubit,
  so a reset is a measurement followed by a conditional flip. Switching
  variants changes the physical measurement and needs its own control; Aer
  lacks `measure_2`, so local simulation needs an explicit representation
  (QPU_EXECUTION_ROADMAP.md).
- **`xslow`** is a native 1 us X that shares its reported error with `x` and
  `sx` on every qubit; the preset transpiler at optimization levels 1 to 3
  never emits it, so it appears only where a circuit names it.
- **Dynamic-circuit limits** (execute-dynamic-circuits guide): one level of
  `if` with no nesting, no reset or measurement inside a conditional,
  operands of at most 32 bits, no loops, switch or arithmetic, and a
  per-job broadcast budget of about 300 broadcasts of 60 bits or 2400 of 1
  bit. `store` is a supported instruction from runtime 0.47.
- **Repetition delay** defaults to 250 us within `backend.rep_delay_range`,
  0 to 2 ms on all three; the range changes over time, so a design reads
  it. A lower delay raises state-preparation error, and `rep_delay` is one
  value per job.
- **Execution order.** Circuits iterate column-wise over shots; neither PUB
  order nor single-batch execution of a job is guaranteed, so adjacent
  entries of a shot array are not adjacent physical executions.
- **Billing** is QPU lock time with about 2 s of overhead per sub-job, and
  the service splits a job too large for its execution engine into
  sub-jobs. `scheduler_timing` and the compilation circuit time are
  schedule evidence, not billing. In job and batch mode a job cancelled or
  failed by user error bills what it consumed, preparation overhead
  included, and a system error bills zero; a session bills its active
  wall-clock time, idle time and failed jobs included.
- **Calibration** runs as roughly hourly monitoring interleaved with user
  jobs plus triggered recalibration, under two hours a day on Heron, so two
  jobs submitted together, or one job waiting in the queue, can execute
  under a calibration other than the one it was planned against.
  live_run.py checks calibration at each submitted batch, and `--collect`
  fetches `properties(datetime=...)` and `target_history(datetime=...)` at
  each PUB's execution start and replays under them, so the planning
  Target and the execution calibration are separate identities.
- **Fractional gates** (`use_fractional_gates=True`, experimental):
  `rzz(theta)` for 0 < theta <= pi/2 and `rx(theta)` for any theta; a bound
  parameter outside that range fails the job; Pauli twirling, PEC and PEA
  are unsupported with them and TREX is supported. Reported `rx` errors copy
  `sx` on every qubit, while `rzz` reports its own error on more than 90
  percent of pairs and can exceed `cz`. A fractional decomposition is an
  intervention with its own controls, never a silent substitution.
- **Stretch** (Qiskit 2.0 or later) resolves at compile time and adds any
  remainder to the first delay that uses it; the resolved values come from
  the experimental execution options `stretch_values` and
  `scheduler_timing`, and equal symbolic halves are checked against them.
- **Runtime 0.48 to 0.50.** 0.48 deprecates differing `pub.shots` across the
  PUBs of one job; 0.49 adds `MidCircuitReset` and
  `ConvertToMidCircuitResetAndMeasure`; 0.50 adds the client-side
  `executor_sampler.Sampler`, moves `max_execution_time` to the top level
  (live_run.py sets it there) and adds `XSlowGate`.

**Python stack on the build host.** requirements.txt and
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
<!-- heron-execution-facts:end -->
