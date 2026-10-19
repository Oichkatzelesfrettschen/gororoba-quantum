> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d3240f27ce6b8daae12981243222842bf07a3988d537f1ae23f364d7a53908f9.

# database_serialization

Full path: exa.common.sweep.database_serialization

Functions that encode and decode all sweep arguments(different types of sweeps, return parameters, settings, etc.). The module provides functions for serializing and deserializing sweep arguments before saving them to database.

Functions

|  |  |
|----|----|
| [`decode_and_validate_sweeps`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_and_validate_sweeps.html#exa.common.sweep.database_serialization.decode_and_validate_sweeps "exa.common.sweep.database_serialization.decode_and_validate_sweeps")(sweeps_json) | Decodes and validates json string of list of Sweeps and tuples of Sweeps. |
| [`decode_return_parameters`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_return_parameters.html#exa.common.sweep.database_serialization.decode_return_parameters "exa.common.sweep.database_serialization.decode_return_parameters")(json_str) | Deserialize return parameters. |
| [`decode_settings`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.decode_settings.html#exa.common.sweep.database_serialization.decode_settings "exa.common.sweep.database_serialization.decode_settings")(json_str) | Deserialize settings from json string |
| [`encode_nd_sweeps`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.encode_nd_sweeps.html#exa.common.sweep.database_serialization.encode_nd_sweeps "exa.common.sweep.database_serialization.encode_nd_sweeps")(sweeps, \*\*kwargs) | Encode sweeps to a JSON string. |
| [`encode_return_parameters`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.database_serialization.encode_return_parameters.html#exa.common.sweep.database_serialization.encode_return_parameters "exa.common.sweep.database_serialization.encode_return_parameters")(return_parameters, ...) | Encode sweeps to a JSON string. |
