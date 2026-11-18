# Reconciliation of the review of pull request 924

One local reviewer ran, `codex` on `gpt-daybreak-blue-latest` at high effort ([codex-report.md](codex-report.md)); the
Advisor reviewed last. Each finding was checked against the source at head `efb66aa0a`.

| # | Finding | Check against the source | Outcome | Advisor |
|---|---|---|---|---|
| 1 | `transitions()` keeps unstamped, unsorted and duplicate points, and the consumer aborts on a null stamp | `qi_monitoring.series()` writes a null stamp for a frame with no time field | fixed: points are read in time order, unstamped and null ones are dropped, the last of several at one stamp stands; `test_transitions_order_points_and_drop_unstamped_or_null_ones` | confirmed, fix holds |
| 2 | error text is copied unredacted; the retained files hold a raw IPv4 address | `_error()` and `_reach()` copied the text | fixed: `redact()` on every error text, retained JSON rewritten; the address stays in commit `efb66aa0a` of this branch and stood on main before it, in `docs/evidence/tuna-projector-geometry/README.md` | confirmed, fix holds |
| 3 | `AttributeError` on a body of another shape escapes `document()` | `result.get` on a null result | fixed: `AttributeError` and `IndexError` join `READ_ERRORS`; the account section catches `Exception`, since the SDK's authorization error derives from it alone; two tests | confirmed; the Advisor added the authorization class |
| 4 | the page draws a missing queue count or calibration value as 0 | `Number(null)` in the consumer | fixed in gororoba-infrastructure | confirmed, fix holds |
| 5 | "every request is a read" omits the token exchange of `qi_platform.Client` | `Client.__init__` calls `refresh()` | fixed: docstring and evidence README narrowed | confirmed, fix holds |
| 6 | the link burst counted 23 requests, the text said 20 | `link-burst-observation.json`: 4 redirected, 19 refused | fixed | confirmed |
| 7 | the OpenAPI path list was not retained | `api-route-observation.json` held schema fields only | fixed: 53 paths and the digest of the served bytes retained | confirmed, fix holds |

Conjecture of the reviewer: the provider's drain state (`/drain_mode`) as a further status signal. The account
reads HTTP 403 on that route (`api-route-observation.json`), so the signal is closed to it.
