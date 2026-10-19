> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1ca7bbf6e5866e1beecd9c2a2dae027e437172ce25c82e305993fc066f0b26fe.

# CouplerMOVE_CRF

Module: [`iqm.pulse.gates.coupler_move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.html#module-iqm.pulse.gates.coupler_move "iqm.pulse.gates.coupler_move")

*class* iqm.pulse.gates.coupler_move.CouplerMOVE_CRF(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CouplerMOVEGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVEGate.html#iqm.pulse.gates.coupler_move.CouplerMOVEGate "iqm.pulse.gates.coupler_move.CouplerMOVEGate")

COUPLER_MOVE gate using CRF on coupler only.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.parameters "iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.parameters") | Required calibration data, may be nested |
| [`qubit_wave`](#iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.qubit_wave "iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.qubit_wave") | Coupler flux pulse Waveform |
| [`symmetric`](#iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.symmetric "iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.locus_mapping_function "iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.locus_mapping_function") | Get custom locus mapping for this GateImplementation. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave  
alias of [`CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFall.html#iqm.models.playlist.waveforms.CosineRiseFall "(in IQM data definitions v3.1.0)")

locus_mapping_function()  
Get custom locus mapping for this GateImplementation.

Returns:  
Locus mapping of qubit-coupler pairs for coupler flux implementation.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: NestedParams* *= {'coupler': {'amplitude': Parameter(name='', label='Coupler flux pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='Coupler flux pulse center_offset of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'full_width': Parameter(name='', label='Coupler flux pulse full_width of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='Coupler flux pulse rise_time of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

qubit_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Coupler flux pulse Waveform

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.coupler_move.CouplerMOVE_CRF](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-076c31680b131dfcd74ac3d09d19554290242761.png)
