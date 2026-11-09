# Ascella Architecture, Foundational Axioms, and Photonic Quantum Stack

This document synthesizes the physical first principles, mathematical axioms, hardware architecture, and
software stack governing Quandela's **Ascella** quantum processing unit (`qpu:ascella`), its historical lineage,
and its Python development ecosystem (`perceval-quandela`, `exqalibur`). It establishes
the formal literature and reference foundation for all Quandela-targeted research in this repository.

---

## 1. Corporate Lineage and Commercial Evolution of Quandela

Quandela was founded in 2017 as a spin-off from the **Centre de Nanosciences et de Nanotechnologies (C2N)**,
a joint research laboratory of the French National Centre for Scientific Research (CNRS) and Universite
Paris-Saclay. The founding team combined world-leading expertise in solid-state quantum optics, semiconductor
fabrication, and optical engineering:

- **Pascale Senellart**: Research Director at CNRS, leading authority on semiconductor quantum dot cavity
  quantum electrodynamics, and inventor of deterministic in situ optical lithography for microcavity coupling.
- **Valerian Giesz**: Optical physicist specializing in cavity-enhanced single-photon emission, co-founder and
  chief operating officer / executive leadership.
- **Niccolo Somaschi**: Specialist in high-purity single-photon sources and quantum optics, chief technology officer.

### Product and Platform Milestones
1. **e-PIXELS / Promethee (2017-2021)**: Modular, fiber-coupled, cryogenic semiconductor single-photon sources
   operating under resonant excitation, supplying academic and industrial quantum optics laboratories worldwide.
2. **Ascella (MOSAIQ-6, 2022)**: The world's first commercial, cloud-accessible, discrete-variable photonic
   quantum computer based on deterministic single-photon generation. Features a 12-mode universal linear-optical
   interferometer operating with up to 6 demultiplexed single photons.
3. **Belenos (MOSAIQ-12, 2024-2025)**: Successor commercial QPU featuring a 24-mode programmable MZI mesh
   (552 directional couplers, 574 phase elements) driven by a 12-channel demultiplexer, enabling 12-photon
   entanglement and variational processing.
4. **Altair / MosaiQ On-Premise Systems (2025-2026)**: Rack-mounted, air-cooled photonic quantum computing units
   integrated into high-performance computing centers (including OVHcloud and the EuroHPC Jules Verne consortium).

---

## 2. Foundational Axioms and First Principles of Linear Optical Quantum Computing (LOQC)

Photonic quantum computing on discrete variables operates by injecting single-photon Fock states into passive
reconfigurable interferometers and performing projective detection. The mathematical framework rests on six
foundational axioms and theorems:

### Axiom I: Bosonic Fock Space and Canonical Commutation Relations
A system of $m$ optical spatial/temporal modes is described by a bosonic Fock space $\mathcal{H} = \bigotimes_{j=0}^{m-1} \mathcal{H}_j$.
Mode annihilation and creation operators $a_j, a_k^\dagger$ satisfy the canonical commutation relations:
$$[a_j, a_k^\dagger] = \delta_{jk} \mathbb{I}, \quad [a_j, a_k] = 0, \quad [a_j^\dagger, a_k^\dagger] = 0$$

A basis state (Fock state) is parameterized by occupation numbers $\mathbf{s} = (s_0, s_1, \dots, s_{m-1}) \in \mathbb{N}^m$:
$$|\mathbf{s}\rangle = |s_0, s_1, \dots, s_{m-1}\rangle = \prod_{j=0}^{m-1} \frac{(a_j^\dagger)^{s_j}}{\sqrt{s_j!}} |0\rangle^{\otimes m}$$
The total photon number operator is $\hat{N} = \sum_{j=0}^{m-1} a_j^\dagger a_j = \sum_{j=0}^{m-1} \hat{n}_j$.

### Axiom II: Unitary Passive Linear Transformation (Bogoliubov Scattering)
A lossless, passive $m$-mode linear optical network implements a unitary transformation on the single-photon
subspace. Under a scattering matrix $U \in U(m)$, the mode creation operators transform linearly according to:
$$a_i^\dagger \longrightarrow \sum_{j=0}^{m-1} U_{ji} a_j^\dagger$$
Because the physical network is passive and energy-conserving, total photon number is strictly conserved:
$$[\hat{N}, \hat{U}] = 0$$

### Axiom III: Quantum Transition Amplitudes and Matrix Permanents
For an $n$-photon input state $|\mathbf{s}\rangle = |s_0, \dots, s_{m-1}\rangle$ and output state $|\mathbf{t}\rangle = |t_0, \dots, t_{m-1}\rangle$
(with $\sum s_i = \sum t_j = n$), the quantum transition amplitude under $U$ is given by the matrix permanent:
$$\langle \mathbf{t} | \hat{U} | \mathbf{s} \rangle = \frac{\text{perm}(U_{\mathbf{s}, \mathbf{t}})}{\sqrt{\prod_{i=0}^{m-1} s_i! \prod_{j=0}^{m-1} t_j!}}$$
where $U_{\mathbf{s}, \mathbf{t}}$ is the $n \times n$ submatrix formed by taking $s_i$ copies of column $i$ and $t_j$
copies of row $j$ of the transfer matrix $U$.
- The permanent of an $n \times n$ matrix $A$ is defined by:
  $$\text{perm}(A) = \sum_{\sigma \in S_n} \prod_{k=1}^n A_{k, \sigma(k)}$$
- **Complexity consequence (Troyansky, Tichy, Aaronson & Arkhipov 2011/2013)**: Computing matrix permanents
  is $\#\mathbf{P}$-hard (Valiant 1979). Simulating non-interacting bosons scattering through a linear network
  (Boson Sampling) cannot be computed efficiently by a classical Turing machine unless the polynomial hierarchy
  collapses to its third level. That theorem covers exact sampling; the approximate case rests on the
  permanent-of-Gaussians conjectures of Aaronson & Arkhipov.
- **Additive approximation (Gurvits 2005)**: Glynn's identity
  $\text{perm}(A) = \mathbb{E}_{x \in \{\pm 1\}^n}\left[\prod_i x_i \prod_i (Ax)_i\right]$ gives an unbiased estimator
  whose every sample has modulus at most $\lVert A \rVert^n$, so $O(1/\varepsilon^2)$ samples of $O(n^2)$ work each
  estimate $\text{perm}(A)$ within $\pm\varepsilon \lVert A \rVert^n$. A submatrix of a unitary has
  $\lVert A \rVert \le 1$, so the error is absolute, while a typical $n$-photon amplitude on $m$ modes is of order
  $\sqrt{n!/m^n}$: the estimator resolves bunched or otherwise large amplitudes and leaves the typical outcomes
  that carry the hardness argument below its noise floor. Aaronson & Hance (2014) generalize and derandomize it.

### Axiom IV: Hong-Ou-Mandel (HOM) Two-Photon Quantum Interference
When two indistinguishable single photons enter opposite input ports of a balanced 50:50 beam splitter with
scattering matrix $B = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$:
$$|1, 1\rangle = a_0^\dagger a_1^\dagger |0,0\rangle \xrightarrow{B} \frac{1}{2} (a_0^\dagger + a_1^\dagger)(a_0^\dagger - a_1^\dagger)|0,0\rangle = \frac{1}{2} \left((a_0^\dagger)^2 - (a_1^\dagger)^2\right)|0,0\rangle = \frac{1}{\sqrt{2}} (|2, 0\rangle - |0, 2\rangle)$$
- **Coincidence extinction**: The probability of coincidence detection $P(1, 1) = |\langle 1, 1 | B | 1, 1 \rangle|^2 = 0$.
- **Partial indistinguishability model**: In real physical devices, the input state is a statistical mixture of
  indistinguishable photons (weight $V_{\text{HOM}}$) and distinguishable photons (weight $1 - V_{\text{HOM}}$).
  The measured coincidence probability evaluates to:
  $$P_{\text{coinc}}(V_{\text{HOM}}) = \frac{1 - V_{\text{HOM}}}{2}$$
  yielding the direct calibration relation: $V_{\text{HOM}} = 1 - 2 P_{\text{coinc}}$.

### Axiom V: Measurement-Induced Nonlinearity (The KLM Theorem)
Photons do not exhibit direct optical nonlinear interactions at single-quantum energies in linear media.
Knill, Laflamme, and Milburn (KLM, *Nature* 2001) proved that scalable, universal quantum computation is achievable
using only:
1. Single-photon Fock sources;
2. Passive linear optical networks (beam splitters, phase shifters);
3. Single-photon detectors (or threshold detectors);
4. Measurement-induced non-linear sign shifts (NS gates) aided by ancillary photons and feed-forward.

Dual-rail qubit encoding maps logical states to path modes:
$$|0\rangle_L \equiv |1, 0\rangle, \quad |1\rangle_L \equiv |0, 1\rangle$$
Entangling gates (such as CZ and CNOT) succeed non-deterministically (e.g. $P_{\text{succ}} = 1/9$ or $1/16$ in
basic post-selected arrangements), scaled to near-deterministic fault-tolerance via optical cluster states
(Raussendorf-Briegel, Browne-Rudolph 2005) and static linear optics (Mezher et al. 2023).

### Axiom VI: Universal Unitary Mesh Synthesis (Reck and Clements Decompositions)
Any discrete $m$-mode unitary transformation $U \in U(m)$ can be decomposed exactly into a mesh of balanced
beam splitters and phase shifters:
1. **Reck et al. (1994, PRL)**: Triangular mesh topology using $m(m-1)/2$ Mach-Zehnder Interferometers (MZIs).
   Optical depth scales as $2m - 3$; transmission loss is unbalanced across modes.
2. **Clements et al. (2016, Optica)**: Rectangular mesh topology using $m(m-1)/2$ MZIs. Optical depth is balanced
   at exactly $m$, equalizing optical loss and dispersion across all paths.

Each constituent MZI consists of two 50:50 directional couplers ($R_x$ rotations) enclosing internal ($\theta$)
and external ($\phi$) phase shifters:
$$\text{MZI}(\theta, \phi) = R_x\left(\frac{\pi}{2}\right) \begin{pmatrix} e^{i\theta} & 0 \\ 0 & 1 \end{pmatrix} R_x\left(\frac{\pi}{2}\right) \begin{pmatrix} e^{i\phi} & 0 \\ 0 & 1 \end{pmatrix}$$

*Universality vs. Physical Reachability Boundary*: Ideal Clements universality assumes perfectly balanced 50:50 couplers.
On physical processors (including Ascella), fabrication deviations ($R \approx 56.7\text{--}56.8\%$) contract the reachable
unitary subspace. Target fidelity is achieved through numerical parameter optimization to an average Haar-ensemble
fidelity of $F = 99.7 \pm 0.08\%$ (Maring et al. 2024), rather than an unconstrained worst-case algebraic certificate.

---

## 3. Ascella Hardware Architecture Dissection

Quandela's **Ascella** processor (`qpu:ascella`) couples an ultra-bright solid-state quantum dot source, an
active temporal-to-spatial demultiplexer, a 12-mode reconfigurable integrated optical chip, and a superconducting
nanowire detector array.

```
+-----------------------------------------------------------------------------------------+
|                                  ASCELLA QPU ARCHITECTURE                               |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Pulsed Laser 80 MHz]                                                                  |
|         | (LA-phonon-assisted near-resonant excitation @ 928 nm)                        |
|         v                                                                               |
|  +------------------------+                                                             |
|  | Gated InGaAs QD Cavity |  --> Repetition rate: 80 MHz                                |
|  | Monolithic Micropillar |  --> Lifetime T_1: 92 ps; First lens brightness: 55%        |
|  | Cryostat @ 5 Kelvin    |  --> Purity P = 1 - g^(2)(0) > 99% (baseline g2 = 0.0073)   |
|  +------------------------+  --> Source indistinguishability M_s = 94.38%               |
|         |                                                                               |
|         v (Sequential single-photon train)                                              |
|  +------------------------+                                                             |
|  | Active Optical Demux   |  --> Demultiplexing clock: 80 MHz / 6 = 13.33 MHz            |
|  | Fiber Delays & Shutters|  --> Injects |1,0,1,0,1,0,1,0,1,0,1,0> into modes 0,2,4,6,8,10  |
|  +------------------------+                                                             |
|         | | | | | | (6 spatial optical fibers, 70% demux transmission)                  |
|         v v v v v v                                                                     |
|  +-----------------------------------------------------------------------------------+  |
|  |           12-MODE UNIVERSAL RECONFIGURABLE PHOTONIC CHIP (CLEMENTS)               |  |
|  |                                                                                   |  |
|  |  - 12 Waveguide spatial modes (PIC insertion & transmission: 45%)                 |  |
|  |  - 132 Directional couplers (theta in [1.4204, 1.4739] rad; R = 56.8 +- 0.6%)   |  |
|  |  - 126 Thermo-optic microheater phase shifters (phi = A * V^(o2) + b)             |  |
|  |  - Clear-box physical crosstalk model (Fyrillas et al., Optica 2024; no neural net)|  |
|  +-----------------------------------------------------------------------------------+  |
|         | | | | | | | | | | | | (12 output spatial modes)                               |
|         v v v v v v v v v v v v                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |              SUPERCONDUCTING NANOWIRE DETECTORS (SNSPDs @ 92% Eff)                |  |
|  |                                                                                   |  |
|  |  - 12 Threshold single-photon counting channels (dark counts < 20 Hz baseline)   |  |
|  |  - Swabian Instruments Time Tagger (TDC) with 1 ns coincidence integration window |  |
|  |  - Total optical setup efficiency: 8.4 +- 0.2% (live reported transmittance 5.5%) |  |
|  +-----------------------------------------------------------------------------------+  |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

### 3.1 Quantum Dot Microcavity Single-Photon Source
- **Emitter material & structure**: Gated Indium Gallium Arsenide (InGaAs) quantum dot embedded in a monolithic
  GaAs/AlAs distributed Bragg reflector (DBR) micropillar cavity (Somaschi et al., *Nature Photonics* 2016),
  operated inside a closed-cycle cryostat at 5 K.
- **Excitation scheme**: Near-resonant longitudinal-acoustic (LA) phonon-assisted optical excitation (Thomas et al.,
  *Phys. Rev. Lett.* 126, 233601, 2021). The excitation laser is detuned from the exciton resonance, with lattice
  phonons absorbing or emitting the energy differential. This bypasses the cross-polarization filtering losses of
  strictly resonant $\pi$-pulse schemes while suppressing excitation laser leakage.
- **Spectral parameters**:
  - Operating wavelength: $\lambda = 928\text{ nm}$.
  - Emission lifetime: $T_1 = 92\text{ ps}$.
  - First-lens collection brightness: $55\%$.
  - Spectral filtering: Free-space bandpass filter module ($\text{FWHM} = 800\text{ pm}$, transmission $75\%$)
    and single-mode fiber coupling ($70\%$).
- **Source purity and indistinguishability**:
  - Normalized second-order correlation at zero delay: $g^{(2)}(0) = (7.32 \pm 0.07) \times 10^{-3} = 0.00732$.
    Single-photon purity $P = 1 - g^{(2)}(0) > 99\%$. (Note: live calibration on `qpu:ascella` reports drifting
    operational values, e.g. $g_2 = 2.1\%$).
  - Hong-Ou-Mandel visibility: $V_{\text{HOM}} = 0.9296 \pm 0.0003$.
  - Corrected 2-photon source indistinguishability: $M_s = 0.9438 \pm 0.0003$ ($94.38\%$). Pairwise on-chip
    indistinguishability $M_{ij}$ across all 15 pairs ranges from $91.1\%$ to $94.3\%$. Genuine 4-photon and
    6-photon indistinguishabilities evaluate to $p_4 = 0.85 \pm 0.02$ and $p_6 = 0.76 \pm 0.02$.

### 3.2 Active Optical Demultiplexer
Because photons are emitted sequentially by a single quantum dot, Ascella uses an active optical demultiplexer
(transmission $70\%$):
- Optical pump laser repetition rate: Exactly $80\text{ MHz}$ (period $12.5\text{ ns}$).
- Fiber delay lines of matched graduated lengths route sequential pulses into 6 spatial optical fibers.
- Active optical shutters select photon inputs, enabling states with $N < 6$ photons.
- Synchronized injection into the 6 physical input modes: **0, 2, 4, 6, 8, 10**.
- Resulting processor master clock rate:
  $$f_{\text{clock}} = \frac{80\text{ MHz}}{6} = 13.33\text{ MHz}$$
  This division accounts for the six spatial demultiplexer channels routing pulses from the 80 MHz pump train, matching the live `qpu:ascella` specification field `Clock (MHz): 13.33` (consistent model timing rather than an explicit causal derivation in the primary text).

### 3.3 12-Mode Programmable Photonic Chip
- **Interferometer size**: 12 optical waveguide modes in a folded Clements rectangular mesh topology.
- **PIC insertion and transmission**: $45\%$.
- **Components**: 132 directional couplers and 126 thermo-optic phase shifters ($\phi_0 \dots \phi_{125}$).
  - Directional coupler reflectivity: $R = (56.8 \pm 0.6)\%$ (Supplementary Section 2; the main text states $(56.7 \pm 0.6)\%$), corresponding to calibrated rotation angles
    $\theta = 2 \arccos\sqrt{R} \in [1.4204, 1.4739]\text{ rad}$ (mean $1.4347\text{ rad}$).
  - Static phases: $\mathbf{b} = (0.1 \pm 1.2)\text{ rad}$.
  - Microheater efficiency: diagonal crosstalk element $A_{ii} = (0.034 \pm 0.001)\text{ rad/V}^2$, requiring
    approximately $10\text{ V}$ to induce a $\pi$ phase shift.
  - Spatial loss uniformity: Output mode 10 exhibits a relative transmission of $75\%$ compared to mode 6 due to
    the compact folded layout of the chip.
- **Fixed input state and permutation**:
  The physical chip input is fixed to $|\mathbf{s}_{\text{default}}\rangle = |1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0\rangle$.
  To execute a target unitary $U$ on an arbitrary input state $|\text{IN}\rangle$, the transpiler computes the
  permutation matrix $U_{\text{perm}}$ such that $U_{\text{perm}} |\mathbf{s}_{\text{default}}\rangle = |\text{IN}\rangle$,
  and synthesizes the composite unitary $U' = U \cdot U_{\text{perm}}$.
- **Clear-box physical chip characterization (Fyrillas et al., Optica 2024)**:
  Rather than using black-box neural networks (which lack interpretability and physical error bounds), Quandela
  implements an exact physical forward model:
  $$\hat{\boldsymbol{\phi}} = A \cdot \mathbf{V}^{\odot 2} + \mathbf{b}$$
  where $A$ is the $126 \times 126$ thermal crosstalk matrix and $\mathbf{b}$ is the static phase vector.
  High-dimensional parameter optimization fits the $\approx 16,000$ physical parameters (crosstalk elements,
  directional coupler reflectivities, and mode losses) against measured transmission fringes.

### 3.4 Detection and Readout
- **Detectors**: Array of 12 Superconducting Nanowire Single-Photon Detectors (SNSPDs).
  - Average detection efficiency: $92\%$.
  - Dark count rate: under $20\text{ Hz}$ at baseline; live device telemetry shows operational dark counts
    ranging from $76$ to $281\text{ counts/s}$ (peaking up to $1,885\text{--}2,169\text{ counts/s}$ on mode 10 in retained telemetry records).
- **Readout electronics**: Swabian Instruments Time Tagger (time-to-digital converter, TDC).
  - Coincidence integration window: $1\text{ ns}$ (the Supplementary specifies the TDC and the $1\text{ ns}$ coincidence window;
    the underlying hardware implementation details are not stated, making earlier 'sub-nanosecond FPGA' claims unsupported).
  - Post-processing samples $N$-photon ($1 \le N \le 6$) coincidence distributions across all 12 channels.
  - Overall optical setup efficiency: $(8.4 \pm 0.2)\%$ at publication (live reported transmittance $5.52\%$).
  - 6-photon coincidence count rate: $4\text{ Hz}$ at $80\text{ MHz}$ pump rate.

---

## 4. The Quandela Python Software Stack

Quandela's software architecture organizes quantum computing via linear optics into a layered stack
comprising high-level circuit and processor abstractions, compiled C++ mathematical engines, and REST-based
cloud communication:

```
                      +-----------------------------+
                      |   User Application / Qiskit |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |       Perceval 1.3.1        |
                      |   (pcvl.Circuit, Processor, |
                      |    BasicState, StateVector, |
                      |       Source, NoiseModel)   |
                      +-----------------------------+
                        /                         \
                       / (pybind11 C++ engine)     \ (HTTP REST / requests)
                      v                             v
+-------------------------------+      +---------------------------------+
|       exqalibur 1.4.2         |      | perceval.providers.quandela     |
|  - SLOS permanent engines     |      |  - QuandelaCommunicationLayer   |
|    (SLOS, SLOS_V2, SLOS_V3)   |      |  - RPCHandler (Bearer Auth)     |
|  - Clifford & Clifford sampler|      |  - Job serialization & dispatch |
|  - RectangularDecomposer      |      |  - QPU / Sim telemetry polling  |
|  - CircuitOptimizer           |      | (packaged in perceval-quandela) |
+-------------------------------+      +---------------------------------+
                                                        |
                                                        v
                                       +---------------------------------+
                                       |      Quandela Cloud API         |
                                       |   (qpu:ascella, qpu:belenos,    |
                                       |    sim:ascella, sim:belenos)    |
                                       +---------------------------------+
```

### 4.1 `exqalibur`: Compiled C++ Engine
`exqalibur` provides optimized linear optics computational routines bound via pybind11:
- **Matrix permanents (`permanent_cx`, `permanent_fl`, `permanent_in`)**: Exact permanents of square
  matrices by Ryser's or Glynn's formula (`ptype="ryser"` or `"glynn"`). The docstring states the default:
  Glynn on one or two threads, Ryser otherwise; `exqalibur.Config.compute_max_thread_count` sets the thread
  count. exqalibur ships no source, so the subset order is inferred from cost: measured single-thread time
  grows as $n^{k} 2^n$ with $k = 1.18$ (Ryser) and $1.22$ (Glynn) over $n = 14$ to $24$, which matches
  Gray-code traversal ($k = 1$) and excludes a plain subset sum ($k = 2$); Glynn runs about 7 times faster
  than Ryser on one thread. Measured on Darwin arm64, exqalibur 1.4.1
  ([probe](../../evidence/quandela/permanent-estimators/permanent_probe.py),
  [results](../../evidence/quandela/permanent-estimators/permanent_probe.json)).
- **Permanent estimation (`estimate_permanent_cx`, `estimate_permanent_fl`; `ptype="gurvits"`, the only
  accepted value)**: Gurvits' randomized estimator. It returns the permanent of a diagonal matrix exactly with
  a zero interval, which identifies Glynn's $\pm 1$ sampling distribution. The reported 99% half-width
  scales as $1/\sqrt{n_\text{iter}}$ and is an empirical (sample-variance) interval, about 19 times narrower
  than the worst-case Hoeffding bound of Gurvits' analysis; on 300 Ascella-sized $6 \times 6$ blocks of Haar
  unitaries at $n_\text{iter} = 10^4$ it contained the exact permanent in 99.3% of trials. The docstring warns
  that the estimate is accurate in modulus and not in phase. Perceval reaches it only through
  `NaiveApproxBackend(gurvits_iterations=10000)`, which reports amplitudes and probability intervals with it.
- **Where the estimator pays**: at $10^4$ iterations it overtakes exact Glynn near $n = 19$ on one thread
  (8 ms against 220 ms at $n = 24$), but on an $n \times n$ Haar unitary its half-width exceeds the modulus of
  the permanent by 185 times at $n = 20$ and 460 times at $n = 24$. At Ascella's six photons the median
  $|\text{perm}|$ is $7.3 \times 10^{-3}$ against a half-width of $1.7 \times 10^{-3}$, while the exact
  $6 \times 6$ permanent costs microseconds; exact backends (`SLOS`, `Naive`) are the right tool for Ascella and
  Belenos, and the estimator serves large permanents (bunched outputs, near-identity or nonnegative blocks)
  where $|\text{perm}(A)|$ is comparable to $\lVert A \rVert^n$.
- **Sampling (`Clifford2017`, `SLAPSampler`, `SourceSampler`)**: `Clifford2017` implements the Clifford &
  Clifford (2018) sampler, whose cost per sample is $O(n 2^n)$ plus a polynomial in $m$ and $n$: exponential
  in the photon number, and far below enumerating every output amplitude. `SourceSampler` draws input states
  from a noisy-source model (`Source.create_sampler`); `SLAPSampler` carries no docstring.
- **Circuit transpilation and optimization**:
  - `RectangularDecomposer`: Decomposes arbitrary unitary transformations $U \in U(m)$ into the Clements
    rectangular MZI mesh architecture.
  - `CircuitOptimizer`: Fits a target unitary on an interferometer with variable parameters by gradient
    descent, scoring the fit by fidelity.
  - *Note*: Triangular Reck decomposition is implemented in pure Python within `perceval.utils.algorithms.decomposition.decompose_triangle`.

### 4.2 `perceval` Core Library
- **State representations**:
  - `pcvl.BasicState`: Represents definite Fock states $|n_0, n_1, \dots, n_{m-1}\rangle$.
    ```python
    import perceval as pcvl
    # 2 photons in modes 0 and 2 of a 12-mode processor
    input_state = pcvl.BasicState([1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    ```
  - `pcvl.StateVector`: Represents coherent linear superpositions of Fock states $\sum c_i |s_i\rangle$.
  - `pcvl.SVDistribution`: Represents classical probability mixtures over state vectors.
  - *Note*: `pcvl.State` does not exist; Fock states are instantiated via `BasicState`.
- **Circuit composition**:
  ```python
  circuit = pcvl.Circuit(12)
  circuit.add(0, pcvl.BS())          # Beam splitter on modes 0 and 1
  circuit.add(0, pcvl.PS(phi=0.785)) # Phase shift on mode 0
  ```
- **Backend hierarchy (`pcvl.BackendFactory`)**:
  - `SLOS`: Default strong simulation backend instantiated via `SLOSExqaliburBackend` (`perceval.backends._slos_exqalibur`),
    interfacing with compiled C++ `exqalibur.SLOS`, `SLOS_V2`, and `SLOS_V3`.
  - `SLOS_LEGACY`: Pure-Python reference implementation (`SLOSBackend` in `perceval.backends._slos`).
  - `CliffordClifford2017`: Fast sampling backend (`Clifford2017Backend` in `perceval.backends._clifford2017`).
  - `SamplingStepper`: Step-by-step sampling backend (`StepperBackend` in `perceval.backends._stepper`) calling `SLAPBackend` per step.
  - `SLAP`: Sub-linear algebra package backend (`SLAPBackend` in `perceval.backends._slap`).
  - `MPS`: Matrix Product State tensor network backend (`MPSBackend` in `perceval.backends._mps`).
  - `Naive` / `NaiveApprox`: Brute-force permanent evaluation backends (`NaiveBackend`, `NaiveApproxBackend`).
- **Noise modeling (`pcvl.NoiseModel`)**:
  - Constructor parameters: `brightness`, `indistinguishability`, `g2`, `g2_distinguishable`, `transmittance`,
    `phase_imprecision`, `phase_error`.
  - Detectors in Perceval model photon loss via system-wide `transmittance`. Perceval's `NoiseModel` does not
    contain a detector dark count parameter; dark count rates are tracked in hardware performance dictionaries
    rather than simulated natively in the circuit noise model.
- **Cloud integration (`perceval-quandela`)**:
  - Remote execution on physical QPUs (`qpu:ascella`, `qpu:belenos`) or cloud simulators (`sim:ascella`) is mediated
    by `QuandelaCommunicationLayer` (`perceval.providers.quandela.quandela_communication_layer`), which subclasses
    `RPCBasedCommunicationLayer`.
  - Transport uses standard HTTP REST via `requests` with Bearer token authentication and JSON RPC serialization;
    there is no standalone `quandela-cloud-client` package and no WebSocket connection.

### 4.3 Error Mitigation Suite
Perceval provides client-side error mitigation managed via `perceval.runtime.error_mitigation.MitigationFactory`.
The factory defines a standard, recommended mitigation ordering via `MitigationFactory.MITIGATION_ORDER` (though the runtime `Computer.mitigations` accepts and preserves caller-specified orderings):
1. `CompilationAveraging`: Transpiles the target unitary into multiple equivalent MZI mesh configurations
   (using different random transpilation seeds) and averages over hardware phase errors and directional coupler imbalances.
2. `DistinguishablePhotonMitigation`: Expands and inverts the distinguishing mixture matrix arising from finite HOM visibility
   ($V_{\text{HOM}} < 1$) up to a specified photon-count expansion order.
3. `PhotonRecycling`: Re-bins and recovers events with missing photons where partial detection patterns retain projective information.
4. `DetectorBalancing`: Normalizes measured coincidence frequencies by inverse channel detection efficiencies and spatial mode transmission disparities.

---

## 5. Comprehensive Bibliographic Catalog and Reading Guide

The following works constitute the primary literature corpus for Quandela, Ascella, Belenos, and linear optical
quantum computing, verified against Crossref, DataCite, and repository holdings:

### 5.1 Foundational Textbooks and Monographs
1. **Kok, P., & Lovett, B. W.** (2010). *Introduction to Optical Quantum Information Processing*. Cambridge University Press. ISBN: 978-0-521-51914-4. DOI: 10.1017/CBO9781139193658.
   - *Core reference for linear optical quantum information, Fock space algebra, HOM interference, beam splitter unitary representations, and KLM gate implementations.*
2. **Gerry, C. C., & Knight, P. L.** (2005). *Introductory Quantum Optics*. Cambridge University Press. ISBN: 978-0-521-52735-4. DOI: 10.1017/CBO9780511791239.
   - *Foundational treatment of electromagnetic field quantization, creation/annihilation operators, single-photon states, and optical interferometers.*
3. **Bachor, H.-A., & Ralph, T. C.** (2019). *A Guide to Experiments in Quantum Optics* (3rd ed.). Wiley-VCH. ISBN: 978-3-527-41193-1. DOI: 10.1002/9783527695805.
   - *Practical laboratory guide to photodetectors, SNSPDs, quantum noise, homodyne and direct photon counting.*
4. **Michler, P. (Ed.)** (2017). *Quantum Dots for Quantum Information Technologies*. Springer. ISBN: 978-3-319-56378-7. DOI: 10.1007/978-3-319-56378-7.
   - *Covers cavity QED, DBR micropillar fabrication, Purcell enhancement, and solid-state single-photon generation.*
5. **Nielsen, M. A., & Chuang, I. L.** (2000). *Quantum Computation and Quantum Information*. Cambridge University Press. ISBN: 978-0-521-63503-5.
   - *Standard reference for quantum circuits, process tomography, distance measures, and quantum error correction (the 2000 edition is held in the workspace).*

### 5.2 Foundational Linear Optical Quantum Computing & Boson Sampling
6. **Hong, C. K., Ou, Z. Y., & Mandel, L.** (1987). "Measurement of subpicosecond time intervals between two photons by interference". *Phys. Rev. Lett.* 59, 2044-2046. DOI: 10.1103/PhysRevLett.59.2044.
   - *The seminal discovery of two-photon destructive interference on a beam splitter.*
7. **Reck, M., Zeilinger, A., Bernstein, H. J., & Bertani, P.** (1994). "Experimental realization of any discrete unitary operator". *Phys. Rev. Lett.* 73, 58-61. DOI: 10.1103/PhysRevLett.73.58.
   - *Proves that any unitary matrix U(m) can be synthesized by a triangular mesh of beam splitters and phase shifters.*
8. **Knill, E., Laflamme, R., & Milburn, G. J.** (2001). "A scheme for efficient quantum computation with linear optics". *Nature* 409, 46-52. DOI: 10.1038/35051009.
   - *The KLM theorem proving universal quantum computing using linear optics, single photons, and projective measurement.*
9. **Kok, P., Munro, W. J., Nemoto, K., Ralph, T. C., Dowling, J. P., & Milburn, G. J.** (2007). "Linear optical quantum computing with photonic qubits". *Rev. Mod. Phys.* 79, 135-174. DOI: 10.1103/RevModPhys.79.135. arXiv: quant-ph/0512071.
   - *Comprehensive review of discrete-variable optical quantum computing, dual-rail qubits, and entangling gate architectures.*
10. **Aaronson, S., & Arkhipov, A.** (2013). "The computational complexity of linear optics". *Theory of Computing* 9, 143-252. DOI: 10.4086/toc.2013.v009a004. arXiv: 1011.3245.
    - *Formal formulation of Boson Sampling and the classical hardness of simulating linear optical circuits.*
11. **Clements, W. R., Humphreys, P. C., Metcalf, B. J., Kolthammer, W. S., & Walmsley, I. A.** (2016). "Optimal design for universal multiport interferometers". *Optica* 3, 1460-1465. DOI: 10.1364/OPTICA.3.001460. arXiv: 1603.08788.
    - *The rectangular mesh architecture that balances optical depth and equalizes loss across modes.*
12. **Clifford, P., & Clifford, R.** (2018). "The classical complexity of Boson Sampling". *SODA 2018*, pp. 146-155. arXiv: 1706.01260.
    - *Introduces the classical sampling algorithm implemented in Perceval's CliffordClifford2017 backend.*

### 5.3 Semiconductor Quantum-Dot Sources (The Senellart / C2N / Quandela Lineage)
13. **Somaschi, N., et al.** (2016). "Near-optimal single-photon sources in the solid state". *Nature Photonics* 10, 340-345. DOI: 10.1038/nphoton.2016.23. arXiv: 1510.06499.
    - *Seminal demonstration of cavity-enhanced InGaAs QD micropillars achieving indistinguishability > 99% and high extraction efficiency.*
14. **Giesz, V., et al.** (2016). "Coherent manipulation of a solid-state artificial atom with few photons". *Nature Communications* 7, 11986. DOI: 10.1038/ncomms11986.
    - *Demonstrates coherent control and non-linear optical interaction in micropillar-coupled quantum dots (see also their two-photon interference paper, Phys. Rev. B 92, 161302(R), 2015).*
15. **Senellart, P., Solomon, G., & White, A.** (2017). "High-performance semiconductor quantum-dot single-photon sources". *Nature Nanotechnology* 12, 1026-1039. DOI: 10.1038/nnano.2017.218.
    - *Definitive review of quantum dot microcavity single-photon generation, dephasing mechanisms, and device design.*
16. **Ollivier, H., et al.** (2020). "Reproducibility of high-performance quantum dot single-photon sources". *ACS Photonics* 7, 1050-1059. DOI: 10.1021/acsphotonics.9b01805. arXiv: 1910.08863.
    - *Industrial reproducibility and stability study of deterministic micropillar sources feeding Quandela processors.*
17. **Thomas, S. E., et al.** (2021). "Bright Polarized Single-Photon Source Based on a Linear Dipole". *Phys. Rev. Lett.* 126, 233601. DOI: 10.1103/PhysRevLett.126.233601.
    - *Primary reference for Ascella's optical excitation scheme (Maring et al. ref 26): near-resonant excitation assisted by longitudinal-acoustic (LA) phonons, achieving high photon purity and indistinguishability without cross-polarization filtering losses.*

### 5.4 Ascella & Belenos Platform Publications
18. **Maring, N., et al.** (2024). "A versatile single-photon-based quantum computing platform". *Nature Photonics* 18, 603-609. DOI: 10.1038/s41566-024-01403-4. arXiv: 2306.00874.
    - *The core peer-reviewed paper detailing Quandela's Ascella hardware architecture, cloud accessibility, 12-mode chip, and error mitigation.*
19. **Pont, M., et al.** (2022). "Quantifying n-photon indistinguishability with a cyclic integrated interferometer". *Phys. Rev. X* 12, 031033. DOI: 10.1103/PhysRevX.12.031033. arXiv: 2201.13333.
    - *Establishes genuine multi-photon indistinguishability benchmarks for Quandela's optical processors.*
20. **Pont, M., et al.** (2022). "High-fidelity generation of four-photon GHZ states on-chip". arXiv: 2211.15626.
    - *Source of Ascella's demultiplexer architecture: an active optical demultiplexer generating a spatial train of synchronized single photons from a high-repetition-rate single-photon source.*
21. **Taballione, C., et al.** (2021). "A universal fully reconfigurable 12-mode quantum photonic processor". *Mater. Quantum Technol.* 1, 035002. DOI: 10.1088/2633-4356/ac12b4.
    - *The 12-mode stoichiometric silicon nitride (Si3N4 TriPlex) processor chip used in Ascella (Maring et al. ref 28; see also Taballione et al. 2022, arXiv:2203.01801, for the 20-mode scaling benchmark).*
22. **Mezher, R., & Mansfield, S.** (2022). "Assessing the quality of near-term photonic quantum devices". arXiv: 2202.04735.
    - *Quandela diagnostic framework assessing state preparation, circuit fidelity, and non-classicality under experimental imperfections.*
23. **Tzitrin, I., et al.** (2021). "Fault-tolerant quantum computation with static linear optics". *PRX Quantum* 2, 040353. DOI: 10.1103/PRXQuantum.2.040353.
    - *Theoretical architecture for fault-tolerant linear optical quantum computing via continuous-variable and dual-rail cluster states.*
24. **Barzaghi, M., et al.** (2025). "A low-loss, 24-mode laser-written universal photonic processor in a glass-based platform". arXiv: 2505.01609.
    - *Detailed physical and optical characterization of the Belenos 24-mode glass chip.*
25. **Thomas, H., Chabaud, U., & Emeriau, P.-E.** (2025). "Shedding light on classical shadows: learning photonic quantum states". arXiv: 2510.07240.
    - *Hardware execution of randomized Clifford measurements and classical shadows on Quandela 12- and 24-mode processors.*
26. **Franco, S., Camillini, A., & Galvão, E. F.** (2026). "Interaction-free measurement of multiple objects using a universal integrated photonic processor". *Quantum Sci. Technol.* DOI: 10.1088/2058-9565/ae8df9. arXiv: 2604.04691.
    - *Experimental execution of quantum interrogation and interaction-free measurement protocols on the cloud-accessible Ascella QPU.*
27. **Quandela** (2026). "Technology Roadmap and Platform Scaling (2026-03)".
    - *Hardware scaling trajectories, error correction integration, and quantum networking partnerships (detailed in `docs/notes/quandela/roadmap-2026-03.md`).*

### 5.5 Perceval Software Stack, Transpilation, and Algorithms
28. **Heurtel, N., et al.** (2023). "Perceval: A Software Platform for Discrete Variable Photonic Quantum Computing". *Quantum* 7, 931. DOI: 10.22331/q-2023-02-21-931. arXiv: 2204.00602.
    - *The core software paper introducing Perceval, exqalibur, SLOS, circuit composition, and simulation backends.*
29. **Fyrillas, A., Faure, O., Maring, N., Senellart, J., & Belabas, N.** (2024). "Scalable machine learning-assisted clear-box characterization for optimally controlled photonic circuits". *Optica* 11(3), 427-436. DOI: 10.1364/OPTICA.512148. arXiv: 2310.15349.
    - *Physical forward-model characterization and parameter fitting ($\hat{\boldsymbol{\phi}} = A \mathbf{V}^{\odot 2} + \mathbf{b}$ for thermal crosstalk and static phases) using classical machine learning, explicitly contrasted with black-box neural networks.*
30. **Fyrillas, A., et al.** (2024). "Certified Randomness in Tight Space". *PRX Quantum* 5, 020348. DOI: 10.1103/PRXQuantum.5.020348. arXiv: 2301.03536.
    - *Device-independent certified randomness protocols executed natively on photonic quantum processors.*
31. **Fyrillas, A., et al.** (2025). "Resource-efficient crosstalk mitigation for the high-fidelity operation of photonic integrated circuits with induced phase shifters". arXiv: 2506.05988.
    - *Demonstrates compensation of thermal crosstalk across universal multiport interferometers by adding virtual control degrees of freedom.*
32. **Tully, E., Washburn, J., & Simons, M.** (2026). "Characterization of nested Walsh parity-check filters in a single-photon eight-mode register on a cloud photonic processor". arXiv: 2606.18408.
    - *Hardware characterization of nested Walsh parity-check filters on an eight-mode single-photon register executed on Quandela Belenos.*

### 5.6 Permanent Computation and Estimation
33. **Gurvits, L.** (2005). "On the complexity of mixed discriminants and related problems". *MFCS 2005*, Lecture Notes in Computer Science 3618, pp. 447-458. DOI: 10.1007/11549345_39.
    - *Randomized additive approximation of the permanent within $\pm\varepsilon\lVert A\rVert^n$ from $O(1/\varepsilon^2)$ samples of Glynn's $\pm 1$ estimator; exqalibur's `estimate_permanent_cx`.*
34. **Glynn, D. G.** (2010). "The permanent of a square matrix". *European Journal of Combinatorics* 31, 1887-1891. DOI: 10.1016/j.ejc.2010.01.010.
    - *The $\pm 1$ sign-vector formula behind exqalibur's exact `ptype="glynn"` and the Gurvits estimator.*
35. **Aaronson, S., & Hance, T.** (2014). "Generalizing and derandomizing Gurvits's approximation algorithm for the permanent". *Quantum Information and Computation* 14, 541-559. DOI: 10.26421/QIC14.7-8-1. arXiv: 1212.0025.
    - *Extends the additive estimator to other matrix functions and gives a deterministic variant.*
