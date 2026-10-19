> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.varint_serializers.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.varint_serializers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6b9a2b42740703fb071deed11cf06cad3fd2794dd65be9ddd4fc81ac30bd9082.

# varint_serializers

Full path: iqm.station_control.client.serializers.varint_serializers

Helpers for protobuf-style varint serialization.

Protobuf automatically varint-encodes integer values inside a message body. These functions are needed when a varint must appear outside any message - for example, as a length prefix in a hand-assembled byte stream - where the protobuf library has no opportunity to perform the encoding automatically.

Functions

|  |  |
|----|----|
| [`decode_varint`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.varint_serializers.decode_varint.html#iqm.station_control.client.serializers.varint_serializers.decode_varint "iqm.station_control.client.serializers.varint_serializers.decode_varint")(buffer, offset) | Decode a protobuf varint from `buffer` starting at `offset`. |
| [`encode_varint`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.varint_serializers.encode_varint.html#iqm.station_control.client.serializers.varint_serializers.encode_varint "iqm.station_control.client.serializers.varint_serializers.encode_varint")(value) | Encode a non-negative integer using protobuf varint encoding. |
