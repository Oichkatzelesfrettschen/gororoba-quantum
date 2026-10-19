> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fef2e50b3574c7e98535c045a44cae33f03d94f0c5a97368607d283b07417575.

# Layer

Module: [`iqm.qaoa.transpiler.routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html#module-iqm.qaoa.transpiler.routing "iqm.qaoa.transpiler.routing")

*class* iqm.qaoa.transpiler.routing.Layer(*qpu*, *int_gates=None*, *swap_gates=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L222-L386)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A class describing one layer of the QAOA phase separator, consisting of swap and interaction gates.

The class knows about the QPU topology (from `qpu`) and uses it to decide which gates are applicable. A [`Layer`](#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") object contains an internal copy of the QPU graph [`iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph "iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph"), but with edges labelled based on whether an interaction or a swap occurs along that edge in this layer. Similarly, the nodes are labelled based on whether they’re “occupied” in the present layer.

Parameters:  
- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – A `QPU` object, containing the underlying QPU topology.

- **int_gates** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[HardEdge\]* *\|* *None*) – A set of [`HardEdge`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardEdge.html#iqm.qaoa.transpiler.quantum_hardware.HardEdge "iqm.qaoa.transpiler.quantum_hardware.HardEdge") interaction gates to be implemented in the layer. Further interaction gates may be added to the layer by using [`apply_int_gate()`](#iqm.qaoa.transpiler.routing.Layer.apply_int_gate "iqm.qaoa.transpiler.routing.Layer.apply_int_gate").

- **swap_gates** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[HardEdge\]* *\|* *None*) – A set of [`HardEdge`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardEdge.html#iqm.qaoa.transpiler.quantum_hardware.HardEdge "iqm.qaoa.transpiler.quantum_hardware.HardEdge") swap gates to be implemented in the layer. Further swap gates may be added to the layer by using [`apply_swap_gate()`](#iqm.qaoa.transpiler.routing.Layer.apply_swap_gate "iqm.qaoa.transpiler.routing.Layer.apply_swap_gate").

Methods

|  |  |
|----|----|
| [`apply_int_gate`](#iqm.qaoa.transpiler.routing.Layer.apply_int_gate "iqm.qaoa.transpiler.routing.Layer.apply_int_gate") | Apply an interaction gate if it is applicable within the given layer. |
| [`apply_swap_gate`](#iqm.qaoa.transpiler.routing.Layer.apply_swap_gate "iqm.qaoa.transpiler.routing.Layer.apply_swap_gate") | Apply swap gate if it is applicable within the given layer. |
| [`draw`](#iqm.qaoa.transpiler.routing.Layer.draw "iqm.qaoa.transpiler.routing.Layer.draw") | Plot a sketch of the QPU, coloring the physical couplers based on the gate applied. |
| [`int_gate_applicable`](#iqm.qaoa.transpiler.routing.Layer.int_gate_applicable "iqm.qaoa.transpiler.routing.Layer.int_gate_applicable") | True iff the proposed interaction gate can be executed within the given layer. |
| [`swap_gate_applicable`](#iqm.qaoa.transpiler.routing.Layer.swap_gate_applicable "iqm.qaoa.transpiler.routing.Layer.swap_gate_applicable") | True iff the proposed SWAP gate can be executed within the given layer. |

int_gate_applicable(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L264-L288)  
True iff the proposed interaction gate can be executed within the given layer.

Goes through a few checks:

- If the required connection doesn’t exist in the QPU, return `False`.

- If there is already a gate applied between these qubits, and it’s the swap gate, return `True` since the interaction gate can be combined with it. If it’s not a simple swap gate, return `False`.

- Otherwise, check if either of the qubits is involved in other gates and return the outcome of that.

Parameters:  
**gate** (*HardEdge*) – The pair of qubits for which we’re checking the applicability of an interaction gate.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

apply_int_gate(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L290-L306)  
Apply an interaction gate if it is applicable within the given layer.

Parameters:  
**gate** (*HardEdge*) – The pair of qubits between which we apply the interaction gate.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If for whatever reason the interaction gate cannot be applied in this layer.

Return type:  
None

swap_gate_applicable(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L308-L331)  
True iff the proposed SWAP gate can be executed within the given layer.

Goes through a few checks:

- If the required connection doesn’t exist in the QPU, return `False`.

- If there is already a swap gate between these qubits, return `True` (since the new swap gate can cancel it).

- If there is already an interaction gate between these qubits, return `True` (since the swap gate can combine with it).

- Otherwise, check if either of the qubits is involved in other gates.

Parameters:  
**gate** (*HardEdge*) – The pair of qubits for which we’re checking the applicability of a swap gate.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

apply_swap_gate(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L333-L355)  
Apply swap gate if it is applicable within the given layer.

Parameters:  
**gate** (*HardEdge*) – The pair of qubits between which we apply the swap gate.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If for whatever reason the swap gate cannot be applied in this layer.

Return type:  
None

draw(*mapping=None*, *ax=None*, *show=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L357-L386)  
Plot a sketch of the QPU, coloring the physical couplers based on the gate applied.

- Yellow highlight if a combination of swap and int is applied.

- Blue highlight if a swap gate is applied.

- Green highlight if an interaction gate is applied.

- No highlight (black) if nothing is happening along the edge.

The labels for the hardware qubits in the plot are the names of the associated logical qubits.

Parameters:  
- **mapping** ([*Mapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") *\|* *None*) – The [`Mapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") object used.

- **ax** ([*Axes*](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes "(in Matplotlib v3.11.2)") *\|* *None*) – [`matplotlib.axes.Axes`](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes "(in Matplotlib v3.11.2)") object to specify where to draw the picture.

- **show** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean to specift if the plot is to be shown (or e.g., processed somehow).

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing.Layer](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-d98c4c1fff377012365b4247f6beb1a43ba71853.png)
