> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.LRU_F0G1.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.LRU_F0G1.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 efab003f732195f9bc7be5528022cc5ce2c41a59488b1cf2707b9b04c3e4fa6a.

# LRU_F0G1

Module: [`iqm.pulse.gates.lru`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.html#module-iqm.pulse.gates.lru "iqm.pulse.gates.lru")

*class* iqm.pulse.gates.lru.LRU_F0G1(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`SinglePulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.SinglePulseGate.html#iqm.pulse.gate_implementation.SinglePulseGate "iqm.pulse.gate_implementation.SinglePulseGate")

Leakage reduction unit implementation driving the \\\|f0\rangle \leftrightarrow \|g1\rangle\\ transition.

This gate implementation removes qubit leakage (population of the \\\|2\rangle\\ state) by driving at the frequency of the \\\|f0\rangle \leftrightarrow \|g1\rangle\\ transition which causes Rabi oscillation between those two states. The excited readout resonator quickly decays to its ground state, thus eventually causing the \\\|2\rangle\\ state population of the qubit to move to the \\\|0\rangle\\ state (basis here: \\\|\text{qubit}, \text{readout resonator}\rangle\\).

See \[[1](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id7 "P. Magnard, P. Kurpiers, B. Royer, T. Walter, J.-C. Besse, S. Gasparinetti, M. Pechal, J. Heinsoo, S. Storz, A. Blais, and A. Wallraff. Fast and Unconditional All-Microwave Reset of a Superconducting Qubit. Physical Review Letters, 121(6):060502, 2018. URL: https://link.aps.org/doi/10.1103/PhysRevLett.121.060502, arXiv:1801.07689, doi:10.1103/PhysRevLett.121.060502.")\] for reference of an experiment where such a pulse was used.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.lru.LRU_F0G1.parameters "iqm.pulse.gates.lru.LRU_F0G1.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.lru.LRU_F0G1.locus_mapping_function "iqm.pulse.gates.lru.LRU_F0G1.locus_mapping_function") | One-qubit loci with physical drive and readout. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

parameters*: NestedParams* *= {'amplitude': Parameter(name='', label='F0G1 pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='F0G1 pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='F0G1 pulse width', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='F0G1 pulse modulation frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'phase_increment': Setting(parameter=Parameter(name='', label='F0G1 pulse phase increment', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'rise_time': Parameter(name='', label='F0G1 pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

locus_mapping_function()  
One-qubit loci with physical drive and readout.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gates.lru.LRU_F0G1](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-5fa3b51950d5108cf1a15d1482d57f532a1411c4.png)
