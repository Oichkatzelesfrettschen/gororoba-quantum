# Case: restart Azure VM 2 for the E8-bar->N+ and W8->N- special fibers (method B, then A at degree 2)

**Approval.** Standing owner approval of 2026-10-29 (~10:00 UTC): new Azure cases are approved provided the case is on
file. This file is that case, written before the VM starts.

**What it measures.** The special fiber F(I) of the Pfaffian kernel-coordinate ideal I = (G) on the E8-bar closure at
N+ (9 slice variables, 21 generators) and on the W8 closure at N- (7 variables, 24 generators): projective dimension,
degree, Hilbert numerator and h_1..h_5, by pivot saturation (`templates/b_body.sing`, decision record section 2 row
"B"). This is the limit set roadmap item 6 needs (`purpose.md`).

**Why the host and Kaggle do not answer it.** The original W8 run reached 83 GB resident before h_2
(`azure-vm2/results/w8_nm_fiber.log`), the E8-bar msolve runs exhausted memory entering degree 7. Method B's memory
is unmeasured; the host carries other capped jobs (about 37 GB available) and Kaggle CPU sessions cap at about
30 GB. VM 2 gives 84 GB to one job at a time. Host-side method A at degree 2 runs first (runs/e8_a2, runs/w8_a2) and
is the first measurement; VM 2 runs B, which that host budget cannot hold if it grows like the original W8 module.

**Resource.** Existing deallocated VM `gororoba-a5-fiber-2`, westus2, Standard_FX4mds_v2 (4 vCPU, 84 GiB), its own
4-vCPU regional quota (eastus VM 1 is separate). Retail price read 2026-10-29 from prices.azure.com: 0.547 USD/h
(Linux, consumption). Trial subscription with spending limit on: usage beyond the credit is not billed; VMs are
deallocated when the credit ends.

**Run.** One job at a time, each under `systemd-run --scope -p MemoryMax=78G -p MemorySwapMax=0`, never
`prlimit --as`, `MALLOC_ARENA_MAX=2`, one Singular thread, RSS sampling every 30 s:
1. `e8_b` (method B, E8-bar), timeout 10 h;
2. `w8_b` (method B, W8), timeout 10 h.

**Expected cost.** At most 20 h x 0.547 = 10.94 USD of trial credit; a deadline watcher deallocates the VM at the
earlier of both jobs ending or 2026-10-30 08:00 UTC.

**Falsifiers.** F5 (projective dim <= 4 for E8-bar, <= 5 for W8); F6 (a nonzerodivisor pivot exists, else the job
prints `no_nonzerodivisor_pivot` and ends); h_1 = 21 (E8-bar) and 24 (W8), already measured by method A on the host;
h_2 must equal method A's degree-2 rank when both complete (F4).

**Records.** Logs, samples, `fiber.txt` and `rees.txt` copy back to `docs/local/a5-failed-runs/runs/<job>/vm2/`
before deallocation.
