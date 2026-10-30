# zbMATH Open interface report (draft, unsent)

Status: draft, held for falsification; nothing has been sent to FIZ Karlsruhe. The owner approves the text and
the channel before any message leaves the repository. Two messages follow, one per channel: message A to
`api@zbmath.org` (REST API and citation matcher, the contact the OpenAPI document names) and message B to
`repo.admin@zbmath.org` (OAI-PMH, the `adminEmail` of its Identify answer).

Every item cites a capture of the audit retained at merge commit `a9956e3`
([evidence/zbmath-api-audit](../../evidence/zbmath-api-audit/README.md)) and the deviation analysis of the
[guide](README.md#falsification-of-the-deviations). An item enters a sent message only after its falsifier
below has been run on the day of sending and has failed to falsify it.

Neither message is needed by this repository: `scripts/zbmath.py` already handles every behavior below
(`check_window` enforces the paging bounds, `envelope` reads `execution_bool` rather than the HTTP status,
`oai_parse` takes the OAI error code from the element text, and `run_match` and `run_bibtex` send `m` explicitly).
An upstream fix changes no current result here. Three items would add content or reach for this repository:
A7 (the matcher honoring its documented default), A9 and B9 (summaries now withheld behind the license
placeholder), and B4 (a harvestable `openaire` set). The remaining items benefit other clients, generated
code and validators. Sending is therefore a courtesy the owner may decline, and the record stands as the
audit's reconciliation either way.

A message cites only retained bytes. A behavior verified by curl but absent from the retained captures
carries its reproduction line and the words "not among the retained captures".

## Falsification ledger

Before sending: run `"$PYTHON" scripts/zbmath.py capture --out docs/evidence/zbmath-api-audit-SENDDATE` and
`check` on it (named by the send date, since a capture directory is immutable), rerun the curl lines of each
item, and search https://zbmath.org/general-help/, https://zbmath.org/faq/ and the OpenAPI descriptions for
the behavior. An item whose finding no longer holds, or that turns out to be documented, leaves the message.

| Item | Claim | Falsifier | Status |
|---|---|---|---|
| A1 | the OpenAPI document states neither the page-size range 1..500 nor the 10,000-result window | a `minimum`/`maximum` in a `page` or `results_per_page` schema, or the bounds named in an endpoint description or help page | open |
| A2 | the `_structured_search` examples use parameter names the endpoints ignore (the name mismatch is in capture 00; the ignored-name responses are curl-only, not retained) | any of `reference_zbmath_id`, `zbmath_id`, `contributor_name`, `author_code`, `collective`, `in_collective` returning results alone | open |
| A3 | `last_id` is null on every answer while the OpenAPI example shows 1000000 | a non-null `last_id` on any request, or a request parameter that consumes it | open |
| A4 | `/docs` redirects to a 404 envelope (capture 57); `/redoc` and the with-cookie variant are curl-only, not retained | `/docs` serving the Swagger page | open |
| A5 | error envelopes stamp `time_stamp` in local time without a zone | an error `time_stamp` within seconds of the UTC `time_stamp` of an adjacent success answer, or carrying a zone | open |
| A6 | an unknown id answers HTTP 200 while a search without hits answers HTTP 404 | the two status codes agreeing on the send date | open |
| A7 | the citation matcher returns hits below its documented default minimum score 5.0 when `m` is absent | a request without `m` returning only scores of 5.0 or more for a query that yields lower-scored hits with `m=0` | open |
| A8 | `rf:`, `st:s` and `ai:` work in document search and are undocumented; the matcher returns undocumented `probability` and `arxiv_id` | any of them listed in the General Help page, the OpenAPI descriptions or the matcher PDF | open |
| A9 | the summary of document 6123912, whose `license` field is CC BY 4.0, is the placeholder in REST | the REST record serving the summary, or the `license` field changing | open; a question |
| B1 | the first resumptionToken carries `cursor="100"` | `cursor="0"` on the first page of a list | open |
| B2 | `earliestDatestamp` is the bare year `1755` | a full `YYYY-MM-DDThh:mm:ssZ` value | open |
| B3 | a month `from` and a mixed-granularity `from`/`until` are accepted | `badArgument` for either request | open |
| B4 | an unknown set (capture 44), and the advertised `openaire` set in ListIdentifiers `oai_dc` (capture 51), answer `invalid set`; the ListRecords and `oai_zb_preview` variants are curl-only, not retained | a protocol error code, or records for `openaire` | open |
| B5 | a resumptionToken not shaped as a UUID answers an HTML HTTP 500 | `badResumptionToken` for `deadbeef` | open |
| B6 | the `oai_zb_preview` schema URL is relative and resolves to 404 against the base URL | an absolute schema URL, or the schema served under `/v1/static/` | open |
| B7 | absent values print as the string `None` in `oai_dc` and `oai_zb_preview` | empty or omitted elements for the absent contributor and reviewer of 6123912 | open |
| B8 | OAI errors carry HTTP 400 or 404 | HTTP 200 on error answers | withheld from message B: section 3.1.2.2 permits non-200 codes, so the point is advice, not conformance |
| B9 | the `oai_zb_preview` summary of 6123912 was served in the 13:54:39Z observation and the placeholder in the later capture 34 | the summary served again | open; a question, labeled B8 in message B |

Withheld, with the reason: DOI in the REST path (route design; `doi:` search serves it), HEAD and OPTIONS
405, absent compression, validator, CORS and rate-limit headers on REST (design choices with no stated
contract), the Cloudflare challenge on the collaboration-distance page (site policy for a web tool), the
missing cursor beyond 10,000 REST results (OAI-PMH serves bulk access), and HTTP 400/404 on OAI errors (B8,
permitted by section 3.1.2.2).

## Message A: REST API and citation matcher

To: `api@zbmath.org`
Subject: zbMATH Open REST API 1.9.33 and citation matcher: documentation points and three questions

> Dear zbMATH Open API team,
>
> The zbMATH Open REST API (OpenAPI version 1.9.33) and the citation matcher (Script API v1.6.26) serve a
> literature audit for research on Cayley-Dickson algebras. A pass over each endpoint and the documented search
> fields on 2026-10-29 found the interfaces robust and well suited to citation work. Nine observations concern
> documentation and a few response conventions; each links the retained raw response and gives a one-line
> reproduction.
>
> **A1. Paging bounds.** `results_per_page` accepts 1 to 500 and `(page + 1) * results_per_page` may not
> exceed 10,000; requests outside answer HTTP 400 with clear messages ("between 1 and 500", "Result window is
> too large"). The OpenAPI schemas of `page` and `results_per_page` carry no `minimum` or `maximum`, and the
> endpoint descriptions name neither bound, while the API description announces endpoint-specific limits.
> Stating both bounds in the schemas would let generated clients validate locally.
> `curl 'https://api.zbmath.org/v1/document/_search?search_string=cc:17&results_per_page=501'` and
> `curl 'https://api.zbmath.org/v1/document/_search?search_string=cc:17&page=10000&results_per_page=1'`
> (captures 14 and 16).
>
> **A2. Structured-search examples.** The examples of `/document/_structured_search` and
> `/author/_structured_search` use `reference_zbmath_id`, `zbmath_id`, `contributor_name`, `author_code`,
> `collective` and `in_collective`, while the same document declares the parameters under descriptive names
> (`Reference text`, `Author name`, `Collective code`, ...) (capture 00). A request carrying only an example
> name answers "no parameters given", the answer of an empty request (capture 19); the example-name
> response itself is not among the retained captures:
> `curl 'https://api.zbmath.org/v1/document/_structured_search?zbmath_id=6383667'`.
>
> **A3. `last_id`.** Every retained answer carries `"last_id": null`; the example response in the OpenAPI document shows
> `"last_id": 1000000` beside `"internal_code": "dev id to find bugs"`. A sentence on the intended meaning of
> `last_id`, or its removal from the example, would settle how clients should treat it (capture 00).
>
> **A4. Documentation path.** `https://api.zbmath.org/docs` redirects to `/v1/docs`, which answers the JSON
> 404 envelope; the Swagger page itself lives at `https://api.zbmath.org/?tnc_agreed=1` (captures 57 and
> 58).
>
> **A5. Time stamps.** Success envelopes stamp `time_stamp` in UTC with a `Z` suffix
> (`2026-10-29T15:28:34Z`); error envelopes stamp local time without a zone and with a space separator
> (`2026-10-29 16:28:33.197009`, from the request one second earlier). One UTC format throughout would make
> the two comparable (captures 05 and 06).
>
> **A6. Status codes.** An unknown identifier answers HTTP 200 with `execution_bool` false, and a search
> without hits answers HTTP 404. The reverse pairing is the common HTTP convention; whichever convention the
> API keeps, a sentence in the description would guide clients (captures 05 and 09).
> `curl -w '%{http_code}' 'https://api.zbmath.org/v1/document/99999999999'` and
> `curl -w '%{http_code}' 'https://api.zbmath.org/v1/document/_search?search_string=zzqqxxnotaword'`.
>
> **A7. Citation matcher default score.** The Script API PDF gives `m` a default of 5.0. A `match` request
> without `m` returns hits scored 0.0, and the same request with `m=5` returns only the hit scored 15.0
> (captures 52 and 53). The matcher also returns `probability` and, for arXiv-linked items, `arxiv_id`, both
> useful and absent from the PDF.
>
> **A8. Undocumented search fields.** Three fields work in document search and appear in neither the General
> Help page nor the OpenAPI descriptions: `rf:ID` returns the documents whose reference lists contain the
> document with internal id `ID` (`rf:6123912` returns four, each carrying that id in `references`), `st:s`
> selects single-author items (a state code present in records), and `ai:CODE` selects an author's documents.
> All three are valuable for citation analysis, and listing them would make them discoverable. The field
> probes are retained in
> [`zbmath-search-fields/fields.json`](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/a9956e3/docs/evidence/zbmath-search-fields/fields.json).
>
> **Question A9.** Document 6123912 (Adv. Appl. Clifford Algebr. 22, 757-769, 2012) carries
> `license: ["https://creativecommons.org/licenses/by/4.0/"]` in REST, and its summary is the placeholder
> "zbMATH Open Web Interface contents unavailable due to conflicting licenses." Is the summary of an article
> under CC BY 4.0 withheld by agreement with the publisher, or could it be served (capture 02)?
>
> The raw responses, their headers and an offline replay of every observation are public at
> https://github.com/Oichkatzelesfrettschen/gororoba-quantum/tree/a9956e3/docs/evidence/zbmath-api-audit
> (captures named by number). Thank you for maintaining zbMATH Open and its open interfaces.
>
> With kind regards,
> OWNER NAME

## Message B: OAI-PMH

To: `repo.admin@zbmath.org`
Subject: zbMATH Open OAI-PMH (https://oai.zbmath.org/v1/): conformance points against OAI-PMH 2.0

> Dear zbMATH Open repository administrators,
>
> The zbMATH Open OAI-PMH interface serves incremental harvests by MSC class for a research literature audit.
> A conformance pass on 2026-10-29 against the OAI-PMH 2.0 specification
> (https://www.openarchives.org/OAI/openarchivesprotocol.html) found the verbs, both metadata formats and
> resumption working. Six conformance points, a metadata-quality point and a question each cite the clause
> concerned and the retained raw response.
>
> **B1. Cursor.** The first ListIdentifiers page returns `<resumptionToken completeListSize="135"
> cursor="100">`. Section 3.5 defines `cursor` as "a count of the number of elements of the complete list thus
> far returned (i.e. cursor starts at 0)", so the first page carries 0 and the second 100 (capture 36).
> `curl -s 'https://oai.zbmath.org/v1/?verb=ListIdentifiers&metadataPrefix=oai_dc&set=17&from=2026-10-01T00:00:00Z' | grep -o '<resumptionToken[^>]*>'`.
>
> **B2. earliestDatestamp.** Identify returns `<earliestDatestamp>1755</earliestDatestamp>` with granularity
> `YYYY-MM-DDThh:mm:ssZ`. Section 4.2 requires earliestDatestamp at the finest supported granularity, and the
> schema type `UTCdatetimeType` admits a date or a `Z` date-time; `1755-01-01T00:00:00Z` satisfies both
> (capture 30).
>
> **B3. Argument granularity.** Section 3.3.1 names `YYYY-MM-DD` and `YYYY-MM-DDThh:mm:ssZ` as the legitimate
> formats and requires `from` and `until` to share one granularity. A month value (`from=2026-10`) and a mixed
> pair (`from=2026-10-27&until=2026-10-27T23:59:59Z`) both return records, where `badArgument` is the
> specified answer (captures 42 and 45; an unparseable value already returns `badArgument`, capture 41).
>
> **B4. Sets.** An unknown set returns `<error code="400">invalid set</error>`; section 3.6 lists the error
> codes, and `badArgument` fits an illegal set. ListSets advertises `openaire` ("Required set for OpenAIRE"),
> and a ListIdentifiers request naming it returns the same `invalid set` (captures 32, 44 and 51). Should
> `openaire` remain advertised?
>
> **B5. Malformed resumptionToken.** A token outside the UUID shape (`resumptionToken=deadbeef`) returns an
> HTML "500 Internal Server Error" page, while an unknown UUID-shaped token returns `badResumptionToken`
> as specified. The same code for both keeps harvesters on the protocol path (captures 46 and 47).
>
> **B6. Schema URL.** ListMetadataFormats gives the `oai_zb_preview` schema as `static/oai_zb_preview.xsd`.
> Section 3.4 calls for the URL of the schema; resolved against the base URL it becomes
> `https://oai.zbmath.org/v1/static/oai_zb_preview.xsd`, which answers 404, while
> `https://oai.zbmath.org/static/oai_zb_preview.xsd` serves the schema. An absolute URL would let validators
> fetch it (captures 31, 48 and 49).
>
> **B7. Absent values.** GetRecord for `oai:zbmath.org:6123912` prints `<dc:contributor>None</dc:contributor>`
> in `oai_dc` and `<zbmath:reviewer>None</zbmath:reviewer>`, `<zbmath:reviewer_id>None</zbmath:reviewer_id>`
> and `<zbmath:review_sign>None</zbmath:review_sign>` in `oai_zb_preview`, where the record has no such value;
> omitting the element keeps "None" from entering harvested metadata as a name (captures 33 and 34).
>
> **Question B8.** At 2026-10-29T13:54:39Z, GetRecord in `oai_zb_preview` for `oai:zbmath.org:6123912` served
> the full summary of the article; the later capture at 15:29:28Z served the license placeholder. Which of the
> two reflects the intended state of that record?
>
> The raw responses and an offline replay of every point are public at
> https://github.com/Oichkatzelesfrettschen/gororoba-quantum/tree/a9956e3/docs/evidence/zbmath-api-audit
> (captures named by number). Thank you for running a harvestable zbMATH Open.
>
> With kind regards,
> OWNER NAME
