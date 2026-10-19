> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.ReadoutMapping.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.ReadoutMapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 74db80be3e29b8a9ff6437627519fa759e139fd1ca36f67ee25bc4ebf446f42e.

# ReadoutMapping

iqm.cpc.interface.circuit_execution.ReadoutMapping  
Type for matching measurement keys from a quantum circuit with acquisition labels in Station Control.

In quantum circuits, measurements are identified by measurement keys. Measurements in Station Control are identified by acquisition labels. This type is a dictionary mapping measurement keys to lists of acquisition labels — each acquisition label should hold the readout of a single qubit at a single point in the circuit, and the order in the list corresponds to the order of qubits in the measurement instruction. E.g. if one has measurement instruction with `key='mk'` and `qubits=[QB2, QB1]`, then the corresponding entry in this dict would be `'mk': ('QB2__mk', 'QB1__mk')`

The values of the ReadoutMapping are used to determine which measurement results Station Control should return.

alias of [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`tuple`](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]
