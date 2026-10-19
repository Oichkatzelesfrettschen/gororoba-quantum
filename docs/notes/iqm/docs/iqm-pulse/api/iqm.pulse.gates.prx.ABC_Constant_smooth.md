> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.ABC_Constant_smooth.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.ABC_Constant_smooth.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ff2d9e6922e520334a661155b48dcdc1e39e448813e673d54404b6c6394ecea9.

# ABC_Constant_smooth

Module: [`iqm.pulse.gates.prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx")

*class* iqm.pulse.gates.prx.ABC_Constant_smooth(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`PrxGateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PrxGateImplementation.html#iqm.pulse.gates.prx.PrxGateImplementation "iqm.pulse.gates.prx.PrxGateImplementation")

Base class for creating gates with an arbitrarily long Constant pulses with smooth rise and fall.

This pulse creates a :’Segment’ consisting of three instructions : \[rise_waveform, main_waveform, fall_waveform\]. This class is created so that one can use middle waveform as a constant, thus enabling to use arbitrarily long pulses, not limited by the awg memory.

Attributes::  
main_waveform: The middle part of the pulse, which should (but doesn’t have to) be a Constant waveform rise_waveform: rise part of the pulse fall_waveform: fall part of the pulse channel: Name of the drive channel on which the AC Stark pulse is played.

Constructs an instance of the AC Stark pulse for the given locus.

Attributes

|  |  |
|----|----|
| `main_waveform` |  |
| `rise_waveform` |  |
| `fall_waveform` |  |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx.ABC_Constant_smooth](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-40aa2a4ecae0938d679ebe069d047c9116739eeb.png)
