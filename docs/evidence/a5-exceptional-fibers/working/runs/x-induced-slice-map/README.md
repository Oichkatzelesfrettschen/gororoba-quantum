# The map that the slice change induces on the fiber cone of same-sign X, over Q(i)

Ledger rows A5-638 and A5-640 hold the module map of the nilradical of the quadric ring of X- -> N- and X+ -> N+ on
the header slices and on the weight slice, in unrelated generator coordinates. This directory computes the linear map
between the two sets of 15 generators that the change of slice induces, over Q(i), and checks its reductions against
every retained header relation file of same-sign X (ledger row A5-644). The comparison of the module maps under it
is `slice_module_map_comparison.py --family x` of the
[kernel-attachment evidence](../../../../a5-kernel-attachments/README.md) (A5-645).

## Mechanism

The construction is the one of [the E8-bar directory](../e8-induced-slice-map/README.md) (A5-598), whose README holds
the argument: where the two pivot Pfaffians are units, the header-frame and the weight-frame families of 126
principal 4-Pfaffians generate one ideal I, and the header frame's selected Pfaffians, restricted to the weight
slice, are constant combinations of the weight-slice generators modulo J + m I. `x_induced_slice_map.py` imports the
Singular stages, the header frame and the readers of `induced_slice_map.py` and replaces what names the source: the
closure equations of X- or X+ (`xm`, `xp` of the weight-slice producer), the 15 header generators of the incidence in
`nullity16-rees-fibers-result.json`, and the counts 15, 69, dimension 4 and multiplicity 12, read from the count
table of the weight-slice producer and from the nullity-8 import record. That E8-bar README states that the X cells
need no map for the fiber cone itself, which the header slice decides over Q(i) (A5-270, A5-305); the map here serves
the comparison of the module maps.

## Result

| Cell | Header Pfaffians in the span | Map | Weight relations over Q(i) |
|---|---|---|---|
| X- -> N- | 15 of 15, residual 0 | 15 x 15 over Q(i), constant entries, invertible | 69, digest of the retained record |
| X+ -> N+ | 15 of 15, residual 0 | 15 x 15 over Q(i), constant entries, invertible | 69, digest of the retained record |

The header Pfaffians reach weight 29 and the weight-slice generators weight 9; the part of weight above 9 of every
header Pfaffian lies in J + m I by an untruncated standard basis (`header_high_weight_outside 0`). Reduced at a prime
and a root of -1, the transported ideal equals the retained header ideal in both directions:

| Cell | Prime, root | Header relation file | Transported modulo header, header modulo transported | Controls (identity; one entry raised; header generators 1 and 2 swapped) | Other root |
|---|---|---|---|---|---|
| X- -> N- | 32009, 10754 | `a5-xm-d4/xm_p1` | 0, 0 | 55, 55; 2, 4; 45, 34 | 21255: 35, 31 |
| X- -> N- | 32029, 9115 | `a5-p2-small/xm_p2` | 0, 0 | 55, 55; 2, 4; 45, 34 | 22914: 35, 31 |
| X- -> N- | 32057, 8059 | `third-prime/relations/xm-nm` | 0, 0 | 55, 55; 2, 4; 45, 34 | 23998: 35, 31 |
| X+ -> N+ | 32009, 10754 | `a5-xp-p1-d2/xp_p1` | 0, 0 | 55, 55; 2, 4; 45, 34 | 21255: 35, 31 |
| X+ -> N+ | 32029, 9115 | `a5-p2-small/xp_p2` | 0, 0 | 55, 55; 2, 4; 45, 34 | 22914: 35, 31 |
| X+ -> N+ | 32057, 8059 | `third-prime/relations/xp-np` | 0, 0 | 55, 55; 2, 4; 45, 34 | 23998: 35, 31 |

Each check also reads 69 minimal generators, dimension 4, multiplicity 12 and a nonzero determinant. The last column
is the reduction of the same Q(i) record at the other root of -1 of the prime, which leaves 35 and 31 nonzero
remainders: each header file fixes its root, and a record that passed at both roots would not test the imaginary
parts of the map. A polynomial outside I (the first header Pfaffian plus s2) leaves a nonzero residual against the
span.

## Scope

- The six header relation files were computed by engines that never saw this map, at three primes.
- The two cells are one line of evidence at each prime, three in all. `witnesses.jsonl` of the fiber evidence holds a
  sign isomorphism from the X- header presentation to the X+ one (the flip of t9, with signs on the generators), and
  the reduction logs of the two cells agree byte for byte at each prime while their scripts differ.
  `hypothesis:` the opposite signs of the module-map scalar of A5-645 on the two cells follow from that isomorphism;
  the test is to transport the X- module maps by it and compare.
- The reductions compare ideals. That G is the induced map, and not another equivalence of the two ideals, rests on
  the deduction of the E8-bar README, which is prose.
- Same-sign X only. Opposite-sign X has 3 generators and no relation, and W8 and Iso are not run.

## Replay

    PYTHON=python3 sh docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/run_x_induced.sh

from the repository root, with Singular on PATH and sympy and python-flint in that interpreter. The driver calls
`x_induced_slice_map.py --run`, which sends the six Q(i) scripts and then the twelve reductions through
`parallel.ordered_map`, and exits nonzero unless both records pass their internal checks, all six reductions print
`INDUCED VERDICT ... PASS` and all six reductions at the other root print `FAIL` with nonzero remainders in both
directions. The retained run used Singular 4.4.1 and Python 3.14.7 on an x86-64 Linux host: 11 s in all on its workers and 22 s on one, 89 MiB at the peak, with the same bytes in every retained file.
`tests/test_a5_x_induced_slice_map.py` reads the retained records, logs and digest list.

| File | Content |
|---|---|
| `x_induced_slice_map.py` | script generator (`--emit`), record builder (`--collect`), reduction check (`--check`) and the whole run (`--run`) |
| `run_x_induced.sh` | the replay command: `x_induced_slice_map.py --run` |
| `map-SOURCE-qi.sing`, `.log` | the induced map over Q(i) |
| `relations-SOURCE-qi.sing`, `.log` | the weight-slice producer's script for the cell and its 69 relations |
| `high-SOURCE-qi.sing`, `.log` | the membership test of the high-weight parts of the header Pfaffians |
| `induced-SOURCE.json` | the record: map, relations, selections, digests, verdict |
| `check-SOURCE-pPRIME-rROOT.sing`, `.log` | one reduction check |
| `control-SOURCE-pPRIME-rROOT.sing`, `.log` | one reduction at the other root, which must fail |
| `sha256.txt` | sha256 of every other file of this directory |
