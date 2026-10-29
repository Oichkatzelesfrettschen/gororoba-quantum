"""zbMATH Open client: REST lookups and searches, OAI-PMH harvesting, citation matching and the API audit capture.

FIZ Karlsruhe serves three keyless HTTP interfaces under the zbMATH Open API
terms (https://static.zbmath.org/legal/api-terms-and-conditions.html), which
ask for a "reasonable" request rate without naming one. Every request here
waits until MIN_INTERVAL seconds have passed since the previous one and
retries 500, 502, 503 and 504 answers RETRIES times with doubling back-off.

- REST v1, https://api.zbmath.org/v1 (OpenAPI document at /v1/openapi.json):
  documents, authors, serials, software and MSC2020 classifications, each
  through /{id}, /_search (the zbMATH query syntax) and /_structured_search
  (named fields). A page holds 1 to 500 results and page * results_per_page
  + results_per_page may not exceed RESULT_WINDOW, so a result set larger
  than the window is reachable only through OAI-PMH. Success is the envelope
  flag status.execution_bool, not the HTTP code: an unknown id answers HTTP
  200 with the flag false, and a search without hits answers HTTP 404.
- OAI-PMH 2.0, https://oai.zbmath.org/v1/: oai_dc and oai_zb_preview records
  in sets named by two-digit MSC classes, 100 headers per page under a
  resumptionToken. Protocol errors arrive with HTTP 400 or 404, which OAI-PMH
  2.0 section 3.1.2.2 reserves for the transport layer, so the client reads
  the <error> element whatever the HTTP code.
- Citation matching, https://zbmath.org/citationmatching/ (Script API PDF
  v1.6.26): match (GET, or POST with up to 100 queries), bibtex/match and
  bibtex/convert_file. The service does not apply its documented default
  minimum score, so match and bibtex always send m.

Subcommands (all but check, check-fields and --self-test reach the network):

- get ENTITY ID; search ENTITY QUERY; structured ENTITY FIELD=VALUE...
  print the REST result list as JSON; --page and --per-page select a page,
  --all walks every page inside the result window.
- oai VERB [ARG=VALUE...] prints one OAI-PMH response; with --out DIR it
  follows resumptionTokens and writes page-NNNN.xml files into DIR.
- match QUERY [-n N] [-m SCORE], match --bulk FILE.json, bibtex FILE and
  bibtex FILE --convert call the citation matcher.
- fields --out FILE runs FIELD_PROBES, a positive and a negative query per
  one-line search field against an anchor record, and check-fields FILE
  (offline) requires every positive to find the anchor alone and every
  negative to find nothing.
- capture --out DIR runs the fixed request inventory CAPTURES, writes each
  response's raw bytes and MANIFEST.json (URL, method, HTTP status, content
  type, sha256), then runs check. A directory holding a MANIFEST.json is
  retained evidence and is refused.
- check DIR (offline) requires the file set to equal the manifest, the
  manifest to equal CAPTURES in order, every sha256 to match, and every
  finding in FINDINGS to hold on the retained bytes, so a re-capture that
  fails check names the behavior the service changed.
- --self-test requires check to reject an altered byte, a removed file, an
  unlisted file, a changed URL, a flipped HTTP status, an added ETag and an
  altered observation, check-fields to reject a negative control that found
  documents, and the pure helpers to classify synthetic envelopes and OAI
  errors.

Usage: "$PYTHON" scripts/zbmath.py COMMAND ... | --self-test, COMMAND one of get, search, structured,
oai, match, bibtex, capture, check, fields, check-fields
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "docs/evidence/zbmath-api-audit"
SCHEMA = "zbmath-api-capture-v1"
REST = "https://api.zbmath.org/v1"
OAI = "https://oai.zbmath.org/v1/"
CITATION = "https://zbmath.org/citationmatching"
ENTITIES = ("document", "author", "serial", "software", "classification")
USER_AGENT = "gororoba-quantum-zbmath (+https://github.com/Oichkatzelesfrettschen/gororoba-quantum)"
PLACEHOLDER = "zbMATH Open Web Interface contents unavailable due to conflicting licenses."
NO_RESULTS = "successful access. No results found."
MAX_PER_PAGE = 500
RESULT_WINDOW = 10_000
MIN_INTERVAL = 1.0
RETRIES = 3
RETRY_STATUS = frozenset({500, 502, 503, 504})
OAI_NS = {"o": "http://www.openarchives.org/OAI/2.0/"}
EXTENSIONS = {"json": ".json", "xml": ".xml", "html": ".html", "bibtex": ".bib", "octet-stream": ".xsd"}


class ZbmathError(RuntimeError):
    """A request the service refused, or an answer the client cannot read."""


@dataclass(frozen=True)
class Reply:
    url: str
    method: str
    status: int
    headers: dict[str, str]
    body: bytes
    elapsed: float

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "").split(";")[0].strip() or "application/octet-stream"


class Transport:
    """Paced HTTP client: one request per MIN_INTERVAL, retries on RETRY_STATUS unless the caller expects it.

    Every request offers gzip; OAI-PMH compresses its answers and REST does not. A gzip body is decompressed,
    so Reply.body holds the payload bytes and Reply.headers keeps the Content-Encoding the server sent.
    """

    def __init__(self, interval: float = MIN_INTERVAL, retries: int = RETRIES) -> None:
        self.interval = interval
        self.retries = retries
        self._last = 0.0

    def send(
        self,
        url: str,
        method: str = "GET",
        body: bytes | None = None,
        content_type: str | None = None,
        expect: int | None = None,
        extra: tuple[tuple[str, str], ...] = (),
    ) -> Reply:
        headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip", **dict(extra)}
        if content_type:
            headers["Content-Type"] = content_type
        for attempt in range(self.retries + 1):
            wait = self._last + self.interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            start = time.monotonic()
            request = urllib.request.Request(url, data=body, method=method, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    status, received, payload = response.status, response.headers, response.read()
            except urllib.error.HTTPError as error:
                with error:
                    status, received, payload = error.code, error.headers, error.read()
            finally:
                self._last = time.monotonic()
            fields = {key.lower(): value for key, value in received.items()}
            if fields.get("content-encoding", "").lower() == "gzip":
                payload = gzip.decompress(payload)
            reply = Reply(url, method, status, fields, payload, self._last - start)
            if reply.status not in RETRY_STATUS or reply.status == expect or attempt == self.retries:
                return reply
            time.sleep(2.0 ** (attempt + 1))
        raise ZbmathError("unreachable")


def rest_url(path: str, params: dict[str, Any] | None = None) -> str:
    query = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v is not None})
    return f"{REST}/{path}" + (f"?{query}" if query else "")


def check_window(page: int, per_page: int) -> None:
    """Refuse a page the REST service answers with HTTP 400 before sending it."""
    if not 1 <= per_page <= MAX_PER_PAGE:
        raise ZbmathError(f"results_per_page {per_page} lies outside 1..{MAX_PER_PAGE}")
    if page < 0:
        raise ZbmathError(f"page {page} is negative")
    if (page + 1) * per_page > RESULT_WINDOW:
        raise ZbmathError(
            f"page {page} at {per_page} per page ends past the {RESULT_WINDOW}-result window; harvest through OAI-PMH"
        )


def envelope(status: int, body: bytes) -> tuple[Any, dict[str, Any]]:
    """Return (result, status block) of a REST answer; a search without hits yields an empty list."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError as error:
        raise ZbmathError(f"HTTP {status}: body is not JSON: {body[:120]!r}") from error
    if status == 422:
        raise ZbmathError(f"HTTP 422: {data.get('detail')}")
    block = data.get("status") if isinstance(data, dict) else None
    if not isinstance(block, dict):
        raise ZbmathError(f"HTTP {status}: answer carries no status block")
    if block.get("execution_bool") is True:
        return data["result"], block
    if block.get("internal_code") == NO_RESULTS:
        return [], block
    raise ZbmathError(f"HTTP {status}: {block.get('execution')} {block.get('internal_code')}")


def rest(transport: Transport, path: str, params: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
    reply = transport.send(rest_url(path, params))
    return envelope(reply.status, reply.body)


def rest_pages(transport: Transport, path: str, params: dict[str, Any], per_page: int) -> Iterator[dict[str, Any]]:
    """Yield every result inside the result window, page by page."""
    page = 0
    seen = 0
    while True:
        check_window(page, per_page)
        result, block = rest(transport, path, {**params, "page": page, "results_per_page": per_page})
        yield from result
        seen += len(result)
        total = block.get("nr_total_results") or 0
        if not result or seen >= total:
            return
        if (page + 2) * per_page > RESULT_WINDOW:
            print(
                f"zbmath: {total} results exceed the {RESULT_WINDOW}-result window; stopped at {seen}", file=sys.stderr
            )
            return
        page += 1


def oai_parse(body: bytes) -> tuple[ET.Element, str | None, str | None]:
    """Return (root, OAI error code or None, non-empty resumptionToken or None)."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as failure:
        raise ZbmathError(f"OAI answer is not XML: {body[:120]!r}") from failure
    error = root.find("o:error", OAI_NS)
    code = None
    if error is not None:
        # zbMATH puts the HTTP status in the code attribute and the protocol code in the element text.
        code = error.get("code") or ""
        if not code[:1].isalpha():
            code = (error.text or "").strip()
    node = root.find(".//o:resumptionToken", OAI_NS)
    token = (node.text or "").strip() if node is not None else ""
    return root, code, token or None


def multipart(field: str, filename: str, payload: bytes, mime: str) -> tuple[bytes, str]:
    boundary = f"zbmath-{uuid.uuid4().hex}"
    head = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode()
    return head + payload + f"\r\n--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


# ---- capture inventory and findings


@dataclass(frozen=True)
class Probe:
    name: str
    url: str
    method: str = "GET"
    body: str | None = None
    content_type: str | None = None
    expect: int | None = None
    headers: tuple[tuple[str, str], ...] = ()


def _oai(**params: str) -> str:
    return OAI + "?" + urllib.parse.urlencode(params)


def _cite(path: str, **params: str) -> str:
    return f"{CITATION}/{path}" + ("?" + urllib.parse.urlencode(params) if params else "")


BIBTEX = (
    "@article{moreno1998, title={The zero divisors of the {C}ayley-{D}ickson algebras over the real numbers}, "
    "author={Moreno, Guillermo}, journal={Bol. Soc. Mat. Mex.}, year={1998}}\n"
)
CITE = (
    "J. Lawrynowicz, O. Suzuki, A. Niemczynowicz, On the ternary approach to Clifford structures and Ising "
    "lattices, Adv. Appl. Clifford Algebr. 22 (2012) 757-769"
)
BULK = json.dumps(
    {
        "queries": [
            {"q": "Moreno, The zero divisors of the Cayley-Dickson algebras over the real numbers, 1998"},
            {"t": "zzqq nonexistent title", "a": ["Nobody"]},
        ]
    }
)
FORM_BOUNDARY = "zbmath-capture-boundary"
FORM = (
    f'--{FORM_BOUNDARY}\r\nContent-Disposition: form-data; name="bibtex_file"; filename="moreno.bib"\r\n'
    f"Content-Type: application/x-bibtex\r\n\r\n{BIBTEX}\r\n--{FORM_BOUNDARY}--\r\n"
)

CAPTURES = (
    Probe("rest-openapi", f"{REST}/openapi.json"),
    Probe("rest-document-intro", f"{REST}/document/"),
    Probe("rest-document-by-internal-id", rest_url("document/6123912")),
    Probe("rest-document-by-zbl-id", rest_url("document/1257.82097")),
    Probe("rest-document-by-doi-path", rest_url("document/10.1007/s00006-012-0360-6")),
    Probe("rest-document-unknown-id", rest_url("document/99999999999")),
    Probe("rest-document-search", rest_url("document/_search", {"search_string": "sedenion", "results_per_page": 100})),
    Probe("rest-document-search-doi", rest_url("document/_search", {"search_string": "doi:10.1007/s00006-012-0360-6"})),
    Probe("rest-document-search-arxiv", rest_url("document/_search", {"search_string": "arxiv:math/0511691"})),
    Probe("rest-document-search-no-hits", rest_url("document/_search", {"search_string": "zzqqxxnotaword"})),
    Probe("rest-document-search-missing-query", rest_url("document/_search")),
    Probe("rest-document-search-page-not-integer", rest_url("document/_search", {"search_string": "x", "page": "x"})),
    Probe("rest-document-search-page-negative", rest_url("document/_search", {"search_string": "x", "page": -1})),
    Probe(
        "rest-document-search-per-page-zero",
        rest_url("document/_search", {"search_string": "x", "results_per_page": 0}),
    ),
    Probe(
        "rest-document-search-per-page-501",
        rest_url("document/_search", {"search_string": "x", "results_per_page": 501}),
    ),
    Probe(
        "rest-document-search-window-last",
        rest_url("document/_search", {"search_string": "cc:17", "page": 9999, "results_per_page": 1}),
    ),
    Probe(
        "rest-document-search-window-past",
        rest_url("document/_search", {"search_string": "cc:17", "page": 10000, "results_per_page": 1}),
    ),
    Probe(
        "rest-document-structured-doi", rest_url("document/_structured_search", {"DOI": "10.1007/s00006-012-0360-6"})
    ),
    Probe(
        "rest-document-structured-title-year",
        rest_url("document/_structured_search", {"Title": "sedenion", "Year": "2000-2026", "results_per_page": 3}),
    ),
    Probe("rest-document-structured-empty", rest_url("document/_structured_search")),
    Probe("rest-author-by-code", rest_url("author/bourbaki.nicolas")),
    Probe("rest-author-structured", rest_url("author/_structured_search", {"Family name": "Cawagas"})),
    Probe("rest-classification-by-code", rest_url("classification/17A35")),
    Probe("rest-classification-level-0", rest_url("classification/_structured_search", {"Level": "0"})),
    Probe("rest-serial-by-id", rest_url("serial/3191")),
    Probe("rest-serial-search-issn", rest_url("serial/_search", {"search_string": "sn:0003-486X"})),
    Probe("rest-software-structured", rest_url("software/_structured_search", {"Software name": "Macaulay2"})),
    Probe("rest-head-method", rest_url("document/6123912"), method="HEAD"),
    Probe(
        "rest-conditional-cross-origin",
        rest_url("document/6123912"),
        headers=(
            ("If-None-Match", '"6123912"'),
            ("If-Modified-Since", "Thu, 01 Jan 2099 00:00:00 GMT"),
            ("Origin", "https://example.org"),
        ),
    ),
    Probe(
        "rest-cors-preflight",
        rest_url("document/6123912"),
        method="OPTIONS",
        headers=(("Origin", "https://example.org"), ("Access-Control-Request-Method", "GET")),
    ),
    Probe("oai-identify", _oai(verb="Identify")),
    Probe("oai-list-metadata-formats", _oai(verb="ListMetadataFormats")),
    Probe("oai-list-sets", _oai(verb="ListSets")),
    Probe("oai-get-record-dc", _oai(verb="GetRecord", metadataPrefix="oai_dc", identifier="oai:zbmath.org:6123912")),
    Probe(
        "oai-get-record-zb-preview",
        _oai(verb="GetRecord", metadataPrefix="oai_zb_preview", identifier="oai:zbmath.org:6123912"),
    ),
    Probe(
        "oai-list-identifiers-set-window",
        _oai(
            verb="ListIdentifiers",
            metadataPrefix="oai_dc",
            set="17",
            **{"from": "2026-10-27T00:00:00Z", "until": "2026-10-27T23:59:59Z"},
        ),
    ),
    Probe(
        "oai-list-identifiers-paged",
        _oai(verb="ListIdentifiers", metadataPrefix="oai_dc", set="17", **{"from": "2026-10-01T00:00:00Z"}),
    ),
    Probe("oai-error-bad-verb", _oai(verb="Nope")),
    Probe(
        "oai-error-bad-format",
        _oai(verb="GetRecord", metadataPrefix="marc", identifier="oai:zbmath.org:6123912"),
    ),
    Probe(
        "oai-error-unknown-id",
        _oai(verb="GetRecord", metadataPrefix="oai_dc", identifier="oai:zbmath.org:999999999"),
    ),
    Probe(
        "oai-error-no-match", _oai(verb="ListIdentifiers", metadataPrefix="oai_dc", **{"from": "2099-01-01T00:00:00Z"})
    ),
    Probe("oai-error-bad-date", _oai(verb="ListIdentifiers", metadataPrefix="oai_dc", set="17", **{"from": "garbage"})),
    Probe(
        "oai-month-date-accepted",
        _oai(verb="ListIdentifiers", metadataPrefix="oai_dc", set="17", **{"from": "2026-10"}),
    ),
    Probe("oai-error-missing-prefix", _oai(verb="ListIdentifiers", set="17")),
    Probe("oai-error-bad-set", _oai(verb="ListIdentifiers", metadataPrefix="oai_dc", set="zz")),
    Probe(
        "oai-mixed-granularity-accepted",
        _oai(
            verb="ListIdentifiers",
            metadataPrefix="oai_dc",
            set="17",
            **{"from": "2026-10-27", "until": "2026-10-27T23:59:59Z"},
        ),
    ),
    Probe("oai-error-bad-token", _oai(verb="ListIdentifiers", resumptionToken="deadbeef"), expect=500),
    Probe(
        "oai-error-unknown-uuid-token",
        _oai(verb="ListIdentifiers", resumptionToken="00000000-0000-0000-0000-000000000000"),
    ),
    Probe("oai-zb-preview-schema", "https://oai.zbmath.org/static/oai_zb_preview.xsd"),
    Probe("oai-zb-preview-schema-relative", "https://oai.zbmath.org/v1/static/oai_zb_preview.xsd"),
    Probe("oai-zb-preview-imported-schema", "https://oai.zbmath.org/static/simplezbmath20200901.xsd"),
    Probe(
        "oai-error-openaire-set",
        _oai(verb="ListIdentifiers", metadataPrefix="oai_dc", set="openaire", **{"from": "2026-10-01T00:00:00Z"}),
    ),
    Probe("cite-match", _cite("match", q=CITE, n="3")),
    Probe("cite-match-explicit-minimum", _cite("match", q=CITE, n="3", m="5")),
    Probe("cite-match-bulk", _cite("match", n="1"), "POST", BULK, "application/json"),
    Probe("cite-bibtex-match", _cite("bibtex/match", bibtex=BIBTEX)),
    Probe(
        "cite-bibtex-convert",
        _cite("bibtex/convert_file"),
        "POST",
        FORM,
        f"multipart/form-data; boundary={FORM_BOUNDARY}",
    ),
    Probe("rest-docs-path", "https://api.zbmath.org/docs"),
    Probe("rest-terms-agreed-page", "https://api.zbmath.org/?tnc_agreed=1"),
)


def _json(body: bytes) -> Any:
    return json.loads(body)


def _status(body: bytes) -> dict[str, Any]:
    return dict(_json(body)["status"])


def _oai_code(body: bytes) -> str | None:
    return oai_parse(body)[1]


def _headers(body: bytes) -> list[ET.Element]:
    return oai_parse(body)[0].findall(".//o:header", OAI_NS)


def _contributions(body: bytes) -> list[dict[str, Any]]:
    return [c for r in _json(body)["result"] for c in r["editorial_contributions"]]


def _oai_text(body: bytes, path: str) -> str | None:
    return oai_parse(body)[0].findtext(path, namespaces=OAI_NS)


def _formats(body: bytes) -> list[str | None]:
    formats = oai_parse(body)[0].findall(".//o:metadataFormat", OAI_NS)
    return [f.findtext("o:metadataPrefix", namespaces=OAI_NS) for f in formats]


def _sets(body: bytes) -> list[str]:
    return [s.text or "" for s in oai_parse(body)[0].findall(".//o:set/o:setSpec", OAI_NS)]


def _requested_set(body: bytes) -> str | None:
    node = oai_parse(body)[0].find("o:request", OAI_NS)
    return node.get("set") if node is not None else None


def _zb_review(body: bytes) -> str:
    root = oai_parse(body)[0]
    node = root.find(".//{https://zbmath.org/zbmath/elements/1.0/}review_text")
    return (node.text or "") if node is not None else ""


Finding = tuple[str, str, Callable[[int, bytes], bool]]

# (capture name, finding, predicate on (HTTP status, body)). check requires every predicate.
FINDINGS: tuple[Finding, ...] = (
    (
        "rest-openapi",
        "the OpenAPI document declares one server, /v1",
        lambda s, b: _json(b)["servers"] == [{"url": "/v1"}],
    ),
    (
        "rest-openapi",
        "the OpenAPI document declares no security scheme: the API is keyless",
        lambda s, b: (
            "openapi" in _json(b)
            and "schemas" in _json(b)["components"]
            and "securitySchemes" not in _json(b)["components"]
        ),
    ),
    (
        "rest-document-intro",
        "an entity root answers help text under a bare string status, not the status block",
        lambda s, b: s == 200 and _json(b)["status"] == "successful request" and "details" in _json(b)["result"],
    ),
    (
        "rest-document-by-internal-id",
        "a document answers by its internal id with a single result object",
        lambda s, b: s == 200 and _json(b)["result"]["identifier"] == "1257.82097",
    ),
    (
        "rest-document-by-zbl-id",
        "the Zbl identifier resolves to the same document as the internal id",
        lambda s, b: s == 200 and _json(b)["result"]["id"] == 6123912,
    ),
    (
        "rest-document-by-doi-path",
        "a DOI in the path answers HTTP 404 Not Found; DOIs resolve through search",
        lambda s, b: s == 404 and _status(b)["internal_code"] == "Not Found",
    ),
    (
        "rest-document-unknown-id",
        "an unknown id answers HTTP 200 with execution_bool false",
        lambda s, b: s == 200 and _status(b)["execution_bool"] is False and _json(b)["result"] is None,
    ),
    (
        "rest-document-unknown-id",
        "an error envelope stamps time_stamp without a zone and with a space separator",
        lambda s, b: " " in _status(b)["time_stamp"] and not _status(b)["time_stamp"].endswith("Z"),
    ),
    (
        "rest-document-search",
        "a success envelope stamps time_stamp in UTC with a Z suffix",
        lambda s, b: _status(b)["time_stamp"].endswith("Z"),
    ),
    (
        "rest-document-search",
        "last_id stays null on a search response",
        lambda s, b: _status(b)["last_id"] is None,
    ),
    (
        "rest-document-search",
        "the license placeholder replaces some summaries and never a zbMATH review",
        lambda s, b: (
            any(c["text"] == PLACEHOLDER for c in _contributions(b))
            and not any(c["text"] == PLACEHOLDER for c in _contributions(b) if c["contribution_type"] == "review")
        ),
    ),
    (
        "rest-document-search",
        "the per-record license field lists the article license and is empty on most records",
        lambda s, b: (
            any(r["license"] == [] for r in _json(b)["result"]) and any(r["license"] for r in _json(b)["result"])
        ),
    ),
    (
        "rest-document-search-doi",
        "the doi: search field finds the document",
        lambda s, b: s == 200 and _json(b)["result"][0]["id"] == 6123912,
    ),
    (
        "rest-document-search-arxiv",
        "the arxiv: search field finds an old-style arXiv identifier",
        lambda s, b: (
            s == 200
            and _status(b)["nr_total_results"] == 1
            and {"identifier": "math/0511691", "type": "arxiv", "url": "https://arxiv.org/abs/math/0511691"}
            in _json(b)["result"][0]["links"]
        ),
    ),
    (
        "rest-document-search-no-hits",
        "a search without hits answers HTTP 404 with result null",
        lambda s, b: s == 404 and _status(b)["internal_code"] == NO_RESULTS and _json(b)["result"] is None,
    ),
    (
        "rest-document-search-missing-query",
        "a missing search_string answers the framework's HTTP 422 detail list",
        lambda s, b: s == 422 and _json(b)["detail"][0]["loc"] == ["query", "search_string"],
    ),
    (
        "rest-document-search-page-not-integer",
        "a non-integer page answers HTTP 422",
        lambda s, b: s == 422 and _json(b)["detail"][0]["loc"] == ["query", "page"],
    ),
    (
        "rest-document-search-page-negative",
        "a negative page answers HTTP 400",
        lambda s, b: s == 400 and "[0,inf)" in _status(b)["internal_code"],
    ),
    (
        "rest-document-search-per-page-zero",
        "results_per_page 0 answers HTTP 400 naming the range 1 to 500",
        lambda s, b: s == 400 and "between 1 and 500" in _status(b)["internal_code"],
    ),
    (
        "rest-document-search-per-page-501",
        "results_per_page 501 answers HTTP 400 naming the range 1 to 500",
        lambda s, b: s == 400 and "between 1 and 500" in _status(b)["internal_code"],
    ),
    (
        "rest-document-search-window-last",
        "the 10,000th result is reachable",
        lambda s, b: (
            s == 200 and _status(b)["nr_request_results"] == 1 and _status(b)["nr_total_results"] > RESULT_WINDOW
        ),
    ),
    (
        "rest-document-search-window-past",
        "the 10,001st result answers HTTP 400 result window too large",
        lambda s, b: s == 400 and "Result window is too large" in _status(b)["internal_code"],
    ),
    (
        "rest-document-structured-doi",
        "structured search takes field names with spaces and capitals as query keys",
        lambda s, b: s == 200 and _json(b)["result"][0]["id"] == 6123912,
    ),
    (
        "rest-document-structured-title-year",
        "structured fields combine conjunctively and honor results_per_page",
        lambda s, b: s == 200 and _status(b)["nr_request_results"] == 3 and _status(b)["nr_total_results"] > 3,
    ),
    (
        "rest-document-structured-empty",
        "a structured search with no field answers HTTP 400",
        lambda s, b: s == 400 and "no parameters given" in _status(b)["internal_code"],
    ),
    (
        "rest-author-by-code",
        "an author code resolves to a profile with external identifiers and collective members",
        lambda s, b: (
            s == 200 and bool(_json(b)["result"]["collective_of"]) and bool(_json(b)["result"]["external_ids"])
        ),
    ),
    (
        "rest-author-structured",
        "author structured search answers a result list",
        lambda s, b: s == 200 and _json(b)["result"][0]["code"].startswith("cawagas."),
    ),
    (
        "rest-classification-by-code",
        "an MSC2020 code resolves with its level and parent",
        lambda s, b: _json(b)["result"]["level"] == 2 and _json(b)["result"]["parent"] == "17Axx",
    ),
    (
        "rest-classification-level-0",
        "MSC2020 has 63 two-digit classes",
        lambda s, b: _status(b)["nr_total_results"] == 63,
    ),
    (
        "rest-serial-by-id",
        "a serial resolves with its lineage and ISSN list",
        lambda s, b: s == 200 and "lineage" in _json(b)["result"] and "issn" in _json(b)["result"],
    ),
    (
        "rest-serial-search-issn",
        "an ISSN search returns every serial carrying that print ISSN",
        lambda s, b: (
            s == 200
            and len(_json(b)["result"]) == _status(b)["nr_total_results"] > 0
            and all({"number": "0003-486X", "type": "print"} in r["issn"] for r in _json(b)["result"])
        ),
    ),
    (
        "rest-software-structured",
        "a software record carries related software and the placeholder description",
        lambda s, b: (
            bool(_json(b)["result"][0]["related_software"]) and _json(b)["result"][0]["description"] == PLACEHOLDER
        ),
    ),
    ("rest-head-method", "HEAD answers HTTP 405", lambda s, b: s == 405),
    (
        "rest-conditional-cross-origin",
        "conditional request headers are ignored: a future If-Modified-Since still returns the full record",
        lambda s, b: s == 200 and _json(b)["result"]["id"] == 6123912,
    ),
    ("rest-cors-preflight", "a CORS preflight OPTIONS answers HTTP 405", lambda s, b: s == 405),
    (
        "oai-identify",
        "earliestDatestamp is the bare year 1755 against the declared second granularity",
        lambda s, b: (
            _oai_text(b, ".//o:earliestDatestamp") == "1755"
            and _oai_text(b, ".//o:granularity") == "YYYY-MM-DDThh:mm:ssZ"
        ),
    ),
    (
        "oai-identify",
        "the repository declares deletedRecord no",
        lambda s, b: _oai_text(b, ".//o:deletedRecord") == "no",
    ),
    (
        "oai-list-metadata-formats",
        "two formats, oai_dc and oai_zb_preview, the latter with a relative schema URL",
        lambda s, b: _formats(b) == ["oai_dc", "oai_zb_preview"] and b"<schema>static/oai_zb_preview.xsd" in b,
    ),
    (
        "oai-list-sets",
        "sets are the 63 two-digit MSC classes plus JFM and openaire",
        lambda s, b: (
            _sets(b)[-2:] == ["JFM", "openaire"]
            and len(_sets(b)) == 65
            and all(x.isdigit() and len(x) == 2 for x in _sets(b)[:-2])
        ),
    ),
    (
        "oai-get-record-dc",
        "oai_dc prints an absent contributor as the string None",
        lambda s, b: "<dc:contributor>None</dc:contributor>" in b.decode(),
    ),
    (
        "oai-get-record-zb-preview",
        "oai_zb_preview serves the record's review_text as the placeholder or as the summary (OBSERVATIONS)",
        lambda s, b: _zb_review(b) == PLACEHOLDER or _zb_review(b).startswith("Summary: We continue"),
    ),
    (
        "oai-get-record-zb-preview",
        "oai_zb_preview carries references with matched zbMATH ids",
        lambda s, b: "<zbmath:ref_id>" in b.decode(),
    ),
    (
        "oai-list-identifiers-set-window",
        "the request echoes set 17 as classification:17",
        lambda s, b: _requested_set(b) == "classification:17",
    ),
    (
        "oai-list-identifiers-paged",
        "the first page's resumptionToken reads cursor 100, where OAI-PMH 2.0 section 3.5 starts the cursor at 0",
        lambda s, b: b'completeListSize="135" cursor="100"' in b,
    ),
    (
        "oai-list-identifiers-paged",
        "a list page holds 100 headers under a resumptionToken with completeListSize and expirationDate",
        lambda s, b: (
            len(_headers(b)) == 100
            and oai_parse(b)[2] is not None
            and "completeListSize" in b.decode()
            and "expirationDate" in b.decode()
        ),
    ),
    (
        "oai-error-bad-verb",
        "badVerb arrives with HTTP 404",
        lambda s, b: s == 404 and _oai_code(b) == "badVerb",
    ),
    (
        "oai-error-bad-format",
        "cannotDisseminateFormat arrives with HTTP 400",
        lambda s, b: s == 400 and _oai_code(b) == "cannotDisseminateFormat",
    ),
    (
        "oai-error-unknown-id",
        "idDoesNotExist arrives with HTTP 400",
        lambda s, b: s == 400 and _oai_code(b) == "idDoesNotExist",
    ),
    (
        "oai-error-no-match",
        "noRecordsMatch arrives with HTTP 400",
        lambda s, b: s == 400 and _oai_code(b) == "noRecordsMatch",
    ),
    (
        "oai-error-bad-date",
        "an unparseable from answers badArgument with HTTP 400",
        lambda s, b: s == 400 and _oai_code(b) == "badArgument",
    ),
    (
        "oai-month-date-accepted",
        "a month-granularity from, outside the two formats section 3.3.1 permits, is accepted",
        lambda s, b: s == 200 and _oai_code(b) is None and len(_headers(b)) > 0,
    ),
    (
        "oai-mixed-granularity-accepted",
        "a day-granularity from with a second-granularity until is accepted; section 3.3.1 requires one granularity",
        lambda s, b: s == 200 and _oai_code(b) is None and len(_headers(b)) > 0,
    ),
    (
        "oai-error-missing-prefix",
        "a missing metadataPrefix answers badArgument with HTTP 404",
        lambda s, b: s == 404 and _oai_code(b) == "badArgument",
    ),
    (
        "oai-error-bad-set",
        "an unknown set answers the non-protocol code 'invalid set'",
        lambda s, b: s == 400 and _oai_code(b) == "invalid set",
    ),
    (
        "oai-error-bad-token",
        "a resumptionToken not shaped as a UUID answers an HTML HTTP 500 instead of badResumptionToken",
        lambda s, b: s == 500 and b.lstrip().startswith(b"<!DOCTYPE HTML"),
    ),
    (
        "oai-error-unknown-uuid-token",
        "an unknown UUID-shaped resumptionToken answers badResumptionToken with HTTP 404",
        lambda s, b: s == 404 and _oai_code(b) == "badResumptionToken",
    ),
    (
        "oai-zb-preview-schema",
        "the oai_zb_preview schema resolves at the host root",
        lambda s, b: s == 200 and b'<schema targetNamespace="https://zbmath.org/OAI/2.0/oai_zb_preview/"' in b,
    ),
    (
        "oai-zb-preview-schema-relative",
        "the schema URL resolved against the base URL /v1/ answers an HTML HTTP 404",
        lambda s, b: s == 404 and b"<title>404 Not Found</title>" in b,
    ),
    (
        "oai-zb-preview-imported-schema",
        "the element schema the preview schema imports resolves beside it",
        lambda s, b: s == 200 and b'targetNamespace="https://zbmath.org/zbmath/elements/1.0/"' in b,
    ),
    (
        "oai-error-openaire-set",
        "the openaire set ListSets advertises answers 'invalid set'",
        lambda s, b: s == 400 and _oai_code(b) == "invalid set",
    ),
    (
        "cite-match",
        "match ranks the cited document first and adds an undocumented probability field",
        lambda s, b: _json(b)["results"][0]["zbl_id"] == "1257.82097" and "probability" in _json(b)["results"][0],
    ),
    (
        "cite-match",
        "without m, match returns hits scored 0.0: the documented default minimum score 5.0 is not applied",
        lambda s, b: any(r["score"] < 5.0 for r in _json(b)["results"]),
    ),
    (
        "cite-match-explicit-minimum",
        "an explicit m=5 removes the hits scored below 5.0",
        lambda s, b: bool(_json(b)["results"]) and all(r["score"] >= 5.0 for r in _json(b)["results"]),
    ),
    (
        "cite-match-bulk",
        "bulk match answers one list per query, in order",
        lambda s, b: len(_json(b)["results"]) == 2 and _json(b)["results"][0][0]["zbl_id"] == "1006.17005",
    ),
    (
        "cite-bibtex-match",
        "bibtex/match adds an undocumented arxiv_id field and can return an arXiv identifier as zbl_id",
        lambda s, b: (
            _json(b)["results"][0].get("arxiv_id") == "q-alg/9710013"
            and any(str(r["zbl_id"]).startswith("arXiv:") for r in _json(b)["results"])
        ),
    ),
    (
        "cite-bibtex-convert",
        "convert_file returns the BibTeX with a zbl field",
        lambda s, b: s == 200 and b"zbl = {1006.17005}" in b,
    ),
    (
        "rest-docs-path",
        "the documentation path /docs redirects to /v1/docs, which answers the JSON 404 envelope",
        lambda s, b: s == 404 and _status(b)["internal_code"] == "Not Found",
    ),
    (
        "rest-terms-agreed-page",
        "the page behind the terms form is Swagger UI 3.52.5 loading /v1/openapi.json",
        lambda s, b: s == 200 and b"swagger-ui/v3.52.5/swagger-ui-bundle.js" in b and b"url: '/v1/openapi.json'" in b,
    ),
)

CACHE_HEADERS = ("etag", "last-modified", "cache-control", "expires")


def _rate_limited(headers: dict[str, str]) -> bool:
    return any("ratelimit" in key or key == "retry-after" for key in headers)


# (capture name, finding, predicate on the lower-cased response headers). Every request offered gzip.
HEADER_FINDINGS: tuple[tuple[str, str, Callable[[dict[str, str]], bool]], ...] = (
    (
        "rest-document-by-internal-id",
        "REST answers uncompressed although the request offers gzip",
        lambda h: "content-encoding" not in h and h.get("server") == "uvicorn",
    ),
    (
        "rest-document-by-internal-id",
        "REST sends no validator or freshness header despite the OpenAPI description calling it cacheable",
        lambda h: not any(key in h for key in CACHE_HEADERS),
    ),
    (
        "rest-document-search",
        "REST sends no rate-limit header",
        lambda h: not _rate_limited(h),
    ),
    (
        "rest-conditional-cross-origin",
        "REST sends no Access-Control-Allow-Origin, so a browser page cannot read it cross-origin",
        lambda h: "access-control-allow-origin" not in h,
    ),
    (
        "rest-cors-preflight",
        "the preflight answer carries no Access-Control-Allow-Origin",
        lambda h: "access-control-allow-origin" not in h,
    ),
    (
        "oai-identify",
        "OAI-PMH answers gzip when offered, from an Apache server",
        lambda h: h.get("content-encoding") == "gzip" and h.get("server") == "Apache",
    ),
    (
        "oai-list-identifiers-paged",
        "OAI-PMH sends no rate-limit or cache header on a list page",
        lambda h: not _rate_limited(h) and not any(key in h for key in CACHE_HEADERS),
    ),
    (
        "rest-terms-agreed-page",
        "the agreed-terms page sets a 30-day tsnc cookie; no API endpoint in this capture sends or needs it",
        lambda h: h.get("set-cookie", "").startswith("tsnc=<redacted>") and "Max-Age=2595600" in h["set-cookie"],
    ),
    (
        "cite-match",
        "the citation matcher answers through Cloudflare with no rate-limit header",
        lambda h: h.get("server") == "cloudflare" and not _rate_limited(h),
    ),
)


# Responses fetched outside the capture run, retained under observations/ because a capture cannot reproduce
# them: GetRecord oai_zb_preview for oai:zbmath.org:6123912 at responseDate 2026-10-29T13:54:39Z served the
# summary text that every fetch from 14:04Z on replaced with PLACEHOLDER.
OBSERVATIONS = {
    "oai-get-record-zb-preview-summary-served.xml": "a6c3ad7fa6ff09d5060a552a1a6562ffb34d6de43db689033ece5529117e9f15",
}


def redact(headers: dict[str, str]) -> dict[str, str]:
    """Replace each cookie value a server sets, which a capture retains in public, with <redacted>."""
    out = dict(headers)
    if "set-cookie" in out:
        out["set-cookie"] = re.sub(r"^([^=;]+)=[^;]*", r"\1=<redacted>", out["set-cookie"])
    return out


def capture_name(index: int, probe: Probe, content_type: str) -> str:
    extension = EXTENSIONS.get(content_type.split("/")[-1].removeprefix("x-"), ".txt")
    return f"{index:02d}-{probe.name}{extension}"


def capture(out: Path, transport: Transport) -> int:
    if (out / "MANIFEST.json").exists():
        raise ZbmathError(f"{out}/MANIFEST.json exists; retained captures are immutable, choose a new directory")
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, probe in enumerate(CAPTURES):
        body = probe.body.encode() if probe.body is not None else None
        reply = transport.send(probe.url, probe.method, body, probe.content_type, probe.expect, probe.headers)
        name = capture_name(index, probe, reply.content_type)
        (out / name).write_bytes(reply.body)
        entries.append(
            {
                "name": probe.name,
                "file": name,
                "method": probe.method,
                "url": probe.url,
                "request_body": probe.body,
                "request_headers": [list(pair) for pair in probe.headers],
                "status": reply.status,
                "response_headers": redact(reply.headers),
                "content_type": reply.content_type,
                "bytes": len(reply.body),
                "sha256": hashlib.sha256(reply.body).hexdigest(),
                "elapsed_seconds": round(reply.elapsed, 3),
            }
        )
        print(f"{reply.status} {reply.elapsed:5.2f}s {name}", file=sys.stderr)
    manifest = {
        "schema": SCHEMA,
        "captured_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_agent": USER_AGENT,
        "entries": entries,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return check(out)


def check_problems(directory: Path) -> list[str]:
    manifest_path = directory / "MANIFEST.json"
    if not manifest_path.is_file():
        return [f"{manifest_path} is missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems = []
    if manifest.get("schema") != SCHEMA:
        problems.append(f"schema {manifest.get('schema')!r} is not {SCHEMA}")
    entries = manifest.get("entries", [])
    names = [e.get("name") for e in entries]
    if names != [p.name for p in CAPTURES]:
        problems.append("manifest entries differ from the CAPTURES inventory")
    files = {p.name for p in directory.iterdir()} - {"MANIFEST.json", "README.md", "observations"}
    listed = {e.get("file") for e in entries}
    for extra in sorted(files - listed):
        problems.append(f"{extra} is not in the manifest")
    # OBSERVATIONS belong to the retained audit directory; a successor capture elsewhere carries none.
    observed = directory / "observations"
    present = {p.name for p in observed.iterdir()} if observed.is_dir() else set()
    if (observed.is_dir() or directory.resolve() == EVIDENCE.resolve()) and present != set(OBSERVATIONS):
        problems.append(f"observations/ holds {sorted(present)}, not {sorted(OBSERVATIONS)}")
    for name, digest in OBSERVATIONS.items():
        if name in present and hashlib.sha256((observed / name).read_bytes()).hexdigest() != digest:
            problems.append(f"observations/{name}: bytes differ from OBSERVATIONS")
    probes = {p.name: p for p in CAPTURES}
    bodies: dict[str, tuple[int, bytes]] = {}
    headers: dict[str, dict[str, str]] = {}
    for entry in entries:
        probe = probes.get(entry.get("name"))
        request = (entry.get("url"), entry.get("method"), entry.get("request_body"), entry.get("request_headers"))
        if probe and request != (probe.url, probe.method, probe.body, [list(pair) for pair in probe.headers]):
            problems.append(f"{entry['name']}: request differs from the inventory")
        if isinstance(entry.get("response_headers"), dict):
            headers[str(entry.get("name"))] = entry["response_headers"]
            if entry["response_headers"] != redact(entry["response_headers"]):
                problems.append(f"{entry.get('name')}: a Set-Cookie value is retained unredacted")
        path = directory / str(entry.get("file"))
        if not path.is_file():
            problems.append(f"{entry.get('file')} is missing")
            continue
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != entry.get("sha256") or len(body) != entry.get("bytes"):
            problems.append(f"{entry['file']}: bytes differ from the manifest sha256")
            continue
        bodies[entry["name"]] = (int(entry["status"]), body)
    for name, finding, predicate in FINDINGS:
        if name not in bodies:
            problems.append(f"{name}: no verified capture for finding '{finding}'")
            continue
        try:
            holds = predicate(*bodies[name])
        except (KeyError, IndexError, TypeError, ValueError, AttributeError, ZbmathError, ET.ParseError) as error:
            holds = False
            finding = f"{finding} ({type(error).__name__}: {error})"
        if not holds:
            problems.append(f"{name}: finding no longer holds: {finding}")
    for name, finding, header_predicate in HEADER_FINDINGS:
        if name not in headers or name not in bodies:
            problems.append(f"{name}: no verified response headers for finding '{finding}'")
        elif not header_predicate(headers[name]):
            problems.append(f"{name}: finding no longer holds: {finding}")
    return problems


def check(directory: Path) -> int:
    problems = check_problems(directory)
    for problem in problems:
        print(f"zbmath check: {problem}", file=sys.stderr)
    if not problems:
        count = len(FINDINGS) + len(HEADER_FINDINGS)
        print(f"zbmath check: {directory.name}: {len(CAPTURES)} captures, {count} findings hold")
    return 1 if problems else 0


def self_test() -> int:
    failures = []

    def expect_raise(label: str, action: Callable[[], object]) -> None:
        try:
            action()
        except ZbmathError:
            return
        failures.append(f"{label} was accepted")

    expect_raise("per_page 0", lambda: check_window(0, 0))
    expect_raise("per_page 501", lambda: check_window(0, 501))
    expect_raise("page -1", lambda: check_window(-1, 10))
    expect_raise("window end 10,001", lambda: check_window(10_000, 1))
    check_window(9_999, 1)
    check_window(19, 500)
    hit = json.dumps({"result": [1], "status": {"execution_bool": True}}).encode()
    miss = json.dumps({"result": None, "status": {"execution_bool": False, "internal_code": NO_RESULTS}}).encode()
    gone = json.dumps({"result": None, "status": {"execution_bool": False, "internal_code": "id does not exist"}})
    if envelope(200, hit)[0] != [1] or envelope(404, miss)[0] != []:
        failures.append("envelope misread a hit or an empty search")
    expect_raise("unknown id under HTTP 200", lambda: envelope(200, gone.encode()))
    expect_raise("HTTP 422", lambda: envelope(422, b'{"detail": []}'))
    expect_raise("non-JSON body", lambda: envelope(502, b"<html>"))
    error = b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><error code="400">idDoesNotExist</error></OAI-PMH>'
    token = (
        b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><ListIdentifiers>'
        b"<resumptionToken>t1</resumptionToken></ListIdentifiers></OAI-PMH>"
    )
    last = token.replace(b"<resumptionToken>t1</resumptionToken>", b"<resumptionToken/>")
    if oai_parse(error)[1] != "idDoesNotExist" or oai_parse(token)[2] != "t1" or oai_parse(last)[2] is not None:
        failures.append("oai_parse misread an error code or a resumptionToken")
    if redact({"set-cookie": "k=secret; Path=/"}) != {"set-cookie": "k=<redacted>; Path=/"}:
        failures.append("redact kept a cookie value")
    if EVIDENCE.joinpath("MANIFEST.json").is_file():
        if check_problems(EVIDENCE):
            failures.append("the retained capture fails check")
        tampers: list[tuple[str, Callable[[Path, dict[str, Any]], object]]] = [
            ("altered byte", lambda d, m: _flip(d / m["entries"][2]["file"])),
            ("removed file", lambda d, m: (d / m["entries"][3]["file"]).unlink()),
            ("unlisted file", lambda d, m: (d / "extra.json").write_text("{}")),
            ("changed url", lambda d, m: _edit(d, m, 4, "url", m["entries"][4]["url"] + "x")),
            ("flipped status", lambda d, m: _edit(d, m, 5, "status", 404)),
            (
                "added ETag",
                lambda d, m: _edit(d, m, 2, "response_headers", {**m["entries"][2]["response_headers"], "etag": "x"}),
            ),
            ("altered observation", lambda d, m: _flip(next((d / "observations").iterdir()))),
        ]
        for label, tamper in tampers:
            with tempfile.TemporaryDirectory() as scratch:
                copy = Path(scratch) / "capture"
                shutil.copytree(EVIDENCE, copy)
                tamper(copy, json.loads((copy / "MANIFEST.json").read_text(encoding="utf-8")))
                if not check_problems(copy):
                    failures.append(f"check accepted a capture with a {label}")
    else:
        failures.append(f"{EVIDENCE} holds no MANIFEST.json")
    if FIELDS.is_file():
        record = json.loads(FIELDS.read_text(encoding="utf-8"))
        if field_problems(record):
            failures.append("the retained field audit fails check-fields")
        record["rows"][0]["negative_total"] = 3
        if not field_problems(record):
            failures.append("check-fields accepted a negative control that found documents")
    else:
        failures.append(f"{FIELDS} is missing")
    for failure in failures:
        print(f"zbmath self-test: {failure}", file=sys.stderr)
    if not failures:
        print("zbmath self-test: passed")
    return 1 if failures else 0


def _flip(path: Path) -> None:
    data = bytearray(path.read_bytes())
    data[len(data) // 2] ^= 0x01
    path.write_bytes(bytes(data))


def _edit(directory: Path, manifest: dict[str, Any], index: int, key: str, value: object) -> None:
    manifest["entries"][index][key] = value
    (directory / "MANIFEST.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")


# ---- one-line search field audit

FIELDS = ROOT / "docs/evidence/zbmath-search-fields/fields.json"
FIELDS_SCHEMA = "zbmath-search-fields-v1"


@dataclass(frozen=True)
class FieldProbe:
    """`anchor & field:positive` must find exactly the anchor; `anchor & field:negative` must find nothing."""

    entity: str
    anchor: str
    field: str
    positive: str
    negative: str | None
    documented: bool = True


_A, _B, _C = "an:1257.82097", "an:1137.17007", "an:1518.14003"
FIELD_PROBES = (
    *(
        FieldProbe("document", _A, f, p, n)
        for f, p, n in (
            ("any", "sedenions", "zzqqxx"),
            ("au", "Lawrynowicz", "Zzqqxx"),
            ("ti", "ternary", "zzqq"),
            ("ut", "sedenions", "zzqq"),
            ("cc", "82C44", "05C99"),
            ("cc", "*82C44", "*15A66"),
            ("py", "2012", "1999"),
            ("py", "2010-2013", "1990-1995"),
            ("so", "Clifford", "Topology"),
            ("doi", "10.1007/s00006-012-0360-6", "10.1000/zzqq"),
            ("en", "10.1007/s00006-012-0360-6", "10.1000/zzqq"),
            ("se", "2038", "57"),
            ("la", "English", "French"),
            ("la", "EN", "FR"),
            ("pu", "Springer", "Elsevier"),
            ("dt", "j", "b"),
            ("db", "Zbl", "JFM"),
            ("st", "c", None),
            ("st", "r", None),
            ("st", "o", None),
            ("na", "3", "1"),
            ("na", "2-4", "5-9"),
            ("rft", "Ising", "zzqqxx"),
            ("ab", "Onsager", "zzqqxx"),
        )
    ),
    FieldProbe("document", "an:1263.01009", "st", "s", None, documented=False),
    FieldProbe("document", _A, "ai", "lawrynowicz.julian", "smith.ivan", documented=False),
    FieldProbe("document", "an:1412.82015", "rf", "6123912", "1257.82097", documented=False),
    FieldProbe("document", "an:1566.14003", "ci", "3336606", "6123912"),
    FieldProbe("document", "an:1566.14003", "ci", "0212.26101", "1257.82097"),
    FieldProbe("document", _B, "arxiv", "math/0511691", "math/0000001"),
    FieldProbe("document", _B, "rv", "Elduque", "Zzqqxx"),
    FieldProbe("document", _B, "rn", "5518", "1"),
    FieldProbe("document", _B, "pt", "r", "t"),
    FieldProbe("document", _C, "sw", "Macaulay2", "Zzqqxx"),
    FieldProbe("document", _C, "si", "537", "1"),
    FieldProbe("document", "an:1263.01009", "br", "Hilbert", "Zzqqxx"),
    FieldProbe("document", "an:1391.81004", "ed", "Wheeler", "Zzqqxx"),
    FieldProbe("document", "an:1474.30019", "li", "*", None),
    *(
        FieldProbe("author", "ai:lawrynowicz.julian", f, p, n)
        for f, p, n in (
            ("any", "Lawrynowicz", "Zzqqxx"),
            ("au", "Lawrynowicz", "Zzqqxx"),
            ("ln", "Ławrynowicz", "Zzqqxx"),
            ("fn", "Julian", "Zzqqxx"),
            ("cc", "30", "05"),
            ("py", "2012", "1900"),
        )
    ),
    FieldProbe("author", "ai:bourbaki.nicolas", "en", "Q190529", "Q1"),
    FieldProbe("author", "ai:bourbaki.nicolas", "st", "o", None),
    FieldProbe("author", "ai:elduque.alberto", "rv", "5518", "1"),
    FieldProbe("author", "ai:elduque.alberto", "st", "z", None),
    FieldProbe("author", "ai:serre.jean-pierre", "aw", "Fields", "Zzqqxx"),
    FieldProbe("author", "ai:serre.jean-pierre", "co", "bourbaki.nicolas", "zz.qq"),
    *(
        FieldProbe("serial", "se:2038", f, p, n)
        for f, p, n in (
            ("any", "Clifford", "zzqqxx"),
            ("jt", "Clifford", "Topology"),
            ("sn", "0188-7009", "0003-486X"),
            ("cy", "CH", "FR"),
            ("la", "EN", "ZH"),
            ("cc", "15", "05"),
            ("pu", "Springer", "Elsevier"),
            ("tp", "j", "b"),
            ("st", "c", None),
            ("py", "2000", "1800"),
            ("li", "*", None),
        )
    ),
    *(
        FieldProbe("software", "si:537", f, p, n)
        for f, p, n in (
            ("any", "Macaulay2", "zzqqxx"),
            ("sw", "Macaulay2", "Zzqqxx"),
            ("au", "Grayson", "Zzqqxx"),
            ("ut", "CAS", "zzqqxx"),
            ("cc", "13", "03"),
            ("ab", "algebraic", "zzqqxx"),
        )
    ),
    FieldProbe("software", "si:630", "pl", "C", "Fortran"),
    *(
        FieldProbe("classification", "cc:17A35", f, p, n)
        for f, p, n in (("any", "division", "zzqq"), ("ct", "division", "zzqq"), ("lv", "2", "0"))
    ),
)


def _total(transport: Transport, entity: str, query: str) -> int:
    _, block = rest(transport, f"{entity}/_search", {"search_string": query, "results_per_page": 1})
    return int(block.get("nr_total_results") or 0)


def field_audit(out: Path, transport: Transport) -> int:
    if out.exists():
        raise ZbmathError(f"{out} exists; retained field audits are immutable, choose a new path")
    rows = []
    for probe in FIELD_PROBES:
        positive = _total(transport, probe.entity, f"{probe.anchor} & {probe.field}:{probe.positive}")
        negative = None
        if probe.negative is not None:
            negative = _total(transport, probe.entity, f"{probe.anchor} & {probe.field}:{probe.negative}")
        rows.append({**probe.__dict__, "positive_total": positive, "negative_total": negative})
        print(f"{probe.entity} {probe.field}:{probe.positive} -> {positive}, {negative}", file=sys.stderr)
    record = {"schema": FIELDS_SCHEMA, "captured_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "rows": rows}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return check_fields(out)


def field_problems(record: dict[str, Any]) -> list[str]:
    problems = []
    if record.get("schema") != FIELDS_SCHEMA:
        problems.append(f"schema {record.get('schema')!r} is not {FIELDS_SCHEMA}")
    rows = record.get("rows", [])
    if [{k: r.get(k) for k in FieldProbe.__dataclass_fields__} for r in rows] != [p.__dict__ for p in FIELD_PROBES]:
        problems.append("rows differ from the FIELD_PROBES inventory")
    for row in rows:
        label = f"{row.get('entity')} {row.get('anchor')} & {row.get('field')}"
        if row.get("positive_total") != 1:
            problems.append(f"{label}:{row.get('positive')} found {row.get('positive_total')}, not the anchor alone")
        if row.get("negative") is not None and row.get("negative_total") != 0:
            problems.append(f"{label}:{row.get('negative')} found {row.get('negative_total')}, not 0")
    return problems


def check_fields(path: Path) -> int:
    problems = field_problems(json.loads(path.read_text(encoding="utf-8")))
    for problem in problems:
        print(f"zbmath check-fields: {problem}", file=sys.stderr)
    if not problems:
        print(f"zbmath check-fields: {len(FIELD_PROBES)} field probes hold")
    return 1 if problems else 0


# ---- command line


def emit(value: object) -> None:
    print(json.dumps(value, indent=1, ensure_ascii=False))


def run_rest(args: argparse.Namespace, transport: Transport) -> int:
    if args.command == "get":
        result, _ = rest(transport, f"{args.entity}/{urllib.parse.quote(args.id, safe='.-_')}")
        emit(result)
        return 0
    if args.command == "search":
        params: dict[str, Any] = {"search_string": args.query}
        path = f"{args.entity}/_search"
    else:
        params = {}
        for pair in args.fields:
            key, sep, value = pair.partition("=")
            if not sep:
                raise ZbmathError(f"structured field {pair!r} is not FIELD=VALUE")
            params[key] = value
        path = f"{args.entity}/_structured_search"
    if args.all:
        emit(list(rest_pages(transport, path, params, args.per_page)))
        return 0
    check_window(args.page, args.per_page)
    result, block = rest(transport, path, {**params, "page": args.page, "results_per_page": args.per_page})
    print(f"zbmath: {block.get('nr_total_results') or 0} results in total", file=sys.stderr)
    emit(result)
    return 0


def run_oai(args: argparse.Namespace, transport: Transport) -> int:
    params = {"verb": args.verb}
    for pair in args.arguments:
        key, sep, value = pair.partition("=")
        if not sep:
            raise ZbmathError(f"OAI argument {pair!r} is not NAME=VALUE")
        params[key] = value
    url = OAI + "?" + urllib.parse.urlencode(params)
    page = 0
    while True:
        reply = transport.send(url)
        if reply.status >= 500:
            raise ZbmathError(f"OAI HTTP {reply.status} for {url}")
        _, code, token = oai_parse(reply.body)
        if code == "noRecordsMatch":
            print("zbmath: noRecordsMatch", file=sys.stderr)
            return 0
        if code:
            raise ZbmathError(f"OAI error {code} (HTTP {reply.status})")
        if args.out is None:
            sys.stdout.write(reply.body.decode("utf-8"))
            return 0
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / f"page-{page:04d}.xml").write_bytes(reply.body)
        print(f"zbmath: page {page} written", file=sys.stderr)
        if token is None:
            return 0
        url = OAI + "?" + urllib.parse.urlencode({"verb": args.verb, "resumptionToken": token})
        page += 1


def run_match(args: argparse.Namespace, transport: Transport) -> int:
    if args.bulk is not None:
        body = args.bulk.read_bytes()
        queries = json.loads(body).get("queries", [])
        if not 1 <= len(queries) <= 100:
            raise ZbmathError(f"a bulk request holds 1 to 100 queries, not {len(queries)}")
        reply = transport.send(_cite("match", n=str(args.n), m=str(args.m)), "POST", body, "application/json")
    else:
        if args.query is None:
            raise ZbmathError("match needs QUERY or --bulk FILE")
        reply = transport.send(_cite("match", q=args.query, n=str(args.n), m=str(args.m)))
    if reply.status != 200:
        raise ZbmathError(f"citation matcher HTTP {reply.status}")
    emit(_json(reply.body))
    return 0


def run_bibtex(args: argparse.Namespace, transport: Transport) -> int:
    payload = args.file.read_bytes()
    if args.convert:
        body, content_type = multipart("bibtex_file", args.file.name, payload, "application/x-bibtex")
        reply = transport.send(_cite("bibtex/convert_file", m=str(args.m)), "POST", body, content_type)
        if reply.status != 200:
            raise ZbmathError(f"citation matcher HTTP {reply.status}")
        sys.stdout.write(reply.body.decode("utf-8"))
        return 0
    reply = transport.send(_cite("bibtex/match", bibtex=payload.decode("utf-8"), n=str(args.n), m=str(args.m)))
    if reply.status != 200:
        raise ZbmathError(f"citation matcher HTTP {reply.status}")
    emit(_json(reply.body))
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    top.add_argument("--self-test", action="store_true")
    top.add_argument("--interval", type=float, default=MIN_INTERVAL, help="seconds between requests")
    sub = top.add_subparsers(dest="command")
    get = sub.add_parser("get")
    get.add_argument("entity", choices=ENTITIES)
    get.add_argument("id")
    for name, positional in (("search", "query"), ("structured", "fields")):
        command = sub.add_parser(name)
        command.add_argument("entity", choices=ENTITIES)
        command.add_argument(positional, nargs=1 if name == "search" else "+")
        command.add_argument("--page", type=int, default=0)
        command.add_argument("--per-page", type=int, default=100)
        command.add_argument("--all", action="store_true")
    oai = sub.add_parser("oai")
    oai.add_argument("verb")
    oai.add_argument("arguments", nargs="*")
    oai.add_argument("--out", type=Path)
    match = sub.add_parser("match")
    match.add_argument("query", nargs="?")
    match.add_argument("--bulk", type=Path)
    bibtex = sub.add_parser("bibtex")
    bibtex.add_argument("file", type=Path)
    bibtex.add_argument("--convert", action="store_true")
    for command in (match, bibtex):
        command.add_argument("-n", type=int, default=1, help="number of results")
        command.add_argument("-m", type=float, default=5.0, help="minimum score")
    cap = sub.add_parser("capture")
    cap.add_argument("--out", type=Path, required=True)
    chk = sub.add_parser("check")
    chk.add_argument("directory", type=Path)
    fields = sub.add_parser("fields")
    fields.add_argument("--out", type=Path, required=True)
    check_field = sub.add_parser("check-fields")
    check_field.add_argument("path", type=Path)
    return top


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.self_test:
        return self_test()
    if args.command == "check":
        return check(args.directory)
    if args.command == "check-fields":
        return check_fields(args.path)
    if args.command is None:
        parser().print_usage(sys.stderr)
        return 2
    if args.command == "search":
        args.query = args.query[0]
    transport = Transport(args.interval)
    try:
        if args.command in ("get", "search", "structured"):
            return run_rest(args, transport)
        if args.command == "oai":
            return run_oai(args, transport)
        if args.command == "match":
            return run_match(args, transport)
        if args.command == "bibtex":
            return run_bibtex(args, transport)
        if args.command == "fields":
            return field_audit(args.out, transport)
        return capture(args.out, transport)
    except ZbmathError as error:
        print(f"zbmath: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
