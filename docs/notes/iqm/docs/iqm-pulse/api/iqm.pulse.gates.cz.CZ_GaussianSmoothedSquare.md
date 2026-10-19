> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fff2aabc3cf5e32b8d49ca0f1ad27f063cc2054bd4aaf831c460f1ddd59cc921.

# CZ_GaussianSmoothedSquare

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`FluxPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate.html#iqm.pulse.gates.cz.FluxPulseGate "iqm.pulse.gates.cz.FluxPulseGate")

CZ gate using a GaussianSmoothedSquare flux pulse on the coupler.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.parameters "iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.parameters") | Required calibration data, may be nested |
| [`qubit_wave`](#iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.qubit_wave "iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.qubit_wave") | Flux pulse waveform for the locus component flux AWGs. |
| [`symmetric`](#iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.symmetric "iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.locus_mapping_function "iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.locus_mapping_function") | Two-component loci (qubits + resonators), connected through a coupler with fast flux, symmetric. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave  
alias of [`GaussianSmoothedSquare`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.GaussianSmoothedSquare.html#iqm.models.playlist.waveforms.GaussianSmoothedSquare "(in IQM data definitions v3.1.0)")

locus_mapping_function()  
Two-component loci (qubits + resonators), connected through a coupler with fast flux, symmetric.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: NestedParams* *= {'coupler': {'amplitude': Parameter(name='', label='Coupler flux pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'center_offset': Setting(parameter=Parameter(name='', label='Coupler flux pulse center_offset of gss', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), value=0.0, read_only=False, path=''), 'gaussian_sigma': Parameter(name='', label='Coupler flux pulse gaussian_sigma of gss', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'square_width': Parameter(name='', label='Coupler flux pulse square_width of gss', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Required calibration data, may be nested

qubit_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Flux pulse waveform for the locus component flux AWGs.

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-c15ef428ac06dae6bc98e2fc6e75e7dc68a0dd8d.png)
