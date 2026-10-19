> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1babf69bc3963137418a1637af03d768f4c7bc5a88c3b38683e28a39ba2c3b1a.

# sweep_serializers

Full path: iqm.station_control.client.serializers.sweep_serializers

Serializers and deserializers for sweep related models.

Functions

|  |  |
|----|----|
| [`deserialize_sweep_data`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_data.html#iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_data "iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_data")(data) | Convert JSON serializable dictionary into SweepData. |
| [`deserialize_sweep_definition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_definition.html#iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_definition "iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_definition")(...) | Convert sweep proto into SweepDefinition. |
| [`deserialize_sweep_results`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results.html#iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results "iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results")(sweep_results_str) | Convert binary string into SweepResults. |
| [`deserialize_sweep_results_chunks`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks.html#iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks "iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks")(...) | Convert a size-delimited protobuf chunk stream into SweepResults. |
| [`serialize_sweep_definition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_definition.html#iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_definition "iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_definition")(sweep_definition) | Convert SweepDefinition into sweep proto. |
| [`serialize_sweep_results`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results.html#iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results "iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results")(sweep_id, sweep_results) | Convert SweepResults into binary string. |
| [`serialize_sweep_results_chunk`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results_chunk.html#iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results_chunk "iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results_chunk")(sweep_id, ...) | Serialize one sweep result item as a size-delimited protobuf chunk. |

Classes

|  |  |
|----|----|
| [`SweepResultsArtifactFormat`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.SweepResultsArtifactFormat.html#iqm.station_control.client.serializers.sweep_serializers.SweepResultsArtifactFormat "iqm.station_control.client.serializers.sweep_serializers.SweepResultsArtifactFormat") | Supported artifact payload formats for sweep results. |

Inheritance

![Inheritance diagram of iqm.station_control.client.serializers.sweep_serializers](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-7e4fe055ca7e01219680f80ae1dd4ddfea9285b7.png)
