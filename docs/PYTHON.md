# Python in this repository

This page routes a Python task to its interpreter, its library and the
document that owns the rule. Versions live in the pin files and the
inventory, never here: [requirements.txt](../requirements.txt) (runtime),
[ci/requirements-ci.txt](../ci/requirements-ci.txt) (gate tools),
[ci/requirements-replay.txt](../ci/requirements-replay.txt) (historical
Qiskit 2.5.2 replays), and the build host's Arch packages in
[python-stack.md](notes/build_host/python-stack.md). The
[library register](state/hypercomplex-libraries/libraries.md) lists every
distribution with its role and every tracked file that imports it; gate
core-630 compares it with a fresh AST scan of `gororoba_quantum/`,
`scripts/`, `ci/` and `kaggle_kernel/`, so a new import in those trees
enters the register in the same change.

## Interpreters

| Interpreter | Runs | Authority |
| --- | --- | --- |
| `$PYTHON`, exported | every script, gate and dry run | [AGENTS.md](../AGENTS.md) "Layout and gates" |
| `--replay-python` or `REPLAY_PYTHON` | gates marked `"runtime": "qiskit-2.5"`; without it they exit 127 | [ci/AGENTS.md](../ci/AGENTS.md) |
| `QI_PYTHON` (Python 3.13) | Quantum Inspire SDK, qxelarator, cQASM, OpenSquirrel | [quantum_inspire/README.md](notes/quantum_inspire/README.md) |
| `OQ_PYTHON` | Open Quantum SDK | [open_quantum/README.md](notes/open_quantum/README.md) |
| `QD_PYTHON` | the Quandela MCP server; Perceval itself runs on `$PYTHON` | [quandela/README.md](notes/quandela/README.md) |
| `iqm-python` | IQM Resonance client stack | [iqm/README.md](notes/iqm/README.md) |
| Kaggle kernel | simulations of 14 qubits or fewer | [kaggle/README.md](notes/kaggle/README.md) |

Every interpreter starts with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, which the Qiskit Rust
and Aer OpenMP extensions need. Gates run with `-B -W error`, and many also
under `-O`, so a check raises explicitly instead of using `assert`.

## Libraries by job

| Job | Library | Use it when | Rule and evidence |
| --- | --- | --- | --- |
| Cayley-Dickson products and signs | `cd_core` (in tree) | always: it is the specification | [algebra_circuit_rules.md](notes/algebra_circuit_rules.md) |
| Arrays, batched linear algebra | numpy | any float work; vectorize before pooling | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#vectorization-in-numpy) |
| Least squares, decompositions, statistics, sparse | scipy | `lstsq` or pivoted QR, never normal equations; `scipy.sparse` for structured systems | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#least-squares-and-conditioning) |
| Exact rank modulo p, rational null spaces | python-flint through `scripts/exact_rank.py` | every rank or nullity certificate | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#exact-backends) |
| Symbolic algebra, exact matrices | sympy, as `DomainMatrix` for integer products | polynomial identities and charts | same section |
| Arbitrary precision | mpmath | refining a float result past float64 rounding; `eigsy` on L^T L where `svd_r` fails on repeated singular values | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#precision) |
| p-adic and finite-field arithmetic | pyadic, galois | rational reconstruction, F_p linear algebra beyond FLINT | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#runtime-packages) |
| Circuits and transpilation | qiskit | every circuit; the live Target is the timing authority | [ibm_heron_platform.md](notes/ibm_heron_platform.md) |
| Noise simulation | qiskit-aer, CPU or the host's CUDA build | 14 qubits or fewer on Kaggle; larger runs are decision-gated | [AGENTS.md](../AGENTS.md) "QPU time and calibration", [substrates.md](notes/kaggle/substrates.md) |
| IBM hardware | qiskit-ibm-runtime, client-side `executor_sampler` | `--submit` after an approved case | [qpu-submission.md](notes/ibm_quantum/qpu-submission.md) |
| Layout and graph search | rustworkx | replica placement (`vf2_mapping`) | `gororoba_quantum/` |
| Batched density-matrix sweeps | jax | error-scale sweeps in `jax_bridge` on CPU | [jax-bridge-structure-report.md](notes/kaggle/jax-bridge-structure-report.md) |
| Tensor networks, contraction order | quimb, cotengra, opt_einsum | networks beyond a few tensors | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#vectorization-in-numpy) |
| Photonic circuits | perceval, exqalibur | Quandela runs and their simulations | [quandela/README.md](notes/quandela/README.md) |
| Hypercomplex cross-checks | hypercomplex, hyprat, octonion and the other packages in the register | a declared map onto `cd_core`, checked on every basis pair | [packages/README.md](notes/packages/README.md) |
| Audits that need SageMath | sage | build-host audits whose retained output a pinned gate checks | [rank_locus_rotation_composite](evidence/rank_locus_rotation_composite/README.md#symmetry) |
| Plots | matplotlib | measured figures only; mock outcomes never enter them | [AGENTS.md](../AGENTS.md) "Layout and gates" |
| Tests | pytest, pytest-xdist | the behavioral suite | [ci/AGENTS.md](../ci/AGENTS.md) |
| Thread accounting | threadpoolctl | recording the BLAS and OpenMP runtimes a gate used | [numerics_best_practice.md](notes/topics/numerics_best_practice.md#parallelism-and-blas-threads) |
| Provider MCP servers | mcp | `scripts/*_mcp_server.py` | provider guides |
| Kaggle control, browser checks | kaggle, kagglesdk, requests; playwright, selenium | kernel push and status; rendered-viewer and session checks | [kaggle/README.md](notes/kaggle/README.md) |
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
   from a file rather than stdin. The pool pins BLAS and OpenMP to one
   thread per worker.
5. **Move exact work to FLINT.** `nmod_mat.rank` and `nullspace` modulo a
   word-size prime replace Python elimination; a structured sparse system
   compresses through a `scipy.sparse` product before elimination. A
   modulo-p rank bounds the rational rank from below, and a certificate
   checks its kernel vectors in Python integers.
6. **Use an accelerator only where a run qualified it.** The host's CUDA Aer
   build and Kaggle GPUs serve the circuits their notes measured; small
   dynamic circuits stay on CPU ([substrates.md](notes/kaggle/substrates.md)).
7. **Shard.** A pooled, batched run that still exceeds one host's budget
   shards to Kaggle CPU sessions by item range.

## Correctness rules

- Seed every generator and record the seed; a replay reproduces bytes.
- float64 suffices wherever sampling sets the error. An exact claim uses
  exact arithmetic, and extended precision only refines a float estimate.
- Float tolerances decide nothing about rank, nullity or local dimension.
  A floating projection stops once a residual falls under its tolerance, so
  a direction along which the residual vanishes to high order passes
  uncorrected; such a test needs a scale where that order exceeds the
  tolerance, or extended precision.
- Run ruff and mypy through `ci/pinned_tool.py` on every touched file.
- Record the versions a result depends on inside the result.
- Mock outcomes (`--native-dry-run`) never enter an analysis or a figure.
