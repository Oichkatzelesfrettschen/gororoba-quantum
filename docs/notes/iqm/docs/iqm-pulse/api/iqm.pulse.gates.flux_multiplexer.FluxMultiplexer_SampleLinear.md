> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ba89d3c97ec9c8330374ee992fd1c4e6bbf20ff594f49a0b61a4537d18697f66.

# FluxMultiplexer_SampleLinear

Module: [`iqm.pulse.gates.flux_multiplexer`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.flux_multiplexer.html#module-iqm.pulse.gates.flux_multiplexer "iqm.pulse.gates.flux_multiplexer")

*class* iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Linear flux pulse multiplexed (user for correcting flux crosstalk).

The required calibration data is the flux cross-talk correction matrix, where the element \\C_ij\\ represents the correction needed for flux component `i` arising from the crosstalk caused by flux component `j`, so that after the corrections, the flux pulse played at `i` is \\f(t) = A_i w_i(t) + \sum_j C_ij A_j w_j(t)\\, where \\A_j\`\\ is the flux pulse amplitude for `j` and \\w_j(t)\\ the (normalized) waveform.

The flux crosstalk correction matrix is given in a sparse form via two calibration parameters (we do not support dict- or xarray-valued Parameters yet…). Parameter `matrix_index` lists the relevant (non-zero) elements of the matrix as a flat `np.array` of strings of the form `<flux component i>__<flux component j>`. Parameter `matrix_elements` lists the corresponding matrix values \\C_ij\\ (the lengths of these arrays must match).

TODO: this is for now an experimental R&D implementation, and everything here is subject to change still

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear.parameters "iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear.locus_mapping_function "iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear.locus_mapping_function") | One-qubit loci. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

parameters*: NestedParams* *= {'matrix_elements': Parameter(name='matrix_elements', label='Flux crosstalk correction sparse matrix elements', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'matrix_index': Parameter(name='matrix_index', label='Flux crosstalk correction sparse matrix index', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.LIST: 1\>, element_indices=None)}*  
Required calibration data, may be nested

*static* locus_mapping_function(*station_properties*)  
One-qubit loci.

Parameters:  
**station_properties** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gates.flux_multiplexer.FluxMultiplexer_SampleLinear](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-dd64ca41352f77df73bfc35e05e54a56136b280c.png)
