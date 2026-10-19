> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 aad1873dd1331401a6e9bd72872481e56a38695466b70a9c70f7a750961ee3df.

# iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager

iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager(*connectivity: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *effort: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 100*, *depth_weight: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *ignore_nodes: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *ignore_edges: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *seed: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → PassManager  
Create a `PassManager` pre-configured for IQM transpilation.

This pass applies the full transpilation pipeline including: - Layout and routing (SABRE-based) - SWAP optimization - Gate conversions (to CZ + PRX) - Gate cancellation and optimization

Parameters:  
- **connectivity** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The connectivity describing the device topology.

- **effort** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) – Effort level for layout and routing. Default is 100.

- **depth_weight** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* *optional*) –

  Tradeoff between gate count and circuit depth (-1.0 to 1.0).

  - `-1`: Circuit optimized purely for swap count.

  - `0` (default): Balanced.

  - `+1`: Circuit optimized purely for circuit depth.

- **ignore_nodes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* *optional*) – Qubit indices to ignore (e.g., faulty qubits). Ignored nodes are removed from the effective connectivity via `shift_graph_edges()` so that layout and routing never place logical qubits on them.

- **ignore_edges** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\],* *optional*) – Edges to ignore in the connectivity. Like *ignore_nodes*, these are stripped from the effective topology before the passes are configured.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) –

  Random seed forwarded to both the layout and the routing pass, which use it to draw candidate layouts and to break ties while routing.

  Both passes re-seed on every invocation, so the returned PassManager is reproducible: running it repeatedly on the same circuit yields the same transpiled circuit. Pass a different `seed` to explore a different set of candidates.

Returns:  
A configured PassManager with all IQM transpilation passes. Call `pm.run(qc)` to apply all passes to a circuit.

Return type:  
PassManager

Examples

```
>>> from qrisp import QuantumCircuit
>>> from iqm.qrisp_iqm import create_iqm_pass_manager
>>> qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1); qc.measure(qc.qubits)
>>> connectivity = [(0, 1), (1, 2), (2, 3)]
>>> pm = create_iqm_pass_manager(connectivity)
>>> transpiled_qc = pm.run(qc)
```

Excluding a faulty qubit:

```
>>> pm = create_iqm_pass_manager(
...     connectivity, ignore_nodes=[2]
... )
>>> transpiled_qc = pm.run(circuit)
```
