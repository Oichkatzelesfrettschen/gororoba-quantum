# Oracle Cloud Infrastructure (OCI)

The owner's OCI tenancy has one subscribed region, `us-sanjose-1` (US West,
San Jose), which is also its home region and reads READY
(`oci iam region-subscription list`, 2026-10-31). The build host reaches it
through three clients: the Python SDK, the CLI and the Ansible collection.
The facts below were read on 2026-10-31; the console and the API stay the
authority.

## Clients on the build host

| Client | Version | Install | Role |
|---|---|---|---|
| OCI Python SDK (`import oci`) | 2.189.0 | AUR `python-oci` | API calls from Python |
| OCI CLI (`oci`) | 3.95.1 | `~/Github/PKGBUILDs/oci-cli` (pkgrel 2) | shell scripting of infrastructure operations |
| `oracle.oci` Ansible collection | 5.5.0 | `ansible-galaxy collection install oracle.oci` (`~/.ansible/collections`) | infrastructure configuration and orchestration; not a Python import library |

The AUR `oci-cli` 3.95.1-1 launcher fails at start with
`'services' is not a package` on a host that also carries `impacket`:
Python prepends the script directory `/usr/bin` to `sys.path`, and
impacket's `/usr/bin/services.py` shadows the CLI's top-level `services`
package. The local PKGBUILD rewrites the launcher's shebang to
`#!/usr/bin/python -P`, which omits the script directory from `sys.path`.
An AUR upgrade of `oci-cli` reinstates the failure, so the package rebuilds
from the local PKGBUILD (`makepkg -si` there) after a version bump.

## Credential

API signing-key authentication reads `~/.oci/config` (file 600, directory
700) with profile `[DEFAULT]`: `user`, `tenancy`, `fingerprint`, `region`
and `key_file=~/.oci/oci_api_key.pem` (600). The public half is
`~/.oci/oci_api_key_public.pem`. The console's "Add API key" dialog
generates the pair; the key's fingerprint in My profile, API keys must
equal `openssl rsa -in ~/.oci/oci_api_key.pem -pubout -outform DER | openssl md5 -c`.
A newly added key returned 401 `NotAuthenticated` for several minutes
before the first call succeeded, so a fresh key gets that delay before a
401 is diagnosed. The key and the OCIDs are account identifiers: they stay
out of every commit, log and record.

## Read-only checks

```sh
oci iam region-subscription list --output table
oci iam availability-domain list
```

From Python, `oci.config.from_file()` followed by
`oci.config.validate_config(config)` loads the same profile. Creating or
changing any resource, and any spend, waits for the owner's approval of a
written case.
