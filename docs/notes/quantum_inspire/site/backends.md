> Full piece: [https://www.quantum-inspire.com/backends/](https://www.quantum-inspire.com/backends/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 53b1723afde0909013262a606e42c02307e330c99f04ea335d118e177c9c382b.

# Chip Overview

# Execute your algorithms on various hardware chips

We have multiple simulators and real hardware chips available. Find out below what they can do for you or get started and register for immediate access.

[Questions? Contact an expert](mailto:support@quantum-inspire.com)

### Quantum Inspire is powered by

- ![TU Delft - logo](https://www.datocms-assets.com/119587/1585561913-logotu-delft.svg)
- ![QuTech - logo](https://www.datocms-assets.com/119587/1585561911-logoqutech.svg)
- ![TNO - logo](https://www.datocms-assets.com/119587/1585561912-logotno.svg)

## Multiple superconducting backends

We offer multiple transmon-based processors with fixed and tunable qubit-qubit couplers

[Overview of superconducting backends](https://www.quantum-inspire.com/backends/transmons/)

## Spin-2+ performance specs (taken offline)

We are working on a new Spin qubit processor. You can download the performance spec of our previous Spin-2+ processor.

[Performance fact sheet Spin-2+](https://www.datocms-assets.com/119587/1738752183-4-technical-fact-sheet-quantum-inspire-spin-2-plus.pdf)

## New : Rydberg emulator

Meet our brand new TU Eindhoven Rydberg emulator

[Rydberg neutral atom emulator](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/)

## Available quantum processors

### Transmons New

We offer multiple transmon-based quantum computing systems: Currently, these are Tuna-5, Tuna-9 and Tuna-17. Tuna-5 has 5 transmons in a starfish configuration with 4 flux-tunable qubit couplers. Tuna-9 has 9 transmons in a diamond configuration with 12 flux-tunable qubit couplers. Tuna-17 has 17 transmons in a ninja-star configuration with 24 flux-tunable qubit couplers.

- ![](https://www.datocms-assets.com/119587/1586265605-startmon-5uspconnectivity.svg) High qubit connectivity
- ![](https://www.datocms-assets.com/119587/1586265606-startmon-5uspfast.svg) Fast two-qubit gates
- ![](https://www.datocms-assets.com/119587/1586265606-startmon-5uspextensible-architecture.svg) Extensible architecture

[Learn more](https://www.quantum-inspire.com/backends/transmons/)

### Spin-2+ (taken offline)

Our Spin-2+ QPU is an upgrade of Spin-2. This device uses a linear array of six quantum dots. Spin-2+ utilizes the left three dots to define one ancilla qubit in dot 1 and two data qubits in dots 2 and 3. The readout of the two data qubits is enabled via the ancilla qubit, based on spin-blockade relying on Pauli exclusion. This device has been taken offline in order to suppport the development of new Spin quantum processors.

- ![](https://www.datocms-assets.com/119587/1586265604-spin-2uspnanosize.svg) Nanosize - scalability
- ![](https://www.datocms-assets.com/119587/1586265603-spin-2usplong-coherence-time.svg) Long coherence time
- ![](https://www.datocms-assets.com/119587/1586265602-spin-2uspextensible-architecture.svg) Semiconductor compatibility

[Learn more](https://www.quantum-inspire.com/backends/spin-2-plus/)

## Available emulators

### QX-Emulator

#### 26-qubit

### Ry emulator

#### Rydberg neutral atom emulator

[Learn more about the QX emulator](https://www.quantum-inspire.com/backends/qx-simulator/)

## Full-stack quantum computer

Quantum Inspire is built using first-rate engineering practices. Starting from experimental set-ups, a layered and modular system was designed to end up with a solid and robust hardware system. This quantum computer consists of a number of layers including quantum chip hardware, classical control electronics, a quantum compiler and a software front-end with a cloud-accessible web-interface. Such a system is called a full-stack. Full-stack systems are essential testbeds for understanding this novel computational paradigm. They can act as technology accelerators because only through careful analysis of the individual system layers and their interdependencies it becomes possible to detect the gaps and necessary next steps in the innovation roadmap and supply chain.

- ![](https://www.datocms-assets.com/119587/1586164747-applicationcolor.svg)
  ### Web portal and user interaction

  ### Quantum Inspire

  
  Quantum Inspire's user experience comes with a web portal with an intuitive editor for novice users and a software development kit (SDK) to program algorithms, execute these algorithms and examine the results in various ways. Account management, job and result management is available for all registered users. You can execute your algorithms on one of our quantum processors, Spin-2 and Starmon-7, or on our QX simulator. [This short animation explains the journey of the quantum algorithm through Quantum Inspire.](https://youtu.be/wdIea5uGMW0)
- ![](https://www.datocms-assets.com/119587/1586164750-languagecolor.svg)
  ### cQASM and SDK

  ### Programming language

  
  The programming language of Quantum Inspire is [cQASM](https://arxiv.org/abs/1805.09607), developed by the [Quantum & Computer Engineering group at TU Delft](https://www.tudelft.nl/ewi/onderzoek/quantum-computing/ "QCE"). cQASM algorithms can be programmed using the QI online editor or using the [Quantum Inspire SDK](https://github.com/QuTech-Delft/quantuminspire).  The SDK makes it possible to programmatically generate quantum circuits and process the results. This Python layer consists of

  - A Python interface to the [REST API of the Quantum Inspire platform](https://api.quantum-inspire.com/)
  - A backend for the [ProjectQ](https://projectq.ch/) framework
  - A backend for the [QisKit](https://qiskit.org/) framework

  The SDK performs any translation between projectQ or Qiskit and Quantum Inspire. A nice article on how to use the SDK with Qiskit can be found [here](https://medium.com/qiskit/quantum-inspire-and-qiskit-f1be608f8955).
- ![](https://www.datocms-assets.com/119587/1586164748-compilercolor.svg)
  ### OpenQL and projectQ

  ### Transpiler and Compiler

  
  Quantum Inspire uses different modules for the *transpilation* (conversion from one qubit operation to other qubit operations) and *compilation* (conversion from native qubit operations to digital micro-instructions) of qubit operations.

  The following modules are used:

  - [OpenQL](http://openql.org/)
  - [ProjectQ](http://projectq.ch/)
  - Low level device specific compilers (in-house)

  The two systems offer different gate sets for the users. Starmon-7 offers arbitrary singe-qubit rotations and fast two-qubit gates with high fidelity on 7 superconducting qubits. Spin-2 offers arbitrary single-qubit rotations and two-qubit gates on 2 electron spin qubits.
- ![](https://www.datocms-assets.com/119587/1586164750-electronicscolor.svg)
  ### Classical to quantum

  ### Control Electronics

  
  The digital and analog processing steps make use of both commercial electronics as well as in-house electronics developed by TNO and TU Delft, in an engineering feat that delivers the phase and amplitude modulated microwave pulses and voltage steps to execute the required qubit operations whilst synchronised at picosecond timescales. Conventional DC-carrying cables and high frequency transmission lines bring the signals to and from the quantum processor. A central controller orchestrates the interaction between the control signals. Room temperature vector sources, arbitrary wave generators and vector switches are used to generate and steer the required analog signals to perform the qubit operations and readout. The modularity of the system allows for future integration of cryogenic control hardware currently under development [such as Horse Ridge](https://qutech.nl/cryo-chip-overcomes-obstacle-to-large-scale-quantum-computers/), and hardware developed in [Quantum Delft](http://quantumdelft.nl/).
- ![](https://www.datocms-assets.com/119587/1586164749-devicecolor.svg)
  ### Quantum hardware

  ### Quantum processors

  
  As a registered user you have access to mulitple programmable quantum processors and simulators. Currently these are:

  - [**Tuna-17**](https://www.quantum-inspire.com/backends/transmons/): a **17-qubit processor** based on superconducting transmon qubits with 24 flux-tunable qubit couplers;
  - [**Tuna-9**](https://www.quantum-inspire.com/backends/transmons/): a **9-qubit processor** based on superconducting transmon qubits with 12 flux-tunable qubit couplers;
  - [**Tuna-5**](https://www.quantum-inspire.com/backends/transmons/): a **5-qubit processor** based on superconducting transmon qubits with 4 flux-tunable qubit couplers;[](https://www.quantum-inspire.com/backends/transmons/)
  - [**QX emulator**](https://www.quantum-inspire.com/backends/qx-simulator): a programmable quantum computer simulator up to **26 qubits;**
  - **Rydberg emulator.**

  Legacy backends no longer available:

  - [**Starmon-5**](https://www.quantum-inspire.com/backends/transmons/): a **5-qubit processor** based on superconducting transmon qubits with 4 fixed-frequency couplers.
  - [**Starmon-7**](https://www.quantum-inspire.com/backends/transmons/): a **7-qubit processor** based on superconducting transmon qubits with 8 fixed-frequency couplers;
  - [**Spin-2+**](https://www.quantum-inspire.com/backends/spin-2/): a **2-qubit** **processor** based on single electron spin qubits in silicon.
  - [**Spin-2**](https://www.quantum-inspire.com/backends/spin-2/): a **2-qubit** **processor** based on single electron spin qubits in silicon.

## Become a partner of QuTech

One of Europe's largest research and innovation initiatives bringing together scientists and engineers from academia and industry, as well as future users of Quantum Technologies.

[Contact us](mailto:M.Matters@tudelft.nl,%20C.J.M.Eijkel@tudelft.nl)
