> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.adonis.Adonis.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.adonis.Adonis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 57c6d72fb65c87dfb5a05bdc9a3a29eeff0f200c609806e92d08e2946b358b5f.

# Adonis

Module: [`iqm.cirq_iqm.devices.adonis`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.adonis.html#module-iqm.cirq_iqm.devices.adonis "iqm.cirq_iqm.devices.adonis")

*class* iqm.cirq_iqm.devices.adonis.Adonis  
Bases: [`IQMDevice`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice")

IQM’s five-qubit transmon device.

The qubits are connected thus:

```
      QB1
       |
QB2 - QB3 - QB4
       |
      QB5
```

where the lines denote which qubit pairs can be subject to two-qubit gates.

Adonis has native PhasedXPowGate, XPowGate, and YPowGate gates. The two-qubit gate CZ is native, as well. The qubits can be measured simultaneously or separately any number of times.

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.cirq_iqm.devices.adonis.Adonis](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-82dfcdaa83487bd3bda837ac1dd472a31e2cf072.png)
