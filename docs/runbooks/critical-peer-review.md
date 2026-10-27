# Critical peer review of quantum-hardware results

This runbook is the checklist a reviewer follows for a document that reports a quantum-hardware measurement, a
preregistered contrast or a correlation computed from one: a case record, a findings note, a claim in
[research_state.json](../state/research_state.json), a pull request that retains a run. It covers review of the result
and of the words around it; the submission gates of [AGENTS.md](../../AGENTS.md#qpu-time-and-calibration) cover whether
a run may happen at all. Each item names the check, the signal that fails it, and the source note that grounds it.
Locators are PDF pages of the retained copy named in each note.

A reviewer re-derives a number before judging it. Every item ends in one of three verdicts: `pass` with the artifact
path that shows it, `fail` with the line or value that breaks it, or `not run` with the reason. A review that leaves an
item without a verdict is incomplete.

## Sources

| Short name | Note | Scope used here |
|---|---|---|
| Ioannidis | [ioannidis-2005-false-findings.md](../notes/papers/ioannidis-2005-false-findings.md) | positive predictive value of a significant finding under bias, number of teams, effect size |
| Munafo | [munafo-2017-reproducible-science.md](../notes/papers/munafo-2017-reproducible-science.md) | preregistration, outcome switching, disclosure, data masking, registered reports |
| ASA | [asa-2016-p-value-statement.md](../notes/papers/asa-2016-p-value-statement.md) | six principles on p-values (from the ASA release; the statement body is unread) |
| cocor | [diedenhofen-musch-2015-cocor.md](../notes/papers/diedenhofen-musch-2015-cocor.md) | direct tests for comparing correlations, formulas and a reproduction check |
| Eisert | [1910.06343.md](../notes/papers/1910.06343.md) | certification framework: assumptions, i.i.d., trusted measurement, simulable regimes |
| Proctor | [2407.08828.md](../notes/papers/2407.08828.md) | benchmark properties, drift and non-Markovian error, compilation, error mitigation |
| Quantum | [quantum-journal-referee-instructions.md](../notes/papers/quantum-journal-referee-instructions.md) | the questions a journal asks a referee, including reproducibility of experiments |
| van Enk | [1302.0932.md](../notes/papers/1302.0932.md) | common-state assumption and source drift (already in the library) |

The APS Physical Review referee guidance was not retrievable and carries no item here.

## Procedure

1. Read the registered plan before the result: the approved case, the approved record and its digest, and the
   preregistered decision rule. Write down the primary contrast, its arms, its null arm and its threshold before opening
   any analysis output.
2. Read the claim sentence of the document under review and list every number it rests on.
3. Walk items 1 to 12 below in order. Rerun every computation a reviewer can rerun from retained bytes; mark the rest
   `not run`.
4. Write the report in the format at the end and place it under `docs/archive/reviews/` when it is retained.

## Checklist

### 1. Preregistration and forking paths

Check that the primary outcome, the exclusion rules, the model and the decision threshold were fixed before the raw data
existed, and that the document labels every later analysis as post hoc.

- The criterion on every provider is that the plan's digest predates the raw bytes: the case file, the approved record
  and the analysis code are fixed at a named digest before the shots exist, and the headline number comes from that
  analysis. For IBM live runs the preregistered analysis is `collect.json` at the run's experiment digest, and a second
  analysis of the same raw files is `adjudicate.py` output named by its own analysis digest
  ([AGENTS.md, Records](../../AGENTS.md#records)); a reviewer confirms that the headline number comes from the first and
  that any figure from the second is labeled exploratory. For Quandela runs the plan is the case (`cases.json`,
  `circuit.json`) copied into the run directory, `plan` checks its digests before `submit`, and the analysis script
  retained beside `results.json` and `raw/result.json` is the analysis to compare
  ([Quandela notes, run directory](../notes/quandela/README.md)). Quantum Inspire runs follow the case manifest and the
  usage ledger named in [AGENTS.md](../../AGENTS.md#records).
- Fails when the decision rule appears only in the result document, when a threshold, a subset, a predictor or an
  exclusion changed after the raw bytes were read, or when the document does not say whether it did.
- Fails when an outcome in the registered plan is absent from the result without a stated reason: unreported registered
  outcomes are the audited failure of Munafo (PDF p. 4, 13 percent of registered trials reported their outcomes
  consistently; about 70 percent of audited reports omitted an outcome measure).
- Grounds: Munafo PDF p. 2-4 (pre-registration is blinding because the data do not exist; outcome switching; data-contingent
  choices of models, exclusion rules and covariates are P-hacking; confirmatory versus exploratory), Box 3 (post hoc
  analyses clearly labeled); Ioannidis PDF p. 3 Corollary 4 (flexibility in designs, outcomes and analytical modes raises
  bias) and Box 1.

### 2. Multiplicity

Check the denominator: count the contrasts, parameter values, meshes, subsets, predictors and thresholds probed, whether
or not each appears in the result.

- Fails when the document reports one significant contrast and does not state how many were examined, or when the
  claim's p-value is not adjusted for the stated count. The arithmetic is 1 - (1 - alpha)^k: at alpha = 0.05 and k = 15
  the chance of at least one P < 0.05 under the null is 0.54 (Munafo Box 6, PDF p. 6).
- Fails when several teams or sessions probed the same question and only the positive one is quoted: the probability
  that an isolated positive is true falls with the number of independent teams (Ioannidis PDF p. 2, Table 3).
- A correction for multiplicity needs the count; a reviewer cannot recover it from the report (Ioannidis PDF p. 6). The
  sources fix the need for a stated correction, and the choice of method belongs to the preregistered plan.
- Grounds: Munafo Box 6; Ioannidis PDF p. 2-3 (Corollary 3 and Corollary 6) and PDF p. 6.

### 3. Effect size versus significance

Check that the document gives the effect size with its unit beside every p-value and that a significant result is not
read as an important one.

- Fails when the claim cites a p-value without the effect, when significance is read as the probability that the
  hypothesis is true, or when a decision rests on crossing a threshold alone. A p-value indicates incompatibility with a
  specified model and measures neither effect size nor the probability of the hypothesis (ASA principles 1, 2, 3 and 5,
  PDF p. 2).
- Fails when an observed effect exceeds what the instrument can show: "too large and too highly significant effects may
  actually be more likely to be signs of large bias" (Ioannidis PDF p. 5). A hardware correlation above the simulated
  ceiling of the same circuit prompts the checks of items 6 and 8 before any celebration.
- Grounds: ASA PDF p. 2; Ioannidis PDF p. 5 and Corollary 2 (smaller effects, lower probability of truth).

### 4. Confidence bounds

Check that every headline estimate carries an interval, that the interval is the one the plan names, and that the
decision uses the bound.

- Fails when only a point estimate appears, when the interval belongs to a different quantity than the claim (an interval
  for one correlation under a claim about a difference), or when the interval's method is not stated. Estimation with
  confidence, credibility or prediction intervals supplements p-values (ASA PDF p. 2); a certification states a region
  and says whether it is heuristic, Bayesian (prior dependent) or rigorous (Eisert PDF p. 3).
- A claim "exceeds by at least delta" tests the interval bound against delta, not zero (cocor PDF p. 3, 5).
- Grounds: ASA PDF p. 2; Eisert PDF p. 3; cocor PDF p. 3, 5.

### 5. Dependent-correlation comparisons

Check that a claim comparing two correlations uses a direct test of their difference matched to the data layout.

- Fails when one correlation is significant, another is not, and the document concludes they differ: that is a
  statistical fallacy, and the difference needs its own test (cocor PDF p. 1-2).
- Classify the pair first. Two correlations computed over the same units that share one variable (response with
  predictor A and with predictor B) are dependent and overlapping and take Williams t, Steiger z or Meng z, each of which
  needs the correlation between the two predictors, r_kh. Two correlations over disjoint sets are independent and take
  Fisher z. Two over the same units with no shared variable are dependent and nonoverlapping (cocor PDF p. 2).
- Fails when the document omits r_kh, n, the test name or the formula. A reviewer reruns the test with the formulas of
  [cocor](../notes/papers/diedenhofen-musch-2015-cocor.md) and requires that Williams, Steiger and Meng agree in
  conclusion; the note's reproduction of the cocor example (Williams t = -2.7743, Steiger z = -2.7513, Meng z = -2.7432,
  Zou interval [-0.3689, -0.0630] for r_jk = 0.1038, r_jh = 0.3213, r_kh = 0.0257, n = 291) is the unit check for any
  implementation. A disagreement between tests is reported, because no test is uniformly preferable (cocor PDF p. 2).
- Fails when the test treats mesh-level or shot-level values that share a seed, a calibration or a layout as independent
  units; the effective n is the number of independent units.
- Grounds: cocor PDF p. 1-3, 8-9 and S1 Eq. 12 to 14, 19 to 26, 31 to 36.

### 6. Calibration drift and confounds

Check that the contrast arms see the same device state and that the design separates the effect from drift.

- Fails when arms were acquired in different calibration windows, backends, qubit sets or layouts without a measured
  bridge. Certification and tomography assume independent, identically distributed copies, and repeated acquisitions
  across a drifting device violate that (Eisert PDF p. 4; van Enk and Blume-Kohout, [note](../notes/papers/1302.0932.md)).
  A reviewer asks for a drift test before pooled data are used.
- Fails when a benchmark gate error stands in for the error that matters: single- and two-qubit randomized benchmarking
  is insensitive to crosstalk (Proctor PDF p. 3-4), real devices show coherent and stochastic errors, crosstalk and slow
  drifts (Proctor Box 1, PDF p. 2), and non-Markovian error corrupts benchmarks (Proctor PDF p. 4-5).
- Repository rules the reviewer checks: for IBM live runs calibration is fetched in the process that decides and submits
  and never read back from a file ([AGENTS.md, QPU time and calibration](../../AGENTS.md#qpu-time-and-calibration)); a
  probe of an algebraic property passes the mutation test, lists its +, -, -, + arms and decides against a null arm
  ([Hardware probes](../notes/algebra_circuit_rules.md#hardware-probes)); where the platform runs each circuit as its own
  job (Quantum Inspire), the executed order of arms is read from the provider's timestamps and the decision uses only
  contrasts whose executed order holds the design. A reviewer of another provider's result asks for the equivalent
  calibration snapshot and execution order that provider retains.
- Grounds: Eisert PDF p. 4; Proctor PDF p. 2-5; van Enk note; the repository rules above.

### 7. Provenance and replay

Check that a second person can regenerate every number from retained bytes.

- Fails when the run lacks raw shot-ordered results, the platform snapshot (for IBM, the Target or properties snapshot
  with `backend_version` and `processor_type`; for Quandela, `platform-before-submission.json` or the platform record in
  `submission.json`), the circuit and compile settings, the analysis code at a named digest, or the seeds with their
  source. A referee asks whether experiments can be reproduced from "source code, documentation, experimental data,
  experimental setup specifications" (Quantum question 5); disclosure of the whole design and all data is the
  precondition for evaluating results (Munafo Box 6, PDF p. 6) and transparency outranks trust (Munafo PDF p. 5).
- Repository checks: the record names the approved-record digest; every new seed cites its quantum random number draw
  and index ([AGENTS.md, Seeds](../../AGENTS.md#layout-and-gates)); the run is registered in
  [research_state.json](../state/research_state.json); denominators of executions come from the
  [evidence-closure procedure](evidence-closure.md). A reviewer reruns the analysis from the retained raw results (IBM:
  `raw/<job_id>/`; Quandela: `raw/result.json`) and compares the digest.
- Grounds: Quantum question 5; Munafo PDF p. 5-6, Boxes 5 and 6.

### 8. Simulation versus hardware boundary

Check that every statement says whether the number came from a device, a noise simulation, a mock or an ideal model.

- Fails when mock outcomes (`--native-dry-run` timing) enter a scientific analysis or a measured visualization
  ([AGENTS.md, Code style](../../AGENTS.md#layout-and-gates)), or when an ideal-simulation expectation is presented as a
  hardware measurement.
- Fails when agreement in a classically simulable regime is extended to a regime that is not: trust extends only if "no
  additional sources of errors arise when moving out of the strictly certifiable regime" (Eisert PDF p. 4), and the
  claim wording states that as an assumption.
- Fails when the circuit is classically easy to compile away: a benchmark that lets a classical compiler replace a circuit
  by a precomputed output can be gamed whenever the circuit is simulable (Proctor Box 3, PDF p. 7), and the verification
  of a large circuit rests on simulable proxies or noise assumptions (Proctor Box 4, PDF p. 8).
- Grounds: Eisert PDF p. 4; Proctor PDF p. 7-8; the repository rule on mock outcomes.

### 9. Error mitigation, compilation and post-processing

Check which mitigation, twirling, dynamical decoupling, postselection or filtering touched the number and that the
unprocessed counterpart is reported.

- Fails when results are shown only after mitigation: such results should be interpreted "with extreme caution" because
  the link between mitigated performance and progress is not established (Proctor PDF p. 7).
- Fails when postselection or exclusion changes the sample the claim describes without the survival fraction and the
  unselected result beside it (Munafo Box 6 on exclusions, PDF p. 6).
- Grounds: Proctor PDF p. 7; Munafo PDF p. 6.

### 10. Strength of the certified statement

Check which assumptions the evidence supports and that the claim does not sit in a stronger column of the assumption
table than the data allow.

- Fails when a statement needs trusted measurements, i.i.d. copies or a known noise model and the document supplies none
  of them. Eisert separates the device, the measurement apparatus and the classical processing, and ranks protocols by
  information gained, assumptions made and measurement, sample and post-processing complexity (Eisert PDF p. 2-3, Box 4
  and Table I, PDF p. 5, 7).
- Fails when a single scalar metric stands for performance (Proctor PDF p. 3, 11-12).
- Grounds: Eisert PDF p. 2-5; Proctor PDF p. 3, 11-12.

### 11. Claim wording

Check that the sentence claims what the retained evidence shows, no more.

- Fails when the wording uses "confirms", "demonstrates" or "proves" for an exploratory or underpowered result, omits
  the limits of the design, or states a mechanism the contrast did not isolate. A referee asks whether assumptions and
  limitations are clearly described (Quantum question 4) and whether conclusions are "appropriately evidence-bound"
  (Munafo Box 3, PDF p. 5).
- Fails when a benchmark-style figure is used to rank machines or methods without stating what it does not measure
  (Proctor PDF p. 4, 8).
- Fails when significance is called importance (ASA principle 5) or a p-value is called the probability of the
  hypothesis (ASA principle 2).
- Required elements of a claim sentence: the arm and null arm, the effect with its interval, the count of probed
  contrasts, the device and date of the calibration, the boundary of the regime tested, and the label confirmatory or
  exploratory.
- Grounds: Quantum question 4; Munafo Box 3; ASA PDF p. 2; Proctor PDF p. 4, 8.

### 12. Independence and conflicts

Check who designed, ran and analyzed the result and who reviews it.

- Fails when the reviewer helped to design the contrast, chose the threshold or wrote the analysis: nonfinancial
  commitment to one's own findings biases interpretation (Ioannidis PDF p. 3, Corollary 5), and independent methodologists
  with no stake mitigate it (Munafo Box 1, PDF p. 2, 4). The reviewer states any such tie in the report, the way a
  referee declares conflicts of interest (Quantum).
- A second session that shares the author's assumptions is not independent; the review names a check the author did not
  design.
- Grounds: Ioannidis PDF p. 3; Munafo PDF p. 2, 4; Quantum referee page.

## Report format

```text
Document reviewed: <path or PR>, head <commit>
Reviewer and ties to the design: <names, roles>
Registered plan read before the result: <paths, digests>
Primary contrast: <arms, null arm, threshold>
Items 1-12: <pass | fail | not run> <artifact path or failing value> (one line each)
Recomputed numbers: <each rerun, its inputs and its result against the document's value>
Not rerun: <what, why>
Decision: <accept | revise | reject>, with the findings that decide it ordered by consequence
```

A reviewer ranks findings by what they do to the claim: a failed item 1, 2, 5, 6 or 8 can remove the claim, a failed item
3, 4, 9 or 10 narrows it, and a failed item 7, 11 or 12 blocks acceptance until repaired. Where a source is silent, such
as the choice among multiplicity corrections, the report says the decision rests on the preregistered plan and cites it.
