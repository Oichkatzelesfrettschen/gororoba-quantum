# mthree

## NAME

mthree 3.0.0 (runningman 2.3.0) -- matrix-free measurement mitigation (M3)
of readout error in measured bitstring distributions.

## SYNOPSIS

```python
import mthree
mit = mthree.M3Mitigation(backend_or_None)
mit.cals_from_system(qubits, shots=N, async_cal=False)   # calibrate on a backend (Aer here)
mit.cals_from_matrices(list_of_2x2)                      # calibrate from known assignment matrices
quasi = mit.apply_correction(counts, qubits)             # QuasiDistribution
quasi.expval()                                           # <Z...Z> from quasiprobabilities
```

| Substrate | Status |
| --- | --- |
| Build host | python-mthree 3.0.0 and python-runningman 2.3.0 (Arch) |
| Kaggle | `mthree==3.0.0` and `runningman==2.3.0` in the `quantum-tools` group; both installed at their pins on the CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` (`pin_groups.json`) |

## CAPABILITIES IN THIS REPOSITORY

- The readout-factor question. A single-qubit assignment matrix
  `A = [[1-e10, e01], [e10, 1-e01]]` (columns are the prepared state) scales a
  measured Z expectation by `A[0,0] + A[1,1] - 1 = 1 - P(1|0) - P(0|1)`.
  `results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md` reads Ramsey visibility
  against this factor (0.47 and 0.60 on Kingston qubits 0 and 1) rather than
  against decoherence. `M3Mitigation.single_qubit_cals` holds exactly these
  matrices after any calibration, so the factor is `a[0,0] + a[1,1] - 1` per
  qubit and the same quantity the mitigator inverts.
- Replay of retained jobs: `cals_from_matrices` builds a mitigator from any
  list of 2 x 2 assignment matrices with no backend. Fed the e10/e01 pairs of
  `docs/evidence/calibration/*.json` it reproduces the reported readout
  channel (the replay noise model); fed matrices measured from the job's own
  preparation baselines it corrects that job's counts. The two differ on
  Kingston qubits 0 and 1 (see Traps).
- Aer calibration: `M3Mitigation(AerSimulator)` followed by `cals_from_system`
  measures the assignment matrices the noise model implements, which checks
  that the replay noise reproduces the calibration (example below).
- Dynamic circuits: `final_measurement_mapping` reports, per classical bit, the
  qubit of the last measurement writing it. A mid-circuit measurement whose
  classical bit is not overwritten stays in the map as if it were a final
  readout, so a circuit with feed-forward needs its map built by hand.
- Not covered: correlated readout error beyond the matrix-free subspace
  truncation, and measurement variants `measure_2` (a separate calibration).

## API ENTRY POINTS

`mthree` public names (18), by introspection:

classes:

```text
  M3Mitigation
```

functions:

```text
  about
```

modules:

```text
  circuits, classes, converters, direct, exceptions, expval, generators,
  iterative, matrix, matvec, mitigation, norms, probability, utils, version
```

other:

```text
  openmp
```

`mthree:M3Mitigation` public names (10), by introspection:

functions:

```text
  apply_correction, cals_from_file, cals_from_matrices, cals_from_system,
  cals_to_file, cals_to_matrices, readout_fidelity, reduced_cal_matrix,
  tensored_cals_from_file, tensored_cals_from_system
```

`mthree.utils` public names (14), by introspection:

classes:

```text
  M3Error, ProbCollection, ProbDistribution, QuasiCollection,
  QuasiDistribution
```

functions:

```text
  counts_to_vector, expval, expval_and_stddev, final_measurement_mapping,
  marg_dist, marginal_distribution, stddev, vector_to_quasiprobs
```

modules:

```text
  np
```

## EXAMPLES

### Mitigator from the retained calibration, no backend

```python
import json
import numpy as np, mthree

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
# mthree columns are the prepared state, rows the measured one: A[i, j] = P(read i | prepared j).
# The snapshot stores e10 = P(1|0) and e01 = P(0|1).
mats = [np.array([[1 - x["e10"], x["e01"]], [x["e10"], 1 - x["e01"]]]) for x in snap["qubits"][:2]]
m = mthree.M3Mitigation(None)
m.cals_from_matrices(mats)
for k, a in enumerate(m.single_qubit_cals):
    print(f"qubit {k}: readout factor 1 - P(1|0) - P(0|1) = {a[0, 0] + a[1, 1] - 1:.6f}")

counts = {"00": 9000, "01": 600, "10": 200, "11": 200}
qp = m.apply_correction(counts, [0, 1], details=True)
print({k: round(float(v), 6) for k, v in qp[0].items()}, qp[1]["method"], qp[1]["dimension"])
print("sum of quasiprobabilities", round(float(sum(qp[0].values())), 9),
      " min", round(float(min(qp[0].values())), 6))
# rightmost key bit is qubits[0]: row '01', column '00' is qubit 0 flipping 0 -> 1
red = m.reduced_cal_matrix(counts, [0, 1])[0]
print("P(read 01 | prepared 00) =", round(float(red[1, 0]), 6), " e10 of qubit 0 =", snap["qubits"][0]["e10"])
```

Output:

```text
qubit 0: readout factor 1 - P(1|0) - P(0|1) = 0.981689
qubit 1: readout factor 1 - P(1|0) - P(0|1) = 0.989990
{'00': 0.905901, '01': 0.05764, '10': 0.016337, '11': 0.020121} direct 4
sum of quasiprobabilities 0.99999994  min 0.016337
P(read 01 | prepared 00) = 0.003648  e10 of qubit 0 = 0.003662109375
```

### Calibrating against the density-matrix replay

```python
import json, sys
import numpy as np, mthree
sys.path.insert(0, "gororoba_quantum")
import calibration_snapshot as cs
from qiskit import QuantumCircuit, transpile

snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
sim = cs.noise_simulator(snap)               # 156-qubit Target, density-matrix Aer, Kingston noise
mit = mthree.M3Mitigation(sim)
mit.cals_from_system([0, 1], shots=4000, async_cal=False)   # runs balanced/independent cals on the Aer backend
for k, a in enumerate(mit.single_qubit_cals[:2]):
    print(f"qubit {k} measured readout factor {a[0, 0] + a[1, 1] - 1:.4f}")

theta = 2 * np.arccos(np.sqrt(0.9))          # ideal P(0) = 0.9, <Z> = 0.8
qc = QuantumCircuit(2, 2)
qc.ry(theta, 0); qc.ry(theta, 1); qc.measure([0, 1], [0, 1])
tc = transpile(qc, sim, initial_layout=[0, 1], optimization_level=1, seed_transpiler=1)
counts = sim.run(tc, shots=100000, seed_simulator=5).result().get_counts()
maps = mthree.utils.final_measurement_mapping(tc)
print("measurement map", maps)
quasi = mit.apply_correction(counts, maps)
raw = {k: v / 100000 for k, v in counts.items()}
z0_raw = sum(p * (1 if k[-1] == "0" else -1) for k, p in raw.items())
print("raw <Z0>", round(z0_raw, 4), " corrected <Z0>", round(float(sum(p * (1 if k[-1] == "0" else -1) for k, p in quasi.items())), 4), " ideal 0.8")
```

Output:

```text
qubit 0 measured readout factor 0.9827
qubit 1 measured readout factor 0.9870
measurement map {0: 0, 1: 1}
raw <Z0> 0.7946  corrected <Z0> 0.7986  ideal 0.8
```

## INTEROP WITH QISKIT

| Path | Result on this host (qiskit 2.5.2, qiskit-aer 0.17.2) |
| --- | --- |
| `M3Mitigation(AerSimulator)` from `calibration_snapshot.noise_simulator`, `cals_from_system([0, 1], async_cal=False)` | works; runs the calibration circuits on the Aer backend |
| `cals_from_matrices(list_of_2x2)` with `M3Mitigation(None)` | works; no backend |
| `apply_correction(counts, mthree.utils.final_measurement_mapping(transpiled_circuit))` | works for static circuits |
| IBM Runtime mode (`runtime_mode=Batch/Session`) and `Sampler` calibration | not run: needs an IBM service |
| `measure_2` calibration | not run |

The key convention: the rightmost bit of a counts key belongs to `qubits[0]`.
The example confirms it: `P(read 01 | prepared 00)` equals the e10 of qubit 0.

## CPU AND GPU

CPU. The correction is a solve in the observed-bitstring subspace: `method`
is `auto`, `direct` or `iterative`, and `auto` switches to the iterative
solver at `iter_threshold` bitstrings (default 4096). `mthree.openmp` is a
boolean that reads False on this host. No GPU path exists in the package.

## TRAPS

- The snapshot's `e10` and `e01` are reported backend properties, so a replay applies the reported readout channel and not the measured one. `results/live/ZERO_DIVISOR_AND_CORNER_FINDINGS.md` records Kingston qubits 0 and 1 misassigning the ground state 39 and 27 percent of the time and the excited state 14 and 12 percent on a device run, against reported readout errors below 1 percent, with Ramsey visibilities matching readout factors of 0.47 and 0.60. The examples above use the same qubits and recover the reported factor (about 0.98); they do not reproduce the measured fault. Mitigating or interpreting a retained job needs assignment matrices from that job's own preparation baselines.
- A calibration from 4000 shots carries sampling error of about 0.002 in each
  matrix element; the example's measured factor for qubit 0 (0.9843) differs
  from the snapshot's (0.9817) by that amount. Use `cals_from_matrices` for the
  retained numbers.
- Quasiprobabilities can be negative; they sum to 1 only to float32 precision
  (the example prints 0.99999994).
- Columns are prepared states, rows are measured states; the snapshot JSON
  stores `e10 = P(1|0)` and `e01 = P(0|1)`, which transposes naturally if
  copied without thought.
- `final_measurement_mapping` on a circuit with a mid-circuit measurement of
  qubit 0 into bit 0 followed by a CX still lists `{0: 0}`.
- `cals_from_system` defaults to async calibration; pass `async_cal=False`
  when the next line needs the matrices, as the example does.

## LICENSE

Apache-2.0 (mthree and runningman).
