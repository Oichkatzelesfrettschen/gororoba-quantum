# Brief: gororoba-quantum pull request 924, scripts/qi_status.py (Quantum Inspire status document)

Read first: the workspace AGENTS.md, then AGENTS.md and scripts/AGENTS.md.
Work read-only: change no file; never commit, push, stash, submit to a provider or start a cloud resource; spawn no
subagents. Send no request to quantum-inspire.com, qutech.support or any other network host: the link service limits
bursts and the retained files below hold the answers. You may run git, and python3 with pytest on the two test
files; keep each computation under 5 minutes, in a scratch directory outside every repository.

Material: worktree the gororoba-quantum worktree, branch qi-status-document; the change is `git diff origin/main...qi-status-document`.
Files: scripts/qi_status.py, tests/scripts/test_qi_status.py, docs/evidence/quantum_inspire/status-sources-2026-11-15/.
Context it imports and must not change: scripts/qi_monitoring.py (sha256-pinned by
docs/evidence/tuna-projector-geometry/local-verification.json), scripts/qi_platform.py (class Client).
Consumer, for the contract only: gororoba-infrastructure:broker/publish_qi_status.py and gororoba-infrastructure:dashboard/infra.html (function qi).

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. Every request qi_status.py can send is a read: GET on the compute API, GET on the link service and Grafana
   definition, and POST only to a public dashboard's stored panel query. Status: by inspection. Support:
   scripts/qi_status.py account(), _panel(). Falsifier: a code path that reaches client.post, client.patch or a
   mutating route.
2. No code path of qi_status.py exchanges the OAuth refresh token except through qi_platform.Client's own refresh.
   Status: by inspection. Falsifier: a direct call into the SDK's auth manager, or a path that builds a Client when
   main() was given --public-only.
3. A section that fails leaves the others readable. Status: tested. Support: test_sections_fail_alone. Falsifier: an
   exception class a real failure raises that READ_ERRORS does not catch and that escapes document() (consider
   requests exceptions, json decoding, AttributeError on an unexpected body shape, StopIteration, IndexError).
4. The link service receives exactly one request per dashboard per document() call. Status: tested. Support:
   test_document_asks_the_link_service_once_per_dashboard_and_stops_at_a_dead_datasource. Falsifier: a second
   resolve() reachable from document().
5. transitions() and the history it feeds are correct for the frames Grafana returns, including null values,
   unsorted or duplicate stamps and a frame with no time field. Status: partly tested. Falsifier: an input shape
   in the retained status-document.json or allowed by qi_monitoring.series() that yields a wrong row.
6. _reach() classifies the retained answers as the README states: Tuna-17 and Tuna-9 datasource-error, Tuna-5
   http-error, Ry emulator no-panels. Status: measured. Support: calibration-panel-observation.json and
   status-document.json in the evidence directory. Falsifier: a retained answer the function classifies otherwise,
   or a mixed answer (one reference errors, one returns data) it mislabels.
7. The document carries no team, member or user identifier and no token. Status: by inspection. Falsifier: a field
   of the API responses copied through TYPE_FIELDS, LIMIT_FIELDS, QUEUE_FIELDS, _instance or an error text.
8. definition_sha256 is stable across runs for an unchanged backend type and changes when its gate set or topology
   changes. Status: tested for the gate set. Falsifier: a source of nondeterminism in the digest input.
9. The README's statements match the retained files beside it. Status: measured. Falsifier: any number or state in
   README.md that its JSON or text files contradict.

## Questions to answer

- Defects in code, tests, docstrings and the evidence README, each with file:line.
- Does any comment or docstring state a measurement the retained files do not support?
- Contract: does publish_qi_status.merge() or infra.html's qi() read a field qi_status.py does not write, or assume
  a type it does not guarantee?
- Conjecture: what further status signal do the retained API fields support that the document drops?

Report ranked by consequence, every finding tied to a file:line or a command with its output, each marked proved,
computed, measured or hypothesis. Print it as your answer, under 150 lines.
