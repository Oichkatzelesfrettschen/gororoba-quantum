> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_Samples.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_Samples.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 448e02ca97ff746058595c75e305c1be36f53aade11e085e5125707f145ce13c.

# PRX_Samples

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_Samples(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms")

See [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms").

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_Samples.dependent_waves "iqm.pulse.gates.prx.PRX_Samples.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`excluded_parameters`](#iqm.pulse.gates.prx.PRX_Samples.excluded_parameters "iqm.pulse.gates.prx.PRX_Samples.excluded_parameters") | Parameters names to be excluded from `self.parameters`. |
| [`parameters`](#iqm.pulse.gates.prx.PRX_Samples.parameters "iqm.pulse.gates.prx.PRX_Samples.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

excluded_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= \['duration'\]*  
Parameters names to be excluded from `self.parameters`. Inheriting classes may override this if certain parameters are not wanted in that class (also parameters defined by the waveforms can be excluded).

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'i': {'samples': Parameter(name='', label='I wave samples of Samples', unit='s', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}, 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'q': {'samples': Parameter(name='', label='Q wave samples of Samples', unit='s', data_type=\<DataType.COMPLEX: 2\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None)}}*  
Required calibration data, may be nested

wave_i  
alias of [`Samples`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Samples.html#iqm.models.playlist.waveforms.Samples "(in IQM data definitions v3.1.0)")

wave_q  
alias of [`Samples`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Samples.html#iqm.models.playlist.waveforms.Samples "(in IQM data definitions v3.1.0)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_Samples](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-403fec222fc55141651229f5a5067c2fb5e992c0.png)
