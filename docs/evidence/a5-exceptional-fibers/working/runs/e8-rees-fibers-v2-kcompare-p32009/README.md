# Quadric-ideal comparison of the v2 Rees runs with the weight-slice producer

The runs of `../e8-rees-fibers-v2-p32009/` decide the fiber ideal L of three weight-slice cells modulo p = 32009 (root of
-1 = 10754) by comparing it with the quadric ideal K that each script builds from its own degree-2 relations. This directory
decides, in Singular 4.4.1, that each script's K is the ideal of the relations that `weight_slice_fiber_relations.py`
regenerates for the same cell, and measures how those weight-slice relations sit against the header-slice relation sets K2 of
A5-570. The ledger rows are A5-579 to A5-581 (the K equalities), A5-582 (the span measurement) and A5-583 (the open hypothesis).

## Result

| Cell | Script (sha256 in its log) | Producer relation digest | Script K | Producer K | Mutual remainders | Drop control | Added-monomial control | Wall time, memory |
|---|---|---|---|---|---|---|---|---|
| E8-bar -> N- | `e8-nm-p.v2-u-full` | `42b1d8ff03d4c505597b39fe303c52ac45fcdc4d35bbf01d0b8e7e23a97367d0` (the record cell) | 148 generators, dim 5, mult 11 | the same | 0 and 0 | unequal | unequal | 23 s, 74 MB |
| E8-bar -> N+ | `e8-np-p.v2-u-full` | `b9b7372bce35e7ce286aa572f9b1ebf656d1ac04ba0e63349c640efed88658ee` (no record cell, A5-577) | 148 generators, dim 5, mult 11 | the same | 0 and 0 | unequal | unequal | 23 s, 74 MB |
| Iso -> N- | `iso-nm-p.v2-u-full` | `4b9f84948f9ffa00f5e735ccc8943b6be0b7afc4a932f8a3c600b92b6e3e99c5` (no record cell, A5-577) | 68 generators, dim 5, mult 23 | the same | 0 and 0 | unequal | unequal | 5 s, 34 MB |

- The comparison script `kcmp-CELL.sing` is the run script cut before its Rees stage, followed by `kcompare-tail.sing`; the
  cut keeps the run's own ring, relations and K, so K is the object that the run's `FIBER outside_K` and
  `K_outside_fiber` counts refer to. Equality is both remainders zero (each generator set reduced modulo a standard basis of the
  other) with equal numbers of minimal generators.
- A known-bad control must come out unequal before the verdict counts: the producer relations without their first relation
  (K does not reduce to zero modulo the 147 that remain) and the producer relations with the first quadratic monomial outside K
  added (the enlarged ideal does not reduce to zero modulo K). `kcompare.done` holds the verdict lines that the scripts
  print, `KCMP RESULT cell NAME equal 1 control_drop_unequal 1 control_added_unequal 1` for each cell.
- `kcompare.py prepare` regenerates the producer relations (one Singular process per cell) and stops unless the relation
  count, the generator count and the relation digest equal those of the run's own `REL` lines; the digest of the N- cell also
  occurs in `weight-slice-fiber-relations-result.json`. The producer's Singular is the installed 4.4.1 of the comparison.

## Span of the weight-slice relations against the header slice

`SPAN` lines compare the 148 weight-slice relations K with the header-slice relation set K2 over the same variables y(1..21)
(N-: `working/distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel`, sha256
`e047f996ad609a40ca9d65a64cb7f28755cbaeea3013a9ada7ff71e76e708de6`; N+: `working/runs/e8_a2/e8_k2.rel`, sha256
`bbe9bb734af739d735ca4ca4938b85fce9ed87c07b7373ec5353c47335be0652`, the K2 file of A5-570). Both sets have rank 148 with
dimension 5 and multiplicity 11. The supports are 207 monomials (weight slice) and 217 (header slice). The union has rank 223 at
N- and 224 at N+, so the spans meet in dimension 73 and 72; the header relations reduce to nonzero remainders modulo K for 134
and 133 of the 148 relations. The two quadric ideals are not equal in these coordinates (A5-582). No file of this directory
or of `../e8-rees-fibers-v2-p32009/` writes out a linear change of the 21 generators that relates them, so the hypothesis of
that README that the two slices differ by a linear change of coordinates stays open (A5-583); the closing computation is
named in that row.

## Files

| File | Content |
|---|---|
| `kcompare.py` | `prepare`: regenerates the producer relations, checks their digests, writes `KA-CELL.sing`, `KH-CELL.sing` and `kcmp-CELL.sing`, prints the support and union-rank lines |
| `kcompare-tail.sing` | the Singular comparison, controls and verdict lines appended to each cut run script |
| `run_kcompare.sh` | the launcher: one Singular process per cell in turn, tool version and script digest at the top of each log, a timing file, an `EXIT` line, and `kcompare.done` as the completion marker |
| `KA-CELL.sing` | the producer relations as an ideal in y(1..g) |
| `KH-CELL.sing` | the header-slice relation file as an ideal (N- and N+ of E8-bar) |
| `kcmp-CELL.sing`, `kcmp-CELL.log`, `kcmp-CELL.time` | the comparison script, its Singular output and the `/usr/bin/time -v` record |
| `prepare.log` | the output of `kcompare.py prepare` (the `TIE` and `SPAN` lines) |
| `kcompare.done` | one verdict block per cell and the line `KCOMPARE ALL DONE` |
| `sha256.txt` | sha256 of every retained file |

## Replay

From this directory, with the producer's Python dependencies and Singular 4.4.1 on the path, `python -B kcompare.py prepare`
rewrites the `KA`, `KH` and `kcmp` files and `sh run_kcompare.sh Singular 3000 e8-nm e8-np iso-nm` runs the comparison (under a
minute); the launcher refuses to overwrite a log. The banner line of every retained log of the v2 runs, of their replay and of
these comparison logs reads `Singular for x86_64-Linux version 4.4.1 (44105, 64 bit) Dec  6 2025 11:10:58`.

## Scope

Three cells at one prime and one root of -1, one execution each. The comparison decides that the scripts' K and the producer's
relation ideal are one ideal; it does not run the Rees stage again (A5-578) and leaves the second prime and root open (A5-576).
