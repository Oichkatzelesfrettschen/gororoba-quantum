> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0fc9a8132d81bf80f7ea3c296467dc928f5b2bdadff577ee318c2c06aaadb8a6.

# iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters

iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters(*effort: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *num_2qb_gates: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *cpu_count: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 128*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Derive transpiler parameters from a single effort level.

Parameters:  
- **effort** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Classical compute investment level (≥ 1). - effort=1 : fast — one parallel wave, C=1-2 - effort=3 : moderate — 1-2 layout waves, C=2-6 - effort=5 : thorough — several layout waves, C=4-10 Wall-clock time scales roughly linearly with effort.

- **cpu_count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) – Number of available CPU cores (auto-detected by default).

- **num_2qb_gates** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *optional*) – Number of 2-qubit gates in the circuit. Controls the budget split between layout attempts (ILA) and routing diversity (C). Shallow circuits (\< ~100 gates) invest more in ILA; deep circuits invest more in C. When *None*, a balanced 50/50 split is used.

Returns:  
Keys: `init_layout_attempts`, `C`, `layout_iterations`.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")

Examples

```
>>> params = compute_parameters(1, cpu_count=16)
>>> params['init_layout_attempts'] >= 16
True
>>> params['C'] >= 1
True
>>> params['layout_iterations']
3
```

```
>>> # Shallow circuit → heavy ILA, light C
>>> p = compute_parameters(5, cpu_count=16, num_2qb_gates=30)
>>> p['init_layout_attempts'] >= 48
True
>>> p['C'] <= 5
True
```

```
>>> # Deep circuit → light ILA, heavy C
>>> p = compute_parameters(5, cpu_count=16, num_2qb_gates=1000)
>>> p['init_layout_attempts'] <= 32
True
>>> p['C'] >= 8
True
```
