> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0479c5560039e3efd33415465926b5c961be32f5bdca60a901267a8aca50624c.

# ImmutableBaseModel

Module: [`exa.common.qcm_data.immutable_base_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.immutable_base_model.html#module-exa.common.qcm_data.immutable_base_model "exa.common.qcm_data.immutable_base_model")

*class* ImmutableBaseModel  
Bases: `BaseModel`

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.model_config "exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |

Methods

&nbsp;

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.immutable_base_model.ImmutableBaseModel](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-a23cdae1a799bb7799867d322f4363a1f30c4a4f.png)
