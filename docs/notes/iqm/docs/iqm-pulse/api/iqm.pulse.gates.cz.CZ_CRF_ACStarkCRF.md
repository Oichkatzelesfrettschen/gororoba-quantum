> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 469199cd6ed1ff291dc8f175e6085e51b89b50b6e8f1eacdd9c5e6cd5c9b678f.

# CZ_CRF_ACStarkCRF

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CouplerFluxPulseQubitACStarkPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.html#iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate "iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate")

Controlled-Z two-qubit gate.

CZ gate implemented using a cosine rise fall flux pulse for the coupler and a modulated cosine rise fall (CRF) AC Stark pulse on one qubit.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.parameters "iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.parameters") | Required calibration data, may be nested |
| [`symmetric`](#iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.symmetric "iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.locus_mapping_function "iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.locus_mapping_function") | Two-qubit loci, connected through a coupler with fast flux, both qubits have drive. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave  
alias of [`CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFall.html#iqm.models.playlist.waveforms.CosineRiseFall "(in IQM data definitions v3.1.0)")

locus_mapping_function()  
Two-qubit loci, connected through a coupler with fast flux, both qubits have drive.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: NestedParams* *= {'coupler': {'amplitude': Parameter(name='', label='amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'full_width': Parameter(name='', label='full_width of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='rise_time of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'first_qubit': {'amplitude': Parameter(name='', label='amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'full_width': Parameter(name='', label='full_width of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation_frequency of mcrf', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'phase': Setting(parameter=Parameter(name='', label='phase of mcrf', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'rise_time': Parameter(name='', label='rise_time of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'second_qubit': {'amplitude': Parameter(name='', label='amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'full_width': Parameter(name='', label='full_width of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation_frequency of mcrf', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'phase': Setting(parameter=Parameter(name='', label='phase of mcrf', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'rise_time': Parameter(name='', label='rise_time of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Required calibration data, may be nested

qubit_drive_wave  
alias of [`ModulatedCosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.ModulatedCosineRiseFall.html#iqm.models.playlist.waveforms.ModulatedCosineRiseFall "(in IQM data definitions v3.1.0)")

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-355951b2f13cffeaa419f7414600b620f9801e80.png)
