> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 050ba88af4a687cdba13a6a0d6439987d4d3c1b3105aa27d158589ccfe1f5bb0.

# TranspilerOption

Module: [`iqm.qaoa.circuits`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.html#module-iqm.qaoa.circuits "iqm.qaoa.circuits")

*class* iqm.qaoa.circuits.TranspilerOption(*value*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L60-L74)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

Available transpilation (routing) strategies for QAOA circuits.

Attributes

|  |  |
|----|----|
| [`DEFAULT`](#iqm.qaoa.circuits.TranspilerOption.DEFAULT "iqm.qaoa.circuits.TranspilerOption.DEFAULT") | Use the default Qiskit transpilation. |
| [`HARDWIRED`](#iqm.qaoa.circuits.TranspilerOption.HARDWIRED "iqm.qaoa.circuits.TranspilerOption.HARDWIRED") | Use the 'hardwired_router' transpiler for IQM Crystal backends. |
| [`SPARSE`](#iqm.qaoa.circuits.TranspilerOption.SPARSE "iqm.qaoa.circuits.TranspilerOption.SPARSE") | Use the 'greedy_router' sparse transpiler for IQM Crystal backends. |
| [`SWAP_NETWORK`](#iqm.qaoa.circuits.TranspilerOption.SWAP_NETWORK "iqm.qaoa.circuits.TranspilerOption.SWAP_NETWORK") | Use the 'sn_router' swap network transpiler for IQM Crystal backends. |
| [`MINIMUM_VERTEX_COVER`](#iqm.qaoa.circuits.TranspilerOption.MINIMUM_VERTEX_COVER "iqm.qaoa.circuits.TranspilerOption.MINIMUM_VERTEX_COVER") | Use the minimum vertex cover transpiler for IQM Star backends. |
| [`PARITY_TWINE_NETWORK`](#iqm.qaoa.circuits.TranspilerOption.PARITY_TWINE_NETWORK "iqm.qaoa.circuits.TranspilerOption.PARITY_TWINE_NETWORK") | Use the parity-twine network transpiler for IQM Crystal backends. |

Methods

DEFAULT *= 'Default'*  
Use the default Qiskit transpilation.

HARDWIRED *= 'HardwiredTranspiler'*  
Use the ‘hardwired_router’ transpiler for IQM Crystal backends.

SPARSE *= 'SparseTranspiler'*  
Use the ‘greedy_router’ sparse transpiler for IQM Crystal backends.

SWAP_NETWORK *= 'SwapNetwork'*  
Use the ‘sn_router’ swap network transpiler for IQM Crystal backends.

MINIMUM_VERTEX_COVER *= 'MinimumVertexCover'*  
Use the minimum vertex cover transpiler for IQM Star backends.

PARITY_TWINE_NETWORK *= 'ParityTwineNetwork'*  
Use the parity-twine network transpiler for IQM Crystal backends.

Inheritance

![Inheritance diagram of iqm.qaoa.circuits.TranspilerOption](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-13f92146f214e687014d5400f9018bded71cbcd8.png)
