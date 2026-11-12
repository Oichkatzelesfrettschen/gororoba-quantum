# Reviews of the kernel-plane limits and the fiber-to-Grassmannian map (pull request 817)

Two local reviewers read the branch on [brief.md](brief.md): the `codex` command-line agent on gpt-daybreak-blue at
high effort ([review-codex.md](review-codex.md)) and NVIDIA nemotron-3-ultra through the read-only analyst harness
([review-nemotron.md](review-nemotron.md)). The Advisor step did not run: the `advisor` tool was not available in the
session. The hosted Codex and Copilot rounds followed on the pull request. `A5-NNN` is a row of
[the A_5 claim ledger](../../../evidence/a5-exceptional-fibers/ledger.tsv).

| Source | Finding | Verdict | Disposition |
|---|---|---|---|
| codex (local) | the identity between the two VB parametrizations is stated with the wrong sign | survives | with e = (1 + i kappa)/(1 - i kappa), i omega = -kappa/(1 + kappa^2), so k = -kappa; `vb_special_arcs.py` and the README are corrected |
| codex (local) | the SHA-256 parameter values are called generic without a test | survives | the README states what the sample establishes; the mutation arm and `distinct_fiber_points` are added |
| codex (local) | the fit records carry no verdict and the script exits 0 on a failed fit | survives | each case holds a verdict and the script exits nonzero unless every case reads `degree_2_fit_validated` |
| codex (local) | A5-295 cites a runtime that no record retains | survives | the clause is removed |
| nemotron (local) | the fit is a construction and not a test | refuted | the held-out arcs are independent of the fitted ones and the shifted pairing of the mutation arm has no solution in every record |
| Codex (hosted) | the fit cases of a family run serially | survives | they run through `parallel.ordered_map`; two recomputed records are byte-identical |
| Codex (hosted) | a held-out arc whose fitted vector is zero counts as agreement | survives | agreement needs a nonzero fitted vector proportional to the Plucker vector |
| Copilot (hosted) | `--held-out 0` reports a validated fit | survives | the verdict needs a nonempty held-out set |
| Copilot (hosted) | a rejected arc shifts the fit and held-out split | survives | the split goes by arc index and a run with a rejected arc exits nonzero; no committed record dropped an arc |
