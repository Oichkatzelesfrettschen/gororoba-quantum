> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 786c512509466bbe73dd5cfb7b7cb71cf1a0a58deaf466fb33b819e51a213a76.

# Using ScheduleBuilder

This section describes how to use [`ScheduleBuilder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder") to compose instruction schedules. ScheduleBuilder encapsulates the registered [`QuantumOps`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") and [`GateImplementations`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation"), their calibration information, the [`QPU components and their topology`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html#exa.common.qcm_data.chip_topology.ChipTopology "(in iqm-exa-common v29.0.0)"), and the [`control channel properties`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties"), i.e. all you need to construct [`Schedules`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") and [`Playlists`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)").

In the context of IQM Client and EXA workflows, an instance of ScheduleBuilder is obtained from `Compiler`, and it contains all the necessary information to produce schedules that execute against a particular quantum computer instance. Here, we assume that user has an instance of ScheduleBuilder `builder` to work with.

## Creating TimeBoxes

A typical workflow begins with calling [`get_implementation()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder.get_implementation "iqm.pulse.builder.ScheduleBuilder.get_implementation") with the name of a desired QuantumOp and the locus for the operation. The locus is the logical target of the operation, usually a sequence of qubits or computational resonators. This outputs a an instance of [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation"), which is capable of producing TimeBoxes with the correct calibration for that locus.

For example, here we ask for the GateImplementation of `prx`, `cz`, and `measure`, all of which are standard gates recognized by IQM Pulse, for qubits `QB1` and `QB3`. Any gate which is registered in the runtime can be requested this way.

``` python
qubits = ["QB1", "QB3"]
cz_gate_impl = builder.get_implementation("cz", qubits)
prx_gate_impl = builder.get_implementation("prx", ["QB1"])
measure_gate_impl = builder.get_implementation("measure", qubits)

# equivalent shortcuts:
cz_gate_impl = builder.cz(qubits)
prx_gate_impl = builder.prx(["QB1"])
measure_gate_impl = builder.measure(qubits)
```

Notice how the number of qubits matches the operation: CZ acts on 2 qubits, while PRX acts on only one. Measure can act on any number of qubits.

There might be several different implementations available for an operation. `get_implementation` gives the implementation that is set as the default (for that locus), unless a specific implementation is requested with a keyword argument.

To instantiate some concrete TimeBoxes, we call the implementation with the arguments of the operation, defined in the QuantumOp instance it implements. PRX has 2 parameters: the two angles of a phased rotation. CZ does not have any parameters.

``` python
import numpy as np
x180 = prx_gate_impl(np.pi, 0)
y90 = prx_gate_impl(np.pi/2, np.pi/2)
cz = cz_gate_impl()
measure = measure_gate_impl()

# equivalent shortcuts for prx:
x180 = prx_gate_impl.rx(np.pi)
y90 = prx_gate_impl.ry(np.pi/2)
```

Another important method is the [`wait()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder.wait "iqm.pulse.builder.ScheduleBuilder.wait"), which blocks the control channels of the given components for a certain time:

``` python
wait = builder.wait(qubits, duration=100e-9, rounding=True)  # Duration in seconds
```

In all of the examples above, the resulting TimeBoxes are atomic. They can be organized into composite TimeBoxes to define their relative order.

## Composing TimeBoxes

TimeBoxes can be concatenated with the following rules:

- Addition (`+`) concatenates the children of the operands into the children of a single composite TimeBox. Use addition to allow gates on disjoint loci to execute simultaneously, for example doing a PRX on all qubits.

- The pipe operation (`|`) groups two TimeBoxes together without concatenating. This results in composite TimeBox with two children, the operands, which are scheduled separately. Use the pipe to ensure that certain operations execute before some others.

- Iterables of TimeBoxes are treated as the sum of the elements.

This would execute 2 PRX gates on QB1 and QB2 simultaneously:

``` python
p1 = builder.prx(["QB1"]).rx(0.1)
p2 = builder.prx(["QB2"]).rx(0.2)
p1 + p2 + p1 + p2
```

If the last operator was `|` instead, the second gate on QB2 would execute only after the first 3 gates.

``` python
p1 + p2 + p1 | p2

# equivalent:
from iqm.pulse.timebox.TimeBox import TimeBox
TimeBox.composite([p1 + p2 + p1, p2])
```

Together, these rules provide a handy way of defining complex circuits easily:

``` python
# Do Y90, wait, CZ, X180 in this order, and right-align everything to be as close to measure as possible:
circuit1 = (y90 + wait + cz + x180).set_alap() | measure

# Do X180, then repeat (Y90, wait) 5 times, then measure:
circuit2 = x180 + [y90, wait] * 5 + measure

# Concatenate boxes, preserving their internal alignment:
circuit3 = circuit1 | circuit2 | circuit1
```

The method [`TimeBox.set_alap()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox.set_alap "iqm.pulse.timebox.TimeBox.set_alap") is used to change the [`SchedulingStrategy`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy") of the composite TimeBox from ASAP (as soon as possible, the default) to ALAP (as late as possible). The method [`TimeBox.set_asap()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox.set_asap "iqm.pulse.timebox.TimeBox.set_asap") can be used to change it back. In the example above, the circuits concatenated with the `|` operator are scheduled separately, where the contents of `circuit1` are scheduled as late as possible, and the contents of `circuit2` as soon as possible. Let us now discuss resolving and scheduling in more detail.

## Resolving TimeBoxes into a Schedule

A TimeBox is made atomic by *resolving* it using [`ScheduleBuilder.resolve_timebox()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder.resolve_timebox "iqm.pulse.builder.ScheduleBuilder.resolve_timebox"). When using a framework like IQM Client or EXA, the framework will take care of the resolving as part of compilation, so the user does not need to do it explicitly.

TimeBoxes are resolved recursively: The children of a TimeBox are resolved, and resulting (sub-)Schedules are aligned according to the [`SchedulingStrategy`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy") (ASAP or ALAP) of the TimeBox. The time duration of a TimeBox is determined by its contents and the way they are scheduled during the resolution. Finally, all channels are padded with Waits so that the total duration of Instructions on every channel is equal. In other words, the Schedule becomes a “rectangle”.

An important part of the scheduling are the blocking rules, that is, whether the contents of two TimeBoxes block or slide past each other. The rules are:

- An atomic TimeBox is considered to act on a component if it has instructions on any of the non-virtual channels related to that component.

- A composite TimeBox acts on the union of its children’s locus components.

- A TimeBox blocks all channels related to any component it acts on.

- When scheduling two TimeBoxes, their instructions will not overlap in time if the TimeBoxes share at least one locus component.

In addition to blocking all the channels of components whose channels are actually used in a TimeBox, it is possible to block channels of neighbouring components as well (for example in order to limit cross-talk). The applied neighbourhood is specified in [`ScheduleBuilder.resolve_timebox()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder.resolve_timebox "iqm.pulse.builder.ScheduleBuilder.resolve_timebox"). The neighbourhood is defined as an integer such that 0 means “block only the channels of involved components”, 1 means “same as 0, but also block the channels of all couplers neighboring the involved components”, 2 means “same as 1, but also block the channels of all components connected to those couplers”, and so on. The blocking rules do not add actual Wait or Block instructions to the neighbourhood channels, and two overlapping neighbourhoods do not block each other. The blocking comes in question only when actual content would be added to those neighbourhood channels.

In practice, the rules and default GateImplementations ensure that the user can concatenate arbitrary gates without worrying that the gates have an adverse effect on each other. For example, the pulse of a PRX gate playing at the same time as a CZ gate or a measurement on the same locus would ruin both operations. If such overlapping of gates is desired, the best way is to arrange the Instructions on the Schedule level and wrap the schedule into an atomic TimeBox.

Note

Virtual channels are special channels that exist only to aid the scheduling algorithm. Examples are tracking the phases of the MOVE gate, and timing of fast feedback. These channels are removed when the Playlist is finalized.

## Miscellaneous features

You are encouraged to discover the many features of ScheduleBuilder and TimeBox by reading the API: [`ScheduleBuilder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"), [`TimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox").

A quick reference of selected features is provided in the examples below.

Finding information about the target system:

``` python
# Find component information:
all_qubits = builder.chip_topology.qubits

# Find topology information, such as native qubit connectivity:
builder.chip_topology.get_neighbor_locus_components(["QB3"])

# Find control channels and their properties
channel_name = builder.get_drive_channel("QB3")
properties = builder.channels[channel_name]

# Modify any calibration value:
builder.calibration["prx"]["drag_gaussian"][("QB1",)]["duration"] = 160e-9
```

Working with TimeBoxes:

``` python
# Access children of a composite box:
circuit1.children[0] == circuit1[0]

# Access the schedule and instructions of an atomic box:
cz_schedule = cz.atom

# Print contents of a box
circuit3.print()

# Ask for a non-default implementation:
builder.get_implementation("prx", ["QB1"], implementation="drag_gaussian")

# Override calibration in one specific box:
builder.get_implementation("prx", ["QB1"], priority_calibration={"duration": 80e-9})
```

## Common pitfalls

Some typical errors that are easy to make with the syntax:

- Not calling the implementation to get a TimeBox. The call is easy to forget especially if there are no parameters to give:

  ``` python
  cz = builder.cz(qubits)
  cz + cz  # Error!
  cz() + cz()  # Correct
  ```

- Giving a single component as locus:

  ``` python
  builder.prx("QB3")  # Error! "Q" is not a valid component
  builder.prx(["QB3"])  # Correct
  ```

- Accidentally unpacking a TimeBox using a `+` operator instead of a `|` operator:

  ``` python
  qubits = ["QB1", "QB20"]
  circ = TimeBox.composite([builder.prx([qubit])(np.pi, 0.0) for qubit in qubits]).set_alap()
  circ += builder.measure(qubits)() # measurements END simultaneously
  circ |= builder.measure(qubits)() # measurements START simultaneously
  ```
