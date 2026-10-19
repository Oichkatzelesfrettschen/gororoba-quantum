> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.unpack_playlist.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.unpack_playlist.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 174c6eab88b27982d0e586fe2c9e9e5258fd04d508eab811dae7fba377580453.

# iqm.station_control.client.serializers.playlist_serializers.unpack_playlist

unpack_playlist(*proto_playlist*)  
Unpack a protobuf representation of a playlist into its runtime representation.

Parameters:  
**proto_playlist** ([*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.playlist_pb2.Playlist.html#iqm.data_definitions.common.v1.playlist_pb2.Playlist "(in IQM data definitions v3.1.0)")) – serialized playlist

Returns:  
`proto_playlist` in runtime representation

Return type:  
[*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)")
