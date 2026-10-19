> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 afe837d308075352bfb2cb68acb57ac6fb308482e7795d52b09410fed20fa0f6.

# iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions

iqm.error_reduction_tools.readout_characterization.topologies.get_subset_positions(*topology*, *qubit_labels*)  
Get positions for a subset of qubits from a topology.

Useful when running characterization on a subset of qubits but still wanting to visualize them on the full QPU layout.

Parameters:  
- **topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology")) – [`QPUTopology`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology") instance.

- **qubit_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – List of qubit labels to get positions for.

Returns:  
Dictionary mapping qubit indices to (x, y) positions.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

Example

```
>>> topology = topology_from_qc(client)  # obtain from a connected quantum computer
>>> subset = ["QB1", "QB2", "QB5", "QB6"]
>>> positions = get_subset_positions(topology, subset)
```
