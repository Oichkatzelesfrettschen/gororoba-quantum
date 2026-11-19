# kernel-limits-variants

Class: code copy with a difference. The checkouts held these scripts when the `kl`, `fpm` and `vb-special` family scripts ran (the run scripts name the checkout directories `gq-repo`, `gq-main` and `gq-kl`; `kl-rerun.sh` ran from `gq-kl`, which is not preserved, and `fpm2` result JSONs equal tracked files).

Each file sits at the repository-relative path it had in its checkout, under the checkout's directory: `gq-repo/` (the checkout at a5 kernel-limits commit ac6ef083f, whose copy of `vb_limit_span.py` was untracked there) and `gq-main/` (a checkout of main whose working tree held three modified scripts). The tracked scripts of `../../kernel-limits/` on main differ and, in the three diffs read, are the refactored or extended versions (`vb_limit_span.py` on main takes `SLUG` and `limits.e8_phi` and maps its slices through `parallel.ordered_map`; the gq-repo copy inlines the arc formula); these files stay here beside the outputs they made and replace nothing.

| File | Relation to the tracked file on main |
|---|---|
| `gq-repo/docs/evidence/a5-exceptional-fibers/kernel-limits/vb_limit_span.py` | differs from the tracked script (30 differing lines in a diff against it) |
| `gq-main/docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py` | older docstring: ledger rows A5-272 and A5-275 only; lacks the A5-292 families |
| `gq-main/docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py` | lacks the provenance block (`file_digests`, `input_files`, `plucker_subsets`, `map_provenance`) of the tracked script |
| `gq-main/docs/evidence/a5-exceptional-fibers/kernel-limits/vb_special_arcs.py` | older docstring on the sign convention of the VB coordinate k0 |

The dirty copy of `vb_pole_arcs.py` and the six `monomial-ladder` scripts equal the tracked files and are not repeated. The outputs of the runs that used them are the files of the sibling directories named above. Generator and command: none; these files are scripts, not outputs, and the commands that ran them are recorded in the run scripts of the sibling families (`kl-rerun.sh` and the `fpm` and `vb-special` drivers). Host role: the compute workstation; dates 2026-11-10.
