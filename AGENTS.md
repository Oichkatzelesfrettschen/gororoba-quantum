# gororoba-quantum agent guide

This file carries the repository's own rules; the user-level agent guide
supplies what it leaves unstated. CLAUDE.md loads it.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only.

GitHub Actions runs every gate ([.github/workflows/ci.yml](.github/workflows/ci.yml)).
[ci/gates.json](ci/gates.json) lists each gate as one command with its
working directory; [ci/run_gates.py](ci/run_gates.py) runs a shard of them on
a thread pool sized to the runner's CPUs and keeps going past failures, so a
red shard lists every failing gate. Each gate records its measured seconds;
shards are assigned longest-first. Pull requests run the `pr` tier and affected
`full` gates on six shards;
pushes to main use the same selection on twelve shards. Nightly and manual
runs execute every gate on twelve shards. The changed-path selection follows
local Python imports and the dynamic data/source scopes in
[ci/full_gate_inputs.json](ci/full_gate_inputs.json). Every full gate declares
its non-imported inputs there, including source digests and JSON-selected
raw evidence; a missing declaration fails selection. CI and dependency-pin
changes select every gate, and an unavailable diff base runs the full suite.
Gate seconds are scheduling estimates, independent of tier membership.
[CI runtime analysis](docs/notes/build_host/ci-runtime.md) records the timing
denominators, measured bottlenecks and replay commands. Runners are 2-vCPU,
8 GB machines on Python 3.14
with the pins in requirements.txt and ci/requirements-ci.txt (mypy, ruff and
the plotting-only `matplotlib==3.11.2`). A pull request merges when every
shard and the `qi-stack` and `external-ground-truth` jobs are green and its
review threads are resolved; a red main or nightly run is fixed in the next
change. The `qi-stack` job applies the same changed-input selection to the gates
that ci/gates.json
tags `"requires": ["qi"]`, under the Quantum Inspire interpreter
([Quantum Inspire](#quantum-inspire)). The
`external-ground-truth` job runs `verify.py` over the open_gororoba commit
named in [ci/open_gororoba.pin](ci/open_gororoba.pin):
`ci/fetch_open_gororoba.sh` sparse-checks out the paths it is given, and
`scripts/materialize_gororoba_csv.py` rewrites the git-ignored `data/csv`
files from the registry records, whose sha256 pins `verify.py` rechecks. A
pin bump is a reviewed commit. A new module, evidence replay or contract
joins the gate list in ci/gates.json in the same change.
The lint and type gates (core-000, core-001, core-002, core-039) cover
gororoba_quantum/, scripts/, ci/ and kaggle_kernel/ whole, so a module there
is linted and type-checked without a list edit; a checked file elsewhere in
the tree, such as an evidence replay under results/ or docs/, is named in
those gates' commands.

Gate commands invoke `"$PYTHON"`. ci/run_gates.py sets it to its own
interpreter when the environment leaves it unset, and sets
`GOROROBA_WORKERS=1` the same way. A gate command run outside run_gates.py
needs `PYTHON` exported (`export PYTHON="${PYTHON:-python3}"`): a variable
assigned without `export` expands empty in the child shell, and every gate
then exits 127 in 0.0 s with `/bin/sh: line 1: : command not found`, which
reads as a gate failure.


Every CPU-bound loop over independent items (embedding scores in replica
placement, operator checks, registry parsing, exact certificates, synthesis
searches) runs through parallel.py, an order-preserving process pool started
with spawn on every platform, so a parallel run returns exactly what the
serial loop returns; a serial loop over such items is a defect review
rejects. Items that share a seeded generator draw every item's inputs first,
in the generator's order, and then map, so pooled and serial runs write the
same bytes. The worker count comes from the host the process runs on:
`parallel.available_cpus()` takes the scheduler affinity mask bounded by the
CPU quota of the process's cgroup and every ancestor, so the build host, a
CI runner and a Kaggle kernel each use every CPU they grant.
`GOROROBA_WORKERS=N` caps the worker count and `GOROROBA_WORKERS=1` runs
serially; the default (`parallel.default_threads()`) also sets
`--simulation-threads`. A search too long for one host shards by item range
across Kaggle CPU sessions (five run concurrently), each running the same
pool, and merges the shard records in index order. Aer runs batch
every replica of a choice in one call and parallelize experiments itself.
`ci/run_gates.py --device GPU` exports `GOROROBA_AER_DEVICE=GPU` to every
gate, so a local run computes the simulation replays on the GPU while CI's
runners keep the CPU; a gate that passes locally and fails on CI exposes a
device-dependent result. Contracts that compare seeded shot counts keep
Aer's CPU sampler, whose counts their records retain.

A classical estimator evaluated over many synthetic replicates (a null
calibration, a parametric or resampling bootstrap) is batched across
replicates with numpy before it is pooled or sharded: one call fits a block
of replicates, and parallel.py maps the blocks. The scalar form stays as the
reference that analyses call, and a gate proves that the batched path
returns the reference's bits on the record's own streams and on adversarial
inputs. The bits agree when the batched code keeps the scalar arithmetic
order, repeats builtin `sum()`'s Neumaier compensation, and sends every
replicate-dependent `exp` and `** 2` through `math.exp` and `math.pow`;
[vectorized-fits.md](docs/notes/build_host/vectorized-fits.md) gives the
rules, the equivalence gates and the measured speedup.

A change to live_run.py or experiments.py also gets a dry run,
`"$PYTHON" live_run.py --out ../results/live`, whose audit record lands under
results/live/.

The matched diagnostic families and statistical design contracts are documented
in [QPU_OPTIMIZATION.md](gororoba_quantum/QPU_OPTIMIZATION.md). Their local
gates exercise exact labeled laws, bounded inference, fake-backend layouts,
aggregate budgets, and negative dry-run records; hardware claims require
separately approved results.

The independently admitted packed ripple and rank-sector families are described
in [PACKED_ALGEBRA.md](gororoba_quantum/PACKED_ALGEBRA.md). `--native-dry-run`
calls Runtime with `dry_run=True` and retains mock timing in a separate sidecar.
Mock outcomes never enter scientific analysis or measured visualizations.

The measured folded-job figure uses `results/ripple/folded-job-review.json`.
After changing its renderer, run `"$PYTHON" scripts/render_folded_job_review.py
--png results/ripple/folded-job-review.png --check` from the root. Independent
raw replay uses `"$PYTHON" scripts/review_folded_jobs.py --run-dir "$FOLDED_RUN"
--check`, with `FOLDED_RUN` pointing to the retained archive in hardware
[evidence PR #37](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/37).
The raw archive remains owned by that evidence change.

The N=21 target-flip certificate gets a fresh Rocq compile and kernel check
when its generator, witnesses, or evaluator changes. Run the checks on a copy
under temporary storage so the checkout retains source files only:

```sh
(
  set -eu
  proof_tmp="$(mktemp -d)"
  cp proofs/TargetFlipN21.v "$proof_tmp/"
  (cd "$proof_tmp"
    rocq compile -q -w +all TargetFlipN21.v >compile.log 2>&1
    if rg -n "Warning:" compile.log; then exit 1; fi
    rocq check -silent -o TargetFlipN21)
)
```

The certificate proves finite Boolean permutation action. Operator checks in
modular_arithmetic.py establish Qiskit phase and clean-workspace behavior.

Changes to `proofs/FoldAverageDescent.v`, `proofs/TerminalChannelSeparation.v`,
`proofs/TerminalChannelSeparationReal.v`, or their receipts also run
`ROCQ="${ROCQ:-rocq}" sh docs/evidence/formal_certificates/replay_rocq.sh` with the
toolchain its `toolchain.txt` pins, Rocq 9.2 with OCaml 5.5.0. The replay compiles in temporary storage,
treats warnings as errors, kernel-checks, and compares raw assumptions.
The [bundle](docs/evidence/formal_certificates/README.md) distinguishes
real foundations, deterministic interval premises and unproved coverage.

The recovered wide-control acquisition uses
`scripts/review_wide_control_job.py --check` and `--self-test`, each in
normal and optimized Python. `scripts/reconcile_qpu_inventory.py --check`
binds the complete recorded service inventory to every raw job archive and
the account's consumed seconds to the final charges of the jobs that ran
inside its rolling usage period; its synthetic contract rejects
missing/duplicate jobs, altered denominators, off-window chronology and raw
corruption. `scripts/inventory_retained_runs.py` requires every job id a
runner record or retention file names to belong to that inventory, and
mock and local artifacts to declare no QPU execution. These replays and
measured extraction/render checks join `ci/gates.json`.

Changes to the C881 proof sources or receipts also run the pinned Rocq
procedure in `docs/evidence/c881_exhaustive/README.md`. The CI receipt
check verifies retained hashes. The ci.yml job `rocq-replay` replays the
formal_certificates, c881_exhaustive, folding_proofs and TargetFlipN21
bundles under the opam switch of `ci/rocq_toolchain.pin` (Rocq 9.2.0 on OCaml
5.5.0) on a pull request that touches `proofs/`, a replay bundle, the replay
driver, a pin or the workflow (`ci/rocq_changed.sh` holds the path list), and
adds the stiefel_witness bundle on pushes to main and the nightly schedule.
Gates core-403 and core-404 hold the pin, the toolchain.txt banners, the path
list and the open_gororoba fetch in agreement. The manual procedure remains
the local replay. A pull request merges when `rocq-replay` is green whenever
it ran.

## Source library and research replay

`docs/` owns source notes, retained PDFs, retrieval identities and research
replays. `literature -> docs` preserves recorded paths; new Markdown links use
`docs/`. Immutable source ledgers retain their recorded bytes. The
`sources` suite in ci/gates.json covers the source registry, the evidence
replays (normal and optimized modes) and their checksum ledgers.


Changes to proof replay inputs also follow the pinned Rocq replay in
`docs/evidence/folding_proofs/README.md`. Imported paper parser diagnostics
remain source limitations in the registry; checksum admission preserves the
original bytes and differs from a fresh mathematical proof check.

## Mandatory source and hardware grounding

All architectural design, code synthesis, circuit optimization, and review decisions
must be strictly grounded in verified repository sources rather than inferred or
approximated from external generalizations. Never guess or estimate hardware
specifications, timing budgets, algebraic conventions, or mathematical invariants.

Grounding binds all operations through two authoritative pillars:

1. **Heron r2 Hardware Documentation and Live Snapshots.**
   The repository maintains authoritative hardware definitions and execution constraints:
   - `docs/notes/ibm_quantum/`: Transcribed reference documentation covering processor
     families (`processor-types.md`), backend details and basis instruction sets
     (`qpu-information.md`), transpilation to ISA circuits (`transpile.md`), pass
     managers (`transpile-with-pass-managers.md`), transpiler stages (`transpiler-stages.md`),
     dynamic circuits and mid-circuit measurement (`execute-dynamic-circuits.md`),
     native fractional gate limits (`fractional-gates.md`), stretch delays (`stretch.md`),
     circuit timing (`qiskit-runtime-circuit-timing.md`), repetition rates and shot loops
     (`repetition-rate-execution.md`), calibration cadence (`calibration-jobs.md`),
     and execution time estimation (`estimate-job-run-time.md`).
   - `docs/notes/ibm_heron_platform.md`: Measured platform targets, timing alignments,
     instruction variants (`measure_2`, `reset_2`, `xslow`), and fractional-gate error
     evaluations across `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh`.
   - `docs/evidence/heron_platform/targets.json`: Complete, machine-readable Target
     snapshots across all 156 qubits and 352 coupling pairs.

2. **Mathematical Papers, Notes, and Formal Proofs.**
   The repository contains exact algebraic specifications, proof certificates, and
   literature records:
   - Primary research notes in `docs/notes/` and hosted/local papers in `docs/pdf/`
     and `docs/local_source_cache/` (indexed in `docs/INDEX.md` and `docs/SOURCES.json`).
     When mathematical derivations require broader context, follow the linked arXiv
     version of record directly.
   - Proof certificates in `proofs/` and verification evidence in `docs/evidence/`
     (including Rocq formal certificates for `TargetFlipN21`, `FoldAverageDescent`,
     `TerminalChannelSeparation`, and `C881`).
   - Sedenion, octonion, and Cayley-Dickson multiplication conventions codified in
     `gororoba_quantum/cd_core.py` and the Algebra Circuit Design Rules below.

Every module, test contract, and hardware execution plan reflects these recorded sources.
When an algebraic sign, gate duration, layout connectivity, or error rate is needed, code
directly imports or validates against the registered repository artifact.

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

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- Simulations of 14 qubits or fewer run on Kaggle kernels through
  `scripts/kaggle_run.py` (`push`, `status`, `collect`), which bundles the
  entry's repository imports with `kaggle_kernel/` (the kernel program and
  its AGENTS.md), installs qiskit 2.5.2 and qiskit-ibm-runtime 0.50.0 with
  qiskit-aer 0.17.2 (or qiskit-aer-gpu-cu11 0.17.2 on a GPU), proves the
  hypercomplex package stack before the entry runs, and retains the output
  under results/kaggle/.
  A kernel runs on a CPU machine by default and on a GPU only when its
  widest density matrix reaches `local_compute.GPU_MIN_ACTIVE_QUBITS`;
  [Simulation on Kaggle](#simulation-on-kaggle-cpu-gpu-and-ci-replay)
  gives the machine choice, the GPU setup and the CI replay rules.
  `kaggle_run.py shards` replicates the CI gate shards for a commit on
  Kaggle CPU kernels in place of the build host. `docs/notes/kaggle/` holds the workflow, the measured
  substrates and the package-stack guide. Kaggle allows two concurrent GPU
  and five concurrent CPU batch sessions per account.
- A 15-qubit run is decision-gated: it waits for the user's approval of a
  written case, which names its substrate from the access inventory and
  says why that one answers the question.
  - Simulation: an optimized Aer run on the build host or on a Kaggle
    T4 x2. `SnapshotSimulator.run` cache-blocks the state across both T4s,
    and a 15-qubit density matrix takes about 4 s there
    (`docs/notes/kaggle/substrates.md`). The case's run first applies
    `docs/notes/kaggle/gpu-runbook.md`: local rehearsal, vectorized
    estimators, a sized timeout.
  - Hardware: Tuna-17 through Quantum Inspire, under its submission rules
    (Quantum Inspire below). `submit` refuses while any hardware job of the
    account is unfinished or ended under `HARDWARE_PAUSE_SECONDS` ago, so
    the run cannot overlap another session's job. Fifteen of 17 qubits
    include qubits the Tuna-17 notes exclude for readout or coupler faults
    (`docs/notes/quantum_inspire/experiments.md`), so the case names each
    one it uses.
- IBM hardware serves 16 or more qubits, or a smaller run whose question
  concerns the device itself (a named qubit's readout, detuning or drift);
  its case states why Aer cannot answer it.
- A kernel's
  noise comes from a retained `gororoba_quantum/calibration_snapshot.py`
  export, whose `--export` requires every gate and readout channel to equal
  live_run's noise model, and a Kaggle result enters the research state
  only through a CPU replay gate on a reduced case.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. The case is written against a submit-free dry run, and the
  `--submit` command names that run with `--approved-record`, its record.json
  digest with `--approved-record-sha256`, and the case's seconds with
  `--max-execution-seconds` (the Sampler's max_execution_time, which the
  service enforces; the dry run is made with the same value, since the
  policy carries it). `--max-total-execution-seconds` caps the sum of all
  job ceilings, and `--reserve-seconds` names the retained quota. The fresh
  plan must match the record in experiment
  digest, shots, policy (twirling, DD, budget floor, execution ceiling),
  dependency versions, IBM Cloud instance, groups, backends, seeds, layouts,
  replica qubits, fused PUB manifests, calibration at the refresh and again
  at each batch, and QPY bytes, or the run writes an `approval_required`
  record and sends nothing. The submission plans only over the backends the
  approved record found eligible (`live_run.approved_backend_scope`), so a
  backend whose queue or status changed after the dry run cannot enter the
  plan; an approved backend that turns ineligible still refuses through the
  comparison. `--exclude-qubits BACKEND:Q[,Q|A-B...]` withholds named qubits
  from placement whatever their calibration; the policy records it, so the
  approval binds it, and every snapshot, the per-batch one included,
  applies it. The first batch consumes the approval by writing
  `approval-consumed.json` into the approved record's directory, so a second
  invocation on the same record sends nothing. Calibration reads,
  transpilation, noise simulation, result retrieval, and `--preserve-raw`
  need no approval.
- Calibration is a property of the run. live_run.py fetches each backend's
  Target and properties afresh in the process that decides, compiles,
  simulates, and submits; no calibration value is cached or read back from a
  file to drive a submission.

## Simulation on Kaggle: CPU, GPU and CI replay

`"$PYTHON" scripts/kaggle_run.py push ENTRY --slug SLUG -- ARGS` runs a
repository script on a private Kaggle kernel, and `status` and `collect`
retain its output under results/kaggle/. The kernel's own guide is
`kaggle_kernel/AGENTS.md`. The measurements behind the choices below are in
`docs/notes/kaggle/substrates.md`
(`results/kaggle/2026-10-16T204620Z-gororoba-aer-gpu-probe`).

- **Machine.**
  - CPU, the default: every noisy simulation whose widest density matrix
    stays below 11 qubits, and every small dynamic circuit.
  - GPU (`--machine NvidiaTeslaT4`, two T4s): density matrices of 11 to 14
    qubits and statevectors up to 29 qubits per T4.
  - Measured on the 7-qubit N=21 order-finding circuits: statevector
    trajectories took 2.8 and 36 ms per shot on the CPU against 21.7 and
    54.6 ms on a T4.
  - A dynamic circuit's density matrix evolves per shot, about 160 times
    slower than trajectories of the same channel.
- **A GPU push.** It carries `--timeout SECONDS` sized to the work, and
  kaggle_run.py refuses an accelerator push without one. Read `kaggle quota`
  before and after; the weekly 30 h resets at 00:00 UTC on Saturday. Two GPU
  sessions run at once, and a version is never repushed while it runs. For
  example:

  ```sh
  "$PYTHON" scripts/kaggle_run.py push --slug NAME --machine NvidiaTeslaT4 \
      --timeout 3600 --include SNAPSHOT.json scripts/ENTRY.py -- ARGS
  ```

- **Inside the entry.**
  1. The kernel installs qiskit-aer-gpu-cu11 0.17.2 and sets
     `GOROROBA_AER_DEVICE=GPU`, and `calibration_snapshot.aer_device()`
     reads it.
  2. `calibration_snapshot.noise_simulator(snapshot, device,
     method="density_matrix" | "statevector")` builds live_run's noise
     channels.
  3. `snapshot_laws.restrict_circuit(isa)` with `restrict(snapshot, qubits)`
     keeps the circuit and the noise model at the active width.
  4. `set_options(max_parallel_threads=parallel.workers())` uses every host
     CPU.
- **cuStateVec.** `noise_simulator(..., custatevec=True)` sets Aer's
  `cuStateVec_enable` on a GPU statevector or density-matrix run, and
  `GOROROBA_AER_CUSTATEVEC=1` sets it for every GPU call that leaves
  `custatevec` unset (`calibration_snapshot.aer_custatevec`). qiskit-aer-gpu-cu11 0.17.2
  links libcustatevec.so.1 and libcutensornet.so.2, which `cuquantum-cu11`
  24.8.0 and `cutensor-cu11` 2.2.0 (`KERNEL_PINS` entries) supply. Aer
  0.17.2 reports `cuStateVec_enable` False when `batched_shots_gpu` is also
  set.
  `scripts/aer_gpu_probe.py --workloads n21 --configurations
  cpu_statevector,gpu_statevector_unbatched,gpu_statevector_custatevec` records the three paths
  with Aer's reported `cuStateVec_enable`. On the T4 x2 (gate core-450)
  cuStateVec ran the dynamic density matrix 1.44 and 1.63 times faster than
  the plain GPU executor at 7 and 10 qubits and statevector trajectories
  1.19 to 1.29 times slower, and Aer spread per-shot and batched runs over both
  GPUs (`docs/evidence/aer_gpu_configuration/README.md`).
  `docs/notes/kaggle/custatevec.md` holds the kernel's library chain and
  the T4 check, and `docs/notes/build_host/custatevec.md` the host build.
- **Batched GPU shots.** On a GPU `noise_simulator` enables Aer's
  `batched_shots_gpu` by default for circuits of at most
  `BATCHED_SHOTS_MAX_QUBITS` (10) active qubits, and `batched_shots=False`
  opts out. `SnapshotSimulator.run` runs any circuit with control flow
  unbatched: the batched executor rejects `jump`, and with if_else lowered
  to bfunc-conditioned gates it evaluates the condition before the readout
  channel. Shot branching is never enabled, since Aer 0.17.2's shot
  branching drops a mid-circuit measurement's readout channel
  (`docs/evidence/aer_gpu_configuration/README.md`).
- **Cache blocking.** `SnapshotSimulator.run` blocks a GPU batch whose
  widest active state exceeds one GPU's memory, Aer's own trigger, with
  `calibration_snapshot.blocking_qubits_for`'s chunk (27 statevector, 13
  density-matrix qubits on a T4) and `max_parallel_shots=1`, so every run
  that fits one GPU keeps its executor and counts. On the T4 x2 a 15-qubit
  density matrix ran in 4.2 s and a 30-qubit statevector in 7.2 s across
  both GPUs, where Aer's automatic choice filled host memory until the OOM
  killer ended it. if_else aborts under blocking, so a blocked batch runs in
  `lower_conditionals` form and raises ValueError where none exists; Aer's
  CPU chunk executor misplaces conditions, so blocking stays on the GPU
  (gates core-451 and core-452, `docs/notes/kaggle/substrates.md`).
- **CI replay.**
  - Seeded GPU counts differ from CPU counts, so a gate re-derives a GPU
    record from its retained counts and never resamples on CI.
  - An entry whose output a CI gate recompiles is pushed with `--ci-env`,
    on a CPU or a GPU machine. The kernel then builds CI's Python 3.14.7
    with `ci/install_pins.sh` and runs the entry under CPU Aer, because the
    image's Python 3.13 and numpy 2.1.3 change compiled depths and
    durations.
  - Replays hold routed CZ, layout and classical stages exact, and depth
    and duration within a relative 0.002 across BLAS builds.
- **Pinned GPU environment.** `push --gpu-env` on `NvidiaTeslaT4` runs the
  entry in a venv on the image's Python 3.13, the newest Python the cu11
  wheel ships, holding requirements.txt and ci/requirements-ci.txt with
  `GPU_ENV_AER_PINS` in qiskit-aer's place (`ci/install_pins.sh` with
  `AER_PINS`).
  - Before the entry, `kernel_main.gpu_interpreter` requires every pin at its
    version, qiskit-aer-gpu-cu11 as the only owner of
    `qiskit_aer/__init__.py`, both T4s in nvidia-smi, and seeded Bell runs
    on the GPU that report device GPU, the cuStateVec one with
    `cuStateVec_enable` true.
  - A miss lists its reasons under `failures` in gpu_env.json, and the kernel
    exits 4 without running the entry.
  - `aer_gpu_probe.py --require-gpu` then stops at the first row that leaves
    the GPU.
  - Only Python itself differs from CI's 3.14.7.
  - On a CPU machine the same push stops at the preflight, which proves the
    error path at no GPU cost.
- **Sessions.** Five CPU and two GPU batch sessions run per account. A GPU
  machine's four host CPUs run CPU work, `--ci-env` included, when the CPU
  pool is full, at the price of GPU quota.

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
| python-ruff, mypy | newer than the CI pins ruff 0.14.11 and mypy 1.19.1; `uvx ruff@0.14.11` reproduces CI formatting |

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
and install commands and the probe results. A Kaggle kernel installs qiskit 2.5.2,
qiskit-ibm-runtime 0.50.0 (its fake backends, such as FakeFez, need no
account) and qiskit-aer-gpu-cu11 0.17.2 (the CUDA 12 `qiskit-aer-gpu` wheel
stops at 0.15.1) over the Kaggle image's numpy and scipy, records every
version in `environment.json`, and holds no IBM credential
(`kaggle_kernel/AGENTS.md`).
<!-- heron-execution-facts:end -->

## Quantum Inspire

Quantum Inspire (QuTech, TU Delft and TNO) is the second hardware service the
repository reaches: one free account type with access to every listed
hardware and emulator backend. [docs/notes/quantum_inspire/](docs/notes/quantum_inspire/README.md)
holds the guides, the captured knowledge base, cQASM specification, SDK
documentation, release notes and OpenAPI description; the live pages at
https://www.quantum-inspire.com/kbase/ stay the authority because they change.

**Environment.** The quantuminspire SDK requires Python < 3.14 and
qiskit-quantuminspire caps Qiskit below 2.4, so the Quantum Inspire stack
lives in its own environment, never in the repository's Python 3.14 stack:
`QI_ENV=$HOME/.local/share/quantuminspire/venv`, interpreter
`QI_PYTHON=${QI_PYTHON:-$QI_ENV/bin/python}`, built with
`uv venv --python 3.13 "$QI_ENV"` and
`VIRTUAL_ENV="$QI_ENV" uv pip install -r docs/notes/quantum_inspire/requirements-qi.txt`.
No Arch package carries the stack. CI's `qi-stack` job installs the lock
exactly (`pip install --no-deps` and `pip check`) under Python 3.13.15 beside
Python 3.14.7 and exports `QI_PYTHON`; there qxelarator, libqasm and
OpenSquirrel run locally with no credential, and no SDK call reaches the
network. gororoba_quantum/qi_stack.py reads `QI_PYTHON` from the environment
alone and probes it once per process for the three modules at the lock's
versions. A gate tagged `"requires": ["qi"]` compares a live run with its
retained record where that probe passes; everywhere else (the gate shards,
premerge, Kaggle shard replicas, a shell that has not exported `QI_PYTHON`)
it replays the record and prints one line naming the replay.
`ci/run_gates.py --requires qi` runs the tagged gates alone with
`GOROROBA_QI_REQUIRED=1`, which makes a replay a failure.

| Package | Version | Role |
|---|---|---|
| quantuminspire | 4.1.0 | `qi` CLI, `quantuminspire.api.Api`, OAuth device login |
| qi-compute-api-client | 0.63.0 | generated client of the compute job manager REST API |
| qiskit-quantuminspire | 0.18.5 | `QIProvider`, Qiskit backends, cQASM writer (per-qubit barriers) |
| qiskit | 2.3.1 | the newest release below the provider's < 2.4 cap; the repository runs 2.5.2 |
| opensquirrel | 0.9.1 | compiler: decomposition, mapping, routing, ALAP scheduling |
| libqasm | 1.2.1 | cQASM 3.0 parser and analyzer |
| qxelarator | 0.10.0 | local QX state-vector emulator |
| mcp | 2.3.0 | MCP server SDK for scripts/qi_mcp_server.py |

pennylane-quantuminspire 0.15.5 (PennyLane >= 0.43, < 0.46) is not
installed. The community bridge quantum-vibecoding-mcp 0.1.0 imports
quantuminspire 3.x and mcp 1.x modules absent from these pins and is not
used; scripts/qi_mcp_server.py serves the same role on SDK 4.1.

**Login.** `"$QI_ENV/bin/qi" login` runs the OAuth device flow: it prints a
verification URL and code that the user approves in a browser, then stores
access and refresh tokens in `~/.quantuminspire/config.json`, which the CLI
writes mode 644; `chmod 600` it after login, and scripts/qi_platform.py's
client narrows it to mode 600 before reading it. The
access token lives 3600 s; scripts/qi_platform.py renews it before expiry.
The SDK exchanges the refresh token only within 5 s of access-token expiry,
and its `refresh_tokens` keeps the rotated tokens in memory only. Every
process on the account read invalid_grant after one such expiry (2026-10-17,
two sessions and several MCP servers live); rotation with reuse detection is
the inferred mechanism, unconfirmed by a probe. `Client.refresh` therefore
holds an flock on `~/.quantuminspire/config.json.lock`, rereads the file,
exchanges only near expiry and writes the rotated tokens back atomically. A
long-lived process (an MCP server) started before that rule restarts before
QI work resumes.
An agent that finds no login prompts the user to run `qi login` and approve
the code; tokens never enter a commit, a log or memory.

**Backends.** `scripts/qi_platform.py snapshot --out docs/evidence/quantum_inspire`
reads the account's catalogue and ledger; gate core-347 renders this table
from the retained catalogue and fails when either changes alone:

<!-- quantum-inspire-facts:begin -->
| Backend type (id) | identifier | is_hardware | qubits | couplings | shots default / max | job limit (s) | jobs per batch | batch jobs queued |
|---|---|---|---|---|---|---|---|---|
| QX emulator (1) | QXsinglenodesimulator | false | 10 | 45 | 1024 / 2048 | 3600 | 5 | 5 |
| Tuna-5 (4) | tuna_5 | true | 5 | 4 | 8192 / 131072 | 300 | 5 | 5 |
| Ry emulator (5) | Rydberg | true | 9 | 36 | 1024 / 1024 | 3600 | 5 | 5 |
| Tuna-9 (6) | tuna_9 | true | 9 | 12 | 8192 / 131072 | 300 | 5 | 5 |
| Tuna-17 (7) | tuna_17 | true | 17 | 24 | 8192 / 131072 | 300 | 5 | 5 |

Backend instances: QX emulator (Cloud), Spin-2+ (TU Delft), Starmon-7 (TU Delft), Tuna-5 (TU Delft), Ry emulator (TU/eindhoven), Tuna-9 (TU Delft), Tuna-17 (TU Delft).
<!-- quantum-inspire-facts:end -->

Status, queue length and heartbeat change between reads and live only in the
snapshot. Spin-2+ and Starmon-7 appear as backend instances without a backend
type this account can submit to.

**Execution facts.**
- Tuna: native single-qubit gates last 20 ns, CZ 60 ns, measurement 800 ns,
  initialization 200 or 500 us; H, CNOT and SWAP are decomposed, the other
  gates of the tuna dialect are native; rotation angles quantize to
  multiples of pi/36; the compiler passes decompose only, so a circuit runs
  in the gate order written; OpenSquirrel schedules as late as possible,
  `wait(n)` idles n cycles of 20 ns, and mid-circuit measurement is allowed
  while binary-controlled gates are not, so feed-forward is applied in
  post-processing ([tuna-17-run-design.md](docs/notes/quantum_inspire/tuna-17-run-design.md)).
- Bit order: QX and Tuna results put qubit 0 at the rightmost character; the
  Ry emulator puts it at the leftmost (an X on q[0] read `10` in all 1024
  shots). An analysis states the order of the backend it reads.
- The Ry emulator takes no measurement statements and measures every qubit
  at the end; a circuit that declares a bit register compiles remotely and
  fails at execution with the job message "error interpreting cQASM script"
  (its log stays empty), while H, CNOT, Z, S and Rz run in a circuit without
  one ([ry-emulator.md](docs/notes/quantum_inspire/ry-emulator.md)).
- The Qiskit provider writes a multi-qubit barrier as per-qubit barriers, so
  a timing-sensitive case writes cQASM directly with explicit `wait`.

**Usage and cost.** The account's transaction ledger (`/transactions/`,
`qi_platform.py snapshot` writes usage.json) recorded no entry for the
forty-two jobs of 2026-10-16 on QX, the Ry emulator and Tuna-17, so no metered seconds
or credits apply to this account as observed; the limits are structural: the
table's qubits, shots, per-job execution limit and batch and queue counts,
plus the FAQ's three queued jobs per hardware backend, which is stricter than
the API's five batch jobs. Tuna-17 execution time fits 2.9 s per job plus
0.51 ms per shot over the retained jobs, so a 16384-shot job takes about 11 s
and the 120 s pause, not the shots, sets a batch's cost; QX finished 2048
shots in 0.03 to 10.4 s.
Calibration and tuning run between user jobs (Tuna-17 read `calibrating`
between two reads minutes apart), delay queued jobs and charge the account
nothing. The general conditions license every uploaded algorithm, datum and
code to QuTech for its own and third-party use, so nothing confidential is
submitted.

**Submission.** A Quantum Inspire hardware or emulator submission waits for
the user's approval of a written case, like an IBM run, though it spends no
metered quota. `"$QI_PYTHON" scripts/qi_platform.py submit CASE_DIR
--backend-type-id N --approval TEXT` verifies every circuit against its
cases.json digest, refuses an offline backend or a limit breach, records the
approval in submission.json and sends one batch; `collect CASE_DIR` writes
the raw shots, job records and charged transactions. On hardware a batch
holds at most three circuits and goes in only when none of the account's
batches is queued, so at most three jobs are ever queued (the FAQ's limit
under either reading of "job"); a series runs a QX dry run first, then
submits each hardware batch only after the previous one is collected, passes
its sanity checks and a pause. `submit` also refuses a hardware batch while
any job of the account on a hardware backend type (`is_hardware`, whichever
session submitted it) is unfinished or finished less than
`HARDWARE_PAUSE_SECONDS` = 120 s ago, so sessions that share the account
alternate with that pause and the platform can calibrate between batches;
emulator batches skip the check. The case generators emit each experiment as
a series of `batch-NN/` cases within that limit, and
`scripts/check_qi_platform_retention.py` passes every generated batch through
submit's checks up to the first request. Runs live under
results/quantum_inspire/runs/. A question about the Tuna devices themselves
(their crosstalk, coherent error, readout) is a hardware question; any
simulation of 14 qubits or fewer still runs on Kaggle.

**MCP.** scripts/qi_mcp_server.py, registered at user scope as
`quantum-inspire` for Claude Code and `quantum_inspire` for Codex, serves
catalogue, queue, hardware status, usage ledger, jobs, results and local
qxelarator emulation as read tools and asks before qi_compile (creates remote
resources) and qi_submit_case (executes through the retained-case runner).
The legacy raw-string qi_submit refuses execution. Failures return isError with the
service's message.

**Gates.** core-346 (`capture_qi_docs.py --check`), core-347
(`qi_platform.py check docs/evidence/quantum_inspire --agents AGENTS.md`),
core-327 (`qi_crosstalk_teleport_cases.py --check results/quantum_inspire/cases`),
core-331 (`--replay` of every retained analysis.json), core-348 and core-330
(`qi_zero_divisor_cases.py --check` and `--replay`), core-332 and core-333
(`qi_coupler_zz_map.py` case regeneration with conformance, and the replay of
the coupler map, its QX dry run and the spectator split), core-362
(`qi_readout_ringdown_cases.py` case regeneration with the post-readout
tail and excitation conformance), core-369 (the replay of its QX dry-run
analyses), core-368 (`qi_toolchain_check.py --check`: the libqasm and
OpenSquirrel record names every current case circuit at its sha256, and
under the stack the record regenerates byte for byte), core-527 and core-423
(`box_kite_qx_sweep.py --replay --live N`: the sweep records replay, and
under the stack 24 evenly spaced family a circuits plus each sub-family's
first rerun on qxelarator at their recorded seeds and must reproduce the
retained counts exactly; core-423 adds 8 family de circuits on the full tier),
core-499 (`n21_qx_conformance.py --check --live 0`: under the stack every
reset probe, deferred state and native branch run reruns on qxelarator at its
retained seed and must equal the retained result; each of the 36 sample jobs
takes minutes, so `--live N` adds N of them by hand and `--live 36` all), and
core-340 (`qi_ibm_noise_replay.py --check`, the Kingston-noise replay of
the Tuna-17 cases).

## Open Quantum

Open Quantum (Quantum Rings; Public Compute through qBitTensor Labs) is the
third hardware service: one account brokers IonQ, Rigetti, IQM and AQT
processors through a management API and a scheduler API.
[docs/notes/open_quantum/](docs/notes/open_quantum/README.md) holds the guide,
the captured documentation, site, terms and privacy pages, the PyPI release
records and the environment lock; the live pages at
https://docs.openquantum.com/ stay the authority because they change.

**Environment and key.** openquantum-mcp 0.2.0 requires `mcp<2`, so the stack
lives in its own environment: `OQ_ENV=$HOME/.local/share/openquantum/venv`,
interpreter `OQ_PYTHON=${OQ_PYTHON:-$OQ_ENV/bin/python}`, built with
`uv venv --python 3.14 "$OQ_ENV"` and
`VIRTUAL_ENV="$OQ_ENV" uv pip install -r docs/notes/open_quantum/requirements-oq.txt`
(openquantum-sdk 1.0.0, openquantum-mcp 0.2.0, openquantum-sdk-qiskit 1.0.0,
qiskit 2.5.2). The SDK key is `~/.config/openquantum/sdk-key.json`
(`{client_id, client_secret}`, directory 700, file 600), outside every
checkout; each consumer names it by path through `OPENQUANTUM_SDK_KEY`, so the
secret never enters a registration, command line, log, commit or memory. CI
never imports the stack: its gates read retained JSON with the standard
library.

**MCP.** `openquantum` is registered at Claude Code user scope and in
`~/.codex/config.toml` as `"$OQ_PYTHON" -I -m openquantum_mcp` with
`OPENQUANTUM_MCP_MAX_CREDITS=1`. Claude allows and Codex approves the ten
read tools (organizations, credits, backends, categories, jobs, waiting,
results, calibration); `prepare_job`, `submit_job` and `cancel_job` ask
every time. `prepare_job` uploads the circuit, and the server's spend policy
submits a Public job that Spark covers within the cap without
`confirm_spend`, so the harness prompt is the human approval.

**Submission.** Every upload and every job waits for the user's approval of
a written case, like an IBM or Quantum Inspire run: what it measures, why a
noise simulation cannot answer it, backend, shots, the quoted credits from
`oq_platform.py`'s estimate, and the statement that the circuit becomes
public. A Spark-funded run uses `execution_plan="public"` and
`queue_priority="standard"` in both `prepare_job` and `submit_job`. The
Public tier makes circuits and results non-confidential: they go to
independent qBitTensor Labs operators, Quantum Rings retains them for any
use including AI training, holds a perpetual sublicensable license and may
retain them indefinitely (`site/quantumrings_privacy.md`,
`site/quantumrings_terms.md` sections 5.2 and 6.4), and published research
derived from Public Compute credits Quantum Rings and Open Quantum
(section 3.4, `site/citation.md`). Unpublished methods stay off it.

**Credits.** A job costs `ceil(per_task + shots * per_shot)` credits of its
plan's USD-equivalent rates, one credit per USD-equivalent dollar, plus a
Priority surcharge; `oq_platform.py check` holds every retained estimate to
that rule. Spark Credits pay the Public plan only, arrive as 25 credits at
signup and as a 25-credit batch every 90 days that is claimed by hand on
the free-credits page, and expire 90 days after grant; the site's "$50"
equals 25 credits of work at the Private rate, twice the Public rate. An
organization holds at most 10 active Public jobs, a QASM file is at most
10 MB, and only a Pending job cancels.
`"$OQ_PYTHON" scripts/oq_platform.py snapshot --out docs/evidence/open_quantum`
refreshes the catalogue and the circuit-free estimates; gate core-382
renders this table from them and the captured price list and fails when
either changes alone:

<!-- open-quantum-facts:begin -->
| backend (short code) | provider, modality | qubits (per job) | native ops | shots min / default / max | circuits per job | Public USD task + per shot | Public credits at 128 / 1024 / max shots | shots in a 1-credit job | 1024-shot jobs per 25 Spark |
|---|---|---|---|---|---|---|---|---|---|
| IBEX Q1 (`aqt:ibex-q1`) | AQT, Trapped-ion | 12 | prx, rz, xx | 1 / 100 / 2000 | 1024 | 0.18 + 0.0141 | 2 / 15 / 29 | 58 | 1 |
| Forte-1 (`ionq:forte-1`) | IonQ, Trapped-ion | 36 | gpi, gpi2, zz | 100 / 100 / 5000 | 1024 | 0.18 + 0.048 | 7 / 50 / 241 | - | 0 |
| Forte Enterprise (`ionq:forte-ent`) | IonQ, Trapped-ion | 36 | gpi, gpi2, zz | 100 / 100 / 5000 | 1024 | 0.18 + 0.048 | 7 / 50 / 241 | - | 0 |
| Emerald (`iqm:emerald`) | IQM, Superconducting | 54 | cc_prx, cz, measure_ff, prx | 1 / 100 / 20000 | 1024 | 0.18 + 0.00096 | 1 / 2 / 20 | 854 | 12 |
| Garnet (`iqm:garnet`) | IQM, Superconducting | 20 | cc_prx, cz, measure_ff, prx | 1 / 100 / 20000 | 1024 | 0.18 + 0.00087 | 1 / 2 / 18 | 942 | 12 |
| Cepheus-1-108Q (`rigetti:cepheus-1-108q`) | Rigetti, Superconducting | 108 (107 per job) | cz, rx, rz | 10 / 100 / 50000 | 1024 | 0.18 + 0.000255 | 1 / 1 / 13 | 3215 | 25 |

Features by backend: barriers: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; defcal: rigetti:cepheus-1-108q; dynamic_circuits: iqm:emerald, iqm:garnet; measure: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; mid_circuit_measure: ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet; physical_qubits: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; result_pragmas: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q; verbatim_boxes: aqt:ibex-q1, ionq:forte-1, ionq:forte-ent, iqm:emerald, iqm:garnet, rigetti:cepheus-1-108q.

Queue priority increases in credits: Private Plan Priority Queue +2, Private Plan Standard Queue +0, Public Plan Priority Queue +2, Public Plan Standard Queue +0.
<!-- open-quantum-facts:end -->

`accepting_jobs`, status and queue depth change between reads and live only
in the snapshot; an Online backend can refuse jobs. The MCP cap of 1 credit
admits only the jobs in the 1-credit column.

**Gates.** core-380 (`capture_oq_docs.py --check`), core-381 (its
`--self-test`), core-382
(`oq_platform.py check docs/evidence/open_quantum --agents AGENTS.md
docs/notes/open_quantum/README.md`) and
core-383 (its `--self-test`).

## Quandela Cloud

Quandela Cloud is the fourth hardware service: photonic QPUs (Belenos,
Ascella) and photonic simulators behind one REST API,
https://api.cloud.quandela.com, on the free Explorer offer.
[docs/notes/quandela/](docs/notes/quandela/README.md) holds the guide, the
captured cloud guides, terms, privacy policies, OpenAPI descriptions, offer
strings, Perceval 1.3 pages and PyPI records; the live pages stay the
authority because they change.

**Environment and token.** Perceval is an Arch package on the build host, so
the repository's Python imports it: python-perceval-quandela 1.3.1 (built
from the GitHub tag v1.3.1), python-exqalibur 1.4.2 (binary wheel, CC
BY-NC-ND 4.0) and python-scmver 1.10 come from PKGBUILDs in
`~/Github/PKGBUILDs`, and python-multipledispatch, python-latexcodec and
python-drawsvg from the AUR through `paru`. perceval-interop is not
installed: its Qiskit extra pins qiskit 2.1. Every API call carries a
personal job token created on the portal's Tokens page; the account
service's OAuth endpoints sign users into Quandela's own sites, take no
scope, PKCE or device flow, and Quandela publishes no client registration.
The token lives in `~/.config/quandela/cloud-token` (directory 700, file
600), outside every checkout, and each consumer names it by path through
`QUANDELA_TOKEN_FILE`; Perceval code passes it as `token=` and never calls
`RemoteConfig.save()`, which writes it in plain text. CI never imports
Perceval: its gates read retained JSON and Markdown with the standard
library.

**MCP.** `quandela` is registered at Claude Code user scope and in
`~/.codex/config.toml` as `"$QD_PYTHON" -I scripts/qd_mcp_server.py` with
`QD_PYTHON=${QD_PYTHON:-/usr/bin/python3}`, the system interpreter that
carries mcp 1.29 and Perceval, and `QUANDELA_TOKEN_FILE`. Claude allows and Codex approves the seven read and
local tools (platforms, platform, availability, usage, job status, job
result, local simulation); `qd_cancel_job` asks every time. The server
submits nothing and exposes no QRNG route; gate core-502 holds its tool set,
annotations and the routes each tool may call to the guide's table. Its
`qd_simulate_local` takes a unitary as JSON numbers, because Perceval's
deserializer evaluates parameter expressions through sympy.

**Submission.** Every remote job, simulator or QPU, every QRNG read
(`/qt/qrng/bytes` and `/qt/qrng/ints` are GETs an offer can price per byte)
and every portal notebook session waits for the user's approval of a written
case, like an IBM, Quantum Inspire or Open Quantum run: what it measures,
why a local Perceval simulation cannot answer it, platform, shots or
samples, expected seconds against the 300 s per-job limit, and expected
credits. Free credit is 200 credits a month under the Explorer offer, reset
at the beginning of each calendar month and never carried over; QPUs charge
1e-06 credits per shot and simulators 0, and the offer's per-job, QRNG and
per-second notebook prices are visible only to the logged-in portal. Content
stays the user's; Quandela holds a license limited to providing the service
(terms 11.2 to 11.4), and the www privacy policy reserves processing raw
computation data for quality.
`"$PYTHON" scripts/qd_platform.py snapshot --out docs/evidence/quandela`
(with `QUANDELA_TOKEN_FILE` set) refreshes the catalogue; gate core-502
renders this table from it and fails when either changes alone:

<!-- quandela-facts:begin -->
| platform | kind | description | modes | photons | photon-source input modes | native commands | detector | max s per job | credits per shot |
|---|---|---|---|---|---|---|---|---|---|
| `qpu:ascella` | qpu | Ascella QPU | 1..12 | 1..6 | 0, 2, 4, 6, 8, 10 | probs, samples, sample_count, entropy | threshold | 300 | 1e-06 |
| `qpu:belenos` | qpu | Belenos QPU | 1..24 | 1..12 | 0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22 | probs, samples, sample_count, entropy | threshold | 300 | 1e-06 |
| `sim:ascella` | simulator | Arcturus simulator | 1..12 | 1..6 | 0, 2, 4, 6, 8, 10 | probs, samples, sample_count | threshold | 300 | 0 |
| `sim:belenos` | simulator | Belenos simulator | 1..24 | 1..12 | 0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22 | probs, samples, sample_count, entropy | threshold | 300 | 0 |
| `sim:gpu:medium` | simulator | Clifford on GPU | - | 2..24 | - | samples, sample_count | - | 300 | 0 |
| `sim:gpu:small` | simulator | Clifford on GPU | - | 2..24 | - | probs, samples, sample_count | - | 300 | 0 |
| `sim:sampling` | simulator | Boson sampler simulator with Clifford&Clifford 2017 backend | - | 2..12 | - | probs, samples, sample_count | - | 300 | 0 |
| `sim:slos` | simulator | Simulator with SLOS backend | - | 2..12 | - | probs, samples, sample_count | - | 300 | 0 |

Token job limits (/api/jobs/availability): 1 running, 1 queued, 10 running Quantum Toolbox jobs.

Known error mitigations: CompilationAveraging, DetectorBalancing, DistinguishablePhoton, PhotonRecycling.

Decommissioned at the snapshot: `sim:gpu:medium`.
<!-- quandela-facts:end -->

Status, performance figures, availability statistics and maintenance
windows change between reads and live only in the catalogue.

**Runner.** A run directory is a copy of one case `job-NN/` under
`results/quandela/runs/UTC-PLATFORM-SERIES-job-NN/`. `qd_platform.py plan
RUN_DIR --platform NAME --max-credits C --expected-seconds S
--per-job-credits P` makes every submit check read-only (digest, platform
status and duration, S within max_duration, P plus max_shots times the live
price within C, no running or queued job, Perceval's shot estimate within
max_shots), records the processor's performance figures and prints the body
Perceval would send; the written case states S, P and C and quotes it. `submit`
adds `--approval TEXT`, holds an flock beside the token file, checkpoints
before the POST and never sends a case twice; `collect` retains the raw
result bytes and parses counts without Perceval's deserializer. One job runs
at a time: the next is planned after the previous one is collected. Every
retained run enters docs/state/research_state.json under the `quandela`
provider in the change that retains it.

**Box-kite photonic cases.** `scripts/qd_box_kite_cases.py` writes three
series under `results/quandela/cases/` from the box-kite census: single
(32 one-photon two-label configurations, one four-label control, the
one-hot 16D pair), packed (the 32 configurations six to a job) and pairs
(the 16 sign blocks with two photons). Every unitary is the
exact Halmos dilation over Q(sqrt2); a one-photon block reads the census P
on its algebra modes, and a two-photon block reads (perm M / 4)^2 on its
label pair, 1/4 on a kite edge and 0 on a strut. A dark block is
p_algebra 0, a bright block p_algebra 1. `scripts/cd_two_blade_blocks.py`
records that every two-label two-blade product at D = 16, 32 and 64 uses
one of these configurations, and that the signed zero products (336, 5040,
52080) equal the annihilator nullity sums.

**Gates.** core-500 (`capture_qd_docs.py --check`), core-501 (its
`--self-test`), core-502 (`qd_platform.py check docs/evidence/quandela
--agents AGENTS.md docs/notes/quandela/README.md`), core-503 (its
`--self-test`, the runner's stubbed-service contract included), core-504
(`qd_box_kite_cases.py --check results/quandela/cases`), core-505 (its
`--self-test`), core-506 (`cd_two_blade_blocks.py --check
docs/evidence/box_kite_census/two_blade_blocks.json`) and core-507 (its
`--self-test`).

## Qiskit skills

The Qiskit agent skills come from https://github.com/Qiskit/skills, installed
by copy into `~/.claude/skills/`:

| skill | installed path | upstream commit |
|---|---|---|
| migrate-qiskit-ibm-runtime | `~/.claude/skills/migrate-qiskit-ibm-runtime/` | a5499c7c24f51633cbd0a5e7ea5902841e5b983e |

Upstream also publishes them as a Claude Code plugin:
`/plugin marketplace add Qiskit/skills`, then
`/plugin install qiskit-ai-skills@qiskit`.

**Monthly check.**
1. Compare `git ls-remote https://github.com/Qiskit/skills HEAD` with the
   pinned commit above.
2. On a difference, clone the new commit into a scratch directory and read
   every changed or added file in full before installing: skills are
   instructions an agent executes, so they get the review any code gets.
3. Copy the skill directories into `~/.claude/skills/`, update the table above
   in a PR, and rerun the audit below. A new skill on the upstream roadmap
   (mitigation evaluation, layout selection, circuit optimization) also gets a
   written decision on whether it replaces anything in live_run.py.

**When to invoke.** Run `/migrate-qiskit-ibm-runtime` with scope
gororoba_quantum/ in these cases, and follow its phases, grounding, and report
format:
- any change that touches qiskit-ibm-runtime: primitives, options, jobs,
  service, backends, sessions, or batches;
- any change to the qiskit-ibm-runtime pin in requirements.txt;
- after every monthly skill update.

The skill sets the destination as the client-side
`qiskit_ibm_runtime.executor_sampler.Sampler` from runtime 0.50.0. It forbids
inventing an API path that its guides and the API reference do not enumerate,
so such a path is validated at run time and named in the error when absent.

**Rules the audit established.** The skill's local verification ran circuits
through the client-side Sampler and established the job split live_run.py
uses. In runtime 0.50, gate twirling sends circuits through samplomatic
boxing, which rejects `if_else`, and IBM's Sampler rejects dynamical
decoupling on dynamic circuits. So live_run.py sends circuits with
mid-circuit measurement, reset, or feed-forward in their own job, with
twirling and dynamical decoupling off.

## Reviews and merges

Codex, the chatgpt-codex-connector app, supplies the default pull-request
review. It reviews on open, and an issue comment `@codex review` requests a
review of the current head.

Codex is the only hosted reviewer. Copilot reviews are billed to the owner,
so no pull request requests one; when the Codex app reports exhausted
code-review quota, the owner decides how the PR proceeds.

- *Progress.* The bot keeps one summary comment per PR, marked
  `codex-pull-request-review-summary`, which reads Running while a review is in
  progress.
- *Outcome.* A review with findings publishes inline review comments with P1 or
  P2 badges. A clean review either posts an issue comment whose text, after
  an optional `<!-- codex-review-receipt:v1 -->` marker, begins "Codex
  Review: Didn't find any major issues" with a reviewed commit matching the PR
  head, or adds an app-owned `+1` reaction after the completed summary update
  for the current head. A prior reaction cannot qualify a later review round.
- *Status tool.* `scripts/codex_review_status.sh PR...` prints each PR's head,
  summary head, review state, and head-bound clean signal, then every unresolved
  thread with its root comment id and full body. It accepts comments and
  reactions only from the stable app and bot identities, requires the clean
  comment to follow the current review request and the reaction to occur
  strictly after the completed summary update. It paginates every issue,
  reaction, thread, and thread-comment connection, then re-reads the head and
  PR update marker, and summary to reject a changing snapshot.

**One round, per PR:**
1. Wait until the Codex review completes: its summary stops reading
   Running. Then read every unresolved thread
   in full from `codex_review_status.sh` or the GraphQL thread connection.
   Threads can arrive between rounds and attach to the newest commit, so the
   open-thread list,
   not memory of the last round, is the work queue.
2. Triage each thread against reachability.
   - A defect a user reaches through a documented interface (the CLI, the
     record files the program writes, the default flow) gets a fix.
   - A claim the source refutes gets the refuting line in the reply.
   - Malformed or adversarial input outside the documented domain gets a reply
     naming the boundary and a follow-up issue.
3. Fix every reachable thread on the PR's own branch in one commit; CI runs the
   gates on the push. A change to live_run.py or experiments.py also gets a live dry run,
   and a change to qiskit-ibm-runtime usage also gets `/migrate-qiskit-ibm-runtime`.
   Then push.
4. Reply to each thread's root comment with
   `gh api repos/OWNER/REPO/pulls/PR/comments/ID/replies -f body=...`. The reply
   begins with one of three markers, then says what changed or why:
   - `Fixed in <commit>`
   - `Refuted:` followed by the refuting source line
   - `Boundary:` followed by the documented limit and the follow-up issue
5. Run `scripts/resolve_answered_threads.sh PR`. It resolves only threads
   carrying a reply from the authenticated operator that begins with one of
   those markers, and lists every other open thread as unanswered. A comment
   such as "will fix" or a question resolves nothing. Never resolve a thread
   whose finding has not been read and answered.
6. Request Codex again and start at step 1. A PR leaves the loop when the
   current-head Codex status reports `verdict=clean-comment...` or
   `verdict=clean-reaction...` and every review thread is resolved.

**Stacked PRs.**
- Each branch builds on the one below it, so a fix lands on the lowest branch
  that holds the code and then merges upward, branch by branch, with
  `git merge --no-ff`.
- Rebasing is out because the permission harness denies force-push.
- When one file conflicts heavily, take the lower branch's reviewed version and
  re-apply the upper branch's own changes on top. CI reruns every gate; run a dry
  run on every branch the merge touched.

**Merging.** A PR merges when its latest review is clean, every thread is
resolved, GitHub reports mergeable_state clean, and
`"$PYTHON" ci/premerge_gates.py BRANCH` exits 0. That script merges the
branch into origin/main in a scratch worktree and runs every pr-tier gate
measured at 5 s or less there and on origin/main, each tree through its own
ci/run_gates.py; it fails on a gate the merge breaks. A gate over a
whole-tree record (core-368 over every case circuit, core-270 over every
retained run) can pass on two branches separately and fail on their merge,
and a PR's CI ran against main as it stood then. Full-tier record gates such
as core-289 (every retained family configuration) run only on main's full
CI run. Bottom-up, for each PR:
1. Merge it with a merge commit:
   `gh api -X PUT repos/OWNER/REPO/pulls/PR/merge -f merge_method=merge`.
2. Retarget the next PR to main: `gh api -X PATCH repos/OWNER/REPO/pulls/NEXT -f base=main`.
   Deleting a base branch closes every PR that targets it, so the retarget
   comes first.
3. Delete the merged remote branch:
   `gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH`.
4. Pull main in the primary checkout, then `git worktree remove` and
   `git branch -d` the merged branch.

**API use.** Everything goes through REST with `gh api`, except review
threads, which only GraphQL exposes: both scripts list them through the
reviewThreads connection, and resolution uses resolveReviewThread and
unresolveReviewThread.

## Records

- results/ holds audit records: hw_estimate/ for the fixed ibm_fez compile and
  live/ for live runs.
- A collected run keeps its lossless result under `raw/<job_id>/` (every
  classical register as shot-ordered bit strings, each PUB's metadata with
  the backend scheduler table, the result metadata, the job metrics, and an
  index of sha256s), written by `--collect` before any analysis and
  recoverable with `--preserve-raw DIR` for a record collected under an
  earlier revision. collect.json is the preregistered analysis at the run's
  experiment digest; `adjudicate.py DIR` writes adjudication-<digest>-seed<seed>.json, a second
  analysis of the same raw files named by its own analysis digest, beside
  any earlier one. Raw files
  are never rewritten by a later collection or analysis.
- docs/state/research_state.json registers every acquisition under its
  provider, and scripts/research_state.py holds one adapter per provider
  whose run set the registry matches exactly: `ibm` runs come from the
  retained-run audit, `quantum_inspire` runs from the directories under
  results/quantum_inspire/runs/ (circuits matching cases.json, one raw shot
  list per completed job, failed jobs included) bound to the ledger in
  docs/evidence/quantum_inspire/usage.json. A retained run therefore enters
  the registry, with a claim citing it and a refreshed ledger or inventory,
  in the change that retains it. The ledger is account-wide, so sessions
  that share the account land runs from separate branches: `qi_platform.py
  snapshot` writes `unretained`, the sorted ids of the ledger jobs that no
  run directory of the tree holds, and research_state.py requires every
  retained job to match its ledger row, every ledger job to be retained or
  declared, and every declared job to appear in the ledger. A job both
  retained and declared passes (its run landed after the snapshot), and the
  transaction rows of declared-only jobs belong to the other branch and stay
  uncompared. A branch merging main re-snapshots only when its own retained
  jobs are missing from the snapshot it carries; a `qi-usage-v1` ledger
  declares no unretained job.
- Every run record carries the identity of the system that ran or would
  run it as data: live_run.py records each backend's `backend_version` and
  `processor_type` from its configuration in `backends`, `system_inventory`
  and each group, and the properties' `backend_version` at each execution
  start in collect.json. Calibration and Heron Target snapshots carry the
  same fields; a simulation record that copies a snapshot's calibration
  stamp copies them too (`calibration_snapshot.backend_identity`) beside the
  Aer version and device, and one that names its snapshot by path reaches
  them through that file. A Kaggle submission.json records the entry's Aer
  device and every bundled snapshot's identity. The approved-record
  comparison reads none of these fields, and every checker accepts a
  record without them.
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers, and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`. Account identifiers are credentials, account
  and instance ids, CRNs and email addresses. A public platform handle --
  the GitHub owner in every repository URL, the Kaggle username in a
  kernel or dataset slug (`owner/slug`) -- names published work, and
  records keep it so `collect` and `status` resolve the kernel.
