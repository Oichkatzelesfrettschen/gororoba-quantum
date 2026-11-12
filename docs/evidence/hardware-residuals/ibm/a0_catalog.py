"""Catalog of the retained IBM acquisitions: runs, jobs, PUBs, per-job slot period and execution-time gate."""

import common

if __name__ == "__main__":
    cat = common.build_catalog()
    common.write_json(common.CATALOG, cat)
    gates = [j["predicted_over_exec"] for j in cat["jobs"]]
    print(cat["n_runs"], cat["n_jobs"], cat["n_pubs"], min(gates), max(gates))
    print(
        "jobs with one chunk:",
        sum(j["n_chunks"] == 1 for j in cat["jobs"]),
        "equal shots:",
        sum(j["equal_shots"] for j in cat["jobs"]),
    )
    print("backend none:", [j["run"] for j in cat["jobs"] if j["backend"] is None])
