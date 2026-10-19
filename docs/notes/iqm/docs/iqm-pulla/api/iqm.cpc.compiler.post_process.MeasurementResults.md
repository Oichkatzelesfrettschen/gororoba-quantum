> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.MeasurementResults.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.MeasurementResults.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 14ea46ac5f9efe90ff3649f70945971bb981d26c88d08157c0963a2f3511542a.

# MeasurementResults

iqm.cpc.compiler.post_process.MeasurementResults  
Measurement results for a single circuit.

Maps measurement keys to corresponding results. `results[key][shot][label_index]` is the measurement result corresponding to the acquisition label `GeneralReadoutMapping[key][label_index]`, for the shot `shot`.

alias of [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[`int`](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]
