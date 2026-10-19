> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5638c48c48ca2a05f6fcc3cb6c605d58d709fc34d1dfa023b3d4c85fa8989497.

# RZ_ACStarkShift_CosineRiseFall

Module: [`iqm.pulse.gates.rz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html#module-iqm.pulse.gates.rz "iqm.pulse.gates.rz")

*class* iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`RZ_ACStarkShift`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift.html#iqm.pulse.gates.rz.RZ_ACStarkShift "iqm.pulse.gates.rz.RZ_ACStarkShift")

AC stark pulse implemented as a modulated cosine rise fall pulse.

Constructs an instance of the AC Stark pulse for the given locus.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.parameters "iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.parameters") | Required calibration data, may be nested |
| [`symmetric`](#iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.symmetric "iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

ac_stark_waveform  
alias of [`ModulatedCosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.ModulatedCosineRiseFall.html#iqm.models.playlist.waveforms.ModulatedCosineRiseFall "(in IQM data definitions v3.1.0)")

parameters*: NestedParams* *= {'amplitude': Parameter(name='', label='amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='full_width of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation_frequency of mcrf', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'phase': Setting(parameter=Parameter(name='', label='phase of mcrf', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'phase_increment': Parameter(name='', label='phase increment', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='rise_time of mcrf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8e14d7b2db7bbd12379c0c4a1905fa2b3ac1036e.png)
