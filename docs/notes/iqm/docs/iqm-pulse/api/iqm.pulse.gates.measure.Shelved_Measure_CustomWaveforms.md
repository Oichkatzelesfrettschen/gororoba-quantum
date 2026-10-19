> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ceda670baa3b8d5309582e0fa25357a7009241fa7465eb5c575b0dfd9b0202b8.

# Shelved_Measure_CustomWaveforms

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms"), [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")

Base class for shelved readout.

Shelved readout applies a `prx_12(pi)` gate before and after a standard dispersive readout on each qubit measured. The first `prx_12(pi)` swaps the amplitudes of the \\\|1\rangle\\ and \\\|2\rangle\\ states, and the second one swaps them back after the measurement has (roughly) collapsed the state. If the discriminator of the readout is calibrated such that the \\\|0\rangle\\ state is on one side and the \\\|1\rangle\\ and \\\|2\rangle\\ states are on the other, the end result is equivalent to the standard readout operation but with the advantage that the population in the \\\|2\rangle\\ state is less susceptible to \\T_1\\ decay during the readout than the population in the \\\|1\rangle\\ state.

Attributes

|  |  |
|----|----|
| [`customizable_gates`](#iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.customizable_gates "iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.customizable_gates") | These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. |
| [`dependent_waves`](#iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.dependent_waves "iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`registered_gates`](#iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.registered_gates "iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.registered_gates") | Names of the member operations used by the composite gate. |
| [`root_parameters`](#iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.root_parameters "iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.root_parameters") | Parameters independent of the of Waveforms. |
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

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting\]* *= {'acquisition_delay': Parameter(name='', label='Acquisition delay', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'acquisition_type': Setting(parameter=Parameter(name='', label='Acquisition type', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value='threshold', read_only=False, path=''), 'amplitude_i': Parameter(name='', label='Readout channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Setting(parameter=Parameter(name='', label='Readout channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'block_neighbors': Setting(parameter=Parameter(name='Block neighbors', label='Whether to block neighboring qubits in multiplexing', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=False, read_only=False, path=''), 'do_prx_12': Setting(parameter=Parameter(name='do_prx_12', label='Whether to do the prx_12 flips in the measure operation', unit='', data_type=\<DataType.BOOLEAN: 4\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=True, read_only=False, path=''), 'duration': Parameter(name='', label='Readout pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'frequency': Parameter(name='', label='Readout pulse frequency', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_length': Parameter(name='', label='Integration length', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_threshold': Parameter(name='', label='Integration threshold', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_weights_I': Setting(parameter=Parameter(name='', label='Integration weights for channel I', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), value=array(\[\], dtype=float64), read_only=False, path=''), 'integration_weights_Q': Setting(parameter=Parameter(name='', label='Integration weights for channel Q', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), value=array(\[\], dtype=float64), read_only=False, path=''), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'second_prx_12_offset': Setting(parameter=Parameter(name='second_prx_12_offset', label='Offset of the second PRX_12 pulse from the end the ReadoutTrigger', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path='')}*  
Parameters independent of the of Waveforms. Inheriting classes may override this to include parameters common to all such implementations.

registered_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('prx_12',)*  
Names of the member operations used by the composite gate. There must be corresponding keys in `builder.op_table`.

customizable_gates*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= ('prx_12',)*  
These member operations can be calibrated separately from their common calibration by adding `OCalibrationData` nodes for them under the `OILCalibrationData` node of the composite gate. Must be a subset of [`registered_gates`](#iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.registered_gates "iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.registered_gates"). By default all member operations are customizable.

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-9cca8bfdf49b6b8ea4d9ad440cadfdd04f40e2d8.png)
