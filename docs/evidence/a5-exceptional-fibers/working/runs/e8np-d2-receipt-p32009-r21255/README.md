# Degree-2 receipt of the E8-bar -> N+ header at p = 32009, root of -1 = 21255

The receipt of [../e8np-d2-receipt-p32009](../e8np-d2-receipt-p32009/README.md) covers the root 10754. This directory
retains the same driver run on `working/build/inputs/p32009-r21255/e8-np.sing`, the header at the other root, which
ledger row A5-571 names as its closing computation.

## Result

- The receipt (`receipt/receipt-d2.json`, status `degree-certified`) certifies 148 relations on the 21 generators:
  `membership_check` 148 checked, 0 failures, `rank_h_d` 83 = 231 - 148. The relation file
  `receipt/relations-upto-d2.rel` has sha256 `0c3e97488cb409a77c5eb151d58fe8a960b3eca2811d1f491adc7f397cc913db`.
  These relations are the degree-2 part of the relation ideal L of that header, so the quadric ideal K2 at the root
  21255 is their ideal and lies in L by the membership check.
- Their ideal has 148 minimal generators, dimension 5, multiplicity 11 and Hilbert numerator 1, 16, -12, 10, -5, 1
  (`post.log`), the numbers of the root 10754.
- In the coordinates y(1..21) of the two headers the ideal is not the K2 of the root 10754: against the N+ file
  (`bbe9bb73...`) 110 and 103 remainders are nonzero, and against the N- file (`e047f996...`) 113 and 113. The two
  roots give different coefficient fields for the same formulas, so no equality of files is expected.
- `slice_bridge.py` of [../e8-slice-equivalence-p32009](../e8-slice-equivalence-p32009/README.md) finds an invertible
  linear map from the weight-slice quadric ideal at N+ and from the one at N- (both at the root 10754) onto this
  ideal (`bridge-weight-np.json`, `bridge-weight-nm.json`, verdict `map_found`; the script accepts a map only on
  equal ranks of the transported, the target and the joined spans). These two maps have no separate Singular check.
- Control: the receipt ideal with y(1)^2 added has dimension 4 and multiplicity 22 and differs from the receipt
  ideal in both directions.
- Calibration before the run: the driver on `xm-nm.sing` reproduces the retained relation digest `596c48a7...`
  (`run.log`, `CALIBRATION PASS`).

Scope: one prime and root, (32009, 21255); degree 2; Singular 4.4.1, Python 3.14.4 and python-flint 0.9.0 on an
aarch64 Linux host; the run copied the tree of commit `78c5e5c3a` without git metadata; one run, 3 h 15 min on one
core at 1.39 GB.

## Files

| File | Content |
|---|---|
| `run_receipt.sh` | the calibration and the receipt run of `fiber_cone_driver.py` |
| `post_check.sh`, `post.sing`, `post.log` | the invariants of the receipt ideal, the two comparisons, the control and the two map searches |
| `KH-e8-np-r21255.sing` | the receipt relations as an ideal, the input of the map search |
| `bridge-weight-np.json`, `bridge-weight-nm.json` | the maps from the weight-slice ideals |
| `run.log`, `driver.log`, `calibration-driver.log` | the run, driver and calibration logs |
| `receipt/` | the driver output of degree 2 without the two tables below |
| `sha256.txt` | sha256 of every other file of this directory |

Two driver outputs are not retained because of their size; the receipt binds the first by digest
(`normal_form_sha256`): `nf-d2.txt` (40,286,747 bytes, `84d5485acadabab6ead4035ed4c499c3c33384cf8ced381b164865636f349200`)
and `sq.txt` (173,631,093 bytes, `dc6a2349ee46589248b22e98117d7820d3b4b4c5c73f8d72eafd2b5ddd291b70`).
