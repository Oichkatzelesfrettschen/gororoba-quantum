> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.type_aliases.SweepResults.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.type_aliases.SweepResults.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8e0429cbe689ee27e9f70cd110cbd3c4dc979a6bb6850139cf777c727425b49e.

# SweepResults

SweepResults  
Raw results of a run job.

Maps readout labels to flattened arrays of measurement data. Interpretation requires metadata stored in [`RunDefinition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.run.RunDefinition.html#iqm.station_control.interface.models.run.RunDefinition "iqm.station_control.interface.models.run.RunDefinition").

alias of [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[`ndarray`\]\]
