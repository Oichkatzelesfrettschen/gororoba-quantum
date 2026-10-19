> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ffcae45fb484b8b259218afc1b5490da5179f45d3c736d8a5605e54f81ad3c12.

# MOVE_SLEPIAN_CRF

Module: [`iqm.pulse.gates.move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html#module-iqm.pulse.gates.move "iqm.pulse.gates.move")

*class* iqm.pulse.gates.move.MOVE_SLEPIAN_CRF(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`MOVE_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_CustomWaveforms.html#iqm.pulse.gates.move.MOVE_CustomWaveforms "iqm.pulse.gates.move.MOVE_CustomWaveforms")

MOVE gate using Slepian waveform for the coupler flux pulse and CRF waveform for the qubit flux pulse.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.parameters "iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.parameters") | Required calibration data, may be nested |
| [`symmetric`](#iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.symmetric "iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.locus_mapping_function "iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.locus_mapping_function") | Two-component loci connected through a coupler where the coupler and at least one component has fast flux. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave  
alias of [`Slepian`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Slepian.html#iqm.models.playlist.waveforms.Slepian "(in IQM data definitions v3.1.0)")

locus_mapping_function()  
Two-component loci connected through a coupler where the coupler and at least one component has fast flux.

There must be two locus components connected by a coupler, where the first locus component has fast flux. If both locus components have fast flux, we include both locus orders.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: NestedParams* *= {'coupler': {'amplitude': Parameter(name='', label='Coupler flux pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='Coupler flux pulse center_offset of Slepian', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'coupling_strength_normalized': Parameter(name='', label='Coupler flux pulse coupling_strength_normalized of Slepian', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'flat_width': Setting(parameter=Parameter(name='', label='Coupler flux pulse flat_width of Slepian', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'frequency_initial_normalized': Parameter(name='', label='Coupler flux pulse frequency_initial_normalized of Slepian', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'frequency_to_minimize_normalized': Parameter(name='', label='Coupler flux pulse frequency_to_minimize_normalized of Slepian', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='Coupler flux pulse full_width of Slepian', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'lambda_1': Parameter(name='', label='Coupler flux pulse lambda_1 of Slepian', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'lambda_2': Parameter(name='', label='Coupler flux pulse lambda_2 of Slepian', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'squid_asymmetry': Setting(parameter=Parameter(name='', label='Coupler flux pulse squid_asymmetry of Slepian', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path='')}, 'detuning': Parameter(name='', label='Detuning of the computational components at parking', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'qubit': {'amplitude': Parameter(name='', label='Qubit flux pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='Qubit flux pulse center_offset of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'full_width': Parameter(name='', label='Qubit flux pulse full_width of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='Qubit flux pulse rise_time of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Required calibration data, may be nested

qubit_wave  
alias of [`CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFall.html#iqm.models.playlist.waveforms.CosineRiseFall "(in IQM data definitions v3.1.0)")

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.move.MOVE_SLEPIAN_CRF](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-183bb5b0175be39f3ede1fc1a1f82f2873dc0a3f.png)
