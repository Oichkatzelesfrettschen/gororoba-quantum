# Tuna projector geometry: source and availability observations

The [design and bounded acquisition case](../../design/tuna-projector-geometry.md) owns the proposed experiment.
These observations were read on 27 October 2026; status and calibration availability may subsequently change.

- `backend-observation.json`: authenticated read-only MCP backend/instance/queue observation; Tuna-17 executing,
  enabled, fresh heartbeat, zero account-queued jobs. No job was created.
- `dashboard-observation.json`: public Grafana definition, version 28, updated 26 October; its dated notices
  withhold current performance data and state a 300 ns readout duration from 23 May 2026.
- `direct-readout-query.json`: independent requests call to public Grafana panel 11, HTTP 400; query A reports
  downstream 502 and a TCP timeout from Grafana to the calibration Prometheus datasource.
- `browser-readout-query.json`: same request with a Mozilla/Firefox User-Agent, Origin and Referer headers;
  same downstream 502 after 10.54 seconds. A browser User-Agent does not remedy the observed failure.

The independent direct compute-API read at 15:38:18 UTC also reported executing and enabled, fresh heartbeat,
and zero account-queued jobs. The MCP T1 panel 3 repeated the calibration datasource timeout. Grafana's status
panel 1 succeeded at 15:45:17 UTC and reported Tuna-17 idle, showing that the public dashboard query route works
and that backend status changes between reads. A direct unauthenticated request to the disclosed calibration
Prometheus query endpoint timed out connecting after six seconds. No server-side configuration was accessible.
Five focused `tests/scripts/test_qi_monitoring.py` tests passed under the pinned interpreter.

The fault is bounded to the observed calibration datasource reachability, not authenticated compute reads,
MCP transport, dashboard token resolution, or every Grafana datasource. The exact upstream network or service
failure needs provider-side logs. Retrying through the compute API cannot supply absent calibration fields:
the retained OpenAPI route inventory contains backend/status routes and no calibration/performance route.

## Community CLI assessment

`https://github.com/DeadmanXXXII/Inspire`, inspected at commit `40301831dac2d804bf692061c27c434be870332f`, contains
only `README.md` and `LICENSE.md` (MIT). Its last push is dated 5 September 2024. It supplies illustrative SDK
commands, not an installable CLI. The installed stack is quantuminspire 4.1.0, qiskit-quantuminspire 0.18.5,
OpenSquirrel 0.9.1, libqasm 1.2.1 and qxelarator 0.10.0. Its `quantuminspire.qiskit` module and
`quantuminspire.api.QuantumInspireAPI` class are absent from that installed stack. Its README offers no
calibration retrieval method. Nothing was installed or configured from that repository.

Use the existing guarded `qi_platform.py` for future submissions and collections. Direct read-only API access
is an available diagnostic route; it does not bypass provider admission, calibration uncertainty or queue rules.

## Datasource connection boundary

The follow-up `datasource-connectivity.json` records the 15:52:45 UTC observation.
Grafana's public `/api/health` returned HTTP 200, database `ok`, version 13.1.1,
and commit `e784b7782a43822971f896b3377dc736346a9c66`. The public dashboard definition
assigns both panel 3 (T1) and panel 11 (readout error) to the Prometheus datasource
`prometheus-qi2-monitoring`. DNS resolves its hostname to 131.180.205.138.
A direct HTTPS request to Prometheus's documented `/-/ready` endpoint timed out
establishing a connection after six seconds.

The failed operation is TCP connection establishment. The observed provider error
precedes a TLS handshake, HTTP authentication, PromQL evaluation, and result parsing.
A firewall drop, unavailable listener or host, routing problem, or stale destination
can produce the symptom; these public observations do not distinguish those causes.
The provider operator must test the configured destination from Grafana's own runtime,
inspect routing and firewall policy, confirm the HTTPS listener and reverse proxy,
and then check Prometheus readiness and query logs. A connection failure from the
workstation corroborates public unreachability but does not measure Grafana's network path.

Pacman found neither `prometheus`, `grafana`, nor `python-prometheus-client` installed.
The Quantum Inspire environment has requests 2.34.2 and lacks `prometheus-client`.
The monitoring adapter uses requests against public Grafana endpoints; a local
Prometheus server or instrumentation client is unnecessary for that interface.
Installing either locally would leave the provider-side destination unchanged.

## Upstream versions and matching failure mechanisms

Public upstream reads completed at 15:53:40 UTC on 27 October 2026. GitHub's latest
stable releases were [Grafana 13.3.0](https://github.com/grafana/grafana/releases/tag/v13.3.0)
(published 27 October at 11:08:50 UTC),
[Prometheus 3.15.1](https://github.com/prometheus/prometheus/releases/tag/v3.15.1)
(published 21 October at 16:15:57 UTC), and the
[Prometheus Python client 0.26.0](https://github.com/prometheus/client_python/releases/tag/v0.26.0)
(published 24 July). The provider Grafana health observation above reports 13.1.1.
The provider's Prometheus version remains unknown: Grafana health reports its own
version, and the Prometheus connection failed before a version response could arrive.
An available upstream release establishes an update candidate, rather than a repair
for the observed connection failure.

Grafana's [Prometheus troubleshooting guide at 13.3.0](https://github.com/grafana/grafana/blob/v13.3.0/docs/sources/datasources/prometheus/troubleshooting/index.md)
places connection diagnosis between the Grafana server and Prometheus: configured
URL and port, running service, routing and firewall policy. Its
[datasource configuration guide](https://github.com/grafana/grafana/blob/v13.3.0/docs/sources/datasources/prometheus/configure/_index.md)
distinguishes the HTTP timeout from the Prometheus query timeout. Increasing a query
budget or simplifying PromQL does not directly repair a failed TCP connection.
The [externally shared dashboard contract](https://github.com/grafana/grafana/blob/v13.3.0/docs/sources/visualizations/dashboards/share-dashboards-panels/shared-dashboards.md)
allows read-only execution of stored dashboard queries, confirms Prometheus support,
and excludes arbitrary queries through the public share. These observations used
that public boundary. The [Python client's instrumentation documentation](https://github.com/prometheus/client_python/tree/v0.26.0/docs/content/instrumenting)
describes application metrics such as counters and gauges; that package is separate
from the requests-based reader used here.

Two open upstream reports describe adjacent mechanisms, rather than an identified
cause at QuTech:

- [Grafana issue 132154](https://github.com/grafana/grafana/issues/132154), updated
  9 September 2026, requests datasource transport renewal for DNS-based failover.
  Its reported mechanism reuses an established connection to an unhealthy target;
  the observed QuTech error instead reports a failed TCP dial. Provider transport
  and DNS evidence would be needed to connect the two.
- [Grafana issue 121272](https://github.com/grafana/grafana/issues/121272), updated
  25 September 2026, reports mixed-datasource public dashboards failing after
  12.4.1 to 12.4.2 with `datasource ... was not found`. That error differs from
  the resolved-destination connection timeout observed on provider Grafana 13.1.1.

The inspected release notes and these issue reports establish neither the provider's
Prometheus deployment version nor a version-specific remedy. Provider network and
service diagnostics remain the decisive next evidence.

## Offline circuit verification

`local-verification.json` binds the producer and focused test inputs to the observed
30 passing tests. The [compiler receipt](../../../results/quantum_inspire/proposals/tuna-projector-geometry/local-compiler-receipt.json)
records six local OpenSquirrel compilations with identical per-qubit measurement,
barrier and wait sequences. The topology regression rejects the absent 10-11 edge;
the generated middle data-ancilla-data triple is 13-11-14. Local compilation verifies
compiler acceptance and retained control sequences; remote execution remains a
separate conformance obligation. The [written case](../../design/tuna-projector-geometry.md)
freezes finite-shot QX discrepancy tolerances before acquisition.

## Hardware qualification result

The [Tuna register qualification](tuna-qualification.md) completed all 12,288 shots but
failed its frozen contrast and early/final consistency screens. The record preserves the
refusal, source-grounded diagnostic alternatives and the boundary on successor acquisition.
