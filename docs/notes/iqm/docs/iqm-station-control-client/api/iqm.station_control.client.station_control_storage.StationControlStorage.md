> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_storage.StationControlStorage.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_storage.StationControlStorage.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dc063fbae80eae1d6932449a949a70a22c5d56925d643c4828d22c4ba385d968.

# StationControlStorage

Module: [`iqm.station_control.client.station_control_storage`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_storage.html#module-iqm.station_control.client.station_control_storage "iqm.station_control.client.station_control_storage")

*class* StationControlStorage(*client*)  
Bases: [`StorageInterface`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.storage_interface.StorageInterface.html#iqm.station_control.interface.storage_interface.StorageInterface "iqm.station_control.interface.storage_interface.StorageInterface")

Concrete implementation of the StorageInterface using an IQM Server backend.

Methods

|  |  |
|----|----|
| [`create_observation_set`](#iqm.station_control.client.station_control_storage.StationControlStorage.create_observation_set "iqm.station_control.client.station_control_storage.StationControlStorage.create_observation_set") | Create an observation set in the database. |
| [`create_observations`](#iqm.station_control.client.station_control_storage.StationControlStorage.create_observations "iqm.station_control.client.station_control_storage.StationControlStorage.create_observations") | Create observations in the database. |
| [`create_sequence_metadata`](#iqm.station_control.client.station_control_storage.StationControlStorage.create_sequence_metadata "iqm.station_control.client.station_control_storage.StationControlStorage.create_sequence_metadata") | Create and persist new sequence metadata in the database. |
| [`deserialize`](#iqm.station_control.client.station_control_storage.StationControlStorage.deserialize "iqm.station_control.client.station_control_storage.StationControlStorage.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`finalize_observation_set`](#iqm.station_control.client.station_control_storage.StationControlStorage.finalize_observation_set "iqm.station_control.client.station_control_storage.StationControlStorage.finalize_observation_set") | Finalize an observation set in the database. |
| [`get_calibration_set`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_calibration_set "iqm.station_control.client.station_control_storage.StationControlStorage.get_calibration_set") | Get a calibration set from the database for the given calibration set ID. |
| [`get_calibration_set_quality_metric_set`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_calibration_set_quality_metric_set "iqm.station_control.client.station_control_storage.StationControlStorage.get_calibration_set_quality_metric_set") | Get the latest quality metric set for the given calibration set ID. |
| [`get_chip_design_record`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_chip_design_record "iqm.station_control.client.station_control_storage.StationControlStorage.get_chip_design_record") | Get the chip design record for the given DUT label. |
| [`get_dut_fields`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_dut_fields "iqm.station_control.client.station_control_storage.StationControlStorage.get_dut_fields") | Get available fields for a specific DUT label from the database. |
| [`get_dynamic_quantum_architecture`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_dynamic_quantum_architecture "iqm.station_control.client.station_control_storage.StationControlStorage.get_dynamic_quantum_architecture") | Get the dynamic quantum architecture for the given calibration set ID. |
| [`get_observation_set`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_observation_set "iqm.station_control.client.station_control_storage.StationControlStorage.get_observation_set") | Get an observation set from the database. |
| [`get_observation_set_observations`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_observation_set_observations "iqm.station_control.client.station_control_storage.StationControlStorage.get_observation_set_observations") | Get the constituent observations of an observation set from the database. |
| [`get_run`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_run "iqm.station_control.client.station_control_storage.StationControlStorage.get_run") | Get run data from the database. |
| [`get_sequence_result`](#iqm.station_control.client.station_control_storage.StationControlStorage.get_sequence_result "iqm.station_control.client.station_control_storage.StationControlStorage.get_sequence_result") | Get sequence result from the database. |
| [`query_observation_sets`](#iqm.station_control.client.station_control_storage.StationControlStorage.query_observation_sets "iqm.station_control.client.station_control_storage.StationControlStorage.query_observation_sets") | Query observation sets from the database. |
| [`query_observations`](#iqm.station_control.client.station_control_storage.StationControlStorage.query_observations "iqm.station_control.client.station_control_storage.StationControlStorage.query_observations") | Query observations from the database. |
| [`query_runs`](#iqm.station_control.client.station_control_storage.StationControlStorage.query_runs "iqm.station_control.client.station_control_storage.StationControlStorage.query_runs") | Query runs from the database. |
| [`query_sequence_metadatas`](#iqm.station_control.client.station_control_storage.StationControlStorage.query_sequence_metadatas "iqm.station_control.client.station_control_storage.StationControlStorage.query_sequence_metadatas") | Query sequence metadatas from the database. |
| [`save_sequence_result`](#iqm.station_control.client.station_control_storage.StationControlStorage.save_sequence_result "iqm.station_control.client.station_control_storage.StationControlStorage.save_sequence_result") | Save sequence result in the database. |
| [`serialize`](#iqm.station_control.client.station_control_storage.StationControlStorage.serialize "iqm.station_control.client.station_control_storage.StationControlStorage.serialize") | Serialize the object instance into a dictionary payload. |
| [`update_observation_set`](#iqm.station_control.client.station_control_storage.StationControlStorage.update_observation_set "iqm.station_control.client.station_control_storage.StationControlStorage.update_observation_set") | Update an observation set in the database. |
| [`update_observations`](#iqm.station_control.client.station_control_storage.StationControlStorage.update_observations "iqm.station_control.client.station_control_storage.StationControlStorage.update_observations") | Update observations in the database. |

Parameters:  
**client** ([*StationControlClient*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.station_control_client.StationControlClient.html#iqm.station_control.client.station_control_client.StationControlClient "iqm.station_control.client.station_control_client.StationControlClient"))

get_chip_design_record(*dut_label*)  
Get the chip design record for the given DUT label.

Parameters:  
**dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_run(*run_id*)  
Get run data from the database.

Parameters:  
**run_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

Return type:  
[*RunData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunData.html#iqm.station_control.interface.models.run.RunData "iqm.station_control.interface.models.run.RunData")

query_runs(*\*\*kwargs*)  
Query runs from the database.

Runs are queried by the given query parameters. Currently supported query parameters:  
- run_id: uuid.UUID

- run_id\_\_in: list\[uuid.UUID\]

- sweep_id: uuid.UUID

- sweep_id\_\_in: list\[uuid.UUID\]

- username: str

- username\_\_in: list\[str\]

- username\_\_contains: str

- username\_\_icontains: str

- experiment_label: str

- experiment_label\_\_in: list\[str\]

- experiment_label\_\_contains: str

- experiment_label\_\_icontains: str

- experiment_name: str

- experiment_name\_\_in: list\[str\]

- experiment_name\_\_contains: str

- experiment_name\_\_icontains: str

- software_version_set_id: int

- software_version_set_id\_\_in: list\[int\]

- begin_timestamp\_\_range: tuple\[datetime, datetime\]

- end_timestamp\_\_range: tuple\[datetime, datetime\]

- end_timestamp\_\_isnull: bool

Returns:  
Queried runs with some query related metadata.

Parameters:  
**kwargs** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*ListWithMeta*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.ListWithMeta.html#iqm.station_control.interface.list_with_meta.ListWithMeta "iqm.station_control.interface.list_with_meta.ListWithMeta")\[[*RunLite*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunLite.html#iqm.station_control.interface.models.run.RunLite "iqm.station_control.interface.models.run.RunLite")\]

create_observations(*observation_definitions*)  
Create observations in the database.

Parameters:  
**observation_definitions** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*ObservationDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationDefinition.html#iqm.station_control.interface.models.observation.ObservationDefinition "iqm.station_control.interface.models.observation.ObservationDefinition")*\]*) – A sequence of observation definitions, each containing the content of the observation which will be created.

Returns:  
Created observations, each including also the database created fields like ID and timestamps.

Return type:  
[*ListWithMeta*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.ListWithMeta.html#iqm.station_control.interface.list_with_meta.ListWithMeta "iqm.station_control.interface.list_with_meta.ListWithMeta")\[[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")\]

query_observations(*\*\*kwargs*)  
Query observations from the database.

Observations are queried by the given query parameters. Currently supported query parameters:  
- observation_id: int

- observation_id\_\_in: list\[int\]

- dut_label: str

- dut_field: str

- dut_field\_\_in: list\[str\]

- tags\_\_overlap: list\[str\]

- tags\_\_contains: list\[str\]

- invalid: bool

- source\_\_run_id\_\_in: list\[uuid.UUID\]

- source\_\_sequence_id\_\_in: list\[uuid.UUID\]

- source\_\_type: str

- observation_set_ids\_\_overlap: list\[uuid.UUID\]

- observation_set_ids\_\_contains: list\[uuid.UUID\]

Returns:  
Queried observations with some query related metadata.

Parameters:  
**kwargs** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*ListWithMeta*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.ListWithMeta.html#iqm.station_control.interface.list_with_meta.ListWithMeta "iqm.station_control.interface.list_with_meta.ListWithMeta")\[[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")\]

update_observations(*observation_updates*)  
Update observations in the database.

Parameters:  
**observation_updates** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*ObservationUpdate*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationUpdate.html#iqm.station_control.interface.models.observation.ObservationUpdate "iqm.station_control.interface.models.observation.ObservationUpdate")*\]*) – A sequence of observation updates, each containing the content of the observation which will be updated.

Returns:  
Updated observations, each including also the database created fields like ID and timestamps.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")\]

query_observation_sets(*\*\*kwargs*)  
Query observation sets from the database.

Observation sets are queried by the given query parameters. Currently supported query parameters:  
- observation_set_id: UUID

- observation_set_id\_\_in: list\[UUID\]

- observation_set_type: Literal\[“calibration-set”, “generic-set”, “quality-metric-set”\]

- describes_id: UUID

- describes_id\_\_in: list\[UUID\]

- invalid: bool

- created_timestamp\_\_range: tuple\[datetime, datetime\]

- dut_label: str

- dut_label\_\_in: list\[str\]

Returns:  
Queried observation sets with some query related metadata

Parameters:  
**kwargs** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*ListWithMeta*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.ListWithMeta.html#iqm.station_control.interface.list_with_meta.ListWithMeta "iqm.station_control.interface.list_with_meta.ListWithMeta")\[[*ObservationSetData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetData.html#iqm.station_control.interface.models.observation_set.ObservationSetData "iqm.station_control.interface.models.observation_set.ObservationSetData")\]

create_observation_set(*observation_set_definition*)  
Create an observation set in the database.

Parameters:  
**observation_set_definition** ([*ObservationSetDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetDefinition.html#iqm.station_control.interface.models.observation_set.ObservationSetDefinition "iqm.station_control.interface.models.observation_set.ObservationSetDefinition")) – The content of the observation set to be created.

Returns:  
The content of the observation set.

Raises:  
**IQMError** – If creation failed.

Return type:  
[*ObservationSetData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetData.html#iqm.station_control.interface.models.observation_set.ObservationSetData "iqm.station_control.interface.models.observation_set.ObservationSetData")

get_observation_set(*observation_set_id*)  
Get an observation set from the database.

Parameters:  
**observation_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – Observation set to retrieve.

Returns:  
The content of the observation set.

Raises:  
**IQMError** – If retrieval failed.

Return type:  
[*ObservationSetData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetData.html#iqm.station_control.interface.models.observation_set.ObservationSetData "iqm.station_control.interface.models.observation_set.ObservationSetData")

update_observation_set(*observation_set_update*)  
Update an observation set in the database.

Parameters:  
**observation_set_update** ([*ObservationSetUpdate*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetUpdate.html#iqm.station_control.interface.models.observation_set.ObservationSetUpdate "iqm.station_control.interface.models.observation_set.ObservationSetUpdate")) – The content of the observation set to be updated.

Returns:  
The content of the observation set.

Raises:  
**IQMError** – If updating failed.

Return type:  
[*ObservationSetData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetData.html#iqm.station_control.interface.models.observation_set.ObservationSetData "iqm.station_control.interface.models.observation_set.ObservationSetData")

finalize_observation_set(*observation_set_id*)  
Finalize an observation set in the database.

A finalized set is nearly immutable, allowing to change only `invalid` flag after finalization.

Parameters:  
**observation_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – Observation set to finalize.

Raises:  
**IQMError** – If finalization failed.

Return type:  
*None*

get_observation_set_observations(*observation_set_id*)  
Get the constituent observations of an observation set from the database.

Parameters:  
**observation_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – UUID of the observation set to retrieve.

Returns:  
Observations belonging to the given observation set.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationData.html#iqm.station_control.interface.models.observation.ObservationData "iqm.station_control.interface.models.observation.ObservationData")\]

get_calibration_set(*calibration_set_id*)  
Get a calibration set from the database for the given calibration set ID.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
[*ObservationSetWithObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.html#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData")

get_dynamic_quantum_architecture(*calibration_set_id*)  
Get the dynamic quantum architecture for the given calibration set ID.

Returns:  
Dynamic quantum architecture of the quantum computer for the given calibration set ID.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
[*DynamicQuantumArchitecture*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.html#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture")

get_calibration_set_quality_metric_set(*calibration_set_id*)  
Get the latest quality metric set for the given calibration set ID.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
[*ObservationSetWithObservationData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData.html#iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData "iqm.station_control.interface.models.observation_set.ObservationSetWithObservationData")

get_dut_fields(*dut_label*)  
Get available fields for a specific DUT label from the database.

Scans every field ever observed for the DUT, independent of any actual query need. Prefer filtering observations directly (e.g. by tags or observation set) instead of enumerating all dut fields upfront.

This method will be removed in a future release.

Parameters:  
**dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*DutFieldData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutFieldData.html#iqm.station_control.interface.models.dut.DutFieldData "iqm.station_control.interface.models.dut.DutFieldData")\]

query_sequence_metadatas(*\*\*kwargs*)  
Query sequence metadatas from the database.

Sequence metadatas are queried by the given query parameters. Currently supported query parameters:  
- origin_id: str

- origin_id\_\_in: list\[str\]

- origin_uri: str

- origin_uri\_\_icontains: str

- created_timestamp\_\_range: tuple\[datetime, datetime\]

Returns:  
Sequence metadatas with some query related metadata.

Parameters:  
**kwargs** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"))

Return type:  
[*ListWithMeta*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.ListWithMeta.html#iqm.station_control.interface.list_with_meta.ListWithMeta "iqm.station_control.interface.list_with_meta.ListWithMeta")\[[*SequenceMetadataData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataData.html#iqm.station_control.interface.models.sequence.SequenceMetadataData "iqm.station_control.interface.models.sequence.SequenceMetadataData")\]

create_sequence_metadata(*sequence_metadata_definition*)  
Create and persist new sequence metadata in the database.

Parameters:  
**sequence_metadata_definition** ([*SequenceMetadataDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataDefinition.html#iqm.station_control.interface.models.sequence.SequenceMetadataDefinition "iqm.station_control.interface.models.sequence.SequenceMetadataDefinition"))

Return type:  
[*SequenceMetadataData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataData.html#iqm.station_control.interface.models.sequence.SequenceMetadataData "iqm.station_control.interface.models.sequence.SequenceMetadataData")

save_sequence_result(*sequence_result_definition*)  
Save sequence result in the database.

This method creates the object if it doesn’t exist and completely replaces the “data” and “final” if it does. Timestamps are assigned by the database. “modified_timestamp” is not set on initial creation, but it’s updated on each subsequent call.

Parameters:  
**sequence_result_definition** ([*SequenceResultDefinition*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultDefinition.html#iqm.station_control.interface.models.sequence.SequenceResultDefinition "iqm.station_control.interface.models.sequence.SequenceResultDefinition"))

Return type:  
[*SequenceResultData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultData.html#iqm.station_control.interface.models.sequence.SequenceResultData "iqm.station_control.interface.models.sequence.SequenceResultData")

get_sequence_result(*sequence_id*)  
Get sequence result from the database.

Parameters:  
**sequence_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

Return type:  
[*SequenceResultData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultData.html#iqm.station_control.interface.models.sequence.SequenceResultData "iqm.station_control.interface.models.sequence.SequenceResultData")

serialize()  
Serialize the object instance into a dictionary payload.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data*)  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*StationControlStorage*](#iqm.station_control.client.station_control_storage.StationControlStorage "iqm.station_control.client.station_control_storage.StationControlStorage")

Inheritance

![Inheritance diagram of iqm.station_control.client.station_control_storage.StationControlStorage](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a76602786c5d2b2437314ffc3e4266b8228db1a7.png)
