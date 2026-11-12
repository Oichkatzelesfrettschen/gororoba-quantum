# Offline quantum evidence workbench

This successor adds same-PUB dependence, returned-shot block inspection,
validated rank-sector normalization, separately retained optical cohorts,
and uncertainty-aware partial-qubit compatibility. It does not replace or
rewrite the retained Ramsey viewer, the earlier external atlas, or the
original measured-ripple explorer.

The [runbook](../../../docs/runbooks/evidence-workbench.md) defines commands,
verification levels, assumptions, tests, and remaining admission requirements.
The [reader](../../evidence_workbench.py) owns input validation; the
[builder](../../../scripts/render_evidence_workbench.py) creates a new
standalone HTML file with all selected data embedded.

## Components

- `math.js`: pure coordinate bounds, disk-constrained likelihood, compatible
  Z sets, contingency interpretation and rational display factors.
- `app.js`: seven linked inspection workspaces, native selection controls,
  model separation, exports, and source-bound view persistence.
- `template.html` and `style.css`: offline semantic layout, chart-first mobile
  flow, accessible tables and explicit control labels.

Run bounded numerical checks without any retained acquisition or provider:

```sh
"$PYTHON" -B -m unittest discover -s tests/gororoba_quantum -p test_evidence_workbench.py
"$PYTHON" -B -O -m unittest discover -s tests/gororoba_quantum -p test_evidence_workbench.py
node tests/visualizations/test_evidence_math.cjs
```

Normal repository CI remains the code-admission authority. Behavioral fixtures
remain visibly synthetic. `tests/visualizations/test_evidence_math_node.py` runs
the Node checks inside the pytest suite where Node is installed.

## Browser payload admission

The browser verifies SHA-256 before parsing or rendering the embedded bundle.
Controls remain disabled during admission. A missing digest, mismatched bytes,
malformed JSON, duplicate object key, exceeded allocation bound, or unsupported
bundle envelope withholds the figure and displays an error. Parsed containers
are frozen recursively; ordinary API consumers cannot change retained data.

The renderer's HTML escapes for `<`, `>` and `&` are reversed at JSON token
boundaries. Number spelling, escaped backslashes, whitespace and the final
newline remain unchanged. Hashing a parsed-and-reserialized JavaScript object
would not reproduce Python's `1.0`, `-0.0` and exponent spellings. The bundle
JSON export therefore uses the verified original text and matches the displayed
digest byte for byte.

WebCrypto supplies SHA-256 where available. The bounded portable implementation
supports offline documents without that API. An available WebCrypto operation
that fails causes refusal; its error is not silently replaced by a fallback.
Admission limits are 64 MiB of transport text and recovered UTF-8 bytes, 128
container levels, and one million JSON values. These are whole-bundle limits,
not an assurance that every combination of individually valid source files fits.

Identity is not authenticity: editing both a payload and its declared digest
is outside this check. The source-bound Python builder still owns scientific
schema validation, count conservation, source verification and raw replay.
Runtime hashing does not certify QPY semantics, apparatus behavior, or inference
assumptions. The strict parser and digest helpers are pure functions in
`math.js`; no provider or network access is introduced.

The Node suite includes deterministic standard/differential SHA-256 checks,
Python-style number spellings, HTML-escape round trips, prototype-looking keys,
immutable data, parser budgets, and mutation refusals through both digest paths.
The existing browser checker remains an on-demand check; its browser dependencies
are not added to normal CI by this change.
