> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b72dcb82f4724ac1a02a06dbd97a7e999530d55d72be5e6f159cb5505d530641.

# playlist_serializers

Full path: iqm.station_control.client.serializers.playlist_serializers

Serializers and deserializers for [`Playlist`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)")

Functions

|  |  |
|----|----|
| [`pack_playlist`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.pack_playlist.html#iqm.station_control.client.serializers.playlist_serializers.pack_playlist "iqm.station_control.client.serializers.playlist_serializers.pack_playlist")(playlist) | Pack the given playlist into a protobuf format for further serialization. |
| [`unpack_playlist`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.serializers.playlist_serializers.unpack_playlist.html#iqm.station_control.client.serializers.playlist_serializers.unpack_playlist "iqm.station_control.client.serializers.playlist_serializers.unpack_playlist")(proto_playlist) | Unpack a protobuf representation of a playlist into its runtime representation. |
