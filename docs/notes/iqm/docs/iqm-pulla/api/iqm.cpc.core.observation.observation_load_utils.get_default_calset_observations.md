> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b1061732444a382b6feb9193988c8c2223ac2575608681b412ac065eafc1b38b.

# iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations

iqm.cpc.core.observation.observation_load_utils.get_default_calset_observations(*storage*)  
Loads all observations related to the default calibration set.

Parameters:  
**storage** ([*StorageInterface*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "(in iqm-station-control-client v14.0.0)") *\|* *None*) – The storage backend to query.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "(in iqm-station-control-client v14.0.0)")\]
