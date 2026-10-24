# Albuquerque-Majid cochain convention replay

The [source note](../../notes/math-9802116.md) maps the cochain of Albuquerque
and Majid, *Quasialgebra structure of the octonions* (arXiv math/9802116v1), onto
the repository sign table as `F_AM(a, b) = cd_sign(n, b, a)`. This bundle checks
that map from the paper's side. [am_convention_replay.py](am_convention_replay.py) builds `F_AM` from
Corollary 4.3 alone, doubling `f(x, y) = xy` on `Z_2` (the complex numbers) with
the new generator on the highest index bit, cd_core's last doubling, and reads
cd_core only as the comparison target.

| Comparison | Coverage | Required disagreements |
|---|---|---|
| `F_AM(a, b)` against `cd_sign(n, b, a)` | 5,460 basis pairs, n = 2 to 64 | 0 at every n |
| `F_AM(a, b)` against `cd_sign(n, a, b)`, the untransposed negative control | the same pairs | 0, 6, 42, 210, 930, 3906 |
| Eq. (11) associator of `F_AM` against `triple_sign` and the support of `cd_core.associator` on basis units | 37,448 triples, n = 2 to 32 | 0 at every n |

The associator is blind to the transpose, because `phi(x, y, z) = phi(z, y, x)`
(Lemma 3.4), so the raw-cochain comparison is the one that detects an omitted
transpose. Its first separating pair is n = 4, a = 1, b = 2: `F_AM(1, 2) = -1`
while `cd_sign(4, 1, 2) = +1`, recorded as `untransposed_witness`. Replacing the
`f(y, x) x'` term of the recursion by `f(x, y) x'` fails all three comparisons
from n = 8 on.

[derivation.json](derivation.json) records the source identity (the PDF's
sha256 and size, read from its `docs/SOURCES.json` record, since the PDF stays
outside the tree), the bit convention, the coverage and every count. Gate
sources-395 runs

```sh
"$PYTHON" -B -W error docs/evidence/albuquerque-majid-convention/am_convention_replay.py --check
```

which recomputes the record and compares its bytes; the run takes about 1 s.
The replay checks the convention on finite dimensions; the all-n statement
rests on the recursion of Corollary 4.3 matching the cd_sign recursion, which
the note argues and no proof assistant checks.
