# Captured source-rights evidence

The raw arXiv HTML, Dagstuhl HTML and Zenodo JSON responses bind PDF hosting
decisions to inspectable primary-source metadata. The
[source registry](../../SOURCES.json) records response URLs, retrieval times,
SHA-256 values, reading scopes and canonical capture paths. The captures
preserve original response bytes. External-only sources retain their inspected
rights limitations and optional ignored personal reading copies.

The [source verifier](../../verify_sources.py) treats captures as data.
For hosted arXiv papers it requires one article citation identity, one download
link to the exact version, and one balanced article license section. It rejects
missing or duplicate fields, duplicate relevant attributes, malformed nesting
and generic footer substitutions. The observed URL preserves source spelling;
HTTP-to-HTTPS normalization checks its registered license agreement.

For Dagstuhl, article-specific title, DOI, abstract link, PDF link and license
must agree with the registry and the captured canonical landing URL. The
storage URL must identify that DOI's PDF. A footer grant cannot qualify a
paper. For Zenodo, the record ID/self link and article license must agree;
one matching deposited file must have the registered filename, size and MD5.
Every hosted route checks the canonical capture path, timestamp and hash.

The [licensed source archives](../../INDEX.md#licensed-software-source-snapshots)
use a separate original-software route: exact inventory, pinned retrieval,
archive bytes, regular inspected members, their hashes, and the original
license member/text. The verifier opens archives for inspection and performs
zero extraction or execution. Uninspected links stay opaque. Source-code
licenses apply to the software and leave research-paper rights separate.

The [negative tests](../../check_verify_sources.py) exercise changed hashes,
coordinated relabeling, metadata substitutions, duplicate/missing fields,
invalid paths, altered archive/license members and selected symlink members.
The complete captures and original notices remain available for review.

The collision review's embedded CC0 notice has unresolved author attribution;
its [note](../../notes/2106.11974.md) records the original words and template
context. The [digital-optics note](../../notes/1909.04408.md) separately records
a publisher-advertised CC BY edition whose PDF returned HTTP 403. Neither
observation relabels the retained arXiv bytes. The registry keeps external-only
status and direct retrieval links pending the missing evidence.

Offline checks establish byte integrity and metadata agreement. Primary-source
inspection and review establish provenance and rights interpretation; a
response hash alone supplies neither.
