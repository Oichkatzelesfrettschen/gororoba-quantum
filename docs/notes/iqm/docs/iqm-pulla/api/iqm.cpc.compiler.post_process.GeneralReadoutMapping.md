> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.GeneralReadoutMapping.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.GeneralReadoutMapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 73b3675ac90863097fad357f0a047c1834f00f4afc3cee771385e907e6978298.

# GeneralReadoutMapping

iqm.cpc.compiler.post_process.GeneralReadoutMapping  
Type for matching measurement keys from a quantum circuit with acquisition labels in Station Control.

Maps a readout key to the acquisition labels with that key in the circuit. The order of the labels for a specific key determines the order of the corresponding results in [`MeasurementResults`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.MeasurementResults.html#iqm.cpc.compiler.post_process.MeasurementResults "iqm.cpc.compiler.post_process.MeasurementResults"). Each acquisition label corresponds to the readout of a single qubit at a single point in the circuit. The same acquisition label can be used multiple times.

Note that in general pulse-level execution we don’t guarantee a specific order for the labels of a key, as it can be affected by custom multiplexing and compiler passes.

alias of [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`tuple`](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), …\]\]
