> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bf199b86aaac9c5b8145ef75ded22c4925eb86d5ba3eabc70574a3c8c64fbd67.

# PRX_CustomWaveforms

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.PRX_CustomWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PRX_SinglePulse_GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation.html#iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation "iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation"), [`CustomIQWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CustomIQWaveforms.html#iqm.pulse.gate_implementation.CustomIQWaveforms "iqm.pulse.gate_implementation.CustomIQWaveforms")

Base class for PRX gates implemented using a single IQ pulse and hot-swappable waveforms.

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.prx.PRX_CustomWaveforms.dependent_waves "iqm.pulse.gates.prx.PRX_CustomWaveforms.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`root_parameters`](#iqm.pulse.gates.prx.PRX_CustomWaveforms.root_parameters "iqm.pulse.gates.prx.PRX_CustomWaveforms.root_parameters") | Parameters independent of the of Waveforms. |
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

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting\]* *= {'amplitude_i': Parameter(name='', label='pi pulse I channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='pi pulse Q channel amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='pi pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'modulation_frequency': Setting(parameter=Parameter(name='', label='modulation frequency of the waveforms', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path='')}*  
Parameters independent of the of Waveforms. Inheriting classes may override this to include parameters common to all such implementations.

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.PRX_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-2c87e1d04508a659803a1e69bbd47076e3831699.png)
