# Ascella instrument readiness and packed tests

The hardware programme measures the transfer response of a 12-mode optical
processor, rather than treating ideal circuit synthesis as device evidence.
The [case generator](../../scripts/hypercomplex_photonic_cases.py) preserves
the original frozen cases and writes successors with every physical output
retained. The [operator case runbook](../runbooks/hypercomplex-operator-cases.md)
owns the operator definitions and the submission procedure.

## Instrument failure and repair boundary

Three retained acquisitions return the same instrument diagnostic:

| Job | Request | Observation |
|---|---|---|
| `c2edef5d-5e6f-4161-83fc-aadd024171fb` | 12-mode template, input 4, 12 iterations | error after 1 second, zero shots |
| `e6f2cc2d-e4f8-4b78-ad4a-d16dbf8e9f95` | 4-mode order template, input 0, 8 iterations | error after 1 second, zero shots |
| `f758aa3b-85c6-4c31-8bc5-535c5b1ff05c` | static native H coupler, input 0, all 12 outputs | error after 1 second, zero shots |

The exact diagnostic is
`RuntimeError: hardware_info.circuit_input_ports must be defined in the hardware_configto use Instruments.set_pic_input().`
The static job removes iteration and free-parameter binding from the failing
path. The two input modes are members of the published connected-input list.
The local static circuit gives probabilities 1/2, 1/2 on outputs 0 and 1.
These observations isolate a provider instrument-configuration failure on the
tested sampling paths. They establish neither failure of every Ascella command
nor successful execution after a hypothetical configuration repair.

A fourth retained job, `763c39ea-5ebc-4c75-9d97-eea4d7a6edb9`, tests a static
12-mode circuit matching all 132 calibrated Rx couplers and 126 phase positions
of the published Ascella architecture, with every phase bound to zero. The
local full-operator check and fresh live-architecture admission pass. The job
again fails after one second with zero shots and the same instrument diagnostic.
Matching the published architecture is therefore insufficient to repair the
tested sampling path. The worker's internal compilation decisions remain
unobserved. The [API audit](../evidence/quandela/input-port-api-audit/README.md)
retains the current schemas, portal call sites and authentication boundaries.

The full-source native readiness successor occupies each of the six connected
input modes once and keeps an at-least-one-click filter, including multi-click
outputs. The successor asks whether the
failure depends on selecting a subset of sources; it claims neither a
six-photon coincidence law nor quantum advantage. Its dry plan fits 1024
samples, 2048 shots, 300 seconds and 1.002048 credits, but emits the binding
low-HOM warning at 87.36 percent. The warnings-as-errors rule holds that case
before submission. The case remains prospective.

The recheck `6fa19f42-da09-47e9-aecd-51c690622f4c` follows the observed
`calibration` to `available` transition. Its fresh architecture and status
checks pass, but the job again returns the input-port error after one second
with zero shots and zero debit. The public status transition is insufficient
evidence of restored input control.

### Stopping-rule adjudication

The [static readiness receipt](../../results/quandela/runs/ascella-static-input-readiness/submission.json)
states: "Stop further Ascella submissions on instrument error or zero samples."
Its [collected result](../../results/quandela/runs/ascella-static-input-readiness/results.json)
recorded both conditions at 11:25:22 UTC on 22 October 2026. The
[native-mesh receipt](../../results/quandela/runs/ascella-calibrated-mesh-input-readiness/submission.json)
records a later submission at 11:37:08 UTC; the
[post-status-transition receipt](../../results/quandela/runs/ascella-native-input-map-recheck/submission.json)
records another at 12:09:17 UTC. The retained approval text for those requests
does not record an explicit override of the observed stop.

Both later submissions are protocol deviations. The broad authorization to
investigate and debug supplies context, rather than an explicit supersession
of the recorded stopping rule. Their errors remain descriptive diagnostic
observations; they cannot qualify as adherence to that preregistered protocol
or successful device conformance. The receipts, approval text, cases and raw
results retain their original bytes. Further Ascella execution is paused and
requires the user's heads-up plus an explicit replacement or override of the
stopping rule, as well as the applicable case and resource approval.

A safe protobuf inspection of the published architecture finds empty logical
`input_ports` and `output_ports` maps, alongside the six-source occupation,
twelve detectors and optical circuit. Logical Perceval ports therefore supply
no published instrument-channel map to copy. The API and bundle audit leaves
the private instrument mapping unobserved. The current PyPI release is
Perceval 1.3.1; its release notes identify a local asynchronous deep-copy fix,
rather than an Ascella instrument-configuration remedy.

The current [Cloud API](https://api.cloud.quandela.com/openapi.json)
`JobCreate` schema accepts a job name, payload, maximum duration, Perceval
version, platform and process identities. The current processor record lists
two platform parameters: `final_mode_number` and the legacy
`use_photon_recycling`. Neither interface documents a hardware configuration
write or an input-port instrument map.

Perceval 1.3.1's `PlatformSpecs.parameters` describes the advertised
parameters as the supported `RemoteComputer.set_parameters()` keys.
`RemoteComputer.prepare_payload()` serializes the computation, mitigation
request, platform parameters and custom noise. `RPCBasedCommunicationLayer.send()`
serializes that payload and creates the Cloud job. Those client operations
provide no documented `hardware_info.circuit_input_ports` setter.
The [vendor compilation guide](../notes/quandela/guide/user-guide/04-compilation.md)
documents input-state routing, unitary transpilation and detection setup;
pre-compilation reuses `computed_input` and `computed_circuit`, rather than
provisioning physical source channels.

The provider-configuration hypothesis predicts that an operator inspecting
Ascella's deployed configuration will find a missing physical input-port map.
Restoring that map under the deployment's own configuration schema and loading
the corrected configuration should permit the minimal sampling request.
The physical instrument channel
names and configuration schema remain provider-owned unknowns. The published
mode indices `[0, 2, 4, 6, 8, 10]` identify legal optical inputs; they do not
specify instrument channels. A client must not fabricate that map or inject
an undocumented `hardware_config` field into jobs.

An instrument-level causal trace needs the retained job IDs, terminal
timestamps, exact error, source occupations and minimal static circuit.
Ascella reports hardware-core 3.9.3, mosaiq-arcturus 2.1.5.1.post2,
pcvl-worker 2.1.1 and universalchipworker 2.1.3. The local client versions
are Perceval 1.3.1 and exqalibur 1.4.2. Unobserved causal inputs include the
deployed configuration and worker revision that handled each job and the
mapping the worker loaded. A successful sampling job must demonstrate recovery. The Cloud
portal's public `available` flag remains weaker evidence than that acquisition.

## First-principles measurement model

For one photon on connected input s, an ideal unitary U gives output
probability `p(r|s,U) = |U[r,s]|^2`. Real observations combine input loss,
the implemented mesh, output efficiency, detector background and filtering.
Conditioning on detection removes the common loss scale. Conditional output
counts alone therefore cannot calibrate absolute transmission or distinguish
all source and detector efficiencies. The collector retains reported shots,
physical and logical performance, filtering and scheduler metadata alongside
counts. Published output-transmission entries above 100 percent remain
unqualified calibration metadata.

Phase requires recombination: a phase shift on a directly counted mode leaves
its intensity unchanged. Two-path preparations and output recombination with
four quadratures distinguish real and imaginary coherence. Two-photon
interference requires permanents and explicit threshold-event aggregation;
one-photon propagation cannot qualify indistinguishability. The advertised
`support_multi_photon=false` remains a recorded constraint whose precise
semantics require SDK and provider-contract qualification. Prospective
multi-photon requests use distinct connected sources and require fresh SDK
validation. Threshold clicks cannot recover every output occupation when
photons collide.

## Finite capability frontier

The finite tests below cover declared discretizations of a continuous device.
The Cartesian product of every continuous phase, dwell, circuit and policy
has an unbounded denominator and remains outside a completeness claim.

| Mechanism | Finite denominator | Observable and falsifier | Admission dependency |
|---|---|---|---|
| Instrument readiness | one static native 12-mode request | completed acquisition with positive counts; an instrument error rejects readiness | provider configuration recovery |
| Input/output transfer | 6 sources x 12 routed outputs = 72 settings | conditional transfer and outside-target counts; wrong output labels reject routing | readiness and input identities |
| Single-photon phase response | 6 sources x 66 output pairs x 4 quadratures = 1584 settings | recombined quadrature contrast; phase-independent output rejects the intended interference | transfer and coherent reference synthesis |
| Two-photon interference | 15 distinct source pairs, matched interfering/distinguishable controls | threshold-conditioned coincidence law; scalar independent-photon law is the null | single-photon transfer and processing semantics |
| Photon-order scaling | 63 nonempty subsets of 6 connected sources, orders 1 through 6 | accepted-event rate and detector occupancy; undefined rate or unmodeled collisions reject attribution | source, threshold and timing qualification |
| Compilation response | matched requested operators at declared seeds | returned circuit and output differences; unequal meshes limit drift attribution | complete parameter echoes and mesh receipts |
| Processing policy | explicit empty policy first; separately qualified named mitigations | counts and acceptance before/after policy; absent provenance rejects raw-hardware interpretation | supported mitigation semantics and cost quote |
| Dynamic operator sequence | 17 wave times, 5 free references, 2 representative controls | measured probability evolution; omitted times reject sequence completeness | operator pilot and complete counts |
| Temporal response | repeated matched requests with bracketing references | differences against acquisition order; changed mesh or processing blocks pure-drift attribution | timestamps, seeds and returned circuits |
| Model reconstruction | specified identifiable intensity or PSD model | held-out residuals, solver status and uncertainty; fit failure preserves residuals | sufficient measurement rank and accepted observation law |

The current client supports sequences of parameter settings, inputs and seeds
across acquisitions. Those sequences are dynamic experiments. The retained
Ascella contract establishes neither adaptive mid-shot feed-forward nor pulse
control, so the programme makes neither claim.

The generated [finite frontier](../../results/hypercomplex/photonic-successors/ascella-capability-frontier/frontier.json)
enumerates all 1656 transfer and recombined-phase declarations with unique
source/output/quadrature identities. It also enumerates all 63 nonempty
connected-source subsets. Six photons in twelve modes have 12376 Fock
occupations, whereas threshold detection with one through six clicks has
2509 patterns. These are different observable denominators; a detector click
pattern does not recover every photon occupation. The declared rows retain
`awaiting-instrument-and-timing-admission` and remain distinct from acquisitions.

## Packing and resource accounting

The Explorer per-job maximum is 300 seconds. A job stops at its duration,
sample or shot limit; more iterations do not extend the duration. The measured
iterated tariff is `1 + 0.000001 * largest_iteration_max_shots`, not a flat
one-credit unlimited computation. A static job bills the shots used under
the measured rule. Shared circuit structure, photon filter and processing
policy define a packable job. Incompatible filters or policies require
separate jobs. Every cap and price receives a fresh read-only check.

Ascella's per-setting overhead remains unmeasured because the tested jobs
failed before acquisition. Belenos timing cannot establish Ascella timing.
A successful small acquisition must measure compilation/setup overhead and
sampling rate before a 300-second pack is sized. Packing maximizes informative
completed observations per credit subject to that measured envelope. A partial
answer remains partial and cannot qualify a full finite frontier.

The approved Belenos repeat programme has five jobs, each capped at 180
seconds, 196608 samples, 393216 total shots and 1.016384 credits. The programme
contains 120 settings and has aggregate caps 983040 samples, 1966080 shots,
900 seconds and 5.081920 credits. The static Ascella readiness cap is 1024
samples, 2048 shots, 180 seconds and 1.002048 credits. The existing eight-setting
order pilot remains distinct. Expanded Ascella spending and each newly frozen
case require an explicit bounded authorization record.

## Belenos acquisitions and stage attribution

All five approved jobs completed on 22 October 2026:

| Case | Job | Settings | Samples | Execution seconds | Credits |
|---|---|---:|---:|---:|---:|
| Order, three repeat blocks | `da95ea91-f2c3-4587-9b38-bb789b9689fe` | 24 | 196608 | 151 | 1.016384 |
| Wave, repeat zero | `753ddf1c-18b6-4182-ba89-0a7fb2f6d784` | 24 | 196608 | 144 | 1.016384 |
| Wave, repeat one | `a593971c-8ddb-4906-892d-cee42626482b` | 24 | 196608 | 144 | 1.016384 |
| Wave, repeat two | `acc5bb38-eae4-4568-9324-8473a608905b` | 24 | 196608 | 144 | 1.016384 |
| Fourier, three repeat blocks | `e99c049c-b9c1-4663-bbd0-e57e59bb6993` | 24 | 196608 | 141 | 1.016384 |
| Total | five jobs | 120 | 983040 | 724 | 5.081920 |

The [conditional readout](../../results/hypercomplex/belenos-repeat-readout-pooled.json)
binds every case, circuit, submission, sent body, result and raw result by
digest. All requested parameter echoes and compilation seeds match. Of the
983040 returned samples, 350 are vacuum or multiple-click outcomes and remain
explicitly excluded from the one-click denominator. The 120 matched-repeat
pair comparisons have maximum conditional total variation 0.036181. Every
matched pair carries identical returned compiled-circuit bytes; physical
heater states and calibration-event identity remain unobserved.

The [compiled-mesh audit](../../results/hypercomplex/belenos-compilation-measurement-audit-pooled.json)
uses the bounded protobuf decoder and the repository's Rx convention to
propagate the returned `computed_input` through every numerical mesh. The
largest compiled-versus-requested intensity total variation is 0.000210.
Both returned optical representations, `computed_circuit` and
`computed_experiment`, agree on the tested mesh components. Every field sent
in each job payload matches its returned job-data field; the service adds
`pcvl_version` to that returned payload.

The imaginary-superposition Fourier control on representative zero instead
has measured-versus-compiled total variation 0.996336, 0.997313 and 0.996946
in its three repeats. Its declared ideal probabilities are 1/4, 1/2, 1/4
on even modes 0, 2 and 4. The measured mass instead lies mainly on odd modes
1, 3 and 7. The computed input remains source zero and the returned meshes
predict the intended even-mode distribution. The same measured distributions
are only 0.030785, 0.034049 and 0.033190 from the preceding real-superposition
representative-one mesh prediction.

```mermaid
flowchart LR
    A[Bound request and parameter echo] --> B[Returned numerical mesh]
    B --> C[Applied controls and count association: unobserved]
    C --> D[Retained detector counts]
```

The acquisition and metadata paths are operational. The compiled-intensity
agreement does not qualify the applied operation. A preceding-configuration
or result-association defect is a falsifiable candidate: holding the target
and compilation seed fixed while changing its immediate predecessor should
change the bad target's output if the response follows that predecessor.
A stable setting-specific response predicts a target-associated failure
under those permutations. The existing fixed-order repeats cannot separate
these mechanisms. The next diagnostic case must cross predecessor identity,
target identity, order and a static target control, preserve all returned
meshes and outputs, and retain the same empty processing policy. The approved
five-job ceiling is consumed; that intervention remains an unsubmitted design.

Gate `core-633` replays the descriptive readout and returned-mesh audit.
The [pooled readout producer](../../scripts/photonic_repeat_readout_pooled.py)
and [compiled-mesh producer](../../scripts/photonic_compilation_audit_pooled.py)
validate independent acquisition directories through
`parallel.ordered_map`. Their successor records preserve every scientific
observation and comparison from the serial records. The original producers
and their hash-bound outputs remain immutable historical evidence.
Gate `core-632` replays the frozen successor cases, finite frontier and API
contracts.
The successor replay reads
`results/hypercomplex/photonic-successors/native-target-catalogue.json`, a
frozen planning snapshot, rather than the refreshed live catalogue. Replay
validates historical case bytes; a submission still refreshes live constraints.
Local hardware-independent regressions cover static templates,
failed-result retention, budget mutation, API reference defects and mesh
propagation. The initial full behavioral run reproduced a main-branch failure
in `test_toolchain_successor_preserves_original_rows_and_covers_current_cases`.
The active Quantum Inspire record omitted 60 retained cases whose original
compilation evidence remained available. A complete retained-case successor
restores that coverage. The offline regression checks every original and
rejected-request predecessor row and the complete current case set. The
predecessor compilation records keep their bytes.

## Library use and independence

The [347-distribution inventory](../state/hypercomplex-libraries/libraries.md)
is the finite library denominator. A distribution's presence establishes
neither applicability nor execution. Perceval/exqalibur validate photonic
circuits and provide SLOS/Naive references; NumPy and SciPy compute transfer
laws, propagation, permanent references and numerical residuals; SymPy,
python-flint, gmpy2 and mpmath provide exact or precision controls. The existing
algebra certificates retain cd_core and qualified Cayley-Dickson witnesses.
NetworkX/rustworkx can check connectivity; pandas/xarray retain labeled joins;
Matplotlib renders measured quantities. CVXPY with qualified SCS or Clarabel
can enforce a stated PSD reconstruction, subject to model rank, solver status
and residual checks. OSQP's linear-constraint quadratic model does not replace
a PSD solver. Qiskit/Aer and tensor libraries supply optional complex-encoding
cross-checks, not independent photonic hardware evidence. Provider SDK,
notebook, packaging and documentation dependencies keep their declared
infrastructure roles. Libraries with explicit skip decisions retain them.

The existing inventory check, exact operator certificate, full-operator
template validation and new static/failed-result regressions are independent
gates on their named surfaces. A library-by-library execution ledger must
distinguish used, locally qualified, infrastructure, deferred and incompatible;
an import count cannot stand in for that ledger.
