> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 616849c9f5f571f53a72c976f4752f5d369a2b00ad52c79619e13bad37c3c70f.

# ProbePulse_CustomWaveforms

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.ProbePulse_CustomWaveforms(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms")

Base class for implementing a probe line measurement pulse with custom waveforms in the I and Q channels.

With given `Waveform` waveform definitions `Something` and `SomethingElse`, you may define a measurement implementation that uses them as follows: `class MyGate(ProbePulse_CustomWaveforms, i_wave=Something, q_wave=SomethingElse)`. The measurement [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") instruction will not be automatically modulated by any frequency, so any modulations should be included in the I and Q waveforms themselves.

Due to device limitations this implementation also has to integrate the readout signal (using arbitrary weights), even though it does not make much sense.

Contrary to the `Measure_CustomWaveforms` class, this implementation acts on probe lines directly (i.e. its `locus` is a single probe line) as it is intended to be used in contexts where well-defined qubits may not have been characterized yet (such as readout frequency calibration with a chirp pulse).

Attributes

|  |  |
|----|----|
| [`dependent_waves`](#iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.dependent_waves "iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.dependent_waves") | If set `True`, the Q channel waveform is considered to depend on the I channel's waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). |
| [`root_parameters`](#iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.root_parameters "iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.root_parameters") | Parameters independent of the of Waveforms. |
| `wave_i` | Waveform for the I channel. |
| `wave_q` | Waveform for the Q channel. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.locus_mapping_function "iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.locus_mapping_function") | One-component loci on probe lines. |
| [`time_trace`](#iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.time_trace "iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.time_trace") | Returns a multiplexed simultaneous measurement with an additional time trace acquisition. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting\]* *= {'acquisition_delay': Parameter(name='', label='Acquisition delay', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_i': Parameter(name='', label='Readout channel I amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='Readout channel Q amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='Readout pulse duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'integration_length': Parameter(name='', label='Integration length', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'phase': Parameter(name='', label='Readout pulse phase', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Parameters independent of the of Waveforms. Inheriting classes may override this to include parameters common to all such implementations.

locus_mapping_function()  
One-component loci on probe lines.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

time_trace(*key=''*, *\*\*kwargs*)  
Returns a multiplexed simultaneous measurement with an additional time trace acquisition.

The returned `MeasureBoxes` are the same as the one returned by `__call__()` except the time trace acquisition is appended to the acquisitions of each probe line’s `ReadoutTrigger` instruction.

Parameters:  
- **key** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Readout results generated on this trigger will be used to assigned to `f"{qubit}__{key}"`, where `qubit` goes over the component names in `self.locus`, whereas the recorded time traces will be assigned to `f"{probe_line}__{key}"` where `probe_line` goes through all the probe lines associated with `self.locus`. If empty, the key `"readout.result"` will be used for integrated results and the key `"readout.time_trace"` for the recorded time traces.

- **acquisition_delay** – optionally override the time trace acquisition delay with this value (given in seconds). Does not affect the acquisition delays of the integrated measurements.

- **acquisition_duration** – optionally override the time trace acquisition duration with this value (given in seconds). Does not affect the integration lengths of the integrated measurements.

- **feedback_key** – The signals generated by the integration are routed using this label, prefixed by the component. See `__call__()`.

Returns:  
TimeBox containing the ReadoutTrigger instruction.

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

dependent_waves*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
If set `True`, the Q channel waveform is considered to depend on the I channel’s waveform so that they share the waveform parameters, (e.g. a DRAG PRX implementation). If not provided, will be initialised as `True`.

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.ProbePulse_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-ae1cdafc6e8b373ac3ddf4cf965ace478ba12e67.png)
