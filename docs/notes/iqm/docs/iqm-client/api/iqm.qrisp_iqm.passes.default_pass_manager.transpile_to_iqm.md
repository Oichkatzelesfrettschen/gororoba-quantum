> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a681ad26315777709e232b236ef0b7be048035c349350bf0dc5aea912730893f.

# iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm

iqm.qrisp_iqm.passes.default_pass_manager.transpile_to_iqm(*qc: QuantumCircuit*, *connectivity: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *ignore_nodes: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *ignore_edges: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *effort: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 100*, *depth_weight: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*, *\**, *seed: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → QuantumCircuit  
Transpile a Qrisp QuantumCircuit for execution on IQM hardware.

This function applies the full transpilation pipeline including: - Layout and routing (SABRE-based) - SWAP optimization - Gate conversions (to CZ + PRX) - Gate cancellation and optimization

Internally delegates to [`create_iqm_pass_manager()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager.html#iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager "iqm.qrisp_iqm.passes.default_pass_manager.create_iqm_pass_manager") and applies the resulting `PassManager` to the circuit.

Parameters:  
- **qc** (*QuantumCircuit*) – The Qrisp QuantumCircuit to transpile.

- **connectivity** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The connectivity describing the device topology.

- **ignore_nodes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* *optional*) – Qubit indices to ignore (e.g., faulty qubits).

- **ignore_edges** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\],* *optional*) – Edges to ignore in the connectivity.

- **effort** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) – Effort level for layout and routing. Default is 100.

- **depth_weight** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* *optional*) –

  Tradeoff between gate count and circuit depth (-1.0 to 1.0).

  - `-1`: Circuit optimized purely for swap count.

  - `0` (default): Balanced.

  - `+1`: Circuit optimized purely for circuit depth.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) – Random seed forwarded to the layout and routing passes. This makes the transpilation reproducible: repeated calls with the same arguments return the same circuit.

Returns:  
The transpiled circuit suitable for IQM hardware.

Return type:  
QuantumCircuit

Raises:  
[**Exception**](https://docs.python.org/3.11/library/exceptions.html#Exception "(in Python v3.11)") – If the circuit has more qubits than the device.

Examples

``` python
from qrisp import QuantumCircuit
from iqm.qrisp_iqm import transpile_to_iqm

# Circuit with a non-adjacent CX gate
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 2)
qc.measure(range(3))

# Transpile for a 4-qubit line topology
connectivity = [(0, 1), (1, 2), (2, 3)]
result = transpile_to_iqm(qc, connectivity)

print(result)
```

```
              ┌──────────────┐   ┌─┐
       qb_58: ┤ U3(π/2,-π,π) ├─■─┤M├──────────────────
              ├──────────────┤ │ └╥┘┌─────────────┐┌─┐
       qb_60: ┤ U3(π/2,-π,π) ├─■──╫─┤ U3(π/2,0,0) ├┤M├
              └──────────────┘    ║ └─────┬─┬─────┘└╥┘
       qb_59: ────────────────────╫───────┤M├───────╫─
                                  ║       └╥┘       ║
padding_qb_0: ────────────────────╫────────╫────────╫─
                                  ║        ║        ║
        cb_3: ════════════════════╩════════╩════════╩═
```

The non-adjacent CX(0,2) is decomposed and routed onto the line topology, resulting in a mixture of CZ and native U3 gates.
