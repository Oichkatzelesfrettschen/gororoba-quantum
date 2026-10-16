# Cubic normal form of the dim-32 associator phases

`normal_form.json` is the output of `scripts/associator_cubic_normal_form.py`
(gate core-278). Every degree-3 associator phase at dim 32 is a product of
three independent linear forms plus a quadratic, so one CCZ between CNOT
networks implements its cubic part; the file records the forms and the
compiled CZ counts of the factorized, Reed-Muller and normal-form circuits
for all 360 pairs.

The two notebooks here predate that check. Their resource and fidelity
figures are estimates rather than compiled counts, and their equivalence
tests do not involve an associator circuit;
`docs/evidence/simulation-notebook-audit/README.md` gives the reading of
each against its retained Kaggle log.

`independent_package/` holds a certificate package built with its own
Cayley-Dickson product and Boolean code; gate core-284 requires its shipped
certificates to agree with `normal_form.json` on the cubic part and the
linear forms of all 360 pairs.
