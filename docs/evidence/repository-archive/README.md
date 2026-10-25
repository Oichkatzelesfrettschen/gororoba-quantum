# Repository archive observations

Records written by `scripts/repository_archive.py swh-save` and `swh-status`
([procedure](../../runbooks/repository-archive.md)): each file holds one
request to the Software Heritage API for the public origin, with its UTC
time, HTTP status, response body and the body's sha256. A record observes the
archive at its time; the snapshot SWHID a completed visit reports is the
durable identifier of the archived refs.
