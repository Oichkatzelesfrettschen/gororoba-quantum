# DAS MERGUS review checks

Independent probes behind the two claim ledgers of the DAS MERGUS review:
[algebra](../2026-10-25-das-mergus-algebra-review.md) and
[data](../2026-10-25-das-mergus-data-review.md). Each ledger row names the
script whose output carries its evidence. The probes are review artifacts,
not gated repository code: no gate runs them, and `ci/seed_provenance.py`
scans only the code directories.

- `algebra/` imports `cd_core` from the checkout that `REVIEW_REPO` names,
  a clean checkout of `ec75554a1af800496d99c80ab23022e83c5e20ea`; each
  `*.out` is the stdout of its script, whose stderr was empty. `companion-rerun/` holds the
  outputs of the delivered companion's own scripts, with local paths
  replaced by placeholders; those rows rest on reproduction only.
- `data/` reads the two Ascella runs under
  `results/quandela/runs/2026-10-24T*-qpu_ascella-ascella_signed_coherence-job-0*`
  relative to the repository root; each `*.out` is the run of its script, and
  `census.py`, `refs.py` and `ibm.py` take a checkout path, retained as
  `*-41d5ef0.out` and `*-main.out` (main at `d53a2fe`). `pkgrun/` holds the
  delivered statistics scripts' outputs. `ledger.py` regenerates
  `../2026-10-25-das-mergus-data-claims.json` byte for byte;
  `algebra/build_ledger.py 2026-10-25T09:57:41Z OUT` regenerates the algebra
  ledger.
- `check_small.py`, `check_witnesses.py` and `data/exact.py` map their
  independent items through `gororoba_quantum/parallel.py`, so each runs its
  body under a `__main__` guard; `algebra/assoc_items.py` holds the
  associator items the workers import. The remaining probes finish in under
  a second each, below the start-up cost of a spawn pool.

Every random seed is a value of the ANU QRNG draw
`docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json`, cited by index at
its use: index 0 `data/serial3.py`, 1 `algebra/check_cz_ranks.py`, 2
`algebra/check_pf_crosslink.py`, 3 and 4 `algebra/check_small.py`, 5
`algebra/check_det_membership.py`, 6 `algebra/check_strata.py`.
`check_small.py` spawns 201 child streams of its value through
`numpy.random.SeedSequence`; `serial3.py` serves both jobs from one stream.
`ci/seed_provenance.py` registers only seeds in the code directories and in
retained run records, so its ledger cannot record these uses; no other code
takes these values.

Run under the pinned CI interpreter (Python 3.14.7, numpy 2.5.4, scipy
1.18.1, sympy 1.14.0, python-flint 0.9.0) with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, from the script's own
directory so sibling imports resolve:

```sh
cd docs/archive/reviews/das-mergus-checks/algebra
REVIEW_REPO=/path/to/ec75554-checkout "$PYTHON" -B check_strata.py > check_strata.out
```
