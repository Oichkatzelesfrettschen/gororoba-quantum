> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.fixed_options.FixedOptions.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.fixed_options.FixedOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ec20449c60c0ffab585082dffa88eaf371a843e392078b74bfa39bfcfc1fdfad.

# FixedOptions

Module: [`exa.common.control.sweep.option.fixed_options`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.fixed_options.html#module-exa.common.control.sweep.option.fixed_options "exa.common.control.sweep.option.fixed_options")

*class* FixedOptions(*fixed*)  
Bases: [`SweepOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "exa.common.control.sweep.option.sweep_options.SweepOptions")

Range fixed options.

Attributes

|  |  |
|----|----|
| [`data`](#exa.common.control.sweep.option.fixed_options.FixedOptions.data "exa.common.control.sweep.option.fixed_options.FixedOptions.data") | List of values for `parameter` |
| [`fixed`](#exa.common.control.sweep.option.fixed_options.FixedOptions.fixed "exa.common.control.sweep.option.fixed_options.FixedOptions.fixed") | One-dimensional array of values. |

Methods

Parameters:  
**fixed** (*Annotated\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *PlainValidator(func=~exa.common.control.sweep.sweep_values.validate_sweep_values,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.control.sweep.sweep_values.serialize_sweep_values,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]*)

fixed*: WithJsonSchema(json_schema={}, mode=None)\]*  
One-dimensional array of values.

*property* data*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
List of values for `parameter`

Inheritance

![Inheritance diagram of exa.common.control.sweep.option.fixed_options.FixedOptions](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-66f2712aa46e922ec8aecb1c0475c3496e67cf52.png)
