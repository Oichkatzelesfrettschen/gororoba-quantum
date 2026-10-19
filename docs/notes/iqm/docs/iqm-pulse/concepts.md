> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/concepts.html](https://docs.iqm.tech/4.7/iqm-pulse/concepts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cd777becfc7c0802607421bc013e6b547240890127bcc1464e3c847fba549274.

# Concepts and classes

This section gives an overview of the main concepts and terminology in IQM Pulse.

## Quick reference

- QPUs contain **components**: qubits, computational resonators, couplers, and probelines.

- Each component may have some **control channels** connected to it. Control channels deliver physical control pulses to the QPU.

- Quantum operations have a **locus**, which is the set of quantum information carrying components (qubits and resonators) the operation acts on. One operation may involve sending pulses to multiple control channels.

The assembly of a Playlist, or a batch of quantum circuits, can be summarized as follows:

- A Playlist contains multiple independent **segments**, to be executed as a batch.

- A segment is a conceptual unit at a time scale where the quantum information of the QPU can be assumed to be preserved. A quantum circuit corresponds to one segment.

- What is executed during a segment is determined by a **Schedule**.

- A Schedule is a set of hardware control channels, each with a strictly timed sequence of **Instructions**.

- A Schedule is formed by scheduling a number of **Timeboxes**.

- A TimeBox can contain other TimeBoxes without precise relative timing, or it can be atomic, in which case it contains a single **Schedule**.

The image below illustrates how a Playlist of two segments is formed from TimeBoxes.

![](https://docs.iqm.tech/4.7/iqm-pulse/_images/playlist_breakdown.svg)

## Instructions

[`Hardware instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction") are the lowest-level construct visible on the client side. Instructions are a set of atomic, real-time execution commands for the control hardware supported by IQM. They work in a time scale where the quantum information of the QPU can be assumed to be preserved. Examples of Instructions are [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") to play a microwave pulse on a channel, [`VirtualRZ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.VirtualRZ.html#iqm.pulse.playlist.instructions.VirtualRZ "iqm.pulse.playlist.instructions.VirtualRZ") to adjust the modulation phase, [`ReadoutTrigger`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html#iqm.pulse.playlist.instructions.ReadoutTrigger "iqm.pulse.playlist.instructions.ReadoutTrigger") to acquire measurement data, and [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") to delay the next Instruction for a given time. See [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions") for the complete list.

During execution, each hardware control channel executes its own sequence of Instructions. Each Instruction blocks the next until it is completed. Instructions are as explicit as possible, so that there is no ambiguity on what will be executed when. IQM Station control transforms Instructions to machine-specific commands.

All Instructions have a duration, measured in samples, though the duration can be zero. The durations are subject to hardware-specific granularity constraints. For example, some hardware might require all instructions to be a multiple of 16 samples long, with a minimum of 32. Instructions violating the granularity constraints will raise an error. However, a typical user does not need to concern themselves about the constraints, as the gate implementations and IQM Pulse’s scheduling ensures the constraints are respected. The philosophy is that Station Control, which is inaccessible to the user, does not attempt to do any smart “magic” to fix inconsistencies in the user’s input, it simply executes the Playlist it is given. Instead, the magic happens on the client side so that it is transparent to the user.

Note

For technical reasons, IQM Pulse mostly uses classes from [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions"), but when finalizing the output, the instructions are converted to [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "(in IQM data definitions v3.1.0)"). These two class families are semantically equivalent, apart from a few exceptions like [`Block`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html#iqm.pulse.playlist.instructions.Block "iqm.pulse.playlist.instructions.Block") which only exists on the client side to help with scheduling.

## Schedules

[`Schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") contains a number of control channels, each with a list of Instructions. All channels in a Schedule start executing at the same instant, and the timing is defined by the duration of the individual Instructions. Schedules can be thought of as a fixed block that occupies some interval on a timeline of some channels.

Schedules appear in two contexts: gate implementations and as complete segments. For example, when an implementation of a PRX gate is requested, a small Schedule involving the drive channel of a single qubit is created. When all the desired gates in a circuit have been scheduled by concatenating the gate-schedules together, the end result, a segment, is a large Schedule occupying all necessary channels. A typical segment starts with initializing the qubits and ends with reading out their state.

## TimeBoxes

Whereas a Schedule is a container with strict relative timing, a [`TimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") is a container with undefined relative timing. Each TimeBox can be labeled using a human-readable label describing it, and operates on a number of *locus components*, using some of their control channels. A composite TimeBox contains other TimeBoxes as children, whereas atomic TimeBoxes contain a single Schedule.

TimeBoxes are the main language in which users define the order and relative alignment of execution elements, be it gates, Schedules, or larger TimeBoxes.

A key process is the scheduling, in which TimeBoxes are resolved recursively into a fixed Schedule. When resolving, all Schedules inside the TimeBox are concatenated and are either left-aligned (ASAP) or right-aligned (ALAP), respecting the hardware constraints. Importantly, if some TimeBoxes have content on disjoint channels, their Schedules are allowed to happen simultaneously. If they have content on partly overlapping channels, the Schedules are concatenated while preserving their internal timing. Any interval that does not have explicit instructions is filled with Wait instructions. The figure above demonstrates how TimeBoxes are resolved.

The syntax and rules are explained in more detail in [Using ScheduleBuilder](https://docs.iqm.tech/4.7/iqm-pulse/using_builder.html).

## QuantumOps

A higher-level concept, a [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") (quantum operation) can represent a unitary quantum gate like PRX or CZ, or a nonunitary operation like a measurement or a reset. QuantumOps are simple, abstract, self-contained actions one can apply on the quantum state of the QPU as parts of a quantum circuit. Whereas Schedules and Instructions act on control channels, QuantumOps act on *loci* which are ordered sequences of QPU components, such as qubits or computational resonators.

A QuantumOp has an unambiguous definition in terms of its *intended* effect on the computational subspace of its locus components, but it can be *implemented* on a station in various ways. Each implementation is represented as a GateImplementation.

The list of available QuantumOps at runtime can be obtained with [`iqm.pulse.builder.build_quantum_ops()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.build_quantum_ops.html#iqm.pulse.builder.build_quantum_ops "iqm.pulse.builder.build_quantum_ops"). A new QuantumOp can be registered at runtime using [`iqm.pulse.gates.register_operation()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_operation.html#iqm.pulse.gates.register_operation "iqm.pulse.gates.register_operation").

## GateImplementations

A [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") bridges the gap between QuantumOps and TimeBoxes. It represents the concrete control signals sent to the station in order to apply a QuantumOp. Despite the name, GateImplementations are used to implement all QuantumOps, not just unitary quantum gates.

When a user requests a QuantumOp from [`ScheduleBuilder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder") with specific parameters and locus components, the chosen GateImplementation (usually the default) for the operation is used to produce a TimeBox. This TimeBox, usually atomic, contains a Schedule on the appropriate control channels. The Instructions within are constructed using the calibration values for that operation, implementation and locus from the ScheduleBuilder.

All gate implementations are listed in [`iqm.pulse.gates`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.html#module-iqm.pulse.gates "iqm.pulse.gates"). Section [Custom gate implementations](https://docs.iqm.tech/4.7/iqm-pulse/custom_gates.html) explains how to add more implementations. A new GateImplementation can be added to a known (registered) QuantumOp using [`iqm.pulse.gates.register_implementation()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_implementation.html#iqm.pulse.gates.register_implementation "iqm.pulse.gates.register_implementation").

## Playlists

Once all TimeBoxes are scheduled into large Schedules, one for each segment/circuit, the Schedules are collected into a [`Playlist`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)"). The Playlist is the final product that is sent to Station Control. Its contents are compressed by indexing all unique Instructions and waveforms on each channel, and representing the control channels in each segment as lists of Instruction indices.

During execution, the segments in the Playlist are executed in order, and the whole sequence is repeated a number of times equal to the number of repetitions (shots) requested.

Segments are separated in time by **end delay**, a parameter outside the Playlist. A long end delay can be used to prevent quantum information carrying from one segment to the next, thus resetting the qubits. Alternatively, the reset can be encoded in each segment as a long Wait instruction or using some active reset scheme.

Station Control aims to execute all segments one after another in one go, but sometimes this is not possible due to various memory constraints. In case the whole Playlist does not fit in memory, the segments are split into chunks which are executed separately. The delay between chunks is undefined. Therefore, the time between segments is guaranteed to be at least the duration of the end delay, but can be much larger.

[`inspect_playlist()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.visualisation.base.inspect_playlist.html#iqm.pulse.playlist.visualisation.base.inspect_playlist "iqm.pulse.playlist.visualisation.base.inspect_playlist") provides a neat visual representation of the playlist, as blocks of instructions on a timeline.
