> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4701391fa54c9f098715f84348b213c62fdc7d56ee18c23fbab8781d884adab7.

# iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping

iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping(*sp*)  
Get custom locus mapping for this GateImplementation.

Returns:  
Locus mapping of qubit-coupler pairs for coupler flux implementation. Returns only pairs for which the qubit has fast flux.

Parameters:  
**sp** ([*StationProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.locus_mappings.StationProperties.html#iqm.pulse.locus_mappings.StationProperties "iqm.pulse.locus_mappings.StationProperties"))

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\], [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]
