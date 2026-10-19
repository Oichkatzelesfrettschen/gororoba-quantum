> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Factorizable.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Factorizable.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f125f4c4878b9a94e469b98344d60e6c4e03d3c7e371e0ff8a8d520bbdd31ca9.

# Measure_Factorizable

Module: [`iqm.pulse.gates.measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure")

*class* iqm.pulse.gates.measure.Measure_Factorizable(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Base class for implementing a factorizable measure.

The `measure` operation is factorizable, and its `arity` is 0, which together mean that it can operate on loci of any length, but is calibrated only on single component loci. When the gate is constructed in the `len(locus) > 1` case (e.g. `builder.get_implementation('measure', ('QB1', 'QB2', 'QB3'))()` ), the resulting [`MeasureBoxes`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes") is constructed from the calibrated single-component implementations.

Attributes

|  |  |
|----|----|
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.measure.Measure_Factorizable.duration_in_seconds "iqm.pulse.gates.measure.Measure_Factorizable.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |
| [`locus_mapping_function`](#iqm.pulse.gates.measure.Measure_Factorizable.locus_mapping_function "iqm.pulse.gates.measure.Measure_Factorizable.locus_mapping_function") | One-qubit loci with readout. |
| [`time_trace`](#iqm.pulse.gates.measure.Measure_Factorizable.time_trace "iqm.pulse.gates.measure.Measure_Factorizable.time_trace") | Returns a multiplexed simultaneous measurement with an additional time trace acquisition. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

locus_mapping_function()  
One-qubit loci with readout.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

time_trace(*key=''*, *acquisition_delay=None*, *acquisition_duration=None*, *feedback_key=''*)  
Returns a multiplexed simultaneous measurement with an additional time trace acquisition.

The returned `MeasureBoxes` are the same as the one returned by `__call__()` except the time trace acquisition is appended to the acquisitions of each probe line’s `ReadoutTrigger` instruction.

Parameters:  
- **key** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Readout results generated on this trigger will be used to assigned to `f"{qubit}__{key}"`, where `qubit` goes over the component names in `self.locus`, whereas the recorded time traces will be assigned to `f"{probe_line}__{key}"` where `probe_line` goes through all the probe lines associated with `self.locus`. If empty, the key `"readout.result"` will be used for integrated results and the key `"readout.time_trace"` for the recorded time traces.

- **acquisition_delay** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – optionally override the time trace acquisition delay with this value (given in seconds). Does not affect the acquisition delays of the integrated measurements.

- **acquisition_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – optionally override the time trace acquisition duration with this value (given in seconds). Does not affect the integration lengths of the integrated measurements.

- **feedback_key** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The signals generated by the integration are routed using this label, prefixed by the component. See `__call__()`.

Returns:  
TimeBox containing the ReadoutTrigger instruction.

Return type:  
[*MeasureBoxes*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes")

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure.Measure_Factorizable](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8c275042c8d2b26c3986584a19b58a5c415dd1cb.png)
