> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.json_helper.get_json_encoder.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.helpers.json_helper.get_json_encoder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1bd06cef8c710346a99170ea58dc503450821a2007cc1bfa2516c56d3006dbd5.

# exa.common.helpers.json_helper.get_json_encoder

get_json_encoder()  
Custom JSON encoder for complex number, ndarray or tuple

Can be used in situation when serialization of JSON can be customised (json_encoders config in pydantic models, custom_encoder in jsonable_encoder of fastapi, etc.)

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[…\], [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]\]
