# Brief: pull request 940, the Tuna-17 characterization record

Reviewer: the Advisor, by the owner's selection (no other local reviewer ran). Head read: 0033373a8.

Scope. The pull request retains the Tuna-17 characterization series and its QX twin as 12 run directories, the case's analysis rows, a refit of the retained T1 counts against registered hypotheses (`gororoba_quantum/qi_decay_models.py`, `gororoba_quantum/qi_bit_correlations.py`, `scripts/qi_tuna17_t1_shape.py`), the retained-context rows that the dashboard reads (`scripts/qi_retained_context.py`) and the note `docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md`.

Inputs. The diff against origin/main, the note, the retained run directories, the committed analysis records and the pull request body.

Questions.

1. Does each stated verdict follow from a registered prediction and falsifier, or from a result read before its registration?
2. Does a confound between the T1 delays and the batches limit any claim?
3. Does the merged tree regenerate every generated file from its generator?
4. Which consumers read the regenerated retained context, and do they tolerate added keys?
5. Does the branch raise the memory of the self-test over main?
6. Does each figure in the body name its quantity?
7. Do digest-pinned files, record text and commit bodies stay clean?

Output. One row per finding: the claim, the check against the source, the disposition (survives, refuted, bounded) and the commit.
