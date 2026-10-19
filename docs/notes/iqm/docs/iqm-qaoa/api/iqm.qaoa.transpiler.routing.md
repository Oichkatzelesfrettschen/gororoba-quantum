> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 08c69e8b6692dca0d6c784214f0790a1f7506e96547974465132b09444f8baaa.

# routing

Full path: iqm.qaoa.transpiler.routing

Module containing the main object classes used throughout any routing algorithm.

Specififally, there is [`Mapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping"), which keeps track of the mapping between the logical and the hardware qubits. There is [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") used to construct and save the routing of the phase separator of the QAOA. The routing is saved as a list of layers, [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer").

Classes

|  |  |
|----|----|
| [`BaseMapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseMapping.html#iqm.qaoa.transpiler.routing.BaseMapping "iqm.qaoa.transpiler.routing.BaseMapping") | The base class for various mappings used in routing of QAOA circuits on the QPU. |
| [`BaseRouting`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseRouting.html#iqm.qaoa.transpiler.routing.BaseRouting "iqm.qaoa.transpiler.routing.BaseRouting") | The abstract base class for various routing sub-classes. |
| [`CircuitSynthesis`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.CircuitSynthesis.html#iqm.qaoa.transpiler.routing.CircuitSynthesis "iqm.qaoa.transpiler.routing.CircuitSynthesis") | Synthesize a quantum circuit using parity-based interaction mapping. |
| [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") | A class describing one layer of the QAOA phase separator, consisting of swap and interaction gates. |
| [`Mapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") | Mapping between logical and hardware qubits. |
| [`ParityMapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.ParityMapping.html#iqm.qaoa.transpiler.routing.ParityMapping "iqm.qaoa.transpiler.routing.ParityMapping") | Maps hardware qubits to sets of logical qubits representing parities. |
| [`Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") | The 'standard' routing of a QAOA phase separator. |

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-1f96a228d8ef7d38b49063964c62b0e976bd788a.png)
