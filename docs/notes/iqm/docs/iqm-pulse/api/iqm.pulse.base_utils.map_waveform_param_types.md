> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.base_utils.map_waveform_param_types.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.base_utils.map_waveform_param_types.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 78083d361e69936ecaabd33d083ad751d0e172285d919c0e4a6a20f171a20a17.

# iqm.pulse.base_utils.map_waveform_param_types

iqm.pulse.base_utils.map_waveform_param_types(*type_hint*)  
Map a Python typehint into EXA Parameter’s `(DataType, CollectionType)` tuple.

Parameters:  
**type_hint** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")) – Python typehint.

Returns:  
Corresponding EXA `Parameter` type.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – for a non-supported type.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*DataType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "(in iqm-exa-common v29.0.0)"), [*CollectionType*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "(in iqm-exa-common v29.0.0)")\]
