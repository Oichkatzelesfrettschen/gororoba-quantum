# Review of the slice comparison of the E8-bar module maps

The change adds `slice_module_map_comparison.py` to
[the kernel-attachment evidence](../../../evidence/a5-kernel-attachments/README.md) and ledger row A5-643 of
[ledger.tsv](../../../evidence/a5-exceptional-fibers/ledger.tsv). The Advisor read heads 7fbda52da and 3805a2b9b
before the hosted round; no command-line reviewer ran before this record was written.

## Findings and dispositions

| Finding | Disposition |
|---|---|
| Author, before any review: two of the three controls of the first run (y(1) added to the first image of G; header generators 1 and 2 exchanged) left the scalar unchanged | confirmed as invalid controls: the test reads G on the five coordinates of B_w and on the nilpotent forms alone, and neither change touches those; replaced by a perturbation of G on the leading variable of the first weight-slice image and by the exchange of two header coordinates of B_h, both of which find no scalar on every cell; the docstring and A5-643 state the limit |
| Advisor: the program solved both systems itself and read neither retained map, so the first scalar (-1) held for the program's own normalization only, and the sentence that the two retained maps are one intrinsic map was unsupported | fixed in 3805a2b9b: the header map keeps the normalization of A5-638 and the weight map that of A5-640; `problems()` requires the solved maps to equal `expected_map` of `quadric_and_germ_probes.py` and `images` of `weight_slice_module_map.py`; between the retained maps the scalar is i / 2 on all five cells |
| Advisor: the lint and types lanes reported the same file counts before and after the two new files, so they did not read them | confirmed: the lanes take evidence programs from a list; pinned ruff and mypy run on the two paths found one format change and one line over 120 columns, fixed in 77f5f0126 |
| Advisor: the README and A5-643 gave 17 s, the time of the first version | fixed in 0286ecf83: 25 s for the program, 19 s for the gate |
| Hosted Codex round on head de70d3a9b, P1: the five independent Singular runs execute one after another, against the rule that a CPU-bound loop over independent items uses `parallel.py` | fixed: `parallel.ordered_map(cell, CELLS, min_items=1)`, and the gate takes all workers; the record is reproduced with five workers (4.5 s) and with `GOROROBA_WORKERS=1` |
| Advisor: the identity is forced by A5-598 and the one-dimensional solution spaces, so the run is correlated with those rows | accepted: the docstring, the README and A5-643 call the run a confirmation and claim no independent evidence |

## Open

Same-sign X has no retained slice map; its module maps stay compared by invariants.