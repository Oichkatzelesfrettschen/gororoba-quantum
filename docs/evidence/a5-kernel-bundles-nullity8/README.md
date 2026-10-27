# A_5 kernel bundles on the nullity-eight strata

This evidence directory executes the
[nullity-eight kernel-bundle program](../../design/a5-kernel-bundles-nullity8-program.md). The first exact result
computes the connected compact `G_2 x U(1)` tangent ranks on the five complex nullity-eight orbits from the
[regularity record](../a5-strata-regularity/README.md): `W8`, E8-bar, the isotropic orbit `Iso`, and the two branches
`X_+` and `X_-`. Orbit invariants, complete moduli spaces, stabilizer representations, topology, transition data, and
bundle classes remain open.

Every calculation uses integer or rational arithmetic. [`compact-orbit-ranks-result.json`](compact-orbit-ranks-result.json)
is the output of [`compact_orbit_ranks.py`](compact_orbit_ranks.py) `--out`. The producer carries a byte-exact
`--check` and a `--self-test` whose mutation deletes the base-phase generator.

## Every nullity-eight orbit has generic compact rank fifteen

The connected compact symmetry acting on a unit section has fourteen compact `G_2` generators and the lifted base
phase, for dimension fifteen. The producer evaluates its tangent map at the recorded representative of each orbit
and at three exact moved points. The moves use rational exponentials of nilpotent `G_2(C)` derivations and rational
`SO(2,C)` boosts. Every moved point retains left nullity eight and the same closure-membership pattern as its
representative.

Two exact implementations compute every tangent rank. The first applies the committed 32 by 32 base matrices from
the constant kernel-symmetry solve. The second independently applies the compact octonion derivations to the two
complex seven-vector blocks and appends the direct complex phase tangent. The implementations agree on all twenty
points.

| Orbit | Unit-section dimension | Representative rank | Ranks after exact noncompact moves | Maximum observed rank | Generic local quotient dimension |
| --- | ---: | ---: | --- | ---: | ---: |
| `W8` | 23 | 12 | 15, 15, 15 | 15 | 8 |
| E8-bar | 21 | 12 | 12, 15, 15 | 15 | 6 |
| `Iso` | 21 | 15 | 15, 15, 15 | 15 | 6 |
| `X_+` | 19 | 12 | 12, 15, 15 | 15 | 4 |
| `X_-` | 19 | 12 | 12, 15, 15 | 15 | 4 |

The pointwise rows are **Observed** in the result record. The generic statement is **Inferred** from those exact
rows: rank fifteen is the largest possible rank of the fifteen-generator tangent matrix, and the nonvanishing of a
maximal minor persists on an open neighborhood. Therefore every orbit has generic compact tangent rank fifteen. The
local dimensions of the principal compact-orbit quotients are the unit-section dimensions minus fifteen, namely
eight on `W8`, six on E8-bar and `Iso`, and four on both `X` branches.

The representative data also expose a real compact-orbit refinement inside four complex orbits. The recorded points
of `W8`, E8-bar, `X_+`, and `X_-` have rank twelve even though each orbit contains rank-fifteen points. The recorded
`Iso` point already lies in the full-rank locus. The calculation does not yet identify every lower-rank compact
stratum.

The falsifier was a disagreement between the two exact rank implementations, a moved point that changed nullity or
open-orbit membership, failure to reach the full compact rank on any orbit, or a phase-deletion mutation that left
every downstream rank unchanged. None occurred. The mutation lowers at least one computed tangent rank.

## No nullity-eight orbit is compact homogeneous

**Inferred.** A connected compact orbit has dimension at most fifteen. Each nullity-eight unit section has dimension
at least nineteen, and the exact probe reaches the upper bound fifteen. Consequently none of the five nullity-eight
orbits is transitive under the connected compact symmetry. This answers one standing program question but does not
classify the quotient spaces.

The falsifier was a unit section of dimension at most fifteen or an exact compact tangent rank above fifteen. The
committed unit-section dimensions are 23, 21, 21, 19, and 19, and every computed rank is at most fifteen.

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles-nullity8/compact_orbit_ranks.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles-nullity8/compact_orbit_ranks.py --self-test
"$PYTHON" docs/evidence/a5-kernel-bundles-nullity8/compact_orbit_ranks.py \
    --check docs/evidence/a5-kernel-bundles-nullity8/compact-orbit-ranks-result.json
```

The measured `--check` wall time was 7.84 seconds on the 2026-10-26 build host with four workers. The check builds
the sorted, two-space-indented JSON plus its final newline in memory, compares the UTF-8 bytes with the retained
record, writes no repository file, and exits nonzero on a difference.
