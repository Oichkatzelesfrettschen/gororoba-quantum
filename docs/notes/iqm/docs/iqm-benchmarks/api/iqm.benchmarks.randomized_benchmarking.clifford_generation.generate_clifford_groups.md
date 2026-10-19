> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_generation.generate_clifford_groups.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_generation.generate_clifford_groups.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1b86551d1beb228166b0c231aefba1770f5fe4105f0c76bc1a995f45a891bdf0.

# iqm.benchmarks.randomized_benchmarking.clifford_generation.generate_clifford_groups

iqm.benchmarks.randomized_benchmarking.clifford_generation.generate_clifford_groups() → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), QuantumCircuit\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), QuantumCircuit\]\]  
Generate the 1-qubit and 2-qubit Clifford groups.

Returns:  
- Dictionary of 24 single-qubit Clifford gates

- Dictionary of 11,520 two-qubit Clifford gates

Return type:  
A tuple containing
