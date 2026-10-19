> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.StarQPU.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.StarQPU.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 02e947ab342cf771282dc6f640202f1182cbaab756c47dd326dd2c194df94d60.

# StarQPU

Module: [`iqm.qaoa.transpiler.quantum_hardware`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html#module-iqm.qaoa.transpiler.quantum_hardware "iqm.qaoa.transpiler.quantum_hardware")

*class* iqm.qaoa.transpiler.quantum_hardware.StarQPU(*n*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L521-L535)  
Bases: [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")

A star-shaped QPU (Daneb, Sirius, …).

Importantly, the central resonator always has label 0 in the QPU graph. This is used in circuits built on the star.

Parameters:  
**n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of the spokes of the star graph, so that the graph as a whole has `n+1` vertices, including the central vertex.

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.quantum_hardware.StarQPU](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-fe99fa4a032c34244f02e8126bdd51a109f86f19.png)
