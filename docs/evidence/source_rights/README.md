# Captured source-rights evidence

The raw arXiv HTML and Zenodo JSON responses bind hosted PDF license decisions
to inspectable primary-source metadata. The [source registry](../../SOURCES.json)
records each response URL, retrieval timestamp, SHA-256 and canonical evidence
path. The nine arXiv pages and two Zenodo records retain their original response
bytes; their hashes match the earlier rights audit.

The [source verifier](../../verify_sources.py) reads the captures as data.
For each hosted arXiv paper, its HTML parser requires one `citation_arxiv_id`,
one `download-pdf` link to the exact version, and one balanced `div.abs-license`
containing one `has_license` link. The parser excludes generic footer licenses
and rejects duplicate fields, duplicate relevant attributes and malformed
nesting. The observed license URL retains its source spelling; HTTP-to-HTTPS
normalization checks its agreement with the registered license.

For each Zenodo paper, the verifier reads `metadata.license.id` and checks the
record ID and self link, then identifies one matching file by its self link.
The decoded filename, size and MD5 must agree with that deposited file and the
retained PDF. Both evidence routes first check the capture path, retrieval
timestamp and response hash.

The [mutation tests](../../check_verify_sources.py) exercise changed hashes,
coordinated registry relabeling, rehashed metadata changes, missing or duplicate
fields, malformed captures and substituted files. The tests also admit all
registered hosted arXiv snapshots.

The external-only records retain their manual-audit boundary and optional
personal-copy cache. Offline capture checks establish byte integrity and
metadata agreement. Primary-source inspection and review establish capture
provenance and the rights interpretation; the response hash alone supplies
neither.
