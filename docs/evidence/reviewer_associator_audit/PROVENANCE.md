# Provenance of the reviewer associator audit

The repository owner supplied this CPU-only audit with an external review of a
proposed sedenion-circuit protocol on 2026-10-14. The four files `README.md`,
`audit.py`, `audit_results.json` and `sources.bib` keep the bytes of
`reviewer_associator_audit.zip` (SHA-256
`761a95b623c69f93ecc4ca645a8aff1313ba60df14cd04b9472761ad6926f3da`);
[SHA256SUMS](SHA256SUMS) binds them. The audit pins `cd_core.py` blob
`ccb51aa4b9e9bab6ab8675fa634d25cb77291cf1`, which is the repository's file at
the time of import.

`audit.py` needs NumPy only and reads nothing outside its own code. It checks
the doubling product against the iterative sign algorithm on all 256 sedenion
basis pairs; the reviewer's proposed pair `(e1 + e10)(e2 - e13)`, which is
nonzero; the corpus pair `(e1 + e10)(e4 - e15)`, which is zero; the
reversible signed lookup on all 512 basis states; the universal contraction
`M M^dagger = 16 I`; the fixed-operand LCU outcomes 0, 1/2 and 1; the
fixed-pair associator unitary on all 256 pairs; the 1848 non-associating
triples among 4096; the Hadamard-test measurement basis; and a complex-linear
zero divisor of an associative subalgebra. The algebra circuit design rules
in the root AGENTS.md cite these results.

Gates sources-240 and sources-241 rerun the audit in normal and optimized
Python and compare its printed JSON with `audit_results.json` byte for byte:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" -I -W error docs/evidence/reviewer_associator_audit/audit.py \
  | cmp - docs/evidence/reviewer_associator_audit/audit_results.json
```

The audit establishes ideal arithmetic and ideal circuit behavior; it runs no
QPU job and supplies no gate-cost estimate.
