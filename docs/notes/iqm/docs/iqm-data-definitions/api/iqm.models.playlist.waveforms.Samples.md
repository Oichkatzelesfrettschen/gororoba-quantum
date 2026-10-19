> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Samples.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Samples.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 57a445f6b294a8be92e2b2b7806f6394e04166ee81d72c37ed685bb169b8191f.

# Samples

*class* iqm.models.playlist.waveforms.Samples(*samples*)  
Bases: [`Waveform`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html#iqm.models.playlist.waveforms.Waveform "iqm.models.playlist.waveforms.Waveform")

Custom pre-sampled waveform.

This class can be used to represent an arbitrary waveform that is not supported with the predefined shapes of waveforms.

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|             |                                               |
|-------------|-----------------------------------------------|
| `samples`   |                                               |
| `n_samples` | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`sample`](#iqm.models.playlist.waveforms.Samples.sample "iqm.models.playlist.waveforms.Samples.sample") | Sample the waveform. |

Parameters:  
**samples** (*ndarray*)

sample()  
Sample the waveform.

Contains the boilerplate code for determining the sample coordinates, the actual sampling happens in `_sample()`.

Returns:  
`self` sampled in the window \[-1/2, 1/2\]

Return type:  
*ndarray*
