> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Component.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Component.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7ad2215423078154d3566f18991e75c9da5858c3eab8b3fd1ccc50f119edfe9a.

# Component

Module: [`exa.common.qcm_data.chad_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.html#module-exa.common.qcm_data.chad_model "exa.common.qcm_data.chad_model")

*class* Component(*\**, *name*, *connections=()*)  
Bases: [`ImmutableBaseModel`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.html#exa.common.qcm_data.immutable_base_model.ImmutableBaseModel "exa.common.qcm_data.immutable_base_model.ImmutableBaseModel")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.qcm_data.chad_model.Component.model_config "exa.common.qcm_data.chad_model.Component.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `name` |  |
| `connections` |  |

Methods

|        |     |
|--------|-----|
| `sort` |     |

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **connections** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.chad_model.Component](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-f1728450f12883c5f8d86eadcbb4fc2082a85447.png)
