> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_FastDragSX.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_FastDragSX.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6ef521d5697518f96a0e11eb24200878c95c69016c906a36870cc3c6aabdff93.

# PRX_FastDragSX

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_FastDragSX(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_CustomWaveformsSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveformsSX.html#iqm.pulse.gates.prx.PRX_CustomWaveformsSX "iqm.pulse.gates.prx.PRX_CustomWaveformsSX")

PRX gate, FAST DRAG IQ pulse with VZ-based SX-implementation.

See [`PRX_CustomWaveformsSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveformsSX.html#iqm.pulse.gates.prx.PRX_CustomWaveformsSX "iqm.pulse.gates.prx.PRX_CustomWaveformsSX").

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_FastDragSX.dependent_waves "iqm.pulse.gates.prx.PRX_FastDragSX.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`parameters`](#iqm.pulse.gates.prx.PRX_FastDragSX.parameters "iqm.pulse.gates.prx.PRX_FastDragSX.parameters") | Required calibration data, may be nested |
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

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of fdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'coefficients': Parameter(name='', label='coefficients of fdi', unit='', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'compute_coefs_from_frequencies': Parameter(name='', label='compute_coefs_from_frequencies of fdi', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='pi pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='full_width of fdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'number_of_cos_terms': Parameter(name='', label='number_of_cos_terms of fdi', unit='', data_type=\<DataType.INT: 5\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz_after': Parameter(name='', label='RZ after IQ pulse', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz_before': Parameter(name='', label='RZ before IQ pulse', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'suppressed_frequencies': Parameter(name='', label='suppressed_frequencies of fdi', unit='Hz', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'suppressed_interval_widths': Parameter(name='', label='suppressed_interval_widths of fdi', unit='Hz', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'weights': Parameter(name='', label='weights of fdi', unit='', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}*  
Required calibration data, may be nested

wave_i  
alias of [`FastDragI`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragI.html#iqm.pulse.playlist.fast_drag.FastDragI "iqm.pulse.playlist.fast_drag.FastDragI")

wave_q  
alias of [`FastDragQ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragQ.html#iqm.pulse.playlist.fast_drag.FastDragQ "iqm.pulse.playlist.fast_drag.FastDragQ")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_FastDragSX](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d9b91b6ad4462a8e818316387d2293be094701a5.png)
