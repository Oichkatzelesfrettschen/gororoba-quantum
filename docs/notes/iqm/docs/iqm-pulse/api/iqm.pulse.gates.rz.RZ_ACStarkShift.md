> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9018870b6686c9634f5b1542471ab413369b548747c7985250d2fb801ace8152.

# RZ_ACStarkShift

Module: [`iqm.pulse.gates.rz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html#module-iqm.pulse.gates.rz "iqm.pulse.gates.rz")

*class* iqm.pulse.gates.rz.RZ_ACStarkShift(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Implementation of the RZ gate using an AC Stark pulse.

An AC Stark pulse is a strong off-resonant drive on a qubit. This pulse leads to a frequency shift of the qubit due to the AC Stark effect. The qubit frequency shift depends on the AC Stark pulse amplitude and frequency.

Parameters:  
- **ac_stark_pulse** – AC Stark pulse.

- **channel** – Name of the drive channel on which the AC Stark pulse is played.

- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

Constructs an instance of the AC Stark pulse for the given locus.

Attributes

|  |  |
|----|----|
| `ac_stark_waveform` |  |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`duration_in_seconds`](#iqm.pulse.gates.rz.RZ_ACStarkShift.duration_in_seconds "iqm.pulse.gates.rz.RZ_ACStarkShift.duration_in_seconds") | Duration of the Schedule of the gate implementation (in seconds). |
| [`locus_mapping_function`](#iqm.pulse.gates.rz.RZ_ACStarkShift.locus_mapping_function "iqm.pulse.gates.rz.RZ_ACStarkShift.locus_mapping_function") | One-component loci with drive. |

locus_mapping_function()  
One-component loci with drive.

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

![Inheritance diagram of iqm.pulse.gates.rz.RZ_ACStarkShift](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-71cef5d6dccc5a5c412cb30a8b150e771da3c339.png)
