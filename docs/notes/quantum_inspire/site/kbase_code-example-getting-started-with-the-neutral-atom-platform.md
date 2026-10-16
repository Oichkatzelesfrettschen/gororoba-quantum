> Full piece: [https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform/](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 9c7a238b666ee244f34ab1bf74826e633b44298edd4d7e0a730a282b6396ebc7.

# Code example: Getting started with the neutral atom platform

This page contains some background and basic code examples that apply to the Rydberg Emulator backend on Quantum Inspire, that utilizes neutral atom quantum computing technology.

## Rydberg Physics

In a neutral atom computer, qubits are encoded in specific energy levels of neutral atoms such as rubidium or strontium, atoms which are well-known for their operation in atomic clocks. The atoms are trapped and held in arrays using focused laser beams, so-called optical tweezers. An atom can act as a qubit when just one single atom is trapped in one optical tweezer. In our quantum computing platform, we choose for these energy levels the two clock states $`\vert 0 \rangle`$ and $`\vert 1 \rangle`$ and a highly excited Rydberg state $`\vert r \rangle`$. Transitions between these energy levels are carried out by control lasers. A strong interaction between single atoms in different tweezers can be realized by exciting them into a Rydberg state by using a control laser tuned to a specific wavelength, while a transition between the two clock states is realized by another control laser tuned to a different wavelength.

If one atom is excited to a Rydberg state, nearby atoms are shifted in energy and cannot be excited to that same Rydberg state due to interaction-induced detuning. This phenomenon is called the *Rydberg blockade*, and as a mechanism it is employed for computation to realize the conditional dynamics needed for logic gate operations. Altogether, the control lasers drive the qubit operations and can be used to realize single-, two- and multi-qubit gate operations. For more detailed information, the reader is directed to review papers about the subject \[1\].

The Rydberg blockade is the main source for generating entanglement and responsible for conditional dynamics and logic operations. The blockade strength depends on the physical range of the atomic qubits, which makes the geometric positions of the atoms an integral part of the design of processes run on a neutral atom quantum computer. This translates to lattice positions of the different qubits that are part of a quantum computing circuit, and a user of a neutral atom platform therefore should have the means to place atoms on a lattice. Our platform supports this functionality via directives passed through assembly blocks. The position of an atom can be specified by the following directive inside an assembly block:

    INIT(0,1) q[0]

This line of code assigns the 0th qubit in register q to position $`x=0`$ and $`y=1`$. Important points about the usage of this directive: The position of an atom can only be given at the beginning of a cQASM file, as a directive inside the assembly block, when no operations on the qubits have been performed.

- After an operation is performed, the user can no longer use this directive to change or specify the position of an atom.
- If the position of atom is not specified at the beginning of a cQASM file, our backend will decide its position.
- If this directive is used after another operation is performed, an appropriate error message will be displayed.

## Basic Circuit

The neutral atom platform has several advantages such as arbitrary connectivity and scalability. One aspect that is interesting and has caught the attention of many researchers is the early notion of the platforms' ability to perform analogue simulations. Here, we use the term analogue in the sense that one can directly manipulate the laser control pulses that are applied to the qubits during the quantum simulation. Scientists have been exploiting this capability to optimize gates and operations in a quantum circuit by directly shaping the pulses. Keeping this knowledge in mind, here we explore a very basic circuit that can be run on the Rydberg emulator backend that uses each distinct aspect of it; hoping to instruct the user on the capabilities of the technology and the emulator without going too far into technical details. This circuit has simply a number of single qubit gates and a global Rydberg gate. Here, a global Rydberg gate corresponds to using the Rydberg laser which utilizes the "Rydberg blockade" mechanism on all the atoms in the array. The quantum circuit is described by a cQASM file. In this part, we discuss the cQASM file and its syntax for the circuit:

Close

## Export visualization

File format SVG PNG

Layout Horizontal Vertical

Theme Light Dark

Download

Export

In line 1 we specify the version of the cQASM language as 3.0. In line 2 we define a quantum register of 2 qubits. In lines 4 to 7 we initialize the positions of the qubits in the register. As mentioned before, the positions of the qubits are important for our calculation as it determines which atoms will be in the blockade range during the quantum process. The position of an atom is specified by `INIT(0,1) q[0]`. This line of code assigns the 0th qubit in register q to position $`x=0`$ and $`y=1`$ in the rectangular lattice shown below.

Image taken from Ref. \[1\].

Note that we used the asm(Rydberg)" directive for the INIT" commands. This directive indicates the following raw string (i.e. the code text that is between triple quotations) is Rydberg platform specific. Currently, there are a total of two directives that need to be used in a specific way: INIT and RYD. The second directive will be explained below. Now our circuit looks like:

In lines 9 and 10 we add single-qubit gates. We use an $`X`$ gate for each qubit that will flip each qubit from $`0`$ to $`1`$. With these single qubit gates our circuit looks like:

Here, we show two versions of the same circuit. On the left, we see the circuit with gate names and on the right, we see the same circuit with pulses drawn for the gates. The next step is to apply the Rydberg pulse. To apply this pulse via the Rydberg gate provided on Quantum Inspire, we first need to discretize it. We take small steps and five values for the parameters: $`\Omega, \Delta`$ and $`DT`$, which are the Rabi frequency, the detuning, and the time duration. For this simple example, we will apply a discretized 10 step pulse but for a realistic application more steps might be needed. A discrete Rydberg pulse command (i.e. one discrete step among many) can be specified using the following line:

    RYD( rabi_freq, detuning, dt )

When using the gate, parameters must be changed to actual values that are normalized to our reference Rabi frequency, which is $`1.0`$ in dimensionless units. With the Rydberg pulses, our circuit looks like the picture below.

Finally, we end with two X gates on both qubits and we are done. The circuit doesn't need measurement gates as measurement is implied at the end of every circuit for each qubit.

\[1\] M. Saffman, “Quantum computing with atomic qubits and rydberg inter- actions: progress and challenges,” Journal of Physics B: Atomic, Molecular and Optical Physics, vol. 49, p. 202001, oct 2016.

[Previous](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-transmons/) [Next](https://www.quantum-inspire.com/kbase/code-example-the-maximum-independent-set/)
