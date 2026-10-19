> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.STANDARD_DD_STRATEGY.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.STANDARD_DD_STRATEGY.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b33d613a4401da96cff7a9f7431f1a02c15cb7147a852104bf41b636ae97c63e.

# STANDARD_DD_STRATEGY

iqm.cpc.compiler.dd.STANDARD_DD_STRATEGY *= DDStrategy(merge_contiguous_waits=True, target_qubits=None, skip_leading_wait=True, skip_trailing_wait=True, gate_sequences=\[(9, 'XYXYYXYX', 'asap'), (5, 'YXYX', 'asap'), (2, 'XX', 'center')\])*  
The default DD strategy uses the following gate sequences:

- Simple symmetric CPMG sequence for short idling times.

- Asymmetric (left-aligned) universal XY4 sequence for medium idling times.

- Asymmetric (left-aligned) universal EDD sequence for longer idling times.
