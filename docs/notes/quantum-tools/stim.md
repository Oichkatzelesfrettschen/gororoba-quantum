# stim

## NAME

stim 1.16.0 -- fast Clifford (stabilizer) circuit simulation, Pauli-frame
sampling, detector error models.

## SYNOPSIS

```python
import stim
c = stim.Circuit("H 0\nCX 0 1\nM 0 1")
c.compile_sampler(seed=1).sample(shots)          # shots x measurements, bool
stim.Tableau.from_circuit(c_without_measurements) # Clifford as a tableau
stim.TableauSimulator()                           # interactive stabilizer state
c.detector_error_model(decompose_errors=True)     # for circuits with DETECTOR / noise
```

Versions and availability:

| Substrate | Status |
| --- | --- |
| Build host | python-stim 1.16.0 (Arch) |
| Kaggle | `stim==1.16.0` in the `quantum-tools` group (`push --with quantum-tools`); no kernel with the group has been run yet, so the wheel for Kaggle's Python is unmeasured |

## CAPABILITIES IN THIS REPOSITORY

- Clifford subcircuits of Heron ISA circuits. Design A of `designs.py` (the
  octonion associator witness) is Clifford end to end: its ISA form uses only
  `rz` at multiples of pi/2, `sx`, `x`, `cz`, stim reproduces the ideal
  outcome, and pyzx reports T-count 0 (example below). Stim's gate set contains H, S,
  S_DAG, SQRT_X, SQRT_X_DAG, X, Y, Z, CX, CZ, SWAP, so the `sx`, `x`, `cz`
  gates of the CZ basis map one to one; `rz` maps only at multiples of pi/2
  (S and Z), and every other angle is outside stim.
- Sampling a stabilizer circuit at thousands of qubits is a CPU task far past
  the 14-qubit Aer density-matrix limit. A noisy Clifford circuit with Pauli
  channels (`DEPOLARIZE1/2`, `X_ERROR`, `Z_ERROR`, `PAULI_CHANNEL_1/2`) samples
  at the same cost class. Aer's own `method="stabilizer"` also runs Clifford
  circuits (see [qiskit-aer.md](qiskit-aer.md)) and takes the same
  `AerSimulator` interface, so stim is the choice when detectors, Pauli-frame
  batches or a detector error model are the point.
- Mid-circuit measurement with feed-forward: the record is addressed as
  `rec[-k]` and a classically controlled Pauli is `CX rec[-1] q`, `CY`, `CZ`.
  Only Pauli corrections conditioned on measurement bits are expressible;
  Qiskit `if_else` blocks with arbitrary bodies are not.
- Tableau algebra: `Tableau.from_unitary_matrix`, `to_unitary_matrix`,
  `then`, `inverse`, `from_circuit`, `to_circuit("elimination")` give exact
  Clifford composition, inversion and resynthesis, which checks CZ-basis
  Clifford identities such as the Hadamard-test control wiring without
  statevectors.
- Readout and gate noise from the retained calibration: stim channels take
  probabilities. The mapping used below is a two-qubit depolarizing
  probability 5 e / 4 for an average gate infidelity e (the Target `error`)
  and a symmetric flip at the mean of e10 and e01.
- GF(2) content: `Tableau.to_numpy`, `PauliString.to_numpy` expose the binary
  symplectic form that [galois.md](galois.md) can row-reduce.
- Not covered: non-Clifford gates (T, CCZ, arbitrary rz); the CCZ normal form
  of `gororoba_quantum/boolean_anf.py` leaves stim at its first cubic term.
  Those circuits go to [quimb.md](quimb.md), [pyzx.md](pyzx.md) or Aer.

## API ENTRY POINTS

`stim` public names (44), by introspection:

classes:

```text
  Circuit, CircuitErrorLocation, CircuitErrorLocationStackFrame,
  CircuitInstruction, CircuitRepeatBlock, CircuitTargetsInsideInstruction,
  CliffordString, CompiledDemSampler, CompiledDetectorSampler,
  CompiledMeasurementSampler,
  CompiledMeasurementsToDetectionEventsConverter, DemInstruction,
  DemRepeatBlock, DemTarget, DemTargetWithCoords, DetectorErrorModel,
  ExplainedError, FlipSimulator, FlippedMeasurement, Flow, GateData,
  GateTarget, GateTargetWithCoords, PauliString, PauliStringIterator,
  Tableau, TableauIterator, TableauSimulator
```

functions:

```text
  gate_data, main, read_shot_data_file, target_combined_paulis,
  target_combiner, target_inv, target_logical_observable_id, target_pauli,
  target_rec, target_relative_detector_id, target_separator,
  target_sweep_bit, target_x, target_y, target_z, write_shot_data_file
```

Circuit methods used most:

`stim:Circuit` public names (50), by introspection:

functions:

```text
  append, append_from_stim_program_text, append_operation, approx_equals,
  clear, compile_detector_sampler, compile_m2d_converter, compile_sampler,
  copy, count_determined_measurements, decomposed, detecting_regions,
  detector_error_model, diagram, explain_detector_error_model_errors,
  flattened, flattened_operations, flow_generators, from_file, generated,
  get_detector_coordinates, get_final_qubit_coordinates, has_all_flows,
  has_flow, insert, inverse, likeliest_error_sat_problem, missing_detectors,
  pop, reference_detector_and_observable_signs, reference_sample,
  search_for_undetectable_logical_errors, shortest_error_sat_problem,
  shortest_graphlike_error, solve_flow_measurements,
  time_reversed_for_flows, to_crumble_url, to_file, to_qasm, to_quirk_url,
  to_tableau, with_inlined_feedback, without_noise, without_tags
```

other:

```text
  num_detectors, num_measurements, num_observables, num_qubits,
  num_sweep_bits, num_ticks
```

Tableau and simulator classes:

`stim:Tableau` public names (35), by introspection:

functions:

```text
  append, copy, from_circuit, from_conjugated_generators, from_named_gate,
  from_numpy, from_stabilizers, from_state_vector, from_unitary_matrix,
  inverse, inverse_x_output, inverse_x_output_pauli, inverse_y_output,
  inverse_y_output_pauli, inverse_z_output, inverse_z_output_pauli,
  iter_all, prepend, random, then, to_circuit, to_numpy, to_pauli_string,
  to_stabilizers, to_state_vector, to_unitary_matrix, x_output,
  x_output_pauli, x_sign, y_output, y_output_pauli, y_sign, z_output,
  z_output_pauli, z_sign
```

`stim:TableauSimulator` public names (67), by introspection:

functions:

```text
  c_xyz, c_zyx, canonical_stabilizers, cnot, copy, current_inverse_tableau,
  current_measurement_record, cx, cy, cz, depolarize1, depolarize2, do,
  do_circuit, do_pauli_string, do_tableau, h, h_xy, h_xz, h_yz, iswap,
  iswap_dag, measure, measure_kickback, measure_many, measure_observable,
  peek_bloch, peek_observable_expectation, peek_x, peek_y, peek_z,
  postselect_observable, postselect_x, postselect_y, postselect_z, reset,
  reset_x, reset_y, reset_z, s, s_dag, set_inverse_tableau, set_num_qubits,
  set_state_from_stabilizers, set_state_from_state_vector, sqrt_x,
  sqrt_x_dag, sqrt_y, sqrt_y_dag, state_vector, swap, x, x_error, xcx, xcy,
  xcz, y, y_error, ycx, ycy, ycz, z, z_error, zcx, zcy, zcz
```

other:

```text
  num_qubits
```

## EXAMPLES

Every block below was run on the build host from the repository root; the
output is what the run printed.

### Qiskit Clifford circuit to stim, checked against Qiskit

```python
import numpy as np, stim
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

NAMES = {"h": "H", "s": "S", "sdg": "S_DAG", "x": "X", "y": "Y", "z": "Z", "sx": "SQRT_X",
         "sxdg": "SQRT_X_DAG", "cx": "CX", "cz": "CZ", "swap": "SWAP", "id": "I"}

def qiskit_to_stim(qc):
    """Clifford gates, measure, reset and barrier of a Qiskit circuit as a stim.Circuit."""
    out = stim.Circuit()
    for inst in qc.data:
        name, qs = inst.operation.name, [qc.find_bit(q).index for q in inst.qubits]
        if name in NAMES:
            out.append(NAMES[name], qs)
        elif name == "measure":
            out.append("M", qs)
        elif name == "reset":
            out.append("R", qs)
        elif name == "barrier":
            out.append("TICK")
        else:
            raise ValueError(f"no stim Clifford for {name}")
    return out

qc = QuantumCircuit(3)
qc.h(0); qc.cx(0, 1); qc.s(1); qc.cz(1, 2); qc.sx(2)
sc = qiskit_to_stim(qc)
print(sc)
u_stim = stim.Tableau.from_circuit(sc).to_unitary_matrix(endian="little")
u_qk = Operator(qc).data
k = np.argmax(abs(u_qk))
phase = u_qk.flat[k] / u_stim.flat[k]
print("global phase", np.round(phase, 6), "max deviation", np.abs(u_qk - phase * u_stim).max())
print("from_unitary_matrix equals from_circuit:",
      stim.Tableau.from_unitary_matrix(u_qk, endian="little") == stim.Tableau.from_circuit(sc))
try:
    qiskit_to_stim(QuantumCircuit(1).compose(__import__("qiskit").circuit.library.TGate(), [0]))
except ValueError as e:
    print("non-Clifford:", e)
```

Output:

```text
H 0
CX 0 1
S 1
CZ 1 2
SQRT_X 2
global phase (0.707107+0.707107j) max deviation 0.0
from_unitary_matrix equals from_circuit: True
non-Clifford: no stim Clifford for t
```

### Design A on the CZ basis: stim, density-matrix replay and pyzx

```python
import json, sys, warnings
sys.path.insert(0, "gororoba_quantum")
warnings.filterwarnings("ignore")
import numpy as np
import pyzx as zx
import stim
from qiskit import QuantumCircuit, qasm2, transpile
import calibration_snapshot as cs
import designs

NAMES = {"h": "H", "s": "S", "sdg": "S_DAG", "x": "X", "y": "Y", "z": "Z", "sx": "SQRT_X",
         "sxdg": "SQRT_X_DAG", "cx": "CX", "cz": "CZ", "swap": "SWAP", "id": "I"}


def qiskit_to_stim(qc):
    out = stim.Circuit()
    for inst in qc.data:
        name, qs = inst.operation.name, [qc.find_bit(q).index for q in inst.qubits]
        if name == "rz":   # stim has S and Z only: accept rz at multiples of pi/2
            k = int(round(float(inst.operation.params[0]) / (np.pi / 2)))
            assert abs(float(inst.operation.params[0]) - k * np.pi / 2) < 1e-9, "rz angle is not a multiple of pi/2"
            out.append(["I", "S", "Z", "S_DAG"][k % 4], qs)
        elif name == "measure":
            out.append("M", qs)
        elif name == "barrier":
            out.append("TICK")
        else:
            out.append(NAMES[name], qs)
    return out


def main():
    snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
    sim = cs.noise_simulator(snap)
    design, k0, k1, diff_bit = designs.design_a_associator(1, 2)
    path = [0, 1, 2]
    isa = transpile(design, sim, initial_layout=path, optimization_level=1, seed_transpiler=1)
    compact = QuantumCircuit(3, 1)
    for inst in isa.data:
        compact.append(inst.operation, [isa.find_bit(q).index for q in inst.qubits],
                       [isa.find_bit(c).index for c in inst.clbits])
    print("Design A pair (1, 2):", dict(compact.count_ops()))
    sc = qiskit_to_stim(compact)
    bits = sc.compile_sampler(seed=1).sample(1000)
    print("stim: P(associator bit = 1) =", bits.mean(), "(ideal 1 for every pair)")
    noisy = sim.run(isa, shots=20000, seed_simulator=3).result().get_counts()
    print("Aer snapshot noise: P(bit = 1) =", noisy.get("1", 0) / 20000)
    unitary = compact.remove_final_measurements(inplace=False)
    z = zx.Circuit.from_qasm(qasm2.dumps(unitary))
    print("pyzx T-count of the unitary part:", z.tcount(), " Clifford gates:", z.stats_dict()["clifford"])


if __name__ == "__main__":
    main()
```

Output:

```text
Design A pair (1, 2): {'sx': 52, 'rz': 38, 'cz': 34, 'barrier': 3, 'x': 1, 'measure': 1}
stim: P(associator bit = 1) = 1.0 (ideal 1 for every pair)
Aer snapshot noise: P(bit = 1) = 0.95745
pyzx T-count of the unitary part: 0  Clifford gates: 125
```

### Sampling and stabilizer state

```python
import stim

c = stim.Circuit("""
R 0 1 2
H 0
CX 0 1 1 2
M 0 1 2
""")
print("shots:")
print(c.compile_sampler(seed=3).sample(6).astype(int))

# stabilizer state of the same GHZ preparation
sim = stim.TableauSimulator()
sim.do(stim.Circuit("H 0\nCX 0 1 1 2"))
print("stabilizers:", [str(s) for s in sim.canonical_stabilizers()])
print("<Z0 Z1> =", sim.peek_observable_expectation(stim.PauliString("ZZ_")))

# 100000 shots: bit-packed sampling speed is not asserted; counts are
import numpy as np
s = c.compile_sampler(seed=3).sample(100000)
print("P(000) =", (s.sum(axis=1) == 0).mean(), " P(111) =", (s.sum(axis=1) == 3).mean())
```

Output:

```text
shots:
[[0 0 0]
 [1 1 1]
 [1 1 1]
 [1 1 1]
 [0 0 0]
 [0 0 0]]
stabilizers: ['+XXX', '+Z_Z', '+_ZZ']
<Z0 Z1> = 1
P(000) = 0.49882  P(111) = 0.50118
```

### Feed-forward, detectors and a detector error model

```python
import stim

# Mid-circuit measurement with classical feed-forward: measure q0 of a Bell
# pair, then X-correct q1 conditioned on the record bit (stim: CX rec[-k] q).
c = stim.Circuit("""
H 0
CX 0 1
M 0
CX rec[-1] 1
M 1
DETECTOR rec[-1]
""")
print(c)
print("detectors:", c.num_detectors, " measurements:", c.num_measurements)
print(c.compile_sampler(seed=1).sample(5).astype(int))
print("detector events (always 0 after feed-forward):",
      c.compile_detector_sampler(seed=1).sample(8).astype(int).ravel())
print(c.with_inlined_feedback().__str__().replace("\n", " | "))

# Noisy repetition-code memory: detector error model by Pauli-frame analysis
rep = stim.Circuit.generated("repetition_code:memory", rounds=3, distance=3,
                             after_clifford_depolarization=0.001, before_measure_flip_probability=0.01)
dem = rep.detector_error_model(decompose_errors=True)
print("repetition code d=3 r=3:", rep.num_qubits, "qubits,", rep.num_detectors, "detectors,", dem.num_errors, "DEM errors")
print("shortest graphlike logical error:", len(rep.shortest_graphlike_error()), "faults")
```

Output:

```text
H 0
CX 0 1
M 0
CX rec[-1] 1
M 1
DETECTOR rec[-1]
detectors: 1  measurements: 2
[[1 0]
 [0 0]
 [0 0]
 [1 0]
 [0 0]]
detector events (always 0 after feed-forward): [0 0 0 0 0 0 0 0]
H 0 | CX 0 1 | M 0 1 | DETECTOR rec[-2] rec[-1]
repetition code d=3 r=3: 5 qubits, 8 detectors, 27 DEM errors
shortest graphlike logical error: 3 faults
```

### Calibration noise: stim against the density-matrix replay

The snapshot noise includes thermal relaxation, which is not a Pauli channel,
so the two columns agree to the extent that readout flips dominate.

```python
import json, sys
from pathlib import Path
import stim
sys.path.insert(0, "gororoba_quantum")
import calibration_snapshot as cs
from qiskit import QuantumCircuit, transpile

snap = json.loads(Path("docs/evidence/calibration/ibm_kingston.json").read_text())
qubits = [0, 1]
q = snap["qubits"]
cz = next(r for r in snap["instructions"]["cz"] if r["qargs"] == qubits)
flips = [(q[i]["e10"], q[i]["e01"]) for i in qubits]
print("cz error", cz["error"], " (e10, e01) per qubit", flips)

shots = 200000
sim = cs.noise_simulator(snap)
bell = QuantumCircuit(2, 2); bell.h(0); bell.cx(0, 1); bell.measure([0, 1], [0, 1])
tc = transpile(bell, sim, initial_layout=qubits, optimization_level=1, seed_transpiler=1)
counts = sim.run(tc, shots=shots, seed_simulator=7).result().get_counts()
print("aer counts", dict(sorted(counts.items())))
print("aer P(odd parity)", (counts.get("01", 0) + counts.get("10", 0)) / shots)

# stim: two-qubit depolarizing p = 5 e / 4 for average gate infidelity e, and
# a symmetric flip at the mean of e10 and e01 (stim X_ERROR is symmetric)
c = stim.Circuit()
c.append("H", [0]); c.append("CX", [0, 1])
c.append("DEPOLARIZE2", [0, 1], 1.25 * cz["error"])
for k, (e10, e01) in enumerate(flips):
    c.append("X_ERROR", [k], (e10 + e01) / 2)
c.append("M", [0, 1])
s = c.compile_sampler(seed=7).sample(shots)
print("stim P(odd parity)", (s[:, 0] ^ s[:, 1]).mean())
```

Output:

```text
cz error 0.0010693292575987279  (e10, e01) per qubit [(0.003662109375, 0.0146484375), (0.00390625, 0.006103515625)]
aer counts {'00': 99622, '01': 1059, '10': 1883, '11': 97436}
aer P(odd parity) 0.01471
stim P(odd parity) 0.01454
```

## INTEROP WITH QISKIT

Verified on this host with qiskit 2.5.2:

| Direction | Path | Result |
| --- | --- | --- |
| Qiskit to stim | no converter ships with stim; a gate-name table over `QuantumCircuit.data` (example above) | checked against `Operator(qc)` up to a global phase: deviation 0.0 |
| Qiskit unitary to stim | `stim.Tableau.from_unitary_matrix(Operator(qc).data, endian="little")` | equals the circuit tableau; a non-Clifford matrix raises `ValueError: The state vector wasn't a stabilizer state.` |
| stim to Qiskit | `Circuit.to_qasm(open_qasm_version=3)` then `qiskit.qasm3.loads` | loads; measurement records become a `rec` register |
| Qiskit dynamic circuit to stim | not supported | the converter raises on `if_else`; only `CX rec[-k] q` style Pauli feed-forward exists on the stim side |

### stim back to Qiskit through OpenQASM 3

```python
import stim
from qiskit import qasm3

c = stim.Circuit("H 0\nCX 0 1\nS 1\nCZ 1 2\nSQRT_X 2")
qasm = c.to_qasm(open_qasm_version=3)
print(qasm)
back = qasm3.loads(qasm)
print([(i.operation.name, [back.find_bit(q).index for q in i.qubits]) for i in back.data])
```

Output:

```text
OPENQASM 3.0;
include "stdgates.inc";

qreg q[3];

h q[0];
cx q[0], q[1];
s q[1];
cz q[1], q[2];
sx q[2];

[('h', [0]), ('cx', [0, 1]), ('s', [1]), ('cz', [1, 2]), ('sx', [2])]
```

`endian` is a required keyword of `Tableau.to_unitary_matrix` and
`from_unitary_matrix`; `"little"` matches Qiskit's bit order.

## CPU AND GPU

CPU only. Stim has no GPU backend. The batch size of `FlipSimulator` and the
bit-packed samplers (`sample_bit_packed`) set throughput; use the Kaggle CPU
kernel (4 cores) or the build host, never a GPU kernel, for stim work.

## TRAPS

- `Circuit.to_qasm` renames the measurement register to `rec` and raises
  `ValueError: The circuit contains noise, but OPENQASM 2 doesn't support noise
  operations` on a noisy circuit; call `without_noise()` first.
- Stim has no `rz(theta)`; transpiled ISA circuits contain arbitrary angles and
  fail the converter at the first non-Clifford `rz`.
- `X_ERROR(p)` is a symmetric flip. The calibration is asymmetric (qubit 0 of
  the retained Kingston export: `e10` 0.0037, `e01` 0.0146), and stim has no
  state-dependent flip, so the example uses the mean as an approximation; an
  exact asymmetric readout channel is applied to the sampled bits in NumPy.
- `DETECTOR` sets are only meaningful when the circuit's deterministic parities
  are declared; `Circuit.num_detectors` counts declared detectors, not
  checks the circuit implies.
- The decimal digits of a sampled mean change with the sampler seed; fix
  `seed=` as the examples do.

## LICENSE

Apache-2.0.
