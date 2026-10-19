> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a20492ca354d49f7dff20cb0d785bbad20a676fe628dc4b86a172892ca30f7b4.

# sx

Full path: iqm.pulse.gates.sx

Single-qubit sqrt(X) gate.

The gate is doing pi/2 X gate, with additional Z rotation to correct phase.

\\R = e^{-i\pi \\{\sigma}\_X/4}\\

It rotates the qubit state in XZ plane (or around Y axis) for 90 degree.

Classes

|  |  |
|----|----|
| [`SXGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.SXGate.html#iqm.pulse.gates.sx.SXGate "iqm.pulse.gates.sx.SXGate") | SX gate implementation based on PRX gate, by limiting the angle to pi / 2. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.sx](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-38e2431f2502b22d387cfe9200b99ffa45fd7336.png)
