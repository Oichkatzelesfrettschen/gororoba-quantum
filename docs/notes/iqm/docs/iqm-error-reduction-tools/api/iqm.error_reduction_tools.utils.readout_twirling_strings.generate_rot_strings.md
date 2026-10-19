> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 232c06ca1d7921f7b86d97a20faa33be1b60c920c4cf31869883bb870c6a2dbf.

# iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings

iqm.error_reduction_tools.utils.readout_twirling_strings.generate_rot_strings(*qpu_topology=None*, *active_qubits=None*, *strategy='LOCAL'*, *max_twirling=None*)  
Generate readout twirling strings for the requested strategy.

Parameters:  
- **qpu_topology** ([*QPUTopology*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology.html#iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology "iqm.error_reduction_tools.readout_characterization.topologies.QPUTopology") *\|* *None*) – Topology object providing qubits, neighbors, and control lines. Required for the `LOCAL` and `PROBELINES` strategies. May be `None` for `HADAMARD` and `MINIMAL` when *active_qubits* is provided explicitly.

- **active_qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Subset of qubits to include. If `None`, labels are derived from *qpu_topology* (which must then be provided).

- **strategy** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Twirling strategy name. Matching is case-insensitive and ignores surrounding whitespace.

- **max_twirling** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Maximum number of strings for strategies that can be expanded.

Returns:  
A list of dictionaries mapping each active qubit label to `"I"` or `"X"`.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the strategy is unknown, size constraints are not satisfied, or required arguments are missing.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]
