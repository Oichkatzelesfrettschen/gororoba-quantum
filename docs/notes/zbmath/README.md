# zbMATH Open

zbMATH Open (FIZ Karlsruhe) serves three keyless interfaces, reached through
[`scripts/zbmath.py`](../../../scripts/zbmath.py): REST v1 (`https://api.zbmath.org/v1`, OpenAPI 1.9.33),
OAI-PMH 2.0 (`https://oai.zbmath.org/v1/`) and the citation matcher (`https://zbmath.org/citationmatching/`,
Script API PDF v1.6.26, sha256 `3f28ebb8...255c`). Use is governed by the API terms of June 2021
(https://static.zbmath.org/legal/api-terms-and-conditions.html), which bind on use and ask for a
"reasonable" request rate; the client sends one request per second and retries 5xx answers. zbMATH-generated
content is CC BY-SA 4.0, and third-party abstracts are replaced by the string "zbMATH Open Web Interface
contents unavailable due to conflicting licenses." The retained audit is
[evidence/zbmath-api-audit](../../evidence/zbmath-api-audit/README.md) (2026-10-29, 54 captures, 71 findings
that `check` replays offline; each finding's text lives in `FINDINGS` and `HEADER_FINDINGS` of the script).

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
```

## REST v1 audit

- Five entities (`document`, `author`, `serial`, `software`, `classification`), each with `/{id}`,
  `/_search` (zbMATH syntax: `ti:`, `au:`, `cc:`, `py:`, `doi:`, `arxiv:`, `&`, `|`, `!`, `*`) and
  `/_structured_search` (named fields with spaces, such as `Family name`). Entity roots return help text.
- Success is `status.execution_bool`: an unknown id answers HTTP 200 with the flag false; a search
  without hits answers HTTP 404; a DOI in the path answers 404 (use `doi:` search); type errors answer
  the framework's 422 `detail` list.
- `results_per_page` is 1..500; `(page+1)*results_per_page` above 10,000 answers 400 "Result window is too
  large". `last_id` is always null and no cursor parameter exists, so OAI-PMH is the only route past 10,000.
- Error envelopes stamp `time_stamp` in local Karlsruhe time without a zone; success envelopes in UTC with Z.
- GET only (HEAD and OPTIONS 405); no compression, no ETag/Cache-Control despite "cacheable", conditional
  headers ignored, no CORS and no rate-limit headers.
- Summaries are frequently placeholders (20 of 39 contributions on the sedenion query); zbMATH reviews are
  never replaced. The per-record `license` field is the article's license and is empty on most records.

## OAI-PMH audit

- Formats `oai_dc` and `oai_zb_preview` (references with matched ids, keywords, author codes, DOI). Sets are
  the 63 two-digit MSC classes plus `JFM` and `openaire`; `openaire` answers "invalid set".
- 100 headers per page; the resumptionToken expires after 24 h and its first cursor reads 100 rather than 0.
- Deviations from OAI-PMH 2.0: errors arrive with HTTP 400/404/500 instead of 200; an unknown token answers
  an HTML 500; a month-granularity `from` is accepted; `earliestDatestamp` is the bare year 1755; the
  `oai_zb_preview` schema URL is relative and resolves only at the host root; `oai_dc` prints absent values
  as `None`. Answers are gzip-compressed when offered.
- The same `oai_zb_preview` record served its full summary at 2026-10-29T13:54:39Z and the placeholder from
  14:04Z on (retained under `observations/`).

## Citation matcher audit

`match` (GET, or POST of up to 100 queries), `bibtex/match` and `bibtex/convert_file` work as documented,
with undocumented `probability` and `arxiv_id` fields; hits scored 0.0 are returned despite the documented
default minimum score 5.0, so filter on `probability`. Some preprint hits carry an `arXiv:` id in `zbl_id`.
The PDF states no traffic control exists.

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
