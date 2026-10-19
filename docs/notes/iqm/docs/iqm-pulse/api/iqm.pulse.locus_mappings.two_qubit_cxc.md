> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_qubit_cxc.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.two_qubit_cxc.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b72afa2686e4267d221f013cd1c7936f4044cef2ef6a58f0c8018695caa8df38.

# iqm.pulse.locus_mappings.two_qubit_cxc

iqm.pulse.locus_mappings.two_qubit_cxc(*sp*)  
Two-qubit loci connected via a coupler - another component - coupler chain.

Based on the chip topology identifies pairs of qubits such that they are connected through a chain of coupler - another component - coupler, and adds those pairs to the mapping. It does not matter if qubits are connected via different computational components. The first common neighbor is added to the mapping for convenience.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]
