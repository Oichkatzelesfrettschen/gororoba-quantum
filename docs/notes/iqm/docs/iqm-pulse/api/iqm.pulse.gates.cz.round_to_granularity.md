> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.round_to_granularity.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.round_to_granularity.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d56027f1c7e2143abf02177ccbd3b613e1d1d77eb0191a1aa112bf3efc129020.

# iqm.pulse.gates.cz.round_to_granularity

iqm.pulse.gates.cz.round_to_granularity(*value*, *granularity*, *precision=1e-15*)  
Round a value to the nearest multiple of granularity.

If the value is within a given precision of a multiple, round to that multiple. Otherwise, round down to the nearest lower multiple.

Parameters:  
- **value** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – value to round

- **granularity** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – granularity

- **precision** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rounding precision.

Returns:  
`value` rounded to a granularity.

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
