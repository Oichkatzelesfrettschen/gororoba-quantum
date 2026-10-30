# DeMarrais tower campaign: CZ-graph Pauli propagation on Tuna-17 and QX

The campaign labels its circuits with Cayley-Dickson levels from 16D to 8192D and with Robert de Marrais's
zero-divisor structures (box-kites, sand mandalas, cowbird eggs, kite-chain middens). The Quantum Inspire circuits
carry none of that algebra: every one is a Clifford circuit on a fixed CZ graph whose outcome is fixed by which
qubits receive an X. The hardware runs measure Tuna-17's fidelity on that circuit, and the labels change only the X
positions.

## What the circuits compute

Each circuit is H on every qubit, one CZ layer, X on a set of hub qubits, the same CZ layer, H on every qubit, and a
measurement. Since CZ X_j CZ = X_j Z_N(j) for the CZ neighbourhood N(j), and H exchanges Z and X, the output is the
single basis state whose bit q is the parity of the X'd hubs adjacent to q.
[`pauli_propagation.py`](pauli_propagation.py) parses all eighteen circuits, derives each outcome from the edge
list and hub set alone, and requires it to equal the exact statevector and the manifest's `ideal_shot_string`
(qubit 0 rightmost); [pauli-propagation.json](pauli-propagation.json) records the result, replayed by gate
`core-demarrais-pauli-propagation-replay`.

| Device | CZ graph | Circuits | X hubs per circuit |
|---|---|---|---|
| `tuna_17` (17 transmons) | its 18 native couplers, applied twice (36 CZ) | 9, labelled 8192D, 4096D and 32D | 0 to 4 |
| `QXsinglenodesimulator` | one 10-edge graph | 9, labelled 1024D, 512D and 32D | 0 to 4 |

On each device every circuit uses the same graph. The "32D control", "4096D control" and "8192D pure shell"
circuits differ only in their hub sets, `cd_core` enters no gate, and no circuit's ideal outcome changes when an
algebraic property is removed, so the campaign fails the mutation test of
[the algebra circuit rules](../../notes/algebra_circuit_rules.md#hardware-probes). The analysis's "two-path
destructive interference" is Z Z = I on a qubit with two X'd neighbours. The "sleeper null" removes every X, so it
checks readout bias and the CZ layers, not an algebraic property.

## Measured on Tuna-17

Nine jobs, 75536 shots each (batches 903568, 903631 and 903682; jobs 1642194 to 1642196, 1642263 to 1642265 and
1642316 to 1642318), read from each run's `analysis.json`. The analysis groups the data qubits with an odd number of X'd neighbours
(ideal 1; it names them one-path, though in `explore_8192d_pure` qubit 12 has three) and those with none (ideal 0;
a qubit with two X'd neighbours, also ideal 0, falls in neither group).

| Circuit label | Hubs | Mean P(1), odd-parity qubits | Mean P(1), no-neighbour qubits | Full-string match | Sentinel herald |
|---|---|---:|---:|---:|---:|
| `midden` | 1, 8, 14 | 0.687 | 0.408 | 0.0138 | 0.161 |
| `cowbird` | 2, 7, 15 | 0.723 | 0.383 | 0.0135 | 0.147 |
| `dmz` | 3, 9, 13 | 0.857 | 0.261 | 0.0119 | 0.129 |
| `ctrl_low_32d` | 1, 2 | 0.682 | 0.316 | 0.0092 | 0.128 |
| `ctrl_mid_4096d` | 3, 8, 13 | 0.674 | 0.260 | 0.0089 | 0.125 |
| `explore_8192d_pure` | 8, 14, 15 | 0.686 | 0.353 | 0.0090 | 0.141 |
| `explore_8192d_catamaran` | 1, 2, 8, 15 | 0.736 | 0.390 | 0.0131 | 0.148 |
| `explore_8192d_dmz` | 2, 8, 14 | 0.761 | 0.389 | 0.0117 | 0.142 |
| `null_8192d_sleeper` | none | none | 0.298 | 0.0100 | 0.111 |

The "32D control" reads the same bright and dark levels as the "8192D" circuits. The sentinel herald keeps the shots
whose nine sentinel qubits all read 0, and at the measured per-qubit error that is about 0.79^9 of them, so a
heralded contrast rises by error detection rather than interference. Across the campaign Tuna-17's odd-parity
qubits read 0.67 to 0.86 and its no-neighbour qubits 0.26 to 0.41 on a two-layer, 36-CZ Clifford circuit.

The QX simulator returns each circuit's parity string on every one of its 2048 shots, as a noiseless simulator of a
deterministic Clifford circuit must.

## Quandela tower cases

[`scripts/qd_demarrais_tower.py`](../../../scripts/qd_demarrais_tower.py) builds 12- and 24-mode cases
(`results/quandela/cases/demarrais_tower_8192d/`, `job-dm1` to `job-dm4`) from the 12-mode equitable-partition
quotients of the kite-chain middens. One provider job ran: `sim:belenos` job-dm4 (`0866fc0c`, retained under
`results/quandela/runs/2026-10-30T044809Z-sim_belenos-demarrais_tower_8192d-job-dm4`). Its first nine settings, the
16D to 4096D controls, returned 10000 samples each at the ideal dispersive contrast D = 1.0; the provider's compiler
then failed at the first 8192D setting with "Circuit optimizer: No trial converged", so no 8192D or null setting
returned counts and the analysis withholds its verdict. No QPU job of these cases exists. The analysis reports the
dispersive contrast and decides only against a returned null arm; it certifies no coherence, because a single photon
entering one mode reaches the dispersive modes through the quotient unitary from an incoherent input as well. The tower's `simulate_local_twin` is a local Perceval model with calibration figures, so its
counts describe the model, not `qpu:ascella` or `qpu:belenos`, and it writes to the ignored `docs/local/`.

## Classical structure computations

[`gororoba_quantum/demarrais_structures.py`](../../../gororoba_quantum/demarrais_structures.py) computes the
tower's combinatorics: the 14-level taxonomy to 8192D with its positive cyclic triple counts, the seven sedenion
box-kites with their signed-adjacency spectrum {-4, 0, 0, 0, 2, 2}, the pathion emanation tables and their
high-strut DMZ cell counts 24(2^(N-3) - 1) on the first eight struts above 2^(N-2), and the cowbird octonion eggs certified with `python-flint`. Its
`--self-test` and the unit tests replay them; the full-tower tests take minutes and run in the audit tier. These are
computations from the module's own constructors; no source-registry check compares them with de Marrais's
published tables.

## What an algebra test would need

The X positions or the CZ signs would have to come from a `cd_core`-certified zero-divisor pair, and a mutated
circuit that breaks that pair (a sign flip, a swapped index) would have to change the predicted outcome, decided
against a null arm, as the box-kite photonic cases on Quandela do with their t = +1 and t = -1 blocks.

## Replay

```sh
export PYTHON="${PYTHON:-python3}" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" docs/evidence/demarrais-8192d-cross-platform/pauli_propagation.py --check \
  docs/evidence/demarrais-8192d-cross-platform/pauli-propagation.json
"$PYTHON" scripts/qi_demarrais_tower.py --analyze RUN_DIR --out /dev/stdout
"$PYTHON" gororoba_quantum/demarrais_structures.py --self-test
```
