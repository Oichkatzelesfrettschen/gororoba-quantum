> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 079737a322894b74aada1e673d4bbe59179a10301f923934dbf30550ea043708.

# ScheduleBuilder

Module: [`iqm.pulse.builder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.html#module-iqm.pulse.builder "iqm.pulse.builder")

*class* iqm.pulse.builder.ScheduleBuilder(*op_table*, *calibration*, *station_properties*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Builds instruction schedules out of quantum circuits or individual quantum operations.

Encapsulates known quantum ops, the calibration information for them, QPU components and their topology, and controller properties.

Parameters:  
- **op_table** (*QuantumOpTable*) – definitions of known quantum ops

- **calibration** (*OpCalibrationDataTree*) – calibration data tree for the quantum ops

- **station_properties** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties")) – Static station properties, e.g. QPU topology and available control channels.

Attributes

|  |  |
|----|----|
| [`channels`](#iqm.pulse.builder.ScheduleBuilder.channels "iqm.pulse.builder.ScheduleBuilder.channels") | Station control channel properties. |
| [`chip_topology`](#iqm.pulse.builder.ScheduleBuilder.chip_topology "iqm.pulse.builder.ScheduleBuilder.chip_topology") | Station QPU topology. |
| [`component_channels`](#iqm.pulse.builder.ScheduleBuilder.component_channels "iqm.pulse.builder.ScheduleBuilder.component_channels") | Mapping from QPU component name to mapping from function to its controller. |
| [`feedback_sources`](#iqm.pulse.builder.ScheduleBuilder.feedback_sources "iqm.pulse.builder.ScheduleBuilder.feedback_sources") | Mapping from QPU component name to list of probes that can send feedback bits to control that component. |
| [`has_drive`](#iqm.pulse.builder.ScheduleBuilder.has_drive "iqm.pulse.builder.ScheduleBuilder.has_drive") | Set of QPU components that have a physical drive channel. |
| `barrier` |  |
| `prx` |  |
| `prx_12` |  |
| `cz` |  |
| `move` |  |
| `measure` |  |
| `measure_fidelity` |  |
| `measure_012` |  |
| `cc_prx` |  |
| [`composite_cache`](#iqm.pulse.builder.ScheduleBuilder.composite_cache "iqm.pulse.builder.ScheduleBuilder.composite_cache") | Cache for the CompositeGate TimeBoxes. |

Methods

|  |  |
|----|----|
| [`build_playlist`](#iqm.pulse.builder.ScheduleBuilder.build_playlist "iqm.pulse.builder.ScheduleBuilder.build_playlist") | Build a playlist from a number of instruction schedules. |
| [`circuit_to_timebox`](#iqm.pulse.builder.ScheduleBuilder.circuit_to_timebox "iqm.pulse.builder.ScheduleBuilder.circuit_to_timebox") | Convert a quantum circuit to a TimeBox. |
| [`get_cache`](#iqm.pulse.builder.ScheduleBuilder.get_cache "iqm.pulse.builder.ScheduleBuilder.get_cache") | Get a copy of the gate implementation cache. |
| [`get_calibration`](#iqm.pulse.builder.ScheduleBuilder.get_calibration "iqm.pulse.builder.ScheduleBuilder.get_calibration") | Calibration data for the given quantum operation, implementation and locus. |
| [`get_control_channels`](#iqm.pulse.builder.ScheduleBuilder.get_control_channels "iqm.pulse.builder.ScheduleBuilder.get_control_channels") | Control channels that directly affect quantum operations at the given locus. |
| [`get_drive_channel`](#iqm.pulse.builder.ScheduleBuilder.get_drive_channel "iqm.pulse.builder.ScheduleBuilder.get_drive_channel") | Drive channel for the given QPU component. |
| [`get_flux_channel`](#iqm.pulse.builder.ScheduleBuilder.get_flux_channel "iqm.pulse.builder.ScheduleBuilder.get_flux_channel") | Flux channel for the given QPU component. |
| [`get_implementation`](#iqm.pulse.builder.ScheduleBuilder.get_implementation "iqm.pulse.builder.ScheduleBuilder.get_implementation") | Provide an implementation for a quantum operation at a given locus. |
| [`get_implementation_class`](#iqm.pulse.builder.ScheduleBuilder.get_implementation_class "iqm.pulse.builder.ScheduleBuilder.get_implementation_class") | Implementation class for the given operation. |
| [`get_probe_channel`](#iqm.pulse.builder.ScheduleBuilder.get_probe_channel "iqm.pulse.builder.ScheduleBuilder.get_probe_channel") | Probe line channel for the probe line `component` belongs to. |
| [`get_virtual_feedback_channel_for`](#iqm.pulse.builder.ScheduleBuilder.get_virtual_feedback_channel_for "iqm.pulse.builder.ScheduleBuilder.get_virtual_feedback_channel_for") | Get the virtual fast feedback channel properties for a source component and a target component. |
| [`get_virtual_feedback_channel_names`](#iqm.pulse.builder.ScheduleBuilder.get_virtual_feedback_channel_names "iqm.pulse.builder.ScheduleBuilder.get_virtual_feedback_channel_names") | Get all the virtual fast feedback channel names for a source component and a feedback key. |
| [`has_calibration`](#iqm.pulse.builder.ScheduleBuilder.has_calibration "iqm.pulse.builder.ScheduleBuilder.has_calibration") | True iff there is calibration data for the given quantum operation, implementation and locus. |
| [`inject_calibration`](#iqm.pulse.builder.ScheduleBuilder.inject_calibration "iqm.pulse.builder.ScheduleBuilder.inject_calibration") | Inject new calibration data, changing `calibration` after initialisation. |
| [`inject_gate_definitions`](#iqm.pulse.builder.ScheduleBuilder.inject_gate_definitions "iqm.pulse.builder.ScheduleBuilder.inject_gate_definitions") | Inject gate definition updates, changing `op_table` after initialisation. |
| [`resolve_timebox`](#iqm.pulse.builder.ScheduleBuilder.resolve_timebox "iqm.pulse.builder.ScheduleBuilder.resolve_timebox") | Resolve a TimeBox. |
| [`timebox_to_schedule`](#iqm.pulse.builder.ScheduleBuilder.timebox_to_schedule "iqm.pulse.builder.ScheduleBuilder.timebox_to_schedule") | Resolve a TimeBox to an instruction schedule. |
| [`timeboxes_to_front_padded_playlist`](#iqm.pulse.builder.ScheduleBuilder.timeboxes_to_front_padded_playlist "iqm.pulse.builder.ScheduleBuilder.timeboxes_to_front_padded_playlist") | Temporary helper function, for converting a sequence of TimeBoxes to a Playlist. |
| [`timeboxes_to_playlist`](#iqm.pulse.builder.ScheduleBuilder.timeboxes_to_playlist "iqm.pulse.builder.ScheduleBuilder.timeboxes_to_playlist") | Convert a sequence of TimeBoxes to a Playlist. |
| [`validate_calibration`](#iqm.pulse.builder.ScheduleBuilder.validate_calibration "iqm.pulse.builder.ScheduleBuilder.validate_calibration") | Check that the calibration data matches the known quantum operations. |
| [`validate_quantum_circuit`](#iqm.pulse.builder.ScheduleBuilder.validate_quantum_circuit "iqm.pulse.builder.ScheduleBuilder.validate_quantum_circuit") | Validate a sequence of circuit operations constituting a quantum circuit. |
| [`wait`](#iqm.pulse.builder.ScheduleBuilder.wait "iqm.pulse.builder.ScheduleBuilder.wait") | Utility method for applying Block instructions on every channel of the given locus. |

composite_cache  
Cache for the CompositeGate TimeBoxes. Flushed whenever ANY calibration data is injected into the builder.

*property* chip_topology*: ChipTopology*  
Station QPU topology.

*property* channels*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ChannelProperties](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")\]*  
Station control channel properties.

*property* component_channels*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Mapping from QPU component name to mapping from function to its controller.

*property* has_drive*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Set of QPU components that have a physical drive channel.

*property* feedback_sources*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Mapping from QPU component name to list of probes that can send feedback bits to control that component.

inject_gate_definitions(*partial_gate_definitions*)  
Inject gate definition updates, changing `op_table` after initialisation.

Currently only supports updating the default implementation for quantum operations.

Parameters:  
**partial_gate_definitions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – gate definition data to be injected.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – if attempting to inject unsupported QuantumOp attributes.

Return type:  
*None*

inject_calibration(*partial_calibration*, *cache=None*)  
Inject new calibration data, changing `calibration` after initialisation.

Invalidates the GateImplementation caches for the affected operations/implementations/loci. Also invalidates the cache for any factorizable gate implementation, if any of its locus components was affected.

Parameters:  
- **partial_calibration** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\],* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]\]\]*) – data to be injected. Must have the same structure as `calibration` but does not have to contain all operations/implementations/loci/values. Only the parts of the data that are found will be merged into `calibration` (including any `None` values). `_cache` will be invalidated for the found operations/implementations/loci and only if the new calibration data actually differs from the previous.

- **cache** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\],* [*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]\]\]* *\|* *None*) – if an implementation cache is given, we do not invalidate the cache for affected loci, but instead fetch the implementations from the provided cache (if they exist there).

Return type:  
*None*

get_cache(*ops=None*, *implementations=None*, *loci=None*)  
Get a copy of the gate implementation cache.

Parameters:  
- **ops** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – limit to these QuantumOps.

- **implementations** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – limit to these GateImplementations.

- **loci** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]* *\|* *None*) – limit to these loci.

Returns:  
The gate implementation cache.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")\]\]\]

validate_calibration()  
Check that the calibration data matches the known quantum operations.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – there is something wrong with the calibration data

Return type:  
*None*

get_drive_channel(*component*)  
Drive channel for the given QPU component.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of a QPU component

Returns:  
Name of the drive channel for `component`, if it exists.

Raises:  
[**KeyError**](https://docs.python.org/3.11/library/exceptions.html#KeyError "(in Python v3.11)") – if component does not exist or does not have a drive channel

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_flux_channel(*component*)  
Flux channel for the given QPU component.

See [`get_drive_channel()`](#iqm.pulse.builder.ScheduleBuilder.get_drive_channel "iqm.pulse.builder.ScheduleBuilder.get_drive_channel").

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_probe_channel(*component*)  
Probe line channel for the probe line `component` belongs to.

See [`get_drive_channel()`](#iqm.pulse.builder.ScheduleBuilder.get_drive_channel "iqm.pulse.builder.ScheduleBuilder.get_drive_channel").

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of a QPU component (typically qubit) to probe

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_virtual_feedback_channel_names(*source_component*, *feedback_key*)  
Get all the virtual fast feedback channel names for a source component and a feedback key.

Parameters:  
- **source_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The QPU component that is being measured, sending the feedback bit.

- **feedback_key** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The feedback key.

Returns:  
A set of virtual fast feedback channel names that can be used to control the source component,  
associated with the given feedback key. If no such channels exist, an empty set is returned.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_virtual_feedback_channel_for(*source_component*, *target_component*)  
Get the virtual fast feedback channel properties for a source component and a target component.

Parameters:  
- **source_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The QPU component that is being measured, sending the feedback bit.

- **target_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The QPU component that is being controlled by the feedback bit.

Returns:  
The ChannelProperties for the virtual fast feedback channel.

Return type:  
[*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")

has_calibration(*op_name*, *impl_name*, *locus*)  
True iff there is calibration data for the given quantum operation, implementation and locus.

Parameters:  
- **op_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the quantum operation

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the implementation

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – locus of the operation

Returns:  
True iff requested calibration data was found.

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

get_calibration(*op_name*, *impl_name*, *locus*, *\**, *strict=True*)  
Calibration data for the given quantum operation, implementation and locus.

Parameters:  
- **op_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the quantum operation

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the implementation

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – locus of the operation

- **strict** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, raise an error if the calibration data is missing.

Returns:  
Requested calibration data, or an empty dict if `strict == False` and not found.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Requested calibration data was not found and `strict == True`.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_control_channels(*locus*)  
Control channels that directly affect quantum operations at the given locus.

Includes the probe, drive and flux channels of the locus QPU components. Does not include e.g. any neighboring coupler channels, these will have to be added separately in the TimeBox resolution phase.

Will only return channels that are known to exist, i.e. are found in [`ScheduleBuilder.channels`](#iqm.pulse.builder.ScheduleBuilder.channels "iqm.pulse.builder.ScheduleBuilder.channels").

Parameters:  
**locus** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – locus on which the operation acts

Returns:  
names of the control channels that directly affect the operation

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]

wait(*locus*, *duration*, *\**, *rounding=False*)  
Utility method for applying Block instructions on every channel of the given locus.

The Block instructions guarantee the locus components to idle for the given duration, and cannot e.g. be replaced with e.g. dynamical decoupling sequences. They are treated the same as any other TimeBox contents:

1.  Blocks on different channels remain aligned in time during scheduling.

2.  The actual waiting time on a particular channel may thus be \>= `duration`, if the other channels have less non-blocking space on either side.

Note

TODO For now, this method can round `duration` to the nearest value allowed by each channel if requested. This is for the benefit of EXA sweeping over waiting durations. In the future, EXA sweep generation should be responsible for doing the rounding.

Parameters:  
- **locus** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – locus components that should experience the wait

- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – how long to wait (in seconds)

- **rounding** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, for each channel separately, `duration` will be rounded to the nearest value allowed by the granularity of that channel. The Waits will start simultaneously.

Returns:  
box containing [`Block`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html#iqm.pulse.playlist.instructions.Block "iqm.pulse.playlist.instructions.Block") instructions on every control channel of `locus`

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

get_implementation(*op_name: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['prx', 'prx_12'\]*, *locus: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *impl_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *strict_locus: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *priority_calibration: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *priority_calibration_factorizable: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [PrxGateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PrxGateImplementation.html#iqm.pulse.gates.prx.PrxGateImplementation "iqm.pulse.gates.prx.PrxGateImplementation")\
get_implementation(*op_name: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['cz', 'move'\]*, *locus: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *impl_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *strict_locus: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *priority_calibration: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *priority_calibration_factorizable: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [FluxPulseGate](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate.html#iqm.pulse.gates.cz.FluxPulseGate "iqm.pulse.gates.cz.FluxPulseGate")\
get_implementation(*op_name: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['measure', 'measure_fidelity', 'measure_012'\]*, *locus: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *impl_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *strict_locus: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *priority_calibration: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *priority_calibration_factorizable: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [Measure_CustomWaveforms](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms")\
get_implementation(*op_name: [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['cc_prx'\]*, *locus: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *impl_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *strict_locus: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *priority_calibration: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *priority_calibration_factorizable: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [CCPRX_Composite](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite.html#iqm.pulse.gates.conditional.CCPRX_Composite "iqm.pulse.gates.conditional.CCPRX_Composite")\
get_implementation(*op_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *locus: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *impl_name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *\**, *strict_locus: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *priority_calibration: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *priority_calibration_factorizable: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [GateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")  
Provide an implementation for a quantum operation at a given locus.

The GateImplementations are built when they are first requested, and cached for later use.

For convenience, the returned implementation may use a permuted `locus` (and the calibration data associated with it) based on the following rules:

- If the operation is not symmetric (e.g. CX), different `locus` orders correspond to different operations, and thus the locus order may not be changed.

- If the operation is symmetric (e.g. CZ), all `locus` orders correspond to the same logical operation. However, symmetric operations may have non-symmetric implementations.

  - If the chosen implementation is symmetric, we order `locus` numerically (not lexicographically!), so that we only need to have calibration data for one locus order.

  - Otherwise, if `strict_locus` is False, we check all permutations of `locus`, and pick the first one that has calibration data available. The original order is checked first. If `strict_locus` is True, only the original order may be used.

The attributes `QuantumOp.factorizable`, `GateImplementation.needs_calibration` and whether the implementation is a `CompositeGate` interact in a nontrivial way. Examples of their currently used combinations:

| composite / not composite | factorizable | not factorizable |
|----|----|----|
| needs_calibration | `measure_fidelity.shelved_constant` / `measure.constant` | `cc_prx.prx_composite` / `prx.drag_crf` |
| not needs_calibration | `reset.conditional` / not meaningful | `rz.prx_composite` / `rz.virtual` |

Parameters:  
- **op_name** – Name of the quantum operation.

- **locus** – Locus of the operation.

- **impl_name** – Name of the implementation. `None` means the implementation is chosen automatically using [`QuantumOp.get_default_implementation_for_locus()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp.get_default_implementation_for_locus "iqm.pulse.quantum_ops.QuantumOp.get_default_implementation_for_locus").

- **strict_locus** – Only has an effect if the operation is symmetric (e.g. CZ). Iff False and the chosen *implementation* is non-symmetric, the locus order may be changed if no calibration data is available for the requested locus order.

- **priority_calibration** – Single-locus calibration data to override the common calibration data in `calibration`. Any non-None values found in `priority_calibration` will be merged to the common calibration. If used, `impl_name` must not be None since `priority_calibration` is implementation-specific. Note: using `priority_calibration` will prevent caching.

- **priority_calibration_factorizable** – Like `priority_calibration`, but for factorizable QuantumOps. Mapping from single-qubit loci to overrides of their calibration data.

Returns:  
Requested implementation.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Requested implementation could not be provided.

get_implementation_class(*op_name*, *impl_name=None*)  
Implementation class for the given operation.

Parameters:  
- **op_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the quantum operation.

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Name of the implementation (`None` means use the global default implementation).

Returns:  
requested implementation class

Return type:  
[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")\]

validate_quantum_circuit(*operations*, *\**, *require_measurements=False*)  
Validate a sequence of circuit operations constituting a quantum circuit.

Parameters:  
- **operations** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*\]*) – quantum circuit to be validated

- **require_measurements** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – iff True the circuit must include at least one measurement operation

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `operations` do not constitute a valid quantum circuit

Return type:  
*None*

circuit_to_timebox(*circuit*, *\**, *name=''*, *scheduling=SchedulingStrategy.ASAP*, *scheduling_algorithm=SchedulingAlgorithm.HARD_BOUNDARY*, *locus_mapping=None*)  
Convert a quantum circuit to a TimeBox.

Parameters:  
- **circuit** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*\]*) – quantum circuit

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the circuit

- **scheduling** ([*SchedulingStrategy*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy")) – scheduling strategy (e.g. ASAP or ALAP) to be used in resolving the TimeBoxes.

- **scheduling_algorithm** ([*SchedulingAlgorithm*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm")) – scheduling algorithm to be used in resolving the TimeBoxes.

- **locus_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – optional mapping of placeholder component names to the physical component names used while resolving the circuit into a TimeBox.

Returns:  
unresolved TimeBox that implements `circuit`

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – failed to convert `circuit` to a TimeBox

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

timeboxes_to_front_padded_playlist(*boxes*, *\**, *neighborhood=0*)  
Temporary helper function, for converting a sequence of TimeBoxes to a Playlist.

Each individual TimeBox in `boxes` is resolved into a Schedule, and then each schedule is front-padded with [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions on each channel such that the resulting Schedules have equal durations. This is required since for now in Station Control the delay before the final measurement is the same for all the Schedules in a Playlist, and we do not wish to lose coherence waiting for the measurement after each Schedule is done.

TODO Once Station Control can handle measurements better, this method should be removed, and [`timeboxes_to_playlist()`](#iqm.pulse.builder.ScheduleBuilder.timeboxes_to_playlist "iqm.pulse.builder.ScheduleBuilder.timeboxes_to_playlist") be used instead.

Parameters:  
- **boxes** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")*\]*) – TimeBoxes to include in the playlist

- **neighborhood** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – During scheduling, block neighboring channels of the used components this far. By default, blocks only the defined locus components and any other components which have occupied channels.

Returns:  
playlist that implements `boxes` and the readout metrics for that playlist.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)"), [*ReadoutMetrics*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutMetrics.html#iqm.pulse.playlist.instructions.ReadoutMetrics "iqm.pulse.playlist.instructions.ReadoutMetrics")\]

timeboxes_to_playlist(*boxes*, *\**, *neighborhood=1*)  
Convert a sequence of TimeBoxes to a Playlist.

Resolves the boxes, converts them to Schedules, removes unnecessary channels, and then packs the Schedules into a Playlist. Assumes all the TimeBoxes refer to the same QPU and its control channels.

Parameters:  
- **boxes** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")*\]*) – TimeBoxes to include in the playlist

- **neighborhood** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – During scheduling, block neighboring channels of the used components this far. The default value ensures that quantum operations work as intended, assuming the station is properly calibrated. Higher values may help defend against crosstalk, at the expense of a longer instruction schedule and thus more decoherence.

Returns:  
playlist that implements `boxes`

Return type:  
[*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)")

timebox_to_schedule(*box*, *\**, *neighborhood=1*)  
Resolve a TimeBox to an instruction schedule.

Parameters:  
- **box** ([*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")) – TimeBox to resolve

- **neighborhood** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – During scheduling, block neighboring channels of the used components this far. The default value ensures that quantum operations work as intended, assuming the station is properly calibrated. Higher values may help defend against crosstalk, at the expense of a longer instruction schedule and thus more decoherence.

Returns:  
Schedule that implements `box`.

Return type:  
[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

resolve_timebox(*box*, *\**, *neighborhood*, *compute_neighborhood_hard_boundary=False*)  
Resolve a TimeBox.

Resolves recursively each of the children of the box, and then concatenates the resulting Schedules into a new one using a specific scheduling strategy and algorithm.

The supported algorithms are `HARD_BOUNDARY`, which treats each composite TimeBox as a solid rectangle (the longest channel within defines the duration) and `TETRIS`, which packs the schedule as tightly as possible (solid instructions still cannot overlap) regardless of the TimeBox boundaries.

Modifies `box` so that it becomes atomic, if it isn’t already.

Parameters:  
- **box** ([*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")) – TimeBox to resolve

- **neighborhood** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – During scheduling, block control channels of neighboring QPU components this far from the locus. Values higher than 0 may help defend against crosstalk, at the expense of a longer instruction schedule and thus more decoherence.

- **compute_neighborhood_hard_boundary** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to precompute the neighborhood components while resolving a composite `TimeBox` in the `HARD_BOUNDARY` algorithm. Typically one does not want to do this on the top layer composite `TimeBox`, since it would be unused. The algorithm sets this `True` on lower layers, where it improves the performance as the neighborhood components are needed in scheduling.

Returns:  
instruction schedule that implements `box`

Return type:  
[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")

build_playlist(*schedules*, *finish_schedules=True*)  
Build a playlist from a number of instruction schedules.

This involves compressing the schedules so that no duplicate information needs to be transferred to Station Control.

Parameters:  
- **schedules** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")*\]*) – Instruction schedules to include in the playlist.

- **finish_schedules** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to finalise the schedules (by calling `_finish_schedule()`) before building the playlist. Should be set `True` unless some process has already finalised them before calling this function.

Returns:  
- playlist consisting of the compressed `schedules`

- readout metrics for the playlist

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `schedules` cannot be converted into a valid Playlist.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)"), [*ReadoutMetrics*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutMetrics.html#iqm.pulse.playlist.instructions.ReadoutMetrics "iqm.pulse.playlist.instructions.ReadoutMetrics")\]

Inheritance

![Inheritance diagram of iqm.pulse.builder.ScheduleBuilder](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-fefa7f8c817a9972465754e3224fb6760852cf1d.png)
