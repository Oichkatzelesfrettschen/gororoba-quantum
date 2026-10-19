> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.aphrodite.Aphrodite.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.aphrodite.Aphrodite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 87b3375b632534d0a5a5829056560dcea98b9ab44ccfafc87a4390936867c55b.

# Aphrodite

Module: [`iqm.cirq_iqm.devices.aphrodite`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.aphrodite.html#module-iqm.cirq_iqm.devices.aphrodite "iqm.cirq_iqm.devices.aphrodite")

*class* iqm.cirq_iqm.devices.aphrodite.Aphrodite  
Bases: [`IQMDevice`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice")

IQM’s 54-qubit transmon device.

The qubits are connected thus:

```
      QB54  QB51  QB46  QB39
      /  \  /  \  /  \  /  \
   QB53  QB50  QB45  QB38  QB31
   /  \  /  \  /  \  /  \  /
QB52  QB49  QB44  QB37  QB30
   \  /  \  /  \  /  \  /  \
   QB48  QB43  QB36  QB29  QB22
   /  \  /  \  /  \  /  \  /  \
QB47  QB42  QB35  QB28  QB21  QB14
   \  /  \  /  \  /  \  /  \  /
   QB41  QB34  QB27  QB20  QB13
   /  \  /  \  /  \  /  \  /  \
QB40  QB33  QB26  QB19  QB12  QB7
   \  /  \  /  \  /  \  /  \  /
   QB32  QB25  QB18  QB11  QB6
      \  /  \  /  \  /  \  /  \
      QB24  QB17  QB10  QB5   QB2
      /  \  /  \  /  \  /  \  /
   QB23  QB16  QB9   QB4   QB1
      \  /  \  /  \  /
      QB15  QB8   QB3
```

where the lines denote which qubit pairs can be subject to two-qubit gates.

Aphrodite has native PhasedXPowGate, XPowGate, and YPowGate gates. The two-qubit gate CZ is native, as well. The qubits can be measured simultaneously or separately any number of times.

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.cirq_iqm.devices.aphrodite.Aphrodite](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-c06abcd74b308211d25865d8d7d3a7520786032d.png)
