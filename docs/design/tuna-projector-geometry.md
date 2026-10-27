# Tuna-17 sequential-projector geometry and measurement-context response

Status: prospective; provider execution requires approval of the bounded case below. The first batch qualifies
the instrument and register contract. A later counterbalanced campaign tests measurement-context dependence.
Neither batch proves a new algebra theorem or an unrestricted model of measurement backaction.

## Question and source boundary

Can Tuna-17 implement filters having equal first-pass acceptance but different sequential acceptance, and does
reading the filter ancilla early change that response relative to deferring its readout? The discriminator is the
second moment of squared principal-angle cosines, rather than success probability alone.

The source investigation joins four specific inputs:

- `open_gororoba` commit `5435fe325b83383e82eaa66a19c6f8a09aa50187`,
  [grassmannian.rs](https://github.com/Oichkatzelesfrettschen/open_gororoba/blob/5435fe325b83383e82eaa66a19c6f8a09aa50187/crates/algebra_analysis/src/grassmannian.rs):
  principal angles from singular values of frame overlaps, and numerical sedenion annihilator tests. The present
  two-qubit projectors are an exact illustrative family; they are not certified Cayley-Dickson annihilators.
- The same commit's
  [BranchSignedCoherence.v](https://github.com/Oichkatzelesfrettschen/open_gororoba/blob/5435fe325b83383e82eaa66a19c6f8a09aa50187/proofs/theories/BranchSignedCoherence.v):
  asymmetric branch assignment mixes signed and unsigned moments. Its proof source was inspected; its kernel
  receipt was not replayed during this design. Branch outcomes therefore remain unnormalized in the analysis.
- `openai/math` commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`,
  [exact-factoring manuscript](../notes/papers/openai-2026-exact-quantum-factoring.md), Lemma 2.2, pp. 3-4:
  retaining measurement history coherently reproduces the measured output law. The equality used here is proved
  directly below; the full factoring theorem is unnecessary. Its minimum construction size exceeds this device.
- The quantum repository's [singular-sector analysis](../notes/singular_sector_dynamics.md),
  [algebra contract](../notes/algebra_circuit_rules.md),
  [projected-unitary source note](../notes/papers/1806.01838.md), and
  [Tuna shot-record literature](../notes/quantum_inspire/shot-record-literature.md) establish conventions and known
  nuisance mechanisms. Private reading copies in `gororoba-quantum-documents` supplied primary manuscript pages;
  source text is not redistributed here.

The dimension-six Hadamard manuscript provides another exact-grid Ramsey candidate, but classically compiling
its phases primarily tests phase-word implementation. Embedded qutrit bases need additional approximate synthesis.
The Jacobsthal asymptotic result supplies no finite device-sized bound. These alternatives do not justify claiming
that the selected experiment tests every manuscript. The proposal is a candidate new hardware characterization;
principal-angle identities and deferred measurement are established mathematics, and publication priority remains
unassessed beyond this bounded source comparison.

## Derivation from inner products and Born's rule

For orthonormal column frames A and B, define P = A A-dagger and Q = B B-dagger, both rank r. The singular values
of A-dagger B are cos(alpha_j), where alpha_j are the principal angles. With rho = P/r, cyclicity of the trace gives

    m1 = tr(Q rho) = tr(PQ)/r = sum_j cos(alpha_j)^2/r,
    m2 = tr(P Q rho Q P) = tr(PQPQ)/r = sum_j cos(alpha_j)^4/r.

The second expression is joint acceptance of Q and then P, not conditional acceptance. Consequently
m2 - m1^2 is the variance of cos(alpha_j)^2. A first-moment match leaves that variance undetermined.

Use two data qubits A and B and a history ancilla C. The tensor convention is A, B, C, with standard
Y = [[0,-i],[i,0]] and Ry(theta) = exp(-i theta Y/2). Set

    P = (I + Z_A)/2,
    Q_theta = [I + (cos(theta) Z_A + sin(theta) X_A) Z_B]/2.

The Pauli product in brackets squares to I, so Q_theta is a rank-two orthogonal projector. On the range of P,
P Q_theta P has eigenvalues lambda_plus/minus = (1 +/- cos(theta))/2. Therefore

    m1 = 1/2,
    m2 = (1 + cos(theta)^2)/4,
    m2 - m1^2 = cos(theta)^2/4.

| theta | first acceptance m1 | joint acceptance m2 | second acceptance given first |
|---:|---:|---:|---:|
| 0 degrees | 1/2 | 1/2 | 1 |
| 45 degrees | 1/2 | 3/8 | 3/4 |
| 90 degrees | 1/2 | 1/4 | 1/2 |

The circuit prepares |0>_A |+>_B |0>_C, then applies Ry_A(-theta), CNOT(A,C), CNOT(B,C), Ry_A(theta).
Taking its C=0 matrix element gives Q_theta exactly. In particular,

    Q_theta |0,+> = (|0,+> + cos(theta)|0,-> + sin(theta)|1,->)/2.

The three terms are orthogonal, proving the table directly. Equal B populations suffice: |+>, |-> and I/2 give
the same (A,C) distribution. The experiment realizes the stated two moments without certifying a maximally mixed
input or inter-sector coherence. A classical mixture can reproduce these population data.

An X readout on A adds a sign-sensitive check:

    E[1_(C=0) X_A] = sin(theta) cos(theta)/2.

The values at +/-45 degrees are +/-1/4; division by m1 gives conditional +/-1/2. The joint signed moment, rather
than the ratio, is the primary object. Moving both opposing rotations before the parity computation makes them
cancel, leaving Q_0 and m2=1/2 at every nominal angle. That mutation retains nominal gate slots; its compiled
exposure must be checked rather than presumed unchanged.

## Early versus deferred history

Let E_c be the ancilla's computational projector and F_a the final data projector. Every subsequent data-only
operation V commutes with E_c. Thus tr(F_a V E_c rho E_c V-dagger) equals the terminal joint probability with E_c
deferred until the end. This equality requires neither feed-forward nor a claim about the factoring algorithm.

A physical difference can arise from measurement-induced excitation/dephasing, assignment context, leakage,
elapsed time, coherent gates, or drift. Early C readout versus simultaneous terminal A,C readout changes detector
context as well as timing. The successor campaign must include deferred sequential C-then-A readout and matched
assignment controls; even that comparison requires timing admission before attributing a difference to backaction.
The first qualification batch estimates response and register consistency only.

## Hardware variables and interactions

The [retained live observation](../evidence/tuna-projector-geometry/backend-observation.json) supplies the topology,
native gate set, status, queue and limits at its timestamp. It is not a calibration snapshot.

| Variable | Treatment or control | Remaining inference boundary |
|---|---|---|
| Physical placement | Three disjoint (A,C,B) triples: (1,4,8), (13,11,14), (3,6,9); verify both edges live | First batch confounds geometry and placement; rotate assignments before a geometry claim |
| Filter angle | 0,45,90 degrees, optional -45 sign control | All lie on the documented 5-degree grid; serialization and compiler rounding still checked |
| Native gates | Each CNOT becomes H_C CZ H_C; two CZ per replica | Nominal equality does not establish equal analog error |
| Preparation | A,C in zero, B in plus | Equal B populations required; preparation and assignment errors are coupled |
| T1, T2 Ramsey/echo | Published values unavailable in the observed datasource outage | No contemporary values are imputed from older jobs |
| Measurement duration | Dated dashboard notice says 300 ns; older KB-derived notes say 800 ns | Served schedule unresolved; 15/40-cycle idle arms bracket source values, not a measured duration |
| Wait duration | Explicit cycles of 20 ns, surrounded by barriers | ALAP scheduling and barrier behavior require compiler/source checks |
| Readout timing | Early, deferred simultaneous, deferred sequential | Additional measurement context and total duration require separate accounting |
| Repeated ancilla readout | Preserve first and final C bits | Disagreement mixes assignment, relaxation and imperfect QND behavior |
| Readout joint error | First batch includes all-zero/all-one checks | Those two states cannot identify a full four-state correlated assignment matrix |
| Spectator occupancy | Unused qubits initialized to zero; retain terminal bits | All-one calibration changes spectator context and remains diagnostic |
| Parallel coupling | Three replicas measured in the same shots | Pair covariance reports shared variation; replicas are not independent samples |
| CZ coherent phase/leakage | Same emitted gate locations; later isolated-replica controls | Binary outputs cannot uniquely identify leakage |
| Frame/axis error | Sign-sensitive X endpoint and rotation mutation | Z-only moments cannot detect rotation sign |
| Readout ringing | Explicit settle-gap factor in the successor campaign | A decay with gap does not uniquely identify a resonator mechanism |
| Drift/calibration boundaries | Retain timestamps, status and every raw shot; rotate/counterbalance future assignments | Separate jobs do not share a guaranteed calibration |
| Periodic shot correlations | Preserve shot order and fixed block summaries; inspect the known line | Shot position is not a physical timestamp; binomial errors can be optimistic |
| Job ordering | Initial qualification order frozen; later order needs independently registered randomization | Qualification supports descriptive estimates only |
| Compiler | Local pinned libqasm/OpenSquirrel parsing and native compilation | Remote executed schedule remains outside local verification |
| Register semantics | Qubit 0 rightmost; preserve extra early-history bits on Tuna | QX returns last outcome by qubit and cannot qualify early-bit retention |
| Queue/pause | Repository submit guard: at most three circuits, one hardware batch, account-wide pause | Availability and free credits do not imply exclusive instrument ownership |

All interactions cannot be identified from a small pilot. The successor's principal crossed factors are angle x
placement x readout mode, then gap x mode and spectator/parallel context x mode. Controls determine which channels
can be separated before a model fit. Parameter combinations invisible to the observables stay unresolved.

## Concrete first acquisition case

The generator's manifests and circuit digests are the execution inputs. The procedure first requests approval
for a three-circuit QX conformance batch, then separately for one three-circuit Tuna qualification batch:

| Stage | Backend | Circuits | Shots each | Total shots | Purpose |
|---|---|---:|---:|---:|---|
| Conformance | QX emulator, type 1 | 3 | 2048 | 6144 | Compact nine-qubit normal Z, rotation-mutation Z, normal X; terminal outcome semantics only |
| Qualification | Tuna-17, type 7 | 3 | 4096 | 12288 | All-zero, all-one, and early-history projector circuits on the three placements |

The written case authorizes neither stage by itself. QX execution follows user approval; its result must match
the compiled ideal laws before hardware approval is requested. A QX failure is investigated rather than bypassed.
QX admission freezes a descriptive discrepancy screen before acquisition: every one of the nine replica
herald frequencies must lie within 0.05 of 1/2; the three normal-Z joint frequencies must lie within 0.05
of (1/2, 3/8, 1/4); the three mutation-Z joint frequencies must lie within 0.05 of 1/2; and the three
normal-X signed joint means must lie within 0.10 of (0, 1/4, 0). Counts must equal 2048 and strings
must have width nine. Under independent ideal simulator shots, Hoeffding's inequality and a union bound
for these 18 summaries give a false-refusal bound of 36 exp(-2*2048*0.05^2), approximately 0.00129;
the signed means have range two and use twice the tolerance. This bound assumes independence across
shots, but requires no independence among summaries. The screen qualifies remote sampling conformance;
it supplies neither a hardware significance test nor permission to repeat a failed batch automatically.

The hardware batch fits the FAQ's three-circuit ceiling. Its historical execution estimate is
3*(2.6 + 4096*0.00053) = 14.31264 seconds; that regression is an estimate, not a fresh scheduler promise.
QX's retained per-job range is 0.03-10.4 seconds, hence 0.09-31.2 seconds for the batch. The service reports
per-job limits of 3600 seconds for QX and 300 seconds for Tuna; queue time is additional. Recorded terms imply
zero expected metered credits, subject to a fresh account/terms check before any submission. A pricing change
requires renewed approval. No acquisition outside these exact manifests is covered by the proposed approvals.
The [account-ledger observation](../evidence/tuna-projector-geometry/usage-observation.json) at
16:08:31 UTC on 27 October reports zero recorded credit change; it does not establish future tariff terms.

The hardware question is the physical register/readout response after the return to service; a simulator cannot
establish it. The QX stage only tests remote circuit conformance. The qualification batch does not measure fresh
T1/T2 or resolve the full correlated assignment matrix. Those are later explicit acquisition obligations.

Retain raw outcomes before analysis. Stop if any job fails, widths/counts mismatch, execution exceeds the case
estimate materially, a calibrated qubit's empirical assignment contrast is below 0.5, or more than 10 percent of
ancilla first/final outcomes disagree. The last two thresholds are conservative pilot admission choices, not
literature-derived instrument specifications. Report a refusal descriptively, preserve all data, and reassess.
Passing those screens does not prove stationarity, QND measurement, or measurement backaction.

The maximal independent-shot standard error of a probability with 4096 shots is 1/(2 sqrt(4096)) = 0.0078125.
The ideal endpoint separation is 0.25. These are planning scales only: placement, assignment, drift and temporal
correlations dominate the interpretation until controlled. The analyzer produces counts, unnormalized moments,
herald disagreement, within-shot cross moments and fixed contiguous block summaries; it emits no significance
verdict or independence claim. Confidence and power for a later confirmatory test require a frozen dependence
model and calibration uncertainty from admitted data. Optional stopping and postselected conditional ratios
must not turn the pilot into a confirmatory result.

## Successor campaign and stopping boundary

After qualification: identify all four joint readout states in each readout context; qualify early-bit retention;
rotate geometry across placements; counterbalance early/deferred/deferred-sequential jobs; compare sign-sensitive
and cancelling-rotation controls; vary settle gaps; finally compare parallel versus isolated replicas. Every
stage retains its own case, cost, approval, sanity checks and account pause. The existing plan for algebraic
sequential heralds remains a separate, harder question requiring exact cd_core projectors and a convention map.

The full campaign reaches an interpretable device result only when the compiled instrument, context-dependent
assignment uncertainty, scheduling range and dependence model jointly explain the reported uncertainty. A
rejection then rejects that specified model. It does not establish nonassociative physical evolution, settle
the dimension-six MUB maximum, or prove the exact-factoring manuscript.

The [qualification admission contract](tuna-projector-qualification-admission.md) freezes
the executable pilot decision, records peer-review dispositions and specifies live admission
for the user-authorized unchanged three-circuit hardware case.
