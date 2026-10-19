> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fbbd77ba9f77ca5455c17ae4f4b72d94ed7ecee0275394f89d074bb57f93d85f.

# NoAcquisition_Measure_Constant

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.NoAcquisition_Measure_Constant(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`NoAcquisition_Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.html#iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms "iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms")

Implementation of a single-qubit projective, dispersive measurement in the Z basis.

Uses a constant probe pulse.

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.dependent_waves "iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`parameters`](#iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.parameters "iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='Readout channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='Readout channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'block_neighbors': Parameter(name='Block neighbors', label='Whether to block neighboring qubits in multiplexing', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='Readout pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'frequency': Parameter(name='', label='Readout pulse frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

wave_i  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

wave_q  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.NoAcquisition_Measure_Constant](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-be5aee5c2c58038632d2eb43f6f9c36ceead8c90.png)
