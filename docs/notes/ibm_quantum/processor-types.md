> Full piece: [https://quantum.cloud.ibm.com/docs/en/guides/processor-types](https://quantum.cloud.ibm.com/docs/en/guides/processor-types)

# Processor types

Processor types are named for the general technology qualities that go into builds, consisting of the family and revision. Family (for example, Heron) refers to the size and scale of circuits possible on the chip. This is primarily determined by the number of qubits and the connectivity graph. Revisions (for example, r3) are design variants within a given family, often leading to performance improvements or tradeoffs.

> **Supported instruction set**
>
> To find the supported instruction set for a backend, use [this code](https://quantum.cloud.ibm.com/docs/guides/qpu-information#native-gates-ops). You can see all supported instructions in [this table](https://quantum.cloud.ibm.com/docs/guides/qpu-information#native-gates).

As new processor families are added, older families are retired.  See the [Retired processor families](https://quantum.cloud.ibm.com/docs/guides/retired-qpus#families) section to learn more.

## Nighthawk

![Nighthawk processor icon](https://quantum.cloud.ibm.com/docs/images/guides/processor-types/nighthawk.svg)

With a grid topology, Nighthawk leverages our technology stack from Heron (couplers, signal delivery, and coherence) with increased connectivity for enhanced application workloads.

- [View available Nighthawk processors](https://quantum.cloud.ibm.com/computers?processorType=Nighthawk)

> **Revisions**
>
> - `r2` (September 2026) The second version of Nighthawk, with 120 programmable qubits and 458 physical qubits, including a high speed reset on each qubit which significantly increases the maximum number of circuits per second.
> - `r1` (December 2025) The first version of Nighthawk, with 120 qubits.

## Heron

![Heron processor icon](https://quantum.cloud.ibm.com/docs/images/guides/processor-types/heron.svg)

At 156 qubits, Heron is an Eagle-sized upgrade to Egret that pulls in substantial innovations in signal delivery that were previously deployed in Osprey. The signals required to enable the fast, high-fidelity two-qubit and single-qubit control are delivered with high-density flex cabling.

- [View available Heron processors](https://quantum.cloud.ibm.com/computers?processorType=Heron)

> **Revisions**
>
> `r3` (July 2025) Heron r3 is the result of targeted manufacturing improvements that directly impact coherence, gate fidelity, and readout performance.
>
> `r2` (July 2024) This is a revision of the original Heron processor. The chip has been redesigned to include 156 qubits in a heavy-hexagonal lattice. While continuing to make use of the innovations of the original Heron processors, it also introduces a new TLS mitigation feature that controls the TLS environment of the chip, thereby improving coherence and stability across the whole chip.
>
> `r1` (December 2023) The first version of Heron with 133 qubits.
