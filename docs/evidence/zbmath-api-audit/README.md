# zbMATH Open API audit capture

The files beside this README are raw responses of the zbMATH Open REST API, OAI-PMH API and citation
matcher, fetched by `scripts/zbmath.py capture` and listed with URL, method, request and response headers,
HTTP status and sha256 in `MANIFEST.json`. `observations/` holds one response fetched outside the capture
run. The guide [notes/zbmath/README.md](../../notes/zbmath/README.md) states what each capture shows.

License: the content is zbMATH Open data of FIZ Karlsruhe -- Leibniz-Institut fuer
Informationsinfrastruktur GmbH, distributed under CC BY-SA 4.0
(https://creativecommons.org/licenses/by-sa/4.0/), with bibliographic metadata and I4OC reference data
under CC0. These files are redistributed unmodified under the same license.

`"$PYTHON" scripts/zbmath.py check docs/evidence/zbmath-api-audit` verifies every byte and every finding
offline; a new capture lands in a new directory, because a directory with a MANIFEST.json is refused.
