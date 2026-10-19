> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.drive_crosstalk.DriveCrossTalk.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.drive_crosstalk.DriveCrossTalk.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8c396ec268c6ef6e2f942c503c61d153db699294f8cf6e099dcec57975dd236b.

# DriveCrossTalk

Module: [`iqm.pulse.gates.drive_crosstalk`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.drive_crosstalk.html#module-iqm.pulse.gates.drive_crosstalk "iqm.pulse.gates.drive_crosstalk")

*class* iqm.pulse.gates.drive_crosstalk.DriveCrossTalk(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")

Calibration container and pulse builder for drive crosstalk compensation.

This implementation carries the drive crosstalk calibration data so that it can be calibrated and fetched like any other gate, and it builds the compensation pulses for a resolved schedule. The `apply_drive_crosstalk` compiler pass fetches this implementation via the builder and calls it with a schedule, e.g.:

```
impl = builder.get_implementation("drive_crosstalk", (), impl_name="drive_crosstalk")
compensation_box = impl(schedule, crosstalk_loci)  # TimeBox with the target aux-channel compensation pulses
```

The drive crosstalk is described by a complex matrix, where the element \\C\_{tc}\\ describes the crosstalk drive seen by the **target** `t` when the **control** `c` is driven: its absolute value is the relative crosstalk amplitude, and its argument the crosstalk phase. To cancel it, `apply_drive_crosstalk` replays the control’s drive on an auxiliary drive channel of the target, scaled by the amplitude and phase-shifted accordingly.

The matrix is given in a sparse form via three calibration parameters (we do not support dict- or xarray-valued Parameters yet). Parameter `matrix_index` lists the relevant (non-zero) elements as a flat list of strings of the form `<target>__<control>`. Parameters `crosstalk_amplitudes` and `crosstalk_phases` list the corresponding amplitudes \\\|C\_{tc}\|\\ and phases \\\arg C\_{tc}\\ (in radians). The three arrays must have equal lengths.

TODO: this is for now an experimental R&D implementation, and everything here is subject to change still.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.drive_crosstalk.DriveCrossTalk.parameters "iqm.pulse.gates.drive_crosstalk.DriveCrossTalk.parameters") | Required calibration data, may be nested |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.drive_crosstalk.DriveCrossTalk.locus_mapping_function "iqm.pulse.gates.drive_crosstalk.DriveCrossTalk.locus_mapping_function") | One-qubit loci. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

parameters*: NestedParams* *= {'crosstalk_amplitudes': Parameter(name='crosstalk_amplitudes', label='Drive crosstalk relative amplitudes', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'crosstalk_phases': Parameter(name='crosstalk_phases', label='Drive crosstalk phases', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.NDARRAY: 2\>, element_indices=None), 'matrix_index': Parameter(name='matrix_index', label='Drive crosstalk sparse matrix index', unit='', data_type=\<DataType.STRING: 3\>, collection_type=\<CollectionType.LIST: 1\>, element_indices=None)}*  
Required calibration data, may be nested

*static* locus_mapping_function(*station_properties*)  
One-qubit loci.

Parameters:  
**station_properties** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

Inheritance

![Inheritance diagram of iqm.pulse.gates.drive_crosstalk.DriveCrossTalk](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-af17a2b2cba69e66b52d4486c2f2c27e8c543603.png)
