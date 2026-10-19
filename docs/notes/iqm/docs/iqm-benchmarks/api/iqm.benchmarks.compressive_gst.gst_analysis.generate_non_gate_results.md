> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.generate_non_gate_results.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.generate_non_gate_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2ec1cfe52c4fe40353a0a674b97ac1bba2fd9b7362edcc7b540c70e4c2c04a34.

# iqm.benchmarks.compressive_gst.gst_analysis.generate_non_gate_results

iqm.benchmarks.compressive_gst.gst_analysis.generate_non_gate_results(*df_o: DataFrame*, *bootstrap_results: [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] = None*) → DataFrame  
Creates error bars (if bootstrapping was used) and formats results for non-gate errors.

The resulting tables are also turned into figures, so that they can be saved automatically.

Parameters:  
- **df_o** (*DataFrame*) – A dataframe containing the non-gate quality metrics (SPAM errors and fit quality)

- **bootstrap_results** (*None* *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – If provided, contains the results of the bootstrap analysis.

Returns:  
df_o_final, the final formatted results

Return type:  
*DataFrame*
