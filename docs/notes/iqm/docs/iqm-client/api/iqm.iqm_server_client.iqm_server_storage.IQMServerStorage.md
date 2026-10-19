> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7c4e67b5b74ac51b1a393dae2984c1d9e2d35f079276361c68d38635acc93987.

# IQMServerStorage

Module: [`iqm.iqm_server_client.iqm_server_storage`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_storage.html#module-iqm.iqm_server_client.iqm_server_storage "iqm.iqm_server_client.iqm_server_storage")

*class* iqm.iqm_server_client.iqm_server_storage.IQMServerStorage(*client: [IQMServerClient](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient")*)  
Bases: `StorageInterface`

Concrete implementation of the StorageInterface using an IQM Server backend.

Methods

|  |  |
|----|----|
| [`create_observation_set`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.create_observation_set "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.create_observation_set") | Create an observation set in the database. |
| [`create_observations`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.create_observations "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.create_observations") | Not yet supported. |
| [`create_sequence_metadata`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.create_sequence_metadata "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.create_sequence_metadata") | Create and persist new sequence metadata in the database. |
| [`deserialize`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.deserialize "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.deserialize") | Reconstruct an instance from a dictionary payload. |
| [`finalize_observation_set`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.finalize_observation_set "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.finalize_observation_set") | Finalize an observation set in the database. |
| [`get_calibration_set`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_calibration_set "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_calibration_set") | Get a calibration set from the database for the given calibration set ID. |
| [`get_calibration_set_quality_metric_set`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_calibration_set_quality_metric_set "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_calibration_set_quality_metric_set") | Get the latest quality metric set for the given calibration set ID. |
| [`get_chip_design_record`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_chip_design_record "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_chip_design_record") | Get the chip design record for the given DUT label. |
| [`get_dut_fields`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_dut_fields "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_dut_fields") | Get available fields for a specific DUT label from the database. |
| [`get_dynamic_quantum_architecture`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_dynamic_quantum_architecture "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_dynamic_quantum_architecture") | Get the dynamic quantum architecture for the given calibration set ID. |
| [`get_observation_set`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_observation_set "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_observation_set") | Get an observation set from the database. |
| [`get_observation_set_observations`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_observation_set_observations "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_observation_set_observations") | Get the constituent observations of an observation set from the database. |
| [`get_run`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_run "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_run") | Get run data from the database. |
| [`get_sequence_result`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_sequence_result "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.get_sequence_result") | Get sequence result from the database. |
| [`query_observation_sets`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_observation_sets "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_observation_sets") | Query observation sets from the database. |
| [`query_observations`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_observations "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_observations") | Query observations from the database. |
| [`query_runs`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_runs "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_runs") | Query runs from the database. |
| [`query_sequence_metadatas`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_sequence_metadatas "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.query_sequence_metadatas") | Query sequence metadatas from the database. |
| [`save_sequence_result`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.save_sequence_result "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.save_sequence_result") | Save sequence result in the database. |
| [`serialize`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.serialize "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.serialize") | Serialize the object instance into a dictionary payload. |
| [`update_observation_set`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.update_observation_set "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.update_observation_set") | Update an observation set in the database. |
| [`update_observations`](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.update_observations "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage.update_observations") | Update observations in the database. |

Parameters:  
**client** ([*IQMServerClient*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_server_client.iqm_server_client.IQMServerClient.html#iqm.iqm_server_client.iqm_server_client.IQMServerClient "iqm.iqm_server_client.iqm_server_client.IQMServerClient"))

get_chip_design_record(*dut_label: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Get the chip design record for the given DUT label.

Parameters:  
**dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

get_run(*run_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → RunData  
Get run data from the database.

Parameters:  
**run_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

Return type:  
*RunData*

query_runs(*\*\*kwargs: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*) → ListWithMeta\[RunLite\]  
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
*ListWithMeta*\[*RunLite*\]

create_observations(*observation_definitions: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[ObservationDefinition\]*) → ListWithMeta\[ObservationData\]  
Not yet supported.

Since IqmServerExecutor does not proxy the job sumbission, observations also can’t be saved, due to there not being any job in station-control to link them to.

Parameters:  
**observation_definitions** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[ObservationDefinition\]*)

Return type:  
*ListWithMeta*\[*ObservationData*\]

query_observations(*\*\*kwargs: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*) → ListWithMeta\[ObservationData\]  
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
*ListWithMeta*\[*ObservationData*\]

update_observations(*observation_updates: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[ObservationUpdate\]*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[ObservationData\]  
Update observations in the database.

Parameters:  
**observation_updates** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[ObservationUpdate\]*) – A sequence of observation updates, each containing the content of the observation which will be updated.

Returns:  
Updated observations, each including also the database created fields like ID and timestamps.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*ObservationData*\]

query_observation_sets(*\*\*kwargs: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*) → ListWithMeta\[ObservationSetData\]  
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
*ListWithMeta*\[*ObservationSetData*\]

create_observation_set(*observation_set_definition: ObservationSetDefinition*) → ObservationSetData  
Create an observation set in the database.

Parameters:  
**observation_set_definition** (*ObservationSetDefinition*) – The content of the observation set to be created.

Returns:  
The content of the observation set.

Raises:  
**IQMError** – If creation failed.

Return type:  
*ObservationSetData*

get_observation_set(*observation_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → ObservationSetData  
Get an observation set from the database.

Parameters:  
**observation_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – Observation set to retrieve.

Returns:  
The content of the observation set.

Raises:  
**IQMError** – If retrieval failed.

Return type:  
*ObservationSetData*

update_observation_set(*observation_set_update: ObservationSetUpdate*) → ObservationSetData  
Update an observation set in the database.

Parameters:  
**observation_set_update** (*ObservationSetUpdate*) – The content of the observation set to be updated.

Returns:  
The content of the observation set.

Raises:  
**IQMError** – If updating failed.

Return type:  
*ObservationSetData*

finalize_observation_set(*observation_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Finalize an observation set in the database.

A finalized set is nearly immutable, allowing to change only `invalid` flag after finalization.

Parameters:  
**observation_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – Observation set to finalize.

Raises:  
**IQMError** – If finalization failed.

Return type:  
None

get_observation_set_observations(*observation_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[ObservationData\]  
Get the constituent observations of an observation set from the database.

Parameters:  
**observation_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")) – UUID of the observation set to retrieve.

Returns:  
Observations belonging to the given observation set.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*ObservationData*\]

get_calibration_set(*calibration_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['default'\]*) → ObservationSetWithObservationData  
Get a calibration set from the database for the given calibration set ID.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
*ObservationSetWithObservationData*

get_dynamic_quantum_architecture(*calibration_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['default'\]*) → DynamicQuantumArchitecture  
Get the dynamic quantum architecture for the given calibration set ID.

Returns:  
Dynamic quantum architecture of the quantum computer for the given calibration set ID.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
*DynamicQuantumArchitecture*

get_calibration_set_quality_metric_set(*calibration_set_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") \| [Literal](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")\['default'\]*) → ObservationSetWithObservationData  
Get the latest quality metric set for the given calibration set ID.

Parameters:  
**calibration_set_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* [*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['default'\]*)

Return type:  
*ObservationSetWithObservationData*

get_dut_fields(*dut_label: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[DutFieldData\]  
Get available fields for a specific DUT label from the database.

Scans every field ever observed for the DUT, independent of any actual query need. Prefer filtering observations directly (e.g. by tags or observation set) instead of enumerating all dut fields upfront.

This method will be removed in a future release.

Parameters:  
**dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*DutFieldData*\]

query_sequence_metadatas(*\*\*kwargs: [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*) → ListWithMeta\[SequenceMetadataData\]  
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
*ListWithMeta*\[*SequenceMetadataData*\]

create_sequence_metadata(*sequence_metadata_definition: SequenceMetadataDefinition*) → SequenceMetadataData  
Create and persist new sequence metadata in the database.

Parameters:  
**sequence_metadata_definition** (*SequenceMetadataDefinition*)

Return type:  
*SequenceMetadataData*

save_sequence_result(*sequence_result_definition: SequenceResultDefinition*) → SequenceResultData  
Save sequence result in the database.

This method creates the object if it doesn’t exist and completely replaces the “data” and “final” if it does. Timestamps are assigned by the database. “modified_timestamp” is not set on initial creation, but it’s updated on each subsequent call.

Parameters:  
**sequence_result_definition** (*SequenceResultDefinition*)

Return type:  
*SequenceResultData*

get_sequence_result(*sequence_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*) → SequenceResultData  
Get sequence result from the database.

Parameters:  
**sequence_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

Return type:  
*SequenceResultData*

serialize() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Serialize the object instance into a dictionary payload.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* deserialize(*data: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [IQMServerStorage](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage")  
Reconstruct an instance from a dictionary payload.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*IQMServerStorage*](#iqm.iqm_server_client.iqm_server_storage.IQMServerStorage "iqm.iqm_server_client.iqm_server_storage.IQMServerStorage")

Inheritance

![Inheritance diagram of iqm.iqm_server_client.iqm_server_storage.IQMServerStorage](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-c0dba150ccdad7ff7c7a1588513bae508e96a500.png)
