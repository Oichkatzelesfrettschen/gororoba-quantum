> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a6af67c8ae8652eeedf9573e08ab42fd83c66a65b1c96c1972fc6ea154eecc0e.

# Constant_PRX_with_smooth_rise_fall

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`ABC_Constant_smooth`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.ABC_Constant_smooth.html#iqm.pulse.gates.prx.ABC_Constant_smooth "iqm.pulse.gates.prx.ABC_Constant_smooth")

Constant PRX pulse with cosine rise and fall padding.

Implemented as a 3-instruction Schedule.

Constructs an instance of the AC Stark pulse for the given locus.

Attributes

|  |  |
|----|----|
| [`parameters`](#iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.parameters "iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.parameters") | Required calibration data, may be nested |
| [`symmetric`](#iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.symmetric "iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.symmetric") | True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

fall_waveform  
alias of [`CosineFall`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineFall.html#iqm.pulse.playlist.waveforms.CosineFall "iqm.pulse.playlist.waveforms.CosineFall")

main_waveform  
alias of [`Constant`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Constant.html#iqm.models.playlist.waveforms.Constant "(in IQM data definitions v3.1.0)")

parameters*: NestedParams* *= {'amplitude_i': Parameter(name='', label='amplitude_i', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'amplitude_q': Parameter(name='', label='amplitude_q', unit='', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'duration': Parameter(name='', label='Gate duration', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None), 'rise_time': Parameter(name='', label='gate rise time', unit='s', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)}*  
Required calibration data, may be nested

rise_waveform  
alias of [`CosineRise`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.waveforms.CosineRise.html#iqm.pulse.playlist.waveforms.CosineRise "iqm.pulse.playlist.waveforms.CosineRise")

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
True iff the implementation is symmetric in its locus components, meaning a permuted `locus` produces the same Schedule/TimeBox. Only meaningful if `self.parent.arity != 1`, and the locus components are of the same type.

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-c8680540e936e0094b77de4bf59b0201f2409691.png)
