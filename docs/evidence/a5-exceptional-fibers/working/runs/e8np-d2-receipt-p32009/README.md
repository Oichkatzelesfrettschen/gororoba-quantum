# Degree-2 receipt of the E8-bar -> N+ header at p = 32009

This directory retains the degree-2 fiber-cone membership receipt of `working/build/inputs/p32009-r10754/e8-np.sing`
(p = 32009, root of -1 = 10754), the run that produced it and the check that compares its relations with the retained
N+ K2 file `../e8_a2/e8_k2.rel`. Ledger row A5-570 states the claim; A5-079, A5-559, A5-009, A5-335 and A5-339 cite it.

## Result

- The receipt (`receipt/receipt-d2.json`, status `degree-certified`) certifies 148 relations on the 21 generators:
  `membership_check` 148 checked, 0 failures, `rank_h_d` 83 = 231 - 148. The relation file
  `receipt/relations-upto-d2.rel` has sha256 `50c1047de3ffda330eecfbe8b7a3449abed2196b8858b29149cf239da01e843c`.
- That file and the K2 file (`bbe9bb73...`) are different bytes of one ideal: in F_32009[y(1..21)] each reduces to
  zero modulo a standard basis of the other (`RESULT direct 0 0`). The ideal has dimension 5, multiplicity 11 and 148
  minimal generators, and the numerator of its Hilbert series reads 1, 16, -12, 10, -5, 1.
- Cross-check: with the y signs of the t8, t9 flip applied, the receipt relations and the retained N- receipt relations
  (`../../distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel`, `e047f996...`) reduce to zero against each other
  (`RESULT transport 0 0`). The J and G sign patterns of the flip are in `post.log`.
- Controls: adding y(1)^2 to the K2 file, or to the N- file, leaves nonzero remainders (`control_direct 1 1`,
  `control_transport 1 1`), so the comparison rejects a perturbed ideal.
- Calibration before the run: the same driver on `xm-nm.sing` reproduces the retained relation file of X- -> N-
  (sha256 `596c48a7...`, `run.log`); `post-selftest.log` is `post_check.py` run on the retained K2 file as its own
  receipt before the receipt existed, which passes.

Scope: one prime and one root, (32009, 10754); degree 2; Singular 4.4.1 and Python 3.14.7 on an x86_64 Linux VM at
repository commit `315d884fb12e4c32b98e3fbe38e79468498c74c2` with a clean tree; one run, wall time 2 h 33 min on one core
(`run.log`). The other root at 32009 (21255) and degrees above 2 are not covered by this receipt.

## Files

| File | Content |
|---|---|
| `run_receipt.sh` | the calibration and the receipt run, `fiber_cone_driver.py --header ... --degree 2 --prime 32009` |
| `post_check.sh`, `post_check.py` | the comparison of the receipt relations with the K2 file and, after the sign flip, with the N- receipt |
| `run.log`, `calibration-driver.log`, `driver.log`, `post.log`, `post-selftest.log` | the run, calibration, driver, post-check and self-test logs |
| `receipt/` | the driver output of degree 2 without the two normal-form tables below |
| `sha256.txt` | sha256 of every retained file |

The scripts keep their as-run text except the run directory, which `BASE` names generically here, and the
post-check's file name. `post_check.py` runs from the repository root, as
`python -B working/runs/e8np-d2-receipt-p32009/post_check.py working/runs/e8np-d2-receipt-p32009/receipt/relations-upto-d2.rel working/runs/e8np-d2-receipt-p32009/receipt/receipt-d2.json`
with the repository's `docs/evidence/a5-exceptional-fibers/` prefix on both paths.

Two driver outputs are not retained because of their size; the receipt binds them by digest
(`normal_form_sha256`):

| File | Bytes | sha256 |
|---|---|---|
| `nf-d2.txt` | 40286744 | `885dc8f2d23dbebe8fd1618631fec643a1adfac467c0467da9e6addb2e019ab1` |
| `sq.txt` | 173631093 | `dc6a2349ee46589248b22e98117d7820d3b4b4c5c73f8d72eafd2b5ddd291b70` |

Regenerating them reruns `run_receipt.sh`.
