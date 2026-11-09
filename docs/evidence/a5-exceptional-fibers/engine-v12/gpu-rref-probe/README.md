# GPU reduced row echelon probe

[`rref_probe.py`](rref_probe.py) computes the reduced row echelon form over F_p on the GPU from the recursive PLUQ
factorization of [`pluq.py`](pluq.py) (INT8 four-product Schur updates, then a blocked back substitution) and compares
rows and pivots with `flint.nmod_mat.rref`. It produced the six-case timing table of the GPU row in
[`../../../../runbooks/compute-flags.md`](../../../../runbooks/compute-flags.md) before `gororoba_quantum/modular_echelon.py` took
the method into the repository. Its matrices come from `numpy.random.default_rng(36574)`, index 1001 of the ANU draw
`draw-2026-11-08T170257Z` (`docs/evidence/qrng_seeds/allocations.json`).

The retained bytes differ from the bytes that produced the table by lint and typing edits only: torch and CuPy load
through `importlib`, long lines wrap, an unused name is gone, and the int64 overflow guard on the generator product
raises instead of assigning `None`. The `verify` subcommand of `pluq.py`, which the timing table did not use, drew its
matrices from a date seed; it now takes index 2 of the same draw (`VERIFY_SEED`). The arithmetic is unchanged. [`rerun-2026-11-09.txt`](rerun-2026-11-09.txt) is
the retained bytes on the workstation (RTX 4090 Laptop, `gpuenv`: torch 2.14.1+cu130, CuPy 14.2.0, python-flint
0.9.0): rows and pivots equal to flint at 300 x 700 rank 200 and 2,000 x 15,037 rank 1,800 (p = 32009), the second in
2.1 s against 19.9 s for flint, within the range of the original table.

Run on a CUDA host from this directory: `"$PYTHON" rref_probe.py . 32009 300 700 200 2000 15037 1800`.
