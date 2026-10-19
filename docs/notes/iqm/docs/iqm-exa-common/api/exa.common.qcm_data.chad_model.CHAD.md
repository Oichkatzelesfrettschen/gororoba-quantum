> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.CHAD.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.CHAD.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 000f5442dee6a09d06118f613436b1d5b1e507ba31f98c6497ab404aecb9d885.

# CHAD

Module: [`exa.common.qcm_data.chad_model`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.html#module-exa.common.qcm_data.chad_model "exa.common.qcm_data.chad_model")

*class* CHAD(*\**, *mask_set_name*, *variant*, *components*)  
Bases: [`ImmutableBaseModel`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.immutable_base_model.ImmutableBaseModel.html#exa.common.qcm_data.immutable_base_model.ImmutableBaseModel "exa.common.qcm_data.immutable_base_model.ImmutableBaseModel")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`computational_resonator_names`](#exa.common.qcm_data.chad_model.CHAD.computational_resonator_names "exa.common.qcm_data.chad_model.CHAD.computational_resonator_names") | Names of all the computational resonators declared in CHAD data. |
| [`coupler_names`](#exa.common.qcm_data.chad_model.CHAD.coupler_names "exa.common.qcm_data.chad_model.CHAD.coupler_names") | Names of all the couplers declared in CHAD data. |
| [`model_config`](#exa.common.qcm_data.chad_model.CHAD.model_config "exa.common.qcm_data.chad_model.CHAD.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`probe_line_names`](#exa.common.qcm_data.chad_model.CHAD.probe_line_names "exa.common.qcm_data.chad_model.CHAD.probe_line_names") | Names of all the probe lines declared in CHAD data. |
| [`qubit_names`](#exa.common.qcm_data.chad_model.CHAD.qubit_names "exa.common.qcm_data.chad_model.CHAD.qubit_names") | Names of all the qubits declared in CHAD data. |
| `mask_set_name` |  |
| `variant` |  |
| `components` |  |

Methods

|  |  |
|----|----|
| [`filter_qubit_components`](#exa.common.qcm_data.chad_model.CHAD.filter_qubit_components "exa.common.qcm_data.chad_model.CHAD.filter_qubit_components") | Filter qubit components from the input components. |
| [`get_common_coupler_for`](#exa.common.qcm_data.chad_model.CHAD.get_common_coupler_for "exa.common.qcm_data.chad_model.CHAD.get_common_coupler_for") | Convenience method for getting the name of a coupler connecting a pair of components. |
| [`get_component`](#exa.common.qcm_data.chad_model.CHAD.get_component "exa.common.qcm_data.chad_model.CHAD.get_component") | Get component by component name. |
| [`get_coupler_mapping_for`](#exa.common.qcm_data.chad_model.CHAD.get_coupler_mapping_for "exa.common.qcm_data.chad_model.CHAD.get_coupler_mapping_for") | Get the coupler-component mapping for the couplers that connects to at least two components |
| [`get_probe_line_mapping_for`](#exa.common.qcm_data.chad_model.CHAD.get_probe_line_mapping_for "exa.common.qcm_data.chad_model.CHAD.get_probe_line_mapping_for") | Get the probe line-component mapping. |
| [`get_probe_line_names_for`](#exa.common.qcm_data.chad_model.CHAD.get_probe_line_names_for "exa.common.qcm_data.chad_model.CHAD.get_probe_line_names_for") | Get probe lines for given qubits in CHAD data. |
| [`group_components_per_default_operations`](#exa.common.qcm_data.chad_model.CHAD.group_components_per_default_operations "exa.common.qcm_data.chad_model.CHAD.group_components_per_default_operations") | Groups given qubits/couplers based on their defined default operations. |

Parameters:  
- **mask_set_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **variant** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **components** ([*Components*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Components.html#exa.common.qcm_data.chad_model.Components "exa.common.qcm_data.chad_model.Components"))

get_component(*component_name*)  
Get component by component name.

Parameters:  
**component_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*Component*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.Component.html#exa.common.qcm_data.chad_model.Component "exa.common.qcm_data.chad_model.Component")

*property* qubit_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of all the qubits declared in CHAD data.

*property* coupler_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of all the couplers declared in CHAD data.

*property* probe_line_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of all the probe lines declared in CHAD data.

*property* computational_resonator_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of all the computational resonators declared in CHAD data.

filter_qubit_components(*component_names*)  
Filter qubit components from the input components.

Parameters:  
**component_names** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_probe_line_names_for(*component_names*)  
Get probe lines for given qubits in CHAD data.

Parameters:  
**component_names** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

group_components_per_default_operations(*component_names*)  
Groups given qubits/couplers based on their defined default operations.

The default operations that can be deducted from a CHAD are readout, drive, and flux.

Parameters:  
**component_names** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The component names to which to do the grouping. Other components present in the CHAD will not be included in the returned data.

Returns:  
- Tuple of qubits and couplers mapped to their connected default operations.  
  The data is in the form of a dict with the keys being readout, drive, and flux, and the values the list of component names having that particular operation.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\], [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]\]

get_coupler_mapping_for(*component_names*)  
Get the coupler-component mapping for the couplers that connects to at least two components  
in the given qubits.

Parameters:  
**component_names** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The qubit names. May contain any number of qubits.

Returns:  
Coupler names mapped to the components they connect.

Raises:  
**- ValueError** – If the provided qubit name list contains duplicates.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]

get_probe_line_mapping_for(*component_names*)  
Get the probe line-component mapping.

Parameters:  
**component_names** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The qubit names. May contain any number of qubits.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]

get_common_coupler_for(*first_component*, *second_component*)  
Convenience method for getting the name of a coupler connecting a pair of components.

Parameters:  
- **first_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the first component.

- **second_component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the second component. The order of qubits does not matter, i.e. the first_qubit and second_qubit arguments are interchangeable.

Returns:  
- The name of the coupler that connects the inputted components.

Raises:  
**- ValidationError** – If there were no couplers or more than one coupler connecting the component pair (the latter should not be possible in a realistic chip).

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

model_config*: ClassVar\[ConfigDict\]* *= {'frozen': True, 'ignored_types': (\<class 'functools.cached_property'\>,)}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of exa.common.qcm_data.chad_model.CHAD](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-b2f4b882b928f523af2f927294517f8db93674a7.png)
