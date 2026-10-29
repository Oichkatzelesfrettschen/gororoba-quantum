# zbMATH Open

zbMATH Open (FIZ Karlsruhe) serves three keyless interfaces, reached through
[`scripts/zbmath.py`](../../../scripts/zbmath.py): REST v1 (`https://api.zbmath.org/v1`, OpenAPI 1.9.33),
OAI-PMH 2.0 (`https://oai.zbmath.org/v1/`) and the citation matcher (`https://zbmath.org/citationmatching/`,
Script API PDF v1.6.26, https://zbmath.org/static/citation-matching-api.pdf, sha256
`3f28ebb84123fc52cf1e4c90a807d42c940682f46499474182de16af7f51255c`). Use is governed by the API terms of June 2021
(https://static.zbmath.org/legal/api-terms-and-conditions.html), which bind on use and ask for a
"reasonable" request rate; the client sends one request per second and retries 5xx answers. zbMATH-generated
content is CC BY-SA 4.0, and third-party abstracts are replaced by the string "zbMATH Open Web Interface
contents unavailable due to conflicting licenses." The retained audit is
[evidence/zbmath-api-audit](../../evidence/zbmath-api-audit/README.md) (2026-10-29, 57 captures, 74 findings
that `check` replays offline; each finding's text lives in `FINDINGS` and `HEADER_FINDINGS` of the script).
Protocol clauses below cite the OAI-PMH 2.0 specification,
https://www.openarchives.org/OAI/openarchivesprotocol.html (fetched 2026-10-29, sha256
`d81e32299f773b460c9dc8494bc3fe69d5e919fe4d9ef74c39d1a0e3ed7c2b98`).

## Which interface

| Task | Interface |
|---|---|
| look up a document, author, serial, software or MSC code; search up to 10,000 hits | REST `get`, `search`, `structured` |
| harvest by MSC class and date range, or any result set past 10,000 | OAI-PMH `oai ListRecords ... --out DIR` |
| turn a reference string or BibTeX into a Zbl id | citation matcher `match`, `bibtex` |
| whole-corpus analysis | Zenodo dumps (community `zbmath`), the RDF knowledge graph (Zenodo DOI 10.5281/zenodo.21497975) |

## Commands

```sh
"$PYTHON" scripts/zbmath.py get document 1257.82097          # internal id or Zbl id
"$PYTHON" scripts/zbmath.py search document 'ti:sedenion* py:2020-2026' --all
"$PYTHON" scripts/zbmath.py structured document 'DOI=10.1007/s00006-012-0360-6'
"$PYTHON" scripts/zbmath.py oai ListRecords metadataPrefix=oai_zb_preview set=17 from=2026-10-01T00:00:00Z --out DIR
"$PYTHON" scripts/zbmath.py match 'Moreno, The zero divisors of the Cayley-Dickson algebras, 1998'
"$PYTHON" scripts/zbmath.py bibtex refs.bib --convert         # adds zbl = {...} fields
"$PYTHON" scripts/zbmath.py check docs/evidence/zbmath-api-audit   # offline replay of the audit
```

`match` and `bibtex` send `m=5.0` explicitly, because the service does not apply its documented default.

## REST v1

- Five entities (`document`, `author`, `serial`, `software`, `classification`), each with `/{id}`,
  `/_search` (zbMATH syntax: `ti:`, `au:`, `cc:`, `py:`, `doi:`, `arxiv:`, `&`, `|`, `!`, `*`) and
  `/_structured_search` (named fields with spaces, such as `Family name`). Entity roots return help text.
- Success is `status.execution_bool`: an unknown id answers HTTP 200 with the flag false; a search
  without hits answers HTTP 404; a DOI in the path answers 404, encoded or not (use `doi:` search); type
  errors answer the framework's 422 `detail` list.
- `results_per_page` is 1..500; `(page+1)*results_per_page` above 10,000 answers 400 "Result window is too
  large". `last_id` is always null and no cursor parameter exists, so OAI-PMH is the only route past 10,000.
- Error envelopes stamp `time_stamp` one hour ahead of the HTTP `Date` header and without a zone; success
  envelopes stamp UTC with `Z`.
- GET only (HEAD and OPTIONS 405); no compression when gzip is offered; no ETag, Last-Modified or
  Cache-Control; conditional headers ignored; no CORS or rate-limit headers.
- On the 40 records of the `sedenion` query, 20 of 39 editorial contributions are the placeholder, all of
  them summaries or editorial notes; none of the 4 zbMATH reviews is. The per-record `license` field is the
  article's license and is empty on 29 of the 40.

## OAI-PMH

- Formats `oai_dc` and `oai_zb_preview` (references with matched ids, keywords, author codes, DOI). Sets are
  the 63 two-digit MSC classes plus `JFM` and `openaire`. 100 headers per page; a resumptionToken expires
  after 24 h. Answers are gzip-compressed when offered.
- Errors arrive with HTTP 400 or 404 and carry the HTTP status in the `<error code>` attribute and the
  protocol code in the element text; the client reads the text.
- The `oai_zb_preview` record of document 6123912 served its full summary at 2026-10-29T13:54:39Z and the
  placeholder in every fetch from 14:04Z on (retained under `observations/`).

## Citation matcher

`match` (GET, or POST of up to 100 queries), `bibtex/match` and `bibtex/convert_file` work as documented,
with undocumented `probability` and `arxiv_id` fields. Some preprint hits carry an `arXiv:` id in `zbl_id`.
The PDF states no traffic control exists.

## Falsification of the deviations

Each deviation below was tested against the alternative that the client, the operator or the request
caused it. "Independent client" means curl reproduced the answer outside `scripts/zbmath.py`. A deviation
enters a report to FIZ Karlsruhe only with the verdict "service" and its capture name.

| Deviation | Alternative tested | Test | Verdict |
|---|---|---|---|
| unknown REST id answers HTTP 200 with `execution_bool` false | client path quoting | curl, ids `99999999999` and `abc` | service |
| search without hits answers HTTP 404 | malformed query | curl; valid word query `zzqqxxnotaword` and empty query both 404 | service; API design, no standard violated |
| result window 10,000 | page arithmetic in the client | 100x100, 500x20 and 1x10,000 all fail; 1x9,999 passes | service; documented nowhere in the OpenAPI document |
| DOI in path answers 404 | slash not encoded | `%2F`-encoded DOI also 404 | service; route takes no slash |
| no gzip on REST | client did not offer gzip | `curl --compressed` returns the uncompressed 10,424 bytes | service |
| no validator headers despite "cacheable" | wording means client-side caching | none possible | interpretive; report as a question |
| error `time_stamp` without zone, 1 h ahead | clock skew | `Date` 14:52:16 GMT against `time_stamp` 15:52:16.8 in the same answer | service; the zone is inferred as CET (UTC+1 after 2026-10-25) |
| first resumptionToken `cursor="100"` | cursor counts the current page | section 3.5: "a count of the number of elements of the complete list thus far returned (i.e. cursor starts at 0)" | service |
| `earliestDatestamp` 1755 | year allowed | schema type `UTCdatetimeType` is `date` or `dateTime` with Z, and section 4.2 requires the finest granularity | service |
| month `from` and mixed `from`/`until` granularity accepted | lenient parsing is harmless | section 3.3.1 names two legitimate formats and requires both arguments at one granularity | service; low impact |
| unknown set answers `invalid set` | set code misspelled | `zz` and the advertised `openaire` both, across ListIdentifiers, ListRecords and both formats | service; `invalid set` is outside the error enumeration, `openaire` is advertised by ListSets |
| non-UUID resumptionToken answers HTML 500 | token format | a UUID-shaped unknown token answers `badResumptionToken` | partly operator: malformed input; report as robustness |
| OAI errors with HTTP 400/404 | specification requires 200 | section 3.1.2.2 separates OAI errors from HTTP status codes and permits codes besides 200; it does not require 200 | interpretive; generic harvesters that raise on non-200 lose the error code |
| relative `oai_zb_preview` schema URL | relative URLs resolve | resolved against the base URL `/v1/` it answers 404; it resolves only at the host root | service |
| `oai_dc` prints an absent contributor as `None` | the record names a contributor `None` | the REST record lists no editors or author references, and `oai_zb_preview` of the same record has no contributor element | service |
| summary served, then placeholder | User-Agent, compression, or a different record | same identifier and format; three User-Agents at 14:04Z all placeholder; the 13:54Z answer is retained | observed once; cause unknown (data update or backend), not reproducible |
| zero-score citation hits | client sent `m=0` | the request sent no `m`; explicit `m=5` removes them | service; documented default not applied |

## Other resources

Web tools: author profiles and disambiguation (https://zbmath.org/author-profile/), collaboration distance
(https://zbmath.org/collaboration-distance/), citation matching and BibTeX interface. GitHub
(https://github.com/zbMATHOpen): `zbmath-open-kg` (RDF knowledge graph, ontology, temporary SPARQL endpoint),
`zbRestApiClient` (Swagger client generated for API v0.4.3rc0, stale against 1.9.33), `mscHarvester`,
`linksApi`. Zenodo community `zbmath` (18 records): identifier mapping zbMATH/DOI/ORCID/arXiv (CC BY-SA 4.0,
114 MB), swMATH-zbMATH links, open-access subset, MSC dataset, OCR of volumes 1-529. Reviewer material: the
guide for reviewers, the reviewer service, the CTAN `zbmath-review-template`, the zbNEWS newsletters.
Partners: MathOverflow `zbmath` tag, DLMF, OEIS, ATLAS of Group Representations, Software Heritage,
Wikimedia Math group, MaRDI portal, EOSC/FAIRCORE4EOSC, W3C Math Working Group.
