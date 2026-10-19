> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8c4a38427b1f37c9bfcfd558a14304a289582de9a1e750f7faf4a34cfe2c3c62.

# iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts

iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts(*raw_counts_list*, *rot_string_list*)  
Untwirl and sum measurement counts from multiple circuits.

This function takes a list of dictionaries containing measurement counts and a list of readout twirling strings, applies untwirling based on the provided strings and then sums the counts.

Parameters:  
- **raw_counts_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – List of dictionaries containing measurement counts.

- **rot_string_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – List of readout twirling strings (BIG endian).

Returns:  
A dictionary with summed and untwirled measurement counts.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
