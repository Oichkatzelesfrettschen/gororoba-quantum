> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.group_rzz_gates.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.group_rzz_gates.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 29d1a75d192911c8b62faac6335b048e195a50c1c676875537def8efbb5d7ac3.

# iqm.benchmarks.optimization.qscore.group_rzz_gates

iqm.benchmarks.optimization.qscore.group_rzz_gates(*circuit: QuantumCircuit*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[RZZGate, [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]  
Extract and group commuting RZZ gates so that gates sharing a qubit are placed next to each other.

Parameters:  
**circuit** (*QuantumCircuit*) – QuantumCircuit containing RZZ gates.

Returns:  
list of tuples (instr, \[q0_idx, q1_idx\]) in reordered grouping.

Return type:  
grouped_rzz
