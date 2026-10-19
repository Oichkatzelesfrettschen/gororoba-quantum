> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.PHOTON_CONVERSION_FACTOR_E.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_parameters.PHOTON_CONVERSION_FACTOR_E.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6a11c7e6694d104e5170818d7694d0751263a6b520e470f3b852127f01b8fa0f.

# PHOTON_CONVERSION_FACTOR_E

iqm.cpc.core.observation.observation_parameters.PHOTON_CONVERSION_FACTOR_E *= Parameter(name='photon_conversion_factor_e', label='Linear conversion factor between readout amplitude and photon number for e state', unit='Hz', data_type=\<DataType.FLOAT: 1\>, collection_type=\<CollectionType.SCALAR: 0\>, element_indices=None)*  
Conversion factor between readout DAC amplitude and photon numbers. Conversion defined as: A^2 \* a_dac\*2 = n where A is the photon conversion factor, a_dac is the amplitude in arbitrary units and n is the number of photons.
