> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.TripleFluxPulseGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.TripleFluxPulseGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c4152859aefc4f535741fcaad220f93d2f2563796b4a660cf77228e943af9984.

# TripleFluxPulseGate

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.TripleFluxPulseGate(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`FluxPulseGateBase`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGateBase.html#iqm.pulse.gates.cz.FluxPulseGateBase "iqm.pulse.gates.cz.FluxPulseGateBase")

Base class for flux pulse gate implementations that have flux pulses for both locus components.

The parameters for the component flux pulses are under nodes `first_qubit` and `second_qubit` in the calibration data, where the names refer to the locus order.

Attributes

|  |  |
|----|----|
| [`coupler_wave`](#iqm.pulse.gates.cz.TripleFluxPulseGate.coupler_wave "iqm.pulse.gates.cz.TripleFluxPulseGate.coupler_wave") | Flux pulse waveform for the coupler flux AWG. |
| [`parameters`](#iqm.pulse.gates.cz.TripleFluxPulseGate.parameters "iqm.pulse.gates.cz.TripleFluxPulseGate.parameters") | Required calibration data, may be nested |
| [`qubit_wave`](#iqm.pulse.gates.cz.TripleFluxPulseGate.qubit_wave "iqm.pulse.gates.cz.TripleFluxPulseGate.qubit_wave") | Flux pulse waveform for the locus component flux AWGs. |
| [`symmetric`](#iqm.pulse.gates.cz.TripleFluxPulseGate.symmetric "iqm.pulse.gates.cz.TripleFluxPulseGate.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.cz.TripleFluxPulseGate.locus_mapping_function "iqm.pulse.gates.cz.TripleFluxPulseGate.locus_mapping_function") | Two-component loci (qubits + resonators), connected through a coupler with fast flux, symmetric. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Flux pulse waveform for the coupler flux AWG.

locus_mapping_function()  
Two-component loci (qubits + resonators), connected through a coupler with fast flux, symmetric.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: NestedParams* *= {'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Required calibration data, may be nested

qubit_wave*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[Waveform\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Flux pulse waveform for the locus component flux AWGs.

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.TripleFluxPulseGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-5d699d5ec54708ac1894f3fefc634dc69e81d739.png)
