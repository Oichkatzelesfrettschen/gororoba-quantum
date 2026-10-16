> Full piece: [https://www.quantum-inspire.com/kbase/binary-register/](https://www.quantum-inspire.com/kbase/binary-register/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 c0d1b324a69b1c07653fd6d42f5ab4d7be3c5e9b2a21aebb697851b8e4c4a9ec.

# Bit register

Ubnlike in Quantum Inspire 1.0, where bit registers were directly linked to qubit registers, Quantum Inspire 2.0 offers to define multiple bit registers. This allows you to assign the results of measurements to any bit register you like, thus providing for instance a method to store intermediate measurement results, if a backend supports this ([see operational specifics of backends](https://www.quantum-inspire.com/kbase/hardware-backends/)).

The bit registers are used to store the outcomes of qubit measurements, the so-called [declared states](https://www.quantum-inspire.com/kbase/qubit-basis-states/#declared-states). Declared states are always 0 or 1. The bit register is often referred to as the measurement register.

All entries in the bit register are initialized to zero.

Just like with the qubit register, the individual bit registers are concatened to a full bit register using the order fo declaration of the bit registers.

The measurement register is displayed as a binary string, following the convention that the least significant bit is the rightmost bit and the most significant bit is the leftmost bit. In practice, this means that the measurement result of qubit 0 is shown as the right-most bit. The measurement result of qubit 3 is shown as the third bit from the right.

Let's take a look at an important exmaple:

Close

## Export visualization

File format SVG PNG

Layout Horizontal Vertical

Theme Light Dark

Download

Export

which results in a histogram similar to this one (for a large number of shots):

0.490

00

0.510

11

1.0

0.8

0.6

0.4

0.2

0.0

Although this may look like the two qubits are entangled, just like in a [Bell state](https://www.quantum-inspire.com/kbase/bell-states/) this is not the case. Here we only put the first qubit in a superposition and measured it twice. We did not measure the seond qubit.

Because the first measurement will collapse the qubit state, the second measurements will give the same result as the first measurement.

Measurements can be done in various bases (z-basis, y-basis or x-basis). The correspondence between basis states and declared states is given in [qubit basis states](https://www.quantum-inspire.com/kbase/qubit-basis-states/).

[Previous](https://www.quantum-inspire.com/kbase/qubit-register/) [Next](https://www.quantum-inspire.com/kbase/qubit-basis-states/)
