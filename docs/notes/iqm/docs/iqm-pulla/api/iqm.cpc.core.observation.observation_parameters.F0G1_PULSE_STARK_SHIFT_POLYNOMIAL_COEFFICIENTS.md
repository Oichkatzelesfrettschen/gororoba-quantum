> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.F0G1_PULSE_STARK_SHIFT_POLYNOMIAL_COEFFICIENTS.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.F0G1_PULSE_STARK_SHIFT_POLYNOMIAL_COEFFICIENTS.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4e9f6ba389fc667605e66f86f4b1d2cdd1025fc491ad5242af3b9e4ca5e1f25c.

# F0G1_PULSE_STARK_SHIFT_POLYNOMIAL_COEFFICIENTS

iqm.cpc.core.observation.observation_parameters.F0G1_PULSE_STARK_SHIFT_POLYNOMIAL_COEFFICIENTS *= Parameter(name='f0g1_pulse_stark_shift_polynomial_coefficients', label='F0G1 pulse stark shift polynomial coefficients', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.LIST: 1\>, element_indices=None)*  
Polynomial coefficients of the 1D curve in amplitude-frequency plane, used to search for the optimal IQPulse modulation frequency to drive the F0G1 transition while taking into the account the AC Stark shift at a certain amplitude (used for `lru` or `reset` gates).
