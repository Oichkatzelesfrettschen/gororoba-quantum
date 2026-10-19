> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.TwoQubitGate.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.TwoQubitGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6f05d6d44423dc3c85c94fb0f71886ec5f0852b0668747ee1ba8e467bc09ae99.

# TwoQubitGate

Module: [`iqm.pulse.gates.enums`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.html#module-iqm.pulse.gates.enums "iqm.pulse.gates.enums")

*class* iqm.pulse.gates.enums.TwoQubitGate(*value*)  
Bases: [`Enum`](https://docs.python.org/3.11/library/enum.html#enum.Enum "(in Python v3.11)")

Enumerates a subset of two-qubit gates.

Members of this enum can be mapped to the corresponding unitary propagator using the dictionary returned by [`TWO_QUBIT_UNITARIES`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.TWO_QUBIT_UNITARIES.html#iqm.pulse.gates.enums.TWO_QUBIT_UNITARIES "iqm.pulse.gates.enums.TWO_QUBIT_UNITARIES").

Attributes

|  |  |
|----|----|
| [`CZ`](#iqm.pulse.gates.enums.TwoQubitGate.CZ "iqm.pulse.gates.enums.TwoQubitGate.CZ") | Controlled-Z gate. |
| [`ISWAP`](#iqm.pulse.gates.enums.TwoQubitGate.ISWAP "iqm.pulse.gates.enums.TwoQubitGate.ISWAP") | iSWAP gate. |
| [`SQRT_ISWAP`](#iqm.pulse.gates.enums.TwoQubitGate.SQRT_ISWAP "iqm.pulse.gates.enums.TwoQubitGate.SQRT_ISWAP") | Square root of the iSWAP gate. |

Methods

CZ *= 0*  
Controlled-Z gate.

ISWAP *= 1*  
iSWAP gate.

SQRT_ISWAP *= 2*  
Square root of the iSWAP gate.

Inheritance

![Inheritance diagram of iqm.pulse.gates.enums.TwoQubitGate](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-70f1c0d96087085ab99ae348d3c645576fc3fed3.png)
