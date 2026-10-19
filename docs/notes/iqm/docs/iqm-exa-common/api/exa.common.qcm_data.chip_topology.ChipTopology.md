> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 427ca79757b1aad71c0dc263121fb082a670796d55bbd5037b5b03529dd145d6.

# ChipTopology

Module: [`exa.common.qcm_data.chip_topology`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.html#module-exa.common.qcm_data.chip_topology "exa.common.qcm_data.chip_topology")

*class* ChipTopology(*qubits*, *computational_resonators*, *couplers*, *probe_lines*, *\**, *variant=''*, *mask_set_name=''*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Topology information for a chip (typically a QPU).

Represents the information found in a CHAD/CHEDDAR.

Parameters:  
- **qubits** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Names of the qubits.

- **computational_resonators** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Names of the computational resonators.

- **couplers** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Mapping from coupler name to names of chip components it connects to.

- **probe_lines** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Mapping from probe line name to names of chip components it connects to.

- **variant** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Identifier of the QPU design variant.

- **mask_set_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Identifier of the QPU mask set name.

Attributes

|  |  |
|----|----|
| [`mask_set_name`](#exa.common.qcm_data.chip_topology.ChipTopology.mask_set_name "exa.common.qcm_data.chip_topology.ChipTopology.mask_set_name") | Identifier of the chip mask set name. |
| [`variant`](#exa.common.qcm_data.chip_topology.ChipTopology.variant "exa.common.qcm_data.chip_topology.ChipTopology.variant") | Identifier of the chip design variant. |
| [`qubits`](#exa.common.qcm_data.chip_topology.ChipTopology.qubits "exa.common.qcm_data.chip_topology.ChipTopology.qubits") | Names of the qubits of the chip. |
| [`qubits_sorted`](#exa.common.qcm_data.chip_topology.ChipTopology.qubits_sorted "exa.common.qcm_data.chip_topology.ChipTopology.qubits_sorted") | Names of the qubits sorted in canonical order. |
| [`computational_resonators`](#exa.common.qcm_data.chip_topology.ChipTopology.computational_resonators "exa.common.qcm_data.chip_topology.ChipTopology.computational_resonators") | Names of the computational resonators of the chip. |
| [`computational_resonators_sorted`](#exa.common.qcm_data.chip_topology.ChipTopology.computational_resonators_sorted "exa.common.qcm_data.chip_topology.ChipTopology.computational_resonators_sorted") | Names of the computational resonators sorted in canonical order. |
| [`couplers`](#exa.common.qcm_data.chip_topology.ChipTopology.couplers "exa.common.qcm_data.chip_topology.ChipTopology.couplers") | Names of the tunable couplers of the chip. |
| [`couplers_sorted`](#exa.common.qcm_data.chip_topology.ChipTopology.couplers_sorted "exa.common.qcm_data.chip_topology.ChipTopology.couplers_sorted") | Names of the tunable couplers sorted in canonical order. |
| [`probe_lines`](#exa.common.qcm_data.chip_topology.ChipTopology.probe_lines "exa.common.qcm_data.chip_topology.ChipTopology.probe_lines") | Names of the probe lines of the chip. |
| [`probe_lines_sorted`](#exa.common.qcm_data.chip_topology.ChipTopology.probe_lines_sorted "exa.common.qcm_data.chip_topology.ChipTopology.probe_lines_sorted") | Names of the probe lines sorted in canonical order. |
| [`all_components`](#exa.common.qcm_data.chip_topology.ChipTopology.all_components "exa.common.qcm_data.chip_topology.ChipTopology.all_components") | All the components on the chip. |
| [`coupler_to_components`](#exa.common.qcm_data.chip_topology.ChipTopology.coupler_to_components "exa.common.qcm_data.chip_topology.ChipTopology.coupler_to_components") | Map from each coupler to all other components it connects to. |
| [`component_to_couplers`](#exa.common.qcm_data.chip_topology.ChipTopology.component_to_couplers "exa.common.qcm_data.chip_topology.ChipTopology.component_to_couplers") | Map from each component to all couplers connected to it. |
| [`probe_line_to_components`](#exa.common.qcm_data.chip_topology.ChipTopology.probe_line_to_components "exa.common.qcm_data.chip_topology.ChipTopology.probe_line_to_components") | Map from each probe line to all components it connects to. |
| [`component_to_probe_line`](#exa.common.qcm_data.chip_topology.ChipTopology.component_to_probe_line "exa.common.qcm_data.chip_topology.ChipTopology.component_to_probe_line") | Map from each component to the probe line connected to it. |

Methods

|  |  |
|----|----|
| [`from_chad`](#exa.common.qcm_data.chip_topology.ChipTopology.from_chad "exa.common.qcm_data.chip_topology.ChipTopology.from_chad") | Construct a ChipTopology instance from a CHAD. |
| [`from_chip_design_record`](#exa.common.qcm_data.chip_topology.ChipTopology.from_chip_design_record "exa.common.qcm_data.chip_topology.ChipTopology.from_chip_design_record") | Construct a ChipTopology instance from a raw Chip design record. |
| [`get_all_common_resonators`](#exa.common.qcm_data.chip_topology.ChipTopology.get_all_common_resonators "exa.common.qcm_data.chip_topology.ChipTopology.get_all_common_resonators") | Computational resonators connected to all the given qubits via a coupler. |
| [`get_common_computational_resonator`](#exa.common.qcm_data.chip_topology.ChipTopology.get_common_computational_resonator "exa.common.qcm_data.chip_topology.ChipTopology.get_common_computational_resonator") | Convenience method for getting the name of a computational resonator which is connected to both specified qubit components via tunable couplers. |
| [`get_connected_coupler_map`](#exa.common.qcm_data.chip_topology.ChipTopology.get_connected_coupler_map "exa.common.qcm_data.chip_topology.ChipTopology.get_connected_coupler_map") | Mapping from couplers that only connect to `components`, to the components they connect to. |
| [`get_connected_probe_lines`](#exa.common.qcm_data.chip_topology.ChipTopology.get_connected_probe_lines "exa.common.qcm_data.chip_topology.ChipTopology.get_connected_probe_lines") | Get probelines that are connected to any of the given components. |
| [`get_connecting_couplers`](#exa.common.qcm_data.chip_topology.ChipTopology.get_connecting_couplers "exa.common.qcm_data.chip_topology.ChipTopology.get_connecting_couplers") | Couplers that only connect to the given chip components, and connect at least two of them. |
| [`get_coupler_for`](#exa.common.qcm_data.chip_topology.ChipTopology.get_coupler_for "exa.common.qcm_data.chip_topology.ChipTopology.get_coupler_for") | Common coupler for the given chip components (e.g. qubit or computational resonator). |
| [`get_neighbor_couplers`](#exa.common.qcm_data.chip_topology.ChipTopology.get_neighbor_couplers "exa.common.qcm_data.chip_topology.ChipTopology.get_neighbor_couplers") | Couplers that connect to at least one of the given chip components. |
| [`get_neighbor_locus_components`](#exa.common.qcm_data.chip_topology.ChipTopology.get_neighbor_locus_components "exa.common.qcm_data.chip_topology.ChipTopology.get_neighbor_locus_components") | Chip components that are connected to the given components by a coupler, but not included in them. |
| [`is_computational_resonator`](#exa.common.qcm_data.chip_topology.ChipTopology.is_computational_resonator "exa.common.qcm_data.chip_topology.ChipTopology.is_computational_resonator") | True iff the given component is a computational resonator. |
| [`is_coupler`](#exa.common.qcm_data.chip_topology.ChipTopology.is_coupler "exa.common.qcm_data.chip_topology.ChipTopology.is_coupler") | True iff the given component is a coupler. |
| [`is_probe_line`](#exa.common.qcm_data.chip_topology.ChipTopology.is_probe_line "exa.common.qcm_data.chip_topology.ChipTopology.is_probe_line") | True iff the given component is a probe line. |
| [`is_qubit`](#exa.common.qcm_data.chip_topology.ChipTopology.is_qubit "exa.common.qcm_data.chip_topology.ChipTopology.is_qubit") | True iff the given component is a qubit. |
| [`limit_values`](#exa.common.qcm_data.chip_topology.ChipTopology.limit_values "exa.common.qcm_data.chip_topology.ChipTopology.limit_values") | Prunes the given mapping (e.g. a coupler_to_components map) to a subset. |

mask_set_name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Identifier of the chip mask set name.

variant*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Identifier of the chip design variant.

qubits*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the qubits of the chip.

qubits_sorted*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
Names of the qubits sorted in canonical order.

computational_resonators*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the computational resonators of the chip.

computational_resonators_sorted*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
Names of the computational resonators sorted in canonical order.

couplers*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the tunable couplers of the chip.

couplers_sorted*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
Names of the tunable couplers sorted in canonical order.

probe_lines*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the probe lines of the chip.

probe_lines_sorted*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
Names of the probe lines sorted in canonical order.

all_components*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
All the components on the chip.

coupler_to_components*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]\]*  
Map from each coupler to all other components it connects to. The values are sorted.

component_to_couplers*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Map from each component to all couplers connected to it.

probe_line_to_components*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]\]*  
Map from each probe line to all components it connects to.

component_to_probe_line*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Map from each component to the probe line connected to it. Max 1 probe line per component is assumed. Components without connection to a probe line don’t appear here.

*classmethod* from_chip_design_record(*chip_design_record*)  
Construct a ChipTopology instance from a raw Chip design record.

Parameters:  
**chip_design_record** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")) – Chip design record as returned by Station Control.

Returns:  
Corresponding chip topology.

Return type:  
[*ChipTopology*](#exa.common.qcm_data.chip_topology.ChipTopology "exa.common.qcm_data.chip_topology.ChipTopology")

*classmethod* from_chad(*chad*)  
Construct a ChipTopology instance from a CHAD. Use [`from_chip_design_record()`](#exa.common.qcm_data.chip_topology.ChipTopology.from_chip_design_record "exa.common.qcm_data.chip_topology.ChipTopology.from_chip_design_record") if possible.

Parameters:  
**chad** ([*CHAD*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chad_model.CHAD.html#exa.common.qcm_data.chad_model.CHAD "exa.common.qcm_data.chad_model.CHAD")) – Parsed CHAD model.

Returns:  
Corresponding chip topology.

Return type:  
[*ChipTopology*](#exa.common.qcm_data.chip_topology.ChipTopology "exa.common.qcm_data.chip_topology.ChipTopology")

get_neighbor_couplers(*components*)  
Couplers that connect to at least one of the given chip components.

Parameters:  
**components** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – some chip components, typically qubits and computational resonators

Returns:  
couplers that connect to at least one of `components`

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_connecting_couplers(*components*)  
Couplers that only connect to the given chip components, and connect at least two of them.

Equivalent to returning the edges in the `components`-induced subgraph of the coupling topology.

Parameters:  
**components** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – some chip components, typically qubits and computational resonators

Returns:  
couplers that connect to only members of `components`, and to at least two of them

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_coupler_for(*component_1*, *component_2*)  
Common coupler for the given chip components (e.g. qubit or computational resonator).

Parameters:  
- **component_1** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – first component

- **component_2** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – second component

Returns:  
the common coupler

Raises:  
[**ValidationError**](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError") – the given components have zero or more than one connecting coupler

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_neighbor_locus_components(*components*)  
Chip components that are connected to the given components by a coupler, but not included in them.

Parameters:  
**components** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – some chip components, typically qubits and computational resonators

Returns:  
components that are connected to `components` by a coupler, but not included in them

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_connected_probe_lines(*components*)  
Get probelines that are connected to any of the given components.

Parameters:  
**components** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_connected_coupler_map(*components*)  
Mapping from couplers that only connect to `components`, to the components they connect to.

Additionally, the returned couplers must connect to at least two of `components`.

Parameters:  
**components** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Components for which to find shared couplers.

Returns:  
Mapping from coupler names to the names of `components` they connect to.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]

*static* limit_values(*dct*, *limit_to*)  
Prunes the given mapping (e.g. a coupler_to_components map) to a subset.

Used to prune e.g. [`coupler_to_components`](#exa.common.qcm_data.chip_topology.ChipTopology.coupler_to_components "exa.common.qcm_data.chip_topology.ChipTopology.coupler_to_components") to a subset of relevant elements.

Parameters:  
- **dct** ([*Mapping*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*) – Mapping to prune.

- **limit_to** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – At least one of these components must appear in the mapping values.

Returns:  
The input mapping, but only with key-value pairs where the value intersects with `limit_to`.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]

is_qubit(*component*)  
True iff the given component is a qubit.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

is_coupler(*component*)  
True iff the given component is a coupler.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

is_probe_line(*component*)  
True iff the given component is a probe line.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

is_computational_resonator(*component*)  
True iff the given component is a computational resonator.

Parameters:  
**component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

get_common_computational_resonator(*first_qubit*, *second_qubit*)  
Convenience method for getting the name of a computational resonator which is connected to both specified qubit components via tunable couplers.

Parameters:  
- **first_qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the first qubit.

- **second_qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) –

  The name of the second qubit.

  The order of qubits does not matter, i.e. the first_qubit and second_qubit arguments are interchangeable.

Returns:  
- The name of the computational resonator that is connected to both inputted qubits via tunable couplers.

Raises:  
- **- ValueError** – If no computational resonator was found that is connected to both qubits via tunable

- **couplers.** –

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

get_all_common_resonators(*qubits*)  
Computational resonators connected to all the given qubits via a coupler.

Parameters:  
**qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Qubit names.

Returns:  
Names of the computational resonators neighboring all of `qubits` (can be an empty set).

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of exa.common.qcm_data.chip_topology.ChipTopology](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-d416ab2d9e565c3e0c26ca2bb499b9bfc60a5e54.png)
