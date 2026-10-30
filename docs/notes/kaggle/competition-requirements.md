# Kaggle competition requirements and deadlines

This note records, for ten Kaggle competitions, what each one requires of a
participant, when each deadline falls, and what its prizes and judging rules
say. The text comes from each competition's Overview, Rules, Evaluation,
Timeline, Prizes, Data and Code Requirements pages as the Kaggle MCP server
(`mcp__kaggle__list_competition_pages` and `mcp__kaggle__search_competitions`)
returned them on 2026-10-30. The live pages stay the authority, because
sponsors edit deadlines and prize text during a competition; reread the page
before acting on any date here. Every deadline is 11:59 PM UTC on the stated
day unless the row says otherwise.

The Kaggle MCP server exposes no tool that joins a competition. Entry means
accepting the competition rules on kaggle.com while signed in, and only the
account owner does that.

## Entry status and deadlines

`user_has_entered` in the search result gives the entry status of the
authenticated account.

| Competition | Entered | Last day to enter | Team merger cutoff | Final submission | Prize pool |
| --- | --- | --- | --- | --- | --- |
| [Playground Series S6E10, Predicting Airline Satisfaction](https://www.kaggle.com/competitions/playground-series-s6e10) | no | 2026-10-31 | 2026-10-31 | 2026-10-31 | Kaggle merchandise |
| [ARC Prize 2026, ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3) | no | 2026-10-26 (closed) | 2026-10-26 (closed) | 2026-11-02 | $850,000 |
| [ARC Prize 2026, ARC-AGI-2](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-2) | no | 2026-10-26 (closed) | 2026-10-26 (closed) | 2026-11-02 | $700,000 |
| [ARC Prize 2026, Paper Track](https://www.kaggle.com/competitions/arc-prize-2026-paper-track) | yes | 2026-11-09 | 2026-11-09 | 2026-11-09 | $75,000 plus a bonus of up to $375,000 |
| [Gemma 4 Developer Agent, Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper) | yes | 2026-11-12 | 2026-11-12 | 2026-11-12 | $35,000 |
| [Gemma 4 Developer Agent](https://www.kaggle.com/competitions/gemma-4-developer-agent) | yes | 2026-11-25 | 2026-11-25 | 2026-12-02 | $65,000 plus a $10,000 small-model bonus |
| [Enveda CASMI 2026, Molecule ID From Mass Spectra](https://www.kaggle.com/competitions/enveda-CASMI26-molecule-id-mass-spectra) | yes | 2026-12-07 | 2026-12-07 | 2026-12-14 | $50,000 |
| [Google Quantum AI, Verifiable Quantum Circuit Compilation](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation) | yes | 2027-01-13 | 2027-01-13 | 2027-01-20 | $150,000 |
| [NFL Big Data Bowl 2027](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027) | yes | 2027-01-06 | 2027-01-06 | 2027-01-06 | $100,000 |
| [Squares in Squares](https://www.kaggle.com/competitions/squares-in-squares) | yes | 2027-07-11 | 2027-07-11 | 2027-07-18 | $50,000 |

The ARC-AGI-3 and ARC-AGI-2 entry deadlines passed on 2026-10-26, so the
authenticated account cannot enter either one. The ARC Paper Track requires a
writeup that documents a submission to ARC-AGI-2 or ARC-AGI-3 and requires its
team to match the team that made that submission, so the account's Paper Track
entry yields a scoreable paper only if the account or a team it belongs to
already submitted to one of the two prediction competitions.

The last-day-to-enter and merger values for the Paper Tracks, the NFL
competition and Squares in Squares come from the `new_entrant_deadline` and
`merger_deadline` search fields, because those competitions' Timeline pages
state no entry deadline (the Squares in Squares Timeline page prints the
unrendered template tokens `${competition.ProhibitNewEntrantsExplicitDeadline}`
and `${competition.TeamMergerExplicitDeadline}` in their place).

## Entry audit

The search group `Entered` lists every competition the authenticated account
has joined; the audit ran on 2026-10-30 and returned seven. The `deadline`,
`new_entrant_deadline`, `team_count` and `max_daily_submissions` fields below
come from that listing.

| Entered competition | Teams | Daily submissions | Team size | Last day to enter | Final deadline | Action that remains |
| --- | --- | --- | --- | --- | --- | --- |
| ARC Prize 2026, Paper Track | 355 | 5 | 8 | 2026-11-09 | 2026-11-09 | Submit one writeup; it needs a prior ARC-AGI-2 or ARC-AGI-3 submission and a matching team. |
| Gemma 4 Developer Agent, Paper Track | 429 | 5 | 5 | 2026-11-12 | 2026-11-12 | Submit one research-paper writeup. |
| Gemma 4 Developer Agent | 4,210 | 1 | 5 | 2026-11-25 | 2026-12-02 | Submit `submission.zip` with `agent.yaml`; teams merge until 2026-11-25. |
| Enveda CASMI 2026 | 4,398 | 5 | 5 | 2026-12-07 | 2026-12-14 | Submit a notebook (a code competition); teams merge until 2026-12-07. |
| Google Quantum AI, Verifiable Quantum Circuit Compilation | 1,703 | 5 | 5 | 2027-01-13 | 2027-01-20 | Submit a zip of three circuit sets; the milestone prize closes 2026-11-20. |
| NFL Big Data Bowl 2027 | 446 | 5 | 5 | 2027-01-06 | 2027-01-06 | Submit one writeup. |
| Squares in Squares | 1,282 | 10 | 5 | 2027-07-11 | 2027-07-18 | Submit a CSV; the three-month cutoff is 2027-01-17. |

The account has not entered three of the competitions this note covers:
Playground Series S6E10 (open until 2026-10-31, the day its submissions also
close), and ARC-AGI-3 and ARC-AGI-2 (closed to new entrants on 2026-10-26).
Entering Playground S6E10 stays possible for one more day, and its final
submission deadline is the same day, so a late entry leaves no room for a
second attempt.

`search_competition_submissions` returned an empty result for each of the seven
entered competitions with the groups `All` and sorting by date. An empty result
reports no listed submission and does not distinguish a competition with no
submissions from a tool that cannot see them, so the submission counts stay
unverified; read the Submissions tab of each competition on kaggle.com.

The audit also found one competition outside the original list: the Google
Quantum AI Verifiable Quantum Circuit Compilation competition, which the
account has entered. Its section below records its rules. Its timeline holds
the nearest unmet milestone of the seven, the Mid-Competition Milestone Prize
cutoff on 2026-11-20.

Deadline order across the seven entered competitions: ARC Paper Track
(2026-11-09), Gemma 4 Developer Agent Paper Track (2026-11-12), Quantum AI
mid-competition milestone (2026-11-20), Gemma 4 Developer Agent entry cutoff
(2026-11-25) and final (2026-12-02), Enveda entry cutoff (2026-12-07) and final
(2026-12-14), Quantum AI longest-leader cutoff (2027-01-04), NFL Big Data Bowl
2027 (2027-01-06), Quantum AI entry cutoff (2027-01-13), Squares three-month
cutoff (2027-01-17), Quantum AI final (2027-01-20), and the Squares final
(2027-07-18).

## Rules common to every competition

Every competition except Squares in Squares carries the same General
Competition Rules; Squares in Squares restates them in its own numbering with
the differences listed in its section.

- Eligibility: a registered Kaggle account holder, at least 18 years old or
  the age of majority in the jurisdiction of residence, not a resident of
  Crimea, the so-called Donetsk or Luhansk People's Republics, Cuba, Iran or
  North Korea (the Playground rules also exclude Syria), and not a person or
  entity under U.S. export controls or sanctions. The NFL competition lets
  participants under 18 compete with parental consent and bars them from
  prizes.
- One Kaggle account per person. Submitting from a second account disqualifies
  the participant. Each team member registers individually before joining a
  team, joins only one team, and confirms membership through the team
  notification.
- A team merger needs a combined size within the maximum, a combined submission
  count within the per-day limit multiplied by the days elapsed, and completion
  before the merger deadline or the competition deadline.
- Private sharing of competition code or data outside a team is prohibited.
  Public sharing of code is allowed on the competition's forum or notebooks,
  under an Open Source Initiative approved license that permits commercial use.
  That license governs shared code only; the competition data stays under the
  data license in each section below (CC BY-NC 4.0 for Enveda and the NFL
  competition) and goes to no party outside the competition.
- Open-source components in a submission carry an Open Source Initiative
  approved license that does not limit commercial use, unless a competition's
  specific rules say otherwise.
- External data and models are allowed when publicly available at no cost to
  every participant or when they meet the Reasonableness Standard (a small
  subscription charge is reasonable; a dataset license costing more than a
  prize is not). Automated machine learning tools are allowed with a license
  that permits compliance.
- Submissions may not use hand labeling or human prediction of validation or
  test records (Hackathon-format competitions excepted where the page allows
  it).
- Winners deliver the training code, inference code and a description of the
  computational environment, grant the stated license, and return prize
  acceptance documents (eligibility certification, releases, IRS Form W-9 for
  U.S. residents or W-8BEN for foreign residents) within two weeks of
  notification. Prizes issue about 30 days after Kaggle or the sponsor receives
  the documents. A potential winner who does not answer within one week of the
  first notification loses the prize to the next ranked entrant.
- Taxes on prizes fall on the winner. A team prize splits evenly among members
  unless the team unanimously tells Kaggle a different split before payment.
- The sponsor and Kaggle may use the winner's name and likeness for promotion.
  The governing law is California law with Santa Clara County courts, except
  the NFL competition, which states New York governing law and Santa Clara
  County courts.
- Ties go to the earliest submission. A disqualified participant may lose
  leaderboard placement, points and medals.
- In the competitions that score a held-out test set (Playground S6E10,
  ARC-AGI-3, ARC-AGI-2, Gemma 4 Developer Agent, Enveda), final standing uses
  the private leaderboard over the private test set, and the public
  leaderboard covers a sample of the test data. The Paper Tracks and the NFL
  competition judge writeups against a rubric, Squares in Squares scores the
  submitted placements directly, and the Quantum AI competition scores
  circuits against a verifier seeded from each submission's hash, so none of
  those has a hidden test set.

## Playground Series S6E10, Predicting Airline Satisfaction

Sponsor: Google LLC (hosted by Kaggle). Category: Playground. Format: tabular
prediction competition with a public and a private leaderboard.

| Item | Requirement |
| --- | --- |
| Task | Predict the probability of the binary `satisfaction` variable for each test row. |
| Metric | Area under the ROC curve between predicted probability and the observed target. |
| Submission file | CSV with header `id,satisfaction`; one probability per test `id` (the example ids start at 699635). |
| Files | `train.csv` (target `satisfaction`), `test.csv`, `sample_submission.csv`. |
| Data origin | Synthetic data inspired by the Airline Satisfaction dataset (`arseniyshutko/binary-aviation-satisfaction-129k`); feature distributions are close to, not equal to, the original. |
| Daily submissions | 10 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 3 at most. |
| Start | 2026-10-01. |
| Entry, team merger and final submission deadline | 2026-10-31, all on the same day. |
| Prizes | First, second and third place each choose Kaggle merchandise. Merchandise is awarded once per person across the Playground series; a previous winner is skipped. |
| Winner license | None. |
| Data license | CC BY 4.0, commercial use allowed. |
| External data | Allowed under the common Reasonableness Standard. |
| Winner obligations | Code and documentation delivery per Kaggle's winning-model documentation guidelines. |

## ARC Prize 2026, ARC-AGI-3

Sponsor: ARC Prize Foundation. Category: Featured, code competition, awards
Kaggle points. Format: an agent plays hidden interactive games; Kaggle reruns
the submitted notebook against a private game set.

| Item | Requirement |
| --- | --- |
| Task | Build an agent that explores novel interactive environments, learns the game's rules from play and completes levels with few actions. |
| Observation | A JSON frame with a grid of at most 64 by 64 cells, cell values 0 through 15, origin at the top left, plus metadata. |
| Actions | `RESET`, `ACTION1` through `ACTION5` (simple), `ACTION6` (needs `(x, y)` coordinates) and `ACTION7`; each game defines which actions exist and what they do. |
| Game states | `NOT_FINISHED`, `WIN`, `GAME_OVER`. |
| Evaluation set | A private set of 110 games; half set the public leaderboard score and half set the private score. 25 public games ship in `environment_files/`. |
| Score | Per level: `min(human_actions / agent_actions, 1.0)` squared, where the human baseline is first-time testers. Per game: average of level scores weighted by 1-indexed level number. Total: mean over games, expressed as 0 to 100 percent. |
| Submission file | Generated automatically once the agent acts on any game. |
| Toolkit | `arc-agi` Python package; `ARC-AGI-3-Agents` repository (agents implement `is_done(frames, latest_frame)` and `choose_action(frames, latest_frame)`; a Swarm runs agent instances across games in parallel). Documentation at `docs.arcprize.org`. |
| Code requirements | Submit through a notebook; CPU or GPU notebook at most 9 hours; internet disabled; free public external data and pretrained models allowed. |
| Accelerators | RTX 6000 machines (machine type `g4-standard-48`) exist for notebooks attached to this competition only, internet disabled; other use risks site suspension or an account ban. |
| Daily submissions | 1 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 8 at most. |
| Start | 2026-03-25. |
| Entry and team merger deadline | 2026-10-26 (passed). |
| Final submission deadline | 2026-11-02. |
| Winners announced | 2026-12-04. |

Prizes (total $850,000):

| Prize | Amounts |
| --- | --- |
| Final leaderboard (top score track) | first $40,000, second $15,000, third $10,000, fourth $5,000, fifth $5,000 |
| Milestone cutoff 2026-06-30 (past) | first $25,000, second $7,500, third $5,000 |
| Milestone cutoff 2026-09-30 (past) | first $25,000, second $7,500, third $5,000 |
| Bonus unlocked by a team scoring 100 percent | first $350,000, second $175,000, third $70,000, fourth $70,000, fifth $35,000, split among the top five teams at 100 percent |

Milestone prizes required a public notebook under an open source license by the
cutoff date. Winner obligations: license the winning submission and its source
under CC BY 4.0; deliver an open source system, open source model and open
source weights as the Open Source Initiative's Open Source AI Definition
checklist defines them; interview with the sponsor and work with the host's
technical writer. A prize-eligible participant who does not open source the
solution is removed from the competition. Data license: Apache 2.0.

## ARC Prize 2026, ARC-AGI-2

Sponsor: ARC Prize Foundation. Category: Featured, code competition, awards
Kaggle points. Format: static grid puzzles solved by a notebook rerun against
hidden tasks.

| Item | Requirement |
| --- | --- |
| Task | Produce the output grid for each test input of an abstract reasoning task, with two attempts per test input. |
| Grid format | Rectangular matrix of integers 0 through 9; smallest 1 by 1, largest 30 by 30. |
| Task files | `arc-agi_training-challenges.json` and `-solutions.json`; `arc-agi_evaluation-challenges.json` and `-solutions.json`; `arc-agi_test-challenges.json` (placeholder built from the evaluation tasks until rerun); `sample_submission.json`. |
| Task structure | Each task has `train` (typically 3 input and output pairs) and `test` (the inputs to solve). |
| Rerun set | 240 unseen tasks; most have one test input and a few have two. |
| Score | Share of test outputs for which either of the two attempts matches the ground truth exactly. |
| Submission file | `submission.json`: every task id present; per task a list with one dictionary per test input, in test-input order, each carrying `attempt_1` and `attempt_2` grids (both keys required even when only one guess exists). |
| Code requirements | Notebook submission; CPU or GPU notebook at most 12 hours; internet disabled; free public external data and pretrained models allowed; runtimes are obfuscated, so repeating a submission shows up to 10 minutes of variance before the score returns. |
| Accelerators | L4 by 4 machines (96 GB of GPU memory) for notebooks attached to this competition only, internet disabled; they consume GPU quota at twice the T4 by 2 and P100 rate. |
| Daily submissions | 1 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 5 at most. |
| Start | 2026-03-25. |
| Entry and team merger deadline | 2026-10-26 (passed). |
| Final submission deadline | 2026-11-02. |
| Winners announced | 2026-12-04. |

Prizes (total $700,000):

| Prize | Amounts |
| --- | --- |
| Progress prizes ($275,000) | first $75,000, second $50,000, third $40,000, fourth $35,000, fifth $25,000, sixth $20,000, seventh $15,000, eighth $15,000 |
| Innovation prize ($275,000) | the highest scoring Solution Writeup; all artifacts open sourced and attached to an official competition Solution Writeup within seven days of the submission deadline |
| Bonus ($150,000) | unlocked when a team reaches at least 85 percent; first $75,000, second $25,000, third $20,000, fourth $20,000, fifth $10,000, divided proportionately when fewer than five teams qualify |

The Innovation prize rubric scores six criteria from 0 to 5 and averages them:
accuracy on the leaderboard, universality beyond the competition, progress
toward anyone reaching 85 percent on ARC-AGI-2, theory (why the submission
works), completeness, and novelty against existing public research. The Rules
page calls this the Innovation Prize and the Prizes page calls it the Grand
Prize; both give $275,000. Winner obligations match ARC-AGI-3 (CC BY 4.0 license
for the winning submission, Open Source AI Definition checklist for system,
model and weights, sponsor interview with a technical writer). Data license:
Apache 2.0.

## ARC Prize 2026, Paper Track

Sponsor: ARC Prize Foundation. Format: Hackathon, one writeup per team, judged
by rubric; no leaderboard and no competition data.

| Item | Requirement |
| --- | --- |
| Task | Document the solution submitted to ARC-AGI-2 or ARC-AGI-3 in a Kaggle Writeup. |
| Team rule | The team must match the team that submitted to ARC-AGI-2 or ARC-AGI-3. |
| Writeup | Title, subtitle and analysis of at most 1,500 words (longer submissions may be penalized); a track selected in the Writeup form. |
| Required attachments | A cover image in the Media Gallery; a public Kaggle Notebook in the Project Links field. The submission ID of the matching prediction-competition entry is requested to tie the notebook to its leaderboard score. |
| Optional attachment | A public PDF of the paper through the Public Project Link field. |
| Visibility | A private Kaggle resource attached to a public Writeup becomes public after the deadline. |
| Submission mechanics | Press Submit on the saved Writeup; a draft or unsubmitted Writeup is not judged. |
| Submissions | 1 per team (5 per day is the platform value; the Hackathon rule overrides it). |
| Team size | 8 at most. |
| Start | 2026-03-25. |
| Final submission deadline | 2026-11-09. |

Judging scores six criteria from 0 to 5 and averages them: accuracy (leaderboard
performance), universality, progress (increase in anyone's chance of a top ARC
Prize score), theory, completeness, and novelty. The three highest averages win.
The rubric evaluation is not shared with entrants.

Prizes: first $50,000, second $20,000, third $5,000 ($75,000 in total). A paper
that averages above 4.5 out of 5 qualifies for a bonus; the rules cap the bonus
pool at $375,000 and divide it equally among all papers above 4.5. The winning
paper's license is CC BY 4.0. No data is provided.

## Gemma 4 Developer Agent, Paper Track

Sponsor: Google LLC (Google DeepMind). Format: research paper writeup; joining
the main Gemma 4 Developer Agent competition is optional.

| Item | Requirement |
| --- | --- |
| Task | Submit original, unpublished research that advances agentic software engineering. |
| Topics | Tuning and optimization (parameter-efficient fine-tuning and reinforcement learning for software engineering agents); code comprehension (code-graph generation, parsing, embedding); tasks and benchmarks (new tasks, datasets and resources for code structure and graphs); graph reasoning (language model reasoning over large graphs). |
| Writeup contents | Title and subtitle, abstract, introduction, description of the research with methods and experiments, related work and citations. |
| Length | At most 3,000 words. |
| Optional attachments | A public notebook in Project Links; a public arXiv-ready PDF (LaTeX or Word) through the Public Project Link field. |
| Archival status | Non-archival: submission does not prevent submission to other venues. |
| Submission mechanics | Press Submit on the saved Writeup before the deadline; drafts are not judged. A private Kaggle resource attached to a public Writeup becomes public after the deadline. |
| Daily submissions | 5 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 5 at most. |
| Start | 2026-09-22 (the page text) or 2026-09-23 (the platform's enabled date). |
| Final submission deadline | 2026-11-12. |

Judging scores five criteria from 0 to 5 and averages them: novelty, quality
(generality of the approach), relevance to software engineering and agentic
learning, verifiability, and clarity. Prizes total $35,000: overall best paper
$15,000, best new resource $10,000, best new application $10,000. Winning
papers appear at a Google-hosted event such as a NeurIPS expo workshop. License:
Apache 2.0, which the winner grants under an Open Source Initiative approved
license.

## Gemma 4 Developer Agent

Sponsor: Google LLC (Google DeepMind). Category: Featured, awards Kaggle
points. Format: submit a zip archive that configures an agent; Kaggle compiles
it into a Google Agent Development Kit (ADK) agent and runs it against hidden
software engineering tasks inside a sandbox.

| Item | Requirement |
| --- | --- |
| Task | Post-train and configure an agent on a Gemma 4 model that navigates a Python repository and drafts a patch that fixes a real bug or adds a requested feature. |
| Submission artifact | `submission.zip` with `agent.yaml` at the archive root. Optional contents: `configs/sampling.yaml`, `prompts/*.md` (loaded through `!include`), `sub_agents/*.yaml`, `adapters/<name>/` (PEFT LoRA directories holding `adapter_config.json` and `adapter_model.safetensors`), and `skills/<name>/` (a `SKILL.md` manifest with `name:` frontmatter, plus `scripts/` and `resources/`). |
| Config language | Google ADK Agent Config with restrictions that keep code execution inside the sandbox. `!include` paths resolve relative to the including file; path traversal outside the submission root, including through symlinks, is refused. |
| Models | Exactly one base model for every agent and subagent in a submission, chosen from `gemma-4-31b-it-qat-w4a16-ct`, `gemma-4-12b-it-qat-w4a16-ct`, `gemma-4-e4b-it-qat-w4a16-ct`, `gemma-4-e2b-it-qat-w4a16-ct`. |
| Adapters | Optional LoRA adapters; different agents may use different adapters through `adapter: <name>` on an `LlmAgent`. |
| Tools the harness allows | `run_command`, `submit_patch`, `get_status`, `read_file`, `edit_file`, `write_file`, `get_code_neighbors`, `search_similar_code`, `get_code_subgraph`, `run_skill_script`, `load_skill_resource`, and custom subagents defined through `agent_tool`. |
| Score | Percentage of tasks whose submitted patch passes the task's validation tests (PASS or FAIL per issue, as in SWE-bench). |
| Time limit | 12 hours to produce patches for all tasks, counting sandbox setup and excluding patch validation; per-task limits are optional through `eval_config.yaml`. |
| Public development data | 129 tasks in `tasks.jsonl` from `fastapi/fastapi`, `Textualize/rich`, `psf/requests` and `encode/httpx`; `snapshots/` (a Git tree per task at `base_commit`, history after it removed); `graphs/` (NetworkX call and dependency graphs, 256 files); `embeddings/` (256-dimension float32 vectors per graph node, 256 files); `wheels/` (124 offline Python wheels mounted read-only at `/wheels/`); `docker/` (sandbox Dockerfiles for Python 3.13 and compatibility shims for the removed `imp` and `telnetlib` modules); `sandbox/setup.py`; `sample_submission/`; `HARNESS_README.md`. |
| Hidden test set | About 120 tasks from private repositories, divided evenly between the public and private leaderboard splits; each task's reference fix passes its tests and a frontier model passes it or comes within one test case. |
| Output file | `/kaggle/working/submission.parquet` with columns `id` and `prediction` (a unified `git diff`, or `NO_PATCH`). |
| Accelerators | L4 by 4 machines (96 GB of GPU memory) for notebooks attached to this competition only, internet disabled, GPU quota consumed at twice the T4 by 2 and P100 rate. |
| Daily submissions | 1 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 5 at most. |
| Start | 2026-09-23. |
| Optional paper deadline | 2026-11-12 (the Paper Track above). |
| Entry and team merger deadline | 2026-11-25. |
| Final submission deadline | 2026-12-02. |

Prizes: first $37,000, second $18,000, third $10,000 ($65,000 for the
competition itself). A bonus of $10,000 goes to the highest ranking submission
whose base model is Gemma E2B or Gemma E4B; that submission must be one of the
team's two selected finals, LoRA fine-tuning is allowed, a daily notebook
publishes the filtered standings, and the same submission deadline applies. The
Prizes page totals $110,000 by adding the $35,000 Paper Track pool and the
$10,000 bonus. Top submissions appear at a Google-hosted event such as a
NeurIPS expo workshop. The Prizes page states "Submissions must be made by
November 12, 2026"; that sentence sits in the paper and event paragraph, and
the Timeline page lists 2026-11-12 as the optional research-paper deadline and
2026-12-02 as the final submission deadline, so reread the live Timeline before
treating 2026-11-12 as binding for the agent submission. Winner license: Apache
2.0; the winner delivers training code, inference code and a description of the
computational environment. Data license: Apache 2.0, commercial use allowed.

## Enveda CASMI 2026, Molecule ID From Mass Spectra

Sponsor: Enveda Therapeutics, Inc. Category: Featured, code competition,
awards Kaggle points.

| Item | Requirement |
| --- | --- |
| Task | For each molecule, rank up to 25 candidate 2D structures as SMILES from the molecule's tandem mass spectrometry (MS/MS) spectra. Prediction happens per `molecule_id`, so evidence from all of a molecule's spectra goes into one ranked list. |
| Chemistry scope | Natural-product-like molecules: confirmed and hypothesized natural products, natural-product analogs, and synthetic molecules that plausibly occur in nature. |
| Metric | Mean reciprocal rank at 25: the mean over molecules of one divided by the rank of the first correct structure, zero when none of the 25 is correct. |
| Match rule | A SMILES is correct when its InChIKey first block (InChIKey14, atom connectivity) equals the answer's after both pass RDKit tautomer canonicalization (RDKit pinned at 2026.03.3). Stereochemistry and tautomer form do not affect the score. |
| Submission file | CSV `molecule_id,smiles`; one row per `molecule_id`; the `smiles` field holds up to 25 SMILES joined by semicolons, best first. The platform rejects a file with a missing column, an empty file, a null in either column, a repeated `molecule_id`, or more than 25 guesses for one molecule. |
| Code requirements | Notebook submission; CPU or GPU notebook at most 9 hours; internet disabled; free public external data and pretrained models allowed; output file named `submission.csv`. |
| Training data | `train.parquet`: about 2.5 million spectra over about 275,000 structures, with the structure given (`normalized_smiles`, `inchikey`, `inchikey14`, `molecular_formula`, `ingest_lib`, `adduct_orig`, `precursor_error_ppm`, `num_peaks`). |
| Test data | `test.parquet`: about 1,500 spectra of about 400 molecules (one to 16 spectra per molecule, median 3), all acquired on a Bruker timsTOF, monoisotopic masses 157 to 1,159 Da (median 348). The visible file holds training examples and the hidden test file replaces it at rerun. |
| Novelty classes in the test set | Class one: structure has public reference spectra. Class two: structure is in PubChem or COCONUT but has no public spectra. Class three: structure is absent from PubChem and needs de novo prediction. The class mix and each molecule's class stay hidden. |
| Test cleaning | Spectra whose precursor mass disagrees with the structure and adduct were dropped; spectra with a base peak below 1,000 raw counts were dropped; peaks above precursor plus 2 Da were removed. |
| Collision energy | Use `collision_energy_ev`, the converted column designed to line up with the test file; `collision_energy_orig` and `collision_energy_orig_units` keep the source's value and unit. |
| Daily submissions | 5 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 5 at most. |
| Start | 2026-09-14. |
| Entry and team merger deadline | 2026-12-07. |
| Final submission deadline | 2026-12-14. |

The Data page's library table lists eleven training sources: `enveda-180`
(1,153,785 spectra, same timsTOF, synthetic drug-like compounds),
`pluskal_ms2` (527,581), `riken` (347,171), `gnps` (220,849), `massbank`
(101,727), `mona` (92,416), `spectraverse` (50,933), `msdial` (40,765),
`drug_plus` (2,545), `enveda-np-examples` (1,151 spectra of 250 common natural
products, acquired and processed like the test set) and `masaryk` (652). The
page lists curation options (relative-intensity floor, precursor cutoff,
minimum and maximum peak counts, deisotoping, intensity transforms) and
resources (MIST-CF, SIRIUS, matchms, GNPS suspect annotations excluded from the
training file, MassIVE, GeMS, DreaMS, FragHub).

Prizes: first $16,000, second $12,000, third $9,000, fourth $7,000, fifth
$6,000. Winner license: MIT, granted under an Open Source Initiative approved
license. Data license: CC BY-NC 4.0, so participation uses the data for
non-commercial purposes only.

Two inconsistencies sit in the competition's own pages: the search metadata
names the metric "CASMI: Mean Average Precision" while the Evaluation page
defines mean reciprocal rank at 25, and the Data page says test spectra use
"one of ten adducts" (and lists ten) while the column table says "one of the
seven above". Treat the Evaluation page as the scoring authority and reread
both pages before relying on the metric name or the adduct count.

## NFL Big Data Bowl 2027

Sponsor: National Football League. Format: Hackathon; one writeup per team,
judged by a panel; no leaderboard.

| Item | Requirement |
| --- | --- |
| Theme | Combine to NFL performance: link player movement in NFL Scouting Combine drills to regular-season NFL performance. |
| Task | A writeup that produces an actionable, accessible analysis (a new metric or a comparison of movement traits) for coaches, scouts or front offices. Narrow scope (one movement aspect, one position group, one drill) is encouraged. |
| Pass or fail requirements | The writeup links Combine sensor tracking data to regular-season NFL game performance; the writeup has readable markdown, embedded visuals and an attached public Kaggle Notebook. A writeup that does not use the player tracking data is not scored. |
| Length | At most 2,000 words and fewer than 10 tables or figures; longer submissions may be penalized. Most code belongs in an appendix or the linked notebook. |
| Submissions | 1 per team (the Hackathon rule overrides the platform's 5 per day). |
| Team size | 5 at most. |
| Under-18 participants | Allowed with parental or guardian consent; ineligible for prizes. |
| Start | 2026-10-06. |
| Final submission deadline | 2027-01-06. |
| Judging period | 2027-01-07 through 2027-01-25 (subject to change with the number of submissions). |
| Results announced | 2027-01-26 (anticipated). |

Judging scores four components from 0 to 10, weighted: football score 30
percent (week-to-week usefulness to teams, handling of football's data
complexity, uniqueness), data science score 30 percent (correctness, claims
backed by data, appropriate models, innovation), writeup score 20 percent
(clarity and defined motivation) and data visualization score 20 percent
(accessible, accurate, innovative charts and tables). Judges are analytics
staff of the 32 NFL teams or player tracking vendors that work with NFL teams.

Data: nine CSV files, about 2.2 GiB, covering 510 rookies from the 2023, 2024
and 2025 drafts and signings, with the schemas the Data page lists.

| File | Content |
| --- | --- |
| `players.csv` | identity, position, college, draft year, round and pick for 510 players |
| `combine_results.csv` | measurements, drill times, bench reps and Next Gen Stats grades |
| `combine_tracking.csv` | 10 Hz tracking over 6,310 Combine drill attempts (40-yard dash, 3-cone, short shuttle, position drills) |
| `player_career_successes.csv` | career snaps, games, All-Pro and Pro Bowl counts |
| `player_play.csv` | 316,338 player-play records with Next Gen Stats and play-by-play metrics |
| `games.csv` | 1,002 regular-season and playoff games from 2023 through 2025 |
| `game_tracking_2023.csv`, `game_tracking_2024.csv`, `game_tracking_2025.csv` | 10 Hz in-game tracking of the cohort |

Prizes (total $100,000): the Open Track pays three finalists $10,000 each and
three runners-up $5,000 each ($45,000); the University Track pays the same
($45,000); each finalist is invited to present at the 2027 NFL Scouting
Combine, where one team wins an additional $10,000 Grand Prize. Entries do not
go to the Grand Prize directly. The retrieved pages do not say how a team
selects the Open or University track, because the `tracks-and-awards` page
holds placeholder text; read the Writeup form on kaggle.com for that field.
Winner license: Open Source under an Open Source Initiative approved license.
Data license: CC BY-NC 4.0, so the data serves non-commercial purposes only.

## Squares in Squares

Sponsor: Google LLC. Category: Playground with a $50,000 prize pool. Format:
submit a CSV of square placements; a metric notebook scores it.

| Item | Requirement |
| --- | --- |
| Task | For each puzzle `n` from 1 to 1,000, place `n` unit squares with continuous center coordinates and rotation angle so that no two squares overlap (interior intersection exactly zero) and the axis-aligned container square is as small as possible. |
| Score | Per puzzle `L / sqrt(n) - 1`, where `L` is the container side length computed from the submitted squares; the leaderboard value is the sum over puzzles, and lower is better. |
| Partial submissions | Allowed. A missing puzzle scores `L0 / sqrt(n) - 1`, the trivial grid packing's value. A puzzle whose coordinates do not parse is charged the grid ceiling. |
| Submission file | CSV `id,n,square_id,x,y,angle`: `id` runs from 0 to the row count minus one, `n` names the puzzle (1 to 1,000), `square_id` indexes the square within the puzzle (0 to `n - 1`), `x` and `y` give the center, `angle` is in radians. Coordinates are plain decimal literals, scientific notation allowed. |
| Files | `sample_submission.csv` only; no competition data. |
| Metric implementation | The `metric/squares-in-squares` notebook on Kaggle. |
| Daily submissions | 10 per day. |
| Final submissions | 1 selected for judging. |
| Team size | 5 at most. |
| Start | 2026-10-21. |
| Three-month leaderboard cutoff | 2027-01-17. |
| Six-month leaderboard cutoff | 2027-04-18. |
| Entry and team merger deadline | 2027-07-11. |
| Final submission deadline | 2027-07-18. |

Prizes: final leaderboard first $12,000, second $10,000, third $8,000, fourth
$5,000, fifth $5,000; the top leaderboard score at the three-month cutoff earns
$5,000 and at the six-month cutoff earns $5,000 (ties go to the earliest
qualifying submission). Winner license: the winner licenses the submission and
source code under CC BY 4.0 or Apache 2.0. Data license: CC0 public domain, with
no competition data provided.

The Squares in Squares rules differ from the common set in three places: the
publicity clause grants Kaggle and the sponsor an unrestricted, sublicensable,
perpetual, worldwide license to the participant's name, voice, image and
likeness in recordings; the commercial software exception covers software the
sponsor can procure for no more than a prize amount; and the Final Submission
selection allows one submission.

## Google Quantum AI, Verifiable Quantum Circuit Compilation

Sponsor: Google LLC. Category: Featured with a $150,000 prize pool, awarding
points and medals. Format: submit a zip archive of kickmix circuits that a
verifier simulates and a metric notebook scores. The task needs no quantum
hardware and no training data; the competition's own framing is a closed loop of
AI coding agents, classical optimization and a verifier.

| Item | Requirement |
| --- | --- |
| Task | Shrink three fault-tolerant subroutines written as kickmix circuits (reversible classical gates, diagonal phase gates and measurement-based uncomputation), which the open-source kickmix library in Qualtran fuzz-tests on classical inputs. |
| Task `invsqrt` (fusion energy) | Map `|x>|0>` to `exp(2 pi i / sqrt(x)) |x>|0>` for every `x` from 1 to 3,133,452 in a 22-qubit register `x`; 64 tests per input; every phase within `2^-24 / sqrt(x)` turns. Cost is qubits times Toffoli-equivalents (Toffolis plus T gates divided by 4). |
| Task `dqi` (combinatorial optimization) | A reversible decoder for the Reed-Solomon code RS(4095, 4025) over GF(2^12), with syndromes in registers `S0` to `S69` and a classical record in `E0` to `E4094`; 102,400 test shots, failures allowed. Cost is `R(eps_plus) * Q^2 * T` with a repetition factor that grows with the failure rate. |
| Task `dfthcsos` (quantum chemistry) | Circuits that load the Givens-rotation angles of a factorized FeMoCo Hamiltonian plus `submission.npz` holding the factorization and the Givens tree. A circuit wider than 128 qubits, an encoded Hamiltonian more than 20 mHa from the reference, a normalization above 49.0 or a gap at or below 3.914898 Ha rejects the submission. |
| Score | The geometric mean over the three tasks of the baseline cost divided by the submission cost; the reference submission scores 1.0 and higher is better. |
| Submission file | A zip containing `invsqrt.kmb` or `.kmx`, `dqi.kmb` or `.kmx`, and a folder `dfthcsos` with `angle_k_0` to `angle_k_<n-1>` (numbered without gaps, each `.kmb` or `.kmx`) plus `submission.npz` (`U`, `W`, `H2_I`, `H1_I`, `Hsym_lower`, `tree_edges`). |
| Scoring time | About 45 minutes per submission. |
| Files | `verifiable_circuit_compilation.pdf` (the paper, arXiv 2610.23832), `sample_submission/`, `verifiers/` (each task's verifier and reference-circuit script), `kickmix/` (the simulator `kickmix.so` for the Kaggle notebook image). A separate starter-kit dataset builds a complete `dfthcsos` submission. |
| Metric implementation | The `metric/google-quantum-ai-metric` notebook on Kaggle. |
| Daily submissions | 5 per day. |
| Final submissions | 2 selected for judging. |
| Team size | 5 at most; mergers allowed while the combined submission count stays within days run times 5. |
| Start | 2026-10-22. |
| Mid-Competition Milestone Prize cutoff | 2026-11-20. |
| Longest Leader Prize period ends | 2027-01-04. |
| Entry and team merger deadline | 2027-01-13. |
| Final submission deadline | 2027-01-20. |

Verification seeds each test from a hash of the submission plus a secret salt,
so any change to a circuit draws fresh tests and no hidden test set exists.

Prizes: leaderboard first $50,000, second $25,000, third $10,000, fourth,
fifth and sixth $5,000 each; additional prizes total $50,000. The Mid-Competition
Milestone Prize ($10,000) goes to the highest public leaderboard score at the
2026-11-20 cutoff and needs a public notebook kept public until the final
deadline. The Longest Leader Prize ($10,000) goes to the team whose notebooks
hold the best leaderboard score for the longest time between the start and
2027-01-04, with the notebooks and datasets public by that date. The three
Single Task Performance Prizes pay $10,000 each for the best selected score on
`invsqrt`, `dqi` and `dfthcsos`. Winner license: Apache 2.0 for the submission
and its source code, with an exception for input data or pretrained models under
an incompatible license. Data license: Apache 2.0, and the data may serve
commercial and non-commercial use. A winner delivers training and inference
code, a description of the computational environment, and signed prize
documents with U.S. tax forms.

The Data page states that the kickmix library is to move to PyPI and leave the
competition dataset, and that the metric will then read the PyPI copy; recheck
the Data page for the library source before pinning a version.

## Not read

The Kaggle MCP reads below this level were out of scope for this note: the
competition forums and discussion topics, the public leaderboards, the full
data file listings (the per-competition file lists above come from each Data
page), the winning-model documentation guidelines, the Code Competition FAQ and
the Gemma `HARNESS_README.md` (its content ships inside the Gemma dataset and
needs a download after the account joins the competition).
