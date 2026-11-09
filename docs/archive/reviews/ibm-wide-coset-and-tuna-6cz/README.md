# Review of the wide-coset and Tuna-17 six-CZ claims

The claims `hw-ibm-pathion-wide-coset` and `hw-tuna17-pathion-six-cz-null-blocks` in `docs/state/research_state.json`
register the IBM Heron r2 whole-operand nullity runs at D = 64 and 128, and the Tuna-17 six-CZ null blocks. They also
add the 64D and 128D implications to `docs/evidence/pathion-kernel-map/README.md`.

| file | content |
|---|---|
| [brief.md](brief.md) | the review brief |
| [literature-drift-systematics.md](literature-drift-systematics.md) | documents-repository sources on drift, readout and defects; each entry is tagged source-opened at the cited page, note-only, or held and unopened, and the five tier-one sources were opened page by page with their manifest sha256 recomputed |
| [analysis-claude.md](analysis-claude.md) | the setting-by-setting comparison with the parallel-coset pair and the ibm_fez qubit-90 calibration finding |
| [review-codex.md](review-codex.md) | the `codex` (gpt-daybreak-blue-latest, high effort) review of the claims branch |
| [brief-round2.md](brief-round2.md) | the brief of the second review, of the write-up itself |
| [review-codex-round2.md](review-codex-round2.md) | the second `codex` review (same model and effort), of the analysis, the literature report and this reconciliation |

The Nemotron review did not run. NVIDIA's endpoint reported the model DEGRADED, and OpenRouter's free tier answered 429
for its daily limit on 2026-11-09.

## Reconciliation

| review finding | verdict | evidence and resolution |
|---|---|---|
| Every number in both claims equals its record | survives | Codex summed the Tuna `cases.json` files (19 batches, 56 jobs, 2,293,760 shots) and matched every value to the analysis JSONs. The eight claim-pinned sha256 values match the current bytes |
| Rule counts: kingston 23/23 plus 6/6, fez exactly eight failures | survives | `scripts/pathion_wide_coset_analysis.py` regenerated the retained analysis byte for byte (`cmp` 0) |
| The fez difference failures restate the null failures | survives, bounded | 28.602326 = 28.071373 + 0.530953 and 61.033916 = 59.977929 + 1.055987. The restatement needs the case-specific premise that the targets pass; the claim's boundary states it |
| Tuna-17 decides only `unresolved_batch` | survives | the replicate gate (34.86 against 10.83) precedes every mechanism class in `scripts/qi_pathion_one_cz_null_cases.py` |
| 64D/128D evidence classes | survives | the censuses are computed; the recurrence n -> 2n + 4 has a paper proof that `proofs/CdHalfFold.v` labels open; half-fold doubling is proved (`Qed`). "No A_5 stratum" holds, but "no A_5 circuit" would not: fez runs one D = 32 reference block of a null operand |
| Tuna regeneration is not byte-stable | survives, nonblocking | 186 floating-point differences, at most 1.78e-14 absolute, change no displayed value or decision. Follow-up task: a deterministic serializer as a versioned successor of the pinned analysis producer |
| ibm_fez qubit 90: an execution-time readout channel (`prob_meas0_prep1` 0.835) that its own raw marginal (0.919) contradicts entered the correction (analysis-claude.md) | refuted in the second review | the 0.919 marginal is `pub_02` bit 3, which qubit 89 writes in the routed circuit; qubit 90 writes bit 1 there (P(1) 0.083), and all twelve mapped qubit-90 marginals (0.048 to 0.119) lie inside the 0 to 0.165 its channel admits. The channel stays extreme and unfalsified; the collector gate it motivated is withdrawn |

## Second review

| review finding | verdict | evidence and resolution |
|---|---|---|
| FATAL: the 0.919 marginal belongs to qubit 89, not qubit 90 | survives | `isa.qpy` maps qubit 90 to `g0_r2_c[1]` and qubit 89 to `g0_r2_c[3]` in `pub_02`; the raw `pub_02.json` gives P(1) 0.0831 and 0.9191 on those bits, and a per-PUB writer join over all twelve PUBs reproduces the review's qubit-90 marginals 0.048 to 0.119 (recomputed). analysis-claude.md and check 4 of the literature report now state the channel as extreme and unfalsified; the reconciliation row above is marked refuted |
| SERIOUS: Klimov's law is sigma(t) = 2 D t^(1/2), and a stochastic scale is no bound | survives | PDF p. 3 gives the law sigma(t) = 2 D t^(1/2). The scales are now 2.50, 5.00 and 18.4 MHz at 15 min, 1 h and 13.5 h, and 0.26 MHz at 10 s; the "bounded small" and "bounds drift" statements now leave inter-PUB drift an unmeasured alternative |
| SLOPPY: placement 2 enters the n64 decision total with weight 1/2 | survives | `block_weights` averages the two copies of each n64 block. analysis-claude.md now reports -0.057 of -0.531, -0.474 without placement 2 and -0.505 with its twin; at n128 -1.056 moves to -0.988. All stay outside their bands; no verdict changes |
| SLOPPY: the file table overstated source inspection | survives | the table now distinguishes source-opened, note-only and unopened entries |
| van der Schoot gives no platform-typical failure rate; the Thorbeck mapping is a hypothesis | survives | both sentences now say so |
| SOUND: verdicts, rule counts, Tuna decision and 64D/128D evidence classes | survives | no claim in `docs/state/research_state.json` or `docs/evidence/pathion-kernel-map/README.md` changes |

The Advisor confirmed every row of the second review: the Klimov arithmetic (2.50, 5.00, 18.37 and 0.2635 MHz) and the
n64 weights (-0.474, -0.505; n128 -1.056 to -0.988) recompute, and it required the twelve-PUB writer join above, the
paraphrased PDF locator and the removal of the withdrawn finding from the open-task table and the pull-request text,
all done.

The conjectures carried forward, each with its falsifier in review-codex.md and analysis-claude.md:
- fez loss follows the qubits of placements 7 and 15, not block k28;
- q11 readout switching together with first-and-last-batch time blocking explains the Tuna b0 split;
- kingston's stable -0.03 null offset is a tensor-product readout residual;
- the positive kingston A_7 offset is the N_b = 3 output-bit bias.
