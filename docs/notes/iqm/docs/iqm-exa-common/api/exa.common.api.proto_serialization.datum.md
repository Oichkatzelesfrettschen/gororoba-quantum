> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 61fee36e9cae77ed7236a92975827cd3a684c3e87844c5ff00360ba9d2d1ec4c.

# datum

Full path: exa.common.api.proto_serialization.datum

Convert native Python types and numpy arrays to protos and back.

Functions

|  |  |
|----|----|
| [`deserialize`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.deserialize.html#exa.common.api.proto_serialization.datum.deserialize "exa.common.api.proto_serialization.datum.deserialize")(source) | Deserialize a bitstring into a native Python type or a numpy array. |
| [`pack`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.pack.html#exa.common.api.proto_serialization.datum.pack "exa.common.api.proto_serialization.datum.pack")(value) | Packs a string, numerical value, or an array thereof into protobuf format. |
| [`serialize`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.serialize.html#exa.common.api.proto_serialization.datum.serialize "exa.common.api.proto_serialization.datum.serialize")(value) | Serialize a piece of data into a bitstring. |
| [`unpack`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.api.proto_serialization.datum.unpack.html#exa.common.api.proto_serialization.datum.unpack "exa.common.api.proto_serialization.datum.unpack")(source) | Unpacks a protobuf into a native Python type or a numpy array. |
