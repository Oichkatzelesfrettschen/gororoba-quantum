> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d106e46b3273a93e1e91c8b80a33ceccb59d41c739dbbfb82e033f63ce522313.

# iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology

*class* iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology(*name*, *num_qubits*, *positions=None*, *couplers=None*, *control_lines=None*, *adjacent_qubits=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Container for QPU topology information.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **positions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*)

- **couplers** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]* *\|* *None*)

- **control_lines** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]* *\|* *None*)

- **adjacent_qubits** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]* *\|* *None*)

name  
Name of the quantum computer (e.g., “emerald”, “garnet”)

num_qubits  
Total number of qubits

positions  
Dictionary mapping qubit number to (x, y) position for visualization. Populated when the topology is built via [`topology_from_qc()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.topology_utils.topology_from_qc.html#iqm.error_reduction_tools.utils.topology_utils.topology_from_qc "iqm.error_reduction_tools.utils.topology_utils.topology_from_qc"); empty by default.

couplers  
List of tuples representing connected qubit pairs

control_lines  
List of tuples grouping qubits by control/readout lines

adjacent_qubits  
Optional dictionary mapping each qubit to its neighbors

Methods

|  |  |
|----|----|
| `_compute_adjacent_qubits`() | Compute adjacent qubits from coupler list. |
| [`get_control_line_for_qubit`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_control_line_for_qubit "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_control_line_for_qubit")(qubit) | Get the control line index for a given qubit. |
| [`get_coupler_pairs`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_coupler_pairs "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_coupler_pairs")() | Return list of all coupler pairs (connected qubits). |
| [`get_neighbors`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_neighbors "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_neighbors")(qubit) | Get neighboring qubits for a given qubit, excluding itself. |
| [`get_qubit_labels`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_qubit_labels "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_qubit_labels")() | Return list of all qubit names (e.g., \['QB1', 'QB2', ...\]). |
| [`get_qubits_in_control_line`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_qubits_in_control_line "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.get_qubits_in_control_line")(line_index) | Get qubits belonging to a specific control/readout line. |
| [`parse_qubit_index`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.parse_qubit_index "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.parse_qubit_index")(label) | Extract the numeric index from a qubit name. |
| [`sort_qubit_labels`](#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.sort_qubit_labels "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.sort_qubit_labels")(labels) | Sort qubit labels by their numeric index. |

get_qubit_labels()  
Return list of all qubit names (e.g., \[‘QB1’, ‘QB2’, …\]).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

*static* parse_qubit_index(*label*)  
Extract the numeric index from a qubit name.

Parses names of the form `"QBn"` and returns the integer *n*.

Parameters:  
**label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit name (e.g., `"QB12"`).

Returns:  
The integer index embedded in the name.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Example

```
>>> QPUTopology.parse_qubit_index("QB12")
12
```

*static* sort_qubit_labels(*labels*)  
Sort qubit labels by their numeric index.

Example

```
>>> QPUTopology.sort_qubit_labels(["QB12", "QB4", "QB1"])
['QB1', 'QB4', 'QB12']
```

Parameters:  
**labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_neighbors(*qubit*)  
Get neighboring qubits for a given qubit, excluding itself.

Parameters:  
**qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit label (e.g., ‘QB1’).

Returns:  
List of neighboring qubit labels, **not** including qubit.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Example

```
>>> topology.get_neighbors("QB5")
['QB1', 'QB4', 'QB6', 'QB11']
```

get_qubits_in_control_line(*line_index*)  
Get qubits belonging to a specific control/readout line.

Parameters:  
**line_index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Index of the control line (0-based).

Returns:  
Tuple of qubit labels in that control line.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If no control lines are defined or `line_index` is out of range.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]

get_control_line_for_qubit(*qubit*)  
Get the control line index for a given qubit.

Parameters:  
**qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit label (e.g., ‘QB1’).

Returns:  
Index of the control line containing the `qubit`, or `None` if not found.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

get_coupler_pairs()  
Return list of all coupler pairs (connected qubits).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]
