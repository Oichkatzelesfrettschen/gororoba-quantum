# Provider credits decomposed: cost models and efficiency per system

Tag convention: [P] documentation statement, [M] measured in this repository, [Q] live quote or read of 2026-11-15, [I] repository
interpretation, `hypothesis:` untested. Every number names its source. A design that spends from this note is a new case
and takes the full review course and the owner's approval before any submission.

## Objective

A credit or a second buys records, not qubits. Each system below is reduced to a cost `C` of a job, a set of binding limits,
and one comparable figure, the qubit-shots a unit of cost buys when the job packs every usable qubit with disjoint copies of
the circuit (qubit-shots = qubits used x shots). Packing is useful only when the copies are independent samples of the
measured question; correlated copies, crosstalk and a connected-cell layout lower the usable count, so the figures bound
what a design may claim and set no target.

## Balances and clocks (2026-11-15)

| System | Unit | Balance | Clock |
|---|---|---|---|
| IBM Quantum, primary account | charged QPU seconds | 383 of 600 s [Q] (217 s consumed) | rolling 28 days: each second returns 28 days after it was spent; no reset date |
| IBM Quantum, backup account | charged QPU seconds | 1 of 600 s [Q] (599 s consumed; the 2026-10-29 records read 0 consumed, and the 599 s is unexplained here) | same; quotas never pool |
| IQM Resonance (pay as you go) | credits | 30.00 [Q] | expire 2026-12-01 |
| Quandela Cloud | credits per platform | read by `qd_usage` (free credits consumed so far: qpu:ascella 58.82, qpu:belenos 96.37, sim:belenos 24.0, sim:ascella 15.0 [Q]) | per token; one running and one queued job |
| Open Quantum | Spark credits | 25 Spark, 0 Full [Q] | the site states 25 Spark credits ($50 of compute) every 90 days [P]; the expiry rule is unread |
| Quantum Inspire | account queue and per-job limits | no metered credit observed [M] (`docs/notes/quantum_inspire/usage.md`) | FAQ: at most 3 jobs in the queue per hardware backend (unit unconfirmed) |

## IBM Heron r2 (ibm_fez, ibm_kingston, ibm_marrakesh)

Cost: charged seconds `S = ceil(E + c)`, `c` in (1.672, 1.725] s [M, fitted over 23 jobs], `E` = sum over circuits of
shots x (`rep_delay` + circuit duration) [M]; the documentation's quick formula is `2 + 0.00035 x executions` seconds at the
default `rep_delay` of 250 us [P]. Limits: 156 qubits, 600 s per 28 days per account.

Efficiency: per charged second the executions tend to `1 / (rep_delay + T)`, with `T` the scheduled circuit length. At
`rep_delay` 250 us and `T` 100 us that is 2,857 executions/s, so a full-width job of 156 disjoint copies yields at most
156 x 2,857 = 445,700 qubit-shots per charged second. A job pays `c` once, so several circuits per job and the largest
shot count the failure exposure allows maximize it: at the quick formula the 383 s left on the primary account buy about
1.09 million executions in one job and the 600 s window about 1.7 million. Lowering `rep_delay` raises the ratio (at 50 us
and `T` 100 us it is 6,667 executions/s) at the cost of qubit relaxation between shots [P]. Both accounts' windows are
independent, so the second account is useful only when its window holds seconds.

## IQM Emerald, Garnet, Sirius

Cost: `billed_seconds x price`, `billed_seconds = ceil(runtime)` per job [P, M], prices in credits per second:

| QC | qubits | couplings | price | qubits per (credit/s) | couplings per (credit/s) | seconds for 30 credits |
|---|---:|---:|---:|---:|---:|---:|
| Emerald | 54 | 90 | 0.75 | 72.0 | 120 | 40 |
| Garnet | 20 | 30 | 0.50 | 40.0 | 60 | 60 |
| Sirius | 16 (+8 resonator) | 24 | 0.30 | 53.3 | 80 | 100 |

Emerald maximizes qubits and couplings per credit by 1.35x over Sirius and 1.8x over Garnet [I, from `docs/evidence/iqm/hardware.json`],
which is the IBM-style answer: the widest chip buys the most qubit-shots per credit, if the question uses the width. A
one-hour timeslot costs 2400 credits on Emerald, 80 times the balance, so only pay-as-you-go runs apply.

Runtime model (Garnet, 12 retained jobs, residual 0.17 s [M]): `execution = 0.162 s + 7.862 us x circuit-shots + 6.338 us x
mid-circuit records`, `runtime` exceeds it by 0.04 to 0.41 s, and billing rounds up. Limits per job: 100 circuits, 20,000
shots per circuit, 2,000,000 executions (Emerald 30,000 instructions, Sirius 75,000). Consequences:

- A full job of 2,000,000 executions runs about 15.9 s on Garnet's fit, 8 credits at Garnet's price; the 30 credits fit
  about 3.7 such jobs, so the cap that binds a spend is the per-job execution limit, not the balance.
- Rounding costs at most one second per job (0.75 credits on Emerald), so a few large jobs beat many small ones: 40 s of
  Emerald as one or two jobs loses at most 1.5 credits to rounding, as twenty jobs up to 15.
- `hypothesis:` Emerald's per-circuit-shot cost is of Garnet's order (8 us), which would give at most 9.2 million
  qubit-shots per credit on a 54-qubit packing against 5.1 million on Garnet's 20 qubits at its measured rate; no Emerald job
  has run, so one measured job fixes the number before any larger design.
- The 30 credits expire 2026-12-01, so unspent balance is lost in 16 days; mocks cost nothing on Emerald and Garnet
  (`emerald:mock`, `garnet:mock`) and test a design without spending.

## Quandela (Ascella, Belenos)

Cost of an iterated qpu:ascella job: `1 credit + 1e-6 x min(shots used, largest iteration cap)` [M]. Clock: about 3.07 s per
template iteration at Ascella, so the 300 s limit holds about 72 iterations [M]. The bill binds on the largest cap and the time on
the sum of caps, so equal per-iteration caps buy every iteration the shots the bill already pays for [I]; the retained design
fits 300 s only while transmittance stays near or above 5.6 percent. A sim:belenos job of 24 iterations reached 305 s
against the 300 s limit [M, 2026-11-15, job fa2da727], so the simulator's per-iteration cost (about 12.7 s) bounds a job to
about 23 iterations of that shape. One job at a time holds the token's queue slot.

## Open Quantum (Spark credits)

Cost [Q, `POST /v1/pricing/estimate`, Public Plan, Standard Queue, integer credits per job]: roughly
`ceil(0.18 + per_shot x shots)` with `per_shot` from the pricing page [P]:

| Backend | qubits | per shot | credits for 1,000 / 20,000 / 50,000 shots | qubit-shots per credit (per-shot term) |
|---|---:|---:|---|---:|
| Rigetti Cepheus-1-108q | 108 | 0.000255 | 1 / not offered / 13 | 423,500 |
| IQM Garnet | 20 | 0.00087 | 2 / 18 / not offered | 23,000 |
| IQM Emerald (offline) | 54 | 0.00096 | 2 / 20 / not offered | 56,250 |
| AQT IBEX Q1 | 12 | 0.0141 | 15 / not offered / not offered | 851 |
| IonQ Forte-1 | 36 | 0.048 | 49 / not offered / not offered | 750 |

The simulators (ibm:qiskit, google:cirq, xanadu:pennylane, qr:sim) quote 0 credits. The 25 Spark credits buy at most about
93,000 shots of Cepheus in two jobs (13 + 12), 27,000 shots of Garnet, or 1,700 shots of IBEX. Rigetti Cepheus is therefore
the maximizer of qubit-shots per Spark credit by a factor of 7.5 over Emerald, and the choice reverses only where a
question needs the all-to-all connectivity or the native fidelity of the trapped-ion devices. Open Quantum Public Compute
publishes every uploaded circuit and result, so a design that spends here must be one whose method may be public.

## Quantum Inspire

No credit meters the account [M]; the binding limits are structural: 5 batch jobs per queue, 5 circuits per batch, 2,048 shots
per QX job and 16,384 to 131,072 per Tuna job, the 300 s job limit, and the FAQ's queue clause. A Tuna-17 shot costs
0.60 to 0.77 ms of execution [M, `docs/notes/quantum_inspire/usage.md`], so a 16,384-shot circuit takes 9.9 to 12.6 s and a
wave of three five-circuit batches holds up to about 190 s of device time. The scarce resource is device availability
(Tuna-17 reads calibrating for hours) and the 60 s pause between waves, not a balance.

## How the models compare

| System | Cost driver | Limit that binds first | Optimal packing rule |
|---|---|---|---|
| IBM | charged seconds, fixed `c` per job | 600 s per 28 days | one job per account window with all circuits, shots at the failure bound, `rep_delay` as low as the relaxation allows |
| IQM | billed seconds, round up per job | 2,000,000 executions per job; expiry 2026-12-01 | few large jobs on the widest chip; measure Emerald once before sizing |
| Quandela | 1 credit + 1e-6 x largest cap | 300 s per job, transmittance | equal per-iteration caps sized to the live transmittance |
| Open Quantum | per task + per shot, integer credits | 25 Spark credits | Cepheus for qubit-shots; one or two jobs near the shot cap |
| Quantum Inspire | no meter | 3 batches in flight, 60 s pause, device status | waves of three batches when the device is not calibrating |

Open items: the Emerald per-shot time (one job), the Spark expiry and refresh rule (the Open Quantum MCP returns 401 while
the SDK key reads the balance, see the infrastructure request of 2026-11-15), the backup IBM account's 599 s, and the
exchange rate between a Spark credit and the quoted dollar equivalent (unpublished).
