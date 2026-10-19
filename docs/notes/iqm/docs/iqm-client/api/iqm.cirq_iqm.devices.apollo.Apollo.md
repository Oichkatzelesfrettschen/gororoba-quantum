> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.apollo.Apollo.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.apollo.Apollo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ea21aaf8d33dee9f956b4924369a5a3efb4e3d183097cf669b89d619aa95ced0.

# Apollo

Module: [`iqm.cirq_iqm.devices.apollo`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.apollo.html#module-iqm.cirq_iqm.devices.apollo "iqm.cirq_iqm.devices.apollo")

*class* iqm.cirq_iqm.devices.apollo.Apollo  
Bases: [`IQMDevice`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice")

IQM’s twenty-qubit transmon device.

The qubits are connected thus:

```
      QB20  QB17
      /  \  /  \
   QB19  QB16  QB12
   /  \  /  \  /  \
QB18  QB15  QB11  QB7
   \  /  \  /  \  /
   QB14  QB10  QB6
   /  \  /  \  /
QB13  QB9   QB5
   \  /  \  /  \
   QB8   QB4   QB2
      \  /  \  /
      QB3   QB1
```

where the lines denote which qubit pairs can be subject to two-qubit gates.

Apollo has native PhasedXPowGate, XPowGate, and YPowGate gates. The two-qubit gate CZ is native, as well. The qubits can be measured simultaneously or separately any number of times.

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.cirq_iqm.devices.apollo.Apollo](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-5f5f18cc6dcee0f4a56f06afae30093bbedea62f.png)
