> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1f1b5a774d9e4497734f364a903060c7058edbbe9d0b9b45f63092c3a7b6e776.

# instructions

Instruction definitions.

Full path: iqm.models.playlist.instructions

Classes

|  |  |
|----|----|
| [`AcquisitionMethod`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.AcquisitionMethod.html#iqm.models.playlist.instructions.AcquisitionMethod "iqm.models.playlist.instructions.AcquisitionMethod") | Describes a way to acquire readout data. |
| [`ComplexIntegration`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ComplexIntegration.html#iqm.models.playlist.instructions.ComplexIntegration "iqm.models.playlist.instructions.ComplexIntegration") | Perform a weighted integration of the IQ raw signal, resulting in a complex number. |
| [`ConditionalInstruction`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ConditionalInstruction.html#iqm.models.playlist.instructions.ConditionalInstruction "iqm.models.playlist.instructions.ConditionalInstruction") | Class for Conditional Pulses. |
| [`IQPulse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html#iqm.models.playlist.instructions.IQPulse "iqm.models.playlist.instructions.IQPulse") | Class for IQ Pulses. |
| [`Instruction`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction") | Wrapper class for Instructions. |
| [`MultiplexedIQPulse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.MultiplexedIQPulse.html#iqm.models.playlist.instructions.MultiplexedIQPulse "iqm.models.playlist.instructions.MultiplexedIQPulse") | Instruction to simultaneously play multiple IQ pulses. |
| [`MultiplexedRealPulse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.MultiplexedRealPulse.html#iqm.models.playlist.instructions.MultiplexedRealPulse "iqm.models.playlist.instructions.MultiplexedRealPulse") | Instruction to simultaneously play multiple real pulses. |
| [`ReadoutTrigger`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ReadoutTrigger.html#iqm.models.playlist.instructions.ReadoutTrigger "iqm.models.playlist.instructions.ReadoutTrigger") | Instruction for playing a probe pulse and acquiring the associated readout results. |
| [`RealPulse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.RealPulse.html#iqm.models.playlist.instructions.RealPulse "iqm.models.playlist.instructions.RealPulse") | Class for Real pulses. |
| [`ThresholdStateDiscrimination`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ThresholdStateDiscrimination.html#iqm.models.playlist.instructions.ThresholdStateDiscrimination "iqm.models.playlist.instructions.ThresholdStateDiscrimination") | Perform a weighted integration of the IQ raw signal and compares the real part of the result against a threshold value, resulting in a single bit. |
| [`TimeTrace`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.TimeTrace.html#iqm.models.playlist.instructions.TimeTrace "iqm.models.playlist.instructions.TimeTrace") | Capture the raw IQ signal without integration. |
| [`VirtualRZ`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.VirtualRZ.html#iqm.models.playlist.instructions.VirtualRZ "iqm.models.playlist.instructions.VirtualRZ") | Class for Virtual Rz. |
| [`Wait`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Wait.html#iqm.models.playlist.instructions.Wait "iqm.models.playlist.instructions.Wait") | Class for WaitInstruction. |
