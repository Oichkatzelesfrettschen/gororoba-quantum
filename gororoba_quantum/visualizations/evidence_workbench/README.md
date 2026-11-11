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
python -B -m unittest discover -s tests/gororoba_quantum -p test_evidence_workbench.py
python -B -O -m unittest discover -s tests/gororoba_quantum -p test_evidence_workbench.py
node tests/visualizations/test_evidence_math.cjs
```

Normal repository CI remains the code-admission authority. Behavioral fixtures
remain visibly synthetic. The optional input-packaging workflow copies public
retained files into a short-lived artifact; it does not execute or adjudicate
their scientific analyses.
