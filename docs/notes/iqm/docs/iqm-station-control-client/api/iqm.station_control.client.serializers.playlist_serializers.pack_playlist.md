> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.pack_playlist.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.pack_playlist.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e95c55cab0ff02ddd3adfbe515e7b99d9372bdd683d4523c6d4116314f66ac10.

# iqm.station_control.client.serializers.playlist_serializers.pack_playlist

pack_playlist(*playlist*)  
Pack the given playlist into a protobuf format for further serialization.

Parameters:  
**playlist** ([*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)")) – playlist to pack

Returns:  
`playlist` in protobuf format

Return type:  
[*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.data_definitions.common.v1.playlist_pb2.Playlist.html#iqm.data_definitions.common.v1.playlist_pb2.Playlist "(in IQM data definitions v3.1.0)")
