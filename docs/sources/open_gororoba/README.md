# Retained Cayley-Dickson evidence contracts

The [evidence contract](cayley_dickson_evidence_contracts.txt) preserves the
source repository's reconciliation of sign codes, zero-divisor membership,
annihilator certificates, finite topology, and interpretation boundaries.
The document supplies source context for the
[measurement design](../../notes/reality_ripple_measurement_design.md).

The files were extracted verbatim from
[open_gororoba revision abbf13cada78d9b106fc610a36f6eea54567ecfc](https://github.com/Oichkatzelesfrettschen/open_gororoba/tree/abbf13cada78d9b106fc610a36f6eea54567ecfc)
on 2026-10-12. [manifest.json](manifest.json) records repository-relative
source paths, revision, byte counts, SHA-256 values, and license declarations.
The evidence contract's last source change is
`88c102ac81d9b900f8d50292f29f0413a9ca6d51`.

The source README declares `GPL-2.0-only`, while the workspace Cargo manifest
declares `GPL-2.0-or-later`. The retained
[GPL version 2 license](LICENSE.GPL-2.0) accompanies the copied document.
The manifest preserves the declaration discrepancy; the retention makes
neither a later-version permission claim nor a license change to other
IBMQuantum files. Source copyright and license notices remain intact.

Check the retained source bytes from the repository root:

```sh
(cd docs/sources/open_gororoba && sha256sum -c SHA256SUMS)
```

The source document includes historical source identities, commands, and
claims. Those statements retain their original scope. Copying the document
does not rerun its Rust diagnostics or Rocq proofs. The measurement-design
note names the subset used for the prepared quantum acquisition.

Third-party papers retain separate copyright and retrieval provenance. The
[source library](../../INDEX.md) publishes explicitly licensed copies under
`docs/pdf/` and keeps reading copies without established publication permission
under ignored `docs/local_source_cache/`. The source repository's GPL notice
does not grant redistribution rights over its paper corpus.

The [switching checker](check_signed_kite_switching.py) and its
[finite result](signed_kite_switching.json) are original IBMQuantum artifacts,
separate from the two verbatim files listed in `SHA256SUMS`. The checker reads
the retained ripple graph evidence and verifies a standard signed-graph
deduction using integer matrix arithmetic. It performs no backend operation.
