> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a0a95cf9cac0b8a69eea5047645e664e8552d65db08e27b8525b3c38b31f7203.

# Measure_CustomWaveforms

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.Measure_CustomWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CustomIQWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CustomIQWaveforms.html#iqm.pulse.gate_implementation.CustomIQWaveforms "iqm.pulse.gate_implementation.CustomIQWaveforms"), [`Measure_Factorizable`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Factorizable.html#iqm.pulse.gates.measure.Measure_Factorizable "iqm.pulse.gates.measure.Measure_Factorizable")

Base class for implementing dispersive measurement operations with custom probe pulse waveforms.

You may define a measurement implementation that uses the `Waveform` instances `Something` and `SomethingElse` as the probe pulse waveforms in the I and Q channels as follows: `class MyGate(Measure_CustomWaveforms, i_wave=Something, q_wave=SomethingElse)`.

The `measure` operation is factorizable, and its `arity` is 0, which together mean that it can operate on loci of any length, but is calibrated only on single component loci.

For each measured component, the readout [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") will be modulated with the intermediate frequency (IF), computed as the difference between the readout frequency of that component and the probe line center frequency, and offset in phase by the readout phase of the component.

The measurement is implemented using a [`ReadoutTrigger`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html#iqm.pulse.playlist.instructions.ReadoutTrigger "iqm.pulse.playlist.instructions.ReadoutTrigger") instruction, with a duration set by the requirements of the acquisition(s). Note that this is typically different from `gates.measure.constant.{locus}.duration`, which is the probe pulse duration.

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.measure.Measure_CustomWaveforms.dependent_waves "iqm.pulse.gates.measure.Measure_CustomWaveforms.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`root_parameters`](#iqm.pulse.gates.measure.Measure_CustomWaveforms.root_parameters "iqm.pulse.gates.measure.Measure_CustomWaveforms.root_parameters") | Parameters independent of the of Waveforms. |
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

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting\]* *= {'acquisition_delay': Parameter(name='', label='Acquisition delay', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'acquisition_type': Setting(parameter=Parameter(name='', label='Acquisition type', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value='threshold', read_only=False, path=''), 'amplitude_i': Parameter(name='', label='Readout channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Setting(parameter=Parameter(name='', label='Readout channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'block_neighbors': Setting(parameter=Parameter(name='Block neighbors', label='Whether to block neighboring qubits in multiplexing', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=False, read_only=False, path=''), 'duration': Parameter(name='', label='Readout pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'frequency': Parameter(name='', label='Readout pulse frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_length': Parameter(name='', label='Integration length', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_threshold': Parameter(name='', label='Integration threshold', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_weights_I': Setting(parameter=Parameter(name='', label='Integration weights for channel I', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), value=array(\[\], dtype=float64), read_only=False, path=''), 'integration_weights_Q': Setting(parameter=Parameter(name='', label='Integration weights for channel Q', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), value=array(\[\], dtype=float64), read_only=False, path=''), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Parameters independent of the of Waveforms. Inheriting classes may override this to include parameters common to all such implementations.

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.Measure_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-85f0a6b3c2d74f43a5298ad9123ad2c739b97508.png)
