> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_Virtual.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_Virtual.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6f6a35200c954f1f5fecfec858178e94dc3fa5eee3a18a9cfef6c2b41a8d0399.

# RZ_Virtual

Module: [`iqm.pulse.gates.rz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html#module-iqm.pulse.gates.rz "iqm.pulse.gates.rz")

*class* iqm.pulse.gates.rz.RZ_Virtual(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Implementation of the RZ gate using the virtual z rotation technique.

Implements the RZ gate on a specific qubit using a [`VirtualRZ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.VirtualRZ.html#iqm.pulse.playlist.instructions.VirtualRZ "iqm.pulse.playlist.instructions.VirtualRZ") instruction, which simply changes the phase of the local oscillator driving that qubit. This requires no calibration data as of now. The generated VirtualRZ instruction has the shortest possible duration allowed by the instruments.

The virtual z rotation method is based on algebraically commuting the RZ gates towards the end of the circuit, until they hit a measurement operation, at which point they are eliminated. It assumes that

1.  all the multi-qubit gates in the circuit commute with arbitrary RZ gates (this holds e.g. for CZ since it is diagonal),

2.  measurements are projective and happen in the z basis, so that RZ gates that immediately precede them do not affect the measurement result or the state after the measurement, and thus can be removed, and

3.  conjugating the single-qubit gates in the circuit with RZ is equivalent to incrementing the phase of the drive (holds for [`PRX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")),

    \\R\_\phi(\theta) R_z(\alpha) = R_z(\alpha) R\_{\phi - \alpha}(\theta),\\

    which can be accomplished either by incrementing the phase of the local oscillator of the drive channel, or incrementing the phases of all the [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") s following it on the drive channel.

*If all these assumptions hold* we may implement an RZ gate using a VirtualRZ instruction, with `phase_increment` equal to the negated rotation angle.

Parameters:  
- **channel** – name of the drive channel on which the VirtualRZ acts

- **duration** – time duration of the VirtualRZ instruction, in seconds

- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.rz.RZ_Virtual.parameters "iqm.pulse.gates.rz.RZ_Virtual.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.rz.RZ_Virtual.duration_in_seconds "iqm.pulse.gates.rz.RZ_Virtual.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |
| [`locus_mapping_function`](#iqm.pulse.gates.rz.RZ_Virtual.locus_mapping_function "iqm.pulse.gates.rz.RZ_Virtual.locus_mapping_function") | One-component loci with virtual drive capability. |

locus_mapping_function()  
One-component loci with virtual drive capability.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter\]* *= {}*  
Required calibration data, may be nested

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.rz.RZ_Virtual](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-a624a15820860e0182d0d23ffdf2d60d8e936eae.png)
