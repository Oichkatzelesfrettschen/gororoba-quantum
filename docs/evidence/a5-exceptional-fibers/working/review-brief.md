# Review brief: the executed fiber plan and its results so far

Review adversarially; read only, and return findings as your final message. Read in this order:
`purpose.md` (target object), `first-principles-plan.md` and `codex-consult-v2.md` (the two consultant reports),
`decision-record.md` (the reconciliation, falsifiers F1-F7, steps S0-S7, results, section 6 strategy, section 7
host memory incident). Every run's input, log and normal-form file is under `runs/<job>/`; the templates are
`templates/a2_body.sing` (method A degree 2) and `templates/b_body.sing` (method B, pivot saturation); the rank and
relation helpers are `probes/rank_nf.py` and `probes/relations_nf.py`; the symmetry checks are `runs/s0/` and
`runs/s0b/`.

Answer:
1. Is every reported number (h_d, V(K2) dimension and degree, symmetry signs, span rank 41 for E8-bar N+ vs N-)
   supported by the cited log or file? Name any claim the files do not support.
2. Is method A as coded exactly the degree-d piece of F(I) (membership in J + m*P_d in a global ordering, products
   reduced mod J, Nakayama normal monomials from the previous degree)? Look for a code-level defect: products
   built from kbase leading exponents, `rank_nf.py` parsing of Singular output (signs, coefficients, `^`), the left
   kernel in `relations_nf.py`.
3. Is method B as coded the special fiber F(I) (pivot nonzerodivisor test, sat(H, g), adding the source variables)?
   Does the template's localization at the origin match the local ring A_m, or can a component of the Rees algebra
   away from the origin enter the fiber computed by setting t = 0 globally?
4. Do the conclusions follow: "no cubic relations beyond K2" from h3 = number of normal cubics; X+ from X- by the
   sign substitution; W8 N+ from W8 N- likewise; E8-bar N- distinct from N+ by span rank 41?
5. What should change in the remaining plan (S2 X- method B timed out at 3 h with 6.9G; Iso method B, E8-bar and
   W8 degree 3, VM 2 method B on E8-bar then W8, VM 1 E8-bar N- A and B, second-prime check), ranked by expected
   value per compute-hour? Is any completion certificate cheaper than full saturation?
Cite file:line for every claim.
