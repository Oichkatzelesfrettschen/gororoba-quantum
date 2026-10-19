> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b1cf108576a0c76a7d8e93ae1cd8ca1fb44d8f878242f72b2d74aad3c329ddc3.

# locus_mappings

Full path: iqm.pulse.locus_mappings

Locus mapping creation and caching.

A locus mapping defines all the possible loci a particular gate implementation can be applied on, on a specific station. It is determined from the QPU topology and the available control channels of the station.

For operations with zero `arity`, the locus mapping must consist of single-qubit loci, and a multiqubit locus is valid if all its components are valid single-qubit loci.

The functions in this module build locus mappings for various [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") subclasses, and are shared by them. Each function caches the mappings it creates.

Module Attributes

|  |  |
|----|----|
| [`Locus`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.Locus.html#iqm.pulse.locus_mappings.Locus "iqm.pulse.locus_mappings.Locus") | Sequence of QPU component names a quantum operation is acting on. |
| [`LocusMapping`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.LocusMapping.html#iqm.pulse.locus_mappings.LocusMapping "iqm.pulse.locus_mappings.LocusMapping") | Mapping from the possible loci of a particular GateImplementation subclass to the QPU components used by the implementation on that locus, for a specific station. |

Functions

|  |  |
|----|----|
| [`one_component`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_component.html#iqm.pulse.locus_mappings.one_component "iqm.pulse.locus_mappings.one_component")(sp) | One-component loci. |
| [`one_component_channel`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_component_channel.html#iqm.pulse.locus_mappings.one_component_channel "iqm.pulse.locus_mappings.one_component_channel")(sp) | One-component loci that have at least one channel. |
| [`one_component_drive`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_component_drive.html#iqm.pulse.locus_mappings.one_component_drive "iqm.pulse.locus_mappings.one_component_drive")(sp) | One-component loci with drive. |
| [`one_component_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_component_flux.html#iqm.pulse.locus_mappings.one_component_flux "iqm.pulse.locus_mappings.one_component_flux")(sp) | One-component loci (qubits and couplers) with fast flux. |
| [`one_component_readout`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_component_readout.html#iqm.pulse.locus_mappings.one_component_readout "iqm.pulse.locus_mappings.one_component_readout")(sp) | One-component loci with readout. |
| [`one_component_virtual_drive`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_component_virtual_drive.html#iqm.pulse.locus_mappings.one_component_virtual_drive "iqm.pulse.locus_mappings.one_component_virtual_drive")(sp) | One-component loci with virtual drive capability. |
| [`one_qubit`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_qubit.html#iqm.pulse.locus_mappings.one_qubit "iqm.pulse.locus_mappings.one_qubit")(sp) | One-qubit loci. |
| [`one_qubit_drive_readout`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_qubit_drive_readout.html#iqm.pulse.locus_mappings.one_qubit_drive_readout "iqm.pulse.locus_mappings.one_qubit_drive_readout")(sp) | One-qubit loci with physical drive and readout. |
| [`one_qubit_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_qubit_flux.html#iqm.pulse.locus_mappings.one_qubit_flux "iqm.pulse.locus_mappings.one_qubit_flux")(sp) | One-qubit loci with fast flux. |
| [`one_qubit_readout`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_qubit_readout.html#iqm.pulse.locus_mappings.one_qubit_readout "iqm.pulse.locus_mappings.one_qubit_readout")(sp) | One-qubit loci with readout. |
| [`one_qubit_readout_and_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.one_qubit_readout_and_flux.html#iqm.pulse.locus_mappings.one_qubit_readout_and_flux "iqm.pulse.locus_mappings.one_qubit_readout_and_flux")(sp) | One-qubit loci with readout and fast flux. |
| [`probe_lines`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.probe_lines.html#iqm.pulse.locus_mappings.probe_lines "iqm.pulse.locus_mappings.probe_lines")(sp) | One-component loci on probe lines. |
| [`qubit_coupler`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.qubit_coupler.html#iqm.pulse.locus_mappings.qubit_coupler "iqm.pulse.locus_mappings.qubit_coupler")(sp) | Connected (qubit, coupler) pairs. |
| [`single_qubit_or_resonator_without_probe`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.single_qubit_or_resonator_without_probe.html#iqm.pulse.locus_mappings.single_qubit_or_resonator_without_probe "iqm.pulse.locus_mappings.single_qubit_or_resonator_without_probe")(sp) | Defined for components that have no probe line and that are qubits or resonators. |
| [`two_component_coupler_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_component_coupler_flux.html#iqm.pulse.locus_mappings.two_component_coupler_flux "iqm.pulse.locus_mappings.two_component_coupler_flux")(sp) | Two-component loci (qubits + resonators), connected through a coupler with fast flux, symmetric. |
| [`two_component_one_flux_coupler_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_component_one_flux_coupler_flux.html#iqm.pulse.locus_mappings.two_component_one_flux_coupler_flux "iqm.pulse.locus_mappings.two_component_one_flux_coupler_flux")(sp) | Two-component loci connected through a coupler where the coupler and at least one component has fast flux. |
| [`two_qubit_crc`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_qubit_crc.html#iqm.pulse.locus_mappings.two_qubit_crc "iqm.pulse.locus_mappings.two_qubit_crc")(sp) | Two-qubit loci connected through coupler-resonator-coupler. |
| [`two_qubit_cxc`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_qubit_cxc.html#iqm.pulse.locus_mappings.two_qubit_cxc "iqm.pulse.locus_mappings.two_qubit_cxc")(sp) | Two-qubit loci connected via a coupler - another component - coupler chain. |
| [`two_qubit_drive_coupler_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_qubit_drive_coupler_flux.html#iqm.pulse.locus_mappings.two_qubit_drive_coupler_flux "iqm.pulse.locus_mappings.two_qubit_drive_coupler_flux")(sp) | Two-qubit loci, connected through a coupler with fast flux, both qubits have drive. |
| [`two_qubit_flux_coupler_flux`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_qubit_flux_coupler_flux.html#iqm.pulse.locus_mappings.two_qubit_flux_coupler_flux "iqm.pulse.locus_mappings.two_qubit_flux_coupler_flux")(sp) | Two-qubit loci connected through a coupler, where the coupler and both qubits have fast flux. |

Classes

|  |  |
|----|----|
| [`StationProperties`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties") | Static properties of a station. |

Inheritance

![Inheritance diagram of iqm.pulse.locus_mappings](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-6edcec74107e616ecb6b1d379d747fe671e6a92e.png)
