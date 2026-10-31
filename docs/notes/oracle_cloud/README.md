# Oracle Cloud Infrastructure (OCI)

The owner's OCI account is a personal Free Tier tenancy whose only
subscribed region is its home region, `us-sanjose-1` (US West, San Jose,
key `SJC`), with one availability domain, `US-SANJOSE-1-AD-1`. The account
has no intent-to-pay flag (`osp_gateway` subscription `plan_type FREE_TIER`,
`is_intent_to_pay False`), so it reaches the Always Free resources and the
limits below, and nothing it creates within them is billed. Every fact was
read through the API on 2026-10-31 by the survey in
[Replaying the survey](#replaying-the-survey); the console and the API stay
the authority, because Oracle changes Free Tier limits per tenancy.

## Clients on the build host

| Client | Version | Installed from | Role |
|---|---|---|---|
| OCI Python SDK, `import oci` | 2.189.0 | AUR `python-oci` (`paru -S python-oci`) into the system Python 3.14 | typed clients for every OCI REST service, pagination, waiters, retry |
| OCI CLI, `oci` | 3.95.1 | local PKGBUILD `~/Github/PKGBUILDs/oci-cli` (AUR recipe, pkgrel 2), built with `makepkg -si` | shell scripting of the same services; JMESPath `--query`, `--output table/json` |
| `oracle.oci` Ansible collection | 5.5.0 | Ansible Galaxy, `ansible-galaxy collection install oracle.oci`, into `~/.ansible/collections` | declarative infrastructure modules (`oracle.oci.oci_compute_instance`, `oci_network_vcn`, `*_facts` modules) and the `oracle.oci.oci` dynamic inventory; it calls the SDK and is not a Python import library |

The CLI and the collection both depend on the SDK, so `python-oci` upgrades
first. Ansible itself is the Arch `ansible` 14.5.0 package.

The AUR `oci-cli` 3.95.1-1 launcher fails at start with
`'services' is not a package` on a host that also carries `impacket`:
Python prepends the script directory `/usr/bin` to `sys.path`, and
impacket's `/usr/bin/services.py` shadows the CLI's top-level `services`
package. The local PKGBUILD rewrites the launcher's shebang to
`#!/usr/bin/python -P`, which omits the script directory from `sys.path`.
An AUR upgrade of `oci-cli` reinstates the failure, so a version bump edits
`pkgver` and `sha256sums` in the local PKGBUILD and rebuilds there.

## Credential layout

API signing-key authentication reads `~/.oci/config`, profile `[DEFAULT]`,
with the keys `user`, `tenancy`, `fingerprint`, `region=us-sanjose-1` and
`key_file=~/.oci/oci_api_key.pem`.

| Path | Mode | Content |
|---|---|---|
| `~/.oci/` | 700 | |
| `~/.oci/config` | 600 | the profile above |
| `~/.oci/oci_api_key.pem` | 600 | active RSA private key |
| `~/.oci/oci_api_key_public.pem` | 600 | its public half |
| `~/.oci/keys/retired/` | 700 | key pairs the user does not hold, kept for audit; none signs a request |

The active key's fingerprint in the console (My profile, API keys) equals
`openssl rsa -in ~/.oci/oci_api_key.pem -pubout -outform DER | openssl md5 -c`.
A newly added key returned 401 `NotAuthenticated` for several minutes
before the first call succeeded, so a fresh key gets that delay before a
401 is diagnosed. A user holds at most three API keys. The OCIDs, the
fingerprint, the tenancy name and the Object Storage namespace are account
identifiers and stay out of every commit, log and record.

## Identity and authority

| Item | Value |
|---|---|
| User | the owner, ACTIVE, MFA on; may hold API keys, auth tokens, customer secret keys, SMTP, database and OAuth 2 client credentials |
| Groups | `Administrators` |
| Policy | `Tenant Admin Policy`: `ALLOW GROUP Administrators to manage all-resources IN TENANCY` |
| Identity domains | one, `Default`, license type `free` |
| Compartments | none besides the root |
| Resources | no instances, VCNs, buckets or budgets |

The key therefore carries full administrator authority: anything the API
can create, it can create. The limits below, not permissions, bound what
the tenancy can run.

## Always Free capacity (service limits, 2026-10-31)

| Service (limits name) | Limit | Use |
|---|---|---|
| Compute (`compute`) | `VM.Standard.A1.Flex` (Ampere ARM): 2 OCPUs and 12 GB memory in total | one ARM VM, or two 1-OCPU VMs |
| | `VM.Standard.E2.1.Micro` (AMD): 2 instances | small x86 VMs |
| | `standard-a2` 8 cores, 96 GB | listed, but `list_shapes` offers only `VM.Standard.A1.Flex`, `VM.Standard.E2.1.Micro` and `BM.Standard.A1.160` |
| Block volume (`block-storage`) | 200 GB total (boot volumes included), 5 free backups | |
| Object Storage (`object-storage`) | 20 GiB (21474836480 bytes) | buckets, pre-authenticated download links |
| Networking (`vcn`) | 2 VCNs, 1 internet gateway, 1 reserved public IP, 300 subnets | |
| Load balancer (`load-balancer`) | 1 flexible LB, 10 Mbps | |
| Database (`database`) | 2 Always Free Autonomous Databases, 100 developer ADBs | managed Oracle databases |
| Functions (`faas`) | 61440 MB total concurrency | serverless containers |
| Container Registry | 50 requests/s | OCIR images for Functions or VMs |
| Email Delivery | 100 messages per day, 10 approved senders | |
| Container Engine, Generative AI (`container-engine`, `ai-generative`) | no limit values set | OKE and Generative AI need a paid account |

The A1 allotment reads 2 OCPUs and 12 GB on this tenancy, half the 4 OCPUs
and 24 GB that Oracle's Free Tier page advertises, so the limits service
decides a capacity plan. San Jose Ampere capacity is often exhausted, and
`LaunchInstance` then fails with `Out of host capacity`; that error is a
capacity state and carries no quota meaning. The tenancy holds no GPU, HPC
or quantum shape.

## Usage

CLI, from any directory:

```sh
oci iam region-subscription list --output table
oci compute shape list --compartment-id "$OCI_TENANCY" --query 'data[].shape'
oci limits value list --compartment-id "$OCI_TENANCY" --service-name compute --all
oci os ns get
```

`OCI_TENANCY` is read from the config at run time
(`OCI_TENANCY=$(sed -n 's/^tenancy=//p' ~/.oci/config)`) so the OCID never
enters a command line that a log records.

Python:

```python
import oci

config = oci.config.from_file()
oci.config.validate_config(config)
identity = oci.identity.IdentityClient(config)
compute = oci.core.ComputeClient(config)
shapes = oci.pagination.list_call_get_all_results(compute.list_shapes, config["tenancy"]).data
```

Ansible, read-only:

```sh
ansible localhost -m oracle.oci.oci_identity_availability_domain_facts \
  -a "compartment_id=$OCI_TENANCY"
```

The collection reads the same `~/.oci/config`; playbooks that create
resources use `oracle.oci.oci_compute_instance`, `oci_network_vcn`,
`oci_network_subnet` and `oci_object_storage_bucket`, and the dynamic
inventory plugin `oracle.oci.oci` enumerates instances for configuration
runs.

## Use in this repository

The Always Free shapes give the lab an always-on ARM or x86 host and 20 GiB
of object storage. That covers small classical jobs: cron-driven
calibration reads, the poll loops of `poll-remote-jobs`, null calibrations
that fit 2 OCPUs, and evidence mirrors. Long classical jobs route to Kaggle
or GitHub Actions first (Kaggle CPU bits equal the host's); an OCI VM
serves a job that must run continuously or hold state between runs.
Creating any resource, and any change to the account's plan, waits for the
owner's approval of a written case naming the resource and its limit; an
upgrade to Pay As You Go starts billing beyond Always Free and is the
owner's decision alone.

## Replaying the survey

The facts above come from read-only SDK calls in the home region:
`IdentityClient.get_tenancy`, `get_user`, `list_user_group_memberships`,
`list_compartments`, `list_policies`, `list_availability_domains`,
`list_domains`; `LimitsClient.list_services` and `list_limit_values` per
service; `ComputeClient.list_shapes` and `list_instances`;
`ObjectStorageClient.get_namespace` and `list_buckets`;
`VirtualNetworkClient.list_vcns`; `BudgetClient.list_budgets`; and
`osp_gateway.SubscriptionServiceClient.list_subscriptions`. None creates,
changes or bills anything.
