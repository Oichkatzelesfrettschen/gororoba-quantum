> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dcc78e1110b5a4995840339a10a66a2ca41f6c2d8fa2b1f4788cc962734fdb9e.

# GateImplementation

Module: [`iqm.pulse.gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html#module-iqm.pulse.gate_implementation "iqm.pulse.gate_implementation")

*class* iqm.pulse.gate_implementation.GateImplementation(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

ABC for implementing quantum gates and other quantum operations using instruction schedules.

Every implementation of every operation type can have its own GateImplementation subclass. Each GateImplementation instance represents a particular locus for that implementation, and encapsulates the calibration data it requires.

All GateImplementation subclasses `__init__()` must have exactly the below arguments in order to be usable via [`ScheduleBuilder.get_implementation()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder.get_implementation "iqm.pulse.builder.ScheduleBuilder.get_implementation").

GateImplementation also has the `__call__()` method, which takes the operation parameters (e.g. rotation angles) as input, and builds, caches and then returns a [`TimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") instance which implements an instance of the operation at that locus. `__call__()` normally should not be reimplemented by the subclasses, instead they should define `_call()` which contains the actual implementation without the caching logic.

Even though it is possible, GateImplementations *should not* use other gates to implement themselves, unless they are subclasses of [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate"). This is to encapsulate the calibration data better, and avoid unpredictable dependencies between gates.

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")) – Quantum operation this instance implements.

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the implementation provided by this instance.

- **locus** (*Locus*) – Locus the operation acts on.

- **calibration_data** (*OILCalibrationData*) – (Raw) calibration data for the (operation, implementation, locus) represented by this instance.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder")) – Schedule builder instance that can be used to access system properties (and in the case of [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate"), other gates).

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gate_implementation.GateImplementation.parameters "iqm.pulse.gate_implementation.GateImplementation.parameters") | Required calibration data, may be nested |
| [`qualified_name`](#iqm.pulse.gate_implementation.GateImplementation.qualified_name "iqm.pulse.gate_implementation.GateImplementation.qualified_name") | Qualified name of the implementation. |
| [`symmetric`](#iqm.pulse.gate_implementation.GateImplementation.symmetric "iqm.pulse.gate_implementation.GateImplementation.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| [`id`](#iqm.pulse.gate_implementation.GateImplementation.id "iqm.pulse.gate_implementation.GateImplementation.id") | Unique str identifier, needed for certain caching properties. |
| [`sub_implementations`](#iqm.pulse.gate_implementation.GateImplementation.sub_implementations "iqm.pulse.gate_implementation.GateImplementation.sub_implementations") | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`build_setting_node`](#iqm.pulse.gate_implementation.GateImplementation.build_setting_node "iqm.pulse.gate_implementation.GateImplementation.build_setting_node") | Build the gate calibration settings tree node. |
| [`construct_aggregator`](#iqm.pulse.gate_implementation.GateImplementation.construct_aggregator "iqm.pulse.gate_implementation.GateImplementation.construct_aggregator") | Construct an aggregator implementation for a factorizable operation. |
| [`convert_calibration_data`](#iqm.pulse.gate_implementation.GateImplementation.convert_calibration_data "iqm.pulse.gate_implementation.GateImplementation.convert_calibration_data") | Convert time- and frequency-like items in the calibration data to fractions of the time duration of the gate. |
| [`duration_in_seconds`](#iqm.pulse.gate_implementation.GateImplementation.duration_in_seconds "iqm.pulse.gate_implementation.GateImplementation.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |
| [`get_locus_mapping`](#iqm.pulse.gate_implementation.GateImplementation.get_locus_mapping "iqm.pulse.gate_implementation.GateImplementation.get_locus_mapping") | Get the locus mapping for this GateImplementation. |
| [`get_parameters`](#iqm.pulse.gate_implementation.GateImplementation.get_parameters "iqm.pulse.gate_implementation.GateImplementation.get_parameters") | Default calibration data tree the GateImplementation subclass expects for each locus. |
| [`locus_mapping_function`](#iqm.pulse.gate_implementation.GateImplementation.locus_mapping_function "iqm.pulse.gate_implementation.GateImplementation.locus_mapping_function") | One-qubit loci. |
| [`may_have_calibration`](#iqm.pulse.gate_implementation.GateImplementation.may_have_calibration "iqm.pulse.gate_implementation.GateImplementation.may_have_calibration") | True iff the implementation may have calibration data. |
| [`needs_calibration`](#iqm.pulse.gate_implementation.GateImplementation.needs_calibration "iqm.pulse.gate_implementation.GateImplementation.needs_calibration") | True iff the implementation class needs calibration parameter data. |
| [`optional_calibration_keys`](#iqm.pulse.gate_implementation.GateImplementation.optional_calibration_keys "iqm.pulse.gate_implementation.GateImplementation.optional_calibration_keys") | Optional calibration data keys for this class, in addition to the required items in [`parameters`](#iqm.pulse.gate_implementation.GateImplementation.parameters "iqm.pulse.gate_implementation.GateImplementation.parameters"). |
| [`to_timebox`](#iqm.pulse.gate_implementation.GateImplementation.to_timebox "iqm.pulse.gate_implementation.GateImplementation.to_timebox") | Wraps the given instruction schedule into an atomic/resolved timebox. |

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Parameter](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)") \| [Setting](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "(in iqm-exa-common v29.0.0)") \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]* *= {}*  
Required calibration data, may be nested

locus_mapping_function()  
Locus mapping function [`get_locus_mapping()`](#iqm.pulse.gate_implementation.GateImplementation.get_locus_mapping "iqm.pulse.gate_implementation.GateImplementation.get_locus_mapping") uses.

For convenience the default is “all one-qubit loci”.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

id  
Unique str identifier, needed for certain caching properties.

sub_implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [GateImplementation](#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")\]*  
Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. At least one of self.sub_implementations and self.calibration_data is always empty.

*property* qualified_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Qualified name of the implementation.

*classmethod* needs_calibration()  
True iff the implementation class needs calibration parameter data.

Does not include the calibration data of [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate") member gates.

Returns:  
True iff [`OpCalibrationDataTree`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OpCalibrationDataTree.html#iqm.pulse.gate_implementation.OpCalibrationDataTree "iqm.pulse.gate_implementation.OpCalibrationDataTree") must contain a node `f"{self.parent.name}.{self.name}.{self.locus}` for the calibration data this instance needs.

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

*classmethod* optional_calibration_keys()  
Optional calibration data keys for this class, in addition to the required items in [`parameters`](#iqm.pulse.gate_implementation.GateImplementation.parameters "iqm.pulse.gate_implementation.GateImplementation.parameters").

These keys are not required to be present in [`OILCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OILCalibrationData.html#iqm.pulse.gate_implementation.OILCalibrationData "iqm.pulse.gate_implementation.OILCalibrationData") when validating it. E.g. custom calibration keys for [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate") member gates.

Returns:  
Optional top-level calibration data keys.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]

*final classmethod* may_have_calibration()  
True iff the implementation may have calibration data.

Returns:  
True iff [`OpCalibrationDataTree`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OpCalibrationDataTree.html#iqm.pulse.gate_implementation.OpCalibrationDataTree "iqm.pulse.gate_implementation.OpCalibrationDataTree") may contain a node `"{self.parent.name}.{self.name}.{self.locus}` for the calibration data of this instance.

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

*final classmethod* construct_aggregator(*parent*, *name*, *locus*, *builder*, *sub_implementations*)  
Construct an aggregator implementation for a factorizable operation.

Instead of calibration data this method is given `sub_implementations`, which contains single-qubit implementations for all the components in `locus`.

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

- **sub_implementations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*GateImplementation*](#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]*)

Return type:  
[*GateImplementation*](#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

*final* to_timebox(*schedule*)  
Wraps the given instruction schedule into an atomic/resolved timebox.

Parameters:  
**schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule"))

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

*final classmethod* convert_calibration_data(*calibration_data*, *params*, *channel_props*, *\**, *duration=None*, *\_top_level=True*)  
Convert time- and frequency-like items in the calibration data to fractions of the time duration of the gate.

This is a convenience method for converting calibration data items involving time durations measured in seconds and frequencies measured in Hz into fractions of the duration of the gate, e.g. to be used to parameterize `Waveform` classes.

- Values of items that are not measured in seconds or Hz are returned as is.

- Items named `duration` get special treatment for convenience. They are not included in the converted data. If the `duration` parameter is None, there must be a `"duration"` item at the top level in `calibration_data` whose value will be used instead.

- The `duration` parameter is converted to channel samples and included in the converted data under the top-level key `"n_samples"`.

Parameters:  
- **calibration_data** (*OILCalibrationData*) – (subset of) calibration data for the gate/implementation/locus

- **params** (*NestedParams*) – (subset of) `cls.parameters` specifying the `calibration_data` items to convert and return

- **channel_props** ([*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")) – used to convert `"duration"` from seconds into channel samples

- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – Time duration of the gate, in seconds. If None, `calibration_data` must have an item named `"duration"`, measured in seconds, which will be used instead.

- **\_top_level** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Returns:  
converted `calibration_data` items

Return type:  
OILCalibrationData

*final classmethod* get_parameters(*locus*, *path=()*, *\**, *use_defaults=True*)  
Default calibration data tree the GateImplementation subclass expects for each locus.

Formats the [`parameters`](#iqm.pulse.gate_implementation.GateImplementation.parameters "iqm.pulse.gate_implementation.GateImplementation.parameters") class attribute into a tree of `SettingNode` objects, replacing any wildcard characters.

Parameters:  
- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – Locus component names to replace the wildcard character `"*"` in the calibration parameter names. One `Setting` will be generated for each component name in `locus`. If there are no wildcard characters in `cls.parameters`, this argument has no effect.

- **path** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – parts of the dotted name for the root node, if any.

- **use_defaults** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, return default values for calibration data items that have one.

Returns:  
EXA setting node describing the required calibration data for each locus. The setting values are `None`, unless the corresponding gate parameter has a default value.

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")

*classmethod* build_setting_node(*locus*, *station_properties*, *path=()*, *\**, *use_defaults=True*)  
Build the gate calibration settings tree node.

By default, uses [`get_parameters()`](#iqm.pulse.gate_implementation.GateImplementation.get_parameters "iqm.pulse.gate_implementation.GateImplementation.get_parameters") to build the node, but can be overridden by subclasses if needed (e.g. if the node structure needs to be aware of the `station_properties`).

Parameters:  
- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – Locus component names to replace the wildcard character `"*"` in the calibration parameter names. One `Setting` will be generated for each component name in `locus`. If there are no wildcard characters in `cls.parameters`, this argument has no effect.

- **station_properties** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties")) – The station properties. By default, not used, but subclasses may override this method in order to implement topology or control channel specific node structures.

- **path** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – parts of the dotted name for the root node, if any.

- **use_defaults** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, return default values for calibration data items that have one.

Returns:  
EXA setting node describing the required calibration data for each locus.

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")

*final classmethod* get_locus_mapping(*station*)  
Get the locus mapping for this GateImplementation.

The locus mapping defines all the possible loci where this GateImplementation can be applied. It takes into account the symmetry of the gate and the implementation, and should not include unnecessary duplicate nodes for symmetric implementations, only the one sorted in the canonical (numerical) order.

For arity-0 gates the locus mapping should only have single-component loci.

Parameters:  
**station** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties")) – Static properties of the station for which to create the locus mapping.

Returns:  
Mapping from the possible loci for this GateImplementation to the QPU components used  
by the implementation on that locus.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gate_implementation.GateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-8c7d58591607ca7d75afc6d6cbe92ba472599e89.png)
