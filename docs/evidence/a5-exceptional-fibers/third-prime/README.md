# Quadric rings at a third prime: the test of ledger row A5-548

Ledger row A5-548 states the hypothesis that a quadric ring k[y]/K2 of the fiber track is Cohen-Macaulay exactly when
K2 is radical, and that where it is not, the defect is a nilradical module of rank one over a smaller cone. The rings
at 32009 and 32029 fit it; this directory regenerates the rings at a third prime and decides both properties there.
Row A5-556 records the result: the hypothesis survives at p = 32057.

## Prime, headers and relation files

The prime is the first prime p = 1 mod 4 above 32029, `fiber_inputs.find_split_prime(32030, 1)` = (32057, 8059), with
8059 the smaller square root of -1. From the repository root:

```sh
"$PYTHON" docs/evidence/a5-kernel-attachments/fiber_inputs.py emit --prime 32057 --root 8059 \
  --slug xm-nm --slug xp-np --slug e8-vb --slug iso-nm --slug e8-nm --slug e8-np --slug w8-nm \
  --out docs/evidence/a5-exceptional-fibers/third-prime/inputs
"$PYTHON" docs/evidence/a5-kernel-attachments/fiber_cone_driver.py --header \
  docs/evidence/a5-exceptional-fibers/third-prime/inputs/p32057-r8059/SLUG.sing --degree 2 \
  --out docs/evidence/a5-exceptional-fibers/third-prime/relations/SLUG/d2 --prime 32057 --memory-gib 4 --timeout 1800
```

`emit` writes the headers of [inputs/p32057-r8059/](inputs/p32057-r8059/) with their receipt; each header has the
variables of its 32009 counterpart. The survivor cache that `emit` computes beside them equals
`../working/build/inputs/survivors/` file for file, so it is not retained. The driver calibrates: on
`p32009-r10754/xm-nm.sing` it rewrites the retained `a5-xm-d4/xm_p1/d2/relations-upto-d2.rel` byte for byte
(sha256 `596c48a7...`). Every cell at 32057 is `degree-certified`:

| Slug | Fiber | Generators | Degree-2 relations | Wall time |
|---|---|---|---|---|
| `xm-nm` | X- -> N- | 15 | 69 | 60 s |
| `xp-np` | X+ -> N+ | 15 | 69 | 13 s |
| `e8-vb` | E8-bar -> VB | 10 | 21 | 8 s |
| `iso-nm` | Iso -> N- | 17 | 68 | 14 s |
| `e8-nm` | E8-bar -> N- | 21 | 148 | 1 h 59 min |
| `w8-nm` | W8 -> N- | 24 | 144 | 1 h 52 min |

E8-bar -> N+ is the image of E8-bar -> N- under the sign automorphism of A5-013 (generator by generator over Q(i),
A5-024), whose coordinate change y_i -> c_i y_i carries K2, its radical and its colon ideals, so it is not run; X+ ->
N+ runs as a control of that transport and agrees with X- -> N- in every value.

The two long cells ran on the build host as user services under `MemoryMax` 22 GiB (E8-bar, driver budget 20 GiB) and
14 GiB (W8, driver budget 12 GiB), swap off, one Singular process each, after a written estimate of about two hours
from the retained receipts (W8 6,560 s products stage on this host, E8-bar 12,600 s on a Kaggle CPU at about half
this host's speed). Falsifier: a ring at 32057 that is reduced and not Cohen-Macaulay, or nonreduced and
Cohen-Macaulay. This case was written into the record after the launch. Measured peak resident set: 1.4 GB (E8-bar)
and 2.0 GB (W8). The products files `sq.txt` and `nf-d2.txt` of these two cells (166 and 39 MB, 209 and 61 MB) are
retained for analysis. Each file above 50 MB is split into 45 MiB parts `FILE.part00`, `FILE.part01`, ..., as in
`working/` (`../README.md`), and `cat FILE.part* > FILE` restores it; the 39 MB `e8-nm/d2/nf-d2.txt` stays whole. Each
`receipt-d2.json` binds `nf-d2.txt` by `normal_form_sha256`. The `pr.yml` checkouts skip these blobs, since no check
reads them. The sha256 of each restored file is:

| File | Parts | sha256 |
|---|---|---|
| `relations/e8-nm/d2/sq.txt` | 4 | `eab34c94fe0c04ff561e24f4a82552f0ae35b2f752f4c2f7ef2a4ba413b3d999` |
| `relations/w8-nm/d2/sq.txt` | 5 | `802ff19b125a50736c028068d4bf95d492e68a1d77a967d7f9e2cc68a5a859fb` |
| `relations/e8-nm/d2/nf-d2.txt` | whole | `f3308fcfb504d1b50d4e57fb07062b86aa3bce184ddbce1ff9c42b378ba16e5f` |
| `relations/w8-nm/d2/nf-d2.txt` | 2 | `669d5215dd4b89bf6f02c7eef051d7cd97e23da36b9b64acb9eb2948a9923ac7` |

The relation files the test reads are retained whole.

## The test

[quadric_rings.py](quadric_rings.py) decides, per ring: Cohen-Macaulay by `k2_cm.test` unchanged; nonreduced by a
nonzero linear part N of the radical with N^2 in K2; reduced, for a Cohen-Macaulay ring, by a chart of a linear
section whose multiplication matrix has a squarefree characteristic polynomial, lifted along the regular sequence (the
module docstring carries the argument). It then runs the `x-colon`, `e8-colon` and `vb-components` rows of
[quadric_and_germ_probes.py](../structure/quadric_and_germ_probes.py) on the new files and judges them with that
module's `check`.

`quadric_rings.py --calibrate` runs the same verdicts on five retained 32009 cells whose answers the ledger proves
(A5-010, A5-019, A5-058, A5-061, A5-303, A5-312) and exits 1 on a departure; [calibration-p32009.json](calibration-p32009.json)
is its record, with every answer reproduced. Those five cells never make the chart withhold a verdict: the chart is
squarefree on all of them, nonreduced ones included, since only the Cohen-Macaulay gate lets the chart decide. The
chart's known-bad input is therefore a sixth cell, [calibration/double-plane.rel](calibration/double-plane.rel):
K = (y1^2) in three variables, Cohen-Macaulay and not reduced, whose chart has no squarefree base, so the ring
stays undecided with the nilpotent probe off; a chart that accepted it would fail the calibration. The predictions were recorded in [predictions.md](predictions.md) before
any relation file at 32057 existed, with one labeled correction of three mislabeled counts.

## Result

[quadric-rings-p32057.json](quadric-rings-p32057.json), 44 s:

| Fiber | Krull dimension | Degree | Length | h-vector | Cohen-Macaulay | Reduced |
|---|---|---|---|---|---|---|
| X- -> N- | 4 | 12 | 15 | 1, 11, 3 | no | no (3 nilpotent linear forms) |
| X+ -> N+ | 4 | 12 | 15 | 1, 11, 3 | no | no (3 nilpotent linear forms) |
| E8-bar -> VB | 4 | 7 | 7 | 1, 6 | yes | yes |
| Iso | 5 | 23 | 23 | 1, 12, 10 | yes | yes |
| E8-bar -> N- | 5 | 11 | 20 | 1, 16, 3 | no | no (5 nilpotent linear forms) |
| W8 -> N- | 6 | 50 | 50 | 1, 18, 27, 4 | yes | yes |

Every value equals the 32009 and 32029 value and the recorded prediction. The defect probes pass unchanged: for
same-sign X, A = K2 : P is the plane of 12 linear forms and K2 : A = P; for E8-bar -> N-, R = K2 + N with five forms,
N^2 in K2, A = K2 : R a prime quadric cone of dimension 4, K2 : A = R and the Hilbert identity; for E8-bar -> VB, two
linearly joined primes meeting in one reduced plane. Three primes decide nothing about a fourth prime or about
characteristic 0; the next test is the same program over Q(i) on the weight-slice relations of A5-474.

Replay: `"$PYTHON" docs/evidence/a5-exceptional-fibers/third-prime/quadric_rings.py OUT.json` (Singular 4.4.1,
python-flint 0.9.0).
