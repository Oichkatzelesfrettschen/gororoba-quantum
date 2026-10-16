> Full piece: [https://www.quantum-inspire.com/backends/qx-simulator/](https://www.quantum-inspire.com/backends/qx-simulator/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 ab70ee6042a2453ff7e3f50dd79c5fc1712e506e016acee84723ccef6da93b76.

# QX Quantum Computer Simulator

![](https://www.datocms-assets.com/119587/1530867781-qx-logo.jpg)

# QX Quantum Computer Simulator

Quantum Inspire offers a powerful quantum computer simulator backend based on the QX Simulator. QX simulator is a simulator of cQASM programs, developed by QuTech. At the moment, QX simulator only supports cQASM v3.0 programs (see cQASM-spec for the language specification). It performs simulations of input programs received via file or string. It produces one of the following results: A simulation result: a quantum state and, optionally, a list of measurements. An error. In case of an invalid input program or failed simulation. It can be used as: A standalone executable (built from C++), from the command line. A module (called qxelarator), from Python projects (as a Python package).

[QX simulator documentation](https://qutech-delft.github.io/qx-simulator/latest/)

[Questions? Contact an expert](mailto:richard.versluis@tno.nl)

![](https://www.datocms-assets.com/119587/1586252831-spin-2uspsemiconductorgrad.svg)

## Large number of qubits

Simulating quantum states requires a lot of memory. On our commodity server you cabn simulate up to 26 qubits.

![](https://www.datocms-assets.com/119587/1586250730-startmon-5uspfastgrad.svg)

## Fast

QX emulator is a state of the art simulator written in C++ and using OpenMP for multi-core, multi node simulations. Depending on the type of user account job durations could be maximized to 30 minutes compute time.

![](https://www.datocms-assets.com/119587/1586250729-startmon-5uspextensible-architecturegrad.svg)

## Open source

QX is an open source project developed at the Quantum Engineering lab at TU Delft under Apache2.0 license. Feel free to contribute!

> “In this age of quantum chips with low numbers of noisy qubits, powerful emulators are essential to test use cases but also to set requirements for system developments.”
>
> ![](https://www.datocms-assets.com/119587/1585819003-20181016copyrightmariekedelorijn4003d.jpg?auto=quality&auto=compress&w=80))
>
> #### Richard Versluis
>
> Principal Systems Engineer Quantum Inspire

## System overview

At the heart of our QX simulator are three powerful supercomputer instances supporting the simulations of up to 26 qubits. We provide a rich gate set that you can use to write efficient code to simulate both error-corrected quantum algorithms and more recent variational quantum algorithms proposed for pre-error corrected NISQ devices.

- ![](https://www.datocms-assets.com/119587/1586164747-applicationcolor.svg)
  ### Programming language

  ### cQASM

  
  cQASM is a hardware-agnostic quantum assembly language developed at QuTech. It guarantees interoperability between all quantum compilation and simulation tools. Using the QI online editor you can write your quantum algorithm in cQASM and run it using our QX simulator on several available supercomputers.
- ![](https://www.datocms-assets.com/119587/1586258730-spin-2.svg)
  ### Simulating quantum circuits

  ### Gate set and operations

  
  The cQASM instruction set was designed with particular care to include the user experiences and expectations from different parts of the quantum community. We provide a rich gate set and measurement utilities that can be used to describe error-corrected quantum algorithms as well as the recent variational quantum algorithms and sampling tasks proposed for pre-error corrected NISQ devices.
- ![](https://www.datocms-assets.com/119587/1586164750-electronicscolor.svg)
  ### Noisy quantum systems

  ### Error models

  
  By default, the QX Simulator executes the circuits using perfect qubits and perfect gates, i.e. without any noise or decoherence. However real-world qubit implementations suffer from decoherence and circuits are realised using imperfect gates introducing “noisy” operations. The QX Emulator currently implements one error model: the symmetric depolarising channel. Other methods such as the Pauli-twirling approximation and more powerfull error simulation methods will be developed.\
- ![](https://www.datocms-assets.com/119587/1586164750-languagecolor.svg)
  ### Future developments

  ### Contributing to QX

  
  QX has been developed at the Quantum Engineering Lab at TU Delft. The [QCE github repository](https://github.com/QE-Lab) holds the source code of the QX simulator and other usefull software such as

  - [libQASM: A library to parse cQASM files](https://github.com/QE-Lab/libqasm)
  - [QX-simulator: The QX Simulator itself](https://github.com/QE-Lab/qx-simulator)
  - [OpenQL : A Portable Quantum Programming Framework for Quantum](https://github.com/QE-Lab/OpenQL)
  - [cQASM-Spec: Repository for collaborating on the cQASM (2.0) spec ](https://github.com/QE-Lab/cQASM-spec)
- ![](https://www.datocms-assets.com/119587/1586164748-compilercolor.svg)
  ### Emulator back-end types

  ### Select your best fit

  
  Quantum Inspire now offers just one instance of the QX Emulator hosted on a commodity cloud-based server, which can simulate 26 qubits.

## QX - Emulator backend

QX is our emulator backend for fast and powerfull emulaton of quantum algorithms. We are in the process of upgrading our QX emulator, providing you with different paradigms for simulating quantum circuits, using a larger set of error models and a wider range of functionality to get the most out of your simulations. Contact us if you want to contribute to this.

## Become a partner of QuTech

One of Europe's largest research and innovation initiatives bringing together scientists and engineers from academia and industry, as well as future users of Quantum Technologies.

[Contact our team](mailto:c.j.m.eijkel@tudelft.nl,%20richard.versluis@tno.nl?subject=Quantum%20Inspire%20web%20form)
