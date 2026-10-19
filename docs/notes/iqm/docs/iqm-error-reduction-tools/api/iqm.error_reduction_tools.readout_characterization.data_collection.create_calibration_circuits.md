> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 19caf7e9e36e6026c041611041c516dcec20b254c0a63a3deeac4f613be236a8.

# iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits

iqm.error_reduction_tools.readout_characterization.data_collection.create_calibration_circuits(*qubits*, *number_of_circuits*, *symmetrize=True*, *seed=None*, *equatorial_randomization=False*)  
Generate readout error characterization (REC) circuits and preparation strings.

Creates circuits that prepare qubits in computational basis states (`|0>` or `|1>`) using I (identity) or X gates, then measure all qubits. Optionally applies equatorial randomization to X gates for improved error characterization.

Parameters:  
- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – IQM qubit names to characterize (e.g., \[‘QB1’, ‘QB2’\]).

- **number_of_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of calibration circuits to generate.

- **symmetrize** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, generates complementary circuit pairs (I↔X) to balance `|0>` and `|1>` state preparations across all qubits.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Random seed for reproducible circuit generation.

- **equatorial_randomization** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, randomize X gate phase angles (phi) around the Bloch sphere equator. This distributes state preparation over the XY plane.

Returns:  
- Circuits ready for compilation.

- Preparation strings (same length as circuits), where each character is ‘I’ (prepare `|0>`) or ‘X’ (prepare `|1>`).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If qubits list is empty or `number_of_circuits` \< 1.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]

Example

```
>>> circuits, preps = create_calibration_circuits(['QB1', 'QB2'], 4, symmetrize=True)
>>> len(circuits), len(preps)
(4, 4)
```
