# Independent cubic-core certificate package

These files are a certificate package written independently of
`gororoba_quantum/cd_core.py`: `recheck.py.txt` implements the recursive
Cayley-Dickson product `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))` and
the Boolean algebraic normal form in the standard library only, and
`cubic_core_check.py.txt` derives, for each of the 360 degree-3 dim-32
associator phases, three independent linear forms whose product carries the
cubic part. `cubic_core_certificates.json` and `checks.json` are the outputs
the package shipped with; `MANIFEST.json` gives each file's sha256 as shipped.
The manifest also names an 8,828-byte `README.md` that the Kaggle dataset did
not contain; `retention.json` records it as not shipped and records the two
scripts' `.txt` names, so every manifest entry is accounted for.
The package came from the Kaggle dataset `probablyeric/ccz-certificates`
(retrieved 2026-10-16) and names repository commit e8df46e as its source pin.

The scripts keep their exact bytes under a `.txt` suffix and are not run
here. `scripts/associator_cubic_normal_form.py --cross-check` (gate core-284)
checks every manifest entry, present with its recorded sha256 or listed
as not shipped and absent, and requires the shipped certificates
to name, for every pair, the same cubic part and the same three linear forms
as `../normal_form.json`, which `cd_core` produces; all 360 pairs agree.
