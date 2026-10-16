> Full piece: [https://www.quantum-inspire.com/kbase/what-is-a-qubit/](https://www.quantum-inspire.com/kbase/what-is-a-qubit/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 d2dda935202300a5db8f95c78f87a48c86297be644aa028f6db623c23d08cb65.

# What is a qubit?

## Qubit

A qubit (or quantum bit) is the quantum mechanical analogue of a classical bit. In classical computing the information is encoded in bits, where each bit can have the value zero or one. In quantum computing the information is encoded in qubits. A qubit is a two-level quantum system where the two basis qubit states are usually written as $`\left\lvert 0 \right\rangle`$ and $`\left\lvert 1 \right\rangle`$. A qubit can be in state $`\left\lvert 0 \right\rangle`$, $`\left\lvert 1 \right\rangle`$ or (unlike a classical bit) in a linear combination of both states. The name of this phenomenon is [superposition](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/).

A general -pure- qubit state is expressed as: $`\vert \psi \rangle =\alpha \vert 0\rangle + \beta \vert 1\rangle`$

where $`\alpha`$ and $`\beta`$ are the complex probability amplitudes for each basis state. Note that the choice of basis states is arbitrary, each set of orthogonal states can be used as basis states.

Below it is shown that a general pure qubit state is described by two real numbers, while above we stated that a generic qubit state is described by two complex parameters (probability amplitudes). This apparent contradiction is solved by the following: First of all, the sum of the probabilities of measuring any of the states should always add to 1. This condition constraints the description already to three real parameters. Another aspect from quantum mechanics is that scaling of a qubit state by a scaling vector does not change the measureable properties (observables) of a quantum state. This means that all probability amplitudes can always be scaled by an arbitrary (real) factor without changing any of the observable properties of the system. This is also known as scaling by a global phase factor. This condition constraints the system to a state which can be defined by two real parameters.

This video from the [QuTech Academy](https://qutech.nl/academy/) explains some basic qubit properties.

[Play![](https://www.quantum-inspire.com/icons/play.svg)](https://www.youtube.com/watch?v=5hNlpAxv3Gw&feature=youtu.be)

[QTM1x_2018_08-Qubit-video](https://www.youtube.com/watch?v=5hNlpAxv3Gw&feature=youtu.be)

## Single-qubit computational basis states

The two orthogonal z-basis states of a qubit are defined as:

- $`\vert 0\rangle`$
- $`\vert 1\rangle`$

*When we talk about the qubit basis states we implicitly refer to the z-basis states as the computational basis states.*

The two orthogonal x-basis states are:

``` math
\vert +\rangle =\frac{\vert 0\rangle + \vert 1\rangle}{\sqrt{2}}
\,\,\,\,\vert -\rangle =\frac{\vert 0\rangle - \vert 1\rangle}{\sqrt{2}}
```

The two orthogonal y-basis states are:

``` math
\vert +i\rangle =\frac{\vert 0\rangle + \imath \vert 1\rangle}{\sqrt{2}}
\,\,\,\,\vert -i\rangle =\frac{\vert 0\rangle - \imath \vert 1\rangle}{\sqrt{2}}
```

The basis states are located at opposite points on the Bloch sphere. Note that a pure qubit state can be expressed as a point on the surface of the Bloch sphere and therefore can be described by two angles. In general, the polar angle θ (theta) (angle with respect to positive z-axis), and azimuthal angle φ (phi) (counter-clock wise angle of rotation in the xy-plane from the positive x-axis) are used in quantum physics.

For more information see <https://en.wikipedia.org/wiki/Bloch_sphere>.

![Bloch sphere](https://www.datocms-assets.com/119587/1685537272-bloch-sphere-states.png)

Bloch sphere

Below an interactive plot of the Bloch sphere is shown of a state with $`\theta = 0.2`$ and $`\phi = 0.4`$. Just click and hold the Bloch sphere to view it from different angles.

Theta (θ)  
0.2

Phi (φ)  
0.4

## Qubit technologies

Several different physical implementations of qubits are possible. A number of examples are the polarizations of a photon, two of the (multiple) discrete energy levels of an ion, a superconducting Transmon qubit, the nuclear spin states of an atom or the spin states of an electron. Quantum Inspire is designed to control different qubit technologies. Its modular design allows it to re-use components that are technology independent while replacing components (software and hardware) that are technology dependent.

![False colored SEM picture of Spin-2+ Quantum Processor](https://www.datocms-assets.com/119587/1738707203-6d2s.png)

False colored SEM picture of Spin-2+ Quantum Processor

![Impression of a transmon qubit](https://www.datocms-assets.com/119587/1534340874-transmon-bultink.png)

Impression of a transmon qubit

> QM is in daily use and extremely successful in understanding, predicting and computing observed phenomena - Van Kampen

[Previous](https://www.quantum-inspire.com/kbase/introduction-to-quantum-computing/) [Next](https://www.quantum-inspire.com/kbase/superposition-and-entanglement/)
