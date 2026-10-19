> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LineQPU.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LineQPU.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d75b68765e66ecbb2164a97aea16ee5e064c75c212333216fd7d6da86e406ce6.

# LineQPU

Module: [`iqm.qaoa.transpiler.quantum_hardware`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html#module-iqm.qaoa.transpiler.quantum_hardware "iqm.qaoa.transpiler.quantum_hardware")

*class* iqm.qaoa.transpiler.quantum_hardware.LineQPU(*length*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L494-L518)  
Bases: [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")

A linear QPU (qubits on a line).

Nothing fancy here, just a special case of a qubit hardware connectivity graph, which is a line. Given a `length`, creates a path `hardware_graph` and the corresponding `hardware_layout` which are then passed to [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU") class initialization.

Parameters:  
**length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The length of the QPU (as number of qubits).

Attributes

Methods

|  |  |
|----|----|
| [`embedded_chain`](#iqm.qaoa.transpiler.quantum_hardware.LineQPU.embedded_chain "iqm.qaoa.transpiler.quantum_hardware.LineQPU.embedded_chain") | Embeds a chain in the line QPU (which is just a line). |

embedded_chain()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L511-L518)  
Embeds a chain in the line QPU (which is just a line).

Yields:  
Integer index of the next qubit in the chain.

Return type:  
[*Iterator*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterator "(in Python v3.11)")\[TypeAliasForwardRef(‘~iqm.qaoa.transpiler.quantum_hardware.HardQubit’)\]

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.quantum_hardware.LineQPU](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-a075b642330c49e154154cc361e5bb43a77b9a45.png)
