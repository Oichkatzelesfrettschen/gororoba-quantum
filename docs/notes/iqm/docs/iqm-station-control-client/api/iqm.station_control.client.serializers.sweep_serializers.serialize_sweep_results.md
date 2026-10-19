> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f949b650ae2247568b76b89f2e32fb25d6c67e5be7afa175aa9e2458c3914584.

# iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results

serialize_sweep_results(*sweep_id*, *sweep_results*)  
Convert SweepResults into binary string.

Parameters:  
- **sweep_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **sweep_results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[ndarray\]\]*)

Return type:  
[*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")
