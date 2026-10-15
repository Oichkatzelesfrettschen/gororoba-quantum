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

## Elevated scientific suite grounded in QPU campaign findings

The module provides four scientific experiment families directly grounded in the 21 physical
QPU runs on `ibm_fez` and `ibm_kingston`:

### Run 1: Cayley-Dickson Sedenion and Pathion Non-Associative Witnesses
- **`lcu_zero_product_witness(a_pair, b_pair, sign)`** (5 qubits): Design B's fixed-operand LCU
  (`designs.lcu_witness`) for $x = (e_i + e_j)/\sqrt{2}$ and $y = (e_k + \text{sign}\, e_l)/\sqrt{2}$.
  `cd_core.cd_multiply` certifies the pair and metadata records $P(s=0) = \|xy\|^2/2$: 0 for the
  dark pair $(e_1 + e_{10})(e_4 - e_{15}) = 0$, 1 for its bright control $(e_4 + e_{15})$, and 1/2 for
  the negative regression fixture $(e_1 + e_{10})(e_2 - e_{13})$ (`AGENTS.md`, Algebra Circuit Design Rules).
- **`sedenion_associator_witness(i, j, k)`** (5 qubits): Hadamard test on $\mathbb{S}_{16}$ (4 data
  qubits + 1 control ancilla). Control qubit 4 prepares $|+\rangle$. Branch 0 applies $L_{(e_i e_j) e_k}$
  and branch 1 applies $L_{e_i} L_{e_j} L_{e_k}$. Post-measurement expectation $\langle Z_c \rangle =
  \text{Re}\langle \psi_L | \psi_R \rangle$ yields $+1$ for associating triples (e.g. $(1, 2, 3)$) and $-1$
  for anti-associating triples (e.g. $(1, 2, 4)$), certified by `cd_core.cd_sign`.
- **`pathion_singular_sector_witness(dim=32, i=1, j=16)`** (5 qubits): Evaluates the Walsh spectrum
  of $W = L_{e_i e_j}^\dagger L_{e_i} L_{e_j}$ on $\log_2(32) = 5$ qubits (`designs.design_c_associator_spectrum`),
  probing the 32-dimensional pathion singular sector and Moreno $G_2$ automorphism fibers along the
  nullity-12 locus (`gororoba_quantum/nullity_twelve_locus.py`).

### Run 2: Fano-Plane CSS and Active vs Coherent Stabilizers
- **`fano_plane_incidence_matrix()`**: Returns the $7 \times 7$ binary incidence matrix of the projective
  Fano plane $\text{PG}(2, 2)$, mapping the 7 imaginary octonionic units $\{e_1, \dots, e_7\}$ to the
  7 data qubits and lines of the Steane $[[7,1,3]]$ code (`docs/notes/levratti-2026-fano-css.md`).
- **`steane_z_syndrome_patch(error_qubit, mid_circuit_measure, dd_sequence)`** (10 qubits): Measures the
  three Steane $Z$ parity checks with $CX$ from data qubits onto ancillas 7..9. Unnested `if_test` blocks
  apply $X$ corrections. An optional `dd_sequence` (`"Hahn"` or `"XY4"`) injects dynamical decoupling on
  the data qubits during the syndrome readout delay to suppress physical dephasing drift.
- **`steane_coherent_syndrome_patch(error_qubit)`** (10 qubits): Extracts syndrome into ancillas 7..9,
  then applies coherent multi-controlled corrections `mcx([7, 8, 9], val - 1, ctrl_state=val)` on the data
  qubits without mid-circuit readout or reset. This eliminates the ~11% mid-circuit assignment error
  and controller latency, embodying the 5.8 to 10.9 percentage point coherent advantage demonstrated in
  the physical QPU campaign findings (`results/live/CAMPAIGN_FINDINGS.md` §2).

### Run 3: Vacuum Endpoint Probes, Dynamical Decoupling, and Model Discrimination
- **`bell_delay_probe(delay_dt, dd_sequence)`** (2 qubits): Prepares a Bell pair, applies an idle delay,
  and inverts the state. `dd_sequence` supports `None` (plain idle), `"Hahn"` ($X$ echo at midpoint), or
  `"XY4"` ($X \to Y \to X \to Y$ staggered pulses). In the physical Kingston coherence window run, plain
  idle experienced $-1.130$ rad of dephasing rotation over $4.4\,\mu\text{s}$, while echo pulses reduced
  this drift to $+0.17$ rad (`results/live/N21_ORBIT_RCA.md`); the probe directly tests this countermeasure.
- **`tile_parity_covariance` with `tile_coords`**: Computes pairwise covariance $C_{ij} = \mathbb{E}[P_i P_j] -
  \mathbb{E}[P_i]\mathbb{E}[P_j]$ and pairs it with physical Euclidean/Manhattan chip distances
  $\|\mathbf{r}_i - \mathbf{r}_j\|$ to isolate local two-level system (TLS) defects from chip-wide correlations.
- **`hoeffding_model_discrimination(counts_p, counts_q, alpha=0.01)`**: Computes empirical Total Variation
  distance $D_{\text{TV}}(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)| \in [0, 1]$ and Jensen-Shannon divergence
  $D_{\text{JS}}(P \parallel Q)$. Because $D_{\text{TV}}$ is a bounded statistic in $[0, 1]$, Hoeffding's
  inequality (`docs/notes/hoeffding-1963.md`) establishes a simultaneous two-sided confidence radius
  $r = \sqrt{\frac{\ln(2/\alpha)}{2N}}$ where $N = \min(N_p, N_q)$. For $N=8192$ and $\alpha=0.01$,
  $r \approx 0.0180$, rigorously bounding whether empirical candidate models are statistically separable.

### Run 4: Boolean Bent Hidden Shift
- **`bent_hidden_shift_circuit(n=6, shift=None)`** ($n$ qubits, $n \in \{4, 6, 8\}$): Constructs quadratic
  bent function $f(x) = \bigoplus_{i=0}^{n/2-1} x_{2i} x_{2i+1}$ (certified full rank $n$ via
  `boolean_anf.quadratic_polar_rank`) and shifted $g(x) = f(x \oplus s)$. Implements Rötteler's (2010) algorithm:
  $H^{\otimes n} \to O_g \to H^{\otimes n} \to O_f \to H^{\otimes n} \to \text{Measure}$.
  In ideal execution, measures hidden shift $s$ with probability 1.0, compiling natively to $\{CZ, RZ, H\}$
  to benchmark coherent multi-qubit phase stability across heavy-hex tiles.

## Limits and empirical boundaries

- The $RZ \to CZ \to SX$ pattern detector (`flag_rz_cz_sx`) identifies consecutive executions on couplers
  exceeding the CZ error threshold (4e-3: 45, 35, and 52 couplers across Fez, Kingston, and Marrakesh).
- The 156-qubit carpet finding (`results/live/CAMPAIGN_FINDINGS.md` §7) demonstrated that 87 active qubits
  without guard bands suffered 78.7% shot corruption (mean 1.36 violating replicas per shot). This
  physically validates the requirement that all multiplexed tiles must maintain graph distance
  $\text{dist}_G \ge 2$ guard bands on Heron r2.

