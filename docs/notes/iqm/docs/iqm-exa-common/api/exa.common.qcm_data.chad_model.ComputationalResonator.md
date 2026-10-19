> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.ComputationalResonator.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.ComputationalResonator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b6fdd586f1abf688927a11c5332c008167ac5705e852fb9ae5ffb8b08d8c52d5.

# ComputationalResonator

Module: [`exa.common.qcm_data.chad_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.html#module-exa.common.qcm_data.chad_model "exa.common.qcm_data.chad_model")

*class* ComputationalResonator(*\**, *name*, *connections=()*)  
Bases: [`Component`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Component.html#exa.common.qcm_data.chad_model.Component "exa.common.qcm_data.chad_model.Component")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.qcm_data.chad_model.ComputationalResonator.model_config "exa.common.qcm_data.chad_model.ComputationalResonator.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `name` |  |
| `connections` |  |

Methods

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **connections** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.chad_model.ComputationalResonator](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-37590a54f9b5c8d7ca8998e8d822276b001f4092.png)
