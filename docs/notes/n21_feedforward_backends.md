# N=21 feed-forward: backends besides IBM Heron r2

Status: DRAFT. Each claim names its source; a claim no reachable document
supports is marked unverified, and the [Unverified](#unverified) section lists
them. The ibm_kingston endpoint of 2026-10-18 comes from
[N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md](../../results/live/N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md).

The `n21-feedback-encoded` family (N=21, a=4, two semiclassical phase-estimation
rounds, 7 logical qubits, 2 classical bits) compares a feed-forward arm with an
omitted-correction arm. This note states what the circuit demands of a machine,
tests each candidate service against that demand, and prices the shots.
Every web citation carries its access date (2026-10-17). A claim that no
reachable document supports is marked unverified.

## Requirement from first principles

The labeled law is `qpe_diagnostics.n21_labeled_law`. With feed-forward the
probabilities of (b0 + 2 b1) are (0.375, 0.25, 0.125, 0.25); without it they are
(0.375, 0.125, 0.125, 0.375). The score P(01) - P(11) is 0 against -0.25, an
ideal contrast difference of 0.25. The circuit needs:

1. One mid-circuit measurement of the control qubit, result b0.
2. A reset of that qubit before round 2 (measurement plus a gate conditioned on b0).
3. In round 2 a gate on the control conditioned on b0 and applied before the
   final Hadamard: the factor `(-i)**b0`, a phase of -pi/2 (an S-dagger). The
   angle is fixed at a multiple of pi/2; no arbitrary-angle condition is needed.
4. Both b0 and b1 in the returned counts, because the law is indexed by b0 + 2 b1.
5. Conditioning on exactly one earlier classical bit, applied to the qubit that
   produced it, and no nesting.
6. A routed two-qubit-gate budget small enough that the attenuated contrast stays
   measurable. Three noise-model values exist for the 713-CZ ibm_kingston
   routing of the encoded circuit: 0.0417 under the 2026-10-16 calibration
   ([linear_conjugation](../evidence/linear_conjugation/README.md); 739 is that
   table's median over the admitted cosets), 0.0310 at plan time in the run's
   `record.json`, and 0.0344 replayed at the execution calibration. They retain
   0.17 to 0.12 of the ideal 0.25; the measured endpoint below reproduces none
   of them.

## The ibm_kingston endpoint

The encoded circuit ran on ibm_kingston on 2026-10-18 with 713 routed CZ in the
feedback arm and 714 in the omitted-correction arm, 100,000 shots per arm at a
50 us repetition delay (`results/live/2026-10-18T090603.530638Z`, job
`dba8r7k24mrc738527d0`). The contrast difference is +0.0027 with 95 percent
interval [-0.0129, +0.0184]; the model replayed at the execution calibration
predicts +0.0344, above the interval. Both arms read near-uniform four-outcome
distributions, so a channel outside the calibration noise model removes the
feedback-dependent structure. The findings note names the candidates: mid-circuit
measurement error above the reported assignment error, feed-forward latency
beyond the classical allowance, and dephasing during the conditional branch.

Consequences for this survey:

- The residual factor f below is fitted to the noise-model values, not to a
  measurement. The measured Kingston contrast is consistent with zero, so no
  measured f exists to carry to another machine, and every contrast in the IQM
  screen is an upper estimate.
- A run on a second feed-forward stack now answers a different question than
  "more shots for the same effect": a nonzero contrast on IQM would place the
  missing structure in the Heron r2 feed-forward path, and a null would point
  to the circuit or its routed depth. Both outcomes need the same shot count
  the screen derives.

Deferred measurement (a coherent controlled-S onto an eighth qubit) removes
requirements 1 to 3 and 5 but changes the intervention: the arm no longer tests
classical feed-forward, so it is a separate experiment with its own controls.

## What IQM cc_prx and measure_ff express

| Question | Finding | Source |
| --- | --- | --- |
| Instruction semantics | `measure_ff` measures a qubit and stores the bit under an integer feedback key; `cc_prx` applies a PRX rotation only when the stored bit for that key is 1, and an identity of equal duration otherwise | [AWS Braket dynamic circuits](https://docs.aws.amazon.com/braket/latest/developerguide/braket-experimental-capabilities.html); [Braket blog 2025-06-26](https://aws.amazon.com/blogs/quantum-computing/experiment-with-dynamic-circuits-on-iqm-garnet-with-amazon-braket) |
| Angle | The Braket `CCPRx` class takes two free angles (`angle_1`, `angle_2`) plus the feedback key; Open Quantum's catalogue lists `cc_prx(theta, phi)` with arity 2. Every published example uses theta = pi. Hardware limits on other angles: unverified | [CCPRx source](https://amazon-braket-sdk-python.readthedocs.io/en/latest/_modules/braket/experimental_capabilities/iqm/classical_control.html); `docs/evidence/open_quantum/catalogue.json` |
| Qiskit form | "Only the x, y, rx, ry and r gates can be classically controlled"; "conditioned on one classical bit"; "if_test blocks cannot be nested"; availability depends on the instrument | [Qiskit on IQM guide](https://docs.iqm.tech/iqm-client/user_guide_qiskit) |
| Reset | A measurement followed by a classically controlled X; available only where classical control is | same guide; Braket blog (active reset is a pi rotation conditioned on the bit) |
| Conditioning scope | A qubit's feed-forward is controlled by one qubit (itself or another) per circuit; control applies only within a qubit group (Garnet 2 groups, Emerald 4); feedback keys are unique; `cc_prx` follows its `measure_ff` | Braket developer guide above |
| Execution mode | On Braket the program is a verbatim program; the mid-circuit outcomes "are not returned as part of a task result" | Braket developer guide above |

Consequences for this circuit:

- Requirement 3 is expressible. The required factor is `circuit.p(-pi/2)` in
  `order_finding.factor_order_finding`, the matrix diag(1, -i). With
  PRX(theta, phi) = exp(-i theta/2 (cos phi X + sin phi Y)) (the convention is
  assumed from IQM's native-operation description as relayed by the Braket
  documentation; not checked against IQM's own page), a 2x2 numpy check gives,
  in time order, `prx(pi/2, 0)`, then `cc_prx(pi/2, pi/2)` on feedback bit b0,
  then `prx(-pi/2, 0)`. For b0 = 0 the conditional gate is the identity and the
  sandwich cancels; for b0 = 1 the product equals diag(1, -i) up to a global
  phase. `cc_prx(pi/2, -pi/2)` gives diag(1, i), the wrong sign. The sequence
  costs three one-qubit operations and no CZ, and needs `cc_prx` to accept
  theta = pi/2; public examples show only theta = pi.
- Requirement 2 is the documented active reset, a `cc_prx` with theta = pi on the
  same key.
- Requirement 5 holds because the control qubit conditions itself, which
  satisfies the one-controller and same-group rules by construction. The
  conditioned qubit being reset and re-controlled by the same bit is not
  covered by a stated rule: unverified.
- Requirement 4 conflicts with Braket's statement that mid-circuit outcomes are
  not returned. A copy of the control's Z value onto a spare qubit by one CNOT
  (one CZ and two one-qubit gates) before `measure_ff` puts b0 in the ordinary
  final readout, at the cost of an eighth qubit and one CZ plus its routing,
  which the CZ counts below leave out. Whether Open Quantum returns
  `measure_ff` bits: unverified.
- Open Quantum's QASM path: the catalogue lists `dynamic_circuits` among the
  features of iqm:garnet and iqm:emerald, `cc_prx` and `measure_ff` among
  `supported_ops`, and `qasm` as the only format. The captured documentation
  states nothing on `if`/`else` lowering or on how the feedback key is written
  in QASM. Testing it needs `prepare_job`, which uploads a circuit and is not
  run here. Status: unverified until the owner approves a case.

## Open Quantum arithmetic (cost rule `ceil(per_task + shots * per_shot)`)

Public Standard rates, `docs/evidence/open_quantum/pricing.json`: Garnet
0.18 + 0.00087 per shot; Emerald 0.18 + 0.00096 per shot. Account balance: 25
Spark credits (catalogue). Spark pays the Public plan only. The MCP cap of 1
credit admits floor((1 - 0.18) / 0.00087) = 942 shots on Garnet
(ceil(0.18 + 942 * 0.00087) = 1) and 854 on Emerald. The MCP cap is a setting of
the MCP server; the SDK key itself carries no such cap, but every job still
needs written approval.

Availability. The retained catalogue (`retrieved_utc` 2026-10-17T05:24Z)
reports iqm:garnet and iqm:emerald as status Online with `accepting_jobs` false
and queue depth 0; `spark_available` is true for both, and the account holds
25 Spark and 0 Full credits. IonQ Forte and Rigetti Cepheus accepted jobs at
the catalogue read; AQT IBEX refused as the IQM backends did. A Spark job
cannot be submitted to the IQM backends until `accepting_jobs` flips; the
state is a polling target, and its cause (maintenance, calibration, a booked
window) is unknown.

Largest Spark allotments on Garnet:

| Plan | Shots | Credits |
| --- | --- | --- |
| 25 jobs at the MCP cap | 25 * 942 = 23,550 | 25 |
| one job at the 20,000-shot ceiling | 20,000 | ceil(17.58) = 18 |
| two equal jobs (one per arm), 12 credits each | 2 * 13,586 = 27,172 | 24 |
| one 25-credit job (shots capped at 20,000) | 20,000 | 18 |

The two-arm design needs equal shots per arm, so the working budget is about
13,500 shots per arm. Emerald gives (12 - 0.18) / 0.00096 = 12,312 per arm.

Shots needed. Each arm's score has variance near (p01 + p11) / N = 0.5 / N, so
the contrast difference has standard error 1 / sqrt(N). A k-sigma detection of
contrast c needs N = (k / c)^2 shots per arm. For the three noise-model values
of the 713-CZ Kingston routing, c = 0.0417, 0.0344 and 0.0310, this gives
5,176, 7,606 and 9,366 shots per arm at 3 sigma and 14,377, 21,127 and 26,015
at 5 sigma. The Kingston run spent 100,000 per arm.

First-order contrast model. Contrast = 0.25 * f * exp(-n e), with n the routed CZ
count and e the median CZ error. Kingston's median CZ error in
`docs/evidence/heron_platform/targets.json` (retrieved 2026-10-14) is 0.002125
over the pairs whose reported error is below 1. Matching the model values at
n = 713 fixes the residual factor (readout, one-qubit and idle loss) at
f = 0.759 for c = 0.0417, 0.626 for 0.0344 and 0.564 for 0.0310; the three
values come from calibrations of 2026-10-16 and 2026-10-18 while e comes from
the 2026-10-14 snapshot. Garnet's median CZ fidelity is 99.51 percent
(e = 0.0049) and Emerald's 99.5 percent (e = 0.005) per the Open Quantum
provider pages; f is assumed equal. The model ignores IQM's readout and reset
durations, crosstalk and the fat tail of the CZ error distribution, so treat
it as a screen, not a prediction. Rows use f = 0.759, the upper end.

| Backend | Routed CZ n | Contrast | Shots per arm, 3 sigma | Shots per arm, 5 sigma |
| --- | --- | --- | --- | --- |
| ibm_kingston (model) | 713 | 0.0417 | 5,176 | 14,377 |
| ibm_kingston (measured) | 713 | +0.0027, consistent with 0 | n/a | n/a |
| IQM Garnet | 713 | 0.0058 | 270,858 | 752,383 |
| IQM Garnet | 600 | 0.0100 | 89,497 | 248,601 |
| IQM Garnet | 450 | 0.0209 | 20,578 | 57,160 |
| IQM Garnet | 300 | 0.0436 | 4,732 | 13,143 |
| IQM Garnet | 200 | 0.0712 | 1,776 | 4,933 |

Break-even on Spark. A 3-sigma result at 13,586 shots per arm needs c >= 0.0257,
that is n <= 408 routed CZ on Garnet with f = 0.759 and n <= 347 with f = 0.564.
Emerald, whose per-shot fee leaves 12,312 shots per arm (c >= 0.0270), gives
390 and 330. A 5-sigma result needs c >= 0.0429 on Garnet, n <= 303 or 243.
The Spark threshold is therefore about 350 to 410 routed CZ.
The 713-CZ heavy-hex routing is out of reach on Garnet at any budget this
account holds: 3 sigma needs about 271,000 shots per arm, 20 times the per-arm
Spark budget and 14 jobs of the 20,000-shot ceiling per arm. The deciding input is
the CZ count of a square-lattice routing of the circuit, which no branch of the
repository holds yet; with it in hand the table above converts to a
go/no-go in one lookup. Paid Public credits would cost ceil(0.18 + N * 0.00087)
credits per job at one USD-equivalent dollar per credit, for example 2 * 18 = 36
credits for two 20,000-shot jobs.

## Provider survey

Legend: FF = real-time classically conditioned gates, not only mid-circuit
measurement. Quota rows are what the page states; sources are cited per row.

| Service | FF support | Qubits, connectivity | Free quota | Data terms | Eligibility | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Open Quantum, IQM Garnet / Emerald (Online, `accepting_jobs` false at the 2026-10-17 read) | `dynamic_circuits` feature, `cc_prx`, `measure_ff` ([catalogue](../evidence/open_quantum/catalogue.json)); QASM lowering unverified | 20 / 54, square lattice, 99.51 / 99.5 percent median CZ ([Garnet page](open_quantum/site/providers_iqm_garnet.md)) | 25 Spark credits at signup and 25 every 90 days, claimed by hand ([free-credits page](open_quantum/site/free-credits.md)) | Public tier: circuits and results public, retained by Quantum Rings ([README](open_quantum/README.md)) | Account exists | Verified catalogue; FF path unverified |
| IBM Open Plan, ibm_kingston | `if_else`, tested by the family | 156, heavy-hex | 10 min per 28 days; a one-time 180 min over 12 months for users who log 20 min in any 12 months, opt-in ([IBM blog 2026-03-16](https://www.ibm.com/quantum/blog/open-plan-updates)) | Private | Non-trial Open Plan account | Same machine, larger budget; the 10 min per 28 days is the 600 s rolling window `AGENTS.md` records. Measured null at 713 CZ on 2026-10-18 |
| Amazon Braket, IQM Garnet / Emerald | `measure_ff`, `cc_prx`, experimental, verbatim only; MCM bits not returned ([developer guide](https://docs.aws.amazon.com/braket/latest/developerguide/braket-experimental-capabilities.html)) | 20 / 54, 2 / 4 groups | None for QPUs; $0.30 per task + $0.00145 (Garnet) / $0.00160 (Emerald) per shot ([pricing](https://aws.amazon.com/braket/pricing/)) | AWS terms, not reviewed | Any AWS account | Verified; paid |
| IQM Resonance Starter | Not documented for Resonance; the IQM Qiskit guide says availability depends on the instrument | Crystal 54, Crystal 20, Star 24 beta ([IQM](https://www.iqm.tech/products/iqm-resonance)) | Up to 30 credits per month, availability-dependent; pay-as-you-go from $0.30 per QPU second; credit-to-second conversion unstated (inferred 1 s, unverified) | Unstated on the page | Unstated | FF on Resonance unverified |
| EuroHPC quantum pilot call (Euro-Q-Exa, Lucy, Piast-Q, VLQ) | Not mentioned; VLQ is IQM-built per the [Open Quantum IQM page](open_quantum/site/providers_iqm.md), FF unverified | Not stated | Free; rolling cut-offs on 1 Nov and 1 Dec 2026 ([EuroHPC](https://www.eurohpc-ju.europa.eu/eurohpc-ju-opens-access-its-quantum-computers-2026-06-25_en)) | Not mentioned | Research, public sector or industry in Europe | Unverified FF; eligibility depends on the owner's location |
| Azure Quantum, Quantinuum H2-1 / H2-2 | Conditional logic on measurement results via Qiskit `c_if` or Q# `if`, QIR Adaptive RI ([provider page](https://learn.microsoft.com/azure/quantum/provider-quantinuum)). The page's `c_if` example does not exist in Qiskit 2.5.2 (`QuantumCircuit.x(0)` returns an instruction with no `c_if`); the repo's circuit uses `if_test`, so a port needs the provider's control-flow path, unverified | 56, all-to-all | None on hardware; syntax checkers free; emulator free with a hardware subscription; HQC = 5 + C(N1q + 10 N2q + 5 Nm)/5000 ([pricing](https://learn.microsoft.com/azure/quantum/pricing)); Standard plan $125,000 per month for 10k HQC | Azure terms, not reviewed | Pay-as-you-go via sales contact | Expressive, not free; the $500-per-provider workspace credit is not on the pages fetched: unverified |
| Quantinuum Helios (direct) | Real-time control engine, Guppy language ([coverage](https://www.constellationr.com/insights/news/quantinuum-launches-helios-quantum-computer-touts-fidelity-enterprise-customers)); conditional examples on the Helios MCMR page ([docs](http://docs.quantinuum.com/systems/trainings/helios/getting_started/mcmr.html)) | 98, all-to-all | None found for individuals; institutional agreements only (UWA, DeiC) | Not reviewed | Institutions | Access route unverified |
| Open Quantum, IonQ Forte / AQT IBEX / Rigetti Cepheus | Catalogue lists `mid_circuit_measure` for IonQ and no `dynamic_circuits` for any of the three | 36 / 12 / 108 | Same Spark balance | Public | Account exists | No FF through Open Quantum |
| Quantum Inspire Tuna-5 / 9 / 17 | No binary-controlled gates | 5 / 9 / 17 | Free | Licensed to QuTech | Account exists | Excluded |
| Origin Quantum Cloud | `qif` / `qelse` on simulators ([docs](https://qcloud.originqc.com.cn/document/pyqpanda3-docs/en/tutorial/dynamic-circuits)); hardware support not stated | Wukong-180 | A "Research Incentive Program" of free time, size and terms unstated ([report](https://quantumcomputingreport.com/origin-quantum-unveils-origin-wukong-180-fourth-generation-quantum-computer/)) | Unreached | Unreached | Unverified |
| Quafu / BAQIS ScQ | Dynamic circuits parsed in simulation only per the pyquafu changelog ([pyquafu changelog mirror](https://data.safetycli.com/changelogs/pyquafu)) | 10 in the 2022 paper | Unreached | Unreached | Unreached | Unverified |
| qBraid | Reseller; Garnet 30 credits per task + 0.145 per shot, credit = $0.01 ([qBraid pricing](https://docs.qbraid.com/v2/home/pricing)); inherits Braket's FF limits | 20 | $50 via the Open Quantum partnership, same Spark pool | Open Quantum terms | Account | Duplicate of rows above |
| Rigetti QCS direct (Ankaa-3, Cepheus-1-108Q) | Searched: pyQuil and QCS pages surfaced no mid-circuit feedback documentation; the QCS FAQ has an active-reset section ([FAQ](https://docs.rigetti.com/qcs/faq)) whose text was truncated | 84 / 108, square-type lattice | None found; Azure PAYG $0.02 per 10 ms of execution ([pricing](https://learn.microsoft.com/azure/quantum/pricing)) | Not reviewed | Not reviewed | No feed-forward documentation found |
| IonQ direct | "Dynamic circuit execution is not supported on any IonQ target" ([OpenQASM 3 docs](https://docs.ionq.com/api-reference/v0.4/openqasm3)); branching fails preflight | 36 | Research Credits Program, up to $10,000, 2021 terms: academic researchers, current terms unchecked ([IonQ cloud page](https://ionq.com/quantum-cloud)) | Not reviewed | Academic | Excluded: no FF |
| Oxford Quantum Circuits (Toshiko) | Searched: no feed-forward statement found ([OQC Cloud](https://oqc.tech/access/oqc-cloud/)) | 32 | None found | Not reviewed | Not reviewed | No feed-forward documentation found |
| Alice & Bob (Boson 4) | Searched: no feed-forward statement found; cat-qubit test chip on Google Cloud Marketplace ([report](https://quantumcomputingreport.com/alice-bob-is-making-access-to-their-boson-4-cat-qubit-test-chip-available-to-researchers-through-the-google-cloud-marketplace/)) | Test chip | None found | Not reviewed | Researchers | No feed-forward documentation found |
| SpinQ cloud | Searched: no mid-circuit or feedback statement found ([SpinQ cloud](https://www.spinquanta.com/products-services/quantum-computing-cloud-platform)) | 2 / 3 / 5 / 8 | None found | Not reviewed | Not reviewed | Below 7 qubits |
| Pasqal Fresnel | Analog neutral-atom device ([Azure pricing](https://learn.microsoft.com/azure/quantum/pricing)) | 100 | n/a | n/a | n/a | Not gate-based for this circuit |
| Quandela Cloud, qpu:belenos / qpu:ascella | None: each platform accepts a linear-optical circuit and returns `probs`, `samples`, `sample_count` or `entropy` at the end of the run ([Quandela guide](quandela/README.md)) | 24 / 12 photonic modes | 200 credits per month, QPU shots at 1e-06 credits | Content stays the user's, service license only | Account exists | Excluded: no mid-circuit measurement or conditioned gate |

## Ranking

Criteria in order: expressivity for this circuit, shot ceiling against need,
expected contrast, confidentiality.

1. Open Quantum IQM Garnet (then Emerald), conditional on `accepting_jobs`
   turning true. Expressivity: `cc_prx` with one
   control bit covers the S-dagger correction and the reset; QASM lowering and
   returned MCM bits are the open risks. Shots: 13,500 per arm on Spark, 27,172
   total. Contrast: 0.021 at 450 CZ, 0.044 at 300 CZ; feasible at 3 sigma only for
   n <= 408 routed CZ. Confidentiality: public. Needs no new sign-up.
2. IBM Open Plan with the 180-minute offer (the same machine, not a substitute).
   Expressivity is proven; the contrast is measured and consistent with zero at
   100,000 shots per arm against a predicted 0.034, so more Heron r2 shots of
   the same circuit answer nothing new until the missing channel is identified.
   The 180-minute allowance (10,800 s) is eighteen times the 600 s window.
   Private. Cost is the owner's opt-in.
3. Amazon Braket IQM Garnet. Same chip and instruction set as ranking 1, so the
   same contrast screen, with an unlimited paid shot supply: at 450 CZ,
   2 * (0.30 + 0.00145 * 20,578) = $60.3 for 3 sigma and
   2 * (0.30 + 0.00145 * 57,160) = $166.4 for 5 sigma; at 713 CZ even 3 sigma costs
   2 * (0.30 + 0.00145 * 270,858) = $786.1. Private under AWS terms. MCM bits are not
   returned, so requirement 4 needs the copy-qubit workaround.

Quantinuum H2 or Helios ranks first on contrast (all-to-all connectivity removes
the routing term) and on expressivity (classical conditions through Q# `if` or
QIR Adaptive RI; the Qiskit port path is unverified, see the survey row), but offers no free
individual quota in the pages reached, and the published HQC formula and the
$125,000 Standard plan imply a cost of order $10^4 for 5,000 shots. The estimate
assumes N1q = 600, N2q = 300, Nm = 10 (not derived from a compiled circuit),
giving HQC = 5 + 5000 * (600 + 3000 + 50) / 5000 = 3,655, and prices an HQC at
$12.5 from the subscription ($125,000 for 10,000 HQC); the pay-as-you-go unit
price is not published.
It becomes the first choice only through an institutional or grant route.

## Recommendation and uncertainty

Wait for the Garnet-grid routing and for iqm:garnet to accept jobs. If the CZ
count is at most about 350 (up to 410 at f = 0.759), run the
experiment on Open Quantum Garnet in two Spark-funded jobs of about 13,500
shots, one per arm, after a one-circuit probe confirms the `cc_prx` lowering
and the returned bits. If it is above 410, the Spark balance cannot reach 3
sigma, and the options are the IBM 180-minute offer, or Braket Garnet at the
costs above. Confidence that Garnet reaches 3 sigma on the Spark balance:
low (below 25 percent), set by the unrouted CZ count, by the assumed f (0.564 to
0.759, all fitted to noise-model values the Kingston measurement did not reproduce),
and by whatever removed the effect on Heron r2. A Kingston diagnostic that
identifies that channel raises this rating if it is Heron-specific and lowers
it if it is generic to mid-circuit measurement.
The cost ordering (Open Quantum before Braket) has high confidence, as it
follows from the stated rates. No contrast ordering survives the Kingston
measurement: the only measured contrast is consistent with zero. The residual
factor, IQM readout and reset overhead, and the fat tail of the CZ error would
move the contrast estimate by tens of percent; a
`cc_prx` that rejects theta = pi/2 would invalidate the S-dagger construction.

## Owner actions

1. Approve a written one-circuit probe on iqm:garnet (Public, Spark) that checks
   `cc_prx` with theta = pi/2, the QASM form of the feedback key, and whether
   `measure_ff` bits return in counts. This is the only step that resolves the
   three unverified Open Quantum risks.
2. Decide whether to opt in to IBM's 180-minute Open Plan offer; it buys a
   Heron r2 rerun only once a hypothesis for the measured null exists.
3. State the owner's location, which decides eligibility for the EuroHPC pilot
   call (cut-offs 1 Nov and 1 Dec 2026), and whether an institutional channel to
   Quantinuum exists.
4. Sign-ups for Amazon Braket, Azure Quantum, IQM Resonance and Quantinuum are
   the owner's action and are not needed unless step 1 fails or the Garnet
   routing exceeds about 410 CZ.
5. Approve the Public tier's disclosure terms for any Open Quantum run
   (circuits and results public, retained by Quantum Rings).

## Unverified

- Open Quantum QASM lowering of `if`/`else` to `cc_prx` and return of
  `measure_ff` bits.
- Hardware acceptance of `cc_prx` with theta other than pi.
- Reuse of one feedback key for both the reset and the round-2 correction.
- Feed-forward on IQM Resonance and on the EuroHPC VLQ system.
- IQM Resonance credit-to-second conversion; data terms of Resonance, Braket,
  Azure and EuroHPC.
- Azure Quantum's per-provider free credit and any Quantinuum academic route.
- Origin Quantum hardware feed-forward and Research Incentive terms; Quafu
  hardware feed-forward; Alice & Bob, OQC, SpinQ and direct Rigetti QCS.
- Square-lattice routed CZ count of the circuit.
