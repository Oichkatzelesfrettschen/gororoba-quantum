> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d025d16d634244491bf7c71ddd29c3ae8b9e9552109651a6c3bfae230de8c498.

# gate_implementation

Full path: iqm.pulse.gate_implementation

Implementing abstract quantum operations as instruction schedules.

Note

Note the conceptual difference between [`quantum operations`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") (ops) and [`instruction schedules`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule"). Ops represent abstract, ideal computational operations, whereas instruction schedules represent concrete control signal sequences for the quantum computer. One can (approximately) implement an op using a number of different instruction schedules.

Module Attributes

|  |  |
|----|----|
| [`OILCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OILCalibrationData.html#iqm.pulse.gate_implementation.OILCalibrationData "iqm.pulse.gate_implementation.OILCalibrationData") | Calibration data for a particular implementation of a particular quantum operation at a particular locus. |
| [`OICalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OICalibrationData.html#iqm.pulse.gate_implementation.OICalibrationData "iqm.pulse.gate_implementation.OICalibrationData") | For a particular implementation of a particular quantum operation, maps operation loci to their calibration data. |
| [`OCalibrationData`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OCalibrationData.html#iqm.pulse.gate_implementation.OCalibrationData "iqm.pulse.gate_implementation.OCalibrationData") | For a particular quantum operation, maps implementation names to their calibration data. |
| [`OpCalibrationDataTree`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.OpCalibrationDataTree.html#iqm.pulse.gate_implementation.OpCalibrationDataTree "iqm.pulse.gate_implementation.OpCalibrationDataTree") | Maps [`quantum operation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") names to their calibration data. |
| [`NestedParams`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.NestedParams.html#iqm.pulse.gate_implementation.NestedParams "iqm.pulse.gate_implementation.NestedParams") | Nested dict defining the parameters required by GateImplementation classes. |

Functions

|  |  |
|----|----|
| [`get_waveform_parameters`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.get_waveform_parameters.html#iqm.pulse.gate_implementation.get_waveform_parameters "iqm.pulse.gate_implementation.get_waveform_parameters")(wave\[, label_prefix\]) | Parameters that are required to initialize the given Waveform class. |
| [`init_subclass_composite`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.init_subclass_composite.html#iqm.pulse.gate_implementation.init_subclass_composite "iqm.pulse.gate_implementation.init_subclass_composite")(gate_class) |  |

Classes

|  |  |
|----|----|
| [`CompositeCache`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeCache.html#iqm.pulse.gate_implementation.CompositeCache "iqm.pulse.gate_implementation.CompositeCache") | Cache for CompositeGate TimeBoxes. |
| [`CompositeGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate") | Base class for gate implementations that are defined in terms of other gate implementations. |
| [`CustomIQWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CustomIQWaveforms.html#iqm.pulse.gate_implementation.CustomIQWaveforms "iqm.pulse.gate_implementation.CustomIQWaveforms") | Base class for GateImplementations using custom waveform definition with IQPulses. |
| [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") | ABC for implementing quantum gates and other quantum operations using instruction schedules. |
| [`SinglePulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.SinglePulseGate.html#iqm.pulse.gate_implementation.SinglePulseGate "iqm.pulse.gate_implementation.SinglePulseGate") | Base class for GateImplementations that play a single pulse on a single channel. |

Inheritance

![Inheritance diagram of iqm.pulse.gate_implementation](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-a104101a4f921fe3a6e0eb0fbdfeae1363a0dc64.png)
