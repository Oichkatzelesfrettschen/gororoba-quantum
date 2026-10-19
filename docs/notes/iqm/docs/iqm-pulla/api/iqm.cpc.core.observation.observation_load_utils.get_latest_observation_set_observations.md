> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fc792de8064fa94c2d930b7989a09109922be5c925f10d50712952f24ef60739.

# iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations

iqm.cpc.core.observation.observation_load_utils.get_latest_observation_set_observations(*set_type*, *finalized=True*, *\**, *storage*, *dut_label*)  
Loads all observations related to the latest finalized observation set of given type.

Parameters:  
- **set_type** ([*ObservationSetType*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html#iqm.station_control.interface.models.observation_set.ObservationSetType "(in iqm-station-control-client v14.0.0)")) – Type of set to look for.

- **finalized** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, only finalized sets are considered.

- **storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The storage backend to query.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label of the device being used.

Returns:  
Dict of observations in the found set. If no set is found, the dict is empty.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)")\]
