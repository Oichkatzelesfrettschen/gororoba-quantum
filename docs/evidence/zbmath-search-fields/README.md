# zbMATH Open search-field probes

`fields.json` holds the result of `"$PYTHON" scripts/zbmath.py fields`: for each row of `FIELD_PROBES`,
the REST `/_search` result count of `ANCHOR & FIELD:POSITIVE` and of `ANCHOR & FIELD:NEGATIVE`, where the
anchor is one known record. A field works when the positive query finds the anchor alone and the negative
query finds nothing; `documented` marks fields that neither the General Help page nor the OpenAPI
descriptions list. The file holds counts and query strings only, no zbMATH record content.

`"$PYTHON" scripts/zbmath.py check-fields docs/evidence/zbmath-search-fields/fields.json` replays the rule
offline and requires the rows to equal the inventory in the script. The guide
[notes/zbmath/README.md](../../notes/zbmath/README.md) tabulates the fields and the combinations they allow.
