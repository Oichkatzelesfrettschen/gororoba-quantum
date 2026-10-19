> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.median_with_uncertainty.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.median_with_uncertainty.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 22136385f52cd33d96d245f4b9872f158809343eed34f917c169c690f9ba9bc2.

# iqm.benchmarks.utils.median_with_uncertainty

iqm.benchmarks.utils.median_with_uncertainty(*observations: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Computes the median of a Sequence of float observations and returns value and propagated uncertainty.

Reference: [https://mathworld.wolfram.com/StatisticalMedian.html](https://mathworld.wolfram.com/StatisticalMedian.html)

Parameters:  
**observations** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – a Sequence of floating-point numbers.

Returns:  
A dictionary with keys “value” and “uncertainty” for the median of the input Sequence.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
