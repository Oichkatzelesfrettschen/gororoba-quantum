# A_5 null-slice family: direct relation checks above dimension 512

The first null-slice family satisfies the so(m,1) relations by exhaustive direct check at n = 10, 11 and 12 (dimensions
1024, 2048 and 4096), so the direct check now covers every level from 256 to 4096. The slice has time index 7 * 2^(n-3)
and space [1, 2^(n-2)) without 2^(n-3). The [associator envelope record](../a5-null-slice-associator-envelope/README.md)
checks these relations directly up to n = 9 and through disjoint stars above. Ledger row A5-637.

## Statement

[`scripts/a5_null_slice_family_relations.py`](../../../scripts/a5_null_slice_family_relations.py) checks
[[K_a, K_b], K_c] = delta_bc K_a - delta_ac K_b for every pair a < b and every c in the space. It uses the envelope
record's `triple_item`, imported, with one pool task per pair:

| n | Dimension | m | Relations | Failures | Result |
|---|---|---|---|---|---|
| 10 | 1024 | 254 | 8,161,274 | 0 | [result-n10.json](result-n10.json) |
| 11 | 2048 | 510 | 66,195,450 | 0 | [result-n11.json](result-n11.json) |
| 12 | 4096 | 1022 | 533,209,082 | 0 | [result-n12.json](result-n12.json) |

Each result names the sha256 of the checker and of the envelope script it imports. The relations at n = 10 to 12 now
rest on two lines of evidence: this exhaustive check and the star criterion with the sufficient direction of A5-617.
The two share the cd_sign tables, so they count as one line for the sign convention.

## Timings and host

On the compute workstation under WSL with the pinned interpreter, 32 workers: n = 8 in 1 s, n = 9 in 1 s, n = 10 in
8 s, n = 11 in 78 s; n = 12 in 1242 s at 16 workers, beside another session's jobs. Each level multiplies the cost by
about 8 to 10 at equal workers.

## Controls

`--self-test` checks n = 6 twice: the family's space gives 0 failures, and the same space with its last index replaced
by the excluded index 2^(n-3) gives failures.

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_null_slice_family_relations.py --level 10 --check docs/evidence/a5-null-slice-family-relations/result-n10.json
"$PYTHON" -B -W error scripts/a5_null_slice_family_relations.py --level 11 --check docs/evidence/a5-null-slice-family-relations/result-n11.json
"$PYTHON" -B -W error scripts/a5_null_slice_family_relations.py --level 12 --check docs/evidence/a5-null-slice-family-relations/result-n12.json
```

Gates `core-a5-null-slice-family-relations-n10`, `-n11` and `-n12` run them on demand; the n = 12 gate measured 1242 s at
16 workers, and about 10 minutes at 32 workers is an estimate from the scaling.
