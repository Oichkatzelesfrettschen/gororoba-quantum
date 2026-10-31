# OCI lab operations

Commands for the Always Free lab whose design is in
[oci-free-tier-lab](../design/oci-free-tier-lab.md). Every script reads
`~/.oci/config` and keeps OCIDs, addresses and secrets in `~/.oci/lab/`
(directory 700, files 600): `inventory.env` holds resource ids, `adb-*.admin`
and `adb-*.labml` the database passwords, `wallet-*` the mTLS wallets,
`rdp-lab-micro2.pass` the RDP password, `wg/` the workstation's WireGuard key
and tunnel config. None of these enters a commit, log or command line.
Commands run from the repository root with `PYTHON=${PYTHON:-python3}`.

## Provisioning

`scripts/oci_lab_provision.sh` runs one phase per call and finds each resource
by display name before creating it, so a rerun creates nothing twice:

```sh
sh scripts/oci_lab_provision.sh network   # VCN, internet gateway, route tables, security lists, subnets
sh scripts/oci_lab_provision.sh route     # private 0.0.0.0/0 and the WireGuard range to the edge's private IP
sh scripts/oci_lab_provision.sh a1        # one A1 launch (A1_OCPUS, A1_MEM_GB override 2/12); exit 75 on Out of host capacity
sh scripts/oci_lab_provision.sh volume    # lab-data (50 GB) attached to lab-a1
sh scripts/oci_lab_provision.sh bastion   # lab-bastion on lab-private
sh scripts/oci_lab_provision.sh status
"$PYTHON" -I scripts/oci_lab/a1_capacity.py 1 6   # free placement query per fault domain; exit 75 when none
tmux new-session -d -s oci-a1-retry "sh $PWD/scripts/oci_lab/a1_retry.sh"   # 5 min polls, 48 h
```

`a1_retry.sh` polls the capacity report and launches only when a fault
domain reports AVAILABLE, by default as two 1 OCPU / 6 GB hosts (`lab-a1` at
10.42.1.20, `lab-a1b` at 10.42.1.21; `A1_HOSTS`, `A1_OCPUS` and `A1_MEM_GB`
override). Two A1 boot volumes and the two micros' fill the 200 GB block
storage allowance, so this layout carries no `lab-data` volume. Progress goes
to `~/.oci/lab/a1-retry.log`, and `notify-send` reports the outcome.

A Debian micro is rebuilt from a preserved boot volume, with a running lab
host as the writer (the tenancy cannot import custom images):

```sh
base=https://cloud.debian.org/images/cloud/trixie/latest
curl -fsSLO "$base/SHA512SUMS" && curl -fsSLO "$base/debian-13-genericcloud-amd64.qcow2"
grep ' debian-13-genericcloud-amd64.qcow2$' SHA512SUMS | sha512sum -c -
DEBIAN_QCOW2=$PWD/debian-13-genericcloud-amd64.qcow2 \
  sh scripts/oci_lab/debian_bootvol.sh OLD_NAME NEW_NAME SUBNET_PRIVATE_ID 10.42.1.30 false WRITER_ID WRITER_SSH
```

Host configuration, run as root on the target after `scp`:

| Script | Host | Effect |
|---|---|---|
| `scripts/oci_lab/edge_setup_debian.sh` | edge | 2 GB swap, forwarding, nftables NAT and input filter, WireGuard `wg0` |
| `scripts/oci_lab/desktop_setup_debian.sh` | `lab-micro2` | 2 GB swap, MATE and xrdp, nftables admitting 22, 2049 and 3389 from the VCN and WireGuard |
| `scripts/oci_lab/edge_setup.sh` | Oracle Linux 9 edge | the superseded Oracle Linux route, kept for an Oracle Linux edge |

The Oracle Cloud Agent on Debian: `apt-get install --no-install-recommends
snapd squashfs-tools`, `snap wait system seed.loaded`, `snap install
oracle-cloud-agent --classic`; the plugin set is applied through
`oci compute instance update --agent-config` with the names the agent reports
(`oci.compute_instance_agent.PluginClient.list_instance_agent_plugins`).

## Spend guards

The account runs Pay As You Go, where service limits rise to paid levels, so
two guards hold it to Always Free. The quota policy `lab-free-only`
(`sh scripts/oci_lab/quota_free_only.sh`) zeroes each service family and then
sets the free allowance: A1 2 OCPU / 12 GB, two E2.1.Micro, 200 GB and four
volumes of block storage with five backups, two free Autonomous Databases,
one 10 Mbps flexible load balancer, 20 GB of Object Storage, and zero for
every other compute shape, GPU and paid data service. A quota refuses the
create before it bills; `oci limits resource-availability get` reports the
`effective-quota-value`. MySQL publishes no quota names, so its guard is the
`MySQL.Free` shape in `mysql_create.py`. The budget `lab-guard` alerts on any
actual spend and on a forecast of $1 through the `lab-events` email
subscription, which delivers only after its confirmation link is clicked;
budgets alert and never stop resources.

`scripts/oci_lab/payg_watch.sh` (tmux `oci-payg-watch`) polls the compute
service limits every 30 minutes and reports when the paid-shape limit
leaves 0, together with the A1 service limit the upgraded account holds.
`A1_QUOTA_OCPUS=4 A1_QUOTA_MEM_GB=24 sh scripts/oci_lab/quota_free_only.sh`
raises the A1 quota only after an invoice or Oracle's limits page confirms
that allowance at no charge.

## Resource Manager stack

```sh
sh scripts/oci_lab/rm_stack.sh    # discovery stack lab-stack, patched config, plan job; never applies
```

Resource Discovery captures the core, bastion, database, mysql, ons and
budget services of the tenancy root into the stack `lab-stack` with a state
file that already holds every live resource, so its plan adds and destroys
nothing. The generated Terraform and the patched upload sit in
`~/.oci/lab/rm-config/` and the last plan log in `~/.oci/lab/rm-plan.log`;
the generated files carry OCIDs and stay out of the repository. The plan's
in-place changes are tag timestamps on the budget alert rules and the
`source_details.source_id` of instances launched from a rewritten boot
volume; an apply would only rewrite those fields, and the stack serves as the
rebuild record and drift check. A1 hosts enter the stack by rerunning
discovery after they launch (delete `lab-stack` first; its state is the
discovery snapshot).

## Access

SSH reads `~/.ssh/config.d/oci-lab` (included from `~/.ssh/config`): `lab-edge`
connects to the reserved public IP as `debian`, and `lab-micro2` and `lab-a1`
jump through it.

WireGuard, split tunnel to `10.42.0.0/16` and `10.66.0.0/24`:

```sh
SUDO_ASKPASS=/usr/bin/unified-askpass sudo -A wg-quick up ~/.oci/lab/wg/oci-lab.conf
xfreerdp3 /v:10.42.1.30 /u:debian      # password in ~/.oci/lab/rdp-lab-micro2.pass
SUDO_ASKPASS=/usr/bin/unified-askpass sudo -A wg-quick down ~/.oci/lab/wg/oci-lab.conf
```

A new WireGuard peer generates its key locally and adds only its public key
on the edge: `wg set wg0 peer PUBKEY allowed-ips 10.66.0.N/32`, appended as a
`[Peer]` block to `/etc/wireguard/wg0.conf`.

Run Command over REST, when SSH and WireGuard are down:

```sh
"$PYTHON" scripts/oci_lab/run_command.py lab-micro2 'systemctl --failed; free -m' 120
```

The agent polls the service every few minutes; the dynamic group
`lab-instances` and the policy `lab-instance-agent` grant it
`instance-agent-command-execution-family`, and a newly created policy takes
minutes to propagate before the agent's poll stops returning
`NotAuthorizedOrNotFound`. Repeated 404s open the agent's poll circuit
breaker, which stays open after the policy propagates;
`snap restart oracle-cloud-agent.oracle-cloud-agent` on the host closes it,
and the next poll returns 200.

Bastion port forwarding into the private subnet, independent of the edge:

```sh
. ~/.oci/lab/inventory.env
oci bastion session create-port-forwarding --bastion-id "$BASTION_ID" \
  --target-private-ip 10.42.1.30 --target-port 22 \
  --ssh-public-key-file ~/.ssh/oci_lab_ed25519.pub --session-ttl 10800 --wait-for-state SUCCEEDED
oci bastion session get --session-id SESSION_ID --query 'data."ssh-metadata".command' --raw-output
```

Serial console, independent of the guest network:

```sh
oci compute instance-console-connection create --instance-id INSTANCE_ID \
  --ssh-public-key-file ~/.ssh/oci_lab_ed25519.pub
oci compute instance-console-connection get --instance-console-connection-id ID \
  --query 'data."connection-string"' --raw-output
```

The console login takes the instance user's password, so a host that needs
console access holds a password for `debian`. Cloud Shell, opened from the
console toolbar, carries the same CLI and reaches the private hosts through
`lab-bastion`.

A host that stops answering gets its serial console log first
(`oci compute console-history capture`, then `get-content`), then its
`MemoryUtilization` and `CpuUtilization` from the `oci_computeagent`
namespace, then a `SOFTRESET`; a guest too starved to honor ACPI holds the
instance in STOPPING until OCI forces the stop.

## Autonomous Databases

```sh
python3 -I scripts/oci_lab/adb_create.py OPERATOR_IP     # both Always Free 23ai databases
cd scripts/oci_lab && python3 -I adb_oml_setup.py          # wallets, LABML user, pyqEval probe
```

`adb_create.py` restricts each endpoint's access-control list to the given
addresses and the edge's public IP and requires mutual TLS.
`adb_oml_setup.py` prints each database's service URL names and the probe's
JSON; OML Notebooks opens at the database's `machine_learning_notebook_url`
as `LABML`. SQLcl connects through the wallet's auto-login file, with the
password on standard input:

```sh
{ printf 'connect labml/"%s"@labdw_low\n' "$(cat ~/.oci/lab/adb-lab-adb-dw.labml)"; echo 'select banner_full from v$version;'; } |
  TNS_ADMIN=~/.oci/lab/wallet-lab-adb-dw sqlcl -S /nolog
```

## Host packages

| Package | Version | Source |
|---|---|---|
| `python-oracledb` | 4.0.2 | AUR |
| `sqlcl` (launcher `/usr/bin/sqlcl`) | 25.4.1 | local PKGBUILD `~/Github/PKGBUILDs/sqlcl`: GNU parallel owns `/usr/bin/sql` |
| `terraform` | 1.15.9 | Arch extra |
| `python-borneo` (NoSQL SDK) | 5.5.0 | local PKGBUILD from PyPI |
| `python-oci-openai`, `python-oci-genai-auth` | 1.1.0, 1.1.1 | local PKGBUILDs from PyPI |
| `python-ocifs` (fsspec for Object Storage) | 1.3.4 | local PKGBUILD from PyPI |
| `python-jsonschema-objects` | 0.5.7 | local PKGBUILD from PyPI |
| `python-oracle-ads` (Accelerated Data Science) | 2.16.1 | local PKGBUILD from PyPI, built with `--skip-dependency-check` because the sdist pins `flit-core<4` and Arch ships 4.1.0 |
| `select-ai` | 1.5.0 | venv `~/.cache/gororoba-quantum/venvs/select-ai` (`uv`): it pins `pandas==3.0.3` and the system has 2.3.3 |

`langchain-oracledb` 1.6.0 has a PKGBUILD in `~/Github/PKGBUILDs` that waits
on a full system upgrade: its LangChain dependencies 404 against the host's
mirror database.
