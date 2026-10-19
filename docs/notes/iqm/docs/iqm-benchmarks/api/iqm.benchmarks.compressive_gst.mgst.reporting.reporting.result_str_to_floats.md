> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.result_str_to_floats.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.result_str_to_floats.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b8204d5e7500e6988abbdede9cf959873e1b2e46947516d55e45c65b18b12f1c.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.result_str_to_floats

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.result_str_to_floats(*result_str: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *err: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Converts formated string results from mgst to float (value, uncertainty) pairs.

Parameters:  
- **result_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – str The value of a result parameter formated as str

- **err** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – str The error interval of the parameters

Returns:  
- The parameter value as float

- A single uncertainty value

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
