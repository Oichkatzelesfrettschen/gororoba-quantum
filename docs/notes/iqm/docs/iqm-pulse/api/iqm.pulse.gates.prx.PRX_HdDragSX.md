> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_HdDragSX.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_HdDragSX.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3bf8c4d3984cb388038ffcda32abb4d900a579adf3145b093f03ea322da3f8fc.

# PRX_HdDragSX

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_HdDragSX(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_CustomWaveformsSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveformsSX.html#iqm.pulse.gates.prx.PRX_CustomWaveformsSX "iqm.pulse.gates.prx.PRX_CustomWaveformsSX")

PRX gate, HD DRAG IQ pulse with VZ-based SX-implementation.

See [`PRX_CustomWaveformsSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveformsSX.html#iqm.pulse.gates.prx.PRX_CustomWaveformsSX "iqm.pulse.gates.prx.PRX_CustomWaveformsSX").

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_HdDragSX.dependent_waves "iqm.pulse.gates.prx.PRX_HdDragSX.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`parameters`](#iqm.pulse.gates.prx.PRX_HdDragSX.parameters "iqm.pulse.gates.prx.PRX_HdDragSX.parameters") | Required calibration data, may be nested |
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

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of hdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'coefficients': Parameter(name='', label='coefficients of hdi', unit='', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'compute_coefs_from_frequencies': Parameter(name='', label='compute_coefs_from_frequencies of hdi', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='pi pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='full_width of hdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'rz_after': Parameter(name='', label='RZ after IQ pulse', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz_before': Parameter(name='', label='RZ before IQ pulse', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'suppressed_frequencies': Parameter(name='', label='suppressed_frequencies of hdi', unit='Hz', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}*  
Required calibration data, may be nested

wave_i  
alias of [`HdDragI`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragI.html#iqm.pulse.playlist.hd_drag.HdDragI "iqm.pulse.playlist.hd_drag.HdDragI")

wave_q  
alias of [`HdDragQ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragQ.html#iqm.pulse.playlist.hd_drag.HdDragQ "iqm.pulse.playlist.hd_drag.HdDragQ")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_HdDragSX](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-4c9dda71cf6868f80a264087a3cd4b8893fecf3e.png)
