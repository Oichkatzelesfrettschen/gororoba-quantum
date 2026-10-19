> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.STANDARD_DD_STRATEGY.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.STANDARD_DD_STRATEGY.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 05c12061e3a7e5bd546001838f08dec829c6a19b049502bed6e7c38aab2ee493.

# iqm.iqm_client.models.STANDARD_DD_STRATEGY

iqm.iqm_client.models.STANDARD_DD_STRATEGY *= DDStrategy(merge_contiguous_waits=True, target_qubits=None, skip_leading_wait=True, skip_trailing_wait=True, gate_sequences=\[(9, 'XYXYYXYX', 'asap'), (5, 'YXYX', 'asap'), (2, 'XX', 'center')\])*  
The default DD strategy uses the following gate sequences:

- Simple symmetric CPMG sequence for short idling times.

- Asymmetric (left-aligned) universal XY4 sequence for medium idling times.

- Asymmetric (left-aligned) universal EDD sequence for longer idling times.
