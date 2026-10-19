> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.AVERAGE_RESPONSE_PHASE.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.AVERAGE_RESPONSE_PHASE.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0adf442d81e88969330bde683fdb7d68c17072c747f57e0dcc690ea7b4d46438.

# AVERAGE_RESPONSE_PHASE

iqm.cpc.core.observation.observation_parameters.AVERAGE_RESPONSE_PHASE *= Parameter(name='average_response_phase', label='Average phase accumulation of response', unit='rad', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)*  
Inverse of the phase of average response signal, assuming 0 phase in probe pulse. The complex signal is rotated in the IQ plane by 2 factors: SINGLE_SHOT_READOUT_PHASE which is deliberately added to the probe pulse, and factors related to the signal travel time in the physical setup (=\`AVERAGE_RESPONSE_PHASE\`). This value, together with AVERAGE_RESPONSE_G and AVERAGE_RESPONSE_E, is used to convert measured complex signals to probabilities *in software* by rotating the signals to the real in axis. The rotation angle is the difference of this value and SINGLE_SHOT_READOUT_PHASE. When calibrated correctly, this value equals SINGLE_SHOT_READOUT_PHASE, such that the correct rotation is done by the pulse, and the received complex values do not need to be rotated.
