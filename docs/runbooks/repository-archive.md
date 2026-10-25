# Repository archive copies

The checksum ledgers in this repository detect a changed or missing file but
restore nothing; the copies they are checked against are GitHub and the
workstation clones. `scripts/repository_archive.py` maintains two copies
outside both.

**Software Heritage.** The public origin is saved to the Software Heritage
archive, which stores every object content-addressed under SWHIDs on its own
infrastructure. A save request is anonymous and rate-limited:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/repository_archive.py swh-save \
  --record "docs/evidence/repository-archive/swh-save-$(date -u +%Y-%m-%dT%H%M%SZ).json"
"$PYTHON" scripts/repository_archive.py swh-status \
  --record "docs/evidence/repository-archive/swh-status-$(date -u +%Y-%m-%dT%H%M%SZ).json"
```

Each record keeps the request URL, UTC time, HTTP status and response body
with its sha256. A completed visit reports `visit_status: full` and a
`snapshot_swhid`; the snapshot SWHID names the archived refs and resolves at
`https://archive.softwareheritage.org/<swhid>`. Request a new save after a
release or a run that retains significant evidence.

**Git bundle.** A bundle holds every branch, tag and remote-tracking ref in
one file that `git clone` restores without network access:

```sh
"$PYTHON" scripts/repository_archive.py bundle --out /path/on/another/device
"$PYTHON" scripts/repository_archive.py verify /path/on/another/device/gororoba-quantum-<commit>.bundle
```

`bundle` refuses a directory inside the repository and writes a manifest
beside the bundle (sha256, length, head commit, refs, git version). `verify`
accepts a bundle only after its bytes match the manifest, `git bundle verify`
passes, a mirror clone into a temporary directory passes `git fsck --full`,
and the restored refs equal the manifest's. The output directory belongs on
a different physical device or medium from the workstation's home disk; a
bundle on the same disk survives only a deleted checkout. A bundle of
`f8c6e3e` measured 277 MB and took about one minute to create and twelve
seconds to verify.

`tests/scripts/test_repository_archive.py` builds a bundle of a synthetic
repository and requires `verify` to reject a flipped byte and an edited ref
list.
