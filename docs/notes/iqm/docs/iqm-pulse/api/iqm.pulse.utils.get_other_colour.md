> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.get_other_colour.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.get_other_colour.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 58efde3670e3000866f5668a35aaa9cdfe3aff12e1a04fa46b48a9e8f5575873.

# iqm.pulse.utils.get_other_colour

iqm.pulse.utils.get_other_colour(*station_properties*, *qubit*)  
Get the set of qubits that are in the other colour than the given qubit.

Parameters:  
- **station_properties** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties")) – StationProperties object.

- **qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Qubit to get the other colour from.

Returns:  
The qubits in the other colour.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
