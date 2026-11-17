# Modular Rees fiber certificates of E8-bar and Iso at p = 32009

This directory retains four Singular runs that compute the defining ideal of a fiber cone as the special fiber of a
saturated Rees ideal, on the weight slice of the nullity-8 closures (nine slice coordinates s1 to s9 with torus weights
1, 0, 3, 2, 2, 1, 4, 4, 3; ledger A5-421) modulo p = 32009 with the root of -1 equal to 10754. The ledger rows
A5-572 to A5-575 state the results and A5-576 to A5-578 state what remains open. The two E8-bar runs at (32009, 10754) test the prediction that A5-457 recorded on
2026-11-14 for the direct Rees runs: the fiber cone of E8-bar has dimension 5, multiplicity 11 and 148 minimal
generators, all of degree 2. The third cell of that three-run falsifier, E8-bar -> N- at 32029, is not run (A5-576).

## Result

| Run (script `NAME.sing`) | Cell | Basis size | Leading terms with u | Colon iterations | Fiber ideal L | Wall time, memory |
|---|---|---|---|---|---|---|
| `e8-nm-p.v2-u-full` | E8-bar -> N- | 6,139 | 96 | 1 | 148 minimal generators of degree 2, dimension 5, multiplicity 11 | 13 h 41 min 54 s, 554 MB |
| `e8-np-p.v2-u-full` | E8-bar -> N+ | 5,955 | 95 | 1 | the same | 11 h 22 min 3 s, 527 MB |
| `e8-nm-p.v2-u-y2` | E8-bar -> N-, fiber ideal cut at degree 2 | 2,853 | 92 | 1 | 148 minimal generators of degree 2, dimension 5, multiplicity 11 | 15 min 40 s, 160 MB |
| `iso-nm-p.v2-u-full` | Iso -> N- | 398 | 3 | 0 | 68 minimal generators of degree 2, dimension 5, multiplicity 23 | 14.4 s, 34 MB |

- Every run prints `CERT unit_identity_bad 0 all_positive_degree 1`, `CERT pivot_nonzerodivisor_mod_J 1`,
  `CERT satstd_isSB 1`, `FIBER outside_K 0 K_outside_fiber 0` and `EXIT 0`, and no `CERT FAIL` line. Each wall time and
  memory is one process on one core (`NAME.time`); the four processes ran at once on one cloud VM.
- `FIBER outside_K 0` says that every minimal generator of the fiber ideal lies in the quadric ideal K of the run's own
  degree-2 relations (148 for E8-bar, 68 for Iso), and `K_outside_fiber 0` says that every quadric of K lies in the fiber
  ideal; the two inclusions give L = K. The bounded run keeps only the generators of L of degree at most 2.
- The E8-bar Hilbert numerators of the N- and N+ runs agree: 1, 0, -148, 1562, -8745, 32753, -89936, 190224, -319606,
  435500, -488280, 454948, -354354, 231126, -125840, 56672, -20763, 6028, -1332, 210, -21, 1. The numerator is divisible by
  (1 - t)^16 in 21 variables with cofactor 11 at t = 1, which is dimension 5 and multiplicity 11 (`check_rees_fibers.py`).
  The Iso numerator 1, 0, -68, 452, -1485, 2948, -3630, 2376, 231, -2200, 2376, -1420, 517, -108, 10 is divisible by
  (1 - t)^12 in 17 variables with cofactor 23.
- Ties to tracked bytes: the 148 relation lines of the N- run hash (sorted lines, the weight-slice producer's digest rule)
  to `42b1d8ff03d4c505597b39fe303c52ac45fcdc4d35bbf01d0b8e7e23a97367d0`, the digest of the E8bar -> N- cell modulo 32009
  in `docs/evidence/a5-kernel-attachments/weight-slice-fiber-relations-result.json`; the selected Pfaffians, generator
  weights and Hilbert numerator of both E8-bar runs equal that cell's, and the Iso numerator equals the record's Iso -> N-
  cell over Q(i). The record has no E8bar -> N+ cell modulo 32009, so the 148 N+ relation lines (digest
  `b9b7372bce35e7ce286aa572f9b1ebf656d1ac04ba0e63349c640efed88658ee`) are bound by this run alone (A5-577).
- The relation lines of these cells and the header-slice K2 of A5-570 do not match as spans over F_32009: both sides have
  rank 148 in the 21 variables y(1..21), and their supports hold 207 and 217 monomials (measured with this script's
  parsers on the relation files of the A5-570 receipt and of the retained N- degree-2 run, and on the run lines).
  hypothesis: the two slices of the germ give generators that differ by a linear change of coordinates, so the fiber
  cones agree in Hilbert numerator without agreeing coordinate by coordinate. A5-571 (second root of the header slice)
  is not affected.

## Mechanism

Each script builds the presolved germ ideal J and the 21 (Iso: 17) Nakayama generators G of the weight slice from the
nine-coordinate skew matrix, forms the degree-2 relations K, and then computes the Rees fiber:

1. Unit replacement: each generator G_a is divided by the polynomial c_a(s2) with c_a(0) nonzero that its terms share
   (a unit of the local ring at the origin), leaving g_a with G_a = (c_a(s2) / c_a(0)) g_a modulo J. The script checks the
   identity c_a(0) G_a - c_a g_a in J for every a (`unit_identity_bad 0`) and that every c_a has positive degree.
2. Pivot: the generator of least weight, G_p, is a nonzerodivisor modulo J (`CERT pivot_nonzerodivisor_mod_J 1`).
3. Saturation: H = J + the 2 x 2 minors y_a g_b - y_b g_a + (u - g_p) is saturated by u with `satstd` of
   `customstd.lib` under the weighted ordering `wp`, which gives a standard basis Q with H inside Q inside H : u^infinity
   (`CERT satstd_isSB 1`). A basis in which u divides no leading monomial satisfies Q : u = Q; when the count of leading
   terms with u is positive, the script replaces Q by std(Q : u) until Q : u lies in Q, and prints the iteration count.
4. Fiber: setting s = 0 and u = 0 in Q gives the ideal L of the fiber cone in y(1..g); the script prints its minimal
   generators, dimension, multiplicity and Hilbert numerator and compares L with K both ways.

## What the check decides

`check_rees_fibers.py` runs from this directory's parent `docs/evidence/a5-exceptional-fibers` as
`python -B working/runs/e8-rees-fibers-v2-p32009/check_rees_fibers.py` and runs no Singular. It verifies, for each log,
the Singular banner, the digest of the retained script on line 2, the single `EXIT 0`, the absence of failure lines,
every certificate line, the equality of the generator counts, dimension and multiplicity across the K and FIBER lines,
the degree of every generator, the linear independence of the relation lines over F_32009 and the Hilbert arithmetic; then
the ties to the weight-slice record listed above, the `sha256.txt` table, and the replay below. `--self-test` rejects 16
mutated copies of the Iso log (a nonzero `outside_K`, an `EXIT 1`, each certificate flag, a lost colon line, a changed
multiplicity, numerator or generator degree, a dropped or duplicated relation, a wrong script digest, a failure
line, and three truncations: a log cut before its FIBER lines with and without an appended `EXIT 0`, and a log without
its terminal FIBER line). Singular 4.4.1 exits 0 on SIGTERM (measured), so an `EXIT 0` alone does not show that a run
finished; `run2.sh` only records the exit status, wrapped in `timeout` (status 124 on its own timeout), and the check
is the reader that requires the FIBER lines. `tests/test_a5_rees_fibers_check.py` runs the same verdict on a constructed toy log in the default lane and the
retained logs under `pytest -m audit`.

## Replay on a second host

The replay ran on a second cloud VM with the same Singular banner (4.4.1, build of Dec  6 2025 11:10:58), from the retained scripts
`run2.sh` and `NAME.sing` (`replay/`): the Iso run (9.3 s) and the bounded E8-bar run (12 min 45 s) print logs equal to the retained logs line for line once the Singular timer at the end of each STAGE line and of the colon line is masked, and they write basis files with the original digests (`bases.sha256`: both Iso files and both bounded-run files). The X- -> N- script of the same family (69 relations; `replay/xm-nm-p.v2-u-full.sing`, 7.5 s) prints FIBER 69 minimal generators, dimension 4, multiplicity 12, outside_K 0 and K_outside_fiber 0, as A5-416 states for the same-sign threefold of degree 12; its control with generator 1 doubled (`replay/xm-nm-p.v2-u-full-badcontrol.sing`) prints outside_K 42 and K_outside_fiber 21, so the fiber comparison accepts the known-good script and rejects the known-bad one. `replay/ssi.sha256` lists the digests of every basis file the replay wrote, the X- pair included.

The two E8-bar full runs (13 h 42 min and 11 h 22 min) are not replayed (A5-578).

## Files

| File | Content |
|---|---|
| `NAME.sing` | the four Singular scripts, each self-contained (the skew 15 x 15 matrix of linear forms, the presolve, the relations and the Rees stage) |
| `run2.sh` | the launcher: one Singular process per script, tool version and script digest at the top of each log, a timing file and an `EXIT` line; it refuses to overwrite a log |
| `NAME.log`, `NAME.time` | the Singular output and the `/usr/bin/time -v` record of each run |
| `all.done` | the launcher's completion marker |
| `bases.sha256` | sha256 of the eight basis files written by the runs (not retained, see below) |
| `check_rees_fibers.py` | the verdict described above |
| `replay/` | the logs, time records and basis digests of the second-host replay |
| `sha256.txt` | sha256 of every retained file |

## Provenance of the retained bytes

The runs executed on a cloud VM, and its output directory was copied to the checkout with a sha256 comparison of every
file. Every file retained here is that directory's file under the same name, with the bytes unchanged (`cp -p`), except
`README.md`, `sha256.txt`, `bases.sha256`, `check_rees_fibers.py` and `replay/`, which are written for this
checkout. The scripts derive from three earlier local scripts through a local tool that replaces their Rees stage with the
unit replacement and the saturation above; the `SOURCE sha256` line of each log names the parent
(`226c4af155e80ec36d97165640cd7716f17477b3ef3e196bc58b22c3ce571f50` for the two E8-bar -> N- scripts,
`2281d01d6b47fec4e359ce2c8f0470e23918b0d41026edee87d952083d7c4953` for E8-bar -> N+ and
`452ea270018c239212a9142f86beb6b6ea757b8a999f88e28496c31a912bdcb5` for Iso). The parents and the tool are not retained;
each retained script stands alone. The Iso script writes its basis files under the name `iso-nm-p.c-u-full`, the name of
the variant it derives from.

The script digests are in line 2 of each log: `4e88035959ed486dc7fe168dafcc97ca4314a0624616d039535bb071f6294cc2`
(`e8-nm-p.v2-u-full`), `ee9318b04ec8dcb9e8c09858abc9eeb072da91235d5ac64ec0704633599c43ee` (`e8-np-p.v2-u-full`),
`7b37eef198cd7583ae870fdc5b3832f0b772fadd152de0ae683c7bd62bb6deb5` (`e8-nm-p.v2-u-y2`) and
`dab50bb8edcae66e4703e1597563eee9f63af22207513ce9d08e988ac51ef398` (`iso-nm-p.v2-u-full`).

## Basis files not retained

Each run writes its Rees standard basis (`NAME.hs.ssi`) and, when a colon iteration ran, the saturated basis
(`NAME.sat.ssi`) as Singular `ssi` files. The four largest are 52 to 60 MB; they are bound by digest here and in
`bases.sha256` instead of retained, as the normal-form tables of the A5-570 receipt are. The log is self-checking: the
certificate lines and both inclusions against K are printed from the basis in the run, so the basis files serve only a
re-verification by reading them back into Singular.

| File | Bytes | sha256 |
|---|---|---|
| `e8-nm-p.v2-u-full.hs.ssi` | 59978979 | `1d2405854591c9e6d5f8d8c911a88c25465ffad92ad3a7fe17536fc537eb5cce` |
| `e8-nm-p.v2-u-full.sat.ssi` | 57527395 | `996f29a94f55d045607d54554df54a7561e923bdf9ed418a059f4f4000bdb785` |
| `e8-nm-p.v2-u-y2.hs.ssi` | 10040467 | `4bd837cf176e033c12472465d32f0b653b631b23ded313db4ae5e3549ab08d0e` |
| `e8-nm-p.v2-u-y2.sat.ssi` | 9688751 | `0472cc1e0d56e5f2043efd5a1b19f0be998e15b3f635c0ba2f8c61e6df038ed3` |
| `e8-np-p.v2-u-full.hs.ssi` | 54737425 | `a6106b37b63e493a11faff5a489281c9cf0259726b40410b0fefb4cfd801a7ad` |
| `e8-np-p.v2-u-full.sat.ssi` | 52558259 | `a7afc5be273c09ad3d0636eb618289a21b77d4b2147862513d880ff0119e1812` |
| `iso-nm-p.c-u-full.hs.ssi` | 793270 | `bac46ad90d228acf00a1394235e861c4bc7ac7aaa4e7be829d199a76af445505` |
| `iso-nm-p.c-u-full.sat.ssi` | 793270 | `bac46ad90d228acf00a1394235e861c4bc7ac7aaa4e7be829d199a76af445505` |
The Iso basis and its saturation are one file (`iso-nm-p.c-u-full.hs.ssi` equals `iso-nm-p.c-u-full.sat.ssi`), since the
colon test needed no iteration. Regenerating the full-run files reruns `run2.sh` (11 to 14 hours on one core).

## Scope

A generator that lies in J sends the loop of line 185 into an endless loop (measured on a toy ring); the retained logs
print nonzero `UNIT terms left` for every generator, so no retained run reaches it. The scripts keep their bytes, since
each log binds its digest; the successor script with a guard is proposed in
https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/946.

One prime (32009), one root of -1 (10754), the weight-slice cells of E8-bar -> N-, E8-bar -> N+ and Iso -> N-, one
execution of each full run. The other root (21255) and the second prime (32029) are not run (A5-576); the characteristic-0
statements for these fibers are A5-457 and A5-475.
