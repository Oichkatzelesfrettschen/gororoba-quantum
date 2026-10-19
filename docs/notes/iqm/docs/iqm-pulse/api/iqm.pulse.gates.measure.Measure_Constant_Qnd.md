> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Constant_Qnd.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Constant_Qnd.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ab7a1e67fbeed25c47675122d3cb1ddc6a8ed5689146c73c72d656c8fed306b8.

# Measure_Constant_Qnd

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.Measure_Constant_Qnd(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms")

Implementation of a single-qubit projective, non quantum demolition, dispersive measurements in the Z basis.

Uses a constant probe pulse.

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.measure.Measure_Constant_Qnd.dependent_waves "iqm.pulse.gates.measure.Measure_Constant_Qnd.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`parameters`](#iqm.pulse.gates.measure.Measure_Constant_Qnd.parameters "iqm.pulse.gates.measure.Measure_Constant_Qnd.parameters") | Required calibration data, may be nested |
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

parameters*: NestedParams* *= {'acquisition_delay': Parameter(name='', label='Acquisition delay', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'acquisition_type': Setting(parameter=Parameter(name='', label='Acquisition type', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value='threshold', read_only=False, path=''), 'amplitude_i': Parameter(name='', label='Readout channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Setting(parameter=Parameter(name='', label='Readout channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'block_neighbors': Setting(parameter=Parameter(name='Block neighbors', label='Whether to block neighboring qubits in multiplexing', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=False, read_only=False, path=''), 'duration': Parameter(name='', label='Readout pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'frequency': Parameter(name='', label='Readout pulse frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_length': Parameter(name='', label='Integration length', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_threshold': Parameter(name='', label='Integration threshold', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_weights_I': Setting(parameter=Parameter(name='', label='Integration weights for channel I', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), value=array(\[\], dtype=float64), read_only=False, path=''), 'integration_weights_Q': Setting(parameter=Parameter(name='', label='Integration weights for channel Q', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), value=array(\[\], dtype=float64), read_only=False, path=''), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

wave_i  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

wave_q  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.Measure_Constant_Qnd](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-ba01c9f814a13e0c41ba0e72e496f3fa6898a2f0.png)
