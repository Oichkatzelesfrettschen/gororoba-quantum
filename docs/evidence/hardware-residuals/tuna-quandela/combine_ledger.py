"""Pool the test ledgers of the four analyses, apply Benjamini-Hochberg (q = 0.05) once over every test, and rank."""

from __future__ import annotations

import json

import common as c

FILES = [
    "a1_shot_line_extension.json",
    "a2_readout_bracket_drift.json",
    "a3_belenos_mode_efficiency.json",
    "a4_photon_number_trend.json",
]


def main() -> None:
    rows = []
    for name in FILES:
        data = json.loads((c.HERE / name).read_text())
        rows += [{**r, "source": name} for r in data["ledger"]["rows"]]
    ps = [r["log10_p"] for r in rows]
    bh = c.benjamini_hochberg(ps)
    bf = c.bonferroni(ps)
    out_rows = [
        {**r, "pooled_bh_significant": a, "pooled_bonferroni_significant": b}
        for r, a, b in zip(rows, bh, bf, strict=True)
    ]
    out_rows.sort(key=lambda r: r["log10_p"])
    summary = {
        "tests": len(rows),
        "pooled_bonferroni_alpha": c.sig(c.ALPHA / len(rows)),
        "bh_survivors": sum(bh),
        "bonferroni_survivors": sum(bf),
        "by_analysis": {
            str(a): {
                "tests": sum(1 for r in rows if r["analysis"] == a),
                "bh": sum(1 for r, x in zip(rows, bh, strict=True) if r["analysis"] == a and x),
                "bonferroni": sum(1 for r, x in zip(rows, bf, strict=True) if r["analysis"] == a and x),
            }
            for a in (1, 2, 3, 4)
        },
        "rows": out_rows,
    }
    path = c.write_json("ledger_all.json", summary)
    print(c.rel(path), {k: v for k, v in summary.items() if k != "rows"})


if __name__ == "__main__":
    main()
