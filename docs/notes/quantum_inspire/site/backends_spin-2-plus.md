> Full piece: [https://www.quantum-inspire.com/backends/spin-2-plus/](https://www.quantum-inspire.com/backends/spin-2-plus/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 5492dd7c9aba557b16ca4409cbc04381ee4eac61b7b397c01c201f966852e913.

# Spin-2+

![](https://www.datocms-assets.com/119587/1739459051-spin-2-plus-large-border.svg)

# Spin-2

The Spin-2+ quantum processor has 6 quantum dots and 2 sensing dots. It uses the left three dots, with two dots hosting single electron spin data qubits, and one dot with three qubits ased as ancilla to perform PSB readout. It combines high-fidelity operations with long coherence time. Its nanoscale size and compatibility with standard semiconductor technology makes it ideal for future scaling to large numbers of qubits. Spin-2+ is an upgrade of Spin-2, with single-qubit (X90) fidelity improved from 99,0% to 99,8%, two-qubit (CZ) fidelity improved from 90,0% to 95,5%. More technical details about our system and the QPU (inlcuding a fact sheet with perfomance benchmarks) can be found in the sections below.

[Click here for the Life Performance Monitor](https://monitoring.qutech.support/public-dashboards/0d4f32302c0d4e88aa951268a1882f6d?orgId=1)

[Questions? Contact an expert](mailto:richard.versluis@tno.nl?subject=Quantum%20Inspire%20Spin-2+)

![](https://www.datocms-assets.com/119587/1586250728-spin-2uspnanosizegrad.svg)

## Nanosize - scalability

The small feature size of the qubits makes it an excellent candidate for scaling to large numbers of qubits. Using standard wafers and standard dies, a typical pitch of ~50 nm allows for millions or billions of qubits in one chip.

![](https://www.datocms-assets.com/119587/1586250727-spin-2usplong-coherence-timegrad.svg)

## Long coherence time

The use of 28-Si quantum wells on a Si/SiGe wafer yields a stable environment for long-lived qubits, with T2\* times well over 5 microseconds and T1 times over 200 ms. Even at higher temperatures of a few Kelvin, the coherence times are hardly affected.

![](https://www.datocms-assets.com/119587/1586252831-spin-2uspsemiconductorgrad.svg)

## CMOS compatibility

Design and fabrication is based on standard CMOS prefab processes for growth, litho, etching, cleaning etc, enabling mass-production in standard fabs. This also opens up integration with classical digital electronics in the same chip.

> "Quantum Inspire, a new European success story in quantum computing that will complement our efforts in the Quantum Flagship. Its availability via the cloud will help public and private users start to become familiar with advanced quantum technologies, and to develop promising applications in the field."
>
> ![](https://www.datocms-assets.com/119587/1586512997-tsk2picture25feb16.jpg?auto=quality&auto=compress&w=80))
>
> #### Thomas Skordas
>
> Director of DG Connect Digital Excellence and Science Infrastructure Directorate

## System overview

At the heart of our Spin-2+ QPU lies a solid-state quantum processor made of Isotopically purified Si-28. hosting 6 quantum dots. Three spin qubits offer arbitrary singe-qubit rotations and two-qubit gates. Qubit operations are performed with room-temperature analog and digital control systems programmed using a high-level language and compiler. Extensibility to larger qubit systems is a key feature in the design of every layer of this full stack.

- ![](https://www.datocms-assets.com/119587/1586164747-applicationcolor.svg)
  ### Tuning and calibration

  ### Automated Tuning

  
  To ensure the correct functioning of the quantum processing devices, they need to be calibrated. For this purpose in-house software was developed, that performs automated full calibration of the system taking between 5 and 30 minutes, as required by the state of the system. An example of a parameter to be calibrated is the Pauli X gate, which consists of a single microwave pulse. To achieve good fidelity, the duration and power of this pulse need to be calibrated. For even higher fidelities more parameters such as the pulse shape, or gate latencies need to be determined.
- ![](https://www.datocms-assets.com/119587/1586164750-languagecolor.svg)
  ### OpenSquirrel

  ### High Level Compiler

  
  Although yet small in number of qubits, Spin-2+ can execute arbitrary single-qubit rotations and standard two-qubit operations, creating a universal gate set for various quantum algorithms. Our high level compiler \[OpenSquirrel\](https://qutech-delft.github.io/OpenSquirrel/index.html) translates these gates to the native operations of the chip, which are single-qubit rotations around any axis in the XY-plane and the CZ-gate.

  Single-qubit operations are converted to one or two rotations in the XY-plane com ined with virtual rotations around the z-axis. Two-qubit operations are converted into combinations of CZ-gates and single-qubit rotations using standard decompositions.

  OpenSquirrel,is a flexible quantum program compiler. OpenSquirrel chooses a *modular*, over a *configurable*, approach to prepare and optimize quantum circuits for heterogeneous target architectures. It has a user-friendly interface and is straightforwardly extensible with custom-made readers, compiler passes, and exporters. As a quantum circuit compiler, it is fully aware of the semantics of each gate and arbitrary quantum gates can be constructed manually. It understands the quantum programming language \[cQASM 3\](https://qutech-delft.github.io/cQASM-spec/latest/) and will support additional quantum programming languages in the future. It is developed in modern Python and follows best practices.
- ![](https://www.datocms-assets.com/119587/1586164748-compilercolor.svg)
  ### Low level compiler

  ### Low Level Compiler

  
  Micro-instructions for the Spin-2 quantum processor are generated using [QuPulse](https://github.com/qutech/qupulse) and an in-house developed device specific low-level compiler. It contains a library of generic experiment implementations that are required for autonomously keeping the system calibrated. These experiments consist of a measurement part and an analysis part (to retrieve system parameters from the measurement result). The system parameters are stored in a run-time database that contains all the information needed for executing calibrated quantum algorithms.

  A calibration framework provides the configurable logic to organize the calibration experiments. It needs to balance the conflicting demands of requiring minimal system time versus ensuring maximal quantum performance. In general the strategy is to do quick measurements to check if calibration parameters are still valid and to only execute long experiments for parameters that require recalibration. In practice this can become quite complex due to dependencies between experiments and discontinuous changes in device characteristics. The configurable logic allows to tailor this process for each specific device. For the Spin-2+ system this ensures that it remains calibrated without human intervention for \>24h.
- ![](https://www.datocms-assets.com/119587/1586164750-electronicscolor.svg)
  ### Classical to quantum

  ### Control Electronics

  
  The PCB with QPU is placed inside a dilution fridge, cooling down the sample to approximately 200 mK.  Room Temperature control electronics and electronics inside the fridge (mainly for signal attenuation and filtering) is used to create the DC, AC and MW signals required to control and readout the qubits. Low Level Software (LLS) is used to convert the quantum instructions into micro-instructions for the hardware and to allow for accurate calibration and tuning of the system.

   The QPU is wire-bonded to a PCB. This PCB, mounted on the cold finger of the fridge, is the interface between the fridge wiring carrying all control signals) and the QPU.

   The room temperature control hardware consists of:

  - Stable DACs to create a DC landscape to confine quantum dots
  - AWGs to tune the DC landscape to steer quantum dots and to create the I/Q signals for up-converting
  - Readout modules to initialize and readout the qubits

  Microwave source, mixing I/Q signals with a Local Oscillator (LO) signal to create the MW signals for qubit driving.
- ![](https://www.datocms-assets.com/119587/1586258730-spin-2.svg)
  ### Spin-2

  ### Quantum Processor

  
  The Spin-2+ QPU developed at QuTech is based on a six-qubit device using electron spins in silicon, of which three are used. Two of them are the data qubits allowing for arbitrary single-qubit rotations and two-qubit gates. The remaining qubit is the ancilla qubit allowing for Pauli spin blockade (PSB)-readout via an additional single-electron-transistor charge sensor nearby. The six qubits are hosted in an electrostatically defined linear array of six quantum dots realized in low-disorder, isotopically purified ²⁸Si/SiGe heterostructures. Single and two-qubit gates are implemented by applying microwave and DC pulses to the electrodes which electrostatically define the quantum dots and a micromagnet which enables electric-dipole spin resonance and individual addressing of the qubits. \

  **Material:** ²⁸Si quantum dots in SiGe\
  **Single-qubit control:** EDSR microwave pulsing\
  **Two-qubit control:** Exchange interaction\
  **Read-out:** Pauli spin blockade via aditioanl SET transistor.

  [**Download Factsheet**](https://www.datocms-assets.com/119587/1738752183-4-technical-fact-sheet-quantum-inspire-spin-2-plus.pdf)

  [**Life monitor of performance**](https://monitoring.qutech.support/public-dashboards/0d4f32302c0d4e88aa951268a1882f6d?orgId=1)

## Spin-2+ back-end

Spin-2+ is our next-generation (Gen-) back-end based on semiconducting quantum hardware. Next development steps will be to increase the qubit count, improve the operational fidelities and improve on the control hardware to make more powerfull processors with a larger range of possibilities.

## Become a partner of QuTech

One of Europe's largest research and innovation initiatives bringing together scientists and engineers from academia and industry, as well as future users of Quantum Technologies.

[Contact our team](mailto:c.j.m.eijkel@tudelft.nl,%20richard.versluis@tno.nl?subject=Quantum%20Inspire%20web%20form)
