> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ThresholdStateDiscrimination.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ThresholdStateDiscrimination.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5c3bc575e90deb251640b75b92d160b1a8b4fed796a2d9213a9b54e8d7d4aae9.

# ThresholdStateDiscrimination

*class* iqm.models.playlist.instructions.ThresholdStateDiscrimination(*label*, *delay_samples*, *weights*, *threshold*, *feedback_signal_label=''*)  
Bases: [`ComplexIntegration`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.ComplexIntegration.html#iqm.models.playlist.instructions.ComplexIntegration "iqm.models.playlist.instructions.ComplexIntegration")

Perform a weighted integration of the IQ raw signal and compares the real part of the result against a threshold value, resulting in a single bit.

Module: [`iqm.models.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.html#module-iqm.models.playlist.instructions "iqm.models.playlist.instructions")

Attributes

|  |  |
|----|----|
| [`feedback_signal_label`](#iqm.models.playlist.instructions.ThresholdStateDiscrimination.feedback_signal_label "iqm.models.playlist.instructions.ThresholdStateDiscrimination.feedback_signal_label") | In fast feedback routing, the transmitted signals are associated with this label. |
| [`threshold`](#iqm.models.playlist.instructions.ThresholdStateDiscrimination.threshold "iqm.models.playlist.instructions.ThresholdStateDiscrimination.threshold") | The real part of the integration result is compared against this. |
| `weights` | Integration weights. |
| `label` | Identifier for the returned data, like `QB1__readout.time_trace`. |
| `delay_samples` | Delay from beginning of probe pulse to beginning of acquisition window, in samples. |

Methods

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **delay_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **weights** ([*IQPulse*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html#iqm.models.playlist.instructions.IQPulse "iqm.models.playlist.instructions.IQPulse"))

- **threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **feedback_signal_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

threshold*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The real part of the integration result is compared against this.

feedback_signal_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")* *= ''*  
In fast feedback routing, the transmitted signals are associated with this label. ConditionalInstructions whose “condition” field has the string value of feedback_signal_label will receive the signal from this ThresholdStateDiscrimination. Empty string (default) means the signal is not routed anywhere. The same feedback_signal_label may not be used multiple times within the same ReadoutTrigger. The same feedback_signal_label can be used in different ReadoutTriggers and different segments.
