# Final review of the Ascella CZ compilation-ensemble design, 2026-11-06

Subject: [ascella-cz-compilation-ensemble-case.md](../../design/ascella-cz-compilation-ensemble-case.md) and
`scripts/ascella_cz_served_mesh.py` on branch `quandela/ascella-cz-served-mesh` (pull request 770), at commit
eec5a9189. Three reviewers worked from one brief:

- `codex` on gpt-daybreak-blue-latest at high effort, in a read-only sandbox with tools;
- an Opus agent with the pinned interpreter;
- `grok` headless without tools, on an inlined packet.

Each finding was checked against the source before it counted. The design and script changes that resolve them land
in the same pull request.

## Findings that survive

| Finding | Reviewers | Check | Resolution |
|---|---|---|---|
| The [0.9, 1.1] eligible-rate rule does not make the per-input Hofmann bound sound. | Codex (blocker), Grok (S1, S2) | Codex's single Kraus map passes the rule (ratios 0.906 to 1.094) and violates the lower bound by 0.0034 (L 0.3631, F 0.3596); reproduced exactly. | The rule is gone. The rate-weighted score (sum of correct rates over sum of eligible rates per table) is primary. Each table's inputs form a basis, so its normalization is the Choi trace and the bound holds for any trace-non-increasing CP map: no violation over 20 000 random maps (orchestrator) and 200 000 (Opus), and on both counterexamples. |
| The one-process test cannot detect a twisted pair of processes, so no reading may rest on the bound. | Grok (blocker), Opus (major), earlier Copilot | CZ·Z_control on every ZX setting reproduces each ZX setting's served law exactly, with fidelity 0. | The result is the two rate-weighted scores. [L, U] is a statement conditional on the one-process and shot-denominator hypotheses, and no reading uses it. |
| 0.849 is a non-positive Choi fit, so it is not the estimand of the bound. | Grok (major) | The design itself records the non-positive fit. | New estimate 5 compares each ensemble score with the score the retained tomography fit predicts for the same eight settings. |
| The 200-event floor selects on the quantity under study, and dropping seeds contradicts the fixed 9 degrees of freedom. | Codex (two majors), Grok (major), Opus (suspicion) | Logic; the retained minimum is 423 events. | Every one of the 120 iterations must return counts with at least 200 eligible events, or the case is undecided. |
| Only the between-job anchor test gated pooling. | Codex (major), Opus (minor: recalibration) | Logic. | Within-job tests for each job, a between-job test and a between-job eligible-rate test per anchor (16 at 0.01, Bonferroni). Differing anchor digests between jobs mean a recalibration, and the jobs are reported separately. |
| Two separate 95 % ends do not give a 95 % joint interval, and the seed pairing was undefined. | Codex, Opus, Grok | A Bonferroni bound gives 0.90. | L at one-sided 97.5 %, each table's upper limit at 98.75 %. The seed index is the pre-data draw order. |
| "Mesh variance exceeds binomial in more than half the settings" fires about 24 % of the time on pure shot noise. | Codex, Opus, Grok | Reproduced: P(χ²₉ > 9) = 0.437; P(≥ 5 of 8) = 0.237. | Monte Carlo multinomial homogeneity test per setting at 0.01, Bonferroni over 8. |
| The chi-square anchor test is invalid at sparse cells. | Codex (suspicion) | About 0.67 expected events per wrong cell at 0.99 fidelity. | Monte Carlo multinomial homogeneity tests. |
| The forecast transferred nine-readout input means to single-readout settings. | Codex, Grok | The exact settings read 0.829, 1.147, 0.955 and 0.886; the |−> inputs have no retained analog. | The design quotes the exact settings and marks the |−> inputs unmeasured. The rate rule is gone, so the forecast is now descriptive context. |
| Rail transmission does not explain the eligible-rate variation. | Opus (major) | Reproduced: the per-rail ratios read 1.357 against 1.009; a partial-distinguishability mixture fits V = 0.922 (correlation 0.953, rms 0.026). | Stated as a hypothesis with both numbers. |
| The 1.4 and 2.6 credits were plan ceilings, not charges, and the 2.6 came from in-10-ZZ. | Opus (minor) | `shot-estimate.json`: in-10-ZZ 1 201 113 shots; this design's analogs 133 457 to 240 223. | Corrected, with the 400 000-shot cap and about 1.4 credits per job. |
| The Perceval agreement of the decoder had no durable check. | Codex (minor) | Full comparison: 6.7e-16 over all 144 meshes (Opus). | `tests/scripts/test_ascella_cz_served_mesh.py`: 8 spread meshes unmarked, all 144 under the audit marker, and a mutation that must fail. |
| "Moduli alone" holds for indistinguishable photons only. | Opus (minor) | The distinguishable law passes over 144 meshes (TVD 6.7e-4). | Docstring corrected; the test holds the distinguishable law. |
| The HOM may drift between the tomography and the ensemble. | Opus (minor) | Model estimate 0.013 per HOM point (hypothesis). | A reading states the HOM difference beside each comparison. |

## Findings refuted

| Finding | Reviewer | Evidence against it |
|---|---|---|
| "600 eligible events and 4 % binomial" contradicts the 1.4 and 2.6 credit charges, so the floor or the ceiling must fail. | Grok (blocker) | An iterated job bills at most its largest iteration's `max_shots` (`qd_platform.job_billing`). The retained settings used 145 862 to 1 071 349 shots each, with 423 to 3873 eligible events, under job ceilings of 1.4 and 2.6 credits. The design now states the billing rule. |

## Not resolved by this review

- Both hypotheses of the conditional bound stay untested by construction.
- The false-alarm rates of estimates 1 and 2 at the forecast are simulated in the build, step 2 of the design's
  submission list.
- Hofmann 2005 is not yet registered in the source library.
