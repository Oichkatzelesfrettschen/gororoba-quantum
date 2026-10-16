> Full piece: [https://www.quantum-inspire.com/about-qi/](https://www.quantum-inspire.com/about-qi/)
> Retrieved 2026-10-16T22:10Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 167d35f112da45186af9ea8fdce71e3fdb6b7343b28a0104a50e854b9b4a511d.

# About QI

## What is Quantum Inspire

Quantum Inspire (QI) is a quantum computing platform designed and built by QuTech. The goal of Quantum Inspire is to provide users access to various technologies to perform quantum computations and insights in principles of quantum computing and access to the community.

Quantum Inspire (QI) is initiated by [QuTech](https://www.qutech.nl/) the advanced research center for quantum computing and quantum internet founded by [TU Delft](https://www.tudelft.nl/en/) and [TNO](https://www.tno.nl/en/focus-areas/industry/).

![Quantum Inspire](https://www.datocms-assets.com/119587/1529922403-qi-editor-soft.png)

Quantum Inspire

## Quantum algorithms

Quantum Inspire provides users a variety of ways to program quantum algorithms, execute these algorithms and examine the results. It provides a graphical interface to program in [QASM (Quantum Assembly Language)](https://www.quantum-inspire.com/kbase/cqasm) and to visualize operations in circuit diagrams. With the QI Editor non-quantum experts can learn writing quantum algorithms with support of automatic bug identification and auto complete. Our [Quick Quide](https://www.quantum-inspire.com/kbase/quick-guide) will help you to make your first steps into the fascinating world of quantum computation.

```cqasm
version 3.0

// Implementation of Deutsch algorithm with two qubits for f(x)=x

qubit[2] q
bit[2] b

X q[1]
H q[0]
H q[1]
CNOT q[0],q[1]
H q[0]

b[0] = measure q[0]
```

The output of a quantum algorithm can be examined using our built-in data viewer. Users can also download the output of quantum algorithms.

![Cartesius supercomputer at SurfSara](https://www.datocms-assets.com/119587/1529922393-cartesius00.jpg)

Cartesius supercomputer at SurfSara

We at QuTech strongly believe that only through close collaboration with external partners will it be possible to further accelerate the development and engineering in the field of quantum computing and to bring this technology to higher levels of Technology Readiness (TRL). If your company or institute is interested in investigating ways of cooperation to advance this exciting and challenging technology, you are more than welcome to [contact us](https://www.quantum-inspire.com/contact).

[Play![](https://www.quantum-inspire.com/icons/play.svg)](https://vimeo.com/324171082)

[Quantum Inspire: An Interface for the Computer of the Future](https://vimeo.com/324171082)
