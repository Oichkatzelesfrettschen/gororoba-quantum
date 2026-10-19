> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0ec12b1560c848daee68a15e0543e29ebbe14afa54a33cddb0803ee4ad9f7d76.

# PRX_DRAGCosineRiseFall

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms")

PRX gate, DRAG / CosineRiseFall IQ pulse implementation.

See [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms").

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.dependent_waves "iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`excluded_parameters`](#iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.excluded_parameters "iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.excluded_parameters") | Parameters names to be excluded from `self.parameters`. |
| [`parameters`](#iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.parameters "iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

excluded_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= \['rise_time'\]*  
Parameters names to be excluded from `self.parameters`. Inheriting classes may override this if certain parameters are not wanted in that class (also parameters defined by the waveforms can be excluded).

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='center_offset of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'duration': Parameter(name='', label='pi pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='full_width of crf', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path='')}*  
Required calibration data, may be nested

wave_i  
alias of [`CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFall.html#iqm.models.playlist.waveforms.CosineRiseFall "(in IQM data definitions v3.1.0)")

wave_q  
alias of [`CosineRiseFallDerivative`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CosineRiseFallDerivative.html#iqm.models.playlist.waveforms.CosineRiseFallDerivative "(in IQM data definitions v3.1.0)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d12101a40f693884d4bd196ad2271b86dff9fa25.png)
