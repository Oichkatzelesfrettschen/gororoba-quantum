# analysis

Scripts and tables behind the analysis of the scratch runs and exports. Each script reads retained files only and writes plain TSV; the tables here were produced on the compute workstation from the exports directory of the scratch runs and from this tree, and each figure of the analysis names the table it comes from.

| Script | Reads | Writes |
|---|---|---|
| `exports_audit.py EXPORTS_DIR OUT_DIR` | the 36 Singular quotient export directories (23.6 GB, not retained) | `exports-file-digests.tsv` (sha256 of every file), `exports-audit.tsv` (per export: digest verdicts, standard-monomial count and degree histogram of `qB.txt`, generator count of `s.txt`), `exports-digest-groups.tsv` (files with equal bytes in several directories) |
| `hilbert_samuel.py exports-audit.tsv OUT.tsv` | `exports-audit.tsv` | `hilbert-samuel.tsv` (finite differences of the quotient lengths and of the leading-monomial counts), `hilbert-samuel-relations.tsv` (length equality of E8-bar to VB against X-, and two degree-wise identities) |
| `scratch_ranks.py EVIDENCE_DIR OUT_DIR` | the fiber-rank and fast-ladder records of `../` and `../../ledger.tsv` | `scratch-ranks.tsv` (one row per truncated rank with the ledger Hilbert value and the relation equal, below or above), `scratch-ranks-summary.tsv` |
| `scratch_tables.py SCRATCH_RUNS_DIR OUT_DIR` | the plucker-map, kernel-limit, monomial-probe and Singular timing records of `../` | `plucker-map.tsv`, `kernel-limits.tsv`, `monomial-probes.tsv`, `singular-timings.tsv` |

Reproduction from a checkout: `python3 scratch_ranks.py ../.. . && python3 scratch_tables.py .. .` run in this directory regenerate the last two groups; the first two need the export directories (digests and sizes in [../exports/SHA256SUMS](../exports/SHA256SUMS) and `exports-file-digests.tsv`), whose standard bases take hours to days to regenerate. `hilbert_samuel.py` reads the retained `exports-audit.tsv`, so it regenerates from this tree alone.
