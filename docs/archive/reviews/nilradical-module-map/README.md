# Review of the nilradical module map and the E8-bar prime sections (pull request 1020)

Pull request 1020 decides ledger rows A5-638 and A5-639 of
[ledger.tsv](../../../evidence/a5-exceptional-fibers/ledger.tsv) and adds the cell X+ -> N+ at 32009 to the probes of
[structure/](../../../evidence/a5-exceptional-fibers/structure/README.md). One local reviewer read its first two
commits; the Advisor reviewed last, on the head with the fixes of that audit.

| File | Reviewer | Role |
|---|---|---|
| [brief.md](brief.md) | | audit brief |
| [review-codex.md](review-codex.md) | `codex` on gpt-daybreak-blue, high effort | audit, read-only, no computation |

Local paths in the two files are replaced by repository-relative paths and `SCRATCH`.

## Findings and dispositions

| Finding | Disposition |
|---|---|
| Every changed status fits the ledger's definitions; the argument of A5-638 (Koszul relations and the Euler relation of the quadric generate the syzygies of the irrelevant ideal, 2 invertible) and of A5-639 (a rational point of a reduced section lies on one geometric component) hold | accepted |
| The new degree-2 receipt had path validation only: a changed rank, count or input digest passed every gate | fixed: a `receipt` row reads the receipt, compares its input and relation digests with the files, and `check()` binds it; the replay gate covers the row |
| `check()` holds a section to its condition and does not bind the orbit partition, while the README and docstring said every field | fixed: both texts state what is bound field for field and what is held to the section condition and the replay gate |
| A5-639 said the fourfold has an F_p-point at two to four bases; one cell has one | fixed: the row lists the counts 1, 2, 4, 2 and 2, 4, 2, 4 |
| The brief counted 28 mutations; the table held 29 | the count in the pull-request body is corrected; the table now holds 33 |
| A5-638 claimed the expected map of the X+ cell was written before its run, with nothing retained to show the order | fixed: the sentence is removed; the row states the agreement across cells |
| Conjecture: the module map exists at every good split prime | tested in the pull request: three cells at p = 32057 have the same one-dimensional invertible solution with the constant 2 / i and an empty control (A5-638, A5-560) |
| Conjecture: one module map over Z[i, 1/2] governs every specialization | tested in the pull request over Q(i) on the weight slice: one invertible solution with entries in Z[i] and equal Hilbert numerators (A5-640, proved); the identification of that map with the header-slice maps is not computed |
| Advisor: A5-638 claimed an isomorphism at 32057 without a Hilbert-function input there | fixed: the row cites the numerator identity that A5-560 retains for the three cells |
| Advisor: the phrase that the 32057 constant was computed before the run repeats the unretained ordering claim | fixed: phrase removed |
| Advisor: the registry gave no entry for the new receipt | read: `build_registry.py` validates the receipt against the canonical header; `claims.json` is not regenerated here and holds no entry for it (A5-151) |
| Advisor: the two tests of A5-548 over Q(i) were owed | run in the pull request: the module map over Q(i) (A5-640) and the E8-bar -> VB ring over Q(i) (A5-641) |
