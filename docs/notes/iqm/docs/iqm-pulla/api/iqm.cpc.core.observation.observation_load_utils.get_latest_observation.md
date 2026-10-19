> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_latest_observation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ffffea78d60775df343a6dc24da286b4797d03f9dbff22b994ce952d959ed5a6.

# iqm.cpc.core.observation.observation_load_utils.get_latest_observation

iqm.cpc.core.observation.observation_load_utils.get_latest_observation(*dut_field*, *\**, *storage*, *dut_label*, *include_invalid=False*, *tags=None*, *set_id=None*)  
Get the latest valid observation for the given DUT, based on the created timestamp.

If no observation was found, None is returned.

Parameters:  
- **dut_field** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – the name of the observable to search by.

- **storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)")) – The storage backend to query.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label of the device being used.

- **include_invalid** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – when True, also observations marked as `invalid` are included in the query.

- **tags** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – The tags to filter the observation with. The observations need to have every one of the given tags associated with them.

- **set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*) – The observation set the observation is associated with.

Returns:  
Observation or None

Return type:  
[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)") \| None
