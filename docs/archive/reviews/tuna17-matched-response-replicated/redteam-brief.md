# Red-team brief: replicated Tuna-17 matched-response proposal (Stein two-stage t test)

Read first: the workspace AGENTS.md, then AGENTS.md ("Hardware services", "Seeds", "Grounding and algebra"). You are a red-teamer: try to break the case. Work read-only: change no file, never commit, push, stash, submit to a provider, call a provider API or start a cloud resource; spawn no subagents; run no test suite and no computation longer than 2 minutes on this host (git, grep and short python3 arithmetic, including a small numpy simulation under 2 minutes, are fine).

Nothing has been submitted. The owner will be asked to approve stage 1 of this proposal on Quantum Inspire Tuna-17: 12 batches of 3 circuits, 36 jobs, 16,384 shots each, 406 device seconds, 22 minutes of pauses, 0 credits; and, by the preregistered rule, a stage 2 up to 60 batches in total (180 jobs, 2,031 device seconds).

Tree:  (branch tuna17-matched-response-analysis, draft pull request 998, head 7a4ff6de1). Under review: the last three commits (git log -3; git diff aa669e375..HEAD): gororoba_quantum/qi_replicated_response.py, scripts/qi_matched_zero_divisor_replicated.py, scripts/qi_replicated_stein_simulation.py, tests/scripts/test_qi_replicated_response.py, docs/design/tuna17-matched-response-replicated.md, results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-replicated-q11/. Background: the nine-job predecessor could not decide because its residual did not cancel a region-by-batch interaction (null SD about 0.038 against shot noise 0.0084).

## Claims under review (each is a claim, not a fact)
1. Putting both weighted witness circuits in one batch removes the batch-by-region interaction from the per-replicate residual r_i, and the raw residual's null is equal readout-factor-times-visibility in the two regions: R = (g_2 - g_1)/2 under P_obs = a_r + g_r P.
2. The Stein two-stage rule (n1 = 12, N from s1 alone with constant c = 3.6339e-05, final t on 11 degrees of freedom with s1, reject at |t| >= 3.1058, cap 60) has level 0.01 under normal exchangeable r_i, and the stated power table is right.
3. The schedule (witness order alternating by replicate, readout-0/readout-1 alternating every two replicates) balances order and readout context against a linear drift; the lag-1 and order checks detect a failure of exchangeability.
4. The analysis binds to this proposal and refuses a wrong proposal, a wrong circuit, a reordered schedule, a missing replicate, and a stage 2 whose N differs from the rule; each refusal has a test that can fail.
5. The 60 batches reuse the q11 circuit bytes under their frozen digests; the manifests submit through scripts/qi_platform.py unchanged (each batch <= 3 circuits; the manifests carry nqubits 17 where the q11 manifests do not).
6. Costs: 33.85 device seconds per batch; stage 1 406.2 s; cap 2,031 s; credits 0.

## What to attack
- Stein's procedure: is the N rule applied exactly (N depends on s1 only; the final statistic uses s1 not the pooled SD; what if N from the rule is below 12 or the run stops between stages)? Does the cap or the "undecided at the cap" stop bias the level? Recompute c from the t(11) quantiles. Is the alternative hypothesis value (-0.024) justified once both circuits share a batch (the prediction was made for the two-batch design)?
- Within-batch structure: the three circuits of one batch still run in sequence; does drift within a batch, or the position of the readout circuit, enter r_i with a nonzero mean under the null? Does the alternating order cancel it or convert it to variance? Is the raw residual's nonzero mean under equal visibilities but unequal readout factors (q4 against q11) a guaranteed false rejection? Quantify from the retained readout numbers in docs/design/tuna17-matched-response-region2-selector-q11.md (q11 readout factor 0.933; find q4's).
- Odd N and partial blocks of four; the exploratory corrected estimator's label; the multiplicity of the secondary checks.
- The binding: a path by which a wrong run, a reordered batch, a duplicated replicate or a stage-2 run with a different N passes; a test that cannot fail.
- The Quantum Inspire pause and queue limits for 12 consecutive batches, and anything in docs/notes/quantum_inspire/ that forbids or reshapes it.
- Anything in the diff that edits a digest-bound file, breaks a retained record, or leaks a host name, address or absolute path.

Deliver ranked findings, each tied to a file:line or a short computation and marked proved, computed or hypothesis, each with a concrete change. Then a verdict: submit stage 1 as is, submit after named changes, or do not submit. End with the claims you could not break and what you tried.
