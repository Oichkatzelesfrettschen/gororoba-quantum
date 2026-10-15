# Heron r2 tile packing, wide-circuit composition and Target duration arithmetic

`gororoba_quantum/heron_multiprogramming.py` packs guard-banded tiles on the
coupling map of the retained Target snapshot
(`docs/evidence/heron_platform/targets.json`), composes one circuit per tile
into one wide circuit, and computes duration and shot-rate arithmetic from
Target values. `scripts/heron_spatial_multiprogramming.py` writes the audit
`docs/evidence/heron_platform/spatial_multiprogramming_audit.json` (gates
core-257 and core-258), and `gororoba_quantum/test_heron_multiprogramming.py`
holds the contracts (gate core-256). Nothing here schedules a circuit on a
backend, submits a job, or measures a throughput; every number below is
arithmetic on the snapshot or an assumption stated beside it.

## Why packing matters

The estimate guide (`docs/notes/ibm_quantum/estimate-job-run-time.md`)
bills a job as about 2 s per sub-job plus `(rep_delay + circuit length)`
per execution, independent of how many qubits a circuit touches. A 5-qubit
circuit therefore pays for the whole 156-qubit chip for its duration, and
independent circuits placed side by side in one wide circuit share each
shot. The planner constants 2.3 s and 4.6 s in
`scripts/qpu_runtime_levers.py` are declared client-job scenarios, not the
billed per-sub-job figure.

## Tiles and guard distance

`find_disjoint_tiles(k, min_buffer_distance)` grows a breadth-first tree of
k qubits from every start qubit through its lowest-error couplers, ranks
the trees by estimated success probability (readout, SX and CZ error
products), and accepts a tree when none of its qubits lies within
`min_buffer_distance - 1` hops of an accepted tile. Distance 2 leaves at
least one idle qubit between tiles, distance 3 at least two. The graph
condition is what the code enforces; the snapshot carries no ZZ or
crosstalk magnitude, so the guard band is a placement rule with no stated
suppression factor. `processor-types.md` describes Heron r2 as 156 qubits in
a heavy-hex lattice with TLS mitigation.

| Plan (tile size, requested) | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---:|---:|---:|
| k5, 16 at distance 2 | 16 (80 qubits) | 16 (80) | 16 (80) |
| k10, 8 at distance 2 | 7 (70) | 8 (80) | 7 (70) |
| k2, 20 at distance 2 | 20 (40) | 20 (40) | 20 (40) |
| k7, 12 at distance 2 | 12 (84) | 10 (70) | 12 (84) |
| k5, 16 at distance 3 | 12 | 13 | 9 |

Each tile records its induced couplers, its guard qubits and a serial
duration bound: one SX layer, every internal CZ in series, then the
slowest readout, all from Target durations (for example 1976 ns for the
first ibm_fez k5 tile, whose coupler 146-147 runs 88 ns).

## Composition and routing

`build_multiplexed_pub(circuits, tiles)` places circuit qubit i on
`tile.qubits[i]`, renames each classical register `tile_<k>_<name>`, and
rejects tiles that overlap or sit closer than the guard distance and any
two-qubit operation, inside control-flow bodies included, that lands off
its tile's induced couplers. `route_to_tile(circuit, tile)` compiles a
circuit to cz, rz, sx and x with a coupling map confined to the tile's
couplers, so its output always places. A parameter whose name another
tile already uses for a different `Parameter` object becomes
`tile_<k>_<name>`; one object shared across tiles stays one parameter.
`pack_parameter_sweep_pub` packs a finite, non-empty `(N_sweeps, N_params)`
array with the circuit as one Sampler PUB.

`append_basis_rotations` inserts H (X basis) or Sdg then H (Y basis) before
a measurement only when nothing later acts on that qubit, so a mid-circuit
measurement stays in the Z basis. Raw bit strings from one Sampler PUB
carry every tile's registers per shot. `tile_parity_covariance` returns
`E[P_i P_j] - E[P_i] E[P_j]` for tile parities `P = (-1)^(ones)`; it carries
no chip coordinate, so comparing it with coupling distance needs the tiles'
distances alongside it.

## Target facts from the audit

| Median over the snapshot | ibm_fez | ibm_kingston | ibm_marrakesh |
|---|---:|---:|---:|
| CZ error | 2.683e-3 | 2.149e-3 | 2.867e-3 |
| two-CZ error, 1 - (1 - e_CZ)^2 | 5.359e-3 | 4.294e-3 | 5.727e-3 |
| RZZ error | 2.920e-3 | 2.051e-3 | 4.253e-3 |
| couplers with RZZ error below two-CZ error | 156 of 176 | 158 of 176 | 119 of 176 |
| SX error | 3.013e-4 | 2.603e-4 | 3.964e-4 |
| `measure` / `measure_2` (ns) | 1660 / 1340 | 2180 / 1380 | 2684 / 1884 |
| `reset` / `reset_2` (ns) | 1684 / 1364 | 2212 / 1412 | 2720 / 1920 |
| SX duration (ns, every qubit) | 24 | 32 | 36 |
| couplers with RZZ duration equal to CZ | 173 | 176 | 169 |
| RZZ synthesis over native RZZ, median (min) | 3.41 (2.00) | 3.88 (3.19) | 4.12 (2.00) |

`use_fractional_gates=True` adds `rzz` (0 < theta <= pi/2) and `rx` to the
Target beside the basis `cz, id, rz, sx, x, xslow`
(`fractional-gates.md`); they are fractional instructions, not basis
gates. The preset transpiler synthesizes RZZ(theta) from 2 CZ and 4 SX
with virtual RZ, and `rzz_duration_summary` takes the ASAP critical path of
that synthesis with each coupler's own CZ duration and each qubit's SX
duration. One RZZ replaces two CZ, but its error is not uniformly lower:
the median RZZ error exceeds the median CZ error on ibm_fez and
ibm_marrakesh, and 57 ibm_marrakesh couplers report RZZ error at or above
their two-CZ error (`docs/notes/ibm_heron_platform.md`). A fractional decomposition is an
intervention with its own controls.

## Repetition delay

All three backends report `rep_delay_range` [0, 2 ms] and a 250 us
default. One shot cycle is the circuit duration plus the repetition delay,
so at an assumed 5 us circuit a 50 us delay raises the shot rate 4.64
times, and at an assumed 50 us circuit, the low end of the guide's typical
50 to 100 us, it raises it 3.0 times. Lowering the delay raises the
state-preparation error (`repetition-rate-execution.md`), and
`scripts/qpu_runtime_levers.py` prices 100 us and 50 us only with that
qualification. A shot-rate ratio is a rate at an unqualified operating
point; neither it nor a tile count multiplies into a yield until a
state-preparation control at that delay exists.

## Circuits that fit one tile

- **`lcu_zero_product_witness(a_pair, b_pair, sign)`**, 5 qubits, is Design
  B's fixed-operand LCU (`designs.lcu_witness`) on `x = (e_i + e_j)/sqrt2`
  and `y = (e_k + sign e_l)/sqrt2`. `cd_core.cd_multiply` certifies the pair
  and the circuit metadata carries `P(s = 0) = ||x y||^2 / 2`: 0 for the
  default dark pair `(e1 + e10)(e4 - e15) = 0`, 1 for its bright control
  `(e4 + e15)`, and 1/2 for the negative fixture `(e1 + e10)(e2 - e13)`
  (AGENTS.md, algebra circuit design rules).
- **`steane_z_syndrome_patch(error_qubit, mid_circuit_measure)`**, 10
  qubits, measures the three Steane Z checks with CX from the data qubits
  onto ancillas 7 to 9 (supports {1,3,5,7}, {2,3,6,7} and {4,5,6,7} in
  1-based positions), so an X error on data qubit d reads syndrome d + 1.
  Seven unnested `if_test` blocks on the 3-bit syndrome register apply the
  X correction, within the execute-dynamic-circuits limits of one `if`
  level and operands of at most 32 bits, and a final readout of the data
  register shows the correction. It starts in `|0>^7`, measures no X check
  and prepares no logical codeword. `mid_circuit_measure=True` reads the
  ancillas with `MidCircuitMeasure` (`measure_2`), a different physical
  measurement that Aer does not simulate and that needs its own control.
- **`bell_delay_probe(delay_dt)`**, 2 qubits, prepares a Bell pair, waits a
  fixed number of dt on both qubits and undoes the preparation; it uses no
  stretch and computes no divergence.
- **`designs.design_c_associator_spectrum(128, i, j)`** occupies 7 qubits,
  one k7 tile.

## Limits and open work

- The rz, cz, sx flag (`flag_rz_cz_sx`) is a pattern match on one qubit's
  operation order with an explicit CZ error threshold (4e-3: 45, 35 and 52
  couplers). No source in `docs/` characterizes an error for that pattern;
  rz commutes with cz, and a delay ends the run.
- A defect census, a pathion witness, KL or JS divergence bounds between
  vacuum models, a Boolean hidden-shift instance, stretch-scheduled delay
  sweeps, and replays of the Rocq certificates are separate cases that
  this module does not run. Each needs its own circuit, analysis and
  written case before hardware.
- Hoeffding's bound `n >= ln(2/delta) / (2 epsilon^2)` covers the mean of
  observations bounded in [0, 1] (`docs/notes/hoeffding-1963.md`); at
  epsilon 0.02 and delta 0.01 it gives 6623 shots. It does not bound an
  empirical KL or JS divergence, whose sample size needs its own
  derivation.
