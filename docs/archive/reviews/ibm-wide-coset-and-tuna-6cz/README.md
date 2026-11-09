# Review of the wide-coset and Tuna-17 six-CZ claims

The claims `hw-ibm-pathion-wide-coset` and `hw-tuna17-pathion-six-cz-null-blocks` in `docs/state/research_state.json`
register the IBM Heron r2 whole-operand nullity runs at D = 64 and 128, and the Tuna-17 six-CZ null blocks. They also
add the 64D and 128D implications to `docs/evidence/pathion-kernel-map/README.md`.

| file | content |
|---|---|
| [brief.md](brief.md) | the review brief |
| [literature-drift-systematics.md](literature-drift-systematics.md) | documents-repository sources on drift, readout and defects, each opened at the cited page, with its manifest sha256 recomputed |
| [analysis-claude.md](analysis-claude.md) | the setting-by-setting comparison with the parallel-coset pair and the ibm_fez qubit-90 calibration finding |
| [review-codex.md](review-codex.md) | the `codex` (gpt-daybreak-blue-latest, high effort) review of the claims branch |

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
| ibm_fez qubit 90: an execution-time readout channel (`prob_meas0_prep1` 0.835) that its own raw marginal (0.919) contradicts entered the correction (analysis-claude.md) | survives | it inflates placement 2's standard error 7 to 8 times but leaves the fez null failures (-0.949 and -0.988 without it) and every verdict unchanged. Follow-up task: a collector gate in `gororoba_quantum/live_run.py` |

The conjectures carried forward, each with its falsifier in review-codex.md and analysis-claude.md:
- fez loss follows the qubits of placements 7 and 15, not block k28;
- q11 readout switching together with first-and-last-batch time blocking explains the Tuna b0 split;
- kingston's stable -0.03 null offset is a tensor-product readout residual;
- the positive kingston A_7 offset is the N_b = 3 output-bit bias.
