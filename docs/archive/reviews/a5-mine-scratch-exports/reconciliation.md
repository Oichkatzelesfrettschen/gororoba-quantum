# Review: export manifests and analysis of the a5 scratch runs

Pull request 962 of gororoba-quantum. Reviewers:
- the `codex` command-line agent (gpt-daybreak-blue, high effort, read-only);
- the Advisor;
- the hosted Codex round, which this repository's guide requires before the owner's merge (owner, 2026-11-20).

## Findings and reconciliation

| Finding (codex, e064fd1) | Check | Resolution |
|---|---|---|
| P1: the README names a private host in an archive branch name, and the Ascella `SHA256SUMS` is stale for `compare_outputs.py` | Confirmed. The same name also appeared in `large-files-manifest.tsv`. | Fixed: the text reads "an archive branch of origin", and the Ascella digest list matches the committed bytes (`sha256sum -c` passes). |
| P2: figures in `ANALYSIS.md` disagree with their tables | Confirmed: the largest table is 718,578,393 bytes (`e8nm-p32029-n18-v11/qM9.txt`, checked with awk on `exports-file-digests.tsv`); the retained subtree is 3.0 MB; 8 records lie below the ledger, not 6; the reversed run's standard basis has 1,236 elements. An earlier draft also stated 73/6 for the rank tally, against 71/8 in `scratch-ranks-summary.tsv`. | Fixed in the analysis. |
| Claim 2: the ledger agreements and contradictions match the ledger text | Justified. | The contradiction of A5-244's X- clause by A5-298 and A5-299 is stated in `ANALYSIS.md`. The status cell of A5-244 (`survives`) is left for the a5 ledger's own review. |
| Advisor: the analysis scripts are live generators inside a directory the mypy sweep excludes | Confirmed. | `ci/gates.json` gives `scratch-runs/analysis/` a mypy process of its own, and the partition test lists it. |
| Advisor: the multiplicity-3 reading of E8-bar -> N- | Checked: seven lengths (N = 12 to 18, the first three from A5-321) give fifth differences 3 and 3, and predict l(19) = 93,271. | The analysis labels it a hypothesis, with l(19) as its falsifier. |

## Advisor

The Advisor's items are resolved above.
