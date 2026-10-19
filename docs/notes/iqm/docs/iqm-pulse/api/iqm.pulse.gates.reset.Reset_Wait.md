> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_Wait.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_Wait.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2fcf2862609dfde7f8ff5d15f80b6adc23eecbc6205df39e3de5288f2e2129f0.

# Reset_Wait

Module: [`iqm.pulse.gates.reset`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html#module-iqm.pulse.gates.reset "iqm.pulse.gates.reset")

*class* iqm.pulse.gates.reset.Reset_Wait(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Reset operation by relaxation (idling for a time comparable to the relaxation time of the component).

Adds a Wait pulse for all the (non-virtual) channels of the locus components. In addition, blocks all the probes associated with the locus and in case the locus is connected via couplers, blocks them as well. The operation is factorizable, so that the calibration data it uses (i.e. the wait duration in seconds) is defined for each component, and when acting on multiple components, the maximum of the associated wait durations will be applied.

Reset by relaxation is intended to be used in the circuit initialisation between shots / segments. It also can be called on specific qubits inside a segment, but as it works by waiting longer than the qubit relaxation time, the states of all the other qubits will likely have been destroyed as well by the time the reset has finished.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.reset.Reset_Wait.parameters "iqm.pulse.gates.reset.Reset_Wait.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.reset.Reset_Wait.duration_in_seconds "iqm.pulse.gates.reset.Reset_Wait.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |
| [`locus_mapping_function`](#iqm.pulse.gates.reset.Reset_Wait.locus_mapping_function "iqm.pulse.gates.reset.Reset_Wait.locus_mapping_function") | One-component loci that have at least one channel. |
| [`wait_box`](#iqm.pulse.gates.reset.Reset_Wait.wait_box "iqm.pulse.gates.reset.Reset_Wait.wait_box") | TimeBox that contains Wait instructions for all non-virtual channels associated with `self.locus`. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

parameters*: NestedParams* *= {'duration': Parameter(name='', label='Wait duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

locus_mapping_function()  
One-component loci that have at least one channel.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

wait_box()  
TimeBox that contains Wait instructions for all non-virtual channels associated with `self.locus`.

Does not block any additional components beside the locus itself.

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.reset.Reset_Wait](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-9712168006070fe6d044444c3fa0ac7eee3afdcf.png)
