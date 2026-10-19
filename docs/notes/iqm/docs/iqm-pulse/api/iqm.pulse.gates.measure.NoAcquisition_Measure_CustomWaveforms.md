> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0f7cf5513f45c63bad94195065e974747ee7b579ebafdf202ba4bed3c7899fc1.

# NoAcquisition_Measure_CustomWaveforms

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms")

Base class for `measure` with custom probe IQ waveforms without any integration or acquisition.

Similar to the [`Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms") except that signal acquisition is removed. The implementation is still factorizable, the locus contains qubits, and multi-component readout is performed via multiplexing.

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.dependent_waves "iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`root_parameters`](#iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.root_parameters "iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.root_parameters") | Parameters independent of the of Waveforms. |
| `wave_i` | Waveform for the I channel. |
| `wave_q` | Waveform for the Q channel. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting\]* *= {'amplitude_i': Parameter(name='', label='Readout channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='Readout channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'block_neighbors': Parameter(name='Block neighbors', label='Whether to block neighboring qubits in multiplexing', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='Readout pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'frequency': Parameter(name='', label='Readout pulse frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Parameters independent of the of Waveforms. Inheriting classes may override this to include parameters common to all such implementations.

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-6c5c8f03821bfd840a355fe0cde7afe26c6ca002.png)
