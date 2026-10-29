# zbMATH Open API audit capture

The files beside this README are raw responses of the zbMATH Open REST API, OAI-PMH API and citation
matcher, fetched by `scripts/zbmath.py capture` and listed with URL, method, request and response headers,
HTTP status and sha256 in `MANIFEST.json`. `observations/` holds one response fetched outside the capture
run. The guide [notes/zbmath/README.md](../../notes/zbmath/README.md) states what each capture shows and
which deviations survived the falsification tests.

License: the content is zbMATH Open data of FIZ Karlsruhe -- Leibniz-Institut fuer
Informationsinfrastruktur GmbH, distributed under CC BY-SA 4.0
(https://creativecommons.org/licenses/by-sa/4.0/), with bibliographic metadata and I4OC reference data
under CC0. These files are redistributed unmodified under the same license.

One file carries third-party text under its own license:
`observations/oai-get-record-zb-preview-summary-served.xml` contains the author summary of
Lawrynowicz, Suzuki and Niemczynowicz, "On the ternary approach to Clifford structures and Ising
lattices", Adv. Appl. Clifford Algebr. 22, No. 3, 757-769 (2012), https://doi.org/10.1007/s00006-012-0360-6,
which the record's own REST `license` field (`02-rest-document-by-internal-id.json`) names as
CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

`"$PYTHON" scripts/zbmath.py check docs/evidence/zbmath-api-audit` verifies every byte and every finding
offline; a new capture lands in a new directory, because a directory with a MANIFEST.json is refused.
