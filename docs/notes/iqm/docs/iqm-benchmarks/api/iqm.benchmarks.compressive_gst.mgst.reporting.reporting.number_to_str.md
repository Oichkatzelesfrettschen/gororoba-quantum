> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.number_to_str.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.number_to_str.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 93f95d6e49dcaf5f8cafddfbfe257f89422d70d0984dc29cead795b91c5b7e63.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.number_to_str

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.number_to_str(*number: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *uncertainty: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *precision: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 3*) → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Formats a floating point number to a string with the given precision.

Parameters:  
- **number** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The floating point number to format.

- **uncertainty** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – The upper and lower values of the confidence interval

- **precision** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of decimal places to include in the formatted string.

Returns:  
The formatted floating point number as a string.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
