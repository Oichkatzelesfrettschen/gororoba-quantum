"""Pool the test ledgers of the four analyses; correct by Bonferroni, Benjamini-Hochberg and Benjamini-Yekutieli.

Every procedure runs at level q = 0.05.

Two families are corrected. The full family holds every ledger row. The dependence-safe family holds the rows whose
p-value rests on independent units (a row with a non-empty `dependent` field is excluded). Bonferroni needs only
valid p-values and holds under any dependence among them. Benjamini-Hochberg assumes independence or positive
regression dependence of the p-values, which the paired all-mode and stray-excluded rows and the consecutive pairs
that share runs do not establish; Benjamini-Yekutieli controls the false discovery rate under any dependence, at
the price of dividing q by the harmonic number of the family size.

The `before` block recomputes the full family with the p-value each row carried before its method changed (the
`prior_method` alternative) over the rows that existed then; `residual_checks` lists every row with a p-value
within one decade of a cutoff under any of its readings and states whether each reading would keep it.
"""

from __future__ import annotations

import json
import math
from typing import Any

import common as c

FILES = [
    "a1_shot_line_extension.json",
    "a2_readout_bracket_drift.json",
    "a3_belenos_mode_efficiency.json",
    "a4_photon_number_trend.json",
]
NEW_ROW_SUFFIXES = (".series", ".batch")
NOT_A_READING = ("prior_method", "job_level")


def family_summary(rows: list[dict[str, Any]], prior: bool = False) -> dict[str, Any]:
    """Survivor counts of one family, in total and by analysis; `prior` reads each row's pre-change p-value."""
    ps = [r["alternatives"].get("prior_method", r["log10_p"]) if prior else r["log10_p"] for r in rows]
    decisions = c.survivors(ps)
    m = len(rows)
    by_analysis = {
        str(a): {
            "tests": sum(1 for r in rows if r["analysis"] == a),
            **{
                name: sum(1 for r, x in zip(rows, d, strict=True) if r["analysis"] == a and x)
                for name, d in decisions.items()
            },
        }
        for a in (1, 2, 3, 4)
    }
    return {
        "tests": m,
        "bonferroni_alpha": c.sig(c.ALPHA / m) if m else None,
        "bonferroni_survivors": sum(decisions["bonferroni"]),
        "bh_survivors": sum(decisions["bh"]),
        "by_survivors": sum(decisions["by"]),
        "by_analysis": by_analysis,
    }


def thresholds(m: int) -> dict[str, float]:
    """log10 p-value cutoffs: Bonferroni, and the last-rank bounds of the BH and BY step-up procedures."""
    harmonic = sum(1.0 / i for i in range(1, m + 1))
    return {
        "bonferroni": math.log10(c.ALPHA / m),
        "bh_last_rank": math.log10(c.ALPHA),
        "by_last_rank": math.log10(c.ALPHA / harmonic),
    }


def would_survive(ps: list[float], index: int, value: float) -> dict[str, bool]:
    """Decisions for row `index` when its p-value is replaced by `value` and every other row keeps its own."""
    trial = list(ps)
    trial[index] = value
    return {name: d[index] for name, d in c.survivors(trial).items()}


def main() -> None:
    rows: list[dict[str, Any]] = []
    for name in FILES:
        data = json.loads((c.HERE / name).read_text())
        rows += [{**r, "source": name} for r in data["ledger"]["rows"]]
    if len({r["test_id"] for r in rows}) != len(rows):
        raise ValueError("ledger test ids are not unique")
    ps = [r["log10_p"] for r in rows]
    full = c.survivors(ps)
    safe_rows = [r for r in rows if not r["dependent"]]
    safe = c.survivors([r["log10_p"] for r in safe_rows])
    safe_by_id = {r["test_id"]: {name: d[i] for name, d in safe.items()} for i, r in enumerate(safe_rows)}
    out_rows = []
    for i, r in enumerate(rows):
        flags = safe_by_id.get(r["test_id"])
        out_rows.append(
            {
                **r,
                "pooled_bh_significant": full["bh"][i],
                "pooled_bonferroni_significant": full["bonferroni"][i],
                "pooled_by_significant": full["by"][i],
                "safe_bh_significant": flags["bh"] if flags else None,
                "safe_bonferroni_significant": flags["bonferroni"] if flags else None,
                "safe_by_significant": flags["by"] if flags else None,
            }
        )
    out_rows.sort(key=lambda r: r["log10_p"])

    prior_rows = [r for r in rows if not r["test_id"].endswith(NEW_ROW_SUFFIXES)]
    cut = thresholds(len(rows))
    near = []
    for i, r in enumerate(rows):
        readings = {k: v for k, v in r["alternatives"].items() if k not in NOT_A_READING}
        if not readings:
            continue
        values = {"ledger": r["log10_p"], **readings}
        if not any(abs(v - t) <= 1.0 for v in values.values() for t in (cut["bonferroni"], cut["bh_last_rank"])):
            continue
        near.append(
            {
                "test_id": r["test_id"],
                "readings_log10_p": values,
                "ledger_survives": {name: d[i] for name, d in full.items()},
                "survives_if_this_reading_alone": {k: would_survive(ps, i, v) for k, v in values.items()},
            }
        )

    summary = {
        "tests": len(rows),
        "pooled_bonferroni_alpha": c.sig(c.ALPHA / len(rows)),
        "bh_survivors": sum(full["bh"]),
        "by_survivors": sum(full["by"]),
        "bonferroni_survivors": sum(full["bonferroni"]),
        "by_analysis": family_summary(rows)["by_analysis"],
        "dependence_safe_family": family_summary(safe_rows),
        "before": family_summary(prior_rows, prior=True),
        "cutoffs_log10_p": {k: c.sig(v, 5) for k, v in cut.items()},
        "residual_checks": near,
        "rows": out_rows,
    }
    path = c.write_json("ledger_all.json", summary)
    print(c.rel(path), {k: v for k, v in summary.items() if k not in ("rows", "residual_checks")})


if __name__ == "__main__":
    main()
