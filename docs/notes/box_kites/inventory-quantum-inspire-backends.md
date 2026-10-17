# Backend constraints for the box-kite program (QX, Ry, Tuna-17)

Compiled 2026-10-17 from a read-only inventory of docs/evidence/quantum_inspire/catalogue.json,
docs/notes/quantum_inspire/ and scripts/qi_*.py. file:line references are into the repository.

## Limits

| Backend (type id) | qubits | shots default / max | job limit | jobs/batch |
|---|---|---|---|---|
| QX emulator (1) | 10 (catalogue.json:78) | 1024 / 2048 | 3600 s | 5 |
| Ry emulator (5) | 9 (:604) | 1024 / 1024 | 3600 s | 5 |
| Tuna-17 (7) | 17 (:1136) | 8192 / 131072 | 300 s | 5 |

Repository caps on hardware: scripts/qi_platform.py:70-71 HARDWARE_BATCH_CIRCUITS=3,
HARDWARE_QUEUED_BATCHES=1 (enforced in submit at :520-522). FAQ: 3 queued jobs per hardware backend.
QX doc conflict: KB says 26 qubits, API says 34 on Lisa (catalogue.json:27); account gets 10.

## Tuna-17 topology

24 undirected couplings: 0-1 0-2 1-4 2-4 2-5 3-5 3-6 4-7 4-8 5-8 5-9 6-9 7-10 7-11 8-11 8-12
9-12 10-13 11-13 11-14 12-14 12-15 14-16 15-16.
Degree 2: 0,1,3,6,10,13,15,16. Degree 3: 2,7,9,14. Degree 4: 4,5,8,11,12.
Hamiltonian path: 1-0-2-4-8-5-3-6-9-12-15-16-14-11-13-10-7. Longest induced path 10 qubits: 0-1-4-7-11-14-12-9-5-3.
K1,4 stars (5 qubits): centres 4 {1,2,7,8}, 5 {2,3,8,9}, 8 {4,5,11,12}, 11 {7,8,13,14}, 12 {8,9,14,15}.

Connected induced subgraph counts:
- 4 qubits: 108 sets; 100 trees (76 paths, 24 K1,3); 8 with a 4-cycle.
- 5 qubits: 239 sets; 199 trees (114 paths, 80 max-degree 3, 5 K1,4); 40 with a cycle.
- 8 qubits: 1469 sets; 704 induced trees (64 paths, 584 max-deg 3, 56 max-deg 4). Example path {0,1,2,5,7,8,10,11} order 1-0-2-5-8-11-7-10.
- 9 qubits: 2064 sets; 775 induced trees (26 paths, 672 max-deg 3, 77 max-deg 4). Example path {0,1,2,5,7,9,11,12,14}.

## QX emulator (1)

- Complete coupling, 45 pairs (no routing).
- Gates: H I S Sdag T Tdag X X90 Y Y90 Z Z90 mX90 mY90 mZ90 Rx Ry Rz U Rn CNOT CR CRk CZ SWAP, init, measure, reset, barrier, wait (catalogue.json:30-63). No compiler passes.
- Mid-circuit measurement allowed; binary-controlled gates allowed only here (site/kbase_cqasm-binary-controlled-gates.md:9).
- Result order: qubit 0 rightmost.

## Ry emulator (5, Rydberg)

- 9 atoms, rectangular lattice; INIT(x,y) only before any operation (cqasm.md:159-169).
- Native X Z Rx Rz T S H CNOT; compiler CNOTDecomposer then XZXDecomposer (catalogue.json:560-589).
- No mid-circuit measurement; all qubits measured at the end. Result order: qubit 0 LEFTMOST.
- Measured failure: runs/2026-10-16T211635Z-Rydberg/teleport.cq (bit[9] b, H, CNOT, X; no Rz, no measure) failed "error interpreting cQASM script". X-only diagnostic (no bit register, no measure) ran.
- Stale comment: qi_crosstalk_teleport_cases.py:205 says the emulator rejects measure statements, but the failing file has no measure. cqasm.md:226-229 records the open question (C4): bit register, H, CNOT, or a combination. A box-kite Ry run must first isolate this with a small diagnostic batch (X-only, +bit register, +H, +CNOT).

## Tuna-17 (7)

- Native Rx Ry Rz X90 Y90 mX90 mY90 X Y Z I S Sdag T Tdag CZ init measure reset barrier wait. Decomposed: H CNOT CR CRk SWAP Rn. Forbidden: Display, Not, binary-controlled gates, Toffoli.
- Angles quantize to pi/36. Durations: 1q 20 ns, CZ 60 ns, measure 800 ns, init 200/500 us.
- ALAP scheduling; wait(n) = n x 20 ns per qubit; barrier bounds scheduling; parallel readout needs a barrier.
- Mid-circuit measurement allowed; feed-forward post-processed.
- Declared width must be 17. Result order: qubit 0 rightmost.
- Compiler SWAP2CZDecomposer then CZDecomposer; no mapping or routing.
- 16384 shots in about 10-15 s.

## Existing scripts

- qi_crosstalk_teleport_cases.py: DRIVE_PULSES=40, WAIT_CYCLES=40; Tuna-17 stars T=0 (1,2), 3 (5,6), 4 (7,8), 11 (13,14), 12 (9,15); teleport paths 1-0-2-4, 5-3-6-9, 10-7-11-8, 14-12-15-16. Rydberg excluded from generation (:98).
- qi_zero_divisor_cases.py: frozen edge tuple :107-111; the retained 2026-10-16T221133Z run used regions {0,1,2,4,5}, {7,8,10,11,13} and {9,12,14,15,16}, each a four-cycle plus one pendant qubit (for example cycle 0-1-4-2-0 with pendant 2-5); the generator now places two regions off the excluded qubits below; cases dark, bright, fixture; emits H S Sdag T Tdag X Y Z X90 mX90 CZ barrier measure; readout-0 and readout-1 calibration circuits per batch.

## Tuna-17 qubit exclusions

Two kinds of evidence set the exclusions; a later batch showing recovery
re-admits a qubit.

Readout and pi-pulse. Readout batches of the Tuna-17 ring-down series on
2026-10-17 (all qubits idle in readout-0, all flipped in readout-1) read:

| qubit | 03:39Z | after the ~04:12Z platform calibration (04:18:39Z) | reading |
|---|---|---|---|
| q9 | idle P1 0.03 | idle P1 0.27 in a gate-free circuit | intrinsic shift; couplers 5-9, 6-9, 9-12 carry a mixed ZZ shift onto q5, q6, q12 |
| q0 | P1 0.85 prepared in 1 | P1 0.39 prepared in 1, idle below 0.04 | pi-pulse or T1 collapse, not readout |
| q6 | P1 0.67 prepared in 1 | P1 0.14 prepared in 1, idle below 0.04 | pi-pulse or T1 collapse, not readout |

Those batches are the readout pilot's runs; their raw records land with the
readout ring-down pull request (branch qi/readout-ringdown-pilot), and this
inventory cites them until that change retains them under
results/quantum_inspire/runs/.

Ramsey visibility. The retained coupler-ZZ map
(results/quantum_inspire/coupler_zz_tuna_17_analysis.json, runs
2026-10-16T224924Z-coupler_zz_tuna_17-batch-00..03) gives each qubit's
minimum Ramsey visibility over neighbor sectors at the 0.5 us and 2 us
delays. Its values split into q5 0.043, q6 0.270, q7 0.084 and every other
qubit at 0.755 or above, so a floor of 0.5 excludes q5, q6 and q7;
`visibility_excluded()` in the zero-divisor series branch derives that set from the
retained file.

The excluded set is {0, 5, 6, 7, 9}. Layouts use none of them as data or
selector and leave their couplers idle; q3 then has no usable neighbor, so
the usable coupling graph is 1-4, 2-4, 4-8, 8-11, 8-12, 10-13, 11-13, 11-14,
12-14, 12-15, 14-16, 15-16.
