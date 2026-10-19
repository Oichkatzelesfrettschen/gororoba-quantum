> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_F0G1.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_F0G1.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 200d52bcb9355d447b5c7486b294a7323ca66faf6e35e94059eb68658cdaa6c8.

# Reset_F0G1

Module: [`iqm.pulse.gates.reset`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html#module-iqm.pulse.gates.reset "iqm.pulse.gates.reset")

*class* iqm.pulse.gates.reset.Reset_F0G1(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`SinglePulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.SinglePulseGate.html#iqm.pulse.gate_implementation.SinglePulseGate "iqm.pulse.gate_implementation.SinglePulseGate")

Reset by driving the \\\|f0\rangle \leftrightarrow \|g1\rangle\\ transition.

This gate implementation resets the qubit by driving the \\\|f0\rangle \leftrightarrow \|g1\rangle\\ transition (basis here: \\\|\text{qubit}, \text{readout resonator}\rangle\\) and the \\\|e\rangle \leftrightarrow \|f\rangle\\ transition simultaneously. The principle is the same as for the `lru` gate (see [`LRU_F0G1`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.LRU_F0G1.html#iqm.pulse.gates.lru.LRU_F0G1 "iqm.pulse.gates.lru.LRU_F0G1")), except here we additionally drive the \\\|e\rangle \leftrightarrow \|f\rangle\\ to also reset the \\\|e\rangle\\ state, not just the \\\|f\rangle\\ state. The reset happens due to quick dissipation in the resonator. This operation is therefore non-unitary.

The gate is implemented via a :class:`MultiplexedIQPulse`, combining two modulated pulses which are supposed to drive each of the above mentioned transitions.

See \[[1](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id7 "P. Magnard, P. Kurpiers, B. Royer, T. Walter, J.-C. Besse, S. Gasparinetti, M. Pechal, J. Heinsoo, S. Storz, A. Blais, and A. Wallraff. Fast and Unconditional All-Microwave Reset of a Superconducting Qubit. Physical Review Letters, 121(6):060502, 2018. URL: https://link.aps.org/doi/10.1103/PhysRevLett.121.060502, arXiv:1801.07689, doi:10.1103/PhysRevLett.121.060502.")\] for reference of an experiment where such a pulse was used.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.reset.Reset_F0G1.parameters "iqm.pulse.gates.reset.Reset_F0G1.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.reset.Reset_F0G1.locus_mapping_function "iqm.pulse.gates.reset.Reset_F0G1.locus_mapping_function") | One-qubit loci with physical drive and readout. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

parameters*: NestedParams* *= {'duration': Parameter(name='', label='Multiplexed pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'ef_pulse': {'amplitude_i': Parameter(name='', label='EF pulse channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='EF pulse channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='EF pulse full width', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='EF pulse modulation frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'offset': Setting(parameter=Parameter(name='', label='EF pulse offset from the F0G1 pulse', unit='s', data_type=\<DataType.INT: 5\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'rise_time': Parameter(name='', label='EF pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'f0g1_pulse': {'amplitude': Parameter(name='', label='F0G1 pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='F0G1 pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='F0G1 pulse modulation frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'rise_time': Parameter(name='', label='F0G1 pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Required calibration data, may be nested

locus_mapping_function()  
One-qubit loci with physical drive and readout.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gates.reset.Reset_F0G1](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-48e52b8a2532daae54eea8e9db17d6f463249a17.png)
