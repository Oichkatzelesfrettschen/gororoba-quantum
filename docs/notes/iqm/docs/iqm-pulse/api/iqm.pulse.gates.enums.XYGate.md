> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.XYGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.XYGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1dfb0de35676c9ff2992753e7d3ffd8c7b6cc6c6181dae733891065d444d5dbf.

# XYGate

Module: [`iqm.pulse.gates.enums`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.html#module-iqm.pulse.gates.enums "iqm.pulse.gates.enums")

*class* iqm.pulse.gates.enums.XYGate(*value*)  
Bases: [`IntEnum`](https://docs.python.org/3.11/library/enum.html#enum.IntEnum "(in Python v3.11)")

Enumerate all single-qubit Clifford gates whose rotation axis is in the XY plane.

Members of this enum can be mapped to the corresponding unitary propagator using [`XYGATE_UNITARIES`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.XYGATE_UNITARIES.html#iqm.pulse.gates.enums.XYGATE_UNITARIES "iqm.pulse.gates.enums.XYGATE_UNITARIES").

Only used in the tomography experiments.

Attributes

|            |     |
|------------|-----|
| `IDENTITY` |     |
| `X_90`     |     |
| `X_180`    |     |
| `X_M90`    |     |
| `Y_90`     |     |
| `Y_180`    |     |
| `Y_M90`    |     |

Methods

Inheritance

![Inheritance diagram of iqm.pulse.gates.enums.XYGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-9691f4ada3294351cd43afa150758385bf85d9a3.png)
