> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4f56f3384612dd9056cbbf235e60f3cdcfd284c6c7b95e68414485d172736ece.

# iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts

iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts(*duration*, *full_width*, *rise_time*, *granularity*, *precision=1e-10*)  
Split a flat-top pulse into three consecutive parts (rise, flat, and fall) to save waveform memory.

All the parts conform to the granularity of the device.

Parameters:  
- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – pulse duration in seconds.

- **full_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – full width of the pulse.

- **rise_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rise time of the pulse.

- **granularity** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – minimum allowed pulse duration.

- **precision** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – precision of rounding to granularity,

Returns:  
- flat part duration

- rise (or fall) part duration

- rise time

- flat part’s non-granular leftover, which is transferred to the rise and fall parts

Return type:  
A tuple containing

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Error is raised if duration is not a multiple of granularity.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Error is raised if pulse parameters do not obey duration \>= full_width \>= 2\*rise_time.
