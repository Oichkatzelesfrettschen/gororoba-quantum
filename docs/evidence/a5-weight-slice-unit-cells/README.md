# Weight-slice unit-replacement Rees fibers into N- at both roots of -1

A5-409 records that the header-slice elimination of `nullity16_rees_fibers.py` reached its 300 s limit on all ten
incidences into N+ and N-. A5-574 completes Iso -> N- by the unit-replacement route on the weight slice of A5-421,
in about 900 times less wall time, and replays X- -> N-.
[`scripts/a5_weight_slice_unit_cells.py`](../../../scripts/a5_weight_slice_unit_cells.py) extends that route to every
source into N- except E8-bar, at both roots of -1, under the A5-409 limits: a 300 s timeout and a 16 GiB address-space
limit per Singular process. Ledger row A5-675.

## Method

Each cell script is the retained
[`iso-nm-p.v2-u-full.sing`](../a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/README.md) with two
substitutions. The germ line `ideal J=` becomes the closure equations of the source pulled back to the N- weight slice,
taken from `weight_slice_fiber_relations.source_equations`. The root `number i=10754` becomes 21255 for the second
root. Every other line of the template runs unchanged: the Pfaffians, the Nakayama selection, the relations K, the unit
replacement with its certificate, the pivot, the satstd saturation, the colon loop, the fiber over the origin and the
L = K test.

## Result (Singular 4.4.1, compute workstation, two cells at a time)

| Cell | Root | Nakayama generators | Fiber ideal L: minimal generators, dim, mult | Status, wall |
|---|---|---|---|---|
| Iso -> N- | 10754 | 17 | 68, 5, 23 | done, 7.4 s |
| Iso -> N- | 21255 | 17 | 68, 5, 23 | done, 7.3 s |
| X- -> N- | 10754 | 15 | 69, 4, 12 | done, 5.9 s |
| X- -> N- | 21255 | 15 | 69, 4, 12 | done, 5.8 s |
| X+ -> N- | 10754 | 3 | 0, 3, 1 | done, 0.4 s |
| X+ -> N- | 21255 | 3 | 0, 3, 1 | done, 0.4 s |
| W8 -> N- | 10754 | 24 | not reached | timeout at 300 s |
| W8 -> N- | 21255 | 24 | not reached | timeout at 300 s |

Every finished cell prints `CERT unit_identity_bad 0`, `FIBER outside_K 0 K_outside_fiber 0` and no `CERT FAIL` line,
so its fiber ideal equals its quadric ideal K.

- The regenerated Iso and X- cells at root 10754 read the retained values of A5-574 (68, 5, 23) and (69, 4, 12). This
  is the control that the substitution reproduces the retained scripts.
- X+ -> N- has a zero fiber ideal in 3 variables, so its fiber cone is P^2. This agrees with the import of A5-416
  ("P^2 for opposite-sign X").
- The second root gives the same invariants on all three finished sources.
- W8 -> N- does not finish inside 300 s on this route either.

Not covered: the five incidences into N+, since the template carries only the N- slice matrix. E8-bar -> N+ and N-
are already completed by the same route in 11 to 14 h (A5-572, A5-573). W8 needs a longer limit or another
presentation.

## Control (`--self-test`)

The Iso cell with the X- germ equations in its J line leaves (68, 5, 23); it reads the X- values. A timed-out cell keeps
its status alone, since the output it printed before the limit depends on the host speed.

```sh
"$PYTHON" -B -W error scripts/a5_weight_slice_unit_cells.py --check docs/evidence/a5-weight-slice-unit-cells/result.json
```
