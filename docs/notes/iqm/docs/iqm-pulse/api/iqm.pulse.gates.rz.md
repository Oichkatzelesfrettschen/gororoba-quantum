> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dbf16dd7202f2a033bb5714f94d47f5f4930b5720ff31e409fccef1f3c0178c9.

# rz

Full path: iqm.pulse.gates.rz

Single-qubit RZ gate.

The z rotation gate is defined as

\\R_z(\phi) = e^{-i Z \phi / 2}\\

where the rotation angle \\\phi\\ is in radians.

Functions

|  |  |
|----|----|
| [`get_unitary_rz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.get_unitary_rz.html#iqm.pulse.gates.rz.get_unitary_rz "iqm.pulse.gates.rz.get_unitary_rz")(angle) | Unitary for an RZ gate. |

Classes

|  |  |
|----|----|
| [`RZ_ACStarkShift`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift.html#iqm.pulse.gates.rz.RZ_ACStarkShift "iqm.pulse.gates.rz.RZ_ACStarkShift") | Implementation of the RZ gate using an AC Stark pulse. |
| [`RZ_ACStarkShift_CosineRiseFall`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall.html#iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall "iqm.pulse.gates.rz.RZ_ACStarkShift_CosineRiseFall") | AC stark pulse implemented as a modulated cosine rise fall pulse. |
| [`RZ_ACStarkShift_smoothConstant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_ACStarkShift_smoothConstant.html#iqm.pulse.gates.rz.RZ_ACStarkShift_smoothConstant "iqm.pulse.gates.rz.RZ_ACStarkShift_smoothConstant") | Constant AC stark pulse with cosine rise and fall padding. |
| [`RZ_PRX_Composite`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_PRX_Composite.html#iqm.pulse.gates.rz.RZ_PRX_Composite "iqm.pulse.gates.rz.RZ_PRX_Composite") | RZ gate implemented as a sequence of PRX gates. |
| [`RZ_Virtual`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.RZ_Virtual.html#iqm.pulse.gates.rz.RZ_Virtual "iqm.pulse.gates.rz.RZ_Virtual") | Implementation of the RZ gate using the virtual z rotation technique. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.rz](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-aaa2f51bcab939ed46f8e0ba6919f96eaee08d3c.png)
