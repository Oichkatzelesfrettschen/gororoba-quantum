# Exact local skew Schur reduction evidence

The finite research probe reduces the `32 x 32` skew multiplication matrix
near the three certified rank-path endpoints to the exceptional kernel.
The probe uses rational arithmetic and checks the rank and kernel-lift
identities on six specified perturbations. The result supports the local
method in the [research synthesis](../../notes/koebisu_rank_stratum_research.md);
it does not classify every continuous rank locus or its attachments.

For each endpoint `j=0,1,2`, the probe constructs `U` from the column space
and `V` from the kernel of the exact path multiplication matrix. With
`T=[U,V]`, it checks invertibility of `T` and the complementary pivot `A`.
For each perturbed vector `a(j)+e_i/3`, `i=2,17`, it forms

```text
T^T L_x T = [A,B;-B^T,D],
S = D + B^T A^(-1) B,
T^T L_x T[-A^(-1)B;I] = [0;S].
```

The checks establish skew symmetry of `S`,
`rank L_x=dim(U)+rank S`, and the displayed lifted residual identity.
A changed lift entry must break its residual check. An added scalar-identity
term must fail the skew-symmetry admission check. The program uses explicit
exceptions, so Python's `-O` preserves those checks.

The probe computes `h -> V^T L_h V` on all 30 doubly-pure basis directions
and verifies that the radial direction lies in its kernel. The three
linear-deformation ranks are 6, 8, and 18; the unit-base linearized dimensions
are respectively 23, 21, and 11. The last value agrees with the published
dimension of the maximal stratum `V2(R7)`. The first two values remain
pointwise linearized bounds until higher-order smoothness and coverage
arguments establish more.

The JSON includes Python and SymPy versions. The program checks the
imported module paths and that the probe and its three imported repository
sources keep their bytes during the run; the digests stay out of the
result. It writes its result to stdout; `--check` compares the recomputed
JSON bytes with the retained `result.json`. Runtime or computed-value
changes therefore produce an explicit mismatch rather than silently
relabeling the evidence.

From the repository root, run:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  ruff check --no-cache docs/evidence/local_schur/probe.py
  ruff format --check --no-cache docs/evidence/local_schur/probe.py
  mypy docs/evidence/local_schur/probe.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/local_schur/probe.py --check
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/local_schur/probe.py --check
  (cd docs/evidence/local_schur && sha256sum -c SHA256SUMS)
)
```

The script discovers the repository root from its own path, so both replay
modes also work when invoked by an absolute script path from another working
directory. The retained files carry repository-relative source names and
contain no machine-local absolute paths. All arithmetic runs on the local
CPU; the probe calls no quantum service.
