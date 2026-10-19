> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8151faee19326d516612b755432781bd40ee222874dabedb5e1673f26d9f7c5d.

# iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line

iqm.error_reduction_tools.readout_characterization.topologies.get_qubits_by_control_line(*topology*, *line_indices=None*)  
Get qubit labels grouped by control lines.

Useful for selecting qubits that share readout infrastructure.

Parameters:  
- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology")) – [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology") instance.

- **line_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – Optional list of control line indices to include. If `None`, returns all qubits.

Returns:  
List of qubit labels from the specified control lines.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Example

```
>>> topology = topology_from_qc(client)  # obtain from a connected quantum computer
>>> # Get qubits from first two control lines
>>> qubits = get_qubits_by_control_line(topology, [0, 1])
```
