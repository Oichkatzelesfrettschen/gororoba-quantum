# quimb (with cotengra and autoray)

## NAME

quimb 1.15.0 -- tensor-network circuit simulation and contraction;
cotengra 0.8.2 -- contraction-path search; autoray 0.11.0 -- array-library
dispatch (numpy, torch, cupy, jax).

## SYNOPSIS

```python
import quimb as qu, quimb.tensor as qtn
c = qtn.Circuit.from_openqasm2_str(qasm)       # or qtn.Circuit(n) + c.apply_gate("CZ", 0, 1)
c.local_expectation(qu.pauli("Z"), 11)         # lightcone contraction
c.amplitude("0" * n); c.sample(k); c.to_dense()
qtn.CircuitMPS(n)                              # matrix-product-state circuit
```

| Substrate | Status |
| --- | --- |
| Build host | python-quimb 1.15.0, python-cotengra 0.8.2, python-autoray 0.11.0 (Arch); torch 2.14.1 and cupy 14.2.0 see CUDA on the RTX 4070 Ti |
| Kaggle | `quimb==1.15.0`, `cotengra==0.8.2`, `autoray==0.11.0` in the `quantum-tools` group (pip resolves their dependencies); torch comes from the Kaggle image (2.11.0 in the recorded probes); cupy is not pinned by the repository; the three pins installed on the CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` (`pin_groups.json`) |

## CAPABILITIES IN THIS REPOSITORY

- Ideal simulation beyond the 14-qubit density-matrix limit: a 23-qubit
  CZ-basis circuit built along a Kingston coupling path gives the same
  `<Z_11>` as the Qiskit statevector (example). A density matrix of that
  width needs 1024 TiB. Expectation values of local observables use the
  reverse lightcone, so cost tracks depth and connectivity instead of 2^n.
  Statevector and MPS here are ideal semantics; noise is outside this
  package's use in the repository, and a noisy question beyond 14 qubits
  remains an IBM case (root AGENTS.md routing rule).
- Amplitudes, marginals and bitstring sampling (`amplitude`, `compute_marginal`,
  `sample`, `sample_chaotic`) from a tensor network, with `cotengra` choosing the
  contraction tree; `Circuit.amplitude_tn` exposes the network for the
  path-cost numbers in the example.
- `CircuitMPS` and `CircuitPermMPS` for low-entanglement states with a
  bond-dimension cap (`max_bond`, `cutoff`; signature read, not run in this manual). `Circuit`
  also takes a `to_backend` argument for array conversion (read, not run).
- ISA input: `Circuit.from_openqasm2_str` accepts `rz`, `sx`, `cz`
  from a Qiskit QASM 2 dump (verified, example). The circuit must be reindexed
  to the used qubits first; a 156-qubit register builds a 156-site network.
- Linear algebra on tensors: `quimb.tensor` and `autoray` run the same
  contraction on numpy, torch or cupy arrays, the route to GPU.
- ZX diagrams contract to quimb tensors through `pyzx.to_quimb_tensor`
  (listed by introspection; not run).

## API ENTRY POINTS

`quimb.tensor:Circuit` public names (126), by introspection:

functions:

```text
  amplitude, amplitude_rehearse, amplitude_tn, apply_gate, apply_gate_raw,
  apply_gates, apply_to_arrays, bra_site_ind, calc_qubit_ordering, ccnot,
  ccx, ccy, ccz, clear_storage, cnot, compute_marginal,
  compute_marginal_rehearse, compute_marginal_tn, copy, cphase, crx, cry,
  crz, cswap, cu1, cu2, cu3, cx, cy, cz, draw, fredkin, from_gates,
  from_openqasm2_file, from_openqasm2_str, from_openqasm2_url,
  from_openqasm3_file, from_openqasm3_str, from_openqasm3_url, from_qasm,
  from_qasm_file, from_qasm_url, from_qsim_file, from_qsim_str,
  from_qsim_url, fsim, fsimg, gate_tag, get_gate_by_gate_circuits,
  get_params, get_psi, get_psi_reverse_lightcone, get_psi_simplified,
  get_qubit_distances, get_rdm_lightcone_simplified,
  get_reverse_lightcone_tags, get_uni, givens, givens2, h, hz_1_2, iden,
  iswap, ket_site_ind, local_expectation, local_expectation_rehearse,
  local_expectation_tn, partial_trace, partial_trace_rehearse,
  partial_trace_tn, phase, register_named_params,
  reordered_gates_dfs_clustered, round_tag, rx, rxx, ry, ryy, rz, rzz, s,
  sample, sample_chaotic, sample_chaotic_rehearse, sample_chaotic_tn,
  sample_gate_by_gate, sample_gate_by_gate_rehearse,
  sample_gate_by_gate_tns, sample_rehearse, sample_tns,
  schrodinger_contract, sdg, set_params, simulate_counts, su4, swap, sx,
  sxdg, t, tdg, to_dense, to_dense_rehearse, to_dense_tn, toffoli, u1, u2,
  u3, update_params_from, w_1_2, x, x_1_2, xeb, xeb_ex, xx_minus_yy,
  xx_plus_yy, y, y_1_2, z, z_1_2
```

other:

```text
  gates, named_param_names, named_params, num_gates, param_expressions, psi,
  uni
```

Tensor-network classes in `quimb.tensor`:

`quimb.tensor` public names (231), by introspection:

cotengra:

`cotengra` public names (95), by introspection:

classes:

```text
  AutoHQOptimizer, AutoOptimizer, ContractionTree,
  ContractionTreeCompressed, ContractionTreeMulti, FlowCutterOptimizer,
  GreedyOptimizer, HyperCompressedOptimizer, HyperGraph,
  HyperMultiOptimizer, HyperOptimizer, OptimalOptimizer, PathOptimizer,
  QuickBBOptimizer, RandomGreedyOptimizer, RandomOptimizer,
  ReusableHyperCompressedOptimizer, ReusableHyperOptimizer,
  ReusableRandomGreedyOptimizer, SliceFinder
```

functions:

```text
  UniformOptimizer, array_contract, array_contract_expression,
  array_contract_path, array_contract_tree, auto_hq_optimize, auto_optimize,
  contract, contract_expression, edge_path_to_linear, edge_path_to_ssa,
  einsum, einsum_expression, einsum_tree, get_hyper_space, get_hypergraph,
  get_symbol, get_symbol_map, greedy_optimize, hash_contraction,
  hyper_compressed_optimize, hyper_optimize, linear_to_ssa,
  list_hyper_functions, ncon, optimal_optimize, optimal_outer_optimize,
  optimize_flowcutter, optimize_quickbb, plot_contractions,
  plot_contractions_alt, plot_scatter, plot_scatter_alt, plot_slicings,
  plot_slicings_alt, plot_tree, plot_tree_ring, plot_tree_span,
  plot_tree_tent, plot_trials, plot_trials_alt, random_greedy_optimize,
  register_preset, ssa_to_linear
```

autoray:

`autoray` public names (48), by introspection:

functions:

```text
  astype, autojit, backend_like, compose, conj, dag, do, from_numpy,
  get_backend, get_common_dtype, get_dtype_name, get_lib_fn, get_namespace,
  imag, infer_backend, infer_backend_device_dtype, infer_backend_multi,
  is_array, is_scalar, ndim, real, register_backend, register_function,
  reshape, set_backend, shape, size, stop_gradient, to, to_backend_dtype,
  to_device, to_numpy, transpose, tree_apply, tree_flatten, tree_iter,
  tree_map, tree_unflatten
```

## EXAMPLES

### CZ-basis circuit from Qiskit into quimb, then 23 qubits

```python
import json, sys, time
sys.path.insert(0, "gororoba_quantum")
import numpy as np
import quimb as qu
import quimb.tensor as qtn
import warnings
warnings.filterwarnings('ignore', module='cotengra')
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit.quantum_info import SparsePauliOp, Statevector
import calibration_snapshot as cs

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
view = cs.noise_model(snap)[0]            # BackendV2 carrying the Kingston Target (cz, sx, x, rz, id)


def layered(n, layers, seed):
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n)
    for layer in range(layers):
        for q in range(n):
            qc.ry(rng.uniform(0, 3), q)
        for q in range(layer % 2, n - 1, 2):
            qc.cz(q, q + 1)
    return qc


def compact(isa, qubits):
    """Re-index the used physical qubits 0..n-1 so the QASM register holds only them."""
    out = QuantumCircuit(len(qubits))
    for inst in isa.data:
        out.append(inst.operation, [qubits.index(isa.find_bit(q).index) for q in inst.qubits])
    return out


n = 12
isa = transpile(layered(n, 4, 1), view, initial_layout=list(range(n)), optimization_level=1, seed_transpiler=1)
print("ISA ops:", dict(isa.count_ops()), " register width:", isa.num_qubits)
small = compact(isa, list(range(n)))
circ = qtn.Circuit.from_openqasm2_str(qasm2.dumps(small))
dense = np.asarray(circ.to_dense()).ravel()
ref = Statevector(small).data
# quimb orders qubit 0 as the most significant index; Qiskit's little-endian vector reverses the bits
ref_be = ref.reshape([2] * n).transpose(list(range(n))[::-1]).ravel()
print("overlap |<quimb|qiskit>| =", round(abs(np.vdot(ref_be, dense)), 12))

# beyond the density-matrix limit: 23 qubits along a path of the Kingston coupling graph
path = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 35, 34, 33, 32, 31, 18]
m = len(path)
isa = transpile(layered(m, 4, 2), view, initial_layout=path, optimization_level=1, seed_transpiler=1)
big = compact(isa, path)
c23 = qtn.Circuit.from_openqasm2_str(qasm2.dumps(big))
t0 = time.time()
z = c23.local_expectation(qu.pauli("Z"), 11)
print("23 qubits,", c23.num_gates, "gates: quimb <Z_11> =", round(float(np.real(z)), 8))
exact = Statevector(big).expectation_value(SparsePauliOp("Z"), [11])   # Qiskit qubit 11 = quimb site 11 for a single-site operator
print("Qiskit Statevector <Z_11> =", round(float(exact.real), 8), " (a 23-qubit density matrix needs", 16 * 4**m // 2**40, "TiB)")
```

Output:

```text
ISA ops: {'rz': 92, 'sx': 92, 'cz': 22}  register width: 156
overlap |<quimb|qiskit>| = 1.0
23 qubits, 400 gates: quimb <Z_11> = -0.12788207
Qiskit Statevector <Z_11> = -0.12788207  (a 23-qubit density matrix needs 1024 TiB)
```

### Torch and CuPy arrays, and a cotengra path

The first line of the script is the marker that this example uses the GPU.

```python
# gpu
import warnings
warnings.filterwarnings("ignore")
import numpy as np, quimb as qu, quimb.tensor as qtn
import cupy, torch
import autoray as ar
import cotengra as ctg

n = 22


def make():
    rng = np.random.default_rng(0)
    c = qtn.Circuit(n)
    for layer in range(6):
        for q in range(n):
            c.apply_gate("RY", rng.uniform(0, 3), q)
        for q in range(layer % 2, n - 1, 2):
            c.apply_gate("CZ", q, q + 1)
    return c


c = make()

Z = qu.pauli("Z")
print("numpy  ", round(complex(c.local_expectation(Z, 5)).real, 10))
for name, conv, op in (
    ("torch-cpu ", lambda x: torch.tensor(x), torch.tensor(Z)),
    ("torch-cuda", lambda x: torch.tensor(x, device="cuda"), torch.tensor(Z, device="cuda")),
    ("cupy      ", cupy.asarray, cupy.asarray(Z)),
):
    c2 = make()   # a circuit that already evaluated an expectation keeps numpy caches; build fresh
    c2.apply_to_arrays(conv)
    t0 = c2.psi.tensors[0].data
    print(name, round(complex(c2.local_expectation(op, 5)).real, 10), "| array:", ar.infer_backend(t0), type(t0).__module__.split(".")[0],
          getattr(t0, "device", ""))

try:
    ctg.HyperOptimizer(max_repeats=8, seed=0)
except TypeError as exc:   # default optlib is optuna on this host
    print("HyperOptimizer(seed=0) with the default optlib:", exc)
tn = c.amplitude_tn("0" * n)
tree = tn.contraction_tree(optimize=ctg.HyperOptimizer(max_repeats=8, optlib="random", seed=0, progbar=False))
print("amplitude tree: tensors", tn.num_tensors, " log2 width", round(tree.contraction_width(), 2),
      " log10 flops", round(tree.contraction_cost(log=10), 2))
```

Output:

```text
numpy   -0.2382780325
torch-cpu  -0.2382780325 | array: torch torch cpu
torch-cuda -0.2382780325 | array: torch torch cuda:0
cupy       -0.2382780325 | array: cupy cupy <CUDA Device 0>
HyperOptimizer(seed=0) with the default optlib: create_study() got an unexpected keyword argument 'seed'
amplitude tree: tensors 93  log2 width 3.0  log10 flops 2.98
```

## INTEROP WITH QISKIT

| Path | Result on this host (qiskit 2.5.2, quimb 1.15.0) |
| --- | --- |
| `qasm2.dumps(circuit)` then `Circuit.from_openqasm2_str` | works for `rz`, `sx`, `cz`; overlap with `Statevector` is 1.0 at 12 qubits |
| `qasm3.dumps(circuit)` then `Circuit.from_openqasm3_str` on an ISA circuit | fails: `NotImplementedError: Unknown qubit identifier: $0` (physical-qubit syntax) |
| `qasm3.dumps` of a circuit on virtual qubits, unitary | works (`N = 2` in the dynamic-circuit example) |
| a circuit with `if_else` | fails: `NotImplementedError: The following instruction is not supported: if (c[0]) {` |

The dense vector of `Circuit.to_dense()` indexes qubit 0 as the most
significant bit; Qiskit's is little-endian. The example transposes the
Qiskit vector's axes before comparing; a single-site operator uses the same
site number on both sides (verified at 23 qubits).

```python
import warnings
warnings.filterwarnings("ignore")
import pyzx as zx
import quimb.tensor as qtn
from qiskit import QuantumCircuit, qasm2, qasm3

qc = QuantumCircuit(2, 2)
qc.h(0); qc.measure(0, 0)
with qc.if_test((qc.clbits[0], 1)):
    qc.x(1)
qc.measure(1, 1)

for label, call in (
    ("qasm2.dumps", lambda: qasm2.dumps(qc)),
    ("pyzx.Circuit.from_qasm(qasm3)", lambda: zx.Circuit.from_qasm(qasm3.dumps(qc))),
    ("quimb from_openqasm3_str", lambda: qtn.Circuit.from_openqasm3_str(qasm3.dumps(qc))),
):
    try:
        call()
        print(label, "accepted")
    except Exception as e:
        print(f"{label}: {type(e).__name__}: {str(e).splitlines()[0][:110]}")

plain = QuantumCircuit(2); plain.h(0); plain.cx(0, 1)
print("pyzx from qasm3 (unitary):", zx.Circuit.from_qasm(qasm3.dumps(plain)).stats().splitlines()[0].strip())
print("quimb from qasm3 (unitary): N =", qtn.Circuit.from_openqasm3_str(qasm3.dumps(plain)).N)
```

Output:

```text
qasm2.dumps: QASM2ExportError: 'OpenQASM 2 only supports register-equality conditions'
pyzx.Circuit.from_qasm(qasm3): TypeError: Phase expression 'c[0]' contains unbound variables
quimb from_openqasm3_str: NotImplementedError: The following instruction is not supported: if (c[0]) {
pyzx from qasm3 (unitary): Circuit  on 2 qubits with 2 gates.
quimb from qasm3 (unitary): N = 2
```

## CPU AND GPU

- CPU: default numpy arrays; cotengra searches paths on the CPU.
- GPU: convert tensors with `circuit.apply_to_arrays(fn)` where `fn` moves each
  array (`torch.tensor(x, device="cuda")` or `cupy.asarray`) and pass an
  operator of the same array type to `local_expectation`. The example
  reproduces the numpy value to 10 digits on `torch-cpu`, `torch-cuda` and
  `cupy`. The 22-qubit lightcone is small; no speed-up is claimed.
- JAX is installed without CUDA support on the build host (`jax.devices()`
  returns `['cpu']`), so quimb on JAX runs on the CPU here.
- Kaggle GPU kernels carry torch from the image; quimb on cupy needs cupy
  installed in the kernel, which the repository does not do.

## TRAPS

- A circuit that has already evaluated an expectation caches numpy
  intermediates; `apply_to_arrays` on it, then a second `local_expectation`,
  raised `TypeError: expected Tensor as element 1 in argument 1, but got
  numpy.ndarray` (observed). Build a fresh circuit for each array backend.
- `cotengra.HyperOptimizer(seed=0)` fails with the default `optuna` library:
  `create_study() got an unexpected keyword argument 'seed'`; pass
  `optlib="random"` for a seeded search (example).
- `kahypar` is not installed; cotengra warns "Couldn't import `kahypar`" and
  uses the basic `labels` method, so path quality is lower than the package
  can reach.
- The last digits of an expectation change between runs (contraction order);
  compare to 1e-10, not bitwise.
- `qasm3.dumps` of a transpiled circuit uses `$n` physical qubits that quimb's
  QASM 3 importer rejects; use QASM 2 for unitary ISA circuits.

## LICENSE

Apache-2.0 for quimb, cotengra and autoray.
