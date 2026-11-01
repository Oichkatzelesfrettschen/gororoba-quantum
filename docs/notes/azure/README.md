# Azure Quantum

The workspace's Azure subscription is a free trial holding one Azure Quantum
workspace whose providers are free plans only. The workspace reaches the
Quantinuum H2 syntax checker and emulator, a Pasqal neutral-atom emulator and
Rigetti's QVM; no hardware target is attached. The portal and the CLI stay the
authority.

Every job on any Azure Quantum target, the free emulators included, waits for
the owner's approval of a written case (root AGENTS.md, "Hardware services").
A trial VM draws the trial credit by the hour, so a classical run on it is a
written case with its expected hours and a deallocation step, like any spend
([classical-compute-pool.md](../../runbooks/classical-compute-pool.md)).

The subscription, its spending limit, sign-in, the workspace's resource group,
region and storage, the regional quotas and the VMs are recorded in the private
gororoba-infrastructure repository.
