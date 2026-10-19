> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9cb93b5a6b58028bdb1c3604d6b828e09a28cae0c316db9208a1fa4ddd3c0efd.

# iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep

iqm.error_reduction_tools.readout_characterization.data_processing.CountsByPrep  
Mapping from preparation string to measurement outcome counts.

Outer key: preparation string where each character is `'I'` (prepare `|0⟩`) or `'X'` (prepare `|1⟩`). Inner key: measured bitstring (e.g. `'0110'`). Value: number of shots (or normalized probability) for that outcome.

alias of [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`float`](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]
