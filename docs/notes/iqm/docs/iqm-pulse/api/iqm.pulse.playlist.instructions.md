> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 de0695bc3f304651d2def05df8f600a12404c48b61b6ca0bf8da8094dcb64c52.

# instructions

Full path: iqm.pulse.playlist.instructions

Instructions for control instruments.

Module Attributes

|  |  |
|----|----|
| [`NONSOLID`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.NONSOLID.html#iqm.pulse.playlist.instructions.NONSOLID "iqm.pulse.playlist.instructions.NONSOLID") | Instructions that are converted to [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") after scheduling. |

Classes

|  |  |
|----|----|
| [`AcquisitionMethod`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.AcquisitionMethod.html#iqm.pulse.playlist.instructions.AcquisitionMethod "iqm.pulse.playlist.instructions.AcquisitionMethod") | Describes a way to acquire readout data. |
| [`Block`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Block.html#iqm.pulse.playlist.instructions.Block "iqm.pulse.playlist.instructions.Block") | Behave strictly as if outputting zero-valued samples for the duration of the instruction. |
| [`ComplexIntegration`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ComplexIntegration.html#iqm.pulse.playlist.instructions.ComplexIntegration "iqm.pulse.playlist.instructions.ComplexIntegration") | Perform a weighted integration of the IQ raw signal, resulting in a complex number. |
| [`ConditionalInstruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ConditionalInstruction.html#iqm.pulse.playlist.instructions.ConditionalInstruction "iqm.pulse.playlist.instructions.ConditionalInstruction") | Choice between multiple Instructions, depending on a condition. |
| [`FluxPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.FluxPulse.html#iqm.pulse.playlist.instructions.FluxPulse "iqm.pulse.playlist.instructions.FluxPulse") | RealPulse representing a flux pulse. |
| [`IQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse") | Play an upconverted pulse that contains real in-phase and quadrature waveforms. |
| [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction") | Command that can be executed by the quantum computer on a control channel. |
| [`MultiplexedIQPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.MultiplexedIQPulse.html#iqm.pulse.playlist.instructions.MultiplexedIQPulse "iqm.pulse.playlist.instructions.MultiplexedIQPulse") | Play the sum of multiple IQ pulses. |
| [`Nothing`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html#iqm.pulse.playlist.instructions.Nothing "iqm.pulse.playlist.instructions.Nothing") | Used to extend a control channel in time, without blocking it, during scheduling. |
| [`ReadoutMetrics`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutMetrics.html#iqm.pulse.playlist.instructions.ReadoutMetrics "iqm.pulse.playlist.instructions.ReadoutMetrics") | Necessary readout metrics needed for return data processing for a single `Playlist`. |
| [`ReadoutTrigger`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html#iqm.pulse.playlist.instructions.ReadoutTrigger "iqm.pulse.playlist.instructions.ReadoutTrigger") | Instruction for playing a probe pulse and acquiring the associated readout results. |
| [`RealPulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.RealPulse.html#iqm.pulse.playlist.instructions.RealPulse "iqm.pulse.playlist.instructions.RealPulse") | Play a real-valued pulse. |
| [`ThresholdStateDiscrimination`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.html#iqm.pulse.playlist.instructions.ThresholdStateDiscrimination "iqm.pulse.playlist.instructions.ThresholdStateDiscrimination") | Thresholded integration, resulting in a boolean. |
| [`TimeTrace`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.TimeTrace.html#iqm.pulse.playlist.instructions.TimeTrace "iqm.pulse.playlist.instructions.TimeTrace") | Capture the raw IQ signal without integration. |
| [`VirtualRZ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.VirtualRZ.html#iqm.pulse.playlist.instructions.VirtualRZ "iqm.pulse.playlist.instructions.VirtualRZ") | Change the upconversion phase reference. |
| [`Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Wait.html#iqm.pulse.playlist.instructions.Wait "iqm.pulse.playlist.instructions.Wait") | Behave as if outputting zero-valued samples for the duration of the instruction. |

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-07bc1062e3e74c8289a3e685c8fce11c844af677.png)
