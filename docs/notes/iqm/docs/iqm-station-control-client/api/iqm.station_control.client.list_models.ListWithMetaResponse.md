> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListWithMetaResponse.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListWithMetaResponse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9f38ded95bcef52b76b34a1cfdfb0569f403664d78e402d4cd0fdd3b4c559ece.

# ListWithMetaResponse

Module: [`iqm.station_control.client.list_models`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.html#module-iqm.station_control.client.list_models "iqm.station_control.client.list_models")

*class* ListWithMetaResponse(*\**, *items*, *meta=None*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase"), [`Generic`](https://docs.python.org/3.11/library/typing.html#typing.Generic "(in Python v3.11)")\[`T`\]

Class used for list endpoints to envelope the items to a dict with additional metadata.

This should be used only in REST API communication (JSON). For Python users, this model should be deserialized to `iqm.pulse.ListWithMeta`:, which behaves like a standard list.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.client.list_models.ListWithMetaResponse.model_config "iqm.station_control.client.list_models.ListWithMetaResponse.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `items` |  |
| `meta` |  |

Methods

Parameters:  
- **items** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[T\]*)

- **meta** ([*Meta*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.list_with_meta.Meta.html#iqm.station_control.interface.list_with_meta.Meta "iqm.station_control.interface.list_with_meta.Meta") *\|* *None*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.client.list_models.ListWithMetaResponse](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-ee07cad3cdcbeac63f0e120594c5f843c76257c2.png)
