# Repository archive observations

Records written by `scripts/repository_archive.py swh-save` and `swh-status`
([procedure](../../runbooks/repository-archive.md)): each file holds one
request to the Software Heritage API for the public origin, with its UTC
time, HTTP status, response body and the body's sha256. A record observes the
archive at its time; the snapshot SWHID a completed visit reports is the
durable identifier of the archived refs.

The first save request (2576155) completed on 2026-10-25 with a full visit; its snapshot is
`swh:1:snp:28882c1bdf53ccc0f4e1aef527e4e5ecaef8226d`, recorded in `swh-status-2026-10-25T194835Z.json`.
