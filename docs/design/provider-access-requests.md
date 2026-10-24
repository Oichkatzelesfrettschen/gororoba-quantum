# Provider access requests: drafts for review

Quantinuum, D-Wave, Classiq, OQC, Rigetti, SuperQ and Kipu Quantum admit an
account to hardware or a full platform only after a sign-up form or a written
use case. This document holds one draft per provider, written from the
repository's registered results, for an external reviewer (a person or an
agent) to check before the owner submits it. A draft is never sent by an
agent: the owner submits it, and any job the access later enables still waits
for its own written case and approval (root AGENTS.md, "Hardware services").

Bracketed fields (`[OWNER NAME]`, `[AFFILIATION]`, `[CONTACT EMAIL]`) are the
owner's to fill; no draft names a person, an email address or an account
identifier.

## Review checklist

A reviewer passes a draft only when every item holds:

1. Every result it cites exists as a claim in
   [docs/state/research_state.json](../state/research_state.json) under the
   quoted id, with the evidence class the draft gives it. A proposed
   experiment is never described as a result.
2. Every hardware figure (qubits, connectivity, gate set, feed-forward,
   price) carries a provider source and its retrieval date, and the fit of
   the proposed experiment to that hardware follows from the figure.
3. The requested resources (shots, jobs, hours, credits) follow from a stated
   shot budget, and the draft names what result each experiment would
   change.
4. The data terms are stated: the repository is public
   (<https://github.com/Oichkatzelesfrettschen/gororoba-quantum>), so
   circuits and results are published there, and the draft asks for nothing
   confidential.
5. The language is plain and claims nothing about applications, speedups or
   physics beyond the algebra and device questions below.

## Program summary (shared by every draft)

The project studies the Cayley-Dickson algebras (octonions, sedenions and the
32-dimensional algebra) as quantum circuits. A left-multiplication operator
`L_a` is encoded as a linear map on `log2(D)` qubits, and algebraic
properties become observables: a zero-divisor pair `a b = 0` appears as a
dark output branch of zero probability, its bright control as one of
probability near one, and the non-associativity of the algebra as a phase in
an associator circuit. Every hardware probe passes a mutation test (the ideal
observable changes when the property is removed), runs its arms in a
+, -, -, + order and decides against a preregistered null
([algebra circuit rules](../notes/algebra_circuit_rules.md#hardware-probes)).
The exact algebra is specified in `gororoba_quantum/cd_core.py`; selected
statements are kernel-checked in Rocq (`proofs/`).

Hardware results so far (claim ids in the registry):

- IBM Heron r2 `ibm_fez`: all 84 box-kite bright-minus-dark contrasts reject
  their nulls (`hw-fez-ripple`), and the 8 rank-sector contrasts transfer to
  `ibm_kingston` with the same signs (`hw-kingston-rank-transfer`).
- IBM `ibm_kingston`: the encoded N = 21 order-finding contrast with
  real-time feed-forward is consistent with zero at 100,000 shots per arm
  (`hw-n21-feedback-null-kingston`), so routing depth, not shot count,
  limits that circuit.
- QuTech Tuna-17: the Design B zero-divisor witness of
  `(e1 + e10)(e4 - e15) = 0` contracts toward the incoherent floor
  (`qi-tuna17-zero-divisor-contraction`, `qi-tuna17-zero-divisor-visibility-floor`),
  and the kernel cancellation probe ran at 45 CZ
  (`qi-tuna17-kernel-cancellation`).
- IQM Garnet: the signed sedenion kernel probe at 199 CZ and its null re-test
  (`iqm-garnet-signed-kernel-probe`, `iqm-garnet-signed-null-retest`), and the
  kernel cancellation probe at 37 CZ (`iqm-garnet-kernel-cancellation`).
- Quandela Belenos and Ascella (photonic): all 168 zero products and 168
  bright controls of the 84 box-kite edges in one job
  (`qd-qpu-belenos-84-84-zero-divisor-program`) and a signed-coherence
  conformance run (`ascella-signed-coherence-conformance`).

The common limit across these devices is two-qubit depth after routing on
sparse connectivity: the zero-divisor witnesses and the feed-forward circuit
lose contrast with every SWAP. Devices with all-to-all connectivity, native
mid-circuit measurement with feed-forward, or a different noise mechanism
answer questions the current devices cannot.

## Common template

Each provider draft fills these fields:

| Field | Content |
|---|---|
| Applicant | `[OWNER NAME]`, `[AFFILIATION]` (independent researcher if none), `[CONTACT EMAIL]` |
| Project | the program summary above, two to four sentences |
| Research question | what this provider's hardware answers that the devices above cannot |
| Experiments | each with circuit size, two-qubit count, shots, falsifier and the claim it would change |
| Resources | shots, jobs or hours, with the arithmetic |
| Software | Qiskit 2.x circuits exported as OpenQASM 2/3 or the provider's SDK; the circuits are public |
| Data and publication | results and circuits are published in the public repository with the provider credited as its terms require |
| Timeline | a pilot first, then the full series only if the pilot's checks pass |

## Quantinuum (H-series or Helios)

- **Access route.** Direct access is institutional; Azure Quantum grants new
  workspaces a provider credit (survey row in
  [n21_feedforward_backends.md](../notes/topics/n21_feedforward_backends.md)).
  The draft asks for research access or an academic credit allocation.
- **Research question.** Whether the encoded N = 21 order-finding contrast,
  null on heavy-hex hardware (`hw-n21-feedback-null-kingston`), appears when
  all-to-all connectivity removes the SWAP routing and native mid-circuit
  measurement with conditional gates supplies the feed-forward.
- **Experiments.**
  1. The N = 21 feedback and no-feedback arms as one compiled circuit pair;
     the falsifier is a contrast difference whose interval excludes zero.
  2. The Design B zero-divisor witness without routing: dark probability
     against bright, compared with the routed Tuna-17 and Heron r2 values.
  3. The signed kernel probe at the depth IQM Garnet used, to separate a
     coherent sign error from connectivity.
- **Resources.** `[SHOTS PER ARM]` per arm from the survey's contract; the
  HQC cost follows the published formula once the circuits are compiled,
  and the draft states that number, not an estimate.
- **Open check for the reviewer.** The survey marks the Qiskit-to-Quantinuum
  conditional path as unverified; the draft must name the submission path
  (QIR Adaptive, Guppy or pytket) the experiments use.

## D-Wave (annealing)

- **Fit.** An annealer runs Ising and QUBO problems, not gate circuits, so
  none of the circuit experiments above transfers. The candidate is
  combinatorial: the zero-divisor and box-kite structures of the sedenions
  are finite sign-graph problems, and an exact classical certificate already
  covers them (the census claims `cd-associator-census` and the
  `exact finite certificate` claims).
- **Research question.** Whether an annealer recovers the box-kite
  partition as the ground states of an Ising model built from the sedenion
  sign table, measured against the known exact answer.
- **Experiments.** A QUBO designed so that its ground states encode the
  sedenion box-kite partition, its construction written and checked
  classically against `cd_core` before any submission, then run with
  increasing chain strength; the falsifier is a ground-state distribution
  that misses the known partition.
- **Reviewer note.** This is the weakest fit in the set: the answer is
  already exact, so the run tests the annealer, not the algebra. The owner
  decides whether to submit it.

## Classiq (synthesis platform)

- **Fit.** Classiq synthesizes circuits from functional models; the free
  academic tier runs on simulators and partner backends.
- **Research question.** Whether automated synthesis of `L_a` and of the
  linear-combination-of-unitaries witnesses reaches fewer two-qubit gates
  than the repository's hand-built and Qiskit-transpiled circuits, whose
  routed CZ counts the registry records.
- **Experiments.** Synthesize the octonion and sedenion left-multiplication
  operators and the Design B witness, export the circuits, and verify each
  against `cd_core` on every basis pair before comparing gate counts; the
  falsifier is a synthesized circuit that fails the basis check or uses more
  two-qubit gates.
- **Resources.** Synthesis and simulator time only.

## OQC (Toshiko)

- **Fit.** A superconducting device with a different coupler design from
  IBM, IQM and QuTech.
- **Research question.** Whether the zero-divisor contraction and the
  context-dependent readout misassignment seen on Tuna-17
  (`qi-tuna17-q13-readout-context-q11`) recur on a fourth superconducting
  architecture.
- **Experiments.** The Design B witness with bright control and null arm,
  and a readout-context pair; falsifier as in the Tuna-17 claims.
- **Resources.** `[SHOTS]` from the Tuna-17 shot budget, recomputed for
  Toshiko's readout fidelity.

## Rigetti (Ankaa-3 or Cepheus-1-108Q)

- **Fit.** Square-lattice connectivity, closer to IQM's than to IBM's
  heavy-hex; Cepheus is already listed in the Open Quantum catalogue.
- **Research question.** Whether the kernel cancellation probe's sign
  (`iqm-garnet-kernel-cancellation`, `qi-tuna17-kernel-cancellation`)
  transfers to a third lattice at matched two-qubit depth.
- **Experiments.** The kernel cancellation probe and its bright control at
  the IQM depth; falsifier as in the IQM claim.
- **Resources.** `[SHOTS]` per arm from the IQM case.

## SuperQ

The onboarding form asks optional questions and grants the full platform to
researchers. Draft answers:

- **Role.** `[ROLE]`, independent research program in algebra on quantum
  hardware (program summary above).
- **Use.** Circuit-level experiments on Cayley-Dickson algebra structure
  across devices, all circuits and results public.
- **Experience.** Prior runs on IBM Heron r2, QuTech Tuna-17, IQM Garnet and
  Quandela photonic devices, each preregistered (claim ids above).
- **Reviewer note.** The form's questions are not captured in the
  repository; the reviewer checks each answer against the live form.

## Kipu Quantum (qhub)

The account's approval is pending. The hosted MCP server `qhub-mcp`
(`https://api.hub.kipu-quantum.com/mcp`) is registered at Claude Code user
scope and signs in through `/mcp` once access is granted. A use-case draft
follows the common template once the platform's services are readable.
