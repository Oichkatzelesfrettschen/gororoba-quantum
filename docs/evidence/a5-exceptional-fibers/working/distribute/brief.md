# Distribution brief: A_5 exceptional fibers, Kaggle reset Fri 2026-10-30 17:00 PDT (2026-10-31 00:00 UTC)

Review only; run nothing. Authority: ../decision-record.md (section 10 is the final plan). Answer in under 120 lines,
written to the file named in the prompt.

## Results to decompose (observed)
- X- full fiber, pivot saturation (runs/s2): 12 h cap, exit 124, 11 h 14 min CPU, 9.4 GB peak, no output after
  "pivot 11 terms 64". Third X- stall after the pivot (3 h, 12 h, 12 h).
- VB (E8bar->VB) degree 4, method A products stage: 1 h stage cap, exit 124, 55 min CPU, 2.4 GB peak. Rerunning
  on the host with a 4 h cap, 8 GiB.
- Nullity-16 record regeneration: outer cap 3000 s reached with empty log (10 blocked rows x 300 s serial already
  fill it). Rerunning with 7200 s.
- K2 structure at p=32009, 3 GiB, 600 s (runs/k2struct): X- one prime (3,12), radical h1 12 vs 15; E8bar->N+ two
  primes (4,11),(3,4), radical h1 16 vs 21; VB radical, two primes (3,3),(3,4); Iso and W8->N- unfinished in 600 s.
  J radical and prime through 0 for all five.
- Method A succeeded everywhere it ran: X+- 15,51,122; Iso 17,85,265; E8bar->N+- 21,83; W8 24,156; VB 10,34,80.
- Second-prime headers p=32029, r=9115 are already regenerated from the Q(i) producer for all ten slugs
  (build/inputs/p32029-r9115, receipt.json).

## Compute on hand until the reset (observed from quota API 2026-10-30 00:30 UTC)
- Kaggle CPU: 5 batch sessions (one held by the queued TPU smoke), 4 cores, ~30 GB, 12 h each.
- Kaggle GPU: 26.7 h left, 2 sessions; host 4 cores ~29 GB. Singular cannot use a T4, so a GPU session is a
  third/fourth/... 4-core host and spends quota that expires unused anyway.
- Kaggle TPU: 17.9 h left, 1 queued smoke; never assigned a v5e-8 VM so far.
- Build host: 12 threads, 62 GiB, owner keeps it mostly idle; arc-certificate agent and VB d4 are running.
- GitHub Actions: ~4 CPU, 16 GB, 6 h jobs; standing approval for slow classical jobs.
- qBraid Lab: 100 free CPU hours (renews 2026-11-10), Free profile ~1.8 vCPU; a session there needs an approved case.
- Azure FX4mds_v2 (4 vCPU, 82 GiB): one per region, needs a case on file.

## Proposed distribution (Kaggle, Singular from passagemath-singular 10.8.13, the repo driver unchanged with a
## systemd-run shim that drops the cgroup flags; the session's own RAM is the boundary)
- K1 CPU: second-prime method A, degrees 2-3, for e8-vb, xm-nm, xp-np (expect 10,34,80 / 15,51,122 / 15,51,122).
- K2 CPU: second-prime method A, degrees 2-3, iso-np (expect 17,85,265).
- K3 CPU: second-prime method A, degrees 2-3, w8-nm (expect 24,156, then h3 new; W8 d3 peaked 14 GB on the host).
- K4 CPU: K2 structure at 32009 for Iso and W8->N- (radical, minAssChar, linear_gens), 11 h cap (plan step 5).
- G1 GPU host: second-prime method A degree 2 for e8-np and e8-nm (expect 21,83).
- G2 GPU host: E8bar->N+ method A degree 3 at 32009 (new h3; never computed).
- Host: arcs (agent), VB d4, regen. Nothing on qBraid, Azure or GitHub Actions in this round.

## Questions
1. Is each job's falsifier right? A second-prime h that differs from the first prime's means: bad prime, producer
   drift, or a driver bug. Which?
2. Is anything here a stalled family in new clothes (method B, std(L), full msolve)? Is minAssChar on Iso/W8 K2 at
   11 h a reasonable bet, or should it be the chart-by-chart route the plan names?
3. Better use of the 6 Kaggle slots before the reset, given the arc certificate is the main line?
4. Should GitHub Actions or qBraid Lab take any job instead?
