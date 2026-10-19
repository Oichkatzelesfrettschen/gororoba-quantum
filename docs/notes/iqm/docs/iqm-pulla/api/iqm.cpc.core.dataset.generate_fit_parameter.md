> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.generate_fit_parameter.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.generate_fit_parameter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4c6f68e71ff005830a44bd050a9880561f664573e04778085358565b5de05542.

# iqm.cpc.core.dataset.generate_fit_parameter

iqm.cpc.core.dataset.generate_fit_parameter(*data*)  
Construct a Parameter representing a fit to the given data array.

The name of the generated parameter will be `<name of array>_fit` . The Parameter gets its unit from the dataset and its data_type from the data variable.

Parameters:  
**data** (*DataArray*) – dataArray that contains the raw data.

Returns:  
Generated parameter.

Return type:  
[*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)")
