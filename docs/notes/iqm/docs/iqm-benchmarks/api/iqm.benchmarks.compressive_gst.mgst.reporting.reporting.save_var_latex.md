> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.save_var_latex.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.save_var_latex.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3b086b62e1082579201d25120673c0ba54cd16cd4e5c7c9c9576ddb54b58bc08.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.save_var_latex

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.save_var_latex(*key: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *value: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Saves variables in data file to be read in latex document.

Credit to [https://stackoverflow.com/a/66620671](https://stackoverflow.com/a/66620671)

Parameters:  
- **key** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the variable

- **value** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The variable content, could be a string as in the name of the experiment, or the number of circuits run, or any other python variable that needs to be transfered

Return type:  
None
