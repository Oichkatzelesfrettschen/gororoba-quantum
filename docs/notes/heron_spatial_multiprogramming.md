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

### Elevated scientific suite motivated by QPU campaign observations

The module provides four scientific experiment families motivated by observations across the
retained QPU campaign acquisitions (`results/live/CAMPAIGN_FINDINGS.md`, `results/live/QPU_PROGRAM_CASES.md`,
and `results/live/TERMINAL_CHANNEL_HYPOTHESIS.md`):

### Run 1: Cayley-Dickson Sedenion and Pathion Non-Associative Witnesses
- **`lcu_zero_product_witness(a_pair, b_pair, sign)`** (5 qubits): Design B's fixed-operand LCU
  (`designs.lcu_witness`) for $x = (e_i + e_j)/\sqrt{2}$ and $y = (e_k + \text{sign}\, e_l)/\sqrt{2}$.
  `cd_core.cd_multiply` certifies the pair and metadata records $P(s=0) = \|xy\|^2/2$: 0 for the
  dark pair $(e_1 + e_{10})(e_4 - e_{15}) = 0$, 1 for its bright control $(e_4 + e_{15})$, and 1/2 for
  the negative regression fixture $(e_1 + e_{10})(e_2 - e_{13})$ (`docs/notes/algebra_circuit_rules.md`, Algebra Circuit Design Rules).
- **`sedenion_associator_witness(i, j, k)`** (5 qubits): Hadamard test on $\mathbb{S}_{16}$ (4 data
  qubits + 1 control ancilla). Control qubit 4 prepares $|+\rangle$. Branch 0 applies $L_{(e_i e_j) e_k}$
  and branch 1 applies $L_{e_i} L_{e_j} L_{e_k}$. Post-measurement expectation $\langle Z_c \rangle =
  \text{Re}\langle \psi_L | \psi_R \rangle$ yields $+1$ for associating triples (e.g. $(1, 2, 3)$) and $-1$
  for anti-associating triples (e.g. $(1, 2, 4)$), certified by `cd_core.triple_sign`.
- **`pathion_associator_spectrum_witness(dim=32, i=1, j=16)`** (5 qubits): Evaluates Design C's Walsh spectrum
  of $W = L_{e_i e_j}^\dagger L_{e_i} L_{e_j}$ on $\log_2(32) = 5$ qubits (`designs.design_c_associator_spectrum`)
  for the five-qubit pathion exemplar $(1, 16)$ from `designs.SPECTRUM_EXEMPLARS`.

### Run 2: Fano-Plane CSS and Active vs Coherent Stabilizers
- **`fano_plane_incidence_matrix()`**: Returns the $7 \times 7$ binary incidence matrix of the projective
  Fano plane $\text{PG}(2, 2)$ (associative triples of imaginary octonions $\{e_1, \dots, e_7\}$); the three
  weight-4 Steane $Z$ checks in `steane_z_syndrome_patch` are the complements of three of these lines
  (`docs/notes/papers/levratti-2026-fano-css.md` Theorem 3.1).
- **`steane_z_syndrome_patch(error_qubit, mid_circuit_measure, dd_sequence, idle_delay_dt)`** (10 qubits): Measures the
  three Steane $Z$ parity checks with $CX$ from data qubits onto ancillas 7..9. Unnested `if_test` blocks
  apply $X$ corrections. `idle_delay_dt > 0` inserts an idle on the data qubits after the parity checks, filled by
  `dd_window` with `"CPMG2"` (pulse product $I$) or `"XY4"` (product $-I$); Hahn is refused because one $X$ on all
  seven data qubits is a transversal logical $X$. The patch starts in $|0\rangle^{\otimes 7}$ and reads only $Z$, so it
  tests bit-flip syndrome extraction and frame restoration by the DD block; a phase error on these $Z$ eigenstates
  changes no bit, so the patch is not a dephasing or logical-coherence experiment. The contracts check the pulse
  order and dt intervals after tile routing, and refocusing of a static detuning on an $X$-basis readout.
- **`steane_coherent_syndrome_patch(error_qubit)`** (10 qubits): Extracts syndrome into ancillas 7..9,
  then applies coherent multi-controlled corrections `mcx([7, 8, 9], val - 1, ctrl_state=val)` on the data
  qubits to correct single $X$ errors on $|0\rangle^7$ without mid-circuit readout or reset: an ideal
  measurement-free correction map. The coherent-versus-feed-forward QPE ladder of `results/live/CAMPAIGN_FINDINGS.md`
  Section 2 is a different experiment whose mechanism that note leaves unresolved.

### Run 3: Vacuum Endpoint Probes, Dynamical Decoupling, and Model Discrimination
- **`bell_delay_probe(delay_dt, dd_sequence, quadrature)`** (2 qubits): Prepares a Bell pair, fills an idle with
  `dd_window` (`None`, `"Hahn"`, `"CPMG2"` or `"XY4"`), and inverts the state. With the idle acting as
  $(|00\rangle + V e^{i\theta}|11\rangle)/\sqrt{2}$, quadrature `"x"` returns $P_{00} = (1 + V\cos\theta)/2$, which alone
  cannot separate a contrast loss $V$ from a rotation $\theta$; quadrature `"y"` adds $S^\dagger$ before the inverse and
  returns $(1 + V\sin\theta)/2$, and the two together identify both.
  In physical QPU characterizations, unmitigated idle exposure exhibited both coherent phase rotation and dephasing decay
  (e.g. a directly measured branch-signed coherence rotation of $-1.130$ rad over $4.4\,\mu\text{s}$ on `ibm_kingston`,
  accompanied by $|C|$ moving from $0.413$ to $0.375$, recorded in `results/live/QPU_PROGRAM_CASES.md`). A separate, older
  calibration on `ibm_fez` yielded an independent fitted phase parameter of $+0.17$ rad under different experimental
  conditions (`results/live/N21_ORBIT_RCA.md`); the two quantities reflect distinct observables and execution contexts
  rather than a single differential DD effect. `bell_delay_probe` is a proposed echo testbed for idle rotation and
  contrast loss; it encodes neither number and no hardware result here shows a decoupling benefit.
- **`tile_parity_covariance` with `tile_coords`**: Computes pairwise covariance $C_{ij} = \mathbb{E}[P_i P_j] -
  \mathbb{E}[P_i]\mathbb{E}[P_j]$ and pairs it with physical Euclidean chip distances
  $\|\mathbf{r}_i - \mathbf{r}_j\|$ when coordinate pairs are supplied by the caller.
- **`hoeffding_model_discrimination(counts_p, counts_q, alpha=0.01, *, alphabet_size)`**: Computes empirical Total
  Variation distance $D_{\text{TV}}(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)| \in [0, 1]$ and Jensen-Shannon divergence
  $D_{\text{JS}}(P \parallel Q)$. For single binary projections or parity observables, Hoeffding's inequality
  (`docs/notes/papers/hoeffding-1963.md`) provides a two-sided confidence radius $r_{\text{obs}} = \sqrt{\frac{\ln(2/\alpha)}{2N_{\text{eff}}}}$.
  To bound the plug-in total-variation distance across all $K$ outcome bins simultaneously without falsely reporting
  distinguishable models due to multinomial sampling variation, the module computes the Bretagnolle-Huber-Carol
  finite-sample bound (van der Vaart & Wellner 1996, Proposition A.6.6). `alphabet_size` is required and must give
  the size of the complete outcome alphabet, including outcomes absent from either count map, and for bit-string
  outcomes of width $w$ it cannot exceed $2^w$:
  $\epsilon_m = \sqrt{\frac{2(K \ln 2 + \ln(4/\alpha))}{N_m}}$, yielding simultaneous confidence radius
  $r_{\text{TV}} = \frac{1}{2}(\epsilon_p + \epsilon_q)$.

### Run 4: Boolean Bent Hidden Shift
- **`bent_hidden_shift_circuit(n=6, shift=None)`** ($n$ qubits, $n \in \{4, 6, 8\}$): Constructs quadratic
  bent function $f(x) = \bigoplus_{i=0}^{n/2-1} x_{2i} x_{2i+1}$ (certified full rank $n$ via
  `boolean_anf.quadratic_polar_rank`) and shifted $g(x) = f(x \oplus s)$. Implements Roetteler's (2010) algorithm:
  $H^{\otimes n} \to O_g \to H^{\otimes n} \to O_f \to H^{\otimes n} \to \text{Measure}$.
  In ideal execution, measures hidden shift $s$ with probability 1.0. The ideal circuit is constructed from
  $\{H, CZ, Z\}$, compiling to native Heron r2 ISA instructions $\{cz, rz, sx, x\}$ after transpilation.

## Primary research literature grounding

Every circuit builder, routing policy, and validation threshold in this suite is grounded in
repository source notes, registered preprints, and verified platform artifacts:

1. **Spatial Multiprogramming & Crosstalk Suppression:**
   - **Sarovar et al. (2020)**, *Detecting crosstalk errors in quantum information processors*,
     [arXiv:1908.09855](https://arxiv.org/abs/1908.09855) (`docs/notes/papers/1908.09855.md`, `docs/pdf/1908.09855v3.pdf`):
     Establishes protocols for detecting crosstalk under concurrent drives; the $\text{dist}_G \ge 2$ guard band
     is enforced as a placement policy to separate concurrent execution subgraphs.
   - **Niu & Todri-Sanial (2021, 2023)**, *Enabling Multi-programming Mechanism for Quantum Computing in the NISQ Era*,
     [arXiv:2102.05321](https://arxiv.org/abs/2102.05321) (Quantum 7, 925, 2023; `docs/notes/2102.05321.md`, `docs/pdf/2102.05321v3.pdf`)
     and *How Parallel Circuit Execution Can Be Useful for NISQ Computing?*, [arXiv:2112.00387](https://arxiv.org/abs/2112.00387)
     (`docs/notes/papers/2112.00387.md`, `docs/local_source_cache/2112.00387v1.pdf`): Provides the algorithmic basis for
     multi-programming partitioning, heavy-hex subgraph isolation, and independent classical register multiplexing.
   - **Gambetta et al. (2012)**, *Characterization of addressability by simultaneous randomized benchmarking*,
     [arXiv:1204.6308](https://arxiv.org/abs/1204.6308) (`docs/notes/papers/1204.6308.md`, `docs/local_source_cache/1204.6308v2.pdf`):
     Foundational framework for measuring addressability under simultaneous microwave and coupler drives.

2. **Non-Associative Cayley-Dickson Algebra & Zero-Divisor Loci:**
   - **Freedman, Shokrian-Zini, & Wang (2019)**, *Quantum Computing with Octonions*,
     [arXiv:1811.08580](https://arxiv.org/abs/1811.08580) (`docs/notes/papers/1811.08580.md`, `docs/local_source_cache/1811.08580v5.pdf`):
     Formulates Hilbert space representations and non-associative gate structures on multi-qubit systems.
   - **Biss, Christensen, Dugger, & Isaksen (2009)**, *Eigentheory of Cayley-Dickson algebras*,
     [arXiv:0905.2987](https://arxiv.org/abs/0905.2987) (`docs/notes/0905.2987.md`, `docs/local_source_cache/0905.2987v1.pdf`):
     Characterizes eigenvalues, zero-divisor structures, and annihilator dimensions in Cayley-Dickson algebras
     codified in `gororoba_quantum/cd_core.py`.

3. **Fano-Plane Projective Geometry & Stabilizer Codes:**
   - **Levratti (2026)**, *Fano Duality, Projective Orthogonality, and the CSS Bridge* (`docs/notes/papers/levratti-2026-fano-css.md`,
     `docs/pdf/levratti-2026-fano-css.pdf`) and *Active Stabilizers in Reed-Muller CSS Codes from Cayley-Dickson Zero-Divisors*
     (`docs/notes/papers/levratti-2026-active-stabilizers.md`, `docs/pdf/levratti-2026-active-stabilizers.pdf`): Author-hosted
     manuscripts mapping the 7 points and 7 lines of the projective Fano plane $\text{PG}(2, 2)$ to octonionic triads
     and the Fano line incidence matrix whose line complements yield the Steane $[[7, 1, 3]]$ $Z$ stabilizers (`fano_plane_incidence_matrix`, `steane_z_syndrome_patch`).
   - **Corcoles et al. (2021)**, *Exploiting dynamic quantum circuits in a quantum algorithm with superconducting qubits*,
     [arXiv:2102.01682](https://arxiv.org/abs/2102.01682) (Phys. Rev. Lett. 127, 100501; `docs/notes/2102.01682.md`,
     `docs/pdf/2102.01682.pdf`): Demonstrates physical dynamic circuits and feed-forward on superconducting transmons,
     balancing mid-circuit measurement against coherent routing.
   - **Rudinger et al. (2022)**, *Characterizing mid-circuit measurements on a superconducting qubit using gate set tomography*,
     [arXiv:2103.03008](https://arxiv.org/abs/2103.03008) (2021; Phys. Rev. Applied 17, 014014, 2022; `docs/notes/papers/2103.03008.md`,
     `docs/local_source_cache/2103.03008v1.pdf`): Quantum-instrument tomography characterizing mid-circuit measurement operations.

4. **Boolean Bent Hidden Shift Algorithms:**
   - **Roetteler (2008, 2009)**, *Quantum algorithms for highly non-linear Boolean functions*, [arXiv:0811.3208](https://arxiv.org/abs/0811.3208)
     (Proc. SODA 2010, pp. 448-457; `docs/notes/papers/0811.3208.md`, `docs/local_source_cache/0811.3208v2.pdf`) and *Quantum algorithms
     to solve the hidden shift problem for quadratics and for functions of large Gowers norm*, [arXiv:0911.4724](https://arxiv.org/abs/0911.4724)
     (`docs/notes/papers/0911.4724.md`, `docs/local_source_cache/0911.4724v1.pdf`): Derives the exact quantum algorithm using dual bent
     oracles $O_g$ and $O_{\tilde{f}}$ separated by Hadamard transforms to solve the hidden shift problem with $O(1)$ queries
     and deterministic $P=1.0$ recovery.
   - **Gavinsky, Roetteler, & Roland (2011)**, *Quantum algorithm for the Boolean hidden shift problem*,
     [arXiv:1103.3017](https://arxiv.org/abs/1103.3017) (`docs/notes/papers/1103.3017.md`, `docs/local_source_cache/1103.3017v1.pdf`):
     Establishes the $O(n / \sqrt{\gamma_f})$ quantum query algorithm based on minimum Boolean influence $\gamma_f$,
     showing $O(n)$ query complexity for bent functions and $O(1)$ with dual oracle access.

5. **Statistical Discrimination & Concentration Bounds:**
   - **Hoeffding (1963)**, *Probability inequalities for sums of bounded random variables*, J. Amer. Statist. Assoc. 58, 13-30
     [DOI:10.1080/01621459.1963.10500830](https://doi.org/10.1080/01621459.1963.10500830) (`docs/notes/papers/hoeffding-1963.md`):
     Establishes the non-parametric exponential concentration bound for bounded random variables in $[0, 1]$.
   - **Bretagnolle-Huber-Carol Bound**: The finite-sample multinomial total variation inequality
     $\mathbb{P}(\|\hat{P} - P\|_1 \ge \epsilon) \le 2^K \exp(-n \epsilon^2 / 2)$ (van der Vaart & Wellner 1996,
     *Weak Convergence and Empirical Processes*, Springer, Proposition A.6.6, p. 438). The implemented confidence radius
     $\epsilon_m = \sqrt{\frac{2(K \ln 2 + \ln(4/\alpha))}{N_m}}$ and $r_{\text{TV}} = \frac{1}{2}(\epsilon_p + \epsilon_q)$
     inverts this bound at tail $\alpha/4$ per sample, ensuring multi-outcome sampling variation does not falsely report
     distinguishable models.

6. **IBM Heron r2 Platform & Qiskit Architecture Grounding:**
   - **Fractional Gates & Continuous ISA** (`docs/notes/ibm_quantum/fractional-gates.md`): `use_fractional_gates=True`
     adds `rzz` ($0 < \theta \le \pi/2$) and `rx` to the Target as fractional instructions beside the basis
     `cz, id, rz, sx, x, xslow`; no builder here uses them.
   - **Dynamic Circuits & Mid-Circuit Execution** (`docs/notes/ibm_quantum/execute-dynamic-circuits.md`): Single-level
     `if_test` conditionals, operands $\le 32$ bits, and mid-circuit readout/reset constraints.
   - **Timing, Repetition Rate, and Stretch** (`docs/notes/ibm_quantum/repetition-rate-execution.md`,
     `docs/notes/ibm_quantum/stretch.md`, `docs/notes/ibm_quantum/qiskit-runtime-circuit-timing.md`): Repetition rate
     range $[0, 2\,\text{ms}]$ (default $250\,\mu\text{s}$), and QASM3 stretch timing.
   - **Processor Topologies & Calibration Snapshots** (`docs/notes/ibm_quantum/qpu-information.md`,
     `docs/notes/ibm_quantum/processor-types.md`, `docs/notes/ibm_heron_platform.md`,
     `docs/evidence/heron_platform/targets.json`): 156-qubit heavy-hex lattice, $dt = 4\,\text{ns}$
     timing granularity, and machine-readable Target definitions for `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh`.
   - **Transpiler Stages & Pass Managers** (`docs/notes/ibm_quantum/transpiler-stages.md`,
     `docs/notes/ibm_quantum/transpile-with-pass-managers.md`): Staged pass manager execution and layout synthesis.

## Limits and empirical boundaries

- The $RZ \to CZ \to SX$ pattern detector (`flag_rz_cz_sx`) identifies consecutive executions on couplers
  exceeding the CZ error threshold (4e-3: 45, 35, and 52 couplers across Fez, Kingston, and Marrakesh).
- The 156-qubit carpet characterization (`results/live/CAMPAIGN_FINDINGS.md` Section 7) observed that across 29 disconnected
  3-qubit components totaling 87 gate-active transmons, 403 of 512 shots (78.7%, mean 1.357422 violating replicas per shot)
  exhibited support violations under simultaneous operation. The campaign note explicitly cautions that these counts do not
  isolate causal crosstalk mechanisms, so the observations are recorded as baseline operational support violations without
  causal attribution.
