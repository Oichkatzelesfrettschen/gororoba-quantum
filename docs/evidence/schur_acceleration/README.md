# Schur acceleration evidence

The [proof note](../../notes/schur_acceleration_certificates.md) derives
necessary acceleration equations and a quadratic outer bound for tangent
directions in a fixed same-nullity locus. The
[replay](replay.py) checks exact rational instances, complete affine
acceleration spaces, and every coefficient of two projected quadratic
systems. Compatible jets establish second-order solvability; the explicit
rational curvature path supplies an actual curve for its named direction.

Run from the repository root with the pinned dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/schur_acceleration/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/schur_acceleration/replay.py --check
(cd docs/evidence/schur_acceleration && sha256sum -c SHA256SUMS)
```

The replay reconstructs multiplication matrices directly from `cd_sign`,
then checks the centered frame and every derivative coefficient against
the production chart. Independent exact matrix elimination verifies the
homogeneous kernel's independence and completeness, the particular
acceleration, rank-sized minor, radial correction, and parameterized
solution. A separating covector verifies the incompatible system by its
left-kernel residual and nonzero pairing. First-order failure has a
separate retained status.

Five certificate cases include a nonzero compatible velocity, the `e11`
obstruction, zero velocities at nullities four and sixteen, and radial
first-order rejection. Altered certificate fields, incomplete kernels,
zero or damaged separators, and malformed inputs receive explicit
rejection checks. The symbolic curvature fixture also rejects the wrong
Schur sign and a missing factor of two.

The polynomial checks certify full bases for the first-order sphere
kernel and derivative left kernel. The replay extracts all diagonal and
mixed coefficients by exact polarization. The nullity-eight center uses
276 coefficients on 23 variables; the nullity-sixteen center uses 66
coefficients on 11 variables. Every projected coefficient vanishes, so
the conclusion holds for arbitrary real first-order directions at those
two centers. The coefficient identities supply necessary conditions and
second-order solvability; higher-order curve and stratum geometry remain
separate obligations.

`result.json` retains sparse exact matrices with their shapes, complete
affine kernels, separating witnesses, polynomial coefficient denominators,
and runtime versions (`--check` carries the retained Python patch release
when major.minor agree, gate core-609). Sparse records encode every omitted
entry as zero. A digest replaces only the parameterized example output
and derivative matrix already reconstructed elsewhere in the checks.
The replay verifies loaded module locations and that source hashes match
before and after computation. `SHA256SUMS` binds the README, replay, and
retained result.
Source or dependency changes require reviewed regeneration.

The calculations use CPU exact algebra. The replay submits zero QPU jobs.
The proof identifies an outer bound on the same-nullity tangent cone;
tangent-cone equality, a complete smooth stratification, attachments,
and global topological invariants remain unproved here.
