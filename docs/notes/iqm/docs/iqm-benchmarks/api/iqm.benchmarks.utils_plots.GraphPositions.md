> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.GraphPositions.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.GraphPositions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 08f65edc1c94c4d170eae3679ec40027fc92d9a905466d4abeb819e3b7c07779.

# iqm.benchmarks.utils_plots.GraphPositions

*class* iqm.benchmarks.utils_plots.GraphPositions  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A class to store and generate graph positions for different chip layouts.

This class contains predefined node positions for various quantum chip topologies and provides methods to generate positions for different layout types.

&nbsp;

garnet_positions  
Mapping of node indices to (x,y) positions for Garnet chip.

&nbsp;

deneb_positions  
Mapping of node indices to (x,y) positions for Deneb chip.

&nbsp;

predefined_stations  
Mapping of chip names to their position dictionaries.

Attributes

|  |  |
|----|----|
| [`deneb_positions`](#iqm.benchmarks.utils_plots.GraphPositions.deneb_positions "iqm.benchmarks.utils_plots.GraphPositions.deneb_positions") |  |
| `emerald_positions` |  |
| [`garnet_positions`](#iqm.benchmarks.utils_plots.GraphPositions.garnet_positions "iqm.benchmarks.utils_plots.GraphPositions.garnet_positions") |  |
| `max_qubit_number` |  |
| `node` |  |
| [`predefined_stations`](#iqm.benchmarks.utils_plots.GraphPositions.predefined_stations "iqm.benchmarks.utils_plots.GraphPositions.predefined_stations") |  |
| `previous_nodes` |  |
| `sirius_positions` |  |

Methods

|  |  |
|----|----|
| `__eq__`(other) | Return self==value. |
| `__repr__`() | Return repr(self). |
| [`create_positions`](#iqm.benchmarks.utils_plots.GraphPositions.create_positions "iqm.benchmarks.utils_plots.GraphPositions.create_positions")(graph\[, topology\]) | Generate node positions for a given graph and topology. |
| [`get_positions`](#iqm.benchmarks.utils_plots.GraphPositions.get_positions "iqm.benchmarks.utils_plots.GraphPositions.get_positions")(\[station, graph, num_qubits\]) | Get predefined positions for a specific station or generate positions for a custom graph. |

*static* create_positions(*graph: PyGraph*, *topology: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['star', 'crystal'\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]  
Generate node positions for a given graph and topology.

Parameters:  
- **graph** (*PyGraph*) – The graph to generate positions for.

- **topology** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['star',* *'crystal'\]* *\|* *None*) – The type of layout to generate. Must be either “star” or “crystal”.

Returns:  
A dictionary mapping node indices to (x,y) coordinates.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

&nbsp;

*static* get_positions(*station: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *graph: PyGraph \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]  
Get predefined positions for a specific station or generate positions for a custom graph.

Parameters:  
- **station** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – The name of the station to get predefined positions for. If None, positions will be generated algorithmically.

- **graph** (*PyGraph* *\|* *None*) – The graph to generate positions for if no predefined positions exist. Used only when station is None and num_qubits doesn’t match any predefined layout.

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of qubits to get a layout for. If matches a known system, predefined positions will be used.

Returns:  
A dictionary mapping node indices to (x,y) coordinates.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If none of station, graph, or num_qubits are provided, or if num_qubits doesn’t match any predefined layout and graph is None.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]
