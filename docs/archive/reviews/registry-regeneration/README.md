# Review of the registry regeneration (pull request 1023)

Pull request 1023 regenerates `claims.json` and `unbound.jsonl` of
[the A_5 exceptional-fiber evidence](../../../evidence/a5-exceptional-fibers/README.md) with
`build_registry.py` and adds the on-demand gate `core-a5-registry-check`; it closes issue 1021. The owner's reviewer
question went unanswered, so the recommended default ran: no local reviewer, the Advisor on head 8b993999d, then
the hosted Codex round on that head.

## Findings and dispositions

| Finding | Disposition |
|---|---|
| Advisor: the regenerated diff must be the two entries of issue 1021 with `certificates.jsonl` unchanged, and no file may pin the replaced bytes | checked: the diff is one lower bound in `claims.json` (the receipt of ledger row A5-570) and one line of `unbound.jsonl` (the receipt of A5-571); `certificates.jsonl` keeps its sha256; `git grep` of both replaced sha256 values finds no pin in gororoba-quantum or gororoba-open |
| Advisor: `--check` must also pass on the tree of pull request 1020, whose degree-2 receipt of X+ -> N+ at 32009 is a registry input | run: exit 0 on head c7774fce4 of that pull request with the two regenerated files; that receipt adds no registry entry |
| Advisor: the check against pull request 1020 copied two files and was not a merge, and both branches add entries to `ci/gates.json` | checked: `git merge-tree --write-tree` of the two heads exits 0 |
| Advisor: the README sentence and the gate's `seconds` value changed after the workstation lanes ran | covered by the hosted lanes on head 8b993999d, all ten green |
| Hosted Codex round on head 8b993999d | clean, no review thread |

This record was committed after the hosted round; it changes no file the round read.

## Open

Whether a canonical-header receipt of a cell without a K2 source in `k2-hilbert.jsonl` should add a registry entry
is observed here (it adds none) and is left undecided.
