> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.barrier.Barrier.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.barrier.Barrier.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 adba7c35b25f3b5bf2c4466e47e5e2d44a6ed4520fe271d32d5bbdd85f22f1c8.

# Barrier

Module: [`iqm.pulse.gates.barrier`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.barrier.html#module-iqm.pulse.gates.barrier "iqm.pulse.gates.barrier")

*class* iqm.pulse.gates.barrier.Barrier(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

GateImplementation for the n-qudit `barrier` metaoperation.

Returns a schedule with zero-duration [`Block`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html#iqm.pulse.playlist.instructions.Block "iqm.pulse.playlist.instructions.Block") metainstructions. When this is appended to another [`Schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule"), it causes the affected channels to be padded with [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") instructions to the same length, which in turn imposes a definite temporal order for the operations on different sides of the barrier (the ones preceding it are always executed first).

Note

Assumes that all instructions involve either the drive, flux or probe channels of the locus QPU components.

Parameters:  
- **channels** – channels related to the locus QPU components, to be blocked

- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

Attributes

|  |  |
|----|----|
| [`symmetric`](#iqm.pulse.gates.barrier.Barrier.symmetric "iqm.pulse.gates.barrier.Barrier.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.barrier.Barrier.duration_in_seconds "iqm.pulse.gates.barrier.Barrier.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |
| [`locus_mapping_function`](#iqm.pulse.gates.barrier.Barrier.locus_mapping_function "iqm.pulse.gates.barrier.Barrier.locus_mapping_function") | One-component loci. |

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

locus_mapping_function()  
One-component loci.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

duration_in_seconds()  
Duration of the Schedule of the gate implementation (in seconds).

Can be left unimplemented if the duration e.g. depends on the gate arguments. Subclasses can reimplement this method in case it makes sense in their context.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.pulse.gates.barrier.Barrier](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-1bca79a494aab26e0c6ea0e484efe1a7677bc006.png)
