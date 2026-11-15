# Codex review of pull request 924

Reviewer: `codex exec`, model `gpt-daybreak-blue-latest`, reasoning effort high, read-only sandbox, codex-cli 0.169.0,
2026-11-15, on [brief.md](brief.md) at head `efb66aa0a`. Paths are relative to this repository; a
`gororoba-infrastructure:` prefix names a path in that private repository. The text below is the reviewer's answer, with each file link written as `path:line` at that head.

## Findings

1. SERIOUS — proved: the history contract fails on allowed Grafana frame shapes. `scripts/qi_monitoring.py:163` emits `None` timestamps when a frame has no time field. `scripts/qi_status.py:165` retains `[None, value]`, while `gororoba-infrastructure:broker/publish_qi_status.py:48` calls `.replace()` on that timestamp and aborts publication. `transitions()` also preserves unsorted stamps and multiple values at one stamp; `gororoba-infrastructure:broker/publish_qi_status.py:52` rejects every stamp not later than the preceding row, silently losing changes. Normalize and validate timestamps, sort them, define last-value-wins semantics for duplicates, and test no-time, unsorted, duplicate, and null frames.

2. SERIOUS — proved/measured: raw error text violates the publication boundary. `scripts/qi_status.py:85` and `scripts/qi_status.py:207` copy exception and datasource text without redaction. The retained document contains a raw IPv4 address at `docs/evidence/quantum_inspire/status-sources-2026-11-15/status-document.json:362`, and the calibration record begins repeating it at `docs/evidence/quantum_inspire/status-sources-2026-11-15/calibration-panel-observation.json:21`. A token- or identifier-bearing exception would travel through the same path. Publish structured error classes and HTTP status only; retain sensitive transport detail outside the public repository.

3. SERIOUS — proved: “each section fails alone” is false for malformed provider bodies. `READ_ERRORS` at `scripts/qi_status.py:78` excludes `AttributeError`; non-mapping results, targets, messages, or panels reach `.get()` at lines 94, 148, 158, and 162 and escape `document()`. Requests transport exceptions are covered because `RequestException` inherits `IOError`, and JSON decoding is covered by `ValueError`. `StopIteration` has no production path here, and the `[-1]` reads are guarded against empty lists. Validate external shapes and convert violations into the section’s domain error instead of broadly catching programming errors.

4. SERIOUS — proved contract defect: nullable producer fields become false zeroes in the dashboard. Queue fields are written with `.get()` at `scripts/qi_status.py:111`, but `gororoba-infrastructure:dashboard/infra.html:306` applies `Number(null)`, displaying missing counts or waits as zero. Likewise `scripts/qi_status.py:244` permits a null latest calibration value, and `gororoba-infrastructure:dashboard/infra.html:321` renders it as `0.00`. The consumers read no wholly absent field, but they assume numeric types the producer does not guarantee.

5. MODERATE — proved: “every request is a read” omits OAuth refresh traffic. Normal execution constructs `Client` at `scripts/qi_status.py:291`; its constructor calls `refresh()` and may exchange and persist a rotated refresh token at `scripts/qi_platform.py:330`. The application-data requests are read-only, but the complete request path is not. The module docstring and `docs/evidence/quantum_inspire/status-sources-2026-11-15/README.md:4` need that narrower wording. `--public-only` correctly bypasses `Client`, and `qi_status.py` makes no direct SDK-auth call.

6. MODERATE — computed/measured: the link-burst measurement is misstated. `scripts/qi_status.py:16` and `docs/evidence/quantum_inspire/status-sources-2026-11-15/README.md:11` say 20 requests. `jq` computed 23 entries from `docs/evidence/quantum_inspire/status-sources-2026-11-15/link-burst-observation.json:5`: four redirects and nineteen HTTP 428 responses. The retained time-range evidence does support the docstring’s 1-hour, 24-hour, and 720-hour range statement.

7. MODERATE — proved: the retained evidence does not establish that the OpenAPI definition lists no calibration route. `docs/evidence/quantum_inspire/status-sources-2026-11-15/README.md:32` makes that claim, but `docs/evidence/quantum_inspire/status-sources-2026-11-15/api-route-observation.json:54` retains selected schema fields rather than the OpenAPI path inventory. The evidence proves only that the probed `/metadata/backend/7` route returned 404 and the retained backend-type fields contain no calibration figure.

## Claim disposition

1. Falsified literally; application-data traffic is read-only, OAuth refresh traffic is omitted.
2. Confirmed: no direct auth-manager access, and `--public-only` constructs no `Client`.
3. Falsified by uncaught `AttributeError` paths.
4. Confirmed: each `definition_of()` performs one `resolve()`; the exact five-dashboard sequence is tested.
5. Falsified for no-time, unsorted, and duplicate timestamps.
6. Confirmed for the retained classifications: Tuna-17 and Tuna-9 `datasource-error`, Tuna-5 `http-error`, Ry emulator `no-panels`. A mixed error-plus-data answer becomes `data`; that is consistent with “any data,” though it discards partial-failure detail.
7. The retained document contains no token or team/member/user field, confirmed by an exact key scan. The general guarantee is falsified by unsanitized error text.
8. Confirmed for identical selected JSON and changes to selected fields: `sort_keys=True` is deterministic and topology is included. The test covers only a gate-set change; reordered lists can change the digest without a semantic change.
9. Falsified by the 23-versus-20 count and the unretained OpenAPI-path assertion. The queue, heartbeat, state-change, panel-count, and reach statements match the retained files.

## Tests and conjecture

Computed: Python 3.14.9 with pytest 9.2.0 ran the two permitted files from `/tmp`; all 12 tests passed in 0.26 seconds. `git diff --check origin/main...qi-status-document` passed, and the worktree remained clean. The tests contain no wrong assertion found, but omit every failing shape identified above.

Hypothesis: the strongest dropped status signal is provider drain/deployment state. The retained schema exposes `enabled`, `pending_jobs`, `running_jobs`, and `safe_to_deploy` at `docs/evidence/quantum_inspire/status-sources-2026-11-15/api-route-observation.json:109`. The measured account received HTTP 403 from `/drain_mode`, so that signal is currently unavailable rather than safely collectible.
