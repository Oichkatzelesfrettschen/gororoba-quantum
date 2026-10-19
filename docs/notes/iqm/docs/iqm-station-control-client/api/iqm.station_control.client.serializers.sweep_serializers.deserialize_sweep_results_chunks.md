> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 72dd0be533e574345cc1cd40366202a63f56a7e41a1bc344f4a45020e5b1ed2e.

# iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks

deserialize_sweep_results_chunks(*sweep_results_chunks*)  
Convert a size-delimited protobuf chunk stream into SweepResults.

Parameters:  
**sweep_results_chunks** ([*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*ndarray*\]\]
