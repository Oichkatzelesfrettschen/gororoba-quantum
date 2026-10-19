> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26fc2881b7366f00a8a630d2e0c98de5cf9b476e679e49d003a46c3fb7a801d5.

# FluxPulse_SmoothConstant_SmoothConstant

Module: [`iqm.pulse.gates.cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz")

*class* iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`FluxPulseGate_SmoothConstant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant.html#iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant "iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant")

Constant flux pulse on both qubit and coupler with smooth rise/fall.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.parameters "iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.parameters") | Required calibration data, may be nested |
| [`symmetric`](#iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.symmetric "iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

|  |  |
|----|----|
| [`locus_mapping_function`](#iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.locus_mapping_function "iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.locus_mapping_function") | Two-component loci connected through a coupler where the coupler and at least one component has fast flux. |

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

coupler_wave  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

fall_wave  
alias of [`CosineFallFlex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFallFlex.html#iqm.pulse.playlist.waveforms.CosineFallFlex "iqm.pulse.playlist.waveforms.CosineFallFlex")

locus_mapping_function()  
Two-component loci connected through a coupler where the coupler and at least one component has fast flux.

There must be two locus components connected by a coupler, where the first locus component has fast flux. If both locus components have fast flux, we include both locus orders.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

parameters*: NestedParams* *= {'coupler': {'amplitude': Parameter(name='', label='Coupler flux pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='Coupler flux pulse full width', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='Coupler flux pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'qubit': {'amplitude': Parameter(name='', label='Qubit flux pulse amplitude', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'full_width': Parameter(name='', label='Qubit flux pulse full width', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='Qubit flux pulse rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}, 'rz': {'\*': Parameter(name='', label='Z rotation angle', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}}*  
Required calibration data, may be nested

qubit_wave  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

rise_wave  
alias of [`CosineRiseFlex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRiseFlex.html#iqm.pulse.playlist.waveforms.CosineRiseFlex "iqm.pulse.playlist.waveforms.CosineRiseFlex")

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-19a44fb456da514b060f6e7408277ceea58d79d1.png)
