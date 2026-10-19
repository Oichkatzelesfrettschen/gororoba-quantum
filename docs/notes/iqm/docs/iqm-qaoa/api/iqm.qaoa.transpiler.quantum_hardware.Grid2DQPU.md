> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5f7e62836932ed6c7e2229419a60021e7a2656217399c9af6742b049688b4d0b.

# Grid2DQPU

Module: [`iqm.qaoa.transpiler.quantum_hardware`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.html#module-iqm.qaoa.transpiler.quantum_hardware "iqm.qaoa.transpiler.quantum_hardware")

*class* iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU(*num_rows*, *num_columns*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L446-L491)  
Bases: [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")

Class for 2D rectangular QPU.

Contains variables for number of rows and columns, which determine the hardware graph and layout. Also contains a simple [`embedded_chain()`](#iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.embedded_chain "iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.embedded_chain") method to embed a chain in the hardware graph.

Parameters:  
- **num_rows** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of rows in the grid.

- **num_columns** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of columns in the grid.

Attributes

Methods

|  |  |
|----|----|
| [`embedded_chain`](#iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.embedded_chain "iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU.embedded_chain") | Embeds a chain in the grid QPU (by going around like a snake). |

embedded_chain()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/quantum_hardware.py#L468-L491)  
Embeds a chain in the grid QPU (by going around like a snake).

```
-----------------╷
╷----------------╵
╵----------------╷
╷----------------╵
╵----------------╷
╷----------------╵
╵-----------------
```

Yields:  
Integer index of the next qubit in the chain.

Return type:  
[*Iterator*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterator "(in Python v3.11)")\[TypeAliasForwardRef(‘~iqm.qaoa.transpiler.quantum_hardware.HardQubit’)\]

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.quantum_hardware.Grid2DQPU](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-082896552299882aa363e86981e8095ad4c900d4.png)
