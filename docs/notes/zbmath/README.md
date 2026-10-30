# zbMATH Open

zbMATH Open (FIZ Karlsruhe) serves three keyless interfaces, reached through
[`scripts/zbmath.py`](../../../scripts/zbmath.py): REST v1 (`https://api.zbmath.org/v1`, OpenAPI 1.9.33),
OAI-PMH 2.0 (`https://oai.zbmath.org/v1/`) and the citation matcher (`https://zbmath.org/citationmatching/`,
Script API PDF v1.6.26, https://zbmath.org/static/citation-matching-api.pdf, sha256
`3f28ebb84123fc52cf1e4c90a807d42c940682f46499474182de16af7f51255c`). Use is governed by the API terms of June 2021
(https://static.zbmath.org/legal/api-terms-and-conditions.html), which bind on use and ask for a
"reasonable" request rate; the client sends one request per second and retries 5xx answers. zbMATH-generated
content is CC BY-SA 4.0, and third-party abstracts are replaced by the string "zbMATH Open Web Interface
contents unavailable due to conflicting licenses."

Two retained records carry the audit, both replayed offline by `--self-test`:

- [evidence/zbmath-api-audit](../../evidence/zbmath-api-audit/README.md): 59 raw responses with request and
  response headers, and 77 findings that `check` replays (`FINDINGS` and `HEADER_FINDINGS` in the script).
- [evidence/zbmath-search-fields](../../evidence/zbmath-search-fields/README.md): 71 paired probes of the
  one-line search fields, replayed by `check-fields` (`FIELD_PROBES`).

Sources read for this guide, fetched 2026-10-29: the OpenAPI document (`00-rest-openapi.json`, sha256
`2a655805b4f150b179845ae0f9124e767000bae39e0c1c2238410919570bcef5`), the General Help page
(https://zbmath.org/general-help/, sha256 `0a089ab3ed9824cb0a661e94f57ba2c749ea3916187b63e39e3576e47beb22de`),
the Tools & Resources page (https://zbmath.org/tools-and-resources/, sha256
`6d4949a173657f164b7119a096cbacd4b49a50866e87cdc0bbab17344e7acc80`), the Guide for Reviewers
(https://zbmath.org/static/guide-for-reviewers-a4.pdf, 6 pages, 2024-10-31, sha256
`19c7cba08ecdd32c6d8300744959c3541a6c43441cacee8136fdddcc6bd4fa1d`) and the OAI-PMH 2.0 specification
(https://www.openarchives.org/OAI/openarchivesprotocol.html, sha256
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
"$PYTHON" scripts/zbmath.py check docs/evidence/zbmath-api-audit
"$PYTHON" scripts/zbmath.py check-fields docs/evidence/zbmath-search-fields/fields.json
```

`match` and `bibtex` send `m=5.0` explicitly, because the service does not apply its documented default.
A successor audit runs `capture --out NEWDIR` and `fields --out NEWFILE`; both refuse an existing record, and
`oai --out DIR` refuses a directory that already holds harvest pages. `search --all` walks the whole
10,000-result window for any `--per-page`, sizing each request to start where the previous one ended.

## Search syntax

The one-line syntax of the REST `/_search` endpoints is the syntax of the zbmath.org search box (General
Help). Operators: `a & b` (and, the default, so a space also means and), `a | b`, `!a`, right wildcard
`abc*`, phrase `"ab c"`, grouping `(a b)`; `py:` and `na:` take ranges `2010-2015`; `cc:*CODE` restricts to
the primary MSC code. A term without a field searches `any`.

The documented field sets of the General Help page and of the OpenAPI descriptions agree exactly. "Probe"
names the result of `fields`: the anchor record plus the field value finds the anchor alone, and a wrong
value finds nothing. A field marked "not probed" is documented and untested.

Documents (`document/_search`; `any` covers ab, au, cc, en, rv, so, ti, ut):

| Field | Meaning | Probe |
|---|---|---|
| `ab` | summary or review text | works; it also matches summaries REST returns as the placeholder |
| `an` | document id: internal, Zbl, JFM or ERAM | anchor of every probe |
| `arxiv` | arXiv identifier | works |
| `au` | author, editor or contributor name | works |
| `br` | person with biographic references | works |
| `cc` | MSC code; `*` prefix restricts to the primary code | works, both forms |
| `ci` | document cited in the summary or review | works with the internal id and with the Zbl id |
| `db` | `Zbl`, `JFM`, `eram`, `arxiv` | works |
| `doi` | DOI | works |
| `dt` | `j` journal article, `a` collection article, `b` book, `p` preprint | works |
| `ed` | editor of a book or special issue | works |
| `en` | external id: DOI, arXiv id, ISBN | works with a DOI |
| `la` | language name or ISO 639-1 code | works, both forms |
| `li` | external link URL | works |
| `na` | number of authors, with ranges | works |
| `pt` | reviewing state: `r`, `t`, `p`, `s`, `n` | works |
| `pu` | publisher | works |
| `py` | publication year, with ranges | works |
| `rft` | text in the reference list | works |
| `rn` | reviewer id | works |
| `rv` | reviewer name or id | works |
| `se` | serial id | works |
| `si` | swMATH software id | works |
| `so` | source: serial, volume, pages, year, ISBN | works |
| `st` | `c` cited, `r` has references, `o` open version | works |
| `sw` | software name | works |
| `ti` | title | works |
| `ut` | keywords | works |
| `st:s` | single author (state code present in records, undocumented) | works |
| `ai` | author code (an author-search field, undocumented for documents) | works |
| `rf` | documents whose reference list contains this internal document id (undocumented) | works with the internal id only; the Zbl id finds nothing |

Authors (`author/_search`; `any` covers ai, au, cc): `ai` code, `au` name including variants and name
changes, `aw` award, `cc` main fields (two MSC digits), `co` collective code, `en` external id (ORCID, MGP,
Wikidata), `fn` given name, `ln` family name, `py` publication years, `rv` reviewer id, `st` (`b` biographic
references, `c` cited, `o` collective, `z` reviewer). Probes: all work; `st:b` and `st:c` are not probed.

Serials (`serial/_search`; `any` covers cc, cy, jt, la, li, pu, sn): `cc` main fields, `cy` country name or
ISO 3166-1 code, `jt` title or acronym, `la` language, `li` URL, `pu` publisher, `py` active years, `se`
serial id, `sn` ISSN (print or electronic), `st` (`o` open access, `v` currently indexed, `t` cover to cover,
`c` cited, `r` has references), `tp` (`j` journal, `b` book series). Probes: all work; `st` probed with `c`.

Software (`software/_search`; `any` covers ab, au, sw, ut): `ab` description (searchable although REST
returns it as the placeholder), `au` author, `cc` main fields, `pl` programming language, `si` swMATH id,
`sw` name, `ut` keywords. Probes: all work.

Classification (`classification/_search`, MSC2020 only): `cc` code with two, three or five characters, `ct`
description text, `lv` level (0 two digits, 1 three characters, 2 five characters), `any`. Probes: all work.

Structured search (`/_structured_search`) takes the field descriptions as parameter names (`Author name`,
`Reference text`, `arXiv ID`, `MSC`) and combines them with and. The OpenAPI examples use names the
endpoints do not accept (`reference_zbmath_id`, `zbmath_id`, `contributor_name` for documents; `author_code`,
`collective`, `in_collective` for authors): a request that carries only those answers HTTP 400 "no parameters
given". Use `_search` with `rf:`, `an:`, `au:`, `ai:` and `co:` instead.

## Combinations

Each recipe uses fields the probes confirmed.

- Forward and backward citations of one paper. `get document ID` returns `references[]`, each with
  `zbmath.document_id` when zbMATH matched it, so the papers it cites resolve by `get`; `search document
  'rf:ID' --all` returns the papers whose reference lists cite it (4 for 6123912, each verified to carry the
  id), and `ci:ID` the papers whose reviews cite it.
- DOI or arXiv id to citation network: `search document 'doi:DOI'` or `'arxiv:ID'` gives the internal id,
  then the forward and backward steps above.
- Free-text reference list to zbMATH ids: `bibtex refs.bib --convert` or `match --bulk queries.json` (up to
  100 per request) returns Zbl ids, which `get` resolves; filter matches on `probability`.
- Author profile to topic slice: `get author CODE` lists `main_fields` (MSC counts) and external ids; then
  `search document 'ai:CODE cc:17'` restricts the author's work to one MSC class.
- Software usage in a field: `search document 'si:537 cc:*17'` lists documents whose primary class is 17 and
  that use Macaulay2; `structured software 'Software name=...'` gives the id and `related_software`.
- Hidden text: `ab:` and software `ab:` match summaries and descriptions that REST returns as the
  placeholder, so a search can select records whose text the API does not return.
- Serial profile: `search serial 'sn:ISSN'` gives the serial id, `get serial ID` the lineage
  (predecessors and successors) and main fields, and `search document 'se:ID py:2020-2026'` its recent
  papers.
- Incremental harvest: `oai ListIdentifiers metadataPrefix=oai_dc set=17 from=LAST` lists new or changed
  records of an MSC class; `oai_zb_preview` adds keywords, author codes and matched references in the same
  pass; REST `get` fills the JSON fields OAI omits.

## REST v1

- Five entities, each with `/{id}`, `/_search`, `/_structured_search`; entity roots return help text.
- Success is `status.execution_bool`: an unknown id answers HTTP 200 with the flag false; a search
  without hits answers HTTP 404; a DOI in the path answers 404, encoded or not; type errors answer the
  framework's 422 `detail` list.
- `results_per_page` is 1..500; `(page+1)*results_per_page` above 10,000 answers 400 "Result window is too
  large". `last_id` is always null and no cursor parameter exists, so OAI-PMH is the only route past 10,000.
- Error envelopes stamp `time_stamp` about one hour ahead of the HTTP `Date` header and without a zone;
  success envelopes stamp UTC with `Z`.
- GET only (HEAD and OPTIONS 405); no compression when gzip is offered; no ETag, Last-Modified or
  Cache-Control; conditional headers ignored; no CORS or rate-limit headers.
- On the 40 records of the `sedenion` query, 20 of 39 editorial contributions are the placeholder, all of
  them summaries or editorial notes; none of the 4 zbMATH reviews is. The per-record `license` field is the
  article's license and is empty on 29 of the 40.
- Documentation UI: `https://api.zbmath.org/` serves the terms form; agreeing redirects to
  `/?tnc_agreed=1`, which sets a 30-day `tsnc` cookie and serves Swagger UI 3.52.5 over `/v1/openapi.json`.
  No API endpoint needs the cookie. `/docs` and `/redoc` redirect to `/v1/docs` and `/v1/redoc`, which
  answer the JSON 404 envelope.

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

## Web tools

- Author profiles and disambiguation, https://zbmath.org/author-profile/ and `https://zbmath.org/authors/CODE`:
  HTML; REST `author/{code}` carries the same profile data.
- Collaboration distance, `https://zbmath.org/collaboration-distance/?a=CODE&b=CODE`: answers
  `{"distance", "source", "target"}` to a request with `Accept: application/json`, with distance -1 and a
  null side for an unresolved code, distance 0 for one author, and the target canonicalized (`erdos.paul`
  becomes `erdos.pal`); names instead of codes do not resolve and no path is returned. Cloudflare answers
  a "Just a moment" challenge with HTTP 403 to this path for scripted User-Agents, including this client's,
  while curl's passes. The endpoint is a website tool, not part of the API, so the client does not call it.
- Citation matching and the BibTeX interface, https://zbmath.org/citationmatching/ and `/bibtex`: HTML
  forms over the citation matcher API above.

## Falsification of the deviations

Each deviation below was tested against the alternative that the client, the operator or the request
caused it. Every row up to the citation matcher was reproduced a second time outside `scripts/zbmath.py`,
by a curl 8.23.0 run at 2026-10-29T14:59Z that recorded each HTTP status and the deciding field; that
transcript accompanies the pull request that added this guide. A deviation enters a report to FIZ
Karlsruhe only with the verdict "service" and its capture name. The unsent draft of that report, with a
falsifier for every item, is [upstream-report.md](upstream-report.md).

| Deviation | Alternative tested | Test | Verdict |
|---|---|---|---|
| unknown REST id answers HTTP 200 with `execution_bool` false | client path quoting | ids `99999999999` and `abc` | service |
| search without hits answers HTTP 404 | malformed query | word query `zzqqxxnotaword` and empty query both 404 | service; API design, no standard violated |
| result window 10,000 and page size 1..500 | page arithmetic in the client | 100x100, 500x20 and 1x10,000 fail; 1x9,999 passes; 501 fails | service; no `page` or `results_per_page` schema in the OpenAPI document states a minimum or maximum, and no endpoint description names either bound, although the description promises endpoint-specific limits |
| `last_id` always null | a cursor appears on deep pages | null on every capture; the OpenAPI example envelope shows `"last_id": 1000000` beside `"internal_code": "dev id to find bugs"` | service; documentation example only |
| structured-search examples use unaccepted names | names are aliases | each alone answers "no parameters given" | service; documentation |
| `/docs` and `/redoc` answer 404 | the docs need the terms cookie | with and without the cookie both answer 404; the Swagger UI lives at `/?tnc_agreed=1` | service |
| DOI in path answers 404 | slash not encoded | `%2F`-encoded DOI also 404 | service; route takes no slash |
| no gzip on REST | client did not offer gzip | `curl --compressed` returns the uncompressed 10,424 bytes | service |
| no validator headers despite "cacheable" | wording means client-side caching | none possible | interpretive; report as a question |
| error `time_stamp` without zone, 1 h ahead of UTC | clock skew | the error stamp `16:28:33.197` reads one hour later than the UTC success stamp `15:28:34Z` of the request one second after it; the HTTP `Date` header reads `15:28:27` on both answers, about 6 s behind the service clock, which explained the earlier 8 s spread | service; the zone is inferred as CET (UTC+1 after 2026-10-25) |
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
| REST replaces the summary of a CC BY 4.0 article with the placeholder | the record's license is restrictive | document 6123912 carries `license` CC BY 4.0, its REST summary is the placeholder, and its OAI summary was served once | question for FIZ; their publisher agreements may decide it |
| collaboration distance returns 403 | the endpoint is down or needs a cookie | the same request passes with curl's User-Agent and fails with this client's and with Python's default | site policy (bot challenge), not an API defect; not reported |

Two candidate findings did not survive: "agreeing to the terms sets no cookie" (the 303 answer to the form
sets none, the page it redirects to does) and "OAI-PMH requires HTTP 200 for errors" (section 3.1.2.2 does
not say so).

## Other resources

GitHub (https://github.com/zbMATHOpen): `zbmath-open-kg` (RDF knowledge graph, ontology, temporary SPARQL
endpoint), `zbRestApiClient` (Swagger client generated for API v0.4.3rc0, stale against 1.9.33),
`mscHarvester`, `linksApi`. Zenodo community `zbmath` (18 records): identifier mapping zbMATH/DOI/ORCID/arXiv
(CC BY-SA 4.0, 114 MB), swMATH-zbMATH links, open-access subset, MSC dataset, OCR of volumes 1-529.

Reviewer material: the Guide for Reviewers asks for standard LaTeX without self-defined macros (compiled
with XeLaTeX) and cites other items as "Acta Math. 119, 147--171 (1967; Zbl 0156.10701)", the form that
makes `ci:` searchable; the reviewer service, https://zbmath.org/reviewer-service/; Become a Reviewer,
https://zbmath.org/become-a-reviewer/; the CTAN template `zbmath-review-template`; the zbNEWS newsletters
17 to 21 under https://zbmath.org/static/newsletter/.

Partners: MathOverflow `zbmath` tag, DLMF, OEIS, ATLAS of Group Representations, Software Heritage. Other
resources: the Wikimedia Community User Group Math, the MaRDI portal, EOSC/FAIRCORE4EOSC mathematics case
studies, the W3C Math Working Group.
