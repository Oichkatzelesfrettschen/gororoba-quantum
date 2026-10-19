> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 01fd48f9e2bd996ef2be79a123441fac972262ceea0b55f0ba74b4c38f0ba9db.

# iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId

iqm.error_reduction_tools.readout_characterization.data_processing.ErrorId*: [TypeAlias](https://docs.python.org/3.11/library/typing.html#typing.TypeAlias "(in Python v3.11)")* *= int \| tuple\[int, int\]*  
Error category identifier.

A single `int` (0–3) labels a single-qubit preparation/measurement outcome:

- 0: prepared `|0⟩`, measured 0 (correct)

- 1: prepared `|1⟩`, measured 1 (correct)

- 2: prepared `|0⟩`, measured 1 (0→1 flip)

- 3: prepared `|1⟩`, measured 0 (1→0 flip)

A `tuple[int, int]` labels a joint two-qubit error pair, e.g. `(2, 3)` means qubit i had a 0→1 flip and qubit j had a 1→0 flip.
