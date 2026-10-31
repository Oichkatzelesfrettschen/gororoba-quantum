# OCI Always Free lab: machines, storage, network and service roles

The Oracle Cloud tenancy described in
[the provider guide](../notes/oracle_cloud/README.md) runs a three-machine lab
inside its Always Free limits, plus two Autonomous Databases used as Python
notebook compute. This document records the design and the measured facts
that decided each part; [the lab runbook](../runbooks/oci-lab.md) holds the
commands. Every resource below bills $0 under the tenancy's Always Free
limits, and the `lab-guard` budget (1 USD per month, alerts on any actual
spend and on a 1 USD forecast) reports a departure within a day.

## Machines

| Host | Shape | OS | Subnet | Role |
|---|---|---|---|---|
| `lab-edge` (instance `lab-edge-deb`) | `VM.Standard.E2.1.Micro`: 1/8 OCPU with burst, 1 GB | Debian 13 genericcloud | public `10.42.0.0/24`, `10.42.0.11`, reserved public IP | WireGuard server, NAT router for the private subnet, SSH entry |
| `lab-micro2` | `VM.Standard.E2.1.Micro` | Debian 13 genericcloud | private `10.42.1.0/24`, `10.42.1.30` | MATE desktop over xrdp, utility host |
| `lab-a1` | `VM.Standard.A1.Flex`: 2 OCPU, 12 GB | Ubuntu 26.04 aarch64 | private, `10.42.1.20` | the lab's compute host, NFS server of `/scratch`, Run Command target |

`lab-a1` waits on Oracle capacity: San Jose has one availability domain, and
`LaunchInstance` returns `Out of host capacity` for the A1 shape.
`scripts/oci_lab/a1_retry.sh` attempts the launch every 30 minutes for at most
48 hours in the tmux session `oci-a1-retry` and stops on success or on any
other error.

### Operating systems

Oracle Solaris 11.4 is a free Marketplace image in San Jose, but its listing
names only x86 shapes outside Always Free (Standard1 to 3, E5, E6, DenseIO,
GPU and HPC); neither `VM.Standard.A1.Flex` nor `VM.Standard.E2.1.Micro`
appears, so no Solaris release runs on this tenancy. Oracle Linux is
Oracle's Linux distribution and carries no Solaris code. illumos has no
supported aarch64 port, and the tenancy cannot import an image (below).

Oracle Linux 9.7 Minimal failed on the 1 GB micro in three independent ways,
each observed on the instance:

- `dnf`'s repository metadata for the five enabled Oracle Linux 9 repos held
  680 MB of resident memory and filled 2 GB of swap, and the host stopped
  answering SSH for more than 20 minutes;
- the Oracle Cloud Agent plugins drove memory to 94-98 % right after boot,
  and an ACPI soft reset stalled in STOPPING until OCI forced it;
- the UEK 8 kernel `6.12.0-105.51.5.el9uek` refused `wg-quick` with
  `Protocol not supported`: its WireGuard module lives in
  `kernel-uek-modules-extra`, which `dnf` cannot install on this host.

Debian 13 genericcloud (kernel `6.12.113+deb13-cloud-amd64`) idles at 211 to
223 MB used of 962 MB, ships `wireguard.ko`, installs packages with `apt` on
1 GB without swapping, and runs cloud-init's `DataSourceOracle`, which injects
the SSH key and grows the root filesystem to the 50 GB boot volume.

The tenancy's `custom-image-count` quota is 0 (`ImportImage` returns
`QuotaExceeded`), so Debian enters through a preserved boot volume:
`scripts/oci_lab/debian_bootvol.sh` terminates an instance with
`--preserve-boot-volume true`, attaches the volume to a running writer
instance, writes Debian's genericcloud image raw (checked against Debian's
`SHA512SUMS`), detaches it and launches the new instance from it. Each
rebuild reuses the boot volume, so the block-storage total stays unchanged.

The Oracle Cloud Agent comes from the snap store (`oracle-cloud-agent`
1.63.0-9, publisher Oracle Cloud Infrastructure, classic confinement), the
same channel Ubuntu images use. On a micro it adds about 70 MB of resident
memory (snapd 52 MB, agent, Run Command and workload-protection plugins). The
lab keeps Run Command, Compute Instance Monitoring and Bastion enabled and
disables Cloud Guard Workload Protection, Vulnerability Scanning, Management
Agent and Block Volume Management; OS Management Hub reports
`NOT_SUPPORTED` on Debian.

## Block storage: 200 GB

`LaunchInstance` refuses a boot volume below 50 GB ("Boot volume should be
greater than or equal to 50GB"), although Oracle's Always Free page names 47
GB in one section. The 200 GB grant therefore splits into three 50 GB boot
volumes and one 50 GB data volume, `lab-data`, attached paravirtualized to
`lab-a1` at `/dev/oracleoci/oraclevdb`.

ZFS pools belong to one host, and a block volume formatted with ext4 or ZFS
attaches read-write to one instance, so the shared scratch is one
filesystem served over the private network. The plan, which waits on
`lab-a1` and its `volume` phase: `lab-data` carries ext4 at `/scratch` on
`lab-a1` (`_netdev,nofail` in fstab, so a missing volume never blocks boot)
and is exported over NFSv4 to `10.42.0.0/16` and `10.66.0.0/24`; every
Debian and Ubuntu host mounts it with `nfs-common`. ext4 and NFSv4 serve
Debian, Ubuntu and any later Linux host alike. Object Storage (20 GB) holds
what must outlive the instances: results, images and Run Command output. The
five free volume backups cover the `lab-data` volume and the three boot
volumes, one backup each plus a spare.

## Network

One VCN, `10.42.0.0/16`, holds two subnets:

- `lab-public` (`10.42.0.0/24`) routes `0.0.0.0/0` to the internet gateway;
  its security list admits TCP 22, UDP 51820 and ICMP type 3 code 4 from
  anywhere and all traffic from the VCN.
- `lab-private` (`10.42.1.0/24`) prohibits public IPs and routes
  `0.0.0.0/0` and the WireGuard range `10.66.0.0/24` to the edge's private
  IP. Its security list admits all traffic from the VCN and the WireGuard
  range.

The tenancy's `vcn` limits list an internet gateway but no NAT gateway, so
the edge is the NAT: its VNIC skips the source and destination check, IPv4
forwarding is on, and nftables masquerades VCN and WireGuard sources leaving
`ens3`. The edge's nftables input chain admits SSH, WireGuard, ICMP, the VCN,
the WireGuard range and the link-local metadata range and drops the rest;
`lab-micro2` admits SSH, NFS (2049) and RDP (3389) only from the VCN and
WireGuard ranges.

WireGuard (`wg0`, `10.66.0.1/24`, UDP 51820) is a split tunnel: a peer routes
only `10.42.0.0/16` and `10.66.0.0/24` through it. Every key is generated on
its own host; only public keys move.

Oracle caps an E2.1.Micro at 50 Mbps to the internet and 480 Mbps to private
endpoints, so every download by `lab-a1` and `lab-micro2` passes through the
edge at no more than 50 Mbps and shares its 1/8 OCPU. Traffic inside the VCN
and to Oracle services in the region is unaffected.

### Control paths

| Path | Reaches | Survives |
|---|---|---|
| SSH to the edge, then `ProxyJump` | all hosts | the edge's sshd and the internet gateway |
| WireGuard | all hosts, RDP, NFS | the edge's `wg0` |
| OCI Bastion `lab-bastion` (managed SSH or port forwarding into `lab-private`) | private hosts | the edge failing entirely |
| Run Command over REST (`scripts/oci_lab/run_command.py`) | any host with the agent | SSH and WireGuard failing, while the host reaches OCI |
| Serial console connection (`oci compute instance-console-connection create`) | any host, at the console | the guest network failing |
| Cloud Shell in the console | the OCI API, and the hosts through Bastion | the workstation failing |
| Instance actions (`SOFTRESET`, `RESET`, `STOP`) | any host | everything inside the guest |

## Autonomous Databases as notebook compute

`lab-adb-dw` (Data Warehouse) and `lab-adb-oltp` (Transaction Processing) are
Always Free 23ai databases, each fixed at 1 OCPU and 20 GB of storage;
Oracle publishes no memory figure for them. Each holds the notebook user
`LABML` with `OML_DEVELOPER` and `DWROLE`. The public endpoints admit the
operator's address and the edge's address and require mutual TLS.

OML4Py embedded execution runs inside the database: `pyqEval` from SQL
returned Python 3.13.5, numpy 2.4.6, pandas 2.2.3 and scikit-learn 1.6.1 on
both databases, and a float64 sum over a million elements returned
499999500000. `os.cpu_count()` inside the embedded process reports 16, the
host's count; the service still caps the database at 1 OCPU. SQL-invoked
embedded Python calls back to the OML REST service, so `LABML` needs a host
ACE on the root domain (`pyqAppendHostACE`) and a token from
`/omlusers/api/oauth2/v1/token` (`pyqSetAuthToken`).

The databases serve three roles: an OML Notebooks workspace with the bundled
interpreter and `%conda` environments (8 GB each, stored by the service), a
data-parallel engine (`pyqGroupEval`, `pyqRowEval` and `pyqTableEval`
partition rows across embedded Python invocations), and a scheduler
(`DBMS_SCHEDULER` runs jobs while every VM is down). `lab-adb-oltp` also
holds JSON collections and ORDS REST endpoints for run records.

## Service roles beyond the machines

Free status cites Oracle's
[Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
page unless the row says otherwise; a limit value alone shows only what the
tenancy may create.

| Service | Allowance | Lab role | Free status |
|---|---|---|---|
| MySQL HeatWave | 1 standalone DB system with a single-node HeatWave cluster, 50 GB data and logs, 50 GB backup | in-memory columnar analytics and HeatWave AutoML over result tables, on a private IP in `lab-private` | Always Free page |
| NoSQL Database | 133 M reads and 133 M writes per month, 3 tables of 25 GB | job queue with conditional writes, shot-level results with TTL; client `borneo` | Always Free page |
| Resource Manager | stacks 100, concurrent jobs 1 on this tenancy (the page says 2), 24 h per job | the lab as a Terraform stack, rebuildable after a reclamation; a `local-exec` step runs a script on Oracle's runner, outside the service's documented purpose | Always Free page |
| Container Registry | registry free; image storage billed at the Object Storage Standard rate ([product page](https://www.oracle.com/ua/cloud/cloud-native/container-registry/)) | multi-arch lab images for the VMs and Functions | inferred free within the 20 GB Object Storage grant; the budget alert confirms |
| Functions | `faas` 61440 MB total concurrency | burst fan-out of short pure-Python jobs | absent from the Always Free page; unverified |
| DevOps build runners | 3 concurrent | none | billed: the managed build stage charges for the runner's OCPU and memory ([managed build stage](https://docs.oracle.com/en-us/iaas/Content/devops/using/managed_buildstage.htm)) |
| Cloud Shell | 80 usage hours per month (tenancy limit), 5 GB home, 24 h sessions, 60 min idle timeout ([Cloud Shell](https://docs.cloud.oracle.com/Content/API/Concepts/cloudshellintro.htm)) | browser control plane with the CLI and Terraform | free within the tenancy limits (Cloud Shell page) |
| Bastion | 5 bastions (tenancy limit) | `lab-bastion` on `lab-private` | Always Free page |
| Monitoring, Notifications, Connector Hub | 500 M ingestion data points, 1 M HTTPS and 1000 email notifications per month, 2 connectors | event pipeline that replaces poll loops | Always Free page |
| APM | 1000 tracing events and 10 synthetic monitor runs per hour | scheduled external probe of provider endpoints | Always Free page |
| Email Delivery | 3000 emails per month (page), 100 per day (tenancy limit) | run notifications | Always Free page |
| Vault | software keys free, 20 HSM key versions, 150 secrets | lab secrets, replacing files under `~/.oci/lab` | Always Free page |
| Outbound data transfer | 10 TB per month | result mirrors | Always Free page |
| Load balancer, network load balancer | 1 flexible LB at 10 Mbps, 1 NLB | none | Always Free page |
| Site-to-site VPN, Certificates | 50 IPSec connections; 5 CAs, 150 certificates | none | Always Free page |

### Full limits audit

`LimitsClient.list_limit_values` over all 128 services of 2026-10-31
returned nonzero values for 49 of them: `adm`, `announcements`, `apm`,
`atat`, `auto-scaling`, `block-storage`, `certificates`, `cloud-shell`,
`cloudguard`, `compartments`, `compute`, `compute-management`,
`container-registry`, `dashboard`, `data-catalog`, `data-integration`,
`database`, `dbtools`, `devops`, `digital-assistant`, `email-delivery`,
`faas`, `identity`, `java-management`, `kms`, `limits`, `load-balancer`,
`logging`, `management-agent`, `monitoring`, `mysql`,
`network-load-balancer-api`, `network-path-analyzer`, `nosql`,
`notifications`, `object-storage`, `oci-bastion`, `psacp`, `regions`,
`resource-collection`, `resource-manager`, `resource-scheduler`, `rndrive`,
`secrets`, `security-attributes`, `service-connector-hub`, `tagging`, `vcn`
and `vpn`. The table above assigns a role to every service that executes
code or stores lab data. The remainder are governance and metadata services
(tagging, compartments, dashboards, announcements, security attributes,
resource collections), which carry no compute. Three notable entries:
`dbtools` allows 2 database MCP servers, `resource-scheduler` allows 20
schedules (start and stop instances on a timetable), and `regions` allows one
subscribed region, so the tenancy cannot add a second region and Oracle
fixes the home region at sign-up.

## Idle reclamation

Oracle reclaims an Always Free instance whose 95th-percentile CPU and network
utilization stay below 20 % over 7 days, with memory also below 20 % on A1
shapes. `lab-a1` on a private subnet is the likeliest target. Two pending
measures answer it: steady work on `lab-a1` that keeps one of the three
measures above 20 %, and a Resource Manager stack of the lab that rebuilds a
reclaimed host. Neither exists yet.
