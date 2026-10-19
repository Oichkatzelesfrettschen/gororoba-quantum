> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6157571af8282092ae368ee63fb3f72537f4cbc19fdc827bb7a023d83eb415a5.

# iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations

iqm.cpc.core.observation.observation_load_utils.get_observation_set_observations(*set_ids*, *storage*, *dut_label*)  
Loads all observations related to a given observation set, one set at a time.

Parameters:  
- **set_ids** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*,* *...\]*) – The observation set IDs to load observations for.

- **storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The storage backend to query.

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label of the device being used.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)")\]
