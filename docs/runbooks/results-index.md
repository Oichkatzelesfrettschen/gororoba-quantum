# Results index

`scripts/results_index.py` answers which run, acquisition and claim a job id
or file belongs to, by joining the research registry
(`docs/state/research_state.json`), the provider run sets that
`scripts/research_state.py` validates (IBM retained-run audit, Quantum
Inspire, Quandela and IQM run directories) and the Kaggle receipt chains of
`scripts/kaggle_run.py`. It computes every answer from the retained files at
call time and writes nothing under the repository, so no index file can fall
out of date and no pull request regenerates one.

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/results_index.py summary            # counts and coverage gaps
"$PYTHON" scripts/results_index.py runs --provider ibm
"$PYTHON" scripts/results_index.py job 1528724        # provider job id -> run, acquisition, claims
"$PYTHON" scripts/results_index.py claim a5-stiefel-pfaffian-reduction
"$PYTHON" scripts/results_index.py path results/live/<run>/raw/<job>/pub_00.json
"$PYTHON" scripts/results_index.py --json summary     # any subcommand as JSON
```

`summary` lists three coverage gaps: provider runs no acquisition registers,
acquisitions whose run the provider adapter does not hold, and Kaggle
submissions with no collection receipt. Kaggle runs are simulations and enter
no acquisition. A job id is the provider's own identifier as text (IBM job
id, Quantum Inspire job number, Quandela and IQM job UUID); a Kaggle run's
job is its `owner/slug/version` kernel reference.

`sqlite [OUT]` writes the same relations (`runs`, `jobs`, `acquisitions`,
`claims`, `claim_acquisitions`, `claim_evidence`, `claim_gates`,
`claim_dependencies`) to a new SQLite file for ad hoc SQL. OUT defaults to
`${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/results-index.sqlite` and must
lie outside the repository and not exist; the file is a cache that the
command rebuilds, never a reviewed artifact, because SQLite file bytes vary
with the library version.

```sh
"$PYTHON" scripts/results_index.py sqlite /tmp/results-index.sqlite
sqlite3 /tmp/results-index.sqlite "SELECT a.provider, COUNT(*) FROM claim_acquisitions ca
  JOIN acquisitions a ON a.id = ca.acquisition GROUP BY a.provider"
```

The command reads only what the registry and adapters already validate, so
`scripts/research_state.py --check` failing makes the index refuse to build.
`tests/scripts/test_results_index.py` checks the joins on a synthetic tree
in the pull-request suite, and its `audit` test, in the nightly suite,
requires on the retained tree that every acquisition owns its run, every job
resolves to its run, every claim resolves to the runs of its acquisitions,
and a build leaves `git status` unchanged. The design choice against a committed catalog
is argued in
[the catalog opposition review](../archive/reviews/2026-10-25-results-catalog-opposition.md).
