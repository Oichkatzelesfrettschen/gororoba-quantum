# Destination-response acquisition provenance and upstream request

The [nominal-one acquisition report](../../evidence/tuna-projector-geometry/nominal-one-destination-response.md)
records three complete Tuna-17 jobs and bounded equivalence of the selected response cells. The early and
terminal labels still disagree strongly on declared qubit 11. The available account interfaces expose the
submitted sources and binary outcomes; the inspected routes supplied neither served acquisition settings
nor analog IQ. Those observations leave the physical cause unresolved.

The [contact-route audit](upstream-readout-report.md#verified-contact-routes) owns verified upstream addresses
and software issue trackers. The requests below remain local and unsent.

## What the read-only audit found

The [artifact observations](../../evidence/tuna-projector-geometry/destination-job-artifact-observations.json)
cover the three nominal-zero jobs 1618109, 1618345, 1618590 and the three nominal-one jobs 1620359, 1620485,
1620614. Every returned source digest matches its retained manifest.

| Evidence surface | Measured result | Interpretation boundary |
|---|---|---|
| `/files/{job.file_id}` | Six matching sources; `compile_stage=none`; empty `compile_properties` | Establishes stored-input identity at readback, rather than the served pulse or acquisition program |
| `/files?commit_id=…&generated=true` | Each scoped query returned zero generated siblings | Served lowering artifacts remain unavailable through those queries |
| `/final_results/job/{job_id}` | All six payloads contain exactly execution seconds, requested/done shots, histogram and binary raw data | The [equivalence check](../../evidence/tuna-projector-geometry/destination-final-result-equivalence.json) confirms the same ordered raw lists and result values already retained; the endpoint adds neither IQ nor settings |
| `/metadata/backend/7` | HTTP 404 with `Not Found` | Physical backend 7 is the observed Tuna instance; endpoint availability differs from installed-client support |
| Live `/openapi.json` | 53 paths; zero metadata routes | The [served-API observation](../../evidence/tuna-projector-geometry/destination-served-api-observation.json) distinguishes the accessible service from client 0.64.0's generated metadata methods |
| `/jobs/1620359/logs` | One time-filtered, 20-entry request reached its 10-second read timeout | The [bounded probe](../../evidence/tuna-projector-geometry/destination-job-log-observation.json) establishes availability failure for that request; the documented route concerns hybrid-job logs |

The [runtime observation](../../evidence/tuna-projector-geometry/destination-one-runtime.json) records SDK
4.2.0 and generated client 0.64.0. The client's metadata method addresses a physical backend, despite a
misleading job-ID description in its generated documentation. Backend metadata would still require an
explicit job/configuration association before qualifying as calibration for a particular acquisition.
The measured route failure does not establish whether QI retains the requested data internally.

## Calibration datasource diagnosis

The [post-acquisition connectivity receipt](../../evidence/tuna-projector-geometry/destination-one-calibration-connectivity.json)
records another failed MCP query for the public Tuna readout-error panel. Grafana's request to
`https://prometheus.qi2.qutech.support/api/v1/query` failed while dialing TCP address
`131.180.205.138:443`. A direct local read-only probe resolved the same address and timed out after
5.004992 seconds, with an HTTP status of `000` and zero recorded connection time.

The failure precedes HTTP and therefore precedes transmission of a Mozilla or other HTTP User-Agent.
The provider operator needs to check the configured endpoint, listener, DNS, routing and firewall from
Grafana's runtime. The observations identify the failed connection boundary; they leave the exact network
or service fault unresolved.

The [version-scope observation](../../evidence/tuna-projector-geometry/destination-prometheus-version-scope.json)
records public upstream release `v3.15.1`, published on 2026-10-21. The local `pacman -Q prometheus` lookup
reported that package absent, and the executable lookup found no `prometheus` on PATH. Those measured local
surfaces differ from the provider deployment. Installing a local server would leave the provider's
Grafana-to-Prometheus connection unchanged. The remote Prometheus version remains unmeasured.

## What can resolve the measurement ambiguity

The [instrument diagnosis](../../evidence/tuna-projector-geometry/readout-cause-diagnosis.md) separates physical
transitions, readout context, thresholding and classical reconstruction. The new nominal-one comparison
certifies only the selected realized predictable response contrasts. In its three jobs, declared qubit 11
has early-one counts 1320/1404/1361 and terminal-one counts 3794/3763/3745, each out of 4096. Binary labels
alone cannot identify which stage produced that discrepancy.

A useful request asks for the smallest sufficient trace before requesting a large waveform export:

1. **Association trace.** For every early and terminal event, provide physical qubit, acquisition channel,
   acquisition index/bin, shot index and reconstructed classical destination, plus compiler, exporter,
   controller and reconstruction version/configuration identities.
2. **Pre-packing binary labels.** If analog IQ was discarded, retained discriminated labels indexed by
   acquisition and shot can still test whether classical reconstruction associates the right events.
3. **Integrated IQ and discriminator.** Retained complex points, rotation, threshold and calibration identity
   permit an offline threshold/reconstruction replay. Raw ADC waveforms and the integration kernel become
   necessary when the question concerns integration itself.
4. **Served schedule.** Readout-pulse and acquisition-window starts/ends, units, multiplexing, reset and
   repetition timing distinguish scheduling/context from reconstruction. The public 300 ns readout notice
   does not independently specify those intervals.

A classical renaming provides an exact software test. With unused early destinations cyclically renamed
and the physical instruction stream fixed, a correct classical reconstruction must permute the output
labels correspondingly. Repacking one retained acquisition trace under all six permutations of three
destinations can test that property without another quantum execution. A transformation confined to early
labels preserves every terminal marginal. The older nominal-zero qubit-6 terminal contrast therefore
survives any such relabeling, while its destination attribution remains temporally confounded.

The two preparation cases occurred hours apart, and monitoring reported benchmarking while the final
nominal-one job waited. The baseline screen bounds its selected endpoint contrasts; it does not establish
equal served configurations or exclude a transient during the rotated job. A preparation-dependent physical
effect remains unqualified.

## Unsent private support request

**To:** support@quantum-inspire.com  
**Subject:** Tuna-17 repeated-readout provenance: six retained destination controls and missing acquisition artifacts

Six completed Tuna-17 jobs requested 4096 shots each. They nominally prepare all 17 qubits in zero or one,
measure q4/q11/q6 early into three auxiliary destinations, then measure all qubits terminally into bits
0 through 16. The rotated source changes only early destinations 17/18/19 to 19/17/18. Every returned
width-20 raw string is retained, and the stored source bytes match.

The nominal-zero jobs are 1618109, 1618345, 1618590. Their enclosing six-job case stopped on its request
deadline and retains an unavailable primary endpoint. Its descriptive qubit-6 terminal-one contrast is
0.3836669921875. The separately approved nominal-one jobs are 1620359, 1620485, 1620614. Their frozen
12-cell comparison establishes bounded predictable-response equivalence within 0.10 under its simultaneous
99% bound. Early/terminal disagreement on declared qubit 11 remains approximately two thirds of shots.
These are binary response statements, rather than calibrated populations or a causal destination effect.

Please provide the association trace, pre-packing labels, retained IQ/discriminator configuration and served
schedule described above, where available. Please identify which configuration served each job. Monitoring
reported `benchmarking` at 23:57:46 UTC on 2026-10-27 and 00:08:19 UTC on 2026-10-28, then `executing` at
00:16:19 UTC. Job 1620614 reached `queued_at` at 00:20:03.610042 UTC after a 32 minute 16.258985 second
creation-to-queue interval. Did that service interval change any settings served to the final repeat?

The file queries return no generated siblings or compile properties. The final-result endpoint reproduces
the existing binary results. Installed generated client 0.64.0 documents `/metadata/backend/{backend_id}`,
but the live service's 53-path OpenAPI omits metadata routes and `/metadata/backend/7` returns 404.
Please identify the supported account route or an export mechanism for per-job acquisition provenance.

The public Grafana readout query also fails to connect to `prometheus.qi2.qutech.support:443`. Please check
that datasource connection and clarify whether the public readout duration of 300 ns describes the pulse,
integration window or another interval. The report attributes the response to no particular software or
physical defect; the requested evidence would localize the failure stage without another QPU run.

## Public software issue routing

A public SDK issue can report the client-0.64.0 metadata method, the official host, HTTP 404 and the served
OpenAPI route inventory without account identifiers or completed-job traces. The
[verified SDK tracker](upstream-readout-report.md#verified-contact-routes) is the starting point for that
deployment/documentation discrepancy. The provider support route remains the first contact for private
served settings, acquisition traces and datasource operation.

A separate QX issue should ask about the returned per-qubit last-measurement register versus the classical
register, using the existing [QX contract report](upstream-readout-report.md#unsent-qx-contract-report).
QX terminal conformance does not validate Tuna early-history output. A new OpenSquirrel or Quantify issue
requires an exported, localized reproducer; the historical acquisition-index bug alone does not identify
the served Tuna cause.

Further hardware requires a new written case and approval. That case must account for the observed
1936.258985-second wait, the recorded benchmarking interval, fresh queue conditions, complete-job rules
and the chosen stopping horizon. Independently assigned or counterbalanced job blocks can address some
temporal confounding, but shots within one job do not supply additional intervention assignments and
randomization alone does not remove apparatus carryover.
