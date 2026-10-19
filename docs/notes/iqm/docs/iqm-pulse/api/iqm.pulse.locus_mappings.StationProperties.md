> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 17df04f2915c3775257b24dccb380c417d32514d479f050fffd904e73f58abcb.

# StationProperties

Module: [`iqm.pulse.locus_mappings`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.html#module-iqm.pulse.locus_mappings "iqm.pulse.locus_mappings")

*class* iqm.pulse.locus_mappings.StationProperties(*qpu_topology*, *channels*, *component_channels*, *feedback_sources=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Static properties of a station.

Attributes

|  |  |
|----|----|
| [`qpu_topology`](#iqm.pulse.locus_mappings.StationProperties.qpu_topology "iqm.pulse.locus_mappings.StationProperties.qpu_topology") | QPU topology. |
| [`channels`](#iqm.pulse.locus_mappings.StationProperties.channels "iqm.pulse.locus_mappings.StationProperties.channels") | Mapping of controller names to the configurations of their channels. |
| [`component_channels`](#iqm.pulse.locus_mappings.StationProperties.component_channels "iqm.pulse.locus_mappings.StationProperties.component_channels") | Mapping from QPU component name to a mapping of `('drive', 'flux', 'readout')` to the name of the control channel / controller responsible for that function of the component. |
| [`feedback_sources`](#iqm.pulse.locus_mappings.StationProperties.feedback_sources "iqm.pulse.locus_mappings.StationProperties.feedback_sources") | Mapping from QPU component name to a list of probe line names that can be used as feedback sources for that component. |
| [`can_be_read_out`](#iqm.pulse.locus_mappings.StationProperties.can_be_read_out "iqm.pulse.locus_mappings.StationProperties.can_be_read_out") | QPU components that can be read out via a probeline. |
| [`has_drive`](#iqm.pulse.locus_mappings.StationProperties.has_drive "iqm.pulse.locus_mappings.StationProperties.has_drive") | QPU components that have a physical drive channel. |
| [`has_virtual_drive`](#iqm.pulse.locus_mappings.StationProperties.has_virtual_drive "iqm.pulse.locus_mappings.StationProperties.has_virtual_drive") | QPU components that have a physical or virtual drive channel, and hence can apply virtual phase corrections. |
| [`has_fast_flux`](#iqm.pulse.locus_mappings.StationProperties.has_fast_flux "iqm.pulse.locus_mappings.StationProperties.has_fast_flux") | QPU components that have a fast flux channel. |
| [`station_id`](#iqm.pulse.locus_mappings.StationProperties.station_id "iqm.pulse.locus_mappings.StationProperties.station_id") | Uniquely identifies the station properties, works as a hash key. |

Methods

Parameters:  
- **qpu_topology** ([*ChipTopology*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html#exa.common.qcm_data.chip_topology.ChipTopology "(in iqm-exa-common v29.0.0)"))

- **channels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*)

- **component_channels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

- **feedback_sources** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

qpu_topology*: [ChipTopology](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.qcm_data.chip_topology.ChipTopology.html#exa.common.qcm_data.chip_topology.ChipTopology "(in iqm-exa-common v29.0.0)")*  
QPU topology.

channels*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ChannelProperties](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")\]*  
Mapping of controller names to the configurations of their channels.

component_channels*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Mapping from QPU component name to a mapping of `('drive', 'flux', 'readout')` to the name of the control channel / controller responsible for that function of the component.

feedback_sources*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Mapping from QPU component name to a list of probe line names that can be used as feedback sources for that component.

can_be_read_out*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
QPU components that can be read out via a probeline. NOTE: Only probelines have a readout controller!

has_drive*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
QPU components that have a physical drive channel.

has_virtual_drive*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
QPU components that have a physical or virtual drive channel, and hence can apply virtual phase corrections.

has_fast_flux*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
QPU components that have a fast flux channel.

station_id*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Uniquely identifies the station properties, works as a hash key.

Inheritance

![Inheritance diagram of iqm.pulse.locus_mappings.StationProperties](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-44360993935f42dd17e641dc80a02dacc8c5dbde.png)
