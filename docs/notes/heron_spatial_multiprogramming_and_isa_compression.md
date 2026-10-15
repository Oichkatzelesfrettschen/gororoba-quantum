# Heron r2 Economics, Spatial Multiprogramming, and Temporal ISA Compression

## Executive Summary

On 156-qubit IBM Heron r2 processors (`ibm_fez`, `ibm_marrakesh`, `ibm_kingston`),
billing is strictly denominated in wall-clock QPU execution time rather than per active
qubit. Consequently, executing an isolated 4-qubit to 14-qubit experiment occupies less
than 10% of the heavy-hex lattice while charging for 100% of the chip's duration, wasting
more than 90% of billed quantum capacity.

To maximize scientific yield per QPU-second, execution must exploit two orthogonal axes:
1. **Spatial Multiprogramming**: Tiling 8 to 16 disjoint sub-lattices simultaneously
   into a single wide `QuantumCircuit` per Primitive Unified Bloc (PUB), separated by
   at least 1 idle buffer qubit (crosstalk guard band) between active islands.
2. **Temporal ISA Compression**: Utilizing Heron's native continuous fractional
   $R_{ZZ}(\theta)$ and $R_X(\theta)$ instructions (`use_fractional_gates=True`) to cut
   two-qubit gate depth and coherent duration by $3.88\times$, combined with repetition
   delay (`rep_delay`) tuning down from the $250\,\mu\text{s}$ default toward the
   $10\text{--}50\,\mu\text{s}$ floor via mid-circuit / active reset.

Together, these mechanisms compound to deliver an aggregate **$50\times\text{--}75\times$
multiplier in scientific data throughput per billed QPU-second** on production Heron hardware.

---

## 1. The Heron r2 Economics & ISA Execution Engine

### 1.1 QPU Billing and Execution Mechanics

A primitive job submitted to IBM Quantum Qiskit Runtime incurs charged execution time
governed by:

$$T_{\text{exec}} = \sum_{p=1}^P S_p \times \left( T_{\text{circ}, p} + T_{\text{reset}} + T_{\text{rep\_delay}} \right) + T_{\text{overhead}}$$

where:
- $P$ is the number of PUBs in the job,
- $S_p$ is the shot count of PUB $p$,
- $T_{\text{circ}, p}$ is the scheduled circuit duration (typically $2\text{--}10\,\mu\text{s}$),
- $T_{\text{reset}}$ is the qubit initialization duration ($1.34\text{--}2.68\,\mu\text{s}$),
- $T_{\text{rep\_delay}}$ is the inter-shot relaxation delay (default $250\,\mu\text{s}$),
- $T_{\text{overhead}}$ is the client/sub-job dispatch latency ($2.3\,\text{s}$ nominal, $4.6\,\text{s}$ under stress).

Under default execution:
- A 5-qubit sedenion witness with $T_{\text{circ}} \approx 4\,\mu\text{s}$ spends
  $\frac{250\,\mu\text{s}}{255\,\mu\text{s}} = 98.0\%$ of its cycle time in passive relaxation delay.
- The 5 active qubits occupy $\frac{5}{156} = 3.2\%$ of the lattice, leaving 151 qubits (96.8%) idle.
- Effective QPU utilization is $3.2\% \times 2.0\% \approx 0.064\%$. Running single circuits is
  economically and scientifically prohibitive for deep statistical campaigns.

### 1.2 Spatial Tiling & Guard-Band Mechanics on Heavy-Hex

Heron r2 processors feature 156 physical qubits arranged in a heavy-hexagonal lattice with
176 undirected two-qubit couplers. The node degree distribution consists of:
- 8 degree-1 boundary nodes,
- 100 degree-2 hexagon edge nodes,
- 48 degree-3 hexagon vertex nodes.

Unlike IBM Eagle processors (which use fixed-frequency transmons with always-on parasitic $ZZ$
crosstalk), Heron r2 incorporates **tunable couplers**. When a coupler's intervening spectator
transmon is maintained in its ground state $|0\rangle$, the coupler can be dynamically detuned,
suppressing parasitic $ZZ$ crosstalk below $1\,\text{kHz}$.

To exploit this physical property:
- Active sub-lattices (tiles) must maintain a minimum graph distance of $\text{dist}_G \ge 2$.
- Every active tile $T_i$ is surrounded by a 1-hop buffer guard band $N(T_i) = \{w \notin T_i \mid \exists u \in T_i, (u,w) \in E\}$.
- No buffer qubit is shared or driven by another tile: $T_j \cap (T_i \cup N(T_i)) = \emptyset$ for all $j \ne i$.
- Buffer transmons remain unexcited throughout the circuit duration, ensuring complete dynamical
  decoupling between simultaneous experimental islands.

### 1.3 Fractional Gate ISA: Continuous $R_{ZZ}(\theta)$ vs Decomposed Synthesis

Initializing the backend Target with `use_fractional_gates=True` adds continuous $R_{ZZ}(\theta)$
(valid for $0 < \theta \le \pi/2$) and $R_X(\theta)$ instructions into the native basis
$\{CZ, ID, RZ, SX, X, XSlow, RZZ, RX\}$.

Continuous two-qubit rotations arise ubiquitously in Cayley-Dickson singular-sector parameter sweeps,
algebraic twists, and Hamiltonian simulations:

$$R_{ZZ}(\theta) = \exp\left(-i \frac{\theta}{2} Z \otimes Z\right)$$

#### Decomposition Comparison
1. **Discrete Gate Decomposition** (Standard Heron basis $\{CZ, SX, RZ\}$):
   - Synthesis requires 2 native $CZ$ gates, 4 native $SX$ pulses, and virtual $RZ$ frames:
     $$\text{Duration} = 2 \times T_{CZ} + 4 \times T_{SX} = 2 \times 68\,\text{ns} + 4 \times 32\,\text{ns} = 264.0\,\text{ns}$$
   - Compounded two-qubit error: $e_{2Q} \approx 1 - (1 - e_{CZ})^2 \approx 2 \times 2.68 \times 10^{-3} \approx 5.36 \times 10^{-3}$.
2. **Native Fractional Execution** (`use_fractional_gates=True`):
   - Executed as 1 native pulse: $\text{Duration} = 68.0\,\text{ns}$.
   - Native $R_{ZZ}$ error: median $2.05\text{--}2.92 \times 10^{-3}$ from `targets.json`.
   - **Coherent duration reduction**: $\frac{264.0}{68.0} = 3.882\times$ faster.
   - **Two-qubit gate depth reduction**: $2 \to 1$ ($50\%$ reduction).
   - **Two-qubit error reduction**: $\approx 46\%\text{--}55\%$ lower entangling gate infidelity.

### 1.4 Repetition Rate Tuning and QASM3 Stretch

1. **Repetition Delay Tuning**:
   - Heron r2 supports dynamic repetition rate execution within `backend.rep_delay_range = [0.0, 0.002]\,\text{s}`.
   - When active reset (or mid-circuit `measure_2` followed by fast conditional flip) initializes
     qubits into $|0\rangle$, thermal relaxation during `rep_delay` is largely superfluous.
   - Dropping `rep_delay` from $250\,\mu\text{s}$ to $50\,\mu\text{s}$ increases the single-PUB shot rate from
     $3,921.6\,\text{Hz}$ to $18,181.8\,\text{Hz}$ ($4.636\times$ speedup).
   - Dropping to $20\,\mu\text{s}$ yields $40,000.0\,\text{Hz}$ ($10.20\times$ speedup).
2. **Deferred Timing via QASM3 `stretch` Variables**:
   - In interferometric delay sweeps (Ramsey, echo, vacuum tomography), discrete delay specifications
     in software suffer from rounding to integer clock cycles (4 ns dt) and pulse schedule alignment jitter.
   - QASM3 `stretch` variables allow relative timing to resolve deferred at compile time:
     ```qasm
     OPENQASM 3.0;
     stretch s;
     delay[s] q[0];
     x q[0];
     delay[2*s] q[0];
     x q[0];
     delay[s] q[0];
     ```
   - The compiler calculates exact pulse schedule proportions natively, eliminating edge-dependent
     decoupling phase accumulation.

### 1.5 Compound Scientific Yield Multiplier

The total scientific yield per billed QPU-second compounds the spatial and temporal gains:

$$\text{Yield Multiplier} = M_{\text{tiles}} \times \frac{T_{\text{circuit}} + T_{\text{rep\_delay}}^{\text{default}}}{T_{\text{circuit}} + T_{\text{rep\_delay}}^{\text{compressed}}}$$

For 16 simultaneous 5-qubit tiles with $50\,\mu\text{s}$ repetition delay:
$$\text{Yield Multiplier} = 16 \times 4.636 = 74.18\times$$

Every dollar or second of QPU allocation returns **74 times more experimental data points**
at higher gate fidelity than an un-multiplexed execution.

---

## 2. Prioritized Scientific Runs (Ranked by Science / QPU-Second)

| Priority | Experiment Module | Qubits / Tile | Parallel Tiles (156q) | Key Heron r2 ISA Feature | Primary Scientific Deliverable | Yield Boost |
|:---:|:---|:---:|:---:|:---|:---|:---:|
| **Run 1** | **Sedenion ($\mathbb{S}_{16}$) & Pathion ($\mathbb{P}_{32}$) Hardware Witness** | $5\text{q}$ (dim 16) or $6\text{q}$ (dim 32) | **16 tiles** ($80\text{q}$ active) | Native fractional $R_{ZZ}(\theta)$ & $R_X(\theta)$ | Hardware witness of non-associative defect census, $C_{881}$ rank loci, and FakeFez amplification validation | **$74.2\times$** |
| **Run 2** | **Octonionic Fano-Plane CSS Codes & Active Stabilizers** | $10\text{q}$ ($7\text{q}$ data + $3\text{q}$ syn) | **8 tiles** ($80\text{q}$ active) | Dynamic Circuits (`if_test`, mid-circuit `measure_2`) | Fano-plane incidence stabilizer parity checks, terminal channel separation certificates | **$37.1\times$** |
| **Run 3** | **Vacuum Endpoint Information & Model Discrimination** | $2\text{q}$ to $4\text{q}$ | **20 tiles** ($40\text{q}$ active) | QASM3 `stretch` + Hoeffding-optimal shots | Out-of-sample KL/JS divergence bounding between vacuum models; spatial cross-covariance $C(\mathbf{r}_i, \mathbf{r}_j)$ | **$92.7\times$** |
| **Run 4** | **Boolean Hidden Shift & Fold-Projection Counterexamples** | $7\text{q}$ | **12 tiles** ($84\text{q}$ active) | Staged PassManager (`optimization_level=3`) | Nonlinearity witness (PMC 4957665) & validation of Rocq formal certificates | **$55.6\times$** |

---

### 2.1 Deep Dive Run 1: Cayley-Dickson Sedenion ($\mathbb{S}_{16}$) & Pathion ($\mathbb{P}_{32}$) Hardware Witness

#### Repository Alignment
- Notes: `docs/notes/sedenion_hardware_witness_review.md`, `docs/notes/cd_associator_defect_census.md`
- Evidence: `docs/evidence/singular_sector_dynamics/fakefez_amplification.json`
- Modules: `gororoba_quantum/four_support_doubling.py`, `gororoba_quantum/four_support_rank.py`, `scripts/singular_sector_dynamics.py`, `gororoba_quantum/designs.py`

#### Mathematical Formulation
The 16 basis units of the sedenions $\mathbb{S}_{16}$ map onto a 4-qubit computational register
$\mathcal{H} \cong (\mathbb{C}^2)^{\otimes 4}$, with ancilla qubit 4 serving as the selection register
for Linear Combination of Unitaries (LCU).

For normalized zero-divisor pair $a = (e_i + e_j)/\sqrt{2}$ and $b = (e_k - e_l)/\sqrt{2}$, the LCU circuit
applies:
$$\mathcal{M} = \frac{1}{2}\left(L_{e_i} + L_{e_j}\right)$$
acting on state $|b\rangle$. The success probability on the ancilla is:
$$P(\text{anc}=0) = \frac{\|ab\|^2}{8}$$

For an exact algebraic zero divisor ($ab = 0$), $P(\text{anc}=0) = 0$ strictly by destructive interference.
In the presence of physical noise, the dark floor $P_{\text{dark}} > 0$ characterizes coherent over-rotation
and spectator phase errors.

#### Hardware Execution Mechanics
- **Lattice Allocation**: Querying `docs/evidence/heron_platform/targets.json` on `ibm_fez` yields
  exactly 16 disjoint 5-qubit tiles (80 active qubits) separated by $\text{dist}_G \ge 2$.
  Top tiles exhibit Estimated Success Probability (ESP) between $0.9532$ and $0.8788$, with average
  CZ error $\approx 2.4 \times 10^{-3}$.
- **Simultaneous Zero-Divisor Exploration**: A single execution PUB simultaneously evaluates:
  1. 8 distinct four-support dark witnesses ($ab = 0$) from the 336-row corpus,
  2. 4 bright controls ($ab \ne 0$, $P(\text{anc}=0) = 1/2$),
  3. 4 continuous fractional $R_{ZZ}(\theta)$ phase-sweep fringe points along Moreno's $G_2$ automorphism fibers.
- **Validation of FakeFez Amplification**: Replaces the simulation results in
  `fakefez_amplification.json` (which measured noisy $P(\text{anc}=0) \in [0.0886, 0.3069]$ across 0 to 2
  amplification rounds) with true QPU hardware observations under continuous $R_{ZZ}(\theta)$ twists.

---

### 2.2 Deep Dive Run 2: Octonionic Fano-Plane CSS Codes & Active Stabilizers

#### Repository Alignment
- Notes: `docs/notes/levratti-2026-fano-css.md`, `docs/notes/levratti-2026-active-stabilizers.md`, `docs/notes/ibm_quantum/execute-dynamic-circuits.md`
- Formal Certificates: `docs/evidence/formal_certificates/TerminalChannelSeparation*.v`
- Modules: `gororoba_quantum/correction_circuits.py`, `gororoba_quantum/correction_planning.py`

#### Mathematical Formulation
The 7 imaginary units of the octonions $\mathbb{O}_8$ ($e_1, \dots, e_7$) form the projective Fano
plane $\mathrm{PG}(2, 2)$, which directly defines the parity-check incidence matrix of the $[[7, 1, 3]]$
Steane CSS code. The 7 lines $\{p, r, t\}$ with $e_p e_r = \pm e_t$ biject to the projective dual
vectors $v_L \in \mathbb{F}_2^3$, indexing the weight-4 $Z$-stabilizers $S_Z(v_L)$ with support on
$\{1..7\} \setminus \{p, r, t\}$.

#### Hardware Execution Mechanics
- **Patch Layout**: Embedding the 7 data qubits plus 3 syndrome ancillas (10-qubit tiles) onto Heron's
  heavy-hex lattice requires connected subgraphs with at least 3 degree-3 vertices.
  The lattice solver extracts 7 to 8 disjoint 10-qubit patches ($70\text{--}80$ active qubits) with
  complete buffer isolation.
- **Dynamic Circuit Feedback**: Utilizes Heron r2's mid-circuit readout (`measure_2`, duration $1.34\,\mu\text{s}$)
  and fast feed-forward (`if_test` within $\approx 300\,\text{ns}$):
  ```python
  circuit.measure(ancilla, syn_bit)
  with circuit.if_test((syn_bit, 1)):
      circuit.x(data_qubit)
  ```
- **Terminal Channel Separation**: Compares active stabilizer correction (measured feedback) against
  recorded-bit-independent controls, testing whether active syndrome correction preserves the
  algebraic invariant subspace against physical reset and readout distortion.

---

### 2.3 Deep Dive Run 3: Vacuum Endpoint Information, Reality Ripple & Model Discrimination

#### Repository Alignment
- Notes: `docs/notes/vacuum_field_run_opportunities.md`, `docs/notes/reality_ripple_measurement_design.md`,
  `docs/notes/model_discrimination_optimizer.md`, `docs/notes/hoeffding-1963.md`
- Evidence: `docs/evidence/vacuum_endpoint_information/`, `docs/evidence/vacuum_models/`

#### Mathematical Formulation
The transmon array serves as an open-quantum-system sensor to discriminate between:
1. Standard Markovian Lindblad relaxation/dephasing:
   $$\dot{\rho} = -i [H, \rho] + \gamma_1 \mathcal{D}[\sigma^-]\rho + \frac{\gamma_\phi}{2} \mathcal{D}[\sigma^z]\rho$$
2. Structured vacuum/endpoint fluctuation models (fractional relaxation, long-range bath correlation,
   correlated phase noise).

#### Hardware Execution Mechanics
- **Calibration Stratification**: 20 disjoint 2-qubit entangled pairs ($40$ active qubits) are distributed
  across three calibration strata (top 25% fidelity, median 50%, and bottom 25% edge regions).
- **QASM3 Stretch Tomography**: Coherent wait times $\tau \in [0, 50\,\mu\text{s}]$ are swept using
  `stretch` variables, ensuring exact relative spacing between $X_{\pi/2}$ Ramsey pulses.
- **Hoeffding-Optimal Sample Allocation**: Bounding empirical Kullback-Leibler and Jensen-Shannon
  divergences with distribution-free confidence $1 - \delta = 0.99$:
  $$N_{\text{shots}} \ge \frac{\ln(2/\delta)}{2 \epsilon^2}$$
  At $\epsilon = 0.02$ and $\delta = 0.01$, $N_{\text{shots}} \ge 6,623 \implies 8,192$ shots/PUB.
- **Spatial Cross-Covariance Matrix**: Joint bitstrings across all 20 tiles yield the inter-tile
  cross-covariance matrix:
  $$C_{ij} = \langle Z_i Z_j \rangle - \langle Z_i \rangle \langle Z_j \rangle$$
  Comparing $C_{ij}$ against physical heavy-hex Manhattan distance $D_{ij}$ separates local
  Two-Level System (TLS) defects ($C_{ij} \to 0$ for $D_{ij} \ge 2$) from chip-wide correlated
  vacuum fluctuations ($C_{ij} > 0$ across long distances).

---

### 2.4 Deep Dive Run 4: Boolean Hidden Shift & Fold-Projection Counterexamples

#### Repository Alignment
- Notes: `docs/notes/handbacks/boolean_functions_and_hidden_shift.md`, `docs/notes/pmc-4957665-nonlinearity-measures.md`
- Formal Proofs: `docs/evidence/folding_proofs/`
- Modules: `gororoba_quantum/boolean_anf.py`, `gororoba_quantum/designs.py` (Design C)

#### Hardware Execution Mechanics
- **Lattice Allocation**: 12 disjoint 7-qubit tiles (84 active qubits) with buffer guard bands.
- **Circuit Architecture**: Design C Walsh spectrum witnesses evaluating cubic and quartic Algebraic
  Normal Form (ANF) monomials from Reed-Muller codes $RM(n-2, n-1)$.
- **Staged PassManager (`optimization_level=3`)**: Transpiled using custom routing stages that preserve
  algebraic sign structure and bypass high-noise coupler paths.
- **Deliverable**: Hardware witness validating nonlinearity bounds from Boyar-Find-Peralta (PMC 4957665)
  and empirical confirmation of Rocq formal certificates (`folding_proofs`).

---

## 3. Recommended Qiskit Runtime Packing Pipeline

### 3.1 SamplerV2 vs EstimatorV2 for Multi-Tile Multiplexing

When executing spatially multiprogrammed tiles, **SamplerV2 is mandatory**. EstimatorV2 is unsuitable
for the following architectural reasons:

1. **Obscuration of Joint Bitstring Distributions**:
   EstimatorV2 evaluates expectation values of specific commuting Pauli strings. It does not return raw
   joint bitstrings, making it impossible to evaluate cross-tile correlations $C(\mathbf{r}_i, \mathbf{r}_j)$
   or perform simultaneous multi-observable post-selection.
2. **Hidden Twirling Multipliers**:
   EstimatorV2 applies automated Pauli twirling and Zero-Noise Extrapolation (ZNE), introducing a hidden
   multiplier of $10\times\text{--}60\times$ in circuit evaluations per observable, rapidly exhausting
   the rolling 600-second execution quota.
3. **SamplerV2 Implementation**:
   Each tile appends its own explicit basis change ($H$ for $X$-basis, $S^\dagger H$ for $Y$-basis,
   identity for $Z$-basis) prior to terminal measurement into namespaced classical registers
   `tile_{k}_c`. A single execution returns the full joint 156-qubit bitstring per shot.

### 3.2 Single-PUB Parameter Vector Wave-Table Sweeps

Submitting separate circuits for each parameter point $\theta \in [0, \pi/2]$ incurs severe runtime
penalties due to per-circuit initialization overhead.

**Recommended Approach**:
Bind a `ParameterVector` across an array of shape `(N_angles, N_params)` within a **single PUB**:

```python
from qiskit.circuit import ParameterVector
from qiskit_ibm_runtime import SamplerV2

# Define parameter vector across the multiplexed circuit
theta = ParameterVector("theta", length=16)
# Build wide circuit with theta parameters ...

# Form single PUB with (N_angles, 16) array
pub = (wide_circuit, parameter_values_array, 8192)
job = sampler.run([pub])
```

Heron r2 control electronics load updated parameter values into FPGA wave-table memory in
microseconds during the shot loop, completely eliminating job recompilation latency.

### 3.3 Abnormal Gate Subsequence Detection and Bypass

On `ibm_fez` and `ibm_marrakesh`, hardware characterization has revealed that specific 3-gate native
subsequences trigger severe coherent phase errors:

$$\dots \longrightarrow R_Z(\phi) \longrightarrow CZ \longrightarrow SX \longrightarrow \dots$$

When this sequence executes on couplers with CZ error exceeding $4.0 \times 10^{-3}$ or significant
qubit-coupler frequency detuning:
1. Virtual $R_Z$ phase frame updates immediately precede the dynamic microwave pulse of $CZ$,
2. The subsequent $SX$ drive on either transmon encounters transient Stark detuning and spectator
   state leakage unmodeled by standard VF2 transpiler scoring.

#### Automated Bypass Protocol
The compiler engine in `gororoba_quantum/heron_multiprogramming.py` audits transpiled circuits:
- **Commutation**: Because $CZ = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes Z$ is diagonal
  in the computational basis, $R_Z(\phi) \otimes I$ and $CZ$ strictly commute:
  $$[R_Z(\phi) \otimes I, CZ] = 0$$
  The compiler commutes $R_Z$ past $CZ$, reordering the sequence to $CZ \to R_Z(\phi) \to SX$.
- **Echo Buffering**: Where commutation is prevented by cross-qubit dependencies, a 1-dt alignment delay
  or dynamical decoupling echo pulse is inserted between $CZ$ and $SX$.

---

## 4. Quantitative Target Verification Summary

Based on the live calibration snapshot in `docs/evidence/heron_platform/targets.json`:

| Metric | `ibm_fez` | `ibm_kingston` | `ibm_marrakesh` |
|:---|:---:|:---:|:---:|
| **Physical Qubits** | 156 | 156 | 156 |
| **Undirected CZ Couplers** | 176 | 176 | 176 |
| **Median CZ Error** | $2.6830 \times 10^{-3}$ | $2.1494 \times 10^{-3}$ | $2.8674 \times 10^{-3}$ |
| **Median RZZ Fractional Error** | $2.9198 \times 10^{-3}$ | $2.0507 \times 10^{-3}$ | $4.2530 \times 10^{-3}$ |
| **Median SX Error** | $3.0131 \times 10^{-4}$ | $2.6035 \times 10^{-4}$ | $3.9638 \times 10^{-4}$ |
| **Median Readout (`measure`) Duration** | $1660\,\text{ns}$ | $2180\,\text{ns}$ | $2684\,\text{ns}$ |
| **Median Readout_2 (`measure_2`) Duration** | $1340\,\text{ns}$ | $1380\,\text{ns}$ | $1884\,\text{ns}$ |
| **Run 1 Disjoint 5q Tiles Packed ($\text{dist}_G \ge 2$)** | **16 tiles** ($80\text{q}$) | **16 tiles** ($80\text{q}$) | **16 tiles** ($80\text{q}$) |
| **Run 2 Disjoint 10q Tiles Packed ($\text{dist}_G \ge 2$)** | **7 tiles** ($70\text{q}$) | **7 tiles** ($70\text{q}$) | **7 tiles** ($70\text{q}$) |
| **Run 3 Disjoint 2q Tiles Packed ($\text{dist}_G \ge 2$)** | **20 tiles** ($40\text{q}$) | **20 tiles** ($40\text{q}$) | **20 tiles** ($40\text{q}$) |
| **Run 4 Disjoint 7q Tiles Packed ($\text{dist}_G \ge 2$)** | **12 tiles** ($84\text{q}$) | **12 tiles** ($84\text{q}$) | **12 tiles** ($84\text{q}$) |
| **Run 1 Throughput Multiplier ($50\,\mu\text{s}$ rep_delay)** | **$74.18\times$** | **$74.18\times$** | **$74.18\times$** |

---

## 5. Artifact and Verification Index

- **Engine Module**: [`gororoba_quantum/heron_multiprogramming.py`](../../gororoba_quantum/heron_multiprogramming.py)
- **Unit Test Suite**: [`gororoba_quantum/test_heron_multiprogramming.py`](../../gororoba_quantum/test_heron_multiprogramming.py)
- **Audit Script**: [`scripts/heron_spatial_multiprogramming.py`](../../scripts/heron_spatial_multiprogramming.py)
- **Retained Evidence**: [`docs/evidence/heron_platform/spatial_multiprogramming_audit.json`](../evidence/heron_platform/spatial_multiprogramming_audit.json)
- **Target Calibration Snapshot**: [`docs/evidence/heron_platform/targets.json`](../evidence/heron_platform/targets.json)
