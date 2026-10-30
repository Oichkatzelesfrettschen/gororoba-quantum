# Final-plan consult: A_5 exceptional fibers, with every result and the whole lab

You are one of several independent reviewers (Grok, agy/Gemini, opencode on Groq). This bundle is the whole
evidence. Read it in full; then write your answer. Do not run anything.

Bundle order after this brief: purpose.md, decision-record.md (the authority, every success and failure),
lab-map.md (every machine, service, quantum provider, QRNG, cloud compute, LLM API and policy gate),
greater-picture-gpt-daybreak-blue-latest.md and greater-picture-gpt-6.1-terra.md (two earlier Codex consults),
docs/PYTHON.md and docs/runbooks/compute-flags.md.

## Resolved local findings to build on (each verified in the decision record)

1. Degree-by-degree method A is exact and has succeeded on every pair: X+- h=15,51,122; Iso 17,85,265;
   E8bar->N+ and N- 21,83; W8 24,156; E8bar->VB 10,34,80 (reproduced by the new driver). Nullity-16: eight fibers
   complete (B9: P^2; V: conic; VB, Va: points).
2. Every full-fiber completion (pivot saturation, candidate-ideal std(L)) stalled after the pivot: X- 3 h and 12 h,
   Iso 6 h, VB 2 h, E8bar->N+- 10 h at 72 GB, VB std(L) 3 GB. W8 was cut off by a VM outage (not a stall).
3. The 2.5 GB "no more memory" exits of the nullity-16 producer came from an inherited RLIMIT_AS of 4 GiB set by
   a Python helper, not from the configured cap; cgroup MemoryMax is the only permitted limit.
4. Kaggle TPU v5e-8 queue: 6+ h without assignment for a small smoke kernel.
5. The Codex consults converge on exact arc families with a Jacobian density certificate (VB, then X-), a
   syzygy/Jacobian-dual probe, and VB h4 vs 155 as a diagnostic (running now).

## Questions

1. Attack the converged plan. Where is the arc-family certificate wrong, incomplete, or harder than it looks
   (positive characteristic, inseparability, arithmetic vs geometric primes, nonreduced K2, components missed)?
2. Give one concrete construction of an arc family for E8bar->VB or X- from the data in the bundle (which
   coordinates to parametrize, how to solve J=0 along the arc, what degree in s to expect), as Singular, M2 or
   Sage code a reviewer can run on the host in under 8 GiB.
3. Name any route the two Codex consults missed, using any capability in lab-map.md, including quantum backends,
   QRNG, cloud LLM APIs, Kaggle, Azure, GitHub Actions or local GPU. Say plainly when a capability does not
   apply to this classical algebra problem.
4. Produce a stepwise plan: ordered steps, each with resource, memory cap, time limit, the result it yields, and
   the falsifier that stops it. Mark each claim observed (cite the bundle section) or inferred.

Keep the answer under 200 lines.
