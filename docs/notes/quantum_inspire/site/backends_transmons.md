> Full piece: [https://www.quantum-inspire.com/backends/transmons/](https://www.quantum-inspire.com/backends/transmons/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 9f9f21764ce36e8dc5737243445f9e09ae23906e39147112410491e00b30efb4.

# Transmons

![](https://www.datocms-assets.com/119587/1772648307-tuna-17_schematic-svg.svg)

# Tuna-17

The Tuna-17 backend has 17 transmon qubits in a "ninja-star" configuration, with 24 flux-tuneable couplers connecting nearest neighbors. This system is available since April 2026.

[Questions? Contact an expert](mailto:L.DiCarlo@tudelft.nl,%20V.Sinha@tudelft.nl?subject=Quantum%20Inspire%20Tuna-17)

![](https://www.datocms-assets.com/119587/1766393015-tuna-9_schematic.svg)

# Tuna-9

The Tuna-9 backend has 9 transmon qubits in a diamond-like configuration, with 12 flux-tuneable couplers connecting nearest neighbors. This system is available since December 2025.

[Questions? Contact an expert](mailto:L.DiCarlo@tudelft.nl,%20V.Sinha@tudelft.nl?subject=Quantum%20Inspire%20Tuna-9)

![](https://www.datocms-assets.com/119587/1766393003-tuna-5_schematic.svg)

# Tuna-5

The Tuna-5 backend is the prototype demonstrator of the Delft quantum ecosystem working together on open-architecture, full-stack systems within the QDNL HectoQubit/2 and the EU Quantum Flagship OpenSuperQPlus projects. The name of this backend reflects the use of flux-tuneable couplers to connect nearest-neighbor transmons. Specifically, Tuna-5 has 5 transmon qubits in a starfish configuration, with 4 flux-tuneable couplers connecting the central transmon to the 4 corner transmons. This system is available since May 2025.

[Related publication](https://arxiv.org/abs/2503.13225)

[Questions? Contact an expert](mailto:L.DiCarlo@tudelft.nl,%20V.Sinha@tudelft.nl?subject=Quantum%20Inspire%20Tuna-5)

![](https://www.datocms-assets.com/119587/1766432737-starmon-7_schematic.svg)

# Starmon-7 (discontinued)

Starmon-7 was our second-generation superconducting backend. It replaced the original Starmon-5 in February 2025 and was available until December 2025. Starmon-7 had 7 transmons with 8 fixed-frequency qubit couplers connecting nearest neighbors.

[Related publication](https://arxiv.org/abs/2602.18388)

[Questions? Contact an expert](mailto:L.DiCarlo@tudelft.nl,%20V.Sinha@tudelft.nl?subject=Quantum%20Starmon-7)

![](https://www.datocms-assets.com/119587/1586181001-starmon5-border.svg)

# Starmon-5 (discontinued)

Starmon-5 was the very first superconducting backend of Quantum Inspire. It was available from April 2020 to December 2025. Starmon-5 had 5 transmons with 5 fixed-frequency qubit couplers connecting nearest neighbors.

[Related publication](https://arxiv.org/abs/2602.18388)

[Questions? Contact an expert](mailto:L.DiCarlo@tudelft.nl,%20V.Sinha@tudelft.nl?subject=Quantum%20Starmon-5)

![](https://www.datocms-assets.com/119587/1586250728-startmon-5uspconnectivitygrad.svg)

## High qubit connectivity

Qubits couple to their nearest neighbors using a dedicated bus resonator for each pair.

![](https://www.datocms-assets.com/119587/1586250730-startmon-5uspfastgrad.svg)

## Fast two-qubit gates

The flux-pulsing scheme used offers the fastest native conditional-phase gates. Fasten your seat belt!

![](https://www.datocms-assets.com/119587/1586250729-startmon-5uspextensible-architecturegrad.svg)

## Extensible architecture

Our modular stack, from quantum chip through control electronics and software, is extensible to at least 50 qubits.

> “Quantum Inspire put quantum computers online in a time when the rest of Europe was only talking about it. In its second generation, it is a key part of the success of our project OpenSuperQplus”
>
> ![](https://www.datocms-assets.com/119587/1738681695-fwm.jpeg?auto=quality&auto=compress&w=80))
>
> #### Prof. Frank Wilhelm-Mauch
>
> Coordinator of EU Quantum Flagship project OpenSuperQPlus

## System overview transmon backends

The superconducting backends comprise a suite of quantum processors based on circuit quantum electrodyamics: Starmon-7 and Tuna-5/-9/-17. The nickname Starmon for the transmon qubits in these processors reflects their characteristic geometry resulting from a high degree of nearest-neighbor connectivity. The Tuna processors are specially named because they feature flux-tunable qubit couplers rather than fixed-frequency resonators. Qubit operations are performed with room-temperature analog and digital control systems programmed using a high-level language and compiler. Extensibility to higher qubit counts is a key feature in the design of every layer of this full stack.

- ![](https://www.datocms-assets.com/119587/1586164747-applicationcolor.svg)
  ### Algorithm

  ### Quantum Inspire

  
  Quantum Inspire's user experience comes with a web portal with an intuitive editor for novice users and a software development kit (SDK) to program algorithms, execute these algorithms and examine the results in various ways. Account management, job and result management is available for all registered users.
- ![](https://www.datocms-assets.com/119587/1586164750-languagecolor.svg)
  ### Programming language

  ### cQASM and SDK

  
  The programming language of Quantum Inspire platform is cQASM, developed at QuTech. Quantum algorithms can be programmed in cQASM using the QI online editor. The SDK provides an interface between the QI Application Programming Interface (API) and Python-based quantum programming platforms (e.g. QisKit and Pennylane ) and performs any translation between these languages.
- ![](https://www.datocms-assets.com/119587/1586164748-compilercolor.svg)
  ### OpenSquirrel

  ### Compiler

  
  OpenSquirrel is a quantum compiler that chooses a *modular*, over a *configurable*, approach to prepare and optimize quantum circuits for heterogeneous target architectures. It has a user-friendly interface and is straightforwardly extensible with custom-made readers, compiler passes, and exporters. As a quantum circuit compiler, it is fully aware of the semantics of each gate and arbitrary quantum gates can be constructed manually. It supports the [cQASM](https://qutech-delft.github.io/cQASM-spec/latest/) quantum programming language, using [libQASM](https://github.com/QuTech-Delft/libqasm) as a language parser. It is developed in modern Python and follows best practices. The compiler produces intermediate quantum assembly language, a hardware-agnostic representation of a circuit that can be simulated and run directly on quantum hardware. Compilation starts by decomposing quantum operations into physical instructions. Then, the compiler performs optimizations such as merging of single-qubit rotations. After these steps, the compiler analyzes the dependencies of quantum gates and and schedules instructions respecting the duration of gates. For Tuna backends, OpenSquirrel generates a [quantify](https://quantify-os.org/) schedule instructions to the room-temperature control electronics. For the Starmon-7 backend, OpenSquirrel also uses the legacy OpenQL compiler for some backward compatibility issues.
- ![](https://www.datocms-assets.com/119587/1586164750-electronicscolor.svg)
  ### Classical to quantum

  ### Control Electronics

  
  Modularity was a key design feature for the control electronics used in the Tuna and Starmon-7 backends.

  In the Tuna backends, all control and readout signals are generated and acquired at room temperature using a Qblox Cluster that contains one QRM-RF module for readout, three QCM-RF modules for single-qubit gates, and three QCM modules for baseband flux control of transmons and couplers. 

  In the Starmon-7 backend, custom digital and analog control systems were created to shape and time the microwave-frequency and baseband pulses required to perform qubit operations. Room-temperature microwave sources, mixers and arbitrary waveform generators (AWGs) are used to generate and steer the microwave pulses required to perform single-qubit gates and readout. AWGs are also used to generate the baseband signals needed for two-qubit gates. The QuTech Central Controller orchestrates the operation of all these analog instruments.  Signals inputs are sent to the quantum chip via heavily filtered coaxial lines and signal outputs are conditioned using cryogenic superconducting and semiconducting amplifiers.
- ![](https://www.datocms-assets.com/119587/1586164749-devicecolor.svg)
  ### Quantum hardware

  ### Quantum Processor (QPU)

  
  The **Tuna-5** QPU has 5 transmons in a starfish configuration, with 4 dedicated tunable couplers (TCs) connecting the central transmon Q2 to each of the 4 corner ones. Every transmon has a dedicated microwave-drive line and flux-control line, as well as a dedicated pair of readout Purcell-filter resonators for independent readout via one common feedline. Tunable couplers have dedicated flux-control lines. The otherwise planar device, fabricated from a Ta base layer sputtered on a Si substrate, has Al crossovers and airbridges, including ’shoelacing’ airbridges enabling post-fabrication frequency trimming of readout resonator and Purcell filters. This QPU earns its name "Tuna" from the use of flux-tunable qubit couplers. The Tuna-5 processor was fabricated by QuantWare using the Hamiltonian design provided by the DiCarlo lab at QuTech, TU Delft. 

  **Tuna-9** has 9 transmons in a diamond configuration, with 12 dedicated TCs connecting nearest-neighbor transmon pairs. Every transmon has a dedicated microwave-drive line and flux-control line, as well as a dedicated pair of readout Purcell-filter resonators for independent readout using a total of three feedlines. TCs have dedicated flux-control lines. The otherwise planar device, fabricated from a Ta base layer sputtered on a Sapphire substrate, has Al crossovers and airbridges, including ’shoelacing’ airbridges enabling post-fabrication frequency trimming of readout resonator and Purcell filters.  The Tuna-9 QPU was designed and fabricated  by the DiCarlo lab at QuTech, TU Delft. 

  **Tuna-17** has 17 transmons in a ninja-star configuration, with 24 dedicated TCs connecting nearest-neighbor transmon pairs. Every transmon has a dedicated microwave-drive line and flux-control line, as well as a dedicated pair of readout Purcell-filter resonators for independent readout using a total of three feedlines. TCs have dedicated flux-control lines. The otherwise planar device, fabricated from a Ta base layer sputtered on a Sapphire substrate, has Al crossovers and airbridges, including ’shoelacing’ airbridges enabling post-fabrication frequency trimming of readout resonator and Purcell filters.  The Tuna-17 QPU was fabricated  by the DiCarlo lab at QuTech, TU Delft. 

  **Suggested reading:** The very Tuna-5 QPU available here was previously used in the experiment below: 

  S. Vallés-Sanclemente *et al.,* *Optimizing the frequency positioning of tunable couplers in a circuit QED processor to mitigate spectator effects on quantum operations,* Physical Review Letters (in press). Available on [ArXiv](https://arxiv.org/abs/2503.13225).

## Transmon backends

It is our mission to demonstrate the extensibility of our chip and control architectures by upgrading our available superconducting backends with higher qubit counts and expanded capabilities. Since Quantum Inspire launched in April 2020, we have released 5-, 7-, 9- and 17-transmon QPUs!

## Become a partner of QuTech

One of Europe's largest research and innovation initiatives bringing together scientists and engineers from academia and industry, as well as future users of Quantum Technologies.

[Contact our team](mailto:C.J.M.Eijkel@tudelft.nl,%20M.Matters@tudelft.nl?subject=Quantum%20Inspire%20web%20form)
