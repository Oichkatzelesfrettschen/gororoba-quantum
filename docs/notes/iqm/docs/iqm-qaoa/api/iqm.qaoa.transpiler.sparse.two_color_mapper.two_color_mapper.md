> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 056200eee3ca7a95965e56b33d87fa6dc6bc81395215d3346ebd243810541fbb.

# two_color_mapper

iqm.qaoa.transpiler.sparse.two_color_mapper.two_color_mapper(*problem_bqm*, *qpu*, *color_sets*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sparse/two_color_mapper.py#L270-L325)  
Finds an initial mapping between logical and hardware qubits.

The mapping is constructed so that almost all interactions of two colors of an edge coloring of the problem graph can be executed in the first two layers of the phase separator. It uses an internal function to find a (near-)optimal coloring of the problem graph, take the subgraph induced by the two largest colors and decompose the subgraph into chains and loops. The loops are then broken down into chains and all these small chains are then placed onto a big chain embedded along the `qpu`.

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The `BinaryQuadraticModel` representation of the problem.

- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – The QPU, an object of the [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU") class (or any of its subclasses).

- **color_sets** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.LogEdge')\],* [*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.LogEdge')\]\]*) – The two sets of edges (of the problem graph) colored by two selected colors. This is necessary for the initial placement of the problem qubits onto the hardware qubits.

Returns:  
The initial mapping (as [`Mapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping")) and a list of two lists of [`LogEdge`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogEdge.html#iqm.qaoa.transpiler.quantum_hardware.LogEdge "iqm.qaoa.transpiler.quantum_hardware.LogEdge") interactions that can be implemented in the first two layers of the routing algorithm.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Mapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[TypeAliasForwardRef(‘~iqm.qaoa.transpiler.quantum_hardware.HardEdge’)\]\]\]
