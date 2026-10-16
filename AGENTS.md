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
shards are assigned longest-first. Pull requests run the `pr` tier, every
gate that measured under two minutes, on six shards; pushes to main, the
nightly schedule and manual runs add the `full` tier's long simulation
contracts on twelve shards. Runners are 2-vCPU, 8 GB machines on Python 3.14
with the pins in requirements.txt and ci/requirements-ci.txt (mypy, ruff and
the plotting-only `matplotlib==3.11.2`). A pull request merges when every
shard is green and its review threads are resolved; a red main or nightly
run is fixed in the next change. A new module, evidence
replay or contract joins the gate list in ci/gates.json in the same change.


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
check verifies retained hashes; a fresh kernel replay remains the proof-change
procedure because hosted CI supplies no pinned Rocq toolchain.

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

**Cayley-Dickson packages on the build host.**
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
same eight packages from the same pinned archives (`--fetch` and `--install`
apply the PKGBUILD recipes) and runs its entry only after `--extract`
regenerates `tables.json` byte for byte; SageMath stays on the build host
(`docs/notes/kaggle/hypercomplex-stack.md`).

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

Octonion-Sedenion and pyoctonion are not installed, so their relation to
cd_core is unmeasured and no artifact claims one.
<!-- algebra-circuit-rules:end -->

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- Simulations of 14 qubits or fewer run on Kaggle kernels through
  `scripts/kaggle_run.py` (`push`, `status`, `collect`), which bundles the
  entry's repository imports with `kaggle_kernel/` (the kernel program and
  its AGENTS.md), installs qiskit 2.5.2 with qiskit-aer 0.17.2 (or
  qiskit-aer-gpu-cu11 0.17.2 on a GPU), proves the hypercomplex package
  stack before the entry runs, and retains the output under results/kaggle/.
  A kernel runs on a CPU machine by default; a case requests a GPU
  (`--machine NvidiaTeslaT4`) when its widest density matrix reaches
  `local_compute.GPU_MIN_ACTIVE_QUBITS`, since narrower replays run slower
  on a GPU and the weekly GPU quota is scarce. `kaggle_run.py shards`
  replicates the CI gate shards for a commit on Kaggle CPU kernels in place
  of the build host. `docs/notes/kaggle/` holds the workflow, the measured
  substrates and the package-stack guide. Kaggle allows two concurrent GPU
  and five concurrent CPU batch sessions per account. IBM hardware serves 15 or
  more qubits, or a smaller run whose question concerns the device itself
  (a named qubit's readout, detuning or drift); its case states why Aer
  cannot answer it. A kernel's
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
| python-qiskit-aer-cuda (provides python-qiskit-aer) | qiskit-aer 0.17.2 |
| python-samplomatic | samplomatic 0.21.0, the runtime 0.50 floor |
| python-ibm-quantum-schemas | ibm-quantum-schemas 0.12.20260921, the runtime 0.50 floor |
| python-numpy, python-scipy | numpy 2.5.4, scipy 1.18.1 |
| python-rustworkx, python-sympy | rustworkx 0.18.1, sympy 1.14.0 |
| python-matplotlib | matplotlib 3.11.2 |
| python-pytorch-opt-cuda, python-pandas | torch and pandas for python-octonion and python-cayley-dickson only |
| python-ruff, mypy | newer than the CI pins ruff 0.14.11 and mypy 1.19.1; `uvx ruff@0.14.11` reproduces CI formatting |

A broken or missing package is rebuilt and reinstalled from its PKGBUILD in
`~/Github/PKGBUILDs` with `makepkg -si --nocheck` in the package
directory: python-qiskit-aer and python-samplomatic before
python-qiskit-ibm-runtime. Those PKGBUILDs replace `blas-openblas` with the
`blas` and `lapack` virtuals that the installed AMD AOCL libraries provide,
which leaves AOCL in place; a package without a local PKGBUILD comes from
the distribution repositories through pacman or paru. After a rebuild,
`"$PYTHON" -c "import qiskit, qiskit_ibm_runtime, qiskit_aer"` and a
submit-free dry run confirm the stack. A Kaggle kernel installs qiskit 2.5.2
and qiskit-aer-gpu-cu11 0.17.2 (the CUDA 12 `qiskit-aer-gpu` wheel stops at
0.15.1) over the Kaggle image's numpy and scipy, records every version in
`environment.json`, and holds no IBM credential (`kaggle_kernel/AGENTS.md`).
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
No Arch package carries the stack. CI never imports it: every gate checks
retained JSON or regenerates text with the standard library.

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
access and refresh tokens in `~/.quantuminspire/config.json` (mode 600). The
access token lives 3600 s; scripts/qi_platform.py renews it before expiry.
An agent that finds no login prompts the user to run `qi login` and approve
the code; tokens never enter a commit, a log or memory.

**Backends.** `scripts/qi_platform.py snapshot --out docs/evidence/quantum_inspire`
reads the account's catalogue and ledger; gate core-326 renders this table
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
  initialization 200 or 500 us; rotation angles quantize to multiples of
  pi/36; OpenSquirrel schedules as late as possible, `wait(n)` idles n
  cycles of 20 ns, and mid-circuit measurement is allowed while binary-
  controlled gates are not, so feed-forward is applied in post-processing.
- Bit order: QX and Tuna results put qubit 0 at the rightmost character; the
  Ry emulator puts it at the leftmost (an X on q[0] read `10` in all 1024
  shots). An analysis states the order of the backend it reads.
- The Ry emulator takes no measurement statements and measures every qubit
  at the end; a circuit with a bit register, H and CNOT compiled remotely but
  failed at execution with no log, while the X-only form of its code example
  ran.
- The Qiskit provider writes a multi-qubit barrier as per-qubit barriers, so
  a timing-sensitive case writes cQASM directly with explicit `wait`.

**Usage and cost.** The account's transaction ledger (`/transactions/`,
`qi_platform.py snapshot` writes usage.json) recorded no entry for the
twenty-two jobs of 2026-10-16 on QX, the Ry emulator and Tuna-17, so no metered seconds
or credits apply to this account as observed; the limits are structural: the
table's qubits, shots, per-job execution limit and batch and queue counts,
plus the FAQ's three queued jobs per hardware backend, which is stricter than
the API's five batch jobs. Tuna-17 executed 16384 shots in 9.9 to 15.4 s
(0.60 to 0.94 ms per shot, deeper circuits slower); QX finished 2048 shots
in 0.03 to 10.4 s.
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
the raw shots, job records and charged transactions. Runs live under
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

**Gates.** core-325 (`capture_qi_docs.py --check`), core-326
(`qi_platform.py check docs/evidence/quantum_inspire --agents AGENTS.md`),
core-327 (`qi_crosstalk_teleport_cases.py --check results/quantum_inspire/cases`),
core-331 (`--replay` of every retained analysis.json), core-329 and core-330
(`qi_zero_divisor_cases.py --check` and `--replay`), and core-340
(`qi_ibm_noise_replay.py --check`, the Kingston-noise replay of the Tuna-17
cases).

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
resolved, and GitHub reports mergeable_state clean. Bottom-up, for each PR:
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
  in the change that retains it.
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers, and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`.
