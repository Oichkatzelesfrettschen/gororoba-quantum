> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b11b65dfb71053c50d6a14d14f0df3c4caecabcc8e1a604fcea5331abd0f7459.

# FluxPulseGate_SmoothConstant

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`FluxPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate.html#iqm.pulse.gates.cz.FluxPulseGate "iqm.pulse.gates.cz.FluxPulseGate")

Flux pulse gate implementation which uses a 3-part pulse sequence (cosine rise, constant, cosine fall).

Otherwise, works similar to FluxPulseGate.

Parameters:  
- **flux_pulses** – mapping from flux channel name to its flux pulse

- **rz** – mapping from drive channel name to the virtual z rotation angle, in radians, that should be performed on it

- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

Attributes

|  |  |
|----|----|
| [`root_parameters`](#iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant.root_parameters "iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant.root_parameters") | Parameters shared by all `FluxPulseGateBase` classes. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

rise_wave  
Waveform, rise part of the 3-pulse sequence to be played with qubit and coupler gates.

alias of [`CosineRiseFlex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRiseFlex.html#iqm.pulse.playlist.waveforms.CosineRiseFlex "iqm.pulse.playlist.waveforms.CosineRiseFlex")

fall_wave  
Waveform, fall part of the 3-pulse sequence to be played with qubit and coupler gates.

alias of [`CosineFallFlex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFallFlex.html#iqm.pulse.playlist.waveforms.CosineFallFlex "iqm.pulse.playlist.waveforms.CosineFallFlex")

root_parameters*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Parameter \| Setting \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]* *= {'coupler': {'amplitude': Parameter(name='', label='Coupler pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='Coupler pulse full width', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='Coupler pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'qubit': {'amplitude': Parameter(name='', label='Qubit pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='Qubit pulse full width', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='Qubit pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Parameters shared by all `FluxPulseGateBase` classes. Inheriting classes may override this if there’s a need for additional calibration parameters.

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-cc1d01f21fcffa3b0b77e23431fd2dbdf7cc9bd7.png)
