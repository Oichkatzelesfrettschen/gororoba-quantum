# Quantum and numerics tools: usage manuals

One manual per package, in manpage order: NAME, SYNOPSIS, capabilities in
this repository, API entry points (listed by introspection on the build
host), examples that were run there with their printed output, Qiskit
interop, CPU and GPU, traps, license. The root AGENTS.md owns the rules these
manuals apply: the QPU and Kaggle routing in "QPU time and calibration"; docs/notes/ibm_heron_platform.md holds the
timing and dynamic-circuit facts in "Execution facts"; and the pins
in `requirements.txt` and `scripts/kaggle_run.py` (`KERNEL_PINS`,
`PIN_GROUPS`).

Every example runs from the repository root with the `python3` of the build
host. Noise comes from `docs/evidence/calibration/ibm_kingston.json` through
`calibration_snapshot.noise_model` / `noise_simulator`; nothing contacts IBM.
The runtime examples run in a network namespace without a route
(`unshare -rn`). Scripts that start worker processes (qiskit-experiments,
`transpile` of several circuits) carry a `__main__` guard because the workers
re-import the script under the host's `forkserver` start method.

## Index

Quantum-tools group (`push --with quantum-tools`; the group also pins
qiskit-ibm-runtime, samplomatic, ibm-quantum-schemas, qiskit-mitigation,
qiskit-qasm3-import with openqasm3 and its antlr4 parser, and
qiskit-addon-utils, listed under the core stack below):

| Manual | Package | Pin |
| --- | --- | --- |
| [stim.md](stim.md) | stim | 1.16.0 |
| [mthree.md](mthree.md) | mthree, runningman | 3.0.0, 2.3.0 |
| [qiskit-experiments.md](qiskit-experiments.md) | qiskit-experiments | 0.14.2 |
| [quimb.md](quimb.md) | quimb, cotengra, autoray | 1.15.0, 0.8.2, 0.11.0 |
| [pyzx.md](pyzx.md) | pyzx | 0.10.7 |
| [galois.md](galois.md) | galois, numba | 0.4.11, 0.68.0 |
| [lmfit.md](lmfit.md) | lmfit | 1.3.4 |

Core stack and neighbors:

| Manual | Package | Host version |
| --- | --- | --- |
| [qiskit.md](qiskit.md) | qiskit | 2.5.2 |
| [qiskit-aer.md](qiskit-aer.md) | qiskit-aer (CPU and GPU) | 0.17.2 |
| [qiskit-ibm-runtime.md](qiskit-ibm-runtime.md) | qiskit-ibm-runtime, local aspects only | 0.50.0 |
| [samplomatic.md](samplomatic.md) | samplomatic | 0.21.0 |
| [ibm-quantum-schemas.md](ibm-quantum-schemas.md) | ibm-quantum-schemas | 0.12.20260921 |
| [qiskit-qasm3-import.md](qiskit-qasm3-import.md) | qiskit-qasm3-import, openqasm3 | 0.6.0, 1.0.1 |
| [rustworkx.md](rustworkx.md) | rustworkx | 0.18.1 |
| [numpy-scipy-sympy.md](numpy-scipy-sympy.md) | numpy, scipy, sympy | 2.5.4, 1.18.1, 1.14.0 |
| [gpu-arrays.md](gpu-arrays.md) | torch, cupy, jax, numba CUDA | 2.14.1, 14.2.0, 0.9.0, 0.68.0 |
| [qiskit-addon-utils.md](qiskit-addon-utils.md) | qiskit-addon-utils | 0.4.0 |
| [qiskit-mitigation.md](qiskit-mitigation.md) | qiskit-mitigation (hardware executor tasks; not run) | 0.1.1 |

Crystallography (a cache virtual environment, pinned nowhere):

| Manual | Package | Host version |
| --- | --- | --- |
| [seekpath.md](seekpath.md) | seekpath, spglib | 2.2.2, 2.8.0 |

## Substrates

| Substrate | Where | Limits that matter for these tools |
| --- | --- | --- |
| Host | the build host: 12 threads, 62 GiB RAM, RTX 4070 Ti (12 GiB) | density matrix 15 qubits on RAM and 14 on the GPU, statevector 29 on the GPU (`docs/notes/kaggle/substrates.md`); the only substrate with the IBM credential |
| Kaggle CPU kernel | `push --machine cpu` | 4 cores, about 30 GB RAM, Python 3.13 |
| Kaggle GPU kernel | `push --machine NvidiaTeslaT4` (the default machine is `cpu`, `DEFAULT_MACHINE` in `scripts/kaggle_run.py`) | 2 x T4, 15 GiB each, density matrix 14 and statevector 29 on one T4; two concurrent GPU sessions per account |

A GPU kernel installs `KERNEL_PINS` (`qiskit==2.5.2`,
`qiskit-aer-gpu-cu11==0.17.2`) and a CPU or TPU kernel `CPU_KERNEL_PINS`
(`qiskit==2.5.2`, `qiskit-aer==0.17.2`), plus whatever `--with` groups name,
the pip dependencies of those packages, and the image (numpy 2.1.3, scipy
1.16.3, sympy 1.14.0, pandas 2.3.3, torch 2.11.0 in the recorded probes). The
CPU kernel run
`results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` pushed
`--with quantum-tools` when the group held twelve pins, and its
`output/output/pin_groups.json` records all twelve installed at their
versions. The group now holds nineteen pins; the seven added since (the
runtime dependencies samplomatic, ibm-quantum-schemas and qiskit-mitigation,
the qasm3-import, openqasm3 and antlr4 parser trio, and qiskit-addon-utils)
have not been installed on a kernel. `scripts/kaggle_run.py self-test` builds
a group kernel without network access and checks that `run.py` carries every
group pin.

## Decision table

"Evidence" is the single path by which a result enters the research state
(`docs/notes/kaggle/workflow.md`, `kaggle_kernel/AGENTS.md`): a Kaggle kernel
pushed from a clean committed tree, then a CPU replay gate on a reduced case
in `ci/gates.json`. A host result informs a design and is evidence only after
that path.

| Task | Tool | Host (development) | Kaggle CPU kernel | Kaggle GPU kernel | Entering evidence |
| --- | --- | --- | --- | --- | --- |
| Clifford or stabilizer circuit, Pauli noise, detectors, thousands of qubits | stim ([stim.md](stim.md)); Aer `stabilizer` | yes | yes | no gain (CPU only) | kernel from a clean tree, CPU replay of a reduced case |
| Density-matrix noise replay of a retained job, 14 qubits or fewer | Aer density matrix via `calibration_snapshot.noise_simulator` | yes (CPU or GPU) | yes (small cases) | yes, 14 qubits | kernel from a clean tree, CPU replay gate |
| Readout error and the readout factor `1 - P(1\|0) - P(0\|1)` | mthree (counts), qiskit-experiments `LocalReadoutError` (circuits) | yes | yes | not needed | CPU replay gate; matrices come from the job's own preparation baselines, since the snapshot's e10/e01 are reported values and differ from the measured ones on Kingston qubits 0 and 1 (`results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md`) |
| T1, T2, RB of a replay; Ramsey fits | qiskit-experiments, lmfit | yes | yes | simulation step only | kernel plus CPU replay of a reduced delay set |
| Dynamic circuit with mid-circuit measurement and feed-forward | Aer through the local `executor_sampler.Sampler`; stim for Pauli feed-forward only | yes | yes | yes (simulation step) | kernel from a clean tree, CPU replay |
| Ideal simulation beyond 14 qubits (15 to about 30) | Aer statevector or quimb with cotengra | yes (quimb GPU through torch or cupy) | quimb on CPU | statevector to 29 qubits; quimb on torch (cupy is not installed by the repository) | design support only for an IBM case; noisy results need IBM |
| Tensor-network amplitude, marginal, local expectation | quimb, cotengra, autoray | yes | yes | torch arrays | kernel plus CPU replay of a reduced case |
| ZX rewriting, T-count of algebra circuits | pyzx | yes | yes | no gain (CPU only) | exact tensor equality check as a CPU gate |
| GF(2) linear algebra, ANF, CCZ normal form certificates | galois, `boolean_anf.py` | yes | yes | no gain | exact CPU gate (the normal-form certificates already have gates core-278 and core-284) |
| Layout and placement on the coupling graph | rustworkx | yes | yes | no gain | CPU gate |
| Twirling overhead and samplex shapes | samplomatic | yes | yes | no gain | CPU gate |
| Hardware execution at 16 qubits or more, or a device question (15 qubits go to the substrate an approved case names, Tuna-17 through Quantum Inspire included) | qiskit-ibm-runtime with IBM | only after an approved case | never | never | the IBM job and its raw archive |

## Pushing a kernel with the group

The kernel bundles the entry script, its imports under `gororoba_quantum/` and
`scripts/`, and `KERNEL_FILES`; any other file the entry reads (the calibration
export) joins with `--include`. Commit first and read `git status`, because
`submission.json` records the commit with a `-dirty` suffix when a tracked or
bundled file differs.

```sh
PYTHON=${PYTHON:-python3}
"$PYTHON" scripts/kaggle_run.py self-test                     # offline: bundle and run.py
"$PYTHON" scripts/kaggle_run.py push gororoba_quantum/ENTRY.py \
    --slug SLUG --with quantum-tools --machine cpu \
    --include docs/evidence/calibration/ibm_kingston.json -- ENTRY_ARGS
"$PYTHON" scripts/kaggle_run.py status results/kaggle/RUN_DIR
"$PYTHON" scripts/kaggle_run.py collect results/kaggle/RUN_DIR
```

- `--with quantum-tools` adds the nineteen pins of `PIN_GROUPS["quantum-tools"]`
  to the `pip install` under a constraints file that holds the machine's
  Qiskit pins and the image's numpy and scipy fixed; the kernel stops unless every pin
  installed at its version.
- `--machine cpu` for stim, pyzx, galois, lmfit, mthree, qiskit-experiments and
  CPU quimb (the default machine); pass `--machine NvidiaTeslaT4` when Aer
  `device="GPU"` or torch contraction is the point. The GPU kernel is
  entered with `GOROROBA_AER_DEVICE=GPU`.
- Entries that call `.run()` of qiskit-experiments or `transpile` of many
  circuits keep the `__main__` guard.
- A kernel holds no IBM credential; it reads the retained snapshot.
- The group push ran once, at twelve pins, as
  `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu`.

## Interop summary (qiskit 2.5.2, verified on the host)

| Tool | Qiskit to tool | Tool to Qiskit | Failure observed |
| --- | --- | --- | --- |
| stim | gate-name table over `QuantumCircuit.data`; `Tableau.from_unitary_matrix` | `to_qasm(open_qasm_version=3)` + `qasm3.loads` | `ValueError` on a noisy circuit in `to_qasm`; no `if_else` |
| mthree | `AerSimulator` backend or `cals_from_matrices` | `QuasiDistribution` | none on static circuits |
| qiskit-experiments | any `BackendV2` incl. the snapshot `AerSimulator` | `ExperimentData` | none; needs `__main__` guard |
| quimb | `qasm2.dumps` + `from_openqasm2_str` | `to_dense()` (bit order reversed) | `qasm3` physical qubits (`$0`) and `if_else` rejected |
| pyzx | `qasm2.dumps` or `qasm3.dumps` + `Circuit.from_qasm` | `to_basic_gates().to_qasm()` + `qasm2.loads` | dynamic circuit: `Phase expression 'c[0]' contains unbound variables` |
| galois | via NumPy arrays | via NumPy arrays | mixing plain arrays raises `TypeError` |
| lmfit | via NumPy arrays | none | none |
| cotengra | `HyperOptimizer(seed=...)` | n/a | `create_study() got an unexpected keyword argument 'seed'` with the default `optuna` |

## Kaggle install compatibility

The runner holds numpy 2.1.3 and scipy 1.16.3 fixed and stops if pip cannot
satisfy the constraints. The direct numpy and scipy requirements of the twelve
original group pins, read from the host's package metadata, all admit those
versions:
quimb needs `scipy>=1.16.0` (tightest, met by 1.16.3), numba needs
`numpy<2.6,>=1.22`, mthree `scipy>=1.11.1`, lmfit `scipy>=1.10.0`. Transitive
bounds were not read from metadata. All twelve installed at their pins under
those constraints on
`results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu`
(`pin_groups.json`), mthree among them although PyPI carries no cp313 wheel
for it (`docs/notes/qiskit-ecosystem.md` finding 7). The seven later pins have
not been installed on a kernel.

## Regenerating an example

Each example block is a complete script: save it to a file outside the
repository, run `python3 FILE` with the repository root as the working
directory, and compare the printed text. The sampled digits are seeded; digits of
GPU and contraction-order floating-point sums are rounded in the scripts
where they varied between runs.

## Gaps: useful packages that are not installed

Absent on the build host (`importlib` import failed; `pacman -Qq` shows no
package) and not installed:

| Package | Why it would help | Currently |
| --- | --- | --- |
| pymatching, sinter, stimcirq | decoding and batch statistics for stim detector error models; stim to Cirq | stim DEMs can be sampled and analyzed, not decoded |
| kahypar | cotengra's best path quality; cotengra warns it falls back to `labels` | lower-quality contraction trees |
| qiskit-qec, qiskit-addon-cutting, -obp, -sqd, -mpf | codes, circuit cutting, operator back-propagation, sample-based diagonalization | none; `qiskit-addon-utils` alone is present |
| qiskit-algorithms, qiskit-nature, qiskit-machine-learning, qiskit-dynamics | algorithm library, chemistry, learning, pulse and analog dynamics | none in use |
| mitiq | software error mitigation on Aer | `qiskit-mitigation` (hardware executor tasks) and mthree only |
| cirq, pennylane, pytket, tensorcircuit, qujax | other circuit stacks and differentiable simulation | not required by any module |
| cuquantum (cuStateVec, cuTensorNet), cudaq | GPU statevector and tensor-network beyond Aer's own CUDA build | quimb on torch or cupy covers tensor networks |
| qutip | open-system and Lindblad dynamics | Aer density matrix with an explicit noise model |
| ldpc | LDPC and stabilizer-code tooling | none |

Package-level gaps in what is installed:

- `galois` 0.4.11 has no `ReedMuller` class (the Reed-Muller comparison in
  `docs/evidence/ccz-reduction/` uses repository code).
- `qiskit-qasm3-import` is an optional extra of qiskit; the `quantum-tools`
  group pins it with `openqasm3` and `antlr4-python3-runtime`, so `qasm3.loads`
  on a Kaggle kernel needs `--with quantum-tools`.
- cupy and jax are installed on the host and pinned nowhere for Kaggle; the
  host jaxlib has no CUDA support.
- The seven group pins added after the twelve-pin kernel run have not been
  installed on a kernel (above).

Other installed packages with a quantum-adjacent role, not given manuals:
networkx 3.7 (graphs), opt_einsum 3.4.0 (contraction paths; cotengra's
sibling), sparse 0.17.0 (sparse arrays), optuna 4.9.0 (cotengra's default
hyper-optimizer library), optax 0.2.6 and flax (JAX training), tensorflow
2.21.0, numpy-quaternion 2024.0.13 (Cayley-Calculator), cvxopt 1.3.3.
