> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1f4f2df06bb4aded09afce84bac945db1ebc211d4704788c59a3f790c327113d.

# iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data

iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_data(*set_type*, *finalized=True*, *\**, *storage*, *dut_label*)  
Find the latest finalized observation set of given type.

Parameters:  
- **set_type** ([*ObservationSetType*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html#iqm.station_control.interface.models.observation_set.ObservationSetType "(in iqm-station-control-client v14.0.0)")) – Type of set to look for.

- **finalized** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, only finalized sets are considered.

- **storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The storage backend to query.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label of the device being used.

Returns:  
Metadata of the found set. None if no set is found.

Return type:  
[*ObservationSetData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetData.html#iqm.station_control.interface.models.observation_set.ObservationSetData "(in iqm-station-control-client v14.0.0)") \| None
