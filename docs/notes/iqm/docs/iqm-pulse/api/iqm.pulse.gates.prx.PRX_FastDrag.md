> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_FastDrag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_FastDrag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3deb2d578c8b554608236f9e86900704e5a99c9d56e599fcca26bccc9d5fd2e6.

# PRX_FastDrag

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_FastDrag(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms")

PRX gate, FAST DRAG IQ pulse based on amplitude scaling.

See [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms").

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_FastDrag.dependent_waves "iqm.pulse.gates.prx.PRX_FastDrag.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`parameters`](#iqm.pulse.gates.prx.PRX_FastDrag.parameters "iqm.pulse.gates.prx.PRX_FastDrag.parameters") | Required calibration data, may be nested |
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

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of fdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'coefficients': Parameter(name='', label='coefficients of fdi', unit='', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'compute_coefs_from_frequencies': Parameter(name='', label='compute_coefs_from_frequencies of fdi', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='pi pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='full_width of fdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'number_of_cos_terms': Parameter(name='', label='number_of_cos_terms of fdi', unit='', data_type=\<DataType.INT: 5\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'suppressed_frequencies': Parameter(name='', label='suppressed_frequencies of fdi', unit='Hz', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'suppressed_interval_widths': Parameter(name='', label='suppressed_interval_widths of fdi', unit='Hz', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'weights': Parameter(name='', label='weights of fdi', unit='', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}*  
Required calibration data, may be nested

wave_i  
alias of [`FastDragI`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragI.html#iqm.pulse.playlist.fast_drag.FastDragI "iqm.pulse.playlist.fast_drag.FastDragI")

wave_q  
alias of [`FastDragQ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.fast_drag.FastDragQ.html#iqm.pulse.playlist.fast_drag.FastDragQ "iqm.pulse.playlist.fast_drag.FastDragQ")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_FastDrag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-91b343bc89216b3173229b7a54694579b009c291.png)
