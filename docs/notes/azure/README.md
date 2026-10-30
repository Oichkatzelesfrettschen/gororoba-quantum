# Azure (Azure Quantum workspace and the trial subscription)

The owner's Azure subscription is a free trial in the `hilg.art` directory,
and it holds one Azure Quantum workspace whose providers are free plans only.
The workspace reaches the Quantinuum H2 syntax checker and emulator, a Pasqal
neutral-atom emulator and Rigetti's QVM; no hardware target is attached. The
facts below were read on 2026-10-24; the portal and the CLI stay the
authority.

## Subscription and spend

| Item | Value | Source |
|---|---|---|
| Subscription | "Azure subscription 1", Enabled | `az account show` |
| Offer | `FreeTrial_2014-09-01` | subscription policies (`az rest .../subscriptions/{id}?api-version=2022-12-01`) |
| Spending limit | On | same, `spendingLimit` |
| Registered providers | `Microsoft.Quantum`, `Microsoft.Solutions` (the provider plans deploy through it), `Microsoft.Storage`, `Microsoft.Compute` | `az provider show` |

The trial carries 200 USD of credit for 30 days, and its spending limit
equals that credit and cannot be raised, only removed
([spending limit](https://learn.microsoft.com/azure/cost-management-billing/manage/spending-limit),
updated 2026-04-30). When the credit is spent, Azure removes the deployed
resources from production, stops and deallocates virtual machines, and
leaves storage readable only; nothing is billed. Within 30 days of sign-up
or when the credit is exhausted, the subscription must be upgraded to
pay-as-you-go to keep running
([free account offer](https://azure.microsoft.com/pricing/offers/ms-azr-0044p)).
The upgrade removes the spending limit and starts billing for usage beyond
the 12-month free services, so it is the owner's decision alone. Without an
upgrade the subscription stays disabled; neither page states when its data
is deleted, so anything worth keeping leaves it before the trial ends.

The spending limit does not stop every charge: "some external services
published in the Azure Marketplace can't be used with your subscription
credits, and can incur separate charges even when your spending limit is
set" (same page). Azure Quantum provider plans are Marketplace offers (each
names a publisher), so a paid plan would bill the card even under the
limit. The workspace therefore holds only the free plans, and adding any
other plan is the owner's decision. The
trial credit balance is shown in the portal (Cost Management) and has no
reliable CLI read for this offer: the consumption API refuses the trial's
billing-period query. The subscription id, tenant id and account email stay
out of every commit and record.

## Sign-in

`azure-cli` 2.90.0 comes from the Arch `extra` repository, with the
`quantum` extension 1.0.0b30 (preview; no stable release exists):

```sh
az login --use-device-code
az extension add --name quantum
```

`az login` refuses a directory with no subscription ("No subscriptions
found"); `--allow-no-subscriptions` signs in at directory level, which is
how the subscription created after the first sign-in became visible.

## Quantum workspace

| Item | Value |
|---|---|
| Resource group, workspace | `gororoba-quantum`, `gororoba-quantum`, region eastus |
| Storage | one StorageV2 account, Standard_LRS, TLS 1.2 minimum, HTTPS only, no public blob access |
| Created with | `az quantum workspace create ... -r "quantinuum/basic1, pasqal/pasqal-azure-free-plan, rigetti/azure-basic-qvm-only-unlimited" --skip-autoadd`, after `az quantum offerings accept-terms` for each plan |

`--skip-autoadd` keeps Azure from adding the plans it attaches by default,
so the workspace holds exactly the three free plans:

| Target | Plan | Quota | Status |
|---|---|---|---|
| `quantinuum.sim.h2-1sc` (H2 syntax checker) | `basic1` | free | available |
| `quantinuum.sim.h2-1e` (H2 emulator) | `basic1` | 1,000 eHQC, one-time (`period` Infinite) | available; queue time 16578 |
| `pasqal.sim.emu-free` | `pasqal-azure-free-plan` | 5 emulator hours a month | available |
| `rigetti.sim.qvm` | `azure-basic-qvm-only-unlimited` | none | available |

An emulator job costs eHQC by the Quantinuum formula
`HQC = 5 + C(N1q + 10 N2q + 5 Nm)/5000` (Azure pricing page), so the
one-time 1,000 eHQC pays for about 18 jobs of 1,000 shots on a circuit with
20 two-qubit gates and 10 measurements (5 + 1000 x (200 + 50) / 5000 = 55
eHQC each, before single-qubit gates). The syntax checker costs nothing and
validates a circuit against H2 before any emulator job. The H2 emulator
models the all-to-all trapped-ion device with mid-circuit measurement and
conditional operations, which the repository's other accounts cannot
emulate; it answers how the
[Quantinuum access draft](../../design/provider-access-requests.md) circuits
compile and behave before any hardware request.

The catalog's other plans are paid and stay off the workspace: IonQ
pay-as-you-go (its simulator is free, its QPU jobs bill up to a $10,000
default quota), Quantinuum Standard and Premium (10K and 17K HQC a month),
and the Pasqal and Rigetti pay-as-you-go plans. The IonQ simulator is
reachable free through the IonQ key ([ionq/README.md](../ionq/README.md))
and qBraid ([qbraid/README.md](../qbraid/README.md)).

## Classical compute on the trial

`az vm list-usage -l eastus` caps the subscription at 4 total regional vCPUs
and 3 low-priority vCPUs. The cap is per region: westus2 reports its own
`cores` and `FXmdsv2` limits of 4, so two `Standard_FX4mds_v2` VMs run at
once only in two regions, one in eastus and one in westus2. GPU sizes are unavailable in practice: the T4
family (`Standard NCASv3_T4`) has a quota of 0, and the legacy NC and NV
families sit under the same 4-vCPU regional cap. HPC families (HB, HC, HX)
read 0.

The one size that exceeds the build host is `Standard_FX4mds_v2`: 4 vCPUs
and 84 GB of memory, deployable in eastus within the `FXmdsv2` family quota
of 4. A complex128 statevector of 32 qubits and a density matrix of 16
qubits each need 64 GiB, one qubit past the build host's 62 GiB (statevector
31, density matrix 15; [substrates.md](../kaggle/substrates.md)). Such a VM
draws the trial credit by the hour, so a run on it is a written case with
its expected hours and a deallocation step, like any spend.

## Use in this repository

Every job on any Azure Quantum target, the free emulators included, waits
for the owner's approval of a written case (root AGENTS.md, "Hardware
services"). The provider credits monitor reads the workspace quotas and the
spending-limit state daily ([provider-credits.md](../../runbooks/provider-credits.md)).
