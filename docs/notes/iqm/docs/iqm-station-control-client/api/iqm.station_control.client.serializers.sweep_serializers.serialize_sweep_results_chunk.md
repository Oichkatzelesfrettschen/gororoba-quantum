> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results_chunk.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results_chunk.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 685da65fe3c7267814fdcf9264053bba68affb78f14b7bc0f3a651b96db89941.

# iqm.station_control.client.serializers.sweep_serializers.serialize_sweep_results_chunk

serialize_sweep_results_chunk(*sweep_id*, *spot_idx*, *return_parameter*, *result_value*)  
Serialize one sweep result item as a size-delimited protobuf chunk.

The wire format is the standard length-delimited protobuf stream encoding (see [https://protobuf.dev/programming-guides/techniques/#streaming](https://protobuf.dev/programming-guides/techniques/#streaming)): each chunk is `varint(len) || SweepResultsChunk.SerializeToString()`. The length prefix sits outside the message body, so it must be varint-encoded manually - protobuf only handles varint encoding for fields inside a message. Using a varint for the length prefix is the conventional protobuf framing choice. Chunks are concatenated to form the STREAMING_V2 artifact; the stream is decoded by [`deserialize_sweep_results_chunks()`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks.html#iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks "iqm.station_control.client.serializers.sweep_serializers.deserialize_sweep_results_chunks").

Parameters:  
- **sweep_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **spot_idx** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **return_parameter** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **result_value** (*ndarray*)

Return type:  
[*bytes*](https://docs.python.org/3.11/library/stdtypes.html#bytes "(in Python v3.11)")
