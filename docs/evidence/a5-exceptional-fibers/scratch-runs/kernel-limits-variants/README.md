# kernel-limits-variants

Class: code copy with a difference (the scripts produced the outputs of `../kl`, `../kl-out`, `../kl-pole`, `../kl-iso`, `../kl-w8`, `../kl-xs`, `../fpm`, `../fpm2`, `../vb-special` on the compute workstation).

Each file sits at the repository-relative path it had in its checkout, under the checkout's directory: `gq-repo/` (the checkout at a5 kernel-limits commit ac6ef083f, whose copy of `vb_limit_span.py` was untracked there) and `gq-main/` (a checkout of main whose working tree held three modified scripts). The tracked scripts of `../../kernel-limits/` on main are the later versions; these files stay here beside the outputs they made and replace nothing.

| File | Relation to the tracked file on main |
|---|---|
| `gq-repo/docs/evidence/a5-exceptional-fibers/kernel-limits/vb_limit_span.py` | differs from the tracked script (30 differing lines in a diff against it) |
| `gq-main/docs/evidence/a5-exceptional-fibers/kernel-limits/plucker_limits.py` | older docstring: ledger rows A5-272 and A5-275 only; lacks the A5-292 families |
| `gq-main/docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py` | lacks the provenance block (`file_digests`, `input_files`, `plucker_subsets`, `map_provenance`) of the tracked script |
| `gq-main/docs/evidence/a5-exceptional-fibers/kernel-limits/vb_special_arcs.py` | older docstring on the sign convention of the VB coordinate k0 |

The dirty copy of `vb_pole_arcs.py` and the six `monomial-ladder` scripts equal the tracked files and are not repeated. Their outputs are the files of the sibling directories named above. Host role: the compute workstation; dates 2026-11-10.
