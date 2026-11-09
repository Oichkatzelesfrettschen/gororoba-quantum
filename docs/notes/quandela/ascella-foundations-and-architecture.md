# Ascella Architecture, Foundational Axioms, and Photonic Quantum Stack

This document synthesizes the physical first principles, mathematical axioms, hardware architecture, and
software stack governing Quandela's **Ascella** quantum processing unit (`qpu:ascella`), its historical lineage,
and its Python development ecosystem (`perceval-quandela`, `exqalibur`, `quandela-cloud-client`). It establishes
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
  collapses to its third level.

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
|  [Pulsed Laser 79 MHz]                                                                  |
|         | (pi-pulse @ 925 nm)                                                           |
|         v                                                                               |
|  +------------------------+                                                             |
|  | InGaAs/GaAs QD Cavity  |  --> Repetition rate: 79 MHz                                |
|  | DBR Micropillar (C2N)  |  --> Single-photon purity: 1 - g^(2)(0) >= 98.1%             |
|  | Cryostat @ 4 Kelvin    |  --> Indistinguishability: V_HOM approx 87.5%               |
|  +------------------------+                                                             |
|         |                                                                               |
|         v (Sequential single-photon train)                                              |
|  +------------------------+                                                             |
|  | 1-to-6 Electro-Optic   |  --> Demultiplexing clock: 13.33 MHz                        |
|  | Active Demultiplexer   |  --> Routes photons to input modes 0, 2, 4, 6, 8, 10        |
|  +------------------------+                                                             |
|         | | | | | | (6 spatial optical fibers)                                          |
|         v v v v v v                                                                     |
|  +-----------------------------------------------------------------------------------+  |
|  |               12-MODE RECONFIGURABLE INTEGRATED PHOTONIC CHIP                     |  |
|  |                                                                                   |  |
|  |  - 12 Waveguide spatial modes (dielectric waveguide platform)                      |  |
|  |  - 132 Rx directional couplers (theta in [1.4204, 1.4739] rad)                    |  |
|  |  - 126 Thermo-optic microheater phase shifters (phi in [0, 2pi))                  |  |
|  |  - Machine-learning transpilation (thermal diffusion & crosstalk correction)      |  |
|  +-----------------------------------------------------------------------------------+  |
|         | | | | | | | | | | | | (12 output spatial modes)                               |
|         v v v v v v v v v v v v                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |              SUPERCONDUCTING NANOWIRE DETECTORS (SNSPDs @ < 2.5 K)                |  |
|  |                                                                                   |  |
|  |  - 12 Threshold single-photon counting channels                                   |  |
|  |  - Total system transmittance: ~ 5.2%                                             |  |
|  |  - Coincidence time-tagging unit (FPGA time-to-digital converter)                 |  |
|  +-----------------------------------------------------------------------------------+  |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

### 3.1 Quantum Dot Microcavity Single-Photon Source
- **Emmiter material**: Self-assembled Indium Gallium Arsenide (InGaAs) quantum dot embedded at the antinode of a
  GaAs/AlAs distributed Bragg reflector (DBR) micropillar microcavity.
- **Purcell enhancement**: Strong cavity-QED coupling creates a Purcell factor $F_P > 10$, shortening radiative
  lifetime to $T_1 \approx 150\text{ ps}$ and overcoming environmental acoustic phonon dephasing ($T_2^*$).
- **Excitation**: Resonant pulsed optical $\pi$-pulse excitation ($\sim 79\text{ MHz}$ repetition rate, central
  wavelength $\lambda \approx 925\text{--}930\text{ nm}$).
- **Performance parameters**:
  - Raw indistinguishability: $V_{\text{HOM}} \approx 87.5\%$.
  - Multiphoton suppression: $g^{(2)}(0) \le 0.019$ (purity $> 98.1\%$).
  - Extraction efficiency into single-mode fiber: $> 50\%$.

### 3.2 Active Electro-Optic Demultiplexer
Because photons are emitted sequentially by a single quantum dot, Ascella uses an active, low-loss, fast
spatial-temporal demultiplexing network:
- Takes a burst of 6 consecutive optical pulses from the 79 MHz stream.
- Re-routes each pulse into one of 6 physical fibers with matched optical path delay lines.
- Injects 6 synchronized photons into the physical input ports: modes **0, 2, 4, 6, 8, 10**.
- Effective master clock rate: $79\text{ MHz} / 6 = 13.33\text{ MHz}$.

### 3.3 12-Mode Programmable Photonic Chip
- **Interferometer size**: 12 optical waveguide modes.
- **Component count**: 132 directional couplers (calibrated $R_x$ splitters, nominal $\theta \approx 1.42\text{--}1.47\text{ rad}$)
  and 126 thermo-optic phase shifters ($\phi$).
- **Heater control and thermal diffusion**: Local thermal microheaters adjust the effective refractive index
  via $\Delta n \propto \Delta T$. Because heat diffuses into neighboring waveguides, thermal crosstalk is modeled
  and inverted using clear-box machine learning transpilation (Fyrillas et al. 2023, 2025).

### 3.4 Detection and Readout
- **Detector technology**: 12 cryogenic Superconducting Nanowire Single-Photon Detectors (SNSPDs) operating at
  temperatures below $2.5\text{ K}$.
- **Detection characteristics**:
  - Detection efficiency: $> 85\%$.
  - Dark count rate: typically $< 100\text{ Hz}$ across most ports; maximum port 10 reads $1428\text{--}1885\text{ counts/s}$.
  - System end-to-end transmittance: $\sim 5.25\%$.
  - Readout type: Threshold detection (presence of $\ge 1$ photon recorded as a click). Coincidence events are
    registered by hardware time-correlators with sub-nanosecond coincidence windows.

---

## 4. The Quandela Python Software Stack

Quandela's software architecture separates high-level algorithmic description from compiled high-performance
simulation and cloud execution:

```
                      +-----------------------------+
                      |   User Application / Qiskit |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |       Perceval 1.3.1        |
                      | (pcvl.Circuit, Processor,   |
                      |   State, Source, Noise)     |
                      +-----------------------------+
                        /                         \
                       / (C++ extension)           \ (REST / WebSockets)
                      v                             v
+-------------------------------+      +---------------------------------+
|       exqalibur 1.4.2         |      |     quandela-cloud-client       |
|  - SLOS permanent engine      |      |  - Authentication & token mgmt  |
|  - Clifford & Clifford sampler|      |  - Job serialization & dispatch |
|  - Clements/Reck transpiler   |      |  - QPU / Sim telemetry polling  |
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
`exqalibur` provides optimized Man-in-the-Middle primitives for linear optics:
- **Matrix permanents**: Evaluated using Gray-code implementations of Glynn's formula and Ryser's algorithm,
  enabling exact evaluation of state transition amplitudes.
- **Clifford & Clifford (2018) sampler**: Polynomial-time exact/approximate sampling from $n$-photon $m$-mode
  states without explicitly calculating all exponential state vectors.
- **Circuit transpilation**: Factoring arbitrary matrices $U \in U(m)$ into elementary beam splitter and phase
  shifter parameter schedules.

### 4.2 `perceval` Core Library
- **State management**:
  ```python
  import perceval as pcvl
  # 2 photons in modes 0 and 2 of a 12-mode processor
  input_state = pcvl.State([1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
  ```
- **Circuit composition**:
  ```python
  circuit = pcvl.Circuit(12)
  circuit.add(0, pcvl.BS())          # Beam splitter on modes 0 and 1
  circuit.add(0, pcvl.PS(phi=0.785)) # Phase shift on mode 0
  ```
- **Processor backends**:
  - `SLOSBackend`: Strong simulation computing the full probability distribution.
  - `CliffordClifford2017Backend`: Fast sampling for multi-photon states.
  - `NaiveBackend`: Brute-force permanent evaluation.
  - `StepperBackend`: Mode-by-mode state transformation.

### 4.3 Error Mitigation Suite
Quandela Cloud incorporates four native error mitigation layers:
1. `PhotonRecycling`: Re-bins events with missing photons where losses permit recovery of partial states.
2. `CompilationAveraging`: Transpiles the target unitary into multiple equivalent MZI mesh configurations
   (different random transpilation seeds) and averages over hardware imperfections.
3. `DistinguishablePhoton`: Models and inverts the known $V_{\text{HOM}}$ distinguishing mixture.
4. `DetectorBalancing`: Scales measured click frequencies by inverse channel detection efficiencies.

---

## 5. Comprehensive Bibliographic Catalog and Reading Guide

The following works constitute the essential literature corpus for Quandela, Ascella, and linear optical
quantum computing:

### 5.1 Foundational Textbooks and Monographs
1. **Kok, P., & Lovett, B. W.** (2010). *Introduction to Optical Quantum Information Processing*. Cambridge University Press.
   - *Core reference for linear optical quantum information, Fock space algebra, HOM interference, beam splitter unitary representations, and KLM gate implementations.*
2. **Gerry, C. C., & Knight, P. L.** (2005). *Introductory Quantum Optics*. Cambridge University Press.
   - *Foundational treatment of electromagnetic field quantization, creation/annihilation operators, single-photon states, and optical interferometers.*
3. **Bachor, H.-A., & Ralph, T. C.** (2019). *A Guide to Experiments in Quantum Optics* (3rd ed.). Wiley-VCH.
   - *Practical laboratory guide to photodetectors, SNSPDs, quantum noise, homodyne and direct photon counting.*
4. **Michler, P. (Ed.)** (2017). *Quantum Dots for Quantum Information Technologies*. Springer.
   - *Covers cavity QED, DBR micropillar fabrication, Purcell enhancement, and solid-state single-photon generation.*
5. **Nielsen, M. A., & Chuang, I. L.** (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
   - *Standard reference for quantum circuits, process tomography, distance measures, and quantum error correction.*

### 5.2 Foundational Linear Optical Quantum Computing & Boson Sampling
6. **Hong, C. K., Ou, Z. Y., & Mandel, L.** (1987). "Measurement of subpicosecond time intervals between two photons by interference". *Phys. Rev. Lett.* 59, 2044. DOI: 10.1103/PhysRevLett.59.2044.
   - *The seminal discovery of two-photon destructive interference on a beam splitter.*
7. **Reck, M., Zeilinger, A., Bernstein, H. J., & Bertani, P.** (1994). "Experimental realization of any discrete unitary operator". *Phys. Rev. Lett.* 73, 58. DOI: 10.1103/PhysRevLett.73.58.
   - *Proves that any unitary matrix U(m) can be synthesized by a triangular mesh of beam splitters and phase shifters.*
8. **Knill, E., Laflamme, R., & Milburn, G. J.** (2001). "A scheme for efficient quantum computation with linear optics". *Nature* 409, 46-52. DOI: 10.1038/35051009.
   - *The KLM theorem proving universal quantum computing using linear optics, single photons, and projective measurement.*
9. **Kok, P., et al.** (2007). "Linear optical quantum computing with photonic qubits". *Rev. Mod. Phys.* 79, 135-174. DOI: 10.1103/RevModPhys.79.135.
   - *Comprehensive review of discrete-variable optical quantum computing, dual-rail qubits, and entangling gate architectures.*
10. **Aaronson, S., & Arkhipov, A.** (2013). "The computational complexity of linear optics". *Theory of Computing* 9, 143-252. DOI: 10.4086/toc.2013.v009a004.
    - *Formal formulation of Boson Sampling and the classical hardness of simulating linear optical circuits.*
11. **Clements, W. R., Humphreys, P. C., Metcalf, B. J., Kolthammer, W. S., & Walmsley, I. A.** (2016). "Optimal design for universal multiport interferometers". *Optica* 3, 1460-1465. DOI: 10.1364/OPTICA.3.001460.
    - *The rectangular mesh architecture that balances optical depth and equalizes loss across modes.*
12. **Clifford, P., & Clifford, R.** (2018). "The classical complexity of Boson Sampling". *SODA 2018*, pp. 146-155. arXiv: 1708.06992.
    - *Introduces the classical sampling algorithm implemented in Perceval's CliffordClifford2017 backend.*

### 5.3 Semiconductor Quantum-Dot Sources (The Senellart / C2N / Quandela Lineage)
13. **Somaschi, N., et al.** (2016). "Near-optimal single-photon sources in the solid state". *Nature Photonics* 10, 340-345. DOI: 10.1038/nphoton.2016.23.
    - *Seminal demonstration of cavity-enhanced InGaAs QD micropillars achieving indistinguishability > 99% and high extraction efficiency.*
14. **Senellart, P., Solomon, G., & White, A.** (2017). "High-performance semiconductor quantum-dot single-photon sources". *Nature Nanotechnology* 12, 1026-1039. DOI: 10.1038/nnano.2017.218.
    - *Definitive review of quantum dot microcavity single-photon generation, dephasing mechanisms, and device design.*
15. **Giesz, V., et al.** (2015). "Cavity-enhanced stimulated emission in a single quantum dot". *Nature Communications* 6, 7372. DOI: 10.1038/ncomms8372.
    - *Foundation of the optical pumping protocols and cavity coupling implemented in Quandela sources.*
16. **Ollivier, H., et al.** (2020). "Reproducibility of high-indistinguishability single-photon sources". *ACS Photonics* 7, 1050-1059. DOI: 10.1021/acsphotonics.9b01805.
    - *Industrial reproducibility and stability study of deterministic micropillar sources feeding Quandela processors.*

### 5.4 Ascella & Belenos Platform Publications
17. **Maring, N., et al.** (2024). "A versatile single-photon-based quantum computing platform". *Nature Photonics* 18, 603-609. DOI: 10.1038/s41566-024-01402-2. arXiv: 2306.00874.
    - *The core peer-reviewed paper detailing Quandela's Ascella hardware architecture, cloud accessibility, 12-mode chip, and error mitigation.*
18. **Pont, M., et al.** (2022). "Quantifying n-photon indistinguishability with a cyclic integrated interferometer". *Phys. Rev. X* 12, 031033. DOI: 10.1103/PhysRevX.12.031033. arXiv: 2201.13328.
    - *Establishes genuine multi-photon indistinguishability benchmarks for Quandela's optical processors.*
19. **Fyrillas, A., et al.** (2023). "Certified randomness generation on a photonic quantum computer". *Nature Communications* 14, 8436. arXiv: 2304.14880.
    - *Device-independent protocols executed natively on Quandela QPUs.*
20. **Mezher, R., et al.** (2023). "Fault-tolerant quantum computation with static linear optics". arXiv: 2307.03732.
    - *Quandela theoretical roadmap for scalable fault tolerance using fixed linear optical networks and cluster state fusion.*
21. **Barzaghi, M., et al.** (2025). "Reconfigurable 24-mode universal integrated interferometer in femtosecond-laser-written glass". arXiv: 2505.01609.
    - *Detailed physical and optical characterization of the Belenos 24-mode glass chip.*
22. **Thomas, S., et al.** (2025). "Efficient estimation of multi-qubit states using classical shadows on a 24-mode photonic processor". arXiv: 2510.07240.
    - *Hardware execution of randomized Clifford measurements and classical shadows on Quandela Belenos.*

### 5.5 Perceval Software Stack, Transpilation, and Algorithms
23. **Heurtel, N., et al.** (2023). "Perceval: A Software Platform for Discrete Variable Photonic Quantum Computing". *Quantum* 7, 931. DOI: 10.22331/q-2023-02-21-931. arXiv: 2204.00602.
    - *The core software paper introducing Perceval, exqalibur, SLOS, circuit composition, and simulation backends.*
24. **Fyrillas, A., et al.** (2023). "Clear-box machine-learned compilation for reconfigurable photonic circuits". arXiv: 2310.15349.
    - *Neural-network-assisted transpilation mitigating thermal crosstalk and phase offset errors in Quandela MZI meshes.*
25. **Fyrillas, A., et al.** (2025). "Induced phase shifters and gauge symmetries in universal multiport interferometers". arXiv: 2506.05988.
    - *Characterizes unobservable phase gauges and parasitic phase shifts in integrated MZI arrays.*
26. **Bourdoncle, B., et al.** (2023). "Simulating discrete-variable photonic quantum computing with Perceval". *Proc. SPIE* 12518, 125180J.
    - *Applications of Perceval to variational quantum algorithms, quantum chemistry, and optical state engineering.*
27. **Tully, J., et al.** (2026). "Dynamical decoupling and Walsh filter mitigation on photonic quantum processors". arXiv: 2606.18408.
    - *Thermal drift and low-frequency noise suppression protocols implemented on Quandela hardware.*
