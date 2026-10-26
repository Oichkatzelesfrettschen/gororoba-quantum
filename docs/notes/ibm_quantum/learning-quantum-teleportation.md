# IBM Quantum Learning: quantum teleportation

[P] identifies a statement on the page. [I] identifies a repository
inference. The page is the lesson "Quantum teleportation" of the IBM Quantum
Learning course "Basics of quantum information", unit "Entanglement in
action". It describes the abstract protocol and carries no backend, timing or
calibration statement.

## Source

- URL: https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/entanglement-in-action/quantum-teleportation
- Retrieved 25 October 2026 (09:04 UTC); 963,935 bytes served; SHA-256
  `055874e13681d74869b33c4f41fb02b6d4e409e6cde87a6b67085f0fc24cdf9a`. The
  response is a rendered web page that IBM updates in place; the hash
  identifies the inspected bytes only. The page footer reads "© IBM Corp.,
  2017-2026"; the registry in [SOURCES.json](../../SOURCES.json) retains the response hash
  and no copy of the bytes.
- Reading scope: the page text from the opening paragraph through "Further
  discussion", including the "Protocol", "Analysis" and "Possible outcomes"
  sections. The circuit diagram image and the "Download notebook" content
  were not opened. The quoted text was read from the extracted HTML, where
  the formulas appear as LaTeX source and rendered text.

## Setting

[P] "Quantum teleportation, or just teleportation for short, is a protocol
where a sender (Alice) transmits a qubit to a receiver (Bob) by making use of
a shared entangled quantum state (one e-bit, to be specific) along with two
bits of classical communication."

[P] Alice holds qubit `A` and Bob holds qubit `B`, and the pair `(A, B)` is in
the state `|phi+>`. Alice also holds the qubit `Q` to transmit, in an unknown
state. The page states that "a different process, such as one involving a
third party or a complex distributed process" can establish the shared e-bit
and that "These details are not part of the teleportation protocol itself."

## Protocol and corrections

[P] Alice applies a controlled-NOT with `Q` as control and `A` as target,
applies a Hadamard to `Q`, measures both `A` and `Q` in the standard basis,
and sends the two outcomes to Bob. The page names the outcome of the
measurement of `A` as `a` and the outcome of the measurement of `Q` as `b`.
Bob then acts on `B`:

- "If a = 1, then Bob performs a bit flip (or X gate) on his qubit B."
- "If b = 1, then Bob performs a phase flip (or Z gate) on his qubit B."

[P] Correction table, as the page states it: "conditioned on ab being 00, 01,
10, or 11, Bob performs one of the operations I, Z, X, or ZX on the qubit B."
The "Possible outcomes" analysis labels each case by the two-bit string it
calls `aq`, with `a` the outcome on `A` and `q` the outcome on `Q`; the
analysis cases agree with the corrections:

| Outcome (`a` on A, `b` on Q) | State of `B` before correction | Correction by Bob | Probability |
|---|---|---|---|
| `00` | `alpha|0> + beta|1>` | none ("Bob does nothing") | 1/4 |
| `01` | `alpha|0> - beta|1>` | Z | 1/4 |
| `10` | `alpha|1> + beta|0>` | X | 1/4 |
| `11` | `alpha|1> - beta|0>` | ZX | 1/4 |

[P] "Notice that Alice's measurements yield absolutely no information about
the state `alpha|0> + beta|1>`. That is, the probability for each of the four
possible measurement outcomes is 1/4, irrespective of alpha and beta."

[P] The page extends the analysis to a qubit `Q` entangled with a reference
system `R`: after the protocol, `B` is entangled with `R` as `Q` was, and the
page concludes that the protocol "effectively implements a perfect, noiseless
quantum channel."

## Repository use

[I] The correction table is expressed on the computational-basis outcomes of
a CNOT-Hadamard circuit. A teleportation that identifies the four Bell states
directly (a Bell-state measurement on two photons, as in
[2411.12387](../papers/2411.12387.md)) labels the same four corrections by
Bell state; convert between the two labelings with the circuit that maps
Bell states to computational states: the CNOT-then-Hadamard of this page. Keep
the Pauli order in `ZX` (X applied first, then Z) when composing
corrections.

[I] The page states ideal-protocol results. It makes no statement on noisy
channels, imperfect Bell-state measurements or classical-communication
latency; those need a separate source such as
[quant-ph-9807091](../papers/quant-ph-9807091.md).
