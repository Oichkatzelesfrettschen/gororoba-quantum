> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 56b73309ea8dcb740594195650d32af40b610d1847cb4e690c13ad4c90688b79.

# ThresholdStateDiscrimination

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.ThresholdStateDiscrimination(*label*, *delay_samples*, *implementation*, *weights*, *threshold*, *feedback_signal_label=''*)  
Bases: [`ComplexIntegration`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ComplexIntegration.html#iqm.pulse.playlist.instructions.ComplexIntegration "iqm.pulse.playlist.instructions.ComplexIntegration")

Thresholded integration, resulting in a boolean.

Perform a weighted integration of the IQ raw signal and compare the real part of the result against a threshold value.

Attributes

|  |  |
|----|----|
| [`feedback_signal_label`](#iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.feedback_signal_label "iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.feedback_signal_label") | In fast feedback routing, the transmitted signals are associated with this label. |
| [`threshold`](#iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.threshold "iqm.pulse.playlist.instructions.ThresholdStateDiscrimination.threshold") | The real part of the integration result is compared against this. |
| `weights` | Integration weights. |
| `label` | Identifier for the returned data, like `QB1__readout.time_trace`. |
| `delay_samples` | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |
| `implementation` | Measure operation and implementation that created this AcquisitionMethod, in the format `<operation name>.<implementation name>`. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **weights** ([*IQPulse*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.IQPulse.html#iqm.pulse.playlist.instructions.IQPulse "iqm.pulse.playlist.instructions.IQPulse"))

- **threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **feedback_signal_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

threshold*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The real part of the integration result is compared against this.

feedback_signal_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")* *= ''*  
In fast feedback routing, the transmitted signals are associated with this label. ConditionalInstructions whose “condition” field has the string value of feedback_signal_label will receive the signal from this ThresholdStateDiscrimination. Empty string (default) means the signal is not routed anywhere. The same feedback_signal_label may not be used multiple times within the same ReadoutTrigger. The same feedback_signal_label can be used in different ReadoutTriggers and different segments.

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.ThresholdStateDiscrimination](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-de6eb8259dc514eb2d0d899cdef6d9ee4f228f04.png)
