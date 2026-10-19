> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CanonicalWaveform.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.CanonicalWaveform.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 194cd239b53a7efee7e0c9a9df326277b3e948fdeaaa076d0428a57b3a9d983a.

# CanonicalWaveform

iqm.models.playlist.waveforms.CanonicalWaveform  
Alias for Waveform to emphasize the fact the waveforms defined in this module have their own serialisation.

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|             |                                               |
|-------------|-----------------------------------------------|
| `n_samples` | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| `non_timelike_attributes` | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |
| `sample` | Sample the waveform. |
