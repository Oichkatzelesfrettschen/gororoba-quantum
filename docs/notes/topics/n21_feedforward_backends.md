# N=21 feed-forward: backends besides IBM Heron r2

Status: DRAFT. Each claim names its source; a claim no reachable document
supports is marked unverified, and the [Unverified](#unverified) section lists
them. The ibm_kingston endpoint of 2026-10-18 comes from
[N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md](../../../results/live/N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md).

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
   ([linear_conjugation](../../evidence/linear_conjugation/README.md); 739 is that
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

The [scheduled-idle replay](../../../results/live/2026-10-18T090603.530638Z/IDLE_REPLAY_FINDINGS.md)
reaches the null without any of the three. The service schedule leaves the leaf qubits 104, 106, 124 and 126
idle for 57 to 62 us of the 70 us circuit behind their hubs' CZ chains, and the noise model charged that idle
nothing. Written in as delays under the execution Target's T1 and T2, the idle moves the exact contrast from
+0.0310 to -0.0007, inside the measured interval, and cuts the law distance to hardware by 40 percent in both
arms. A residual of about 0.013 TVD leaves coherent idle error open.

Consequences for this survey:

- The residual factor f below is fitted to the noise-model values, not to a
  measurement. The measured Kingston contrast is consistent with zero, so no
  measured f exists to carry to another machine. The IQM rows are equal-f
  scenarios: IQM's readout, reset, one-qubit and idle survival can exceed
  f = 0.759, and no row alone establishes that a route is infeasible.
- A run on a second feed-forward stack is a stack-level replication. A nonzero
  contrast on IQM would not by itself place the missing structure in the
  Heron r2 feed-forward path, because topology, routed depth, native gates,
  reset and the copy-qubit readout all change with the machine; isolating the
  feed-forward controller needs a matched control. A null would be consistent
  with the Kingston one. Either outcome needs the shot count the screen
  derives.

Deferred measurement (a coherent controlled-S-dagger, `cp(-pi/2)`, onto an
eighth qubit) removes
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
  Braket guide allows repeated control of a qubit only when no active reset
  was performed on it, and this circuit active-resets the control and then
  applies the conditional S-dagger to the same qubit, so Braket's documented
  contract excludes the circuit. Open Quantum's stack states no contract for
  this case: unverified until a probe shows it accepted.
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

Shots needed. The family's admitted contract
([N21_USAGE_BUDGET.md](../../../gororoba_quantum/N21_USAGE_BUDGET.md)) sizes a run
so that detection at alpha plus power 0.8 fits the contrast: K / sqrt(n) <= c
with K = 9.724 under Hoeffding, so n = (K / c)^2 shots per arm. The
empirical-Bernstein opt-in's K of about 9.16 holds near 90,112 Kingston shots
and grows as n falls, and its planning needs per-PUB outcome laws that this
scalar screen lacks, so only the Hoeffding sizing applies here. For the three noise-model values of the
713-CZ Kingston routing, c = 0.0417, 0.0344 and 0.0310, this gives 54,378,
79,905 and 98,394 shots per arm under Hoeffding; the Kingston run spent
100,000 per arm. A 3-sigma normal approximation, (3 / c)^2, understates the
requirement by a factor of about ten and does not size a run.

First-order contrast model. Contrast = 0.25 * f * exp(-n e), with n the routed CZ
count and e the median CZ error. Kingston's median CZ error in
`docs/evidence/heron_platform/targets.json` (retrieved 2026-10-14) is 0.002125
over the pairs whose reported error is below 1. Matching the model values at
n = 713 fixes the residual factor (readout, one-qubit and idle loss) at
f = 0.759 for c = 0.0417, 0.626 for 0.0344 and 0.564 for 0.0310; the three
values come from calibrations of 2026-10-16 and 2026-10-18 while e comes from
the 2026-10-14 snapshot. Garnet's median CZ fidelity is 99.51 percent
(e = 0.0049) and Emerald's 99.5 percent (e = 0.005) per the Open Quantum
provider pages. The rows below are equal-f scenarios at f = 0.759, the largest
fitted value; IQM's own f is unknown. The model ignores IQM's readout and reset
durations, crosstalk and the fat tail of the CZ error distribution, so treat it
as a screen, not a prediction.

| Backend | Routed CZ n | Contrast | Shots per arm, K = 9.724 |
| --- | --- | --- | --- |
| ibm_kingston (model) | 713 | 0.0417 | 54,378 |
| ibm_kingston (measured) | 713 | +0.0027, consistent with 0 | n/a |
| IQM Garnet | 713 | 0.0058 | 2,845,699 |
| IQM Garnet | 450 | 0.0209 | 216,192 |
| IQM Garnet | 300 | 0.0436 | 49,708 |
| IQM Garnet | 200 | 0.0712 | 18,656 |
| IQM Garnet | 150 | 0.0910 | 11,430 |
| IQM Garnet | 100 | 0.1162 | 7,002 |

Break-even on Spark. 13,586 shots per arm meet the contract for c >= 0.0834,
that is n <= 167 routed CZ on Garnet at f = 0.759 and n <= 107 at f = 0.564.
Emerald, whose per-shot fee leaves 12,312 shots per arm (c >= 0.0876), gives
154 and 95. The Spark threshold in the equal-f scenario is therefore about 110
to 170 routed CZ, below every routing of the circuit the repository
records; a larger f on IQM raises it. The deciding inputs are the CZ count of a
square-lattice routing of the circuit, which no branch of the repository holds
yet, and IQM's own f. Paid Public credits cost ceil(0.18 + N * 0.00087)
credits per job at one USD-equivalent dollar per credit: at 300 CZ the
contract's 49,708 shots per arm take three jobs at the 20,000-shot ceiling,
18 + 18 + 9 = 45 credits per arm.

## Provider survey

Legend: FF = real-time classically conditioned gates, not only mid-circuit
measurement. Quota rows are what the page states; sources are cited per row.

| Service | FF support | Qubits, connectivity | Free quota | Data terms | Eligibility | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Open Quantum, IQM Garnet / Emerald (Online, `accepting_jobs` false at the 2026-10-17 read) | `dynamic_circuits` feature, `cc_prx`, `measure_ff` ([catalogue](../../evidence/open_quantum/catalogue.json)); QASM lowering unverified | 20 / 54, square lattice, 99.51 / 99.5 percent median CZ ([Garnet page](../open_quantum/site/providers_iqm_garnet.md)) | 25 Spark credits at signup and 25 every 90 days, claimed by hand ([free-credits page](../open_quantum/site/free-credits.md)) | Public tier: circuits and results public, retained by Quantum Rings ([README](../open_quantum/README.md)) | Account exists | Verified catalogue; FF path unverified |
| IBM Open Plan, ibm_kingston | `if_else`, tested by the family | 156, heavy-hex | 10 min per 28 days; a one-time 180 min over 12 months for users who log 20 min in any 12 months, opt-in ([IBM blog 2026-03-16](https://www.ibm.com/quantum/blog/open-plan-updates)); the job inventory records 449 s, so 751 s more must accrue before the offer opens | IBM data terms not reviewed | Non-trial Open Plan account | Same machine, larger budget; the 10 min per 28 days is the 600 s rolling window `AGENTS.md` records. Measured null at 713 CZ on 2026-10-18 |
| Amazon Braket, IQM Garnet / Emerald | `measure_ff`, `cc_prx`, experimental, verbatim only; MCM bits not returned; repeated control after an active reset excluded ([developer guide](https://docs.aws.amazon.com/braket/latest/developerguide/braket-experimental-capabilities.html)) | 20 / 54, 2 / 4 groups | None for QPUs; $0.30 per task + $0.00145 (Garnet) / $0.00160 (Emerald) per shot ([pricing](https://aws.amazon.com/braket/pricing/)) | AWS terms, not reviewed | Any AWS account | Excludes this circuit (reset then control); paid |
| IQM Resonance Starter | Not documented for Resonance; the IQM Qiskit guide says availability depends on the instrument | Crystal 54, Crystal 20, Star 24 beta ([IQM](https://www.iqm.tech/products/iqm-resonance)) | Up to 30 credits per month, availability-dependent; pay-as-you-go from $0.30 per QPU second; credit-to-second conversion unstated (inferred 1 s, unverified) | Unstated on the page | Unstated | FF on Resonance unverified |
| EuroHPC quantum pilot call (Euro-Q-Exa, Lucy, Piast-Q, VLQ) | Not mentioned; VLQ is IQM-built per the [Open Quantum IQM page](../open_quantum/site/providers_iqm.md), FF unverified | Not stated | Free; rolling cut-offs on 1 Nov and 1 Dec 2026 ([EuroHPC](https://www.eurohpc-ju.europa.eu/eurohpc-ju-opens-access-its-quantum-computers-2026-06-25_en)) | Not mentioned | Research, public sector or industry in Europe | Unverified FF; eligibility depends on the owner's location |
| Azure Quantum, Quantinuum H2-1 / H2-2 | Conditional logic on measurement results via Qiskit `c_if` or Q# `if`, QIR Adaptive RI ([provider page](https://learn.microsoft.com/azure/quantum/provider-quantinuum)). The page's `c_if` example does not exist in Qiskit 2.5.2 (`QuantumCircuit.x(0)` returns an instruction with no `c_if`); the repo's circuit uses `if_test`, so a port needs the provider's control-flow path, unverified | 56, all-to-all | None on hardware; syntax checkers free; emulator free with a hardware subscription; HQC = 5 + C(N1q + 10 N2q + 5 Nm)/5000 ([pricing](https://learn.microsoft.com/azure/quantum/pricing)); Standard plan $125,000 per month for 10k HQC | Azure terms, not reviewed | Pay-as-you-go via sales contact | Expressive, not free; the $500-per-provider workspace credit is not on the pages fetched: unverified |
| Quantinuum Helios (direct) | Real-time control engine, Guppy language ([coverage](https://www.constellationr.com/insights/news/quantinuum-launches-helios-quantum-computer-touts-fidelity-enterprise-customers)); conditional examples on the Helios MCMR page ([docs](http://docs.quantinuum.com/systems/trainings/helios/getting_started/mcmr.html)) | 98, all-to-all | None found for individuals; institutional agreements only (UWA, DeiC) | Not reviewed | Institutions | Access route unverified |
| Open Quantum, IonQ Forte / AQT IBEX / Rigetti Cepheus | Catalogue lists `mid_circuit_measure` for IonQ and no `dynamic_circuits` for any of the three | 36 / 12 / 108 | Same Spark balance | Public | Account exists | No FF through Open Quantum |
| Quantum Inspire Tuna-5 / 9 / 17 | No binary-controlled gates | 5 / 9 / 17 | Free | Licensed to QuTech | Account exists | Excluded |
| Origin Quantum Cloud | `qif` / `qelse` on simulators ([docs](https://qcloud.originqc.com.cn/document/pyqpanda3-docs/en/tutorial/dynamic-circuits)); hardware support not stated | Wukong-180 | A "Research Incentive Program" of free time, size and terms unstated ([report](https://quantumcomputingreport.com/origin-quantum-unveils-origin-wukong-180-fourth-generation-quantum-computer/)) | Unreached | Unreached | Unverified |
| Quafu / BAQIS ScQ | Dynamic circuits parsed in simulation only per the pyquafu changelog ([pyquafu changelog mirror](https://data.safetycli.com/changelogs/pyquafu)) | 10 in the 2022 paper | Unreached | Unreached | Unreached | Unverified |
| qBraid managed Garnet | Reseller of the Braket route; 30 qBraid credits per task + 0.145 per shot, credit = $0.01 ([qBraid pricing](https://docs.qbraid.com/v2/home/pricing)); inherits Braket's FF limits | 20 | qBraid credits only | qBraid terms, not reviewed | Account | Duplicate of the Braket row |
| qBraid Open Quantum integration | Targets `openquantum:*` devices and bills the connected Open Quantum account; qBraid credits do not fund it ([integration](https://docs.qbraid.com/v2/account/integrations/openquantum)) | 20 / 54 | The Open Quantum account's Spark and paid credits | Open Quantum terms | Account plus Open Quantum account | Duplicate of the Open Quantum row |
| Rigetti QCS direct (Ankaa-3, Cepheus-1-108Q) | Searched: pyQuil and QCS pages surfaced no mid-circuit feedback documentation; the QCS FAQ has an active-reset section ([FAQ](https://docs.rigetti.com/qcs/faq)) whose text was truncated | 84 / 108, square-type lattice | None found; Azure PAYG $0.02 per 10 ms of execution ([pricing](https://learn.microsoft.com/azure/quantum/pricing)) | Not reviewed | Not reviewed | No feed-forward documentation found |
| IonQ direct | "Dynamic circuit execution is not supported on any IonQ target" ([OpenQASM 3 docs](https://docs.ionq.com/api-reference/v0.4/openqasm3)); branching fails preflight | 36 | Research Credits Program, up to $10,000, 2021 terms: academic researchers, current terms unchecked ([IonQ cloud page](https://ionq.com/quantum-cloud)) | Not reviewed | Academic | Excluded: no FF |
| Oxford Quantum Circuits (Toshiko) | Searched: no feed-forward statement found ([OQC Cloud](https://oqc.tech/access/oqc-cloud/)) | 32 | None found | Not reviewed | Not reviewed | No feed-forward documentation found |
| Alice & Bob (Boson 4) | Searched: no feed-forward statement found; cat-qubit test chip on Google Cloud Marketplace ([report](https://quantumcomputingreport.com/alice-bob-is-making-access-to-their-boson-4-cat-qubit-test-chip-available-to-researchers-through-the-google-cloud-marketplace/)) | Test chip | None found | Not reviewed | Researchers | No feed-forward documentation found |
| SpinQ cloud | Searched: no mid-circuit or feedback statement found ([SpinQ cloud](https://www.spinquanta.com/products-services/quantum-computing-cloud-platform)) | 2 / 3 / 5 / 8 | None found | Not reviewed | Not reviewed | Below 7 qubits |
| Pasqal Fresnel | Analog neutral-atom device ([Azure pricing](https://learn.microsoft.com/azure/quantum/pricing)) | 100 | n/a | n/a | n/a | Not gate-based for this circuit |
| Quandela Cloud, qpu:belenos / qpu:ascella | None: each platform accepts a linear-optical circuit and returns `probs`, `samples`, `sample_count` or `entropy` at the end of the run ([Quandela guide](../quandela/README.md)) | 24 / 12 photonic modes | 200 credits per month, QPU shots at 1e-06 credits | Content stays the user's, service license only | Account exists | Excluded: no mid-circuit measurement or conditioned gate |

## Ranking

Criteria in order: expressivity for this circuit, shot ceiling against need,
expected contrast, confidentiality.

1. Open Quantum IQM Garnet (then Emerald), conditional on `accepting_jobs`
   turning true. Expressivity: `cc_prx` with one
   control bit covers the S-dagger correction and the reset; QASM lowering,
   returned MCM bits and feedback-key reuse are the open risks. Shots: 13,586
   per arm on Spark, 27,172 total. Contrast in the equal-f scenario: 0.044 at
   300 CZ, 0.071 at 200 CZ; the Spark balance meets the contract only for
   n <= about 170 routed CZ. Confidentiality: public. Needs no new sign-up.
2. IBM Open Plan with the 180-minute offer (the same machine, not a substitute),
   once the account has logged the 1,200 s the offer requires; the job
   inventory (`results/live/qpu-job-inventory.json`) records 449 s, so the
   offer is unavailable today.
   Expressivity is proven; the contrast is measured and consistent with zero at
   100,000 shots per arm against a predicted 0.034, so more Heron r2 shots of
   the same circuit answer nothing new until the missing channel is identified.
   The 180-minute allowance (10,800 s) is eighteen times the 600 s window.
   Confidentiality: IBM data terms not reviewed, so unknown. Cost: 751 s of
   further runtime, then the owner's opt-in.
Amazon Braket IQM Garnet is unranked: its guide excludes repeated control
of a qubit after an active reset, which this circuit needs. Were a variant
admitted, its costs under the contract (K = 9.724) and the 20,000-shot task
ceiling would be 2 * (0.30 + 0.00145 * 18,656) = $54.7 at 200 CZ, three tasks
per arm and about $146.0 at 300 CZ, and 143 tasks per arm (286 tasks) and
about $8,338 at 713 CZ. Confidentiality: AWS data terms not reviewed, so
unknown. MCM bits are not returned, so requirement 4 would need the
copy-qubit workaround.

Quantinuum H2 or Helios removes the SWAP-routing overhead through all-to-all
connectivity, but the circuit's own entangling gates, measurements, resets and
conditional operations still attenuate the contrast; without a compiled circuit
and a hardware-grounded error model its contrast ranking is unverified.
Expressivity covers classical conditions through Q# `if` or QIR Adaptive RI;
the Qiskit port path is unverified (see the survey row). No free individual
quota appears in the pages reached, and the published HQC formula and the
$125,000 Standard plan imply a cost of order $10^4 for 5,000 shots. The
estimate assumes N1q = 600, N2q = 300, Nm = 10 (not derived from a compiled
circuit), giving HQC = 5 + 5000 * (600 + 3000 + 50) / 5000 = 3,655, and prices
an HQC at $12.5 from the subscription ($125,000 for 10,000 HQC); the
pay-as-you-go unit price is not published. It becomes a candidate only through
an institutional or grant route.

## Recommendation and uncertainty

Wait for the Garnet-grid routing and for iqm:garnet to accept jobs. If the CZ
count is at most about 110 to 170 in the equal-f scenario, run the experiment
on Open Quantum Garnet in two Spark-funded jobs of 13,586 shots, one per arm,
after a one-circuit probe confirms the `cc_prx` lowering, feedback-key reuse
and the returned bits. Above that, the Spark balance cannot meet the contract,
and the options are paid Public credits or, once 751 s more of IBM runtime
has accrued, the IBM 180-minute offer. Confidence that Garnet meets the
contract on the
Spark balance: low, set by the unrouted CZ count, by IQM's unknown f (the
fitted 0.564 to 0.759 transfers no bound), and by whatever removed the effect on
Heron r2. A Kingston diagnostic that identifies that channel raises this
rating if it is Heron r2-specific and lowers it if it is generic to mid-circuit
measurement. The cost
ordering (Spark before paid Public credits) has high confidence, as it follows
from the stated rates. No contrast ordering survives
the Kingston measurement: the only measured contrast is consistent with zero.
A `cc_prx` that rejects theta = pi/2 would invalidate the S-dagger
construction.

## Owner actions

1. Approve a written one-circuit probe on iqm:garnet (Public, Spark) that
   checks `cc_prx` with theta = pi/2, the QASM form of the feedback key, both
   conditionals (the active reset and the S-dagger) driven from one
   `measure_ff` key, and whether `measure_ff` bits return in counts. This step
   resolves the four unverified Open Quantum risks.
2. Decide whether to opt in to IBM's 180-minute Open Plan offer once the
   account has logged 1,200 s of runtime; it buys a
   Heron r2 rerun only once a hypothesis for the measured null exists.
3. State the owner's location, which decides eligibility for the EuroHPC pilot
   call (cut-offs 1 Nov and 1 Dec 2026), and whether an institutional channel to
   Quantinuum exists.
4. Sign-ups for Azure Quantum, IQM Resonance and Quantinuum (and Amazon
   Braket, only for a variant that avoids reset-then-control) are
   the owner's action and are not needed unless step 1 fails or the Garnet
   routing exceeds the Spark threshold.
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
