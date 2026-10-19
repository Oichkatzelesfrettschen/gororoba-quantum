> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_HdDrag.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_HdDrag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 368f52dd8e8c25b687b15511877084c2ff23c65449b3cbda83b9cba704103747.

# PRX_HdDrag

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_HdDrag(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms")

PRX gate, HD DRAG IQ pulse based on amplitude scaling.

See [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms").

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_HdDrag.dependent_waves "iqm.pulse.gates.prx.PRX_HdDrag.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`parameters`](#iqm.pulse.gates.prx.PRX_HdDrag.parameters "iqm.pulse.gates.prx.PRX_HdDrag.parameters") | Required calibration data, may be nested |
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

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of hdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0, read_only=False, path=''), 'coefficients': Parameter(name='', label='coefficients of hdi', unit='', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'compute_coefs_from_frequencies': Parameter(name='', label='compute_coefs_from_frequencies of hdi', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='pi pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='full_width of hdi', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'suppressed_frequencies': Parameter(name='', label='suppressed_frequencies of hdi', unit='Hz', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}*  
Required calibration data, may be nested

wave_i  
alias of [`HdDragI`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragI.html#iqm.pulse.playlist.hd_drag.HdDragI "iqm.pulse.playlist.hd_drag.HdDragI")

wave_q  
alias of [`HdDragQ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.hd_drag.HdDragQ.html#iqm.pulse.playlist.hd_drag.HdDragQ "iqm.pulse.playlist.hd_drag.HdDragQ")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_HdDrag](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d147bc9f414bbc4b7b07ee7882c9e834d801e3fd.png)
