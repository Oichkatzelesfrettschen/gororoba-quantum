# A_6 Stiefel witness: kernel-checked invertibility

[StiefelWitnessInvertible.v](../../../proofs/StiefelWitnessInvertible.v) is
the machine-checked finite step of the generic-invertibility theorem in
[stiefel_generic_invertibility.md](../../notes/stiefel_generic_invertibility.md).
`scripts/stiefel_witness_certificate.py --write` generates it from the
`a6_integer_witness` of [nullity.json](../moreno_stiefel/nullity.json) and
`cd_core`, and `--check` re-renders and compares it.

## What the kernel checks

| Theorem | Statement |
| --- | --- |
| `witness_is_stiefel` | v has length 64; its halves (indices 0-31 and 32-63) have zero real part, zero dot product and squared norm 62 each |
| `Lv_left_inverse` | `sum_k N(i, k) L_v(k, j) = d` if `i = j`, else 0, for all `i, j < 64` |
| `Lv_integer_kernel_trivial` | an integer x with `L_v x = 0` is zero |
| `sigma_fuel_adequate` | `cd_sign_fuel` at fuel 7 agrees with fuel 100 on every pair at dimension 64 |

`L_v(i, j) = sigma(i xor j, j) v(i xor j)`, where `sigma` is open_gororoba's
`cd_sign_fuel 7 64`, taken from `proofs/verified/C1474_FuelAdequacy.v` at the
digest in [source_hashes.sha256](source_hashes.sha256). The identity has
`d = 208270573125941552`, the least common denominator of `L_v^-1`, and
`N = d L_v^-1`. N determines `L_v` as `d N^-1`, so the identity holds only
when `cd_sign_fuel` reproduces `cd_core.cd_sign` on this matrix: the check
crosses two independent implementations of the sign rule.
`Print Assumptions` reports every theorem closed under the global context
([assumptions.txt](assumptions.txt)), and [kernel.txt](kernel.txt) reports
no axioms, no type-in-type and no unsafe fixpoints.

[package_cross_check.json](package_cross_check.json) records a third
implementation. python-hypercomplex, `cayley_dickson_algebra(6, Fraction)`,
gives every column `v * e_j` of `L_v` equal to the `cd_core` matrix, with
zero mismatched entries. It runs on the build host with
`--package-cross-check`, because CI installs no algebra packages.

## Replay

```sh
GOROROBA_ROOT=/path/to/open_gororoba ROCQ="${ROCQ:-rocq}" \
  sh docs/evidence/stiefel_witness/replay_rocq.sh
```

The replay requires the Rocq 9.2 / OCaml 5.5.0 toolchain of
[toolchain.txt](toolchain.txt), the same one the C881 replay uses. It
checks the evidence and open_gororoba source digests, copies the two
sources into temporary storage, compiles with `-w @all`, kernel-checks with
`rocq check`, and compares all four outputs byte for byte. Compiling takes
about 35 s; the independent kernel check takes about 4 minutes. Hosted CI
supplies no Rocq toolchain, so CI verifies the retained bytes (`sha256sum
-c SHA256SUMS`), the generator's re-render, the Python identity and
shellcheck. A retained receipt records this run; a later kernel check is a
fresh replay.

open_gororoba's own build pins Rocq 9.1.1 with Flocq through
`proofs/Makefile.rocq.conf`. Neither `C1474_FuelAdequacy.v` nor this proof
imports anything beyond Stdlib, so both compile directly under 9.2 with
explicit `-R` and `-Q` mappings, without that configuration.
