> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a7522a19d479fcb4027906bc1ab64551ed9ee7d41d10bb0e0ad5e1c84e43e61b.

# QPU

Module: [`iqm.qaoa.transpiler.quantum_hardware`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html#module-iqm.qaoa.transpiler.quantum_hardware "iqm.qaoa.transpiler.quantum_hardware")

*class* iqm.qaoa.transpiler.quantum_hardware.QPU(*hardware_graph*, *hardware_layout=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L74-L177)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A parent class for all QPU architectures.

The main purpose of the QPU class is to store the [`hardware_graph`](#iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph "iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph") and the [`shortest_path`](#iqm.qaoa.transpiler.quantum_hardware.QPU.shortest_path "iqm.qaoa.transpiler.quantum_hardware.QPU.shortest_path")/s in there. The method [`draw()`](#iqm.qaoa.transpiler.quantum_hardware.QPU.draw "iqm.qaoa.transpiler.quantum_hardware.QPU.draw") can be used independently to plot the graph (using the [`hardware_layout`](#iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_layout "iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_layout")), but it’s meant to be used by the [`draw()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer.draw "iqm.qaoa.transpiler.routing.Layer.draw") method of the class [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer").

Parameters:  
- **hardware_graph** (*nx.Graph*) – A [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") representing the topology of the QPU, i.e., the connections between the [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s.

- **hardware_layout** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[HardQubit,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[Any,* *Any\]\]* *\|* *None*) – A layout of the QPU, i.e., the coordinates of the qubits in the 2D plane.

Attributes

|  |  |
|----|----|
| [`hardware_graph`](#iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph "iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_graph") | The connectivity graph of the QPU. |
| [`hardware_layout`](#iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_layout "iqm.qaoa.transpiler.quantum_hardware.QPU.hardware_layout") | The layout of the hardware qubits (in the 2D plane). |
| [`qubits`](#iqm.qaoa.transpiler.quantum_hardware.QPU.qubits "iqm.qaoa.transpiler.quantum_hardware.QPU.qubits") | The set of all [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s of the QPU. |
| [`shortest_path`](#iqm.qaoa.transpiler.quantum_hardware.QPU.shortest_path "iqm.qaoa.transpiler.quantum_hardware.QPU.shortest_path") | The dictionary of dictionaries of shortest paths. |

Methods

|  |  |
|----|----|
| [`draw`](#iqm.qaoa.transpiler.quantum_hardware.QPU.draw "iqm.qaoa.transpiler.quantum_hardware.QPU.draw") | A method for drawing the QPU. |
| [`has_edge`](#iqm.qaoa.transpiler.quantum_hardware.QPU.has_edge "iqm.qaoa.transpiler.quantum_hardware.QPU.has_edge") | True iff there is an edge between the qubits involved in `gate`. |

*property* qubits*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.HardQubit')\]*  
The set of all [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s of the QPU.

has_edge(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L105-L115)  
True iff there is an edge between the qubits involved in `gate`.

Parameters:  
**gate** (*HardEdge*) – A [`HardEdge`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardEdge.html#iqm.qaoa.transpiler.quantum_hardware.HardEdge "iqm.qaoa.transpiler.quantum_hardware.HardEdge") between two [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s.

Returns:  
True if there is an edge between the two [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s on the QPU graph and False otherwise.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

*property* hardware_graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The connectivity graph of the QPU.

*property* hardware_layout*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.HardQubit'), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*  
The layout of the hardware qubits (in the 2D plane).

*property* shortest_path*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.HardQubit'), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.HardQubit'), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.HardQubit')\]\]\]*  
The dictionary of dictionaries of shortest paths.

It’s defined so that `shortest_path[source][target]` is the list of nodes lying on the/a shortest path between the `source` and `target` nodes.

draw(*mapping=None*, *ax=None*, *gate_lists=None*, *show=True*, *\*\*kwargs*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L136-L177)  
A method for drawing the QPU.

It displays the picture of the QPU in a pop-up window, with edges colored based on `gate_lists`.

Parameters:  
- **mapping** ([*Mapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") *\|* *None*) – The mapping between the logical and hardware qubits, for labels of the graph nodes.

- **ax** (*Axes* *\|* *None*) – An instance of [`matplotlib.axes.Axes`](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes "(in Matplotlib v3.11.2)") object, to define the plotting area.

- **gate_lists** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[HardQubit\]* *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[HardQubit,* *HardQubit\]\]\]* *\|* *None*) – A dictionary whose keys are colors (as single-letter strings) and values are lists of edges which should be colored that color.

- **show** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean which decides if the graph will be shown in a pop-up window.

- **\*\*kwargs** (*Any*) – Arbitrary keyword arguments for `draw_networkx_edges()`.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.quantum_hardware.QPU](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-118938cfd33217c0238b353a10d45e0114747a1e.png)
